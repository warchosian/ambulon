"""
Module Processing - Ambulon

Traitement et manipulation de documents HTML et Markdown.
Ajout de TOC, fusion, aplatissement, concatenation.
"""

# Export des fonctions métier (pour MCP et usage programmatique)
# Import direct depuis commands pour éviter les problèmes d'imports des CLI apps
from .commands import (
    add_toc_to_html,
    add_toc_to_markdown,
    concatenate_html_files,
    flatten_html_directory,
    flatten_markdown_directory,
    fusion_html_files,
    fusion_markdown_files,
    md2project,
    project_to_markdown,
    make_html_interactive,
)

# Les CLI apps sont importées directement
# Si l'import échoue, on crée des dummy apps
try:
    from .commands.add_toc4html import app as add_toc4html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc4html_cli: {e}")
    add_toc4html_cli = None

try:
    from .commands.add_toc4md import app as add_toc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc4md_cli: {e}")
    add_toc4md_cli = None

try:
    from .commands.concat_html import app as concat_html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load concat_html_cli: {e}")
    concat_html_cli = None

try:
    from .commands.flatten_html import app as flatten_html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load flatten_html_cli: {e}")
    flatten_html_cli = None

try:
    from .commands.flatten_md import app as flatten_md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load flatten_md_cli: {e}")
    flatten_md_cli = None

try:
    from .commands.merge_html import app as merge_html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load merge_html_cli: {e}")
    merge_html_cli = None

try:
    from .commands.merge_md import app as merge_md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load merge_md_cli: {e}")
    merge_md_cli = None

try:
    from .commands.md2project import app as md2project_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load md2project_cli: {e}")
    md2project_cli = None

try:
    from .commands.project2md import app as project2md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load project2md_cli: {e}")
    project2md_cli = None

# Helper pour compatibilité
def get_cli_apps():
    """Retourne les CLI apps disponibles"""
    return {
        'add_toc4html_cli': add_toc4html_cli,
        'add_toc4md_cli': add_toc4md_cli,
        'concat_html_cli': concat_html_cli,
        'flatten_html_cli': flatten_html_cli,
        'flatten_md_cli': flatten_md_cli,
        'merge_html_cli': merge_html_cli,
        'merge_md_cli': merge_md_cli,
        'md2project_cli': md2project_cli,
        'project2md_cli': project2md_cli,
    }

__all__ = [
    # Functions (toujours disponibles)
    'add_toc_to_html',
    'add_toc_to_markdown',
    'concatenate_html_files',
    'flatten_html_directory',
    'flatten_markdown_directory',
    'fusion_html_files',
    'fusion_markdown_files',
    'md2project',
    'project_to_markdown',
    'make_html_interactive',
    # CLI apps
    'add_toc4html_cli',
    'add_toc4md_cli',
    'concat_html_cli',
    'flatten_html_cli',
    'flatten_md_cli',
    'merge_html_cli',
    'merge_md_cli',
    'md2project_cli',
    'project2md_cli',
    # Helper
    'get_cli_apps',
]
