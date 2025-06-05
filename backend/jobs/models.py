from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import URLValidator
import uuid


class JobSource(models.Model):
    """Different job board sources"""
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField(validators=[URLValidator()])
    is_active = models.BooleanField(default=True)
    scraping_enabled = models.BooleanField(default=True)
    
    # Scraping configuration
    scraping_config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class JobListing(models.Model):
    """Individual job listings scraped from various sources"""
    
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('executive', 'Executive'),
    ]
    
    # Unique identifier
    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    external_id = models.CharField(max_length=200, blank=True, help_text="ID from the source website")
    
    # Basic Information
    title = models.CharField(max_length=300)
    company_name = models.CharField(max_length=200)
    company_logo_url = models.URLField(blank=True, validators=[URLValidator()])
    
    # Job Details
    description = models.TextField()
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    is_remote = models.BooleanField(default=False)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, blank=True)
    
    # Compensation
    salary_min = models.PositiveIntegerField(blank=True, null=True)
    salary_max = models.PositiveIntegerField(blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    
    # Source Information
    source = models.ForeignKey(JobSource, on_delete=models.CASCADE, related_name='job_listings')
    source_url = models.URLField(validators=[URLValidator()])
    application_url = models.URLField(blank=True, validators=[URLValidator()])
    
    # Skills and Keywords
    required_skills = models.JSONField(default=list, blank=True)
    preferred_skills = models.JSONField(default=list, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    
    # Application Details
    application_deadline = models.DateTimeField(blank=True, null=True)
    posted_date = models.DateTimeField(blank=True, null=True)
    
    # Automation Flags
    is_auto_applicable = models.BooleanField(default=False)
    auto_apply_difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default='medium'
    )
    
    # Metadata
    scraped_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-posted_date', '-scraped_at']
        indexes = [
            models.Index(fields=['title', 'company_name']),
            models.Index(fields=['location', 'is_remote']),
            models.Index(fields=['employment_type', 'experience_level']),
            models.Index(fields=['posted_date']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    @property
    def salary_range_display(self):
        """Display salary range in readable format"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,} {self.salary_currency}"
        elif self.salary_min:
            return f"${self.salary_min:,}+ {self.salary_currency}"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,} {self.salary_currency}"
        return "Salary not specified"
    
    def get_required_skills_display(self):
        """Return required skills as comma-separated string"""
        return ", ".join(self.required_skills) if self.required_skills else ""


class SavedJob(models.Model):
    """Jobs saved by users for later application"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='saved_by')
    
    notes = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )
    
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class JobAlert(models.Model):
    """Automated job alerts based on user criteria"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    
    name = models.CharField(max_length=200)
    keywords = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    employment_types = models.JSONField(default=list)
    experience_levels = models.JSONField(default=list)
    
    salary_min = models.PositiveIntegerField(blank=True, null=True)
    is_remote_only = models.BooleanField(default=False)
    
    # Alert settings
    is_active = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='daily'
    )
    
    last_sent = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class JobMatch(models.Model):
    """AI-powered job matching scores"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='matches')
    
    # Matching scores (0-100)
    overall_score = models.PositiveIntegerField()
    skills_match_score = models.PositiveIntegerField()
    experience_match_score = models.PositiveIntegerField()
    location_match_score = models.PositiveIntegerField()
    salary_match_score = models.PositiveIntegerField()
    
    # AI Analysis
    match_analysis = models.JSONField(default=dict, blank=True)
    recommendations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-overall_score', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title} ({self.overall_score}%)"
