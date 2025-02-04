#Httpsresponse
from django.shortcuts import render, redirect

#Auth
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm
from django.contrib.auth.decorators import login_required

#message
from django.contrib import messages

#send email
from django.core.mail import send_mail

#encryptors
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password

#URL
from django.urls import reverse

#models
from .models import User

#FUNCTIONS


def send_verification_email(user, request):
    #Transform the user id to bytes then encode the bytes
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    #Django funtion 
    token = default_token_generator.make_token(user)
    
    #Build absolute url turns it into a full URL including the domain
    verification_url = request.build_absolute_uri(
        #reverse  generates the relative URL path
    reverse('verify_email', kwargs={'uidb64': uid, 'token': token}))
    
    #Email structure vars
    subject = 'Verify your email address'
    message = f'Click this link to verify your email: {verification_url}'

    #Declares an email structure
    send_mail(
        subject,
        message,
        'noreply@yourdomain.com',  # From email
        [user.email],  # To email
        fail_silently=False,
    )


#URL VIEWS

def main(request):
    return render(request, 'main.html', {
    })


#takes the url path
def verify_email(request, uidb64, token):
    try:
        #Do the reverse process, code to bytes and then to the User´s id
        uid = force_str(urlsafe_base64_decode(uidb64))
        #search user
        user = User.objects.get(pk=uid)
        
        #if the user´s token is correct turns to active the account
        if default_token_generator.check_token(user, token):
            user.is_verified = True
            #save the changes
            user.save()
            messages.success(request, 'Email verified successfully!')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification link.')
            return redirect('main')
        
        #error management  
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
        return redirect('main')
    

def signup(request):
    if request.method == ('GET'):
         return render(request, 'signup.html', {
              'form':SignupForm() ,
         })
    else:
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save yet
            user.password = make_password(form.cleaned_data['password1'])  # Hash password
            user.is_active = False #Is false until user verify email
            user.save()  # Now save to DB

            #Send verification email
            send_verification_email(request.user, request)

            messages.success(request, 'You have been created a user successfully, please check your email to verify your account.')
            return redirect('login')  # Redirect to login page or another view
        else:
            error = 'Invalid form. Please try again.'
            return render(request, 'signup.html', {
                'form':SignupForm() ,
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

            if not user.is_verified:
                messages.error(request, 'Please verify your email address first.')

                return render(request, 'login.html', {
                    'form': form})
            
            else:
                auth_login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('main')
            
        else:
            # Extract error message from form or use a default
            error = "Invalid username or password. Please try again."
            return render(request, 'login.html', {
                'form': form, 
                'error': error
                })


@login_required
def log_out(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('main')
