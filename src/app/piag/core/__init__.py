"""Core PIAG - Logique métier pour l'API RAG PIAG."""

from .config import (
    load_config,
    get_config,
    get_base_url,
    get_timeout,
    get_headers,
    get_endpoint,
    should_log_requests,
    should_log_responses,
    DEFAULT_BASE_URL
)

from .client import PIAGClient

__all__ = [
    # Configuration
    'load_config',
    'get_config',
    'get_base_url',
    'get_timeout',
    'get_headers',
    'get_endpoint',
    'should_log_requests',
    'should_log_responses',
    'DEFAULT_BASE_URL',
    # Client
    'PIAGClient',
]
