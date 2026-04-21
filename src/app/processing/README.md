# app.processing

Traitement et manipulation de documents Markdown et HTML.

## Commandes

| Commande | Rôle |
| --- | --- |
| `concat-html`   | Concaténer plusieurs HTML |
| `flatten-html`  | Aplatir arborescence HTML en un seul dossier |
| `flatten-md`    | Aplatir arborescence Markdown |
| `merge-html`    | Fusionner HTML (header/footer partagés) |
| `merge-md`      | Fusionner Markdown |
| `md2project`    | Reconstituer une arborescence depuis un monofile `.md` |
| `project2md`    | Générer un monofile `.md` depuis une arborescence |
| `code2md`       | Encapsuler du code source dans des blocs ```lang |
| `augment`       | Ajouter navigation interactive (zoom/drag sur SVG) à un HTML |
| `md2interactive`| Pipeline complet MD → TOC → iTOC → HTML → augment |

## Architecture `core/` vs `commands/`

Convention : la **logique métier** est dans `core/*_logic` (pure, testable,
réutilisable via import), le wrapper **CLI** est dans `commands/` avec un
`def main(argv=None)`.

Exemple :
- `core/project_to_md_converter.py::project_to_markdown_logic(...)` (métier)
- `commands/project2md.py::main(argv=None)` (CLI argparse)
- `commands/__init__.py` ré-exporte `project_to_markdown` comme alias de la logique.

## Note sur `augment` / `make_html_interactive`

Historiquement il existait trois fichiers quasi-identiques (`add_augment.py`,
`make_interactive.py`, `make_html_interactive.py`). Ils ont été fusionnés :
`add_augment.py` est la source canonique avec `def augment(...)`, et
`make_html_interactive` est un alias (`make_html_interactive = augment`)
pour la rétrocompatibilité des imports.
