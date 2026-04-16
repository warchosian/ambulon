"""
CLI command to create GitHub releases.

Usage: ambulon github-release [OPTIONS]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from app.github.core.config import load_github_config, get_github_token
from app.github.core.release_manager import ReleaseManager

logger = logging.getLogger(__name__)


def main(argv=None):
    """
    Create a GitHub release from an existing tag.

    Args:
        argv: Arguments CLI ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        prog="ambulon github-release",
        description="Create a GitHub release from an existing tag with optional asset uploads.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (priority from highest to lowest):
  1. Command-line arguments (--tag, --title, etc.)
  2. YAML configuration file (--config)
  3. Environment variables (GITHUB_*)
  4. Default values

Environment Variables:
  GITHUB_TOKEN        GitHub personal access token (required)
  GITHUB_OWNER        Repository owner (default: warchosian)
  GITHUB_REPO         Repository name (default: ambulon)

Examples:
  # Create release from latest tag with auto-detected wheel
  ambulon github-release --tag 3.5.0

  # With custom title and description
  ambulon github-release --tag 3.5.0 \\
    --title "v3.5.0 - New Features" \\
    --description "See CHANGELOG.md for details"

  # With specific assets
  ambulon github-release --tag 3.5.0 \\
    --asset dist/ambulon-3.5.0-py3-none-any.whl \\
    --asset docs/manual.pdf

  # Create draft release
  ambulon github-release --tag 3.5.0 --draft

  # With configuration file
  ambulon github-release --tag 3.5.0 -c config/github.yaml

  # Via environment variables
  export GITHUB_TOKEN=ghp_...
  export GITHUB_OWNER=myorg
  export GITHUB_REPO=myrepo
  ambulon github-release --tag 1.0.0

See also:
  Git tags management: git tag -l
  Commitizen: cz bump
        """
    )

    # Required arguments
    parser.add_argument(
        "--tag",
        type=str,
        required=True,
        help="Git tag name for the release (must exist)"
    )

    # Optional arguments
    parser.add_argument(
        "--title",
        type=str,
        help="Release title (default: 'v{tag}')"
    )

    parser.add_argument(
        "--description",
        type=str,
        help="Release description (Markdown)"
    )

    parser.add_argument(
        "--description-file",
        type=str,
        help="Read description from file"
    )

    parser.add_argument(
        "--asset",
        action="append",
        dest="assets",
        help="Asset file to upload (can be specified multiple times)"
    )

    parser.add_argument(
        "--auto-wheel",
        action="store_true",
        help="Automatically find and upload wheel for this version"
    )

    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create as draft release"
    )

    parser.add_argument(
        "--prerelease",
        action="store_true",
        help="Mark as pre-release"
    )

    # Configuration
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file path (YAML)"
    )

    parser.add_argument(
        "--token",
        type=str,
        help="GitHub token (or use GITHUB_TOKEN env var)"
    )

    parser.add_argument(
        "--owner",
        type=str,
        help="Repository owner"
    )

    parser.add_argument(
        "--repo",
        type=str,
        help="Repository name"
    )

    # Logging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file_prefix="github_release")

    logger.info("[START] GitHub release creation")

    try:
        # Load configuration
        config = load_github_config(args.config)

        # Apply CLI arguments (highest priority)
        if args.owner:
            config["github"]["owner"] = args.owner
        if args.repo:
            config["github"]["repo"] = args.repo
        if args.token:
            config["github"]["token"] = args.token
        if args.draft:
            config["github"]["release"]["draft"] = args.draft
        if args.prerelease:
            config["github"]["release"]["prerelease"] = args.prerelease

        # Get GitHub token
        token = get_github_token(config)
        owner = config["github"]["owner"]
        repo = config["github"]["repo"]

        logger.info(f"Target repository: {owner}/{repo}")

        # Initialize release manager
        manager = ReleaseManager(token=token, owner=owner, repo=repo)

        # Check if release already exists
        if manager.release_exists(args.tag):
            print(f"\n⚠️  Release {args.tag} already exists!")
            print(f"   URL: https://github.com/{owner}/{repo}/releases/tag/{args.tag}")

            response = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'o', 'oui']:
                print("\n❌ Operation cancelled.")
                return 0

        # Prepare title
        title = args.title or f"v{args.tag}"

        # Prepare description
        description = ""
        if args.description:
            description = args.description
        elif args.description_file:
            desc_path = Path(args.description_file)
            if not desc_path.exists():
                print(f"\n❌ Description file not found: {desc_path}")
                return 1
            with open(desc_path, 'r', encoding='utf-8') as f:
                description = f.read()
        else:
            # Try to get description from git tag annotation
            import subprocess
            try:
                result = subprocess.run(
                    ['git', 'tag', '-l', '-n99', args.tag],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Skip first line (tag name) and get the rest
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    description = '\n'.join(lines[1:]).strip()
                    logger.info("Using description from git tag annotation")
            except Exception as e:
                logger.warning(f"Could not get tag annotation: {e}")

        if not description:
            description = f"Release {args.tag}"

        # Prepare assets
        assets = []
        if args.assets:
            for asset_str in args.assets:
                asset_path = Path(asset_str)
                if not asset_path.exists():
                    print(f"\n⚠️  Asset not found: {asset_path}")
                    continue
                assets.append(asset_path)

        # Auto-detect wheel
        if args.auto_wheel:
            wheel = manager.find_wheel_for_version(args.tag)
            if wheel:
                assets.append(wheel)

        # Display summary
        print(f"\n📦 GitHub Release Summary")
        print(f"   Repository: {owner}/{repo}")
        print(f"   Tag: {args.tag}")
        print(f"   Title: {title}")
        print(f"   Draft: {config['github']['release']['draft']}")
        print(f"   Pre-release: {config['github']['release']['prerelease']}")
        if assets:
            print(f"   Assets: {len(assets)}")
            for asset in assets:
                print(f"     - {asset.name} ({asset.stat().st_size / 1024:.1f} KB)")
        print("\n" + "=" * 70)

        # Create release
        print(f"\n🚀 Creating release...")
        release = manager.create_release_from_tag(
            tag=args.tag,
            title=title,
            description=description,
            assets=assets,
            draft=config["github"]["release"]["draft"],
            prerelease=config["github"]["release"]["prerelease"]
        )

        # Success
        print(f"\n✅ Release created successfully!")
        print(f"   URL: {release['html_url']}")
        if assets:
            print(f"   Assets uploaded: {len(assets)}")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Please check the logs for more details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
