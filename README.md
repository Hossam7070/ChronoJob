# Scheduled Jobs Service

A FastAPI-based service for creating and managing recurring data processing jobs. Each job executes a custom Python script at scheduled times to process data from various sources and delivers results via email.

## Features

- Create recurring jobs with cron-based scheduling
- Fetch data from external APIs or internal files
- Execute custom Python scripts for data processing
- Automatic email delivery of results as CSV attachments
- Persistent job storage with automatic recovery on restart
- RESTful API for job management

## Requirements

- Python 3.8+
- SMTP server access for email delivery

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd scheduled-jobs-service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your SMTP credentials and configuration
```

## Configuration

Edit the `.env` file with your settings:

### Required Variables
- `SMTP_HOST`: Your SMTP server hostname (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (typically 587 for TLS)
- `SMTP_USER`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_FROM_EMAIL`: Sender email address

### Optional Variables
- `SMTP_USE_TLS`: Enable TLS encryption (default: true)
- `JOB_STORAGE_PATH`: Path to job storage file (default: ./data/jobs.json)
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `LOG_FILE`: Optional path to log file for persistent logging (default: none, logs to console only)
- `SCRIPT_TIMEOUT`: Maximum script execution time in seconds (default: 300)
- `API_FETCH_TIMEOUT`: API request timeout in seconds (default: 30)

## Running the Service

Start the FastAPI application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at `http://localhost:8000`

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage

### Creating a Job

Send a POST request to `/jobs/create`:

```bash
curl -X POST "http://localhost:8000/jobs/create" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "daily_sales_report",
    "schedule_time": "0 9 * * 1-5",
    "data_source": {
      "source_type": "api",
      "location": "https://api.example.com/sales"
    },
    "processing_script": "result = data.groupby(\"category\").sum()",
    "consumer_emails": ["analyst@example.com"]
  }'
```

### Cron Expression Format

Schedule times use standard 5-field cron format:
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-6, Sunday=0)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

Examples:
- `0 9 * * 1-5`: 9 AM, Monday through Friday
- `30 14 * * *`: 2:30 PM daily
- `0 */6 * * *`: Every 6 hours
- `0 0 1 * *`: First day of every month at midnight

### Data Source Types

#### External API
```json
{
  "source_type": "api",
  "location": "https://api.example.com/data"
}
```

#### Internal File (CSV)
```json
{
  "source_type": "file",
  "location": "./data/input.csv",
  "file_type": "csv"
}
```

#### Internal File (JSON)
```json
{
  "source_type": "file",
  "location": "./data/input.json",
  "file_type": "json"
}
```

### Processing Script Requirements

Your processing script must:
- Accept input data as a Pandas DataFrame named `data`
- Return a Pandas DataFrame named `result`
- Complete within the configured timeout (default: 300 seconds)

Example script:
```python
# Filter and aggregate data
filtered = data[data['amount'] > 100]
result = filtered.groupby('category').agg({
    'amount': 'sum',
    'quantity': 'count'
}).reset_index()
```

### Listing All Jobs

```bash
curl -X GET "http://localhost:8000/jobs"
```

### Getting a Specific Job

```bash
curl -X GET "http://localhost:8000/jobs/daily_sales_report"
```

### Deleting a Job

```bash
curl -X DELETE "http://localhost:8000/jobs/daily_sales_report"
```

## Project Structure

```
scheduled-jobs-service/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # Pydantic models
│   │   └── job.py
│   ├── api/                    # API endpoints
│   │   └── jobs.py
│   ├── storage/                # Job persistence
│   │   └── job_storage.py
│   ├── scheduler/              # APScheduler integration
│   │   └── scheduler_manager.py
│   ├── executor/               # Job execution logic
│   │   ├── job_executor.py
│   │   ├── data_fetcher.py
│   │   └── script_executor.py
│   └── delivery/               # Email delivery
│       └── email_service.py
├── data/                       # Job storage and data files
│   └── jobs.json
├── tests/                      # Test suite
├── .env                        # Environment configuration (not in git)
├── .env.example                # Example environment configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Email Notifications

### Success Emails
When a job completes successfully, consumers receive an email with:
- Subject: `Job Results: {job_name} - {timestamp}`
- Attachment: CSV file containing the processed data

### Failure Emails
When a job fails, consumers receive an email with:
- Subject: `Job Failed: {job_name} - {timestamp}`
- Body: Error details and stack trace

## Troubleshooting

### SMTP Authentication Issues
- For Gmail, use an App Password instead of your regular password
- Enable "Less secure app access" or use OAuth2 for production
- Verify SMTP_HOST and SMTP_PORT are correct for your provider

### Job Not Executing
- Check logs for scheduler errors
- Verify cron expression is valid
- Ensure the service is running continuously
- Check that jobs.json exists and is readable

### Script Execution Errors
- Verify your script syntax is valid Python
- Ensure the script returns a DataFrame named `result`
- Check that required libraries (pandas, numpy) are available
- Review script timeout settings if processing takes too long

### Data Fetch Failures
- Verify API URLs are accessible
- Check file paths are correct and files exist
- Ensure proper file permissions
- Review API_FETCH_TIMEOUT if requests are timing out

## Logging

The service includes comprehensive structured logging for monitoring and debugging.

### Log Levels

Configure the log level using the `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed information for debugging (includes all operations)
- `INFO`: General informational messages (default, recommended for production)
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for failures that don't stop the service
- `CRITICAL`: Critical errors that may cause service failure

### Log Output

Logs are written to the console by default with colored output for easy reading. To enable file logging, set the `LOG_FILE` environment variable:

```bash
LOG_FILE=./logs/scheduled-jobs.log
```

### Log Format

All log messages include:
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Logger name (module path)
- Log level
- Source file and line number
- Message with context

Example log output:
```
2025-11-09 14:00:32 - app.api.jobs - INFO - [jobs.py:45] - API: Creating new job 'daily_report'
2025-11-09 14:00:32 - app.scheduler.scheduler_manager - INFO - [scheduler_manager.py:78] - Scheduler: Adding job 'daily_report' with schedule: 0 9 * * 1-5
2025-11-09 14:00:32 - app.executor.job_executor - INFO - [job_executor.py:35] - [daily_report] Starting execution for job 'daily_report'
```

### What Gets Logged

#### Application Lifecycle
- Service startup and shutdown events
- Configuration validation
- Scheduler initialization and shutdown
- Job loading from storage

#### API Requests
- All HTTP requests (method, path, status code)
- Request duration
- Slow request warnings (> 1 second)
- API errors with stack traces

#### Job Execution
- Job execution start and completion
- Each step of the job flow (fetch, process, deliver)
- Data shapes and sizes
- Execution errors with details
- Email delivery status

#### Scheduler Events
- Job registration and removal
- Next scheduled run times
- Scheduler errors

#### Storage Operations
- Job save, load, and delete operations
- Storage file creation
- Data corruption warnings

### Monitoring Job Execution

Job execution logs include the job name in brackets for easy filtering:

```bash
# View logs for a specific job
tail -f logs/scheduled-jobs.log | grep "\[daily_report\]"

# View only errors
tail -f logs/scheduled-jobs.log | grep "ERROR"

# View API requests
tail -f logs/scheduled-jobs.log | grep "API:"
```

### Debugging

For detailed debugging, set `LOG_LEVEL=DEBUG`:

```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

This will log:
- Request bodies (when enabled in middleware)
- Query parameters
- Detailed execution steps
- Storage operations
- All function calls

## Development

### Running Tests
```bash
pytest tests/
```

### Testing Logging
```bash
python test_logging.py
```

### Code Style
```bash
# Format code
black app/

# Lint code
flake8 app/
```

## Security Considerations

- Store SMTP credentials securely (use environment variables, never commit .env)
- Implement authentication for API endpoints in production
- Restrict processing script capabilities (whitelist imports)
- Validate and sanitize all user inputs
- Use HTTPS in production
- Implement rate limiting for job creation
- Set resource limits for script execution

## License

[Your License Here]
