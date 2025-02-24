from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import time
from django.shortcuts import redirect
from django.contrib import messages


def send_verification_email(user, request):
    """
    Generate a unique verification link for the user and send a verification email.
    """
    
    # Encode the user's ID into a base64 format
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Generate a token using Django's built-in token generator
    token = default_token_generator.make_token(user)
    
    # Construct the full verification URL
    verification_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    )

    # Define email content
    subject = 'Verify your email address'
    message = f'Click this link to verify your email: {verification_url}'

    # Send the verification email
    send_mail(
        subject,
        message,
        'noreply@yourdomain.com',  # Sender email address
        [user.email],  # Recipient email address
        fail_silently=False,
    )


def resend_verification_email_cooldown(request, user):
    """
    Resend the verification email with different cooldowns:
      - Standard cooldown: 3 minutes (for most requests)
      - Extended cooldown: 6 hours (every 3rd request, after the first one)
    """
    # If the user's mails_count is not zero and is a multiple of 3, use extended cooldown.
    if user.mails_count > 0 and user.mails_count % 3 == 0:
        cooldown = 21600  # 6 hours in seconds
        
    else:
        cooldown = 180    # 3 minutes in seconds

    session_key = 'last_verification_email_sent'
    
    # Get the last sent time from the session.
    last_sent = request.session.get(session_key, 0)
    try:
        last_sent = int(last_sent)
    except (ValueError, TypeError):
        last_sent = 0

    current_time = int(time.time())
    
    # Check if the required cooldown has passed.
    if current_time - last_sent < cooldown:
        wait_minutes = cooldown // 60
        messages.warning(request, f'You must wait {wait_minutes} minutes before resending the email.')
        return redirect('resend-verification')
    
    # Send the verification email.
    send_verification_email(user, request)
    
    # Increment the user's email send count.
    user.mails_count += 1
    user.save()
    
    # Update the session timestamp.
    request.session['last_verification_email_sent'] = int(time.time())
    
    messages.success(request, 'Verification email sent successfully. Please check your inbox and spam folder.')
    return redirect('login')