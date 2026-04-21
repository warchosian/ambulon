"""Module CLI pour Ambulon.

All command handlers use lazy imports inside ``main()`` to keep CLI startup
fast and to avoid pulling heavy dependencies when they are not required.
"""
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path


def show_help():
    """Affiche l'aide principale avec les modules disponibles."""
    from . import hello
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
    print("  md2html               Convertir Markdown en HTML (SANS diagrammes)")
    print("  html2pdf              Convertir HTML en PDF (avec Playwright)")
    print("  pdf2html              Convertir PDF en HTML")
    print("  pdf2md                Convertir PDF en Markdown")
    print("  json2jsonl            Convertir JSON array en JSONL")
    print("  json2md               Convertir JSON en Markdown")
    print()
    print("Modules de diagrammes (conversion MD/HTML avec SVG):")
    print("  md2html-diagrams      Convertir Markdown en HTML AVEC diagrammes en SVG")
    print("  diagram2svg4md        Convertir diagrammes en SVG inline dans Markdown")
    print()
    print("Modules VSCode (gestion des extensions):")
    print("  vscode-install        Installer les extensions recommandées pour diagrammes")
    print("  vscode-uninstall      Désinstaller les extensions redondantes")
    print("  vscode-list           Lister les extensions installées")
    print()
    print("Modules GitHub (gestion des releases):")
    print("  github-release        Créer une release GitHub depuis un tag")
    print()
    print("Modules GitLab (gestion des releases):")
    print("  gitlab-release        Créer une release GitLab depuis un tag")
    print()
    print("Modules ZIP (gestion d'archives):")
    print("  zip-create            Créer une archive ZIP avec chiffrement AES-256")
    print("  zip-extract           Extraire une archive ZIP")
    print()
    print("Modules LLM (génération de documents par IA):")
    print("  llm                   Générer des documents via API LLM (Kimi, ChatGPT, Claude)")
    print("  filter                Filtrer et réduire les gros fichiers code.md")
    print("  summarize             Résumer intelligemment les fichiers code.md via LLM")
    print("  plantuml2mermaid      Convertir diagrammes PlantUML en Mermaid")
    print()
    print("Modules d'encoding:")
    print("  check-utf8            Vérifier l'encodage des fichiers Markdown")
    print("  fix-utf8              Corriger l'encodage des fichiers Markdown")
    print()
    print("Modules WikiSI (Parc applicatif):")
    print("  wikisi-extract        Extraire et filtrer des applications depuis JSON")
    print("  wikisi-extract-apps   Extraire les applications désignées en JSON et MD individuels")
    print("  wikisi-md             Convertir parc applicatif JSON en Markdown (RAG)")
    print("  wikisi-scrape         Aspirer récursivement un site web WikiSI")
    print("  wikisi-sync-api       Synchroniser les données (énumérations, applications) depuis l'API WikiSI")
    print()
    print("Modules Processing (Traitement de documents):")
    print("  add-toc               Ajouter une TOC (détection auto MD/HTML)")
    print("  add-toc4html          Ajouter une table des matières à HTML")
    print("  add-toc4md            Ajouter une table des matières à Markdown")
    print("  add-itoc4md           Ajouter des liens retour (iTOC) vers lignes TOC specifiques")
    print("  check-toc4md          Verifier si une TOC existe dans un fichier Markdown")
    print("  check-itoc4md         Verifier si des liens iTOC existent dans un fichier Markdown")
    print("  diagram2svg4md        Convertir diagrammes en SVG dans Markdown")
    print("  concat-html           Concaténer plusieurs fichiers HTML")
    print("  flatten-html          Aplatir une arborescence HTML")
    print("  flatten-md            Aplatir une arborescence Markdown")
    print("  wikisi-flatten        Aplatir une arborescence WikiSI")
    print("  augment               Augmenter HTML avec navigation interactive (anchors, TOC)")
    print("  md2interactive        Convertir MD en HTML interactif complet")
    print("  merge-html            Fusionner plusieurs fichiers HTML")
    print("  merge-md              Fusionner plusieurs fichiers Markdown")
    print("  md2project            Convertir Markdown en structure de projet")
    print("  project2md            Convertir structure de projet en Markdown")
    print("  code2md               Encapsuler du code dans des blocs Markdown")
    print()
    print("Modules PIAG (Retrieval Augmented Generation & Chat):")
    print("  Gestion des RAG (Collections & Documents):")
    print("    piag-rag-create                 Créer un RAG complet (collection + upload)")
    print("    piag-rag-collection-add         Créer une collection RAG")
    print("    piag-rag-collection-list        Lister les collections RAG")
    print("    piag-rag-collection-get         Obtenir les détails d'une collection")
    print("    piag-rag-collection-update      Mettre à jour une collection")
    print("    piag-rag-collection-rm          Supprimer une collection")
    print("    piag-rag-doc-upload             Upload un document vers une collection")
    print("    piag-rag-doc-list               Lister les documents d'une collection")
    print("    piag-rag-doc-get                Obtenir les détails d'un document")
    print("    piag-rag-doc-rm                 Supprimer un document")
    print("    piag-rag-doc-chunks             Obtenir les chunks d'un document")
    print("    piag-rag-search                 Recherche sémantique dans les collections")
    print("  Chat & Completions:")
    print("    piag-chat-apikey-info           Infos sur le token (budget, dépenses)")
    print("    piag-chat-basic-query           Interroger l'API Chat (mode basique)")
    print("    piag-chat-completion            Complétion de texte (endpoint legacy)")
    print("    piag-chat-query                 Interroger avec contexte RAG")
    print("  Pipeline RAG (Workflow complet):")
    print("    piag-rag-then-chat run          Pipeline complet (4 étapes en une commande)")
    print("    piag-rag-then-chat init         Étape 1: Initialiser la collection")
    print("    piag-rag-then-chat ingest       Étape 2: Ingestion des documents")
    print("    piag-rag-then-chat chunk        Étape 3: Création des chunks")
    print("    piag-rag-then-chat generate     Étape 4: Génération de la réponse")
    print()
    print("Options générales:")
    print("  -h, --help    Afficher cette aide")
    print("  --version     Afficher la version")
    print("  --no-log-file Désactiver les logs fichier (console uniquement)")
    print()
    print("Résolution du répertoire config:")
    print("  - Si AMBULON_HOME est défini: $AMBULON_HOME/config")
    print("  - Sinon: <répertoire de lancement>/config")
    print()
    print("Exemples:")
    print("  ambulon scan --help                 Aide du module scan")
    print("  ambulon img2pdf scans/              Convertir images en PDF")
    print("  ambulon pdf2html doc.pdf -o doc.html Convertir PDF en HTML")
    print("  ambulon pdf2md doc.pdf -o doc.md   Convertir PDF en Markdown")
    print("  ambulon html2md doc.html            Convertir HTML en Markdown")
    print("  ambulon add-toc4md doc.md           Ajouter une TOC à Markdown")
    print("  ambulon add-itoc4md doc.md          Ajouter liens retour (iTOC) à la TOC")
    print("  ambulon flatten-md docs/            Aplatir arborescence Markdown")
    print("  ambulon merge-html dir/ -o out.html Fusionner HTML")
    print("  ambulon code2md script.py           Encapsuler code dans Markdown")
    print("  ambulon wikisi-extract apps.json -o subset.json -r 1-10")
    print("  ambulon wikisi-md apps.json -o apps.md --verbose")
    print("  ambulon mcp                         Démarrer le serveur MCP")
    print("  ambulon gitlab-clone                Cloner les projets configurés")
    print("  ambulon gitlab-monofile G:\\repos\\my-project")
    print()
    print("Exemples RAG PIAG:")
    print("  ambulon piag-rag-create --collection-name 'MonRAG' --desc 'Docs'         Collection vide")
    print("  ambulon piag-rag-create --collection-name 'MonRAG' --directory ./docs    Avec documents")
    print("  ambulon piag-rag-collection-list                                         Lister collections")
    print("  ambulon piag-rag-doc-list --collection-name 'MonRAG'                     Lister documents")
    print("  ambulon piag-rag-search --collection-name 'MonRAG' --query 'question'    Rechercher")
    print("  ambulon piag-chat-query --collection-name 'MonRAG' --query 'question'    Chat avec RAG")
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
            from app.mcp.core.config import export_mcp_config, get_claude_config_path
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
        from app.mcp.core.config import get_claude_config_path
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
        # RAG complet
        'piag-rag-create': ('app.piag.commands.piag_rag_create', 'main'),
        # Collections RAG
        'piag-rag-collection-add': ('app.piag.commands.piag_rag_collection_add', 'main'),
        'piag-rag-collection-list': ('app.piag.commands.piag_rag_collection_list', 'main'),
        'piag-rag-collection-get': ('app.piag.commands.piag_rag_collection_get', 'main'),
        'piag-rag-collection-update': ('app.piag.commands.piag_rag_collection_update', 'main'),
        'piag-rag-collection-rm': ('app.piag.commands.piag_rag_collection_rm', 'main'),
        # Documents RAG
        'piag-rag-doc-upload': ('app.piag.commands.piag_rag_doc_upload', 'main'),
        'piag-rag-doc-list': ('app.piag.commands.piag_rag_doc_list', 'main'),
        'piag-rag-doc-get': ('app.piag.commands.piag_rag_doc_get', 'main'),
        'piag-rag-doc-rm': ('app.piag.commands.piag_rag_doc_rm', 'main'),
        'piag-rag-doc-chunks': ('app.piag.commands.piag_rag_doc_chunks', 'main'),
        # Recherche RAG
        'piag-rag-search': ('app.piag.commands.piag_rag_search', 'main'),
        # Chat
        'piag-chat-apikey-info': ('app.piag.commands.piag_chat_apikey_info', 'main'),
        'piag-chat-basic-query': ('app.piag.commands.piag_chat_basic_query', 'main'),
        'piag-chat-completion': ('app.piag.commands.piag_chat_completion', 'main'),
        'piag-chat-query': ('app.piag.commands.piag_chat_query', 'main'),
        # Pipeline RAG (orchestration complète)
        'piag-rag-then-chat': ('app.piag.commands.piag_rag_then_chat', 'main'),
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
    """Fonction principale appelée par la commande `ambulon`."""
    # Logging minimal sans fichier pour éviter les blocages
    import os
    if '--no-log-file' in sys.argv:
        os.environ["AMBULON_NO_FILE_LOGS"] = "1"
        sys.argv = [arg for arg in sys.argv if arg != '--no-log-file']
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    # Configuration logging basique
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    if len(sys.argv) > 1:
        command = sys.argv[1]

        # Gérer les options d'aide globales
        if command in ['-h', '--help']:
            show_help()
            return 0
        if command == '--version':
            from . import __version__
            print(f"Ambulon version {__version__}")
            import os
            from pathlib import Path
            env_home = os.getenv("AMBULON_HOME")
            base_dir = Path(env_home).expanduser() if env_home else Path.cwd()
            config_dir = base_dir / "config"
            status = "OK" if config_dir.exists() else "NON"
            origin = "AMBULON_HOME" if env_home else "répertoire de lancement"
            print(f"AMBULON_HOME: {env_home if env_home else '<non défini>'}")
            print(f"Config base: {base_dir} (source: {origin})")
            print(f"Config dir:  {config_dir} [{status}]")
            return 0

        # Registry-based dispatch for all "standard" commands whose handler
        # is a plain ``main(argv=None) -> int``. See app.cli.registry.
        from app.cli.dispatch import dispatch_standard
        result = dispatch_standard(command)
        if result is not None:
            return result

        # Fallback: PIAG module has its own dispatcher.
        if command.startswith('piag-'):
            return handle_rag_module(command)

        # Legacy / bespoke-parsing branches live below.
        # Commands with a plain ``main()`` handler have been migrated to
        # app.cli.registry and are dispatched via dispatch_standard() above.
        if command == 'html2md':
            # Convertir HTML en Markdown
            from app.conversion import process_html_to_markdown
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
            # Convertir Markdown en HTML SANS conversion des diagrammes
            from app.conversion.commands.md2html import process_markdown_to_html_simple
            if len(sys.argv) < 3 or sys.argv[2] in ['-h', '--help']:
                print("Usage: ambulon md2html <input.md> [-o <output.html>] [--verbose] [--no-standalone] [--toc-backlinks]")
                print()
                print("Convertit un fichier Markdown en HTML (SANS conversion des diagrammes)")
                print("Les blocs PlantUML/Mermaid restent en texte.")
                print()
                print("Pour convertir AVEC les diagrammes en SVG, utilisez:")
                print("  ambulon md2html-diagrams <input.md>")
                print()
                print("Arguments:")
                print("  <input.md>                    Fichier Markdown source")
                print()
                print("Options:")
                print("  -o, --output <file>           Fichier HTML de sortie (défaut: <input>.html)")
                print("  --verbose                     Mode verbeux (affiche les détails)")
                print("  --no-standalone               Génère un fragment HTML au lieu d'un document complet")
                print("  --toc-backlinks               Ajoute des liens retour (↑) après chaque titre")
                print()
                print("Exemples:")
                print("  ambulon md2html document.md")
                print("  ambulon md2html document.md -o result.html --toc-backlinks")
                return 0 if len(sys.argv) > 2 and sys.argv[2] in ['-h', '--help'] else 1
            input_file = sys.argv[2]
            output_file = None
            verbose = False
            standalone = True
            toc_backlinks = False
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
                elif sys.argv[i] == '--toc-backlinks':
                    toc_backlinks = True
                    i += 1
                else:
                    i += 1
            return process_markdown_to_html_simple(input_file, output_file, verbose, standalone, toc_backlinks)
        elif command == 'md2html-diagrams':
            # Convertir Markdown en HTML AVEC conversion des diagrammes
            from app.diagrams import process_markdown_to_html
            if len(sys.argv) < 3 or sys.argv[2] in ['-h', '--help']:
                print("Usage: ambulon md2html-diagrams <input.md> [-o <output.html>] [-p <orientation>] [--verbose] [--no-standalone] [--toc-backlinks] [--plantuml-method auto|jar|kroki] [--plantuml-jar <path>]")
                print()
                print("Convertit un fichier Markdown en HTML AVEC conversion des diagrammes en SVG")
                print("Supporte: PlantUML, Mermaid, Graphviz")
                print()
                print("Arguments:")
                print("  <input.md>                    Fichier Markdown source")
                print()
                print("Options:")
                print("  -o, --output <file>           Fichier HTML de sortie (défaut: <input>.html)")
                print("  -p, --page-orientation <mode> Optimisation pour génération PDF:")
                print("                                  portrait  - 700px max (A4 portrait)")
                print("                                  landscape - 900px max (A4 landscape)")
                print("                                  (par défaut: taille naturelle des SVG, aucune contrainte)")
                print("  --verbose                     Mode verbeux (affiche les détails)")
                print("  --no-standalone               Génère un fragment HTML au lieu d'un document complet")
                print("  --toc-backlinks               Ajoute des liens retour (↑) après chaque titre")
                print("  --plantuml-method <mode>      Méthode de rendu PlantUML:")
                print("                                  auto   - Détection automatique")
                print("                                  jar    - Utilise PlantUML.jar local (plus fiable)")
                print("                                  kroki  - Utilise le service Kroki en ligne (défaut)")
                print("  --plantuml-jar <path>         Chemin vers le fichier PlantUML.jar")
                print()
                print("Exemples:")
                print("  ambulon md2html-diagrams document.md")
                print("  ambulon md2html-diagrams document.md -o result.html")
                print("  ambulon md2html-diagrams document.md -p landscape --plantuml-method jar")
                print()
                print("Note:")
                print("  Si vous avez des problèmes de connexion avec Kroki, utilisez --plantuml-method jar")
                return 0 if len(sys.argv) > 2 and sys.argv[2] in ['-h', '--help'] else 1
            input_file = sys.argv[2]
            output_file = None
            verbose = False
            standalone = True
            page_orientation = None
            plantuml_method = 'kroki'
            plantuml_jar = None
            toc_backlinks = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-p', '--page-orientation'] and i + 1 < len(sys.argv):
                    page_orientation = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                elif sys.argv[i] == '--no-standalone':
                    standalone = False
                    i += 1
                elif sys.argv[i] == '--toc-backlinks':
                    toc_backlinks = True
                    i += 1
                elif sys.argv[i] == '--plantuml-method' and i + 1 < len(sys.argv):
                    plantuml_method = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--plantuml-jar' and i + 1 < len(sys.argv):
                    plantuml_jar = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            return process_markdown_to_html(input_file, output_file, verbose, standalone, plantuml_method, plantuml_jar, page_orientation, toc_backlinks)
        elif command == 'html2pdf':
            # Convertir HTML en PDF
            from app.conversion.commands.html2pdf import convert_html_to_pdf, install_chromium_guide
            if len(sys.argv) < 3 or sys.argv[2] in ['-h', '--help']:
                print("Usage: ambulon html2pdf <input.html> [-o <output.pdf>] [-p <orientation>] [-m <method>] [--wkhtmltopdf-path <path>] [--verbose]")
                print()
                print("Convertit un fichier HTML en PDF")
                print()
                print("Méthodes de rendu disponibles:")
                print("  - chromium    : Chromium via Playwright (meilleure qualité)")
                print("  - wkhtmltopdf : wkhtmltopdf (pas d'installation requise)")
                print("  - auto        : Essaye chromium, sinon wkhtmltopdf (défaut)")
                print()
                print("Arguments:")
                print("  <input.html>                  Fichier HTML source")
                print()
                print("Options:")
                print("  -o, --output <file>           Fichier PDF de sortie (défaut: <input>.pdf)")
                print("  -p, --page-orientation <mode> Orientation de la page:")
                print("                                  portrait  - Format vertical (défaut)")
                print("                                  landscape - Format horizontal")
                print("  -m, --method <method>         Méthode de rendu: auto, chromium, wkhtmltopdf")
                print("  --wkhtmltopdf-path <path>     Chemin vers l'exécutable wkhtmltopdf")
                print("  --verbose                     Mode verbeux (affiche les détails)")
                print("  --install-chromium            Affiche le guide d'installation de Chromium")
                print()
                print("Exemples:")
                print("  ambulon html2pdf document.html")
                print("  ambulon html2pdf document.html -o result.pdf")
                print("  ambulon html2pdf document.html -p landscape -m wkhtmltopdf")
                print("  ambulon html2pdf document.html --method wkhtmltopdf --wkhtmltopdf-path \"C:\\tools\\wkhtmltopdf.exe\"")
                print()
                print("Note:")
                print("  Pour un workflow optimal, utilisez la même orientation dans md2html et html2pdf:")
                print("    ambulon md2html doc.md -p landscape")
                print("    ambulon html2pdf doc.html -p landscape")
                print()
                print("Installation de Chromium (pour un meilleur rendu SVG):")
                print("    poetry run playwright install chromium")
                print("    ou: ambulon html2pdf --install-chromium")
                return 0 if len(sys.argv) > 2 and sys.argv[2] in ['-h', '--help'] else 1
            
            # Check for --install-chromium
            if '--install-chromium' in sys.argv:
                install_chromium_guide()
                return 0
            input_file = sys.argv[2]
            output_file = None
            orientation = 'portrait'
            method = 'auto'
            wkhtmltopdf_path = None
            verbose = False
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
                    output_file = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-p', '--page-orientation', '--orientation'] and i + 1 < len(sys.argv):
                    orientation = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-m', '--method'] and i + 1 < len(sys.argv):
                    method = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--wkhtmltopdf-path' and i + 1 < len(sys.argv):
                    wkhtmltopdf_path = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--verbose':
                    verbose = True
                    i += 1
                else:
                    i += 1
            return convert_html_to_pdf(input_file, output_file, orientation, method, wkhtmltopdf_path, verbose)
        elif command == 'json2jsonl':
            # Convertir JSON en JSONL
            from app.conversion import json_to_jsonl
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
            from app.conversion import process_json_to_markdown
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
        elif command == 'add-toc':
            # Ajouter TOC (détection auto MD/HTML) - bespoke cli wrapper
            from app.toc import add_toc_cli
            return add_toc_cli(sys.argv[2:])
        elif command == 'add-itoc':
            # Ajouter liens retour (iTOC) - détecte automatiquement MD/HTML
            from app.toc import add_itoc_cli
            return add_itoc_cli(sys.argv[2:])
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
        elif command == 'augment':
            # Augmenter HTML avec navigation interactive
            from app.processing.commands.add_augment import augment
            if len(sys.argv) < 3:
                print("Usage: ambulon augment <input.html> [-o <output.html>] [--verbose]")
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
            return augment(input_file, output, verbose)
        elif command == 'md2interactive':
            # Convertir MD en HTML interactif complet (TOC + iTOC + HTML + interactif)
            from app.processing.commands.md_to_interactive_html import main as md_to_interactive_main
            return md_to_interactive_main(sys.argv[2:])
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


if __name__ == "__main__":
    sys.exit(main())
