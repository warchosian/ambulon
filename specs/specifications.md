 / Ore API PIAG / API PIAG - Appels RAG
API PIAG - Appels RAG
 Phase d'expérimentaons
L'ore API PIAG est en cours de construcon.
Caractéristiques
 Prérequis
Demande de créaon d'un projet RAG pour obtenir un idenant et un token d'accès au projet
apiBase: hps://preprod.api.piag.e2.rie.gouv.fr/rag/
Appels API supportés
 Note
Remplacer dans les requêtes:
"my_project_token" par un token de projet valide
"my_project_id" par un id de projet valide
Corpus documentaires
 Note
Remplacer dans les requêtes "my_collecon_id" par l'idenant de collecon retouné au moment de la créaon de celle-ci
Créer une collecon (corpus) - endpoint "api/v1/collecons"
curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections?project_id=my_project_id' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token' \
 -H 'Content-Type: application/json' \
 -d '{
 "name": "Mon premier corpus",
 "description": "Description de mon premier corpus"
}'
==> Retoune l'idenant de la collecon
Lister les collecons - endpoint "api/v1/collecons"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections?project_id=my_project_id&limit=20&offset=0&order_by=name&order=asc' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token'
Récupérer les informaons sur une collecon - endpoint "api/v1/collecons/{collecon_id}"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token'
Modier une collecon - endpoint "api/v1/collecons/{collecon_id}"



curl -X PUT 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token' \
 -H 'Content-Type: application/json' \
 -d '{
 "name": "Mon premier corpus modifié",
 "description": "Description de mon premier corpus modifié"
}'
Supprimer une collecon - endpoint "api/v1/collecons/{collecon_id}"
curl -X DELETE 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
 -H 'accept: */*' \
 -H 'Authorization: Bearer my_project_token'
Documents
 Note
Remplacer dans les requêtes:
"my_collecon_id" par l'idenant de collecon retouné au moment de la créaon de celle-ci
"my_document_id" par l'idenant de document récupéré au moment de la créaon de celui-ci
Téléverser un document - endpoint "api/v1/collecons/{collecon_id}/documents-upload-slow"
curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id/documents-upload-slow' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token' \
 -H 'Content-Type: multipart/form-data' \
 -F 'file=@mondocument.pdf;type=application/pdf'
==> Retoune l'idenant du document



Récupérer les informaons d'un document - endpoint "/api/v1/documents/{document_id}"
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token'
Vérier le status des documents d'une collecon (corpus) - endpoint "api/v1/collecons/{collecon_id}/documents"
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
Rechercher/récupérer les chunks signicafs d'un corpus documentaire par rapport à une queson - endpoint "api/v1/search"
 Note
Remplacer dans la requête "my_query" par une "query" en rapport avec le contenu de votre corpus.




curl -X POST 'https
://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/search?project_id=my_project_id' \
 -H 'accept: application/json' \
 -H 'Authorization: Bearer my_project_token' \
 -H 'Content-Type: application/json' \
 -d '{
 "collections": [
 "my_collection_id"
 ],
 "query": "my_query"
,
 "rerank": true
,
 "k_rerank": 20
,
 "k": 10
,
 "mode": "hybrid"
}'
