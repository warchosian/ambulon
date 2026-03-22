# 📦 Guide d'Installation Ambulon

Ce guide détaille les différentes méthodes d'installation d'Ambulon sur un poste équipé de **Python 3.10 ou supérieur**.

---

## 📋 Table des Matières

- [Prérequis](#prérequis)
- [Méthode 1 : Environnement Virtuel (Recommandé)](#méthode-1--environnement-virtuel-recommandé)
- [Méthode 2 : Installation Utilisateur](#méthode-2--installation-utilisateur)
- [Méthode 3 : Installation Globale](#méthode-3--installation-globale)
- [Méthode 4 : Installation avec Poetry](#méthode-4--installation-avec-poetry)
- [Vérification de l'Installation](#vérification-de-linstallation)
- [Configuration](#configuration)
- [Utilisation Quotidienne](#utilisation-quotidienne)
- [Dépannage](#dépannage)

---

## 🎯 Prérequis

- **Python 3.10+** (3.10, 3.11, 3.12 ou 3.13)
- **pip** (généralement installé avec Python)
- Fichier **`ambulon-X.Y.Z-py3-none-any.whl`**

### Vérifier Python

```bash
# Vérifier la version de Python
python --version
# ou
python3 --version

# Résultat attendu : Python 3.10.x ou supérieur
```

**Si Python < 3.10 :**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# CentOS/RHEL
sudo yum install python310 python3-pip

# macOS (avec Homebrew)
brew install python@3.10

# Windows
# Télécharger depuis https://www.python.org/downloads/
```

---

## Méthode 1 : Environnement Virtuel (Recommandé)

**✅ Avantages :**
- Isolation complète (pas de conflits avec d'autres packages)
- Facile à supprimer (juste effacer le dossier)
- Recommandé pour la production
- Permet plusieurs versions d'Ambulon sur le même système

**❌ Inconvénients :**
- Nécessite activation à chaque session
- Prend un peu plus d'espace disque

### Installation

```bash
# 1. Créer un répertoire de travail
mkdir -p ~/ambulon
cd ~/ambulon

# 2. Transférer la wheel (si nécessaire)
# Copier ambulon-X.Y.Z-py3-none-any.whl dans ce répertoire

# 3. Créer l'environnement virtuel
python3 -m venv ambulon_env

# Structure créée :
# ambulon_env/
# ├── bin/           (Linux/Mac)
# ├── Scripts/       (Windows)
# ├── lib/
# └── pyvenv.cfg

# 4. Activer l'environnement
# Linux/Mac :
source ambulon_env/bin/activate

# Windows PowerShell :
.\ambulon_env\Scripts\Activate.ps1

# Windows cmd.exe :
ambulon_env\Scripts\activate.bat

# Votre prompt change : (ambulon_env) user@host:~/ambulon$

# 5. Mettre à jour pip (recommandé)
pip install --upgrade pip

# 6. Installer Ambulon
pip install ambulon-2.0.6-py3-none-any.whl

# 7. Vérifier l'installation
ambulon --version
# → Ambulon version 2.0.6
```

### Utilisation Quotidienne (venv)

```bash
# À chaque nouvelle session :

# 1. Activer l'environnement
cd ~/ambulon
source ambulon_env/bin/activate  # Linux/Mac
# OU
.\ambulon_env\Scripts\Activate.ps1  # Windows

# 2. Utiliser Ambulon
ambulon piag-rag-search "ma requête"
ambulon scan -o document.pdf

# 3. Quand terminé, désactiver
deactivate
```

### Créer un Raccourci (Optionnel)

**Linux/Mac (Bash) :**
```bash
# Ajouter à ~/.bashrc
echo 'alias ambulon-start="cd ~/ambulon && source ambulon_env/bin/activate"' >> ~/.bashrc
source ~/.bashrc

# Utilisation :
ambulon-start
ambulon --version
```

**Windows (PowerShell) :**
```powershell
# Créer un profil PowerShell
notepad $PROFILE

# Ajouter :
function Start-Ambulon {
    Set-Location C:\Users\YourName\ambulon
    .\ambulon_env\Scripts\Activate.ps1
}

# Utilisation :
Start-Ambulon
ambulon --version
```

---

## Méthode 2 : Installation Utilisateur

**✅ Avantages :**
- Pas besoin de droits administrateur
- Commande `ambulon` disponible directement
- Pas d'activation nécessaire

**❌ Inconvénients :**
- Peut créer des conflits avec d'autres packages Python
- Nécessite configuration du PATH
- Une seule version d'Ambulon possible

### Installation

```bash
# Installer dans le répertoire utilisateur
pip install --user ambulon-2.0.6-py3-none-any.whl

# L'installation se fait dans :
# Linux/Mac : ~/.local/lib/python3.10/site-packages/
# Windows   : %APPDATA%\Python\Python310\site-packages\
```

### Configuration du PATH

**Linux/Mac :**
```bash
# Ajouter au ~/.bashrc ou ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Vérifier
ambulon --version
```

**Windows :**
```powershell
# Trouver le chemin des Scripts
python -c "import site; print(site.USER_BASE + '\\Scripts')"
# Résultat : C:\Users\YourName\AppData\Roaming\Python\Python310\Scripts

# Ajouter au PATH système :
# Panneau de configuration > Système > Variables d'environnement
# Ajouter le chemin ci-dessus à la variable PATH
```

### Utilisation

```bash
# Directement disponible (après configuration PATH)
ambulon --version
ambulon piag-rag-search "requête"
```

---

## Méthode 3 : Installation Globale

**✅ Avantages :**
- Simple et rapide
- Commande `ambulon` disponible immédiatement
- Pas d'activation nécessaire

**❌ Inconvénients :**
- Nécessite souvent les droits administrateur
- Peut créer des conflits avec d'autres packages
- Affecte tout le système
- **Non recommandé pour la production**

### Installation

```bash
# Installation globale (peut nécessiter sudo sur Linux/Mac)
pip install ambulon-2.0.6-py3-none-any.whl

# Ou avec sudo sur Linux/Mac
sudo pip install ambulon-2.0.6-py3-none-any.whl

# Windows (PowerShell Administrateur)
pip install ambulon-2.0.6-py3-none-any.whl
```

### Utilisation

```bash
# Directement disponible
ambulon --version
ambulon piag-rag-search "requête"
```

---

## Méthode 4 : Installation avec Poetry

**✅ Avantages :**
- Gestion professionnelle des dépendances
- Environnement virtuel automatique
- Lock file pour reproductibilité
- Idéal pour développement

**❌ Inconvénients :**
- Nécessite Poetry installé
- Plus complexe pour un simple usage

### Installation

```bash
# 1. Installer Poetry (si pas déjà fait)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Créer un projet Poetry
mkdir -p ~/ambulon-project
cd ~/ambulon-project
poetry init --no-interaction

# 3. Installer Ambulon
poetry add ambulon-2.0.6-py3-none-any.whl

# 4. Utiliser Ambulon
poetry run ambulon --version

# Ou activer le shell Poetry
poetry shell
ambulon --version
```

---

## ✅ Vérification de l'Installation

Après installation (quelle que soit la méthode), vérifier :

```bash
# 1. Version d'Ambulon
ambulon --version
# → Ambulon version 2.0.6

# 2. Afficher l'aide
ambulon --help

# 3. Lister les packages installés
pip show ambulon
# → Name: ambulon
# → Version: 2.0.6
# → Requires: importlib-resources, pillow, pymupdf, requests, pyyaml, ...

# 4. Vérifier les dépendances
pip list | grep -E "(pyyaml|pillow|requests|pymupdf)"

# 5. Test d'import Python
python -c "import app; print('✅ Ambulon import OK')"
# → ✅ Ambulon import OK

# 6. Test d'une commande
ambulon piag-rag-collection-list --help
```

---

## ⚙️ Configuration

### Créer les Fichiers de Configuration

```bash
# Créer le répertoire config
mkdir -p config

# Fichier de configuration PIAG
cat > config/piag.yaml << 'EOF'
piag:
  rag:
    api_token: "${PIAG_RAG_API_TOKEN:-}"
    project_id: "${PIAG_RAG_PROJECT_ID:-}"
    base_url: "${PIAG_RAG_BASE_URL:-https://piag.example.fr}"
EOF

# Fichier de configuration Scan
cat > config/scan.yaml << 'EOF'
scan:
  resolution: 300
  format: pdf
  ocr: false
  lang: fra

tools:
  naps2_console_command: "C:\\Program Files\\NAPS2\\NAPS2.Console.exe"
  tesseract_command: "tesseract"
  tesseract_enabled: true
EOF

# Fichier de configuration GitLab
cat > config/gitlab.yaml << 'EOF'
gitlab:
  token: "${GITLAB_PRIVATE_TOKEN:-}"
  username: "oauth2"
  base_clone_dir: "./gitlab_clones"
  repositories:
    - "https://gitlab.example.com/group/project1.git"
    - "https://gitlab.example.com/group/project2.git"
EOF
```

### Variables d'Environnement

```bash
# Définir les variables d'environnement
export PIAG_RAG_API_TOKEN="votre-token-ici"
export PIAG_RAG_PROJECT_ID="votre-projet-id"
export GITLAB_PRIVATE_TOKEN="glpat-xxxxx"
export OCR_LANGUAGE="fra"

# Utiliser Ambulon (lit automatiquement les variables)
ambulon piag-rag-search "requête"
```

### Fichier .env (Optionnel)

```bash
# Créer un fichier .env
cat > .env << 'EOF'
PIAG_RAG_API_TOKEN=votre-token
PIAG_RAG_PROJECT_ID=votre-projet-id
PIAG_RAG_BASE_URL=https://piag.example.fr
GITLAB_PRIVATE_TOKEN=glpat-xxxxx
TESSERACT_COMMAND=/usr/bin/tesseract
OCR_LANGUAGE=fra
EOF

# Charger les variables
source .env  # Linux/Mac
# Ou utiliser python-dotenv dans vos scripts
```

---

## 🔄 Utilisation Quotidienne

### Commandes Fréquentes

```bash
# Recherche PIAG
ambulon piag-rag-search "ma requête" -o results.json

# Scanner un document
ambulon scan -o scans/document.pdf --resolution 300

# OCR sur une image
ambulon ocr image.jpg --lang fra -o texte.txt

# Lister les collections PIAG
ambulon piag-rag-collection-list

# Cloner des projets GitLab
ambulon gitlab-clone --config config/gitlab.yaml

# Scraper un site WikiSI
ambulon wikisi-scrape --url https://wikisi.example.fr
```

### Workflow Type (avec venv)

```bash
# 1. Activer l'environnement
cd ~/ambulon
source ambulon_env/bin/activate

# 2. Définir les variables d'environnement
export PIAG_RAG_API_TOKEN="votre-token"

# 3. Exécuter les commandes
ambulon piag-rag-search "intelligence artificielle" -o ia_results.json
ambulon scan -o scans/rapport.pdf
ambulon ocr scans/*.jpg --lang fra

# 4. Désactiver
deactivate
```

---

## 🔧 Dépannage

### Problème 1 : `ambulon: command not found`

**Diagnostic :**
```bash
# Vérifier où ambulon est installé
pip show -f ambulon | grep ambulon

# Vérifier le PATH
echo $PATH  # Linux/Mac
echo %PATH%  # Windows
```

**Solutions :**

1. **Si environnement virtuel** : Vérifier qu'il est activé
   ```bash
   which ambulon  # Doit afficher .../ambulon_env/bin/ambulon
   ```

2. **Si installation utilisateur** : Ajouter au PATH
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Utiliser le chemin complet**
   ```bash
   ~/ambulon/ambulon_env/bin/ambulon --version
   ```

4. **Utiliser python -m**
   ```bash
   python -m app.cli.cli --version
   ```

### Problème 2 : `ModuleNotFoundError: No module named 'app'`

**Cause :** Ambulon n'est pas correctement installé

**Solution :**
```bash
# Réinstaller la wheel
pip install --force-reinstall ambulon-2.0.6-py3-none-any.whl

# Vérifier
pip list | grep ambulon
python -c "import app; print('OK')"
```

### Problème 3 : `ModuleNotFoundError: No module named 'yaml'`

**Cause :** Dépendance PyYAML manquante

**Solution :**
```bash
# Installer PyYAML
pip install pyyaml

# Vérifier
python -c "import yaml; print(yaml.__version__)"
```

### Problème 4 : Scripts PowerShell désactivés (Windows)

**Erreur :**
```
.\ambulon_env\Scripts\Activate.ps1 : Impossible de charger le fichier...
```

**Solution :**
```powershell
# Exécuter en tant qu'administrateur
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ou utiliser cmd.exe
ambulon_env\Scripts\activate.bat
```

### Problème 5 : Erreur de dépendances manquantes

**Erreur :**
```
ERROR: Could not find a version that satisfies the requirement pillow>=10.0.0
```

**Solution :**
```bash
# Option 1 : Installer les dépendances manuellement
pip install pyyaml requests pillow pymupdf importlib-resources chardet beautifulsoup4 lxml markdown python-slugify mcp

# Option 2 : Mettre à jour pip
pip install --upgrade pip
pip install ambulon-2.0.6-py3-none-any.whl
```

### Problème 6 : `ambulon --version` affiche une ancienne version

**Cause :** Plusieurs installations d'Ambulon

**Solution :**
```bash
# Lister toutes les installations
pip list | grep ambulon

# Désinstaller complètement
pip uninstall -y ambulon

# Réinstaller proprement
pip install ambulon-2.0.6-py3-none-any.whl

# Vérifier
ambulon --version
```

---

## 📊 Tableau Comparatif des Méthodes

| Critère | Venv | Utilisateur | Globale | Poetry |
|---------|------|-------------|---------|--------|
| **Isolation** | ✅ Excellente | ⚠️ Moyenne | ❌ Aucune | ✅ Excellente |
| **Simplicité** | ⚠️ Moyenne | ✅ Simple | ✅ Très simple | ❌ Complexe |
| **Droits admin** | ❌ Non requis | ❌ Non requis | ✅ Requis | ❌ Non requis |
| **Production** | ✅ Recommandé | ⚠️ Acceptable | ❌ Déconseillé | ✅ Excellent |
| **Développement** | ✅ Bon | ⚠️ Moyen | ❌ Mauvais | ✅ Excellent |
| **Maintenance** | ✅ Facile | ⚠️ Moyenne | ❌ Difficile | ✅ Excellente |
| **Espace disque** | ⚠️ ~100 MB | ⚠️ ~50 MB | ⚠️ ~50 MB | ⚠️ ~100 MB |

**Recommandations :**
- **Production** : Venv ou Poetry
- **Tests rapides** : Globale (temporaire)
- **Serveurs partagés** : Utilisateur
- **Développement** : Poetry

---

## 🎯 Cas d'Usage Spécifiques

### Serveur MCP pour Claude Desktop

```bash
# Installation dans un environnement dédié
python3 -m venv /opt/ambulon_mcp
source /opt/ambulon_mcp/bin/activate
pip install ambulon-2.0.6-py3-none-any.whl

# Configuration Claude Desktop
# Modifier ~/.config/Claude/claude_desktop_config.json
```

### Automatisation avec Cron

```bash
# Installation utilisateur
pip install --user ambulon-2.0.6-py3-none-any.whl

# Script cron (/etc/cron.daily/ambulon_backup)
#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
ambulon wikisi-scrape --config /etc/ambulon/wikisi.yaml
ambulon piag-rag-doc-upload wikisi-downloaded/*.md
```

### Utilisation dans Docker

```dockerfile
FROM python:3.11-slim

# Copier la wheel
COPY ambulon-2.0.6-py3-none-any.whl /tmp/

# Installer Ambulon
RUN pip install /tmp/ambulon-2.0.6-py3-none-any.whl

# Point d'entrée
ENTRYPOINT ["ambulon"]
CMD ["--help"]
```

---

## 📚 Ressources

- **Documentation complète** : `ambulon --help`
- **Configuration** : Voir `config/*.yaml.example`
- **GitHub** : https://github.com/warchosian/ambulon
- **Issues** : https://github.com/warchosian/ambulon/issues

---

**Version du guide : 2.0.6**
**Dernière mise à jour : 2026-01-17**
