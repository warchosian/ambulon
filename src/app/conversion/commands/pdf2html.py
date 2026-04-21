"""
PDF to HTML Converter - Ambulon
Converts PDF files to HTML using PyMuPDF (fitz).
Follows the standard configuration hierarchy and logging practices.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# Setup logger for this module
logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "conversion": {
        "pdf2html": {
            "include_images": False,
            "page_numbers": True
        }
    }
}

def convert_pdf_to_html(
    input_file: Path,
    output_file: Path,
    include_images: bool,
    page_numbers: bool,
    verbose: bool = False
) -> Optional[Path]:
    """
    Core logic to convert a PDF file to an HTML file.
    Uses logging for status updates.

    Returns:
        The path to the output file on success, None on failure.
    """
    if fitz is None:
        logger.error("PyMuPDF (fitz) is not installed. Please install with: pip install PyMuPDF")
        return None

    try:
        logger.info(f"Starting PDF → HTML conversion for '{input_file.name}'")
        
        pdf_document = fitz.open(str(input_file))
        total_pages = len(pdf_document)
        logger.info(f"PDF has {total_pages} pages.")

        html_content = ["<!DOCTYPE html>", "<html lang='fr'>", "<head>",
                        "  <meta charset='UTF-8'>",
                        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
                        f"  <title>{input_file.stem}</title>",
                        "  <style>body { font-family: sans-serif; max-width: 900px; margin: auto; padding: 20px; line-height: 1.6; } .page { margin-bottom: 40px; padding: 20px; border: 1px solid #eee; } .page-number { color: #999; text-align: right; }</style>",
                        "</head>", "<body>", f"  <h1>{input_file.stem}</h1>"]

        for page_num in range(total_pages):
            page = pdf_document[page_num]
            if verbose:
                logger.debug(f"Processing page {page_num + 1}/{total_pages}...")

            html_content.append("  <div class='page'>")
            if page_numbers:
                html_content.append(f"    <div class='page-number'>Page {page_num + 1}</div>")
            
            text = page.get_text("html") # Use "html" output for better structure
            html_content.append(text)

            if include_images:
                # Image extraction logic (can be added here if needed)
                pass

            html_content.append("  </div>")

        html_content.append("</body></html>")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))

        pdf_document.close()
        return output_file

    except Exception as e:
        logger.error(f"An error occurred during PDF to HTML conversion: {e}", exc_info=True)
        return None

def main(argv=None):
    """
    CLI for converting a PDF file to HTML.

    Configuration Hierarchy (from highest to lowest priority):
    1. Command-line arguments (e.g., --output)
    2. YAML configuration file (`--config`)
    3. Environment variables (not yet implemented for this command)
    4. Default values
    """
    parser = argparse.ArgumentParser(
        description="""
Converts a PDF file to HTML.

Configuration Hierarchy (from highest to lowest priority):
1. Command-line arguments (e.g., --output)
2. YAML configuration file (--config)
3. Environment variables (not yet implemented for this command)
4. Default values
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input PDF file."
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output HTML file (default: same name with .html extension)."
    )
    parser.add_argument(
        "--include-images",
        action="store_true",
        help="Include images from the PDF."
    )
    parser.add_argument(
        "--page-numbers",
        action="store_true",
        default=DEFAULT_CONFIG['conversion']['pdf2html']['page_numbers'],
        help="Include page numbers in the output (default: True)."
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to a YAML configuration file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging."
    )

    args = parser.parse_args(argv)

    # Setup logging
    setup_logging(logging.DEBUG if args.verbose else logging.INFO, log_file_prefix="pdf2html")

    # Check if input file exists
    if not args.input_file.exists():
        logger.error(f"Input file does not exist: {args.input_file}")
        return 1
    if not args.input_file.is_file():
        logger.error(f"Path is not a file: {args.input_file}")
        return 1

    # Determine output path if not provided
    output_file = args.output
    if output_file is None:
        output_file = args.input_file.with_suffix('.html')

    # Config loading
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    final_include_images = args.include_images or config['conversion']['pdf2html'].get('include_images', False)
    final_page_numbers = args.page_numbers or config['conversion']['pdf2html'].get('page_numbers', True)

    # Execute conversion
    result_path = convert_pdf_to_html(
        input_file=args.input_file,
        output_file=output_file,
        include_images=final_include_images,
        page_numbers=final_page_numbers,
        verbose=args.verbose
    )

    if result_path:
        from app.core.output_paths import format_output_path
        relative_path = format_output_path(result_path)
        print(f"\n✓ Conversion réussie !\nFichier produit : {relative_path}")
        return 0
    else:
        logger.error("PDF to HTML conversion failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())