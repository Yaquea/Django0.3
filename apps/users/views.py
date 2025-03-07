from django.shortcuts import render, redirect, get_object_or_404

# Authentication
from django.contrib.auth import login as auth_login, logout ,update_session_auth_hash
from django.contrib.auth.decorators import login_required

# Forms
from django.contrib.auth.forms import AuthenticationForm
from .forms import Signup_Form, Resend_Verification_Email_Form, UserUpdateForm

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
from .security.services import send_verification_email, resend_verification_email_cooldown



def main(request):
    """
    Render the main landing page.
    """
    return render(request, 'main.html', {
        'name': "main"
    })


def verify_email(request, uidb64, token):
    """
    Verify the user's email address.

    This view decodes the base64-encoded user ID, retrieves the corresponding user,
    and checks if the provided token is valid. If valid, the user's account is activated
    and marked as verified.
    """
    try:
        # Decode the base64-encoded user ID to obtain the actual ID.
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

    GET: Display the form to request a new verification email.
    POST: Validate the provided email, ensure the account is not already verified,
          and enforce a cooldown on resend attempts.
    """
    if request.method == 'GET':
        return render(request, 'resend_verification.html', {
            'form': Resend_Verification_Email_Form(),
            'name': "resend email"
        })
    elif request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Please provide an email address.')
            return render(request, 'resend_verification.html', {
                'form': Resend_Verification_Email_Form(),
                'name': "resend email"
            })
    
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'This email is not registered.')
            return render(request, 'resend_verification.html', {
                'form': Resend_Verification_Email_Form(),
                'name': "resend email"
            })
        
        if user.is_verified:
            messages.info(request, 'This email is already verified.')
            return redirect('login')
        
        # Enforce the cooldown for resend attempts.
        resend_verification_email_cooldown(request, user)
        return redirect('login')


def signup(request):
    """
    Handle user signup.

    GET: Display the signup form.
    POST: Validate the submitted data, create a new user with a hashed password,
          set the account as inactive until email verification, and send the verification email.
    """
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': Signup_Form(),
            'name': "sign up",
        })
    else:
        form = Signup_Form(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Do not immediately save the user to the database.
            user.password = make_password(form.cleaned_data['password1'])  # Hash the password.
            user.is_active = False  # Deactivate the account until email verification.
            user.save()  # Save the new user to the database.

            # Send a verification email to the new user.
            send_verification_email(user, request)

            messages.success(
                request,
                'You have successfully created an account. Please check your email to verify your account.'
            )
            return redirect('login')  # Redirect the user to the login page.
        else:
            error = 'Invalid form. Please try again.'
            return render(request, 'signup.html', {
                'form': Signup_Form(),
                'error': error, 
                'name': "sign up",
            })


def login(request):
    """
    Authenticate and log in the user.

    GET: Display the login form.
    POST: Validate the user's credentials and ensure that the email has been verified
          before allowing login.
    """
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm(),
            'name': "log in"
        })
    else:
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check that the user's email is verified.
            if not user.is_verified:
                messages.error(request, 'Please verify your email address first.')
                return render(request, 'login.html', {
                    'form': form,
                    'name': "log in"
                })
            else:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('main')
        else:
            error = "Invalid username or password. Please try again."
            return render(request, 'login.html', {
                'form': form, 
                'error': error,
                'name': "log in"
            })

#LOGIN REQUIRED 

@login_required
def log_out(request):
    """
    Log out the authenticated user.

    After logging out, display a success message and redirect the user to the main page.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main')


@login_required
def user_profile(request, user_name):
    """
    Render the user profile and pass the user's profile information to the template.

    GET: Display the user's profile information.
    POST: If the viewer is the profile owner, redirect to the update view; otherwise, show an error message.
    """
    viewer = request.user
    user_owner = get_object_or_404(User, username=user_name)
    if request.method == 'GET':
        return render(request, 'profile.html', {
            'user_owner': user_owner,
            'user_viewer': viewer,
            'name': user_owner.username,
        })
    else:
        if viewer == user_owner:
            return redirect('update_user')
        else:
            messages.error(request, 'You are not the profile owner.')
            return render(request, 'profile.html', {
                'user_owner': user_owner,
                'user_viewer': viewer,
                'name': user_owner.username,
            })


@login_required
def update_user(request):
    """
    Update the user's information.

    GET: Display the update form pre-populated with the user's current information.
    POST: Update the user's information if the submitted form is valid.
    """
    user = request.user 
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)  
        if form.is_valid():
            user = form.save()
            # Update the session hash to ensure the session remains valid,
            # especially if fields that contribute to the auth hash (like username) change.
            update_session_auth_hash(request, user)
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_profile', user_name=user.username)
    else:
        form = UserUpdateForm(instance=user) 

    return render(request, 'update_user.html', {
        'form': form,
        'name': 'update',
    })