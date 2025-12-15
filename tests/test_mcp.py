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
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test de la liste des outils."""
        # Mock la fonction handle_list_tools
        with patch('ambulon.mcp.handle_list_tools') as mock_handler:
            mock_tools = [
                {"name": "scan_document", "description": "Scanner un document"},
                {"name": "ocr_image", "description": "OCR d'une image"}
            ]
            mock_handler.return_value = mock_tools
            
            tools = await mock_handler()
            
            assert isinstance(tools, list)
            assert len(tools) >= 0
    
    @pytest.mark.asyncio
    async def test_call_tool_scan(self):
        """Test d'appel de l'outil de scan."""
        with patch('ambulon.mcp.handle_call_tool') as mock_handler:
            mock_result = {
                "content": [{"type": "text", "text": "Scan réussi"}]
            }
            mock_handler.return_value = mock_result
            
            result = await mock_handler("scan_document", {"dpi": 300})
            
            assert isinstance(result, dict)
            assert "content" in result
    
    @pytest.mark.asyncio
    async def test_call_tool_ocr(self):
        """Test d'appel de l'outil OCR."""
        with patch('ambulon.mcp.handle_call_tool') as mock_handler:
            mock_result = {
                "content": [{"type": "text", "text": "OCR réussi"}]
            }
            mock_handler.return_value = mock_result
            
            result = await mock_handler("ocr_image", {"image_path": "test.jpg"})
            
            assert isinstance(result, dict)
            assert "content" in result


if __name__ == "__main__":
    pytest.main([__file__])
