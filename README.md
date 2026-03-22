# Ambulon

Suite complète d'outils de numérisation avec serveur MCP pour assistants IA.

Ambulon offre des fonctionnalités de scan, OCR, et traitement PDF, le tout accessible via un serveur MCP (Model Context Protocol) pour une intégration transparente avec les assistants IA.

## 🚀 Fonctionnalités

### Modules principaux
- **📄 Scan** : Scanner des documents avec NAPS2 et profils DPI configurables
- **🔍 OCR** : Reconnaissance optique de caractères avec Tesseract
- **📑 Conversion** : Conversions multiformats (HTML↔MD, JSON→MD, HTML→PDF, JSON→JSONL, Code→MD)
- **🗜️ Compression PDF** : Compression et manipulation de fichiers PDF
- **🌐 WikiSI** : API sync, extraction, transformation et aspiration de données du parc applicatif
- **📝 Processing** : Traitement de documents (TOC, fusion, aplatissement, code wrapping, interactivité)
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

### 🔌 Installation Offline (Sans connexion Internet)

**Pour les environnements sans accès PyPI**, téléchargez le package offline complet depuis GitHub :

📥 **[Télécharger ambulon-3.0.2-offline-install.zip](https://github.com/warchosian/ambulon/raw/preprod/v3.0.2-stable/dist-offline/ambulon-3.0.2-offline-install.zip)** (80.7 MB)

Ce package contient **Ambulon + toutes ses dépendances** (50 wheels) pour une installation complètement offline.

**Installation :**

1. Téléchargez et décompressez le fichier ZIP
2. **Important :** Si vous avez une version précédente, désinstallez-la d'abord :
   ```bash
   cd ambulon-3.0.2-offline-install/scripts
   ./uninstall-ambulon.bat    # Windows
   ```
3. Installez la nouvelle version :
   ```bash
   ./install-ambulon-offline.bat    # Windows
   # OU en ligne de commande :
   pip install --no-index --find-links=../wheels ambulon
   ```

Le README complet avec toutes les instructions est inclus dans le ZIP.

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

# ========== WikiSI (Parc applicatif & Web Scraping) ==========
# Configuration initiale
ambulon init wikisi              # Génère config/wikisi.yaml avec des exemples

# Synchroniser depuis l'API WikiSI (recommandé)
ambulon wikisi-sync-api --verbose
# Génère : wikisi-data/enumerations.json
#          wikisi-data/applications.json
#          wikisi-data/applicationsIA.json
#          wikisi-data/applicationsIA_mini.json

# Aspirer un site WikiSI complet (web scraping)
ambulon wikisi-scrape --url https://wikisi.example.fr --output ./data --depth 2

# Aspirer avec configuration (recommandé)
# Éditez config/wikisi.yaml avec URL, authentification, filtres, etc.
ambulon wikisi-scrape --config config/wikisi.yaml

# Extraire et filtrer des applications depuis JSON
ambulon wikisi-extract apps.json -o subset.json -r 1-10          # Lignes 1-10
ambulon wikisi-extract apps.json -o subset.json -r 1-10,25-30    # Plages multiples
ambulon wikisi-extract apps.json -o subset.json -r -20           # 20 dernières

# Convertir en Markdown pour RAG (Retrieval Augmented Generation)
ambulon wikisi-md apps.json -o apps.md --verbose

# Aplatir une arborescence WikiSI (fusionner tous les fichiers)
ambulon wikisi-flatten ./wikisi-nested -o ./wikisi-flat --verbose

# ========== Processing (Traitement documents) ==========
# Ajouter une table des matières
ambulon add-toc-html document.html -o document-toc.html
ambulon add-toc-md document.md -o document-toc.md

# Encapsuler du code dans des blocs Markdown
ambulon code2md script.py              # Auto-détection → génère script.python.md
ambulon code2md data.json -t json      # Format explicite
ambulon code2md config.yaml -o doc.md  # Sortie personnalisée

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

# ========== RAG PIAG (Retrieval Augmented Generation) ==========
# Configuration initiale
ambulon init piag                # Génère config/piag.yaml avec des exemples

# Collections RAG
ambulon piag-rag-collection-list --token <TOKEN> --project-id <PROJECT_ID>
ambulon piag-rag-collection-add --name "Mon Corpus" --description "Description" --token <TOKEN>
ambulon piag-rag-collection-get --collection <NAME_OR_ID> --project-id <PROJECT_ID> --token <TOKEN>
ambulon piag-rag-collection-update --collection <NAME_OR_ID> --name "Nouveau nom" --token <TOKEN>
ambulon piag-rag-collection-rm --collection <NAME_OR_ID> --token <TOKEN>

# Documents RAG
ambulon piag-rag-doc-upload --collection <NAME_OR_ID> --file document.pdf --token <TOKEN>
ambulon piag-rag-doc-list --collection <NAME_OR_ID> --project-id <PROJECT_ID> --token <TOKEN>
ambulon piag-rag-doc-get --document-id <ID> --token <TOKEN>
ambulon piag-rag-doc-rm --document-id <ID> --token <TOKEN>
ambulon piag-rag-doc-chunks --document-id <ID> --token <TOKEN>

# Recherche sémantique
ambulon piag-rag-search --collection <NAME_OR_ID> --query "Quelle est la procédure ?" --token <TOKEN>

# Utilisation avec configuration (recommandé)
# Éditez config/piag.yaml puis:
ambulon piag-rag-search --collection "Ma Collection" --query "Question" --config config/piag.yaml
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

### Générer les Fichiers de Configuration

La commande `ambulon init` génère automatiquement les fichiers de configuration à partir des templates embarqués dans le package :

```bash
# Initialiser un module spécifique
ambulon init piag          # Crée config/piag.yaml
ambulon init gitlab        # Crée config/gitlab.yaml
ambulon init wikisi        # Crée config/wikisi.yaml

# Initialiser tous les modules en une fois
ambulon init --all

# Écraser un fichier existant
ambulon init piag --force
```

**Pourquoi utiliser `ambulon init` ?**
- ✅ Les templates sont **embarqués dans le wheel** (disponibles après `pip install`)
- ✅ Les fichiers `.example` ne sont **pas inclus dans le wheel** par design
- ✅ Génère des fichiers **pré-commentés** avec tous les paramètres disponibles
- ✅ Évite les erreurs de configuration grâce aux **exemples intégrés**

**Après l'initialisation :**
1. Éditez le fichier généré (ex: `config/piag.yaml`)
2. Remplissez vos credentials (tokens, project IDs, etc.)
3. Les fichiers `config/*.yaml` sont dans `.gitignore` (pas de commit accidentel)

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

### Workflow WikiSI : Synchronisation API et indexation RAG

```bash
# 1. Synchroniser depuis l'API WikiSI (méthode recommandée)
ambulon wikisi-sync-api --verbose

# Génère automatiquement dans wikisi-data/ :
#   - enumerations.json (référentiels)
#   - applications.json (données brutes)
#   - applicationsIA.json (format IA avec énumérations décodées)
#   - applicationsIA_mini.json (format IA allégé, sans champs vides)

# 2. (Optionnel) Extraire un sous-ensemble spécifique
ambulon wikisi-extract wikisi-data/applications.json -o apps-subset.json -r 1-50

# 3. Convertir en Markdown pour RAG
ambulon wikisi-md wikisi-data/applicationsIA_mini.json -o apps-rag.md --verbose

# 4. Uploader vers PIAG RAG
ambulon piag-rag-doc-upload --folder wikisi-data/ --collection-name WIKISI_APPS

# Résultat : Parc applicatif indexé et interrogeable par recherche sémantique
```

### Workflow WikiSI : Web Scraping (méthode alternative)

```bash
# 1. Générer le fichier de configuration
ambulon init wikisi

# 2. Éditer config/wikisi.yaml avec :
#    - URL du site WikiSI
#    - Credentials d'authentification (si requis)
#    - Filtres d'URLs (inclure/exclure)
#    - Profondeur maximale de récursion

# 3. Aspirer le site WikiSI complet
ambulon wikisi-scrape --config config/wikisi.yaml

# 4. Aplatir l'arborescence (optionnel, pour simplifier)
ambulon wikisi-flatten ./wikisi-downloaded -o ./wikisi-flat

# 5. Extraire un sous-ensemble d'applications (optionnel)
ambulon wikisi-extract wikisi-flat/apps.json -o apps-subset.json -r 1-50

# 6. Convertir en Markdown pour RAG
ambulon wikisi-md apps-subset.json -o apps-rag.md --verbose

# Résultat : apps-rag.md prêt pour indexation RAG (PIAG, LangChain, etc.)
```

### Workflow PIAG RAG : Création de corpus et recherche

```bash
# 1. Générer le fichier de configuration
ambulon init piag

# 2. Éditer config/piag.yaml avec :
#    - Token API RAG (JWT Bearer)
#    - Project ID
#    - URL de l'API (défaut: preprod)

# 3. Créer une collection RAG
ambulon piag-rag-collection-add \
  --name "Documentation Technique" \
  --description "Corpus de docs internes" \
  --config config/piag.yaml

# 4. Lister les collections pour récupérer l'ID
ambulon piag-rag-collection-list --config config/piag.yaml

# 5. Uploader des documents dans la collection
ambulon piag-rag-doc-upload \
  --collection "Documentation Technique" \
  --file ./docs/manuel_utilisateur.pdf \
  --config config/piag.yaml

ambulon piag-rag-doc-upload \
  --collection "Documentation Technique" \
  --file ./docs/specifications.pdf \
  --config config/piag.yaml

# 6. Lister les documents uploadés
ambulon piag-rag-doc-list \
  --collection "Documentation Technique" \
  --config config/piag.yaml

# 7. Recherche sémantique (RAG)
ambulon piag-rag-search \
  --collection "Documentation Technique" \
  --query "Comment installer le logiciel ?" \
  --top-k 5 \
  --config config/piag.yaml

# 8. Obtenir les chunks d'un document spécifique
ambulon piag-rag-doc-chunks \
  --document-id <DOCUMENT_ID> \
  --config config/piag.yaml

# Résultat : Recherche sémantique dans votre corpus documentaire
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

# 5. Commit et push vers branche preprod
git checkout -b preprod/v3.0.2-stable
git add dist-offline/
git commit -m "build: Add v3.0.2 offline installation package"
git push origin preprod/v3.0.2-stable
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
