from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    AutomationSession, JobApplication, ApplicationFormField,
    AutomationRule, PlatformCredentials
)
from .serializers import (
    AutomationSessionSerializer, JobApplicationSerializer,
    JobApplicationCreateSerializer, AutomationRuleSerializer,
    PlatformCredentialsSerializer
)
from .tasks import apply_to_job_task, bulk_apply_task


class AutomationSessionViewSet(viewsets.ModelViewSet):
    """Automation session management"""
    serializer_class = AutomationSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AutomationSession.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Start an automation session"""
        session = self.get_object()
        if session.status == 'pending':
            session.status = 'running'
            session.save()
            
            # Start background automation
            bulk_apply_task.delay(session.id)
            
            return Response({'message': 'Automation session started'})
        
        return Response({'error': 'Session is not in pending state'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def stop_session(self, request, pk=None):
        """Stop an automation session"""
        session = self.get_object()
        if session.status == 'running':
            session.status = 'stopped'
            session.save()
            return Response({'message': 'Automation session stopped'})
        
        return Response({'error': 'Session is not running'}, status=status.HTTP_400_BAD_REQUEST)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """Job application management"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobApplicationCreateSerializer
        return JobApplicationSerializer
    
    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user).order_by('-applied_at')
    
    @action(detail=False, methods=['post'])
    def apply_to_job(self, request):
        """Apply to a single job"""
        job_id = request.data.get('job_id')
        cover_letter = request.data.get('cover_letter', '')
        
        if not job_id:
            return Response({'error': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Start background application task
        task = apply_to_job_task.delay(request.user.id, job_id, cover_letter)
        
        return Response({
            'message': 'Job application started',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class AutomationRuleViewSet(viewsets.ModelViewSet):
    """Automation rule management"""
    serializer_class = AutomationRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AutomationRule.objects.filter(user=self.request.user).order_by('-created_at')


class PlatformCredentialsViewSet(viewsets.ModelViewSet):
    """Platform credentials management"""
    serializer_class = PlatformCredentialsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PlatformCredentials.objects.filter(user=self.request.user)


class AutomationStatsView(generics.RetrieveAPIView):
    """Automation statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        stats = {
            'total_applications': JobApplication.objects.filter(user=user).count(),
            'successful_applications': JobApplication.objects.filter(
                user=user, status='applied'
            ).count(),
            'failed_applications': JobApplication.objects.filter(
                user=user, status='failed'
            ).count(),
            'pending_applications': JobApplication.objects.filter(
                user=user, status='pending'
            ).count(),
            'active_sessions': AutomationSession.objects.filter(
                user=user, status='running'
            ).count(),
            'total_sessions': AutomationSession.objects.filter(user=user).count(),
            'active_rules': AutomationRule.objects.filter(
                user=user, is_active=True
            ).count()
        }
        
        return Response(stats)


class BulkApplyView(generics.CreateAPIView):
    """Bulk job application"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        job_ids = request.data.get('job_ids', [])
        cover_letter_template = request.data.get('cover_letter_template', '')
        
        if not job_ids:
            return Response({'error': 'job_ids is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create automation session
        session = AutomationSession.objects.create(
            user=request.user,
            session_type='bulk_apply',
            target_count=len(job_ids),
            status='pending',
            config={
                'job_ids': job_ids,
                'cover_letter_template': cover_letter_template
            }
        )
        
        # Start background bulk application
        bulk_apply_task.delay(session.id)
        
        return Response({
            'message': 'Bulk application started',
            'session_id': session.id
        }, status=status.HTTP_202_ACCEPTED)
