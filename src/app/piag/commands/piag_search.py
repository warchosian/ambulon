"""Module CLI pour effectuer une recherche RAG dans une collection PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Effectue une recherche RAG dans une collection PIAG.")
    parser.add_argument("--collection-id", help="ID de la collection RAG à interroger.")
    parser.add_argument("--query", "-q", help="Question/requête de recherche.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--top-k", type=int, default=5, help="Nombre de résultats à retourner (défaut: 5).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    parser.add_argument("--format", choices=['json', 'text'], default='json', help="Format de sortie: json ou text (défaut: json).")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else (load_config() if os.path.exists("config/piag.yml") else {})

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    collection_id = args.collection_id or config.get('search', {}).get('collection_id') or os.getenv('PIAG_RAG_COLLECTION_ID')
    query = args.query or config.get('search', {}).get('query') or os.getenv('PIAG_RAG_SEARCH_QUERY')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')

    if not collection_id or not query or not api_token:
        print("Erreur: collection_id, query et token requis", file=sys.stderr)
        sys.exit(1)

    try:
        client = PIAGClient(api_token=api_token, base_url=args.base_url, config=config)
        result = client.search(collection_id, query, top_k=args.top_k)

        if args.format == 'json':
            print("Résultats de la recherche RAG :")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Format texte plus lisible
            print("Résultats de la recherche RAG :")
            print(f"\nQuestion: {query}")
            print(f"Collection: {collection_id}")
            print(f"Top {args.top_k} résultats:\n")

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
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)
