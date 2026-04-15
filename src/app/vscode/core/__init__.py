"""
Core modules for VSCode extension management.
"""

from .detector import find_vscode_command, get_vscode_version, is_vscode_installed
from .extension_manager import (
    get_installed_extensions,
    install_extension,
    uninstall_extension,
    check_extension_installed
)
from .extension_config import (
    RECOMMENDED_EXTENSIONS,
    EXTENSIONS_TO_REMOVE,
    get_extensions_by_priority,
    Priority
)

__all__ = [
    "find_vscode_command",
    "get_vscode_version",
    "is_vscode_installed",
    "get_installed_extensions",
    "install_extension",
    "uninstall_extension",
    "check_extension_installed",
    "RECOMMENDED_EXTENSIONS",
    "EXTENSIONS_TO_REMOVE",
    "get_extensions_by_priority",
    "Priority",
]
