"""Module CLI pour récupérer les chunks d'un document RAG PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(description="Récupère les chunks d'un document RAG PIAG.")
    parser.add_argument("--collection-name", help="Nom de la collection RAG (résolution automatique vers ID).")
    parser.add_argument("--collection-id", help="ID exact de la collection RAG (pas de résolution, plus rapide).")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--document-name", help="Nom de fichier du document (résolution automatique vers ID).")
    parser.add_argument("--document-id", help="ID exact du document (pas de résolution, plus rapide).")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    # Hiérarchie de configuration - COLLECTION
    collection_name_or_id = args.collection_name or os.getenv('PIAG_RAG_COLLECTION_NAME') or config.get('project', {}).get('collection_name')
    collection_id = args.collection_id or os.getenv('PIAG_RAG_COLLECTION_ID') or config.get('project', {}).get('collection_id')

    # Hiérarchie de configuration - DOCUMENT
    document_name_or_id = args.document_name or os.getenv('PIAG_RAG_DOCUMENT_NAME')
    document_id = args.document_id or os.getenv('PIAG_RAG_DOCUMENT_ID')

    # Hiérarchie de configuration - AUTRES
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    base_url = args.base_url or config.get('api', {}).get('base_url') or os.getenv('PIAG_RAG_BASE_URL')

    if not collection_name_or_id and not collection_id:
        print("Erreur: La collection est requise (--collection-name, --collection-id, config, ou PIAG_RAG_COLLECTION_NAME/PIAG_RAG_COLLECTION_ID)", file=sys.stderr)
        return 1
    if not document_name_or_id and not document_id:
        print("Erreur: Le document est requis (--document-name, --document-id, ou PIAG_RAG_DOCUMENT_NAME/PIAG_RAG_DOCUMENT_ID)", file=sys.stderr)
        return 1
    if not api_token:
        print("Erreur: Token API requis (--token, config, ou PIAG_RAG_API_TOKEN)", file=sys.stderr)
        return 1
    if not project_id:
        print("Erreur: Project ID requis (--project-id, config, ou PIAG_RAG_PROJECT_ID)", file=sys.stderr)
        return 1

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Résolution COLLECTION
        if collection_id:
            resolved_collection_id = collection_id
        else:
            resolved_collection_id = client.resolve_collection_id(collection_name_or_id, project_id)

        # Résolution DOCUMENT
        if document_id:
            resolved_document_id = document_id
        else:
            resolved_document_id = client.resolve_document_id(document_name_or_id, resolved_collection_id)

        result = client.get_document_chunks(resolved_collection_id, resolved_document_id)
        print("Chunks du document récupérés avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, Exception) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
