"""
Centralized Configuration Loader for Ambulon

This module provides a standardized way to load configuration from multiple
sources, following a defined hierarchy:
1. Default values (provided by the calling module)
2. YAML file
3. Environment variables (substituted within the YAML file)
4. Command-line arguments (handled by the calling module after loading)
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

def deep_merge(base: Dict, override: Dict) -> Dict:
    """Recursively merges two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def _replace_env_var(match: re.Match) -> str:
    """
    Replaces ${VAR:-default} patterns with environment variable values.
    Raises ValueError if a variable is required but not set (e.g., ${VAR}).
    """
    var_expr = match.group(1)
    if ':-' in var_expr:
        var_name, default_value = var_expr.split(':-', 1)
        return os.getenv(var_name, default_value)
    else:
        var_name = var_expr
        value = os.getenv(var_name)
        if value is None:
            # For critical variables, it's better to fail fast.
            # Use ${VAR:-} for optional variables that can be empty.
            raise ValueError(f"Required environment variable '{var_name}' is not set.")
        return value

def load_config(
    config_path: Optional[str] = None,
    default_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Loads configuration from a YAML file, merging it with defaults.
    Performs environment variable substitution in the YAML file.

    Args:
        config_path: Path to the YAML configuration file.
        default_config: A dictionary containing default configuration values.

    Returns:
        A dictionary containing the merged configuration.
    """
    if yaml is None:
        print("Warning: PyYAML not installed, cannot load YAML config. Using defaults.", file=sys.stderr)
        return default_config or {}

    config = default_config or {}

    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_content = f.read()

            # Substitute environment variables
            yaml_content = re.sub(r'\$\{([^}]+)\}', _replace_env_var, yaml_content)

            yaml_config = yaml.safe_load(yaml_content)
            if yaml_config:
                # Merge YAML config over the defaults
                config = deep_merge(config, yaml_config)

        except Exception as e:
            print(f"Error loading or parsing config file at '{config_path}': {e}", file=sys.stderr)
            # In case of error, we stick with the defaults
            pass
            
    return config
