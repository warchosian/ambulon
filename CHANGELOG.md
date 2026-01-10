# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **WikiSI Web Scraper** (`wikisi-scrape`): Aspirateur récursif de sites web avec filtrage d'URLs, support robots.txt et authentification
- **Configuration Hierarchy System**: Système standardisé de hiérarchie de configuration (CLI > YAML > ENV > Defaults) pour tous les modules
- **WikiSI Commands**: Intégration complète des commandes WikiSI (extract, convert to markdown, flatten, scrape)
- **Conversion Commands**: 5 nouvelles commandes de conversion (html2md, md2html, html2pdf, json2jsonl, json2md)
- **Encoding Commands**: Outils de vérification et correction d'encodage UTF-8 (chk-utf8, fix-utf8)
- **Processing Commands**: 11 commandes de traitement de documents (add-toc, flatten, merge, concat, interactive HTML, etc.)
- **GitLab Integration**: Commande `gitlab-clone` pour cloner des projets GitLab par groupes
- Configuration files: `config/wikisi.yaml`, `config/gitlab.yaml` avec support de variables d'environnement
- Documentation: Sections "Hiérarchie de Configuration" et "Tests et Couverture de Code" dans CLAUDE.md

### Changed
- Module reorganization: Moved `flatten_wikisi` from `processing` to `wikisi` module for better logical grouping
- CLI architecture: Migrated from Typer to standard Python argument parsing for consistency
- All modules now support environment variables with ${VAR:-default} substitution in YAML configs

### Fixed
- GitLab clone command: Removed Typer dependency, converted to standard Python
- Import paths: Updated all module `__init__.py` files for proper exports
- Character encoding: Fixed UTF-8 handling in tests and file operations

### Security
- All sensitive config files (`config/*.yaml` except `*.example`) are now in `.gitignore`
- Token/credential handling via environment variables instead of config files
- Protection hooks for sensitive files in Claude Code

### Documentation
- Comprehensive configuration hierarchy documentation with examples
- Test coverage requirements and best practices (80%+ coverage target)
- Examples for unit, integration, and E2E tests
- CLI help text for all new commands with hierarchy documentation

### Dependencies
- New optional dependencies: `requests`, `beautifulsoup4`, `pyyaml` (for wikisi-scrape)

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