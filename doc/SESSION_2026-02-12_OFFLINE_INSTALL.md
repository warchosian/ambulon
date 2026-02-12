# Session 2026-02-12 : Installation Offline Ambulon 3.0.4

## Contexte du projet

**Ambulon** est un outil de conversion Markdown vers HTML avec support avancé de PlantUML.

Cette session a porté sur l'amélioration du **système d'installation offline** permettant d'installer Ambulon sans connexion internet après une phase de téléchargement.

## Architecture du système d'installation offline

### Structure des fichiers
```
dist-offline/
├── wheels/                           # 134 wheels (186.8 MB)
│   ├── ambulon-3.0.4-py3-none-any.whl
│   └── ... (toutes les dépendances)
├── download_wheels.py                # Script ONLINE (téléchargement)
├── install_offline.py                # Script OFFLINE (installation)
├── uninstall_offline.py              # Script de désinstallation
└── README.md                         # Documentation utilisateur
```

### Processus d'installation en 2 phases

**Phase 1 - ONLINE (une seule fois)**
```bash
python download_wheels.py
```
- Télécharge toutes les wheels depuis GitHub
- URL: `https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels/`
- Stocke dans `dist-offline/wheels/`

**Phase 2 - OFFLINE (sans internet)**
```bash
python install_offline.py
```
- Installe ambulon + dépendances depuis wheels locales
- Commande utilisée: `pip install --no-index --find-links=wheels ambulon`
- Vérifie l'installation avec `ambulon --version`

### Génération automatique des scripts

**Script maître**: `scripts/build_offline_package.py`

Ce script génère automatiquement les 3 scripts d'installation:
- `download_wheels.py` : liste complète des wheels à télécharger
- `install_offline.py` : installation avec vérifications
- `uninstall_offline.py` : désinstallation avec gestion des dépendances

**Régénération nécessaire quand**:
- `pyproject.toml` change (nouvelles dépendances)
- `poetry.lock` est mis à jour
- Structure des wheels change

**Commande de régénération**:
```bash
python scripts/build_offline_package.py
```

## Travaux effectués lors de cette session

### 1. Ajout des dates de génération

**Fichiers modifiés**: `scripts/build_offline_package.py`

- Ajout de `from datetime import datetime`
- Génération de `generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
- Insertion dans les headers et affichages de tous les scripts générés

**Exemple dans les scripts générés**:
```python
# ============================================================================
# FICHIER AUTO-GENERE par scripts/build_offline_package.py
# Date de generation: 2026-02-12 11:49:16
# Ne pas modifier manuellement - vos modifications seront ecrasees
# ============================================================================
```

### 2. Vérification d'environnement virtuel

**Problème**: Les utilisateurs pouvaient installer dans l'environnement global Python

**Solution**: Ajout de `check_virtual_env()` dans `install_offline.py` et `uninstall_offline.py`

**Détection en 3 étapes**:
```python
import os
import sys

def check_virtual_env():
    """Verifie et demande confirmation pour environnement virtuel."""
    # Detection robuste : variable d'env, real_prefix (virtualenv), base_prefix (venv)
    in_venv = (
        os.getenv('VIRTUAL_ENV') is not None or      # Variable d'environnement
        hasattr(sys, 'real_prefix') or                # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)  # venv
    )

    if not in_venv:
        # Avertissement + demande de confirmation
        response = input("Continuer quand meme sans environnement virtuel? (oui/non): ")
        if response.lower() not in ['oui', 'o', 'yes', 'y']:
            sys.exit(0)
```

**Commit de correction**:
- Initial: Détection avec seulement `real_prefix` et `base_prefix`
- Bug détecté: Faux négatif sur Windows avec venv activé
- Fix: Ajout de `os.getenv('VIRTUAL_ENV')` (méthode la plus fiable)
- Commit: `d2e7c07` - fix(offline): Improve virtual environment detection

### 3. Changement de l'URL GitHub

**Ancien format**: `https://raw.githubusercontent.com/warchosian/ambulon/main/dist-offline/wheels/`

**Nouveau format**: `https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels/`

**Raison**: URL plus "standard" restant sur le domaine github.com (fonctionnellement identique)

### 4. Affichage amélioré des tailles de wheels

**Avant**: Tailles en KB (ex: "1234 KB")

**Après**: Tailles en octets avec séparation par espaces (ex: "1 234 567 octets")

**Implémentation**:
```python
size_bytes = wheel.stat().st_size
size_formatted = f"{size_bytes:,}".replace(",", " ")
print(f"  - {wheel.name} ({size_formatted} octets)")
```

**Ajout d'un récapitulatif détaillé**:
```
======================================================================
  RECAPITULATIF
======================================================================

Source GitHub : https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels
Stockees dans : G:\...\dist-offline\wheels
Nombre        : 134 wheels
Taille totale : 195 825 467 octets (186.8 MB)
```

### 5. Affichage de la commande exécutée

Dans `install_offline.py`, affichage explicite de la commande pip:

```python
def verify_installation():
    """Verifie que ambulon est installe correctement."""
    print("\n" + "="*70)
    print("  VERIFICATION")
    print("="*70)
    print()
    print("Commande executee : ambulon --version")
    print()
```

### 6. Inclusion d'Ambulon 3.0.4

**Action**: Copie de `dist/ambulon-3.0.4-py3-none-any.whl` vers `dist-offline/wheels/`

**Résultat**: Version 3.0.4 disponible pour distribution offline

## Commits effectués

### Commit 1: `c790255`
```
feat(offline): Add offline installation v3.0.4 with venv check and improved display

- Add ambulon 3.0.4 wheel and all dependencies to dist-offline/wheels/
- Update download_wheels.py: GitHub URL (github.com/raw), byte-accurate sizes
- Update install_offline.py: Virtual environment check with confirmation
- Update uninstall_offline.py: Virtual environment warning
- Update build_offline_package.py: Auto-generate all scripts with templates

BREAKING CHANGE: Scripts now require confirmation if not in virtual environment
```

**Fichiers**: 53 fichiers (49 nouvelles wheels + 4 scripts)

### Commit 2: `cb3df07`
```
Validation 3.0.4
```

**Fichiers**:
- `dist-offline/README_OFFLINE.md` (nouveau)
- `dist/ambulon-3.0.4-py3-none-any.whl` (nouveau)
- `dist/ambulon-3.0.4.tar.gz` (nouveau)
- `test_mcp_client.py` (supprimé)

### Commit 3: `d2e7c07` (dernier)
```
fix(offline): Improve virtual environment detection with VIRTUAL_ENV check

Add os.getenv('VIRTUAL_ENV') check to detect activated virtual environments.
Previous detection using sys.real_prefix and sys.base_prefix could fail
in some configurations, especially on Windows.

Detection now uses 3 methods:
- VIRTUAL_ENV environment variable (most reliable)
- sys.real_prefix (virtualenv)
- sys.base_prefix comparison (venv)

Fixes false negative when running scripts in activated virtual environment.
```

**Fichiers**:
- `scripts/build_offline_package.py`
- `dist-offline/install_offline.py`
- `dist-offline/uninstall_offline.py`

## État actuel du projet

### Version
- **Ambulon**: 3.0.4
- **Python supporté**: 3.10, 3.11, 3.12
- **Wheels**: 134 fichiers (186.8 MB)

### Branche Git
- **Branche**: `main`
- **Remote**: `origin` (https://github.com/warchosian/ambulon.git)
- **État**: À jour avec origin/main
- **Dernier commit**: `d2e7c07`

### Scripts opérationnels

✅ **download_wheels.py**
- Télécharge depuis GitHub
- Affiche tailles en octets
- Affiche récapitulatif détaillé
- Date de génération: 2026-02-12 11:49:16

✅ **install_offline.py**
- Détection robuste du venv (3 méthodes)
- Installation en une commande
- Vérification avec `ambulon --version`
- Date de génération: 2026-02-12 11:49:16

✅ **uninstall_offline.py**
- Détection robuste du venv
- Option `--keep-deps` pour garder les dépendances
- Liste complète des dépendances
- Date de génération: 2026-02-12 11:49:16

### Fichiers temporaires non committés

Le dossier contient plusieurs fichiers de travail non versionnés:
- `doc/*.md`, `doc/*.html`, `doc/*.pdf` (documentation de travail)
- `*.py` à la racine (scripts de tests)
- `*.whl` à la racine (wheels de tests)
- `wikisi-data/`, `wikisi-downloaded/` (données)

Ces fichiers peuvent être nettoyés ou ajoutés à `.gitignore` si nécessaire.

## Points importants pour la prochaine session

### 1. Test de l'installation offline

**À vérifier**:
```bash
# Dans un environnement propre
python -m venv test_env
test_env\Scripts\activate  # Windows
python dist-offline/download_wheels.py
python dist-offline/install_offline.py
ambulon --version
```

**Résultat attendu**:
- Détection correcte du venv
- Installation réussie
- `ambulon --version` affiche "3.0.4"

### 2. Distribution

Les wheels sont maintenant sur GitHub:
- URL: https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels/
- Accessible via `download_wheels.py`

**Note**: Lors des tests précédents, 49 erreurs HTTP 404 ont été observées car les wheels n'étaient pas encore sur GitHub. Maintenant qu'elles sont poussées (commit `c790255`), le téléchargement devrait fonctionner.

### 3. Maintenance du système

**Quand régénérer les scripts**:
- Après modification de `pyproject.toml`
- Après `poetry update`
- Après changement de version d'Ambulon

**Commande**:
```bash
python scripts/build_offline_package.py
git add dist-offline/
git commit -m "chore(offline): Regenerate offline installation scripts"
git push origin main
```

### 4. Améliorations futures possibles

**Documentation**:
- Ajouter des exemples d'utilisation dans README.md
- Créer un guide pas-à-pas pour utilisateurs non techniques

**Scripts**:
- Ajouter une option `--force` pour ignorer le check venv
- Ajouter une vérification de l'espace disque disponible
- Progress bar pour le téléchargement des wheels

**Distribution**:
- Créer une release GitHub avec les wheels
- Créer un archive ZIP complète dist-offline.zip

## Commandes utiles

### Régénération complète
```bash
# Rebuild la wheel ambulon
poetry build

# Régénère tous les scripts offline
python scripts/build_offline_package.py

# Commit
git add dist/ dist-offline/ scripts/
git commit -m "chore: Regenerate distribution files"
git push origin main
```

### Test local
```bash
# Créer un environnement de test
python -m venv test_install
test_install\Scripts\activate

# Tester l'installation
python dist-offline/install_offline.py

# Vérifier
ambulon --version

# Nettoyer
deactivate
rmdir /s test_install
```

### Vérification du statut Git
```bash
git status
git log --oneline -5
git diff origin/main
```

## Références

### Fichiers clés
- `scripts/build_offline_package.py` : Générateur de scripts (MAÎTRE)
- `pyproject.toml` : Dépendances du projet
- `poetry.lock` : Versions exactes des dépendances
- `dist-offline/README.md` : Documentation utilisateur

### Commits importants
- `c790255` : Ajout complet du système offline v3.0.4
- `cb3df07` : Validation de la version 3.0.4
- `d2e7c07` : Fix de la détection d'environnement virtuel

### URLs
- Dépôt: https://github.com/warchosian/ambulon
- Wheels: https://github.com/warchosian/ambulon/raw/main/dist-offline/wheels/

---

**Date de cette session**: 2026-02-12
**Dernière mise à jour**: 2026-02-12 11:49:16
**Version Ambulon**: 3.0.4
**Dernier commit**: d2e7c07
