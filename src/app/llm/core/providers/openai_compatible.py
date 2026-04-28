"""
OpenAI-compatible provider implementation.
Can be used for OpenAI, Kimi, and local servers like Ollama or vLLM.
"""

import json
import logging
import time
from typing import Iterator, Dict, Any, List
import requests

from app.llm.core.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseProvider):
    """
    Generic OpenAI-compatible API provider.
    """

    def __init__(self, api_key: str, base_url: str, config: Dict[str, Any]):
        """
        Initialize provider.

        Args:
            api_key: API key
            base_url: Base URL (e.g., https://api.openai.com/v1)
            config: Provider configuration dict
        """
        super().__init__(api_key, base_url, config)

        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
        else:
            self.session.headers.update({
                "Content-Type": "application/json"
            })

        # Provider defaults
        self.default_model = config.get("model")
        self.default_temperature = config.get("temperature", 0.7)
        self.default_max_tokens = config.get("max_tokens", 4096)
        self.timeout = config.get("timeout", 120)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 2)
        self.ssl_verify = config.get("ssl_verify", True)

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
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"

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

        # Add any extra kwargs to payload
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value

        logger.debug(f"OpenAI-Compatible API request: {url}")

        # Retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(url, json=payload, timeout=self.timeout, verify=self.ssl_verify)

                if response.status_code != 200:
                    try:
                        error_details = response.json()
                        logger.error(f"API Error Response: {json.dumps(error_details, indent=2)}")
                    except Exception:
                        logger.error(f"API Error Response (raw): {response.text}")

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

                return result

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Request timeout. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
            except requests.exceptions.HTTPError as e:
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
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"

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

        # Add any extra kwargs to payload
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value

        response = self.session.post(url, json=payload, timeout=self.timeout, stream=True, verify=self.ssl_verify)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8') if isinstance(line, bytes) else line
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

    def validate_connection(self) -> bool:
        """Test API connectivity."""
        try:
            url = f"{self.base_url.rstrip('/')}/models"
            response = self.session.get(url, timeout=5, verify=self.ssl_verify)
            return response.status_code == 200
        except Exception:
            # Fallback to a simple generation test
            try:
                self.generate(prompt="Test", context="Hi", max_tokens=1)
                return True
            except Exception:
                return False

    def get_provider_name(self) -> str:
        return "openai_compatible"
