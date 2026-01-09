"""Module PIAG pour Ambulon - Interaction avec l'API RAG PIAG.

Ce module fournit des outils pour interagir avec l'API RAG PIAG :
- Gestion des collections (corpus documentaires)
- Gestion des documents
- Recherche sémantique RAG

Utilisation programmatique:
    from app.piag import PIAGClient, load_config

    # Créer un client
    client = PIAGClient(api_token="your_token")

    # Créer une collection
    collection = client.create_collection(
        project_id="project_id",
        name="Ma collection",
        description="Description"
    )

    # Uploader un document
    result = client.upload_document(collection_id, "/path/to/doc.pdf")

    # Rechercher
    results = client.search(collection_id, "ma requête", top_k=5)
"""

from .core import PIAGClient, load_config

# Pour compatibilité avec l'ancienne API
from .core.client import PIAGClient


def create_collection(
    project_id: str,
    name: str,
    description: str,
    api_token: str,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Crée une nouvelle collection RAG."""
    client = PIAGClient(api_token, base_url, config)
    return client.create_collection(project_id, name, description)


def list_collections(
    project_id: str,
    api_token: str,
    limit: int = 20,
    offset: int = 0,
    order_by: str = "name",
    order: str = "asc",
    base_url: str = None,
    config: dict = None
) -> dict:
    """Liste les collections d'un projet."""
    client = PIAGClient(api_token, base_url, config)
    return client.list_collections(project_id, limit, offset, order_by, order)


def get_collection(collection_id: str, api_token: str, base_url: str = None, config: dict = None) -> dict:
    """Récupère les informations d'une collection."""
    client = PIAGClient(api_token, base_url, config)
    return client.get_collection(collection_id)


def update_collection(
    collection_id: str,
    api_token: str,
    name: str = None,
    description: str = None,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Met à jour une collection."""
    client = PIAGClient(api_token, base_url, config)
    return client.update_collection(collection_id, name, description)


def delete_collection(collection_id: str, api_token: str, base_url: str = None, config: dict = None) -> dict:
    """Supprime une collection."""
    client = PIAGClient(api_token, base_url, config)
    return client.delete_collection(collection_id)


def upload_document(
    collection_id: str,
    file_path: str,
    api_token: str,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Téléverse un document vers une collection."""
    client = PIAGClient(api_token, base_url, config)
    return client.upload_document(collection_id, file_path)


def list_documents(
    collection_id: str,
    api_token: str,
    limit: int = 20,
    offset: int = 0,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Liste les documents d'une collection."""
    client = PIAGClient(api_token, base_url, config)
    return client.list_documents(collection_id, limit, offset)


def get_document(
    collection_id: str,
    document_id: str,
    api_token: str,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Récupère les informations d'un document."""
    client = PIAGClient(api_token, base_url, config)
    return client.get_document(collection_id, document_id)


def delete_document(
    collection_id: str,
    document_id: str,
    api_token: str,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Supprime un document."""
    client = PIAGClient(api_token, base_url, config)
    return client.delete_document(collection_id, document_id)


def get_document_chunks(
    collection_id: str,
    document_id: str,
    api_token: str,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Récupère les chunks d'un document."""
    client = PIAGClient(api_token, base_url, config)
    return client.get_document_chunks(collection_id, document_id)


def search_rag(
    collection_id: str,
    query: str,
    api_token: str,
    top_k: int = 5,
    base_url: str = None,
    config: dict = None
) -> dict:
    """Effectue une recherche RAG dans une collection."""
    client = PIAGClient(api_token, base_url, config)
    return client.search(collection_id, query, top_k)


__all__ = [
    # Client
    'PIAGClient',
    'load_config',
    # Collections
    'create_collection',
    'list_collections',
    'get_collection',
    'update_collection',
    'delete_collection',
    # Documents
    'upload_document',
    'list_documents',
    'get_document',
    'delete_document',
    'get_document_chunks',
    # Search
    'search_rag',
]
