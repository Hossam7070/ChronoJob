"""API endpoints for job management."""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.job import JobCreate, JobConfig
from app.storage.job_storage import (
    save_job,
    load_all_jobs,
    get_job,
    delete_job,
    job_exists,
)
from app.scheduler import scheduler_manager
from datetime import datetime


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/create", response_model=JobConfig, status_code=status.HTTP_201_CREATED)
async def create_job(job_data: JobCreate):
    """
    Create a new scheduled job.
    
    Args:
        job_data: Job configuration data
        
    Returns:
        Created job configuration
        
    Raises:
        HTTPException: If job name already exists
    """
    logger.info(f"API: Creating new job '{job_data.job_name}'")
    logger.debug(f"Job details: schedule={job_data.schedule_time}, source={job_data.data_source.source_type}")
    
    # Check if job already exists
    if job_exists(job_data.job_name):
        logger.warning(f"API: Job creation failed - job '{job_data.job_name}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with name '{job_data.job_name}' already exists"
        )
    
    try:
        # Create job configuration
        job_config = JobConfig(
            job_name=job_data.job_name,
            schedule_time=job_data.schedule_time,
            data_source=job_data.data_source,
            processing_script=job_data.processing_script,
            consumer_emails=job_data.consumer_emails,
            created_at=datetime.now(),
        )
        
        # Save to storage
        logger.debug(f"API: Saving job '{job_data.job_name}' to storage")
        save_job(job_config)
        
        # Schedule the job
        logger.debug(f"API: Scheduling job '{job_data.job_name}' with APScheduler")
        scheduler_manager.schedule_job(job_config)
        
        logger.info(f"API: Job '{job_data.job_name}' created successfully")
        return job_config
        
    except Exception as e:
        logger.error(f"API: Failed to create job '{job_data.job_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("", response_model=List[JobConfig])
async def list_jobs():
    """
    List all scheduled jobs.
    
    Returns:
        List of all job configurations
    """
    logger.info("API: Listing all jobs")
    try:
        jobs = load_all_jobs()
        logger.info(f"API: Retrieved {len(jobs)} job(s)")
        return jobs
    except Exception as e:
        logger.error(f"API: Failed to list jobs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


@router.get("/{job_name}", response_model=JobConfig)
async def get_job_details(job_name: str):
    """
    Get details of a specific job.
    
    Args:
        job_name: Unique job identifier
        
    Returns:
        Job configuration
        
    Raises:
        HTTPException: If job not found
    """
    logger.info(f"API: Retrieving job details for '{job_name}'")
    try:
        job = get_job(job_name)
        if job is None:
            logger.warning(f"API: Job '{job_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job '{job_name}' not found"
            )
        logger.info(f"API: Job '{job_name}' retrieved successfully")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to retrieve job '{job_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job: {str(e)}"
        )


@router.delete("/{job_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_endpoint(job_name: str):
    """
    Delete a scheduled job.
    
    Args:
        job_name: Unique job identifier
        
    Raises:
        HTTPException: If job not found
    """
    logger.info(f"API: Deleting job '{job_name}'")
    
    try:
        # Remove from scheduler
        logger.debug(f"API: Removing job '{job_name}' from scheduler")
        scheduler_manager.remove_job(job_name)
        
        # Delete from storage
        logger.debug(f"API: Deleting job '{job_name}' from storage")
        success = delete_job(job_name)
        
        if not success:
            logger.warning(f"API: Job '{job_name}' not found in storage")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job '{job_name}' not found"
            )
        
        logger.info(f"API: Job '{job_name}' deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to delete job '{job_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )
