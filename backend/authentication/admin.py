from django.contrib import admin
from .models import UserActivity, APIKey

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'timestamp', 'ip_address']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['timestamp']
    
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'last_used', 'usage_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'last_used']
    search_fields = ['name', 'user__username']
    readonly_fields = ['key', 'created_at', 'last_used', 'usage_count']
