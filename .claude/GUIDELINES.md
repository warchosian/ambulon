# Claude Code - Directives Générales de Développement

Ce fichier contient les **directives générales applicables à tous les projets Python** développés avec Claude Code.

---

## ⚠️🚨 INTERDICTION ABSOLUE - FRAMEWORK TYPER 🚨⚠️

### **NE JAMAIS UTILISER TYPER - TOUJOURS UTILISER ARGPARSE**

**Cette règle est NON NÉGOCIABLE et s'applique à TOUS les projets.**

### Pourquoi Typer est Interdit

**Typer a été complètement banni** suite à des problèmes récurrents et graves :

#### Problèmes Techniques Critiques

- ❌ **RuntimeWarning** avec `runpy.run_module`
- ❌ **Conflits** avec manipulation de `sys.argv`
- ❌ **"Got unexpected extra arguments"** errors imprévisibles
- ❌ **Complexité inutile** pour des cas d'usage CLI standards
- ❌ **Dépendances externes** non nécessaires
- ❌ **Debugging difficile** et comportements imprévisibles

#### Approche Déclarative vs Impérative : Le Problème Fondamental

**Typer utilise une approche déclarative basée sur les annotations Python**, ce qui a causé des problèmes majeurs d'interprétation et de fiabilité :

**❌ Approche Déclarative (Typer) - INTERDITE**

```python
# Typer : Déclaratif via annotations et décorateurs
import typer

app = typer.Typer()

@app.command()
def my_command(
    input_file: str = typer.Argument(..., help="Fichier d'entrée"),
    output: str = typer.Option(None, "--output", "-o", help="Fichier de sortie"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Mode verbeux")
):
    """Ma commande."""
    pass

# Problèmes constatés :
# - Interprétation des annotations non fiable (typer.Argument vs typer.Option)
# - Conflits lors de l'exécution via runpy.run_module
# - Magie implicite difficile à debugger
# - Comportement imprévisible avec sys.argv
# - Pas de contrôle sur le parsing des arguments
```

**Problèmes d'interprétation des annotations rencontrés :**
- Confusion entre `typer.Argument()` et `typer.Option()` selon le contexte
- Ordre des arguments mal interprété lors de l'appel
- Type hints Python natifs mal gérés par Typer
- Valeurs par défaut (`None`, `...`) créant des ambiguïtés
- Résolution dynamique au runtime source d'erreurs silencieuses

**✅ Approche Impérative (argparse) - OBLIGATOIRE**

```python
# argparse : Impératif, contrôle explicite
import argparse
import sys

def main(argv=None):
    """
    Point d'entrée avec contrôle total.

    Args:
        argv: Arguments CLI (list) ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(description="Ma commande")

    # Contrôle explicite : Argument positionnel
    parser.add_argument("input_file", help="Fichier d'entrée")

    # Contrôle explicite : Options
    parser.add_argument("-o", "--output", help="Fichier de sortie")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")

    args = parser.parse_args(argv)

    # Logique métier
    return process(args.input_file, args.output, args.verbose)

if __name__ == '__main__':
    sys.exit(main())

# Avantages :
# ✅ Parsing explicite et prévisible
# ✅ Pas d'interprétation magique d'annotations
# ✅ Contrôle total sur sys.argv
# ✅ Testable facilement (main(argv=[...]))
# ✅ Pas de dépendances externes
# ✅ Debugging simple et direct
```

**Pourquoi l'approche impérative est supérieure :**

1. **Prévisibilité** : Le code fait exactement ce qui est écrit, pas d'interprétation magique
2. **Contrôle** : Contrôle total sur le parsing, la validation, les messages d'erreur
3. **Testabilité** : `main(argv=["test.txt", "-v"])` fonctionne de manière déterministe
4. **Maintenabilité** : Facile à comprendre et modifier sans surprises
5. **Standard Python** : Bibliothèque standard, documentée, stable depuis Python 2.x
6. **Pas de surprises** : Comportement explicite documenté, pas de résolution dynamique

**Comparaison finale :**

| Aspect | Typer (Déclaratif) | argparse (Impératif) |
|--------|-------------------|----------------------|
| Interprétation | Annotations → Magie → Erreurs | Code explicite → Prévisible |
| Contrôle | Limité, implicite | Total, explicite |
| Debugging | Difficile (callstack complexe) | Simple (code direct) |
| Testabilité | Problématique (mocks requis) | Native (argv paramétrable) |
| Dépendances | Typer + Click + autres | stdlib uniquement |
| Fiabilité | Comportements imprévisibles | 100% stable |

**Verdict :** L'approche déclarative de Typer introduit une couche d'abstraction inutile qui masque la complexité au lieu de la simplifier. L'approche impérative d'argparse est plus verbeuse mais infiniment plus fiable et maintenable.

### Solution Obligatoire : argparse

**`argparse`** est la SEULE solution autorisée pour les CLI :

- ✅ **Bibliothèque standard** Python (pas de dépendances)
- ✅ **Stable** et largement documentée
- ✅ **Contrôle total** sur le parsing et la gestion des arguments
- ✅ **Testable** et prévisible
- ✅ **Support intégré** dans l'écosystème Python

### Pattern CLI Obligatoire

**TOUS les nouveaux modules CLI DOIVENT utiliser ce pattern :**

```python
import sys
import argparse
import logging
from pathlib import Path

def main(argv=None):
    """
    Point d'entrée de la commande.

    Args:
        argv: Arguments en ligne de commande (list), ou None pour utiliser sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        description="Description de la commande",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (from highest to lowest priority):
  1. Command-line arguments
  2. YAML configuration file (--config)
  3. Environment variables
  4. Default values
        """
    )

    # Arguments positionnels
    parser.add_argument("input", help="Fichier d'entrée")

    # Arguments optionnels
    parser.add_argument("-o", "--output", help="Fichier de sortie")
    parser.add_argument("-c", "--config", help="Fichier de configuration YAML")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
    parser.add_argument("-q", "--quiet", action="store_true", help="Mode silencieux")

    args = parser.parse_args(argv)

    # Configuration du logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="module_name")

    try:
        # Logique métier ici
        result = process_data(args.input, args.output)
        return 0
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

### Points Clés Obligatoires

- ✅ Fonction `main(argv=None)` pour testabilité
- ✅ Retour d'un code de sortie (0 ou 1)
- ✅ `if __name__ == '__main__': sys.exit(main())`
- ✅ Documentation de la hiérarchie de configuration dans `--help`
- ✅ Gestion d'exceptions avec logging
- ❌ **JAMAIS** de `import typer`
- ❌ **JAMAIS** de `raise typer.Exit()`
- ❌ **JAMAIS** de décorateurs `@app.command()`

### Sanctions

**Tout code utilisant Typer sera immédiatement rejeté, sans exception.**

---

## Gestion des Logs et Affichage Console

### Principe Général

Toute application doit utiliser un gestionnaire de logs centralisé pour l'affichage console et la persistance des erreurs.

### Affichage du Chemin des Fichiers Générés (OBLIGATOIRE)

**Toute commande générant un fichier en sortie DOIT afficher le chemin relatif de ce fichier à la fin de son exécution, dans un format cliquable par les terminaux modernes (ex: VS Code).**

#### Format d'Affichage Obligatoire

```
✓ <Opération> réussie !
Fichier produit : <chemin/relatif/vers/fichier.ext>
```

#### Implémentation Recommandée

Pour garantir la cliquabilité et la portabilité (Windows/Linux), utilisez `os.path.relpath`.

```python
import os
from pathlib import Path

# ... (votre logique de génération de fichier, output_path est un objet Path)

if output_path:
    try:
        relative_path = os.path.relpath(output_path)
    except ValueError:
        # Fallback si le chemin n'est pas relatif (ex: autre drive sur Windows)
        relative_path = output_path.resolve()

    print(f"\n✓ Conversion réussie !")
    print(f"Fichier produit : {relative_path}")
    return 0
else:
    # Gérer l'échec
    return 1
```

#### Règles d'Utilisation

1. **Chemin relatif** : Toujours afficher le chemin relatif par rapport au répertoire courant (`Path.cwd()`).
2. **Cliquable** : Le format doit être reconnu par le terminal de l'utilisateur comme un lien (souvent, un simple chemin sur sa propre ligne est suffisant).
3. **OS-agnostique** : `os.path.relpath` gère les séparateurs (`/` ou `\`) automatiquement.

### Configuration des Logs

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

### Règles d'Utilisation

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

### Exemple d'Implémentation

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
```

### Avantages

- **Traçabilité** : Tous les événements et erreurs sont enregistrés avec horodatage
- **Débogage** : Fichiers de logs consultables après exécution
- **Cohérence** : Format uniforme pour toutes les applications
- **Performance** : Rotation automatique pour éviter les fichiers trop volumineux

---

## Gestion des Dépendances Python avec Poetry

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

---

## Workflow des Branches Git

### Architecture des Branches (Option B - Production First)

Le projet Ambulon utilise une architecture de branches **orientée production** où `main` est strictement un miroir de la dernière version stable en production.

```
feature branches → preprod/vX.X.X-stable (validation & tests)
                        ↓
                   prod/vX.X.X-stable (production déployée)
                        ↓
                   main (= dernière version stable uniquement)
```

### Rôles des Branches

**1. Branches `feature/*`** - Développement de fonctionnalités
- Créées depuis la dernière `preprod` ou directement pour développement
- Nommage : `feature/<nom-descriptif>` (ex: `feature/gitlab-piag-v1`)
- Commits conventionnels requis
- Supprimées après merge dans preprod

**2. Branches `preprod/vX.X.X-stable`** - Pré-production
- **Rôle** : Validation, tests, stabilisation avant production
- **Contenu** : Code + package offline + documentation
- **Nommage** : `preprod/v3.0.2-stable` (version sémantique)
- **Lifecycle** :
  - Créée depuis feature branch avec nouvelle version
  - Tests et validations effectués
  - Une fois validée → création de `prod/vX.X.X-stable`
  - Conservée sur GitHub pour historique

**3. Branches `prod/vX.X.X-stable`** - Production
- **Rôle** : Version déployée en production, immuable
- **Contenu** : Exactement identique à preprod validée
- **Nommage** : `prod/v3.0.2-stable` (même version que preprod)
- **Lifecycle** :
  - Créée depuis `preprod/vX.X.X-stable` après validation complète
  - Ne reçoit JAMAIS de commits directs
  - Tagguée avec `vX.X.X`
  - Conservée indéfiniment sur GitHub

**4. Branche `main`** - Miroir de Production
- **Rôle** : Branche par défaut GitHub, reflète la dernière prod stable
- **Contenu** : Copie exacte de la dernière branche `prod/vX.X.X-stable`
- **MAJ** : Uniquement après création d'une branche prod
- **Interdiction** : NE JAMAIS développer directement sur `main`
- **Visiteurs GitHub** : Voient toujours la dernière version stable

### Workflow Complet de Release

**Étape 1 : Développement sur feature branch**
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ... développement ...
git add .
cz commit  # Commits conventionnels
git push origin feature/ma-nouvelle-fonctionnalite
```

**Étape 2 : Création de la branche preprod**
```bash
# Depuis la feature branch
cz bump  # Bump version (ex: 3.0.1 → 3.0.2)
poetry build  # Générer la wheel
python scripts/build_offline_package.py  # Générer package offline

git checkout -b preprod/v3.0.2-stable
git add dist/ dist-offline/ pyproject.toml src/app/__init__.py CHANGELOG.md
git commit -m "bump: version 3.0.1 → 3.0.2"
git tag -a 3.0.2 -m "Release v3.0.2"
git push origin preprod/v3.0.2-stable --tags
```

**Étape 3 : Validation en preprod**
- Tester l'installation offline
- Vérifier toutes les fonctionnalités
- Valider la documentation
- Tests d'intégration
- **SI problème** : fixer sur preprod, bumper en 3.0.3, recommencer
- **SI OK** : passer à l'étape 4

**Étape 4 : Promotion vers production**
```bash
# Créer la branche prod depuis preprod validée
git checkout preprod/v3.0.2-stable
git checkout -b prod/v3.0.2-stable
git push origin prod/v3.0.2-stable --tags

# Supprimer l'ancienne preprod sur GitHub (optionnel)
git push origin --delete preprod/v3.0.1-stable
```

**Étape 5 : Mise à jour de `main`** (UNIQUEMENT après prod)
```bash
# Mettre à jour main pour refléter la prod
git checkout main
git merge --ff-only prod/v3.0.2-stable  # Fast-forward uniquement
# OU
git reset --hard prod/v3.0.2-stable  # Force sync avec prod

git push origin main
```

### Règles Strictes

**✅ AUTORISÉ**
- Créer des feature branches pour développement
- Créer preprod depuis feature après version bump
- Créer prod depuis preprod validée
- Mettre à jour main depuis prod uniquement
- Conserver les branches preprod/prod sur GitHub

**❌ INTERDIT**
- Commiter directement sur `main`
- Créer prod sans passer par preprod
- Mettre à jour main avant création de prod
- Modifier une branche prod existante
- Pusher des secrets/tokens

### FAQ Workflow

**Q: Pourquoi ne pas développer sur `main` ?**
A: `main` est un miroir de production, pas une branche de développement. Cela évite confusion et commits accidentels.

**Q: Que faire si je trouve un bug en preprod ?**
A: Fixer sur preprod, bumper la version patch, recréer le package offline, retester.

**Q: Dois-je conserver toutes les branches preprod/prod ?**
A: Oui pour prod (historique des releases), optionnel pour preprod (on peut supprimer les anciennes).

**Q: Comment revenir à une version précédente ?**
A: Checkout de la branche `prod/vX.X.X-stable` correspondante, puis créer nouvelle preprod depuis là.

---

## Workflow de Versioning et de Release

Ce workflow suit le **Semantic Versioning (SemVer)** et utilise [Commitizen](https://commitizen-tool.github.io/commitizen/) pour automatiser la gestion des versions et la génération du changelog.

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
    python -m zipfile -l dist/package-x.y.z-py3-none-any.whl
    ```
    Si des fichiers manquent, retournez à la section "Vérification de l'Intégrité du Build" pour ajuster la configuration `pyproject.toml`, puis recommencez le build.

6.  **Vérification de l'Absence de Secrets** : **🚨 ÉTAPE CRITIQUE - Cette vérification est OBLIGATOIRE avant CHAQUE push vers GitHub/GitLab.**

    Avant de pousser vos changements, vous DEVEZ vérifier qu'aucun secret (tokens, API keys, project IDs, credentials) n'est présent dans les fichiers qui seront poussés.

    **Commandes de vérification obligatoires :**
    ```bash
    # 1. Vérifier les fichiers qui seront poussés
    git diff --staged
    git diff HEAD

    # 2. Rechercher des patterns de secrets dans les fichiers modifiés
    git diff HEAD | grep -i "token\|secret\|password\|api_key\|credential"

    # 3. Vérifier spécifiquement les fichiers de documentation
    grep -r "token\|secret\|password\|api_key\|project_id" doc/ --include="*.md"

    # 4. Vérifier les fichiers de configuration
    grep -r "token\|secret\|password\|api_key" config/ --include="*.yaml" --include="*.example"
    ```

    **⚠️ Si un secret est détecté :**
    - **NE PAS POUSSER** immédiatement
    - Remplacer les secrets par des placeholders (ex: `"VOTRE_TOKEN_ICI"`, `"your_project_id_here"`)
    - Amender le commit si nécessaire : `git commit --amend --no-edit`
    - Re-vérifier l'absence de secrets
    - Si un secret a déjà été poussé, considérer le secret comme compromis et le révoquer immédiatement

    **Checklist de sécurité :**
    - [ ] Aucun token JWT dans les fichiers
    - [ ] Aucun project_id réel dans la documentation
    - [ ] Aucun mot de passe dans les exemples
    - [ ] Les fichiers `.example` contiennent uniquement des placeholders
    - [ ] Les fichiers de config réels (`config/*.yaml`) sont dans `.gitignore`

7.  **Pousser les changements**: Si la vérification du build ET la vérification de l'absence de secrets sont réussies, poussez vos commits et tags vers le dépôt distant.
    ```bash
    git push --follow-tags
    ```

### Vérification de l'Intégrité du Build (`.whl`)

Pour éviter de distribuer des packages incomplets, il est crucial de s'assurer que tous les fichiers nécessaires (y compris les fichiers de configuration, les données, etc.) sont inclus dans le fichier Wheel (`.whl`) généré par `poetry build`.

#### Inclusion des Fichiers dans le Build

La configuration de ce qui est inclus se trouve dans `pyproject.toml`, sous la section `[tool.poetry]`.

1.  **Packages Python**: La directive `packages` indique à Poetry où trouver les packages Python.
    Exemple : `packages = [{include = "app", from = "src"}]`

2.  **Autres fichiers**: Pour inclure des fichiers non-Python (comme des `.json`, `.md`, etc.), utilisez la directive `include`. Elle accepte une liste de chemins ou de motifs (globs).

    Exemple :
    ```toml
    include = ["config/**/*.json"]
    ```

#### Vérifier le Contenu du Fichier Wheel

Après avoir généré le build avec `poetry build`, vous pouvez inspecter son contenu pour vérifier que tout y est. Un fichier `.whl` est une archive zip.

Utilisez la commande suivante pour lister le contenu du fichier Wheel sans l'extraire :

```bash
# Assurez-vous d'activer l'environnement virtuel (poetry shell)
python -m zipfile -l dist/*.whl
```

Cette commande affichera la liste de tous les fichiers embarqués dans la distribution. Vérifiez méticuleusement cette liste pour confirmer la présence de tous vos fichiers de configuration, données, et assets nécessaires au bon fonctionnement de l'application.

Si un fichier manque, ajustez la directive `include` dans votre `pyproject.toml`, reconstruisez avec `poetry build`, et vérifiez à nouveau.

---

## Hooks Claude Code

Les projets peuvent utiliser des **hooks Claude Code** pour automatiser certaines vérifications et afficher des informations visuelles avec des icônes personnalisées pendant le développement avec Claude.

### Qu'est-ce qu'un Hook Claude Code ?

Les hooks Claude Code sont des commandes shell qui s'exécutent automatiquement à différents moments du cycle de vie de Claude (avant/après l'exécution d'outils, au démarrage de session, etc.). Ils permettent de :

- Afficher des notifications visuelles avec des icônes
- Protéger des fichiers sensibles contre les modifications
- Valider automatiquement le code
- Logger les actions de Claude

### Exemples de Hooks Utiles

#### 1. Event Logger (`event_logger.py`)

Affiche des icônes personnalisées pour chaque type d'événement Claude :

| Événement | Icône | Description |
|-----------|-------|-------------|
| PreToolUse | 🔍 | Avant l'exécution d'un outil |
| PostToolUse | ✅ | Après l'exécution d'un outil |
| PermissionRequest | 🔐 | Demande d'autorisation |
| SessionStart | 🚀 | Démarrage de session |
| SessionEnd | 👋 | Fin de session |

#### 2. Protection des Fichiers Sensibles (`protect_sensitive_files.py`)

Bloque automatiquement toute tentative de modification de fichiers sensibles :

- Fichiers `.env`, `.secret`, `.key`, `.pem`
- Fichiers de lock : `poetry.lock`, `package-lock.json`, `yarn.lock`
- Configuration Git : `.git/config`
- Fichiers contenant "credentials"
- Répertoire `.ssh/`

#### 3. Validateur Python (`python_validator.py`)

Vérifie automatiquement la syntaxe Python après chaque modification de fichier `.py`.

### Configuration des Hooks

La configuration se trouve dans `.claude/settings.json` :

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
      }
    ]
  }
}
```

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

---

## Hiérarchie de Configuration

### 🚨 RÈGLE OBLIGATOIRE

**TOUS les modules CLI DOIVENT impérativement respecter la hiérarchie de configuration standardisée définie ci-dessous.**

Cette règle s'applique à :
- ✅ Toutes les nouvelles commandes CLI
- ✅ Tous les nouveaux modules
- ✅ Toutes les modifications de commandes existantes
- ✅ Toutes les intégrations d'API externes
- ✅ Toute fonctionnalité nécessitant une configuration

**Aucune exception n'est autorisée sans validation explicite.**

### Principe de la Hiérarchie (LOI)

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
    # Impossible de configurer via MODULE_URL
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

**Exemple : `config/module.yaml`**
```yaml
main:
  # URL de base - peut être définie par variable d'environnement
  base_url: "${MODULE_BASE_URL:-https://example.com}"
  timeout: 30

authentication:
  type: "${MODULE_AUTH_TYPE:-none}"
  token: "${MODULE_TOKEN:-}"

output:
  directory: "./output"
```

#### 2. Variables d'Environnement

Les variables d'environnement permettent de configurer l'application sans modifier les fichiers :

```bash
# Définir les variables pour une session
export MODULE_BASE_URL="https://production.example.com"
export MODULE_AUTH_TYPE="bearer"
export MODULE_TOKEN="eyJhbGc..."

# Lancer la commande (utilise les variables d'environnement)
my-app my-command
```

#### 3. Arguments CLI

Les arguments CLI ont toujours la priorité la plus haute :

```bash
# Les arguments écrasent YAML et variables d'environnement
my-app my-command \
    --url https://dev.example.com \
    --output ./data \
    --verbose
```

### Obligations de Documentation

#### 1. Documentation dans --help (OBLIGATOIRE)

**Chaque commande DOIT impérativement documenter sa hiérarchie de configuration dans son aide (`--help`).**

**Format obligatoire :**

```bash
my-app my-command --help

Usage: my-app my-command [OPTIONS]

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
  my-app my-command --url https://example.com --output ./data

  # Via variables d'environnement
  MY_MODULE_URL=https://example.com my-app my-command

  # Via fichier de configuration
  my-app my-command --config config/my-module.yaml
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

# Module API
API_BASE_URL
API_TIMEOUT
API_TOKEN
```

**❌ Exemples NON conformes :**
```bash
# Mauvais : minuscules
module_url

# Mauvais : tirets
MODULE-BASE-URL

# Mauvais : pas de préfixe module
BASE_URL

# Mauvais : abréviation obscure
MOD_BU
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
- **Cohérence** : Même hiérarchie pour tous les modules (LOI)
- **Transparence** : Comportement prévisible et documenté
- **Testabilité** : Facile à configurer pour les tests automatisés
- **Maintenabilité** : Pattern standard reconnaissable immédiatement

---

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

Utiliser `pytest` comme framework de tests principal :

```
tests/
├── unit/                    # Tests unitaires (logique métier isolée)
├── integration/             # Tests d'intégration (modules combinés)
├── e2e/                     # Tests end-to-end (scénarios complets)
├── fixtures/                # Données de test réutilisables
└── conftest.py             # Configuration pytest globale
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
