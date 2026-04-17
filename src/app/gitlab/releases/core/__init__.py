"""Core functionality for GitLab releases management."""

from app.gitlab.releases.core.client import GitLabClient
from app.gitlab.releases.core.release_manager import GitLabReleaseManager

__all__ = ["GitLabClient", "GitLabReleaseManager"]
