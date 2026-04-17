"""
CLI command to create GitLab releases.

Usage: ambulon gitlab-release [OPTIONS]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from app.core.logging_config import setup_logging
from app.gitlab.releases.core.config import load_gitlab_config, get_gitlab_token, get_base_url, get_project_id
from app.gitlab.releases.core.release_manager import GitLabReleaseManager

logger = logging.getLogger(__name__)


def main(argv=None):
    """
    Create a GitLab release from an existing tag.

    Args:
        argv: Arguments CLI ou None pour sys.argv

    Returns:
        Code de sortie (0 = succès, non-zéro = erreur)
    """
    parser = argparse.ArgumentParser(
        prog="ambulon gitlab-release",
        description="Create a GitLab release from an existing tag with optional asset uploads.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration Hierarchy (priority from highest to lowest):
  1. Command-line arguments (--tag, --title, etc.)
  2. YAML configuration file (--config)
  3. Environment variables (GITLAB_*)
  4. Default values

Environment Variables:
  GITLAB_PRIVATE_TOKEN   GitLab personal access token (required)
  GITLAB_BASE_URL        GitLab instance URL (default: from config)
  GITLAB_PROJECT_ID      Project ID or namespace/project path

Examples:
  # Create release from latest tag with auto-detected wheel
  ambulon gitlab-release --tag 3.8.0

  # With custom title and description
  ambulon gitlab-release --tag 3.8.0 \\
    --title "v3.8.0 - New Features" \\
    --description "See CHANGELOG.md for details"

  # With specific assets
  ambulon gitlab-release --tag 3.8.0 \\
    --asset dist/ambulon-3.8.0-py3-none-any.whl \\
    --asset docs/manual.pdf

  # Create release with auto-wheel
  ambulon gitlab-release --tag 3.8.0 --auto-wheel

  # With configuration file
  ambulon gitlab-release --tag 3.8.0 -c config/gitlab.yaml

  # Specify different project
  ambulon gitlab-release --tag 1.0.0 \\
    --project-id "namespace/myproject" \\
    --base-url "https://gitlab.example.com"

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

    # Configuration
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Configuration file path (YAML)"
    )

    parser.add_argument(
        "--token",
        type=str,
        help="GitLab token (or use GITLAB_PRIVATE_TOKEN env var)"
    )

    parser.add_argument(
        "--base-url",
        type=str,
        help="GitLab instance URL (e.g., https://gitlab.example.com)"
    )

    parser.add_argument(
        "--project-id",
        type=str,
        help="Project ID (numeric) or namespace/project path"
    )

    parser.add_argument(
        "-y", "--yes", "--force",
        action="store_true",
        dest="force",
        help="Skip confirmation prompts"
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
    setup_logging(level=log_level, log_file_prefix="gitlab_release")

    logger.info("[START] GitLab release creation")

    try:
        # Load configuration
        config = load_gitlab_config(args.config)

        # Apply CLI arguments (highest priority)
        if args.token:
            config["gitlab"]["token"] = args.token
        if args.base_url:
            config["gitlab"]["base_url"] = args.base_url
        if args.project_id:
            config["gitlab"]["project_id"] = args.project_id

        # Get GitLab credentials
        token = get_gitlab_token(config)
        base_url = get_base_url(config)
        project_id = get_project_id(config)

        logger.info(f"Target project: {base_url}/{project_id}")

        # Initialize release manager
        manager = GitLabReleaseManager(token=token, base_url=base_url, project_id=project_id)

        # Check if release already exists
        release_exists = manager.release_exists(args.tag)
        if release_exists:
            print(f"\n⚠️  Release {args.tag} already exists!")
            print(f"   URL: {base_url}/{project_id}/-/releases/{args.tag}")

            if not args.force:
                response = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
                if response not in ['y', 'yes', 'o', 'oui']:
                    print("\n❌ Operation cancelled.")
                    return 0
            else:
                print("   --force specified, will add assets to existing release...")

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
                    check=True,
                    encoding='utf-8'
                )
                # Skip first line (tag name) and get the rest
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    description = '\n'.join(line.strip() for line in lines[1:]).strip()
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
        print(f"\n📦 GitLab Release Summary")
        print(f"   Instance: {base_url}")
        print(f"   Project: {project_id}")
        print(f"   Tag: {args.tag}")
        print(f"   Title: {title}")
        if assets:
            print(f"   Assets: {len(assets)}")
            for asset in assets:
                print(f"     - {asset.name} ({asset.stat().st_size / 1024:.1f} KB)")
        print("\n" + "=" * 70)

        # Create release or add assets to existing release
        if release_exists and args.force:
            print(f"\n📦 Adding assets to existing release...")
            if assets:
                release = manager.add_assets_to_release(tag=args.tag, assets=assets)
                print(f"\n✅ Assets added successfully!")
                print(f"   URL: {base_url}/{project_id}/-/releases/{args.tag}")
                print(f"   Assets uploaded: {len(assets)}")
            else:
                print(f"\n⚠️  No assets to upload.")
                release = manager.client.get_release(args.tag)
                print(f"   URL: {base_url}/{project_id}/-/releases/{args.tag}")
        else:
            print(f"\n🚀 Creating release...")
            release = manager.create_release_from_tag(
                tag=args.tag,
                title=title,
                description=description,
                assets=assets
            )

            # Success
            print(f"\n✅ Release created successfully!")
            print(f"   URL: {base_url}/{project_id}/-/releases/{args.tag}")
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
