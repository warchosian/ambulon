# Patch : Fix Build Script + Multi-Python Wheels

**Fichiers patch** :
- ✅ `offline-build-script-fix.patch` (2.1 KB, 57 lignes) - **À appliquer**
- ⚠️ `offline-wheels-multi-python.patch` (166 MB, 2.5M lignes) - **Référence uniquement**

**Date** : 2026-02-04
**Version** : Ambulon 3.0.2
**Commit** : `995dcae`

---

## 📋 Problème Résolu

### Erreur pip avec --python-version

```
ERROR: When restricting platform and interpreter constraints using
--python-version, --platform, --abi, or --implementation, either
--no-deps must be set, or --only-binary=:all: must be set
```

**Cause** : pip exige `--only-binary=:all:` quand on utilise `--python-version`

**Solution** : Ajouter `--only-binary=:all:` à la commande pip download

---

## 🎯 Contenu du Patch Léger

### `offline-build-script-fix.patch` (2.1 KB)

**Modification** : `scripts/build_offline_package.py`

```diff
         cmd = [
             "pip", "download",
             *dependencies,
             "-d", str(wheels_dir),
             "--python-version", py_version,
+            "--only-binary", ":all:",
             "--no-cache-dir"
         ]
```

**1 ligne ajoutée** : `--only-binary=:all:`

---

## 📦 Obtenir les Wheels (69 fichiers, 129.5 MB)

Les wheels ne sont **pas incluses dans le patch léger** car trop volumineuses (166 MB encodées).

### Option 1 : Récupérer depuis GitHub (Recommandé)

```bash
# Cloner ou pull le dépôt
git clone https://github.com/warchosian/ambulon.git
cd ambulon
git checkout preprod/v3.0.2-stable

# Les wheels sont dans:
ls dist-offline/wheels/
# 69 wheels (129.5 MB)
```

### Option 2 : Rebuilder les Wheels Localement

```bash
# Après avoir appliqué le patch du script:
python scripts/build_offline_package.py

# Télécharge automatiquement les 69 wheels pour Python 3.10, 3.11, 3.12
```

### Option 3 : Télécharger depuis GitHub Raw

```bash
mkdir -p dist-offline/wheels
cd dist-offline/wheels

# Exemple pour quelques wheels clés:
wget https://github.com/warchosian/ambulon/raw/preprod/v3.0.2-stable/dist-offline/wheels/ambulon-3.0.2-py3-none-any.whl
wget https://github.com/warchosian/ambulon/raw/preprod/v3.0.2-stable/dist-offline/wheels/greenlet-3.3.1-cp311-cp311-win_amd64.whl
# ... etc (69 fichiers)
```

---

## 🚀 Application du Patch

### Étape 1 : Appliquer le Fix du Script

```bash
cd /chemin/vers/ambulon

# Vérifier que le patch s'applique
git apply --check offline-build-script-fix.patch

# Appliquer le patch
git am < offline-build-script-fix.patch

# Ou avec git apply
git apply offline-build-script-fix.patch
```

### Étape 2 : Obtenir les Wheels

**Choix A** : Pull depuis GitHub (si accès au dépôt)
```bash
git pull origin preprod/v3.0.2-stable
# Les wheels sont automatiquement récupérées
```

**Choix B** : Rebuilder localement
```bash
python scripts/build_offline_package.py
# Télécharge les 69 wheels (nécessite Internet temporairement)
```

---

## 📊 Wheels Téléchargées (69 fichiers)

### Par Version Python

**Python 3.10** (cp310):
- greenlet-3.3.1-cp310-cp310-win_amd64.whl
- cffi-2.0.0-cp310-cp310-win_amd64.whl
- charset_normalizer-3.4.4-cp310-cp310-win_amd64.whl
- lxml-6.0.2-cp310-cp310-win_amd64.whl
- pillow-12.1.0-cp310-cp310-win_amd64.whl
- pydantic_core-2.41.5-cp310-cp310-win_amd64.whl
- pywin32-311-cp310-cp310-win_amd64.whl
- pyyaml-6.0.3-cp310-cp310-win_amd64.whl
- rpds_py-0.30.0-cp310-cp310-win_amd64.whl

**Python 3.11** (cp311):
- greenlet-3.3.1-cp311-cp311-win_amd64.whl
- cffi-2.0.0-cp311-cp311-win_amd64.whl
- charset_normalizer-3.4.4-cp311-cp311-win_amd64.whl
- lxml-6.0.2-cp311-cp311-win_amd64.whl
- pillow-12.1.0-cp311-cp311-win_amd64.whl
- pydantic_core-2.41.5-cp311-cp311-win_amd64.whl
- pywin32-311-cp311-cp311-win_amd64.whl
- pyyaml-6.0.3-cp311-cp311-win_amd64.whl
- rpds_py-0.30.0-cp311-cp311-win_amd64.whl

**Python 3.12** (cp312):
- greenlet-3.3.1-cp312-cp312-win_amd64.whl
- cffi-2.0.0-cp312-cp312-win_amd64.whl
- charset_normalizer-3.4.4-cp312-cp312-win_amd64.whl
- lxml-6.0.2-cp312-cp312-win_amd64.whl
- pillow-12.1.0-cp312-cp312-win_amd64.whl
- pydantic_core-2.41.5-cp312-cp312-win_amd64.whl
- pywin32-311-cp312-cp312-win_amd64.whl
- pyyaml-6.0.3-cp312-cp312-win_amd64.whl
- rpds_py-0.30.0-cp312-cp312-win_amd64.whl

**Universelles** (py3-none-any):
- ambulon-3.0.2-py3-none-any.whl
- beautifulsoup4-4.14.3-py3-none-any.whl
- requests-2.32.5-py3-none-any.whl
- markdown-3.10.1-py3-none-any.whl
- mcp-1.26.0-py3-none-any.whl
- python-slugify-8.0.4-py2.py3-none-any.whl
- chardet-5.2.0-py3-none-any.whl
- ... (42 fichiers universels au total)

**Total** : 69 wheels, 129.5 MB

---

## ✨ Avant/Après

### Avant le Patch

❌ Erreur : `ERROR: either --no-deps must be set, or --only-binary=:all:`
❌ Téléchargement échoue pour Python 3.10, 3.11, 3.12
❌ Seulement 1 wheel téléchargée (ambulon)

### Après le Patch

✅ Téléchargement réussi pour Python 3.10, 3.11, 3.12
✅ 69 wheels téléchargées (129.5 MB)
✅ Support multi-version fonctionnel
✅ Toutes les dépendances binaires incluses (greenlet, pillow, pymupdf, etc.)

---

## 🔍 Vérification

Après application du patch et obtention des wheels :

```bash
# Vérifier le script
grep "only-binary" scripts/build_offline_package.py
# Devrait montrer: "--only-binary", ":all:",

# Vérifier les wheels
ls dist-offline/wheels/*.whl | wc -l
# Devrait afficher: 69

# Vérifier la taille
du -sh dist-offline/wheels/
# Devrait afficher: ~130M

# Tester l'installation
python dist-offline/install_offline.py
```

---

## 📝 À Propos du Gros Patch (166 MB)

Le fichier `offline-wheels-multi-python.patch` existe mais **n'est PAS recommandé** :
- ⚠️ 166 MB (166 000 KB)
- ⚠️ 2.5 millions de lignes
- ⚠️ Contient 69 wheels encodées en base64
- ⚠️ Difficile à appliquer (git am peut crasher)
- ⚠️ Pas pratique pour distribution

**Recommandation** :
- ✅ Utiliser `offline-build-script-fix.patch` (2.1 KB)
- ✅ Obtenir wheels via git pull ou rebuild

---

## 🐛 Résolution de Problèmes

### Le patch ne s'applique pas

```bash
# Vérifier la version
git log --oneline -1
# Devrait être après: 95b1899 docs(patch): Add offline installation improvements

# Réessayer avec --3way
git apply --3way offline-build-script-fix.patch
```

### Wheels manquantes après le patch

```bash
# Option 1: Rebuilder
python scripts/build_offline_package.py

# Option 2: Pull depuis GitHub
git fetch origin preprod/v3.0.2-stable
git checkout origin/preprod/v3.0.2-stable -- dist-offline/wheels/
```

### Erreur "already exists" lors du rebuild

```bash
# Supprimer les wheels existantes
rm -rf dist-offline/wheels/

# Rebuilder
python scripts/build_offline_package.py
```

---

## 📚 Fichiers Associés

- `offline-build-script-fix.patch` (2.1 KB) - **Patch léger à appliquer**
- `offline-build-script-fix.README.md` - **Ce fichier**
- `offline-wheels-multi-python.patch` (166 MB) - Référence (non recommandé)
- `offline-install-improvements.patch` (44 KB) - Patch précédent (2 commits)
- `offline-install-improvements.README.md` - Documentation précédente

---

## 📦 Commit Inclus

```
commit 995dcae03a8e8bf48db7c8f9e75d8d8e06ed9c4f
Author: herve.marchal <herve.marchal@developpement-durable.gouv.fr>
Date:   Wed Feb 4 22:21:15 2026 +0100

    fix(offline): Add --only-binary flag and build multi-version wheels

    Fix pip download error when using --python-version flag

    Changes:
    - Add --only-binary=:all: to pip download command
    - Build 69 wheels for Python 3.10, 3.11, 3.12 (129.5 MB)

    Result: Multi-version support working correctly
```

---

**Généré par** : Claude Code
**Version** : Ambulon 3.0.2
**Licence** : MIT
