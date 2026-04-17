"""
CLI command to extract ZIP archives with AES-256 decryption support.

Usage: ambulon zip-extract [OPTIONS]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.core.logging_config import setup_logging
from app.zip.core.zip_manager import ZipManager
from app.zip.core.config import (
    load_zip_config,
    get_password,
    get_password_file
)

logger = logging.getLogger(__name__)


def main(argv=None):
    """
    Extract a ZIP archive.

    Args:
        argv: Arguments CLI ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        prog="ambulon zip-extract",
        description="Extract ZIP archives with AES-256 decryption support.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract to current directory
  ambulon zip-extract archive.zip

  # Extract to specific directory
  ambulon zip-extract archive.zip -o extracted/

  # Extract encrypted archive
  ambulon zip-extract secure.zip -p "secret123"

  # Read password from file (more secure)
  ambulon zip-extract secure.zip --password-file .password

  # List archive contents without extracting
  ambulon zip-extract archive.zip --list

  # List with verbose details
  ambulon zip-extract archive.zip --list --verbose

Security Notes:
  - Passwords are never logged or displayed
  - Use --password-file to avoid passwords in shell history
  - Supports AES-256 encrypted archives
  - Compatible with 7-Zip, WinZip, and other standard tools
        """
    )

    # Required arguments
    parser.add_argument(
        "archive",
        type=str,
        help="ZIP archive file to extract"
    )

    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory (default: current directory)"
    )

    parser.add_argument(
        "-p", "--password",
        type=str,
        help="Password for encrypted archives"
    )

    parser.add_argument(
        "--password-file",
        type=str,
        help="Read password from file (more secure than -p)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List archive contents without extracting"
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
    setup_logging(level=log_level, log_file_prefix="zip_extract")

    logger.info("[START] ZIP archive extraction")

    try:
        # Load configuration
        config = load_zip_config(args.config)

        # Get archive path
        archive = Path(args.archive)

        if not archive.exists():
            print(f"\n❌ Archive not found: {archive}")
            return 1

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

        manager = ZipManager()

        # List mode
        if args.list:
            print(f"\n📦 Archive Contents: {archive.name}")
            print("=" * 70)

            try:
                contents = manager.list_contents(archive, password)

                # Calculate totals
                total_files = sum(1 for item in contents if not item['is_dir'])
                total_dirs = sum(1 for item in contents if item['is_dir'])
                total_size = sum(item['file_size'] for item in contents)
                total_compressed = sum(item['compress_size'] for item in contents)

                # Display files
                if args.verbose:
                    # Detailed listing
                    print(f"{'Size':<12} {'Compressed':<12} {'Date':<20} {'Name'}")
                    print("-" * 70)
                    for item in contents:
                        if not item['is_dir']:
                            size = item['file_size']
                            compressed = item['compress_size']
                            dt = datetime(*item['date_time'])
                            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                            print(f"{size:<12,} {compressed:<12,} {date_str:<20} {item['filename']}")
                        else:
                            print(f"{'<DIR>':<12} {'<DIR>':<12} {'':<20} {item['filename']}")
                else:
                    # Simple listing
                    for item in contents:
                        prefix = "[DIR] " if item['is_dir'] else "      "
                        print(f"{prefix}{item['filename']}")

                # Display summary
                print("=" * 70)
                print(f"Total: {total_files} file(s), {total_dirs} directory(ies)")
                print(f"Size: {total_size:,} bytes ({total_size / 1024:.1f} KB)")
                print(f"Compressed: {total_compressed:,} bytes ({total_compressed / 1024:.1f} KB)")
                if total_size > 0:
                    ratio = (1 - total_compressed / total_size) * 100
                    print(f"Compression ratio: {ratio:.1f}%")

                return 0

            except RuntimeError as e:
                print(f"\n❌ Error: {e}")
                return 1

        # Extract mode
        output_dir = Path(args.output) if args.output else Path.cwd()

        # Display summary
        print(f"\n📦 ZIP Archive Extraction")
        print(f"   Archive: {archive}")
        print(f"   Destination: {output_dir}")
        if password:
            print(f"   Encryption: AES-256 (password provided)")
        print("\n" + "=" * 70)

        # Extract archive
        print(f"\n🚀 Extracting archive...")

        extracted_files = manager.extract_archive(
            archive=archive,
            output_dir=output_dir,
            password=password
        )

        # Success
        print(f"\n✅ Extraction complete!")
        print(f"   Files extracted: {len(extracted_files)}")
        print(f"   Destination: {output_dir}")

        if args.verbose and extracted_files:
            print(f"\n📁 Extracted files:")
            for file_path in extracted_files[:20]:  # Show first 20
                print(f"   - {file_path.relative_to(output_dir)}")
            if len(extracted_files) > 20:
                print(f"   ... and {len(extracted_files) - 20} more")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
