# Requirements Document

## Introduction

The Scheduled Jobs Service is a FastAPI-based system that enables users to create and manage recurring jobs. Each job executes a custom Python script at pre-assigned times to process data from various sources and delivers the results via email as CSV attachments.

## Glossary

- **Scheduled Jobs Service**: The FastAPI application that manages job creation, scheduling, execution, and result delivery
- **Job**: A configured task that executes a Python script on a recurring schedule
- **Processing Script**: User-provided Python code that transforms input data into output data
- **Data Source**: The origin of raw data, either an external API URL or an internal file path
- **Consumer**: An email recipient who receives the processed job results
- **Job Executor**: The component responsible for fetching data, executing scripts, and delivering results
- **APScheduler**: The Advanced Python Scheduler library used for managing recurring job execution

## Requirements

### Requirement 1

**User Story:** As a service administrator, I want to create scheduled jobs with complete configuration parameters, so that I can automate data processing and delivery workflows.

#### Acceptance Criteria

1. THE Scheduled Jobs Service SHALL accept a job_name parameter as a unique string identifier for each job
2. THE Scheduled Jobs Service SHALL accept a schedule_time parameter as a cron expression string (format: minute hour day month day-of-week)
3. THE Scheduled Jobs Service SHALL accept a data_source parameter that specifies either an external API URL or an internal file path with file type
4. THE Scheduled Jobs Service SHALL accept a processing_script parameter containing Python code as a string
5. THE Scheduled Jobs Service SHALL accept a consumer_emails parameter as a list of valid email address strings

### Requirement 2

**User Story:** As a service administrator, I want the system to validate job parameters during creation, so that invalid configurations are rejected before scheduling.

#### Acceptance Criteria

1. WHEN a job creation request is received, THE Scheduled Jobs Service SHALL validate that job_name is unique across all existing jobs
2. WHEN a job creation request is received, THE Scheduled Jobs Service SHALL validate that schedule_time follows valid cron expression syntax
3. WHEN a job creation request is received, THE Scheduled Jobs Service SHALL validate that consumer_emails contains at least one valid email address format
4. IF job parameter validation fails, THEN THE Scheduled Jobs Service SHALL return an HTTP 400 error with specific validation failure details

### Requirement 3

**User Story:** As a service administrator, I want jobs to execute automatically at their scheduled times, so that data processing happens without manual intervention.

#### Acceptance Criteria

1. WHEN a job is created, THE Scheduled Jobs Service SHALL register the job with APScheduler using the provided cron expression
2. WHEN a scheduled time is reached, THE Scheduled Jobs Service SHALL trigger the Job Executor for the corresponding job
3. THE Scheduled Jobs Service SHALL maintain job schedules across application restarts by persisting job configurations
4. WHILE the Scheduled Jobs Service is running, THE APScheduler SHALL evaluate all registered job schedules continuously

### Requirement 4

**User Story:** As a service administrator, I want the system to fetch data from configured sources, so that processing scripts receive the correct input data.

#### Acceptance Criteria

1. WHEN a data_source specifies an external API URL, THE Job Executor SHALL retrieve data via HTTP GET request
2. WHEN a data_source specifies an internal file path, THE Job Executor SHALL read the file from the specified location
3. THE Job Executor SHALL convert fetched data into a Pandas DataFrame before passing to the Processing Script
4. IF data retrieval fails, THEN THE Job Executor SHALL log the error and send a failure notification email to all Consumer addresses

### Requirement 5

**User Story:** As a service administrator, I want processing scripts to execute with fetched data, so that custom transformations are applied to the raw data.

#### Acceptance Criteria

1. THE Job Executor SHALL execute the Processing Script in an isolated Python environment with the input DataFrame available
2. THE Job Executor SHALL capture the Pandas DataFrame returned by the Processing Script as output
3. IF the Processing Script raises an exception, THEN THE Job Executor SHALL log the error and send a failure notification email to all Consumer addresses
4. THE Job Executor SHALL enforce a maximum execution time of 300 seconds for each Processing Script

### Requirement 6

**User Story:** As a data consumer, I want to receive processed results via email as CSV attachments, so that I can access the data in a standard format.

#### Acceptance Criteria

1. WHEN a Processing Script completes successfully, THE Job Executor SHALL convert the output DataFrame to CSV format
2. THE Job Executor SHALL send an email to all Consumer addresses with the CSV file attached
3. THE Job Executor SHALL include the job_name and execution timestamp in the email subject line
4. THE Job Executor SHALL use SMTP protocol for email delivery with configurable server settings

### Requirement 7

**User Story:** As a service administrator, I want to manage the lifecycle of scheduled jobs, so that I can update or remove jobs as requirements change.

#### Acceptance Criteria

1. THE Scheduled Jobs Service SHALL provide an API endpoint to retrieve details of a specific job by job_name
2. THE Scheduled Jobs Service SHALL provide an API endpoint to list all registered jobs
3. THE Scheduled Jobs Service SHALL provide an API endpoint to delete a job by job_name
4. WHEN a job is deleted, THE Scheduled Jobs Service SHALL remove the job from APScheduler and delete its persisted configuration

### Requirement 8

**User Story:** As a service administrator, I want the system to handle startup and shutdown gracefully, so that job schedules are properly initialized and cleaned up.

#### Acceptance Criteria

1. WHEN the Scheduled Jobs Service starts, THE Scheduled Jobs Service SHALL initialize APScheduler and load all persisted job configurations
2. WHEN the Scheduled Jobs Service shuts down, THE Scheduled Jobs Service SHALL gracefully stop APScheduler and complete any running jobs
3. THE Scheduled Jobs Service SHALL log all startup and shutdown events with timestamps
4. IF APScheduler initialization fails, THEN THE Scheduled Jobs Service SHALL log the error and prevent application startup
