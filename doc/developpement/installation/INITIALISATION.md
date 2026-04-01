# 🚀 Guide d'initialisation du projet Ambulon

Ce document décrit les étapes pour configurer et démarrer le projet **Ambulon**, un projet Python utilisant **Poetry**, **Git**, et **Commitizen** pour une gestion structurée.

---

## 📋 Prérequis

- **Python 3.10+** installé ([Téléchargement](https://www.python.org/downloads/))
- **Poetry** installé ([Documentation](https://python-poetry.org/docs/#installation))
- **Git** installé ([Téléchargement](https://git-scm.com/downloads))

---

## 📦 Structure du projet

```
ambulon/
├── pyproject.toml          # Configuration Poetry et Commitizen
├── .cz.toml                 # Configuration Commitizen
├── .gitignore               # Fichiers à ignorer par Git
├── .projectignore           # Fichiers à ignorer par l'IDE/outils
├── doc/
│   └── INITIALISATION.md    # Ce fichier
└── src/
    └── ambulon/
        └── __init__.py      # Module principal
```

---

## 🛠️ Étapes d'initialisation

### 1️⃣ Cloner ou créer le répertoire du projet

Si vous partez de zéro, créez le répertoire du projet :
```bash
mkdir G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
```

---

### 2️⃣ Initialiser Poetry

Poetry est utilisé pour gérer les dépendances et l'environnement virtuel.

#### Installer Poetry (si ce n'est pas déjà fait) :
```bash
(powershell) Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

#### Initialiser le projet avec Poetry :
```bash
poetry init --name ambulon --python "^3.10" --dependency commitizen --dev-dependency pytest --dev-dependency black --dev-dependency isort
```

#### Installer les dépendances :
```bash
poetry install
```

---

### 3️⃣ Configurer Git

#### Initialiser le dépôt Git :
```bash
git init
```

#### Créer un fichier `.gitignore` :
Le fichier `.gitignore` est déjà fourni dans le projet. Il ignore les fichiers temporaires, les dépendances, et les fichiers IDE.

#### Faire le premier commit :
```bash
git add .
git commit -m "feat: initial commit"
```

---

### 4️⃣ Configurer Commitizen

Commitizen est utilisé pour standardiser les commits.

#### Initialiser Commitizen :
```bash
poetry run cz init
```

#### Utiliser Commitizen pour les commits :
```bash
poetry run cz commit
```
*(Suivez les instructions pour créer un commit standardisé.)*

---

### 5️⃣ Tester le projet

#### Exécuter un test simple :
```bash
python -c "from src.ambulon import hello; print(hello())"
```
*(Doit afficher : `Hello Ambulon ! (Version: 0.1.0)`)*

---

## 🔄 Mise à jour et maintenance

### Mettre à jour les dépendances :
```bash
poetry update
```

### Ajouter une nouvelle dépendance :
```bash
poetry add <nom_du_paquet>
```

### Utiliser Commitizen pour les versions :
```bash
poetry run cz bump --changelog
```
*(Crée une nouvelle version et met à jour le `CHANGELOG.md`.)*

---

## 🤖 Utilisation avec Continue

Pour utiliser ce projet avec **Continue** :

1. Ouvrez le répertoire `ambulon` dans votre éditeur de code.
2. Continue détectera automatiquement la structure du projet (Poetry, Git, Python).
3. Vous pouvez utiliser Continue pour :
   - **Générer du code** (ex. : ajouter de nouvelles fonctionnalités).
   - **Poser des questions** sur le projet.
   - **Exécuter des commandes** (ex. : `poetry run pytest`).

---

## 📝 Notes supplémentaires

- **Structure `src/`** : Le code source est placé dans `src/ambulon` pour une meilleure organisation.
- **Poetry** : Utilisez `poetry run <commande>` pour exécuter des commandes dans l'environnement virtuel.
- **Commitizen** : Utilisez `poetry run cz commit` pour créer des commits standardisés.

---

## 🚀 Prochaines étapes

- **Lier à un dépôt distant** (GitHub/GitLab) :
  ```bash
  git remote add origin <URL_DU_DÉPÔT>
  git push -u origin main
  ```
- **Configurer des hooks Git** (optionnel) : Utilisez `pre-commit` pour automatiser les vérifications (Black, isort, etc.).
- **Ajouter des tests** : Créez des tests dans un dossier `tests/` et utilisez `pytest`.

---

📌 **Besoin d'aide ?**
Si vous rencontrez des problèmes ou avez des questions, consultez la documentation de [Poetry](https://python-poetry.org/docs/) ou [Commitizen](https://commitizen-tools.github.io/commitizen/), ou demandez de l'aide !