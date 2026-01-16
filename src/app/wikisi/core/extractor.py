"""
Core logic for extracting and filtering applications from JSON data in Ambulon.
Contains helper functions for parsing, filtering, and metadata generation.
"""

import json
import sys
import re
import html
import urllib.parse
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Import version from ambulon package
try:
    from app import __version__
except ImportError:
    __version__ = "0.5.1"  # Fallback version

def normalize_key(key: str) -> str:
    """Normalize a key to lowercase for comparison."""
    return str(key).lower().strip().replace('_', ' ').replace('-', ' ')


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: The string to sanitize
        max_length: Maximum length of the resulting filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    # Replace multiple spaces/underscores with single underscore
    safe_name = re.sub(r'[_\s]+', '_', safe_name)
    # Remove leading/trailing underscores and spaces
    safe_name = safe_name.strip('_ ')
    # Limit length
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    return safe_name


def parse_range_spec(spec: str, total: int) -> List[int]:
    """
    Parse range specification and return list of indices.

    Examples:
        "1-3" -> [0, 1, 2]
        "-5" -> last 5 elements
        "10-" -> from 10 to end
        "1,3,5-7" -> [0, 2, 4, 5, 6]

    Args:
        spec: Range specification string
        total: Total number of elements

    Returns:
        List of indices (0-based)
    """
    if not spec.strip():
        return list(range(total))

    indices = set()
    parts = spec.replace(" ", "").split(",")

    for part in parts:
        if not part:
            continue

        if "-" in part:
            if part.startswith("-"):
                # Last N elements: "-5" means last 5
                n = int(part[1:])
                start = max(0, total - n)
                indices.update(range(start, total))
            elif part.endswith("-"):
                # From N to end: "10-" means from 10 to end
                start = int(part[:-1]) - 1
                if 0 <= start < total:
                    indices.update(range(start, total))
            else:
                # Range: "5-10" means from 5 to 10
                a, b = part.split("-")
                a_i = max(0, int(a) - 1)
                b_i = min(total, int(b))
                indices.update(range(a_i, b_i))
        else:
            # Single index: "5" means element 5 (0-based: index 4)
            i = int(part) - 1
            if 0 <= i < total:
                indices.add(i)

    return sorted(indices)


def sanitize_tag(tag: str) -> str:
    """
    Sanitize a tag for use in filenames.

    Args:
        tag: Tag string to sanitize

    Returns:
        Sanitized tag
    """
    tag = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", tag.strip())
    return re.sub(r'_+', "_", tag)[:50]


def get_field(data: Dict, *key_variants) -> Any:
    """
    Get a field from a dictionary, trying multiple key variants (case-insensitive).

    Args:
        data: Dictionary to search
        *key_variants: One or more key variants to try

    Returns:
        Value if found, None otherwise
    """
    if not isinstance(data, dict):
        return None

    # Create normalized lookup
    normalized = {normalize_key(k): v for k, v in data.items()}

    # Try each variant
    for variant in key_variants:
        norm_variant = normalize_key(variant)
        if norm_variant in normalized:
            return normalized[norm_variant]

    return None


def find_by_name(data_list: List[Dict], name_query: str) -> List[Dict]:
    """
    Filter applications by name (case-insensitive substring match).

    Args:
        data_list: List of application dictionaries
        name_query: Name to search for

    Returns:
        List of matching applications
    """
    results = []
    query = name_query.strip().lower()

    for item in data_list:
        # Try different name field variants
        name = get_field(item, "nom", "name", "title", "label")
        if name and query in str(name).lower():
            results.append(item)

    return results


def find_by_id(data_list: List[Dict], id_query: str) -> List[Dict]:
    """
    Filter applications by ID (case-insensitive substring match).

    Args:
        data_list: List of application dictionaries
        id_query: ID to search for

    Returns:
        List of matching applications
    """
    results = []
    target = id_query.strip().upper()

    for item in data_list:
        # Try to find ID field
        item_id = get_field(item, "id")
        if item_id and target in str(item_id).upper():
            results.append(item)

    return results


def generate_metadata(
    source_file: str,
    original_count: int,
    filtered_count: int,
    filter_type: Optional[str] = None,
    filter_value: Optional[str] = None
) -> Dict:
    """
    Generate metadata for the filtered JSON output.

    Args:
        source_file: Source filename
        original_count: Total number of applications in source
        filtered_count: Number of applications after filtering
        filter_type: Type of filter applied ('range', 'name', 'id', or None)
        filter_value: Value of the filter

    Returns:
        Dictionary containing metadata
    """
    # Determine filter description
    if filter_type == "range":
        if filter_value and filter_value.startswith("-"):
            description = f"{filter_value[1:]} dernières applications"
        elif filter_value and filter_value.endswith("-"):
            description = f"À partir de l'application {filter_value[:-1]}"
        elif filter_value:
            description = f"Applications {filter_value}"
        else:
            description = "Toutes les applications (aucun filtre appliqué)" # Should not happen if filter_type is "range"
    elif filter_type == "name":
        description = f"Applications contenant '{filter_value}' dans le nom (insensible à la casse)"
    elif filter_type == "id":
        description = f"Applications avec ID contenant '{filter_value}' (insensible à la casse)"
    else:
        description = "Toutes les applications (aucun filtre appliqué)"

    # Calculate percentage
    if original_count > 0:
        percentage = f"{(filtered_count / original_count * 100):.1f}%"
    else:
        percentage = "0.0%"

    metadata = {
        "tool": "dyag parkjson2json",
        "version": __version__,
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source": {
            "file": source_file,
            "total_count": original_count
        },
        "filter": {
            "type": filter_type if filter_type else "none",
            "value": filter_value,
            "description": description
        },
        "output": {
            "count": filtered_count,
            "percentage": percentage
        }
    }

    return metadata


def process_parkjson2json_logic(
    input_file: Path,
    output_file: Optional[Path] = None,
    range_spec: Optional[str] = None,
    name_filter: Optional[str] = None,
    id_filter: Optional[str] = None,
    preserve_structure: bool = True,
    include_metadata: bool = True,
    split_dir: Optional[Path] = None
) -> Tuple[int, Optional[Path]]:
    """
    Core logic to extract filtered applications from JSON and save to new JSON file(s).

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file (optional)
        range_spec: Range specification (e.g., "1-3", "-5", "10-")
        name_filter: Filter by application name
        id_filter: Filter by application ID
        preserve_structure: Keep original JSON structure (default: True)
        include_metadata: Include metadata in output JSON (default: True)
        split_dir: Directory to generate separate files for each application

    Returns:
        A tuple: (exit_code: int, generated_path: Optional[Path])
    """
    if not input_file.exists():
        logger.error(f"Error: Input file '{input_file}' does not exist.")
        return 1, None

    if not input_file.is_file():
        logger.error(f"Error: '{input_file}' is not a file.")
        return 1, None

    try:
        # Read JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            json_content = f.read()

        logger.debug(f"[INFO] Read {len(json_content)} characters from {input_file}")

        # Parse JSON
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] Invalid JSON: {e}")
            return 1, None

        # Find applications list and track structure
        apps = None
        apps_key = None
        root_is_list = False

        if isinstance(data, dict):
            for key in data:
                key_lower = normalize_key(key)
                if 'application' in key_lower:
                    apps = data[key]
                    apps_key = key
                    logger.debug(f"[INFO] Found applications under key: {key}")
                    break

            if apps is None:
                logger.debug(f"[INFO] No applications key found, treating as generic JSON")
                apps = [data]
                preserve_structure = False

        elif isinstance(data, list):
            apps = data
            root_is_list = True
            logger.debug(f"[INFO] JSON root is a list with {len(apps)} items")

        if not apps:
            logger.error("[ERROR] No data found in JSON")
            return 1, None

        original_count = len(apps)
        tag_parts = []
        used_filter = False
        filter_type = None
        filter_value = None

        # Apply filters
        if id_filter:
            apps = find_by_id(apps, id_filter)
            clean_id = sanitize_tag(id_filter.upper())
            tag_parts.append(f"ID{clean_id}")
            logger.info(f"[FILTER] ID '{id_filter}' -> {len(apps)} resultat(s)")
            used_filter = True
            filter_type = "id"
            filter_value = id_filter

        elif name_filter:
            apps = find_by_name(apps, name_filter)
            if apps and get_field(apps[0], "nom", "name"):
                tag_name = sanitize_tag(str(get_field(apps[0], "nom", "name")))
            else:
                tag_name = sanitize_tag(name_filter)
            tag_parts.append(tag_name)
            logger.info(f"[FILTER] Nom '{name_filter}' -> {len(apps)} resultat(s)")
            used_filter = True
            filter_type = "name"
            filter_value = name_filter

        elif range_spec:
            indices = parse_range_spec(range_spec, original_count)
            apps = [apps[i] for i in indices] if indices else []
            tag_parts.append(sanitize_tag(range_spec))
            logger.info(f"[FILTER] Plage '{range_spec}' -> {len(apps)} element(s)")
            used_filter = True
            filter_type = "range"
            filter_value = range_spec

        if not apps:
            logger.warning("[WARNING] No applications match the filters")
            return 0, None # Return success code 0 if no apps match filter, but warn

        # SPLIT MODE: Generate separate file for each application
        if split_dir:
            split_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"[INFO] Extracting {len(apps)} application(s) to separate JSON files...")
            logger.info(f"[INFO] Input:  {input_file}")
            logger.info(f"[INFO] Output directory: {split_dir}")

            files_created = 0
            for i, app_data in enumerate(apps): # Renamed 'app' to 'app_data' to avoid conflict with 'app' variable in typer
                if (i + 1) % 100 == 0:
                    logger.debug(f"[INFO] Processed {i + 1}/{len(apps)} applications...")

                # Get application name
                app_name = get_field(app_data, "nom", "name", "title", "label") or f"app_{i+1}"
                safe_app_name = sanitize_filename(app_name)

                # Create filename: inputname_appname.json
                filename = f"{input_file.stem}_{safe_app_name}.json"
                file_path = split_dir / filename

                # Write application to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(app_data, f, ensure_ascii=False, indent=2)

                files_created += 1

            # Calculate percentage for summary
            percentage = f"{(len(apps) / original_count * 100):.1f}%" if original_count > 0 else "0.0%"

            logger.info(f"[SUCCESS] {files_created} JSON files created in {split_dir}")
            logger.info(f"          Contains {len(apps)} application(s) ({percentage} of original)")
            return 0, split_dir # Return split_dir as the generated path

        # NORMAL MODE: Single file output
        # Determine output path
        if output_file is None:
            if used_filter and tag_parts:
                tag_suffix = "_".join(tag_parts)
                output_path = input_file.with_name(f"{input_file.stem}_{tag_suffix}.json")
            else:
                # No filter: just change extension to .json
                output_path = input_file.with_suffix(".json")
        else:
            output_path = output_file

        logger.info(f"[INFO] Extracting {len(apps)} application(s) to JSON...")
        logger.info(f"[INFO] Input:  {input_file}")
        logger.info(f"[INFO] Output: {output_path}")

        # Build output JSON structure
        if preserve_structure and apps_key:
            # Preserve original structure with wrapper key
            output_data = {apps_key: apps}
        elif root_is_list:
            # Root was already a list
            output_data = apps
        else:
            # Default: wrap in applications key
            output_data = {"applications": apps}

        # Add metadata if requested
        if include_metadata:
            logger.debug(f"[INFO] Adding metadata to output...")

            metadata = generate_metadata(
                source_file=input_file.name,
                original_count=original_count,
                filtered_count=len(apps),
                filter_type=filter_type,
                filter_value=filter_value
            )

            # Insert metadata at the beginning
            if isinstance(output_data, dict):
                # Create new dict with metadata first
                output_data = {"_metadata": metadata, **output_data}
            else:
                # If output_data is a list, wrap it with metadata
                output_data = {
                    "_metadata": metadata,
                    "applications": output_data
                }

        # Write JSON file with nice formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        output_size = output_path.stat().st_size
        logger.info(f"[INFO] Wrote {output_size} bytes to {output_path}")
        logger.info(f"[INFO] Metadata included: {'Yes' if include_metadata else 'No'}")

        # Calculate percentage for summary
        percentage = f"{(len(apps) / original_count * 100):.1f}%" if original_count > 0 else "0.0%"

        logger.info(f"[SUCCESS] JSON file created: {output_path}")
        logger.info(f"          Contains {len(apps)} application(s) ({percentage} of original)")
        if include_metadata:
            logger.info(f"          Metadata: Included")
        return 0, output_path

    except Exception as e:
        logger.error(f"Error: Extraction failed: {e}", exc_info=True)
        return 1, None
