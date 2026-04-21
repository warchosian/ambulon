"""Commandes de traitement de documents - Ambulon"""

# TOC helpers live in app.toc (see app/toc/__init__.py) - not re-exported here.
from ..core.html_concatenator import concatenate_html_files_logic as concatenate_html_files
from ..core.html_flattener import flatten_html_directory_logic as flatten_html_directory
from ..core.markdown_flattener import flatten_markdown_directory_logic as flatten_markdown_directory
from ..core.html_merger import fusion_html_files_logic as fusion_html_files
from ..core.markdown_merger import fusion_markdown_files_logic as fusion_markdown_files
from ..core.md_to_project_converter import md2project_logic as md2project
from ..core.project_to_md_converter import project_to_markdown_logic as project_to_markdown

# make_html_interactive n'a pas de core/ séparé, c'est dans le command
from .make_html_interactive import make_html_interactive
from .md_to_interactive_html import md_to_interactive_html

__all__ = [
    'concatenate_html_files',
    'flatten_html_directory',
    'flatten_markdown_directory',
    'make_html_interactive',
    'md_to_interactive_html',
    'fusion_html_files',
    'fusion_markdown_files',
    'md2project',
    'project_to_markdown',
]
