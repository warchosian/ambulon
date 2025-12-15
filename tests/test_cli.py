"""Tests unitaires pour le module CLI."""

import sys
from unittest.mock import patch
import pytest

from ambulon.cli import main, show_help, handle_config_command


class TestCLI:
    """Tests pour l'interface en ligne de commande."""
    
    def test_show_help(self, capsys):
        """Test de l'affichage de l'aide."""
        show_help()
        captured = capsys.readouterr()
        
        assert "Ambulon" in captured.out
        assert "Usage:" in captured.out
        assert "scan" in captured.out
        assert "ocr" in captured.out
        assert "mcp" in captured.out
        assert "config" in captured.out
    
    def test_main_no_args(self, capsys):
        """Test de main sans arguments."""
        with patch.object(sys, 'argv', ['ambulon']):
            result = main()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Ambulon" in captured.out
    
    def test_main_help(self, capsys):
        """Test de main avec --help."""
        with patch.object(sys, 'argv', ['ambulon', '--help']):
            result = main()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "Usage:" in captured.out
    
    def test_main_version(self, capsys):
        """Test de main avec --version."""
        with patch.object(sys, 'argv', ['ambulon', '--version']):
            result = main()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "version" in captured.out
    
    def test_main_unknown_command(self, capsys):
        """Test de main avec commande inconnue."""
        with patch.object(sys, 'argv', ['ambulon', 'unknown']):
            result = main()
            
            assert result == 1
            captured = capsys.readouterr()
            assert "Module inconnu" in captured.out
    
    def test_config_command_help(self, capsys):
        """Test de la commande config avec aide."""
        with patch.object(sys, 'argv', ['ambulon', 'config', '--help']):
            result = handle_config_command()
            
            assert result == 0
            captured = capsys.readouterr()
            assert "export" in captured.out
            assert "install" in captured.out
            assert "status" in captured.out


if __name__ == "__main__":
    pytest.main([__file__])
