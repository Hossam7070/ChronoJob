"""
Main FastAPI application for the Scheduled Jobs Service.

This module initializes the FastAPI application and manages its lifecycle,
including scheduler initialization, job loading, and graceful shutdown.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config, ConfigurationError
from app.logging_config import setup_logging
from app.middleware import RequestLoggingMiddleware
from app.scheduler.scheduler_manager import (
    init_scheduler,
    start_scheduler,
    shutdown_scheduler,
    add_job,
    SchedulerError
)
from app.storage.job_storage import load_all_jobs
from app.executor.job_executor import execute_job


# Configure application-wide logging
setup_logging(
    log_level=config.LOG_LEVEL,
    enable_colors=True,
    log_file=os.getenv('LOG_FILE')  # Optional log file from environment
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifecycle.
    
    This context manager handles startup and shutdown events:
    - Startup: Initialize scheduler and load persisted jobs
    - Shutdown: Gracefully stop scheduler
    """
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Scheduled Jobs Service")
    logger.info("=" * 60)
    
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        logger.info(f"Configuration loaded: {config}")
        logger.info("Configuration validation successful")
        # Initialize APScheduler
        logger.info("Initializing APScheduler...")
        init_scheduler()
        
        # Load persisted jobs from storage
        logger.info("Loading persisted jobs from storage...")
        jobs = load_all_jobs()
        logger.info(f"Found {len(jobs)} persisted job(s)")
        
        # Register each job with the scheduler
        jobs_registered = 0
        for job_config in jobs:
            try:
                logger.info(f"Registering job: {job_config.job_name}")
                add_job(job_config, execute_job)
                jobs_registered += 1
            except Exception as e:
                logger.error(
                    f"Failed to register job '{job_config.job_name}': {str(e)}",
                    exc_info=True
                )
        
        logger.info(f"Successfully registered {jobs_registered}/{len(jobs)} job(s)")
        
        # Start the scheduler
        logger.info("Starting APScheduler...")
        start_scheduler()
        
        logger.info("=" * 60)
        logger.info("Scheduled Jobs Service started successfully")
        logger.info("=" * 60)
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {str(e)}", exc_info=True)
        logger.error("Application startup failed - configuration error")
        raise
    except SchedulerError as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}", exc_info=True)
        logger.error("Application startup failed - scheduler initialization error")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during startup: {str(e)}", exc_info=True)
        logger.error("Application startup failed")
        raise
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down Scheduled Jobs Service")
    logger.info("=" * 60)
    
    try:
        logger.info("Stopping APScheduler...")
        shutdown_scheduler(wait=True)
        logger.info("APScheduler stopped successfully")
        
        logger.info("=" * 60)
        logger.info("Scheduled Jobs Service shutdown complete")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# Initialize FastAPI application
app = FastAPI(
    title="Scheduled Jobs Service",
    description="A service for creating and managing recurring data processing jobs",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=False  # Set to True for debugging (logs request bodies)
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "service": "Scheduled Jobs Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include API routers
from app.api import jobs
app.include_router(jobs.router)
