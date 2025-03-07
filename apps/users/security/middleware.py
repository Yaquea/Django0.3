
from django.contrib.auth import logout
from django.utils import timezone
from django.contrib import messages

class SessionTimeoutMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        """
        If the user does not perform any action for a while, the middleware checks the last activity timestamp 
        and compares it with the current time. If more than 30 minutes have passed, the user is automatically logged out.
        """
        
    def __call__(self, request):
        if request.user.is_authenticated:
            # Retrieve the last activity timestamp from the session
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Calculate idle time in seconds
                idle_time = timezone.now().timestamp() - last_activity
                if idle_time > 1800:  # 30 minutes of inactivity
                    logout(request)
                    messages.info(request, 'Your session has expired.')
                    request.session.flush()
                    
            # Update last activity timestamp when the user makes an action
            request.session['last_activity'] = timezone.now().timestamp()

        return self.get_response(request)
