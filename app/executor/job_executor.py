"""
Job executor orchestration module.

This module orchestrates the complete job execution flow:
1. Fetch data from configured source
2. Execute processing script
3. Convert output to CSV
4. Send email with results
5. Update last_run timestamp
"""
import logging
from datetime import datetime
from typing import Optional
import pandas as pd

from app.models.job import JobConfig
from app.executor.data_fetcher import fetch_data, DataFetchError
from app.executor.script_executor import (
    execute_script,
    ScriptExecutionError,
    ScriptTimeoutError,
    ScriptOutputError
)
from app.delivery.email_service import send_email, send_failure_email
from app.storage.job_storage import save_job


logger = logging.getLogger(__name__)


class JobExecutionError(Exception):
    """Base exception for job execution errors."""
    pass


async def execute_job(job_config: JobConfig) -> None:
    """
    Execute a complete job flow: fetch data, process, and deliver results.
    
    This function orchestrates the entire job execution process:
    1. Fetches data from the configured data source
    2. Executes the processing script on the fetched data
    3. Converts the output DataFrame to CSV format
    4. Sends the CSV as an email attachment to all consumers
    5. Updates the last_run timestamp on successful completion
    
    If any step fails, a failure notification email is sent to all consumers.
    
    Args:
        job_config: The job configuration containing all execution parameters
        
    Raises:
        JobExecutionError: If job execution fails (after sending failure notification)
    """
    job_name = job_config.job_name
    logger.info(f"Starting execution for job '{job_name}'")
    
    try:
        # Step 1: Fetch data from configured source
        logger.info(f"[{job_name}] Step 1: Fetching data from {job_config.data_source.source_type} source")
        try:
            input_df = await fetch_data(job_config.data_source)
            logger.info(f"[{job_name}] Data fetched successfully. Shape: {input_df.shape}")
        except DataFetchError as e:
            error_msg = f"Data fetch failed: {str(e)}"
            logger.error(f"[{job_name}] {error_msg}")
            raise JobExecutionError(error_msg) from e
        
        # Step 2: Execute processing script
        logger.info(f"[{job_name}] Step 2: Executing processing script")
        try:
            result_df = execute_script(job_config.processing_script, input_df)
            logger.info(f"[{job_name}] Script executed successfully. Output shape: {result_df.shape}")
        except (ScriptExecutionError, ScriptTimeoutError, ScriptOutputError) as e:
            error_msg = f"Script execution failed: {str(e)}"
            logger.error(f"[{job_name}] {error_msg}")
            raise JobExecutionError(error_msg) from e
        
        # Step 3: Convert output DataFrame to CSV
        logger.info(f"[{job_name}] Step 3: Converting output to CSV format")
        try:
            csv_content = result_df.to_csv(index=False)
            logger.info(f"[{job_name}] CSV conversion successful. Size: {len(csv_content)} bytes")
        except Exception as e:
            error_msg = f"CSV conversion failed: {str(e)}"
            logger.error(f"[{job_name}] {error_msg}")
            raise JobExecutionError(error_msg) from e
        
        # Step 4: Send email with CSV attachment
        logger.info(f"[{job_name}] Step 4: Sending results via email to {len(job_config.consumer_emails)} recipient(s)")
        try:
            send_email(job_name, job_config.consumer_emails, csv_content)
            logger.info(f"[{job_name}] Email sent successfully")
        except Exception as e:
            error_msg = f"Email delivery failed: {str(e)}"
            logger.error(f"[{job_name}] {error_msg}")
            raise JobExecutionError(error_msg) from e
        
        # Step 5: Update last_run timestamp
        logger.info(f"[{job_name}] Step 5: Updating last_run timestamp")
        try:
            job_config.last_run = datetime.now()
            save_job(job_config)
            logger.info(f"[{job_name}] last_run timestamp updated to {job_config.last_run.isoformat()}")
        except Exception as e:
            # Log error but don't fail the job since execution was successful
            logger.error(f"[{job_name}] Failed to update last_run timestamp: {str(e)}")
        
        logger.info(f"[{job_name}] Job execution completed successfully")
        
    except JobExecutionError as e:
        # Send failure notification to consumers
        logger.error(f"[{job_name}] Job execution failed: {str(e)}")
        
        try:
            logger.info(f"[{job_name}] Sending failure notification to consumers")
            send_failure_email(job_name, job_config.consumer_emails, str(e))
            logger.info(f"[{job_name}] Failure notification sent successfully")
        except Exception as email_error:
            logger.error(f"[{job_name}] Failed to send failure notification: {str(email_error)}")
        
        # Re-raise the original error
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        error_msg = f"Unexpected error during job execution: {str(e)}"
        logger.error(f"[{job_name}] {error_msg}", exc_info=True)
        
        try:
            logger.info(f"[{job_name}] Sending failure notification to consumers")
            send_failure_email(job_name, job_config.consumer_emails, error_msg)
            logger.info(f"[{job_name}] Failure notification sent successfully")
        except Exception as email_error:
            logger.error(f"[{job_name}] Failed to send failure notification: {str(email_error)}")
        
        raise JobExecutionError(error_msg) from e
