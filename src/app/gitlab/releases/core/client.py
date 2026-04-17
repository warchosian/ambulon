"""
GitLab API client for releases management.

Wrapper around GitLab REST API for release operations.
Documentation: https://docs.gitlab.com/ee/api/releases/
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


class GitLabClient:
    """
    GitLab API client for release operations.

    Example:
        >>> client = GitLabClient(
        ...     token="glpat-...",
        ...     base_url="https://gitlab.com",
        ...     project_id="namespace/project"
        ... )
        >>> release = client.create_release("3.5.0", "Release v3.5.0", "Description...")
        >>> client.upload_asset(release["tag_name"], Path("dist/ambulon-3.5.0.whl"))
    """

    def __init__(self, token: str, base_url: str, project_id: str):
        """
        Initialize GitLab client.

        Args:
            token: GitLab personal access token with 'api' scope
            base_url: GitLab instance base URL (e.g., https://gitlab.com)
            project_id: Project ID (numeric) or namespace/project path
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        # URL-encode project_id if it contains slashes
        self.project_id = quote(str(project_id), safe='')
        self.session = requests.Session()
        self.session.headers.update({
            "Private-Token": token,
            "Content-Type": "application/json"
        })

    def create_release(
        self,
        tag_name: str,
        name: str,
        description: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a GitLab release.

        Args:
            tag_name: Git tag name (must exist)
            name: Release title/name
            description: Release description (Markdown)
            ref: Git ref (branch/commit) if tag doesn't exist yet

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/releases"

        payload = {
            "tag_name": tag_name,
            "name": name,
            "description": description
        }

        if ref:
            payload["ref"] = ref

        logger.info(f"Creating GitLab release {tag_name}...")
        response = self.session.post(url, json=payload)
        response.raise_for_status()

        release = response.json()
        logger.info(f"Release created: {release['_links']['self']}")

        return release

    def upload_asset(
        self,
        tag_name: str,
        asset_path: Path,
        asset_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload an asset to a release using GitLab Release Links.

        Note: GitLab doesn't store files like GitHub. Instead, it creates links
        to files uploaded to GitLab's generic package registry or external URLs.

        This method:
        1. Uploads the file to GitLab's generic package registry
        2. Creates a release link to that file

        Args:
            tag_name: Release tag name
            asset_path: Path to asset file
            asset_name: Optional custom name for the asset

        Returns:
            Release link data dictionary

        Raises:
            FileNotFoundError: If asset file doesn't exist
            requests.HTTPError: If upload fails
        """
        if not asset_path.exists():
            raise FileNotFoundError(f"Asset not found: {asset_path}")

        file_name = asset_name or asset_path.name

        logger.info(f"Uploading asset to GitLab package registry: {file_name}")

        # Step 1: Upload to generic package registry
        package_url = (
            f"{self.base_url}/api/v4/projects/{self.project_id}/"
            f"packages/generic/releases/{tag_name}/{file_name}"
        )

        with open(asset_path, 'rb') as f:
            upload_headers = {"Private-Token": self.token}
            upload_response = requests.put(
                package_url,
                headers=upload_headers,
                data=f
            )
            upload_response.raise_for_status()

        upload_data = upload_response.json()
        file_url = upload_data["url"]

        logger.info(f"Asset uploaded to package registry: {file_url}")

        # Step 2: Create release link
        link_url = f"{self.base_url}/api/v4/projects/{self.project_id}/releases/{tag_name}/assets/links"

        link_payload = {
            "name": file_name,
            "url": file_url,
            "link_type": "package"  # Can be: package, image, runbook, other
        }

        link_response = self.session.post(link_url, json=link_payload)
        link_response.raise_for_status()

        link_data = link_response.json()
        logger.info(f"Release link created: {file_name}")

        return link_data

    def get_release(self, tag_name: str) -> Dict[str, Any]:
        """
        Get release by tag name.

        Args:
            tag_name: Tag name

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If release not found
        """
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/releases/{tag_name}"

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

    def list_releases(self, per_page: int = 10) -> List[Dict[str, Any]]:
        """
        List repository releases.

        Args:
            per_page: Number of releases per page

        Returns:
            List of release dictionaries

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/releases"

        response = self.session.get(url, params={"per_page": per_page})
        response.raise_for_status()

        return response.json()

    def delete_release(self, tag_name: str) -> None:
        """
        Delete a release.

        Args:
            tag_name: Tag name

        Raises:
            requests.HTTPError: If deletion fails
        """
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/releases/{tag_name}"

        response = self.session.delete(url)
        response.raise_for_status()

        logger.info(f"Release {tag_name} deleted")

    def update_release(
        self,
        tag_name: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a release.

        Args:
            tag_name: Tag name
            name: New release title
            description: New release description

        Returns:
            Updated release data

        Raises:
            requests.HTTPError: If update fails
        """
        url = f"{self.base_url}/api/v4/projects/{self.project_id}/releases/{tag_name}"

        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.session.put(url, json=payload)
        response.raise_for_status()

        release = response.json()
        logger.info(f"Release {tag_name} updated")

        return release
