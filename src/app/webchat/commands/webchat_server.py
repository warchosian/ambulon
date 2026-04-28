#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Commande webchat pour lancer l'interface webchat RAG dans Ambulon.
"""

import sys
import os
from pathlib import Path

# Configurer l'encodage UTF-8 pour la sortie console (Windows)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def run_webchat_server(args):
    """Lancer le serveur web FastAPI pour l'interface RAG.

    Args:
        args: Namespace d'arguments parsés.
    Returns:
        Code de retour (0 = succès).
    """
    try:
        import uvicorn
    except ImportError:
        print("❌ Erreur: uvicorn n'est pas installé")
        print("Installez-le avec: pip install uvicorn[standard]")
        return 1

    # Chemin vers le backend du webchat (dans ce même package)
    backend_path = Path(__file__).parent.parent / "backend"
    if not backend_path.exists():
        print(f"❌ Erreur: Backend introuvable à {backend_path}")
        return 1

    # Ajouter le backend au PYTHONPATH
    sys.path.insert(0, str(backend_path.parent))

    print(f"\n{'='*70}")
    print("🚀 Ambulon WebChat RAG Server")
    print(f"{'='*70}\n")

    # Configuration serveur
    print("📡 Configuration Serveur:")
    print(f"   • Host: {args.host}")
    print(f"   • Port: {args.port}")
    print(f"   • Debug: {'Oui' if args.debug else 'Non'}")
    print(f"   • Reload: {'Oui' if args.reload else 'Non'}")
    print(f"   • Backend: {backend_path}")

    # Configuration RAG
    print("\n🤖 Configuration RAG:")
    collection = args.collection or os.getenv('DYAG_DEFAULT_COLLECTION', 'applications')
    chroma_path = args.chroma_path or os.getenv('DYAG_DEFAULT_CHROMA_PATH', './chroma_db')
    print(f"   • Collection: {collection}")
    print(f"   • ChromaDB: {chroma_path}")

    # Configuration LLM (utilise la configuration Ambulon)
    print("\n💬 Configuration LLM:")
    llm_provider = os.getenv('LLM_PROVIDER', 'ollama')
    llm_model = args.llm_model if args.llm_model else os.getenv('LLM_MODEL', 'llama3.2')
    print(f"   • Provider: {llm_provider}")
    print(f"   • Modèle: {llm_model}")
    print(f"   • Timeout: {args.timeout}s")

    # Configuration Embedding
    print("\n🔍 Configuration Embedding:")
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    print(f"   • Modèle: {embedding_model}")
    if embedding_model == 'BAAI/bge-m3':
        print(f"   • Dimensions: 1024 ✅")
    elif embedding_model == 'all-MiniLM-L6-v2':
        print(f"   • Dimensions: 384 ⚠️")

    print(f"\n{'='*70}")
    print(f"👉 Interface: http://{args.host}:{args.port}")
    print(f"👉 API docs: http://{args.host}:{args.port}/docs")
    print(f"{'='*70}\n")

    # Exporter les variables d'environnement si renseignées
    if args.collection:
        os.environ['DYAG_DEFAULT_COLLECTION'] = args.collection
    if args.chroma_path:
        os.environ['DYAG_DEFAULT_CHROMA_PATH'] = args.chroma_path
    if args.timeout:
        os.environ['OLLAMA_TIMEOUT'] = str(args.timeout)
    if args.llm_model:
        os.environ['LLM_MODEL'] = args.llm_model

    # Lancer uvicorn
    try:
        uvicorn.run(
            "backend.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="debug" if args.debug else "info",
            access_log=args.debug,
        )
        return 0
    except KeyboardInterrupt:
        print("\n\n✋ Arrêt du serveur...")
        return 0
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage du serveur: {e}")
        return 1


def register_webchat_command(subparsers):
    """Enregistrer la commande webchat pour un parser avec sous‑commandes."""
    parser = subparsers.add_parser(
        "webchat",
        help="Lancer l'interface webchat pour le système RAG",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Adresse IP du serveur (défaut: 127.0.0.1, utilisez 0.0.0.0 pour accès réseau)")
    parser.add_argument("--port", type=int, default=8000, help="Port du serveur (défaut: 8000)")
    parser.add_argument("--debug", action="store_true", help="Mode debug avec logs détaillés")
    parser.add_argument("--reload", action="store_true", help="Recharger automatiquement lors des modifications de code")
    parser.add_argument("--collection", help="Collection ChromaDB par défaut (ex: applications_1008)")
    parser.add_argument("--chroma-path", help="Chemin vers ChromaDB par défaut (ex: ./chroma_db_1008)")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout Ollama en secondes (défaut: 600s = 10 minutes)")
    parser.add_argument("--llm-model", help="Modèle LLM à utiliser (ex: llama3.2:1b, llama3.1:8b, phi3)")
    parser.set_defaults(func=run_webchat_server)
