# CLAUDE Project Guidelines

Ce projet utilise les outils suivants pour la gestion des modules Python et les commits conventionnels.

## Architecture des Modules

Le projet est organisé en un seul package `app` avec des modules catégorisés :

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
    └── conversion/       # Module conversion (PDF, images, compression)
        ├── commands/
        ├── core/
        └── __init__.py
```

### Organisation par Catégories

**`app/cli/`** : Framework CLI principal
- Point d'entrée de la commande `ambulon`
- Routage vers les différents modules
- Utilitaires CLI communs
- Gestion de configuration globale

**Modules métier** : `app/piag/`, `app/ocr/`, `app/scan/`, `app/conversion/`
- Chaque module est une catégorie fonctionnelle indépendante
- Structure standardisée : `commands/` et `core/`
- Pas de dépendances croisées entre modules

### Structure Interne d'une Catégorie

Chaque catégorie sous `app/` suit cette structure :

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

#### Répertoire `commands/`

Contient les modules CLI exécutables via `python -m`. Chaque fichier gère :
- Parsing des arguments CLI avec `argparse`
- Hiérarchie de configuration : CLI > YAML > ENV > Défaut
- Affichage formaté des résultats pour l'utilisateur
- Gestion des erreurs et codes de sortie appropriés
- Invocation des fonctions métier depuis `core/`

#### Répertoire `core/`

Contient la logique métier pure et réutilisable :
- Fonctions métier principales (sans CLI)
- Clients HTTP/API
- Gestion centralisée de la configuration
- Modèles de données et classes métier
- Utilitaires partagés entre commandes
- Code testable indépendamment du CLI

### Exemple : Module PIAG (RAG)

```
src/
└── app/
    ├── __init__.py
    ├── cli/
    │   ├── main.py                # CLI principal, route vers app.piag
    │   └── __init__.py
    └── piag/
        ├── commands/
        │   ├── collection_add.py      # CLI: créer collection
        │   ├── collection_list.py     # CLI: lister collections
        │   ├── doc_upload.py          # CLI: uploader document
        │   └── search.py              # CLI: recherche RAG
        ├── core/
        │   ├── config.py              # Config YAML centralisée
        │   ├── client.py              # Client HTTP PIAG
        │   ├── collections.py         # Logique collections
        │   └── documents.py           # Logique documents
        └── __init__.py                # Exports: create_collection(), etc.
```

**Imports dans le code :**
```python
# Dans app/cli/main.py
from app.piag import create_collection, search_rag

# Dans app/piag/commands/collection_add.py
from app.piag.core.config import load_config
from app.piag.core.client import PIAGClient

# Pour l'utilisateur final (API programmatique)
from app.piag import create_collection, upload_document
```

### Principes de Séparation

1. **Pas de duplication** : Le code commun (config, HTTP, logging) doit être dans `core/`, jamais dupliqué dans `commands/`.

2. **Réutilisabilité** : Les fonctions dans `core/` doivent être utilisables :
   - Par les CLI dans `commands/`
   - Par d'autres modules Python
   - Par des scripts externes
   - Dans des notebooks Jupyter

3. **Testabilité** : La logique métier dans `core/` doit être testable indépendamment du CLI.

4. **Clarté** : Organisation prévisible pour tous les développeurs :
   - Besoin d'une commande CLI → `app/<categorie>/commands/`
   - Besoin de logique métier → `app/<categorie>/core/`
   - Besoin du framework CLI → `app/cli/`

5. **Indépendance** : Chaque catégorie sous `app/` est autonome et n'a pas de dépendances entre catégories.

### Gestion des Logs et Affichage Console

**Principe général** : Toute application doit utiliser un gestionnaire de logs centralisé pour l'affichage console et la persistance des erreurs.

#### Configuration des Logs

```python
import logging
from datetime import datetime
from pathlib import Path

# Format : application_AAAA-MM-JJ_HHhMMmSSs.log
timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"{application_name}_{timestamp}.log"

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),  # Fichier
        logging.StreamHandler()  # Console
    ]
)

logger = logging.getLogger(__name__)
```

#### Règles d'Utilisation

1. **Affichage Console** : Utiliser le logger, pas `print()`
   ```python
   # ❌ Éviter
   print("Traitement en cours...")

   # ✅ Correct
   logger.info("Traitement en cours...")
   ```

2. **Logs d'Erreurs** : Automatiquement enregistrés dans `logs/`
   ```python
   try:
       # code risqué
   except Exception as e:
       logger.error(f"Erreur lors du traitement: {e}", exc_info=True)
   ```

3. **Niveaux de Log** :
   - `DEBUG` : Informations de débogage détaillées
   - `INFO` : Confirmations de déroulement normal
   - `WARNING` : Avertissements (non bloquants)
   - `ERROR` : Erreurs (échecs d'opérations)
   - `CRITICAL` : Erreurs critiques (crash imminent)

4. **Emplacement des Logs** :
   - Répertoire : `logs/` à la racine du projet
   - Format du nom : `{application}_{AAAA-MM-JJ}_{HHhMMmSSs}.log`
   - Exemple : `piag_search_2026-01-09_14h23m45s.log`

5. **Rotation des Logs** : Utiliser `RotatingFileHandler` pour les applications longue durée
   ```python
   from logging.handlers import RotatingFileHandler

   handler = RotatingFileHandler(
       log_file,
       maxBytes=10*1024*1024,  # 10 MB
       backupCount=5,
       encoding='utf-8'
   )
   ```

#### Exemple d'Implémentation

```python
# Dans app/cli/logging_config.py
import logging
from datetime import datetime
from pathlib import Path

def setup_logging(application_name: str, level=logging.INFO):
    """Configure le système de logging pour une application."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{application_name}_{timestamp}.log"

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(application_name)

# Utilisation dans app/piag/commands/search.py
from app.cli.logging_config import setup_logging

logger = setup_logging("piag_search")
logger.info("Démarrage de la recherche RAG...")
```

#### Avantages

- **Traçabilité** : Tous les événements et erreurs sont enregistrés avec horodatage
- **Débogage** : Fichiers de logs consultables après exécution
- **Cohérence** : Format uniforme pour toutes les applications
- **Performance** : Rotation automatique pour éviter les fichiers trop volumineux

## Gestion des dépendances Python avec Poetry

[Poetry](https://python-poetry.org/) est utilisé pour la gestion des dépendances et le packaging. Pour commencer :

1.  **Installer Poetry**: Si vous n'avez pas Poetry, suivez le guide d'installation officiel.
2.  **Installer les dépendances**: Naviguez à la racine du projet et exécutez :
    ```bash
    poetry install
    ```
3.  **Vérification avant Build**: Avant de procéder à un `poetry build`, assurez-vous toujours que le fichier `pyproject.toml` contient toutes les dépendances nécessaires et qu'elles sont cohérentes.
4.  **Activer l'environnement virtuel**: Pour activer l'environnement virtuel du projet, exécutez :
    ```bash
    poetry shell
    ```

## Workflow de Versioning et de Release

Ce projet suit le **Semantic Versioning (SemVer)** et utilise [Commitizen](https://commitizen-tool.github.io/commitizen/) pour automatiser la gestion des versions et la génération du changelog.

### Semantic Versioning (SemVer)

Le numéro de version est structuré en `MAJEUR.MINEUR.PATCH` :
- **MAJEUR** : Incrémenté pour des changements d'API non rétrocompatibles (tout ce qui est marqué comme `BREAKING CHANGE`).
- **MINEUR** : Incrémenté pour de nouvelles fonctionnalités rétrocompatibles (un commit de type `feat`).
- **PATCH** : Incrémenté pour des corrections de bugs rétrocompatibles (un commit de type `fix`).

### Commits Conventionnels (Conventional Commits)

Les messages de commit doivent suivre la spécification [Conventional Commits](https://www.conventionalcommits.org/). C'est Commitizen qui s'en assure. Le type de commit détermine directement l'incrémentation de la version :

- `feat:` : Une nouvelle fonctionnalité pour l'utilisateur. **Résulte en une version MINEURE.**
- `fix:` : Une correction de bug pour l'utilisateur. **Résulte en une version PATCH.**
- `docs:` : Changements affectant uniquement la documentation.
- `style:` : Changements qui n'affectent pas le sens du code (espaces, formatage, etc.).
- `refactor:` : Une modification du code qui ne corrige ni un bug ni n'ajoute de fonctionnalité.
- `perf:` : Une modification du code qui améliore les performances.
- `test:` : Ajout de tests manquants ou correction de tests existants.
- `chore:` : Modifications du processus de build ou des outils auxiliaires.

Un `BREAKING CHANGE:` dans le pied de page du message de commit, ou un `!` après le type/scope (ex: `feat!: Mettre à jour l'API`), **résultera en une version MAJEURE**.

### Processus de Release

Le processus de création d'une nouvelle release est strict et doit suivre ces étapes dans l'ordre :

1.  **Effectuer les modifications** : Modifiez le code comme nécessaire.

2.  **Indexer et Commiter**: Indexez vos changements (`git add .`) et utilisez la commande `cz commit` pour créer un message de commit guidé et conventionnel.
    ```bash
    cz commit
    ```

3.  **Créer la nouvelle version**: Exécutez `cz bump`. Cette commande va automatiquement :
    - Déterminer le nouveau numéro de version (PATCH, MINOR, ou MAJOR) en se basant sur vos commits.
    - Mettre à jour la version dans `pyproject.toml` et `src/app/__init__.py`.
    - Générer ou mettre à jour le `CHANGELOG.md`.
    - Créer un commit et un tag Git pour la nouvelle version.
    ```bash
    cz bump --changelog
    ```

4.  **Générer le build**: Une fois la version taguée, générez les fichiers de distribution.
    ```bash
    poetry build
    ```

5.  **Vérification Systématique du Build**: **Cette étape est obligatoire avant de pousser les changements.** Inspectez le contenu du fichier `.whl` pour garantir qu'il contient tous les fichiers attendus (modules Python, fichiers de configuration, etc.).
    ```bash
    # Remplacez x.y.z par la version que vous venez de créer
    python -m zipfile -l dist/ambulon-x.y.z-py3-none-any.whl
    ```
    Si des fichiers manquent, retournez à la section "Vérification de l'Intégrité du Build" pour ajuster la configuration `pyproject.toml`, puis recommencez le build.

6.  **Pousser les changements**: Si la vérification du build est réussie, poussez vos commits et tags vers le dépôt distant.
    ```bash
    git push --follow-tags
    ```

## Vérification de l'Intégrité du Build (`.whl`)

Pour éviter de distribuer des packages incomplets, il est crucial de s'assurer que tous les fichiers nécessaires (y compris les fichiers de configuration, les données, etc.) sont inclus dans le fichier Wheel (`.whl`) généré par `poetry build`.

### Inclusion des fichiers dans le build

La configuration de ce qui est inclus se trouve dans `pyproject.toml`, sous la section `[tool.poetry]`.

1.  **Packages Python**: La directive `packages` indique à Poetry où trouver les packages Python. La configuration actuelle `packages = [{include = "ambulon", from = "src"}]` inclut correctement tout le code source du répertoire `src/ambulon`.

2.  **Autres fichiers**: Pour inclure des fichiers non-Python (comme des `.json`, `.md`, etc.), utilisez la directive `include`. Elle accepte une liste de chemins ou de motifs (globs).

    Votre `pyproject.toml` contient déjà :
    ```toml
    include = ["config/mcp-config.json"]
    ```

    Si vous avez besoin d'inclure d'autres fichiers ou des répertoires entiers, vous pouvez l'étendre. Par exemple, pour inclure tous les fichiers `.json` du répertoire `config` :
    ```toml
    include = ["config/**/*.json"]
    ```

### Vérifier le contenu du fichier Wheel

Après avoir généré le build avec `poetry build`, vous pouvez inspecter son contenu pour vérifier que tout y est. Un fichier `.whl` est une archive zip.

Utilisez la commande suivante pour lister le contenu du fichier Wheel sans l'extraire :

```bash
# Assurez-vous d'activer l'environnement virtuel (poetry shell)
python -m zipfile -l dist/*.whl
```

Cette commande affichera la liste de tous les fichiers embarqués dans la distribution. Vérifiez méticuleusement cette liste pour confirmer la présence de tous vos fichiers de configuration, données, et assets nécessaires au bon fonctionnement de l'application.

Si un fichier manque, ajustez la directive `include` dans votre `pyproject.toml`, reconstruisez avec `poetry build`, et vérifiez à nouveau.

### Stratégie de Vérification des Dépendances de Modules

Pour garantir qu'aucun module ne manque de ses composants nécessaires (fichiers de configuration, données, assets), il est recommandé d'adopter une stratégie de vérification en plusieurs étapes :

1.  **Analyse Statique Manuelle**: Pour chaque module, le développeur doit identifier et lister tous les fichiers externes qu'il utilise. Par exemple, si `ambulon/ocr.py` charge un fichier de configuration ou des données d'entraînement, ces fichiers doivent être notés.

2.  **Configuration de l'Inclusion**: Assurez-vous que chaque fichier identifié à l'étape 1 est bien couvert par la directive `include` dans votre `pyproject.toml`. Utilisez des motifs glob (ex: `config/**/*.json`) pour inclure des groupes de fichiers de manière fiable.

3.  **Tests d'Intégration**: Créez des tests qui exercent spécifiquement les fonctionnalités qui dépendent de ces fichiers externes. L'exécution réussie de ces tests après une installation propre (`poetry install`) est la meilleure validation que les dépendances (code et fichiers) sont correctement gérées.

4.  **Vérification Post-Build**: Après chaque `poetry build`, utilisez la commande `python -m zipfile -l dist/*.whl` pour confirmer que les fichiers identifiés à l'étape 1 sont bien présents dans l'archive finale. C'est votre filet de sécurité final avant la distribution.

En combinant l'analyse du code, une configuration `pyproject.toml` explicite, des tests robustes et une inspection finale du livrable, vous réduirez considérablement le risque de distribuer un package incomplet.

## Hooks Claude Code

Ce projet utilise des **hooks Claude Code** pour automatiser certaines vérifications et afficher des informations visuelles avec des icônes personnalisées pendant le développement avec Claude.

### Qu'est-ce qu'un Hook Claude Code ?

Les hooks Claude Code sont des commandes shell qui s'exécutent automatiquement à différents moments du cycle de vie de Claude (avant/après l'exécution d'outils, au démarrage de session, etc.). Ils permettent de :

- Afficher des notifications visuelles avec des icônes
- Protéger des fichiers sensibles contre les modifications
- Valider automatiquement le code
- Logger les actions de Claude

### Hooks Configurés dans ce Projet

Le projet utilise 3 hooks Python principaux, tous situés dans `.claude/hooks/` :

#### 1. Event Logger (`event_logger.py`)

Affiche des icônes personnalisées pour chaque type d'événement Claude :

| Événement | Icône | Description |
|-----------|-------|-------------|
| PreToolUse | 🔍 | Avant l'exécution d'un outil |
| PostToolUse | ✅ | Après l'exécution d'un outil |
| PermissionRequest | 🔐 | Demande d'autorisation |
| Notification | 💬 | Notification générale |
| UserPromptSubmit | 📝 | Soumission d'un prompt utilisateur |
| Stop | ⛔ | Fin de réponse de Claude |
| SubagentStop | 🤖 | Fin d'exécution d'un sous-agent |
| SessionStart | 🚀 | Démarrage de session |
| SessionEnd | 👋 | Fin de session |
| PreCompact | 🗜️ | Compactage de conversation |

**Exemple de sortie :**
```
🔍 [PRE-EXECUTION] Préparation: Edit
   📄 Fichier: src/ambulon/ocr.py
```

#### 2. Protection des Fichiers Sensibles (`protect_sensitive_files.py`)

Bloque automatiquement toute tentative de modification de fichiers sensibles :

- Fichiers `.env`, `.secret`, `.key`, `.pem`
- Fichiers de lock : `poetry.lock`, `package-lock.json`, `yarn.lock`
- Configuration Git : `.git/config`
- Fichiers contenant "credentials"
- Répertoire `.ssh/`

**Exemple de sortie :**
```
🔒 [PROTECTION] Fichier sensible détecté: .env
⛔ Opération bloquée pour des raisons de sécurité
```

#### 3. Validateur Python (`python_validator.py`)

Vérifie automatiquement la syntaxe Python après chaque modification de fichier `.py` :

**Exemple de sortie :**
```
🐍 [PYTHON-CHECK] Vérification de la syntaxe Python
   📄 Fichier: src/app/ocr/ocr.py
   ✅ Syntaxe Python valide
```

### Configuration des Hooks

La configuration se trouve dans `.claude/settings.json`. Voici la structure actuelle :

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protect_sensitive_files.py",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/python_validator.py",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/event_logger.py",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/event_logger.py",
            "timeout": 5
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/event_logger.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### Personnalisation des Hooks

Pour personnaliser les hooks :

1. **Modifier un hook existant** : Éditez le fichier Python correspondant dans `.claude/hooks/`
2. **Ajouter un nouveau hook** :
   - Créez un nouveau script Python dans `.claude/hooks/`
   - Ajoutez-le dans `.claude/settings.json` en spécifiant l'événement et le matcher approprié
3. **Désactiver un hook** : Commentez ou supprimez la section correspondante dans `.claude/settings.json`

### Matchers (Filtres d'Outils)

Les matchers permettent de cibler des outils spécifiques :

| Pattern | Cible |
|---------|-------|
| `*` ou `""` | Tous les outils |
| `Edit\|Write` | Les outils Edit OU Write (regex) |
| `Bash` | Seulement les commandes Bash |
| `Read` | Seulement l'outil Read |
| `Task` | Seulement l'outil Task |

### Codes de Sortie

Les hooks utilisent des codes de sortie pour contrôler le comportement de Claude :

- **Code 0** : Succès, la sortie stdout est affichée
- **Code 2** : Erreur bloquante, l'action est annulée
- **Autre code** : Erreur non-bloquante, affichée en mode verbose

### Sécurité

⚠️ **Points de vigilance** :

- Les hooks s'exécutent automatiquement avec vos permissions
- Toujours vérifier le code avant d'ajouter un hook
- Ne jamais exposer de secrets ou tokens dans les hooks
- Utiliser `$CLAUDE_PROJECT_DIR` pour les chemins relatifs au projet

### Commandes Utiles

**Gérer les hooks via CLI :**
```bash
/hooks
```

Cela ouvre un menu interactif pour configurer les hooks.

**Voir la documentation complète :**
- Guide des hooks : https://code.claude.com/docs/en/hooks-guide.md
- Référence complète : https://code.claude.com/docs/en/hooks.md
