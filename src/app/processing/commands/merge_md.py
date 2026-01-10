"""
Command to merge/fusion multiple Markdown files into a single document.

This module reads all .md files from a flat directory, merges them into
a single Markdown file with a table of contents, section identifiers,
and adapted internal links.

Example:
    doc-flat/ → doc-flattened-merged/merged.md
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def sanitize_anchor(text: str) -> str:
    """
    Convert text to a valid HTML anchor ID.

    Args:
        text: Text to convert

    Returns:
        Sanitized anchor ID
    """
    # Convert to lowercase
    anchor = text.lower()

    # Replace spaces and dots with hyphens
    anchor = anchor.replace(' ', '-').replace('.', '-')

    # Remove invalid characters
    anchor = re.sub(r'[^a-z0-9\-_]', '', anchor)

    # Remove multiple consecutive hyphens
    anchor = re.sub(r'-+', '-', anchor)

    # Remove leading/trailing hyphens
    anchor = anchor.strip('-')

    return anchor


def create_file_anchor(filename: str) -> str:
    """
    Create an anchor ID from a filename.

    Args:
        filename: Original filename (e.g., "Getting-Started.Quick-Start.md")

    Returns:
        Anchor ID (e.g., "getting-started-quick-start")
    """
    stem = Path(filename).stem
    return sanitize_anchor(stem)


def check_code_blocks_balanced(file_path: Path) -> Tuple[bool, int]:
    """
    Check if a markdown file has balanced code blocks.

    Args:
        file_path: Path to markdown file

    Returns:
        Tuple of (is_balanced, backtick_count)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    backtick_count = content.count('```')
    is_balanced = backtick_count % 2 == 0

    return is_balanced, backtick_count


def collect_markdown_files(
    source_dir: Path,
    verbose: bool = False
) -> List[Tuple[Path, str]]:
    """
    Collect all .md files and sort them alphabetically.

    Args:
        source_dir: Source directory with .md files
        verbose: Print progress

    Returns:
        List of (file_path, filename) tuples sorted alphabetically
    """
    md_files = []

    for md_file in source_dir.glob('*.md'):
        md_files.append((md_file, md_file.name))

    # Sort alphabetically by filename
    md_files.sort(key=lambda x: x[1])

    if verbose:
        print(f"[INFO] Found {len(md_files)} Markdown files to merge")

    return md_files


def validate_markdown_files(
    files: List[Tuple[Path, str]],
    verbose: bool = False
) -> Tuple[List[Tuple[Path, str]], List[str]]:
    """
    Validate markdown files for balanced code blocks.

    Args:
        files: List of (file_path, filename) tuples
        verbose: Print validation details

    Returns:
        Tuple of (valid_files, unbalanced_filenames)
    """
    valid_files = []
    unbalanced_files = []

    for file_path, filename in files:
        is_balanced, backtick_count = check_code_blocks_balanced(file_path)

        if is_balanced:
            valid_files.append((file_path, filename))
        else:
            unbalanced_files.append(filename)
            if verbose:
                print(f"[WARN] {filename}: {backtick_count} backticks (unbalanced - excluded)", file=sys.stderr)

    return valid_files, unbalanced_files


def adapt_links_for_fusion(
    content: str,
    current_file: str,
    file_anchors: Dict[str, str],
    verbose: bool = False
) -> str:
    """
    Adapt Markdown links to work in fused document.

    Internal links to other .md files are converted to anchor links.
    External links and anchor-only links are preserved.

    Args:
        content: Markdown content
        current_file: Current filename
        file_anchors: Mapping of filename → anchor ID
        verbose: Print adaptation details

    Returns:
        Content with adapted links
    """
    # Pattern to match Markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    adapted_count = 0

    def replace_link(match):
        nonlocal adapted_count

        link_text = match.group(1)
        link_url = match.group(2)

        # Skip absolute URLs (http://, https://, etc.)
        if '://' in link_url:
            return match.group(0)

        # Check if it's an anchor-only link
        if link_url.startswith('#'):
            return match.group(0)

        # Parse the link (might have anchor)
        if '#' in link_url:
            link_file, anchor = link_url.split('#', 1)
        else:
            link_file = link_url
            anchor = ''

        # Skip empty links
        if not link_file:
            return match.group(0)

        # Check if this is a link to another .md file
        if link_file.endswith('.md'):
            # Get the target anchor
            if link_file in file_anchors:
                target_anchor = file_anchors[link_file]

                # If there's an additional anchor, append it
                if anchor:
                    new_link = f"#{target_anchor}-{anchor}"
                else:
                    new_link = f"#{target_anchor}"

                adapted_count += 1
                return f"[{link_text}]({new_link})"

        # Keep link as is (external or other)
        return match.group(0)

    adapted_content = re.sub(link_pattern, replace_link, content)

    if verbose and adapted_count > 0:
        print(f"[INFO] {current_file}: {adapted_count} links adapted")

    return adapted_content


def generate_table_of_contents(
    files: List[Tuple[Path, str]],
    file_anchors: Dict[str, str]
) -> str:
    """
    Generate table of contents for the fused document.

    Args:
        files: List of (file_path, filename) tuples
        file_anchors: Mapping of filename → anchor ID

    Returns:
        Table of contents as Markdown
    """
    toc_lines = [
        "# 📚 Table des matières",
        "",
        "> Document fusionné généré automatiquement",
        "",
    ]

    for file_path, filename in files:
        anchor = file_anchors[filename]
        stem = Path(filename).stem

        # Create a readable title from the filename
        title = stem.replace('.', ' › ')

        toc_lines.append(f"- [{title}](#{anchor})")

    toc_lines.append("")
    toc_lines.append("---")
    toc_lines.append("")

    return '\n'.join(toc_lines)


def create_section_separator(filename: str, anchor: str) -> str:
    """
    Create a section separator with file identification.

    Args:
        filename: Original filename
        anchor: Anchor ID for this section

    Returns:
        Section separator as Markdown
    """
    stem = Path(filename).stem
    title = stem.replace('.', ' › ')

    separator = [
        "",
        "---",
        "",
        f'<a id="{anchor}"></a>',
        "",
        f"# 📄 {title}",
        "",
        f"> **Source :** `{filename}`",
        "",
    ]

    return '\n'.join(separator)


def fusion_markdown_files(
    source_dir: str,
    output_dir: Optional[str] = None,
    output_name: str = "merged.md",
    verbose: bool = False
) -> int:
    """
    Merge multiple Markdown files into a single fused document.

    Args:
        source_dir: Source directory with .md files
        output_dir: Output directory (default: {source_dir}-merged)
        output_name: Name of output file (default: merged.md)
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
        output_path = source_path.parent / f"{source_path.name}-merged"

    if verbose:
        print(f"[INFO] Source: {source_path}")
        print(f"[INFO] Output: {output_path}")

    # Collect all .md files
    all_files = collect_markdown_files(source_path, verbose)

    if not all_files:
        print(f"[ERROR] No Markdown files found in {source_dir}", file=sys.stderr)
        return 1

    # Validate files for balanced code blocks
    files, unbalanced_files = validate_markdown_files(all_files, verbose)

    if unbalanced_files:
        print(f"\n[WARN] {len(unbalanced_files)} file(s) excluded due to unbalanced code blocks:", file=sys.stderr)
        for filename in unbalanced_files:
            print(f"  - {filename}", file=sys.stderr)
        print(f"[WARN] Fix unbalanced backticks (```) in these files before merging", file=sys.stderr)
        print()

    if not files:
        print(f"[ERROR] No valid Markdown files to merge (all files have unbalanced code blocks)", file=sys.stderr)
        return 1

    # Create anchor mapping
    file_anchors = {}
    for file_path, filename in files:
        anchor = create_file_anchor(filename)
        file_anchors[filename] = anchor

    if verbose:
        print(f"\n[INFO] Merging {len(files)} files...")

    # Generate table of contents
    toc = generate_table_of_contents(files, file_anchors)

    # Merge all files
    merged_content = [toc]
    success_count = 0
    error_count = 0

    for file_path, filename in files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Adapt links
            adapted_content = adapt_links_for_fusion(
                content,
                filename,
                file_anchors,
                verbose
            )

            # Create section separator
            anchor = file_anchors[filename]
            separator = create_section_separator(filename, anchor)

            # Add to merged content
            merged_content.append(separator)
            merged_content.append(adapted_content)

            success_count += 1

            if verbose:
                print(f"[OK] {filename}")

        except Exception as e:
            error_count += 1
            print(f"[ERROR] Failed to process {filename}: {e}", file=sys.stderr)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Write merged file
    output_file = output_path / output_name

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))

        if verbose:
            print(f"\n[OK] Merged content written to {output_file}")

    except Exception as e:
        print(f"[ERROR] Failed to write output file: {e}", file=sys.stderr)
        return 1

    # Summary
    print(f"\n{'='*70}")
    print(f"Merge complete")
    print(f"{'='*70}")
    print(f"Files merged:     {success_count}/{len(files)}")
    if len(unbalanced_files) > 0:
        print(f"Files excluded:   {len(unbalanced_files)} (unbalanced)")
    if error_count > 0:
        print(f"Errors:          {error_count}")
    print(f"Output file:     {output_file}")

    # Calculate file size
    file_size = output_file.stat().st_size
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"
    elif file_size > 1024:
        size_str = f"{file_size / 1024:.2f} KB"
    else:
        size_str = f"{file_size} bytes"

    print(f"File size:       {size_str}")
    print(f"{'='*70}\n")

    return 0 if error_count == 0 else 1


def register_merge_md_command(subparsers):
    """Register the merge-md command."""
    parser = subparsers.add_parser(
        'merge-md',
        help='Merge multiple Markdown files into a single fused document',
        description='Merge all .md files from a directory into one document with TOC and adapted links'
    )

    parser.add_argument(
        'source',
        type=str,
        help='Source directory with .md files'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory (default: {source}-merged)'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        default='merged.md',
        help='Output filename (default: merged.md)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    def execute(args):
        return fusion_markdown_files(
            args.source,
            args.output,
            args.name,
            args.verbose
        )

    parser.set_defaults(func=execute)


if __name__ == '__main__':
    # Allow running as standalone script
    import argparse
    parser = argparse.ArgumentParser(
        description="Merge Markdown files into a single fused document"
    )
    parser.add_argument('source', help='Source directory')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-n', '--name', default='merged.md', help='Output filename')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    sys.exit(fusion_markdown_files(args.source, args.output, args.name, args.verbose))
