#!/usr/bin/env python3
"""Client MCP simple pour tester le serveur Ambulon."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path


class SimpleMCPClient:
    """Client MCP simple pour les tests."""
    
    def __init__(self):
        self.process = None
    
    async def start_server(self):
        """Démarre le serveur MCP."""
        try:
            # Lancer le serveur MCP en tant que processus
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "ambulon.mcp",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            print("✓ Serveur MCP démarré")
            return True
        except Exception as e:
            print(f"✗ Erreur lors du démarrage du serveur: {e}")
            return False
    
    async def send_request(self, method, params=None):
        """Envoie une requête au serveur MCP."""
        if not self.process:
            raise RuntimeError("Serveur non démarré")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        
        # Envoyer la requête
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Lire la réponse
        response_line = await self.process.stdout.readline()
        if response_line:
            return json.loads(response_line.decode())
        return None
    
    async def test_initialize(self):
        """Test d'initialisation du serveur."""
        print("\n=== Test d'initialisation ===")
        try:
            response = await self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            })
            
            if response and "result" in response:
                print("✓ Initialisation réussie")
                print(f"  Serveur: {response['result'].get('serverInfo', {}).get('name', 'inconnu')}")
                return True
            else:
                print(f"✗ Réponse d'initialisation invalide: {response}")
                return False
        except Exception as e:
            print(f"✗ Erreur lors de l'initialisation: {e}")
            return False
    
    async def test_list_tools(self):
        """Test de la liste des outils."""
        print("\n=== Test de la liste des outils ===")
        try:
            response = await self.send_request("tools/list")
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                print(f"✓ {len(tools)} outils listés:")
                for tool in tools:
                    print(f"  - {tool.get('name', 'inconnu')}: {tool.get('description', 'pas de description')}")
                return True
            else:
                print(f"✗ Réponse de liste des outils invalide: {response}")
                return False
        except Exception as e:
            print(f"✗ Erreur lors de la liste des outils: {e}")
            return False
    
    async def test_call_tool(self, tool_name, arguments):
        """Test d'appel d'un outil."""
        print(f"\n=== Test d'appel de l'outil {tool_name} ===")
        try:
            response = await self.send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            if response and "result" in response:
                result = response["result"]
                print(f"✓ Outil {tool_name} appelé avec succès")
                if "content" in result:
                    content = result["content"]
                    if content and len(content) > 0:
                        print(f"  Résultat: {content[0].get('text', 'pas de texte')[:100]}...")
                return True
            else:
                print(f"✗ Réponse d'appel d'outil invalide: {response}")
                return False
        except Exception as e:
            print(f"✗ Erreur lors de l'appel de l'outil: {e}")
            return False
    
    async def stop_server(self):
        """Arrête le serveur MCP."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("✓ Serveur MCP arrêté")


async def main():
    """Fonction principale de test du client."""
    print("🔌 Test du client MCP avec le serveur Ambulon")
    print("=" * 60)
    
    client = SimpleMCPClient()
    
    try:
        # Démarrer le serveur
        if not await client.start_server():
            return 1
        
        # Attendre un peu que le serveur démarre
        await asyncio.sleep(2)
        
        # Tests
        tests = [
            ("Initialisation", lambda: client.test_initialize()),
            ("Liste des outils", lambda: client.test_list_tools()),
            ("Appel outil scan", lambda: client.test_call_tool("scan_document", {
                "dpi": 300,
                "output_path": "test_scan.jpg"
            })),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                success = await test_func()
                if success:
                    passed += 1
            except Exception as e:
                print(f"✗ {test_name}: Exception - {e}")
        
        print(f"\n{'=' * 60}")
        print(f"📊 Résultats: {passed}/{total} tests réussis")
        
        return 0 if passed == total else 1
        
    finally:
        await client.stop_server()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
        sys.exit(1)
