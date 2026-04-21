# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 4.1.0 (2026-04-21)

### Fix

- unblock src/app/gitlab application code and ignore workplace clones explicitly
- anchor 'gitlab/' gitignore rule to repo root only
- replace remaining bare except clauses with specific exceptions

### Refactor

- migrate print() to logging in PIAGClient and config_loader
- **cli**: introduce command registry to replace giant if/elif chain
- **piag,vscode**: remove mutable module-level globals
- **mcp**: unify on mcp.core, turn legacy mcp_server/mcp_config into shims
- **processing**: de-duplicate augment/make_html_interactive commands
- **scan,vscode**: remove hardcoded personal G:\\WarchoLife paths

### Perf

- **piag,wikisi**: reuse requests.Session for HTTP clients

## 4.0.0 (2026-04-21)

### Feat

- **wikisi**: expose short application name as explicit metadata in markdown output
- **wikisi**: add wikisi-extract-apps command for per-app JSON and MD export
- **gitlab-clone**: auto-generate filtered and summarized code.md versions
- **llm**: Add document preprocessing and PlantUML to Mermaid conversion
- **llm**: Add LLM module for document generation via AI APIs

### Refactor

- **llm**: extract OpenAI-compatible base, add local and chatgpt providers

## 3.8.0 (2026-04-17)

### Feat

- **gitlab-clone**: ajout options TOC/iTOC/augment pour fichiers générés

## 3.7.0 (2026-04-17)

### Feat

- **zip**: module complet de gestion d'archives ZIP avec chiffrement AES-256

## 3.6.0 (2026-04-16)

### Feat

- **github**: ajout option --force et support ajout assets aux releases existantes
- **github**: module gestion releases GitHub avec API

## 3.5.0 (2026-04-15)

### Feat

- **vscode**: ajout support Cursor et VS Code Insiders + doc --help
- **vscode**: module gestion extensions VS Code/VSCodium
- **scripts**: ajoute script création release GitHub avec token masqué

## 3.4.0 (2026-04-02)

### Feat

- **piag**: ajout étape 5 publication (HTML + PDF) dans doc-kit
- **piag**: gestion interactive des contraintes réseau VPN

### Refactor

- **piag**: simplifier organisation doc-kit (sans sous-répertoire)

## 3.3.0 (2026-04-01)

### Feat

- **config**: système complet de tracking de configuration

### Fix

- **tests**: correct import paths in config tests
- **md2interactive**: corrige variable non définie + enrichit documentation

## 3.2.0 (2026-03-22)

### Feat

- **piag**: PIPELINE RAG CHAT

## 3.1.1-dev.1 (2026-03-01)

## v3.1.0 (2026-02-28)

### BREAKING CHANGE

- iTOC links now point to specific TOC line anchors
instead of the general TOC heading.
- Command names now use consistent '4md' format:
- add-toc-html → add-toc4html
- add-toc-md → add-toc4md
- add-toc-backlinks-md → add-itoc4md (renamed to inverse TOC)
- check-toc-md → check-toc4md
- check-itoc-md → check-itoc4md (NEW)

### Feat

- release v3.1.0 - modules TOC et diagrams
- Improve iTOC links to point to specific TOC lines
- Add Table of Contents with back-to-TOC navigation links
- **md2html**: Add proportional height constraints for better PDF rendering
- **md2html**: Add page orientation support for optimized PDF generation
- Add PlantUML checker and diagram extractor modules

### Fix

- **toc**: Remove [TOC] marker to prevent duplicate TOC in HTML output
- **md2html**: Enable horizontal scroll for natural mode diagrams
- **md2html**: Fix SVG distortion by correcting PlantUML output
- Correct CLI issues and reorganize project structure

### Refactor

- Reorganize TOC modules into dedicated app/toc package
- **md2html**: Remove max-height, let SVG proportions adjust naturally

## v3.0.5 (2026-02-13)

### BREAKING CHANGE

- Scripts now require confirmation if not in virtual environment

### Feat

- **offline**: Add offline installation v3.0.4 with venv check and improved display

### Fix

- **offline**: Improve virtual environment detection with VIRTUAL_ENV check

## 3.0.4 (2026-02-10)

### Feat

- **offline**: Add automatic installer with online/offline modes

### Fix

- **dist-offline**: amelioration de install_offline
- **Correction-de-md2html**: Mise en prod
- Mise en production
- **offline**: Remove Unicode chars for Windows compatibility + add Option A guide
- **offline**: Add install_from_wheels.py for true offline installation

### Refactor

- **offline**: Separate download and install scripts

## 3.0.3 (2026-02-05)

### Fix

- **offline**: Add --only-binary flag and build multi-version wheels
- **offline**: Add missing greenlet dependency to offline package

## 3.0.2 (2026-02-02)

### Feat

- **build**: Add offline installation package generator

### Fix

- **offline**: Install dependencies before ambulon to avoid resolution errors
- **readme**: Fix offline package download link to point to prod branch
- **cli**: Remove unused requests and json imports
- **conversion**: Remove unused markdown import from md2html

### Refactor

- Rename prod to preprod for branch naming

## v3.0.0 (2026-01-29)

### Feat

- **processing**: Add code2md module for Markdown code block wrapping
- **wikisi**: Add WikiSI API client and CLI integration
- **piag**: Add timeout/retry + update config templates

### Fix

- **wikisi**: Add missing requests import
- **wikisi**: Add wikisi wrapper to DEFAULT_CONFIG structure
- **wikisi**: Correct setup_logging call and config structure access
- **wikisi**: Remove invalid env_prefix parameter and fix config structure
- **piag**: Optimize search performance and user experience

### Refactor

- **processing**: Clean up project2md formatting
- **piag**: Standardize argument naming with explicit -name/-id suffixes

## 2.1.4 (2026-01-22)

## 2.1.3 (2026-01-22)

## 2.1.2 (2026-01-22)

## 2.1.1 (2026-01-22)

### Feat

- **gitlab**: document rag monofile directories

## 2.1.0 (2026-01-22)

### Feat

- **piag**: Add flexible argument handling for collections and documents

### Fix

- **piag**: Fix search API to match PIAG RAG spec (page 5)

### Refactor

- **piag**: Rename --collections to --collection-list for clarity

## 2.0.7 (2026-01-17)

### Fix

- **gitlab**: Improve config validation with detailed error messages
- **config**: Add multi-location config file search

## 2.0.6 (2026-01-17)

### Fix

- **cli**: Prevent empty ambulon_cli log files creation

## 2.0.5 (2026-01-17)

### BREAKING CHANGE

- Complete removal of Typer dependency

### Refactor

- **scan,ocr**: Complete Typer elimination - Convert to argparse

## 2.0.4 (2026-01-17)

### Refactor

- Complete Typer elimination - final 3 files migrated to argparse

## 2.0.3 (2026-01-17)

### Fix

- Support tilde (~) in config paths and add --repo CLI argument
- **piag**: Load config from current working directory, not package install dir

## 2.0.2 (2026-01-17)

### Fix

- **piag**: Remove unused DEFAULT_CONFIG from exports

## 2.0.1 (2026-01-16)

### BREAKING CHANGE

- Typer dependency completely removed from project

### Fix

- **cli**: Import __version__ from app instead of hardcoding 1.0.0
- **cli**: Replace runpy with direct imports for PIAG and WikiSI commands

### Refactor

- Replace Typer with argparse in all CLI commands

## 1.1.1 (2026-01-16)

### Fix

- **piag**: Remove config loading warning at module import

## 1.1.0 (2026-01-16)

### Feat

- **cli**: Add ambulon init command for config generation

### Fix

- **piag**: Stabilize PIAG module with comprehensive test suite

## 1.0.0 (2026-01-13)

### BREAKING CHANGE

- Structure de packages modifiée de ambulon à app

### Feat

- **conversion**: Add PDF to HTML converter (pdf2html)
- **mcp**: Add comprehensive MCP tools for WikiSI, Conversion, Processing and Encoding
- **wikisi**: Add comprehensive web scraper with configuration hierarchy
- **cli**: Intégration complète des modules WikiSI et Processing
- **cli**: Intégration complète des modules conversion et encoding
- add RAG PIAG module with collections, documents and search operations

### Fix

- **gitlab**: Gestion des URLs avec préfixe https:// dans gitlab_clone
- **readme**: Fix offline package download link to point to prod branch

### Refactor

- **wikisi**: Move flatten_wikisi from processing to wikisi module
- Restructuration complète de l'architecture des modules
- Rename prod to preprod for branch naming

## 0.5.1 (2026-01-08)

### Feat

- ajout des fonctions de traitement OCR par dossier et PDF

### Fix

- **packaging**: Embed config data and fix NameError issues to ensure reliable build and execution
- améliorer la détection des répertoires dans le module OCR
- améliorer la détection du mode de traitement OCR
- corrige la gestion des dossiers et fichiers dans le module OCR

### Refactor

- améliorer la détection du type de chemin d'entrée pour l'OCR
- corriger la détection du mode de traitement OCR (dossier/fichier)
- améliorer la détection et la gestion des chemins d'entrée pour l'OCR

## 0.4.0 (2025-12-15)

### Feat

- ajouter les modules img2pdf et compress-pdf à Ambulon
- ajout de scripts de test avancés pour le serveur MCP
- ajout de tests d'intégration complets pour le serveur MCP Ambulon
- corriger les tests d'OCR et de scan pour améliorer la robustesse
- Ajouter une structure complète de tests unitaires avec pytest
- ajout du module de configuration pour Ambulon
- ajouter le fichier de configuration JSON au package Poetry
- ajout de la gestion de configuration MCP et de l'export de configuration Claude
- intégrer le serveur MCP comme module Ambulon
- intégrer l'option `--no-increment` dans le serveur MCP pour le scan
- ajouter une vérification pour empêcher l'écrasement de répertoires lors de la numérisation
- ajout de l'option --no-increment pour désactiver l'auto-incrémentation des noms de fichiers
- ajout de l'auto-incrémentation pour les fichiers de scan
- Migrer le serveur MCP de Dyag vers Ambulon
- intégrer le serveur MCP pour Ambulon avec support des outils de scan et OCR
- ajouter un serveur MCP pour les outils dyag avec des fonctionnalités avancées
- améliore l'interface CLI d'Ambulon avec une aide détaillée et des modules disponibles
- intégrer le module OCR dans l'interface CLI d'Ambulon
- ajouter le module OCR pour le traitement d'images

### Fix

- ajouter la fonction setup_logging dans le module cli
- Ajouter la gestion du cas sans incrémentation dans le nommage des fichiers
- corriger l'initialisation de la variable output_file dans le mode de scan standard
- corriger la gestion des chemins de sortie dans le module de scan
- importer Path depuis pathlib pour vérifier l'existence du script de test
- corriger les tests et dépendances pour améliorer la compatibilité
- gérer l'aide et corriger l'encodage des messages de configuration
- améliorer la gestion du mode simulation de scan avec des informations détaillées
- corrige la gestion des erreurs de scan et d'OCR pour les fichiers vides
- ajouter le champ capabilities manquant dans InitializationOptions
- supprimer l'appel de get_capabilities() dans l'initialisation du serveur MCP
- corrige l'utilisation de false par False en Python

### Refactor

- modifier la logique d'incrémentation des noms de fichiers par défaut

## 0.2.0 (2026-03-22)

### Feat

- **piag**: PIPELINE RAG CHAT

## 3.1.1-dev.1 (2026-03-01)

## v3.1.0 (2026-02-28)

### BREAKING CHANGE

- iTOC links now point to specific TOC line anchors
instead of the general TOC heading.
- Command names now use consistent '4md' format:
- add-toc-html → add-toc4html
- add-toc-md → add-toc4md
- add-toc-backlinks-md → add-itoc4md (renamed to inverse TOC)
- check-toc-md → check-toc4md
- check-itoc-md → check-itoc4md (NEW)

### Feat

- release v3.1.0 - modules TOC et diagrams
- Improve iTOC links to point to specific TOC lines
- Add Table of Contents with back-to-TOC navigation links
- **md2html**: Add proportional height constraints for better PDF rendering
- **md2html**: Add page orientation support for optimized PDF generation
- Add PlantUML checker and diagram extractor modules

### Fix

- **toc**: Remove [TOC] marker to prevent duplicate TOC in HTML output
- **md2html**: Enable horizontal scroll for natural mode diagrams
- **md2html**: Fix SVG distortion by correcting PlantUML output
- Correct CLI issues and reorganize project structure

### Refactor

- Reorganize TOC modules into dedicated app/toc package
- **md2html**: Remove max-height, let SVG proportions adjust naturally

## v3.0.5 (2026-02-13)

### BREAKING CHANGE

- Scripts now require confirmation if not in virtual environment

### Feat

- **offline**: Add offline installation v3.0.4 with venv check and improved display

### Fix

- **offline**: Improve virtual environment detection with VIRTUAL_ENV check

## 3.0.4 (2026-02-10)

### Feat

- **offline**: Add automatic installer with online/offline modes

### Fix

- **dist-offline**: amelioration de install_offline
- **Correction-de-md2html**: Mise en prod
- Mise en production
- **offline**: Remove Unicode chars for Windows compatibility + add Option A guide
- **offline**: Add install_from_wheels.py for true offline installation

### Refactor

- **offline**: Separate download and install scripts

## 3.0.3 (2026-02-05)

### Fix

- **offline**: Add --only-binary flag and build multi-version wheels
- **offline**: Add missing greenlet dependency to offline package
- **readme**: Fix offline package download link to point to prod branch

### Refactor

- Rename prod to preprod for branch naming

## [3.0.2] - 2026-01-31

## [3.0.4] - 2026-02-10

### Changed
- **conversion**: Consolidation md2html and contextual logging for PlantUML/Kroki
- **dependencies**: Make Kroki mandatory and include it in offline install (pyproject + dist-offline)

### Fixed
- **offline-install**: Fix dependency resolution errors in offline installation
  - Install all dependencies BEFORE ambulon to avoid pip resolution failures
  - Two-step installation process: dependencies first, then ambulon
  - Fixes "Could not find a version that satisfies the requirement lxml/pillow..." errors
  - Updated `scripts/build_offline_package.py` and `install-ambulon-offline.bat`
  - Rebuilt `dist-offline/ambulon-3.0.2-offline-install.zip` with corrected installation order

### Changed
- **metadata**: Update author information to Hervé Marchal <herve.marchal@hotmail.fr>
- **branches**: Rename prod/* branches to preprod/* for clearer pre-production naming

## [3.0.1] - 2026-01-29

### Fixed
- **conversion**: Remove unused `markdown` import from md2html module
  - Fixes `ModuleNotFoundError` when markdown package not installed
  - md2html uses custom conversion logic, not markdown library
- **cli**: Remove unused `requests` and `json` imports
  - Prevents import errors when optional dependencies are missing
  - Cleaner module-level imports

## [3.0.0] - 2026-01-28

### BREAKING CHANGES
- **piag**: Refonte complète des arguments avec suffixes explicites `-name`/`-id`
  - `--collection` devient `--collection-name` ou `--collection-id`
  - `--collection-list` devient `--collection-name-list` ou `--collection-id-list`
  - Améliore la clarté et évite les ambiguïtés de résolution
  - Migration requise pour les scripts existants

### Added
- **wikisi**: Nouveau module `wikisi-sync-api` pour synchronisation avec l'API WikiSI
  - Récupération automatique des énumérations et applications
  - Génération de formats IA-ready (applicationsIA.json, applicationsIA_mini.json)
  - Support de la configuration hiérarchique (CLI > YAML > ENV > defaults)
  - Token API optionnel selon les endpoints
- **processing**: Nouveau module `code2md` pour encapsuler du code dans des blocs Markdown
  - Détection automatique de format (30+ langages supportés)
  - Support python, bash, json, yaml, plantuml, mermaid, graphviz, sql, etc.
  - Interface cohérente avec les autres modules de conversion
  - Génération automatique du nom de sortie: `<nom>.<format>.md`
- **piag**: Configuration timeout et retry
  - Argument CLI `--timeout` (défaut: 120s pour RAG)
  - Argument CLI `--max-retries` (défaut: 3)
  - Support variables d'env: `PIAG_RAG_TIMEOUT`, `PIAG_RAG_MAX_RETRIES`
  - Mécanisme de retry avec backoff pour les timeouts

### Fixed
- **piag**: Optimisation de la résolution des collections
  - Heuristique pour éviter les 404 inutiles (détection noms vs IDs)
  - Les noms avec underscore vont directement à la recherche liste
  - Améliore les performances et réduit les logs d'erreur
- **piag**: UX améliorée pour la recherche RAG
  - Affichage de la source de configuration en mode debug
  - Messages de progression pendant les opérations longues
  - Help display corrigé avec nom de commande complet
- **piag**: Synchronisation des templates de configuration
  - Mise à jour de `config_template.py` avec nouveaux paramètres
  - Documentation AMBULON_HOME
  - Exemples de commandes corrigés
- **wikisi**: Corrections multiples de configuration
  - Suppression du paramètre inexistant `env_prefix`
  - Ajout du wrapper `wikisi:` dans la structure YAML
  - Extraction correcte de `wikisi` depuis `loaded_config`
  - Correction de `setup_logging()` sans paramètre `log_file`
  - Ajout de l'import `requests` manquant

### Refactored
- **processing**: Nettoyage du formatage project2md
- **piag**: Standardisation complète de la nomenclature des arguments

## 2.1.4 (2026-01-22)

## 2.1.3 (2026-01-22)

## 2.1.2 (2026-01-22)

## 2.1.1 (2026-01-22)

### Feat

- **gitlab**: document rag monofile directories

## 2.1.0 (2026-01-22)

### Feat

- **piag**: Add flexible argument handling for collections and documents
- **gitlab**: Generate .rag directories with monofiles (code + wiki) for RAG ingestion

### Fix

- **piag**: Fix search API to match PIAG RAG spec (page 5)

### Refactor

- **piag**: Rename --collections to --collection-list for clarity

## 2.0.7 (2026-01-17)

### Fix

- **gitlab**: Improve config validation with detailed error messages
- **config**: Add multi-location config file search

## 2.0.6 (2026-01-17)

### Fix

- **cli**: Prevent empty ambulon_cli log files creation

## 2.0.5 (2026-01-17)

### BREAKING CHANGE

- Complete removal of Typer dependency

### Refactor

- **scan,ocr**: Complete Typer elimination - Convert to argparse

## 2.0.4 (2026-01-17)

### Refactor

- Complete Typer elimination - final 3 files migrated to argparse

## 2.0.3 (2026-01-17)

### Fix

- Support tilde (~) in config paths and add --repo CLI argument
- **piag**: Load config from current working directory, not package install dir

## 2.0.2 (2026-01-17)

### Fix

- **piag**: Remove unused DEFAULT_CONFIG from exports

## 2.0.1 (2026-01-16)

### BREAKING CHANGE

- Typer dependency completely removed from project

### Fix

- **cli**: Import __version__ from app instead of hardcoding 1.0.0
- **cli**: Replace runpy with direct imports for PIAG and WikiSI commands

### Refactor

- Replace Typer with argparse in all CLI commands

## 1.1.1 (2026-01-16)

### Fix

- **piag**: Remove config loading warning at module import

## 1.1.0 (2026-01-16)

### Feat

- **cli**: Add ambulon init command for config generation

## 1.0.1 (2026-01-16)

### Fix

- **piag**: Stabilize PIAG module with comprehensive test suite

## 1.0.0 (2026-01-13)

### BREAKING CHANGE

- Structure de packages modifiée de ambulon à app

### Feat

- **conversion**: Add PDF to HTML converter (pdf2html)
- **mcp**: Add comprehensive MCP tools for WikiSI, Conversion, Processing and Encoding
- **wikisi**: Add comprehensive web scraper with configuration hierarchy
- **cli**: Intégration complète des modules WikiSI et Processing
- **cli**: Intégration complète des modules conversion et encoding
- add RAG PIAG module with collections, documents and search operations

### Fix

- **gitlab**: Gestion des URLs avec préfixe https:// dans gitlab_clone

### Refactor

- **wikisi**: Move flatten_wikisi from processing to wikisi module
- Restructuration complète de l'architecture des modules

## [0.5.1] - 2026-01-07
### Fixed
- Remove accidental GitHub token exposure (`response_to_user.txt`)
- Restore release documentation and configuration files

## [0.5.0] - 2026-01-07
### Added
- MCP configuration support (`mcp-config.json`)
- Improved OCR input path detection
### Fixed
- `NameError` on module import for optional MCP dependency
### Changed
- Packaging workflow (reliable inclusion of config files)
- Release process documentation (`GEMINI.md`, `README.md`)
### Built
- Distribution artifacts for version `0.5.0` (wheel, source)

## [0.4.0] - [Date]
### Added
- Initial MCP integration
### Changed
- Project structure

[0.5.1]: https://github.com/warchosian/ambulon/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/warchosian/ambulon/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/warchosian/ambulon/compare/0.2.0...0.4.0
