# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
