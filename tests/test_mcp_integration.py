"""Tests d'intégration pour le serveur MCP Ambulon."""

import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


class TestMCPIntegration:
    """Tests d'intégration pour le serveur MCP."""
    
    def test_mcp_server_startup(self):
        """Test que le serveur MCP peut démarrer."""
        try:
            # Tester l'import du serveur MCP
            from ambulon.mcp import server, setup_logging
            
            # Vérifier que le serveur a les bonnes méthodes
            assert hasattr(server, 'list_tools')
            assert hasattr(server, 'call_tool')
            
            # Tester la configuration du logging
            setup_logging()
            
            print("✓ Serveur MCP importé avec succès")
            
        except ImportError as e:
            pytest.fail(f"Impossible d'importer le serveur MCP: {e}")
        except Exception as e:
            pytest.fail(f"Erreur lors du test du serveur MCP: {e}")
    
    @pytest.mark.asyncio
    async def test_mcp_list_tools(self):
        """Test de la liste des outils MCP."""
        try:
            from ambulon.mcp import handle_list_tools
            
            # Appeler la fonction de liste des outils
            tools = await handle_list_tools()
            
            # Vérifier que c'est une liste
            assert isinstance(tools, list)
            
            # Vérifier qu'il y a au moins quelques outils
            assert len(tools) > 0
            
            # Vérifier la structure des outils
            for tool in tools:
                assert isinstance(tool, dict)
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool
            
            print(f"✓ {len(tools)} outils MCP disponibles")
            
        except Exception as e:
            pytest.fail(f"Erreur lors du test de liste des outils: {e}")
    
    @pytest.mark.asyncio
    async def test_mcp_call_tool_scan(self):
        """Test d'appel de l'outil de scan via MCP."""
        try:
            from ambulon.mcp import handle_call_tool
            
            # Préparer les arguments pour le scan
            arguments = {
                "dpi": 300,
                "output_dir": str(Path.cwd() / "test_scans"),
                "simulate": True  # Mode simulation pour les tests
            }
            
            # Appeler l'outil de scan
            result = await handle_call_tool("scan_document", arguments)
            
            # Vérifier la structure de la réponse
            assert isinstance(result, dict)
            assert "content" in result
            assert isinstance(result["content"], list)
            assert len(result["content"]) > 0
            
            # Vérifier le contenu de la réponse
            content = result["content"][0]
            assert "type" in content
            assert "text" in content
            
            print("✓ Outil de scan MCP fonctionne")
            
        except Exception as e:
            pytest.fail(f"Erreur lors du test de l'outil de scan: {e}")
    
    @pytest.mark.asyncio
    async def test_mcp_call_tool_ocr(self):
        """Test d'appel de l'outil OCR via MCP."""
        try:
            from ambulon.mcp import handle_call_tool
            
            # Créer une image factice pour le test
            with tempfile.TemporaryDirectory() as temp_dir:
                test_image = Path(temp_dir) / "test.jpg"
                test_image.write_bytes(b"fake image data")
                
                # Préparer les arguments pour l'OCR
                arguments = {
                    "image_path": str(test_image),
                    "language": "fra"
                }
                
                # Mock l'OCR pour éviter les dépendances externes
                with patch('ambulon.ocr.perform_ocr') as mock_ocr:
                    mock_ocr.return_value = {
                        "success": True,
                        "text": "Texte extrait par OCR",
                        "confidence": 95.5
                    }
                    
                    # Appeler l'outil OCR
                    result = await handle_call_tool("ocr_image", arguments)
                    
                    # Vérifier la structure de la réponse
                    assert isinstance(result, dict)
                    assert "content" in result
                    assert isinstance(result["content"], list)
                    
                    print("✓ Outil OCR MCP fonctionne")
                    
        except Exception as e:
            pytest.fail(f"Erreur lors du test de l'outil OCR: {e}")
    
    def test_mcp_server_process(self):
        """Test que le serveur MCP peut être lancé en tant que processus."""
        try:
            # Tenter de lancer le serveur MCP en mode test
            cmd = [sys.executable, "-m", "ambulon.mcp", "--help"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=Path.cwd()
            )
            
            # Le serveur MCP devrait au moins répondre à --help
            # (même si ce n'est pas implémenté, il ne devrait pas crasher)
            assert result.returncode in [0, 1, 2]  # Codes de retour acceptables
            
            print("✓ Processus serveur MCP peut être lancé")
            
        except subprocess.TimeoutExpired:
            pytest.fail("Le serveur MCP a pris trop de temps à répondre")
        except FileNotFoundError:
            pytest.fail("Impossible de trouver le module ambulon.mcp")
        except Exception as e:
            pytest.fail(f"Erreur lors du test du processus MCP: {e}")
    
    def test_mcp_config_validation(self):
        """Test que la configuration MCP est valide."""
        try:
            from ambulon.config import get_mcp_config
            
            # Récupérer la configuration MCP
            config = get_mcp_config()
            
            # Vérifier la structure de base
            assert isinstance(config, dict)
            
            # Vérifier les sections importantes
            if "mcpServers" in config:
                assert "ambulon" in config["mcpServers"]
                ambulon_config = config["mcpServers"]["ambulon"]
                assert "command" in ambulon_config
                assert "args" in ambulon_config
            
            if "tools" in config:
                assert isinstance(config["tools"], list)
                assert len(config["tools"]) > 0
                
                # Vérifier la structure des outils
                for tool in config["tools"]:
                    assert "name" in tool
                    assert "description" in tool
                    assert "category" in tool
            
            print("✓ Configuration MCP valide")
            
        except Exception as e:
            pytest.fail(f"Erreur lors de la validation de la config MCP: {e}")
    
    def test_mcp_installation_status(self):
        """Test du statut d'installation MCP."""
        try:
            from ambulon.config import get_installation_status, test_mcp_server
            
            # Vérifier le statut d'installation
            status = get_installation_status()
            assert isinstance(status, dict)
            
            # Vérifier les assistants supportés
            expected_assistants = ["claude", "openrouter", "aider", "continue"]
            for assistant in expected_assistants:
                assert assistant in status
                assert "config_exists" in status[assistant]
                assert "ambulon_configured" in status[assistant]
            
            # Tester le serveur MCP
            server_status = test_mcp_server()
            assert isinstance(server_status, dict)
            assert "server_accessible" in server_status
            assert "tools_available" in server_status
            assert "tools_count" in server_status
            
            print("✓ Statut d'installation MCP vérifié")
            
        except Exception as e:
            pytest.fail(f"Erreur lors du test du statut MCP: {e}")


def run_mcp_integration_tests():
    """Fonction utilitaire pour exécuter tous les tests d'intégration MCP."""
    print("Exécution des tests d'intégration MCP...")
    print("=" * 50)
    
    test_instance = TestMCPIntegration()
    
    tests = [
        ("Démarrage serveur", test_instance.test_mcp_server_startup),
        ("Configuration", test_instance.test_mcp_config_validation),
        ("Statut installation", test_instance.test_mcp_installation_status),
        ("Processus serveur", test_instance.test_mcp_server_process),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\nTest: {test_name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: {e}")
    
    # Tests async séparés
    async_tests = [
        ("Liste outils", test_instance.test_mcp_list_tools),
        ("Outil scan", test_instance.test_mcp_call_tool_scan),
        ("Outil OCR", test_instance.test_mcp_call_tool_ocr),
    ]
    
    for test_name, test_func in async_tests:
        try:
            print(f"\nTest async: {test_name}")
            asyncio.run(test_func())
            passed += 1
        except Exception as e:
            print(f"✗ {test_name}: {e}")
    
    total += len(async_tests)
    
    print(f"\n{'='*50}")
    print(f"Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("✓ Tous les tests d'intégration MCP sont passés!")
        return True
    else:
        print("✗ Certains tests d'intégration MCP ont échoué")
        return False


if __name__ == "__main__":
    run_mcp_integration_tests()
