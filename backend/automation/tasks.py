from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from .models import AutomationSession, JobApplication
from jobs.models import JobListing
from .automation_engine import LinkedInAutomator, IndeedAutomator
import logging

logger = logging.getLogger('automation')


@shared_task
def scrape_jobs_task(user_id, source_name, search_criteria):
    """
    Background task to scrape jobs from various sources
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Create automation session
        session = AutomationSession.objects.create(
            user=user,
            session_type='job_scraping',
            target_platform=source_name,
            automation_config=search_criteria,
            status='running',
            started_at=timezone.now()
        )
        
        logger.info(f"Starting job scraping session {session.session_id} for {source_name}")
        
        # Initialize appropriate scraper
        if source_name.lower() == 'linkedin':
            scraper = LinkedInAutomator(user, session)
        elif source_name.lower() == 'indeed':
            scraper = IndeedAutomator(user, session)
        else:
            raise ValueError(f"Unsupported job source: {source_name}")
        
        # Perform scraping
        results = scraper.scrape_jobs(search_criteria)
        
        # Update session with results
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.jobs_processed = len(results.get('jobs', []))
        session.results_summary = results
        session.save()
        
        logger.info(f"Completed job scraping session {session.session_id}. Found {session.jobs_processed} jobs")
        
        return {
            'session_id': str(session.session_id),
            'status': 'completed',
            'jobs_found': session.jobs_processed,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Job scraping task failed: {str(e)}")
        if 'session' in locals():
            session.status = 'failed'
            session.error_message = str(e)
            session.completed_at = timezone.now()
            session.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def apply_to_job_task(user_id, job_id, session_id=None):
    """
    Background task to automatically apply to a specific job
    """
    try:
        user = User.objects.get(id=user_id)
        job = JobListing.objects.get(id=job_id)
        
        # Get or create session
        if session_id:
            session = AutomationSession.objects.get(session_id=session_id)
        else:
            session = AutomationSession.objects.create(
                user=user,
                session_type='job_application',
                target_platform=job.source.name,
                status='running',
                started_at=timezone.now(),
                total_jobs_targeted=1
            )
        
        logger.info(f"Starting job application for {job.title} at {job.company_name}")
        
        # Create application record
        application = JobApplication.objects.create(
            user=user,
            job=job,
            session=session,
            is_automated=True,
            status='pending'
        )
        
        # Initialize appropriate automator
        if job.source.name.lower() == 'linkedin':
            automator = LinkedInAutomator(user, session)
        elif job.source.name.lower() == 'indeed':
            automator = IndeedAutomator(user, session)
        else:
            raise ValueError(f"Unsupported platform: {job.source.name}")
        
        # Perform application
        result = automator.apply_to_job(job, application)
        
        # Update application status
        if result.get('success'):
            application.status = 'submitted'
            application.applied_at = timezone.now()
            session.applications_submitted += 1
        else:
            application.status = 'failed'
            application.error_details = result.get('error', 'Unknown error')
            session.applications_failed += 1
        
        application.automation_logs = result.get('logs', [])
        application.save()
        
        # Update session progress
        session.jobs_processed += 1
        if session.jobs_processed >= session.total_jobs_targeted:
            session.status = 'completed'
            session.completed_at = timezone.now()
        session.save()
        
        logger.info(f"Job application completed. Status: {application.status}")
        
        return {
            'application_id': str(application.application_id),
            'status': application.status,
            'success': result.get('success', False),
            'message': result.get('message', '')
        }
        
    except Exception as e:
        logger.error(f"Job application task failed: {str(e)}")
        if 'application' in locals():
            application.status = 'failed'
            application.error_details = str(e)
            application.save()
        
        if 'session' in locals():
            session.applications_failed += 1
            session.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def bulk_apply_task(user_id, job_ids, automation_config):
    """
    Background task to apply to multiple jobs in bulk
    """
    try:
        user = User.objects.get(id=user_id)
        jobs = JobListing.objects.filter(id__in=job_ids)
        
        # Create automation session
        session = AutomationSession.objects.create(
            user=user,
            session_type='job_application',
            target_platform='multiple',
            automation_config=automation_config,
            status='running',
            started_at=timezone.now(),
            total_jobs_targeted=len(jobs)
        )
        
        logger.info(f"Starting bulk application session {session.session_id} for {len(jobs)} jobs")
        
        results = []
        
        # Apply to each job
        for job in jobs:
            try:
                result = apply_to_job_task.delay(user_id, job.id, str(session.session_id))
                results.append({
                    'job_id': job.id,
                    'job_title': job.title,
                    'company': job.company_name,
                    'result': result.get()
                })
                
                # Add delay between applications to avoid being flagged
                import time
                time.sleep(automation_config.get('delay_between_applications', 30))
                
            except Exception as e:
                logger.error(f"Failed to apply to job {job.id}: {str(e)}")
                results.append({
                    'job_id': job.id,
                    'job_title': job.title,
                    'company': job.company_name,
                    'result': {'status': 'failed', 'error': str(e)}
                })
        
        # Update session
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.results_summary = {'applications': results}
        session.save()
        
        logger.info(f"Bulk application session completed. Applied to {session.applications_submitted} jobs")
        
        return {
            'session_id': str(session.session_id),
            'status': 'completed',
            'total_jobs': len(jobs),
            'successful_applications': session.applications_submitted,
            'failed_applications': session.applications_failed,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Bulk apply task failed: {str(e)}")
        if 'session' in locals():
            session.status = 'failed'
            session.error_message = str(e)
            session.completed_at = timezone.now()
            session.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def cleanup_old_sessions():
    """
    Periodic task to cleanup old automation sessions
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    old_sessions = AutomationSession.objects.filter(created_at__lt=cutoff_date)
    
    count = old_sessions.count()
    old_sessions.delete()
    
    logger.info(f"Cleaned up {count} old automation sessions")
    return f"Cleaned up {count} sessions"


@shared_task
def send_job_alerts():
    """
    Periodic task to send job alerts to users
    """
    from jobs.models import JobAlert
    from django.core.mail import send_mail
    
    active_alerts = JobAlert.objects.filter(is_active=True)
    
    for alert in active_alerts:
        try:
            # Check if it's time to send the alert
            if alert.should_send_now():
                # Find matching jobs
                matching_jobs = alert.find_matching_jobs()
                
                if matching_jobs.exists():
                    # Send email notification
                    send_mail(
                        subject=f"New jobs matching '{alert.name}'",
                        message=f"Found {matching_jobs.count()} new jobs matching your criteria.",
                        from_email='noreply@hopeforjob.com',
                        recipient_list=[alert.user.email],
                        fail_silently=False,
                    )
                    
                    alert.last_sent = timezone.now()
                    alert.save()
                    
                    logger.info(f"Sent job alert to {alert.user.email} with {matching_jobs.count()} jobs")
                    
        except Exception as e:
            logger.error(f"Failed to send job alert for user {alert.user.id}: {str(e)}")
    
    return "Job alerts processed"
