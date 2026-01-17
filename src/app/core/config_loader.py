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

def find_config_file(config_name: str) -> Optional[Path]:
    """
    Searches for a configuration file in multiple locations.

    Search order:
    1. Current directory: ./config/<config_name>.yaml
    2. User config directory: ~/.config/ambulon/<config_name>.yaml
    3. Environment variable: $AMBULON_CONFIG_DIR/<config_name>.yaml

    Args:
        config_name: Name of the config file (without .yaml extension)

    Returns:
        Path to the config file if found, None otherwise.
    """
    search_paths = [
        # 1. Current directory
        Path.cwd() / "config" / f"{config_name}.yaml",
        # 2. User config directory
        Path.home() / ".config" / "ambulon" / f"{config_name}.yaml",
    ]

    # 3. Environment variable directory
    env_config_dir = os.getenv("AMBULON_CONFIG_DIR")
    if env_config_dir:
        search_paths.append(Path(env_config_dir) / f"{config_name}.yaml")

    for path in search_paths:
        if path.exists():
            return path

    return None

def load_config(
    config_path: Optional[str] = None,
    default_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Loads configuration from a YAML file, merging it with defaults.
    Performs environment variable substitution in the YAML file.

    Args:
        config_path: Path to the YAML configuration file. Can be:
                    - Absolute path (e.g., /home/user/config/gitlab.yaml)
                    - Relative path (e.g., config/gitlab.yaml)
                    - Config name only (e.g., gitlab) - will search in standard locations
        default_config: A dictionary containing default configuration values.

    Returns:
        A dictionary containing the merged configuration.
    """
    if yaml is None:
        print("Warning: PyYAML not installed, cannot load YAML config. Using defaults.", file=sys.stderr)
        return default_config or {}

    config = default_config or {}

    if config_path:
        # Expand ~ and environment variables in the path
        expanded_path = Path(config_path).expanduser()

        # If path doesn't exist and looks like just a name (no path separators),
        # try to find it in standard locations
        if not expanded_path.exists() and "/" not in config_path and "\\" not in config_path:
            # Remove .yaml extension if present
            config_name = config_path.replace(".yaml", "")
            found_path = find_config_file(config_name)
            if found_path:
                expanded_path = found_path

        if expanded_path.exists():
            try:
                with open(expanded_path, 'r', encoding='utf-8') as f:
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
