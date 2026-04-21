"""
GitHub configuration loader.

Thin wrapper around :mod:`app.core.config_loader` that knows the GitHub default
schema. Pre-4.1.0 this file reimplemented its own ``_deep_merge`` and
``_substitute_env_vars``; they are gone.
"""

import logging
import os
from typing import Any, Dict, Optional

from app.core.config_loader import load_config as _load_config

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


def load_github_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load GitHub configuration from YAML with environment variable substitution.

    Configuration hierarchy (from highest to lowest priority):
    1. Command-line arguments (applied by caller)
    2. YAML configuration file
    3. Environment variables (via ``${VAR:-default}`` substitution)
    4. Default values (:data:`DEFAULT_GITHUB_CONFIG`)

    Args:
        config_path: Path to config file. If not provided, falls back to
            the standard AMBULON_HOME / cwd / AMBULON_CONFIG_DIR lookup for
            ``github.yaml``.

    Returns:
        Configuration dictionary with resolved values.
    """
    # Delegate discovery + substitution + merge to the shared loader.
    return _load_config(
        config_path or "github",
        default_config=DEFAULT_GITHUB_CONFIG,
    )


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
