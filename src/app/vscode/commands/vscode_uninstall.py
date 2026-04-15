"""
CLI command to uninstall redundant VS Code extensions.

Usage: ambulon vscode-uninstall [--editor code|codium] [--yes]
"""

import argparse
import logging
import sys

from app.core.logging_config import setup_logging
from app.vscode.core import (
    find_vscode_command,
    get_installed_extensions,
    uninstall_extension,
    EXTENSIONS_TO_REMOVE
)

logger = logging.getLogger(__name__)


def main(argv=None):
    """Main function for vscode-uninstall command."""
    parser = argparse.ArgumentParser(
        description="Uninstall redundant/unnecessary VS Code extensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  ambulon vscode-uninstall

  # Auto-confirm uninstallation
  ambulon vscode-uninstall --yes

  # Use specific editor
  ambulon vscode-uninstall --editor codium
"""
    )

    parser.add_argument(
        "--editor",
        type=str,
        choices=["code", "codium"],
        help="Specify editor: 'code' for VS Code, 'codium' for VSCodium"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Auto-confirm uninstallation without prompting"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="vscode_uninstall")

    logger.info("[START] VSCode extension uninstallation")

    try:
        # Find VS Code/VSCodium
        vscode_cmd = find_vscode_command(args.editor)
        logger.info(f"Using editor: {vscode_cmd}")

        # Get installed extensions
        logger.info("Checking installed extensions...")
        installed = get_installed_extensions(vscode_cmd)

        # Find redundant extensions
        extensions_to_uninstall = [
            (ext_id, reason)
            for ext_id, reason in EXTENSIONS_TO_REMOVE.items()
            if ext_id in installed
        ]

        if not extensions_to_uninstall:
            print("\n✅ No redundant extensions found. Your configuration is optimal!")
            return 0

        # Display redundant extensions
        print(f"\n📋 {len(extensions_to_uninstall)} redundant extension(s) detected:\n")

        for ext_id, reason in extensions_to_uninstall:
            print(f"  • {ext_id}")
            print(f"    └─ Reason: {reason}")

        print("\n" + "=" * 70)

        # Confirm uninstallation
        if args.yes:
            logger.info("Auto-confirm mode enabled")
            response = "y"
        else:
            response = input("\n⚠️  Uninstall these extensions? (y/N): ").strip().lower()

        if response not in ['y', 'yes', 'o', 'oui']:
            print("\n❌ Uninstallation cancelled.")
            return 0

        # Uninstall extensions
        print("\n🗑️  Uninstalling extensions...\n")

        success_count = 0
        failed_count = 0

        for ext_id, reason in extensions_to_uninstall:
            print(f"  Uninstalling {ext_id}... ", end='', flush=True)

            if uninstall_extension(ext_id, vscode_cmd):
                print("✅ OK")
                success_count += 1
            else:
                print("❌ FAILED")
                failed_count += 1

        # Summary
        print("\n" + "=" * 70)
        print(f"\n📊 Summary:")
        print(f"  • Successful: {success_count}")
        print(f"  • Failed: {failed_count}")

        if success_count > 0:
            print(f"\n✅ {success_count} extension(s) uninstalled successfully!")
            print("💡 Restart VS Code to finalize changes.")

        if failed_count > 0:
            print(f"\n⚠️  {failed_count} extension(s) could not be uninstalled.")

        return 0 if failed_count == 0 else 1

    except FileNotFoundError as e:
        logger.error(f"Editor not found: {e}")
        print(f"\n❌ {e}")
        return 1
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        print(f"\n❌ {e}")
        return 1
    except ValueError as e:
        logger.error(f"Invalid value: {e}")
        print(f"\n❌ {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n❌ Uninstallation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
