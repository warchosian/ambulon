"""Module CLI pour Ambulon."""
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

from . import hello
from .scan import main as scan_main
from .ocr import main as ocr_main
from .mcp import main as mcp_main
from .img2pdf import main as img2pdf_main
from .compress_pdf import main as compress_pdf_main
from .config import export_mcp_config, get_claude_config_path


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
    print("  scan         Module de scan TWAIN avec profils DPI")
    print("  ocr          Module OCR - Reconnaissance optique de caractères")
    print("  img2pdf      Convertir images en PDF")
    print("  compress-pdf Compresser un fichier PDF")
    print("  mcp          Serveur MCP pour assistants IA")
    print("  config       Gestion de la configuration MCP")
    print("  test         Tests des modules Ambulon")
    print()
    print("Options générales:")
    print("  -h, --help    Afficher cette aide")
    print("  --version     Afficher la version")
    print()
    print("Exemples:")
    print("  ambulon scan --help          Aide du module scan")
    print("  ambulon scan -r 300 -o scans/")
    print("  ambulon ocr --help           Aide du module OCR")
    print("  ambulon ocr -i image.jpg -l fra")
    print("  ambulon img2pdf scans/       Convertir images en PDF")
    print("  ambulon compress-pdf doc.pdf Compresser un PDF")
    print("  ambulon mcp                  Démarrer le serveur MCP")
    print("  ambulon config export        Exporter la config MCP")
    print("  ambulon test config          Tester la configuration")
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
        from .config import (create_claude_config, create_openrouter_config, 
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
        from .config import get_installation_status, test_mcp_server
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
        from .config import test_mcp_server
        
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
            from .mcp import handle_list_tools
            
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
        from .config import get_config_paths
        
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
        elif command == 'config':
            return handle_config_command()
        elif command == 'test':
            return handle_test_command()
        else:
            print(f"Module inconnu: {command}")
            print("Utilisez 'ambulon --help' pour voir les modules disponibles.")
            return 1
    else:
        show_help()
        return 0
