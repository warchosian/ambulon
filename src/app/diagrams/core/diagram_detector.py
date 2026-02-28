"""
DEPRECATED: This module has been merged into the unified diagrams core.

Please use app.diagrams.core.detector instead:
    from app.diagrams.core import extract_diagram_blocks, get_diagram_stats

This file will be removed in a future version.
"""

# Re-export from the new unified module for backward compatibility
from .detector import (
    extract_diagram_blocks,
    extract_diagram_blocks_from_file,
    get_diagram_stats,
    find_diagrams_in_directory,
    has_diagrams,
    count_diagrams,
    _extract_figcaption,
)

__all__ = [
    'extract_diagram_blocks',
    'extract_diagram_blocks_from_file',
    'get_diagram_stats',
    'find_diagrams_in_directory',
    'has_diagrams',
    'count_diagrams',
]
