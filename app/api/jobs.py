"""API endpoints for job management."""

import logging
from typing import List
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import Response

from app.models.job import JobCreate, JobConfig
from app.storage.job_storage import (
    save_job,
    load_all_jobs,
    get_job,
    delete_job,
    job_exists,
)
from app.scheduler import scheduler_manager
from app.executor.data_fetcher import fetch_data, DataFetchError
from app.executor.script_executor import (
    execute_script,
    ScriptExecutionError,
    ScriptTimeoutError,
    ScriptOutputError
)
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


@router.put("/{job_name}", response_model=JobConfig)
async def update_job(job_name: str, job_data: JobCreate):
    """
    Update an existing scheduled job.
    
    Args:
        job_name: Current job name
        job_data: Updated job configuration data
        
    Returns:
        Updated job configuration
        
    Raises:
        HTTPException: If job not found or update fails
    """
    logger.info(f"API: Updating job '{job_name}'")
    
    # Check if job exists
    existing_job = get_job(job_name)
    if existing_job is None:
        logger.warning(f"API: Job update failed - job '{job_name}' not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_name}' not found"
        )
    
    # If job name is changing, check if new name already exists
    if job_name != job_data.job_name and job_exists(job_data.job_name):
        logger.warning(f"API: Job update failed - new name '{job_data.job_name}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with name '{job_data.job_name}' already exists"
        )
    
    try:
        # Create updated job configuration, preserving created_at and last_run
        job_config = JobConfig(
            job_name=job_data.job_name,
            schedule_time=job_data.schedule_time,
            data_source=job_data.data_source,
            processing_script=job_data.processing_script,
            consumer_emails=job_data.consumer_emails,
            created_at=existing_job.created_at,
            last_run=existing_job.last_run,
        )
        
        # If job name changed, delete old job
        if job_name != job_data.job_name:
            logger.debug(f"API: Job name changed from '{job_name}' to '{job_data.job_name}'")
            scheduler_manager.remove_job(job_name)
            delete_job(job_name)
        else:
            # Remove old schedule
            scheduler_manager.remove_job(job_name)
        
        # Save updated job to storage
        logger.debug(f"API: Saving updated job '{job_data.job_name}' to storage")
        save_job(job_config)
        
        # Reschedule the job
        logger.debug(f"API: Rescheduling job '{job_data.job_name}' with APScheduler")
        scheduler_manager.schedule_job(job_config)
        
        logger.info(f"API: Job '{job_name}' updated successfully")
        return job_config
        
    except Exception as e:
        logger.error(f"API: Failed to update job '{job_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
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


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a data file to the server.
    
    Args:
        file: The file to upload
        
    Returns:
        Dictionary with file path
        
    Raises:
        HTTPException: If file upload fails
    """
    logger.info(f"API: Uploading file '{file.filename}'")
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.csv', '.json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_ext}. Only .csv and .json files are allowed."
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / file.filename
        
        # Check if file already exists
        if file_path.exists():
            logger.warning(f"API: File '{file.filename}' already exists, overwriting")
        
        # Write file content
        content = await file.read()
        file_path.write_bytes(content)
        
        logger.info(f"API: File '{file.filename}' uploaded successfully to {file_path}")
        
        # Return the path that should be used in job configuration
        return {
            "filename": file.filename,
            "path": f"/data/uploads/{file.filename}",
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to upload file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.post("/{job_name}/test")
async def test_job(job_name: str):
    """
    Test a job by executing it immediately and returning the CSV result.
    
    This endpoint allows testing a job configuration without scheduling it.
    It fetches data, processes it, and returns the CSV output for download.
    
    Args:
        job_name: Unique job identifier
        
    Returns:
        CSV file as downloadable response
        
    Raises:
        HTTPException: If job not found or execution fails
    """
    logger.info(f"API: Testing job '{job_name}'")
    
    try:
        # Get job configuration
        job_config = get_job(job_name)
        if job_config is None:
            logger.warning(f"API: Job '{job_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job '{job_name}' not found"
            )
        
        # Step 1: Fetch data
        logger.info(f"API: Fetching data for job '{job_name}'")
        try:
            input_df = await fetch_data(job_config.data_source)
            logger.info(f"API: Data fetched successfully. Shape: {input_df.shape}")
        except DataFetchError as e:
            logger.error(f"API: Data fetch failed for job '{job_name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data fetch failed: {str(e)}"
            )
        
        # Step 2: Execute processing script
        logger.info(f"API: Executing processing script for job '{job_name}'")
        try:
            result_df = execute_script(job_config.processing_script, input_df)
            logger.info(f"API: Script executed successfully. Output shape: {result_df.shape}")
        except (ScriptExecutionError, ScriptTimeoutError, ScriptOutputError) as e:
            logger.error(f"API: Script execution failed for job '{job_name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Script execution failed: {str(e)}"
            )
        
        # Step 3: Convert to CSV
        logger.info(f"API: Converting output to CSV for job '{job_name}'")
        try:
            csv_content = result_df.to_csv(index=False)
            logger.info(f"API: CSV conversion successful. Size: {len(csv_content)} bytes")
        except Exception as e:
            logger.error(f"API: CSV conversion failed for job '{job_name}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CSV conversion failed: {str(e)}"
            )
        
        logger.info(f"API: Job '{job_name}' test completed successfully")
        
        # Return CSV as downloadable file
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={job_name}_test_result.csv"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to test job '{job_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test job: {str(e)}"
        )
