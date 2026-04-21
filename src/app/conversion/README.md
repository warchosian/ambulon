# app.conversion

Conversions de formats documentaires.

## Commandes

| Commande | Rôle | Handler |
| --- | --- | --- |
| `img2pdf`         | Images d'un dossier → PDF unique | `img2pdf_main` |
| `compress-pdf`    | Compression d'un PDF via PyMuPDF | `compress_pdf_main` |
| `pdf2html`        | PDF → HTML | `pdf2html_main` |
| `pdf2md`          | PDF → Markdown | `pdf2md_main` |
| `html2md`         | HTML → Markdown | `process_html_to_markdown` |
| `md2html`         | Markdown → HTML **sans** diagrammes | `process_markdown_to_html_simple` |
| `md2html-diagrams`| Markdown → HTML **avec** PlantUML/Mermaid/Graphviz en SVG | voir `app.diagrams` |
| `html2pdf`        | HTML → PDF via Chromium (Playwright) ou wkhtmltopdf | `convert_html_to_pdf` |
| `json2jsonl`      | JSON (array) → JSONL | `json_to_jsonl` |
| `json2md`         | JSON → Markdown | `process_json_to_markdown` |

## Dépendances externes

- **Playwright Chromium** (recommandé pour `html2pdf`) :
  `poetry run playwright install chromium`
- **wkhtmltopdf** (fallback) : installer manuellement, passer le chemin via
  `--wkhtmltopdf-path` ou laisser la détection PATH.
- **PyMuPDF** (`pymupdf`) pour la compression et le parsing PDF.
