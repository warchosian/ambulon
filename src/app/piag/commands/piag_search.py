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
    parser = argparse.ArgumentParser(
        prog='ambulon piag-search',
        description="Effectue une recherche RAG dans une ou plusieurs collections PIAG."
    )
    parser.add_argument("--collection-name", help="UNE collection par nom (résolution automatique vers ID).")
    parser.add_argument("--collection-id", help="UNE collection par ID exact (pas de résolution, plus rapide).")
    parser.add_argument("--collection-name-list", help="LISTE de collections par noms séparés par virgule (résolution automatique).")
    parser.add_argument("--collection-id-list", help="LISTE de collections par IDs séparés par virgule (pas de résolution).")
    parser.add_argument("--project-id", help="ID du projet RAG.")
    parser.add_argument("--query", "-q", help="Question/requête de recherche.")
    parser.add_argument("--token", help="Token API RAG Bearer.")
    parser.add_argument("--top-k", type=int, help="Nombre de résultats à retourner (défaut: 10).")
    parser.add_argument("--rerank", action="store_true", default=True, help="Activer le reranking (défaut: activé).")
    parser.add_argument("--no-rerank", action="store_false", dest="rerank", help="Désactiver le reranking.")
    parser.add_argument("--k-rerank", type=int, help="Nombre de résultats pour le reranking (défaut: 20).")
    parser.add_argument("--mode", choices=['hybrid', 'semantic', 'keyword'], help="Mode de recherche (défaut: hybrid).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG.")
    parser.add_argument("--timeout", type=int, help="Timeout HTTP en secondes (défaut: 120).")
    parser.add_argument("--max-retries", type=int, help="Nombre maximum de tentatives en cas d'échec (défaut: 3).")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug.")
    parser.add_argument("--format", choices=['json', 'text'], default='text', help="Format de sortie: json ou text (défaut: text).")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    # Affichage visible de la config si --debug (le log INFO n'est pas toujours visible)
    if args.debug and config:
        from pathlib import Path
        env_home = os.getenv("AMBULON_HOME")
        base_dir = Path(env_home).expanduser() if env_home else Path.cwd()
        config_source = f"$AMBULON_HOME/config/piag.yaml" if env_home else "./config/piag.yaml"
        print(f"[DEBUG] Configuration chargée depuis: {config_source} (base={base_dir})", file=sys.stderr)

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

    # Hiérarchie pour timeout et max_retries
    timeout = args.timeout or config.get('api', {}).get('timeout') or os.getenv('PIAG_RAG_TIMEOUT') or 120
    timeout = int(timeout)
    max_retries = args.max_retries or config.get('api', {}).get('max_retries') or os.getenv('PIAG_RAG_MAX_RETRIES') or 3
    max_retries = int(max_retries)

    # Injecter dans la config pour le client
    config.setdefault('api', {})
    config['api']['timeout'] = timeout
    config['api']['max_retries'] = max_retries

    # Gestion des collections (4 sources possibles)
    collection_name_single = args.collection_name or os.getenv('PIAG_RAG_COLLECTION_NAME') or config.get('project', {}).get('collection_name')
    collection_id_single = args.collection_id or os.getenv('PIAG_RAG_COLLECTION_ID') or config.get('project', {}).get('collection_id')
    collection_name_list_multi = args.collection_name_list or os.getenv('PIAG_RAG_COLLECTION_NAME_LIST') or config.get('project', {}).get('collection_name_list')
    collection_id_list_multi = args.collection_id_list or os.getenv('PIAG_RAG_COLLECTION_ID_LIST') or config.get('project', {}).get('collection_id_list')

    # Validation: au moins une collection fournie
    if not any([collection_name_single, collection_id_single, collection_name_list_multi, collection_id_list_multi]):
        print("❌ Erreur: Au moins une collection est requise", file=sys.stderr)
        print("   Vous pouvez la fournir via:", file=sys.stderr)
        print("   • --collection-name <name> (1 collection par nom, résolution auto)", file=sys.stderr)
        print("   • --collection-id <id> (1 collection par ID, pas de résolution)", file=sys.stderr)
        print("   • --collection-name-list <name1,name2> (liste par noms, résolution auto)", file=sys.stderr)
        print("   • --collection-id-list <id1,id2> (liste par IDs, pas de résolution)", file=sys.stderr)
        print("   • Variables d'env: PIAG_RAG_COLLECTION_NAME, PIAG_RAG_COLLECTION_ID,", file=sys.stderr)
        print("                      PIAG_RAG_COLLECTION_NAME_LIST, PIAG_RAG_COLLECTION_ID_LIST", file=sys.stderr)
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

        if collection_id_list_multi:
            # Liste de collections par IDs (pas de résolution)
            resolved_collection_ids = [c.strip() for c in collection_id_list_multi.split(',')]
            if args.debug:
                print(f"[DEBUG] Utilisation de liste de collections (IDs exacts): {resolved_collection_ids}", file=sys.stderr)

        elif collection_name_list_multi:
            # Liste de collections par noms (avec résolution)
            collection_names = [c.strip() for c in collection_name_list_multi.split(',')]
            if args.debug:
                print(f"[DEBUG] Résolution de liste de collections: {collection_names}", file=sys.stderr)
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

        elif collection_name_single:
            # Une seule collection par nom (avec résolution)
            if args.debug:
                print(f"[DEBUG] Résolution d'une collection: {collection_name_single}", file=sys.stderr)
            resolved_id = client.resolve_collection_id(collection_name_single, project_id)
            resolved_collection_ids = [resolved_id]
            if args.debug:
                print(f"[DEBUG]   '{collection_name_single}' → {resolved_id}", file=sys.stderr)

        # Appel à l'API de recherche
        print(f"\n[INFO] Recherche RAG en cours dans {len(resolved_collection_ids)} collection(s)...", file=sys.stderr)
        print(f"[INFO] (Cela peut prendre jusqu'à 2 minutes selon le volume de données)", file=sys.stderr, flush=True)

        result = client.search(
            collections=resolved_collection_ids,
            query=query,
            project_id=project_id,
            top_k=top_k,
            rerank=args.rerank,
            k_rerank=k_rerank,
            mode=mode
        )

        print(f"[INFO] Recherche terminée.\n", file=sys.stderr)

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
