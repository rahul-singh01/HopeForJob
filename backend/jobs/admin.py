from django.contrib import admin
from .models import JobSource, JobListing, SavedJob, JobAlert, JobMatch

@admin.register(JobSource)
class JobSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_url', 'is_active', 'scraping_enabled', 'created_at']
    list_filter = ['is_active', 'scraping_enabled', 'created_at']
    search_fields = ['name', 'base_url']

@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'location', 'employment_type', 'scraped_at', 'source']
    list_filter = ['employment_type', 'experience_level', 'scraped_at', 'source']
    search_fields = ['title', 'company_name', 'location', 'description']
    date_hierarchy = 'scraped_at'

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'priority', 'saved_at']
    list_filter = ['priority', 'saved_at']
    search_fields = ['user__username', 'job__title', 'job__company_name']

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_active', 'frequency', 'created_at']
    list_filter = ['is_active', 'frequency', 'created_at']
    search_fields = ['user__username', 'name']

@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'overall_score', 'skills_match_score', 'created_at']
    list_filter = ['overall_score', 'created_at']
    search_fields = ['user__username', 'job__title', 'job__company_name']
