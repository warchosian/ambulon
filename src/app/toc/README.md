# app.toc

Génération de tables des matières (TOC) et liens retour (iTOC) pour Markdown
et HTML.

## Commandes

| Commande | Rôle |
| --- | --- |
| `add-toc`        | Ajouter TOC, détection auto MD/HTML |
| `add-toc4md`     | TOC dans un Markdown |
| `add-toc4html`   | TOC dans un HTML |
| `add-itoc`       | Liens retour `[↑]` après chaque titre, auto MD/HTML |
| `add-itoc4md`    | iTOC dans Markdown |
| `check-toc4md`   | Vérifier présence d'une TOC |
| `check-itoc4md`  | Vérifier présence d'iTOC |

## Modules

- `core/markdown_toc_generator.py` : `add_toc_to_markdown_logic(...)`
- `core/markdown_itoc.py` : `add_toc_backlinks_logic(...)`
- `core/html_toc_generator.py` : équivalent HTML

Ces modules sont aussi importés par :

- `app.processing.commands.md_to_interactive_html` (pipeline TOC + iTOC + HTML interactif)
- `app.gitlab.commands.gitlab_clone` (post-traitement automatique avec `-E`)
- `app.mcp.core.server` (outil MCP `add_toc_to_markdown`)
