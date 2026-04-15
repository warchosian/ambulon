"""
VS Code extension configuration.

This module loads recommended and redundant extensions for diagram visualization
from config/vscode.yaml.
"""

import logging
from pathlib import Path
from typing import Dict, List, Literal, TypedDict

import yaml

logger = logging.getLogger(__name__)

Priority = Literal["ESSENTIEL", "FORTEMENT RECOMMANDÉ", "OPTIONNEL"]


class ExtensionInfo(TypedDict):
    """Type definition for extension metadata."""
    description: str
    category: str
    priority: Priority


def _load_vscode_config() -> Dict:
    """Load VSCode extensions configuration from YAML file."""
    # Find config directory (go up from src/app/vscode/core to project root)
    try:
        config_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "vscode.yaml"
        config_path = config_path.resolve()  # Resolve to absolute path
    except Exception as e:
        logger.error(f"Failed to resolve config path: {e}")
        return {"recommended_extensions": {}, "extensions_to_remove": {}}

    # Check if config file exists
    if not config_path.exists():
        logger.warning(
            f"VSCode config file not found: {config_path}. "
            f"Using empty configuration. Please create config/vscode.yaml in the project root."
        )
        return {"recommended_extensions": {}, "extensions_to_remove": {}}

    # Check if parent directory exists
    if not config_path.parent.exists():
        logger.error(
            f"Config directory not found: {config_path.parent}. "
            f"Please create the 'config' directory in the project root."
        )
        return {"recommended_extensions": {}, "extensions_to_remove": {}}

    # Load YAML file
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

            if config is None:
                logger.warning(f"VSCode config file is empty: {config_path}")
                return {"recommended_extensions": {}, "extensions_to_remove": {}}

            if not isinstance(config, dict):
                logger.error(f"VSCode config file has invalid format (not a dictionary): {config_path}")
                return {"recommended_extensions": {}, "extensions_to_remove": {}}

            logger.debug(f"Loaded VSCode config from {config_path}")
            return config

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file {config_path}: {e}")
        return {"recommended_extensions": {}, "extensions_to_remove": {}}
    except PermissionError:
        logger.error(f"Permission denied reading config file: {config_path}")
        return {"recommended_extensions": {}, "extensions_to_remove": {}}
    except Exception as e:
        logger.error(f"Unexpected error loading VSCode config from {config_path}: {e}")
        return {"recommended_extensions": {}, "extensions_to_remove": {}}


# Load configuration from YAML
_CONFIG = _load_vscode_config()
RECOMMENDED_EXTENSIONS: Dict[str, ExtensionInfo] = _CONFIG.get("recommended_extensions", {})
EXTENSIONS_TO_REMOVE: Dict[str, str] = _CONFIG.get("extensions_to_remove", {})


def get_extensions_by_priority(priority: Priority) -> List[str]:
    """
    Get extension IDs filtered by priority level.

    Args:
        priority: Priority level to filter by

    Returns:
        List of extension IDs matching the priority
    """
    return [
        ext_id
        for ext_id, info in RECOMMENDED_EXTENSIONS.items()
        if info["priority"] == priority
    ]


def get_essential_extensions() -> List[str]:
    """Get list of essential extension IDs."""
    return get_extensions_by_priority("ESSENTIEL")


def get_recommended_extensions() -> List[str]:
    """Get list of strongly recommended extension IDs."""
    return get_extensions_by_priority("FORTEMENT RECOMMANDÉ")


def get_optional_extensions() -> List[str]:
    """Get list of optional extension IDs."""
    return get_extensions_by_priority("OPTIONNEL")
