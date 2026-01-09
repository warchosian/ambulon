"""Client HTTP pour l'API RAG PIAG.

Ce module fournit une classe PIAGClient qui encapsule toutes les opérations
HTTP vers l'API PIAG avec gestion centralisée de la configuration et des erreurs.
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import mimetypes

from .config import (
    get_config,
    get_base_url,
    get_timeout,
    get_headers,
    get_endpoint,
    should_log_requests,
    should_log_responses
)


class PIAGClient:
    """Client HTTP pour interagir avec l'API RAG PIAG."""

    def __init__(
        self,
        api_token: str,
        base_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise le client PIAG.

        Args:
            api_token: Token d'authentification Bearer.
            base_url: URL de base de l'API. Si None, utilise la config.
            config: Configuration personnalisée. Si None, utilise la config par défaut.
        """
        self.api_token = api_token
        self.config = get_config(config)
        self.base_url = get_base_url(base_url, self.config)
        self.timeout = get_timeout(self.config)

    def _log_request(self, method: str, url: str, **kwargs):
        """Log une requête HTTP si le logging est activé."""
        if should_log_requests(self.config):
            print(f"[DEBUG] Requête {method} vers: {url}", file=sys.stderr)
            if 'data' in kwargs:
                print(f"[DEBUG] Payload: {kwargs['data']}", file=sys.stderr)
            if 'params' in kwargs:
                print(f"[DEBUG] Paramètres: {json.dumps(kwargs['params'], indent=2)}", file=sys.stderr)

    def _log_response(self, response: requests.Response):
        """Log une réponse HTTP si le logging est activé."""
        if should_log_responses(self.config):
            try:
                print(f"[DEBUG] Réponse: {json.dumps(response.json(), indent=2, ensure_ascii=False)}", file=sys.stderr)
            except:
                print(f"[DEBUG] Réponse (non-JSON): {response.text}", file=sys.stderr)

    def _request(
        self,
        method: str,
        endpoint: str,
        include_content_type: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API PIAG.

        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE).
            endpoint: Endpoint relatif (ex: /api/v1/collections).
            include_content_type: Si True, ajoute Content-Type aux headers.
            **kwargs: Arguments supplémentaires pour requests (params, data, files, etc.).

        Returns:
            Réponse JSON de l'API.

        Raises:
            requests.exceptions.RequestException: En cas d'erreur HTTP.
        """
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        headers = get_headers(self.api_token, self.config, include_content_type)

        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        self._log_request(method, url, **kwargs)

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()

            result = response.json()
            self._log_response(response)

            return result

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête {method} {endpoint}: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Réponse API: {e.response.text}", file=sys.stderr)
            raise

    # Collections

    def create_collection(
        self,
        project_id: str,
        name: str,
        description: str
    ) -> Dict[str, Any]:
        """Crée une nouvelle collection RAG."""
        endpoint = f"{get_endpoint('collections', self.config)}?project_id={project_id}"
        payload = {"name": name, "description": description}

        return self._request(
            'POST',
            endpoint,
            include_content_type=True,
            data=json.dumps(payload)
        )

    def list_collections(
        self,
        project_id: str,
        limit: int = 20,
        offset: int = 0,
        order_by: str = "name",
        order: str = "asc"
    ) -> Dict[str, Any]:
        """Liste les collections d'un projet."""
        endpoint = get_endpoint('collections', self.config)
        params = {
            'project_id': project_id,
            'limit': limit,
            'offset': offset,
            'order_by': order_by,
            'order': order
        }

        return self._request('GET', endpoint, params=params)

    def get_collection(self, collection_id: str) -> Dict[str, Any]:
        """Récupère les informations d'une collection."""
        endpoint = get_endpoint('collection_detail', self.config).replace('{collection_id}', collection_id)
        return self._request('GET', endpoint)

    def update_collection(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Met à jour une collection."""
        endpoint = get_endpoint('collection_detail', self.config).replace('{collection_id}', collection_id)
        payload = {}
        if name is not None:
            payload['name'] = name
        if description is not None:
            payload['description'] = description

        return self._request(
            'PUT',
            endpoint,
            include_content_type=True,
            data=json.dumps(payload)
        )

    def delete_collection(self, collection_id: str) -> Dict[str, Any]:
        """Supprime une collection."""
        endpoint = get_endpoint('collection_detail', self.config).replace('{collection_id}', collection_id)
        return self._request('DELETE', endpoint)

    # Documents

    def upload_document(self, collection_id: str, file_path: str) -> Dict[str, Any]:
        """Téléverse un document vers une collection."""
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")

        endpoint = get_endpoint('documents_upload', self.config).replace('{collection_id}', collection_id)

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        with open(file_path, 'rb') as f:
            files = {'file': (file_path_obj.name, f, mime_type)}

            # Pour les uploads de fichiers, on ne passe pas par _request car files est spécial
            url = f"{self.base_url.rstrip('/')}{endpoint}"
            headers = get_headers(self.api_token, self.config, include_content_type=False)

            self._log_request('POST', url, files=files)

            response = requests.post(url, headers=headers, files=files, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            self._log_response(response)

            return result

    def list_documents(
        self,
        collection_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Liste les documents d'une collection."""
        endpoint = get_endpoint('documents', self.config).replace('{collection_id}', collection_id)
        params = {'limit': limit, 'offset': offset}

        return self._request('GET', endpoint, params=params)

    def get_document(self, collection_id: str, document_id: str) -> Dict[str, Any]:
        """Récupère les informations d'un document."""
        endpoint = get_endpoint('document_detail', self.config)
        endpoint = endpoint.replace('{collection_id}', collection_id).replace('{document_id}', document_id)

        return self._request('GET', endpoint)

    def delete_document(self, collection_id: str, document_id: str) -> Dict[str, Any]:
        """Supprime un document."""
        endpoint = get_endpoint('document_detail', self.config)
        endpoint = endpoint.replace('{collection_id}', collection_id).replace('{document_id}', document_id)

        return self._request('DELETE', endpoint)

    def get_document_chunks(self, collection_id: str, document_id: str) -> Dict[str, Any]:
        """Récupère les chunks d'un document."""
        endpoint = get_endpoint('document_chunks', self.config)
        endpoint = endpoint.replace('{collection_id}', collection_id).replace('{document_id}', document_id)

        return self._request('GET', endpoint)

    # Search

    def search(
        self,
        collection_id: str,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Effectue une recherche RAG dans une collection."""
        endpoint = get_endpoint('search', self.config)
        payload = {
            'collection_id': collection_id,
            'query': query,
            'top_k': top_k
        }

        return self._request(
            'POST',
            endpoint,
            include_content_type=True,
            data=json.dumps(payload)
        )
