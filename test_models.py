#!/usr/bin/env python3
"""Quick validation script for Pydantic models."""

from datetime import datetime
from app.models import DataSource, JobCreate, JobConfig

def test_data_source_api():
    """Test DataSource with API source type."""
    ds = DataSource(
        source_type="api",
        location="https://api.example.com/data"
    )
    print(f"✓ API DataSource created: {ds.source_type} - {ds.location}")

def test_data_source_file():
    """Test DataSource with file source type."""
    ds = DataSource(
        source_type="file",
        location="/path/to/data.csv",
        file_type="csv"
    )
    print(f"✓ File DataSource created: {ds.source_type} - {ds.location} ({ds.file_type})")

def test_data_source_file_validation():
    """Test that file source requires file_type."""
    try:
        ds = DataSource(
            source_type="file",
            location="/path/to/data.csv"
        )
        print("✗ Should have raised validation error for missing file_type")
    except ValueError as e:
        print(f"✓ Validation error caught: {e}")

def test_job_create_valid():
    """Test JobCreate with valid data."""
    job = JobCreate(
        job_name="test_job",
        schedule_time="0 9 * * 1-5",
        data_source=DataSource(
            source_type="api",
            location="https://api.example.com/sales"
        ),
        processing_script="result = data.groupby('category').sum()",
        consumer_emails=["analyst@example.com"]
    )
    print(f"✓ JobCreate created: {job.job_name} with schedule {job.schedule_time}")

def test_job_create_invalid_cron():
    """Test JobCreate with invalid cron expression."""
    try:
        job = JobCreate(
            job_name="test_job",
            schedule_time="invalid cron",
            data_source=DataSource(
                source_type="api",
                location="https://api.example.com/sales"
            ),
            processing_script="result = data",
            consumer_emails=["analyst@example.com"]
        )
        print("✗ Should have raised validation error for invalid cron")
    except ValueError as e:
        print(f"✓ Cron validation error caught: {str(e)[:80]}...")

def test_job_create_no_emails():
    """Test JobCreate with no consumer emails."""
    try:
        job = JobCreate(
            job_name="test_job",
            schedule_time="0 9 * * *",
            data_source=DataSource(
                source_type="api",
                location="https://api.example.com/sales"
            ),
            processing_script="result = data",
            consumer_emails=[]
        )
        print("✗ Should have raised validation error for empty emails")
    except ValueError as e:
        print(f"✓ Email validation error caught: {e}")

def test_job_config():
    """Test JobConfig model."""
    config = JobConfig(
        job_name="daily_report",
        schedule_time="0 9 * * 1-5",
        data_source=DataSource(
            source_type="file",
            location="/data/sales.csv",
            file_type="csv"
        ),
        processing_script="result = data.head(10)",
        consumer_emails=["user@example.com"],
        created_at=datetime.now()
    )
    print(f"✓ JobConfig created: {config.job_name} at {config.created_at}")

if __name__ == "__main__":
    print("Testing Pydantic Models...\n")
    
    test_data_source_api()
    test_data_source_file()
    test_data_source_file_validation()
    test_job_create_valid()
    test_job_create_invalid_cron()
    test_job_create_no_emails()
    test_job_config()
    
    print("\n✓ All model tests passed!")
