"""Module CLI pour effectuer une recherche RAG dans une collection PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    """
    Point d'entrée principal pour la commande piag-search.

    Args:
        argv: Arguments CLI (list of str), ou None pour utiliser sys.argv

    Returns:
        int: Code de sortie (0 = succès, 1 = erreur)
    """
    parser = argparse.ArgumentParser(description="Effectue une recherche RAG dans une collection PIAG.")
    parser.add_argument("--collection", help="Nom ou ID de la collection RAG à interroger.")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--query", "-q", help="Question/requête de recherche.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--top-k", type=int, help="Nombre de résultats à retourner (défaut: 5).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    parser.add_argument("--format", choices=['json', 'text'], default='json', help="Format de sortie: json ou text (défaut: json).")
    args = parser.parse_args(argv)

    config = load_config(args.config) if args.config else (load_config() if os.path.exists("config/piag.yaml") else {})

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    # Hiérarchie de configuration
    collection_name_or_id = args.collection or config.get('project', {}).get('collection_id') or os.getenv('PIAG_RAG_COLLECTION_ID')
    query = args.query or config.get('search', {}).get('query') or os.getenv('PIAG_RAG_SEARCH_QUERY')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    base_url = args.base_url or config.get('api', {}).get('base_url') or os.getenv('PIAG_RAG_BASE_URL')
    top_k = args.top_k or config.get('search', {}).get('top_k') or os.getenv('PIAG_RAG_TOP_K') or 5
    top_k = int(top_k)

    # Validations
    if not collection_name_or_id:
        print("Erreur: Le nom ou l'ID de la collection est requis (--collection, config, ou PIAG_RAG_COLLECTION_ID)", file=sys.stderr)
        return 1
    if not query:
        print("Erreur: La requête de recherche est requise (--query, config, ou PIAG_RAG_SEARCH_QUERY)", file=sys.stderr)
        return 1
    if not api_token:
        print("Erreur: Token API requis (--token, config, ou PIAG_RAG_API_TOKEN)", file=sys.stderr)
        return 1
    if not project_id:
        print("Erreur: Project ID requis (--project-id, config, ou PIAG_RAG_PROJECT_ID)", file=sys.stderr)
        return 1

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)
        
        # Résoudre le nom ou l'ID de la collection en ID
        resolved_collection_id = client.resolve_collection_id(collection_name_or_id, project_id)

        result = client.search(resolved_collection_id, query, top_k=top_k)

        if args.format == 'json':
            print("Résultats de la recherche RAG :")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Format texte plus lisible
            print("Résultats de la recherche RAG :")
            print(f"\nQuestion: {query}")
            print(f"Collection: {collection_name_or_id} (ID: {resolved_collection_id})")
            print(f"Top {top_k} résultats:\n")

            if isinstance(result, dict) and 'chunks' in result:
                for i, chunk in enumerate(result.get('chunks', []), 1):
                    score = chunk.get('score', 'N/A')
                    text = chunk.get('text', chunk.get('content', 'N/A'))
                    doc_id = chunk.get('document_id', 'N/A')

                    print(f"--- Résultat {i} (score: {score}) ---")
                    print(f"Document ID: {doc_id}")
                    print(f"Contenu: {text[:200]}{'...' if len(text) > 200 else ''}")
                    print()
            elif isinstance(result, list):
                for i, chunk in enumerate(result, 1):
                    print(f"--- Résultat {i} ---")
                    print(json.dumps(chunk, indent=2, ensure_ascii=False))
                    print()

            print(f"\nTotal: {len(result.get('chunks', result)) if isinstance(result, dict) else len(result)} résultat(s)")
        return 0
    except (ValueError, Exception) as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
