"""
Script execution module for running user-provided Python scripts safely.
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
from typing import Any, Dict
from app.config import config

logger = logging.getLogger(__name__)


class ScriptExecutionError(Exception):
    """Raised when script execution fails."""
    pass


class ScriptTimeoutError(ScriptExecutionError):
    """Raised when script execution exceeds timeout."""
    pass


class ScriptOutputError(ScriptExecutionError):
    """Raised when script output is invalid."""
    pass


def execute_script(script_content: str, input_df: pd.DataFrame, timeout: int = None) -> pd.DataFrame:
    """
    Execute a user-provided Python script with a restricted execution environment.
    
    Args:
        script_content: The Python script code to execute
        input_df: The input Pandas DataFrame to pass to the script
        timeout: Maximum execution time in seconds (default: from config)
        
    Returns:
        pd.DataFrame: The output DataFrame returned by the script
        
    Raises:
        ScriptExecutionError: If script execution fails
        ScriptTimeoutError: If script execution exceeds timeout
        ScriptOutputError: If script output is not a valid DataFrame
    """
    # Use config timeout if not specified
    if timeout is None:
        timeout = config.SCRIPT_TIMEOUT
    
    logger.info(f"Starting script execution with timeout of {timeout} seconds")
    
    # Validate input
    if not isinstance(input_df, pd.DataFrame):
        raise ScriptExecutionError("Input data must be a Pandas DataFrame")
    
    if not script_content or not script_content.strip():
        raise ScriptExecutionError("Script content cannot be empty")
    
    # Set up restricted execution environment
    # Whitelist only safe imports and built-in functions
    import time
    
    safe_globals = {
        '__builtins__': {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'max': max,
            'min': min,
            'range': range,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'zip': zip,
        },
        'pd': pd,
        'pandas': pd,
        'np': np,
        'numpy': np,
        'datetime': datetime,
        'timedelta': timedelta,
        'time': time,
    }
    
    # Create local namespace with input data
    local_namespace: Dict[str, Any] = {
        'data': input_df.copy(),  # Pass a copy to prevent modification of original
        'result': None,
    }
    
    # Container for execution result and errors
    execution_result = {'completed': False, 'error': None, 'namespace': None}
    
    def run_script():
        """Execute the script in a separate thread."""
        try:
            logger.debug("Executing user script")
            exec(script_content, safe_globals, local_namespace)
            execution_result['namespace'] = local_namespace
            execution_result['completed'] = True
            logger.debug("Script execution completed successfully")
        except Exception as e:
            logger.error(f"Script execution error: {str(e)}", exc_info=True)
            execution_result['error'] = e
            execution_result['completed'] = True
    
    # Execute script in a separate thread with timeout
    execution_thread = threading.Thread(target=run_script, daemon=True)
    execution_thread.start()
    execution_thread.join(timeout=timeout)
    
    # Check if thread is still alive (timeout occurred)
    if execution_thread.is_alive():
        logger.error(f"Script execution exceeded timeout of {timeout} seconds")
        raise ScriptTimeoutError(f"Script execution exceeded timeout of {timeout} seconds")
    
    # Check if execution completed
    if not execution_result['completed']:
        raise ScriptExecutionError("Script execution did not complete")
    
    # Check for execution errors
    if execution_result['error']:
        error = execution_result['error']
        raise ScriptExecutionError(f"Script execution failed: {type(error).__name__}: {str(error)}")
    
    # Extract result from namespace
    result_namespace = execution_result['namespace']
    if result_namespace is None:
        raise ScriptExecutionError("Script execution namespace is empty")
    
    # Try to get result - check for 'result' variable first, then fall back to 'data'
    output_df = result_namespace.get('result')
    
    if output_df is None:
        # If no 'result' variable, check if 'data' was modified
        output_df = result_namespace.get('data')
        logger.info("No 'result' variable found, using 'data' as output")
    
    # Validate output is a DataFrame
    if not isinstance(output_df, pd.DataFrame):
        raise ScriptOutputError(
            f"Script must return a Pandas DataFrame. Got {type(output_df).__name__} instead. "
            "Assign your output DataFrame to a variable named 'result'."
        )
    
    if output_df.empty:
        logger.warning("Script returned an empty DataFrame")
    
    logger.info(f"Script execution successful. Output shape: {output_df.shape}")
    return output_df
