# Ambulon

Suite complète d'outils de numérisation avec serveur MCP pour assistants IA.

Ambulon offre des fonctionnalités de scan, OCR, et traitement PDF, le tout accessible via un serveur MCP (Model Context Protocol) pour une intégration transparente avec les assistants IA.

## 🚀 Fonctionnalités

### Modules principaux
- **📄 Scan** : Scanner des documents avec NAPS2 et profils DPI configurables
- **🔍 OCR** : Reconnaissance optique de caractères avec Tesseract
- **📑 IMG2PDF** : Conversion d'images en PDF avec compression
- **🗜️ Compress-PDF** : Compression de fichiers PDF existants
- **🤖 Serveur MCP** : Intégration avec assistants IA (Claude, OpenRouter, Aider, Continue)

### 7 outils MCP disponibles
1. `scan_document` - Scanner un document avec NAPS2
2. `ocr_image` - OCR d'une image
3. `ocr_batch` - OCR en lot sur plusieurs images
4. `scan_with_ocr` - Scanner + OCR en une opération
5. `process_existing_scans` - Traiter des scans existants
6. `images_to_pdf` - Convertir images en PDF
7. `compress_pdf` - Compresser un PDF

## 📦 Installation

### 🔌 Installation Offline (Sans connexion Internet)

**Pour les environnements sans accès PyPI**, téléchargez le package offline complet depuis GitHub :

📥 **[Télécharger ambulon-3.0.1-offline-install.zip](dist-offline/ambulon-3.0.1-offline-install.zip)** (80.7 MB)

Ce package contient **Ambulon + toutes ses dépendances** (50 wheels) pour une installation complètement offline.

**Installation :**

1. Téléchargez et décompressez le fichier ZIP
2. **Important :** Si vous avez une version précédente, désinstallez-la d'abord :
   ```bash
   cd ambulon-3.0.1-offline-install/scripts
   ./uninstall-ambulon.bat    # Windows
   ```
3. Installez la nouvelle version :
   ```bash
   ./install-ambulon-offline.bat    # Windows
   # OU en ligne de commande :
   pip install --no-index --find-links=../wheels ambulon
   ```

Voir [README-OFFLINE.txt](dist-offline/ambulon-3.0.1-offline-install.zip) pour les instructions complètes.

---

### 🌐 Installation Standard (Avec connexion Internet)

```bash
# Installer depuis PyPI (quand disponible)
pip install ambulon

# Ou cloner et installer avec Poetry
git clone https://github.com/warchosian/ambulon.git
cd ambulon
poetry install
```

## 🎯 Utilisation

### Interface en ligne de commande

```bash
# Afficher l'aide
ambulon --help

# Scanner un document
ambulon scan -r 300 -o documents/facture.jpg

# OCR d'une image
ambulon ocr -i documents/facture.jpg -l fra -o documents/facture.txt

# Convertir images en PDF
ambulon img2pdf documents/ -o documents/rapport.pdf

# Compresser un PDF
ambulon compress-pdf gros_fichier.pdf -q 60

# Scanner + OCR en une fois
ambulon scan -r 300 -o documents/contrat.jpg --ocr --lang fra

# Gérer les collections RAG
ambulon rag --help
ambulon rag create-collection --project-id <ID> --name "Mon Corpus" --description "Ma description" --token <TOKEN>
```

### Configuration MCP pour assistants IA

```bash
# Installer la configuration pour Claude Desktop
ambulon config install claude

# Installer pour tous les assistants supportés
ambulon config install all

# Vérifier le statut des configurations
ambulon config status

# Tester le serveur MCP
ambulon config test
```

### Serveur MCP

```bash
# Démarrer le serveur MCP
ambulon mcp

# Tester le serveur en conditions réelles
ambulon test mcp-live
```

## 🔧 Configuration

### Assistants IA supportés

- **Claude Desktop** : Configuration automatique via `%APPDATA%\Claude\claude_desktop_config.json`
- **OpenRouter** : Support des serveurs MCP
- **Aider** : Intégration via configuration JSON
- **Continue (VSCode)** : Extension VSCode avec support MCP

### Exemple de configuration Claude Desktop

```json
{
  "mcpServers": {
    "ambulon": {
      "command": "python",
      "args": ["-m", "ambulon.mcp"],
      "cwd": "/path/to/ambulon"
    }
  }
}
```

## 🧪 Tests

```bash
# Tous les tests
ambulon test all

# Tests spécifiques
ambulon test config
ambulon test mcp
ambulon test scan
ambulon test ocr

# Tests d'intégration MCP
ambulon test mcp-live
```

## 📋 Exemples d'utilisation

### Workflow complet de numérisation

```bash
# 1. Scanner une facture
ambulon scan -r 300 -o courses/facture_picard.jpg

# 2. Extraire le texte par OCR
ambulon ocr -i courses/facture_picard.jpg -l fra -o courses/facture_picard.txt

# 3. Convertir plusieurs documents en PDF
ambulon img2pdf courses/ -o courses/factures_decembre.pdf

# 4. Compresser le PDF final
ambulon compress-pdf courses/factures_decembre.pdf -q 70
```

### Via serveur MCP (assistant IA)

L'assistant peut directement utiliser les outils :

```
Peux-tu scanner la facture et faire l'OCR ?
→ L'assistant utilise scan_with_ocr automatiquement

Convertis les images du dossier "documents" en PDF
→ L'assistant utilise images_to_pdf
```

## 🛠️ Développement

### Structure du projet

```
ambulon/
├── src/ambulon/           # Code source principal
│   ├── scan.py           # Module de scan TWAIN
│   ├── ocr.py            # Module OCR
│   ├── img2pdf.py        # Conversion images → PDF
│   ├── compress_pdf.py   # Compression PDF
│   ├── mcp.py            # Serveur MCP
│   ├── config.py         # Gestion configuration
│   └── cli.py            # Interface ligne de commande
├── tests/                # Tests unitaires
├── config/               # Configurations MCP
└── integration/          # Scripts d'intégration
```

### Commits conventionnels

```bash
# Utiliser Commitizen
cz commit

# Créer une nouvelle version
cz bump
```

### Générer le package d'installation offline

Pour créer un package offline (utile pour les environnements sans accès Internet) :

```bash
# Générer le package offline dans dist-offline/
python scripts/build_offline_package.py
```

Le script :
- ✅ Détecte automatiquement la version depuis `pyproject.toml`
- ✅ Utilise la wheel existante dans `dist/` (pas de rebuild inutile)
- ✅ Télécharge toutes les dépendances depuis PyPI
- ✅ Génère les scripts `install-ambulon-offline.bat` et `uninstall-ambulon.bat`
- ✅ Crée un README complet avec instructions
- ✅ Produit `dist-offline/ambulon-<version>-offline-install.zip` prêt pour distribution

**Workflow de release avec package offline :**

```bash
# 1. Développement
git checkout -b feature/ma-fonctionnalite
# ... modifications ...
git commit -m "feat: ma nouvelle fonctionnalité"

# 2. Bump version
cz bump
# Génère nouveau tag (ex: 3.0.2)

# 3. Build wheel
poetry build

# 4. Générer package offline
python scripts/build_offline_package.py
# Crée dist-offline/ambulon-3.0.2-offline-install.zip

# 5. Commit et push vers branche prod
git checkout -b prod/v3.0.2-stable
git add dist-offline/
git commit -m "build: Add v3.0.2 offline installation package"
git push origin prod/v3.0.2-stable
```

### Dépendances

- **Pillow** : Traitement d'images
- **PyMuPDF** : Manipulation PDF
- **pytesseract** : Interface Python pour Tesseract
- **importlib-resources** : Accès aux ressources du package
- **pytest** : Framework de tests

## 📄 Licence

MIT License - voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter avec des messages conventionnels
4. Ajouter des tests
5. Soumettre une Pull Request

## 📞 Support

Pour toute question ou problème :

1. Vérifiez la documentation
2. Lancez `ambulon config test` pour diagnostiquer
3. Consultez les logs dans le répertoire `logs/`
4. Ouvrez une issue sur le repository
