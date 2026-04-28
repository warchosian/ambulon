"""
Google Gemini provider implementation.

API Documentation: https://ai.google.dev/gemini-api/docs/openai
"""

import logging
from typing import Dict, Any, List

from app.llm.core.providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)


class GeminiProvider(OpenAICompatibleProvider):
    """
    Google Gemini API provider.

    Uses OpenAI-compatible API endpoints provided by Google.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google Gemini API key
            base_url: Base URL (default: https://generativelanguage.googleapis.com/v1beta/openai)
            config: Provider configuration dict
        """
        # Google provides an OpenAI-compatible endpoint at this path
        if not base_url or "generativelanguage.googleapis.com" in base_url and "/openai" not in base_url:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
            
        super().__init__(api_key, base_url, config)

    def get_provider_name(self) -> str:
        """Get provider identifier."""
        return "gemini"

    def get_supported_models(self) -> List[str]:
        """Get list of supported Gemini models."""
        return [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]
