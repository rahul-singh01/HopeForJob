from django.contrib import admin
from .models import UserProfile, Experience, Education, ApplicationTemplate

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_position', 'location', 'years_of_experience', 'created_at']
    list_filter = ['created_at', 'updated_at', 'auto_apply_enabled']
    search_fields = ['user__username', 'user__email', 'current_position', 'location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['profile', 'position_title', 'company_name', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'start_date', 'end_date']
    search_fields = ['profile__user__username', 'position_title', 'company_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['profile', 'degree_type', 'field_of_study', 'institution_name', 'start_date', 'end_date']
    list_filter = ['degree_type', 'start_date', 'end_date']
    search_fields = ['profile__user__username', 'degree_type', 'field_of_study', 'institution_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ApplicationTemplate)
class ApplicationTemplateAdmin(admin.ModelAdmin):
    list_display = ['profile', 'name', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['profile__user__username', 'name']
    readonly_fields = ['created_at', 'updated_at']
