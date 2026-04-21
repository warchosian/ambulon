# app.piag

Client et commandes pour l'API **RAG PIAG** (Platform Intelligence Artificielle
Gouvernementale).

## Architecture

- **`core/client.py`** : `PIAGClient` — client HTTP avec `requests.Session`
  (pool de connexions), retry avec back-off, logging configurable, support
  context manager (`with PIAGClient(...) as c: ...`).
- **`core/config.py`** : chargement paresseux de `config/piag.yaml` avec
  `@functools.lru_cache`. Expose `get_config()`, `get_base_url()`, `get_timeout()`,
  `get_headers()`, etc.
- **`core/config_template.py`** : template embarqué utilisé par `ambulon init piag`.
- **`commands/`** : 18 commandes CLI, toutes préfixées `piag-` et dispatchées via
  `handle_rag_module()` dans `cli.py`.

## Commandes exposées

### Collections RAG

| Commande | Rôle |
| --- | --- |
| `piag-rag-collection-add`    | Créer une collection |
| `piag-rag-collection-list`   | Lister les collections du projet |
| `piag-rag-collection-get`    | Détails d'une collection |
| `piag-rag-collection-update` | Mettre à jour (nom, description) |
| `piag-rag-collection-rm`     | Supprimer |

### Documents

| Commande | Rôle |
| --- | --- |
| `piag-rag-doc-upload`  | Uploader un fichier |
| `piag-rag-doc-list`    | Lister les documents d'une collection |
| `piag-rag-doc-get`     | Détails d'un document |
| `piag-rag-doc-rm`      | Supprimer un document |
| `piag-rag-doc-chunks`  | Récupérer les chunks d'un document |

### Recherche & Chat

| Commande | Rôle |
| --- | --- |
| `piag-rag-search`       | Recherche sémantique dans une collection |
| `piag-rag-create`       | Pipeline création collection + upload batch |
| `piag-chat-apikey-info` | Vérifier le token |
| `piag-chat-query`       | Chat avec contexte RAG |
| `piag-chat-completion`  | Complétion simple (sans RAG) |
| `piag-chat-basic-query` | Query minimale |

## Configuration

Voir `config/piag.yaml.example`. Hiérarchie de priorité :

1. Arguments CLI (`--token`, `--project-id`, ...)
2. Variables d'environnement (`PIAG_RAG_API_TOKEN`, `PIAG_RAG_PROJECT_ID`, ...)
3. Fichier `config/piag.yaml`
4. Valeurs par défaut intégrées (dans `core/config.py`)

**Secret** : ne jamais mettre `token:` dans `piag.yaml`. Utiliser `PIAG_RAG_API_TOKEN`.

## Exemple

```bash
export PIAG_RAG_API_TOKEN="..."
ambulon piag-rag-collection-list --project-id my-project
ambulon piag-rag-collection-add --collection-name "MyDocs" --description "..."
ambulon piag-rag-doc-upload --collection-name "MyDocs" --file document.pdf
ambulon piag-rag-search --collection-name "MyDocs" --query "quelle est la procédure ?"
```
