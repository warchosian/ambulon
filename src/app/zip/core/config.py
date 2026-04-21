"""
Configuration management for ZIP module.

Uses the centralized ConfigManager for consistent configuration handling
across all Ambulon modules.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

#: ZIP default configuration.
DEFAULT_ZIP_CONFIG: Dict[str, Any] = {
    "zip": {
        "compression": {"level": 6, "recursive": True},
        "exclude": {"patterns": []},
        "encryption": {"password": "", "password_file": None},
    }
}

# Global config manager instance
_config_manager = ConfigManager(
    module_name="zip",
    defaults=DEFAULT_ZIP_CONFIG,
    env_prefix="AMBULON_ZIP",
    sensitive_keys=["password"]
)


def load_zip_config(
    config_file: Optional[str] = None,
    cli_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load ZIP configuration using the centralized ConfigManager.

    Configuration hierarchy:
    1. Command-line arguments (cli_overrides)
    2. YAML configuration file
    3. Environment variables (AMBULON_ZIP_*)
    4. Default values

    Args:
        config_file: Optional path to config file. If None, looks up
            ``zip.yaml`` via the standard AMBULON_HOME / cwd search.
        cli_overrides: CLI argument overrides in format {'zip.compression.level': value}

    Returns:
        Configuration dictionary.
    """
    return _config_manager.load(
        config_path=config_file or "zip.yaml",
        cli_overrides=cli_overrides
    )


def get_config_manager() -> ConfigManager:
    """Get the ZIP ConfigManager instance for advanced operations."""
    return _config_manager


# Backward-compat thin wrappers - deprecated, use ConfigManager directly
def substitute_env_vars(config: Any) -> Any:
    """Deprecated: Use ConfigManager directly."""
    import warnings
    warnings.warn("substitute_env_vars is deprecated, use ConfigManager", DeprecationWarning)
    return _config_manager._format_value(config)


def merge_configs(base: Dict, override: Dict) -> Dict:
    """Deprecated: Use ConfigManager directly."""
    import warnings
    warnings.warn("merge_configs is deprecated, use ConfigManager", DeprecationWarning)
    from app.core.config_loader import deep_merge
    return deep_merge(base, override)


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
