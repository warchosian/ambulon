"""Module RAG PIAG pour Ambulon.

Ce module fournit des outils pour interagir avec l'API RAG PIAG.

Fonctionnalités:
- Gestion des collections (corpus documentaires)
- Gestion des documents
- Recherche sémantique RAG
"""

# Collections
from .piag_collection_add import create_rag_collection, load_config
from .piag_collection_list import list_collections
from .piag_collection_get import get_collection
from .piag_collection_update import update_collection
from .piag_collection_rm import delete_collection

# Documents
from .piag_doc_upload import upload_document
from .piag_doc_get import get_document
from .piag_doc_list import list_documents
from .piag_doc_rm import delete_document
from .piag_doc_chunks import get_document_chunks

# Recherche RAG
from .piag_search import search_rag

__all__ = [
    # Collections
    'create_rag_collection',
    'list_collections',
    'get_collection',
    'update_collection',
    'delete_collection',

    # Documents
    'upload_document',
    'get_document',
    'list_documents',
    'delete_document',
    'get_document_chunks',

    # Recherche
    'search_rag',

    # Utilitaires
    'load_config'
]
