"""Module CLI pour Ambulon."""
import sys
import argparse

from . import hello
from .scan import main as scan_main
from .ocr import main as ocr_main
from .mcp import main as mcp_main
from .config import export_mcp_config, get_claude_config_path


def show_help():
    """Affiche l'aide principale avec les modules disponibles."""
    print(hello())
    print()
    print("Usage: ambulon [MODULE] [OPTIONS]")
    print()
    print("Modules disponibles:")
    print("  scan    Module de scan TWAIN avec profils DPI")
    print("  ocr     Module OCR - Reconnaissance optique de caractères")
    print("  mcp     Serveur MCP pour assistants IA")
    print("  config  Gestion de la configuration MCP")
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
    print("  ambulon mcp                  Démarrer le serveur MCP")
    print("  ambulon config export        Exporter la config MCP")
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
        print("  claude-path          Afficher le chemin de config Claude")
        print()
        print("Exemples:")
        print("  ambulon config export")
        print("  ambulon config export mon-config.json")
        print("  ambulon config claude-path")
        return 1
    
    subcommand = sys.argv[2]
    
    if subcommand == 'export':
        try:
            from pathlib import Path
            output_file = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("mcp-config.json")
            exported_path = export_mcp_config(output_file)
            print(f"Configuration MCP exportée vers: {exported_path}")
            print()
            print("Pour utiliser avec Claude Desktop:")
            claude_path = get_claude_config_path()
            print(f"1. Créez le répertoire: {claude_path.parent}")
            print(f"2. Copiez le contenu dans: {claude_path}")
            return 0
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return 1
    
    elif subcommand == 'claude-path':
        claude_path = get_claude_config_path()
        print(f"Chemin de configuration Claude Desktop:")
        print(f"  {claude_path}")
        print()
        if claude_path.exists():
            print("✓ Le fichier existe")
        else:
            print("✗ Le fichier n'existe pas")
            print(f"  Créez d'abord le répertoire: {claude_path.parent}")
        return 0
    
    else:
        print(f"Commande inconnue: {subcommand}")
        print("Utilisez 'ambulon config' pour voir les commandes disponibles.")
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
        elif command == 'config':
            return handle_config_command()
        else:
            print(f"Module inconnu: {command}")
            print("Utilisez 'ambulon --help' pour voir les modules disponibles.")
            return 1
    else:
        show_help()
        return 0
