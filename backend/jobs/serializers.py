from rest_framework import serializers
from .models import JobListing, JobSource, SavedJob, JobAlert, JobMatch


class JobSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSource
        fields = '__all__'
        read_only_fields = ('id',)


class JobListingSerializer(serializers.ModelSerializer):
    source = JobSourceSerializer(read_only=True)
    
    class Meta:
        model = JobListing
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class JobListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobListing
        fields = (
            'title', 'company', 'location', 'description', 'requirements',
            'salary_min', 'salary_max', 'job_type', 'experience_level',
            'url', 'source', 'external_id', 'posted_date', 'application_deadline'
        )


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobListingSerializer(read_only=True)
    
    class Meta:
        model = SavedJob
        fields = '__all__'
        read_only_fields = ('id', 'user', 'saved_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JobAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAlert
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'last_triggered')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JobMatchSerializer(serializers.ModelSerializer):
    job = JobListingSerializer(read_only=True)
    
    class Meta:
        model = JobMatch
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')
