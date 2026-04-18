"""
Provider registry for LLM integrations.
"""

from typing import Dict, Type, List
from app.llm.core.providers.base import BaseProvider
from app.llm.core.providers.kimi import KimiProvider

# Provider registry for dynamic loading
PROVIDERS: Dict[str, Type[BaseProvider]] = {
    'kimi': KimiProvider,
    # Future providers:
    # 'chatgpt': ChatGPTProvider,
    # 'claude': ClaudeProvider,
}


def get_provider(name: str, api_key: str, base_url: str, config: Dict) -> BaseProvider:
    """
    Factory function to instantiate providers.

    Args:
        name: Provider name (kimi, chatgpt, claude)
        api_key: API authentication key
        base_url: Base URL for API
        config: Provider configuration

    Returns:
        Instantiated provider

    Raises:
        ValueError: If provider name is unknown
    """
    if name not in PROVIDERS:
        available = list(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {name}. Available providers: {available}")

    provider_class = PROVIDERS[name]
    return provider_class(api_key=api_key, base_url=base_url, config=config)


def list_providers() -> List[str]:
    """
    List all registered providers.

    Returns:
        List of provider names
    """
    return list(PROVIDERS.keys())


__all__ = ["BaseProvider", "KimiProvider", "get_provider", "list_providers", "PROVIDERS"]
