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
    parser = argparse.ArgumentParser(description="Effectue une recherche RAG dans une ou plusieurs collections PIAG.")
    parser.add_argument("--collection", help="UNE collection (nom ou ID, résolution automatique).")
    parser.add_argument("--collection-id", help="UNE collection (ID exact, pas de résolution).")
    parser.add_argument("--collections", help="PLUSIEURS collections séparées par virgule (noms ou IDs, résolution automatique).")
    parser.add_argument("--collections-id", help="PLUSIEURS collections séparées par virgule (IDs exacts, pas de résolution).")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--query", "-q", help="Question/requête de recherche.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--top-k", type=int, help="Nombre de résultats à retourner (défaut: 10).")
    parser.add_argument("--rerank", action="store_true", default=True, help="Activer le reranking (défaut: activé).")
    parser.add_argument("--no-rerank", action="store_false", dest="rerank", help="Désactiver le reranking.")
    parser.add_argument("--k-rerank", type=int, help="Nombre de résultats pour le reranking (défaut: 20).")
    parser.add_argument("--mode", choices=['hybrid', 'semantic', 'keyword'], help="Mode de recherche (défaut: hybrid).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    parser.add_argument("--format", choices=['json', 'text'], default='text', help="Format de sortie: json ou text (défaut: text).")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    if args.debug:
        config.setdefault('logging', {}).update({'enable_debug': True, 'log_requests': True, 'log_responses': True})

    # Hiérarchie de configuration
    query = args.query or config.get('search', {}).get('query') or os.getenv('PIAG_RAG_SEARCH_QUERY')
    api_token = args.token or config.get('security', {}).get('token') or os.getenv('PIAG_RAG_API_TOKEN')
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    base_url = args.base_url or config.get('api', {}).get('base_url') or os.getenv('PIAG_RAG_BASE_URL')
    top_k = args.top_k or config.get('search', {}).get('top_k') or os.getenv('PIAG_RAG_TOP_K') or 10
    top_k = int(top_k)
    k_rerank = args.k_rerank or config.get('search', {}).get('k_rerank') or 20
    k_rerank = int(k_rerank)
    mode = args.mode or config.get('search', {}).get('mode') or 'hybrid'

    # Gestion des collections (4 sources possibles)
    collection_single = args.collection or os.getenv('PIAG_RAG_COLLECTION') or config.get('project', {}).get('collection')
    collection_id_single = args.collection_id or os.getenv('PIAG_RAG_COLLECTION_ID') or config.get('project', {}).get('collection_id')
    collections_multi = args.collections or os.getenv('PIAG_RAG_COLLECTIONS')
    collections_id_multi = args.collections_id or os.getenv('PIAG_RAG_COLLECTIONS_ID')

    # Validation: au moins une collection fournie
    if not any([collection_single, collection_id_single, collections_multi, collections_id_multi]):
        print("❌ Erreur: Au moins une collection est requise", file=sys.stderr)
        print("   Vous pouvez la fournir via:", file=sys.stderr)
        print("   • --collection <name> (1 collection, résolution auto)", file=sys.stderr)
        print("   • --collection-id <id> (1 collection, ID exact)", file=sys.stderr)
        print("   • --collections <name1,name2> (plusieurs, résolution auto)", file=sys.stderr)
        print("   • --collections-id <id1,id2> (plusieurs, IDs exacts)", file=sys.stderr)
        print("   • Variable d'env: PIAG_RAG_COLLECTION, PIAG_RAG_COLLECTION_ID,", file=sys.stderr)
        print("                     PIAG_RAG_COLLECTIONS, PIAG_RAG_COLLECTIONS_ID", file=sys.stderr)
        print("   • Fichier de config: config/piag.yaml", file=sys.stderr)
        print("\n💡 Pour créer un fichier de configuration:", file=sys.stderr)
        print("   ambulon init piag", file=sys.stderr)
        return 1
    if not query:
        print("❌ Erreur: La requête de recherche est requise", file=sys.stderr)
        print("   Utilisez: --query \"Votre question ici\"", file=sys.stderr)
        return 1
    if not api_token:
        print("❌ Erreur: Token API requis", file=sys.stderr)
        print("   Vous pouvez le fournir via:", file=sys.stderr)
        print("   • --token <votre_token>", file=sys.stderr)
        print("   • Variable d'env: PIAG_RAG_API_TOKEN", file=sys.stderr)
        print("   • Fichier de config: config/piag.yaml (section security.token)", file=sys.stderr)
        print("\n💡 Pour créer un fichier de configuration:", file=sys.stderr)
        print("   ambulon init piag", file=sys.stderr)
        return 1
    if not project_id:
        print("❌ Erreur: Project ID requis", file=sys.stderr)
        print("   Vous pouvez le fournir via:", file=sys.stderr)
        print("   • --project-id <votre_id>", file=sys.stderr)
        print("   • Variable d'env: PIAG_RAG_PROJECT_ID", file=sys.stderr)
        print("   • Fichier de config: config/piag.yaml (section project.project_id)", file=sys.stderr)
        print("\n💡 Pour créer un fichier de configuration:", file=sys.stderr)
        print("   ambulon init piag", file=sys.stderr)
        return 1

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)

        # Résoudre les collections en liste d'IDs
        resolved_collection_ids = []

        if collections_id_multi:
            # Plusieurs collections par IDs (pas de résolution)
            resolved_collection_ids = [c.strip() for c in collections_id_multi.split(',')]
            if args.debug:
                print(f"[DEBUG] Utilisation de plusieurs collections (IDs exacts): {resolved_collection_ids}", file=sys.stderr)

        elif collections_multi:
            # Plusieurs collections par noms/IDs (avec résolution)
            collection_names = [c.strip() for c in collections_multi.split(',')]
            if args.debug:
                print(f"[DEBUG] Résolution de plusieurs collections: {collection_names}", file=sys.stderr)
            for cname in collection_names:
                resolved_id = client.resolve_collection_id(cname, project_id)
                resolved_collection_ids.append(resolved_id)
                if args.debug:
                    print(f"[DEBUG]   '{cname}' → {resolved_id}", file=sys.stderr)

        elif collection_id_single:
            # Une seule collection par ID (pas de résolution)
            resolved_collection_ids = [collection_id_single]
            if args.debug:
                print(f"[DEBUG] Utilisation d'une collection (ID exact): {collection_id_single}", file=sys.stderr)

        elif collection_single:
            # Une seule collection par nom/ID (avec résolution)
            if args.debug:
                print(f"[DEBUG] Résolution d'une collection: {collection_single}", file=sys.stderr)
            resolved_id = client.resolve_collection_id(collection_single, project_id)
            resolved_collection_ids = [resolved_id]
            if args.debug:
                print(f"[DEBUG]   '{collection_single}' → {resolved_id}", file=sys.stderr)

        # Appel à l'API de recherche
        result = client.search(
            collections=resolved_collection_ids,
            query=query,
            project_id=project_id,
            top_k=top_k,
            rerank=args.rerank,
            k_rerank=k_rerank,
            mode=mode
        )

        if args.format == 'json':
            print("Résultats de la recherche RAG :")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Format texte plus lisible
            print("Résultats de la recherche RAG :")
            print(f"\nQuestion: {query}")
            print(f"Collection(s): {', '.join(resolved_collection_ids)} ({len(resolved_collection_ids)} collection(s))")
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
