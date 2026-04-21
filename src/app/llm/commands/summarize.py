#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Summarize command for intelligently summarizing large code documentation files using LLM.

Usage:
    ambulon summarize -i sireines.code.md
    ambulon summarize -i sireines.code.md -o custom_output.md
    ambulon summarize --input sireines.code.md --chunk-size 100000
"""

import argparse
import logging
from pathlib import Path
import sys
import io

# Force UTF-8 encoding for stdout/stderr on Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Reconfigure stdout/stderr with UTF-8 and replace errors to avoid crashes
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from app.llm.preprocessing.document_summarizer import summarize_document

logger = logging.getLogger(__name__)


def get_output_filename(input_file: str) -> str:
    """
    Generate output filename with .summarized.md extension.

    Args:
        input_file: Input file path

    Returns:
        Output filename with .summarized.md extension

    Examples:
        sireines.code.md -> sireines.code.summarized.md
        project.md -> project.summarized.md
    """
    input_path = Path(input_file)

    # Remove .md extension if present
    stem = input_path.stem
    if stem.endswith('.md'):
        stem = stem[:-3]

    # Add .summarized.md extension
    output_name = f"{stem}.summarized.md"

    # Keep in same directory as input
    return str(input_path.parent / output_name)


def main(argv=None):
    """
    Summarize command entry point.

    Args:
        argv: Command line arguments (for testing). ``None`` uses ``sys.argv``.
    """
    parser = argparse.ArgumentParser(
        description="Intelligently summarize large code documentation files using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ambulon summarize -i workplace-ambulon/gitlab/sireines.rag/sireines.code.md
  ambulon summarize -i myproject.code.md -o summary.md
  ambulon summarize -i large.code.md --chunk-size 100000

Output:
  Creates a summarized version with .summarized.md extension by default.
  Example: sireines.code.md -> sireines.code.summarized.md

Note:
  This command uses the configured LLM provider (see config/llm.yaml).
  Large files will be chunked and each chunk summarized separately.
"""
    )

    parser.add_argument(
        '-i', '--input',
        required=True,
        metavar='FILE',
        help='Input code documentation file (usually .code.md)'
    )

    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='Output file (default: <input>.summarized.md)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=50000,
        metavar='CHARS',
        help='Maximum characters per chunk (default: 50000)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parsed_args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Determine output file
    input_file = parsed_args.input
    output_file = parsed_args.output if parsed_args.output else get_output_filename(input_file)

    # Validate input
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    logger.info(f"[START] Document summarization")
    logger.info(f"Input: {input_file}")
    logger.info(f"Output: {output_file}")
    logger.info(f"Chunk size: {parsed_args.chunk_size} characters")

    print(f"\n📄 Document Summarizer (LLM-powered)")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Chunk size: {parsed_args.chunk_size} characters")
    print("=" * 70)

    try:
        # Run summarization
        print("\n🤖 Analyzing document with LLM...")
        stats = summarize_document(input_file, output_file, chunk_size=parsed_args.chunk_size)

        # Display results
        print(f"\n✓ Summarization completed successfully!")
        print(f"\n📊 Statistics:")
        print(f"   Chunks processed: {stats['chunks']}")
        print(f"   LLM Provider: {stats['provider']}")
        print(f"   Model: {stats['model']}")
        print(f"   Output: {output_file}")

        logger.info(f"[SUCCESS] Summarization completed")
        logger.info(f"Chunks: {stats['chunks']}, Provider: {stats['provider']}")

    except Exception as e:
        logger.error(f"[ERROR] Summarization failed: {e}", exc_info=parsed_args.verbose)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
