"""
Configuration management for ZIP module.

Supports configuration hierarchy:
1. Command-line arguments (highest priority)
2. YAML configuration file
3. Environment variables
4. Default values

Pre-4.1.0 this module owned its own ``substitute_env_vars`` and
``merge_configs`` helpers; they now live in :mod:`app.core.config_loader`
and the public wrappers ``substitute_env_vars`` / ``merge_configs`` remain as
thin aliases for backward compatibility.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config_loader import deep_merge as _deep_merge, load_config as _load_config

logger = logging.getLogger(__name__)

#: ZIP default configuration.
DEFAULT_ZIP_CONFIG: Dict[str, Any] = {
    "zip": {
        "compression": {"level": 6, "recursive": True},
        "exclude": {"patterns": []},
        "encryption": {"password": "", "password_file": None},
    }
}


def load_zip_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load ZIP configuration from YAML file with environment variable substitution.

    Delegates discovery, substitution and defaults-merge to
    :func:`app.core.config_loader.load_config`.

    Args:
        config_file: Optional path to config file. If None, looks up
            ``zip.yaml`` via the standard AMBULON_HOME / cwd search.

    Returns:
        Configuration dictionary.
    """
    return _load_config(config_file or "zip", default_config=DEFAULT_ZIP_CONFIG)


# Backward-compat thin wrappers around app.core.config_loader.
def substitute_env_vars(config: Any) -> Any:
    """Alias kept for backward compatibility; uses the shared substitution."""
    import re

    from app.core.config_loader import _replace_env_var

    if isinstance(config, dict):
        return {k: substitute_env_vars(v) for k, v in config.items()}
    if isinstance(config, list):
        return [substitute_env_vars(item) for item in config]
    if isinstance(config, str):
        return re.sub(r"\$\{([^}]+)\}", _replace_env_var, config)
    return config


def merge_configs(base: Dict, override: Dict) -> Dict:
    """Alias kept for backward compatibility; delegates to ``deep_merge``."""
    return _deep_merge(base, override)


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
