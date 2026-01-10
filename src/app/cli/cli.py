"""Module CLI pour Ambulon."""
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

from . import hello
from app.scan.commands.scan_main import main as scan_main
from app.ocr.commands.ocr_main import main as ocr_main
from app.mcp.mcp_server import main as mcp_main
from app.mcp.mcp_config import export_mcp_config, get_claude_config_path
from app.piag import create_collection # NEW - migration vers nouvelle architecture
from app.gitlab.commands.gitlab_clone import main as gitlab_clone_main

# Modules de conversion
from app.conversion import (
    compress_pdf_main,
    img2pdf_main,
    process_html_to_markdown,
    process_markdown_to_html,
    convert_html_to_pdf,
    json_to_jsonl,
    process_json_to_markdown,
)

# Modules d'encoding
from app.encoding import check_md_cli, fix_md_cli

# Module WikiSI
from app.wikisi import process_parkjson2json, process_parkjson2md, flatten_wikisi_directory, scrape_wikisi

# Module Processing
from app.processing import (
    add_toc_to_html,
    add_toc_to_markdown,
    concatenate_html_files,
    flatten_html_directory,
    flatten_markdown_directory,
    make_html_interactive,
    fusion_html_files,
    fusion_markdown_files,
    md2project,
    project_to_markdown,
)

import requests # NEW
import json # NEW


def setup_logging(verbose: bool = False):
    """Configure le système de logging pour les modules."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    log_file = logs_dir / f"ambulon.{timestamp}.log"
    
    level = logging.DEBUG if verbose else logging.INFO
    
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    
    logging.basicConfig(
        level=level,
        handlers=[file_handler, console_handler],
        force=True
    )
    
    return log_file


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
    print("  gitlab-clone          Cloner des projets GitLab depuis la configuration")
    print("  test                  Tests des modules Ambulon")
    print()
    print("Modules de conversion:")
    print("  img2pdf               Convertir images en PDF")
    print("  compress-pdf          Compresser un fichier PDF")
    print("  html2md               Convertir HTML en Markdown")
    print("  md2html               Convertir Markdown en HTML")
    print("  html2pdf              Convertir HTML en PDF (avec Playwright)")
    print("  json2jsonl            Convertir JSON array en JSONL")
    print("  json2md               Convertir JSON en Markdown")
    print()
    print("Modules d'encoding:")
    print("  chk-utf8              Vérifier l'encodage des fichiers Markdown")
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
    print("  flatten-wikisi        Aplatir une arborescence WikiSI")
    print("  make-interactive      Rendre HTML interactif (anchors, navigation)")
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
    print()
    print("Exemples:")
    print("  ambulon scan --help                 Aide du module scan")
    print("  ambulon img2pdf scans/              Convertir images en PDF")
    print("  ambulon html2md doc.html            Convertir HTML en Markdown")
    print("  ambulon add-toc-md doc.md           Ajouter une TOC à Markdown")
    print("  ambulon flatten-md docs/            Aplatir arborescence Markdown")
    print("  ambulon merge-html dir/ -o out.html Fusionner HTML")
    print("  ambulon wikisi-extract apps.json -o subset.json -r 1-10")
    print("  ambulon wikisi-md apps.json -o apps.md --verbose")
    print("  ambulon mcp                         Démarrer le serveur MCP")
    print("  ambulon gitlab-clone                Cloner les projets configurés")
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
        from app.mcp.mcp_config import (create_claude_config, create_openrouter_config, 
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
        from app.mcp.mcp_config import get_installation_status, test_mcp_server
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
        from app.mcp.mcp_config import test_mcp_server
        
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
            from app.mcp.mcp_server import handle_list_tools
            
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
        from app.mcp.mcp_config import get_config_paths
        
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
    Exécute un module RAG en lançant son __main__ block.

    Args:
        module_name: Le nom du module Python (ex: 'piag_collection_add')

    Returns:
        Le code de retour du module.
    """
    # Mapper les noms de commandes aux noms de modules Python
    command_to_module = {
        'piag-collection-add': 'piag_collection_add',
        'piag-collection-list': 'piag_collection_list',
        'piag-collection-get': 'piag_collection_get',
        'piag-collection-update': 'piag_collection_update',
        'piag-collection-rm': 'piag_collection_rm',
        'piag-doc-upload': 'piag_doc_upload',
        'piag-doc-list': 'piag_doc_list',
        'piag-doc-get': 'piag_doc_get',
        'piag-doc-rm': 'piag_doc_rm',
        'piag-doc-chunks': 'piag_doc_chunks',
        'piag-search': 'piag_search',
    }

    python_module = command_to_module.get(module_name)
    if not python_module:
        print(f"Module RAG inconnu: {module_name}", file=sys.stderr)
        return 1

    # Manipuler sys.argv pour enlever le nom de la commande
    original_argv = sys.argv
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    try:
        # Importer et exécuter le module comme __main__
        import runpy
        runpy.run_module(f'app.piag.commands.{python_module}', run_name='__main__')
        return 0
    except SystemExit as e:
        return e.code if e.code else 0
    except Exception as e:
        print(f"Erreur lors de l'exécution du module {module_name}: {e}", file=sys.stderr)
        return 1
    finally:
        sys.argv = original_argv


def main():
    """Fonction principale appelée par la commande `ambulon`."""
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
        elif command == 'chk-utf8':
            # Vérifier l'encodage des fichiers Markdown
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return check_md_cli()
            finally:
                sys.argv = original_argv
        elif command == 'fix-utf8':
            # Corriger l'encodage des fichiers Markdown
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return fix_md_cli()
            finally:
                sys.argv = original_argv
        elif command == 'wikisi-extract':
            # Extraire et filtrer des applications depuis JSON
            if len(sys.argv) < 3:
                print("Usage: ambulon wikisi-extract <input.json> -o <output.json> [-r RANGE] [-n NAME] [-i ID] [--verbose] [--split-dir DIR]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            range_spec = None
            name_filter = None
            id_filter = None
            verbose = False
            preserve_structure = True
            include_metadata = True
            split_dir = None
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-r', '--range'] and i + 1 < len(sys.argv):
                    range_spec = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-n', '--name'] and i + 1 < len(sys.argv):
                    name_filter = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-i', '--id'] and i + 1 < len(sys.argv):
                    id_filter = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--split-dir' and i + 1 < len(sys.argv):
                    split_dir = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--no-preserve-structure':
                    preserve_structure = False
                    i += 1
                elif sys.argv[i] == '--no-metadata':
                    include_metadata = False
                    i += 1
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                else:
                    i += 1
            if not output_file and not split_dir:
                print("Error: Either -o/--output or --split-dir is required")
                return 1
            return process_parkjson2json(input_file, output_file, verbose, range_spec, name_filter, id_filter, preserve_structure, include_metadata, split_dir)
        elif command == 'wikisi-md':
            # Convertir parc applicatif JSON en Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon wikisi-md <input.json> [-o <output.md>] [-r RANGE] [-n NAME] [-i ID] [--verbose] [--split-dir DIR]")
                return 1
            input_file = sys.argv[2]
            output_file = None
            range_spec = None
            name_filter = None
            id_filter = None
            verbose = False
            split_dir = None
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-r', '--range'] and i + 1 < len(sys.argv):
                    range_spec = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-n', '--name'] and i + 1 < len(sys.argv):
                    name_filter = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-i', '--id'] and i + 1 < len(sys.argv):
                    id_filter = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--split-dir' and i + 1 < len(sys.argv):
                    split_dir = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                else:
                    i += 1
            return process_parkjson2md(input_file, output_file, verbose, range_spec, name_filter, id_filter, split_dir)
        elif command == 'wikisi-scrape':
            # Aspirer récursivement un site web WikiSI
            url = None
            output_dir = None
            config_path = None
            max_depth = None
            delay = None
            verbose = False
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] in ['-u', '--url'] and i + 1 < len(sys.argv):
                    url = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_dir = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-c', '--config'] and i + 1 < len(sys.argv):
                    config_path = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-d', '--depth'] and i + 1 < len(sys.argv):
                    max_depth = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == '--delay' and i + 1 < len(sys.argv):
                    delay = float(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                elif sys.argv[i] in ['-h', '--help']:
                    print("Usage: ambulon wikisi-scrape [OPTIONS]")
                    print()
                    print("Options:")
                    print("  -u, --url URL         URL du site WikiSI à aspirer (ou WIKISI_BASE_URL)")
                    print("  -o, --output DIR      Répertoire de sortie (ou WIKISI_OUTPUT_DIR)")
                    print("  -c, --config FILE     Fichier de configuration YAML")
                    print("  -d, --depth N         Profondeur maximale de récursion (-1 = illimité)")
                    print("  --delay SECONDS       Délai entre requêtes (en secondes)")
                    print("  -v, --verbose         Mode verbeux (logs détaillés)")
                    print("  -h, --help            Afficher cette aide")
                    print()
                    print("Hiérarchie de configuration (priorité décroissante):")
                    print("  1. Arguments CLI")
                    print("  2. Fichier YAML (--config)")
                    print("  3. Variables d'environnement (WIKISI_*)")
                    print("  4. Valeurs par défaut")
                    print()
                    print("Variables d'environnement supportées:")
                    print("  WIKISI_BASE_URL       URL du site à aspirer")
                    print("  WIKISI_OUTPUT_DIR     Répertoire de sortie")
                    print("  WIKISI_MAX_DEPTH      Profondeur maximale")
                    print("  WIKISI_DELAY          Délai entre requêtes")
                    print("  WIKISI_AUTH_TYPE      Type d'authentification (none/basic/bearer)")
                    print("  WIKISI_USERNAME       Nom d'utilisateur (basic auth)")
                    print("  WIKISI_PASSWORD       Mot de passe (basic auth)")
                    print("  WIKISI_TOKEN          Token d'authentification (bearer)")
                    print("  WIKISI_LOG_LEVEL      Niveau de log (debug/info/warning/error)")
                    print()
                    print("Exemples:")
                    print("  ambulon wikisi-scrape --url https://wikisi.example.fr --output ./data")
                    print("  ambulon wikisi-scrape --config config/wikisi.yaml --verbose")
                    print("  WIKISI_BASE_URL=https://wikisi.fr ambulon wikisi-scrape -o ./wikisi-data")
                    return 0
                else:
                    i += 1
            return scrape_wikisi(url, output_dir, config_path, max_depth, delay, verbose)
        elif command == 'add-toc-html':
            # Ajouter TOC à HTML
            if len(sys.argv) < 3:
                print("Usage: ambulon add-toc-html <input.html> [-o <output.html>] [--min-level N] [--max-level N] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output = None
            min_level = 1
            max_level = 6
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--min-level' and i + 1 < len(sys.argv):
                    min_level = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == '--max-level' and i + 1 < len(sys.argv):
                    max_level = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            return add_toc_to_html(input_file, output, min_level, max_level, verbose)
        elif command == 'add-toc-md':
            # Ajouter TOC à Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon add-toc-md <input.md> [-o <output.md>] [--min-level N] [--max-level N] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output = None
            min_level = 1
            max_level = 6
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--min-level' and i + 1 < len(sys.argv):
                    min_level = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] == '--max-level' and i + 1 < len(sys.argv):
                    max_level = int(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            return add_toc_to_markdown(input_file, output, min_level, max_level, verbose)
        elif command == 'concat-html':
            # Concaténer HTML
            if len(sys.argv) < 3:
                print("Usage: ambulon concat-html <directory> -o <output.html> [--verbose]")
                return 1
            directory = sys.argv[2]
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
            if not output:
                print("Error: -o/--output is required")
                return 1
            return concatenate_html_files(directory, output, verbose)
        elif command == 'flatten-html':
            # Aplatir HTML
            if len(sys.argv) < 3:
                print("Usage: ambulon flatten-html <source_dir> [-o <output_dir>] [--verbose]")
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
            return flatten_html_directory(source, output, verbose)
        elif command == 'flatten-md':
            # Aplatir Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon flatten-md <source_dir> [-o <output_dir>] [--verbose]")
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
            return flatten_markdown_directory(source, output, verbose)
        elif command == 'flatten-wikisi':
            # Aplatir WikiSI
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
        elif command == 'make-interactive':
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
            if len(sys.argv) < 3:
                print("Usage: ambulon merge-html <directory> -o <output.html> [--verbose]")
                return 1
            directory = sys.argv[2]
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
            if not output:
                print("Error: -o/--output is required")
                return 1
            return fusion_html_files(directory, output, verbose)
        elif command == 'merge-md':
            # Fusionner Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon merge-md <directory> -o <output.md> [--verbose]")
                return 1
            directory = sys.argv[2]
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
            if not output:
                print("Error: -o/--output is required")
                return 1
            return fusion_markdown_files(directory, output, verbose)
        elif command == 'md2project':
            # Convertir Markdown en projet
            if len(sys.argv) < 3:
                print("Usage: ambulon md2project <input.md> [-o <output_dir>] [--dry-run] [--overwrite] [--merge] [--verbose]")
                return 1
            input_file = sys.argv[2]
            output = None
            dry_run = False
            overwrite = False
            merge = False
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--dry-run':
                    dry_run = True
                    i += 1
                elif sys.argv[i] == '--overwrite':
                    overwrite = True
                    i += 1
                elif sys.argv[i] == '--merge':
                    merge = True
                    i += 1
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            return md2project(input_file, output, dry_run, overwrite, merge, verbose)
        elif command == 'project2md':
            # Convertir projet en Markdown
            if len(sys.argv) < 3:
                print("Usage: ambulon project2md <project_dir> [-o <output.md>] [--exclude DIR] [--verbose]")
                return 1
            project_dir = sys.argv[2]
            output = None
            exclude_dirs = set()
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--exclude' and i + 1 < len(sys.argv):
                    exclude_dirs.add(sys.argv[i + 1])
                    i += 2
                elif sys.argv[i] in ['-v', '--verbose']:
                    verbose = True
                    i += 1
                else:
                    i += 1
            return project_to_markdown(project_dir, output, exclude_dirs, verbose)
        elif command == 'config':
            return handle_config_command()
        elif command == 'gitlab-clone':
            # Retirer 'gitlab-clone' des arguments et lancer le module gitlab
            original_argv = sys.argv
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            try:
                return gitlab_clone_main()
            finally:
                sys.argv = original_argv
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
