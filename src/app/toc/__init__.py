"""
Module TOC - Ambulon

Gestion de tables des matières pour documents Markdown et HTML.
Génération, ajout, vérification et navigation de TOC.
"""

# Import des CLI apps
try:
    from .commands.add_toc import add_toc_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc_cli: {e}")
    add_toc_cli = None

try:
    from .commands.add_toc4html import main as add_toc4html_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc4html_cli: {e}")
    add_toc4html_cli = None

try:
    from .commands.add_toc4md import main as add_toc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_toc4md_cli: {e}")
    add_toc4md_cli = None

try:
    from .commands.add_itoc4md import main as add_itoc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_itoc4md_cli: {e}")
    add_itoc4md_cli = None

try:
    from .commands.add_itoc import main as add_itoc_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load add_itoc_cli: {e}")
    add_itoc_cli = None

try:
    from .commands.check_toc4md import main as check_toc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load check_toc4md_cli: {e}")
    check_toc4md_cli = None

try:
    from .commands.check_itoc4md import main as check_itoc4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load check_itoc4md_cli: {e}")
    check_itoc4md_cli = None

# Helper pour compatibilité
def get_cli_apps():
    """Retourne les CLI apps disponibles pour la TOC"""
    return {
        'add_toc_cli': add_toc_cli,
        'add_toc4html_cli': add_toc4html_cli,
        'add_toc4md_cli': add_toc4md_cli,
        'add_itoc4md_cli': add_itoc4md_cli,
        'add_itoc_cli': add_itoc_cli,
        'check_toc4md_cli': check_toc4md_cli,
        'check_itoc4md_cli': check_itoc4md_cli,
    }

__all__ = [
    # CLI apps
    'add_toc_cli',
    'add_toc4html_cli',
    'add_toc4md_cli',
    'add_itoc4md_cli',
    'add_itoc_cli',
    'check_toc4md_cli',
    'check_itoc4md_cli',
    # Helper
    'get_cli_apps',
]
