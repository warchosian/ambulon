"""
CLI command to extract designated applications from WikiSI data to individual JSON and MD files.
Reads the application list from config/wikisi.yaml and generates separate files for each.
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.core.config_loader import load_config as load_app_config
from app.core.logging_config import setup_logging
from ..core.api_client import WikiSIAPIClient
from ..core.json_to_md_converter import convert_app_to_markdown

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'wikisi': {
        'api': {
            'url': 'https://wikisi.e2.rie.gouv.fr/wikisi/api',
            'token': '',
            'user_agent': 'Ambulon Wiki SI Sync API/1.0',
            'page_limit': 25,
        },
        'output': {
            'directory': 'workplace-ambulon/wikisi/download',
            'enumerations_file': 'enumerations.json',
            'applications_file': 'applications.json',
            'applications_ia_file': 'applicationsIA.json',
            'applications_ia_mini_file': 'applicationsIA_mini.json',
        },
        'applications': {
            'extract': {}
        }
    }
}


def normalize_identifier(identifier: str) -> str:
    """Normalize an identifier for case-insensitive comparison."""
    return str(identifier).lower().strip()


def match_application(app: Dict[str, Any], identifier: str) -> bool:
    """
    Check if an application matches the given identifier.

    Args:
        app: Application dictionary
        identifier: ID, name, or business number to match

    Returns:
        True if the application matches, False otherwise
    """
    normalized_id = normalize_identifier(identifier)

    # Try matching by ID (lowercase 'id' or capitalized 'Id')
    for id_key in ['id', 'Id']:
        if id_key in app and normalize_identifier(str(app[id_key])) == normalized_id:
            return True

    # Try matching by name (lowercase 'nom' or capitalized 'Nom')
    for name_key in ['nom', 'Nom']:
        if name_key in app and normalize_identifier(app[name_key]) == normalized_id:
            return True

    # Try matching by numero_affaire (business number)
    # Handle both formats: simple string or list of objects
    for num_key in ['numero_affaire', 'Numéros d\'affaire']:
        if num_key in app and app[num_key]:
            if isinstance(app[num_key], list):
                # Format: [{"Numéro d'affaire": "AFF123", ...}, ...]
                for num_obj in app[num_key]:
                    if isinstance(num_obj, dict) and "Numéro d'affaire" in num_obj:
                        if normalize_identifier(str(num_obj["Numéro d'affaire"])) == normalized_id:
                            return True
            else:
                # Format: "AFF123"
                if normalize_identifier(str(app[num_key])) == normalized_id:
                    return True

    return False


def find_application(applications: List[Dict[str, Any]], identifier: str) -> Optional[Dict[str, Any]]:
    """
    Find an application by identifier (ID, name, or business number).

    Args:
        applications: List of all applications
        identifier: ID, name, or business number to search for

    Returns:
        Matching application dictionary or None
    """
    for app in applications:
        if match_application(app, identifier):
            return app
    return None


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: The string to sanitize
        max_length: Maximum length of the resulting filename

    Returns:
        Sanitized filename safe for filesystem
    """
    import re
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


def extract_applications_to_files(
    applications: List[Dict[str, Any]],
    extract_config: Dict[str, Any],
    output_dir: Path,
    force: bool = False,
    copy_to_rag: bool = False,
    rag_base_dir: Optional[Path] = None
) -> Tuple[int, int]:
    """
    Extract designated applications to individual JSON and MD files.

    Args:
        applications: List of all applications
        extract_config: Configuration dict with identifiers and optional new names
        output_dir: Directory to save extracted files
        force: If True, overwrite existing files
        copy_to_rag: If True, copy .wikisi.md files to RAG directories
        rag_base_dir: Base directory for RAG folders (e.g., workplace-ambulon/gitlab)

    Returns:
        Tuple of (success_count, error_count)
    """
    success_count = 0
    error_count = 0

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # If extract_config is empty dict {}, extract all applications
    if not extract_config:
        logger.info("Empty extract configuration - extracting ALL applications")
        extract_config = {}
        for i, app in enumerate(applications):
            # Get app identifier (prefer nom/Nom, fallback to id/Id)
            app_id = app.get('nom') or app.get('Nom') or app.get('id') or app.get('Id', f"app_{i}")
            extract_config[app_id] = None

    for identifier, new_name in extract_config.items():
        # Find the application
        app = find_application(applications, str(identifier))

        if not app:
            logger.warning(f"Application not found: {identifier}")
            error_count += 1
            continue

        # Determine filename (use new_name if provided, otherwise use app name or ID)
        if new_name:
            filename_base = sanitize_filename(str(new_name))
        elif 'nom' in app:
            filename_base = sanitize_filename(app['nom'])
        elif 'Nom' in app:
            filename_base = sanitize_filename(app['Nom'])
        else:
            app_id = app.get('id') or app.get('Id', identifier)
            filename_base = sanitize_filename(f"app_{app_id}")

        # Save JSON file
        json_path = output_dir / f"{filename_base}.wikisi.json"
        md_path = output_dir / f"{filename_base}.wikisi.md"

        # Check if files exist and force is not set
        if not force and (json_path.exists() or md_path.exists()):
            logger.warning(f"Files already exist for '{filename_base}' - use --force to overwrite")
            error_count += 1
            continue

        try:
            # Save JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(app, f, ensure_ascii=False, indent=2)
            logger.info(f"✓ Generated JSON: {json_path.name}")

            # Save Markdown
            md_content = convert_app_to_markdown(app, verbose=False)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"✓ Generated MD: {md_path.name}")

            # Copy to RAG directory if enabled
            if copy_to_rag and rag_base_dir:
                rag_dir = rag_base_dir / f"{filename_base}.rag"
                rag_dir.mkdir(parents=True, exist_ok=True)
                rag_md_path = rag_dir / f"{filename_base}.wikisi.md"

                # Copy the markdown file
                import shutil
                shutil.copy2(md_path, rag_md_path)
                logger.info(f"✓ Copied to RAG: {rag_dir.name}/{rag_md_path.name}")

            success_count += 1

        except Exception as e:
            logger.error(f"Error processing application '{identifier}': {e}")
            error_count += 1

    return success_count, error_count


def main(argv=None):
    """
    Entry point for wikisi-extract-apps command.

    Args:
        argv: Command-line arguments (list), or None to use sys.argv

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="""
        Extracts designated applications from WikiSI data to individual JSON and Markdown files.
        Reads the application list from config/wikisi.yaml under 'applications.extract'.

        Configuration format in config/wikisi.yaml:
          applications:
            extract:
              Admin EP: adminep          # ID or name: new_name
              bo: bo                     # name: new_name
              42: mon_application        # numeric ID: new_name
              AFF-2024-001: affaire_001  # business number: new_name
              {}                         # Empty dict = extract ALL applications

        Configuration Hierarchy (from highest to lowest priority):
        1. Command-line arguments
        2. YAML configuration file (--config, e.g., config/wikisi.yaml)
        3. Default values
        """
    )

    parser.add_argument("--config", "-c", type=Path, default="config/wikisi.yaml",
                       help="Path to YAML configuration file (default: config/wikisi.yaml).")
    parser.add_argument("--output-dir", "-o", type=Path,
                       help="Output directory for extracted files (overrides config).")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Overwrite existing files without prompting.")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging (DEBUG level).")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress most output messages (WARNING level).")

    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else (logging.WARNING if args.quiet else logging.INFO)
    setup_logging(level=log_level, log_file_prefix="wikisi_extract_apps")
    logger.info("[START] Starting wikisi-extract-apps module.")
    logger.debug(f"CLI arguments: {vars(args)}")

    # Load configuration
    config = load_app_config(str(args.config) if args.config else None, DEFAULT_CONFIG)
    wikisi_config = config.get('wikisi', {})

    # Get extract configuration
    extract_config = wikisi_config.get('applications', {}).get('extract', {})

    if not extract_config:
        logger.error("No applications configured for extraction in config file.")
        logger.error("Please configure applications.extract in config/wikisi.yaml")
        return 1

    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = Path(wikisi_config.get('output', {}).get('directory', 'workplace-ambulon/wikisi/download'))

    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Applications to extract: {len(extract_config) if extract_config else 'ALL'}")

    try:
        # Initialize WikiSI API client (will load or fetch applications)
        client = WikiSIAPIClient(wikisi_config)

        # Load applications from file or API
        app_file = client.output_dir / wikisi_config['output']['applications_file']
        app_ia_file = client.output_dir / wikisi_config['output']['applications_ia_file']

        applications = None

        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                applications = data.get('applications', [])
            logger.info(f"Loaded {len(applications)} applications from {app_file}")
        elif app_ia_file.exists():
            # Fallback to applicationsIA.json if applications.json doesn't exist
            logger.info(f"applications.json not found, using {app_ia_file} as fallback")
            with open(app_ia_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                applications = data.get('applicationsIA', [])
            logger.info(f"Loaded {len(applications)} applications from {app_ia_file}")
        else:
            logger.info("Applications file not found, fetching from API...")
            applications = client.extract_applications_list()
            logger.info(f"Fetched {len(applications)} applications from API")

        # Get RAG configuration
        copy_to_rag = wikisi_config.get('output', {}).get('copy_to_rag', False)
        rag_base_dir_str = wikisi_config.get('output', {}).get('rag_base_directory', 'workplace-ambulon/gitlab')
        rag_base_dir = Path(rag_base_dir_str) if copy_to_rag else None

        if copy_to_rag:
            logger.info(f"RAG copy enabled: {rag_base_dir}")

        # Extract applications to files
        success_count, error_count = extract_applications_to_files(
            applications=applications,
            extract_config=extract_config,
            output_dir=output_dir,
            force=args.force,
            copy_to_rag=copy_to_rag,
            rag_base_dir=rag_base_dir
        )

        # Print summary
        print(f"\n{'='*60}")
        print(f"Extraction Summary:")
        print(f"  ✓ Successful: {success_count}")
        print(f"  ✗ Failed: {error_count}")
        print(f"  Output directory: {output_dir}")
        print(f"{'='*60}")

        if success_count > 0:
            logger.info(f"[SUCCESS] Extracted {success_count} applications successfully.")
            return 0
        else:
            logger.error("[FAILED] No applications were extracted successfully.")
            return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
