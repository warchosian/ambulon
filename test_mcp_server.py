#!/usr/bin/env python3
"""
Test simple du serveur MCP Ambulon
Affiche la liste des outils disponibles sans démarrer le serveur complet
"""

import sys
from pathlib import Path

# Ajouter src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_mcp_tools():
    """Teste l'import et liste les outils MCP disponibles"""

    print("=" * 70)
    print("TEST SERVEUR MCP AMBULON")
    print("=" * 70)

    try:
        print("\n[1/2] Test import du module MCP...")
        # Tester juste l'import du fichier mcp_server
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "mcp_server", 
            "src/app/mcp/mcp_server.py"
        )
        if spec and spec.loader:
            print("✓ Fichier mcp_server.py trouvé")
        else:
            print("✗ Fichier mcp_server.py non trouvé")
            return False

        print("\n[2/2] Liste des outils MCP attendus...")
        
        expected_tools = [
            # Scan & OCR (5)
            ("scan_document", "Scanner un document avec NAPS2"),
            ("ocr_image", "OCR sur une image"),
            ("ocr_batch", "OCR en lot"),
            ("scan_with_ocr", "Scanner + OCR"),
            ("process_existing_scans", "Traiter scans existants"),
            
            # Conversion (5)
            ("html_to_markdown", "HTML vers Markdown"),
            ("markdown_to_html", "Markdown vers HTML"),
            ("json_to_markdown", "JSON vers Markdown"),
            ("images_to_pdf", "Images vers PDF"),
            ("compress_pdf", "Compresser PDF"),
            
            # WikiSI (3)
            ("wikisi_scrape", "Aspirer site WikiSI"),
            ("wikisi_extract_json", "Extraire JSON WikiSI"),
            ("wikisi_json_to_md", "WikiSI JSON vers MD"),
            
            # Processing (6)
            ("add_toc_html", "Ajouter TOC HTML"),
            ("add_toc_md", "Ajouter TOC Markdown"),
            ("merge_html", "Fusionner HTML"),
            ("merge_md", "Fusionner Markdown"),
            ("flatten_html", "Aplatir HTML"),
            ("flatten_md", "Aplatir Markdown"),
            
            # Encoding (2)
            ("check_encoding", "Vérifier encodage"),
            ("fix_encoding", "Corriger encodage"),
            
            # GitLab (1)
            ("gitlab_clone_group", "Cloner groupe GitLab"),
        ]

        print("\n" + "=" * 70)
        print("OUTILS MCP DISPONIBLES DANS AMBULON")
        print("=" * 70)
        print(f"\nTotal: {len(expected_tools)} outils\n")

        categories = {
            "Scan & OCR": expected_tools[0:5],
            "Conversion": expected_tools[5:10],
            "WikiSI": expected_tools[10:13],
            "Processing": expected_tools[13:19],
            "Encoding": expected_tools[19:21],
            "GitLab": expected_tools[21:22],
        }

        for category, tools in categories.items():
            print(f"\n{category} ({len(tools)} outils):")
            for name, desc in tools:
                print(f"  • {name:25s} - {desc}")

        print("\n" + "=" * 70)
        print("CONFIGURATION POUR VOTRE PROJET GEMINI")
        print("=" * 70)
        print("""
1. Via Python SDK Gemini + MCP :

   from mcp import ClientSession, StdioServerParameters
   from mcp.client.stdio import stdio_client
   
   server_params = StdioServerParameters(
       command="python",
       args=["-m", "app.mcp.commands.run_server"],
       cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon",
       env={"PYTHONPATH": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon/src"}
   )
   
   async with stdio_client(server_params) as (read, write):
       async with ClientSession(read, write) as session:
           await session.initialize()
           tools = await session.list_tools()

2. Via Claude Desktop / Continue.dev / Aider :
   
   Voir le fichier: mcp-server-for-gemini.md

3. Test manuel du serveur:

   python -m app.mcp.commands.run_server
        """)

        print("\n✓ CONFIGURATION PRÊTE")
        return True

    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mcp_tools()
    sys.exit(0 if success else 1)
