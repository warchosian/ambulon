# Scripts GitHub

Scripts utilitaires pour gérer les releases GitHub d'Ambulon.

## create_github_release.py

Crée automatiquement une release GitHub et uploade la wheel correspondante.

### Prérequis

- Python 3.10+
- Package `requests` : `pip install requests`
- Token GitHub avec permissions `repo`

### Obtenir un token GitHub

1. Aller sur https://github.com/settings/tokens
2. Cliquer sur "Generate new token (classic)"
3. Cocher la permission `repo`
4. Générer et copier le token

### Usage

```bash
# Méthode 1 : Via variable d'environnement (recommandé)
export GITHUB_TOKEN=your_github_token_here
python scripts-github/create_github_release.py

# Méthode 2 : Via argument
python scripts-github/create_github_release.py --token your_github_token_here

# Spécifier une version différente
python scripts-github/create_github_release.py --version 3.5.0

# Spécifier un chemin de wheel personnalisé
python scripts-github/create_github_release.py --wheel /path/to/ambulon-3.4.0-py3-none-any.whl
```

### Workflow complet

```bash
# 1. Bump version avec commitizen
cz bump --increment MINOR

# 2. Build la wheel
pip wheel . --no-deps -w dist

# 3. Push version et tags
git push && git push --tags

# 4. Créer la release GitHub avec la wheel
export GITHUB_TOKEN=your_token
python scripts-github/create_github_release.py
```

### Sortie attendue

```
📦 Wheel trouvée : ambulon-3.4.0-py3-none-any.whl (377.0 KB)

🚀 Création de la release 3.4.0...
✅ Release créée : https://github.com/warchosian/ambulon/releases/tag/3.4.0

📤 Upload de la wheel...
✅ Wheel uploadée avec succès !

🎉 Release complète disponible : https://github.com/warchosian/ambulon/releases/tag/3.4.0
```
