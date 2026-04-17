# GitLab Releases Module

Module d'intégration GitLab pour gérer les releases et opérations sur les dépôts GitLab.

## 📦 Architecture

```
src/app/gitlab/releases/
├── core/
│   ├── client.py           # Client API GitLab (wrapper requests)
│   ├── release_manager.py  # Gestion des releases (logique métier)
│   └── config.py          # Chargement config/gitlab.yaml
├── commands/
│   └── gitlab_release.py   # CLI: ambulon gitlab-release
```

## 🚀 Commandes CLI

### **`ambulon gitlab-release`** - Créer une release GitLab

Crée une release GitLab depuis un tag Git existant avec upload optionnel d'assets.

```bash
# Créer release depuis un tag
ambulon gitlab-release --tag 3.8.0

# Avec titre et description personnalisés
ambulon gitlab-release --tag 3.8.0 \
  --title "v3.8.0 - New Features" \
  --description "See CHANGELOG.md for details"

# Avec assets spécifiques
ambulon gitlab-release --tag 3.8.0 \
  --asset dist/ambulon-3.8.0-py3-none-any.whl \
  --asset docs/manual.pdf

# Auto-détection de la wheel pour cette version
ambulon gitlab-release --tag 3.8.0 --auto-wheel

# Description depuis un fichier
ambulon gitlab-release --tag 3.8.0 --description-file RELEASE_NOTES.md

# Avec fichier de configuration
ambulon gitlab-release --tag 3.8.0 -c config/gitlab.yaml

# Spécifier projet et instance différents
ambulon gitlab-release --tag 1.0.0 \
  --project-id "namespace/myproject" \
  --base-url "https://gitlab.example.com"
```

**Options :**
- `--tag TAG` : Nom du tag Git (obligatoire, doit exister)
- `--title TITLE` : Titre de la release (défaut: "v{tag}")
- `--description TEXT` : Description de la release (Markdown)
- `--description-file FILE` : Lire la description depuis un fichier
- `--asset FILE` : Asset à uploader (répétable)
- `--auto-wheel` : Auto-détecte et uploade la wheel pour cette version
- `--token TOKEN` : Token GitLab (ou via GITLAB_PRIVATE_TOKEN)
- `--base-url URL` : URL de l'instance GitLab
- `--project-id ID` : ID ou namespace/project du projet
- `-c, --config FILE` : Fichier de configuration YAML
- `-y, --force` : Skip confirmation prompts
- `-v, --verbose` : Mode verbeux

---

## ⚙️ Configuration

### Fichier `config/gitlab.yaml`

```yaml
gitlab:
  # API Settings
  token: "${GITLAB_PRIVATE_TOKEN:-}"

  # Base URL for GitLab instance
  base_url: "https://gitlab-forge.din.developpement-durable.gouv.fr"

  # Repository for releases (project ambulon)
  project_id: "snum/pnm3/gti/ambulon"  # Can be project ID number or namespace/project

  # Release Settings
  release:
    auto_generate_notes: false  # Auto-generate release notes from commits
```

### Variables d'Environnement

```bash
# Token GitLab (OBLIGATOIRE)
export GITLAB_PRIVATE_TOKEN=glpat-your_token_here

# Repository settings (optionnels si dans config)
export GITLAB_BASE_URL="https://gitlab-forge.din.developpement-durable.gouv.fr"
export GITLAB_PROJECT_ID="snum/pnm3/gti/ambulon"
```

### Hiérarchie de Configuration

1. **Arguments CLI** (`--tag`, `--title`, etc.) - Priorité maximale
2. **Fichier YAML** (`-c config/gitlab.yaml`)
3. **Variables d'environnement** (`GITLAB_*`)
4. **Valeurs par défaut**

---

## 🔑 Obtenir un Token GitLab

### Étapes

1. Aller sur votre instance GitLab : `https://gitlab.example.com/-/user_settings/personal_access_tokens`
2. Cliquer sur **"Add new token"**
3. Donner un nom : `Ambulon Release Token`
4. Cocher les permissions :
   - ✅ `api` (Access the authenticated user's API)
5. Cliquer sur **"Create personal access token"**
6. **Copier le token immédiatement** (vous ne pourrez plus le revoir)

### Définir le token

**Linux / macOS :**
```bash
export GITLAB_PRIVATE_TOKEN=glpat-your_token_here
```

**Windows PowerShell :**
```powershell
$env:GITLAB_PRIVATE_TOKEN = "glpat-your_token_here"
```

**Windows CMD :**
```cmd
set GITLAB_PRIVATE_TOKEN=glpat-your_token_here
```

**Permanent (fichier .bashrc / .zshrc) :**
```bash
echo 'export GITLAB_PRIVATE_TOKEN=glpat-your_token_here' >> ~/.bashrc
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
pip wheel . --no-deps -w dist

# 5. Pousser commits et tags
git push origin main --follow-tags

# 6. Créer la release GitLab avec auto-wheel
export GITLAB_PRIVATE_TOKEN=glpat-...
ambulon gitlab-release --tag $(git describe --tags --abbrev=0) --auto-wheel

# 7. Vérifier la release
# https://gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/gti/ambulon/-/releases
```

### Workflow Simplifié (Tag Existant)

```bash
# Si le tag existe déjà et a été poussé
export GITLAB_PRIVATE_TOKEN=glpat-...
ambulon gitlab-release --tag 3.8.0 --auto-wheel
```

### Double Sauvegarde (GitHub + GitLab)

```bash
# Créer release GitHub
export GITHUB_TOKEN=ghp-...
ambulon github-release --tag 3.8.0 --auto-wheel

# Créer release GitLab (même version)
export GITLAB_PRIVATE_TOKEN=glpat-...
ambulon gitlab-release --tag 3.8.0 --auto-wheel
```

---

## 📚 API Python

### Utilisation Programmatique

```python
from pathlib import Path
from app.gitlab.releases.core import GitLabClient, GitLabReleaseManager

# Via GitLabClient (bas niveau)
client = GitLabClient(
    token="glpat-...",
    base_url="https://gitlab-forge.din.developpement-durable.gouv.fr",
    project_id="snum/pnm3/gti/ambulon"
)

release = client.create_release(
    tag_name="3.8.0",
    name="v3.8.0 - New Features",
    description="Release notes here..."
)

# Upload asset
client.upload_asset(
    tag_name="3.8.0",
    asset_path=Path("dist/ambulon-3.8.0-py3-none-any.whl")
)

# Via GitLabReleaseManager (haut niveau, recommandé)
manager = GitLabReleaseManager(
    token="glpat-...",
    base_url="https://gitlab-forge.din.developpement-durable.gouv.fr",
    project_id="snum/pnm3/gti/ambulon"
)

release = manager.create_release_from_tag(
    tag="3.8.0",
    title="v3.8.0 - New Features",
    description="Release notes...",
    assets=[
        Path("dist/ambulon-3.8.0-py3-none-any.whl"),
        Path("docs/manual.pdf")
    ]
)

# Auto-détection de la wheel
wheel = manager.find_wheel_for_version("3.8.0")
if wheel:
    print(f"Found wheel: {wheel}")

# Vérifier si release existe
if manager.release_exists("3.8.0"):
    print("Release already exists")
```

---

## 🐛 Dépannage

### Token non trouvé

**Erreur** : `GitLab token not found`

**Solution** :
```bash
# Définir la variable d'environnement
export GITLAB_PRIVATE_TOKEN=glpat-your_token_here

# Vérifier
echo $GITLAB_PRIVATE_TOKEN

# Ou passer via CLI
ambulon gitlab-release --tag 3.8.0 --token glpat-your_token_here
```

### Project ID non trouvé

**Erreur** : `GitLab project_id not found`

**Solution** :
```bash
# Via CLI
ambulon gitlab-release --tag 3.8.0 --project-id "snum/pnm3/gti/ambulon"

# Ou configurer dans config/gitlab.yaml
```

### Tag n'existe pas

**Erreur** : `404 Not Found` ou `tag not found`

**Solution** :
```bash
# Lister les tags existants
git tag -l

# Créer un tag
git tag -a 3.8.0 -m "Release v3.8.0"

# Pousser le tag
git push origin 3.8.0
```

### Release existe déjà

**Erreur** : `Release 3.8.0 already exists`

**Solution** :
```bash
# Utiliser --force pour ajouter des assets
ambulon gitlab-release --tag 3.8.0 --asset file.whl --force
```

---

## 🔒 Sécurité

### Bonnes Pratiques

✅ **À FAIRE** :
- Toujours utiliser `${GITLAB_PRIVATE_TOKEN}` dans le YAML
- Stocker le token dans les variables d'environnement
- Ajouter `config/gitlab.yaml` au `.gitignore` si le token est dedans
- Utiliser des tokens avec permissions minimales (seulement `api`)
- Révoquer les tokens non utilisés

❌ **À NE PAS FAIRE** :
- Jamais commiter un vrai token dans Git
- Jamais hardcoder le token dans le code
- Jamais partager le token publiquement
- Jamais utiliser un token avec plus de permissions que nécessaire

---

## 📝 Exemples Complets

### Exemple 1 : Release Simple

```bash
export GITLAB_PRIVATE_TOKEN=glpat-...
ambulon gitlab-release --tag 3.8.0
```

### Exemple 2 : Release avec Assets

```bash
ambulon gitlab-release --tag 3.8.0 \
  --title "v3.8.0 - GitLab Module" \
  --description "Module complet de gestion des releases GitLab" \
  --asset dist/ambulon-3.8.0-py3-none-any.whl \
  --asset docs/guide.pdf
```

### Exemple 3 : Double Sauvegarde

```bash
# GitHub
export GITHUB_TOKEN=ghp-...
ambulon github-release --tag 3.8.0 --auto-wheel

# GitLab (même release)
export GITLAB_PRIVATE_TOKEN=glpat-...
ambulon gitlab-release --tag 3.8.0 --auto-wheel
```

---

## 📄 Différences avec GitHub

| Feature | GitHub | GitLab |
|---------|--------|--------|
| **Draft releases** | ✅ Oui | ❌ Non |
| **Pre-releases** | ✅ Oui | ✅ Oui (via milestones) |
| **Asset storage** | Directement sur GitHub | Package Registry + Links |
| **API Authentication** | `Authorization: token XXX` | `Private-Token: XXX` |
| **Project identifier** | `owner/repo` | Numeric ID ou `namespace/project` |

---

## 🔗 Voir Aussi

- [GitLab Releases API Documentation](https://docs.gitlab.com/ee/api/releases/)
- [GitLab Package Registry](https://docs.gitlab.com/ee/user/packages/package_registry/)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Commitizen](https://commitizen-tool.github.io/commitizen/)

---

## 📄 Licence

Ce module fait partie du projet Ambulon.
