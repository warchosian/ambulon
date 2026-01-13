"""Module Conversion pour Ambulon - Conversion de formats de fichiers."""

# PDF et images
from .commands.compress_pdf import main as compress_pdf_main
from .commands.img2pdf import main as img2pdf_main
from .commands.pdf2html import convert_pdf_to_html
from .commands.pdf2html import main as pdf2html_main
from .commands.pdf2md import main as pdf2md_main

# HTML <-> Markdown
from .commands.html2md import process_html_to_markdown
from .commands.md2html import process_markdown_to_html

# HTML -> PDF
from .commands.html2pdf import convert_html_to_pdf

# JSON conversions
from .commands.json2jsonl import json_to_jsonl
from .commands.json2md import process_json_to_markdown

__all__ = [
    # PDF et images
    'compress_pdf_main',
    'img2pdf_main',
    'convert_pdf_to_html',
    'pdf2html_main',
    'pdf2md_main',
    # HTML <-> Markdown
    'process_html_to_markdown',
    'process_markdown_to_html',
    # HTML -> PDF
    'convert_html_to_pdf',
    # JSON
    'json_to_jsonl',
    'process_json_to_markdown',
]
