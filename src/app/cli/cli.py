"""Module CLI pour Ambulon."""
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

from . import hello
from app.scan.commands.scan import main as scan_main
from app.ocr.commands.ocr import main as ocr_main
from app.mcp.commands.run_server import main as mcp_main
from app.mcp.core.config import export_mcp_config, get_claude_config_path
from app.gitlab.commands.gitlab_clone import main as gitlab_clone_main
from app.gitlab.commands.gitlab_monofile import main as gitlab_monofile_main

# Modules de conversion
from app.conversion import (
    compress_pdf_main,
    img2pdf_main,
    process_html_to_markdown,
    process_markdown_to_html,
    convert_html_to_pdf,
    json_to_jsonl,
    process_json_to_markdown,
    pdf2html_main,
    pdf2md_main,
)

# Modules d'encoding
from app.encoding import check_md_cli, fix_md_cli



# Module WikiSI



# Module Processing
from app.processing import (
    add_toc4html_cli,
    add_toc4md_cli,
    concat_html_cli,
    flatten_html_cli,
    flatten_md_cli,
    make_html_interactive,
    merge_html_cli,
    merge_md_cli,
    md2project_cli,
    project2md_cli,
    fusion_markdown_files,
    project_to_markdown,
)

import requests # NEW
import json # NEW
from app.core.logging_config import setup_logging
from app.cli.commands import handle_init_command



def show_help():
    """Affiche l'aide principale avec les modules disponibles."""
    print(hello())
    print()
    print("Usage: ambulon [MODULE] [OPTIONS]")
    print()
    print("Modules disponibles:")
    print("  scan                  Module de scan TWAIN avec profils DPI")
    print("  ocr                   Module OCR - Reconnaissance optique de caractères")
    print("  mcp                   Serveur MCP pour assistants IA")
    print("  config                Gestion de la configuration MCP")
    print("  init                  Générer les fichiers de configuration (piag, gitlab, wikisi)")
    print("  gitlab-clone          Cloner des projets GitLab depuis la configuration")
    print("  gitlab-monofile       Generer un monofile a partir d'un repo clone")
    print("  test                  Tests des modules Ambulon")
    print()
    print("Modules de conversion:")
    print("  img2pdf               Convertir images en PDF")
    print("  compress-pdf          Compresser un fichier PDF")
    print("  html2md               Convertir HTML en Markdown")
    print("  md2html               Convertir Markdown en HTML")
    print("  html2pdf              Convertir HTML en PDF (avec Playwright)")
    print("  pdf2html              Convertir PDF en HTML")
    print("  pdf2md                Convertir PDF en Markdown")
    print("  json2jsonl            Convertir JSON array en JSONL")
    print("  json2md               Convertir JSON en Markdown")
    print()
    print("Modules d'encoding:")
    print("  check-utf8            Vérifier l'encodage des fichiers Markdown")
    print("  fix-utf8              Corriger l'encodage des fichiers Markdown")
    print()
    print("Modules WikiSI (Parc applicatif):")
    print("  wikisi-extract        Extraire et filtrer des applications depuis JSON")
    print("  wikisi-md             Convertir parc applicatif JSON en Markdown (RAG)")
    print("  wikisi-scrape         Aspirer récursivement un site web WikiSI")
    print()
    print("Modules Processing (Traitement de documents):")
    print("  add-toc-html          Ajouter une table des matières à HTML")
    print("  add-toc-md            Ajouter une table des matières à Markdown")
    print("  concat-html           Concaténer plusieurs fichiers HTML")
    print("  flatten-html          Aplatir une arborescence HTML")
    print("  flatten-md            Aplatir une arborescence Markdown")
    print("  wikisi-flatten        Aplatir une arborescence WikiSI")
    print("  make-html-interactive Rendre HTML interactif (anchors, navigation)")
    print("  merge-html            Fusionner plusieurs fichiers HTML")
    print("  merge-md              Fusionner plusieurs fichiers Markdown")
    print("  md2project            Convertir Markdown en structure de projet")
    print("  project2md            Convertir structure de projet en Markdown")
    print()
    print("Modules RAG PIAG (Retrieval Augmented Generation):")
    print("  Collections:")
    print("    piag-collection-add     Créer une collection RAG")
    print("    piag-collection-list    Lister les collections")
    print("    piag-collection-get     Obtenir les détails d'une collection")
    print("    piag-collection-update  Mettre à jour une collection")
    print("    piag-collection-rm      Supprimer une collection")
    print("  Documents:")
    print("    piag-doc-upload         Upload un document")
    print("    piag-doc-list           Lister les documents")
    print("    piag-doc-get            Obtenir les détails d'un document")
    print("    piag-doc-rm             Supprimer un document")
    print("    piag-doc-chunks         Obtenir les chunks d'un document")
    print("  Recherche:")
    print("    piag-search             Recherche sémantique RAG")
    print()
    print("Options générales:")
    print("  -h, --help    Afficher cette aide")
    print("  --version     Afficher la version")
    print("  --no-log-file Désactiver les logs fichier (console uniquement)")
    print()
    print("Exemples:")
    print("  ambulon scan --help                 Aide du module scan")
    print("  ambulon img2pdf scans/              Convertir images en PDF")
    print("  ambulon pdf2html doc.pdf -o doc.html Convertir PDF en HTML")
    print("  ambulon pdf2md doc.pdf -o doc.md   Convertir PDF en Markdown")
    print("  ambulon html2md doc.html            Convertir HTML en Markdown")
    print("  ambulon add-toc-md doc.md           Ajouter une TOC à Markdown")
    print("  ambulon flatten-md docs/            Aplatir arborescence Markdown")
    print("  ambulon merge-html dir/ -o out.html Fusionner HTML")
    print("  ambulon wikisi-extract apps.json -o subset.json -r 1-10")
    print("  ambulon wikisi-md apps.json -o apps.md --verbose")
    print("  ambulon mcp                         Démarrer le serveur MCP")
    print("  ambulon gitlab-clone                Cloner les projets configurés")
    print("  ambulon gitlab-monofile G:\\repos\\my-project")
    print()
    print("Pour plus d'informations sur un module spécifique:")
    print("  ambulon [MODULE] --help")


def handle_config_command():
    """Gère les commandes de configuration MCP."""
    if len(sys.argv) < 3:
        print("Usage: ambulon config [COMMANDE]")
        print()
        print("Commandes disponibles:")
        print("  export [FICHIER]     Exporter la configuration MCP")
        print("  install [ASSISTANT]  Installer la config pour un assistant")
        print("  status               Afficher le statut des configurations")
        print("  test                 Tester le serveur MCP")
        print("  paths                Afficher tous les chemins de config")
        print("  claude-path          Afficher le chemin de config Claude")
        print()
        print("Assistants supportes pour install:")
        print("  claude, openrouter, aider, continue, all")
        print()
        print("Exemples:")
        print("  ambulon config export")
        print("  ambulon config install claude")
        print("  ambulon config install all")
        print("  ambulon config status")
        print("  ambulon config test")
        return 1
    
    subcommand = sys.argv[2]
    
    # Gérer l'aide pour le module config
    if subcommand in ['-h', '--help']:
        print("Usage: ambulon config [COMMANDE]")
        print()
        print("Commandes disponibles:")
        print("  export [FICHIER]     Exporter la configuration MCP")
        print("  install [ASSISTANT]  Installer la config pour un assistant")
        print("  status               Afficher le statut des configurations")
        print("  test                 Tester le serveur MCP")
        print("  paths                Afficher tous les chemins de config")
        print("  claude-path          Afficher le chemin de config Claude")
        print()
        print("Assistants supportes pour install:")
        print("  claude, openrouter, aider, continue, all")
        print()
        print("Exemples:")
        print("  ambulon config export")
        print("  ambulon config install claude")
        print("  ambulon config install all")
        print("  ambulon config status")
        print("  ambulon config test")
        return 0
    
    if subcommand == 'export':
        try:
            from pathlib import Path
            output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("mcp-config.json")
            exported_path = export_mcp_config(output_file)
            print(f"Configuration MCP exportee vers: {exported_path}")
            print()
            print("Pour utiliser avec Claude Desktop:")
            claude_path = get_claude_config_path()
            print(f"1. Creez le repertoire: {claude_path.parent}")
            print(f"2. Copiez le contenu dans: {claude_path}")
            return 0
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return 1
    
    elif subcommand == 'install':
        from app.mcp.core.config import (create_claude_config, create_openrouter_config, 
                           create_aider_config, create_continue_config)
        
        assistant = sys.argv[3] if len(sys.argv) > 3 else "claude"
        force = "--force" in sys.argv
        
        try:
            if assistant == "all":
                print("Installation de la configuration MCP pour tous les assistants...")
                print()
                
                configs = {
                    "Claude Desktop": create_claude_config,
                    "OpenRouter": create_openrouter_config,
                    "Aider": create_aider_config,
                    "Continue (VSCode)": create_continue_config
                }
                
                for name, create_func in configs.items():
                    try:
                        create_func(force)
                        print(f"OK {name}: Configuration installee")
                    except Exception as e:
                        print(f"ERREUR {name}: Erreur - {e}")
                
            elif assistant == "claude":
                create_claude_config(force)
                print("OK Configuration Claude Desktop installee")
                
            elif assistant == "openrouter":
                create_openrouter_config(force)
                print("OK Configuration OpenRouter installee")
                
            elif assistant == "aider":
                create_aider_config(force)
                print("OK Configuration Aider installee")
                
            elif assistant == "continue":
                create_continue_config(force)
                print("OK Configuration Continue (VSCode) installee")
                
            else:
                print(f"Assistant inconnu: {assistant}")
                print("Assistants supportes: claude, openrouter, aider, continue, all")
                return 1
            
            print()
            print("Redemarrez votre assistant pour prendre en compte les changements.")
            return 0
            
        except Exception as e:
            print(f"Erreur lors de l'installation: {e}")
            return 1
    
    elif subcommand == 'status':
        from app.mcp.core.config import get_installation_status, test_mcp_server
        from pathlib import Path
        
        print("Statut des configurations MCP Ambulon:")
        print("=" * 50)
        
        status = get_installation_status()
        
        for assistant, info in status.items():
            print(f"\n{assistant.upper()}:")
            print(f"  Repertoire: {'OK' if info['directory_exists'] else 'NON'} {Path(info['config_path']).parent}")
            print(f"  Config:     {'OK' if info['config_exists'] else 'NON'} {info['config_path']}")
            print(f"  Ambulon:    {'OK' if info['ambulon_configured'] else 'NON'} {'Configure' if info['ambulon_configured'] else 'Non configure'}")
        
        print(f"\nSERVEUR MCP:")
        test_results = test_mcp_server()
        print(f"  Accessible: {'OK' if test_results['server_accessible'] else 'NON'}")
        print(f"  Outils:     {'OK' if test_results['tools_available'] else 'NON'} ({test_results['tools_count']} disponibles)")
        
        if test_results['error']:
            print(f"  Erreur:     {test_results['error']}")
        
        return 0
    
    elif subcommand == 'test':
        from app.mcp.core.config import test_mcp_server
        
        print("Test du serveur MCP Ambulon...")
        print()
        
        results = test_mcp_server()
        
        if results['server_accessible']:
            print("OK Serveur MCP accessible")
        else:
            print("NON Serveur MCP non accessible")
        
        if results['tools_available']:
            print(f"OK Outils disponibles ({results['tools_count']} outils)")
        else:
            print("NON Aucun outil disponible")
        
        if results['error']:
            print(f"ERREUR: {results['error']}")
            return 1
        
        # Test d'intégration rapide
        print("\nTest d'intégration rapide...")
        try:
            import asyncio
            from app.mcp.core.server import handle_list_tools
            
            # Test de liste des outils
            tools = asyncio.run(handle_list_tools())
            print(f"OK {len(tools)} outils MCP listés avec succès")
            
            # Afficher les outils disponibles
            print("\nOutils MCP disponibles:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
        except Exception as e:
            print(f"ERREUR lors du test d'intégration: {e}")
            return 1
        
        print()
        print("Le serveur MCP fonctionne correctement!")
        return 0
    
    elif subcommand == 'paths':
        from app.mcp.core.config import get_config_paths
        
        print("Chemins de configuration pour tous les assistants:")
        print("=" * 55)
        
        paths = get_config_paths()
        
        for assistant, assistant_paths in paths.items():
            print(f"\n{assistant.upper()}:")
            for path_type, path in assistant_paths.items():
                exists = "OK" if path.exists() else "NON"
                print(f"  {path_type}: {exists} {path}")
        
        return 0
    
    elif subcommand == 'claude-path':
        claude_path = get_claude_config_path()
        print(f"Chemin de configuration Claude Desktop:")
        print(f"  {claude_path}")
        print()
        if claude_path.exists():
            print("Le fichier existe")
        else:
            print("Le fichier n'existe pas")
            print(f"  Creez d'abord le repertoire: {claude_path.parent}")
        return 0
    
    else:
        print(f"Commande inconnue: {subcommand}")
        print("Utilisez 'ambulon config' pour voir les commandes disponibles.")
        return 1


def handle_test_command():
    """Gère les commandes de test."""
    import subprocess
    import os
    from pathlib import Path
    
    if len(sys.argv) < 3:
        print("Usage: ambulon test [MODULE]")
        print()
        print("Modules de test disponibles:")
        print("  config    Tester le module de configuration MCP")
        print("  scan      Tester le module de scan")
        print("  ocr       Tester le module OCR")
        print("  mcp       Tester le serveur MCP")
        print("  mcp-live  Tester le serveur MCP en conditions réelles")
        print("  all       Tester tous les modules")
        print()
        print("Exemples:")
        print("  ambulon test config")
        print("  ambulon test all")
        return 1
    
    test_module = sys.argv[2]
    
    if test_module in ['-h', '--help']:
        print("Usage: ambulon test [MODULE]")
        print()
        print("Modules de test disponibles:")
        print("  config    Tester le module de configuration MCP")
        print("  scan      Tester le module de scan")
        print("  ocr       Tester le module OCR")
        print("  mcp       Tester le serveur MCP")
        print("  all       Tester tous les modules")
        print()
        print("Exemples:")
        print("  ambulon test config")
        print("  ambulon test all")
        return 0
    
    # Utiliser pytest pour exécuter les tests
    try:
        if test_module == 'all':
            print("Execution de tous les tests avec pytest...")
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/", "-v", "--tb=short"
            ], cwd=os.getcwd())
            return result.returncode
            
        elif test_module in ['config', 'scan', 'ocr', 'mcp', 'mcp-live']:
            print(f"Execution des tests {test_module} avec pytest...")
            
            if test_module == 'mcp':
                # Pour MCP, exécuter aussi les tests d'intégration
                print("Tests unitaires MCP...")
                test_file = "tests/test_mcp.py"
                if os.path.exists(test_file):
                    result1 = subprocess.run([
                        sys.executable, "-m", "pytest", 
                        test_file, "-v", "--tb=short"
                    ], cwd=os.getcwd())
                
                print("\nTests d'intégration MCP...")
                integration_file = "tests/test_mcp_integration.py"
                if os.path.exists(integration_file):
                    result2 = subprocess.run([
                        sys.executable, "-m", "pytest", 
                        integration_file, "-v", "--tb=short"
                    ], cwd=os.getcwd())
                    return max(result1.returncode if 'result1' in locals() else 0, 
                              result2.returncode)
                else:
                    # Exécuter les tests d'intégration directement
                    try:
                        from tests.test_mcp_integration import run_mcp_integration_tests
                        success = run_mcp_integration_tests()
                        return 0 if success else 1
                    except ImportError:
                        print("Tests d'intégration MCP non disponibles")
                        return result1.returncode if 'result1' in locals() else 1
            elif test_module == 'mcp-live':
                print("Test du serveur MCP en conditions réelles...")
                
                # Vérifier si le script de test existe
                test_script = Path("test_mcp_server.py")
                if test_script.exists():
                    result = subprocess.run([
                        sys.executable, str(test_script)
                    ], cwd=os.getcwd())
                    return result.returncode
                else:
                    print("Script de test MCP non trouvé. Créez test_mcp_server.py")
                    return 1
            else:
                test_file = f"tests/test_{test_module}.py"
                if not os.path.exists(test_file):
                    print(f"Fichier de test {test_file} introuvable")
                    return 1
                
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    test_file, "-v", "--tb=short"
                ], cwd=os.getcwd())
                return result.returncode
        else:
            print(f"Module de test inconnu: {test_module}")
            print("Modules disponibles: config, scan, ocr, mcp, all")
            return 1
            
    except FileNotFoundError:
        print("pytest n'est pas installe. Installez-le avec: pip install pytest")
        return 1
    except Exception as e:
        print(f"Erreur lors de l'execution des tests: {e}")
        return 1


def handle_rag_module(module_name: str):
    """
    Exécute un module RAG PIAG.

    Args:
        module_name: Le nom de la commande (ex: 'piag-collection-add')

    Returns:
        Le code de retour du module.
    """
    # Mapper les noms de commandes aux fonctions main()
    command_to_import = {
        'piag-collection-add': ('app.piag.commands.piag_collection_add', 'main'),
        'piag-collection-list': ('app.piag.commands.piag_collection_list', 'main'),
        'piag-collection-get': ('app.piag.commands.piag_collection_get', 'main'),
        'piag-collection-update': ('app.piag.commands.piag_collection_update', 'main'),
        'piag-collection-rm': ('app.piag.commands.piag_collection_rm', 'main'),
        'piag-doc-upload': ('app.piag.commands.piag_doc_upload', 'main'),
        'piag-doc-list': ('app.piag.commands.piag_doc_list', 'main'),
        'piag-doc-get': ('app.piag.commands.piag_doc_get', 'main'),
        'piag-doc-rm': ('app.piag.commands.piag_doc_rm', 'main'),
        'piag-doc-chunks': ('app.piag.commands.piag_doc_chunks', 'main'),
        'piag-search': ('app.piag.commands.piag_search', 'main'),
    }

    import_info = command_to_import.get(module_name)
    if not import_info:
        print(f"Module RAG inconnu: {module_name}", file=sys.stderr)
        return 1

    module_path, function_name = import_info

    try:
        # Importer dynamiquement la fonction main()
        import importlib
        module = importlib.import_module(module_path)
        main_func = getattr(module, function_name)

        # Préparer les arguments (enlever 'ambulon' et le nom de la commande)
        args = sys.argv[2:]

        # Appeler la fonction main() avec les arguments
        return main_func(args)
    except Exception as e:
        print(f"Erreur lors de l'exécution du module {module_name}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    print("DEBUG: app.cli.cli main() function entered.", file=sys.stderr)
    """Fonction principale appelée par la commande `ambulon`."""
    # Configure logging for the main CLI entry point
    # Console output only (no log file) - each command creates its own log file
    if '--no-log-file' in sys.argv:
        import os
        os.environ["AMBULON_NO_FILE_LOGS"] = "1"
        # Remove the flag so subcommand parsers don't reject it
        sys.argv = [arg for arg in sys.argv if arg != '--no-log-file']
    verbose = '--verbose' in sys.argv or '-v' in sys.argv # Check for verbose early
    setup_logging(level=logging.DEBUG if verbose else logging.INFO, log_file_prefix=None)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Gérer les options d'aide globales
        if command in ['-h', '--help']:
            show_help()
            return 0
        elif command == '--version':
            from . import __version__
            print(f"Ambulon version {__version__}")
            return 0
        elif command == 'scan':
            # Retirer 'scan' des arguments et lancer le module scan
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # Garder le nom du programme et les arguments après 'scan'
            try:
                return scan_main()
            finally:
                sys.argv = original_argv
        elif command == 'ocr':
            # Retirer 'ocr' des arguments et lancer le module ocr
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # Garder le nom du programme et les arguments après 'ocr'
            try:
                return ocr_main()
            finally:
                sys.argv = original_argv
        elif command == 'mcp':
            # Retirer 'mcp' des arguments et lancer le module mcp
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]  # Garder le nom du programme et les arguments après 'mcp'
            try:
                return mcp_main()
            finally:
                sys.argv = original_argv
        elif command == 'img2pdf':
            # Retirer 'img2pdf' des arguments et lancer le module img2pdf
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return img2pdf_main()
            finally:
                sys.argv = original_argv
        elif command == 'compress-pdf':
            # Retirer 'compress-pdf' des arguments et lancer le module compress_pdf
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return compress_pdf_main()
            finally:
                sys.argv = original_argv
        elif command == 'html2md':
            # Convertir HTML en Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon html2md <input.html> [-o <output.md>] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                else:
                    i += 1
            return process_html_to_markdown(input_file, output_file, verbose)
        elif command == 'md2html':
            # Convertir Markdown en HTML
            if len(sys.argv) < 3:
                print("Usage: ambulon md2html <input.md> [-o <output.html>] [--verbose] [--no-standalone]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            verbose = False
            standalone = True
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                elif sys.argv[i] == '--no-standalone':
                    standalone = False
                    i += 1
                else:
                    i += 1
            return process_markdown_to_html(input_file, output_file, verbose, standalone)
        elif command == 'html2pdf':
            # Convertir HTML en PDF
            if len(sys.argv) < 3:
                print("Usage: ambulon html2pdf <input.html> [-o <output.pdf>] [--orientation portrait|landscape] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            orientation = 'portrait'
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--orientation' and i + 1 < len(sys.argv):
                    orientation = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                else:
                    i += 1
            return convert_html_to_pdf(input_file, output_file, orientation, verbose)
        elif command == 'json2jsonl':
            # Convertir JSON en JSONL
            if len(sys.argv) < 3:
                print("Usage: ambulon json2jsonl <input.json> -o <output.jsonl> [--array-key KEY] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            array_key = None
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--array-key' and i + 1 < len(sys.argv):
                    array_key = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            if not output_file:
                print("Error: -o/--output is required")
                return 1
            return json_to_jsonl(input_file, output_file, array_key, verbose)
        elif command == 'json2md':
            # Convertir JSON en Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon json2md <input.json> [-o <output.md>] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                else:
                    i += 1
            return process_json_to_markdown(input_file, output_file, verbose)
        elif command == 'pdf2html':
            # Convertir PDF en HTML
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return pdf2html_main()
            finally:
                sys.argv = original_argv
        elif command == 'pdf2md':
            # Convertir PDF en Markdown
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return pdf2md_main()
            finally:
                sys.argv = original_argv
        elif command == 'check-utf8':
            # Vérifier l'encodage des fichiers Markdown
            return check_md_cli(sys.argv[2:])
        elif command == 'fix-utf8':
            # Corriger l'encodage des fichiers Markdown
            return fix_md_cli(sys.argv[2:])
        elif command == 'wikisi-extract':
            # Extraire et filtrer des applications depuis JSON
            from app.wikisi import wikisi_extract_json_cli
            return wikisi_extract_json_cli(sys.argv[2:])
        elif command == 'wikisi-md':
            # Convertir parc applicatif JSON en Markdown
            from app.wikisi import wikisi_json_to_md_cli
            return wikisi_json_to_md_cli(sys.argv[2:])
        elif command == 'wikisi-scrape':
            # Aspirer récursivement un site web WikiSI
            from app.wikisi.commands.wikisi_scraper import main as wikisi_scrape_main
            return wikisi_scrape_main(sys.argv[2:])
        elif command == 'add-toc-html':
            # Ajouter TOC à HTML
            return add_toc4html_cli(sys.argv[2:])
        elif command == 'add-toc-md':
            # Ajouter TOC à Markdown
            return add_toc4md_cli(sys.argv[2:])
        elif command == 'concat-html':
            # Concaténer HTML
            return concat_html_cli(sys.argv[2:])
        elif command == 'flatten-html':
            # Aplatir HTML
            return flatten_html_cli(sys.argv[2:])
        elif command == 'flatten-md':
            # Aplatir Markdown
            return flatten_md_cli(sys.argv[2:])
        elif command == 'wikisi-flatten':
            # Aplatir WikiSI
            from app.wikisi import flatten_wikisi_directory
            if len(sys.argv) < 3:
                print("Usage: ambulon flatten-wikisi <source_dir> [-o <output_dir>] [--verbose]")
                return 1
            source = sys.argv[2]
            output = None
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            return flatten_wikisi_directory(source, output, verbose)
        elif command == 'make-html-interactive':
            # Rendre HTML interactif
            if len(sys.argv) < 3:
                print("Usage: ambulon make-interactive <input.html> [-o <output.html>] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output = None
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            return make_html_interactive(input_file, output, verbose)
        elif command == 'merge-html':
            # Fusionner HTML
            return merge_html_cli(sys.argv[2:])
        elif command == 'merge-md':
            # Fusionner Markdown
            return merge_md_cli(sys.argv[2:])
        elif command == 'md2project':
            # Convertir Markdown en projet
            return md2project_cli(sys.argv[2:])
        elif command == 'project2md':
            # Convertir projet en Markdown
            return project2md_cli(sys.argv[2:])
        elif command == 'config':
            return handle_config_command()
        elif command == 'init':
            return handle_init_command()
        elif command == 'gitlab-clone':
            # Cloner des projets GitLab depuis la configuration
            return gitlab_clone_main(sys.argv[2:])
        elif command == 'gitlab-monofile':
            # Generer un monofile depuis un repo clone
            return gitlab_monofile_main(sys.argv[2:])
        elif command == 'test':
            return handle_test_command()
        # Commandes RAG PIAG
        elif command in ['piag-collection-add', 'piag-collection-list', 'piag-collection-get',
                        'piag-collection-update', 'piag-collection-rm',
                        'piag-doc-upload', 'piag-doc-list', 'piag-doc-get',
                        'piag-doc-rm', 'piag-doc-chunks', 'piag-search']:
            return handle_rag_module(command)
        else:
            print(f"Module inconnu: {command}")
            print("Utilisez 'ambulon --help' pour voir les modules disponibles.")
            return 1
    else:
        show_help()
        return 0
