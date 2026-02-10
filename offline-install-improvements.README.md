# Patch : Améliorations Installation Offline

**Fichier patch** : `offline-install-improvements.patch`
**Taille** : 44 KB
**Date** : 2026-02-04
**Version** : Ambulon 3.0.2

---

## 📋 Contenu du Patch

Ce patch contient **2 commits** qui améliorent l'installation offline d'Ambulon :

### Commit 1 : `fix(offline): Add missing greenlet dependency`
- **Problème** : Installation offline échouait avec `ERROR: No matching distribution found for greenlet`
- **Solution** : Ajout de greenlet aux dépendances du package offline
- **Fichiers modifiés** :
  - `scripts/build_offline_package.py`
  - `dist-offline/ambulon-3.0.2-offline-install.zip`

### Commit 2 : `patch(offline): Add exposed wheels mode with multi-Python support`
- **Problème** : ZIP massif de 80 MB, incompatibilité Python 3.11/3.12
- **Solution** : Nouveau mode "exposed" avec wheels accessibles par URL
- **Fichiers modifiés/créés** :
  - `scripts/build_offline_package.py` (refactoré)
  - `dist-offline/install_offline.py` (nouveau)
  - `dist-offline/uninstall_offline.py` (nouveau)

---

## 🎯 Améliorations Apportées

### ✅ Support Multi-Version Python
- Python 3.10, 3.11, 3.12 supportés automatiquement
- Détection automatique de la version
- Téléchargement uniquement des wheels compatibles

### ✅ Nouveau Mode "Exposed"
- Pas de ZIP massif à télécharger
- Wheels exposées dans `dist-offline/wheels/`
- Scripts Python légers (~10 KB)
- Installation intelligente avec `pip download`

### ✅ Scripts Intelligents
- `install_offline.py` : Installation automatique
- `uninstall_offline.py` : Désinstallation propre avec `--keep-deps`

### ✅ Rétrocompatibilité
- Ancien mode ZIP conservé avec `--mode zip`
- Choix laissé à l'utilisateur

---

## 📦 Application du Patch

### Méthode 1 : Avec git am (recommandé)

```bash
cd /chemin/vers/ambulon
git am < offline-install-improvements.patch
```

### Méthode 2 : Avec git apply

```bash
cd /chemin/vers/ambulon
git apply --check offline-install-improvements.patch  # Vérifier d'abord
git apply offline-install-improvements.patch
```

### Méthode 3 : Avec patch

```bash
cd /chemin/vers/ambulon
patch -p1 < offline-install-improvements.patch
```

---

## 🚀 Utilisation Après Application

### Mode Exposed (nouveau, par défaut)

```bash
# 1. Builder les wheels
python scripts/build_offline_package.py

# 2. Committer dist-offline/
git add dist-offline/
git commit -m "feat: Add offline installation wheels"
git push

# 3. Les utilisateurs téléchargent uniquement install_offline.py
# 4. Exécutent:
python install_offline.py
```

### Mode ZIP (ancien)

```bash
# Builder le ZIP
python scripts/build_offline_package.py --mode zip

# Distribuer dist-offline/ambulon-3.0.2-offline-install.zip
```

---

## ✨ Avant/Après

### Avant le Patch

❌ Erreur : `greenlet-cp310-win_amd64.whl is not a supported wheel` (Python 3.11)
❌ Téléchargement obligatoire de 80 MB de ZIP
❌ Une seule version Python supportée à la fois

### Après le Patch

✅ Support automatique Python 3.10, 3.11, 3.12
✅ Téléchargement de ~10 KB (scripts uniquement)
✅ Installation intelligente avec détection automatique
✅ Wheels téléchargées à la demande

---

## 🔍 Vérification

Après application du patch :

```bash
# Vérifier les fichiers créés
ls -la dist-offline/install_offline.py
ls -la dist-offline/uninstall_offline.py

# Tester le build
python scripts/build_offline_package.py --help

# Devrait afficher :
# --mode {zip,exposed}  Mode de packaging
```

---

## 📚 Documentation Complète

- `scripts/build_offline_package.py` : Script de build avec `--mode` argument
- `dist-offline/install_offline.py` : Script d'installation intelligent
- `dist-offline/uninstall_offline.py` : Script de désinstallation
- `dist-offline/README.md` : Documentation utilisateur (générée automatiquement)

---

## 🐛 Résolution de Problèmes

### Le patch ne s'applique pas

```bash
# Vérifier la branche
git branch
# Devrait être sur : preprod/v3.0.2-stable ou main

# Vérifier les conflits
git apply --check offline-install-improvements.patch
```

### Conflits détectés

```bash
# Appliquer manuellement avec résolution
git apply --3way offline-install-improvements.patch
# Résoudre les conflits
git add .
git am --continue
```

---

## 📝 Commits Inclus

```
commit 5290a4c410907c81fff5bc9315e5b4a26fa26a8f
Author: herve.marchal <herve.marchal@developpement-durable.gouv.fr>
Date:   Wed Feb 4 21:37:45 2026 +0100

    patch(offline): Add exposed wheels mode with multi-Python support

commit 325913222da0ba56022c965959cd72804dbb419e
Author: herve.marchal <herve.marchal@developpement-durable.gouv.fr>
Date:   Wed Feb 4 09:55:42 2026 +0100

    fix(offline): Add missing greenlet dependency to offline package
```

---

**Généré par** : Claude Code
**Version** : Ambulon 3.0.2
**Licence** : MIT
