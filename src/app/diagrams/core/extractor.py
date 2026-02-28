"""
Extraction de diagrammes vers des fichiers séparés.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Iterable

from slugify import slugify

from .base import DiagramBlock, DiagramType, get_diagram_extension
from .detector import extract_diagram_blocks_from_file

logger = logging.getLogger(__name__)


def extract_diagrams_to_files(
    input_path: Path,
    output_dir: Optional[Path] = None,
    allowed_types: Optional[Iterable[DiagramType]] = None,
    naming_scheme: str = "{index:03d}_{caption}.{ext}"
) -> tuple[int, List[Path]]:
    """
    Extrait les blocs de diagrammes d'un fichier Markdown vers des fichiers séparés.
    
    Args:
        input_path: Chemin vers le fichier Markdown source
        output_dir: Répertoire de sortie (défaut: {input}-diagrams/)
        allowed_types: Types de diagrammes à extraire (None = tous)
        naming_scheme: Schéma de nommage des fichiers
        
    Returns:
        Tuple (code_retour, liste_fichiers_générés)
        
    Raises:
        FileNotFoundError: Si le fichier source n'existe pas
    """
    if not input_path.exists():
        logger.error("Input file does not exist: %s", input_path)
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    if not input_path.is_file():
        logger.error("Input path is not a file: %s", input_path)
        raise ValueError(f"Input path is not a file: {input_path}")
    
    # Détermine le répertoire de sortie
    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.stem}-diagrams"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extrait les diagrammes
    try:
        diagrams = extract_diagram_blocks_from_file(input_path, allowed_types)
    except Exception as exc:
        logger.error("Failed to extract diagrams: %s", exc)
        raise
    
    if not diagrams:
        logger.info("No diagram blocks found in %s", input_path)
        return 0, []
    
    # Génère les fichiers
    generated: List[Path] = []
    for index, block in enumerate(diagrams, start=1):
        file_path = _generate_diagram_file(
            block=block,
            index=index,
            output_dir=output_dir,
            naming_scheme=naming_scheme
        )
        generated.append(file_path)
    
    logger.info("Extracted %s diagram(s) to %s", len(generated), output_dir)
    return 0, generated


def _generate_diagram_file(
    block: DiagramBlock,
    index: int,
    output_dir: Path,
    naming_scheme: str
) -> Path:
    """
    Génère un fichier pour un diagramme.
    
    Args:
        block: Bloc de diagramme
        index: Numéro d'index
        output_dir: Répertoire de sortie
        naming_scheme: Schéma de nommage
        
    Returns:
        Chemin du fichier créé
    """
    # Détermine l'extension
    ext = get_diagram_extension(block.diagram_type)
    
    # Génère le nom de fichier
    caption_slug = _slugify_caption(block.figcaption or f"diagram-{index}")
    
    filename = naming_scheme.format(
        index=index,
        caption=caption_slug,
        ext=ext,
        type=block.diagram_type.value
    )
    
    # Nettoie le nom de fichier
    filename = _sanitize_filename(filename)
    
    output_path = output_dir / filename
    
    # Écrit le contenu
    output_path.write_text(block.content, encoding='utf-8')
    
    logger.debug("Created %s: %s lines", output_path, len(block.content.splitlines()))
    
    return output_path


def _slugify_caption(caption: str) -> str:
    """
    Convertit une légende en slug utilisable dans un nom de fichier.
    
    Args:
        caption: Texte de la légende
        
    Returns:
        Slug sécurisé pour nom de fichier
    """
    if not caption:
        return "unnamed"
    
    # Utilise python-slugify pour nettoyer
    slug = slugify(caption, max_length=50, word_boundary=True)
    
    if not slug:
        return "unnamed"
    
    return slug


def _sanitize_filename(filename: str) -> str:
    """
    Assainit un nom de fichier pour Windows/Unix.
    
    Args:
        filename: Nom de fichier potentiellement dangereux
        
    Returns:
        Nom de fichier sécurisé
    """
    # Caractères interdits sur Windows
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Évite les noms réservés Windows
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
        'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
        'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_without_ext = filename.split('.')[0].upper()
    if name_without_ext in reserved_names:
        filename = f"_{filename}"
    
    # Limite la longueur
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:200 - len(ext) - 1] if ext else name[:200]
        filename = f"{name}.{ext}" if ext else name
    
    return filename


def batch_extract_diagrams(
    input_files: List[Path],
    output_base_dir: Optional[Path] = None,
    allowed_types: Optional[Iterable[DiagramType]] = None
) -> dict[Path, tuple[int, List[Path]]]:
    """
    Extrait les diagrammes de plusieurs fichiers en batch.
    
    Args:
        input_files: Liste des fichiers à traiter
        output_base_dir: Répertoire de base pour les sorties
        allowed_types: Types de diagrammes à extraire
        
    Returns:
        Dictionnaire {fichier_source: (code_retour, fichiers_générés)}
    """
    results = {}
    
    for input_file in input_files:
        try:
            if output_base_dir:
                relative = input_file.parent.name if input_file.parent != Path('.') else input_file.stem
                output_dir = output_base_dir / relative / f"{input_file.stem}-diagrams"
            else:
                output_dir = None
            
            exit_code, generated = extract_diagrams_to_files(
                input_path=input_file,
                output_dir=output_dir,
                allowed_types=allowed_types
            )
            results[input_file] = (exit_code, generated)
            
        except Exception as e:
            logger.error("Failed to process %s: %s", input_file, e)
            results[input_file] = (1, [])
    
    return results
