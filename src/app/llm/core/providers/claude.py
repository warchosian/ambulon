"""
Claude (Anthropic) provider implementation.

API Documentation: https://docs.anthropic.com/claude/reference/messages_post
"""

import json
import logging
import time
from typing import Iterator, Dict, Any, List
import requests

from app.llm.core.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseProvider):
    """
    Claude (Anthropic) API provider.

    Uses Anthropic Messages API.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            base_url: Base URL (default: https://api.anthropic.com/v1)
            config: Provider configuration dict
        """
        super().__init__(api_key, base_url, config)

        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        })

        # Provider defaults
        self.default_model = config.get("model", "claude-3-opus-20240229")
        self.default_temperature = config.get("temperature", 1.0)
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
            prompt: System prompt (sent as 'system' parameter)
            context: User context/input (sent as 'user' role message)
            model: Model name (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens (optional)
            **kwargs: Additional parameters

        Returns:
            Dict with keys: content, tokens, model, metadata
        """
        url = f"{self.base_url}/messages"

        payload = {
            "model": model or self.default_model,
            "system": prompt,
            "messages": [
                {"role": "user", "content": context}
            ],
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            "stream": False
        }

        logger.debug(f"Claude API request: {url}")
        logger.debug(f"Model: {payload['model']}")

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()

                # Extract response
                # Anthropic response format: data['content'][0]['text']
                content = ""
                for item in data.get("content", []):
                    if item.get("type") == "text":
                        content += item.get("text", "")

                usage = data.get("usage", {})

                result = {
                    "content": content,
                    "tokens": {
                        "prompt_tokens": usage.get("input_tokens", 0),
                        "completion_tokens": usage.get("output_tokens", 0),
                        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                    },
                    "model": data.get("model", payload["model"]),
                    "metadata": {
                        "id": data.get("id"),
                        "type": data.get("type"),
                        "role": data.get("role"),
                        "stop_reason": data.get("stop_reason"),
                        "stop_sequence": data.get("stop_sequence")
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
                # Log error details for debugging
                try:
                    error_details = e.response.json()
                    logger.error(f"API Error Response: {json.dumps(error_details, indent=2)}")
                except Exception:
                    logger.error(f"API Error Response (raw): {e.response.text}")

                if e.response.status_code < 500:
                    raise
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
        Generate response with streaming.

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
        url = f"{self.base_url}/messages"

        payload = {
            "model": model or self.default_model,
            "system": prompt,
            "messages": [
                {"role": "user", "content": context}
            ],
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            "stream": True
        }

        logger.debug(f"Claude API streaming request: {url}")

        response = self.session.post(url, json=payload, timeout=self.timeout, stream=True)
        response.raise_for_status()

        # Anthropic SSE format is slightly different from OpenAI
        # events: message_start, content_block_start, content_block_delta, content_block_stop, message_delta, message_stop
        # data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "..."}}

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8') if isinstance(line, bytes) else line

                if line.startswith('data: '):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        event_type = data.get("type")

                        if event_type == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield delta.get("text", "")
                        
                        elif event_type == "message_stop":
                            break

                    except json.JSONDecodeError:
                        continue

    def validate_connection(self) -> bool:
        """Test connection."""
        try:
            self.generate(prompt="Test", context="Hi", max_tokens=5)
            return True
        except Exception:
            return False

    def get_provider_name(self) -> str:
        return "claude"

    def get_supported_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620"
        ]
