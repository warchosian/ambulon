"""
Tests unitaires pour dyag.mcp.commands.mcp_server
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from dyag.mcp.commands.mcp_server import MCPServer


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPServer:
    """Tests du serveur MCP."""

    def test_init(self):
        """Test initialisation serveur MCP."""
        server = MCPServer()
        assert server is not None

    @patch('dyag.mcp.commands.mcp_server.RAGQuerySystem')
    def test_handle_query_tool(self, mock_rag_system, mock_mcp_request):
        """Test gestion outil query."""
        mock_rag = MagicMock()
        mock_rag.query.return_value = "Réponse test"
        mock_rag_system.return_value = mock_rag

        server = MCPServer()
        response = server.handle_tool_call(mock_mcp_request)

        assert response is not None
        # Vérifier le format de réponse MCP

    def test_list_tools(self):
        """Test listage des outils disponibles."""
        server = MCPServer()
        tools = server.list_tools()

        assert tools is not None
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_handle_invalid_tool(self):
        """Test gestion outil invalide."""
        server = MCPServer()
        invalid_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "invalid_tool",
                "arguments": {}
            }
        }

        response = server.handle_tool_call(invalid_request)

        # Devrait retourner une erreur
        assert "error" in response or response is None


@pytest.mark.unit
@pytest.mark.mcp
class TestMCPProtocol:
    """Tests du protocole MCP."""

    def test_valid_mcp_request_format(self, mock_mcp_request):
        """Test format requête MCP valide."""
        assert "jsonrpc" in mock_mcp_request
        assert mock_mcp_request["jsonrpc"] == "2.0"
        assert "id" in mock_mcp_request
        assert "method" in mock_mcp_request

    def test_valid_mcp_response_format(self, mock_mcp_response):
        """Test format réponse MCP valide."""
        assert "jsonrpc" in mock_mcp_response
        assert "id" in mock_mcp_response
        assert "result" in mock_mcp_response
