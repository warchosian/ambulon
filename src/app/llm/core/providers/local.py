"""
Local LLM provider implementation (Ollama, LM Studio, vLLM, etc.).
"""

from typing import Dict, Any, List
from app.llm.core.providers.openai_compatible import OpenAICompatibleProvider


class LocalProvider(OpenAICompatibleProvider):
    """
    Local LLM provider using OpenAI-compatible API.
    Works well with Ollama, LM Studio, etc.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize local provider.

        Args:
            api_key: API key (often not needed for local, default to "local")
            base_url: Base URL (default: http://localhost:11434/v1 for Ollama)
            config: Provider configuration
        """
        # Default local URL if not provided
        if not base_url:
            base_url = "http://localhost:11434/v1"
        
        # Default key if not provided
        if not api_key:
            api_key = "local"

        super().__init__(api_key, base_url, config)

    def get_provider_name(self) -> str:
        """Get provider identifier."""
        return "local"

    def get_supported_models(self) -> List[str]:
        """
        Get list of commonly used local models.
        """
        return [
            "qwen2.5-7b",
            "qwen3.5-7b",  # Future-proofing as requested
            "gemma2-9b",
            "gemma4-9b",   # Future-proofing as requested
            "llama3.1-8b",
            "mistral-nemo"
        ]
