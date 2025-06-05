"""
Base automation engine for job application automation
"""
import time
import random
import logging
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from django.conf import settings
from django.utils import timezone
from .models import JobApplication, ApplicationFormField
from jobs.models import JobListing
import openai

logger = logging.getLogger('automation')


class BaseAutomator(ABC):
    """Base class for job board automation"""
    
    def __init__(self, user, session):
        self.user = user
        self.session = session
        self.browser = None
        self.page = None
        self.playwright = None
        
        # Configure OpenAI if available
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.ai_enabled = True
        else:
            self.ai_enabled = False
            logger.warning("OpenAI API key not configured. AI features disabled.")
    
    def __enter__(self):
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
    
    def start_browser(self):
        """Initialize browser session"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Create new page with user agent
            context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            self.page = context.new_page()
            
            # Set viewport
            self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info("Browser session started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            raise
    
    def close_browser(self):
        """Close browser session"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Browser session closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def take_screenshot(self, name="screenshot"):
        """Take screenshot for debugging"""
        try:
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            screenshot_path = f"logs/screenshots/{filename}"
            self.page.screenshot(path=screenshot_path)
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def wait_for_element(self, selector, timeout=10000):
        """Wait for element to be visible"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            logger.warning(f"Element not found: {selector}")
            return False
    
    def safe_click(self, selector, timeout=5000):
        """Safely click an element with error handling"""
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            if element:
                element.click()
                self.random_delay(0.5, 1.5)
                return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
        return False
    
    def safe_fill(self, selector, text, timeout=5000):
        """Safely fill an input field"""
        try:
            element = self.page.wait_for_selector(selector, timeout=timeout)
            if element:
                element.clear()
                element.fill(text)
                self.random_delay(0.5, 1.0)
                return True
        except Exception as e:
            logger.error(f"Failed to fill element {selector}: {str(e)}")
        return False
    
    def analyze_form_with_ai(self, form_html, job_context):
        """Use AI to analyze form fields and suggest answers"""
        if not self.ai_enabled:
            return {}
        
        try:
            prompt = f"""
            Analyze this job application form and suggest appropriate answers based on the user profile and job context.
            
            Job: {job_context.get('title', '')} at {job_context.get('company', '')}
            User Profile: {self.get_user_profile_summary()}
            
            Form HTML:
            {form_html}
            
            Please provide JSON responses for each form field with confidence scores.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI form analysis failed: {str(e)}")
            return {}
    
    def get_user_profile_summary(self):
        """Get a summary of user profile for AI context"""
        try:
            profile = self.user.profile
            return {
                'name': profile.full_name,
                'current_position': profile.current_position,
                'experience_years': profile.years_of_experience,
                'skills': profile.skills,
                'location': profile.location,
                'education': [str(edu) for edu in profile.education.all()[:2]],
                'experience': [str(exp) for exp in profile.experiences.all()[:3]]
            }
        except Exception as e:
            logger.error(f"Failed to get user profile summary: {str(e)}")
            return {}
    
    @abstractmethod
    def login(self):
        """Login to the job platform"""
        pass
    
    @abstractmethod
    def search_jobs(self, criteria):
        """Search for jobs based on criteria"""
        pass
    
    @abstractmethod
    def apply_to_job(self, job, application):
        """Apply to a specific job"""
        pass
    
    @abstractmethod
    def scrape_jobs(self, criteria):
        """Scrape job listings"""
        pass


class LinkedInAutomator(BaseAutomator):
    """LinkedIn-specific automation"""
    
    def __init__(self, user, session):
        super().__init__(user, session)
        self.base_url = "https://www.linkedin.com"
        self.logged_in = False
    
    def login(self):
        """Login to LinkedIn"""
        try:
            # Get credentials
            credentials = self.user.platform_credentials.filter(
                platform_name='LinkedIn',
                is_active=True
            ).first()
            
            if not credentials:
                raise ValueError("LinkedIn credentials not found")
            
            logger.info("Attempting LinkedIn login")
            
            # Navigate to login page
            self.page.goto(f"{self.base_url}/login")
            self.random_delay(2, 4)
            
            # Fill login form
            if self.safe_fill('input[name="session_key"]', credentials.username):
                if self.safe_fill('input[name="session_password"]', credentials.password_encrypted):  # Note: decrypt in production
                    if self.safe_click('button[type="submit"]'):
                        self.random_delay(3, 5)
                        
                        # Check if login was successful
                        if self.page.url.startswith(f"{self.base_url}/feed") or "challenge" not in self.page.url:
                            self.logged_in = True
                            logger.info("LinkedIn login successful")
                            return True
            
            logger.error("LinkedIn login failed")
            return False
            
        except Exception as e:
            logger.error(f"LinkedIn login error: {str(e)}")
            return False
    
    def search_jobs(self, criteria):
        """Search for jobs on LinkedIn"""
        try:
            if not self.logged_in and not self.login():
                raise ValueError("Failed to login to LinkedIn")
            
            # Navigate to jobs page
            self.page.goto(f"{self.base_url}/jobs/")
            self.random_delay(2, 3)
            
            # Build search query
            keywords = criteria.get('keywords', [])
            location = criteria.get('location', '')
            
            # Search for jobs
            if keywords:
                search_query = ' '.join(keywords)
                if self.safe_fill('input[aria-label="Search by title, skill, or company"]', search_query):
                    self.random_delay(1, 2)
            
            if location:
                if self.safe_fill('input[aria-label="City, state, or zip code"]', location):
                    self.random_delay(1, 2)
            
            # Submit search
            if self.safe_click('button[aria-label="Search"]'):
                self.random_delay(3, 5)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"LinkedIn job search error: {str(e)}")
            return False
    
    def apply_to_job(self, job, application):
        """Apply to a specific job on LinkedIn"""
        try:
            if not self.logged_in and not self.login():
                raise ValueError("Failed to login to LinkedIn")
            
            logger.info(f"Applying to {job.title} at {job.company_name}")
            
            # Navigate to job page
            self.page.goto(job.source_url)
            self.random_delay(2, 4)
            
            # Look for Easy Apply button
            easy_apply_selector = 'button[aria-label*="Easy Apply"]'
            if self.wait_for_element(easy_apply_selector, timeout=5000):
                if self.safe_click(easy_apply_selector):
                    return self._handle_easy_apply_flow(job, application)
            
            # Look for regular apply button
            apply_selector = 'a[data-control-name="jobdetails_topcard_inapply"]'
            if self.wait_for_element(apply_selector, timeout=5000):
                if self.safe_click(apply_selector):
                    return self._handle_external_apply(job, application)
            
            return {
                'success': False,
                'error': 'No apply button found',
                'logs': ['Navigate to job page', 'No apply options available']
            }
            
        except Exception as e:
            logger.error(f"LinkedIn job application error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'logs': [f'Error: {str(e)}']
            }
    
    def _handle_easy_apply_flow(self, job, application):
        """Handle LinkedIn Easy Apply flow"""
        logs = ['Started Easy Apply flow']
        
        try:
            # Wait for application modal
            if self.wait_for_element('.jobs-easy-apply-modal', timeout=10000):
                logs.append('Easy Apply modal opened')
                
                # Handle multi-step application
                max_steps = 5
                current_step = 0
                
                while current_step < max_steps:
                    current_step += 1
                    logs.append(f'Processing step {current_step}')
                    
                    # Check for form fields
                    form_fields = self.page.query_selector_all('input, select, textarea')
                    
                    for field in form_fields:
                        field_name = field.get_attribute('name') or ''
                        field_type = field.get_attribute('type') or field.tag_name
                        
                        # Fill field based on type and name
                        if 'phone' in field_name.lower():
                            field.fill(self.user.profile.phone_number or '')
                        elif 'cover' in field_name.lower() and field.tag_name == 'textarea':
                            field.fill(self._generate_cover_letter(job))
                        # Add more field handling logic
                    
                    self.random_delay(1, 2)
                    
                    # Look for Next button
                    next_button = self.page.query_selector('button[aria-label="Continue to next step"]')
                    if next_button:
                        next_button.click()
                        self.random_delay(2, 3)
                        continue
                    
                    # Look for Submit button
                    submit_button = self.page.query_selector('button[aria-label="Submit application"]')
                    if submit_button:
                        submit_button.click()
                        logs.append('Application submitted')
                        self.random_delay(2, 4)
                        
                        # Verify submission
                        if self.page.query_selector('.jobs-easy-apply-confirmation'):
                            return {
                                'success': True,
                                'message': 'Application submitted successfully',
                                'logs': logs
                            }
                    
                    break
                
            return {
                'success': False,
                'error': 'Failed to complete Easy Apply flow',
                'logs': logs
            }
            
        except Exception as e:
            logs.append(f'Error in Easy Apply: {str(e)}')
            return {
                'success': False,
                'error': str(e),
                'logs': logs
            }
    
    def _handle_external_apply(self, job, application):
        """Handle external application (opens in new tab)"""
        # For external applications, we can't automate fully
        # but we can track the attempt
        return {
            'success': False,
            'error': 'External application - manual action required',
            'logs': ['Redirected to external application page']
        }
    
    def _generate_cover_letter(self, job):
        """Generate cover letter for the job"""
        try:
            template = self.user.profile.cover_letter_template
            if not template:
                template = f"Dear Hiring Manager,\n\nI am interested in the {job.title} position at {job.company_name}."
            
            # Simple placeholder replacement
            cover_letter = template.replace('{job_title}', job.title)
            cover_letter = cover_letter.replace('{company_name}', job.company_name)
            cover_letter = cover_letter.replace('{user_name}', self.user.profile.full_name)
            
            return cover_letter
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {str(e)}")
            return f"I am interested in the {job.title} position at {job.company_name}."
    
    def scrape_jobs(self, criteria):
        """Scrape job listings from LinkedIn"""
        try:
            if not self.search_jobs(criteria):
                raise ValueError("Failed to perform job search")
            
            jobs = []
            max_pages = criteria.get('max_pages', 3)
            
            for page_num in range(max_pages):
                logger.info(f"Scraping page {page_num + 1}")
                
                # Wait for job listings to load
                if self.wait_for_element('.jobs-search-results-list', timeout=10000):
                    job_cards = self.page.query_selector_all('.job-search-card')
                    
                    for card in job_cards:
                        job_data = self._extract_job_data_from_card(card)
                        if job_data:
                            jobs.append(job_data)
                
                # Go to next page
                next_button = self.page.query_selector('button[aria-label="View next page"]')
                if next_button and not next_button.is_disabled():
                    next_button.click()
                    self.random_delay(3, 5)
                else:
                    break
            
            return {
                'jobs': jobs,
                'total_found': len(jobs),
                'pages_scraped': page_num + 1
            }
            
        except Exception as e:
            logger.error(f"LinkedIn job scraping error: {str(e)}")
            return {
                'jobs': [],
                'error': str(e)
            }
    
    def _extract_job_data_from_card(self, card):
        """Extract job data from a LinkedIn job card"""
        try:
            title_element = card.query_selector('.job-search-card__title a')
            company_element = card.query_selector('.job-search-card__subtitle a')
            location_element = card.query_selector('.job-search-card__location')
            
            if not (title_element and company_element):
                return None
            
            job_data = {
                'title': title_element.inner_text().strip(),
                'company_name': company_element.inner_text().strip(),
                'location': location_element.inner_text().strip() if location_element else '',
                'source_url': title_element.get_attribute('href'),
                'external_id': self._extract_job_id_from_url(title_element.get_attribute('href')),
                'source': 'LinkedIn'
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Failed to extract job data: {str(e)}")
            return None
    
    def _extract_job_id_from_url(self, url):
        """Extract job ID from LinkedIn URL"""
        try:
            import re
            match = re.search(r'/jobs/view/(\d+)', url)
            return match.group(1) if match else None
        except:
            return None


class IndeedAutomator(BaseAutomator):
    """Indeed-specific automation (placeholder)"""
    
    def __init__(self, user, session):
        super().__init__(user, session)
        self.base_url = "https://www.indeed.com"
    
    def login(self):
        """Indeed login implementation"""
        # Implement Indeed-specific login
        pass
    
    def search_jobs(self, criteria):
        """Indeed job search implementation"""
        # Implement Indeed-specific search
        pass
    
    def apply_to_job(self, job, application):
        """Indeed job application implementation"""
        # Implement Indeed-specific application
        pass
    
    def scrape_jobs(self, criteria):
        """Indeed job scraping implementation"""
        # Implement Indeed-specific scraping
        pass
