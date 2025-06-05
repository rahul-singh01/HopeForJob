from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from jobs.models import JobListing
import uuid


class AutomationSession(models.Model):
    """Automation session tracking"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automation_sessions')
    
    # Session Details
    session_type = models.CharField(
        max_length=50,
        choices=[
            ('job_scraping', 'Job Scraping'),
            ('job_application', 'Job Application'),
            ('profile_update', 'Profile Update'),
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Configuration
    target_platform = models.CharField(max_length=50)  # LinkedIn, Indeed, etc.
    automation_config = models.JSONField(default=dict, blank=True)
    
    # Progress Tracking
    total_jobs_targeted = models.PositiveIntegerField(default=0)
    jobs_processed = models.PositiveIntegerField(default=0)
    applications_submitted = models.PositiveIntegerField(default=0)
    applications_failed = models.PositiveIntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    estimated_duration = models.DurationField(blank=True, null=True)
    
    # Logs and Results
    session_logs = models.JSONField(default=list, blank=True)
    error_message = models.TextField(blank=True)
    results_summary = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.session_type} - {self.user.username} ({self.status})"
    
    @property
    def duration(self):
        """Calculate session duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None
    
    @property
    def success_rate(self):
        """Calculate application success rate"""
        total_attempts = self.applications_submitted + self.applications_failed
        if total_attempts > 0:
            return (self.applications_submitted / total_attempts) * 100
        return 0


class JobApplication(models.Model):
    """Track individual job applications"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('offered', 'Offered'),
        ('accepted', 'Accepted'),
        ('failed', 'Application Failed'),
    ]
    
    application_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    session = models.ForeignKey(
        AutomationSession, 
        on_delete=models.CASCADE, 
        related_name='applications',
        blank=True, 
        null=True
    )
    
    # Application Details
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    is_automated = models.BooleanField(default=False)
    
    # Application Content
    cover_letter_used = models.TextField(blank=True)
    custom_answers = models.JSONField(default=dict, blank=True)
    resume_version = models.CharField(max_length=200, blank=True)
    
    # Tracking
    applied_at = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    
    # Response Tracking
    response_received_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)
    interview_notes = models.TextField(blank=True)
    
    # Automation Metadata
    automation_logs = models.JSONField(default=list, blank=True)
    error_details = models.TextField(blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-applied_at', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} -> {self.job.title} ({self.status})"
    
    @property
    def time_since_application(self):
        """Time since application was submitted"""
        if self.applied_at:
            return timezone.now() - self.applied_at
        return None


class ApplicationFormField(models.Model):
    """Track form fields encountered during automation"""
    
    FIELD_TYPES = [
        ('text', 'Text Input'),
        ('textarea', 'Text Area'),
        ('select', 'Dropdown Select'),
        ('radio', 'Radio Button'),
        ('checkbox', 'Checkbox'),
        ('file', 'File Upload'),
        ('date', 'Date Picker'),
        ('number', 'Number Input'),
    ]
    
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='form_fields')
    
    # Field Information
    field_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    field_label = models.CharField(max_length=500, blank=True)
    is_required = models.BooleanField(default=False)
    
    # Field Metadata
    css_selector = models.CharField(max_length=500, blank=True)
    xpath = models.CharField(max_length=500, blank=True)
    field_options = models.JSONField(default=list, blank=True)  # For select/radio fields
    
    # AI Mapping
    suggested_answer = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.job.title} - {self.field_label or self.field_name}"


class AutomationRule(models.Model):
    """User-defined automation rules"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automation_rules')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Rule Conditions
    conditions = models.JSONField(default=dict, help_text="Conditions that trigger this rule")
    
    # Rule Actions
    actions = models.JSONField(default=dict, help_text="Actions to take when conditions are met")
    
    # Rule Settings
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=1)
    max_applications_per_day = models.PositiveIntegerField(default=10)
    
    # Usage Statistics
    times_triggered = models.PositiveIntegerField(default=0)
    successful_applications = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class PlatformCredentials(models.Model):
    """Encrypted credentials for job platforms"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='platform_credentials')
    
    platform_name = models.CharField(max_length=100)  # LinkedIn, Indeed, etc.
    username = models.CharField(max_length=255)
    password_encrypted = models.TextField()  # Encrypted password
    
    # Additional platform-specific data
    additional_data = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_verified = models.DateTimeField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('failed', 'Failed'),
            ('expired', 'Expired'),
        ],
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'platform_name')
    
    def __str__(self):
        return f"{self.platform_name} - {self.user.username}"
