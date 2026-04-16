"""
GitHub configuration loader.

Loads GitHub configuration from config/github.yaml with environment variable substitution.
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

logger = logging.getLogger(__name__)


def load_github_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load GitHub configuration from YAML file with environment variable substitution.

    Configuration hierarchy (from highest to lowest priority):
    1. Command-line arguments (applied by caller)
    2. YAML configuration file
    3. Environment variables (via ${VAR:-default} substitution)
    4. Default values

    Args:
        config_path: Path to config file (default: config/github.yaml)

    Returns:
        Configuration dictionary with resolved values

    Example YAML:
        github:
          owner: "${GITHUB_OWNER:-warchosian}"
          repo: "${GITHUB_REPO:-ambulon}"
          token: "${GITHUB_TOKEN:-}"
    """
    # Default config path
    if not config_path:
        config_path = Path(__file__).parent.parent.parent.parent.parent / "config" / "github.yaml"
    else:
        config_path = Path(config_path)

    # Default configuration
    default_config = {
        "github": {
            "owner": "warchosian",
            "repo": "ambulon",
            "token": "",
            "release": {
                "draft": False,
                "prerelease": False,
                "generate_notes": False
            }
        }
    }

    # If config file doesn't exist, return defaults
    if not config_path.exists():
        logger.warning(f"GitHub config file not found: {config_path}. Using defaults.")
        return default_config

    try:
        # Read YAML file
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        # Substitute environment variables
        yaml_content = _substitute_env_vars(yaml_content)

        # Parse YAML
        config = yaml.safe_load(yaml_content)

        if not config:
            logger.warning(f"GitHub config file is empty: {config_path}")
            return default_config

        # Merge with defaults (config overrides defaults)
        merged_config = _deep_merge(default_config, config)

        logger.debug(f"Loaded GitHub config from {config_path}")
        return merged_config

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file {config_path}: {e}")
        return default_config
    except Exception as e:
        logger.error(f"Unexpected error loading GitHub config: {e}")
        return default_config


def _substitute_env_vars(content: str) -> str:
    """
    Substitute ${VAR:-default} patterns with environment variable values.

    Args:
        content: YAML content with ${VAR:-default} patterns

    Returns:
        Content with substituted values
    """
    def replace_env_var(match):
        var_expr = match.group(1)

        # Handle ${VAR:-default} syntax
        if ':-' in var_expr:
            var_name, default_value = var_expr.split(':-', 1)
            return os.getenv(var_name, default_value)

        # Handle ${VAR} syntax (required variable)
        var_name = var_expr
        value = os.getenv(var_name)
        if value is None:
            logger.warning(f"Required environment variable not set: {var_name}")
            return ""
        return value

    return re.sub(r'\$\{([^}]+)\}', replace_env_var, content)


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Override dictionary (values take precedence)

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


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
