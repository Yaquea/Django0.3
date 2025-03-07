from rest_framework import serializers
from users.models import User
from PIL import Image

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'profile_image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    def validate_profile_image(self, value):
        # 1. Validate file size
        max_size = 2 * 1024 * 1024  # 2 MB
        if value.size > max_size:
            raise serializers.ValidationError("Profile image file size should not exceed 2MB.")
        
        # 2. Validate image dimensions using PIL
        try:
            img = Image.open(value)
            max_width = 1024
            max_height = 1024
            if img.width > max_width or img.height > max_height:
                raise serializers.ValidationError("Profile image dimensions should not exceed 1024x1024 pixels.")
        except Exception as e:
            raise serializers.ValidationError("Invalid image file.")
        
        return value
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'profile_image']

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        if 'profile_image' in validated_data:
            instance.profile_image = validated_data.get('profile_image')
        instance.save()
        return instance
    
    def validate_profile_image(self, value):
        # 1. Validate file size
        max_size = 2 * 1024 * 1024  # 2 MB
        if value.size > max_size:
            raise serializers.ValidationError("Profile image file size should not exceed 2MB.")
        
        # 2. Validate image dimensions
        try:
            img = Image.open(value)
            max_width = 1024
            max_height = 1024
            if img.width > max_width or img.height > max_height:
                raise serializers.ValidationError("Profile image dimensions should not exceed 1024x1024 pixels.")
        except Exception as e:
            raise serializers.ValidationError("Invalid image file.")
        
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','first_name', 'last_name', 'email', 'is_active', 'date_joined', 'profile_image']
        extra_kwargs = {
            'password': {'write_only': True}
        }