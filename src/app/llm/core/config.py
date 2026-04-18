"""
Configuration management for LLM module.

Supports configuration hierarchy:
1. Command-line arguments (highest priority)
2. YAML configuration file
3. Environment variables
4. Default values
"""

import os
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


def load_llm_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load LLM configuration from YAML file with environment variable substitution.

    Args:
        config_file: Optional path to config file. If None, uses default location.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file is specified but doesn't exist
    """
    # Default configuration
    default_config = {
        "llm": {
            "default_provider": "kimi",
            "timeout": 120,
            "max_retries": 3,
            "enable_streaming": False,
            "providers": {
                "kimi": {
                    "enabled": True,
                    "base_url": "https://api.moonshot.cn/v1",
                    "api_key": "",
                    "model": "moonshot-v1-8k",
                    "temperature": 0.7,
                    "max_tokens": 4096,
                    "retry_delay": 2
                },
                "chatgpt": {
                    "enabled": False,
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "",
                    "model": "gpt-4-turbo-preview",
                    "temperature": 0.7,
                    "max_tokens": 4096
                },
                "claude": {
                    "enabled": False,
                    "base_url": "https://api.anthropic.com/v1",
                    "api_key": "",
                    "model": "claude-3-opus-20240229",
                    "temperature": 1.0,
                    "max_tokens": 4096
                }
            },
            "documents": {
                "separator": "\n\n---\n\n",
                "include_metadata": True,
                "allowed_extensions": [".md", ".markdown", ".txt"],
                "default_encoding": "utf-8"
            },
            "output": {
                "default_file": "response.md",
                "create_output_dir": True,
                "save_metadata": True,
                "metadata_filename": "generation_metadata.json"
            }
        }
    }

    # Determine config file path
    if config_file:
        config_path = Path(config_file)
    else:
        # Try multiple default locations in order
        search_paths = []

        # 1. Current directory config/llm.yaml
        search_paths.append(Path.cwd() / "config" / "llm.yaml")

        # 2. AMBULON_HOME/config/llm.yaml
        ambulon_home = os.getenv("AMBULON_HOME")
        if ambulon_home:
            search_paths.append(Path(ambulon_home).expanduser() / "config" / "llm.yaml")

        # Find first existing config file
        config_path = None
        for path in search_paths:
            if path.exists():
                config_path = path
                break

        # If none found, use first default location
        if not config_path:
            config_path = search_paths[0]

    # If config doesn't exist, return defaults
    if not config_path.exists():
        logger.debug(f"Config file not found: {config_path}, using defaults")
        return default_config

    logger.info(f"Loading LLM config from: {config_path}")

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


def get_provider_config(provider_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get provider-specific configuration.

    Args:
        provider_name: Provider name (kimi, chatgpt, claude)
        config: Full configuration dictionary

    Returns:
        Provider configuration

    Raises:
        ValueError: If provider not found in config
    """
    try:
        provider_config = config["llm"]["providers"][provider_name]
        return provider_config
    except KeyError:
        raise ValueError(f"Provider '{provider_name}' not found in configuration")


def get_api_key(provider_name: str, config: Dict[str, Any]) -> str:
    """
    Get API key for provider.

    Hierarchy:
    1. Provider config (from YAML or CLI override)
    2. Environment variable (KIMI_API_KEY, OPENAI_API_KEY, etc.)
    3. Error if not found

    Args:
        provider_name: Provider name
        config: Configuration dictionary

    Returns:
        API key

    Raises:
        ValueError: If API key not found
    """
    provider_config = get_provider_config(provider_name, config)

    # Try config first (may have come from CLI or YAML)
    api_key = provider_config.get("api_key", "")
    if api_key:
        return api_key

    # Try environment variable
    env_var_names = {
        "kimi": "KIMI_API_KEY",
        "chatgpt": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY"
    }

    env_var = env_var_names.get(provider_name)
    if env_var:
        env_key = os.getenv(env_var)
        if env_key:
            return env_key

    raise ValueError(
        f"API key for provider '{provider_name}' not found. "
        f"Set {env_var} environment variable or configure 'llm.providers.{provider_name}.api_key' in config/llm.yaml"
    )


def get_base_url(provider_name: str, config: Dict[str, Any]) -> str:
    """
    Get base URL for provider.

    Args:
        provider_name: Provider name
        config: Configuration dictionary

    Returns:
        Base URL
    """
    provider_config = get_provider_config(provider_name, config)
    return provider_config.get("base_url", "")


def get_default_provider(config: Dict[str, Any]) -> str:
    """
    Get default provider name from config.

    Args:
        config: Configuration dictionary

    Returns:
        Default provider name
    """
    return config.get("llm", {}).get("default_provider", "kimi")


def get_timeout(config: Dict[str, Any]) -> int:
    """
    Get timeout value from config.

    Args:
        config: Configuration dictionary

    Returns:
        Timeout in seconds
    """
    return config.get("llm", {}).get("timeout", 120)


def is_streaming_enabled(config: Dict[str, Any]) -> bool:
    """
    Check if streaming is enabled by default.

    Args:
        config: Configuration dictionary

    Returns:
        True if streaming enabled, False otherwise
    """
    return config.get("llm", {}).get("enable_streaming", False)
