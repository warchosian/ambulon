#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter command for preprocessing large code documentation files.

Usage:
    ambulon filter -i sireines.code.md
    ambulon filter -i sireines.code.md -o custom_output.md
    ambulon filter --input sireines.code.md --max-size 10000
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

from app.llm.preprocessing.document_filter import filter_document

logger = logging.getLogger(__name__)


def get_output_filename(input_file: str) -> str:
    """
    Generate output filename with .filtered.md extension.

    Args:
        input_file: Input file path

    Returns:
        Output filename with .filtered.md extension

    Examples:
        sireines.code.md -> sireines.code.filtered.md
        project.md -> project.filtered.md
    """
    input_path = Path(input_file)

    # Remove .md extension if present
    stem = input_path.stem
    if stem.endswith('.md'):
        stem = stem[:-3]

    # Add .filtered.md extension
    output_name = f"{stem}.filtered.md"

    # Keep in same directory as input
    return str(input_path.parent / output_name)


def main(argv=None):
    """
    Filter command entry point.

    Args:
        argv: Command line arguments (for testing). ``None`` uses ``sys.argv``.
    """
    parser = argparse.ArgumentParser(
        description="Filter large code documentation files to reduce size",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ambulon filter -i workplace-ambulon/gitlab/sireines.rag/sireines.code.md
  ambulon filter -i myproject.code.md -o output.md
  ambulon filter -i large.code.md --max-size 10000

Output:
  Creates a filtered version with .filtered.md extension by default.
  Example: sireines.code.md -> sireines.code.filtered.md
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
        help='Output file (default: <input>.filtered.md)'
    )

    parser.add_argument(
        '--max-size',
        type=int,
        default=5000,
        metavar='BYTES',
        help='Maximum file size to keep full content (default: 5000 bytes)'
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

    logger.info(f"[START] Document filtering")
    logger.info(f"Input: {input_file}")
    logger.info(f"Output: {output_file}")
    logger.info(f"Max file size: {parsed_args.max_size} bytes")

    print(f"\n📄 Document Filter")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Max size for full content: {parsed_args.max_size} bytes")
    print("=" * 70)

    try:
        # Run filtering
        print("\n🔍 Analyzing document...")
        stats = filter_document(input_file, output_file, max_file_size=parsed_args.max_size)

        # Display results
        print(f"\n✓ Filtering completed successfully!")
        print(f"\n📊 Statistics:")
        print(f"   Total files analyzed: {stats['total']}")
        print(f"   Files kept (full content): {stats['kept']}")
        print(f"   Files excluded (binary/generated): {stats['excluded']}")
        print(f"   Files omitted (non-priority): {stats['omitted']}")
        print(f"   Original size: {stats['total_size']/1024/1024:.2f} MB")
        print(f"   Filtered size: {stats['kept_size']/1024/1024:.2f} MB")

        reduction = (1 - stats['kept_size']/stats['total_size']) * 100 if stats['total_size'] > 0 else 0
        print(f"   Size reduction: {reduction:.1f}%")

        logger.info(f"[SUCCESS] Filtering completed")
        logger.info(f"Size reduction: {reduction:.1f}%")

    except Exception as e:
        logger.error(f"[ERROR] Filtering failed: {e}", exc_info=parsed_args.verbose)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
