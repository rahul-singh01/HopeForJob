from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import JobListing, JobSource, SavedJob, JobAlert, JobMatch
from .serializers import (
    JobListingSerializer, JobListingCreateSerializer,
    JobSourceSerializer, SavedJobSerializer,
    JobAlertSerializer, JobMatchSerializer
)
from .tasks import scrape_jobs_task


class JobListingViewSet(viewsets.ModelViewSet):
    """Job listing viewset"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobListingCreateSerializer
        return JobListingSerializer
    
    def get_queryset(self):
        queryset = JobListing.objects.all().order_by('-scraped_at')
        
        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(company_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filter by job type
        job_type = self.request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(employment_type=job_type)
            
        return queryset


class JobSourceViewSet(viewsets.ModelViewSet):
    """Job source viewset"""
    queryset = JobSource.objects.all()
    serializer_class = JobSourceSerializer
    permission_classes = [IsAuthenticated]


class SavedJobViewSet(viewsets.ModelViewSet):
    """Saved job viewset"""
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).order_by('-saved_at')


class JobAlertViewSet(viewsets.ModelViewSet):
    """Job alert viewset"""
    serializer_class = JobAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user).order_by('-created_at')


class JobMatchViewSet(viewsets.ModelViewSet):
    """Job match viewset"""
    serializer_class = JobMatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return JobMatch.objects.filter(user=self.request.user).order_by('-match_score')


class JobSearchView(generics.ListAPIView):
    """Job search view"""
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = JobListing.objects.all()
        
        # Advanced search filters
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(company_name__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query)
            )
        
        return queryset.order_by('-scraped_at')


class JobScrapingView(generics.CreateAPIView):
    """Job scraping view"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        source_name = request.data.get('source', 'linkedin')
        search_query = request.data.get('query', '')
        location = request.data.get('location', '')
        
        # Start background scraping task
        task = scrape_jobs_task.delay(source_name, search_query, location)
        
        return Response({
            'message': 'Job scraping started',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class JobRecommendationsView(generics.ListAPIView):
    """Job recommendations view"""
    serializer_class = JobListingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get user's saved jobs and matches to recommend similar ones
        user_saved_jobs = SavedJob.objects.filter(user=self.request.user).values_list('job_id', flat=True)
        
        # Simple recommendation: jobs from same companies or similar titles
        recommended_jobs = JobListing.objects.exclude(id__in=user_saved_jobs)
        
        if user_saved_jobs:
            saved_companies = JobListing.objects.filter(id__in=user_saved_jobs).values_list('company_name', flat=True)
            recommended_jobs = recommended_jobs.filter(company_name__in=saved_companies)
        
        return recommended_jobs.order_by('-scraped_at')[:20]


class JobAnalyticsView(generics.RetrieveAPIView):
    """Job analytics view"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        analytics = {
            'total_saved_jobs': SavedJob.objects.filter(user=user).count(),
            'total_applications': 0,  # Will be filled from automation app
            'active_alerts': JobAlert.objects.filter(user=user, is_active=True).count(),
            'job_matches': JobMatch.objects.filter(user=user).count(),
            'top_companies': list(
                SavedJob.objects.filter(user=user)
                .values_list('job__company_name', flat=True)
                .distinct()[:10]
            )
        }
        
        return Response(analytics)
