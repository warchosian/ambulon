"""
Core module for diagrams - Unified diagram processing functionality.

This module provides all the core functionality for working with diagrams:
- Detection of diagram blocks in Markdown
- Conversion to SVG (PlantUML, Mermaid, Graphviz)
- SVG cleaning and optimization
- PlantUML compliance checking
- Extraction to separate files
"""

from .base import (
    DiagramType,
    ConversionMethod,
    DiagramBlock,
    ConversionResult,
    Violation,
    normalize_diagram_type,
    get_diagram_extension,
    is_diagram_code_block,
    DIAGRAM_PATTERNS,
    DIAGRAM_EXTENSIONS,
)

from .detector import (
    extract_diagram_blocks,
    extract_diagram_blocks_from_file,
    get_diagram_stats,
    find_diagrams_in_directory,
    has_diagrams,
    count_diagrams,
)

from .converters import (
    convert_plantuml,
    convert_mermaid,
    convert_graphviz,
    convert_diagram,
    CONVERTERS,
)

from .svg_utils import (
    clean_svg_content,
    optimize_svg_for_pdf,
    extract_svg_viewbox,
    get_svg_dimensions,
    wrap_svg_for_html,
    is_valid_svg,
)

from .checker import (
    PlantUMLChecker,
    check_plantuml_file,
)

from .extractor import (
    extract_diagrams_to_files,
    batch_extract_diagrams,
)

from .markdown_to_html import (
    markdown_to_html_basic,
    wrap_html_document,
    generate_toc,
    convert_markdown_table,
    convert_inline_markdown,
)

__all__ = [
    # Enums and types
    'DiagramType',
    'ConversionMethod',
    'DiagramBlock',
    'ConversionResult',
    'Violation',
    
    # Base utilities
    'normalize_diagram_type',
    'get_diagram_extension',
    'is_diagram_code_block',
    'DIAGRAM_PATTERNS',
    'DIAGRAM_EXTENSIONS',
    
    # Detection
    'extract_diagram_blocks',
    'extract_diagram_blocks_from_file',
    'get_diagram_stats',
    'find_diagrams_in_directory',
    'has_diagrams',
    'count_diagrams',
    
    # Conversion
    'convert_plantuml',
    'convert_mermaid',
    'convert_graphviz',
    'convert_diagram',
    'CONVERTERS',
    
    # SVG utilities
    'clean_svg_content',
    'optimize_svg_for_pdf',
    'extract_svg_viewbox',
    'get_svg_dimensions',
    'wrap_svg_for_html',
    'is_valid_svg',
    
    # Checking
    'PlantUMLChecker',
    'check_plantuml_file',
    
    # Extraction
    'extract_diagrams_to_files',
    'batch_extract_diagrams',
    
    # Markdown to HTML
    'markdown_to_html_basic',
    'wrap_html_document',
    'generate_toc',
    'convert_markdown_table',
    'convert_inline_markdown',
]
