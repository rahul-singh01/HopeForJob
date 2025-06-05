from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class UserActivity(models.Model):
    """Track user activity for analytics and security"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('job_application', 'Job Application'),
        ('automation_start', 'Automation Started'),
        ('automation_stop', 'Automation Stopped'),
        ('job_search', 'Job Search'),
        ('settings_change', 'Settings Change'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    
    # Activity Details
    description = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Request Information
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"


class APIKey(models.Model):
    """API keys for external integrations"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    
    name = models.CharField(max_length=200)
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Permissions
    permissions = models.JSONField(default=list, blank=True)
    
    # Usage tracking
    last_used = models.DateTimeField(blank=True, null=True)
    usage_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def is_expired(self):
        """Check if API key is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
