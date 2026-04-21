"""Deprecated shim: re-exports ``make_html_interactive`` from ``add_augment``.

The original file was a character-corrupted duplicate of ``add_augment.py``
(only a function rename differed). The canonical implementation now lives in
``add_augment`` and is aliased so existing imports
``from app.processing.commands.make_html_interactive import make_html_interactive``
keep working.
"""

from .add_augment import augment, make_html_interactive, register_make_interactive_command

__all__ = ["augment", "make_html_interactive", "register_make_interactive_command"]
