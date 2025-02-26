from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .permissions import IsSelf

class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    
    def get_serializer_class(self):
    
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == ['retrieve', 'update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        # For creating a user, allow any unauthenticated user.
        if self.action == 'create':
            return [permissions.AllowAny()]
        # For admins, allow all actions.
        elif self.request.user.is_staff:
            return [permissions.IsAdminUser()]
        # For actions like retrieve, update, or partial_update, ensure the user is only accessing their own data.
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsSelf()]

        return [permissions.IsAdminUser()]
