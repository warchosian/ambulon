"""
Command to flatten an HTML directory structure.

This module copies all .html files from a nested directory structure
to a flat directory with filenames based on their paths, and adapts
internal HTML links to work in the flattened structure.

Examples:
    doc/getting-started/index.html → doc-flattened/getting-started.index.html
    doc/api/methods/detail.html → doc-flattened/api.methods.detail.html
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


def flatten_html_path(relative_path: Path) -> str:
    """
    Convert a relative path to a flattened filename using dots as separators.

    Examples:
        getting-started/index.html → getting-started.index.html
        api/methods/detail.html → api.methods.detail.html
        index.html → index.html

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


def collect_html_files(
    source_dir: Path,
    verbose: bool = False
) -> List[Tuple[Path, str, Path]]:
    """
    Collect all .html files and their flattened names.

    Args:
        source_dir: Root source directory
        verbose: Print progress

    Returns:
        List of (source_path, flattened_name, relative_path) tuples
    """
    files = []

    # Find all .html files recursively
    html_files = list(source_dir.rglob('*.html'))

    if verbose:
        print(f"[INFO] Found {len(html_files)} HTML files")

    for file_path in html_files:
        # Get relative path from source_dir
        relative_path = file_path.relative_to(source_dir)

        # Generate flattened name
        flattened_name = flatten_html_path(relative_path)

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


def adapt_html_links(
    content: str,
    current_relative_path: Path,
    link_mapping: Dict[Path, str],
    source_dir: Path,
    verbose: bool = False
) -> str:
    """
    Adapt HTML links in content to work in flattened structure.

    Only adapts href attributes pointing to other HTML files.
    Preserves all asset references (CSS, JS, images, etc.).

    Args:
        content: HTML content
        current_relative_path: Relative path of current file
        link_mapping: Mapping of relative paths to flattened names
        source_dir: Source directory root
        verbose: Print adaptation details

    Returns:
        Content with adapted links
    """
    # Asset extensions to always preserve
    ASSET_EXTENSIONS = {
        '.css', '.js',  # Stylesheets and scripts
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp',  # Images
        '.woff', '.woff2', '.ttf', '.eot',  # Fonts
        '.mp4', '.webm', '.ogg', '.mp3', '.wav',  # Media
        '.pdf', '.zip', '.tar', '.gz',  # Documents/Archives
    }

    # Pattern to match href attributes: href="..." or href='...'
    link_pattern = r'href=["\']([^"\']+)["\']'

    adapted_count = 0
    preserved_count = 0

    def replace_link(match):
        nonlocal adapted_count, preserved_count

        href = match.group(1)

        # 1. Skip absolute URLs (http://, https://, //, etc.)
        if '://' in href or href.startswith('//'):
            preserved_count += 1
            return match.group(0)

        # 2. Skip anchor-only links
        if href.startswith('#'):
            preserved_count += 1
            return match.group(0)

        # 3. Parse href (might have anchor or query params)
        # Split on # and ? to get the path part
        path_part = href.split('#')[0].split('?')[0]

        # 4. Skip empty paths
        if not path_part:
            preserved_count += 1
            return match.group(0)

        # 5. Check if this is an asset by extension
        path_lower = path_part.lower()
        if any(path_lower.endswith(ext) for ext in ASSET_EXTENSIONS):
            # This is an asset reference - preserve it
            preserved_count += 1
            return match.group(0)

        # 6. Extract anchor and query parts (if any)
        anchor = ''
        query = ''

        if '#' in href and '?' in href:
            # Both anchor and query present
            base_and_query = href.split('#')
            path_and_query = base_and_query[0].split('?')
            path_part = path_and_query[0]
            query = path_and_query[1] if len(path_and_query) > 1 else ''
            anchor = base_and_query[1].split('?')[0] if '?' not in base_and_query[1] else base_and_query[1]
        elif '#' in href:
            # Only anchor present
            parts = href.split('#', 1)
            path_part = parts[0]
            anchor = parts[1]
        elif '?' in href:
            # Only query present
            parts = href.split('?', 1)
            path_part = parts[0]
            query = parts[1]

        # 7. Check if it's an HTML file (explicitly .html/.htm or no extension)
        is_html = (path_lower.endswith('.html') or
                   path_lower.endswith('.htm') or
                   ('.' not in Path(path_part).name))  # No extension might be HTML

        if not is_html:
            # Not HTML and not a known asset - preserve as-is
            preserved_count += 1
            return match.group(0)

        # 8. Resolve the link relative to current file
        current_dir = current_relative_path.parent

        try:
            # Clean up ./ prefix
            if path_part.startswith('./'):
                path_part = path_part[2:]

            # Calculate absolute path within source_dir
            absolute_link = (source_dir / current_dir / path_part).resolve()

            # Check if link is within source_dir
            try:
                link_relative = absolute_link.relative_to(source_dir)

                # Check if this file is in our mapping (it's an HTML file we're flattening)
                if link_relative in link_mapping:
                    # Internal HTML link - adapt it
                    new_link = link_mapping[link_relative]

                    # Rebuild with anchor and query if present
                    if anchor and query:
                        new_link = f"{new_link}?{query}#{anchor}"
                    elif anchor:
                        new_link = f"{new_link}#{anchor}"
                    elif query:
                        new_link = f"{new_link}?{query}"

                    adapted_count += 1
                    return f'href="{new_link}"'
                else:
                    # File exists but not in mapping (not an .html file we're processing)
                    preserved_count += 1
                    return match.group(0)

            except ValueError:
                # Link points outside source_dir - preserve
                preserved_count += 1
                return match.group(0)

        except Exception as e:
            if verbose:
                print(f"[WARN] Could not adapt link '{href}': {e}", file=sys.stderr)
            preserved_count += 1
            return match.group(0)

    # Replace all href attributes
    adapted_content = re.sub(link_pattern, replace_link, content)

    if verbose and (adapted_count > 0 or preserved_count > 0):
        print(f"[INFO] {current_relative_path}: {adapted_count} links adapted, {preserved_count} preserved")

    return adapted_content


def flatten_html_directory(
    source_dir: str,
    output_dir: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Flatten an HTML directory structure.

    Args:
        source_dir: Source directory with nested .html files
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

    # Collect all .html files
    files = collect_html_files(source_path, verbose)

    if not files:
        print(f"[WARN] No HTML files found in {source_dir}", file=sys.stderr)
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
            adapted_content = adapt_html_links(
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


def register_flatten_html_command(subparsers):
    """Register the flatten-html command."""
    parser = subparsers.add_parser(
        'flatten-html',
        help='Flatten an HTML directory structure',
        description='Copy all .html files from nested directory to flat structure with adapted links'
    )

    parser.add_argument(
        'source',
        type=str,
        help='Source directory with nested .html files'
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
        return flatten_html_directory(
            args.source,
            args.output,
            args.verbose
        )

    parser.set_defaults(func=execute)


if __name__ == '__main__':
    # Allow running as standalone script
    import argparse
    parser = argparse.ArgumentParser(
        description="Flatten an HTML directory structure"
    )
    parser.add_argument('source', help='Source directory')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    sys.exit(flatten_html_directory(args.source, args.output, args.verbose))
