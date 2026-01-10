# Ambulon

Suite complète d'outils de numérisation avec serveur MCP pour assistants IA.

Ambulon offre des fonctionnalités de scan, OCR, et traitement PDF, le tout accessible via un serveur MCP (Model Context Protocol) pour une intégration transparente avec les assistants IA.

## 🚀 Fonctionnalités

### Modules principaux
- **📄 Scan** : Scanner des documents avec NAPS2 et profils DPI configurables
- **🔍 OCR** : Reconnaissance optique de caractères avec Tesseract
- **📑 Conversion** : Conversions multiformats (HTML↔MD, JSON→MD, HTML→PDF, JSON→JSONL)
- **🗜️ Compression PDF** : Compression et manipulation de fichiers PDF
- **🌐 WikiSI** : Extraction, transformation et aspiration de données du parc applicatif
- **📝 Processing** : Traitement de documents (TOC, fusion, aplatissement, interactivité)
- **🔤 Encoding** : Vérification et correction d'encodage UTF-8
- **🦊 GitLab** : Clonage de projets GitLab par groupes
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

```bash
# Cloner le projet
git clone <repository-url>
cd ambulon

# Installer avec Poetry
poetry install

# Ou installer directement
pip install ambulon
```

## 🎯 Utilisation

### Interface en ligne de commande

```bash
# Afficher l'aide
ambulon --help

# ========== Scan & OCR ==========
# Scanner un document
ambulon scan -r 300 -o documents/facture.jpg

# OCR d'une image
ambulon ocr -i documents/facture.jpg -l fra -o documents/facture.txt

# Scanner + OCR en une fois
ambulon scan -r 300 -o documents/contrat.jpg --ocr --lang fra

# ========== Conversion ==========
# HTML vers Markdown
ambulon html2md document.html -o document.md

# Markdown vers HTML
ambulon md2html document.md -o document.html

# HTML vers PDF
ambulon html2pdf document.html -o document.pdf

# JSON vers JSONL
ambulon json2jsonl data.json -o data.jsonl

# JSON vers Markdown
ambulon json2md data.json -o data.md

# Convertir images en PDF
ambulon img2pdf documents/ -o documents/rapport.pdf

# Compresser un PDF
ambulon compress-pdf gros_fichier.pdf -q 60

# ========== WikiSI (Parc applicatif) ==========
# Extraire et filtrer des applications
ambulon wikisi-extract apps.json -o subset.json -r 1-10

# Convertir en Markdown pour RAG
ambulon wikisi-md apps.json -o apps.md --verbose

# Aspirer un site WikiSI
ambulon wikisi-scrape --url https://wikisi.example.fr --output ./data

# Aplatir une arborescence WikiSI
ambulon flatten-wikisi ./wikisi-source -o ./wikisi-flat

# ========== Processing (Traitement documents) ==========
# Ajouter une table des matières
ambulon add-toc-html document.html -o document-toc.html
ambulon add-toc-md document.md -o document-toc.md

# Fusionner plusieurs fichiers
ambulon merge-html dir/ -o merged.html
ambulon merge-md dir/ -o merged.md

# Aplatir une arborescence
ambulon flatten-html ./html-nested -o ./html-flat
ambulon flatten-md ./md-nested -o ./md-flat

# Concaténer des fichiers
ambulon concat-html dir/ -o concatenated.html

# Rendre HTML interactif (navigation)
ambulon make-interactive document.html -o interactive.html

# Convertir projet en Markdown / Markdown en projet
ambulon project2md ./project -o project.md
ambulon md2project project.md -o ./new-project

# ========== Encoding ==========
# Vérifier l'encodage UTF-8
ambulon chk-utf8 documents/

# Corriger l'encodage UTF-8
ambulon fix-utf8 documents/

# ========== GitLab ==========
# Cloner des projets GitLab
ambulon gitlab-clone

# ========== RAG PIAG ==========
# Collections RAG
ambulon piag-collection-list --token <TOKEN>
ambulon piag-collection-add --name "Mon Corpus" --description "Description" --token <TOKEN>
ambulon piag-collection-get --collection-id <ID> --token <TOKEN>
ambulon piag-collection-update --collection-id <ID> --name "Nouveau nom" --token <TOKEN>
ambulon piag-collection-rm --collection-id <ID> --token <TOKEN>

# Documents RAG
ambulon piag-doc-upload --collection-id <ID> --file document.pdf --token <TOKEN>
ambulon piag-doc-list --collection-id <ID> --token <TOKEN>
ambulon piag-doc-get --document-id <ID> --token <TOKEN>
ambulon piag-doc-rm --document-id <ID> --token <TOKEN>
ambulon piag-doc-chunks --document-id <ID> --token <TOKEN>

# Recherche sémantique
ambulon piag-search --collection-id <ID> --query "Quelle est la procédure ?" --token <TOKEN>
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

### Hiérarchie de Configuration

Ambulon utilise une **hiérarchie de configuration standardisée** pour tous ses modules :

1. **Arguments CLI** (priorité maximale) - Passés directement en ligne de commande
2. **Fichier YAML** - Configuration structurée dans `config/*.yaml`
3. **Variables d'environnement** - Variables système (ex: `WIKISI_BASE_URL`)
4. **Valeurs par défaut** (priorité minimale)

**Exemple avec wikisi-scrape :**
```bash
# 1. Via arguments CLI (priorité maximale)
ambulon wikisi-scrape --url https://wikisi.fr --output ./data

# 2. Via variables d'environnement
export WIKISI_BASE_URL="https://wikisi.fr"
export WIKISI_OUTPUT_DIR="./data"
ambulon wikisi-scrape

# 3. Via fichier YAML
# Créez config/wikisi.yaml puis :
ambulon wikisi-scrape --config config/wikisi.yaml
```

**Fichiers de configuration disponibles :**
- `config/wikisi.yaml` - Configuration aspirateur WikiSI
- `config/gitlab.yaml` - Configuration clonage GitLab
- `config/piag.yaml` - Configuration RAG PIAG

**Substitution de variables d'environnement dans YAML :**
```yaml
site:
  base_url: "${WIKISI_BASE_URL:-https://default.example.fr}"
  token: "${WIKISI_TOKEN:-}"
```

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

### Dépendances

#### Dépendances principales
- **Pillow** : Traitement d'images
- **PyMuPDF** : Manipulation PDF
- **pytesseract** : Interface Python pour Tesseract
- **importlib-resources** : Accès aux ressources du package
- **pytest** : Framework de tests

#### Dépendances optionnelles
- **requests** : Client HTTP (pour wikisi-scrape, piag)
- **beautifulsoup4** : Parsing HTML (pour wikisi-scrape, html2md, conversion)
- **pyyaml** : Configuration YAML (pour wikisi-scrape, piag, gitlab)
- **markdown** : Conversion Markdown (pour md2html)
- **weasyprint** : Génération PDF (pour html2pdf)

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
