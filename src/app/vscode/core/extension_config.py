"""
VS Code extension configuration.

Uses the centralized ConfigManager for consistent configuration handling
across all Ambulon modules.
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, TypedDict

from app.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

Priority = Literal["ESSENTIEL", "FORTEMENT RECOMMANDÉ", "OPTIONNEL"]


class ExtensionInfo(TypedDict):
    """Type definition for extension metadata."""
    description: str
    category: str
    priority: Priority


# Default VSCode configuration
DEFAULT_VSCODE_CONFIG: Dict[str, Any] = {
    "recommended_extensions": {},
    "extensions_to_remove": {}
}

# Global config manager instance
_config_manager = ConfigManager(
    module_name="vscode",
    defaults=DEFAULT_VSCODE_CONFIG,
    env_prefix="AMBULON_VSCODE"
)


@lru_cache(maxsize=1)
def _get_vscode_config() -> Dict:
    """Load VSCode configuration using ConfigManager, cached."""
    return _config_manager.load(config_path="vscode.yaml")


def __getattr__(name: str) -> Any:
    """Lazy module-level access to YAML-backed dicts (PEP 562)."""
    if name == "RECOMMENDED_EXTENSIONS":
        return _cached_config().get("recommended_extensions", {})
    if name == "EXTENSIONS_TO_REMOVE":
        return _cached_config().get("extensions_to_remove", {})
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_extensions_by_priority(priority: Priority) -> List[str]:
    """
    Get extension IDs filtered by priority level.

    Args:
        priority: Priority level to filter by

    Returns:
        List of extension IDs matching the priority
    """
    return [
        ext_id
        for ext_id, info in _cached_config().get("recommended_extensions", {}).items()
        if info["priority"] == priority
    ]


def get_essential_extensions() -> List[str]:
    """Get list of essential extension IDs."""
    return get_extensions_by_priority("ESSENTIEL")


def get_recommended_extensions() -> List[str]:
    """Get list of strongly recommended extension IDs."""
    return get_extensions_by_priority("FORTEMENT RECOMMANDÉ")


def get_optional_extensions() -> List[str]:
    """Get list of optional extension IDs."""
    return get_extensions_by_priority("OPTIONNEL")
