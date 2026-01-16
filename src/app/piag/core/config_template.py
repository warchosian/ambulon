"""Template de configuration PIAG embarqué dans le code."""

PIAG_CONFIG_TEMPLATE = """# ============================================================================
# FICHIER DE CONFIGURATION EXEMPLE - API RAG PIAG
# ============================================================================
# Ce fichier sert de template pour l'intégration avec l'API RAG PIAG
#
# INSTRUCTIONS:
# 1. Copiez ce fichier vers config/piag.yaml
# 2. Remplissez les valeurs nécessaires (project_id, token, etc.)
# 3. Le fichier config/piag.yaml est dans .gitignore et ne sera pas commité
#
# HIÉRARCHIE DE PRIORITÉ: Arguments CLI > YAML > Variables d'environnement > Valeurs par défaut
# ============================================================================

# ==========================
# CONFIGURATION DE L'API
# ==========================
api:
  # URL de base de l'API RAG
  base_url: "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
  version: "v1"
  timeout: 30  # Timeout en secondes pour les requêtes HTTP
  max_retries: 3  # Nombre maximum de tentatives en cas d'échec

# ==========================
# ENDPOINTS DE L'API
# ==========================
endpoints:
  # Collections (corpus documentaires)
  collections: "/api/v1/collections"
  collection_detail: "/api/v1/collections/{collection_id}"

  # Documents
  documents_upload: "/api/v1/collections/{collection_id}/documents-upload-slow"
  document_detail: "/api/v1/documents/{document_id}"
  collection_documents: "/api/v1/collections/{collection_id}/documents"
  document_chunks: "/api/v1/documents/{document_id}/chunks"

  # Recherche RAG
  search: "/api/v1/search"

# ==========================
# HEADERS HTTP PAR DÉFAUT
# ==========================
headers:
  accept: "application/json"
  content_type: "application/json"
  user_agent: "Ambulon RAG Client/1.0"

# ==========================
# CONFIGURATION DU PROJET
# ==========================
# Ces valeurs ÉCRASENT les variables d'environnement si définies
project:
  # Identifiant du projet (fourni par votre administrateur)
  # project_id: "VOTRE_PROJECT_ID"

  # Nom et description par défaut pour les nouvelles collections (optionnel)
  # name: "Ma Collection"
  # description: "Description de la collection"

  # Identifiant d'une collection par défaut (optionnel)
  # collection_id: ""

# ==========================
# CONFIGURATION DE LA SÉCURITÉ
# ==========================
security:
  # ⚠️ ATTENTION: Stocker le token ici n'est PAS recommandé pour des raisons de sécurité
  # Préférez utiliser les variables d'environnement ou les arguments CLI
  #
  # Token d'authentification (JWT Bearer Token)
  # ⚠️ NE PAS COMMITER CE TOKEN DANS UN DÉPÔT PUBLIC ⚠️
  #
  # Pour utiliser ce token, décommentez la ligne ci-dessous UNIQUEMENT pour des tests locaux:
  # token: "VOTRE_TOKEN_ICI"

  # Variable d'environnement à utiliser si le token n'est pas fourni en argument ou dans le YAML
  # Recommandation: Exporter la variable d'environnement avec:
  #   export PIAG_RAG_API_TOKEN="VOTRE_TOKEN"
  token_env_var: "PIAG_RAG_API_TOKEN"

# ==========================
# CONFIGURATION DU LOGGING
# ==========================
logging:
  enable_debug: false  # Active les logs détaillés
  log_requests: true   # Affiche les requêtes HTTP envoyées
  log_responses: true  # Affiche les réponses HTTP reçues
  log_to_file: false   # Écrire les logs dans un fichier
  log_file_path: "logs/piag_rag.log"  # Chemin du fichier de log

# ==========================
# CONFIGURATION DU LISTING
# ==========================
listing:
  # Paramètres par défaut pour la pagination et le tri
  default_limit: 20  # Nombre maximum de résultats par page
  default_offset: 0  # Nombre de résultats à sauter
  default_order_by: "name"  # Champ de tri (name, created_at, updated_at, etc.)
  default_order: "asc"  # Ordre de tri: asc ou desc

# ==========================
# CONFIGURATION DES DOCUMENTS
# ==========================
document:
  # Identifiant du document par défaut (optionnel)
  # document_id: ""

upload:
  # collection_id: ""  # Collection cible (optionnel)
  # file_path: ""  # Chemin du fichier à téléverser (optionnel)

  # Types MIME autorisés
  allowed_mime_types:
    - "application/pdf"
    - "text/plain"
    - "text/markdown"
    - "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # DOCX
    - "application/msword"  # DOC
    - "text/html"

  # Taille maximale de fichier en Mo
  max_file_size_mb: 50

# ==========================
# CONFIGURATION DES CHUNKS
# ==========================
chunks:
  # Paramètres par défaut pour la récupération de chunks
  default_from_index: 0   # Index de départ
  default_to_index: 10    # Index de fin
  max_chunks_per_request: 100  # Nombre maximum de chunks par requête

# ==========================
# CONFIGURATION DE LA RECHERCHE RAG
# ==========================
search:
  # collection_id: ""  # Collection à interroger (optionnel)
  # query: ""  # Question/requête de recherche (optionnel)
  default_top_k: 5  # Nombre de résultats à retourner par défaut
  min_score: 0.5    # Score de similarité minimum (0.0 à 1.0)
  output_format: "json"  # Format de sortie: json ou text

# ==========================
# EXEMPLES D'UTILISATION
# ==========================
# Voici quelques exemples de commandes CLI avec cette configuration:
#
# 1. Lister les collections:
#    ambulon piag-collection-list --token $PIAG_RAG_API_TOKEN
#
# 2. Créer une nouvelle collection:
#    ambulon piag-collection-add --name "Ma Collection" --description "Test" --token $PIAG_RAG_API_TOKEN
#
# 3. Upload un document:
#    ambulon piag-doc-upload --collection-id <id> --file document.pdf --token $PIAG_RAG_API_TOKEN
#
# 4. Recherche RAG:
#    ambulon piag-search --collection-id <id> --query "Quelle est la procédure?" --token $PIAG_RAG_API_TOKEN
#
# Note: Le project_id est automatiquement récupéré depuis cette configuration si non fourni en CLI
"""
