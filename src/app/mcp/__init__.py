"""Module MCP pour Ambulon - Serveur MCP et configuration."""

from app.mcp.commands.run_server import main as server_main
from app.mcp.core.config import export_mcp_config, get_claude_config_path

__all__ = ['server_main', 'export_mcp_config', 'get_claude_config_path']
