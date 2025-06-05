from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import JobSource, JobListing
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create sample job data for testing'

    def handle(self, *args, **options):
        # Create job sources
        sources_data = [
            {
                'name': 'LinkedIn',
                'base_url': 'https://linkedin.com/jobs',
                'is_active': True,
            },
            {
                'name': 'Indeed',
                'base_url': 'https://indeed.com',
                'is_active': True,
            },
            {
                'name': 'Glassdoor',
                'base_url': 'https://glassdoor.com/jobs',
                'is_active': True,
            }
        ]

        for source_data in sources_data:
            source, created = JobSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            if created:
                self.stdout.write(f'Created job source: {source.name}')

        # Get the sources for job listings
        linkedin = JobSource.objects.get(name='LinkedIn')
        indeed = JobSource.objects.get(name='Indeed')
        glassdoor = JobSource.objects.get(name='Glassdoor')

        # Sample job listings
        jobs_data = [
            {
                'title': 'Senior Full Stack Developer',
                'company_name': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'description': 'We are looking for a senior full stack developer to join our team. Experience with React, Node.js, and Python required.',
                'salary_min': 120000,
                'salary_max': 180000,
                'employment_type': 'full_time',
                'experience_level': 'senior',
                'source_url': 'https://linkedin.com/jobs/123456',
                'source': linkedin,
            },
            {
                'title': 'Frontend Developer',
                'company_name': 'StartupXYZ',
                'location': 'New York, NY',
                'description': 'Join our growing startup as a frontend developer. React and TypeScript experience preferred.',
                'salary_min': 80000,
                'salary_max': 120000,
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'source_url': 'https://indeed.com/jobs/234567',
                'source': indeed,
            },
            {
                'title': 'Python Backend Developer',
                'company_name': 'DataSolutions LLC',
                'location': 'Austin, TX',
                'description': 'Backend developer position focusing on Python/Django development. Experience with APIs and databases required.',
                'salary_min': 90000,
                'salary_max': 140000,
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'source_url': 'https://glassdoor.com/jobs/345678',
                'source': glassdoor,
            },
            {
                'title': 'DevOps Engineer',
                'company_name': 'CloudTech Solutions',
                'location': 'Seattle, WA',
                'description': 'DevOps engineer to manage our cloud infrastructure. AWS, Docker, and Kubernetes experience required.',
                'salary_min': 110000,
                'salary_max': 160000,
                'employment_type': 'full_time',
                'experience_level': 'senior',
                'source_url': 'https://linkedin.com/jobs/456789',
                'source': linkedin,
            },
            {
                'title': 'Junior Software Engineer',
                'company_name': 'Innovation Labs',
                'location': 'Boston, MA',
                'description': 'Entry-level position for recent graduates. Training provided for JavaScript, Python, and cloud technologies.',
                'salary_min': 65000,
                'salary_max': 85000,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'source_url': 'https://indeed.com/jobs/567890',
                'source': indeed,
            },
            {
                'title': 'Product Manager',
                'company_name': 'MegaCorp',
                'location': 'Los Angeles, CA',
                'description': 'Product manager for our consumer-facing applications. Experience with agile methodologies required.',
                'salary_min': 130000,
                'salary_max': 200000,
                'employment_type': 'full_time',
                'experience_level': 'senior',
                'source_url': 'https://glassdoor.com/jobs/678901',
                'source': glassdoor,
            },
            {
                'title': 'UI/UX Designer',
                'company_name': 'Design Studio Pro',
                'location': 'Denver, CO',
                'description': 'Creative UI/UX designer to work on web and mobile applications. Figma and Adobe Creative Suite experience required.',
                'salary_min': 70000,
                'salary_max': 100000,
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'source_url': 'https://linkedin.com/jobs/789012',
                'source': linkedin,
            },
            {
                'title': 'Data Scientist',
                'company_name': 'Analytics Corp',
                'location': 'Chicago, IL',
                'description': 'Data scientist position focusing on machine learning and predictive analytics. Python, R, and SQL experience required.',
                'salary_min': 100000,
                'salary_max': 150000,
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'source_url': 'https://indeed.com/jobs/890123',
                'source': indeed,
            },
            {
                'title': 'Marketing Coordinator',
                'company_name': 'BrandForward',
                'location': 'Miami, FL',
                'description': 'Entry-level marketing position. Social media and content creation experience preferred.',
                'salary_min': 45000,
                'salary_max': 60000,
                'employment_type': 'full_time',
                'experience_level': 'junior',
                'source_url': 'https://glassdoor.com/jobs/901234',
                'source': glassdoor,
            },
            {
                'title': 'Remote Software Developer',
                'company_name': 'RemoteFirst Tech',
                'location': 'Remote',
                'description': 'Fully remote position for experienced developers. Flexible schedule and great benefits.',
                'salary_min': 95000,
                'salary_max': 135000,
                'employment_type': 'full_time',
                'experience_level': 'mid',
                'source_url': 'https://linkedin.com/jobs/012345',
                'source': linkedin,
            }
        ]

        for job_data in jobs_data:
            job, created = JobListing.objects.get_or_create(
                title=job_data['title'],
                company_name=job_data['company_name'],
                defaults=job_data
            )
            if created:
                self.stdout.write(f'Created job: {job.title} at {job.company_name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample job data!')
        )
