from django.contrib import admin
from .models import AutomationSession, JobApplication, ApplicationFormField, AutomationRule, PlatformCredentials

@admin.register(AutomationSession)
class AutomationSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_type', 'status', 'total_jobs_targeted', 'started_at']
    list_filter = ['status', 'session_type', 'started_at']
    search_fields = ['user__username', 'session_type', 'target_platform']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'status', 'applied_at', 'is_automated']
    list_filter = ['status', 'applied_at', 'is_automated']
    search_fields = ['user__username', 'job__title', 'job__company_name']

@admin.register(ApplicationFormField)
class ApplicationFormFieldAdmin(admin.ModelAdmin):
    list_display = ['job', 'field_name', 'field_type', 'is_required']
    list_filter = ['field_type', 'is_required']
    search_fields = ['field_name', 'job__title']

@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'name']

@admin.register(PlatformCredentials)
class PlatformCredentialsAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform_name', 'is_active', 'verification_status', 'created_at']
    list_filter = ['platform_name', 'is_active', 'verification_status', 'created_at']
    search_fields = ['user__username', 'platform_name']
