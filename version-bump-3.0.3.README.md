# Patch : Version Bump 3.0.2 → 3.0.3

**Fichier patch** : `version-bump-3.0.3.patch`
**Taille** : 1.4 KB (51 lignes)
**Date** : 2026-02-05
**Commit** : `b5dc149`

---

## 📋 Contenu du Patch

Ce patch bump la version d'Ambulon de **3.0.2 → 3.0.3**.

### Fichiers modifiés (2)

1. **`pyproject.toml`** (2 changements)
   ```diff
   -version = "3.0.2"
   +version = "3.0.3"
   ```

2. **`src/app/__init__.py`** (1 changement)
   ```diff
   -__version__ = "3.0.2"
   +__version__ = "3.0.3"
   ```

**Total** : 3 lignes modifiées

---

## 🎯 Raison du Bump

La version 3.0.3 contient plusieurs **fix** et **patch** importants :

### Commits inclus dans v3.0.3

1. **`3259132`** - fix(offline): Add missing greenlet dependency
2. **`5290a4c`** - patch(offline): Add exposed wheels mode with multi-Python support
3. **`995dcae`** - fix(offline): Add --only-binary flag and build multi-version wheels

### Amélioration majeure

✅ **Installation offline multi-version Python** (3.10, 3.11, 3.12)
✅ **69 wheels exposées** (129.5 MB)
✅ **Scripts intelligents** d'installation/désinstallation

---

## 📦 Application du Patch

### Méthode 1 : git am (recommandé)

```bash
cd /chemin/vers/ambulon
git am < version-bump-3.0.3.patch
```

### Méthode 2 : git apply

```bash
cd /chemin/vers/ambulon
git apply --check version-bump-3.0.3.patch  # Vérifier
git apply version-bump-3.0.3.patch
```

### Méthode 3 : patch classique

```bash
cd /chemin/vers/ambulon
patch -p1 < version-bump-3.0.3.patch
```

---

## ✅ Vérification

Après application du patch :

```bash
# Vérifier pyproject.toml
grep '^version = ' pyproject.toml
# Devrait afficher: version = "3.0.3"

# Vérifier __init__.py
grep '__version__' src/app/__init__.py
# Devrait afficher: __version__ = "3.0.3"

# Tester avec ambulon
python -c "from app import __version__; print(__version__)"
# Devrait afficher: 3.0.3

# Ou directement
ambulon --version
# Devrait afficher: Ambulon version 3.0.3
```

---

## 🔗 Patches Associés

Pour obtenir toutes les fonctionnalités de la v3.0.3, appliquez ces patches dans l'ordre :

1. **`offline-install-improvements.patch`** (44 KB)
   - fix(offline): Add missing greenlet dependency
   - patch(offline): Add exposed wheels mode

2. **`offline-build-script-fix.patch`** (2.1 KB)
   - fix(offline): Add --only-binary flag

3. **`version-bump-3.0.3.patch`** (1.4 KB) ← **Ce patch**
   - bump: version 3.0.2 → 3.0.3

---

## 📊 Changelog Complet v3.0.3

### 🚀 Nouvelles Fonctionnalités

- **Installation offline intelligente** avec détection automatique Python 3.10/3.11/3.12
- **Mode "exposed"** : wheels accessibles par URL (pas de ZIP de 80 MB)
- **Scripts Python** : `install_offline.py` et `uninstall_offline.py`

### 🐛 Corrections

- Ajout de la dépendance manquante `greenlet`
- Fix flag `--only-binary` pour pip download multi-version
- Support des wheels binaires pour toutes versions Python

### 📦 Contenu

- **69 wheels** (129.5 MB) dans `dist-offline/wheels/`
- **3 patches** disponibles pour application progressive

---

## 🏷️ Tag Git

Ce patch correspond au tag Git **`3.0.3`** :

```bash
# Créer le tag après avoir appliqué le patch
git tag -a 3.0.3 -m "Release v3.0.3

Multi-version Python support (3.10, 3.11, 3.12) for offline installation.
69 wheels exposed in dist-offline/wheels/ (129.5 MB)."

# Pousser le tag
git push origin 3.0.3
```

---

## 🐛 Résolution de Problèmes

### Le patch ne s'applique pas

**Vérifier que vous êtes après le commit `248eef4`** :
```bash
git log --oneline -1
# Devrait être : 248eef4 docs(patch): Add lightweight patch for build script fix
```

**Si vous êtes sur une version antérieure** :
```bash
# Appliquer d'abord les patches précédents
git am < offline-install-improvements.patch
git am < offline-build-script-fix.patch
# Puis celui-ci
git am < version-bump-3.0.3.patch
```

### Conflit sur la version

Si vous avez déjà modifié les versions localement :
```bash
# Résolution manuelle
git apply --reject version-bump-3.0.3.patch
# Puis éditez manuellement les fichiers en conflit
# Et committez
```

---

## 📝 Notes de Release

Cette version bump marque une **évolution majeure** de l'installation offline d'Ambulon :

**Avant (v3.0.2)** :
- ❌ ZIP massif de 80 MB à télécharger
- ❌ Une seule version Python supportée
- ❌ Erreur greenlet avec Python 3.11

**Après (v3.0.3)** :
- ✅ Scripts légers (~10 KB) à télécharger
- ✅ Support Python 3.10, 3.11, 3.12
- ✅ Installation intelligente automatique
- ✅ 69 wheels accessibles par URL

---

**Généré par** : Claude Code
**Licence** : MIT
