"""
CLI command to create ZIP archives with optional AES-256 encryption.

Usage: ambulon zip-create [OPTIONS]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from app.zip.core.zip_manager import ZipManager
from app.zip.core.config import (
    load_zip_config,
    get_compression_level,
    get_password,
    get_password_file,
    get_exclude_patterns,
    is_recursive
)

logger = logging.getLogger(__name__)


def main(argv=None):
    """
    Create a ZIP archive from files and directories.

    Args:
        argv: Arguments CLI ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        prog="ambulon zip-create",
        description="Create a ZIP archive with optional AES-256 encryption.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create simple archive
  ambulon zip-create docs/

  # Create archive with custom name
  ambulon zip-create docs/ -o documentation.zip

  # Create encrypted archive (AES-256)
  ambulon zip-create docs/ -p "secret123"

  # Read password from file (more secure)
  ambulon zip-create docs/ --password-file .password

  # Archive multiple sources
  ambulon zip-create src/ tests/ README.md -o project.zip

  # Exclude files
  ambulon zip-create src/ --exclude "*.pyc" --exclude "__pycache__"

  # High compression
  ambulon zip-create docs/ --compression 9

  # Non-recursive (only files in specified directories)
  ambulon zip-create docs/ --no-recursive

Configuration Hierarchy:
  1. Command-line arguments (highest priority)
  2. YAML configuration file (--config)
  3. Environment variables (AMBULON_ZIP_*)
  4. Default values

Environment Variables:
  AMBULON_ZIP_PASSWORD       Default password for encryption
  AMBULON_ZIP_COMPRESSION    Default compression level (0-9)
  AMBULON_HOME              Base directory for config files

Security Notes:
  - Passwords are never logged or displayed
  - Use --password-file to avoid passwords in shell history
  - AES-256 encryption is used for password-protected archives
  - Encrypted archives are compatible with 7-Zip, WinZip, etc.
        """
    )

    # Required arguments
    parser.add_argument(
        "sources",
        nargs="+",
        type=str,
        help="File(s) or directory(ies) to archive"
    )

    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output ZIP file path (default: <first_source>.zip)"
    )

    parser.add_argument(
        "-p", "--password",
        type=str,
        help="Password for AES-256 encryption"
    )

    parser.add_argument(
        "--password-file",
        type=str,
        help="Read password from file (more secure than -p)"
    )

    parser.add_argument(
        "--exclude",
        action="append",
        dest="exclude_patterns",
        help="Glob pattern to exclude (can be specified multiple times)"
    )

    parser.add_argument(
        "--compression",
        type=int,
        default=6,
        choices=range(0, 10),
        metavar="LEVEL",
        help="Compression level 0-9 (default: 6, 0=none, 9=max)"
    )

    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not include subdirectories recursively"
    )

    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file path (YAML)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="zip_create")

    logger.info("[START] ZIP archive creation")

    try:
        # Load configuration
        config = load_zip_config(args.config)

        # Convert sources to Path objects
        sources = [Path(s) for s in args.sources]

        # Determine output path
        if args.output:
            output = Path(args.output)
        else:
            # Default: <first_source>.zip
            first_source = sources[0]
            if first_source.is_dir():
                output = Path(f"{first_source.name}.zip")
            else:
                output = Path(f"{first_source.stem}.zip")

        # Get password (hierarchy: CLI > password-file (CLI) > config > env)
        password: Optional[str] = None
        if args.password:
            # 1. CLI argument (highest priority)
            password = args.password
            logger.debug("Using password from CLI argument")
        elif args.password_file:
            # 2. Password file from CLI
            password_file = Path(args.password_file)
            if not password_file.exists():
                print(f"\n❌ Password file not found: {password_file}")
                return 1
            password = password_file.read_text(encoding='utf-8').strip()
            logger.info("Password loaded from file (CLI)")
        else:
            # 3. Try config file password_file option
            config_password_file = get_password_file(config)
            if config_password_file and config_password_file.exists():
                password = config_password_file.read_text(encoding='utf-8').strip()
                logger.info(f"Password loaded from file (config): {config_password_file}")
            else:
                # 4. Try config/env password
                password = get_password(config)
                if password:
                    logger.debug("Using password from config/environment")

        # Get compression level (hierarchy: CLI > env > config > default)
        compression_level = args.compression if hasattr(args, 'compression') else get_compression_level(config)

        # Get exclude patterns (hierarchy: CLI > config)
        exclude_patterns = args.exclude_patterns if args.exclude_patterns else get_exclude_patterns(config)

        # Get recursive flag (hierarchy: CLI > config)
        recursive = not args.no_recursive if args.no_recursive else is_recursive(config)

        # Display summary
        print(f"\n📦 ZIP Archive Creation")
        print(f"   Sources: {len(sources)}")
        for source in sources:
            print(f"     - {source}")
        print(f"   Output: {output}")
        print(f"   Compression: {compression_level}/9")
        print(f"   Recursive: {recursive}")
        if password:
            print(f"   Encryption: AES-256 (password protected)")
        if exclude_patterns:
            print(f"   Exclude patterns: {', '.join(exclude_patterns)}")
        print("\n" + "=" * 70)

        # Create archive
        print(f"\n🚀 Creating archive...")

        manager = ZipManager()
        created_archive = manager.create_archive(
            sources=sources,
            output=output,
            password=password,
            compression_level=compression_level,
            exclude_patterns=exclude_patterns or [],
            recursive=recursive
        )

        # Success
        file_size = created_archive.stat().st_size / 1024  # KB
        print(f"\n✅ Archive created successfully!")
        print(f"   Path: {created_archive}")
        print(f"   Size: {file_size:.1f} KB")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
