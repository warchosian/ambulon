"""Lazy command dispatcher for the Ambulon CLI.

Looks up a command name in :mod:`app.cli.registry.STANDARD_COMMANDS`, imports
the target module on demand, rewrites ``sys.argv`` to hide the command name
from the delegated handler, and calls its ``main`` (or equivalent) callable.

The ``sys.argv`` rewrite keeps backward compatibility with handlers that still
introspect ``sys.argv`` directly instead of accepting an ``argv`` argument.
"""

from __future__ import annotations

import importlib
import sys
from typing import Optional

from .registry import STANDARD_COMMANDS


def dispatch_standard(command: str) -> Optional[int]:
    """Dispatch a registered standard command.

    Args:
        command: Command name (what the user typed after ``ambulon``).

    Returns:
        The handler's exit code, or ``None`` if ``command`` is not registered.
    """
    entry = STANDARD_COMMANDS.get(command)
    if entry is None:
        return None

    module_path, attr_name = entry
    module = importlib.import_module(module_path)
    handler = getattr(module, attr_name)

    original_argv = sys.argv
    # Keep the program name, then everything after the command token.
    sys.argv = [sys.argv[0], *sys.argv[2:]]
    try:
        result = handler()
    finally:
        sys.argv = original_argv
    return result if isinstance(result, int) else 0


__all__ = ["dispatch_standard"]
