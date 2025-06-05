from rest_framework import serializers
from .models import UserProfile, Experience, Education, ApplicationTemplate


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'
        read_only_fields = ('id',)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('id',)


class ApplicationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationTemplate
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserProfileSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    application_templates = ApplicationTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'phone', 'location', 'linkedin_url', 'github_url', 'portfolio_url',
            'summary', 'skills', 'preferred_job_types', 'preferred_locations',
            'salary_expectation_min', 'salary_expectation_max', 'availability'
        )
