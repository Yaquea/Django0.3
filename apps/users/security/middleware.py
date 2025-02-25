from django.contrib.auth import logout
from django.utils import timezone
from django.contrib import messages

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                idle_time = timezone.now().timestamp() - last_activity
                if idle_time > 1800:  # Tiempo de inactividad en segundos
                    logout(request)
                    messages.info(request, 'Your session has been expired.')
                    request.session.flush()
                    
            # Actualiza la marca de tiempo
            request.session['last_activity'] = timezone.now().timestamp()

        return self.get_response(request)
