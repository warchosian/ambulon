"""
Configuration management for LLM module.

Uses the centralized ConfigManager for consistent configuration handling
across all Ambulon modules.
"""

import logging
import os
from typing import Any, Dict, Optional

from app.core.config_manager import ConfigManager

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
                "enabled": True,
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
                "model": "qwen2.5:1.5b",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "local_llama3_1_8b": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "llama3.1:8b",
                "temperature": 0.7,
                "max_tokens": 16384,
            },
            "local_qwen2_5_1_5b": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "qwen2.5:1.5b",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "local_phi3_mini": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "phi3:mini",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "cloud_gpt_oss_120b": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "gpt-oss:120b-cloud",
                "temperature": 0.7,
                "max_tokens": 16384,
            },
            "cloud_gpt_oss_20b": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "gpt-oss:20b-cloud",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "cloud_qwen3_coder_480b": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "qwen3-coder:480b-cloud",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "cloud_deepseek_v3_1_671b": {
                "enabled": True,
                "base_url": "http://localhost:11434/v1",
                "api_key": "local",
                "model": "deepseek-v3.1:671b-cloud",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "glm": {
                "enabled": True,
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key": "",
                "model": "glm-5.1-cloud",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
            },
            "qwen": {
                "enabled": True,
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "model": "qwen-3.6-max",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
            },
            "deepseek": {
                "enabled": True,
                "base_url": "https://api.deepseek.com/chat/completions",
                "api_key": "",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
            },
            # Cloud providers with standardized names
            "cloud_kimi": {
                "enabled": True,
                "base_url": "https://api.moonshot.cn/v1",
                "api_key": "",
                "model": "moonshot-v1-128k",
                "temperature": 0.7,
                "max_tokens": 16384,
                "retry_delay": 2,
            },
            "cloud_kimi_k2": {
                "enabled": True,
                "base_url": "https://api.moonshot.cn/v1",
                "api_key": "",
                "model": "kimi-k2.6:cloud",
                "temperature": 0.7,
                "max_tokens": 16384,
                "retry_delay": 2,
            },
            "cloud_glm": {
                "enabled": True,
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key": "",
                "model": "glm-5.1-cloud",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
                "ssl_verify": False,
            },
            "cloud_glm_4_7": {
                "enabled": True,
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "api_key": "",
                "model": "glm-4.7-flash",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
                "ssl_verify": False,
            },
            "cloud_qwen": {
                "enabled": True,
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key": "",
                "model": "qwen-3.6-max",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
            },
            "cloud_deepseek": {
                "enabled": True,
                "base_url": "https://api.deepseek.com/chat/completions",
                "api_key": "",
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
            },
            "cloud_deepseek_v4": {
                "enabled": True,
                "base_url": "https://api.deepseek.com/chat/completions",
                "api_key": "",
                "model": "deepseek-v4-flash",
                "temperature": 0.7,
                "max_tokens": 8192,
                "retry_delay": 2,
            },
            "cloud_claude": {
                "enabled": True,
                "base_url": "https://api.anthropic.com/v1",
                "api_key": "",
                "model": "claude-3-haiku-20240307",
                "temperature": 1.0,
                "max_tokens": 4096,
            },
            "cloud_chatgpt": {
                "enabled": True,
                "base_url": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4-turbo-preview",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            "cloud_gemini": {
                "enabled": True,
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "api_key": "",
                "model": "gemini-2.5-flash",
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


# Global config manager instance
_config_manager = ConfigManager(
    module_name="llm",
    defaults=DEFAULT_LLM_CONFIG,
    env_prefix="AMBULON_LLM",
    sensitive_keys=["api_key", "token"]
)


def load_llm_config(
    config_file: Optional[str] = None,
    cli_overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load LLM configuration using the centralized ConfigManager.

    Configuration hierarchy:
    1. Command-line arguments (cli_overrides)
    2. YAML configuration file
    3. Environment variables (AMBULON_LLM_*)
    4. Default values

    Args:
        config_file: Optional path to config file. If None, looks up
            ``llm.yaml`` via the standard AMBULON_HOME / cwd search.
        cli_overrides: CLI argument overrides in format {'llm.providers.kimi.api_key': value}

    Returns:
        Configuration dictionary.
    """
    return _config_manager.load(
        config_path=config_file or "llm.yaml",
        cli_overrides=cli_overrides
    )


def get_config_manager() -> ConfigManager:
    """Get the LLM ConfigManager instance for advanced operations."""
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
        # List available for debugging
        available = list(config.get("llm", {}).get("providers", {}).keys())
        raise ValueError(f"Provider '{provider_name}' not found. Available: {available}")


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
        "glm": "GLM_API_KEY",
        "qwen": "ALIBABA_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "alibaba": "ALIBABA_API_KEY",
        "local": "LOCAL_LLM_API_KEY",
        # Cloud provider names
        "cloud_kimi": "KIMI_API_KEY",
        "cloud_kimi_k2": "KIMI_API_KEY",
        "cloud_chatgpt": "OPENAI_API_KEY",
        "cloud_claude": "ANTHROPIC_API_KEY",
        "cloud_gemini": "GEMINI_API_KEY",
        "cloud_glm": "GLM_API_KEY",
        "cloud_glm_4_7": "GLM_API_KEY",
        "cloud_qwen": "ALIBABA_API_KEY",
        "cloud_deepseek": "DEEPSEEK_API_KEY",
        "cloud_deepseek_v4": "DEEPSEEK_API_KEY",
        "cloud_gpt_oss_120b": "LOCAL_LLM_API_KEY",
        "cloud_gpt_oss_20b": "LOCAL_LLM_API_KEY",
        "cloud_qwen3_coder_480b": "LOCAL_LLM_API_KEY",
        "cloud_deepseek_v3_1_671b": "LOCAL_LLM_API_KEY",
    }

    env_var = env_var_names.get(provider_name)
    if env_var:
        env_key = os.getenv(env_var)
        if env_key:
            return env_key

    raise ValueError(
        f"API key for provider '{provider_name}' not found. "
        f"Set {env_var or 'appropriate'} environment variable or configure 'llm.providers.{provider_name}.api_key' in config/llm.yaml"
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
