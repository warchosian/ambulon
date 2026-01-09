"""Module CLI pour récupérer les informations d'un document RAG PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Récupère les informations d'un document RAG PIAG.")
    parser.add_argument("--collection-id", help="ID de la collection RAG.")
    parser.add_argument("--document-id", help="ID du document.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else (load_config() if os.path.exists("config/piag.yml") else {})

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    collection_id = args.collection_id or config.get('project', {}).get('collection_id') or os.getenv('PIAG_RAG_COLLECTION_ID')
    document_id = args.document_id or os.getenv('PIAG_RAG_DOCUMENT_ID')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')

    if not collection_id or not document_id or not api_token:
        print("Erreur: collection_id, document_id et token requis", file=sys.stderr)
        sys.exit(1)

    try:
        client = PIAGClient(api_token=api_token, base_url=args.base_url, config=config)
        result = client.get_document(collection_id, document_id)
        print("Informations du document récupérées avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
