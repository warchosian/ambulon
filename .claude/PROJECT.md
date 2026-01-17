# Ambulon - Architecture du Projet

Ce fichier contient les **directives spécifiques au projet Ambulon**.

Pour les règles générales de développement (argparse, configuration, tests, Poetry, etc.), consultez [GUIDELINES.md](GUIDELINES.md).

---

## Architecture des Modules

Le projet Ambulon est organisé en un seul package `app` avec des modules catégorisés :

```
src/
└── app/
    ├── cli/              # CLI principal et framework
    │   ├── main.py       # Point d'entrée de la commande
    │   └── __init__.py
    ├── piag/             # Module RAG PIAG
    │   ├── commands/     # CLI pour les opérations PIAG
    │   ├── core/         # Logique métier PIAG
    │   └── __init__.py
    ├── ocr/              # Module OCR
    │   ├── commands/
    │   ├── core/
    │   └── __init__.py
    ├── scan/             # Module Scanner
    │   ├── commands/
    │   ├── core/
    │   └── __init__.py
    ├── conversion/       # Module conversion (PDF, images, compression)
    │   ├── commands/
    │   ├── core/
    │   └── __init__.py
    ├── processing/       # Module traitement HTML/markdown
    │   ├── commands/
    │   ├── core/
    │   └── __init__.py
    ├── encoding/         # Module encodage/décodage
    │   ├── commands/
    │   ├── core/
    │   └── __init__.py
    ├── wikisi/           # Module WikiSI scraping
    │   ├── commands/
    │   ├── core/
    │   └── __init__.py
    └── gitlab/           # Module GitLab cloning
        ├── commands/
        ├── core/
        └── __init__.py
```

## Organisation par Catégories

### `app/cli/` : Framework CLI Principal

- Point d'entrée de la commande `ambulon`
- Routage vers les différents modules
- Utilitaires CLI communs
- Gestion de configuration globale

### Modules Métier

Chaque module sous `app/` est une catégorie fonctionnelle indépendante :

#### `app/piag/` - Module RAG PIAG
- Interaction avec l'API RAG PIAG (Retrieval-Augmented Generation)
- Gestion de collections de documents
- Upload et indexation de documents
- Recherche sémantique
- Configuration : `config/piag.yaml`
- Variables d'environnement : `PIAG_RAG_*`

#### `app/wikisi/` - Module WikiSI Scraping
- Aspiration de sites web WikiSI
- Extraction de données structurées
- Conversion vers formats exploitables
- Configuration : `config/wikisi.yaml`
- Variables d'environnement : `WIKISI_*`

#### `app/gitlab/` - Module GitLab Cloning
- Clonage automatisé de projets GitLab
- Gestion de tokens PAT
- Support multi-repositories
- Configuration : `config/gitlab.yaml`
- Variables d'environnement : `GITLAB_*`

#### `app/conversion/` - Module Conversion
- Conversion PDF vers Markdown/HTML
- Compression de PDF
- Conversion d'images vers PDF
- Pas de configuration externe (arguments CLI uniquement)

#### `app/processing/` - Module Traitement
- Aplatissement de HTML
- Création de HTML interactif
- Extraction de données structurées
- Pas de configuration externe (arguments CLI uniquement)

#### `app/encoding/` - Module Encodage
- Vérification UTF-8
- Conversion d'encodage
- Détection automatique d'encodage
- Pas de configuration externe (arguments CLI uniquement)

#### `app/ocr/` - Module OCR
- Reconnaissance optique de caractères
- Support Tesseract
- Extraction de texte depuis images
- Pas de configuration externe (arguments CLI uniquement)

#### `app/scan/` - Module Scanner
- Numérisation de documents
- Intégration scanner matériel
- Traitement post-scan
- Pas de configuration externe (arguments CLI uniquement)

### Caractéristiques Communes

- Structure standardisée : `commands/` et `core/`
- Pas de dépendances croisées entre modules
- Chaque module est autonome et testable indépendamment

## Structure Interne d'une Catégorie

Chaque catégorie sous `app/` suit cette structure standardisée :

```
app/<categorie>/
├── commands/       # Scripts CLI et points d'entrée
│   ├── cmd_operation1.py
│   ├── cmd_operation2.py
│   └── ...
├── core/          # Logique métier réutilisable
│   ├── config.py   # Gestion de configuration
│   ├── client.py   # Client API/HTTP
│   ├── models.py   # Classes métier
│   └── utils.py    # Utilitaires spécifiques
└── __init__.py    # Exports publics
```

### Répertoire `commands/`

Contient les modules CLI exécutables via `python -m`. Chaque fichier gère :
- Parsing des arguments CLI avec `argparse` (JAMAIS Typer)
- Hiérarchie de configuration : CLI > YAML > ENV > Défaut
- Affichage formaté des résultats pour l'utilisateur
- Gestion des erreurs et codes de sortie appropriés
- Invocation des fonctions métier depuis `core/`

### Répertoire `core/`

Contient la logique métier pure et réutilisable :
- Fonctions métier principales (sans CLI)
- Clients HTTP/API
- Gestion centralisée de la configuration
- Modèles de données et classes métier
- Utilitaires partagés entre commandes
- Code testable indépendamment du CLI

## Exemple : Module PIAG (RAG)

```
src/
└── app/
    ├── __init__.py
    ├── cli/
    │   ├── main.py                # CLI principal, route vers app.piag
    │   └── __init__.py
    └── piag/
        ├── commands/
        │   ├── piag_collection_add.py      # CLI: créer collection
        │   ├── piag_collection_list.py     # CLI: lister collections
        │   ├── piag_doc_upload.py          # CLI: uploader document
        │   └── piag_search.py              # CLI: recherche RAG
        ├── core/
        │   ├── config.py              # Config YAML centralisée
        │   ├── client.py              # Client HTTP PIAG
        │   ├── collections.py         # Logique collections
        │   └── documents.py           # Logique documents
        └── __init__.py                # Exports: create_collection(), etc.
```

### Imports dans le Code

```python
# Dans app/cli/main.py
from app.piag.commands import piag_collection_add, piag_search

# Dans app/piag/commands/piag_collection_add.py
from app.piag.core.config import load_config
from app.piag.core.client import PIAGClient

# Pour l'utilisateur final (API programmatique)
from app.piag.core import PIAGClient
```

## Principes de Séparation

### 1. Pas de Duplication

Le code commun (config, HTTP, logging) doit être dans `core/`, jamais dupliqué dans `commands/`.

**❌ Anti-pattern :**
```python
# Dans commands/cmd1.py
def load_config():
    # ... duplication de code config

# Dans commands/cmd2.py
def load_config():
    # ... même code dupliqué
```

**✅ Pattern correct :**
```python
# Dans core/config.py
def load_config():
    # ... logique centralisée

# Dans commands/cmd1.py et commands/cmd2.py
from ..core.config import load_config
```

### 2. Réutilisabilité

Les fonctions dans `core/` doivent être utilisables :
- Par les CLI dans `commands/`
- Par d'autres modules Python
- Par des scripts externes
- Dans des notebooks Jupyter

### 3. Testabilité

La logique métier dans `core/` doit être testable indépendamment du CLI.

**Exemple :**
```python
# tests/unit/test_piag/test_client.py
from app.piag.core.client import PIAGClient

def test_create_collection():
    """Test création de collection sans passer par le CLI."""
    client = PIAGClient(base_url="https://api.example.com", token="test")
    result = client.create_collection("test-collection")
    assert result['status'] == 'success'
```

### 4. Clarté

Organisation prévisible pour tous les développeurs :
- Besoin d'une commande CLI → `app/<categorie>/commands/`
- Besoin de logique métier → `app/<categorie>/core/`
- Besoin du framework CLI → `app/cli/`

### 5. Indépendance

Chaque catégorie sous `app/` est autonome et n'a pas de dépendances entre catégories.

**❌ Interdit :**
```python
# Dans app/piag/core/client.py
from app.wikisi.core.scraper import WikiSIScraper  # ❌ Dépendance croisée
```

**✅ Correct :**
```python
# Si nécessaire, créer un module commun dans app/core/
from app.core.http_client import HTTPClient  # ✅ Utilitaire commun
```

## Commandes Disponibles

### Module PIAG

- `ambulon piag-collection-add` - Créer une collection
- `ambulon piag-collection-list` - Lister les collections
- `ambulon piag-collection-get` - Obtenir les détails d'une collection
- `ambulon piag-collection-update` - Mettre à jour une collection
- `ambulon piag-collection-rm` - Supprimer une collection
- `ambulon piag-doc-upload` - Uploader un document
- `ambulon piag-doc-list` - Lister les documents
- `ambulon piag-doc-get` - Obtenir les détails d'un document
- `ambulon piag-doc-chunks` - Afficher les chunks d'un document
- `ambulon piag-doc-rm` - Supprimer un document
- `ambulon piag-search` - Effectuer une recherche RAG

### Module WikiSI

- `ambulon wikisi-scrape` - Aspirer un site WikiSI
- `ambulon wikisi-extract-json` - Extraire des données JSON
- `ambulon wikisi-flatten-json` - Aplatir un JSON complexe
- `ambulon wikisi-parkjson2json` - Convertir PARK JSON vers JSON standard
- `ambulon wikisi-parkjson2md` - Convertir PARK JSON vers Markdown

### Module GitLab

- `ambulon gitlab-clone` - Cloner des projets GitLab

### Module Conversion

- `ambulon pdf2md` - Convertir PDF vers Markdown
- `ambulon pdf2html` - Convertir PDF vers HTML
- `ambulon compress-pdf` - Compresser un PDF
- `ambulon img2pdf` - Convertir images vers PDF

### Module Processing

- `ambulon flatten-html` - Aplatir un fichier HTML
- `ambulon make-html-interactive` - Créer un HTML interactif

### Module Encoding

- `ambulon check-utf8` - Vérifier l'encodage UTF-8

### Module OCR

- `ambulon ocr` - Effectuer une OCR sur une image

### Module Scan

- `ambulon scan` - Numériser un document

## Configuration des Modules

### Modules avec Configuration YAML

Les modules suivants utilisent la hiérarchie de configuration complète (CLI > YAML > ENV > Defaults) :

#### Module PIAG
- Fichier : `config/piag.yaml`
- Variables d'environnement : `PIAG_RAG_*`
- Exemple : `PIAG_RAG_API_TOKEN`, `PIAG_RAG_PROJECT_ID`, `PIAG_RAG_BASE_URL`

#### Module WikiSI
- Fichier : `config/wikisi.yaml`
- Variables d'environnement : `WIKISI_*`
- Exemple : `WIKISI_BASE_URL`, `WIKISI_AUTH_TYPE`, `WIKISI_TOKEN`

#### Module GitLab
- Fichier : `config/gitlab.yaml`
- Variables d'environnement : `GITLAB_*`
- Exemple : `GITLAB_PRIVATE_TOKEN`, `GITLAB_USERNAME`, `GITLAB_BASE_URL`

### Modules sans Configuration YAML

Les modules suivants utilisent uniquement des arguments CLI (pas de fichier YAML) :

- `app/conversion/` - Conversion de documents
- `app/processing/` - Traitement HTML/markdown
- `app/encoding/` - Encodage/décodage
- `app/ocr/` - OCR
- `app/scan/` - Scanner

## Emplacement des Fichiers de Configuration

**TOUS les fichiers de configuration DOIVENT être cherchés depuis le répertoire courant (`Path.cwd()`) où ambulon est lancé, PAS depuis le répertoire d'installation du package.**

**❌ Anti-pattern (INTERDIT) :**
```python
# Dans app/piag/core/config.py
current_dir = Path(__file__).parent  # ❌ Cherche depuis l'installation du package
config_path = current_dir / "config" / "piag.yaml"
```

**✅ Pattern correct (OBLIGATOIRE) :**
```python
# Dans app/piag/core/config.py
cwd = Path.cwd()  # ✅ Cherche depuis le répertoire courant
config_path = cwd / "config" / "piag.yaml"
```

**Support des chemins avec tilde (`~`) :**
```python
# Dans app/core/config_loader.py
if config_path:
    # Expand ~ and environment variables in the path
    expanded_path = Path(config_path).expanduser()

    if expanded_path.exists():
        # ...
```

## Point d'Entrée Principal

Le point d'entrée de l'application est `src/app/cli/main.py`.

**Commande :** `ambulon [SOUS-COMMANDE] [OPTIONS]`

**Exemples :**
```bash
# Afficher la version
ambulon --version

# Afficher l'aide générale
ambulon --help

# Afficher l'aide d'une sous-commande
ambulon piag-search --help

# Exécuter une commande
ambulon piag-search --query "test" --collection-id "abc123"
```

## Versioning

La version est gérée dans `src/app/__init__.py` :

```python
"""Package principal app - tous les modules métier d'Ambulon."""

__version__ = "2.0.3"
```

**IMPORTANT :** La version est importée dynamiquement dans `src/app/cli/__init__.py` :

```python
"""CLI framework for Ambulon."""

from app import __version__

__all__ = ['__version__']
```

**❌ Ne JAMAIS hardcoder la version** dans `app/cli/__init__.py`, toujours importer depuis `app.__init__.py`.

## Tests Spécifiques à Ambulon

### Structure des Tests

```
tests/
├── unit/
│   ├── test_piag/
│   ├── test_wikisi/
│   ├── test_gitlab/
│   ├── test_conversion/
│   ├── test_processing/
│   ├── test_encoding/
│   ├── test_ocr/
│   └── test_scan/
├── integration/
│   ├── test_piag_workflow.py
│   ├── test_wikisi_pipeline.py
│   └── test_gitlab_clone.py
└── e2e/
    ├── test_piag_e2e.py
    └── test_wikisi_e2e.py
```

### Objectifs de Couverture par Module

| Module | Couverture Minimale | Couverture Cible | Notes |
|--------|---------------------|------------------|-------|
| `app/piag/` | 85% | 95% | Module critique (API externe) |
| `app/wikisi/` | 80% | 90% | Web scraping complexe |
| `app/gitlab/` | 80% | 90% | Clonage Git critique |
| `app/conversion/` | 80% | 90% | Transformations de données |
| `app/processing/` | 75% | 85% | Traitement HTML |
| `app/encoding/` | 90% | 95% | Manipulation encodage (critique) |
| `app/ocr/` | 70% | 85% | Dépend de Tesseract externe |
| `app/scan/` | 70% | 85% | Dépend de matériel externe |
| `app/cli/` | 70% | 85% | CLI (testable via E2E) |

## Dépendances Externes

### APIs et Services

- **API PIAG RAG** : `https://preprod.api.piag.e2.rie.gouv.fr/rag/`
  - Authentication : Bearer token
  - Timeout par défaut : 30 secondes

### Outils Externes

- **Tesseract OCR** : Requis pour le module OCR
- **Git** : Requis pour le module GitLab
- **Scanner** : Requis pour le module Scan (matériel)

### Librairies Python Principales

- `requests` : Requêtes HTTP
- `PyYAML` : Parsing de fichiers YAML
- `pypdf` : Manipulation de PDF
- `Pillow` : Traitement d'images
- `beautifulsoup4` : Parsing HTML
- `markdown` : Conversion Markdown
- `pytesseract` : Interface Tesseract OCR

## Workflows Métier Spécifiques

### Workflow PIAG RAG

1. Créer une collection : `piag-collection-add`
2. Uploader des documents : `piag-doc-upload`
3. Rechercher dans la collection : `piag-search`
4. (Optionnel) Voir les chunks : `piag-doc-chunks`
5. (Optionnel) Supprimer documents/collection : `piag-doc-rm` / `piag-collection-rm`

### Workflow WikiSI

1. Aspirer le site : `wikisi-scrape`
2. Extraire les données : `wikisi-extract-json`
3. Aplatir le JSON : `wikisi-flatten-json`
4. Convertir vers Markdown : `wikisi-parkjson2md`

### Workflow GitLab

1. Configurer token PAT dans `config/gitlab.yaml` ou variables d'env
2. Cloner les projets : `gitlab-clone`

## Maintenance et Évolution

### Ajout d'un Nouveau Module

1. Créer la structure : `app/<nouveau-module>/`
   - `commands/` - Scripts CLI
   - `core/` - Logique métier
   - `__init__.py` - Exports publics

2. Implémenter les commandes avec argparse (JAMAIS Typer)

3. Si le module nécessite une configuration :
   - Créer `config/<nouveau-module>.yaml.example`
   - Ajouter `config/<nouveau-module>.yaml` dans `.gitignore`
   - Implémenter la hiérarchie CLI > YAML > ENV > Defaults

4. Ajouter les routes dans `app/cli/main.py`

5. Écrire les tests (couverture ≥ 80%)

6. Mettre à jour la documentation :
   - Ce fichier (`PROJECT.md`)
   - `README.md`
   - `CHANGELOG.md`

### Ajout d'une Nouvelle Commande à un Module Existant

1. Créer `app/<module>/commands/<nouvelle-commande>.py`
2. Implémenter avec argparse et la hiérarchie de configuration
3. Ajouter la route dans `app/cli/main.py`
4. Écrire les tests
5. Mettre à jour la documentation

---

**Pour les directives générales de développement (argparse, configuration, tests, Poetry, etc.), consultez [GUIDELINES.md](GUIDELINES.md).**
