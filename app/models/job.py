from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from croniter import croniter


class DataSource(BaseModel):
    """Data source configuration for job input data."""
    source_type: Literal["api", "file"]
    location: str  # URL for API or file path for file
    file_type: Optional[Literal["csv", "json"]] = None
    
    @model_validator(mode='after')
    def validate_file_type(self):
        """Ensure file_type is provided when source_type is 'file'."""
        if self.source_type == "file" and self.file_type is None:
            raise ValueError("file_type is required when source_type is 'file'")
        if self.source_type == "api" and self.file_type is not None:
            raise ValueError("file_type should not be provided when source_type is 'api'")
        return self


class JobCreate(BaseModel):
    """Model for creating a new scheduled job."""
    job_name: str
    schedule_time: str  # Cron expression
    data_source: DataSource
    processing_script: str
    consumer_emails: List[EmailStr]
    
    @field_validator('schedule_time')
    @classmethod
    def validate_cron(cls, v: str) -> str:
        """Validate that schedule_time is a valid cron expression."""
        try:
            # croniter will raise ValueError if cron expression is invalid
            croniter(v)
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid cron expression: {v}. Error: {str(e)}")
        return v
    
    @field_validator('job_name')
    @classmethod
    def validate_job_name(cls, v: str) -> str:
        """Validate job_name is not empty and contains valid characters."""
        if not v or not v.strip():
            raise ValueError("job_name cannot be empty")
        if len(v) > 100:
            raise ValueError("job_name cannot exceed 100 characters")
        return v.strip()
    
    @field_validator('consumer_emails')
    @classmethod
    def validate_consumer_emails(cls, v: List[EmailStr]) -> List[EmailStr]:
        """Validate that at least one consumer email is provided."""
        if not v or len(v) == 0:
            raise ValueError("At least one consumer email is required")
        return v
    
    @field_validator('processing_script')
    @classmethod
    def validate_processing_script(cls, v: str) -> str:
        """Validate that processing_script is not empty."""
        if not v or not v.strip():
            raise ValueError("processing_script cannot be empty")
        return v


class JobConfig(BaseModel):
    """Model for storing job configuration with metadata."""
    job_name: str
    schedule_time: str
    data_source: DataSource
    processing_script: str
    consumer_emails: List[str]
    created_at: datetime
    last_run: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
