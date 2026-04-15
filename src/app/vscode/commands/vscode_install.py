"""
CLI command to install recommended VS Code extensions.

Usage: ambulon vscode-install [--mode 1|2|3] [--editor code|codium] [--yes]
"""

import argparse
import logging
import sys
from typing import List, Tuple

from app.core.logging_config import setup_logging
from app.vscode.core import (
    find_vscode_command,
    get_installed_extensions,
    install_extension,
    RECOMMENDED_EXTENSIONS,
    Priority
)

logger = logging.getLogger(__name__)


def main(argv=None):
    """Main function for vscode-install command."""
    parser = argparse.ArgumentParser(
        description="Install recommended VS Code extensions for diagram visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  ambulon vscode-install

  # Install essentials only
  ambulon vscode-install --mode 1

  # Install essentials + recommended (default)
  ambulon vscode-install --mode 2

  # Install all extensions
  ambulon vscode-install --mode 3

  # Auto-confirm installation
  ambulon vscode-install --mode 2 --yes

  # Use specific editor
  ambulon vscode-install --editor codium
"""
    )

    parser.add_argument(
        "--mode",
        type=int,
        choices=[1, 2, 3],
        help="Installation mode: 1=Essential, 2=Essential+Recommended (default), 3=All"
    )
    parser.add_argument(
        "--editor",
        type=str,
        choices=["code", "codium", "cursor", "code-insiders"],
        help="Specify editor: 'code' for VS Code, 'codium' for VSCodium, 'cursor' for Cursor, 'code-insiders' for VS Code Insiders"
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Auto-confirm installation without prompting"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="vscode_install")

    logger.info("[START] VSCode extension installation")

    try:
        # Find VS Code/VSCodium
        vscode_cmd = find_vscode_command(args.editor)
        logger.info(f"Using editor: {vscode_cmd}")

        # Get installed extensions
        logger.info("Checking installed extensions...")
        installed = get_installed_extensions(vscode_cmd)

        # Categorize extensions
        essential, recommended, optional, already_installed = _categorize_extensions(installed)

        # Display already installed
        if already_installed:
            print("\n✅ Extensions already installed:")
            for ext_id, info in already_installed:
                print(f"  • {ext_id}")
                print(f"    └─ {info['description']}")

        # Display available extensions
        to_install = essential + recommended + optional

        if not to_install:
            print("\n🎉 All recommended extensions are already installed!")
            return 0

        print(f"\n📋 {len(to_install)} recommended extension(s) not installed:\n")

        if essential:
            print("⭐ ESSENTIAL:")
            for ext_id, info in essential:
                print(f"  • {ext_id}")
                print(f"    └─ {info['description']}")
            print()

        if recommended:
            print("💡 STRONGLY RECOMMENDED:")
            for ext_id, info in recommended:
                print(f"  • {ext_id}")
                print(f"    └─ {info['description']}")
            print()

        if optional:
            print("🔧 OPTIONAL:")
            for ext_id, info in optional:
                print(f"  • {ext_id}")
                print(f"    └─ {info['description']}")
            print()

        # Determine installation mode
        if args.mode:
            mode = args.mode
            logger.info(f"Using specified mode: {mode}")
        elif args.yes:
            mode = 2  # Default to essential + recommended
            logger.info("Auto mode: using mode 2 (essential + recommended)")
        else:
            mode = _prompt_installation_mode()

        # Select extensions to install
        extensions_to_install = _select_extensions_by_mode(mode, essential, recommended, to_install)

        if not extensions_to_install:
            print("\n✅ No extensions to install.")
            return 0

        # Confirm installation
        if not args.yes:
            response = input(f"\n📥 Install {len(extensions_to_install)} extension(s)? (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'o', 'oui']:
                print("\n❌ Installation cancelled.")
                return 0

        # Install extensions
        print(f"\n📥 Installing {len(extensions_to_install)} extension(s)...\n")
        success_count, failed_count, failed_extensions = _install_extensions(
            extensions_to_install, vscode_cmd
        )

        # Summary
        print("\n" + "=" * 70)
        print(f"\n📊 Summary:")
        print(f"  • Successful: {success_count}")
        print(f"  • Already installed: {len(already_installed)}")
        print(f"  • Failed: {failed_count}")

        if success_count > 0:
            print(f"\n✅ {success_count} extension(s) installed successfully!")
            print("💡 Restart VS Code to activate the extensions.")

        if failed_extensions:
            print(f"\n⚠️  Failed extensions:")
            for ext_id, message in failed_extensions:
                print(f"  • {ext_id}")
                if message:
                    print(f"    └─ {message}")

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
        print("\n\n❌ Installation cancelled by user.")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs for more details.")
        return 1


def _categorize_extensions(installed: set) -> tuple:
    """Categorize extensions into essential, recommended, optional, and already installed."""
    essential = []
    recommended = []
    optional = []
    already_installed = []

    for ext_id, info in RECOMMENDED_EXTENSIONS.items():
        if ext_id in installed:
            already_installed.append((ext_id, info))
        elif info["priority"] == "ESSENTIEL":
            essential.append((ext_id, info))
        elif info["priority"] == "FORTEMENT RECOMMANDÉ":
            recommended.append((ext_id, info))
        else:
            optional.append((ext_id, info))

    return essential, recommended, optional, already_installed


def _prompt_installation_mode() -> int:
    """Prompt user for installation mode."""
    print("=" * 70)
    print("\nInstallation options:")
    print("  1 - Install ONLY ESSENTIAL extensions")
    print("  2 - Install ESSENTIAL + STRONGLY RECOMMENDED")
    print("  3 - Install ALL extensions")
    print("  0 - Cancel")

    while True:
        try:
            choice = input("\nYour choice (1/2/3/0): ").strip()
            if choice in ["1", "2", "3"]:
                return int(choice)
            elif choice == "0":
                print("\n❌ Installation cancelled.")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 0.")
        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Installation cancelled.")
            sys.exit(0)


def _select_extensions_by_mode(mode: int, essential: list, recommended: list, all_extensions: list) -> list:
    """Select extensions based on installation mode."""
    if mode == 1:
        return essential
    elif mode == 2:
        return essential + recommended
    elif mode == 3:
        return all_extensions
    else:
        return []


def _install_extensions(extensions: list, vscode_cmd: str) -> Tuple[int, int, list]:
    """
    Install a list of extensions.

    Returns:
        Tuple of (success_count, failed_count, failed_extensions)
    """
    success_count = 0
    failed_count = 0
    failed_extensions = []

    for ext_id, info in extensions:
        print(f"  Installing {ext_id}... ", end='', flush=True)

        success, message = install_extension(ext_id, vscode_cmd)

        if success:
            print("✅ OK")
            success_count += 1
        else:
            print("❌ FAILED")
            failed_count += 1
            failed_extensions.append((ext_id, message))

    return success_count, failed_count, failed_extensions


if __name__ == "__main__":
    sys.exit(main())
