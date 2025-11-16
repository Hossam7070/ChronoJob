"""Storage management for scripts."""
import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from app.models.script import ScriptConfig

logger = logging.getLogger(__name__)

SCRIPTS_FILE = Path("data/scripts.json")


def _ensure_storage_exists():
    """Ensure the scripts storage file exists."""
    SCRIPTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SCRIPTS_FILE.exists():
        SCRIPTS_FILE.write_text("[]")
        logger.info(f"Created scripts storage file: {SCRIPTS_FILE}")


def save_script(script: ScriptConfig) -> None:
    """Save a script to storage."""
    _ensure_storage_exists()
    
    scripts = load_all_scripts()
    
    # Remove existing script with same name if it exists
    scripts = [s for s in scripts if s.script_name != script.script_name]
    
    # Add new script
    scripts.append(script)
    
    # Save to file
    with open(SCRIPTS_FILE, 'w') as f:
        json.dump(
            [s.model_dump() for s in scripts],
            f,
            indent=2,
            default=str
        )
    
    logger.info(f"Saved script '{script.script_name}' to storage")


def load_all_scripts() -> List[ScriptConfig]:
    """Load all scripts from storage."""
    _ensure_storage_exists()
    
    try:
        with open(SCRIPTS_FILE, 'r') as f:
            data = json.load(f)
            scripts = [ScriptConfig(**script_data) for script_data in data]
            logger.debug(f"Loaded {len(scripts)} script(s) from storage")
            return scripts
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse scripts file: {e}")
        return []
    except Exception as e:
        logger.error(f"Failed to load scripts: {e}")
        return []


def get_script(script_name: str) -> Optional[ScriptConfig]:
    """Get a specific script by name."""
    scripts = load_all_scripts()
    for script in scripts:
        if script.script_name == script_name:
            logger.debug(f"Found script '{script_name}'")
            return script
    logger.debug(f"Script '{script_name}' not found")
    return None


def delete_script(script_name: str) -> bool:
    """Delete a script from storage."""
    _ensure_storage_exists()
    
    scripts = load_all_scripts()
    original_count = len(scripts)
    
    # Filter out the script to delete
    scripts = [s for s in scripts if s.script_name != script_name]
    
    if len(scripts) == original_count:
        logger.warning(f"Script '{script_name}' not found for deletion")
        return False
    
    # Save updated list
    with open(SCRIPTS_FILE, 'w') as f:
        json.dump(
            [s.model_dump() for s in scripts],
            f,
            indent=2,
            default=str
        )
    
    logger.info(f"Deleted script '{script_name}' from storage")
    return True


def script_exists(script_name: str) -> bool:
    """Check if a script exists."""
    return get_script(script_name) is not None
