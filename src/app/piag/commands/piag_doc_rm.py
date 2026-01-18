"""Module CLI pour supprimer un document d'une collection RAG PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(description="Supprime un document d'une collection RAG PIAG.")
    parser.add_argument("--collection", help="Nom ou ID de la collection RAG (résolution automatique).")
    parser.add_argument("--collection-id", help="ID exact de la collection RAG (pas de résolution).")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--document", help="Nom de fichier ou ID du document (résolution automatique).")
    parser.add_argument("--document-id", help="ID exact du document (pas de résolution).")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    parser.add_argument("--force", action="store_true", help="Supprime sans confirmation.")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    # Hiérarchie de configuration
    collection_name_or_id = args.collection or args.collection_id or config.get('project', {}).get('collection_id') or os.getenv('PIAG_RAG_COLLECTION_ID')
    document_name_or_id = args.document or args.document_id or os.getenv('PIAG_RAG_DOCUMENT_ID')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    base_url = args.base_url or config.get('api', {}).get('base_url') or os.getenv('PIAG_RAG_BASE_URL')

    if not collection_name_or_id:
        print("Erreur: La collection est requise (--collection, --collection-id, config, ou PIAG_RAG_COLLECTION_ID)", file=sys.stderr)
        return 1
    if not document_name_or_id:
        print("Erreur: Le document est requis (--document, --document-id, ou PIAG_RAG_DOCUMENT_ID)", file=sys.stderr)
        return 1
    if not api_token:
        print("Erreur: Token API requis (--token, config, ou PIAG_RAG_API_TOKEN)", file=sys.stderr)
        return 1
    if not project_id:
        print("Erreur: Project ID requis (--project-id, config, ou PIAG_RAG_PROJECT_ID)", file=sys.stderr)
        return 1

    if not args.force:
        confirm = input(f"Voulez-vous vraiment supprimer le document {document_name_or_id} ? (oui/non): ")
        if confirm.lower() != 'oui':
            print("Suppression annulée")
            return 0

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Résoudre collection : si --collection-id fourni, utiliser directement, sinon résoudre
        if args.collection_id:
            resolved_collection_id = args.collection_id
        else:
            resolved_collection_id = client.resolve_collection_id(collection_name_or_id, project_id)

        # Résoudre document : si --document-id fourni, utiliser directement, sinon résoudre
        if args.document_id:
            resolved_document_id = args.document_id
        else:
            resolved_document_id = client.resolve_document_id(document_name_or_id, resolved_collection_id)

        result = client.delete_document(resolved_collection_id, resolved_document_id)
        print("Document supprimé avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, Exception) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
