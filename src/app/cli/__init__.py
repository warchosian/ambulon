"""Module principal d'Ambulon."""

from app import __version__

def hello():
    """Affiche un message de salutation avec la version courante."""
    return f"Hello Ambulon ! (Version: {__version__})"
