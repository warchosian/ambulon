"""
CLI command to list installed VS Code extensions.

Usage: ambulon vscode-list [--editor code|codium] [--show-recommended]
"""

import argparse
import logging
import sys

from app.core.logging_config import setup_logging
from app.vscode.core import (
    find_vscode_command,
    get_installed_extensions,
    get_vscode_version,
    RECOMMENDED_EXTENSIONS,
    EXTENSIONS_TO_REMOVE
)

logger = logging.getLogger(__name__)


def main(argv=None):
    """Main function for vscode-list command."""
    parser = argparse.ArgumentParser(
        description="List installed VS Code extensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all installed extensions
  ambulon vscode-list

  # Show comparison with recommended extensions
  ambulon vscode-list --show-recommended

  # Use specific editor
  ambulon vscode-list --editor codium
"""
    )

    parser.add_argument(
        "--editor",
        type=str,
        choices=["code", "codium"],
        help="Specify editor: 'code' for VS Code, 'codium' for VSCodium"
    )
    parser.add_argument(
        "--show-recommended",
        action="store_true",
        help="Show comparison with recommended extensions"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="vscode_list")

    logger.info("[START] VSCode extension list")

    try:
        # Find VS Code/VSCodium
        vscode_cmd = find_vscode_command(args.editor)
        version = get_vscode_version(vscode_cmd)

        # Get installed extensions
        installed = get_installed_extensions(vscode_cmd)

        # Display header
        print(f"\n📦 VS Code/VSCodium Extensions")
        print(f"   Editor: {vscode_cmd}")
        print(f"   Version: {version}")
        print(f"   Total installed: {len(installed)}")
        print("\n" + "=" * 70)

        if not installed:
            print("\n⚠️  No extensions installed.")
            return 0

        if args.show_recommended:
            _display_with_recommendations(installed)
        else:
            _display_simple_list(installed)

        return 0

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
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs for more details.")
        return 1


def _display_simple_list(installed: set):
    """Display simple list of installed extensions."""
    print("\n📋 Installed extensions:\n")
    for ext_id in sorted(installed):
        print(f"  • {ext_id}")


def _display_with_recommendations(installed: set):
    """Display comparison with recommended extensions."""
    # Categorize installed extensions
    recommended_set = set(RECOMMENDED_EXTENSIONS.keys())
    redundant_set = set(EXTENSIONS_TO_REMOVE.keys())

    installed_recommended = installed & recommended_set
    missing_recommended = recommended_set - installed
    installed_redundant = installed & redundant_set
    other_installed = installed - recommended_set - redundant_set

    # Display installed recommended
    if installed_recommended:
        print("\n✅ Recommended extensions (installed):\n")
        for ext_id in sorted(installed_recommended):
            info = RECOMMENDED_EXTENSIONS[ext_id]
            priority_icon = {"ESSENTIEL": "⭐", "FORTEMENT RECOMMANDÉ": "💡", "OPTIONNEL": "🔧"}
            icon = priority_icon.get(info["priority"], "•")
            print(f"  {icon} {ext_id}")
            print(f"    └─ {info['description']}")

    # Display missing recommended
    if missing_recommended:
        print("\n⚠️  Recommended extensions (NOT installed):\n")
        for ext_id in sorted(missing_recommended):
            info = RECOMMENDED_EXTENSIONS[ext_id]
            priority_icon = {"ESSENTIEL": "⭐", "FORTEMENT RECOMMANDÉ": "💡", "OPTIONNEL": "🔧"}
            icon = priority_icon.get(info["priority"], "•")
            print(f"  {icon} {ext_id}")
            print(f"    └─ {info['description']}")

    # Display redundant extensions
    if installed_redundant:
        print("\n🗑️  Redundant extensions (consider removing):\n")
        for ext_id in sorted(installed_redundant):
            reason = EXTENSIONS_TO_REMOVE[ext_id]
            print(f"  • {ext_id}")
            print(f"    └─ {reason}")

    # Display other extensions
    if other_installed:
        print(f"\n📦 Other extensions ({len(other_installed)}):\n")
        for ext_id in sorted(other_installed):
            print(f"  • {ext_id}")

    # Summary
    print("\n" + "=" * 70)
    print("\n📊 Summary:")
    print(f"  • Recommended (installed): {len(installed_recommended)}")
    print(f"  • Recommended (missing): {len(missing_recommended)}")
    print(f"  • Redundant: {len(installed_redundant)}")
    print(f"  • Other: {len(other_installed)}")
    print(f"  • Total: {len(installed)}")

    if missing_recommended:
        print(f"\n💡 Tip: Run 'ambulon vscode-install' to install missing extensions")
    if installed_redundant:
        print(f"💡 Tip: Run 'ambulon vscode-uninstall' to remove redundant extensions")


if __name__ == "__main__":
    sys.exit(main())
