"""
Fixtures et configuration pour les tests TOC
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_markdown_content():
    """Contenu Markdown de test standard"""
    return """# Document Principal

**Version**: 1.0.0
**Date**: 2024-01-15
**Auteur**: Test

## Section 1

Contenu de la section 1.

### Sous-section 1.1

Détails de la sous-section.

### Sous-section 1.2

Autres détails.

## Section 2

Contenu de la section 2.

### Sous-section 2.1

Encore des détails.
"""


@pytest.fixture
def markdown_with_toc():
    """Markdown avec TOC déjà présente"""
    return """# Document

## Table des matières
<ul>
<li><a href="#section-1">Section 1</a></li>
<li><a href="#section-2">Section 2</a></li>
</ul>
---

## Section 1
Texte

## Section 2
Texte
"""


@pytest.fixture
def markdown_with_itoc():
    """Markdown avec backlinks déjà présents"""
    return """# Document [↑](#toc-document)

## Section 1 [↑](#toc-section-1)

### Sous-section [↑](#toc-sous-section)

## Section 2 [↑](#toc-section-2)
"""


@pytest.fixture
def markdown_with_toc_marker():
    """Markdown avec marqueur [TOC]"""
    return """# Document Principal

[TOC]

## Section 1
Texte

## Section 2
Texte
"""


@pytest.fixture
def empty_markdown():
    """Markdown vide"""
    return ""


@pytest.fixture
def markdown_no_headings():
    """Markdown sans titres"""
    return """Juste du texte.

Sans aucun titre.
"""


@pytest.fixture
def complex_markdown():
    """Markdown complexe avec tables, code, etc."""
    return """# Documentation

## Table des matières

## Introduction

Voici une `variable` et du **gras**.

### Exemple de code

```python
def hello():
    print("Hello World")
```

### Tableau

| Nom | Valeur |
|-----|--------|
| A   | 1      |
| B   | 2      |

## Conclusion

C'est fini.
"""
