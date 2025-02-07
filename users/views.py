from django.shortcuts import render, redirect

# Authentication
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required

# Forms
from django.contrib.auth.forms import AuthenticationForm
from .forms import Signup_Form, Resend_Verification_Email_Form

# Messages
from django.contrib import messages

# Security
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password

# Models
from .models import User

# Services
from .security.services import send_verification_email, Resend_email_count

# URL Views

def main(request):
    """
    Render the main landing page.
    """
    return render(request, 'main.html', {})

def verify_email(request, uidb64, token):
    """
    Handle email verification.

    This view decodes the base64-encoded user ID, retrieves the corresponding user,
    and checks if the provided token is valid. If valid, the user's account is activated
    and marked as verified.
    """
    try:
        # Decode the base64 encoded user ID to obtain the actual ID.
        uid = force_str(urlsafe_base64_decode(uidb64))
        # Retrieve the user based on the decoded ID.
        user = User.objects.get(pk=uid)
        
        # Verify that the token is valid for the retrieved user.
        if default_token_generator.check_token(user, token):
            user.is_verified = True
            user.is_active = True
            # Save the changes to the user model.
            user.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification link.')
            return redirect('main')
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # Handle errors such as an invalid UID or non-existent user.
        messages.error(request, 'Invalid verification link.')
        return redirect('main')

def resend_verification_email(request):
    """
    Allow users to request a new verification email.

    For GET requests, display the resend verification email form.
    For POST requests, validate the provided email, verify that the account has not already been
    verified, and then enforce a limit on the number of resend attempts via the Resend_email_count service.
    """
    if request.method == 'GET':
        return render(request, 'resend_verification.html', {'form': Resend_Verification_Email_Form})
    
    elif request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Please provide an email address.')
            return render(request, 'resend_verification.html', {'form': Resend_Verification_Email_Form})
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'This email is not registered.')
            return render(request, 'resend_verification.html', {'form': Resend_Verification_Email_Form})
        
        if user.is_verified:
            messages.info(request, 'This email is already verified.')
            return redirect('login')
        
        # Enforce the limit on resend attempts.
        Resend_email_count(request, user)

        return redirect('login')

def signup(request):
    """
    Handle user signup.

    On GET requests, display the signup form.
    On POST requests, validate the submitted data, create a new user with a hashed password,
    set the account as inactive until email verification, and send the verification email.
    """
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': Signup_Form(),
        })
    else:
        form = Signup_Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Do not immediately save the user to the database.
            user.password = make_password(form.cleaned_data['password1'])  # Hash the password.
            user.is_active = False  # Deactivate the account until email verification.
            user.save()  # Save the new user to the database.

            # Send a verification email to the new user.
            send_verification_email(user, request)

            messages.success(request, 'You have successfully created a user. Please check your email to verify your account.')
            return redirect('login')  # Redirect the user to the login page.
        else:
            error = 'Invalid form. Please try again.'
            return render(request, 'signup.html', {
                'form': Signup_Form(),
                'error': error
            })
        
def login(request):
    """
    Authenticate and log in the user.

    On GET requests, display the login form.
    On POST requests, validate the user's credentials and ensure that the email has been verified
    before allowing login.
    """
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm()
        })
    else:
        print(request.POST)
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check that the user's email is verified.
            if not user.is_verified:
                messages.error(request, 'Please verify your email address first.')
                return render(request, 'login.html', {
                    'form': form
                })
            else:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('main')
        else:
            print(form.errors)
            # Use a default error message if authentication fails.
            error = "Invalid username or password. Please try again."
            return render(request, 'login.html', {
                'form': form, 
                'error': error
            })

@login_required
def log_out(request):
    """
    Log out the authenticated user.

    After logout, display a success message and redirect the user to the main page.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main')
