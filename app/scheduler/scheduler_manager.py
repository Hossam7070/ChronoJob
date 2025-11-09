"""
Scheduler manager module for APScheduler integration.

This module manages the lifecycle of the APScheduler BackgroundScheduler,
including initialization, job registration, job removal, and graceful shutdown.
"""
import logging
from typing import Optional, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError

from app.models.job import JobConfig


logger = logging.getLogger(__name__)


# Global scheduler instance
_scheduler: Optional[BackgroundScheduler] = None


class SchedulerError(Exception):
    """Base exception for scheduler-related errors."""
    pass


def init_scheduler() -> BackgroundScheduler:
    """
    Initialize and return a BackgroundScheduler instance.
    
    Creates a new BackgroundScheduler with appropriate configuration
    for running scheduled jobs in the background without blocking
    the main application thread.
    
    Returns:
        BackgroundScheduler: Configured scheduler instance
        
    Raises:
        SchedulerError: If scheduler initialization fails
    """
    global _scheduler
    
    try:
        logger.info("Initializing APScheduler BackgroundScheduler")
        
        # Create BackgroundScheduler with configuration
        scheduler = BackgroundScheduler(
            timezone='UTC',  # Use UTC for consistency
            job_defaults={
                'coalesce': True,  # Combine multiple missed executions into one
                'max_instances': 1,  # Only one instance of each job at a time
                'misfire_grace_time': 300  # Allow 5 minutes grace for missed jobs
            }
        )
        
        _scheduler = scheduler
        logger.info("APScheduler initialized successfully")
        return scheduler
        
    except Exception as e:
        error_msg = f"Failed to initialize scheduler: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise SchedulerError(error_msg) from e


def get_scheduler() -> BackgroundScheduler:
    """
    Get the global scheduler instance.
    
    Returns:
        BackgroundScheduler: The global scheduler instance
        
    Raises:
        SchedulerError: If scheduler has not been initialized
    """
    if _scheduler is None:
        raise SchedulerError("Scheduler has not been initialized. Call init_scheduler() first.")
    return _scheduler


def add_job(job_config: JobConfig, executor_func: Callable) -> None:
    """
    Register a job with APScheduler using a CronTrigger.
    
    This function adds a new job to the scheduler with the specified
    cron schedule. The job will execute the provided executor function
    with the job configuration as an argument.
    
    Args:
        job_config: Job configuration containing schedule and execution details
        executor_func: Callable function to execute when job is triggered
                      (should accept job_config as argument)
        
    Raises:
        SchedulerError: If job registration fails
    """
    try:
        scheduler = get_scheduler()
        job_name = job_config.job_name
        
        logger.info(f"Scheduler: Adding job '{job_name}' with schedule: {job_config.schedule_time}")
        
        # Create CronTrigger from cron expression
        trigger = CronTrigger.from_crontab(job_config.schedule_time, timezone='UTC')
        
        # Log next run time
        next_run = trigger.get_next_fire_time(None, None)
        if next_run:
            logger.info(f"Scheduler: Job '{job_name}' next scheduled run: {next_run}")
        
        # Add job to scheduler
        # Use job_name as the job ID for easy lookup and removal
        scheduler.add_job(
            func=executor_func,
            trigger=trigger,
            args=[job_config],
            id=job_name,
            name=job_name,
            replace_existing=True  # Replace if job with same ID exists
        )
        
        logger.info(f"Scheduler: Job '{job_name}' added successfully to APScheduler")
        
    except SchedulerError:
        # Re-raise scheduler errors
        raise
    except Exception as e:
        error_msg = f"Failed to register job '{job_config.job_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise SchedulerError(error_msg) from e


def remove_job(job_name: str) -> None:
    """
    Remove a job from APScheduler.
    
    Unregisters a job from the scheduler, preventing future executions.
    If the job is currently running, it will complete but no new
    executions will be scheduled.
    
    Args:
        job_name: Name/ID of the job to remove
        
    Raises:
        SchedulerError: If job removal fails or job not found
    """
    try:
        scheduler = get_scheduler()
        
        logger.info(f"Scheduler: Removing job '{job_name}' from scheduler")
        
        # Remove job by ID
        scheduler.remove_job(job_name)
        
        logger.info(f"Scheduler: Job '{job_name}' removed successfully from APScheduler")
        
    except JobLookupError:
        error_msg = f"Job '{job_name}' not found in scheduler"
        logger.warning(f"Scheduler: {error_msg}")
        raise SchedulerError(error_msg)
    except SchedulerError:
        # Re-raise scheduler errors
        raise
    except Exception as e:
        error_msg = f"Failed to remove job '{job_name}': {str(e)}"
        logger.error(f"Scheduler: {error_msg}", exc_info=True)
        raise SchedulerError(error_msg) from e


def start_scheduler() -> None:
    """
    Start the APScheduler to begin executing scheduled jobs.
    
    This function starts the scheduler's background thread, which will
    begin monitoring and executing registered jobs according to their
    schedules.
    
    Raises:
        SchedulerError: If scheduler start fails
    """
    try:
        scheduler = get_scheduler()
        
        if scheduler.running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting APScheduler")
        scheduler.start()
        logger.info("APScheduler started successfully")
        
    except SchedulerError:
        # Re-raise scheduler errors
        raise
    except Exception as e:
        error_msg = f"Failed to start scheduler: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise SchedulerError(error_msg) from e


def shutdown_scheduler(wait: bool = True) -> None:
    """
    Gracefully shutdown the APScheduler.
    
    Stops the scheduler and optionally waits for all currently executing
    jobs to complete before shutting down.
    
    Args:
        wait: If True, wait for running jobs to complete before shutdown.
              If False, shutdown immediately (default: True)
        
    Raises:
        SchedulerError: If scheduler shutdown fails
    """
    global _scheduler
    
    try:
        if _scheduler is None:
            logger.warning("Scheduler is not initialized, nothing to shutdown")
            return
        
        if not _scheduler.running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info(f"Shutting down APScheduler (wait={wait})")
        _scheduler.shutdown(wait=wait)
        logger.info("APScheduler shutdown successfully")
        
        _scheduler = None
        
    except Exception as e:
        error_msg = f"Failed to shutdown scheduler: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise SchedulerError(error_msg) from e


def get_scheduled_jobs() -> list:
    """
    Get list of all currently scheduled jobs.
    
    Returns:
        list: List of scheduled job objects with details
        
    Raises:
        SchedulerError: If scheduler is not initialized
    """
    try:
        scheduler = get_scheduler()
        jobs = scheduler.get_jobs()
        
        logger.debug(f"Retrieved {len(jobs)} scheduled jobs")
        return jobs
        
    except SchedulerError:
        raise
    except Exception as e:
        error_msg = f"Failed to get scheduled jobs: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise SchedulerError(error_msg) from e


class SchedulerManager:
    """
    High-level scheduler manager class for managing job lifecycle.
    
    This class provides a simplified interface for managing scheduled jobs,
    including initialization, job scheduling, and cleanup.
    """
    
    def __init__(self):
        """Initialize the scheduler manager."""
        self._scheduler = None
        self._initialized = False
    
    def start(self) -> None:
        """
        Initialize and start the scheduler, loading all persisted jobs.
        
        This method should be called during application startup.
        """
        if self._initialized:
            logger.warning("Scheduler already initialized")
            return
        
        try:
            # Initialize scheduler
            self._scheduler = init_scheduler()
            
            # Start scheduler
            start_scheduler()
            
            # Load and schedule all persisted jobs
            from app.storage.job_storage import load_all_jobs
            from app.executor.job_executor import execute_job
            
            jobs = load_all_jobs()
            logger.info(f"Loading {len(jobs)} persisted jobs")
            
            for job_config in jobs:
                try:
                    add_job(job_config, execute_job)
                    logger.info(f"Scheduled job: {job_config.job_name}")
                except Exception as e:
                    logger.error(f"Failed to schedule job {job_config.job_name}: {e}")
            
            self._initialized = True
            logger.info("Scheduler manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler manager: {e}", exc_info=True)
            raise
    
    def schedule_job(self, job_config: JobConfig) -> None:
        """
        Schedule a new job.
        
        Args:
            job_config: Job configuration to schedule
        """
        from app.executor.job_executor import execute_job
        add_job(job_config, execute_job)
    
    def remove_job(self, job_name: str) -> None:
        """
        Remove a scheduled job.
        
        Args:
            job_name: Name of the job to remove
        """
        try:
            remove_job(job_name)
        except SchedulerError as e:
            # Job not found is acceptable during deletion
            logger.warning(f"Job removal warning: {e}")
    
    def shutdown(self) -> None:
        """
        Gracefully shutdown the scheduler.
        
        This method should be called during application shutdown.
        """
        if not self._initialized:
            logger.warning("Scheduler not initialized, nothing to shutdown")
            return
        
        try:
            shutdown_scheduler(wait=True)
            self._initialized = False
            logger.info("Scheduler manager shutdown successfully")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}", exc_info=True)
    
    def get_jobs(self) -> list:
        """
        Get list of all currently scheduled jobs.
        
        Returns:
            list: List of scheduled job objects
        """
        return get_scheduled_jobs()
