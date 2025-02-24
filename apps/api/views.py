from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import User
from .serializers import UserSerializer, UserCreateSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        return UserCreateSerializer if self.action == 'create' else UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)