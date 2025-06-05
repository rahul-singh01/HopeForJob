from rest_framework import serializers
from .models import (
    AutomationSession, JobApplication, ApplicationFormField,
    AutomationRule, PlatformCredentials
)


class ApplicationFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFormField
        fields = '__all__'
        read_only_fields = ('id',)


class JobApplicationSerializer(serializers.ModelSerializer):
    form_fields = ApplicationFormFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('id', 'user', 'applied_at', 'updated_at')


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = (
            'job', 'cover_letter', 'resume_file', 'status', 'notes',
            'automation_session'
        )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AutomationSessionSerializer(serializers.ModelSerializer):
    applications = JobApplicationSerializer(many=True, read_only=True)
    
    class Meta:
        model = AutomationSession
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AutomationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PlatformCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformCredentials
        fields = ('id', 'user', 'platform', 'username', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
        extra_kwargs = {
            'password': {'write_only': True},
            'encrypted_password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
