"""
Base provider abstract class for LLM integrations.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, List


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.

    All providers must implement this interface to be compatible
    with the llm module.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize provider.

        Args:
            api_key: API authentication key
            base_url: Base URL for API endpoints
            config: Provider-specific configuration
        """
        self.api_key = api_key
        self.base_url = base_url
        self.config = config

    @abstractmethod
    def generate(
        self,
        prompt: str,
        context: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate response (non-streaming).

        Args:
            prompt: System prompt for the LLM
            context: User context/input
            model: Model name (optional, uses default if None)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum response tokens (optional)
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary with keys:
                - content: Generated text
                - tokens: Token usage dict (prompt_tokens, completion_tokens, total_tokens)
                - model: Model used
                - metadata: Additional provider metadata

        Raises:
            requests.HTTPError: If API call fails
        """
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        context: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Generate response with streaming (SSE).

        Args:
            prompt: System prompt for the LLM
            context: User context/input
            model: Model name (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum response tokens (optional)
            **kwargs: Additional provider-specific parameters

        Yields:
            Text chunks as they are generated

        Raises:
            requests.HTTPError: If API call fails
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Test API connectivity and authentication.

        Returns:
            True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get provider identifier.

        Returns:
            Provider name (e.g., "kimi", "chatgpt", "claude")
        """
        pass

    def get_supported_models(self) -> List[str]:
        """
        Get list of supported models.

        Returns:
            List of model names

        Note:
            Default implementation returns empty list.
            Providers should override this method.
        """
        return []
