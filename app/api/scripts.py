"""API endpoints for script management and debugging."""

import logging
from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse

from app.models.script import ScriptCreate, ScriptConfig, ScriptTestRequest
from app.storage.script_storage import (
    save_script,
    load_all_scripts,
    get_script,
    delete_script,
    script_exists,
)
from app.executor.script_executor import (
    execute_script,
    ScriptExecutionError,
    ScriptTimeoutError,
    ScriptOutputError
)
from app.executor.data_fetcher import fetch_data, DataFetchError
from app.models.job import DataSource
from datetime import datetime
import pandas as pd
import traceback


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/create", response_model=ScriptConfig, status_code=status.HTTP_201_CREATED)
async def create_script(script_data: ScriptCreate):
    """
    Create a new script.
    
    Args:
        script_data: Script configuration data
        
    Returns:
        Created script configuration
        
    Raises:
        HTTPException: If script name already exists
    """
    logger.info(f"API: Creating new script '{script_data.script_name}'")
    
    # Check if script already exists
    if script_exists(script_data.script_name):
        logger.warning(f"API: Script creation failed - script '{script_data.script_name}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Script with name '{script_data.script_name}' already exists"
        )
    
    try:
        # Create script configuration
        now = datetime.now()
        script_config = ScriptConfig(
            script_name=script_data.script_name,
            description=script_data.description,
            script_content=script_data.script_content,
            created_at=now,
            updated_at=now,
        )
        
        # Save to storage
        logger.debug(f"API: Saving script '{script_data.script_name}' to storage")
        save_script(script_config)
        
        logger.info(f"API: Script '{script_data.script_name}' created successfully")
        return script_config
        
    except Exception as e:
        logger.error(f"API: Failed to create script '{script_data.script_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create script: {str(e)}"
        )


@router.put("/{script_name}", response_model=ScriptConfig)
async def update_script(script_name: str, script_data: ScriptCreate):
    """
    Update an existing script.
    
    Args:
        script_name: Current script name
        script_data: Updated script configuration data
        
    Returns:
        Updated script configuration
        
    Raises:
        HTTPException: If script not found or update fails
    """
    logger.info(f"API: Updating script '{script_name}'")
    
    # Check if script exists
    existing_script = get_script(script_name)
    if existing_script is None:
        logger.warning(f"API: Script update failed - script '{script_name}' not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Script '{script_name}' not found"
        )
    
    # If script name is changing, check if new name already exists
    if script_name != script_data.script_name and script_exists(script_data.script_name):
        logger.warning(f"API: Script update failed - new name '{script_data.script_name}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Script with name '{script_data.script_name}' already exists"
        )
    
    try:
        # Create updated script configuration, preserving created_at
        script_config = ScriptConfig(
            script_name=script_data.script_name,
            description=script_data.description,
            script_content=script_data.script_content,
            created_at=existing_script.created_at,
            updated_at=datetime.now(),
        )
        
        # If script name changed, delete old script
        if script_name != script_data.script_name:
            logger.debug(f"API: Script name changed from '{script_name}' to '{script_data.script_name}'")
            delete_script(script_name)
        
        # Save updated script to storage
        logger.debug(f"API: Saving updated script '{script_data.script_name}' to storage")
        save_script(script_config)
        
        logger.info(f"API: Script '{script_name}' updated successfully")
        return script_config
        
    except Exception as e:
        logger.error(f"API: Failed to update script '{script_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update script: {str(e)}"
        )


@router.get("", response_model=List[ScriptConfig])
async def list_scripts():
    """
    List all scripts.
    
    Returns:
        List of all script configurations
    """
    logger.info("API: Listing all scripts")
    try:
        scripts = load_all_scripts()
        logger.info(f"API: Retrieved {len(scripts)} script(s)")
        return scripts
    except Exception as e:
        logger.error(f"API: Failed to list scripts: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list scripts: {str(e)}"
        )


@router.get("/{script_name}", response_model=ScriptConfig)
async def get_script_details(script_name: str):
    """
    Get details of a specific script.
    
    Args:
        script_name: Unique script identifier
        
    Returns:
        Script configuration
        
    Raises:
        HTTPException: If script not found
    """
    logger.info(f"API: Retrieving script details for '{script_name}'")
    try:
        script = get_script(script_name)
        if script is None:
            logger.warning(f"API: Script '{script_name}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script '{script_name}' not found"
            )
        logger.info(f"API: Script '{script_name}' retrieved successfully")
        return script
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to retrieve script '{script_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve script: {str(e)}"
        )


@router.delete("/{script_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script_endpoint(script_name: str):
    """
    Delete a script.
    
    Args:
        script_name: Unique script identifier
        
    Raises:
        HTTPException: If script not found
    """
    logger.info(f"API: Deleting script '{script_name}'")
    
    try:
        success = delete_script(script_name)
        
        if not success:
            logger.warning(f"API: Script '{script_name}' not found in storage")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Script '{script_name}' not found"
            )
        
        logger.info(f"API: Script '{script_name}' deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to delete script '{script_name}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete script: {str(e)}"
        )


@router.post("/test")
async def test_script(test_request: ScriptTestRequest):
    """
    Test a script with sample data and return detailed results including errors.
    
    Args:
        test_request: Script test request with script content and test file path
        
    Returns:
        JSON response with execution results, output preview, and error logs
    """
    logger.info(f"API: Testing script with file '{test_request.test_file_path}'")
    
    try:
        # Load test data
        file_path = Path(test_request.test_file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test file not found: {test_request.test_file_path}"
            )
        
        # Determine file type and load data
        file_ext = file_path.suffix.lower()
        try:
            if file_ext == '.csv':
                input_df = pd.read_csv(file_path)
            elif file_ext == '.json':
                input_df = pd.read_json(file_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {file_ext}"
                )
            logger.info(f"API: Loaded test data. Shape: {input_df.shape}")
        except Exception as e:
            logger.error(f"API: Failed to load test data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to load test data: {str(e)}"
            )
        
        # Execute script
        try:
            result_df = execute_script(test_request.script_content, input_df)
            logger.info(f"API: Script executed successfully. Output shape: {result_df.shape}")
            
            # Prepare success response
            return JSONResponse(content={
                "success": True,
                "input_shape": list(input_df.shape),
                "output_shape": list(result_df.shape),
                "input_columns": list(input_df.columns),
                "output_columns": list(result_df.columns),
                "output_preview": result_df.head(10).to_dict(orient='records'),
                "output_dtypes": {col: str(dtype) for col, dtype in result_df.dtypes.items()},
                "error": None,
                "error_type": None,
                "traceback": None
            })
            
        except (ScriptExecutionError, ScriptTimeoutError, ScriptOutputError) as e:
            logger.error(f"API: Script execution failed: {str(e)}")
            
            # Get detailed traceback
            tb = traceback.format_exc()
            
            # Return error details
            return JSONResponse(
                status_code=status.HTTP_200_OK,  # Return 200 so frontend can handle gracefully
                content={
                    "success": False,
                    "input_shape": list(input_df.shape),
                    "output_shape": None,
                    "input_columns": list(input_df.columns),
                    "output_columns": None,
                    "output_preview": None,
                    "output_dtypes": None,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "traceback": tb
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to test script: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test script: {str(e)}"
        )


@router.post("/upload-test-file")
async def upload_test_file(file: UploadFile = File(...)):
    """
    Upload a test data file for script debugging.
    
    Args:
        file: The file to upload
        
    Returns:
        Dictionary with file path
    """
    logger.info(f"API: Uploading test file '{file.filename}'")
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.csv', '.json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_ext}. Only .csv and .json files are allowed."
            )
        
        # Create test uploads directory
        upload_dir = Path("data/uploads/test")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / file.filename
        
        # Write file content
        content = await file.read()
        file_path.write_bytes(content)
        
        logger.info(f"API: Test file '{file.filename}' uploaded successfully to {file_path}")
        
        return {
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: Failed to upload test file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload test file: {str(e)}"
        )
