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

## Hiérarchie de Configuration

### 🚨 RÈGLE OBLIGATOIRE DU PROJET

**TOUS les modules, commandes et fonctionnalités du projet Ambulon DOIVENT impérativement respecter la hiérarchie de configuration standardisée définie ci-dessous.**

Cette règle s'applique à :
- ✅ Toutes les nouvelles commandes CLI
- ✅ Tous les nouveaux modules (app/*)
- ✅ Toutes les modifications de commandes existantes
- ✅ Toutes les intégrations d'API externes
- ✅ Toute fonctionnalité nécessitant une configuration

**Aucune exception n'est autorisée sans validation explicite dans les issues du projet.**

### Principe de la Hiérarchie (LOI DU PROJET)

La configuration **DOIT** suivre cet ordre de priorité décroissant, du plus spécifique au plus général :

1. **Arguments CLI** - Priorité la plus haute (OBLIGATOIRE)
2. **Fichier YAML** - Configuration structurée (OBLIGATOIRE)
3. **Variables d'environnement** - Configuration système (OBLIGATOIRE)
4. **Valeurs par défaut** - Priorité la plus basse (OBLIGATOIRE)

**Règle d'écrasement :** Chaque niveau **DOIT** écraser les niveaux inférieurs. Par exemple, un argument CLI écrasera la valeur correspondante dans le fichier YAML, les variables d'environnement et les valeurs par défaut.

### ❌ Anti-Patterns Interdits

Les pratiques suivantes sont **STRICTEMENT INTERDITES** :

```python
# ❌ INTERDIT : Configuration uniquement par arguments CLI
def my_command(url: str, output: str):
    # Pas de support YAML ni variables d'env
    pass

# ❌ INTERDIT : Priorité inversée (YAML écrase CLI)
config = load_yaml()
if cli_arg:
    config['url'] = cli_arg  # FAUX : CLI devrait avoir priorité absolue

# ❌ INTERDIT : Variables d'env non supportées
def my_command(url: str):
    # Impossible de configurer via WIKISI_URL
    pass

# ❌ INTERDIT : Pas de valeurs par défaut
def my_command(url: str = None):
    if url is None:
        raise ValueError("URL required")  # FAUX : doit avoir un défaut
```

### ✅ Pattern Obligatoire

**TOUS les nouveaux modules DOIVENT utiliser ce pattern :**

```python
def my_command(
    url: Optional[str] = None,
    output_dir: Optional[str] = None,
    config_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Ma commande avec hiérarchie de configuration complète.

    Hiérarchie (du plus au moins prioritaire) :
    1. Arguments CLI (url, output_dir, etc.)
    2. Fichier YAML (config_path)
    3. Variables d'environnement (MY_MODULE_URL, MY_MODULE_OUTPUT_DIR)
    4. Valeurs par défaut
    """
    # 1. Charger configuration (YAML + ENV + Defaults)
    config = load_config(config_path)

    # 2. Appliquer arguments CLI (priorité maximale)
    if url is not None:
        config['url'] = url
    if output_dir is not None:
        config['output_dir'] = output_dir

    # 3. Valider que toutes les valeurs requises sont présentes
    if not config.get('url'):
        print("Error: URL required (via --url, config file, or MY_MODULE_URL)", file=sys.stderr)
        return 1

    # 4. Exécuter la logique métier
    return execute_business_logic(config)
```

### Exemple d'Implémentation

#### 1. Fichier de Configuration YAML

Les fichiers YAML supportent la substitution de variables d'environnement avec la syntaxe `${VAR_NAME:-default_value}`.

**Exemple : `config/wikisi.yaml`**
```yaml
site:
  # URL de base - peut être définie par variable d'environnement
  base_url: "${WIKISI_BASE_URL:-https://wikisi.example.gouv.fr}"
  max_depth: -1
  timeout: 30

authentication:
  type: "${WIKISI_AUTH_TYPE:-none}"
  username: "${WIKISI_USERNAME:-}"
  token: "${WIKISI_TOKEN:-}"

output:
  directory: "./wikisi-downloaded"
```

#### 2. Variables d'Environnement

Les variables d'environnement permettent de configurer l'application sans modifier les fichiers :

```bash
# Définir les variables pour une session
export WIKISI_BASE_URL="https://wikisi.production.fr"
export WIKISI_AUTH_TYPE="bearer"
export WIKISI_TOKEN="eyJhbGc..."

# Lancer la commande (utilise les variables d'environnement)
ambulon wikisi-scrape
```

#### 3. Arguments CLI

Les arguments CLI ont toujours la priorité la plus haute :

```bash
# Les arguments écrasent YAML et variables d'environnement
ambulon wikisi-scrape \
    --url https://wikisi.dev.fr \
    --output ./data \
    --depth 5 \
    --verbose
```

### Ordre de Résolution - Exemple Complet

Pour un paramètre `base_url`, le système recherche dans cet ordre :

```python
def get_base_url(cli_arg, config_dict, env_vars, defaults):
    # 1. Argument CLI (priorité maximale)
    if cli_arg is not None:
        return cli_arg

    # 2. Fichier YAML (avec substitution de variables d'env)
    if 'base_url' in config_dict:
        yaml_value = config_dict['base_url']
        # Substitution ${VAR:-default}
        return substitute_env_vars(yaml_value)

    # 3. Variable d'environnement directe
    if 'WIKISI_BASE_URL' in env_vars:
        return env_vars['WIKISI_BASE_URL']

    # 4. Valeur par défaut (priorité minimale)
    return defaults.get('base_url', 'https://default.example.fr')
```

### Modules Utilisant Cette Hiérarchie

Cette hiérarchie est implémentée dans :

- **Module WikiSI** (`app/wikisi/`)
  - `wikisi-scrape` : Aspiration de site web
  - Configuration : `config/wikisi.yaml`
  - Variables : `WIKISI_*`

- **Module PIAG** (`app/piag/`)
  - Toutes les commandes RAG
  - Configuration : `config/piag.yaml`
  - Variables : `PIAG_RAG_*`

- **Module GitLab** (`app/gitlab/`)
  - `gitlab-clone` : Clonage de projets
  - Configuration : `config/gitlab.yaml`
  - Variables : `GITLAB_*`

### Obligations de Documentation

#### 1. Documentation dans --help (OBLIGATOIRE)

**Chaque commande DOIT impérativement documenter sa hiérarchie de configuration dans son aide (`--help`).**

**Format obligatoire :**

```bash
ambulon my-command --help

Usage: ambulon my-command [OPTIONS]

Description de la commande...

Options:
  -u, --url URL         URL à traiter
  -o, --output DIR      Répertoire de sortie
  -c, --config FILE     Fichier de configuration YAML
  -v, --verbose         Mode verbeux
  -h, --help            Afficher cette aide

Hiérarchie de configuration (priorité décroissante):
  1. Arguments CLI (--url, --output, etc.)
  2. Fichier YAML (--config)
  3. Variables d'environnement (MY_MODULE_*)
  4. Valeurs par défaut

Variables d'environnement supportées:
  MY_MODULE_URL         URL à traiter
  MY_MODULE_OUTPUT_DIR  Répertoire de sortie
  MY_MODULE_TIMEOUT     Timeout en secondes
  MY_MODULE_TOKEN       Token d'authentification

Exemples:
  # Via arguments CLI
  ambulon my-command --url https://example.com --output ./data

  # Via variables d'environnement
  MY_MODULE_URL=https://example.com ambulon my-command

  # Via fichier de configuration
  ambulon my-command --config config/my-module.yaml
```

**❌ L'absence de cette documentation dans --help est considérée comme une non-conformité bloquante.**

#### 2. Fichiers de Configuration (OBLIGATOIRE)

**Pour chaque nouveau module, vous DEVEZ créer deux fichiers de configuration :**

1. **`config/mon-module.yaml.example`** (VERSIONNÉ dans Git)
   - Template avec toutes les options documentées
   - Valeurs d'exemple (pas de vrais tokens)
   - Commentaires explicatifs pour chaque section
   - Support de substitution ${VAR:-default}

2. **`config/mon-module.yaml`** (NON VERSIONNÉ, dans .gitignore)
   - Configuration réelle de l'utilisateur
   - Peut contenir des tokens/secrets
   - Créé par l'utilisateur en copiant le .example

**Format obligatoire du fichier .example :**

```yaml
# Configuration Mon Module - Example Template
# Copiez ce fichier vers mon-module.yaml et ajustez les valeurs

# Section principale
main:
  # URL de base (peut être définie par variable d'environnement)
  url: "${MY_MODULE_URL:-https://default.example.com}"

  # Timeout en secondes
  timeout: 30

# Authentification
authentication:
  # Type: "none", "basic", "bearer"
  type: "${MY_MODULE_AUTH_TYPE:-none}"

  # Token (⚠️ NE JAMAIS commiter de vrais tokens)
  token: "${MY_MODULE_TOKEN:-}"

# Sortie
output:
  directory: "./output"
  format: "json"
```

**❌ Ne JAMAIS commiter de tokens ou secrets dans les fichiers .example**

#### 3. Sécurité des Tokens (OBLIGATOIRE)

**Règles de sécurité strictes :**

- ✅ **OBLIGATOIRE** : Utiliser des variables d'environnement pour les tokens/secrets
- ✅ **OBLIGATOIRE** : Tous les `config/*.yaml` (sauf `*.example`) DOIVENT être dans `.gitignore`
- ✅ **OBLIGATOIRE** : Les fichiers `.example` ne doivent contenir QUE des exemples (jamais de vrais tokens)
- ❌ **INTERDIT** : Commiter des tokens/secrets dans le dépôt Git
- ❌ **INTERDIT** : Hardcoder des tokens dans le code Python
- ❌ **INTERDIT** : Afficher des tokens en clair dans les logs (même en mode verbose)

#### 4. Substitution de Variables dans YAML (OBLIGATOIRE)

**Tous les fichiers YAML DOIVENT supporter la substitution de variables d'environnement.**

**Syntaxe obligatoire :**

```yaml
# Variable avec valeur par défaut (RECOMMANDÉ)
url: "${API_URL:-https://default.example.fr}"

# Variable sans défaut (chaîne vide si non définie)
token: "${API_TOKEN:-}"

# Variable obligatoire (génère une erreur si non définie) - À utiliser avec parcimonie
project_id: "${PROJECT_ID}"  # Pas de ":-"
```

**Implémentation obligatoire dans `load_config()` :**

```python
import re
import os

def replace_env_var(match):
    """Remplace ${VAR:-default} par la valeur de la variable d'environnement."""
    var_expr = match.group(1)
    if ':-' in var_expr:
        var_name, default_value = var_expr.split(':-', 1)
        return os.getenv(var_name, default_value)
    else:
        # Variable sans défaut - DOIT exister
        var_name = var_expr
        value = os.getenv(var_name)
        if value is None:
            raise ValueError(f"Variable d'environnement requise non définie: {var_name}")
        return value

# Appliquer la substitution
yaml_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, yaml_content)
```

#### 5. Nommage des Variables d'Environnement (OBLIGATOIRE)

**Convention de nommage stricte :**

```
{MODULE}_{SECTION}_{PARAMETRE}
```

**Règles obligatoires :**
- ✅ Tout en MAJUSCULES
- ✅ Séparation par underscore (_)
- ✅ Préfixe = nom du module
- ✅ Noms explicites et descriptifs
- ❌ Pas d'abréviations obscures
- ❌ Pas de tirets (-)
- ❌ Pas de caractères spéciaux

**Exemples conformes :**
```bash
# Module WikiSI
WIKISI_BASE_URL
WIKISI_AUTH_TYPE
WIKISI_OUTPUT_DIR
WIKISI_MAX_DEPTH
WIKISI_TOKEN

# Module PIAG
PIAG_RAG_API_TOKEN
PIAG_RAG_PROJECT_ID
PIAG_RAG_BASE_URL

# Module GitLab
GITLAB_PRIVATE_TOKEN
GITLAB_BASE_URL
GITLAB_GROUP_ID
```

**❌ Exemples NON conformes :**
```bash
# Mauvais : minuscules
wikisi_url

# Mauvais : tirets
WIKISI-BASE-URL

# Mauvais : pas de préfixe module
BASE_URL

# Mauvais : abréviation obscure
WIKISI_BU
```

### Exemple de Code - Fonction de Chargement de Config

```python
import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(
    config_path: Optional[str] = None,
    default_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Charge la configuration avec hiérarchie : CLI > YAML > ENV > Défaut.

    Args:
        config_path: Chemin vers fichier YAML (optionnel)
        default_config: Configuration par défaut

    Returns:
        Configuration fusionnée
    """
    # Valeurs par défaut
    config = default_config or {}

    # Charger YAML si spécifié
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()

        # Substitution des variables d'environnement
        def replace_env_var(match):
            var_expr = match.group(1)
            if ':-' in var_expr:
                var_name, default = var_expr.split(':-', 1)
                return os.getenv(var_name, default)
            return os.getenv(var_expr, '')

        yaml_content = re.sub(r'\$\{([^}]+)\}', replace_env_var, yaml_content)
        yaml_config = yaml.safe_load(yaml_content)

        # Fusionner avec défauts
        config = deep_merge(config, yaml_config)

    # Les arguments CLI sont appliqués par le code appelant
    return config

def deep_merge(base: Dict, override: Dict) -> Dict:
    """Fusionne récursivement deux dictionnaires."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
```

### ✅ Checklist de Conformité (OBLIGATOIRE avant commit)

**Avant CHAQUE commit ajoutant/modifiant une commande ou un module, vérifier :**

#### Configuration
- [ ] La commande supporte les 4 niveaux de hiérarchie (CLI > YAML > ENV > Defaults)
- [ ] Fichier `config/mon-module.yaml.example` créé et versionné
- [ ] Fichier `config/mon-module.yaml` dans `.gitignore`
- [ ] Substitution de variables d'env ${VAR:-default} implémentée dans YAML
- [ ] Fonction `load_config()` implémentée avec fusion des sources
- [ ] Arguments CLI écrasent bien YAML/ENV (priorité correcte)

#### Documentation
- [ ] `--help` documente la hiérarchie de configuration
- [ ] Toutes les variables d'environnement listées dans `--help`
- [ ] Au moins 3 exemples d'utilisation fournis (CLI, ENV, YAML)
- [ ] Nommage des variables d'env conforme ({MODULE}_{SECTION}_{PARAM})
- [ ] README.md mis à jour avec la nouvelle commande
- [ ] CHANGELOG.md mis à jour

#### Sécurité
- [ ] Aucun token/secret hardcodé dans le code
- [ ] Fichiers `.example` ne contiennent que des exemples (pas de vrais tokens)
- [ ] Tous les `config/*.yaml` (sauf `*.example`) dans `.gitignore`
- [ ] Tokens jamais affichés en clair dans les logs

#### Tests
- [ ] Tests unitaires pour `load_config()` avec différentes sources
- [ ] Tests pour chaque niveau de la hiérarchie
- [ ] Tests de sécurité (tokens non affichés)
- [ ] Couverture ≥ 80% pour le nouveau code

#### Code
- [ ] Pattern obligatoire respecté (voir section "Pattern Obligatoire")
- [ ] Pas d'anti-patterns présents
- [ ] Type hints utilisés (`Optional[str]`, etc.)
- [ ] Docstring avec hiérarchie documentée

**❌ Un commit ne respectant pas cette checklist sera considéré comme non conforme et devra être corrigé.**

### Résumé des Avantages

- **Flexibilité** : Adapter la configuration selon le contexte (dev/prod/CI)
- **Sécurité** : Secrets dans variables d'env, jamais dans le code
- **Cohérence** : Même hiérarchie pour tous les modules (LOI DU PROJET)
- **Transparence** : Comportement prévisible et documenté
- **Testabilité** : Facile à configurer pour les tests automatisés
- **Maintenabilité** : Pattern standard reconnaissable immédiatement

## Tests et Couverture de Code

### 🚨 RÈGLE OBLIGATOIRE - TESTS

**TOUS les nouveaux modules, commandes et fonctionnalités DOIVENT être couverts par des tests.**

**Cette règle s'applique à :**
- ✅ Toute nouvelle fonctionnalité (feature)
- ✅ Toute correction de bug (fix)
- ✅ Toute modification de code existant (refactor)
- ✅ Toute nouvelle intégration d'API

**Aucun code ne peut être mergé sans tests appropriés.**

### Objectifs de Couverture (OBLIGATOIRES)

- **Couverture minimale** : 80% du code DOIT être couvert par des tests
- **Couverture cible** : 90% ou plus pour le code critique (core/, client.py, config.py)
- **Code critique** : 100% pour les fonctions de sécurité, authentification et gestion des erreurs

**❌ Tout pull request avec une couverture < 80% sera automatiquement rejeté.**

### Obligations Spécifiques

#### Pour la Hiérarchie de Configuration (OBLIGATOIRE)

**Chaque module implémentant la hiérarchie de configuration DOIT avoir des tests pour :**

1. **Arguments CLI prioritaires** :
   ```python
   def test_cli_args_override_all():
       """Test que les arguments CLI écrasent YAML, ENV et defaults."""
       # Setup
       os.environ['MY_MODULE_URL'] = 'https://from-env.com'
       config_file = create_yaml({'url': 'https://from-yaml.com'})

       # Execute
       result = my_command(
           url='https://from-cli.com',  # CLI arg
           config_path=config_file
       )

       # Assert - CLI doit gagner
       assert 'https://from-cli.com' in result
   ```

2. **Fichier YAML écrase ENV** :
   ```python
   def test_yaml_overrides_env():
       """Test que YAML écrase les variables d'environnement."""
       os.environ['MY_MODULE_URL'] = 'https://from-env.com'
       config_file = create_yaml({'url': 'https://from-yaml.com'})

       result = my_command(config_path=config_file)

       assert 'https://from-yaml.com' in result
   ```

3. **Variables d'env écrasent defaults** :
   ```python
   def test_env_overrides_defaults():
       """Test que ENV écrase les valeurs par défaut."""
       os.environ['MY_MODULE_URL'] = 'https://from-env.com'

       result = my_command()  # Pas de CLI ni YAML

       assert 'https://from-env.com' in result
   ```

4. **Defaults utilisés si rien d'autre** :
   ```python
   def test_uses_defaults_when_no_config():
       """Test que les defaults sont utilisés en dernier recours."""
       # Aucune config fournie
       result = my_command()

       # Doit utiliser la valeur par défaut
       assert 'https://default.example.com' in result
   ```

**❌ L'absence de ces 4 tests pour un nouveau module est bloquante.**

### Structure des Tests

Le projet utilise `pytest` comme framework de tests principal :

```
tests/
├── unit/                    # Tests unitaires (logique métier isolée)
│   ├── test_piag/
│   │   ├── test_config.py
│   │   ├── test_client.py
│   │   └── test_collections.py
│   ├── test_wikisi/
│   │   ├── test_scraper.py
│   │   ├── test_extract.py
│   │   └── test_flatten.py
│   └── test_conversion/
│       ├── test_html2md.py
│       └── test_pdf.py
├── integration/             # Tests d'intégration (modules combinés)
│   ├── test_piag_workflow.py
│   ├── test_wikisi_pipeline.py
│   └── test_cli_integration.py
├── e2e/                     # Tests end-to-end (scénarios complets)
│   ├── test_piag_e2e.py
│   └── test_wikisi_e2e.py
├── fixtures/                # Données de test réutilisables
│   ├── sample_data.json
│   ├── mock_responses.py
│   └── test_config.yaml
└── conftest.py             # Configuration pytest globale
```

### Types de Tests

#### 1. Tests Unitaires (`tests/unit/`)

Testent des fonctions et classes isolées, sans dépendances externes :

```python
# tests/unit/test_wikisi/test_extract.py
import pytest
from app.wikisi.commands.wikisi_extract_json import parse_range_spec

def test_parse_range_spec_simple():
    """Test simple range parsing."""
    result = parse_range_spec("1-3", 10)
    assert result == [0, 1, 2]

def test_parse_range_spec_last_n():
    """Test last N elements range."""
    result = parse_range_spec("-5", 10)
    assert result == [5, 6, 7, 8, 9]

def test_parse_range_spec_from_n():
    """Test from N to end range."""
    result = parse_range_spec("7-", 10)
    assert result == [6, 7, 8, 9]

def test_parse_range_spec_invalid():
    """Test invalid range handling."""
    with pytest.raises(ValueError):
        parse_range_spec("invalid", 10)
```

**Caractéristiques** :
- Tests rapides (< 1ms par test)
- Pas de réseau, fichiers, ou base de données
- Utilisent des mocks pour les dépendances
- Testent les cas nominaux ET les cas d'erreur

#### 2. Tests d'Intégration (`tests/integration/`)

Testent l'interaction entre plusieurs modules :

```python
# tests/integration/test_wikisi_pipeline.py
import pytest
from pathlib import Path
from app.wikisi import process_parkjson2json, process_parkjson2md

def test_json_to_markdown_pipeline(tmp_path):
    """Test complete JSON extraction -> Markdown conversion pipeline."""
    # Setup
    input_json = tmp_path / "input.json"
    filtered_json = tmp_path / "filtered.json"
    output_md = tmp_path / "output.md"

    # Create test data
    test_data = {
        "applications": [
            {"nom": "App1", "description": "Test app 1"},
            {"nom": "App2", "description": "Test app 2"}
        ]
    }
    input_json.write_text(json.dumps(test_data))

    # Step 1: Extract/filter JSON
    result = process_parkjson2json(
        str(input_json),
        str(filtered_json),
        verbose=False,
        range_spec="1-1"
    )
    assert result == 0
    assert filtered_json.exists()

    # Step 2: Convert to Markdown
    result = process_parkjson2md(
        str(filtered_json),
        str(output_md),
        verbose=False
    )
    assert result == 0
    assert output_md.exists()

    # Verify output
    md_content = output_md.read_text()
    assert "# App1" in md_content
    assert "App2" not in md_content  # Filtered out
```

**Caractéristiques** :
- Tests moyennement rapides (< 100ms par test)
- Utilisent des fichiers temporaires (`tmp_path`)
- Mockent les API externes
- Testent les flux de données entre modules

#### 3. Tests End-to-End (`tests/e2e/`)

Testent des scénarios utilisateur complets, incluant CLI :

```python
# tests/e2e/test_wikisi_e2e.py
import pytest
import subprocess
from pathlib import Path

def test_wikisi_scrape_full_workflow(tmp_path):
    """Test complete WikiSI scraping workflow via CLI."""
    output_dir = tmp_path / "scraped"

    # Run CLI command
    result = subprocess.run(
        [
            "ambulon", "wikisi-scrape",
            "--url", "https://example.com",
            "--output", str(output_dir),
            "--depth", "1"
        ],
        capture_output=True,
        text=True
    )

    # Verify success
    assert result.returncode == 0
    assert output_dir.exists()
    assert (output_dir / "index.html").exists()
    assert (output_dir / "scrape_metadata.json").exists()
```

**Caractéristiques** :
- Tests lents (> 100ms, parfois plusieurs secondes)
- Testent l'application comme un utilisateur réel
- Peuvent utiliser des services externes (avec mocks optionnels)
- Validés en environnement de pré-production

### Bonnes Pratiques de Tests

#### 1. Utiliser des Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_wikisi_json():
    """Fixture providing sample WikiSI JSON data."""
    return {
        "applications": [
            {
                "nom": "Application Test",
                "id": "APP001",
                "description": "Application de test"
            }
        ]
    }

@pytest.fixture
def temp_config(tmp_path):
    """Fixture providing temporary config file."""
    config = tmp_path / "config.yaml"
    config.write_text("""
    site:
      base_url: "https://test.example.com"
      max_depth: 2
    """)
    return config
```

#### 2. Mocker les Dépendances Externes

```python
# tests/unit/test_wikisi/test_scraper.py
import pytest
from unittest.mock import Mock, patch
from app.wikisi.commands.wikisi_scraper import WikiSIScraper

@patch('app.wikisi.commands.wikisi_scraper.requests.Session')
def test_scraper_fetch_page(mock_session, sample_config):
    """Test page fetching with mocked HTTP."""
    # Setup mock
    mock_response = Mock()
    mock_response.text = "<html><body>Test</body></html>"
    mock_response.status_code = 200
    mock_session.return_value.get.return_value = mock_response

    # Test
    scraper = WikiSIScraper(sample_config)
    content = scraper._fetch_page("https://test.example.com")

    # Verify
    assert "Test" in content
    mock_session.return_value.get.assert_called_once()
```

#### 3. Tester les Cas d'Erreur

```python
def test_scraper_handles_network_error():
    """Test scraper gracefully handles network errors."""
    with patch('requests.Session.get', side_effect=requests.ConnectionError):
        scraper = WikiSIScraper(config)
        result = scraper.scrape()

        assert result['pages_failed'] > 0
        assert result['pages_downloaded'] == 0
```

#### 4. Tests Paramétrés

```python
@pytest.mark.parametrize("range_spec,total,expected", [
    ("1-3", 10, [0, 1, 2]),
    ("-5", 10, [5, 6, 7, 8, 9]),
    ("7-", 10, [6, 7, 8, 9]),
    ("1,3,5", 10, [0, 2, 4]),
])
def test_parse_range_variants(range_spec, total, expected):
    """Test multiple range specification variants."""
    result = parse_range_spec(range_spec, total)
    assert result == expected
```

### Exécution des Tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests avec couverture
pytest --cov=app --cov-report=html

# Tests avec détails
pytest -v

# Tests d'un module spécifique
pytest tests/unit/test_wikisi/

# Tests avec rapport de couverture
pytest --cov=app --cov-report=term-missing

# Tests en parallèle (plus rapide)
pytest -n auto
```

### Intégration Continue (CI)

Les tests doivent s'exécuter automatiquement dans la CI :

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: poetry install

      - name: Run tests with coverage
        run: |
          poetry run pytest --cov=app --cov-report=xml --cov-report=term

      - name: Check coverage threshold
        run: |
          poetry run coverage report --fail-under=80
```

### Couverture par Module - Objectifs

| Module | Couverture Minimale | Couverture Cible | Notes |
|--------|---------------------|------------------|-------|
| `app/piag/` | 85% | 95% | Module critique (API externe) |
| `app/wikisi/` | 80% | 90% | Web scraping complexe |
| `app/conversion/` | 80% | 90% | Transformations de données |
| `app/cli/` | 70% | 85% | CLI (testable via E2E) |
| `app/encoding/` | 90% | 95% | Manipulation encodage (critique) |

### Exclusions de Couverture

Certaines parties peuvent être exclues de la couverture :

```python
# .coveragerc
[run]
omit =
    tests/*
    */migrations/*
    */settings.py
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

### 🚨 Obligations Avant CHAQUE Commit (BLOQUANT)

**Avant CHAQUE commit, vous DEVEZ exécuter et vérifier :**

#### 1. Tous les tests passent (OBLIGATOIRE)
```bash
pytest
# Exit code DOIT être 0
```

**❌ Un commit avec des tests qui échouent est INTERDIT.**

#### 2. Couverture de code ≥ 80% (OBLIGATOIRE)
```bash
pytest --cov=app --cov-report=term
# Coverage DOIT afficher ≥ 80%
```

**❌ Un commit qui fait baisser la couverture globale sous 80% est INTERDIT.**

#### 3. Pas de régression de couverture (OBLIGATOIRE)
```bash
# Comparer avec la couverture précédente
pytest --cov=app --cov-report=term | grep "TOTAL"
```

**❌ Une baisse de couverture sur un module existant est INTERDITE (sauf justification documentée).**

#### 4. Tests pour nouvelles fonctionnalités (OBLIGATOIRE)

**Toute nouvelle fonctionnalité DOIT avoir :**
- [ ] Au moins 3 tests unitaires
- [ ] Au moins 1 test d'intégration
- [ ] Tests de la hiérarchie de configuration (si applicable)
- [ ] Tests des cas d'erreur

**❌ Une fonctionnalité sans tests ne peut PAS être commitée.**

#### 5. Checklist de Tests pour Modules de Configuration

Pour tout module implémentant la hiérarchie de configuration :

- [ ] Test CLI écrase tout
- [ ] Test YAML écrase ENV et defaults
- [ ] Test ENV écrase defaults
- [ ] Test defaults utilisés en dernier recours
- [ ] Test substitution de variables ${VAR:-default}
- [ ] Test gestion des tokens (non affichés dans logs)
- [ ] Test fichier config inexistant (utilise defaults)
- [ ] Test valeurs invalides (gestion d'erreur)

**❌ L'absence d'un seul de ces tests est bloquante.**

### Résumé des Règles de Tests

#### Règles OBLIGATOIRES (Non négociables)

1. ✅ **Écrire des tests** pour CHAQUE nouvelle fonctionnalité (LOI)
2. ✅ **Couverture ≥ 80%** pour TOUT le code (LOI)
3. ✅ **Hiérarchie de config testée** pour tous les modules configurables (LOI)
4. ✅ **Tests passent** avant CHAQUE commit (LOI)
5. ✅ **Pas de régression** de couverture tolérée (LOI)

#### Bonnes Pratiques (Fortement recommandées)

- **Utiliser des fixtures** pour éviter la duplication
- **Mocker les dépendances** externes (API, fichiers, réseau)
- **Tester les erreurs** autant que les cas nominaux
- **Tests paramétrés** pour tester plusieurs cas similaires
- **Intégrer dans la CI** pour validation automatique

#### Sanctions

- ❌ Commit sans tests → Rejeté systématiquement
- ❌ Couverture < 80% → Rejeté systématiquement
- ❌ Tests qui échouent → Rejeté systématiquement
- ❌ Régression non justifiée → Rejeté systématiquement
