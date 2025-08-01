#!/usr/bin/env python3
"""
Cover Letter Generator - Independent Module
Generates cover letters from existing job content files
"""

import asyncio
import os
import argparse
from pathlib import Path
from cover_letter_generator_killer import CoverLetterGenerator
from personal_context import PERSONAL_CONTEXT


class IndependentCoverLetterGenerator:
    def __init__(self, api_key=None):
        """Initialize the independent cover letter generator"""
        self.api_key = api_key or self.get_api_key()
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.generator = CoverLetterGenerator(self.api_key, PERSONAL_CONTEXT)

    def get_api_key(self):
        """Get OpenAI API key from environment or .env file"""
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key and Path('.env').exists():
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break

        return api_key

    async def generate_for_company(self, company_name, force=False):
        """Generate cover letter for a specific company"""
        job_postings = CoverLetterGenerator.load_jobs_from_processed_file("processed_jobs.json")

        target_job = None
        for job in job_postings:
            if job.company_name.lower() == company_name.lower():
                target_job = job
                break

        if not target_job:
            print(f"❌ No job found for company: {company_name}")
            available_companies = list(set(job.company_name for job in job_postings))
            print(f"📋 Available companies: {', '.join(sorted(available_companies))}")
            return None

        # Check if cover letter already exists
        if not force and self.generator.check_existing_cover_letter(target_job.company_name, target_job.job_id, target_job.job_title):
            print(f"⏭️  Cover letter already exists for {target_job.company_name} (Job ID: {target_job.job_id}). Use --force to regenerate.")
            return None

        result = await self.generator.generate_cover_letter(target_job)
        return result

    async def generate_for_job_id(self, job_id, force=False):
        """Generate cover letter for a specific job ID"""
        job_postings = CoverLetterGenerator.load_jobs_from_processed_file("processed_jobs.json")

        target_job = None
        for job in job_postings:
            if job.job_id == job_id:
                target_job = job
                break

        if not target_job:
            print(f"❌ No job found with ID: {job_id}")
            return None

        # Check if cover letter already exists
        if not force and self.generator.check_existing_cover_letter(target_job.company_name, target_job.job_id, target_job.job_title):
            print(f"⏭️  Cover letter already exists for {target_job.company_name} (Job ID: {job_id}). Use --force to regenerate.")
            return None

        result = await self.generator.generate_cover_letter(target_job)
        return result

    async def generate_all(self, force=False, max_letters=None):
        """Generate cover letters for all available jobs"""
        job_postings = CoverLetterGenerator.load_jobs_from_processed_file("processed_jobs.json")

        if not job_postings:
            print("❌ No job postings found")
            return []

        # Filter out jobs that already have cover letters (unless force=True)
        jobs_to_process = []
        skipped_count = 0

        for job in job_postings:
            if not force and self.generator.check_existing_cover_letter(job.company_name, job.job_id, job.job_title):
                skipped_count += 1
                print(f"⏭️  Skipping {job.company_name} - {job.job_title} - cover letter already exists")
            else:
                jobs_to_process.append(job)

        if skipped_count > 0:
            print(f"📊 Skipped {skipped_count} jobs with existing cover letters")

        if not jobs_to_process:
            print("✅ All jobs already have cover letters!")
            return []

        if max_letters is not None:
            jobs_to_process = jobs_to_process[:max_letters]

        print(f"🚀 Processing {len(jobs_to_process)} jobs...")
        results = await self.generator.process_job_batch(jobs_to_process)
        return results

    def list_available_jobs(self):
        """List all available jobs"""
        job_postings = CoverLetterGenerator.load_jobs_from_processed_file("processed_jobs.json")

        if not job_postings:
            print("❌ No job postings found")
            return

        print(f"\n📋 Available Jobs ({len(job_postings)} total):")
        print("-" * 80)

        for i, job in enumerate(job_postings, 1):
            has_cover_letter = self.generator.check_existing_cover_letter(job.company_name, job.job_id, job.job_title)
            status = "✅ Has cover letter" if has_cover_letter else "📝 Needs cover letter"

            print(f"{i:3d}. {job.company_name:<30} | {job.job_title:<40} | {status}")
            print(f"     Job ID: {job.job_id}")
            print()


async def main():
    parser = argparse.ArgumentParser(description="Generate cover letters from processed job data")
    parser.add_argument("--company", type=str, help="Generate cover letter for specific company")
    parser.add_argument("--job-id", type=str, help="Generate cover letter for specific job ID")
    parser.add_argument("--all", action="store_true", help="Generate cover letters for all jobs")
    parser.add_argument("--list", action="store_true", help="List all available jobs")
    parser.add_argument("--force", action="store_true", help="Force regenerate even if cover letter exists")
    parser.add_argument("--max", type=int, help="Maximum number of cover letters to generate (useful with --all)")

    args = parser.parse_args()

    try:
        generator = IndependentCoverLetterGenerator()

        if args.list:
            generator.list_available_jobs()
        elif args.company:
            result = await generator.generate_for_company(args.company, force=args.force)
            if result and result["success"]:
                print(f"✅ Successfully generated cover letter for {args.company}")
        elif args.job_id:
            result = await generator.generate_for_job_id(args.job_id, force=args.force)
            if result and result["success"]:
                print(f"✅ Successfully generated cover letter for job ID {args.job_id}")
        elif args.all:
            results = await generator.generate_all(force=args.force, max_letters=args.max)
            successful = sum(1 for r in results if r["success"])
            print(f"✅ Generated {successful}/{len(results)} cover letters successfully")
        else:
            print("Please specify --company, --job-id, --all, or --list")
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
