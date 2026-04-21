# app.wikisi

Scraping et extraction du parc applicatif **WikiSI**.

## Architecture

- **`core/api_client.py`** : `WikiSIAPIClient` — client HTTP avec
  `requests.Session` pour les appels API WikiSI. Charge/cache les énumérations
  dans `workplace-ambulon/wikisi/download/enumerations.json`.
- **`core/scraper.py`** : `WikiSIScraper` — aspiration récursive d'un site web
  WikiSI (HTML → fichiers locaux).
- **`core/extractor.py`** : filtrage/extraction d'applications depuis JSON.
- **`core/json_to_md_converter.py`** : conversion applications → Markdown RAG.
- **`core/config_template.py`** : template embarqué pour `ambulon init wikisi`.

## Commandes exposées

| Commande | Rôle |
| --- | --- |
| `wikisi-sync-api`     | Synchroniser énumérations + applications depuis l'API |
| `wikisi-extract-apps` | Extraire les applications désignées (1 fichier JSON+MD par app) |
| `wikisi-extract`      | Filtrer des applications depuis un JSON local |
| `wikisi-md`           | Convertir le parc applicatif JSON en Markdown |
| `wikisi-scrape`       | Aspirer récursivement un site web WikiSI |
| `wikisi-flatten`      | Aplatir une arborescence WikiSI |

## Configuration

Voir `config/wikisi.yaml.example`. Variables d'environnement reconnues :

- `WIKISI_TOKEN` (optionnel) : token `X-Wikis-API-Key`
- `WIKISI_URL` (optionnel) : URL de base de l'API

## Exemple

```bash
# 1. Rapatrier les données de l'API
ambulon wikisi-sync-api

# 2. Extraire les applications listées dans config/wikisi.yaml
ambulon wikisi-extract-apps

# 3. Générer un Markdown consolidé pour RAG
ambulon wikisi-md --output applications.md
```
