from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserActivity, APIKey
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserActivitySerializer, APIKeySerializer
)
import logging

logger = logging.getLogger('authentication')


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Log user activity
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })


class LogoutView(generics.GenericAPIView):
    """User logout endpoint"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        # Log user activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': 'Logged out successfully'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get user profile"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserActivityListView(generics.ListAPIView):
    """List user activities"""
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-timestamp')


class APIKeyListCreateView(generics.ListCreateAPIView):
    """API key management"""
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API key detail"""
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
