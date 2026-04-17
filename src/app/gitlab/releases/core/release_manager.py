"""
GitLab Release Manager.

High-level release management with business logic.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.gitlab.releases.core.client import GitLabClient

logger = logging.getLogger(__name__)


class GitLabReleaseManager:
    """
    Manages GitLab releases with high-level operations.

    Example:
        >>> manager = GitLabReleaseManager(
        ...     token="glpat-...",
        ...     base_url="https://gitlab-forge.din.developpement-durable.gouv.fr",
        ...     project_id="snum/pnm3/gti/ambulon"
        ... )
        >>> release = manager.create_release_from_tag(
        ...     tag="3.8.0",
        ...     title="v3.8.0 - New Features",
        ...     description="...",
        ...     assets=[Path("dist/ambulon-3.8.0-py3-none-any.whl")]
        ... )
    """

    def __init__(self, token: str, base_url: str, project_id: str):
        """
        Initialize release manager.

        Args:
            token: GitLab token
            base_url: GitLab instance URL
            project_id: Project ID or namespace/project path
        """
        self.client = GitLabClient(token, base_url, project_id)
        self.base_url = base_url
        self.project_id = project_id

    def create_release_from_tag(
        self,
        tag: str,
        title: str,
        description: str,
        assets: Optional[List[Path]] = None,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete release from an existing tag.

        Args:
            tag: Git tag name (must exist)
            title: Release title
            description: Release description (Markdown)
            assets: List of file paths to upload
            ref: Git ref if tag doesn't exist yet

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If release creation fails
        """
        logger.info(f"Creating GitLab release for tag {tag}...")

        # Create release
        release = self.client.create_release(
            tag_name=tag,
            name=title,
            description=description,
            ref=ref
        )

        # Upload assets
        if assets:
            logger.info(f"Uploading {len(assets)} asset(s)...")
            for asset_path in assets:
                try:
                    self.client.upload_asset(release["tag_name"], asset_path)
                except Exception as e:
                    logger.error(f"Failed to upload {asset_path.name}: {e}")

        logger.info(f"Release complete: {release['_links']['self']}")
        return release

    def get_latest_release(self) -> Dict[str, Any]:
        """
        Get the latest release.

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If no release found
        """
        releases = self.client.list_releases(per_page=1)
        if not releases:
            raise ValueError("No releases found")

        return releases[0]

    def release_exists(self, tag: str) -> bool:
        """
        Check if a release exists for a tag.

        Args:
            tag: Tag name

        Returns:
            True if release exists
        """
        try:
            self.client.get_release(tag)
            return True
        except Exception:
            return False

    def find_wheel_for_version(self, version: str, dist_dir: Path = Path("dist")) -> Optional[Path]:
        """
        Find wheel file for a specific version.

        Args:
            version: Version string (e.g., "3.8.0")
            dist_dir: Distribution directory

        Returns:
            Path to wheel file or None
        """
        if not dist_dir.exists():
            logger.warning(f"Distribution directory not found: {dist_dir}")
            return None

        # Pattern: ambulon-{version}-py3-none-any.whl
        pattern = f"ambulon-{version}-py3-none-any.whl"
        wheel_path = dist_dir / pattern

        if wheel_path.exists():
            logger.info(f"Found wheel: {wheel_path}")
            return wheel_path

        # Try glob pattern
        wheels = list(dist_dir.glob(f"ambulon-{version}*.whl"))
        if wheels:
            logger.info(f"Found wheel: {wheels[0]}")
            return wheels[0]

        logger.warning(f"No wheel found for version {version} in {dist_dir}")
        return None

    def add_assets_to_release(self, tag: str, assets: List[Path]) -> Dict[str, Any]:
        """
        Add assets to an existing release.

        Args:
            tag: Tag name of the release
            assets: List of file paths to upload

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If release not found or upload fails
        """
        logger.info(f"Adding assets to existing GitLab release {tag}...")

        # Get existing release
        release = self.client.get_release(tag)

        # Upload assets
        if assets:
            logger.info(f"Uploading {len(assets)} asset(s)...")
            for asset_path in assets:
                try:
                    self.client.upload_asset(tag, asset_path)
                except Exception as e:
                    logger.error(f"Failed to upload {asset_path.name}: {e}")

        logger.info(f"Assets added to release: {release['_links']['self']}")
        return release
