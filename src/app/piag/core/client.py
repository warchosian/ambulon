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

    def resolve_collection_id(self, collection_name_or_id: str, project_id: str) -> str:
        """
        Résout un nom ou un ID de collection en un ID de collection.

        Args:
            collection_name_or_id: Nom ou ID de la collection.
            project_id: ID du projet auquel la collection appartient.

        Returns:
            L'ID de la collection.

        Raises:
            ValueError: Si la collection n'est pas trouvée.
        """
        if not collection_name_or_id:
            raise ValueError("Le nom ou l'ID de la collection ne peut pas être vide.")

        # Première tentative : l'argument est déjà un ID
        try:
            self.get_collection(collection_name_or_id)
            return collection_name_or_id
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise # Renvoyer les erreurs autres que "Not Found"

        # Deuxième tentative : l'argument est un nom
        collections = self.list_collections(project_id, limit=1000).get('items', [])
        for collection in collections:
            if collection.get('name') == collection_name_or_id:
                return collection['id']

        raise ValueError(f"Collection '{collection_name_or_id}' non trouvée dans le projet '{project_id}'.")


    # Documents

    def resolve_document_id(self, document_name_or_id: str, collection_id: str) -> str:
        """
        Résout un nom ou un ID de document en un ID de document.

        Args:
            document_name_or_id: Nom de fichier ou ID du document.
            collection_id: ID de la collection contenant le document.

        Returns:
            L'ID du document.

        Raises:
            ValueError: Si le document n'est pas trouvé.
        """
        if not document_name_or_id:
            raise ValueError("Le nom ou l'ID du document ne peut pas être vide.")

        # Première tentative : l'argument est déjà un ID
        try:
            self.get_document(collection_id, document_name_or_id)
            return document_name_or_id
        except requests.exceptions.HTTPError as e:
            if e.response.status_code != 404:
                raise  # Renvoyer les erreurs autres que "Not Found"

        # Deuxième tentative : l'argument est un nom de fichier
        documents = self.list_documents(collection_id, limit=1000).get('items', [])
        for document in documents:
            if document.get('name') == document_name_or_id:
                return document['id']

        raise ValueError(f"Document '{document_name_or_id}' non trouvé dans la collection '{collection_id}'.")

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
        collection_id: str = None,
        collections: list = None,
        query: str = None,
        project_id: str = None,
        top_k: int = 10,
        rerank: bool = True,
        k_rerank: int = 20,
        mode: str = "hybrid"
    ) -> Dict[str, Any]:
        """
        Effectue une recherche RAG dans une ou plusieurs collections.

        Args:
            collection_id: ID d'une seule collection (converti en liste)
            collections: Liste d'IDs de collections (prioritaire sur collection_id)
            query: Question/requête de recherche
            project_id: ID du projet RAG (requis, passé en query parameter)
            top_k: Nombre de résultats à retourner
            rerank: Activer le reranking des résultats
            k_rerank: Nombre de résultats pour le reranking
            mode: Mode de recherche ("hybrid", "semantic", "keyword")

        Returns:
            Résultats de recherche avec chunks pertinents
        """
        # Déterminer la liste de collections
        if collections is not None:
            # Utiliser la liste fournie
            collection_list = collections
        elif collection_id is not None:
            # Convertir l'ID unique en liste
            collection_list = [collection_id]
        else:
            raise ValueError("Vous devez fournir soit collection_id soit collections")

        if not query:
            raise ValueError("Le paramètre query est requis")

        if not project_id:
            raise ValueError("Le paramètre project_id est requis")

        endpoint = get_endpoint('search', self.config)

        # project_id en query parameter (selon spec API page 5)
        params = {'project_id': project_id}

        payload = {
            'collections': collection_list,  # API attend "collections" (liste)
            'query': query,
            'k': top_k,                      # API attend "k" pas "top_k"
            'rerank': rerank,
            'k_rerank': k_rerank,
            'mode': mode
        }

        return self._request(
            'POST',
            endpoint,
            params=params,                   # project_id dans l'URL
            include_content_type=True,
            data=json.dumps(payload)
        )
