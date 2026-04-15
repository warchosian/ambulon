"""
Core logic for merging multiple Markdown files into a single document in Ambulon.
Handles file collection, natural sorting, internal link adaptation, TOC generation,
and validation of code blocks.
"""

import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any

logger = logging.getLogger(__name__)


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

    # Replace spaces, dots, and double underscores with hyphens
    anchor = anchor.replace(' ', '-').replace('.', '-').replace('__', '-')

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

    # Count triple backticks that are actual code block delimiters
    # (ignore inline backticks like ` ``` ` in text)
    lines = content.split('\n')
    code_block_backticks = 0

    for line in lines:
        stripped = line.strip()
        # Count only lines that START with ``` (actual code blocks)
        # This filters out inline backticks like: "use ` ``` ` for code"
        if stripped.startswith('```'):
            code_block_backticks += 1

    is_balanced = code_block_backticks % 2 == 0

    return is_balanced, code_block_backticks


def natural_sort_key(s: str) -> List[Any]:
    """
    Create a sort key for natural string sorting (e.g., "file2.md" comes before "file10.md").
    """
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'([0-9]+)', s)]


def collect_markdown_files_for_merging(
    source_dir: Path,
) -> List[Tuple[Path, str]]:
    """
    Collect all .md files and sort them alphabetically.

    Args:
        source_dir: Source directory with .md files

    Returns:
        List of (file_path, filename) tuples sorted alphabetically
    """
    md_files = []

    for md_file in source_dir.glob('*.md'):
        md_files.append((md_file, md_file.name))

    # Sort with Home.md first, then alphabetically by filename
    def sort_key_with_home_first(item):
        """Sort key that puts Home.md first, then sorts alphabetically."""
        file_path, filename = item
        # Check if this is Home.md (case-insensitive)
        if filename.lower() == 'home.md':
            # Return a tuple that will sort before all others
            # Using empty string ensures it comes first
            return (0, '')
        else:
            # Regular files sort after Home (1 > 0)
            return (1, natural_sort_key(filename))

    md_files.sort(key=sort_key_with_home_first)

    logger.info(f"Found {len(md_files)} Markdown files to merge (Home.md first if present).")

    return md_files


def validate_markdown_files(
    files: List[Tuple[Path, str]],
) -> Tuple[List[Tuple[Path, str]], List[str]]:
    """
    Validate markdown files for balanced code blocks.

    Args:
        files: List of (file_path, filename) tuples

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
            logger.warning(f"{filename}: {backtick_count} backticks (unbalanced - excluded from merge)")

    return valid_files, unbalanced_files


def fix_nested_code_blocks(content: str) -> str:
    """
    Remove all ```markdown wrapper blocks to ensure proper rendering.

    In documentation/prompt files, ```markdown blocks are used to show examples,
    but when merged they prevent proper rendering of:
    - Special diagrams (mermaid, plantuml, etc.)
    - Nested code blocks (bash, python, etc.)
    - HTML tags (<details>, <code>, etc.)

    Strategy: Remove ALL ```markdown wrappers to let content render normally.

    Args:
        content: Markdown content

    Returns:
        Content with ```markdown wrappers removed
    """
    lines = content.split('\n')

    # Find all ```markdown blocks
    markdown_blocks_to_unwrap = []  # List of (start_idx, end_idx) tuples
    in_markdown_block = False
    markdown_block_start = -1

    for i, line in enumerate(lines):
        stripped = line.strip()

        if stripped == '```markdown':
            in_markdown_block = True
            markdown_block_start = i
        elif in_markdown_block and stripped == '```':
            # This closes the markdown block
            if markdown_block_start != -1:
                markdown_blocks_to_unwrap.append((markdown_block_start, i))
            in_markdown_block = False
            markdown_block_start = -1

    # If no markdown blocks to unwrap, return original content
    if not markdown_blocks_to_unwrap:
        return content

    # Remove the ```markdown and closing ``` for all blocks
    lines_to_skip = set()
    for start_idx, end_idx in markdown_blocks_to_unwrap:
        lines_to_skip.add(start_idx)  # Skip opening ```markdown
        lines_to_skip.add(end_idx)     # Skip closing ```

    result_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_skip:
            result_lines.append(line)

    fixed_count = len(markdown_blocks_to_unwrap)
    if fixed_count > 0:
        logger.info(f"Unwrapped {fixed_count} ```markdown block(s) - all content will render correctly")

    return '\n'.join(result_lines)


def adapt_links_for_fusion(
    content: str,
    current_file: str,
    file_anchors: Dict[str, str],
) -> str:
    """
    Adapt Markdown links in content to work in fused document.

    Internal links to other .md files are converted to anchor links.
    External links and anchor-only links are preserved.

    Args:
        content: Markdown content
        current_file: Current filename
        file_anchors: Mapping of filename → anchor ID

    Returns:
        Content with adapted links
    """
    # Pattern to match Markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'

    adapted_count = 0
    preserved_count = 0 # for external/unmatched links

    def replace_link(match):
        nonlocal adapted_count, preserved_count

        link_text = match.group(1)
        link_url = match.group(2)

        # Skip if it's an absolute URL (http://, https://, etc.)
        if '://' in link_url:
            preserved_count += 1
            return match.group(0)

        # Check if it's an anchor-only link
        if link_url.startswith('#'):
            preserved_count += 1
            return match.group(0)

        # Parse the link (might have anchor)
        if '#' in link_url:
            link_file, anchor = link_url.split('#', 1)
            has_anchor = True
        else:
            link_file = link_url
            anchor = ''
            has_anchor = False

        # Skip empty links
        if not link_file:
            preserved_count += 1
            return match.group(0)

        # Check if this is a link to another .md file
        matched_file = None

        # Try 1: Link already has .md extension
        if link_file.endswith('.md') and link_file in file_anchors:
            matched_file = link_file
        # Try 2: Try adding .md extension (for wiki links without extension)
        elif not link_file.endswith('.md'):
            link_with_md = link_file + '.md'
            if link_with_md in file_anchors:
                matched_file = link_with_md
                logger.debug(f"Wiki link without .md extension found: '{link_file}' → '{link_with_md}'")

        if matched_file:
            # Get the target anchor
            target_anchor = file_anchors[matched_file]

            # If there's an additional anchor, append it
            if anchor:
                new_link = f"#{target_anchor}-{anchor}"
            else:
                new_link = f"#{target_anchor}"

            adapted_count += 1
            logger.debug(f"Adapted link in {current_file}: '{link_url}' -> '{new_link}'")
            return f"[{link_text}]({new_link})"
        else:
            # Not a link to a file in our anchors, preserve as-is
            preserved_count += 1
            return match.group(0)


    adapted_content = re.sub(link_pattern, replace_link, content)

    if adapted_count > 0:
        logger.debug(f"File {current_file}: {adapted_count} links adapted, {preserved_count} external/preserved.")

    return adapted_content


def extract_headings_from_content(content: str, min_level: int = 2, max_level: int = 3) -> List[dict]:
    """
    Extract headings from markdown content.

    Args:
        content: Markdown content
        min_level: Minimum heading level to extract (default: 2 for H2)
        max_level: Maximum heading level to extract (default: 3 for H3)

    Returns:
        List of dicts with 'level', 'text', 'anchor'
    """
    headings = []
    lines = content.split('\n')

    # Pattern to match markdown headings: ## Heading, ### Heading, etc.
    heading_pattern = re.compile(r'^(#{2,6})\s+(.+?)(?:\s*\{#([a-zA-Z0-9\-_]+)\})?\s*(?:\[↑\]\(#[^\)]+\))?\s*$')

    for line in lines:
        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))  # Count number of #
            text = match.group(2).strip()
            custom_id = match.group(3)  # Custom ID if present

            # Only extract headings within specified range
            if min_level <= level <= max_level:
                # Generate anchor from text or use custom ID
                if custom_id:
                    anchor = custom_id
                else:
                    # Generate ID from heading text (same logic as sanitize_anchor)
                    anchor = text.lower()
                    anchor = anchor.replace(' ', '-').replace('.', '-').replace('__', '-')
                    anchor = re.sub(r'[^a-z0-9\-_àâäéèêëïîôùûüÿæœç]', '', anchor)
                    anchor = re.sub(r'-+', '-', anchor)
                    anchor = anchor.strip('-')

                headings.append({
                    'level': level,
                    'text': text,
                    'anchor': anchor
                })

    return headings


def generate_table_of_contents(
    files: List[Tuple[Path, str]],
    file_anchors: Dict[str, str],
    file_contents: Dict[str, str]
) -> str:
    """
    Generate table of contents for the fused document with 2 levels.

    Level 1: Merged file sections
    Level 2: H2 and H3 headings within each file (with TOC anchors)

    Args:
        files: List of (file_path, filename) tuples
        file_anchors: Mapping of filename → anchor ID
        file_contents: Mapping of filename → content

    Returns:
        Table of contents as HTML (for proper nested list rendering)
    """
    toc_lines = [
        "# 📚 Table des matières",
        "",
        "> Document fusionné généré automatiquement",
        "",
        '<div class="table-of-contents">',
        "<ul>",
    ]

    for file_path, filename in files:
        anchor = file_anchors[filename]
        stem = Path(filename).stem

        # Create a readable title from the filename (__ separates hierarchy levels)
        title = stem.replace('__', ' › ')

        # Level 1: File section
        toc_lines.append(f'<li><a href="#{anchor}">{title}</a>')

        # Level 2: Extract H2 and H3 from file content
        content = file_contents.get(filename, '')
        if content:
            headings = extract_headings_from_content(content, min_level=2, max_level=3)

            if headings:
                # Open nested list for H2/H3
                toc_lines.append("<ul>")

                current_level = None
                for heading in headings:
                    # Create TOC anchor ID for this heading
                    toc_anchor_id = f"toc-{heading['anchor']}"
                    level = heading['level']

                    # Handle H3 (need to nest further)
                    if level == 3 and current_level == 2:
                        # Open H3 sub-list
                        toc_lines.append("<ul>")
                    elif level == 2 and current_level == 3:
                        # Close H3 sub-list and go back to H2
                        toc_lines.append("</ul>")
                        toc_lines.append("</li>")
                    elif current_level == 3:
                        # Close previous H3 item
                        toc_lines.append("</li>")
                    elif current_level == 2 and level == 2:
                        # Close previous H2 item
                        toc_lines.append("</li>")

                    # Add the TOC entry
                    toc_lines.append(f'<li><span id="{toc_anchor_id}"></span><a href="#{heading["anchor"]}">{heading["text"]}</a>')

                    current_level = level

                # Close any remaining open tags
                if current_level == 3:
                    toc_lines.append("</ul>")
                    toc_lines.append("</li>")
                elif current_level == 2:
                    toc_lines.append("</li>")

                # Close nested list for H2/H3
                toc_lines.append("</ul>")

        # Close file section
        toc_lines.append("</li>")

    toc_lines.append("</ul>")
    toc_lines.append("</div>")
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
    # Transform __ separators into readable hierarchy (e.g., "config__gitlab" → "config › gitlab")
    title = stem.replace('__', ' › ')

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


def fusion_markdown_files_logic(
    source_dir: Path,
    output_file: Path,
    output_name: str = "merged.md",
    title: str = "Merged Markdown Document", # New title for Markdown
    force: bool = False,
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to merge multiple Markdown files into a single fused document.

    Args:
        source_dir: Source directory with .md files
        output_file: Output file path
        output_name: Name of output file (default: merged.md)
        title: Title for the merged Markdown document
        force: If True, overwrite output file if it exists (default: False)

    Returns:
        A tuple: (exit_code: int, generated_path: Optional[Path])
    """
    # Fix encoding for Windows console (moved from CLI to here as it's a core concern)
    if sys.platform == 'win32':
        import codecs
        stdout_buffer = getattr(sys.stdout, "buffer", None)
        stderr_buffer = getattr(sys.stderr, "buffer", None)
        if stdout_buffer is not None:
            sys.stdout = codecs.getwriter('utf-8')(stdout_buffer, 'strict')
        if stderr_buffer is not None:
            sys.stderr = codecs.getwriter('utf-8')(stderr_buffer, 'strict')

    source_path = source_dir.resolve()

    if not source_path.exists():
        logger.error(f"Error: Source directory does not exist: {source_dir}.")
        return 1, None

    if not source_path.is_dir():
        logger.error(f"Error: '{source_dir}' is not a directory.")
        return 1, None

    logger.info(f"Source directory: {source_path}")
    logger.info(f"Output file: {output_file}")

    # Collect all .md files
    all_files = collect_markdown_files_for_merging(source_path)

    if not all_files:
        logger.warning(f"No Markdown files found in '{source_dir}'. Nothing to merge.")
        return 1, None

    # Validate files for balanced code blocks
    files, unbalanced_files = validate_markdown_files(all_files)

    if unbalanced_files:
        logger.warning(f"{len(unbalanced_files)} file(s) excluded from merge due to unbalanced code blocks:")
        for filename in unbalanced_files:
            logger.warning(f"  - {filename}")
        logger.warning("Fix unbalanced backticks (```) in these files before merging.")

    if not files:
        logger.error(f"No valid Markdown files to merge (all files have unbalanced code blocks).")
        return 1, None

    # Create anchor mapping
    file_anchors = {}
    for file_path, filename in files:
        anchor = create_file_anchor(filename)
        file_anchors[filename] = anchor
    logger.debug(f"Generated file anchors for {len(file_anchors)} files.")

    # First pass: Read all files and store their content
    logger.info("Reading all files...")
    file_contents = {}  # Mapping of filename → original content
    file_adapted_contents = {}  # Mapping of filename → adapted content

    for file_path, filename in files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store original content for TOC generation
            file_contents[filename] = content

            # Fix nested code blocks (mermaid inside markdown, etc.)
            content = fix_nested_code_blocks(content)

            # Adapt links
            adapted_content = adapt_links_for_fusion(
                content,
                filename,
                file_anchors,
            )

            # Store adapted content for final merge
            file_adapted_contents[filename] = adapted_content

            logger.debug(f"Read: {filename}")

        except Exception as e:
            logger.error(f"Failed to read {filename}: {e}", exc_info=True)
            file_contents[filename] = ''
            file_adapted_contents[filename] = ''

    # Generate table of contents with 2 levels (files + their headings)
    logger.info("Generating Table of Contents with sub-headings...")
    toc = generate_table_of_contents(files, file_anchors, file_contents)

    # Second pass: Build final merged content
    logger.info("Merging all content...")
    merged_content_parts = [toc]
    success_count = 0
    error_count = 0

    for file_path, filename in files:
        try:
            adapted_content = file_adapted_contents.get(filename, '')

            if not adapted_content:
                error_count += 1
                continue

            # Create section separator
            anchor = file_anchors[filename]
            separator = create_section_separator(filename, anchor)

            # Add to merged content
            merged_content_parts.append(separator)
            merged_content_parts.append(adapted_content)

            success_count += 1
            logger.info(f"Processed: {filename}")

        except Exception as e:
            error_count += 1
            logger.error(f"Failed to process {filename}: {e}", exc_info=True)

    final_markdown_content = '\n'.join(merged_content_parts)

    if not final_markdown_content.strip():
        logger.warning("Merged content is empty. No output file will be written.")
        return 1, None

    # Ensure output directory exists
    try:
        # Check if parent exists as a file (not a directory)
        if output_file.parent.exists() and output_file.parent.is_file():
            logger.error(f"Cannot create output file: parent path '{output_file.parent}' exists as a file, not a directory.")
            logger.error(f"Output file would be: {output_file}")
            logger.error(f"Hint: The output path may be incorrectly constructed. Check if you meant to specify a file path ending in .md")
            return 1, None

        output_file.parent.mkdir(parents=True, exist_ok=True)
    except FileExistsError as e:
        logger.error(f"Cannot create output directory '{output_file.parent}': path exists as a file.")
        logger.error(f"Output file would be: {output_file}")
        logger.error(f"Hint: Check if the output path is correct. If specifying a file, ensure it ends with .md")
        return 1, None
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}", exc_info=True)
        return 1, None

    # Check if output file already exists
    file_existed = output_file.exists()
    if file_existed and not force:
        logger.error(f"Output file already exists: {output_file}")
        logger.error(f"Use -f/--force to overwrite the existing file.")
        return 1, None

    # Write merged file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_markdown_content)

        if file_existed and force:
            logger.info(f"Overwritten existing file: {output_file}")
        else:
            logger.info(f"Merged content written to {output_file}.")

    except Exception as e:
        logger.error(f"Failed to write output file: {e}", exc_info=True)
        return 1, None

    # Summary
    logger.info("="*70)
    logger.info("Markdown Merging complete")
    logger.info("="*70)
    logger.info(f"Files merged:     {success_count}/{len(files)}")
    if len(unbalanced_files) > 0:
        logger.warning(f"Files excluded:   {len(unbalanced_files)} (unbalanced code blocks)")
    if error_count > 0:
        logger.error(f"Errors:          {error_count}")
        return 1, None
    
    logger.info(f"Output file:     {output_file}")

    # Calculate file size
    file_size = output_file.stat().st_size
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.2f} MB"
    elif file_size > 1024:
        size_str = f"{file_size / 1024:.2f} KB"
    else:
        size_str = f"{file_size} bytes"
    logger.info(f"File size:       {size_str}")
    logger.info("="*70)

    return 0, output_file
