"""Module CLI pour téléverser un document vers une collection RAG PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Téléverse un document vers une collection RAG PIAG.")
    parser.add_argument("--collection-id", help="ID de la collection RAG.")
    parser.add_argument("--file", help="Chemin vers le fichier à téléverser (requis).")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else (load_config() if os.path.exists("config/piag.yml") else {})

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    collection_id = args.collection_id or config.get('upload', {}).get('collection_id') or os.getenv('PIAG_RAG_COLLECTION_ID')
    file_path = args.file or config.get('upload', {}).get('file_path') or os.getenv('PIAG_RAG_UPLOAD_FILE')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')

    if not collection_id or not file_path or not api_token:
        print("Erreur: collection_id, fichier et token requis", file=sys.stderr)
        sys.exit(1)

    try:
        client = PIAGClient(api_token=api_token, base_url=args.base_url, config=config)
        result = client.upload_document(collection_id, file_path)
        print("Document téléversé avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except FileNotFoundError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
