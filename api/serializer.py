from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from core.models import Profile, CustomUser
from rest_framework_simplejwt .serializers import TokenObtainPairSerializer

class MyTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username
        
        return token

class RegisterSrializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password', 'password2']
        
    def validate(self, attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError({'password': "Passwords didn't match"})
        
        return attr
    
    def create(self, validated_data):
        user = CustomUser.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email']
        )
        
        email_username, _ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data['password'])
        user.save()
        
        return user
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"