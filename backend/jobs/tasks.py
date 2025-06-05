from celery import shared_task
from .models import JobListing, JobSource
import logging

logger = logging.getLogger('jobs')


@shared_task
def scrape_jobs_task(source_name, search_query='', location=''):
    """
    Background task to scrape jobs from various sources
    """
    try:
        # Get or create job source
        source, created = JobSource.objects.get_or_create(
            name=source_name,
            defaults={'url': f'https://{source_name}.com', 'is_active': True}
        )
        
        # Import automation engine
        from automation.automation_engine import LinkedInAutomator
        
        if source_name.lower() == 'linkedin':
            automator = LinkedInAutomator()
            jobs = automator.search_jobs(search_query, location)
            
            created_count = 0
            for job_data in jobs:
                job, created = JobListing.objects.get_or_create(
                    external_id=job_data.get('id'),
                    source=source,
                    defaults={
                        'title': job_data.get('title', ''),
                        'company': job_data.get('company', ''),
                        'location': job_data.get('location', ''),
                        'description': job_data.get('description', ''),
                        'url': job_data.get('url', ''),
                        'job_type': job_data.get('job_type', 'full_time'),
                        'experience_level': job_data.get('experience_level', 'entry')
                    }
                )
                if created:
                    created_count += 1
            
            logger.info(f"Scraped {created_count} new jobs from {source_name}")
            return f"Successfully scraped {created_count} new jobs"
        
        else:
            logger.warning(f"Scraping not implemented for source: {source_name}")
            return f"Scraping not implemented for {source_name}"
            
    except Exception as e:
        logger.error(f"Error scraping jobs from {source_name}: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def check_job_alerts():
    """
    Check job alerts and notify users of new matching jobs
    """
    from .models import JobAlert
    
    active_alerts = JobAlert.objects.filter(is_active=True)
    
    for alert in active_alerts:
        # Simple implementation - check for new jobs matching alert criteria
        new_jobs = JobListing.objects.filter(
            title__icontains=alert.keywords,
            location__icontains=alert.location,
            created_at__gt=alert.last_triggered or alert.created_at
        )
        
        if new_jobs.exists():
            # Update last triggered
            alert.last_triggered = timezone.now()
            alert.save()
            
            # Here you would send notification (email, push, etc.)
            logger.info(f"Found {new_jobs.count()} new jobs for alert {alert.id}")
    
    return f"Processed {active_alerts.count()} job alerts"


@shared_task
def cleanup_old_jobs():
    """
    Clean up old job listings that are no longer relevant
    """
    from datetime import timedelta
    from django.utils import timezone
    
    # Delete jobs older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    old_jobs = JobListing.objects.filter(created_at__lt=cutoff_date)
    count = old_jobs.count()
    old_jobs.delete()
    
    logger.info(f"Cleaned up {count} old job listings")
    return f"Cleaned up {count} old job listings"
