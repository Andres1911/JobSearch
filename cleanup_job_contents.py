#!/usr/bin/env python3
"""
Cleanup script to remove generic job_description.md files from company folders
and keep only the properly named job description files
"""

import os
from pathlib import Path


def cleanup_job_contents():
    """Remove generic job_description.md files from company folders"""
    job_contents_dir = Path("./job_contents")

    if not job_contents_dir.exists():
        print("❌ job_contents directory not found")
        return

    removed_count = 0
    companies_cleaned = []

    # Iterate through all company folders
    for company_folder in job_contents_dir.iterdir():
        if company_folder.is_dir():
            generic_file = company_folder / "job_description.md"

            if generic_file.exists():
                # Check if there are properly named job description files
                proper_files = list(company_folder.glob("*_job_description.md"))

                if proper_files:
                    print(f"🗑️  Removing generic file from {company_folder.name}")
                    print(f"   Keeping {len(proper_files)} properly named files:")
                    for file in proper_files:
                        print(f"     - {file.name}")

                    # Remove the generic file
                    generic_file.unlink()
                    removed_count += 1
                    companies_cleaned.append(company_folder.name)
                else:
                    print(f"⚠️  {company_folder.name} only has generic file, keeping it for now")

    print(f"\n📊 Cleanup Summary:")
    print(f"   🗑️  Removed {removed_count} generic job_description.md files")
    print(f"   🏢 Companies cleaned: {len(companies_cleaned)}")

    if companies_cleaned:
        print(f"   📋 Cleaned companies: {', '.join(sorted(companies_cleaned))}")


def cleanup_empty_folders():
    """Remove empty company folders"""
    job_contents_dir = Path("./job_contents")
    removed_folders = []

    for company_folder in job_contents_dir.iterdir():
        if company_folder.is_dir():
            # Check if folder is empty or only contains hidden files
            contents = list(company_folder.iterdir())
            if not contents:
                print(f"🗂️  Removing empty folder: {company_folder.name}")
                company_folder.rmdir()
                removed_folders.append(company_folder.name)

    if removed_folders:
        print(f"🗂️  Removed {len(removed_folders)} empty folders: {', '.join(sorted(removed_folders))}")


def main():
    """Main cleanup function"""
    print("🧹 Starting job_contents cleanup...")
    print("=" * 60)

    cleanup_job_contents()
    print()
    cleanup_empty_folders()

    print("\n✅ Cleanup completed!")


if __name__ == "__main__":
    main()
