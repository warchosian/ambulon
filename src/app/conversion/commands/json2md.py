"""
Simple and fast JSON to Markdown converter.

Converts JSON files to Markdown format with automatic structure detection.
Optimized for applications data but works with any JSON structure.

Example:
    dyag json2md input.json -o output.md --verbose
"""

import json
import sys
from pathlib import Path
from typing import Any, List, Optional


def dict_to_md(data: dict, indent: int = 0) -> List[str]:
    """
    Convert a dictionary to Markdown lines.

    Args:
        data: Dictionary to convert
        indent: Indentation level

    Returns:
        List of Markdown lines
    """
    lines = []
    prefix = "  " * indent

    for key, value in data.items():
        # Format key nicely
        key_formatted = str(key).replace('_', ' ').title()

        if isinstance(value, dict):
            lines.append(f"{prefix}**{key_formatted}**:")
            lines.extend(dict_to_md(value, indent + 1))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            lines.append(f"{prefix}**{key_formatted}**:")
            for item in value:
                lines.extend(dict_to_md(item, indent + 1))
                if len(value) > 1:
                    lines.append("")
        elif isinstance(value, list) and value:
            lines.append(f"{prefix}**{key_formatted}**:")
            for v in value:
                lines.append(f"{prefix}  - {v}")
        elif value is not None and value != "":
            # Simple key-value
            val_str = str(value).replace('\r\n', ' ').replace('\n', ' ')[:200]
            lines.append(f"{prefix}**{key_formatted}**: {val_str}")

    return lines


def convert_json_to_markdown(json_content: str, verbose: bool = False) -> str:
    """
    Convert JSON content to Markdown.

    Args:
        json_content: JSON string
        verbose: Print progress info

    Returns:
        Markdown string
    """
    try:
        data = json.loads(json_content)

        if verbose:
            print(f"[INFO] JSON parsed successfully")

        # Find applications list
        apps = None
        if isinstance(data, dict):
            for key in data:
                key_lower = str(key).lower().replace('_', ' ').replace('-', ' ')
                if 'application' in key_lower:
                    apps = data[key]
                    if verbose:
                        print(f"[INFO] Found applications under key: {key}")
                    break
            # If no applications key, treat entire dict as generic JSON
            if apps is None:
                if verbose:
                    print(f"[INFO] No applications key found, treating as generic JSON")
                apps = [data]  # Treat as single-item list

        elif isinstance(data, list):
            apps = data
            if verbose:
                print(f"[INFO] JSON root is a list with {len(apps)} items")

        if not apps:
            print("[ERROR] No data found in JSON", file=sys.stderr)
            return ""

        if verbose:
            print(f"[INFO] Found {len(apps)} item(s)")
            print(f"[INFO] Converting to Markdown...")

        md_lines = [
            "# Applications IA - Ministère de la Transition Écologique",
            "",
            f"**Nombre d'applications**: {len(apps)}",
            "",
            "---",
            ""
        ]

        for i, app in enumerate(apps):
            if verbose and (i + 1) % 100 == 0:
                print(f"[INFO] Processed {i + 1}/{len(apps)} items...")

            # Get item name/title
            nom = None
            for key in ["nom", "Nom", "name", "Name", "title", "Title", "label", "Label"]:
                if isinstance(app, dict) and key in app and app[key]:
                    nom = app[key]
                    break

            if not nom:
                nom = f"Item {i + 1}"

            md_lines.append(f"# {nom}")
            md_lines.append("")

            # Convert all fields
            if isinstance(app, dict):
                md_lines.extend(dict_to_md(app, 0))
            else:
                md_lines.append(str(app))

            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")

        return '\n'.join(md_lines)

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return ""


def process_json_to_markdown(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Process JSON file to Markdown.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output Markdown file (optional)
        verbose: Show detailed progress

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: '{input_file}' does not exist.", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"Error: '{input_file}' is not a file.", file=sys.stderr)
        return 1

    # Determine output path
    if output_file is None:
        output_path = input_path.with_suffix('.md')
    else:
        output_path = Path(output_file)

    if verbose:
        print(f"[INFO] Converting JSON to Markdown...")
        print(f"[INFO] Input:  {input_path}")
        print(f"[INFO] Output: {output_path}")

    try:
        # Read JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            json_content = f.read()

        if verbose:
            print(f"[INFO] Read {len(json_content)} characters from {input_path}")

        # Convert to Markdown
        markdown_content = convert_json_to_markdown(json_content, verbose)

        if not markdown_content:
            print("[WARNING] Conversion produced empty result", file=sys.stderr)
            return 1

        # Write Markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        if verbose:
            print(f"[INFO] Wrote {len(markdown_content)} characters to {output_path}")

        print(f"[SUCCESS] Markdown file created: {output_path}")
        return 0

    except Exception as e:
        print(f"Error: Conversion failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_json2md_command(subparsers):
    """Register the json2md command."""
    parser = subparsers.add_parser(
        'json2md',
        help='Convert JSON to Markdown',
        description='Convert JSON file to Markdown format with automatic structure detection. Optimized for applications data but works with any JSON.'
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Input JSON file path'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output Markdown file path (default: input file with .md extension)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.set_defaults(func=lambda args: process_json_to_markdown(
        args.input_file,
        args.output,
        args.verbose
    ))
