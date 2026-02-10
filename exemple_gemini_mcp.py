"""
Exemple d'utilisation du serveur MCP Ambulon avec Gemini
========================================================

Ce script montre comment connecter Gemini au serveur MCP d'Ambulon
pour utiliser les 22 outils de traitement de documents.
"""

import asyncio
import os
from pathlib import Path

# Configuration du serveur MCP Ambulon
AMBULON_PATH = Path(__file__).parent
MCP_CONFIG = {
    "command": "python",
    "args": ["-m", "app.mcp.commands.run_server"],
    "cwd": str(AMBULON_PATH),
    "env": {
        "PYTHONPATH": str(AMBULON_PATH / "src")
    }
}

async def example_with_mcp():
    """
    Exemple d'utilisation du serveur MCP avec le SDK Python MCP
    
    IMPORTANT: Installez d'abord le SDK MCP:
        pip install mcp
    """
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print("ERREUR: Le SDK MCP n'est pas installe")
        print("Installez-le avec: pip install mcp")
        return
    
    print("=" * 70)
    print("CONNEXION AU SERVEUR MCP AMBULON")
    print("=" * 70)
    
    server_params = StdioServerParameters(
        command=MCP_CONFIG["command"],
        args=MCP_CONFIG["args"],
        cwd=MCP_CONFIG["cwd"],
        env=MCP_CONFIG["env"]
    )
    
    print("\n1. Demarrage du serveur MCP...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("2. Initialisation de la session...")
            await session.initialize()
            
            print("3. Recuperation de la liste des outils...")
            tools = await session.list_tools()
            
            print(f"\n[OK] {len(tools.tools)} outils MCP disponibles\n")
            
            # Afficher quelques outils
            print("Exemples d'outils:")
            for tool in tools.tools[:5]:
                print(f"  - {tool.name}: {tool.description}")
            print(f"  ... et {len(tools.tools) - 5} autres\n")
            
            # EXEMPLE 1: Convertir HTML vers Markdown
            print("=" * 70)
            print("EXEMPLE 1: Conversion HTML vers Markdown")
            print("=" * 70)
            
            example_html = AMBULON_PATH / "example.html"
            if example_html.exists():
                result = await session.call_tool(
                    "html_to_markdown",
                    arguments={
                        "input_file": str(example_html),
                        "output_file": "example.md"
                    }
                )
                print("\nResultat:", result.content[0].text)
            else:
                print("\nPour tester, creez un fichier example.html")
            
            # EXEMPLE 2: OCR sur une image
            print("\n" + "=" * 70)
            print("EXEMPLE 2: OCR sur une image")
            print("=" * 70)
            
            example_img = AMBULON_PATH / "facture.jpg"
            if example_img.exists():
                result = await session.call_tool(
                    "ocr_image",
                    arguments={
                        "image_path": str(example_img),
                        "language": "fra"
                    }
                )
                print("\nResultat:", result.content[0].text)
            else:
                print("\nPour tester, placez une image facture.jpg")
            
            # EXEMPLE 3: Fusionner plusieurs Markdown
            print("\n" + "=" * 70)
            print("EXEMPLE 3: Fusion de fichiers Markdown")
            print("=" * 70)
            
            docs_dir = AMBULON_PATH / "docs"
            if docs_dir.exists():
                result = await session.call_tool(
                    "merge_md",
                    arguments={
                        "input_dir": str(docs_dir),
                        "output_file": "docs_merged.md"
                    }
                )
                print("\nResultat:", result.content[0].text)
            else:
                print("\nPour tester, creez un dossier docs/ avec des fichiers .md")
            
            print("\n" + "=" * 70)
            print("INTEGRATION AVEC GEMINI")
            print("=" * 70)
            print("""
Maintenant que le serveur MCP fonctionne, vous pouvez:

1. Utiliser ces outils avec Google Gemini via le SDK MCP
2. Integrer dans votre projet Gemini existant
3. Creer des workflows automatises (scan + OCR + conversion)

Exemple de workflow complet:
  1. scan_document -> Scanner un document
  2. ocr_image -> Extraire le texte
  3. html_to_markdown -> Convertir pour analyse
  4. [Votre traitement Gemini ici]

Voir mcp-server-for-gemini.md pour plus d'exemples.
            """)

def example_without_mcp():
    """
    Exemple d'utilisation directe des fonctions Ambulon (sans MCP)
    
    Utile si vous voulez appeler les fonctions directement depuis Python
    sans passer par le protocole MCP.
    """
    
    import sys
    sys.path.insert(0, str(AMBULON_PATH / "src"))
    
    print("=" * 70)
    print("UTILISATION DIRECTE DES FONCTIONS AMBULON")
    print("=" * 70)
    
    try:
        # Import direct des fonctions
        from app.conversion.commands.html2md import html_to_markdown_logic
        
        print("\n[OK] Import reussi")
        print("\nVous pouvez maintenant appeler:")
        print("  html_to_markdown_logic(input_file, output_file)")
        print("\nVoir la documentation dans chaque module core/")
        
    except ImportError as e:
        print(f"\n[ERREUR] Probleme d'import: {e}")
        print("\nLe projet a besoin de corrections d'imports.")

if __name__ == "__main__":
    print("""
EXEMPLE D'UTILISATION - SERVEUR MCP AMBULON AVEC GEMINI
========================================================

Choisissez un mode:

1. Mode MCP (recommande pour Gemini):
   - Utilise le protocole MCP standard
   - Compatible avec tous les clients MCP
   - Execute: python exemple_gemini_mcp.py mcp

2. Mode Direct (pour tests):
   - Appelle les fonctions Python directement
   - Pas de protocole MCP
   - Execute: python exemple_gemini_mcp.py direct

3. Voir la documentation complete:
   - Lire: mcp-server-for-gemini.md
    """)
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "mcp":
            asyncio.run(example_with_mcp())
        elif sys.argv[1] == "direct":
            example_without_mcp()
        else:
            print(f"\nOption inconnue: {sys.argv[1]}")
            print("Utilisez: mcp ou direct")
    else:
        print("\nAjoutez 'mcp' ou 'direct' comme argument")
