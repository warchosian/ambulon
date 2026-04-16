"""
GitHub API client.

Wrapper around GitHub REST API for common operations.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


class GitHubClient:
    """
    GitHub API client for repository operations.

    Example:
        >>> client = GitHubClient(token="ghp_...", owner="warchosian", repo="ambulon")
        >>> release = client.create_release("3.5.0", "Release v3.5.0", "Description...")
        >>> client.upload_asset(release["id"], Path("dist/ambulon-3.5.0-py3-none-any.whl"))
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, owner: str, repo: str):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token with 'repo' scope
            owner: Repository owner (username or organization)
            repo: Repository name
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        })

    def create_release(
        self,
        tag_name: str,
        name: str,
        body: str,
        draft: bool = False,
        prerelease: bool = False,
        generate_release_notes: bool = False
    ) -> Dict[str, Any]:
        """
        Create a GitHub release.

        Args:
            tag_name: Git tag name (must exist)
            name: Release title
            body: Release description (Markdown)
            draft: Create as draft release
            prerelease: Mark as pre-release
            generate_release_notes: Auto-generate notes from commits

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If API call fails
        """
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/releases"

        payload = {
            "tag_name": tag_name,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease,
            "generate_release_notes": generate_release_notes
        }

        logger.info(f"Creating release {tag_name}...")
        response = self.session.post(url, json=payload)
        response.raise_for_status()

        release = response.json()
        logger.info(f"Release created: {release['html_url']}")

        return release

    def upload_asset(
        self,
        release_id: int,
        asset_path: Path,
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        Upload an asset to a release.

        Args:
            release_id: Release ID
            asset_path: Path to asset file
            content_type: MIME type

        Returns:
            Asset data dictionary

        Raises:
            FileNotFoundError: If asset file doesn't exist
            requests.HTTPError: If upload fails
        """
        if not asset_path.exists():
            raise FileNotFoundError(f"Asset not found: {asset_path}")

        # Get upload URL
        release = self.get_release(release_id)
        upload_url = release['upload_url'].replace('{?name,label}', '')
        upload_url = f"{upload_url}?name={asset_path.name}"

        logger.info(f"Uploading asset: {asset_path.name} ({asset_path.stat().st_size / 1024:.1f} KB)")

        # Upload file
        headers = {
            "Authorization": f"token {self.token}",
            "Content-Type": content_type
        }

        with open(asset_path, 'rb') as f:
            response = requests.post(upload_url, headers=headers, data=f)
            response.raise_for_status()

        asset = response.json()
        logger.info(f"Asset uploaded: {asset['browser_download_url']}")

        return asset

    def get_release(self, release_id: int) -> Dict[str, Any]:
        """
        Get release by ID.

        Args:
            release_id: Release ID

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If release not found
        """
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/releases/{release_id}"

        response = self.session.get(url)
        response.raise_for_status()

        return response.json()

    def get_release_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Get release by tag name.

        Args:
            tag: Tag name

        Returns:
            Release data dictionary

        Raises:
            requests.HTTPError: If release not found
        """
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/releases/tags/{tag}"

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
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/releases"

        response = self.session.get(url, params={"per_page": per_page})
        response.raise_for_status()

        return response.json()

    def delete_release(self, release_id: int) -> None:
        """
        Delete a release.

        Args:
            release_id: Release ID

        Raises:
            requests.HTTPError: If deletion fails
        """
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/releases/{release_id}"

        response = self.session.delete(url)
        response.raise_for_status()

        logger.info(f"Release {release_id} deleted")

    def update_release(
        self,
        release_id: int,
        name: Optional[str] = None,
        body: Optional[str] = None,
        draft: Optional[bool] = None,
        prerelease: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a release.

        Args:
            release_id: Release ID
            name: New release title
            body: New release description
            draft: Update draft status
            prerelease: Update prerelease status

        Returns:
            Updated release data

        Raises:
            requests.HTTPError: If update fails
        """
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/releases/{release_id}"

        payload = {}
        if name is not None:
            payload["name"] = name
        if body is not None:
            payload["body"] = body
        if draft is not None:
            payload["draft"] = draft
        if prerelease is not None:
            payload["prerelease"] = prerelease

        response = self.session.patch(url, json=payload)
        response.raise_for_status()

        release = response.json()
        logger.info(f"Release {release_id} updated")

        return release
