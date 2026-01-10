"""
Command to flatten a Markdown directory structure.

This module copies all .md files from a nested directory structure
to a flat directory with filenames based on their paths, and adapts
internal Markdown links to work in the flattened structure.

Examples:
    doc/Getting-Started/Quick-Start.md → doc-flattened/Getting-Started.Quick-Start.md
    doc/RAG-System/Chunking/Algorithm.md → doc-flattened/RAG-System.Chunking.Algorithm.md
"""

import sys
import shutil
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use in filenames.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string safe for filenames
    """
    # Replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name


def flatten_md_path(relative_path: Path) -> str:
    """
    Convert a relative path to a flattened filename using dots as separators.

    Examples:
        Getting-Started/Quick-Start.md → Getting-Started.Quick-Start.md
        RAG-System/Chunking/Algorithm.md → RAG-System.Chunking.Algorithm.md
        README.md → README.md

    Args:
        relative_path: Path relative to source root

    Returns:
        Flattened filename
    """
    parts = list(relative_path.parts)

    # Get filename without extension
    filename = parts[-1]
    stem = Path(filename).stem
    suffix = Path(filename).suffix

    # Get directory path (all parts except the last one)
    dir_parts = parts[:-1]

    if not dir_parts:
        # File at root level
        return filename

    # Sanitize each directory part
    sanitized_dirs = [sanitize_filename(part) for part in dir_parts]

    # Join directory parts with dots and add filename
    flattened = '.'.join(sanitized_dirs) + '.' + filename

    return flattened


def collect_md_files(
    source_dir: Path,
    verbose: bool = False
) -> List[Tuple[Path, str, Path]]:
    """
    Collect all .md files and their flattened names.

    Args:
        source_dir: Root source directory
        verbose: Print progress

    Returns:
        List of (source_path, flattened_name, relative_path) tuples
    """
    files = []

    # Find all .md files recursively
    md_files = list(source_dir.rglob('*.md'))

    if verbose:
        print(f"[INFO] Found {len(md_files)} Markdown files")

    for file_path in md_files:
        # Get relative path from source_dir
        relative_path = file_path.relative_to(source_dir)

        # Generate flattened name
        flattened_name = flatten_md_path(relative_path)

        files.append((file_path, flattened_name, relative_path))

    return files


def build_link_mapping(files: List[Tuple[Path, str, Path]]) -> Dict[Path, str]:
    """
    Build a mapping from relative paths to flattened names.

    Args:
        files: List of (source_path, flattened_name, relative_path) tuples

    Returns:
        Dictionary mapping relative_path → flattened_name
    """
    mapping = {}
    for source_path, flattened_name, relative_path in files:
        mapping[relative_path] = flattened_name
    return mapping


def adapt_markdown_links(
    content: str,
    current_relative_path: Path,
    link_mapping: Dict[Path, str],
    source_dir: Path,
    verbose: bool = False
) -> str:
    """
    Adapt Markdown links in content to work in flattened structure.

    Args:
        content: Markdown content
        current_relative_path: Relative path of current file
        link_mapping: Mapping of relative paths to flattened names
        source_dir: Source directory root
        verbose: Print adaptation details

    Returns:
        Content with adapted links
    """
    # Pattern to match Markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    adapted_count = 0
    external_count = 0

    def replace_link(match):
        nonlocal adapted_count, external_count

        link_text = match.group(1)
        link_url = match.group(2)

        # Skip if it's an absolute URL (http://, https://, etc.)
        if '://' in link_url or link_url.startswith('#'):
            return match.group(0)

        # Parse the link (might have anchor)
        if '#' in link_url:
            link_path, anchor = link_url.split('#', 1)
            has_anchor = True
        else:
            link_path = link_url
            anchor = ''
            has_anchor = False

        # Skip empty links
        if not link_path:
            return match.group(0)

        # Resolve the link relative to current file
        current_dir = current_relative_path.parent

        try:
            # Resolve relative path
            if link_path.startswith('./'):
                link_path = link_path[2:]
            elif link_path.startswith('../'):
                pass  # Will be handled by resolve()

            # Calculate absolute path within source_dir
            absolute_link = (source_dir / current_dir / link_path).resolve()

            # Check if link is within source_dir
            try:
                link_relative = absolute_link.relative_to(source_dir)

                # Check if this file is in our mapping
                if link_relative in link_mapping:
                    # Internal link - adapt it
                    new_link = link_mapping[link_relative]
                    if has_anchor:
                        new_link = f"{new_link}#{anchor}"

                    adapted_count += 1
                    return f"[{link_text}]({new_link})"
                else:
                    # File exists but not in mapping (not a .md file)
                    # Keep original link
                    external_count += 1
                    return match.group(0)

            except ValueError:
                # Link points outside source_dir - keep as is
                external_count += 1
                return match.group(0)

        except Exception as e:
            if verbose:
                print(f"[WARN] Could not adapt link '{link_url}': {e}", file=sys.stderr)
            return match.group(0)

    # Replace all links
    adapted_content = re.sub(link_pattern, replace_link, content)

    if verbose and (adapted_count > 0 or external_count > 0):
        print(f"[INFO] {current_relative_path}: {adapted_count} links adapted, {external_count} kept")

    return adapted_content


def flatten_markdown_directory(
    source_dir: str,
    output_dir: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Flatten a Markdown directory structure.

    Args:
        source_dir: Source directory with nested .md files
        output_dir: Output directory (default: {source_dir}-flattened)
        verbose: Print detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        print(f"[ERROR] Source directory does not exist: {source_dir}", file=sys.stderr)
        return 1

    if not source_path.is_dir():
        print(f"[ERROR] Source path is not a directory: {source_dir}", file=sys.stderr)
        return 1

    # Determine output directory
    if output_dir:
        output_path = Path(output_dir).resolve()
    else:
        output_path = source_path.parent / f"{source_path.name}-flattened"

    if verbose:
        print(f"[INFO] Source: {source_path}")
        print(f"[INFO] Output: {output_path}")

    # Collect all .md files
    files = collect_md_files(source_path, verbose)

    if not files:
        print(f"[WARN] No Markdown files found in {source_dir}", file=sys.stderr)
        return 1

    # Build link mapping
    link_mapping = build_link_mapping(files)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\n[INFO] Flattening {len(files)} files...")

    # Copy and adapt files
    success_count = 0
    error_count = 0

    for source_file, flattened_name, relative_path in files:
        try:
            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Adapt links
            adapted_content = adapt_markdown_links(
                content,
                relative_path,
                link_mapping,
                source_path,
                verbose
            )

            # Write to output
            output_file = output_path / flattened_name
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(adapted_content)

            success_count += 1

            if verbose:
                print(f"[OK] {relative_path} → {flattened_name}")

        except Exception as e:
            error_count += 1
            print(f"[ERROR] Failed to process {relative_path}: {e}", file=sys.stderr)

    # Summary
    print(f"\n{'='*70}")
    print(f"Flattening complete")
    print(f"{'='*70}")
    print(f"Files processed:  {success_count}/{len(files)}")
    if error_count > 0:
        print(f"Errors:          {error_count}")
    print(f"Output directory: {output_path}")
    print(f"{'='*70}\n")

    return 0 if error_count == 0 else 1


def register_flatten_md_command(subparsers):
    """Register the flatten-md command."""
    parser = subparsers.add_parser(
        'flatten-md',
        help='Flatten a Markdown directory structure',
        description='Copy all .md files from nested directory to flat structure with adapted links'
    )

    parser.add_argument(
        'source',
        type=str,
        help='Source directory with nested .md files'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory (default: {source}-flattened)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    def execute(args):
        return flatten_markdown_directory(
            args.source,
            args.output,
            args.verbose
        )

    parser.set_defaults(func=execute)


if __name__ == '__main__':
    # Allow running as standalone script
    import argparse
    parser = argparse.ArgumentParser(
        description="Flatten a Markdown directory structure"
    )
    parser.add_argument('source', help='Source directory')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    sys.exit(flatten_markdown_directory(args.source, args.output, args.verbose))
