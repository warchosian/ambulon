# Installation Offline d'Ambulon v3.0.3

## 📦 Installation Simple (Recommandé)

### Prérequis
- Python 3.10, 3.11 ou 3.12
- pip installé

---

## 🚀 Option A : Installation Automatique (Séparée)

### Etape 1 : Télécharger les wheels (ONLINE)

```bash
# Télécharger le script de téléchargement
curl -O https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/download_wheels.py

# Ou avec wget
wget https://raw.githubusercontent.com/warchosian/ambulon/preprod/v3.0.2-stable/dist-offline/download_wheels.py

# Exécuter le téléchargement
python download_wheels.py
```

Le script téléchargera les 70 wheels (~130 MB) depuis GitHub et affichera la liste.

### Etape 2 : Installer Ambulon (OFFLINE)

```bash
pip install --no-index --find-links=wheels ambulon
```

**C'est tout ! ✓**

Pip installera automatiquement ambulon + toutes les dépendances depuis les wheels locales.

**Avantages de cette approche** :
- **Séparation claire** : téléchargement (online) vs installation (offline)
- **Simple** : une commande pip standard, pas de script supplémentaire
- **Réutilisable** : téléchargez une fois, installez plusieurs fois
- **Offline complet** : installation sans internet après téléchargement
- **Transparent** : liste complète des wheels téléchargées par download_wheels.py

---

## 📥 Option B : Installation Manuelle

**1. Télécharger le dossier `wheels/`**

Récupérer les 70 wheels depuis GitHub :
```bash
# Option 1 : Cloner le dépôt (si git disponible)
git clone --depth 1 https://github.com/warchosian/ambulon.git -b preprod/v3.0.2-stable
cd ambulon/dist-offline

# Option 2 : Télécharger le ZIP
# https://github.com/warchosian/ambulon/archive/refs/heads/preprod/v3.0.2-stable.zip
# Extraire et aller dans dist-offline/
```

**2. Installer avec pip**

```bash
pip install --no-index --find-links=./wheels ambulon
```

**C'est tout ! ✓**

pip installera automatiquement :
- ambulon
- Toutes les dépendances dans le bon ordre
- Les bonnes wheels pour votre version Python

---

## ✅ Vérification

```bash
ambulon --version
# Ambulon version 3.0.3
```

---

## 🗑️ Désinstallation

### Désinstaller uniquement Ambulon
```bash
pip uninstall ambulon
```

### Désinstaller Ambulon + dépendances
```bash
pip uninstall ambulon mcp playwright greenlet markdown beautifulsoup4 python-slugify lxml chardet pyyaml requests pymupdf pillow importlib-resources
```

---

## 📂 Contenu du dossier wheels/

**70 wheels** (129.8 MB) pour Python 3.10, 3.11, 3.12 :

### Wheels spécifiques par version Python
- `greenlet-3.3.1-cp310-*.whl` (Python 3.10)
- `greenlet-3.3.1-cp311-*.whl` (Python 3.11)
- `greenlet-3.3.1-cp312-*.whl` (Python 3.12)
- `pillow-12.1.0-cp310-*.whl`
- `pillow-12.1.0-cp311-*.whl`
- `pillow-12.1.0-cp312-*.whl`
- ... (27 wheels binaires)

### Wheels universelles (toutes versions Python)
- `ambulon-3.0.3-py3-none-any.whl`
- `beautifulsoup4-4.14.3-py3-none-any.whl`
- `requests-2.32.5-py3-none-any.whl`
- `mcp-1.26.0-py3-none-any.whl`
- ... (42 wheels universelles)

pip choisira automatiquement les wheels compatibles avec votre Python.

---

## 🔧 Options Avancées

### Installer dans un environnement virtuel (recommandé)

```bash
# Créer un venv
python -m venv ambulon-env

# Activer
# Windows:
ambulon-env\Scripts\activate
# Linux/Mac:
source ambulon-env/bin/activate

# Installer
pip install --no-index --find-links=./wheels ambulon

# Utiliser
ambulon --version
```

### Forcer une réinstallation

```bash
pip install --no-index --find-links=./wheels --force-reinstall ambulon
```

### Installer sans dépendances

```bash
pip install --no-index --find-links=./wheels --no-deps ambulon
```

---

## 📥 Téléchargement des Wheels

### Structure requise
```
votre-dossier/
└── wheels/              ← Dossier avec les 69 .whl
    ├── ambulon-3.0.3-py3-none-any.whl
    ├── greenlet-3.3.1-cp311-cp311-win_amd64.whl
    ├── pillow-12.1.0-cp311-cp311-win_amd64.whl
    └── ... (66 autres wheels)
```

### URLs GitHub
- **Dossier wheels/** : https://github.com/warchosian/ambulon/tree/preprod/v3.0.2-stable/dist-offline/wheels
- **ZIP complet** : https://github.com/warchosian/ambulon/archive/refs/heads/preprod/v3.0.2-stable.zip

---

## 🐛 Dépannage

### Erreur : "No matching distribution found"

**Cause** : Le dossier wheels/ est introuvable ou vide

**Solution** :
```bash
# Vérifier que wheels/ existe
ls wheels/
# Devrait afficher 69 fichiers .whl

# Vérifier le chemin
pip install --no-index --find-links=./wheels ambulon
# Ou avec chemin absolu :
pip install --no-index --find-links=/chemin/complet/vers/wheels ambulon
```

### Erreur : "is not a supported wheel"

**Cause** : Mauvaise version Python (ex: vous avez Python 3.9, wheels pour 3.10+)

**Solution** :
```bash
# Vérifier votre version
python --version

# Installer Python 3.10, 3.11 ou 3.12
# https://www.python.org/downloads/
```

### Erreur : "ambulon command not found" après installation

**Solution** :
```bash
# Redémarrer le terminal

# Ou utiliser le chemin complet
python -m app.cli.cli --version

# Ou ajouter Python Scripts au PATH
```

---

## 📝 Notes

### Pourquoi pas de script d'installation ?

Une simple commande pip suffit :
```bash
pip install --no-index --find-links=./wheels ambulon
```

C'est plus simple, plus standard, et pip gère automatiquement :
- L'ordre des dépendances
- La compatibilité Python
- Les wheels binaires vs universelles

### Taille du téléchargement

- **Wheels totales** : 129.5 MB
- **Après installation** : ~130 MB sur disque

Si vous avez déjà certaines dépendances (requests, pillow, etc.),
pip les détectera et ne les réinstallera pas.

---

**Version** : 3.0.3
**Licence** : MIT
**Support** : https://github.com/warchosian/ambulon/issues
