import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any


class FileUtils:
    """Utility class for file operations"""

    @staticmethod
    def load_json(file_path: Path, default: Any = None) -> Any:
        """Load JSON file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File {file_path} not found. Using default values.")
            return default or {}
        except json.JSONDecodeError:
            print(f"Error reading {file_path}. Using default values.")
            return default or {}

    @staticmethod
    def save_json(file_path: Path, data: Any, indent: int = 2):
        """Save data to JSON file with error handling"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving to {file_path}: {e}")
            raise

    @staticmethod
    def save_text(file_path: Path, content: str):
        """Save text content to file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)


class StringUtils:
    """Utility class for string operations"""

    @staticmethod
    def get_safe_filename(text: str) -> str:
        """Convert text to safe filename by removing/replacing unsafe characters"""
        safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()
        return safe_text.replace(' ', '_')

    @staticmethod
    def get_safe_company_name(company_name: str) -> str:
        """Convert company name to safe folder name"""
        return "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect if text is primarily French or English"""
        french_indicators = [
            'développement', 'stagiaire', 'entreprise', 'équipe', 'expérience',
            'compétences', 'université', 'français', 'poste', 'candidat'
        ]

        text_lower = text.lower()
        french_count = sum(1 for indicator in french_indicators if indicator in text_lower)

        return 'french' if french_count >= 2 else 'english'


class CacheUtils:
    """Utility class for cache operations"""

    @staticmethod
    def is_cache_fresh(cached_data: Dict, max_age_days: int = 730) -> bool:
        """Check if cached data is fresh (less than max_age_days old)"""
        if not cached_data or 'timestamp' not in cached_data:
            return False

        try:
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            return datetime.now() - cached_time < timedelta(days=max_age_days)
        except (ValueError, KeyError):
            return False

    @staticmethod
    def create_cache_entry(data: Any) -> Dict:
        """Create a cache entry with timestamp"""
        return {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }


class PathUtils:
    """Utility class for path operations"""

    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """Create directory if it doesn't exist and return path"""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def file_exists(path: Path) -> bool:
        """Check if file exists"""
        return path.exists() and path.is_file()
