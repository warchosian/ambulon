"""
Kimi (Moonshot AI) provider implementation.

API Documentation: https://platform.moonshot.cn/docs/api-reference
"""

import logging
from typing import Dict, Any, List

from app.llm.core.providers.openai_compatible import OpenAICompatibleProvider

logger = logging.getLogger(__name__)


class KimiProvider(OpenAICompatibleProvider):
    """
    Kimi (Moonshot AI) API provider.

    Uses OpenAI-compatible API endpoints.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize Kimi provider.

        Args:
            api_key: Kimi API key
            base_url: Base URL (default: https://api.moonshot.cn/v1)
            config: Provider configuration dict
        """
        if not base_url:
            base_url = "https://api.moonshot.cn/v1"
        super().__init__(api_key, base_url, config)

    def get_provider_name(self) -> str:
        """Get provider identifier."""
        return "kimi"

    def get_supported_models(self) -> List[str]:
        """Get list of supported Kimi models."""
        return [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k"
        ]
