"""
Module Processing - Ambulon

Traitement et manipulation de documents HTML et Markdown.
Ajout de TOC, fusion, aplatissement, concatenation.
"""

# Export des commandes principales
from .commands.add_toc4html import add_toc_to_html
from .commands.add_toc4md import add_toc_to_markdown
from .commands.concat_html import concatenate_html_files
from .commands.flatten_html import flatten_html_directory
from .commands.flatten_md import flatten_markdown_directory
from .commands.flatten_wikisi import flatten_wikisi_directory
from .commands.make_interactive import make_html_interactive
from .commands.merge_html import fusion_html_files
from .commands.merge_md import fusion_markdown_files
from .commands.md2project import md2project
from .commands.project2md import project_to_markdown

__all__ = [
    'add_toc_to_html',
    'add_toc_to_markdown',
    'concatenate_html_files',
    'flatten_html_directory',
    'flatten_markdown_directory',
    'flatten_wikisi_directory',
    'make_html_interactive',
    'fusion_html_files',
    'fusion_markdown_files',
    'md2project',
    'project_to_markdown',
]
