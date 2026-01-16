"""Module CLI pour lister les collections RAG PIAG."""

import os
import sys
import json
import argparse
from app.piag.core import PIAGClient, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Liste les collections RAG PIAG d'un projet.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut"
    )
    parser.add_argument("--project-id", help="ID du projet RAG (écrase YAML et env).")
    parser.add_argument("--token", help="Token API RAG Bearer (écrase YAML et env).")
    parser.add_argument("--limit", type=int, help="Nombre maximum de résultats (défaut: 20).")
    parser.add_argument("--offset", type=int, help="Nombre de résultats à sauter (défaut: 0).")
    parser.add_argument("--order-by", help="Champ de tri (défaut: name).")
    parser.add_argument("--order", choices=['asc', 'desc'], help="Ordre de tri: asc ou desc (défaut: asc).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG (écrase YAML).")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug (logging détaillé).")

    args = parser.parse_args(argv)

    # Charger la configuration
    config = None
    if args.config:
        try:
            config = load_config(args.config)
            print(f"Configuration chargée depuis: {args.config}")
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}", file=sys.stderr)
            return 1
    else:
        try:
            config = load_config()
        except Exception:
            config = {}

    if args.debug and config:
        if 'logging' not in config:
            config['logging'] = {}
        config['logging']['enable_debug'] = True
        config['logging']['log_requests'] = True
        config['logging']['log_responses'] = True

    # Résolution des paramètres (CLI > YAML > ENV)
    project_id = args.project_id or config.get('project', {}).get('project_id') or os.getenv('PIAG_RAG_PROJECT_ID')
    if not project_id:
        print("Erreur: project_id requis", file=sys.stderr)
        return 1

    api_token = args.token or config.get('security', {}).get('token') or os.getenv(config.get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN'))
    if not api_token:
        print("Erreur: Token API requis", file=sys.stderr)
        return 1

    limit = args.limit or config.get('listing', {}).get('default_limit', 20)
    offset = args.offset or config.get('listing', {}).get('default_offset', 0)
    order_by = args.order_by or config.get('listing', {}).get('default_order_by', 'name')
    order = args.order or config.get('listing', {}).get('default_order', 'asc')
    base_url = args.base_url

    try:
        client = PIAGClient(api_token=api_token, base_url=base_url, config=config)
        result = client.list_collections(project_id=project_id, limit=limit, offset=offset, order_by=order_by, order=order)

        print("Collections RAG récupérées avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if isinstance(result, dict) and 'items' in result:
            print(f"\nRésumé: {len(result.get('items', []))} collection(s)")
        elif isinstance(result, list):
            print(f"\nRésumé: {len(result)} collection(s)")

        return 0
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
