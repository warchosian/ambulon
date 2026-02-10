 / Offre API PIAG / API PIAG - Appels RAG
API PIAG - Appels RAG
Phase d'expérimentations
L'offre API PIAG est en cours de construction.
Caractéristiques
Prérequis
Demande de création d'un projet RAG pour obtenir un identifiant et un token d'accès au projet
apiBase: https://preprod.api.piag.e2.rie.gouv.fr/rag/
Appels API supportés
Note
Remplacer dans les requêtes:
"my_project_token" par un token de projet valide
"my_project_id" par un id de projet valide
Corpus documentaires
Note


---

Remplacer dans les requêtes "my_collection_id" par l'identifiant de collection retouné au moment de la création de celle-ci
Créer une collection (corpus) - endpoint "api/v1/collections"
curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections?project_id=my_project_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Mon premier corpus",
  "description": "Description de mon premier corpus"
}'
==> Retoune l'identifiant de la collection
Lister les collections - endpoint "api/v1/collections"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections?project_id=my_project_id&limit=20&offset=0&order_by=name&order=asc' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
Récupérer les informations sur une collection - endpoint "api/v1/collections/{collection_id}"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
Modifier une collection - endpoint "api/v1/collections/{collection_id}"





---

curl -X PUT 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Mon premier corpus modifié",
  "description": "Description de mon premier corpus modifié"
}'
Supprimer une collection - endpoint "api/v1/collections/{collection_id}"
curl -X DELETE 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer my_project_token'
Documents
Note
Remplacer dans les requêtes:
"my_collection_id" par l'identifiant de collection retouné au moment de la création de celle-ci
"my_document_id" par l'identifiant de document récupéré au moment de la création de celui-ci
Téléverser un document - endpoint "api/v1/collections/{collection_id}/documents-upload-slow"
curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id/documents-upload-slow' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@mondocument.pdf;type=application/pdf'
==> Retoune l'identifiant du document





---

Récupérer les informations d'un document - endpoint "/api/v1/documents/{document_id}"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
Vérifier le status des documents d'une collection (corpus) - endpoint "api/v1/collections/{collection_id}/documents"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id/documents?limit=20&offset=0&order_by=name&order=asc' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
Supprimer d'un document - endpoint "api/v1/documents/{document_id}"
curl -X DELETE 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer my_project_token'
Récupérer les "chunks" d'un document - endpoint "api/v1/documents/{document_id}/chunks"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id/chunks?from_index=0&to_index=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
Recherche
Rechercher/récupérer les chunks significatifs d'un corpus documentaire par rapport à une question - endpoint "api/v1/search"
Note
Remplacer dans la requête "my_query" par une "query" en rapport avec le contenu de votre corpus.






---

curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/search?project_id=my_project_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: application/json' \
  -d '{
  "collections": [
    "my_collection_id"
  ],
  "query": "my_query",
  "rerank": true,
  "k_rerank": 20,
  "k": 10,
  "mode": "hybrid"
}'

