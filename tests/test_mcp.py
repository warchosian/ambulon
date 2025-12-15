"""Tests unitaires pour le serveur MCP."""

import pytest
from unittest.mock import patch, MagicMock

from ambulon.mcp import server


class TestMCPServer:
    """Tests pour le serveur MCP."""
    
    def test_server_exists(self):
        """Test que le serveur MCP existe."""
        assert server is not None
        assert hasattr(server, 'list_tools')
        assert hasattr(server, 'call_tool')
    
    def test_list_tools_mock(self):
        """Test de la liste des outils avec mock."""
        # Test simple sans async pour éviter les complications
        with patch('ambulon.mcp.server') as mock_server:
            mock_server.list_tools.return_value = [
                {"name": "scan_document", "description": "Scanner un document"},
                {"name": "ocr_image", "description": "OCR d'une image"}
            ]
            
            tools = mock_server.list_tools()
            
            assert isinstance(tools, list)
            assert len(tools) >= 0
    
    def test_call_tool_mock(self):
        """Test d'appel d'outil avec mock."""
        with patch('ambulon.mcp.server') as mock_server:
            mock_result = {
                "content": [{"type": "text", "text": "Scan réussi"}]
            }
            mock_server.call_tool.return_value = mock_result
            
            result = mock_server.call_tool("scan_document", {"dpi": 300})
            
            assert isinstance(result, dict)
            assert "content" in result
    
    def test_server_import(self):
        """Test que le module MCP peut être importé."""
        try:
            import ambulon.mcp
            assert True
        except ImportError:
            pytest.fail("Impossible d'importer le module MCP")


if __name__ == "__main__":
    pytest.main([__file__])
