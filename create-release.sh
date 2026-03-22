#!/bin/bash
# Script pour créer la Release GitHub v3.0.3

# Note : Nécessite un token GitHub avec permissions repo
# Créer un token sur : https://github.com/settings/tokens

REPO="warchosian/ambulon"
TAG="3.0.3"
NAME="v3.0.3 - Multi-Python Offline Installation"

BODY="## 🎉 Version 3.0.3

### 🚀 Nouvelles Fonctionnalités

#### Installation Offline Multi-Version Python
- **Support Python 3.10, 3.11, 3.12** : Installation automatique avec détection de version
- **Mode Exposed** : Wheels accessibles directement (pas de ZIP de 80 MB)
- **Scripts intelligents** : \`install_offline.py\` et \`uninstall_offline.py\`

### 🐛 Corrections

- **fix(offline)**: Ajout de la dépendance manquante \`greenlet\`
- **fix(offline)**: Flag \`--only-binary\` pour téléchargement multi-version

### 📦 Contenu

- **69 wheels** (129.5 MB) pour Python 3.10, 3.11, 3.12
- **2 patches** disponibles :
  - \`offline-build-script-fix.patch\` (2.1 KB) - Fix léger
  - \`offline-install-improvements.patch\` (44 KB) - Changements complets

### 📥 Installation

\`\`\`bash
# Option 1 : Installation avec script
wget https://github.com/warchosian/ambulon/raw/preprod/v3.0.2-stable/dist-offline/install_offline.py
python install_offline.py

# Option 2 : Installation classique
pip install ambulon
\`\`\`

### 🔗 Liens

- [Documentation complète](https://github.com/warchosian/ambulon/blob/preprod/v3.0.2-stable/dist-offline/README.md)
- [Patch fixes](https://github.com/warchosian/ambulon/blob/preprod/v3.0.2-stable/offline-build-script-fix.README.md)
- [Wheels directory](https://github.com/warchosian/ambulon/tree/preprod/v3.0.2-stable/dist-offline/wheels)

### 📝 Changelog

**Commits:**
- \`3259132\` fix(offline): Add missing greenlet dependency
- \`5290a4c\` patch(offline): Add exposed wheels mode with multi-Python support
- \`995dcae\` fix(offline): Add --only-binary flag and build multi-version wheels

---

**Taille totale** : ~130 MB de wheels
**Licence** : MIT"

# Créer la release (nécessite GITHUB_TOKEN dans l'environnement)
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/$REPO/releases \
  -d "{
    \"tag_name\": \"$TAG\",
    \"name\": \"$NAME\",
    \"body\": $(echo "$BODY" | jq -Rs .),
    \"draft\": false,
    \"prerelease\": false
  }"
