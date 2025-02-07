from django.shortcuts import render, redirect

# Authentication
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required

#Forms
from django.contrib.auth.forms import AuthenticationForm
from .forms import Signup_Form, Resend_Verification_Email_Form

# Messages
from django.contrib import messages

# Send email
from django.core.mail import send_mail

# Encryptors
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

# URL utilities
from django.urls import reverse

# Models
from .models import User

#Time
import time
from django.utils.timezone import now

# FUNCTIONS

def send_verification_email(user, request):
    
    # Convert the user ID to bytes and encode it
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # Generate a token using Django's default token generator
    token = default_token_generator.make_token(user)
    
    # Build an absolute URL, including the domain
    verification_url = request.build_absolute_uri(
    reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
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
    ),

# URL VIEWS

def main(request):
    user = authenticate(username="IA", password="IA")
    print(user)
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
            user.is_active = True
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

def resend_verification_email(request):
    if request.method == 'GET':
        return render(request, 'resend_verification.html', {'form': Resend_Verification_Email_Form})
    
    elif request.method == 'POST':
        email = request.POST.get('email')



        
        if not email:
            messages.error(request, 'please, send an email.')
            return render(request, 'resend_verification.html', {'form': Resend_Verification_Email_Form})
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'This email is not registred.')
            return render(request, 'resend_verification.html', {'form': Resend_Verification_Email_Form})
        
        if user.is_verified:
            messages.info(request, 'This email is alredy verify.')
            return redirect('login')
        
    #Intentar encapsular en una funcion
        #calls the last time the users send the mail
        last_sent = request.session.get('last_verification_email_sent', 0)

        #Turns in int
        try:
            last_sent = int(last_sent)
        except (ValueError, TypeError):
            last_sent = 0

        #calls the current time
        current_time = int(time.time())  

        #Compares these two times to get an interval of 180 seconds or 3 minuts
        if current_time - last_sent < 180:
            #Send a warning only if two mins not passed yet
            messages.warning(request, '3 mins for can resend the mail.')
            return redirect('resend-verification')
        
        #send the mail
        send_verification_email(user, request)
        
        #Now set the time session with the current time, this works like a for 
        request.session['last_verification_email_sent'] = int(time.time())
        
        messages.success(request, 'The mail has been send, please check your email and check the spam')
        return redirect('login')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': Signup_Form(),
        })
    else:
        form = Signup_Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.password = make_password(form.cleaned_data['password1'])  # password
            user.is_active = False  # It is false until the user verifies their email
            user.save()  # Now save to DB

            # Send the verification email
            send_verification_email(user, request)

            messages.success(request, 'You have successfully created a user. Please check your email to verify your account.')
            return redirect('login')  # Redirect to the login 
        else:
            error = 'Invalid form. Please try again.'
            return render(request, 'signup.html', {
                'form': Signup_Form(),
                'error': error
            })
        
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html', {
            'form': AuthenticationForm()
        })
    else:
        print(request.POST)
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
            print(form.errors)
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

    #List
        #make a limit of resend mails, this must modifies the model

        #The email tokens never expires so XD
        
        #put the non views functions on security/functions