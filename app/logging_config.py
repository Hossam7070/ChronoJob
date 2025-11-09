"""
Centralized logging configuration for the Scheduled Jobs Service.

This module provides structured logging setup with configurable log levels,
consistent formatting, and context-aware logging for all application components.
"""
import logging
import sys
from typing import Optional
from datetime import datetime


class ContextFilter(logging.Filter):
    """
    Custom logging filter to add contextual information to log records.
    
    This filter can be used to add additional context like request IDs,
    job names, or other metadata to log records.
    """
    
    def __init__(self, context: Optional[dict] = None):
        """
        Initialize the context filter.
        
        Args:
            context: Dictionary of context values to add to log records
        """
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context to the log record.
        
        Args:
            record: The log record to filter
            
        Returns:
            True to allow the record to be logged
        """
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color to console output based on log level.
    
    This makes it easier to visually distinguish between different log levels
    when viewing logs in the console.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with color.
        
        Args:
            record: The log record to format
            
        Returns:
            Formatted log string with color codes
        """
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # Format the message
        result = super().format(record)
        
        # Reset levelname for other formatters
        record.levelname = levelname
        
        return result


def setup_logging(
    log_level: str = "INFO",
    log_format: Optional[str] = None,
    enable_colors: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Configure application-wide logging with structured format.
    
    This function sets up logging with:
    - Configurable log level
    - Structured log format with timestamps and context
    - Optional colored console output
    - Optional file logging
    - Proper handler configuration for all loggers
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string (uses default if None)
        enable_colors: Whether to enable colored console output
        log_file: Optional path to log file for persistent logging
    """
    # Default structured log format with timestamp and context
    if log_format is None:
        log_format = (
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(filename)s:%(lineno)d] - %(message)s'
        )
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Remove any existing handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set root logger level
    root_logger.setLevel(numeric_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Use colored formatter for console if enabled
    if enable_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(
            log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(numeric_level)
            
            # File logs should not have colors
            file_formatter = logging.Formatter(
                log_format,
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"File logging enabled: {log_file}")
        except Exception as e:
            root_logger.error(f"Failed to setup file logging: {e}")
    
    # Configure third-party library loggers to reduce noise
    # Set higher log level for noisy libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    root_logger.info(f"Logging configured: level={log_level}, format=structured")


def get_logger(name: str, context: Optional[dict] = None) -> logging.Logger:
    """
    Get a logger instance with optional context.
    
    This function returns a logger configured with the application's
    logging settings and optionally adds context information.
    
    Args:
        name: Name of the logger (typically __name__ of the module)
        context: Optional dictionary of context to add to all log records
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add context filter if context is provided
    if context:
        context_filter = ContextFilter(context)
        logger.addFilter(context_filter)
    
    return logger


def log_function_call(logger: logging.Logger, func_name: str, **kwargs) -> None:
    """
    Log a function call with its parameters.
    
    Useful for debugging and tracing execution flow.
    
    Args:
        logger: Logger instance to use
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    params = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"Calling {func_name}({params})")


def log_execution_time(logger: logging.Logger, operation: str, start_time: datetime) -> None:
    """
    Log the execution time of an operation.
    
    Args:
        logger: Logger instance to use
        operation: Description of the operation
        start_time: Start time of the operation
    """
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"{operation} completed in {duration:.2f} seconds")


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds job context to all log messages.
    
    This adapter automatically prefixes log messages with job information,
    making it easier to trace job execution in logs.
    """
    
    def process(self, msg, kwargs):
        """
        Process the log message to add context.
        
        Args:
            msg: The log message
            kwargs: Additional keyword arguments
            
        Returns:
            Tuple of (message, kwargs)
        """
        job_name = self.extra.get('job_name')
        if job_name:
            return f"[{job_name}] {msg}", kwargs
        return msg, kwargs


def get_job_logger(job_name: str) -> LoggerAdapter:
    """
    Get a logger adapter configured for a specific job.
    
    This logger automatically adds the job name to all log messages,
    making it easier to filter and trace job execution.
    
    Args:
        job_name: Name of the job
        
    Returns:
        LoggerAdapter configured with job context
    """
    logger = logging.getLogger('app.executor.job_executor')
    return LoggerAdapter(logger, {'job_name': job_name})
