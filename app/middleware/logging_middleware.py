"""
Logging middleware for FastAPI to log all API requests and responses.

This middleware provides structured logging of HTTP requests and responses,
including timing information, status codes, and error details.
"""
import logging
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming HTTP requests and outgoing responses.
    
    This middleware logs:
    - Request method, path, and query parameters
    - Request headers (excluding sensitive data)
    - Response status code
    - Response time
    - Error details for failed requests
    """
    
    def __init__(self, app: ASGIApp, log_request_body: bool = False):
        """
        Initialize the logging middleware.
        
        Args:
            app: The ASGI application
            log_request_body: Whether to log request bodies (default: False)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            The HTTP response
        """
        # Generate a unique request ID for tracing
        request_id = id(request)
        
        # Record start time
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"[ID: {request_id}]"
        )
        
        # Log query parameters if present
        if request.url.query:
            logger.debug(f"Query params [ID: {request_id}]: {request.url.query}")
        
        # Log request body if enabled (for debugging)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON for better formatting
                    try:
                        body_json = json.loads(body)
                        logger.debug(
                            f"Request body [ID: {request_id}]: "
                            f"{json.dumps(body_json, indent=2)}"
                        )
                    except json.JSONDecodeError:
                        logger.debug(f"Request body [ID: {request_id}]: {body.decode()}")
            except Exception as e:
                logger.warning(f"Failed to read request body [ID: {request_id}]: {e}")
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate response time
            duration = time.time() - start_time
            duration_ms = duration * 1000
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[ID: {request_id}] - Status: {response.status_code} - "
                f"Duration: {duration_ms:.2f}ms"
            )
            
            # Log warning for slow requests (> 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} "
                    f"took {duration:.2f}s"
                )
            
            return response
            
        except Exception as e:
            # Calculate response time even for errors
            duration = time.time() - start_time
            duration_ms = duration * 1000
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[ID: {request_id}] - Error: {str(e)} - "
                f"Duration: {duration_ms:.2f}ms",
                exc_info=True
            )
            
            # Re-raise the exception to be handled by FastAPI
            raise


def log_api_call(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    error: str = None
) -> None:
    """
    Log an API call with structured information.
    
    This is a utility function for manual API call logging when not using
    the middleware (e.g., for internal API calls).
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        error: Optional error message
    """
    log_data = {
        'method': method,
        'path': path,
        'status_code': status_code,
        'duration_ms': duration_ms,
    }
    
    if error:
        log_data['error'] = error
        logger.error(f"API call failed: {json.dumps(log_data)}")
    else:
        logger.info(f"API call: {json.dumps(log_data)}")
