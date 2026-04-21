"""Deprecated shim: re-exports the MCP server from ``app.mcp.core.server``.

This file previously held a 1396-line near-duplicate of ``app/mcp/core/server.py``
(with stale imports referencing scan helpers that have since moved). The
canonical implementation lives in :mod:`app.mcp.core.server` and is re-exported
here for backward compatibility with any code still importing
``app.mcp.mcp_server``.

Prefer ``from app.mcp.commands.run_server import main`` for new code.
"""

from app.mcp.core.server import (
    handle_call_tool,
    handle_list_tools,
    run_server,
    server,
    setup_logging,
)
from app.mcp.commands.run_server import main

__all__ = [
    "handle_call_tool",
    "handle_list_tools",
    "main",
    "run_server",
    "server",
    "setup_logging",
]
