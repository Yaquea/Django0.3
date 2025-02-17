from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.main, name=("main")),
    path('signup/', views.signup ,name=("signup")),
    path('login/', views.login ,name=("login")),
    path('logout/', views.log_out ,name=("logout")),
    path('<str:user_name>/', views.user_profile, name='user_profile'),
    path('Update/User', views.update_user, name='update_user'),

    path('email-verification/<str:uidb64>/<str:token>/', views.verify_email, name='verify-email'),
    path('resend-verification/', views.resend_verification_email, name='resend-verification'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
