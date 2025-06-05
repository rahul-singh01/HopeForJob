from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile, Experience, Education, ApplicationTemplate
from .serializers import (
    UserProfileSerializer, UserProfileUpdateSerializer,
    ExperienceSerializer, EducationSerializer, ApplicationTemplateSerializer
)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """User profile detail view"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserProfileUpdateSerializer
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ExperienceListCreateView(generics.ListCreateAPIView):
    """Experience list and create view"""
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Experience.objects.filter(user_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(user_profile=profile)


class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Experience detail view"""
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Experience.objects.filter(user_profile__user=self.request.user)


class EducationListCreateView(generics.ListCreateAPIView):
    """Education list and create view"""
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Education.objects.filter(user_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(user_profile=profile)


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Education detail view"""
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Education.objects.filter(user_profile__user=self.request.user)


class ApplicationTemplateListCreateView(generics.ListCreateAPIView):
    """Application template list and create view"""
    serializer_class = ApplicationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApplicationTemplate.objects.filter(user_profile__user=self.request.user)
    
    def perform_create(self, serializer):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(user_profile=profile)


class ApplicationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Application template detail view"""
    serializer_class = ApplicationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApplicationTemplate.objects.filter(user_profile__user=self.request.user)


class ResumeUploadView(generics.CreateAPIView):
    """Resume upload view"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if 'resume' in request.FILES:
            profile.resume = request.FILES['resume']
            profile.save()
            return Response({
                'message': 'Resume uploaded successfully',
                'resume_url': profile.resume.url if profile.resume else None
            }, status=status.HTTP_201_CREATED)
        
        return Response({'error': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)
