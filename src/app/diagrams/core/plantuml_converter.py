"""
DEPRECATED: This module has been merged into the unified diagrams core.

Please use app.diagrams.core.converters instead:
    from app.diagrams.core import convert_plantuml, convert_diagram

This file will be removed in a future version.
"""

# Re-export from the new unified module for backward compatibility
from .converters import (
    convert_plantuml,
    convert_mermaid,
    convert_graphviz,
    convert_diagram,
    CONVERTERS,
    _java_available,
    _kroki_module_available,
    _try_kroki_module_render,
)
from .svg_utils import clean_svg_content

__all__ = [
    'convert_plantuml',
    'convert_mermaid',
    'convert_graphviz',
    'convert_diagram',
    'clean_svg_content',
    'CONVERTERS',
]
