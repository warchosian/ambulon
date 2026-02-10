# Tests d'intégration

Ce répertoire contient les tests d'intégration pour le projet DYAG.

## Description

Les tests d'intégration valident le bon fonctionnement des différentes fonctionnalités de DYAG en conditions réelles, avec de vrais fichiers et données.

## Liste des tests

### Conversions de fichiers

- **test_md2html.py** - Test de conversion Markdown vers HTML
- **test_html2pdf.py** - Test de conversion HTML vers PDF
- **test_mcp_md2html.py** - Test de conversion via le serveur MCP

### Fonctionnalités avancées

- **test_add_toc.py** - Test d'ajout de table des matières
- **test_project2md.py** - Test de conversion projet vers Markdown

### RAG et LLM

- **test_create_rag.py** - Test de création de fichiers RAG
- **test_rag_simple.py** - Tests simples des fonctionnalités RAG
- **test_rag_vivacite.py** - Tests RAG avec des données Wikisi
- **test_llm_provider.py** - Test des providers LLM (OpenAI, Anthropic)

### Utilitaires

- **test_new_pattern.py** - Test de nouveaux patterns
- **test_regex_pattern.py** - Test de patterns regex

## Exécution des tests

### Exécuter tous les tests d'intégration
```bash
pytest tests/integration/
```

### Exécuter un test spécifique
```bash
pytest tests/integration/test_md2html.py
```

### Exécuter avec verbosité
```bash
pytest tests/integration/ -v
```

## Notes

- Ces tests peuvent nécessiter des dépendances externes (Playwright, LLM API keys, etc.)
- Certains tests peuvent être longs car ils traitent de vrais fichiers
- Assurez-vous d'avoir configuré votre fichier `.env` pour les tests LLM
