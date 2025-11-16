"""Models for script management."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class ScriptCreate(BaseModel):
    """Model for creating a new script."""
    script_name: str
    description: Optional[str] = None
    script_content: str
    
    @field_validator('script_name')
    @classmethod
    def validate_script_name(cls, v: str) -> str:
        """Validate script_name is not empty and contains valid characters."""
        if not v or not v.strip():
            raise ValueError("script_name cannot be empty")
        if len(v) > 100:
            raise ValueError("script_name cannot exceed 100 characters")
        return v.strip()
    
    @field_validator('script_content')
    @classmethod
    def validate_script_content(cls, v: str) -> str:
        """Validate that script_content is not empty."""
        if not v or not v.strip():
            raise ValueError("script_content cannot be empty")
        return v


class ScriptConfig(BaseModel):
    """Model for storing script configuration with metadata."""
    script_name: str
    description: Optional[str] = None
    script_content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScriptTestRequest(BaseModel):
    """Model for testing a script with sample data."""
    script_content: str
    test_file_path: str  # Path to uploaded test file
