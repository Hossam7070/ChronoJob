"""Data fetcher module for retrieving data from external APIs and files."""

import logging
import asyncio
from pathlib import Path
from typing import Any, Dict
import pandas as pd
import httpx
from app.models.job import DataSource
from app.config import config


logger = logging.getLogger(__name__)


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass


async def fetch_from_api(url: str, max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch data from an external API with retry logic.
    
    Args:
        url: The API endpoint URL
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        pd.DataFrame: The fetched data as a Pandas DataFrame
    
    Raises:
        DataFetchError: If data fetching fails after all retries
    """
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            logger.info(f"Fetching data from API: {url} (attempt {retry_count + 1}/{max_retries})")
            
            async with httpx.AsyncClient(timeout=float(config.API_FETCH_TIMEOUT)) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # Convert to DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    # If dict, try to find the data array or convert dict to single-row DataFrame
                    if any(isinstance(v, list) for v in data.values()):
                        df = pd.DataFrame(data)
                    else:
                        df = pd.DataFrame([data])
                else:
                    raise DataFetchError(f"Unexpected data format from API: {type(data)}")
                
                logger.info(f"Successfully fetched {len(df)} rows from API")
                return df
                
        except httpx.TimeoutException as e:
            last_error = e
            logger.warning(f"Timeout fetching from API {url}: {str(e)}")
        except httpx.HTTPStatusError as e:
            last_error = e
            logger.warning(f"HTTP error fetching from API {url}: {e.response.status_code}")
        except (httpx.RequestError, ValueError, KeyError) as e:
            last_error = e
            logger.warning(f"Error fetching from API {url}: {str(e)}")
        
        retry_count += 1
        
        if retry_count < max_retries:
            # Exponential backoff: 2^retry_count seconds
            wait_time = 2 ** retry_count
            logger.info(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    # All retries exhausted
    error_msg = f"Failed to fetch data from API {url} after {max_retries} attempts. Last error: {str(last_error)}"
    logger.error(error_msg)
    raise DataFetchError(error_msg)


def fetch_from_file(file_path: str, file_type: str) -> pd.DataFrame:
    """
    Read data from a local file.
    
    Args:
        file_path: Path to the file
        file_type: Type of file ('csv' or 'json')
    
    Returns:
        pd.DataFrame: The file data as a Pandas DataFrame
    
    Raises:
        DataFetchError: If file reading fails
    """
    try:
        logger.info(f"Reading data from file: {file_path} (type: {file_type})")
        
        path = Path(file_path)
        
        if not path.exists():
            raise DataFetchError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise DataFetchError(f"Path is not a file: {file_path}")
        
        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "json":
            df = pd.read_json(file_path)
        else:
            raise DataFetchError(f"Unsupported file type: {file_type}")
        
        logger.info(f"Successfully read {len(df)} rows from file")
        return df
        
    except pd.errors.EmptyDataError as e:
        error_msg = f"File is empty: {file_path}"
        logger.error(error_msg)
        raise DataFetchError(error_msg)
    except pd.errors.ParserError as e:
        error_msg = f"Error parsing {file_type} file {file_path}: {str(e)}"
        logger.error(error_msg)
        raise DataFetchError(error_msg)
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(error_msg)
        raise DataFetchError(error_msg)


async def fetch_data(data_source: DataSource) -> pd.DataFrame:
    """
    Main function to fetch data from configured source.
    
    Routes to appropriate fetcher based on source_type.
    
    Args:
        data_source: DataSource configuration object
    
    Returns:
        pd.DataFrame: The fetched data as a Pandas DataFrame
    
    Raises:
        DataFetchError: If data fetching fails
    """
    try:
        if data_source.source_type == "api":
            return await fetch_from_api(data_source.location)
        elif data_source.source_type == "file":
            # Run synchronous file reading in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                fetch_from_file, 
                data_source.location, 
                data_source.file_type
            )
        else:
            raise DataFetchError(f"Unsupported source type: {data_source.source_type}")
    except DataFetchError:
        # Re-raise DataFetchError as-is
        raise
    except Exception as e:
        error_msg = f"Unexpected error fetching data: {str(e)}"
        logger.error(error_msg)
        raise DataFetchError(error_msg)
