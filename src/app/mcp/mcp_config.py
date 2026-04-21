"""Deprecated shim: re-exports MCP config helpers from ``app.mcp.core.config``.

This file previously held a 568-line near-duplicate of
``app/mcp/core/config.py``. The canonical implementation lives in
:mod:`app.mcp.core.config`; import from there in new code.
"""

from app.mcp.core.config import (
    create_aider_config,
    create_claude_config,
    create_continue_config,
    create_openrouter_config,
    export_mcp_config,
    get_claude_config_path,
    get_config_paths,
    get_installation_status,
    get_mcp_config,
    test_mcp_server,
)

__all__ = [
    "create_aider_config",
    "create_claude_config",
    "create_continue_config",
    "create_openrouter_config",
    "export_mcp_config",
    "get_claude_config_path",
    "get_config_paths",
    "get_installation_status",
    "get_mcp_config",
    "test_mcp_server",
]
