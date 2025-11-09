Scheduled Jobs Service Agent
Goal: Design, build, and deploy a robust Scheduled Jobs Service using FastAPI in Python.

Core Functionality: The service must allow users to create and manage recurring jobs that execute at pre-assigned times. Each job will execute a custom Python script to process data and then deliver the results via email.

1. Job Creation and Structure
The service must implement a mechanism (e.g., a Pydantic model for the API endpoint) to accept the following parameters for a new scheduled job:

job_name (string): A unique, descriptive name for the job.

schedule_time (string): The recurring execution time, specified in a standard format (e.g., Cron expression like 0 9 * * 1-5 for 9 AM, Monday-Friday, or a simple time like HH:MM). Specify a clear format.

data_source (string/enum): The origin of the raw data. Must support:

External API URL (string)

Internal Data Import (e.g., a path to a stored file, specifying the expected file type like CSV or JSON).

processing_script (string): The content of the Python script to be executed. Crucially, the script is expected to accept the raw data as input (e.g., a Pandas DataFrame or raw JSON) and must return a Pandas DataFrame as its output.

consumer_emails (list of strings): A list of email addresses that will receive the final report.

2. Technical Implementation Details
Framework: FastAPI (for the API endpoints and main service structure).

Scheduling Library: APScheduler (Advanced Python Scheduler) is the preferred library for managing recurring jobs within the FastAPI application.

Data Processing: Pandas must be used within the execution environment for data manipulation.

Data Input/Output: The data retrieval step must convert the fetched data (from API or file) into a Pandas DataFrame before passing it to the processing_script.

Output Format: The final Pandas DataFrame returned by the script must be converted into a CSV file.

Delivery: Use an appropriate Python library (e.g., smtplib) to send the final CSV file as an attachment via email to all listed consumers.

3. Agent Deliverables (Expected Output)
The AI agent should provide a comprehensive plan, including:

Project Structure: A suggested file and directory layout.

Code Snippets:

The FastAPI app structure (main.py).

The Pydantic model for job creation.

The job submission endpoint (/jobs/create).

A generic job_executor function that handles fetching, script execution, CSV creation, and emailing.

APScheduler setup and integration with FastAPI lifecycle (startup/shutdown).

Setup Instructions: Clear steps on necessary dependencies (pip install ...) and environment variables (e.g., SMTP server details).# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure: app/, app/models/, app/api/, app/storage/, app/scheduler/, app/executor/, app/delivery/, data/, tests/
  - Create requirements.txt with all necessary dependencies (fastapi, uvicorn, pydantic, apscheduler, pandas, httpx, python-dotenv, email-validator)
  - Create .env.example file with SMTP configuration template
  - Create main README.md with setup and usage instructions
  - _Requirements: 8.1_

- [x] 2. Implement data models and validation
  - [x] 2.1 Create Pydantic models for job configuration
    - Implement DataSource model with source_type, location, and file_type fields
    - Implement JobCreate model with all required fields and validators
    - Add cron expression validator using croniter library
    - Add email format validation using pydantic EmailStr
    - Implement JobConfig model for storage with timestamps
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3_

- [x] 3. Implement job storage layer
  - [x] 3.1 Create JSON-based job storage system
    - Implement save_job() function to persist JobConfig to jobs.json
    - Implement load_all_jobs() function to read all jobs from storage
    - Implement get_job() function to retrieve specific job by name
    - Implement delete_job() function to remove job from storage
    - Implement job_exists() function to check for duplicate names
    - Create data/ directory initialization on first run
    - _Requirements: 2.1, 3.3, 7.4_

- [x] 4. Implement data fetching functionality
  - [x] 4.1 Create data fetcher for external APIs and files
    - Implement fetch_from_api() using httpx with 30-second timeout
    - Implement fetch_from_file() supporting CSV and JSON formats
    - Implement main fetch_data() function that routes to appropriate fetcher
    - Convert all fetched data to Pandas DataFrame format
    - Add error handling with logging for fetch failures
    - Implement retry logic with exponential backoff (3 attempts)
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 5. Implement script execution engine
  - [x] 5.1 Create safe Python script executor
    - Implement execute_script() function with restricted execution environment
    - Set up whitelisted imports (pandas, numpy, datetime)
    - Inject input DataFrame as 'data' variable in script namespace
    - Implement 300-second timeout using threading or signal
    - Validate that script output is a Pandas DataFrame
    - Add comprehensive error handling and logging
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 6. Implement email delivery service
  - [x] 6.1 Create SMTP-based email service
    - Implement send_email() function with CSV attachment support
    - Create email with subject line including job_name and timestamp
    - Implement send_failure_email() for error notifications
    - Configure SMTP connection using environment variables
    - Add retry logic for email delivery (2 attempts with 5-second delay)
    - Support TLS/SSL configuration
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 7. Implement job executor orchestration
  - [x] 7.1 Create main job execution flow
    - Implement execute_job() function that orchestrates full job flow
    - Integrate data fetching, script execution, and email delivery
    - Add error handling that sends failure notifications to consumers
    - Implement last_run timestamp update after successful execution
    - Add comprehensive logging for all execution steps
    - _Requirements: 3.2, 4.4, 5.3, 6.1_

- [x] 8. Implement APScheduler integration
  - [x] 8.1 Create scheduler manager
    - Initialize BackgroundScheduler with appropriate configuration
    - Implement add_job() function to register jobs with CronTrigger
    - Implement remove_job() function to unregister jobs
    - Implement start_scheduler() and shutdown_scheduler() functions
    - Configure scheduler to use job_executor.execute_job as callback
    - Add error handling for scheduler operations
    - _Requirements: 3.1, 3.2, 3.4, 7.4, 8.2_

- [x] 9. Implement FastAPI application and lifecycle management
  - [x] 9.1 Create main FastAPI application
    - Initialize FastAPI app with metadata
    - Implement startup event handler to initialize scheduler
    - Implement startup event handler to load persisted jobs
    - Implement shutdown event handler to gracefully stop scheduler
    - Add logging for startup and shutdown events
    - Configure CORS if needed
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10. Implement job management API endpoints
  - [x] 10.1 Create POST /jobs/create endpoint
    - Accept JobCreate model in request body
    - Validate job parameters using Pydantic
    - Check for duplicate job_name using storage
    - Save job configuration to storage
    - Register job with APScheduler
    - Return created job details with 201 status
    - Handle validation errors with 400 status
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 3.1_

  - [x] 10.2 Create GET /jobs endpoint
    - Retrieve all jobs from storage
    - Return list of JobConfig objects
    - Handle empty list case
    - _Requirements: 7.2_

  - [x] 10.3 Create GET /jobs/{job_name} endpoint
    - Retrieve specific job by job_name from storage
    - Return JobConfig object
    - Return 404 if job not found
    - _Requirements: 7.1_

  - [x] 10.4 Create DELETE /jobs/{job_name} endpoint
    - Remove job from APScheduler
    - Delete job from storage
    - Return 204 on success
    - Return 404 if job not found
    - _Requirements: 7.3, 7.4_

- [x] 11. Add configuration and environment management
  - [x] 11.1 Implement configuration loading
    - Use python-dotenv to load .env file
    - Define all required environment variables (SMTP settings)
    - Define optional environment variables with defaults
    - Add validation for required environment variables on startup
    - Create .env.example with all configuration options documented
    - _Requirements: 6.4, 8.1_

- [x] 12. Add logging infrastructure
  - [x] 12.1 Configure application-wide logging
    - Set up Python logging with configurable log level
    - Add structured logging for all major operations
    - Log job execution start, success, and failure events
    - Log API requests and responses
    - Log scheduler events (job added, removed, executed)
    - Configure log format with timestamps and context
    - _Requirements: 4.4, 5.3, 8.3_

- [ ]* 13. Write integration tests
  - [ ]* 13.1 Create end-to-end test suite
    - Write test for complete job creation and execution flow
    - Write test for job persistence and loading on restart
    - Write test for all API endpoints (CRUD operations)
    - Write test for scheduler integration
    - Mock external dependencies (SMTP, external APIs)
    - Use pytest and pytest-asyncio for async tests
    - _Requirements: All_

- [ ]* 14. Create documentation
  - [ ]* 14.1 Write comprehensive README
    - Document installation steps
    - Document environment variable configuration
    - Provide example job creation requests
    - Document API endpoints with examples
    - Include cron expression examples
    - Add troubleshooting section
    - _Requirements: All_

  - [ ]* 14.2 Add API documentation
    - Configure FastAPI automatic OpenAPI documentation
    - Add detailed docstrings to all API endpoints
    - Include request/response examples in endpoint descriptions
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.1, 7.2, 7.3_
