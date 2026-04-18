"""
Module LLM pour génération de documents via API externes.

Génère des documents via des API LLM (Kimi, ChatGPT, Claude) à partir
de fichiers .md sources et d'un prompt.
"""

from app.llm.core.manager import DocumentManager
from app.llm.core.providers import get_provider, list_providers

__all__ = ["DocumentManager", "get_provider", "list_providers"]
