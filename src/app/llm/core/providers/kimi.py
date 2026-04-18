"""
Kimi (Moonshot AI) provider implementation.

API Documentation: https://platform.moonshot.cn/docs/api-reference
"""

import json
import logging
import time
from typing import Iterator, Dict, Any, List
import requests

from app.llm.core.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class KimiProvider(BaseProvider):
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
        super().__init__(api_key, base_url, config)

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

        # Provider defaults
        self.default_model = config.get("model", "moonshot-v1-8k")
        self.default_temperature = config.get("temperature", 0.7)
        self.default_max_tokens = config.get("max_tokens", 4096)
        self.timeout = config.get("timeout", 120)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 2)

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
            prompt: System prompt
            context: User context/input
            model: Model name (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens (optional)
            **kwargs: Additional parameters

        Returns:
            Dict with keys: content, tokens, model, metadata
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model or self.default_model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": context}
            ],
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            "stream": False
        }

        logger.debug(f"Kimi API request: {url}")
        logger.debug(f"Model: {payload['model']}")
        logger.debug(f"Temperature: {payload['temperature']}")
        logger.debug(f"Max tokens: {payload['max_tokens']}")

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()

                # Extract response
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {})

                result = {
                    "content": content,
                    "tokens": {
                        "prompt_tokens": tokens.get("prompt_tokens", 0),
                        "completion_tokens": tokens.get("completion_tokens", 0),
                        "total_tokens": tokens.get("total_tokens", 0)
                    },
                    "model": data.get("model", payload["model"]),
                    "metadata": {
                        "id": data.get("id"),
                        "created": data.get("created"),
                        "finish_reason": data["choices"][0].get("finish_reason")
                    }
                }

                logger.info(f"Generation successful. Tokens used: {result['tokens']['total_tokens']}")
                return result

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Request timeout. Retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    raise
            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if e.response.status_code < 500:
                    raise
                # Retry on 5xx errors (server errors)
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Server error {e.response.status_code}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

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
            prompt: System prompt
            context: User context/input
            model: Model name (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens (optional)
            **kwargs: Additional parameters

        Yields:
            Text chunks as they are generated
        """
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model or self.default_model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": context}
            ],
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            "stream": True
        }

        logger.debug(f"Kimi API streaming request: {url}")
        logger.debug(f"Model: {payload['model']}")

        response = self.session.post(url, json=payload, timeout=self.timeout, stream=True)
        response.raise_for_status()

        # Process Server-Sent Events (SSE)
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8') if isinstance(line, bytes) else line

                # SSE format: "data: <json>"
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix

                    if data == '[DONE]':
                        break

                    try:
                        chunk = json.loads(data)

                        # Extract delta content
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')

                            if content:
                                yield content

                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON chunk: {data}")
                        continue

    def validate_connection(self) -> bool:
        """
        Test API connectivity.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Send minimal test request
            test_response = self.generate(
                prompt="Test connection",
                context="Hello",
                max_tokens=5
            )
            return test_response is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

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
