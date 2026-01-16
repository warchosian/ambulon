"""Module GitLab pour Ambulon - Clonage de projets GitLab."""

from .commands.gitlab_clone import main as gitlab_clone_main

__all__ = ['gitlab_clone_main']
