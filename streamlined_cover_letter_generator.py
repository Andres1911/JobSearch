from openai import AsyncOpenAI
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from personal_context import PERSONAL_CONTEXT, PersonalContext
from prompts_new import COMPANY_RESEARCH_PROMPT, COVER_LETTER_GENERATION_PROMPT_ENGLISH, COVER_LETTER_GENERATION_PROMPT_FRENCH
from shared_utils import FileUtils, StringUtils, CacheUtils, PathUtils

@dataclass
class JobPosting:
    company_name: str
    job_title: str
    job_description: str
    job_id: str
    link: Optional[str] = None

class CoverLetterGenerator:
    def __init__(self, openai_api_key: str, personal_context: PersonalContext, config_file="user_config.json"):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.personal_context = personal_context

        # Load user configuration using shared utility
        self.config = FileUtils.load_json(Path(config_file), {})

        # Directory paths
        self.job_contents_dir = Path("./job_contents")
        self.company_research_cache = Path("./company_research_cache.json")

        # Professional contact information from config
        personal_info = self.config.get('personal_info', {})
        self.contact_info = {
            "name": personal_info.get('name', 'Your Name'),
            "email": personal_info.get('email', 'your.email@example.com'),
            "phone": personal_info.get('phone', '(000) 000-0000'),
            "linkedin": personal_info.get('linkedin', 'linkedin.com/in/yourprofile')
        }

    def check_existing_cover_letter(self, company_name: str, job_id: str, job_title: str = None) -> bool:
        """Check if a cover letter already exists for this job"""
        company_folder = self.get_company_folder(company_name)

        # Check for position-specific files if job_title is provided
        if job_title:
            safe_title = StringUtils.get_safe_filename(job_title)
            for ext in ['pdf', 'docx']:
                if PathUtils.file_exists(company_folder / f"{safe_title}_cover_letter.{ext}"):
                    return True

        # Fallback: check for generic files (backward compatibility)
        for ext in ['pdf', 'docx']:
            if PathUtils.file_exists(company_folder / f"cover_letter.{ext}"):
                return True

        return False

    def get_company_folder(self, company_name: str) -> Path:
        """Get the company folder path, create if it doesn't exist"""
        safe_name = StringUtils.get_safe_company_name(company_name)
        return PathUtils.ensure_dir(self.job_contents_dir / safe_name)

    def save_job_description(self, company_folder: Path, job_posting: JobPosting):
        """Save job description to company folder"""
        safe_title = StringUtils.get_safe_filename(job_posting.job_title)
        job_desc_file = company_folder / f"{safe_title}_job_description.md"

        content = f"""# {job_posting.job_title}

**Company:** {job_posting.company_name}
**Job ID:** {job_posting.job_id}
{f"**Link:** {job_posting.link}" if job_posting.link else ""}

## Job Description

{job_posting.job_description}"""

        FileUtils.save_text(job_desc_file, content)

    def save_research_results(self, company_folder: Path, company_name: str, research_data: dict):
        """Save research results to company folder"""
        research_file = company_folder / f"Research_{StringUtils.get_safe_company_name(company_name)}.json"
        FileUtils.save_json(research_file, CacheUtils.create_cache_entry(research_data))

    def load_company_research_cache(self) -> Dict:
        """Load cached company research results"""
        return FileUtils.load_json(self.company_research_cache, {})

    def save_company_research_cache(self, cache: Dict):
        """Save company research results to cache"""
        try:
            print(f"💾 Saving company research cache to: {self.company_research_cache}")
            FileUtils.save_json(self.company_research_cache, cache)
            print(f"✅ Successfully saved cache with {len(cache)} companies")
        except Exception as e:
            print(f"❌ Error saving company research cache: {e}")
            print(f"   Cache path: {self.company_research_cache}")
            print(f"   Cache data keys: {list(cache.keys()) if cache else 'None'}")
            raise

    def is_research_fresh(self, cached_data: Dict) -> bool:
        """Check if cached research is less than 2 years old"""
        return CacheUtils.is_cache_fresh(cached_data, max_age_days=730)

    def load_job_description(self, company_name: str, job_title: str, job_id: str) -> Optional[str]:
        """Load job description from company folder"""
        try:
            company_folder = self.get_company_folder(company_name)
            safe_title = StringUtils.get_safe_filename(job_title)
            job_desc_file = company_folder / f"{safe_title}_job_description.md"

            # Try multiple fallback locations for backward compatibility
            fallback_files = [
                company_folder / f"Job_Description_{job_id}.md",
                company_folder / "job_description.md",
                self.job_contents_dir / f"{safe_title}_{job_id}.md"
            ]

            if not PathUtils.file_exists(job_desc_file):
                for fallback in fallback_files:
                    if PathUtils.file_exists(fallback):
                        job_desc_file = fallback
                        break
                else:
                    print(f"⚠️ Job description file not found for {company_name} - {job_title}")
                    return None

            with open(job_desc_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract job description content
            description_match = re.search(r'## Job Description\s*\n\n(.*)', content, re.DOTALL)
            if description_match:
                return description_match.group(1).strip()

            # Fallback: return content after the first few metadata lines
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('## Job Description') or (i > 5 and line.strip()):
                    return '\n'.join(lines[i+1:]).strip()

            return content.strip()

        except Exception as e:
            print(f"❌ Error loading job description: {e}")
            return None

    def detect_language(self, text: str) -> str:
        """Detect if text is primarily French or English"""
        return StringUtils.detect_language(text)

    # Continue with the rest of the methods from the original file...
    # This is just the beginning of the streamlined version
