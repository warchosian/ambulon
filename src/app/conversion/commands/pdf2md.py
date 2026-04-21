"""
PDF to Markdown Converter - Ambulon

Converts PDF files to Markdown.
Uses PyMuPDF (fitz) for content extraction.
"""
import sys
import os
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def convert_pdf_to_markdown(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> Optional[Path]:
    """
    Converts a PDF file to a Markdown file.

    Args:
        input_file: Path to the input PDF file.
        output_file: Path to the output Markdown file (optional).
        verbose: Enable detailed messages.

    Returns:
        The path to the output file on success, None on failure.
    """
    if fitz is None:
        print("Error: PyMuPDF (fitz) is not installed.", file=sys.stderr)
        print("Install with: pip install PyMuPDF", file=sys.stderr)
        return None

    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: PDF file not found: {input_file}", file=sys.stderr)
        return None

    if output_file is None:
        output_file = str(input_path.with_suffix('.md'))
    output_path = Path(output_file)

    try:
        if verbose:
            print(f"Converting PDF → Markdown")
            print(f"  Input: {input_path}")
            print(f"  Output: {output_path}")

        pdf_document = fitz.open(str(input_path))
        total_pages = len(pdf_document)

        if verbose:
            print(f"  Pages: {total_pages}")

        markdown_content = []
        for page_num in range(total_pages):
            page = pdf_document[page_num]
            if verbose and (page_num + 1) % 10 == 0:
                print(f"  Processing page {page_num + 1}/{total_pages}...")
            
            # Simple text extraction for now
            text = page.get_text("text")
            markdown_content.append(text)
            # Add a page break for clarity, can be removed if not desired
            if page_num < total_pages - 1:
                markdown_content.append("\n---\n")

        # Write the Markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_content))

        pdf_document.close()

        return output_path

    except Exception as e:
        print(f"Error: An error occurred during conversion: {e}", file=sys.stderr)
        import traceback
        if verbose:
            traceback.print_exc()
        return None

def main():
    """CLI entry point for PDF to Markdown conversion."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert a PDF to a Markdown file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my_document.pdf
  %(prog)s my_document.pdf -o my_document.md
  %(prog)s my_document.pdf --verbose
        """
    )

    parser.add_argument('input_file', help='Input PDF file')
    parser.add_argument('-o', '--output', dest='output_file',
                        help='Output Markdown file (default: same name with .md extension)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')

    args = parser.parse_args()

    output_path = convert_pdf_to_markdown(
        input_file=args.input_file,
        output_file=args.output_file,
        verbose=args.verbose
    )

    if output_path:
        from app.core.output_paths import format_output_path
        relative_path = format_output_path(output_path)
        print(f"\n✓ Conversion successful!\nFile produced: {relative_path}")
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
