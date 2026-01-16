"""Module CLI pour téléverser un document vers une collection RAG PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    """
    Point d'entrée principal pour la commande piag-doc-upload.

    Args:
        argv: Arguments CLI (list of str), ou None pour utiliser sys.argv

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
    """
    parser = argparse.ArgumentParser(description="Téléverse un document vers une collection RAG PIAG.")
    parser.add_argument("--collection", help="Nom ou ID de la collection RAG.")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--file", help="Chemin vers le fichier à téléverser (requis).")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    args = parser.parse_args(argv)

    config = load_config(args.config) if args.config else (load_config() if os.path.exists("config/piag.yaml") else {})

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    # Hiérarchie de configuration
    collection_name_or_id = args.collection or config.get('upload', {}).get('collection_id') or os.getenv('PIAG_RAG_COLLECTION_ID')
    file_path = args.file or config.get('upload', {}).get('file_path') or os.getenv('PIAG_RAG_UPLOAD_FILE')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    base_url = args.base_url or config.get('api', {}).get('base_url') or os.getenv('PIAG_RAG_BASE_URL')

    if not collection_name_or_id or not file_path or not api_token:
        print("Erreur: collection, fichier et token requis", file=sys.stderr)
        return 1

    if not project_id:
        print("Erreur: Project ID requis (--project-id, config, ou PIAG_RAG_PROJECT_ID)", file=sys.stderr)
        return 1

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Résoudre le nom ou l'ID de la collection en ID
        resolved_collection_id = client.resolve_collection_id(collection_name_or_id, project_id)

        result = client.upload_document(resolved_collection_id, file_path)
        print("Document téléversé avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except FileNotFoundError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    except (ValueError, Exception) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
