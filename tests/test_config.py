"""Tests unitaires pour le module de configuration MCP."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest

from ambulon.config import (
    get_mcp_config, export_mcp_config, get_config_paths,
    create_claude_config, test_mcp_server, get_installation_status,
    create_openrouter_config, create_aider_config, create_continue_config
)


class TestMCPConfig:
    """Tests pour la gestion de la configuration MCP."""
    
    def test_get_config_paths(self):
        """Test de récupération des chemins de configuration."""
        paths = get_config_paths()
        
        assert isinstance(paths, dict)
        assert "claude" in paths
        assert "openrouter" in paths
        assert "aider" in paths
        assert "continue" in paths
        
        for assistant, assistant_paths in paths.items():
            assert "config" in assistant_paths
            assert isinstance(assistant_paths["config"], Path)
    
    def test_export_mcp_config(self):
        """Test d'export de la configuration MCP."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_config.json"
            
            # Mock la fonction get_mcp_config pour éviter les dépendances
            mock_config = {"test": "config"}
            with patch('ambulon.config.get_mcp_config', return_value=mock_config):
                result_path = export_mcp_config(output_path)
                
                assert result_path.exists()
                
                with result_path.open("r") as f:
                    config = json.load(f)
                
                assert config == mock_config
    
    def test_create_claude_config(self):
        """Test de création de configuration Claude."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "claude_desktop_config.json"
            
            with patch('ambulon.config.get_claude_config_path', return_value=config_path):
                config = create_claude_config()
                
                assert isinstance(config, dict)
                assert "mcpServers" in config
                assert "ambulon" in config["mcpServers"]
                assert config_path.exists()
    
    def test_create_openrouter_config(self):
        """Test de création de configuration OpenRouter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            
            with patch('ambulon.config.get_config_paths') as mock_paths:
                mock_paths.return_value = {
                    "openrouter": {"config": config_path}
                }
                
                config = create_openrouter_config()
                
                assert isinstance(config, dict)
                assert "mcp_servers" in config
                assert "ambulon" in config["mcp_servers"]
                assert config_path.exists()
    
    def test_create_aider_config(self):
        """Test de création de configuration Aider."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            
            with patch('ambulon.config.get_config_paths') as mock_paths:
                mock_paths.return_value = {
                    "aider": {"config": config_path}
                }
                
                config = create_aider_config()
                
                assert isinstance(config, dict)
                assert "mcp" in config
                assert "servers" in config["mcp"]
                assert "ambulon" in config["mcp"]["servers"]
                assert config_path.exists()
    
    def test_create_continue_config(self):
        """Test de création de configuration Continue."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "settings.json"
            
            with patch('ambulon.config.get_config_paths') as mock_paths:
                mock_paths.return_value = {
                    "continue": {"config": config_path}
                }
                
                config = create_continue_config()
                
                assert isinstance(config, dict)
                assert "continue.mcp.servers" in config
                assert len(config["continue.mcp.servers"]) > 0
                assert any(server.get("name") == "ambulon" for server in config["continue.mcp.servers"])
                assert config_path.exists()
    
    def test_mcp_server_test(self):
        """Test du serveur MCP."""
        results = test_mcp_server()
        
        assert isinstance(results, dict)
        assert "server_accessible" in results
        assert "tools_available" in results
        assert "tools_count" in results
        assert isinstance(results["server_accessible"], bool)
        assert isinstance(results["tools_available"], bool)
        assert isinstance(results["tools_count"], int)
    
    def test_installation_status(self):
        """Test du statut d'installation."""
        status = get_installation_status()
        
        assert isinstance(status, dict)
        
        for assistant in ["claude", "openrouter", "aider", "continue"]:
            assert assistant in status
            assert "config_exists" in status[assistant]
            assert "config_path" in status[assistant]
            assert "directory_exists" in status[assistant]
            assert "ambulon_configured" in status[assistant]
            
            assert isinstance(status[assistant]["config_exists"], bool)
            assert isinstance(status[assistant]["config_path"], str)
            assert isinstance(status[assistant]["directory_exists"], bool)
            assert isinstance(status[assistant]["ambulon_configured"], bool)
    
    def test_config_merge_existing(self):
        """Test de fusion avec une configuration existante."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "claude_desktop_config.json"
            
            # Créer une config existante
            existing_config = {
                "mcpServers": {
                    "other_server": {
                        "command": "other",
                        "args": []
                    }
                }
            }
            
            with config_path.open("w") as f:
                json.dump(existing_config, f)
            
            with patch('ambulon.config.get_claude_config_path', return_value=config_path):
                config = create_claude_config()
                
                # Vérifier que les deux serveurs sont présents
                assert "mcpServers" in config
                assert "ambulon" in config["mcpServers"]
                assert "other_server" in config["mcpServers"]


if __name__ == "__main__":
    pytest.main([__file__])
