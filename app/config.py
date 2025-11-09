"""
Configuration management for the Scheduled Jobs Service.

This module loads and validates environment variables using python-dotenv,
providing centralized configuration access throughout the application.
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Config:
    """
    Application configuration loaded from environment variables.
    
    Required environment variables:
    - SMTP_HOST: SMTP server hostname
    - SMTP_USER: SMTP username
    - SMTP_PASSWORD: SMTP password
    - SMTP_FROM_EMAIL: Sender email address
    
    Optional environment variables with defaults:
    - SMTP_PORT: SMTP server port (default: 587)
    - SMTP_USE_TLS: Enable TLS (default: true)
    - JOB_STORAGE_PATH: Path to jobs.json file (default: ./data/jobs.json)
    - LOG_LEVEL: Logging level (default: INFO)
    - SCRIPT_TIMEOUT: Script execution timeout in seconds (default: 300)
    - API_FETCH_TIMEOUT: API fetch timeout in seconds (default: 30)
    """
    
    # SMTP Configuration (Required)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    SMTP_USE_TLS: bool
    
    # Optional Configuration with defaults
    JOB_STORAGE_PATH: str
    LOG_LEVEL: str
    SCRIPT_TIMEOUT: int
    API_FETCH_TIMEOUT: int
    
    def __init__(self):
        """Initialize configuration and validate required variables."""
        self._load_smtp_config()
        self._load_optional_config()
        self._validate_config()
    
    def _load_smtp_config(self):
        """Load SMTP configuration from environment variables."""
        self.SMTP_HOST = os.getenv('SMTP_HOST', '')
        self.SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
        self.SMTP_USER = os.getenv('SMTP_USER', '')
        self.SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
        self.SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')
        self.SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    def _load_optional_config(self):
        """Load optional configuration with defaults."""
        self.JOB_STORAGE_PATH = os.getenv('JOB_STORAGE_PATH', './data/jobs.json')
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.SCRIPT_TIMEOUT = int(os.getenv('SCRIPT_TIMEOUT', '300'))
        self.API_FETCH_TIMEOUT = int(os.getenv('API_FETCH_TIMEOUT', '30'))
    
    def _validate_config(self):
        """
        Validate that all required configuration is present.
        
        Raises:
            ConfigurationError: If required configuration is missing
        """
        required_vars = {
            'SMTP_HOST': self.SMTP_HOST,
            'SMTP_USER': self.SMTP_USER,
            'SMTP_PASSWORD': self.SMTP_PASSWORD,
            'SMTP_FROM_EMAIL': self.SMTP_FROM_EMAIL,
        }
        
        missing_vars = [
            var_name for var_name, var_value in required_vars.items()
            if not var_value
        ]
        
        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please set these variables in your .env file or environment."
            )
            raise ConfigurationError(error_msg)
        
        # Validate numeric values are positive
        if self.SMTP_PORT <= 0:
            raise ConfigurationError("SMTP_PORT must be a positive integer")
        
        if self.SCRIPT_TIMEOUT <= 0:
            raise ConfigurationError("SCRIPT_TIMEOUT must be a positive integer")
        
        if self.API_FETCH_TIMEOUT <= 0:
            raise ConfigurationError("API_FETCH_TIMEOUT must be a positive integer")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL not in valid_log_levels:
            raise ConfigurationError(
                f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}"
            )
    
    def get_smtp_config(self) -> dict:
        """
        Get SMTP configuration as a dictionary.
        
        Returns:
            Dictionary containing SMTP configuration
        """
        return {
            'host': self.SMTP_HOST,
            'port': self.SMTP_PORT,
            'user': self.SMTP_USER,
            'password': self.SMTP_PASSWORD,
            'from_email': self.SMTP_FROM_EMAIL,
            'use_tls': self.SMTP_USE_TLS,
        }
    
    def __repr__(self) -> str:
        """String representation of config (hiding sensitive data)."""
        return (
            f"Config("
            f"SMTP_HOST={self.SMTP_HOST}, "
            f"SMTP_PORT={self.SMTP_PORT}, "
            f"SMTP_USER={self.SMTP_USER}, "
            f"SMTP_FROM_EMAIL={self.SMTP_FROM_EMAIL}, "
            f"SMTP_USE_TLS={self.SMTP_USE_TLS}, "
            f"JOB_STORAGE_PATH={self.JOB_STORAGE_PATH}, "
            f"LOG_LEVEL={self.LOG_LEVEL}, "
            f"SCRIPT_TIMEOUT={self.SCRIPT_TIMEOUT}, "
            f"API_FETCH_TIMEOUT={self.API_FETCH_TIMEOUT}"
            f")"
        )


# Global configuration instance
# This will be initialized when the module is imported
try:
    config = Config()
except ConfigurationError as e:
    # Log the error but don't crash on import
    # The application startup will handle this appropriately
    logging.error(f"Configuration error: {str(e)}")
    raise
