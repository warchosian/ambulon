# Description Fonctionnelle - Ambulon v3.0.5

## Vue d'ensemble

**Ambulon** est une suite complète d'outils de numérisation et de traitement documentaire, intégrant un serveur MCP (Model Context Protocol) pour une interopérabilité transparente avec les assistants IA (Claude, OpenRouter, Aider, Continue).

---

## 🎯 Objectifs fonctionnels

1. **Numérisation intelligente** : Scanner, OCR et traitement de documents papier
2. **Conversion universelle** : Transformer tout document dans le format souhaité
3. **Enrichissement sémantique** : Tables des matières, liens, interactivité
4. **RAG (Retrieval Augmented Generation)** : Gestion de collections et recherche sémantique
5. **Intégration IA** : Exposition des fonctionnalités via MCP aux assistants IA

---

## 📦 Modules fonctionnels

### 1. Scan & OCR (`scan/`, `ocr/`)

| Fonction | Description | Usage typique |
|----------|-------------|---------------|
| `scan` | Numérisation TWAIN avec profils DPI | Numériser factures, contrats |
| `ocr` | Reconnaissance de caractères (Tesseract) | Extraire texte d'images |
| `scan_with_ocr` | Scan + OCR en chaîne | Document papier → Texte exploitable |

**Caractéristiques :**
- Profils DPI configurables (150, 300, 600)
- Support formats de sortie : JPG, PNG, TIFF, PDF
- OCR multilingue (fra, eng, deu, spa, ita)

---

### 2. Conversion de formats (`conversion/`)

| Commande | Entrée | Sortie | Usage |
|----------|--------|--------|-------|
| `img2pdf` | Images (JPG, PNG) | PDF | Assembler images en PDF |
| `compress-pdf` | PDF | PDF compressé | Réduire taille fichier |
| `html2md` | HTML | Markdown | Archiver pages web |
| `md2html` | Markdown | HTML | Générer documentation |
| `html2pdf` | HTML | PDF | Générer rapports PDF |
| `pdf2html` | PDF | HTML | Extraire contenu PDF |
| `pdf2md` | PDF | Markdown | Convertir PDF éditable |
| `json2jsonl` | JSON Array | JSONL | Préparer données ML |
| `json2md` | JSON | Markdown | Documenter structures JSON |

**Caractéristiques :**
- Rendu PlantUML intégré (Kroki ou JAR local)
- Support des diagrammes SVG dans Markdown
- Génération PDF via Playwright (rendu fidèle)

---

### 3. Traitement de documents (`processing/`)

#### Tables des matières (`toc/`)
| Commande | Fonction |
|----------|----------|
| `add-toc` | Détection auto MD/HTML + ajout TOC |
| `add-toc4md` | TOC Markdown avec ancres |
| `add-toc4html` | TOC HTML navigationnelle |
| `add-itoc4md` | Liens retour (↑) vers TOC |
| `check-toc4md` | Vérifier existence TOC |
| `check-itoc4md` | Vérifier liens retour |

#### Manipulation de documents
| Commande | Fonction |
|----------|----------|
| `flatten-md` | Aplatir arborescence MD en un fichier |
| `flatten-html` | Aplatir arborescence HTML |
| `merge-md` | Fusionner plusieurs fichiers MD |
| `merge-html` | Fusionner plusieurs fichiers HTML |
| `concat-html` | Concaténer HTML avec navigation |
| `make-html-interactive` | Ajouter ancres et navigation |
| `md2project` | Convertir MD en structure de projet (fichiers) |
| `project2md` | Convertir projet en MD monofile |
| `code2md` | Encapsuler code dans blocs Markdown |

---

### 4. Diagrammes (`diagrams/`)

| Commande | Fonction |
|----------|----------|
| `diagram2svg4md` | Convertir diagrammes PlantUML en SVG inline |

**Formats supportés :** PlantUML, Mermaid (via Kroki)

---

### 5. RAG PIAG (`piag/`)

Système de Retrieval Augmented Generation pour l'indexation et la recherche sémantique.

#### Gestion des collections
| Commande | Fonction |
|----------|----------|
| `piag-rag-collection-add` | Créer une collection RAG |
| `piag-rag-collection-list` | Lister les collections |
| `piag-rag-collection-get` | Détails d'une collection |
| `piag-rag-collection-update` | Modifier une collection |
| `piag-rag-collection-rm` | Supprimer une collection |

#### Gestion des documents
| Commande | Fonction |
|----------|----------|
| `piag-rag-doc-upload` | Uploader un document (chunking auto) |
| `piag-rag-doc-list` | Lister les documents d'une collection |
| `piag-rag-doc-get` | Détails d'un document |
| `piag-rag-doc-rm` | Supprimer un document |
| `piag-rag-doc-chunks` | Visualiser les chunks d'un document |

#### Recherche
| Commande | Fonction |
|----------|----------|
| `piag-rag-search` | Recherche sémantique dans les collections |

**Caractéristiques :**
- Chunking automatique des documents
- Embedding sémantique
- Similarité cosinus pour la recherche
- Support PDF, MD, TXT, HTML

---

### 6. WikiSI (`wikisi/`)

Gestion du parc applicatif via l'API WikiSI.

| Commande | Fonction |
|----------|----------|
| `wikisi-sync-api` | Synchroniser énumérations et applications depuis API |
| `wikisi-extract` | Extraire/filtrer applications depuis JSON |
| `wikisi-md` | Convertir parc applicatif JSON en Markdown RAG |
| `wikisi-scrape` | Aspirer récursivement site web WikiSI |
| `wikisi-flatten` | Aplatir arborescence WikiSI téléchargée |

---

### 7. GitLab (`gitlab/`)

| Commande | Fonction |
|----------|----------|
| `gitlab-clone` | Cloner projets GitLab par groupes (config YAML) |
| `gitlab-monofile` | Générer monofile Markdown depuis repo cloné |

---

### 8. Encodage (`encoding/`)

| Commande | Fonction |
|----------|----------|
| `check-utf8` | Vérifier encodage des fichiers Markdown |
| `fix-utf8` | Corriger problèmes d'encodage UTF-8 |

---

### 9. Serveur MCP (`mcp/`)

Exposition des fonctionnalités via Model Context Protocol.

| Commande | Fonction |
|----------|----------|
| `mcp` | Démarrer le serveur MCP |
| `config export` | Exporter configuration MCP |
| `config install` | Installer config pour assistant (claude, openrouter, aider, continue) |
| `config status` | Statut des configurations |
| `config test` | Tester le serveur MCP |

**Outils MCP exposés (7) :**
1. `scan_document` - Scanner avec profils DPI
2. `ocr_image` - OCR sur image
3. `ocr_batch` - OCR en lot
4. `scan_with_ocr` - Scan + OCR chaîné
5. `process_existing_scans` - Traiter scans existants
6. `images_to_pdf` - Convertir images en PDF
7. `compress_pdf` - Compresser PDF

---

## 🔧 Configuration

### Hiérarchie de configuration
```
CLI args > YAML config > ENV vars > Defaults
```

### Fichiers de configuration (`config/`)

| Fichier | Variables ENV | Description |
|---------|---------------|-------------|
| `piag.yaml` | `PIAG_RAG_*` | Endpoint RAG, API keys |
| `gitlab.yaml` | `GITLAB_*` | URL, token, groupes |
| `wikisi.yaml` | `WIKISI_*` | URL API, credentials |

### Variables d'environnement globales
| Variable | Usage |
|----------|-------|
| `AMBULON_HOME` | Répertoire base config (défaut: cwd) |
| `AMBULON_NO_FILE_LOGS` | Désactiver logs fichier |

---

## 📋 Cas d'usage typiques

### Workflow 1 : Document papier → PDF archivable
```bash
# Scanner en haute qualité
ambulon scan -r 300 -o scan.jpg

# OCR pour rendre searchable
ambulon ocr scan.jpg -o scan.txt

# Assembler en PDF
ambulon img2pdf scans/ -o document.pdf

# Compresser
ambulon compress-pdf document.pdf -o document_compact.pdf
```

### Workflow 2 : Documentation technique → Site web
```bash
# Convertir MD en HTML avec TOC
ambulon add-toc4md docs/*.md
ambulon md2html docs/guide.md -o site/guide.html --toc-backlinks

# Rendre interactif
ambulon make-html-interactive site/ -o site_final/
```

### Workflow 3 : Parc applicatif → RAG
```bash
# Synchroniser depuis API
ambulon wikisi-sync-api

# Convertir en MD
ambulon wikisi-md apps.json -o apps_rag.md

# Créer collection et uploader
ambulon piag-rag-collection-add apps
ambulon piag-rag-doc-upload apps_rag.md --collection apps

# Rechercher
ambulon piag-rag-search "authentification SSO" --collection apps
```

### Workflow 4 : Projet GitLab → Documentation IA
```bash
# Cloner groupe de projets
ambulon gitlab-clone --group mon-equipe

# Générer monofile
ambulon gitlab-monofile G:/repos/mon-projet -o projet.md

# Enrichir et convertir
ambulon add-toc4md projet.md
ambulon md2html projet.md -o projet.html
```

---

## 🔗 Intégrations externes

| Service | Usage | Module |
|---------|-------|--------|
| **NAPS2** | Scan TWAIN | `scan` |
| **Tesseract OCR** | Reconnaissance de caractères | `ocr` |
| **PIAG RAG** | Recherche sémantique | `piag` |
| **WikiSI API** | Parc applicatif | `wikisi` |
| **GitLab API** | Clonage projets | `gitlab` |
| **Kroki** | Rendu PlantUML | `conversion`, `diagrams` |
| **Playwright** | Génération PDF | `conversion` |

---

## 📊 Métriques du projet

| Métrique | Valeur |
|----------|--------|
| Modules métier | 14 |
| Commandes CLI | ~50 |
| Outils MCP | 7 |
| Tests | 48 fichiers |
| Documentation | 37 fichiers MD |
| Langage | Python 3.10+ |
| Packaging | Poetry |

---

## 🚀 Démarrage rapide

```bash
# Aide générale
ambulon --help

# Aide d'un module
ambulon md2html --help

# Version et config
ambulon --version

# Initialiser les configs
ambulon init
```

---

*Document généré automatiquement - Version 3.0.5*
