
"""Module pour récupérer les chunks d'un document RAG PIAG."""

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

def get_document_chunks(
    document_id: str,
    api_token: str,
    from_index: int = 0,
    to_index: int = 10,
    base_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Récupère les chunks (segments) d'un document RAG PIAG.

    Args:
        document_id: L'identifiant du document.
        api_token: Le token d'autorisation pour l'API RAG (Bearer token).
        from_index: Index de départ (défaut: 0).
        to_index: Index de fin (défaut: 10).
        base_url: L'URL de base de l'API RAG. Si None, utilise la config.
        config: Dictionnaire de configuration. Si None, utilise la config par défaut.

    Returns:
        La réponse JSON de l'API contenant les chunks du document.

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

    endpoint = config.get('endpoints', {}).get('document_chunks', '/api/v1/documents/{document_id}/chunks')
    endpoint = endpoint.replace('{document_id}', document_id)

    params = {
        'from_index': from_index,
        'to_index': to_index
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
        print(f"Erreur lors de la récupération des chunks: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse API: {e.response.text}", file=sys.stderr)
        raise

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Récupère les chunks d'un document RAG PIAG.",
        epilog="HIÉRARCHIE DE PRIORITÉ: Arguments CLI > Fichier YAML > Variables d'environnement > Valeurs par défaut"
    )
    parser.add_argument("--document-id", help="ID du document RAG (écrase YAML et env).")
    parser.add_argument("--token", help="Token API RAG Bearer (écrase YAML et env).")
    parser.add_argument("--from-index", type=int, help="Index de départ (défaut: 0).")
    parser.add_argument("--to-index", type=int, help="Index de fin (défaut: 10).")
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

    # DOCUMENT_ID
    document_id = args.document_id
    if not document_id:
        document_id = config.get('document', {}).get('document_id')
    if not document_id:
        document_id = os.getenv('PIAG_RAG_DOCUMENT_ID')
    if not document_id:
        print("Erreur: document_id requis. Utilisez --document-id, définissez-le dans le YAML, ou via PIAG_RAG_DOCUMENT_ID", file=sys.stderr)
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

    # FROM_INDEX
    from_index = args.from_index
    if from_index is None:
        from_index = config.get('chunks', {}).get('default_from_index', 0)
    if from_index is None:
        from_env = os.getenv('PIAG_RAG_CHUNKS_FROM_INDEX')
        from_index = int(from_env) if from_env else 0

    # TO_INDEX
    to_index = args.to_index
    if to_index is None:
        to_index = config.get('chunks', {}).get('default_to_index', 10)
    if to_index is None:
        to_env = os.getenv('PIAG_RAG_CHUNKS_TO_INDEX')
        to_index = int(to_env) if to_env else 10

    base_url = args.base_url

    try:
        result = get_document_chunks(
            document_id=document_id,
            api_token=api_token,
            from_index=from_index,
            to_index=to_index,
            base_url=base_url,
            config=config
        )

        print("✅ Chunks du document récupérés avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if isinstance(result, dict) and 'chunks' in result:
            print(f"\n📊 Résumé: {len(result.get('chunks', []))} chunk(s) retourné(s)")
        elif isinstance(result, list):
            print(f"\n📊 Résumé: {len(result)} chunk(s) retourné(s)")

    except requests.exceptions.RequestException:
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)
