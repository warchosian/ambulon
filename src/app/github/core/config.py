"""
GitHub configuration loader.

Uses the centralized ConfigManager for consistent configuration handling
across all Ambulon modules.
"""

import logging
import os
from typing import Any, Dict, Optional

from app.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

#: GitHub default config — caller can override any key via YAML.
DEFAULT_GITHUB_CONFIG: Dict[str, Any] = {
    "github": {
        "owner": "warchosian",
        "repo": "ambulon",
        "token": "",
        "release": {
            "draft": False,
            "prerelease": False,
            "generate_notes": False,
        },
    }
}

# Global config manager instance
_config_manager = ConfigManager(
    module_name="github",
    defaults=DEFAULT_GITHUB_CONFIG,
    env_prefix="AMBULON_GITHUB",
    sensitive_keys=["token"]
)


def load_github_config(
    config_path: Optional[str] = None,
    cli_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load GitHub configuration using the centralized ConfigManager.

    Configuration hierarchy (from highest to lowest priority):
    1. Command-line arguments (cli_overrides)
    2. YAML configuration file
    3. Environment variables (AMBULON_GITHUB_*)
    4. Default values

    Args:
        config_path: Path to config file. If not provided, falls back to
            the standard AMBULON_HOME / cwd lookup for ``github.yaml``.
        cli_overrides: CLI argument overrides in format {'github.token': value}

    Returns:
        Configuration dictionary with resolved values.
    """
    return _config_manager.load(
        config_path=config_path or "github.yaml",
        cli_overrides=cli_overrides
    )


def get_config_manager() -> ConfigManager:
    """Get the GitHub ConfigManager instance for advanced operations."""
    return _config_manager


def get_github_token(config: Dict[str, Any]) -> Optional[str]:
    """
    Get GitHub token from config or environment.

    Args:
        config: Configuration dictionary

    Returns:
        GitHub token or None

    Raises:
        ValueError: If token is not found
    """
    token = config.get("github", {}).get("token")

    # Try environment variable if not in config
    if not token:
        token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise ValueError(
            "GitHub token not found. Please provide via:\n"
            "  1. Environment variable: export GITHUB_TOKEN=your_token\n"
            "  2. Config file: config/github.yaml (github.token: ${GITHUB_TOKEN})\n"
            "  3. Command line: --token your_token"
        )

    return token
