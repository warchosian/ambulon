"""
Core logic to isolate diagram blocks from a Markdown file.

DEPRECATED: This module is kept for backward compatibility.
Please use app.diagrams.core.extractor directly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

# Import from the unified diagrams core
from app.diagrams.core import (
    DiagramBlock,
    DiagramType,
    extract_diagrams_to_files as _extract_diagrams_to_files,
    batch_extract_diagrams as _batch_extract_diagrams,
)

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = [
    'DiagramBlock',
    'isolate_diagrams_logic',
]


def isolate_diagrams_logic(
    input_path: Path,
    output_dir: Optional[Path],
    allowed_types: Iterable[str],
) -> Tuple[int, List[Path]]:
    """
    Extract diagram blocks from a Markdown file and write each block into its own file.
    
    DEPRECATED: Use app.diagrams.core.extract_diagrams_to_files() instead.
    
    Args:
        input_path: Path to input Markdown file
        output_dir: Directory for output files (default: {input}-diagrams/)
        allowed_types: List of allowed diagram type strings (e.g., ['plantuml', 'mermaid'])
        
    Returns:
        Tuple of (exit_code, list_of_generated_files)
    """
    # Convert string types to DiagramType enum
    diagram_types = None
    if allowed_types:
        diagram_types = []
        for t in allowed_types:
            try:
                diagram_types.append(DiagramType(t.lower()))
            except ValueError:
                logger.warning(f"Unknown diagram type: {t}")
    
    try:
        exit_code, generated = _extract_diagrams_to_files(
            input_path=input_path,
            output_dir=output_dir,
            allowed_types=diagram_types
        )
        return exit_code, generated
    except FileNotFoundError:
        logger.error("Input Markdown file does not exist: %s", input_path)
        return 1, []
    except Exception as exc:
        logger.error("Failed to extract diagrams: %s", exc)
        return 1, []


# Alias for backward compatibility
extract_diagrams = isolate_diagrams_logic
