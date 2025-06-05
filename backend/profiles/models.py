from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
import json


class UserProfile(models.Model):
    """Extended user profile for job application automation"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    linkedin_url = models.URLField(blank=True, validators=[URLValidator()])
    github_url = models.URLField(blank=True, validators=[URLValidator()])
    
    # Resume and Documents
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter_template = models.TextField(blank=True, help_text="Template for cover letters with placeholders")
    
    # Professional Information
    current_position = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    desired_salary_min = models.PositiveIntegerField(blank=True, null=True)
    desired_salary_max = models.PositiveIntegerField(blank=True, null=True)
    preferred_locations = models.JSONField(default=list, blank=True)
    
    # Skills and Preferences
    skills = models.JSONField(default=list, blank=True, help_text="List of skills")
    job_preferences = models.JSONField(default=dict, blank=True)
    
    # Automation Settings
    auto_apply_enabled = models.BooleanField(default=False)
    max_applications_per_day = models.PositiveIntegerField(default=10)
    
    # LinkedIn Automation Credentials (encrypted)
    linkedin_email = models.CharField(max_length=255, blank=True)
    linkedin_password_encrypted = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    def get_skills_display(self):
        """Return skills as comma-separated string"""
        return ", ".join(self.skills) if self.skills else ""


class Experience(models.Model):
    """Work experience model"""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experiences')
    
    company_name = models.CharField(max_length=200)
    position_title = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.position_title} at {self.company_name}"


class Education(models.Model):
    """Education model"""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='education')
    
    institution_name = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=100)  # Bachelor's, Master's, PhD, etc.
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.degree_type} in {self.field_of_study} from {self.institution_name}"


class ApplicationTemplate(models.Model):
    """Templates for job applications"""
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='templates')
    
    name = models.CharField(max_length=200)
    cover_letter_template = models.TextField()
    custom_answers = models.JSONField(default=dict, blank=True, help_text="Common application question answers")
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.profile.user.username}"
