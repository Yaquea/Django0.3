from django.shortcuts import render, redirect

# Authentication
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm
from django.contrib.auth.decorators import login_required

# Messages
from django.contrib import messages

# Send email
from django.core.mail import send_mail

# Encryptors
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password

# URL utilities
from django.urls import reverse

# Models
from .models import User

# FUNCTIONS

def send_verification_email(user, request):
    # Convert the user ID to bytes and encode it
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Generate a token using Django's default token generator
    token = default_token_generator.make_token(user)
    
    # Build an absolute URL, including the domain
    verification_url = request.build_absolute_uri(
        # The reverse function generates the relative URL path
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    
    # Email structure variables
    subject = 'Verify your email address'
    message = f'Click this link to verify your email: {verification_url}'

    # Send the verification email
    send_mail(
        subject,
        message,
        'noreply@yourdomain.com',  # From email
        [user.email],  # To email
        fail_silently=False,
    )

# URL VIEWS

def main(request):
    return render(request, 'main.html', {})

# Handles the email verification URL path
def verify_email(request, uidb64, token):
    try:
        # Perform the reverse process: decode from base64 to bytes, then get the user's ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        # Search for the user
        user = User.objects.get(pk=uid)
        
        # If the user's token is correct, activate the account
        if default_token_generator.check_token(user, token):
            user.is_verified = True
            # Save the changes
            user.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification link.')
            return redirect('main')
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        # Error handling
        messages.error(request, 'Invalid verification link.')
        return redirect('main')
    
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': SignupForm(),
        })
    else:
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.password = make_password(form.cleaned_data['password1'])  # Hash password
            user.is_active = False  # It is false until the user verifies their email
            user.save()  # Now save to DB

            # Send the verification email
            send_verification_email(user, request)

            messages.success(request, 'You have successfully created a user. Please check your email to verify your account.')
            return redirect('login')  # Redirect to the login page or another view
        else:
            error = 'Invalid form. Please try again.'
            return render(request, 'signup.html', {
                'form': SignupForm(),
                'error': error
            })
        
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm()
        })
    else:
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check if the user's email is verified before allowing login
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
            # Extract the error message from the form or use a default one
            error = "Invalid username or password. Please try again."
            return render(request, 'login.html', {
                'form': form, 
                'error': error
            })

@login_required
def log_out(request):
    logout(request)
    # Display a success message after logging out
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main')