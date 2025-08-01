#!/usr/bin/env python3
"""
Job Content Scraper - Independent Module
Scrapes detailed job descriptions from processed_jobs.json and saves to job_contents/
"""

import json
import time
import pickle
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class JobContentScraper:
    def __init__(self, config_file="user_config.json"):
        """Initialize the job content scraper"""
        self.driver = None
        self.processed_jobs_file = "processed_jobs.json"
        self.job_contents_dir = Path("./job_contents")
        self.cookies_file = Path("cookies/linkedin_cookies.pkl")
        self.job_contents_dir.mkdir(exist_ok=True)
        self.config = self.load_config(config_file)

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found, using defaults")
            return {}
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {}

    def should_filter_job(self, job_title: str) -> bool:
        """Check if job should be filtered based on reject keywords"""
        title_lower = job_title.lower()
        reject_keywords = self.config.get('filtering', {}).get('reject_keywords', [])

        for keyword in reject_keywords:
            if keyword.lower() in title_lower:
                return True
        return False

    def setup_driver(self):
        """Set up Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def load_cookies(self):
        """Load LinkedIn cookies if they exist"""
        if self.cookies_file.exists():
            try:
                with open(self.cookies_file, 'rb') as f:
                    cookies = pickle.load(f)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                print("✅ Loaded existing LinkedIn cookies")
                return True
            except Exception as e:
                print(f"⚠️ Could not load cookies: {e}")
        return False

    def save_cookies(self):
        """Save LinkedIn cookies for future use"""
        try:
            self.cookies_file.parent.mkdir(exist_ok=True)
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            print("✅ Saved LinkedIn cookies")
        except Exception as e:
            print(f"⚠️ Could not save cookies: {e}")

    def login_if_needed(self):
        """Check if login is needed and prompt user"""
        self.driver.get("https://www.linkedin.com/feed/")
        time.sleep(3)

        # Check if we're on login page
        if "login" in self.driver.current_url or "challenge" in self.driver.current_url:
            print("🔐 Please log in to LinkedIn manually in the browser window...")
            print("✋ Press Enter here after you've successfully logged in...")
            input()
            self.save_cookies()
        else:
            print("✅ Already logged in to LinkedIn")

    def load_processed_jobs(self):
        """Load jobs from processed_jobs.json"""
        try:
            if not Path(self.processed_jobs_file).exists():
                print(f"❌ {self.processed_jobs_file} not found")
                return {}

            with open(self.processed_jobs_file, 'r', encoding='utf-8') as f:
                jobs = json.load(f)

            print(f"📂 Loaded {len(jobs)} jobs from {self.processed_jobs_file}")
            return jobs

        except Exception as e:
            print(f"❌ Error loading processed jobs: {e}")
            return {}

    @staticmethod
    def get_safe_company_name(company_name: str) -> str:
        """Convert company name to safe folder name"""
        return "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')

    @staticmethod
    def get_safe_filename(text: str) -> str:
        """Convert text to safe filename by removing/replacing unsafe characters"""
        # Replace spaces with underscores and remove unsafe characters
        safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()
        return safe_text.replace(' ', '_')

    def get_company_folder(self, company_name: str) -> Path:
        """Get the company folder path, create if it doesn't exist"""
        safe_name = self.get_safe_company_name(company_name)
        company_folder = self.job_contents_dir / safe_name
        company_folder.mkdir(parents=True, exist_ok=True)
        return company_folder

    def job_content_exists(self, company_name: str, job_title: str, job_id: str):
        """Check if job content already exists using new organized structure"""
        # First check new structure with job title
        company_folder = self.get_company_folder(company_name)
        safe_title = self.get_safe_filename(job_title)
        new_filepath = company_folder / f"{safe_title}_job_description.md"

        if new_filepath.exists():
            return True

        # Fallback: check old structure
        safe_title_old = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).strip()
        old_filepath = self.job_contents_dir / f"{safe_title_old}_{job_id}.md"

        return old_filepath.exists()

    def scrape_job_content(self, job_data, job_id):
        """Scrape detailed job content from LinkedIn"""
        try:
            job_url = job_data.get('link')
            if not job_url:
                print(f"⚠️ No URL found for job {job_id}")
                return None

            print(f"🔍 Scraping: {job_data['job_title']} at {job_data['company']}")

            # Navigate to job page
            self.driver.get(job_url)
            time.sleep(3)

            # Scroll down to load the full job description
            print("📜 Scrolling to load full job description...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll back up a bit and then down again to trigger loading
            self.driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Look for the "Show more" or "See more" button and click it if present
            try:
                show_more_selectors = [
                    "button[aria-label*='Show more']",
                    "button[aria-label*='See more']",
                    ".jobs-description__container button",
                    "[data-tracking-control-name='public_jobs_show-more-html-btn']"
                ]

                for selector in show_more_selectors:
                    try:
                        show_more_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if show_more_btn.is_displayed() and show_more_btn.is_enabled():
                            print("🔽 Clicking 'Show more' button...")
                            self.driver.execute_script("arguments[0].click();", show_more_btn)
                            time.sleep(2)
                            break
                    except NoSuchElementException:
                        continue
            except Exception as e:
                print(f"⚠️ Could not click show more button: {e}")

            # Wait for job details to load with multiple attempts
            job_description = ""
            max_attempts = 3

            for attempt in range(max_attempts):
                print(f"🔍 Attempt {attempt + 1}/{max_attempts} to find job description...")

                # Try the specific selector you mentioned first
                selectors = [
                    "div.jobs-box__html-content#job-details",
                    ".jobs-box__html-content",
                    ".jobs-description-content__text",
                    ".jobs-search__job-details .jobs-box__html-content",
                    ".jobs-description-content",
                    "[data-job-id] .jobs-description-content",
                    ".jobs-description__container",
                    "#job-details"
                ]

                for selector in selectors:
                    try:
                        # Wait for the element to be present
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )

                        desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        job_description = desc_element.text.strip()

                        if job_description and len(job_description) > 100:  # Ensure we got substantial content
                            print(f"✅ Found job description using selector: {selector}")
                            print(f"📝 Description length: {len(job_description)} characters")
                            break

                    except (NoSuchElementException, TimeoutException):
                        continue

                if job_description and len(job_description) > 100:
                    break

                # If we didn't find it, scroll more and wait
                if attempt < max_attempts - 1:
                    print("📜 Scrolling more to load content...")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)

            if not job_description or len(job_description) < 50:
                print("⚠️ Could not find substantial job description content")
                print(f"📊 Page source length: {len(self.driver.page_source)} characters")

                # Debug: Save page source for inspection
                debug_file = f"debug_page_{job_id}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"🐛 Saved page source to {debug_file} for debugging")

                return None

            # Format content
            content = f"""# {job_data['job_title']}

**Company:** {job_data['company']}

**Job ID:** {job_id}

**Link:** {job_url}

---

## Job Description

{job_description}
"""

            return content

        except Exception as e:
            print(f"❌ Error scraping job {job_id}: {e}")
            return None

    def save_job_content(self, content, company_name, job_title, job_id):
        """Save job content to markdown file"""
        try:
            company_folder = self.get_company_folder(company_name)
            safe_title = self.get_safe_filename(job_title)
            filepath = company_folder / f"{safe_title}_job_description.md"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Saved: {filepath}")
            return True

        except Exception as e:
            print(f"❌ Error saving job content: {e}")
            return False

    def run_content_scraping(self, max_jobs=None, skip_existing=True):
        """Main content scraping workflow"""
        try:
            print("🚀 Starting Job Content Scraper")

            # Load processed jobs
            jobs = self.load_processed_jobs()
            if not jobs:
                return

            # Setup driver
            self.setup_driver()
            self.driver.get("https://www.linkedin.com")

            # Load cookies and login if needed
            self.load_cookies()
            self.login_if_needed()

            # Process jobs
            processed_count = 0
            skipped_count = 0
            failed_count = 0
            filtered_count = 0

            for job_id, job_data in jobs.items():
                # Check if we've reached max jobs limit
                if max_jobs and processed_count >= max_jobs:
                    print(f"📊 Reached maximum jobs limit ({max_jobs})")
                    break

                # Filter out positions based on config (double-check)
                if self.should_filter_job(job_data['job_title']):
                    print(f"🚫 Filtered out by config: {job_data['job_title']}")
                    filtered_count += 1
                    continue

                # Skip if content already exists
                if skip_existing and self.job_content_exists(job_data['company'], job_data['job_title'], job_id):
                    print(f"⏭️ Skipping existing: {job_data['job_title']}")
                    skipped_count += 1
                    continue

                # Scrape job content
                content = self.scrape_job_content(job_data, job_id)

                if content:
                    if self.save_job_content(content, job_data['company'], job_data['job_title'], job_id):
                        processed_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1

                # Add delay between requests
                time.sleep(2)

            print(f"\n📊 Content Scraping Summary:")
            print(f"   ✅ Successfully processed: {processed_count}")
            print(f"   ⏭️ Skipped (already exist): {skipped_count}")
            print(f"   🚫 Filtered (Master/PhD): {filtered_count}")
            print(f"   ❌ Failed: {failed_count}")
            print(f"   📁 Content saved to: {self.job_contents_dir}")

        except Exception as e:
            print(f"❌ Error during content scraping: {e}")

        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main function to run the content scraper"""
    import argparse

    parser = argparse.ArgumentParser(description='Scrape detailed job content from LinkedIn')
    parser.add_argument('--max-jobs', type=int, help='Maximum number of jobs to process')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing job content files')

    args = parser.parse_args()

    scraper = JobContentScraper()
    scraper.run_content_scraping(
        max_jobs=args.max_jobs,
        skip_existing=not args.overwrite
    )


if __name__ == "__main__":
    main()
