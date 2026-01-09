
"""Module pour lister les documents d'une collection RAG PIAG."""

import json
import os
import sys
import yaml
import requests
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Charge la configuration depuis le fichier piag_rag.yaml."""
    if config_path is None:
        current_dir = Path(__file__).parent
        config_path = current_dir.parent.parent.parent / "config" / "piag_rag.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

try:
    _DEFAULT_CONFIG = load_config()
    RAG_API_BASE_URL = _DEFAULT_CONFIG['api']['base_url']
except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
    print(f"Avertissement: Impossible de charger la configuration: {e}", file=sys.stderr)
    RAG_API_BASE_URL = "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
    _DEFAULT_CONFIG = None

def list_documents(
    collection_id: str,
    api_token: str,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "name",
    order: str = "asc",
    base_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Liste les documents d'une collection RAG PIAG.

    Args:
        collection_id: L'identifiant de la collection.
        api_token: Le token d'autorisation pour l'API RAG (Bearer token).
        limit: Nombre maximum de résultats à retourner (défaut: 20).
        offset: Nombre de résultats à sauter (pour la pagination, défaut: 0).
        order_by: Champ de tri (défaut: "name").
        order: Ordre de tri "asc" ou "desc" (défaut: "asc").
        base_url: L'URL de base de l'API RAG. Si None, utilise la config.
        config: Dictionnaire de configuration. Si None, utilise la config par défaut.

    Returns:
        La réponse JSON de l'API contenant la liste des documents.

    Raises:
        requests.exceptions.RequestException: En cas d'erreur réseau ou de réponse HTTP non-2xx.
    """
    if config is None:
        config = _DEFAULT_CONFIG or {}

    if base_url is None:
        base_url = config.get('api', {}).get('base_url', RAG_API_BASE_URL)

    timeout = config.get('api', {}).get('timeout', 30)

    headers = {
        "accept": config.get('headers', {}).get('accept', 'application/json'),
        "Authorization": f"Bearer {api_token}"
    }

    endpoint = config.get('endpoints', {}).get('collection_documents', '/api/v1/collections/{collection_id}/documents')
    endpoint = endpoint.replace('{collection_id}', collection_id)

    params = {
        'limit': limit,
        'offset': offset,
        'order_by': order_by,
        'order': order
    }

    url = f"{base_url.rstrip('/')}{endpoint}"

    if config.get('logging', {}).get('log_requests', False):
        print(f"[DEBUG] Requête GET vers: {url}", file=sys.stderr)
        print(f"[DEBUG] Paramètres: {json.dumps(params, indent=2)}", file=sys.stderr)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()

        result = response.json()

        if config.get('logging', {}).get('log_responses', False):
            print(f"[DEBUG] Réponse: {json.dumps(result, indent=2)}", file=sys.stderr)

        return result
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des documents: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse API: {e.response.text}", file=sys.stderr)
        raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Liste les documents d'une collection RAG PIAG.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut"
    )
    parser.add_argument("--collection-id", help="ID de la collection RAG (écrase YAML et env).")
    parser.add_argument("--token", help="Token API RAG Bearer (écrase YAML et env).")
    parser.add_argument("--limit", type=int, help="Nombre maximum de résultats (défaut: 20).")
    parser.add_argument("--offset", type=int, help="Nombre de résultats à sauter (défaut: 0).")
    parser.add_argument("--order-by", help="Champ de tri (défaut: name).")
    parser.add_argument("--order", choices=['asc', 'desc'], help="Ordre de tri: asc ou desc (défaut: asc).")
    parser.add_argument("--base-url", help="URL de base de l'API RAG (écrase YAML).")
    parser.add_argument("--config", help="Chemin vers un fichier de configuration personnalisé.")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug (logging détaillé).")

    args = parser.parse_args()

    config = None
    if args.config:
        try:
            config = load_config(args.config)
            print(f"Configuration chargée depuis: {args.config}")
        except Exception as e:
            print(f"Erreur lors du chargement de la config: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        config = _DEFAULT_CONFIG if _DEFAULT_CONFIG else {}

    if args.debug and config:
        if 'logging' not in config:
            config['logging'] = {}
        config['logging']['enable_debug'] = True
        config['logging']['log_requests'] = True
        config['logging']['log_responses'] = True

    # COLLECTION_ID
    collection_id = args.collection_id
    if not collection_id:
        collection_id = config.get('project', {}).get('collection_id')
    if not collection_id:
        collection_id = os.getenv('PIAG_RAG_COLLECTION_ID')
    if not collection_id:
        print("Erreur: collection_id requis. Utilisez --collection-id, définissez-le dans le YAML, ou via PIAG_RAG_COLLECTION_ID", file=sys.stderr)
        sys.exit(1)

    # TOKEN
    api_token = args.token
    if not api_token:
        api_token = config.get('security', {}).get('token')
    if not api_token:
        token_env_var = config.get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN')
        api_token = os.getenv(token_env_var)
    if not api_token:
        print(f"Erreur: Token API requis. Utilisez --token, définissez-le dans le YAML (non recommandé), ou via {token_env_var}", file=sys.stderr)
        sys.exit(1)

    # LIMIT
    limit = args.limit
    if limit is None:
        limit = config.get('listing', {}).get('default_limit', 20)
    if limit is None:
        limit_env = os.getenv('PIAG_RAG_DOC_LIST_LIMIT')
        limit = int(limit_env) if limit_env else 20

    # OFFSET
    offset = args.offset
    if offset is None:
        offset = config.get('listing', {}).get('default_offset', 0)
    if offset is None:
        offset_env = os.getenv('PIAG_RAG_DOC_LIST_OFFSET')
        offset = int(offset_env) if offset_env else 0

    # ORDER_BY
    order_by = args.order_by
    if not order_by:
        order_by = config.get('listing', {}).get('default_order_by', 'name')
    if not order_by:
        order_by = os.getenv('PIAG_RAG_DOC_LIST_ORDER_BY', 'name')

    # ORDER
    order = args.order
    if not order:
        order = config.get('listing', {}).get('default_order', 'asc')
    if not order:
        order = os.getenv('PIAG_RAG_DOC_LIST_ORDER', 'asc')

    base_url = args.base_url

    try:
        result = list_documents(
            collection_id=collection_id,
            api_token=api_token,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order=order,
            base_url=base_url,
            config=config
        )

        print("✅ Documents de la collection récupérés avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if isinstance(result, dict) and 'items' in result:
            print(f"\n📊 Résumé: {len(result.get('items', []))} document(s) retourné(s)")
        elif isinstance(result, list):
            print(f"\n📊 Résumé: {len(result)} document(s) retourné(s)")

    except requests.exceptions.RequestException:
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)
