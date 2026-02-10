"""Module MCP pour Ambulon - Serveur MCP et configuration."""

from .mcp_server import main as server_main
from .mcp_config import export_mcp_config, get_claude_config_path

__all__ = ['server_main', 'export_mcp_config', 'get_claude_config_path']
