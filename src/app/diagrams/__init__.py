"""
Module Diagrams - Ambulon

Conversion et traitement de diagrammes (PlantUML, Mermaid, Graphviz) vers SVG.
Gestion des diagrammes dans les fichiers Markdown.
"""

# Import du core unifié
from .core import (
    # Types
    DiagramType,
    ConversionMethod,
    DiagramBlock,
    ConversionResult,
    Violation,
    
    # Détection
    extract_diagram_blocks,
    extract_diagram_blocks_from_file,
    get_diagram_stats,
    has_diagrams,
    count_diagrams,
    
    # Conversion
    convert_plantuml,
    convert_mermaid,
    convert_graphviz,
    convert_diagram,
    
    # SVG
    clean_svg_content,
    optimize_svg_for_pdf,
    wrap_svg_for_html,
    is_valid_svg,
    
    # Vérification
    PlantUMLChecker,
    check_plantuml_file,
    
    # Extraction
    extract_diagrams_to_files,
    batch_extract_diagrams,
    
    # Markdown to HTML
    markdown_to_html_basic,
    wrap_html_document,
    generate_toc,
)

# Import des commandes CLI
try:
    from .commands.diagram2svg4md import main as diagram2svg4md_cli
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load diagram2svg4md_cli: {e}")
    diagram2svg4md_cli = None

try:
    from .commands.md2html import main as md2html_cli
    from .commands.md2html import process_markdown_to_html
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not load md2html_cli: {e}")
    md2html_cli = None
    process_markdown_to_html = None

__all__ = [
    # Core - Types
    'DiagramType',
    'ConversionMethod',
    'DiagramBlock',
    'ConversionResult',
    'Violation',
    
    # Core - Detection
    'extract_diagram_blocks',
    'extract_diagram_blocks_from_file',
    'get_diagram_stats',
    'has_diagrams',
    'count_diagrams',
    
    # Core - Conversion
    'convert_plantuml',
    'convert_mermaid',
    'convert_graphviz',
    'convert_diagram',
    
    # Core - SVG
    'clean_svg_content',
    'optimize_svg_for_pdf',
    'wrap_svg_for_html',
    'is_valid_svg',
    
    # Core - Checking
    'PlantUMLChecker',
    'check_plantuml_file',
    
    # Core - Extraction
    'extract_diagrams_to_files',
    'batch_extract_diagrams',
    
    # Core - Markdown to HTML
    'markdown_to_html_basic',
    'wrap_html_document',
    'generate_toc',
    
    # CLI commands
    'diagram2svg4md_cli',
    'md2html_cli',
    'process_markdown_to_html',  # AVEC conversion des diagrammes
]
