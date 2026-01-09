"""
Command to convert JSON (array of objects) to JSONL (one object per line).

Handles:
- JSON files with root array: [obj1, obj2, ...]
- JSON files with nested array: {"key": [obj1, obj2, ...]}
- Automatically detects the array structure
"""

import json
import sys
from pathlib import Path


def find_array_in_json(data):
    """
    Find the first array in JSON data.

    Args:
        data: Parsed JSON data

    Returns:
        The array, or None if not found
    """
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                return value

    return None


def json_to_jsonl(
    input_file: str,
    output_file: str,
    array_key: str = None,
    verbose: bool = False
) -> int:
    """
    Convert JSON to JSONL.

    Args:
        input_file: Input JSON file path
        output_file: Output JSONL file path
        array_key: Optional key to extract array from (auto-detect if None)
        verbose: Show detailed progress

    Returns:
        Number of objects written, or -1 on error
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_file}", file=sys.stderr)
        return -1

    try:
        # Load JSON
        if verbose:
            print(f"Loading JSON from: {input_file}")

        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract array
        if array_key:
            if isinstance(data, dict) and array_key in data:
                array = data[array_key]
            else:
                print(f"[ERROR] Key '{array_key}' not found in JSON", file=sys.stderr)
                return -1
        else:
            array = find_array_in_json(data)

        if array is None:
            print("[ERROR] No array found in JSON file", file=sys.stderr)
            return -1

        if not isinstance(array, list):
            print("[ERROR] Found data is not an array", file=sys.stderr)
            return -1

        if verbose:
            print(f"Found array with {len(array)} objects")

        # Write JSONL
        if verbose:
            print(f"Writing JSONL to: {output_file}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            for obj in array:
                f.write(json.dumps(obj, ensure_ascii=False) + '\n')

        if verbose:
            print(f"[OK] Converted {len(array)} objects to JSONL")

        return len(array)

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}", file=sys.stderr)
        return -1
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return -1


def run_json2jsonl(args):
    """Run json2jsonl command with parsed args."""
    result = json_to_jsonl(
        input_file=args.input,
        output_file=args.output,
        array_key=args.array_key,
        verbose=args.verbose
    )

    return 0 if result >= 0 else 1


def register_json2jsonl_command(subparsers):
    """Register json2jsonl command."""
    parser = subparsers.add_parser(
        'json2jsonl',
        help='Convertir JSON (array) en JSONL (une ligne par objet)'
    )

    parser.add_argument(
        'input',
        type=str,
        help='Fichier JSON source'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help='Fichier JSONL de sortie'
    )
    parser.add_argument(
        '--array-key',
        type=str,
        default=None,
        help='Clé contenant l\'array (auto-détection si non spécifié)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Affichage détaillé'
    )

    parser.set_defaults(func=run_json2jsonl)
