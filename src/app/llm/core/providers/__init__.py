"""
Provider registry for LLM integrations.
"""

from typing import Dict, Type, List
from app.llm.core.providers.base import BaseProvider
from app.llm.core.providers.kimi import KimiProvider
from app.llm.core.providers.claude import ClaudeProvider
from app.llm.core.providers.local import LocalProvider
from app.llm.core.providers.chatgpt import ChatGPTProvider
from app.llm.core.providers.gemini import GeminiProvider
from app.llm.core.providers.openai_compatible import OpenAICompatibleProvider

# Provider registry for dynamic loading
PROVIDERS: Dict[str, Type[BaseProvider]] = {
    'kimi': KimiProvider,
    'claude': ClaudeProvider,
    'local': LocalProvider,
    'chatgpt': ChatGPTProvider,
    'gemini': GeminiProvider,
    # Cloud provider aliases (same implementation as non-cloud)
    'cloud_kimi': KimiProvider,
    'cloud_kimi_k2': KimiProvider,
    'cloud_claude': ClaudeProvider,
    'cloud_chatgpt': ChatGPTProvider,
    'cloud_gemini': GeminiProvider,
    # OpenAI-compatible cloud providers
    'cloud_glm': OpenAICompatibleProvider,
    'cloud_glm_4_7': OpenAICompatibleProvider,
    'cloud_qwen': OpenAICompatibleProvider,
    'cloud_deepseek': OpenAICompatibleProvider,
    'cloud_deepseek_v4': OpenAICompatibleProvider,
    # Ollama local models (with cloud naming convention)
    'cloud_gpt_oss_120b': OpenAICompatibleProvider,
    'cloud_gpt_oss_20b': OpenAICompatibleProvider,
    'cloud_qwen3_coder_480b': OpenAICompatibleProvider,
    'cloud_deepseek_v3_1_671b': OpenAICompatibleProvider,
    'cloud_minimax_2_7': OpenAICompatibleProvider,
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
