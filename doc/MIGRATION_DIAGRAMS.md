# Migration des modules de diagrammes

## Résumé

Toute la logique liée aux diagrammes a été migrée sous `src/app/diagrams/` avec un core unifié.

## Structure finale

```
src/app/diagrams/
├── __init__.py                    # API publique
├── README.md                      # Documentation
├── commands/
│   ├── diagram2svg4md.py         # Commande: diagrammes -> SVG inline
│   └── md2html.py                # Commande: Markdown -> HTML avec diagrammes
└── core/                          # Core unifié
    ├── __init__.py               # Exports
    ├── base.py                   # Types et enums
    ├── detector.py               # Détection des diagrammes
    ├── converters.py             # Conversion vers SVG
    ├── svg_utils.py              # Utilitaires SVG
    ├── checker.py                # Vérification PlantUML
    ├── extractor.py              # Extraction vers fichiers
    ├── markdown_to_html.py       # Conversion MD -> HTML
    ├── diagram_detector.py       # SHIM (compatibilité)
    └── plantuml_converter.py     # SHIM (compatibilité)
```

## Changements effectués

### 1. Core unifié créé

Nouveaux fichiers dans `diagrams/core/`:
- `base.py` - Types: `DiagramType`, `ConversionMethod`, `DiagramBlock`, `ConversionResult`, `Violation`
- `detector.py` - Détection: `extract_diagram_blocks()`, `get_diagram_stats()`, etc.
- `converters.py` - Conversion: `convert_plantuml()`, `convert_mermaid()`, `convert_graphviz()`
- `svg_utils.py` - Utilitaires: `clean_svg_content()`, `is_valid_svg()`, etc.
- `checker.py` - Vérification: `PlantUMLChecker` class
- `extractor.py` - Extraction: `extract_diagrams_to_files()`
- `markdown_to_html.py` - Conversion MD->HTML complète

### 2. Commandes distinctes

Deux commandes distinctes sont maintenant disponibles :

| Commande | Module | Description |
|----------|--------|-------------|
| `md2html` | `conversion` | Markdown → HTML **sans** conversion des diagrammes |
| `md2html-diagrams` | `diagrams` | Markdown → HTML **avec** conversion des diagrammes en SVG |

### 3. CLI mis à jour

`src/app/cli/cli.py`:
- `md2html` - Utilise `app.conversion.commands.md2html` (conversion simple)
- `md2html-diagrams` - Utilise `app.diagrams.commands.md2html` (avec diagrammes)

### 4. Shims de compatibilité

Les anciens modules redirigent vers le nouveau core:

| Ancien module | Statut |
|--------------|--------|
| `processing/core/diagram_extractor.py` | SHIM (import depuis diagrams) |
| `encoding/core/plantuml_checker.py` | SHIM (import depuis diagrams) |
| `diagrams/core/diagram_detector.py` | SHIM (ré-export) |
| `diagrams/core/plantuml_converter.py` | SHIM (ré-export) |

## Distinction entre `md2html` et `md2html-diagrams`

### md2html (module conversion)

Convertit Markdown en HTML **sans** traiter les diagrammes.
Les blocs PlantUML, Mermaid et Graphviz restent en texte.

```bash
ambulon md2html document.md
ambulon md2html doc.md -o output.html --toc-backlinks
```

```python
from app.conversion import process_markdown_to_html_simple

process_markdown_to_html_simple(
    markdown_path="doc.md",
    output_path="doc.html",
    verbose=False,
    standalone=True,
    add_toc_backlinks=False
)
```

### md2html-diagrams (module diagrams)

Convertit Markdown en HTML **avec** conversion des diagrammes en SVG.
Supporte PlantUML, Mermaid et Graphviz.

```bash
ambulon md2html-diagrams document.md
ambulon md2html-diagrams doc.md -o output.html --plantuml-method jar -p landscape
```

```python
from app.diagrams import process_markdown_to_html

process_markdown_to_html(
    markdown_path="doc.md",
    output_path="doc.html",
    verbose=False,
    standalone=True,
    plantuml_method='kroki',  # 'kroki', 'jar', ou 'auto'
    plantuml_jar=None,        # Chemin vers plantuml.jar
    page_orientation=None,    # 'portrait', 'landscape' ou None
    add_toc_backlinks=False
)
```

## API publique

### Pour la conversion de diagrammes uniquement

```python
from app.diagrams import (
    # Détection
    extract_diagram_blocks, has_diagrams, count_diagrams,
    
    # Conversion diagrammes
    convert_plantuml, convert_mermaid, convert_graphviz, convert_diagram,
    
    # Vérification et extraction
    PlantUMLChecker, check_plantuml_file,
    extract_diagrams_to_files, batch_extract_diagrams,
    
    # Utilitaires SVG
    clean_svg_content, is_valid_svg, wrap_svg_for_html,
)
```

### Pour la conversion complète MD → HTML avec diagrammes

```python
from app.diagrams import process_markdown_to_html

# Avec conversion des diagrammes
process_markdown_to_html("input.md", "output.html")
```

### Pour la conversion simple MD → HTML (sans diagrammes)

```python
from app.conversion import process_markdown_to_html_simple

# Sans conversion des diagrammes
process_markdown_to_html_simple("input.md", "output.html")
```

## CLI

### Conversion simple (sans diagrammes)

```bash
ambulon md2html document.md
ambulon md2html doc.md -o out.html --toc-backlinks
```

### Conversion avec diagrammes

```bash
ambulon md2html-diagrams document.md
ambulon md2html-diagrams doc.md -o out.html --plantuml-method jar -p landscape
```

### Extraction de diagrammes

```bash
ambulon diagram2svg4md document.md
```

## Variables d'environnement

- `PLANTUML_JAR` - Chemin vers le fichier JAR PlantUML
- `GRAPHVIZ_EXE` - Chemin vers l'exécutable dot (Graphviz)

## Migration recommandée pour le code existant

### Avant

```python
from app.conversion import process_markdown_to_html
from app.processing.core.diagram_extractor import isolate_diagrams_logic
from app.encoding.core.plantuml_checker import PlantUMLChecker
```

### Après

```python
# Pour conversion SANS diagrammes
from app.conversion import process_markdown_to_html_simple

# Pour conversion AVEC diagrammes
from app.diagrams import process_markdown_to_html

# Pour extraction et vérification
from app.diagrams import extract_diagrams_to_files, PlantUMLChecker
```

## Tests

Pour vérifier la migration:

```bash
# Test des deux commandes
ambulon md2html --help
ambulon md2html-diagrams --help

# Test d'import
python -c "from app.conversion import process_markdown_to_html_simple; print('OK')"
python -c "from app.diagrams import process_markdown_to_html; print('OK')"
```
