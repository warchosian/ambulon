"""
Configuration management for GitLab releases module.

Uses the centralized ConfigManager for consistent configuration handling
across all Ambulon modules.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_GITLAB_CONFIG: Dict[str, Any] = {
    "gitlab": {
        "token": "",
        "base_url": "https://gitlab.com",
        "project_id": "",
        "release": {
            "auto_generate_notes": False
        }
    }
}

# Global config manager instance
_config_manager = ConfigManager(
    module_name="gitlab",
    defaults=DEFAULT_GITLAB_CONFIG,
    env_prefix="AMBULON_GITLAB",
    sensitive_keys=["token"]
)


def load_gitlab_config(
    config_file: Optional[str] = None,
    cli_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load GitLab configuration using the centralized ConfigManager.

    Configuration hierarchy:
    1. Command-line arguments (cli_overrides)
    2. YAML configuration file
    3. Environment variables (AMBULON_GITLAB_*)
    4. Default values

    Args:
        config_file: Optional path to config file. If None, uses default location.
        cli_overrides: CLI argument overrides in format {'gitlab.token': value}

    Returns:
        Configuration dictionary
    """
    return _config_manager.load(
        config_path=config_file or "gitlab.yaml",
        cli_overrides=cli_overrides
    )


def get_config_manager() -> ConfigManager:
    """Get the GitLab ConfigManager instance for advanced operations."""
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


def get_gitlab_token(config: Dict[str, Any]) -> str:
    """
    Get GitLab token from config or environment variable.

    Hierarchy:
    1. GITLAB_PRIVATE_TOKEN env var
    2. config['gitlab']['token']

    Args:
        config: Configuration dictionary

    Returns:
        GitLab token

    Raises:
        ValueError: If token is not found
    """
    # Try environment variable first
    env_token = os.getenv("GITLAB_PRIVATE_TOKEN")
    if env_token:
        return env_token

    # Try config
    try:
        token = config["gitlab"]["token"]
        if token:  # Non-empty string
            return token
    except (KeyError, TypeError):
        pass

    raise ValueError(
        "GitLab token not found. Set GITLAB_PRIVATE_TOKEN environment variable "
        "or configure 'gitlab.token' in config/gitlab.yaml"
    )


def get_base_url(config: Dict[str, Any]) -> str:
    """
    Get GitLab base URL from config.

    Args:
        config: Configuration dictionary

    Returns:
        Base URL
    """
    try:
        base_url = config["gitlab"]["base_url"]
        if base_url:
            return base_url
    except (KeyError, TypeError):
        pass

    return "https://gitlab.com"  # Default


def get_project_id(config: Dict[str, Any]) -> str:
    """
    Get GitLab project ID from config.

    Args:
        config: Configuration dictionary

    Returns:
        Project ID

    Raises:
        ValueError: If project_id is not found
    """
    try:
        project_id = config["gitlab"]["project_id"]
        if project_id:
            return str(project_id)
    except (KeyError, TypeError):
        pass

    raise ValueError(
        "GitLab project_id not found. Configure 'gitlab.project_id' in config/gitlab.yaml "
        "or pass --project-id argument"
    )
