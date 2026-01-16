"""
Script de test pour lister les outils MCP Ambulon depuis Gemini
================================================================

Ce script se connecte au serveur MCP Ambulon et affiche tous les outils disponibles.

Usage:
    python test_list_tools_gemini.py
"""

import asyncio
import sys
from pathlib import Path

# Configuration du serveur MCP Ambulon
AMBULON_DIR = Path(__file__).parent  # Ajuster si nécessaire
MCP_SERVER_SCRIPT = "mcp_server_standalone.py"

async def list_ambulon_tools():
    """
    Se connecte au serveur MCP Ambulon et liste tous les outils disponibles
    """
    
    print("=" * 70)
    print("CONNEXION AU SERVEUR MCP AMBULON DEPUIS GEMINI")
    print("=" * 70)
    
    try:
        # Import du SDK MCP
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print("\n[ERREUR] Le SDK MCP n'est pas installé")
        print("\nInstallez-le avec:")
        print("    pip install mcp")
        return False
    
    # Configuration de la connexion au serveur
    server_params = StdioServerParameters(
        command="python",
        args=[MCP_SERVER_SCRIPT],
        cwd=str(AMBULON_DIR),
        env={"PYTHONPATH": str(AMBULON_DIR / "src")}
    )
    
    print(f"\n[1/3] Démarrage du serveur MCP...")
    print(f"      Dossier: {AMBULON_DIR}")
    print(f"      Script: {MCP_SERVER_SCRIPT}")
    
    try:
        # Connexion au serveur
        async with stdio_client(server_params) as (read, write):
            print("[2/3] Connexion établie")
            
            async with ClientSession(read, write) as session:
                print("[3/3] Session initialisée")
                
                # Initialiser la session
                await session.initialize()
                
                # Lister les outils disponibles
                tools_result = await session.list_tools()
                
                print("\n" + "=" * 70)
                print("OUTILS MCP DISPONIBLES")
                print("=" * 70)
                
                if not tools_result.tools:
                    print("\nAucun outil disponible")
                    return False
                
                print(f"\nTotal: {len(tools_result.tools)} outil(s)\n")
                
                # Afficher chaque outil avec ses détails
                for i, tool in enumerate(tools_result.tools, 1):
                    print(f"\n{i}. {tool.name}")
                    print(f"   Description: {tool.description}")
                    
                    # Afficher le schéma des paramètres
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        schema = tool.inputSchema
                        if 'properties' in schema:
                            print(f"   Paramètres:")
                            for param_name, param_info in schema['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_desc = param_info.get('description', '')
                                required = '(obligatoire)' if param_name in schema.get('required', []) else '(optionnel)'
                                print(f"     - {param_name}: {param_type} {required}")
                                if param_desc:
                                    print(f"       {param_desc}")
                
                print("\n" + "=" * 70)
                print("EXEMPLE D'UTILISATION")
                print("=" * 70)
                
                if tools_result.tools:
                    # Prendre le premier outil comme exemple
                    example_tool = tools_result.tools[0]
                    print(f"""
# Exemple: Utiliser l'outil '{example_tool.name}'

async def use_tool_example():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Appeler l'outil
            result = await session.call_tool(
                "{example_tool.name}",
                arguments={{
                    # Ajouter vos arguments ici selon le schéma ci-dessus
                }}
            )
            
            # Afficher le résultat
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)

asyncio.run(use_tool_example())
                    """)
                
                print("\n" + "=" * 70)
                print("[OK] Connexion réussie - Outils listés")
                print("=" * 70)
                
                return True
    
    except FileNotFoundError:
        print(f"\n[ERREUR] Script serveur non trouvé: {AMBULON_DIR / MCP_SERVER_SCRIPT}")
        print("\nVérifiez que le chemin est correct:")
        print(f"  Dossier Ambulon: {AMBULON_DIR}")
        print(f"  Script MCP: {MCP_SERVER_SCRIPT}")
        return False
    
    except Exception as e:
        print(f"\n[ERREUR] Connexion au serveur MCP échouée")
        print(f"  Type: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        
        import traceback
        print("\nDétails complets:")
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal"""
    
    print("\n" + "=" * 70)
    print("TEST DE CONNEXION MCP AMBULON POUR GEMINI")
    print("=" * 70)
    print()
    print("Ce script va:")
    print("  1. Démarrer le serveur MCP Ambulon")
    print("  2. Se connecter depuis votre projet Gemini")
    print("  3. Lister tous les outils disponibles")
    print()
    print("-" * 70)
    
    # Exécuter la connexion
    success = asyncio.run(list_ambulon_tools())
    
    if success:
        print("\n✓ Test réussi!")
        print("\nVous pouvez maintenant utiliser ces outils dans votre projet Gemini")
        print("Consultez: mcp-server-for-gemini.md pour plus d'exemples")
        sys.exit(0)
    else:
        print("\n✗ Test échoué")
        print("\nVérifiez:")
        print("  1. Le SDK MCP est installé: pip install mcp")
        print("  2. Le serveur standalone existe: mcp_server_standalone.py")
        print("  3. Les dépendances sont installées: pip install typer pyyaml")
        sys.exit(1)

if __name__ == "__main__":
    main()
