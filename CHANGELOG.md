# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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