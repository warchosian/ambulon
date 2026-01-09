"""Module de configuration centralisé pour l'API RAG PIAG.

Ce module gère le chargement de la configuration depuis le fichier piag_rag.yaml
et fournit des valeurs par défaut pour tous les modules PIAG.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Charge la configuration depuis le fichier piag.yml.

    Args:
        config_path: Chemin personnalisé vers le fichier de configuration.
                     Si None, utilise config/piag.yml à la racine du projet.

    Returns:
        Dictionnaire contenant la configuration.

    Raises:
        FileNotFoundError: Si le fichier de configuration n'est pas trouvé.
        yaml.YAMLError: Si le fichier YAML est mal formé.
    """
    if config_path is None:
        # Trouver le répertoire racine du projet (où se trouve config/)
        current_dir = Path(__file__).parent
        config_path = current_dir.parent.parent.parent.parent / "config" / "piag.yml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


# Charger la configuration par défaut au niveau du module
try:
    DEFAULT_CONFIG = load_config()
    DEFAULT_BASE_URL = DEFAULT_CONFIG['api']['base_url']
except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
    print(f"Avertissement: Impossible de charger la configuration: {e}", file=sys.stderr)
    # Fallback sur l'URL en dur
    DEFAULT_BASE_URL = "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
    DEFAULT_CONFIG = None


def get_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retourne la configuration à utiliser.

    Args:
        config: Configuration personnalisée. Si None, utilise la config par défaut.

    Returns:
        Dictionnaire de configuration.
    """
    if config is None:
        return DEFAULT_CONFIG or {}
    return config


def get_base_url(base_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Retourne l'URL de base de l'API à utiliser.

    Args:
        base_url: URL explicite. Si fournie, prioritaire sur la config.
        config: Configuration contenant l'URL. Si None, utilise la config par défaut.

    Returns:
        L'URL de base de l'API.
    """
    if base_url is not None:
        return base_url

    cfg = get_config(config)
    return cfg.get('api', {}).get('base_url', DEFAULT_BASE_URL)


def get_timeout(config: Optional[Dict[str, Any]] = None) -> int:
    """
    Retourne le timeout HTTP à utiliser.

    Args:
        config: Configuration contenant le timeout. Si None, utilise la config par défaut.

    Returns:
        Timeout en secondes.
    """
    cfg = get_config(config)
    return cfg.get('api', {}).get('timeout', 30)


def should_log_requests(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Détermine si les requêtes doivent être loggées.

    Args:
        config: Configuration. Si None, utilise la config par défaut.

    Returns:
        True si le logging des requêtes est activé.
    """
    cfg = get_config(config)
    return cfg.get('logging', {}).get('log_requests', False)


def should_log_responses(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Détermine si les réponses doivent être loggées.

    Args:
        config: Configuration. Si None, utilise la config par défaut.

    Returns:
        True si le logging des réponses est activé.
    """
    cfg = get_config(config)
    return cfg.get('logging', {}).get('log_responses', False)


def get_endpoint(endpoint_key: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Retourne l'endpoint API pour une opération donnée.

    Args:
        endpoint_key: Clé de l'endpoint dans la configuration.
        config: Configuration. Si None, utilise la config par défaut.

    Returns:
        Chemin de l'endpoint.
    """
    cfg = get_config(config)
    endpoints = cfg.get('endpoints', {})

    # Mapping des endpoints par défaut
    default_endpoints = {
        'collections': '/api/v1/collections',
        'collection_detail': '/api/v1/collections/{collection_id}',
        'documents_upload': '/api/v1/collections/{collection_id}/documents-upload-slow',
        'documents': '/api/v1/collections/{collection_id}/documents',
        'document_detail': '/api/v1/collections/{collection_id}/documents/{document_id}',
        'document_chunks': '/api/v1/collections/{collection_id}/documents/{document_id}/chunks',
        'search': '/api/v1/search',
    }

    return endpoints.get(endpoint_key, default_endpoints.get(endpoint_key, ''))


def get_headers(api_token: str, config: Optional[Dict[str, Any]] = None,
                include_content_type: bool = False) -> Dict[str, str]:
    """
    Construit les headers HTTP pour les requêtes API.

    Args:
        api_token: Token d'authentification Bearer.
        config: Configuration. Si None, utilise la config par défaut.
        include_content_type: Si True, ajoute le header Content-Type: application/json.

    Returns:
        Dictionnaire des headers HTTP.
    """
    cfg = get_config(config)

    headers = {
        "accept": cfg.get('headers', {}).get('accept', 'application/json'),
        "Authorization": f"Bearer {api_token}"
    }

    if include_content_type:
        headers["Content-Type"] = cfg.get('headers', {}).get('content_type', 'application/json')

    return headers
