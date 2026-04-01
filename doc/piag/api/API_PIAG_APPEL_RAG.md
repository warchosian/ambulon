# API PIAG - Appels RAG

> ⚠️ **Phase d'expérimentations**  
> L'offre API PIAG est en cours de construction.

---

## 📋 Prérequis

- Demande de création d'un projet RAG pour obtenir un identifiant et un token d'accès au projet
- **Base URL** : `https://preprod.api.piag.e2.rie.gouv.fr/rag/`

## 🔧 Appels API supportés

> 📝 **Note** : Remplacer dans les requêtes :
> - `"my_project_token"` par un token de projet valide
> - `"my_project_id"` par un id de projet valide

---

## 📚 Corpus documentaires

> 📝 **Note** : Remplacer dans les requêtes `"my_collection_id"` par l'identifiant de collection retourné au moment de la création de celle-ci.

### Créer une collection (corpus)  
**Endpoint** : `POST /api/v1/collections`

```bash
curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections?project_id=my_project_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Mon premier corpus",
    "description": "Description de mon premier corpus"
  }'
```
✅ Retourne l'identifiant de la collection

---

### Lister les collections  
**Endpoint** : `GET /api/v1/collections`

```bash
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections?project_id=my_project_id&limit=20&offset=0&order_by=name&order=asc' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
```

---

### Récupérer les informations sur une collection  
**Endpoint** : `GET /api/v1/collections/{collection_id}`

```bash
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
```

---

### Modifier une collection  
**Endpoint** : `PUT /api/v1/collections/{collection_id}`

```bash
curl -X PUT 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Mon premier corpus modifié",
    "description": "Description de mon premier corpus modifié"
  }'
```

---

### Supprimer une collection  
**Endpoint** : `DELETE /api/v1/collections/{collection_id}`

```bash
curl -X DELETE 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer my_project_token'
```

---

## 📄 Documents

> 📝 **Note** : Remplacer dans les requêtes :
> - `"my_collection_id"` par l'identifiant de collection retourné au moment de la création
> - `"my_document_id"` par l'identifiant de document récupéré au moment de la création

### Téléverser un document  
**Endpoint** : `POST /api/v1/collections/{collection_id}/documents-upload-slow`

```bash
curl -X POST 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id/documents-upload-slow' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@mondocument.pdf;type=application/pdf'
```
✅ Retourne l'identifiant du document

---

### Récupérer les informations d'un document  
**Endpoint** : `GET /api/v1/documents/{document_id}`

```bash
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
```

---

### Vérifier le statut des documents d'une collection  
**Endpoint** : `GET /api/v1/collections/{collection_id}/documents`

```bash
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/collections/my_collection_id/documents?limit=20&offset=0&order_by=name&order=asc' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
```

---

### Supprimer un document  
**Endpoint** : `DELETE /api/v1/documents/{document_id}`

```bash
curl -X DELETE 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer my_project_token'
```

---

### Récupérer les "chunks" d'un document  
**Endpoint** : `GET /api/v1/documents/{document_id}/chunks`

```bash
curl -X GET 'https://preprod.api.piag.e2.rie.gouv.fr/rag/api/v1/documents/my_document_id/chunks?from_index=0&to_index=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer my_project_token'
```

---

## 🔍 Recherche

### Rechercher/récupérer les chunks significatifs d'un corpus documentaire par rapport à une question  
**Endpoint** : `POST /api/v1/search`

> 📝 **Note** : Remplacer dans la requête `"my_query"` par une query en rapport avec le contenu de votre corpus.

```bash
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
```

### Paramètres de recherche

| Paramètre | Type | Description |
|-----------|------|-------------|
| `collections` | array | Liste des IDs de collections à interroger |
| `query` | string | Question ou requête de recherche |
| `rerank` | boolean | Activer le re-ranking des résultats |
| `k_rerank` | integer | Nombre de résultats à re-ranker |
| `k` | integer | Nombre final de résultats à retourner |
| `mode` | string | Mode de recherche : `"hybrid"`, `"semantic"`, `"keyword"` |

---

> ℹ️ **Environment** : Préproduction (`preprod`)  
> 🌐 **Domaine** : `api.piag.e2.rie.gouv.fr`  
> 🔐 **Authentification** : Bearer Token via header `Authorization`

