"""JSON-based job storage system for persisting job configurations."""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from app.models.job import JobConfig
from app.config import config


logger = logging.getLogger(__name__)

# Get storage path from configuration
STORAGE_FILE = Path(config.JOB_STORAGE_PATH)
STORAGE_DIR = STORAGE_FILE.parent


def _ensure_storage_directory() -> None:
    """Create data directory if it doesn't exist."""
    if not STORAGE_DIR.exists():
        logger.info(f"Creating storage directory: {STORAGE_DIR}")
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_storage_file() -> None:
    """Create jobs.json file if it doesn't exist."""
    _ensure_storage_directory()
    if not STORAGE_FILE.exists():
        logger.info(f"Creating storage file: {STORAGE_FILE}")
        STORAGE_FILE.write_text("[]")


def _read_jobs_file() -> List[dict]:
    """Read and parse the jobs.json file."""
    _ensure_storage_file()
    try:
        content = STORAGE_FILE.read_text()
        jobs = json.loads(content)
        logger.debug(f"Read {len(jobs)} job(s) from storage")
        return jobs
    except json.JSONDecodeError as e:
        # If file is corrupted, return empty list
        logger.error(f"Failed to parse jobs.json: {e}. Returning empty list.")
        return []


def _write_jobs_file(jobs: List[dict]) -> None:
    """Write jobs list to jobs.json file."""
    _ensure_storage_directory()
    logger.debug(f"Writing {len(jobs)} job(s) to storage")
    STORAGE_FILE.write_text(json.dumps(jobs, indent=2))


def save_job(job_config: JobConfig) -> None:
    """
    Persist a JobConfig to jobs.json.
    
    If a job with the same job_name exists, it will be updated.
    Otherwise, a new job will be added.
    
    Args:
        job_config: The job configuration to save
    """
    jobs = _read_jobs_file()
    
    # Convert JobConfig to dict
    job_dict = job_config.model_dump(mode='json')
    
    # Check if job already exists and update it
    job_exists_flag = False
    for i, job in enumerate(jobs):
        if job.get("job_name") == job_config.job_name:
            jobs[i] = job_dict
            job_exists_flag = True
            logger.info(f"Updated job '{job_config.job_name}' in storage")
            break
    
    # If job doesn't exist, append it
    if not job_exists_flag:
        jobs.append(job_dict)
        logger.info(f"Added new job '{job_config.job_name}' to storage")
    
    _write_jobs_file(jobs)


def load_all_jobs() -> List[JobConfig]:
    """
    Load all job configurations from storage.
    
    Returns:
        List of JobConfig objects
    """
    jobs = _read_jobs_file()
    
    job_configs = []
    for job_dict in jobs:
        try:
            # Parse datetime fields
            if 'created_at' in job_dict and isinstance(job_dict['created_at'], str):
                job_dict['created_at'] = datetime.fromisoformat(job_dict['created_at'])
            if 'last_run' in job_dict and job_dict['last_run'] and isinstance(job_dict['last_run'], str):
                job_dict['last_run'] = datetime.fromisoformat(job_dict['last_run'])
            
            job_config = JobConfig(**job_dict)
            job_configs.append(job_config)
        except Exception as e:
            # Skip invalid job configurations
            logger.warning(f"Failed to load job configuration: {e}")
            continue
    
    logger.info(f"Loaded {len(job_configs)} job(s) from storage")
    return job_configs


def get_job(job_name: str) -> Optional[JobConfig]:
    """
    Retrieve a specific job configuration by job_name.
    
    Args:
        job_name: The unique name of the job to retrieve
        
    Returns:
        JobConfig if found, None otherwise
    """
    jobs = load_all_jobs()
    
    for job in jobs:
        if job.job_name == job_name:
            return job
    
    return None


def delete_job(job_name: str) -> bool:
    """
    Remove a job from storage.
    
    Args:
        job_name: The unique name of the job to delete
        
    Returns:
        True if job was deleted, False if job was not found
    """
    jobs = _read_jobs_file()
    
    # Find and remove the job
    initial_length = len(jobs)
    jobs = [job for job in jobs if job.get("job_name") != job_name]
    
    if len(jobs) < initial_length:
        _write_jobs_file(jobs)
        logger.info(f"Deleted job '{job_name}' from storage")
        return True
    
    logger.warning(f"Job '{job_name}' not found in storage for deletion")
    return False


def job_exists(job_name: str) -> bool:
    """
    Check if a job with the given name exists in storage.
    
    Args:
        job_name: The unique name of the job to check
        
    Returns:
        True if job exists, False otherwise
    """
    jobs = _read_jobs_file()
    
    for job in jobs:
        if job.get("job_name") == job_name:
            return True
    
    return False
