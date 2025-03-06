# views.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from .permissions import IsSelf

class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update', 'me']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        # For creating a user, allow any unauthenticated user.
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.request.user.is_staff:
            return [permissions.IsAdminUser()]
        elif self.action in ['me']:
            return [permissions.IsAuthenticated(), IsSelf()]
        return [permissions.IsAdminUser()]

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'])
    def me(self, request):
        """
        Get or update the user information

        Endpoint: /api/users/me/
        """
        user = request.user
        serializer = self.get_serializer(user)
        
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(
                user, 
                data=request.data, 
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
        return Response(serializer.data)