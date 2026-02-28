"""
Classes de base et types pour le module diagrams.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable


class DiagramType(Enum):
    """Types de diagrammes supportés."""
    PLANTUML = "plantuml"
    MERMAID = "mermaid"
    GRAPHVIZ = "graphviz"
    DOT = "dot"
    UNKNOWN = "unknown"


class ConversionMethod(Enum):
    """Méthodes de conversion disponibles."""
    KROKI = "kroki"
    JAR = "jar"
    AUTO = "auto"


@dataclass(frozen=True)
class DiagramBlock:
    """Représente un bloc de diagramme dans un fichier Markdown."""
    diagram_type: DiagramType
    content: str
    start_line: int
    end_line: int
    full_block: str
    figcaption: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def type_name(self) -> str:
        """Retourne le nom du type de diagramme."""
        return self.diagram_type.value


@dataclass
class ConversionResult:
    """Résultat d'une conversion de diagramme."""
    success: bool
    svg_content: Optional[str] = None
    error_message: Optional[str] = None
    method_used: Optional[str] = None


@dataclass
class Violation:
    """Représente une violation de règle PlantUML."""
    rule_number: str
    rule_name: str
    line_number: int
    severity: str  # "erreur" ou "warning"
    message: str
    code_snippet: str = ""


# Patterns pour la détection des diagrammes
DIAGRAM_PATTERNS = {
    DiagramType.PLANTUML: [
        re.compile(r'^```(?:plantuml|puml)\s*$', re.IGNORECASE),
    ],
    DiagramType.MERMAID: [
        re.compile(r'^```mermaid\s*$', re.IGNORECASE),
    ],
    DiagramType.GRAPHVIZ: [
        re.compile(r'^```(?:graphviz|dot)\s*$', re.IGNORECASE),
    ],
}

# Mapping des extensions de fichier
DIAGRAM_EXTENSIONS = {
    DiagramType.PLANTUML: ['puml', 'plantuml'],
    DiagramType.MERMAID: ['mmd', 'mermaid'],
    DiagramType.GRAPHVIZ: ['dot', 'gv'],
}


def normalize_diagram_type(type_str: str) -> DiagramType:
    """
    Normalise une chaîne de type en DiagramType.
    
    Args:
        type_str: Type de diagramme (ex: 'plantuml', 'puml', 'mermaid')
        
    Returns:
        DiagramType correspondant
    """
    type_lower = type_str.lower().strip()
    
    if type_lower in ('plantuml', 'puml'):
        return DiagramType.PLANTUML
    elif type_lower == 'mermaid':
        return DiagramType.MERMAID
    elif type_lower in ('graphviz', 'dot'):
        return DiagramType.GRAPHVIZ
    else:
        return DiagramType.UNKNOWN


def get_diagram_extension(diagram_type: DiagramType) -> str:
    """
    Retourne l'extension par défaut pour un type de diagramme.
    
    Args:
        diagram_type: Type de diagramme
        
    Returns:
        Extension de fichier (sans le point)
    """
    extensions = DIAGRAM_EXTENSIONS.get(diagram_type, ['txt'])
    return extensions[0] if extensions else 'txt'


def is_diagram_code_block(line: str) -> Tuple[bool, Optional[DiagramType]]:
    """
    Vérifie si une ligne démarre un bloc de code diagramme.
    
    Args:
        line: Ligne à analyser
        
    Returns:
        Tuple (est_un_diagramme, type_de_diagramme)
    """
    stripped = line.strip()
    
    for diagram_type, patterns in DIAGRAM_PATTERNS.items():
        for pattern in patterns:
            if pattern.match(stripped):
                return True, diagram_type
    
    return False, None
