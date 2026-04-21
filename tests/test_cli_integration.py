"""Tests d'intégration pour le CLI Ambulon."""

import pytest
import sys
from unittest.mock import patch


class TestCLIIntegration:
    """Tests d'intégration pour le CLI principal."""

    def test_cli_module_can_be_imported(self):
        """Test que le module CLI peut être importé sans erreur."""
        from app.cli import cli
        assert hasattr(cli, 'main')

    def test_cli_help_works(self):
        """Test que l'aide CLI fonctionne."""
        from app.cli.cli import show_help
        
        # Should not raise any exception
        show_help()

    def test_cli_version_works(self):
        """Test que --version fonctionne."""
        from app.cli.cli import main
        
        with patch('sys.argv', ['ambulon', '--version']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                assert result == 0
                # Should have printed version info
                assert mock_print.called

    def test_cli_main_with_no_args_shows_help(self):
        """Test que ambulon sans arguments affiche l'aide."""
        from app.cli.cli import main
        
        with patch('sys.argv', ['ambulon']):
            with patch('app.cli.cli.show_help') as mock_help:
                result = main()
                
                assert result == 0
                mock_help.assert_called_once()

    def test_cli_main_with_unknown_command(self):
        """Test que ambulon avec une commande inconnue retourne une erreur."""
        from app.cli.cli import main
        
        with patch('sys.argv', ['ambulon', 'unknown-command-xyz']):
            with patch('builtins.print') as mock_print:
                result = main()
                
                assert result == 1
                # Should have printed error message
                mock_print.assert_called()

    def test_config_command_help(self):
        """Test que ambulon config --help fonctionne."""
        from app.cli.cli import handle_config_command
        
        with patch('sys.argv', ['ambulon', 'config', '--help']):
            result = handle_config_command()
            
            assert result == 0

    def test_test_command_help(self):
        """Test que ambulon test --help fonctionne."""
        from app.cli.cli import handle_test_command
        
        with patch('sys.argv', ['ambulon', 'test', '--help']):
            result = handle_test_command()
            
            assert result == 0

    def test_rag_module_dispatcher_exists(self):
        """Test que le dispatcher des modules RAG existe."""
        from app.cli.cli import handle_rag_module
        
        # Should not raise ImportError
        assert callable(handle_rag_module)

    def test_logging_setup_works(self):
        """Test que la configuration de logging fonctionne."""
        from app.core.logging_config import setup_logging
        import logging
        
        # Should not raise any exception
        setup_logging(level=logging.INFO, log_file_prefix="test")


if __name__ == "__main__":
    pytest.main([__file__])
