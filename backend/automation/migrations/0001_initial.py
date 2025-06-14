# Generated by Django 5.2.2 on 2025-06-05 12:38

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationFormField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=200)),
                ('field_type', models.CharField(choices=[('text', 'Text Input'), ('textarea', 'Text Area'), ('select', 'Dropdown Select'), ('radio', 'Radio Button'), ('checkbox', 'Checkbox'), ('file', 'File Upload'), ('date', 'Date Picker'), ('number', 'Number Input')], max_length=20)),
                ('field_label', models.CharField(blank=True, max_length=500)),
                ('is_required', models.BooleanField(default=False)),
                ('css_selector', models.CharField(blank=True, max_length=500)),
                ('xpath', models.CharField(blank=True, max_length=500)),
                ('field_options', models.JSONField(blank=True, default=list)),
                ('suggested_answer', models.TextField(blank=True)),
                ('confidence_score', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='form_fields', to='jobs.joblisting')),
            ],
        ),
        migrations.CreateModel(
            name='AutomationRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('conditions', models.JSONField(default=dict, help_text='Conditions that trigger this rule')),
                ('actions', models.JSONField(default=dict, help_text='Actions to take when conditions are met')),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.PositiveIntegerField(default=1)),
                ('max_applications_per_day', models.PositiveIntegerField(default=10)),
                ('times_triggered', models.PositiveIntegerField(default=0)),
                ('successful_applications', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automation_rules', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['priority', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AutomationSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('session_type', models.CharField(choices=[('job_scraping', 'Job Scraping'), ('job_application', 'Job Application'), ('profile_update', 'Profile Update')], max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('target_platform', models.CharField(max_length=50)),
                ('automation_config', models.JSONField(blank=True, default=dict)),
                ('total_jobs_targeted', models.PositiveIntegerField(default=0)),
                ('jobs_processed', models.PositiveIntegerField(default=0)),
                ('applications_submitted', models.PositiveIntegerField(default=0)),
                ('applications_failed', models.PositiveIntegerField(default=0)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('estimated_duration', models.DurationField(blank=True, null=True)),
                ('session_logs', models.JSONField(blank=True, default=list)),
                ('error_message', models.TextField(blank=True)),
                ('results_summary', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='automation_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('submitted', 'Submitted'), ('in_review', 'In Review'), ('interview_scheduled', 'Interview Scheduled'), ('rejected', 'Rejected'), ('withdrawn', 'Withdrawn'), ('offered', 'Offered'), ('accepted', 'Accepted'), ('failed', 'Application Failed')], default='pending', max_length=30)),
                ('is_automated', models.BooleanField(default=False)),
                ('cover_letter_used', models.TextField(blank=True)),
                ('custom_answers', models.JSONField(blank=True, default=dict)),
                ('resume_version', models.CharField(blank=True, max_length=200)),
                ('applied_at', models.DateTimeField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('follow_up_date', models.DateTimeField(blank=True, null=True)),
                ('response_received_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('interview_notes', models.TextField(blank=True)),
                ('automation_logs', models.JSONField(blank=True, default=list)),
                ('error_details', models.TextField(blank=True)),
                ('screenshots', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.joblisting')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='automation.automationsession')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-applied_at', '-created_at'],
                'unique_together': {('user', 'job')},
            },
        ),
        migrations.CreateModel(
            name='PlatformCredentials',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_name', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=255)),
                ('password_encrypted', models.TextField()),
                ('additional_data', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(default=True)),
                ('last_verified', models.DateTimeField(blank=True, null=True)),
                ('verification_status', models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('failed', 'Failed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platform_credentials', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'platform_name')},
            },
        ),
    ]
