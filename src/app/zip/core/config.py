"""
Configuration management for ZIP module.

Supports configuration hierarchy:
1. Command-line arguments (highest priority)
2. YAML configuration file
3. Environment variables
4. Default values
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import re

logger = logging.getLogger(__name__)


def load_zip_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load ZIP configuration from YAML file with environment variable substitution.

    Args:
        config_file: Optional path to config file. If None, uses default location.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file is specified but doesn't exist
    """
    # Default configuration
    default_config = {
        "zip": {
            "compression": {
                "level": 6,
                "recursive": True
            },
            "exclude": {
                "patterns": []
            },
            "encryption": {
                "password": "",
                "password_file": None
            }
        }
    }

    # Determine config file path
    if config_file:
        config_path = Path(config_file)
    else:
        # Try default location
        ambulon_home = os.getenv("AMBULON_HOME")
        if ambulon_home:
            base_dir = Path(ambulon_home).expanduser()
        else:
            base_dir = Path.cwd()

        config_path = base_dir / "config" / "zip.yaml"

    # If config doesn't exist, return defaults
    if not config_path.exists():
        logger.debug(f"Config file not found: {config_path}, using defaults")
        return default_config

    logger.info(f"Loading ZIP config from: {config_path}")

    # Load YAML
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)

        # Substitute environment variables
        config = substitute_env_vars(raw_config or default_config)

        # Merge with defaults
        merged_config = merge_configs(default_config, config)

        return merged_config

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        return default_config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return default_config


def substitute_env_vars(config: Any) -> Any:
    """
    Recursively substitute environment variables in config.

    Syntax: ${VAR_NAME:-default_value}

    Args:
        config: Configuration object (dict, list, or str)

    Returns:
        Configuration with substituted values
    """
    if isinstance(config, dict):
        return {key: substitute_env_vars(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [substitute_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Pattern: ${VAR_NAME:-default}
        pattern = r'\$\{([^}:]+)(?::-(.*?))?\}'

        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2) or ""
            return os.getenv(var_name, default_value)

        return re.sub(pattern, replacer, config)
    else:
        return config


def merge_configs(base: Dict, override: Dict) -> Dict:
    """
    Merge two configuration dictionaries recursively.

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def get_compression_level(config: Dict[str, Any]) -> int:
    """
    Get compression level from config or environment variable.

    Hierarchy:
    1. AMBULON_ZIP_COMPRESSION env var
    2. config['zip']['compression']['level']
    3. Default: 6

    Args:
        config: Configuration dictionary

    Returns:
        Compression level (0-9)
    """
    # Try environment variable first
    env_level = os.getenv("AMBULON_ZIP_COMPRESSION")
    if env_level:
        try:
            level = int(env_level)
            if 0 <= level <= 9:
                return level
        except ValueError:
            pass

    # Try config
    try:
        level = config["zip"]["compression"]["level"]
        if isinstance(level, int) and 0 <= level <= 9:
            return level
    except (KeyError, TypeError):
        pass

    # Default
    return 6


def get_password(config: Dict[str, Any]) -> Optional[str]:
    """
    Get password from config or environment variable.

    Hierarchy:
    1. AMBULON_ZIP_PASSWORD env var
    2. config['zip']['encryption']['password']
    3. None

    Args:
        config: Configuration dictionary

    Returns:
        Password or None
    """
    # Try environment variable first
    env_password = os.getenv("AMBULON_ZIP_PASSWORD")
    if env_password:
        return env_password

    # Try config
    try:
        password = config["zip"]["encryption"]["password"]
        if password:  # Non-empty string
            return password
    except (KeyError, TypeError):
        pass

    return None


def get_password_file(config: Dict[str, Any]) -> Optional[Path]:
    """
    Get password file path from config.

    Args:
        config: Configuration dictionary

    Returns:
        Password file path or None
    """
    try:
        password_file = config["zip"]["encryption"]["password_file"]
        if password_file:
            return Path(password_file)
    except (KeyError, TypeError):
        pass

    return None


def get_exclude_patterns(config: Dict[str, Any]) -> list:
    """
    Get exclude patterns from config.

    Args:
        config: Configuration dictionary

    Returns:
        List of exclude patterns
    """
    try:
        patterns = config["zip"]["exclude"]["patterns"]
        if isinstance(patterns, list):
            return patterns
    except (KeyError, TypeError):
        pass

    return []


def is_recursive(config: Dict[str, Any]) -> bool:
    """
    Get recursive flag from config.

    Args:
        config: Configuration dictionary

    Returns:
        True if recursive
    """
    try:
        recursive = config["zip"]["compression"]["recursive"]
        if isinstance(recursive, bool):
            return recursive
    except (KeyError, TypeError):
        pass

    return True  # Default: recursive
