from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.shortcuts import redirect
#Time
import time
# Messages
from django.contrib import messages

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

def Resend_email_count(request, user):
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