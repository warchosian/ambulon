"""
Détection et extraction des blocs de diagrammes dans du Markdown.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterator, List, Optional, Dict, Any, Iterable

from .base import DiagramBlock, DiagramType, is_diagram_code_block, normalize_diagram_type

logger = logging.getLogger(__name__)


def extract_diagram_blocks(
    md_content: str,
    allowed_types: Optional[Iterable[DiagramType]] = None
) -> List[DiagramBlock]:
    """
    Extrait tous les blocs de diagrammes du contenu Markdown.
    
    Args:
        md_content: Contenu Markdown
        allowed_types: Types de diagrammes à extraire (None = tous)
        
    Returns:
        Liste des blocs de diagrammes trouvés
    """
    diagrams = []
    lines = md_content.split('\n')
    
    if allowed_types is not None:
        allowed_types = set(allowed_types)
    
    i = 0
    while i < len(lines):
        is_diagram, diagram_type = is_diagram_code_block(lines[i])
        
        if is_diagram and (allowed_types is None or diagram_type in allowed_types):
            start_line = i
            i += 1
            
            # Collecte le contenu jusqu'au ``` de fermeture
            diagram_lines = []
            while i < len(lines) and not lines[i].strip() == '```':
                diagram_lines.append(lines[i])
                i += 1
            
            if i < len(lines):  # Trouvé le fermant
                end_line = i
                
                # Construit le bloc complet
                full_block_lines = lines[start_line:end_line + 1]
                full_block = '\n'.join(full_block_lines)
                diagram_content = '\n'.join(diagram_lines)
                
                # Extrait la légende si présente
                figcaption = _extract_figcaption(lines, end_line + 1)
                
                diagrams.append(DiagramBlock(
                    diagram_type=diagram_type,
                    content=diagram_content,
                    start_line=start_line,
                    end_line=end_line,
                    full_block=full_block,
                    figcaption=figcaption
                ))
                
                logger.debug(f"Found {diagram_type.value} diagram at lines {start_line}-{end_line}")
        
        i += 1
    
    return diagrams


def extract_diagram_blocks_from_file(
    file_path: Path,
    allowed_types: Optional[Iterable[DiagramType]] = None
) -> List[DiagramBlock]:
    """
    Extrait les blocs de diagrammes d'un fichier Markdown.
    
    Args:
        file_path: Chemin vers le fichier Markdown
        allowed_types: Types de diagrammes à extraire
        
    Returns:
        Liste des blocs de diagrammes
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        IOError: Si erreur de lecture
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    content = file_path.read_text(encoding='utf-8')
    return extract_diagram_blocks(content, allowed_types)


def _extract_figcaption(lines: List[str], start_idx: int) -> Optional[str]:
    """
    Extrait la légende (figcaption) après un bloc de diagramme.
    
    Cherche dans les 5 lignes suivantes une balise <figcaption>.
    
    Args:
        lines: Toutes les lignes du document
        start_idx: Index de départ pour la recherche
        
    Returns:
        Texte de la légende ou None
    """
    figcaption_pattern = re.compile(r'<figcaption>(.*?)</figcaption>', re.IGNORECASE)
    
    for i in range(start_idx, min(start_idx + 5, len(lines))):
        match = figcaption_pattern.search(lines[i])
        if match:
            return match.group(1).strip()
    
    return None


def get_diagram_stats(diagrams: List[DiagramBlock]) -> Dict[str, Any]:
    """
    Calcule les statistiques sur les diagrammes trouvés.
    
    Args:
        diagrams: Liste des blocs de diagrammes
        
    Returns:
        Dictionnaire avec les statistiques
    """
    stats = {
        'total': len(diagrams),
        'plantuml': 0,
        'mermaid': 0,
        'graphviz': 0,
        'other': 0,
        'with_caption': 0,
        'without_caption': 0,
    }
    
    for diagram in diagrams:
        if diagram.diagram_type == DiagramType.PLANTUML:
            stats['plantuml'] += 1
        elif diagram.diagram_type == DiagramType.MERMAID:
            stats['mermaid'] += 1
        elif diagram.diagram_type == DiagramType.GRAPHVIZ:
            stats['graphviz'] += 1
        else:
            stats['other'] += 1
        
        if diagram.figcaption:
            stats['with_caption'] += 1
        else:
            stats['without_caption'] += 1
    
    return stats


def find_diagrams_in_directory(
    directory: Path,
    pattern: str = "*.md",
    allowed_types: Optional[Iterable[DiagramType]] = None
) -> Iterator[Tuple[Path, List[DiagramBlock]]]:
    """
    Trouve tous les diagrammes dans les fichiers Markdown d'un répertoire.
    
    Args:
        directory: Répertoire à scanner
        pattern: Pattern de fichiers à rechercher
        allowed_types: Types de diagrammes à extraire
        
    Yields:
        Tuples (chemin_fichier, liste_diagrammes)
    """
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return
    
    for md_file in directory.rglob(pattern):
        try:
            diagrams = extract_diagram_blocks_from_file(md_file, allowed_types)
            if diagrams:
                yield md_file, diagrams
        except Exception as e:
            logger.warning(f"Error processing {md_file}: {e}")


def has_diagrams(md_content: str) -> bool:
    """
    Vérifie si le contenu Markdown contient des diagrammes.
    
    Args:
        md_content: Contenu Markdown
        
    Returns:
        True si des diagrammes sont présents
    """
    return len(extract_diagram_blocks(md_content)) > 0


def count_diagrams(md_content: str) -> int:
    """
    Compte le nombre de diagrammes dans le contenu.
    
    Args:
        md_content: Contenu Markdown
        
    Returns:
        Nombre de diagrammes
    """
    return len(extract_diagram_blocks(md_content))
