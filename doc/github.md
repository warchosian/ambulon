# GitHub Integration Module

Module d'intégration GitHub pour gérer les releases et opérations sur les dépôts.

## 📦 Architecture

```
src/app/github/
├── core/
│   ├── client.py           # Client API GitHub (wrapper requests)
│   ├── release_manager.py  # Gestion des releases (logique métier)
│   └── config.py          # Chargement config/github.yaml
├── commands/
│   └── github_release.py   # CLI: ambulon github-release
```

## 🚀 Commandes CLI

### **`ambulon github-release`** - Créer une release GitHub

Crée une release GitHub depuis un tag Git existant avec upload optionnel d'assets.

```bash
# Créer release depuis un tag
ambulon github-release --tag 3.5.0

# Avec titre et description personnalisés
ambulon github-release --tag 3.5.0 \
  --title "v3.5.0 - New Features" \
  --description "See CHANGELOG.md for details"

# Avec assets spécifiques
ambulon github-release --tag 3.5.0 \
  --asset dist/ambulon-3.5.0-py3-none-any.whl \
  --asset docs/manual.pdf

# Auto-détection de la wheel pour cette version
ambulon github-release --tag 3.5.0 --auto-wheel

# Créer un brouillon (draft)
ambulon github-release --tag 3.5.0 --draft

# Marquer comme pre-release (alpha, beta)
ambulon github-release --tag 3.5.0 --prerelease

# Description depuis un fichier
ambulon github-release --tag 3.5.0 --description-file RELEASE_NOTES.md

# Avec fichier de configuration
ambulon github-release --tag 3.5.0 -c config/github.yaml

# Spécifier repo et owner différents
ambulon github-release --tag 1.0.0 \
  --owner myorg --repo myproject
```

**Options :**
- `--tag TAG` : Nom du tag Git (obligatoire, doit exister)
- `--title TITLE` : Titre de la release (défaut: "v{tag}")
- `--description TEXT` : Description de la release (Markdown)
- `--description-file FILE` : Lire la description depuis un fichier
- `--asset FILE` : Asset à uploader (répétable)
- `--auto-wheel` : Auto-détecte et uploade la wheel pour cette version
- `--draft` : Créer comme brouillon
- `--prerelease` : Marquer comme pre-release
- `--token TOKEN` : Token GitHub (ou via GITHUB_TOKEN)
- `--owner OWNER` : Propriétaire du repository
- `--repo REPO` : Nom du repository
- `-c, --config FILE` : Fichier de configuration YAML
- `-v, --verbose` : Mode verbeux

---

## ⚙️ Configuration

### Fichier `config/github.yaml`

```yaml
github:
  # Repository
  owner: "${GITHUB_OWNER:-warchosian}"
  repo: "${GITHUB_REPO:-ambulon}"

  # Authentication (toujours via variable d'environnement)
  token: "${GITHUB_TOKEN:-}"

  # Release settings
  release:
    draft: false          # Créer comme brouillon
    prerelease: false     # Marquer comme pre-release
    generate_notes: false # Auto-générer notes depuis commits
```

### Variables d'Environnement

```bash
# Token GitHub (OBLIGATOIRE)
export GITHUB_TOKEN=ghp_your_token_here

# Repository settings (optionnels)
export GITHUB_OWNER=warchosian
export GITHUB_REPO=ambulon
```

### Hiérarchie de Configuration

1. **Arguments CLI** (`--tag`, `--title`, etc.) - Priorité maximale
2. **Fichier YAML** (`-c config/github.yaml`)
3. **Variables d'environnement** (`GITHUB_*`)
4. **Valeurs par défaut**

---

## 🔑 Obtenir un Token GitHub

### Étapes

1. Aller sur https://github.com/settings/tokens
2. Cliquer sur **"Generate new token (classic)"**
3. Donner un nom : `Ambulon Release Token`
4. Cocher les permissions :
   - ✅ `repo` (Full control of private repositories)
5. Cliquer sur **"Generate token"**
6. **Copier le token immédiatement** (vous ne pourrez plus le revoir)

### Définir le token

**Linux / macOS :**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Windows PowerShell :**
```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

**Windows CMD :**
```cmd
set GITHUB_TOKEN=ghp_your_token_here
```

**Permanent (fichier .bashrc / .zshrc) :**
```bash
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
source ~/.bashrc
```

⚠️ **Sécurité** : Ne jamais commiter le token dans Git !

---

## 🎯 Workflow Recommandé

### Workflow Complet de Release

```bash
# 1. Développer et commiter les changements
git add .
cz commit

# 2. Bump version avec Commitizen
cz bump --changelog

# 3. Vérifier le tag créé
git tag -l -n9 $(git describe --tags --abbrev=0)

# 4. Construire la wheel (si nécessaire)
poetry build
# ou
pip wheel . --no-deps -w dist

# 5. Pousser commits et tags
git push origin beyond-basic-evolutions --follow-tags

# 6. Créer la release GitHub avec auto-wheel
export GITHUB_TOKEN=ghp_...
ambulon github-release --tag $(git describe --tags --abbrev=0) --auto-wheel

# 7. Vérifier la release
# https://github.com/warchosian/ambulon/releases
```

### Workflow Simplifié (Tag Existant)

```bash
# Si le tag existe déjà et a été poussé
export GITHUB_TOKEN=ghp_...
ambulon github-release --tag 3.5.0 --auto-wheel
```

### Workflow avec Description Personnalisée

```bash
# Créer fichier de notes
cat > RELEASE_NOTES.md <<EOF
## Nouvelles Fonctionnalités

- Feature 1
- Feature 2

## Corrections de Bugs

- Fix 1
- Fix 2
EOF

# Créer la release
ambulon github-release --tag 3.5.0 \
  --description-file RELEASE_NOTES.md \
  --auto-wheel
```

---

## 📚 API Python

### Utilisation Programmatique

```python
from app.github.core import GitHubClient, ReleaseManager
from pathlib import Path

# Via GitHubClient (bas niveau)
client = GitHubClient(
    token="ghp_...",
    owner="warchosian",
    repo="ambulon"
)

release = client.create_release(
    tag_name="3.5.0",
    name="v3.5.0 - New Features",
    body="Release notes here...",
    draft=False,
    prerelease=False
)

# Upload asset
client.upload_asset(
    release["id"],
    Path("dist/ambulon-3.5.0-py3-none-any.whl")
)

# Via ReleaseManager (haut niveau, recommandé)
manager = ReleaseManager(
    token="ghp_...",
    owner="warchosian",
    repo="ambulon"
)

release = manager.create_release_from_tag(
    tag="3.5.0",
    title="v3.5.0 - New Features",
    description="Release notes...",
    assets=[
        Path("dist/ambulon-3.5.0-py3-none-any.whl"),
        Path("docs/manual.pdf")
    ]
)

# Auto-détection de la wheel
wheel = manager.find_wheel_for_version("3.5.0")
if wheel:
    print(f"Found wheel: {wheel}")

# Vérifier si release existe
if manager.release_exists("3.5.0"):
    print("Release already exists")
```

### Charger Configuration

```python
from app.github.core.config import load_github_config, get_github_token

# Charger config avec substitution ENV
config = load_github_config("config/github.yaml")

# Extraire token
token = get_github_token(config)

# Accéder aux paramètres
owner = config["github"]["owner"]
repo = config["github"]["repo"]
draft = config["github"]["release"]["draft"]
```

---

## 🐛 Dépannage

### Token non trouvé

**Erreur** : `GitHub token not found`

**Solution** :
```bash
# Définir la variable d'environnement
export GITHUB_TOKEN=ghp_your_token_here

# Vérifier
echo $GITHUB_TOKEN

# Ou passer via CLI
ambulon github-release --tag 3.5.0 --token ghp_your_token_here
```

### Tag n'existe pas

**Erreur** : `404 Not Found` ou `tag not found`

**Solution** :
```bash
# Lister les tags existants
git tag -l

# Créer un tag
git tag -a 3.5.0 -m "Release v3.5.0"

# Pousser le tag
git push origin 3.5.0
```

### Release existe déjà

**Erreur** : `Release 3.5.0 already exists`

**Solution** :
```bash
# Option 1: Utiliser un tag différent
ambulon github-release --tag 3.5.1

# Option 2: Supprimer la release existante sur GitHub
# (via interface web ou API)

# Option 3: Continuer quand même (le script demande confirmation)
ambulon github-release --tag 3.5.0
# Répondre 'y' à la confirmation
```

### Wheel non trouvée

**Erreur** : `No wheel found for version 3.5.0`

**Solution** :
```bash
# Construire la wheel
poetry build

# Ou spécifier le chemin explicitement
ambulon github-release --tag 3.5.0 \
  --asset dist/ambulon-3.5.0-py3-none-any.whl
```

### Permissions insuffisantes

**Erreur** : `403 Forbidden` ou `Resource not accessible`

**Solution** :
- Vérifier que le token a la permission `repo`
- Créer un nouveau token avec les bonnes permissions
- Vérifier que vous avez accès en écriture au repository

---

## 🔒 Sécurité

### Bonnes Pratiques

✅ **À FAIRE** :
- Toujours utiliser `${GITHUB_TOKEN}` dans le YAML
- Stocker le token dans les variables d'environnement
- Ajouter `config/github.yaml` au `.gitignore` (déjà fait)
- Utiliser des tokens avec permissions minimales (seulement `repo`)
- Révoquer les tokens non utilisés

❌ **À NE PAS FAIRE** :
- Jamais commiter un vrai token dans Git
- Jamais hardcoder le token dans le code
- Jamais partager le token publiquement
- Jamais utiliser un token avec plus de permissions que nécessaire

### Vérifier l'Absence de Token dans Git

```bash
# Avant de commiter
git diff | grep -i "ghp_"

# Vérifier fichiers staged
git diff --cached | grep -i "ghp_"

# Scanner l'historique
git log -p | grep -i "ghp_"
```

---

## 📝 Exemples Complets

### Exemple 1 : Release Simple

```bash
export GITHUB_TOKEN=ghp_...
ambulon github-release --tag 3.5.0
```

### Exemple 2 : Release avec Assets

```bash
ambulon github-release --tag 3.5.0 \
  --title "v3.5.0 - Module VSCode" \
  --description "Nouveau module pour gérer les extensions VS Code" \
  --asset dist/ambulon-3.5.0-py3-none-any.whl \
  --asset docs/guide.pdf
```

### Exemple 3 : Pre-Release (Beta)

```bash
ambulon github-release --tag 3.5.0-beta.1 \
  --title "v3.5.0-beta.1 - Test Release" \
  --prerelease \
  --auto-wheel
```

### Exemple 4 : Release avec Description depuis Tag

```bash
# Le tag a une annotation détaillée
git tag -a 3.5.0 -m "Release v3.5.0

Module VSCode pour gérer les extensions.

Nouvelles fonctionnalités:
- vscode-install
- vscode-list
- vscode-uninstall
"

git push origin 3.5.0

# La description sera extraite automatiquement du tag
ambulon github-release --tag 3.5.0 --auto-wheel
```

### Exemple 5 : Configuration via YAML

```yaml
# config/github.yaml
github:
  owner: myorg
  repo: myproject
  token: "${GITHUB_TOKEN}"
  release:
    draft: true  # Toujours créer en draft
```

```bash
ambulon github-release --tag 1.0.0 -c config/github.yaml
```

---

## 🔗 Voir Aussi

- [GitHub REST API Documentation](https://docs.github.com/en/rest/releases)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Commitizen](https://commitizen-tool.github.io/commitizen/)
- [Semantic Versioning](https://semver.org/)

---

## 📄 Licence

Ce module fait partie du projet Ambulon.
