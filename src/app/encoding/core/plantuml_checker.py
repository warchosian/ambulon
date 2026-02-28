"""
PlantUML Markdown Checker - Compatibility shim.

DEPRECATED: This module is kept for backward compatibility.
Please use app.diagrams.core.checker directly.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

# Import from the unified diagrams core
from app.diagrams.core import (
    PlantUMLChecker as _PlantUMLChecker,
    check_plantuml_file as _check_plantuml_file,
    Violation,
)

# Re-export for backward compatibility
__all__ = [
    'Violation',
    'PlantUMLChecker',
    'main',
]


class PlantUMLChecker(_PlantUMLChecker):
    """
    Vérificateur de conformité PlantUML.
    
    DEPRECATED: Use app.diagrams.core.PlantUMLChecker directly.
    """
    pass


def check_plantuml_file(
    file_path: Path | str,
    output_report: Optional[Path | str] = None
) -> tuple[int, int]:
    """
    Vérifie un fichier et génère un rapport.
    
    DEPRECATED: Use app.diagrams.core.check_plantuml_file directly.
    """
    return _check_plantuml_file(file_path, output_report)


def main():
    """Point d'entrée CLI - DEPRECATED."""
    if len(sys.argv) < 2:
        print("Usage: python plantuml_checker.py <fichier.md> [rapport.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    violations, critical = check_plantuml_file(input_file, output_file)

    print(f"Analyse terminee : {violations} violations detectees")
    if output_file:
        print(f"Rapport genere : {output_file}")

    sys.exit(1 if critical > 0 else 0)


if __name__ == '__main__':
    main()
