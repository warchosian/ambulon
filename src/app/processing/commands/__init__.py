"""Commandes de traitement de documents - Ambulon"""

from .add_toc4html import add_toc_to_html
from .add_toc4md import add_toc_to_markdown
from .concat_html import concatenate_html_files
from .flatten_html import flatten_html_directory
from .flatten_md import flatten_markdown_directory
from .flatten_wikisi import flatten_wikisi_directory
from .make_interactive import make_html_interactive
from .merge_html import fusion_html_files
from .merge_md import fusion_markdown_files
from .md2project import md2project
from .project2md import project_to_markdown

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
