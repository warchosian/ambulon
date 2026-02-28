"""
Module Processing - Ambulon

Traitement et manipulation de documents HTML et Markdown.
Ajout de TOC, fusion, aplatissement, concatenation.
"""

# Export des fonctions métier (pour MCP et usage programmatique)
# Import direct depuis commands pour éviter les problèmes d'imports des CLI apps
from .commands import (
    # add_toc_to_html,  # TODO: module n'existe pas encore
    # add_toc_to_markdown,  # TODO: module n'existe pas encore
    concatenate_html_files,
    flatten_html_directory,
    flatten_markdown_directory,
    fusion_html_files,
    fusion_markdown_files,
    md2project,
    project_to_markdown,
    make_html_interactive,
    md_to_interactive_html,
)

# Les CLI apps sont importées directement
# Si l'import échoue, on crée des dummy apps
# Les apps TOC sont maintenant dans app.toc
try:
    from app.toc import add_toc4html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc4html_cli: {e}")
    add_toc4html_cli = None

try:
    from app.toc import add_toc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc4md_cli: {e}")
    add_toc4md_cli = None

try:
    from app.toc import add_itoc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_itoc4md_cli: {e}")
    add_itoc4md_cli = None

try:
    from app.toc import check_toc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load check_toc4md_cli: {e}")
    check_toc4md_cli = None

try:
    from app.toc import check_itoc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load check_itoc4md_cli: {e}")
    check_itoc4md_cli = None

try:
    from .commands.concat_html import main as concat_html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load concat_html_cli: {e}")
    concat_html_cli = None

try:
    from .commands.flatten_html import main as flatten_html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load flatten_html_cli: {e}")
    flatten_html_cli = None

try:
    from .commands.flatten_md import main as flatten_md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load flatten_md_cli: {e}")
    flatten_md_cli = None

try:
    from .commands.merge_html import main as merge_html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load merge_html_cli: {e}")
    merge_html_cli = None

try:
    from .commands.merge_md import main as merge_md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load merge_md_cli: {e}")
    merge_md_cli = None

try:
    from .commands.md2project import main as md2project_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load md2project_cli: {e}")
    md2project_cli = None

try:
    from .commands.project2md import main as project2md_cli
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
        'add_itoc4md_cli': add_itoc4md_cli,
        'check_toc4md_cli': check_toc4md_cli,
        'check_itoc4md_cli': check_itoc4md_cli,
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
    # 'add_toc_to_html',  # TODO: module n'existe pas encore
    'add_toc_to_markdown',
    'concatenate_html_files',
    'flatten_html_directory',
    'flatten_markdown_directory',
    'fusion_html_files',
    'fusion_markdown_files',
    'md2project',
    'project_to_markdown',
    'make_html_interactive',
    'md_to_interactive_html',
    # CLI apps
    'add_toc4html_cli',
    'add_toc4md_cli',
    'add_itoc4md_cli',
    'check_toc4md_cli',
    'check_itoc4md_cli',
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
