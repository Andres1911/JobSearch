#!/usr/bin/env python3
"""
LinkedIn Job Scraper - Independent Module
Scrapes job postings from LinkedIn and saves to processed_jobs.json
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


class LinkedInJobScraper:
    def __init__(self, config_file="user_config.json"):
        """Initialize the LinkedIn job scraper"""
        self.config = self.load_config(config_file)
        self.driver = None
        self.processed_jobs_file = "processed_jobs.json"
        self.cookies_file = Path("cookies/linkedin_cookies.pkl")

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found")
            return {}

    def should_filter_job(self, job_title: str) -> bool:
        """Check if job should be filtered based on reject keywords"""
        title_lower = job_title.lower()
        reject_keywords = self.config.get('filtering', {}).get('reject_keywords', [])

        for keyword in reject_keywords:
            if keyword.lower() in title_lower:
                return True
        return False

    def meets_requirements(self, job_title: str) -> bool:
        """Check if job meets requirement keywords"""
        title_lower = job_title.lower()
        require_keywords = self.config.get('filtering', {}).get('require_keywords', [])

        # If no requirements specified, accept all
        if not require_keywords:
            return True

        # Check if at least one requirement keyword is present
        for keyword in require_keywords:
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

    def scrape_job_listings(self, search_params):
        """Scrape job listings based on search parameters"""
        print(f"🔍 Scraping jobs with params: {search_params}")

        # Navigate to LinkedIn jobs page first
        self.driver.get("https://www.linkedin.com/jobs/")
        time.sleep(3)

        # Enter keywords in search box and press enter
        if 'keywords' in search_params:
            try:
                # Find the keyword search box
                keyword_box = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label*='Search by title'], input[placeholder*='Search by title'], .jobs-search-box__text-input")
                keyword_box.clear()
                keyword_box.send_keys(search_params['keywords'].replace('+', ' '))
                print(f"🔤 Entered keywords: {search_params['keywords']}")

                # Press Enter to search
                from selenium.webdriver.common.keys import Keys
                keyword_box.send_keys(Keys.RETURN)
                time.sleep(4)  # Wait for results to load

            except Exception as e:
                print(f"⚠️ Could not enter keywords, falling back to URL method: {e}")
                # Fallback to URL method
                self._search_by_url(search_params)
        else:
            # No keywords, use URL method
            self._search_by_url(search_params)

        jobs = {}
        page = 1
        max_pages = search_params.get('max_pages', 5)

        while page <= max_pages:
            print(f"📄 Scraping page {page}/{max_pages}")

            # Scroll to load more job cards
            print("📜 Scrolling to load job cards...")
            self._scroll_to_load_jobs()

            # Wait for job cards to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-job-id]"))
                )
            except TimeoutException:
                print("⚠️ No job cards found on this page")
                break

            # Get job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[data-job-id]")
            print(f"Found {len(job_cards)} job cards on page {page}")

            for card in job_cards:
                try:
                    job_id = card.get_attribute("data-job-id")
                    if not job_id:
                        continue

                    # Extract job title
                    title_element = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title a")
                    job_title = title_element.text.strip()
                    job_link = title_element.get_attribute("href")

                    # Filter out positions based on config
                    if self.should_filter_job(job_title):
                        print(f"🚫 Filtered out by config: {job_title}")
                        continue

                    # Extract company name
                    company_element = card.find_element(By.CSS_SELECTOR, "h4.base-search-card__subtitle a")
                    company_name = company_element.text.strip()

                    # Extract location
                    try:
                        location_element = card.find_element(By.CSS_SELECTOR, "span.job-search-card__location")
                        location = location_element.text.strip()
                    except NoSuchElementException:
                        location = "N/A"

                    # Extract posted time
                    try:
                        time_element = card.find_element(By.CSS_SELECTOR, "time")
                        posted_time = time_element.get_attribute("datetime")
                    except NoSuchElementException:
                        posted_time = "N/A"

                    jobs[job_id] = {
                        "job_title": job_title,
                        "company": company_name,
                        "location": location,
                        "link": job_link,
                        "posted_time": posted_time,
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }

                    print(f"✅ Scraped: {job_title} at {company_name}")

                except Exception as e:
                    print(f"⚠️ Error scraping job card: {e}")
                    continue

            # Try to go to next page
            if not self._go_to_next_page():
                break

            page += 1
            time.sleep(3)

        return jobs

    def _search_by_url(self, search_params):
        """Fallback method to search using URL parameters"""
        base_url = "https://www.linkedin.com/jobs/search/?"
        params = []

        if 'keywords' in search_params:
            params.append(f"keywords={search_params['keywords']}")
        if 'location' in search_params:
            params.append(f"location={search_params['location']}")
        if 'experience_level' in search_params:
            params.append(f"f_E={search_params['experience_level']}")
        if 'job_type' in search_params:
            params.append(f"f_JT={search_params['job_type']}")

        search_url = base_url + "&".join(params)
        print(f"🌐 Search URL: {search_url}")

        self.driver.get(search_url)
        time.sleep(3)

    def _scroll_to_load_jobs(self):
        """Scroll the page to trigger loading of more job cards"""
        # Scroll down gradually to load more jobs
        for i in range(3):
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll back up a bit
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(1)

            # Scroll down again
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    def _go_to_next_page(self):
        """Navigate to the next page of results"""
        try:
            # Look for next page button with multiple selectors
            next_selectors = [
                "button[aria-label='View next page']",
                "button[aria-label*='Next']",
                ".artdeco-pagination__button--next",
                ".jobs-search-results-list__pagination button:last-child"
            ]

            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled() and next_button.is_displayed():
                        print("📄 Going to next page...")
                        self.driver.execute_script("arguments[0].click();", next_button)
                        return True
                except NoSuchElementException:
                    continue

            print("📄 No more pages available")
            return False

        except Exception as e:
            print(f"⚠️ Error navigating to next page: {e}")
            return False

    def save_processed_jobs(self, jobs):
        """Save jobs to processed_jobs.json"""
        try:
            # Load existing jobs if file exists
            existing_jobs = {}
            if Path(self.processed_jobs_file).exists():
                with open(self.processed_jobs_file, 'r', encoding='utf-8') as f:
                    existing_jobs = json.load(f)

            # Merge with new jobs (new jobs override existing ones)
            existing_jobs.update(jobs)

            # Save updated jobs
            with open(self.processed_jobs_file, 'w', encoding='utf-8') as f:
                json.dump(existing_jobs, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved {len(jobs)} new jobs to {self.processed_jobs_file}")
            print(f"📊 Total jobs in database: {len(existing_jobs)}")

        except Exception as e:
            print(f"❌ Error saving jobs: {e}")

    def run_scraping(self):
        """Main scraping workflow"""
        try:
            print("🚀 Starting LinkedIn Job Scraper")

            # Setup
            self.setup_driver()
            self.driver.get("https://www.linkedin.com")

            # Load cookies and login if needed
            self.load_cookies()
            self.login_if_needed()

            # Get search parameters from config
            search_params = self.config.get('job_search', {})
            if not search_params:
                print("❌ No job search parameters found in user_config.json")
                return

            # Scrape jobs
            jobs = self.scrape_job_listings(search_params)

            if jobs:
                self.save_processed_jobs(jobs)
                print(f"🎉 Successfully scraped {len(jobs)} jobs!")
            else:
                print("⚠️ No jobs found")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")

        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main function to run the job scraper"""
    scraper = LinkedInJobScraper()
    scraper.run_scraping()


if __name__ == "__main__":
    main()
