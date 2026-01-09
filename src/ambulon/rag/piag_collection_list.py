
"""Module pour lister les collections de l'API RAG PIAG."""

import json
import os
import sys
import yaml
import requests
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Charge la configuration depuis le fichier piag_rag.yaml.

    Args:
        config_path: Chemin personnalisé vers le fichier de configuration.
                     Si None, utilise config/piag_rag.yaml à la racine du projet.

    Returns:
        Dictionnaire contenant la configuration.

    Raises:
        FileNotFoundError: Si le fichier de configuration n'est pas trouvé.
        yaml.YAMLError: Si le fichier YAML est mal formé.
    """
    if config_path is None:
        # Trouver le répertoire racine du projet (où se trouve config/)
        current_dir = Path(__file__).parent
        config_path = current_dir.parent.parent.parent / "config" / "piag_rag.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

# Charger la configuration par défaut
try:
    _DEFAULT_CONFIG = load_config()
    RAG_API_BASE_URL = _DEFAULT_CONFIG['api']['base_url']
except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
    print(f"Avertissement: Impossible de charger la configuration: {e}", file=sys.stderr)
    # Fallback sur l'URL en dur
    RAG_API_BASE_URL = "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
    _DEFAULT_CONFIG = None

def list_collections(
    project_id: str,
    api_token: str,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "name",
    order: str = "asc",
    base_url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Liste les collections (corpus) d'un projet RAG spécifié.

    Args:
        project_id: L'identifiant du projet RAG.
        api_token: Le token d'autorisation pour l'API RAG (Bearer token).
        limit: Nombre maximum de résultats à retourner (défaut: 20).
        offset: Nombre de résultats à sauter (pour la pagination, défaut: 0).
        order_by: Champ de tri (défaut: "name").
        order: Ordre de tri "asc" ou "desc" (défaut: "asc").
        base_url: L'URL de base de l'API RAG. Si None, utilise la config.
        config: Dictionnaire de configuration. Si None, utilise la config par défaut.

    Returns:
        La réponse JSON de l'API contenant la liste des collections.

    Raises:
        requests.exceptions.RequestException: En cas d'erreur réseau ou de réponse HTTP non-2xx.
    """
    # Utiliser la configuration fournie ou la configuration par défaut
    if config is None:
        config = _DEFAULT_CONFIG or {}

    # Déterminer l'URL de base
    if base_url is None:
        base_url = config.get('api', {}).get('base_url', RAG_API_BASE_URL)

    # Récupérer le timeout depuis la config
    timeout = config.get('api', {}).get('timeout', 30)

    # Construire les headers depuis la config
    headers = {
        "accept": config.get('headers', {}).get('accept', 'application/json'),
        "Authorization": f"Bearer {api_token}"
    }

    # L'endpoint pour lister les collections
    endpoint = config.get('endpoints', {}).get('collections', '/api/v1/collections')

    # Construire l'URL avec les paramètres de query
    params = {
        'project_id': project_id,
        'limit': limit,
        'offset': offset,
        'order_by': order_by,
        'order': order
    }

    url = f"{base_url.rstrip('/')}{endpoint}"

    # Logger si activé dans la config
    if config.get('logging', {}).get('log_requests', False):
        print(f"[DEBUG] Requête GET vers: {url}", file=sys.stderr)
        print(f"[DEBUG] Paramètres: {json.dumps(params, indent=2)}", file=sys.stderr)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()  # Lève une exception pour les codes d'état HTTP 4xx/5xx

        result = response.json()

        # Logger la réponse si activé
        if config.get('logging', {}).get('log_responses', False):
            print(f"[DEBUG] Réponse: {json.dumps(result, indent=2)}", file=sys.stderr)

        return result
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des collections RAG: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Réponse API: {e.response.text}", file=sys.stderr)
        raise

if __name__ == "__main__":
    # Exemple d'utilisation
    # HIÉRARCHIE: Arguments CLI > YAML > Variables d'environnement > Valeurs par défaut
    #
    # python -m ambulon.rag.piag_collection_list --project-id <id> --token <token>
    # ou avec variable d'environnement:
    # export PIAG_RAG_API_TOKEN=<token>
    # python -m ambulon.rag.piag_collection_list --project-id <id>
    import argparse

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

    args = parser.parse_args()

    # Charger la configuration personnalisée si spécifiée
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

    # Activer le debug si demandé
    if args.debug and config:
        if 'logging' not in config:
            config['logging'] = {}
        config['logging']['enable_debug'] = True
        config['logging']['log_requests'] = True
        config['logging']['log_responses'] = True

    # HIÉRARCHIE: Arguments CLI > YAML > Variables d'environnement > Erreur

    # 1. PROJECT_ID
    project_id = args.project_id  # Argument CLI (priorité 1)
    if not project_id:
        project_id = config.get('project', {}).get('project_id')  # YAML (priorité 2)
    if not project_id:
        project_id = os.getenv('PIAG_RAG_PROJECT_ID')  # Variable d'env (priorité 3)
    if not project_id:
        print("Erreur: project_id requis. Utilisez --project-id, définissez-le dans le YAML, ou via PIAG_RAG_PROJECT_ID", file=sys.stderr)
        sys.exit(1)

    # 2. TOKEN
    api_token = args.token  # Argument CLI (priorité 1)
    if not api_token:
        api_token = config.get('security', {}).get('token')  # YAML (priorité 2) - NON RECOMMANDÉ
    if not api_token:
        # Variable d'env (priorité 3)
        token_env_var = config.get('security', {}).get('token_env_var', 'PIAG_RAG_API_TOKEN')
        api_token = os.getenv(token_env_var)
    if not api_token:
        print(f"Erreur: Token API requis. Utilisez --token, définissez-le dans le YAML (non recommandé), ou via {token_env_var}", file=sys.stderr)
        sys.exit(1)

    # 3. LIMIT (optionnel avec valeur par défaut)
    limit = args.limit  # Argument CLI (priorité 1)
    if limit is None:
        limit = config.get('listing', {}).get('default_limit', 20)  # YAML (priorité 2)
    if limit is None:
        limit_env = os.getenv('PIAG_RAG_LIST_LIMIT')  # Variable d'env (priorité 3)
        limit = int(limit_env) if limit_env else 20

    # 4. OFFSET (optionnel avec valeur par défaut)
    offset = args.offset  # Argument CLI (priorité 1)
    if offset is None:
        offset = config.get('listing', {}).get('default_offset', 0)  # YAML (priorité 2)
    if offset is None:
        offset_env = os.getenv('PIAG_RAG_LIST_OFFSET')  # Variable d'env (priorité 3)
        offset = int(offset_env) if offset_env else 0

    # 5. ORDER_BY (optionnel avec valeur par défaut)
    order_by = args.order_by  # Argument CLI (priorité 1)
    if not order_by:
        order_by = config.get('listing', {}).get('default_order_by', 'name')  # YAML (priorité 2)
    if not order_by:
        order_by = os.getenv('PIAG_RAG_LIST_ORDER_BY', 'name')  # Variable d'env (priorité 3)

    # 6. ORDER (optionnel avec valeur par défaut)
    order = args.order  # Argument CLI (priorité 1)
    if not order:
        order = config.get('listing', {}).get('default_order', 'asc')  # YAML (priorité 2)
    if not order:
        order = os.getenv('PIAG_RAG_LIST_ORDER', 'asc')  # Variable d'env (priorité 3)

    # 7. BASE_URL (optionnel, a des valeurs par défaut)
    base_url = args.base_url  # Argument CLI (priorité 1)
    # Si None, sera géré par list_collections qui utilisera le YAML puis la constante

    try:
        result = list_collections(
            project_id=project_id,
            api_token=api_token,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order=order,
            base_url=base_url,
            config=config
        )

        print("✅ Collections RAG récupérées avec succès :")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Afficher un résumé si la structure le permet
        if isinstance(result, dict) and 'items' in result:
            print(f"\n📊 Résumé: {len(result.get('items', []))} collection(s) retournée(s)")
        elif isinstance(result, list):
            print(f"\n📊 Résumé: {len(result)} collection(s) retournée(s)")

    except requests.exceptions.RequestException:
        sys.exit(1)
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}", file=sys.stderr)
        sys.exit(1)
