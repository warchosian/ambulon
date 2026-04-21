"""
ChatGPT (OpenAI) provider implementation.
"""

from typing import Dict, Any, List
from app.llm.core.providers.openai_compatible import OpenAICompatibleProvider


class ChatGPTProvider(OpenAICompatibleProvider):
    """
    ChatGPT (OpenAI) API provider.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize ChatGPT provider.

        Args:
            api_key: OpenAI API key
            base_url: Base URL (default: https://api.openai.com/v1)
            config: Provider configuration
        """
        if not base_url:
            base_url = "https://api.openai.com/v1"
        super().__init__(api_key, base_url, config)

    def get_provider_name(self) -> str:
        """Get provider identifier."""
        return "chatgpt"

    def get_supported_models(self) -> List[str]:
        """Get list of supported ChatGPT models."""
        return [
            "gpt-4o",
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
