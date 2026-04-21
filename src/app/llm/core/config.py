"""
Configuration management for LLM module.

Supports configuration hierarchy:
1. Command-line arguments (highest priority)
2. YAML configuration file
3. Environment variables (``${VAR:-default}`` substitution)
4. Default values (:data:`DEFAULT_LLM_CONFIG`)

Pre-4.1.0 this module re-implemented its own ``substitute_env_vars`` and
``merge_configs`` helpers; they now delegate to :mod:`app.core.config_loader`.
"""

import logging
import os
from typing import Any, Dict, Optional

from app.core.config_loader import deep_merge as _deep_merge, load_config as _load_config

logger = logging.getLogger(__name__)

#: LLM default configuration.
DEFAULT_LLM_CONFIG: Dict[str, Any] = {
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
                "retry_delay": 2,
            },
            "chatgpt": {
                "enabled": False,
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "claude": {
                "enabled": False,
                "base_url": "https://api.anthropic.com/v1",
                "api_key": "",
                "model": "claude-3-opus-20240229",
                "temperature": 1.0,
                "max_tokens": 4096,
            },
            "local": {
                "enabled": False,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "qwen2.5-7b",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
        },
        "documents": {
            "separator": "\n\n---\n\n",
            "include_metadata": True,
            "allowed_extensions": [".md", ".markdown", ".txt"],
            "default_encoding": "utf-8",
        },
        "output": {
            "default_file": "response.md",
            "create_output_dir": True,
            "save_metadata": True,
            "metadata_filename": "generation_metadata.json",
        },
    }
}


def load_llm_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load LLM configuration from YAML with environment variable substitution.

    Args:
        config_file: Optional path to config file. If None, looks up
            ``llm.yaml`` via the standard AMBULON_HOME / cwd search.

    Returns:
        Configuration dictionary.
    """
    return _load_config(config_file or "llm", default_config=DEFAULT_LLM_CONFIG)


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
        "claude": "ANTHROPIC_API_KEY",
        "local": "LOCAL_LLM_API_KEY"
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
