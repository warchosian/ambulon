"""
Core logic for checking if inverse TOC (iTOC) links exist in Markdown files in Ambulon.
Detects back-to-TOC navigation links (↑) after headings.
"""

import re
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict

logger = logging.getLogger(__name__)


def detect_itoc_links(md_content: str, link_pattern: str = r'\[↑\]\(#[^\)]+\)') -> Dict[str, any]:
    """
    Detect inverse TOC (back-to-TOC) links in Markdown content.

    Args:
        md_content: Markdown content as string
        link_pattern: Regex pattern for iTOC links (default: [↑](#...))

    Returns:
        Dictionary with detection results
    """
    results = {
        'has_itoc_links': False,
        'itoc_count': 0,
        'headings_with_itoc': [],
        'headings_without_itoc': [],
        'total_headings': 0,
    }

    # Extract all headings
    heading_pattern = r'^(#{1,6})\s+(.+?)$'
    lines = md_content.split('\n')

    for line_num, line in enumerate(lines):
        match = re.match(heading_pattern, line)
        if match:
            results['total_headings'] += 1
            heading_level = len(match.group(1))
            heading_text = match.group(2).strip()

            # Check if this heading has an iTOC link
            if re.search(link_pattern, line):
                results['has_itoc_links'] = True
                results['itoc_count'] += 1
                results['headings_with_itoc'].append({
                    'level': heading_level,
                    'text': heading_text,
                    'line': line_num
                })
            else:
                results['headings_without_itoc'].append({
                    'level': heading_level,
                    'text': heading_text,
                    'line': line_num
                })

    return results


def check_itoc_exists_logic(
    input_file: Path,
    verbose: bool = False,
    min_coverage: float = 0.0,
    link_pattern: str = r'\[↑\]\(#[^\)]+\)'
) -> Tuple[int, Optional[Dict]]:
    """
    Core logic to check if inverse TOC links exist in a Markdown file.

    Args:
        input_file: Path to input Markdown file
        verbose: Enable verbose output
        min_coverage: Minimum percentage of headings that must have iTOC links (0.0-1.0)
        link_pattern: Regex pattern for iTOC links

    Returns:
        A tuple: (exit_code: int, detection_results: Optional[Dict])
        exit_code:
            - 0 if iTOC links exist and coverage >= min_coverage
            - 1 if no iTOC links found or coverage < min_coverage
            - 2 for errors
    """
    if not input_file.exists():
        logger.error(f"Error: Input file '{input_file}' does not exist.")
        return 2, None

    if not input_file.is_file():
        logger.error(f"Error: '{input_file}' is not a file.")
        return 2, None

    logger.info(f"Checking iTOC links in: {input_file}")

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

        # Detect iTOC links
        results = detect_itoc_links(md_content, link_pattern)

        # Calculate coverage
        if results['total_headings'] > 0:
            coverage = results['itoc_count'] / results['total_headings']
            results['coverage'] = coverage
        else:
            coverage = 0.0
            results['coverage'] = 0.0

        # Determine if iTOC exists based on coverage requirement
        itoc_exists = results['has_itoc_links'] and coverage >= min_coverage

        # Log results
        if itoc_exists:
            logger.info(f"✓ iTOC links found: {results['itoc_count']}/{results['total_headings']} headings ({coverage*100:.1f}% coverage)")
            if verbose and results['headings_without_itoc']:
                logger.info(f"  {len(results['headings_without_itoc'])} headings without iTOC links")
        else:
            if results['total_headings'] == 0:
                logger.info(f"✗ No headings found in file")
            elif not results['has_itoc_links']:
                logger.info(f"✗ No iTOC links found (0/{results['total_headings']} headings)")
            else:
                logger.info(f"✗ iTOC coverage too low: {coverage*100:.1f}% < {min_coverage*100:.1f}% required")
                logger.info(f"  Only {results['itoc_count']}/{results['total_headings']} headings have iTOC links")

        # Return appropriate exit code
        exit_code = 0 if itoc_exists else 1
        return exit_code, results

    except Exception as e:
        logger.error(f"Error: Failed to check iTOC: {e}", exc_info=True)
        return 2, None
