"""
Core logic for checking if a Table of Contents exists in Markdown files in Ambulon.
Detects TOC markers, HTML nav elements, and formatted TOC sections.
"""

import re
import logging
from pathlib import Path
from typing import Tuple, Optional, List, Dict

logger = logging.getLogger(__name__)


def detect_toc_markers(md_content: str) -> Dict[str, bool]:
    """
    Detect various TOC markers in Markdown content.

    Args:
        md_content: Markdown content as string

    Returns:
        Dictionary with detection results for different TOC types
    """
    results = {
        'toc_marker': False,          # [TOC] marker
        'html_nav': False,             # <nav class="table-of-contents">
        'markdown_toc_section': False, # ## Table des matières or ## Table of Contents
        'any_toc': False               # At least one type found
    }

    # Check for [TOC] marker
    if '[TOC]' in md_content or '[toc]' in md_content.lower():
        results['toc_marker'] = True
        logger.debug("Found [TOC] marker")

    # Check for HTML nav element with table-of-contents class or id
    html_nav_pattern = r'<nav[^>]*(?:class|id)=["\']?[^"\']*table-of-contents[^"\']*["\']?[^>]*>'
    if re.search(html_nav_pattern, md_content, re.IGNORECASE):
        results['html_nav'] = True
        logger.debug("Found HTML <nav> element with table-of-contents")

    # Check for Markdown TOC section (heading with "Table" and "matières" or "Contents")
    toc_heading_pattern = r'^#{1,6}\s+.*(?:table\s+(?:des?\s+)?mati[èe]res|table\s+of\s+contents).*$'
    if re.search(toc_heading_pattern, md_content, re.IGNORECASE | re.MULTILINE):
        results['markdown_toc_section'] = True
        logger.debug("Found Markdown TOC heading section")

    # Set any_toc flag
    results['any_toc'] = any([
        results['toc_marker'],
        results['html_nav'],
        results['markdown_toc_section']
    ])

    return results


def check_toc_exists_logic(
    input_file: Path,
    verbose: bool = False,
    strict: bool = False
) -> Tuple[int, Optional[Dict]]:
    """
    Core logic to check if a TOC exists in a Markdown file.

    Args:
        input_file: Path to input Markdown file
        verbose: Enable verbose output
        strict: In strict mode, only accept [TOC] marker or HTML nav (not Markdown sections)

    Returns:
        A tuple: (exit_code: int, detection_results: Optional[Dict])
        exit_code: 0 if TOC exists, 1 if no TOC found, 2 for errors
    """
    if not input_file.exists():
        logger.error(f"Error: Input file '{input_file}' does not exist.")
        return 2, None

    if not input_file.is_file():
        logger.error(f"Error: '{input_file}' is not a file.")
        return 2, None

    logger.info(f"Checking TOC in: {input_file}")

    try:
        # Read Markdown content
        encodings_to_try = ['utf-8', 'cp1252', 'latin-1', 'iso-8859-1']
        md_content = None

        for encoding in encodings_to_try:
            try:
                with open(input_file, 'r', encoding=encoding) as f:
                    md_content = f.read()
                if verbose and encoding != 'utf-8':
                    logger.info(f"File read with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue

        if md_content is None:
            logger.error(f"Error: Could not decode file with any supported encoding")
            return 2, None

        # Detect TOC markers
        results = detect_toc_markers(md_content)

        # Determine if TOC exists based on mode
        if strict:
            # Strict mode: only [TOC] marker or HTML nav
            toc_exists = results['toc_marker'] or results['html_nav']
        else:
            # Normal mode: any type of TOC
            toc_exists = results['any_toc']

        # Log results
        if toc_exists:
            logger.info(f"✓ TOC found in file")
            if verbose:
                if results['toc_marker']:
                    logger.info("  - [TOC] marker detected")
                if results['html_nav']:
                    logger.info("  - HTML <nav> element detected")
                if results['markdown_toc_section']:
                    logger.info("  - Markdown TOC section detected")
        else:
            logger.info(f"✗ No TOC found in file")
            if verbose:
                logger.info("  No TOC markers detected ([TOC], HTML nav, or TOC section)")

        # Return appropriate exit code
        exit_code = 0 if toc_exists else 1
        return exit_code, results

    except Exception as e:
        logger.error(f"Error: Failed to check TOC: {e}", exc_info=True)
        return 2, None
