"""
Core logic to isolate diagram blocks from a Markdown file.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from slugify import slugify

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiagramBlock:
    block_type: str
    content: str
    figcaption: Optional[str]


def _strip_blockquote_prefix(line: str) -> str:
    stripped = line.lstrip()
    if not stripped.startswith(">"):
        return line
    idx = line.find(">")
    rest = line[idx + 1 :]
    if rest.startswith(" "):
        rest = rest[1:]
    return rest


def _parse_fence_language(line: str) -> Optional[str]:
    stripped = _strip_blockquote_prefix(line).strip()
    if not stripped.startswith(""):
                break
            i += 1

        figcaption = _extract_figcaption(lines, i + 1)
        block_content = "\n".join(block_lines).rstrip() + "\n"
        blocks.append(DiagramBlock(block_type=lang, content=block_content, figcaption=figcaption))
        i += 1

    return blocks


def isolate_diagrams_logic(
    input_path: Path,
    output_dir: Optional[Path],
    allowed_types: Iterable[str],
) -> Tuple[int, List[Path]]:
    """
    Extract diagram blocks from a Markdown file and write each block into its own file.
    """
    if not input_path.exists():
        logger.error("Input Markdown file does not exist: %s", input_path)
        return 1, []

    try:
        content = input_path.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error("Failed to read Markdown file: %s", exc)
        return 1, []

    lines = content.splitlines()
    blocks = _extract_diagram_blocks(lines, allowed_types)
    if not blocks:
        logger.info("No diagram blocks found in %s", input_path)
        return 0, []

    if output_dir is None:
        output_dir = input_path.parent / f"{input_path.name}-diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    generated: List[Path] = []
    for index, block in enumerate(blocks, start=1):
        seq = f"{index:03d}"
        name = _slugify_caption(block.figcaption)
        ext = _sanitize_block_type(block.block_type)
        filename = f"{seq}_{name}.{ext}"
        output_path = output_dir / filename
        output_path.write_text(block.content, encoding="utf-8")
        generated.append(output_path)

    logger.info("Extracted %s diagram blocks.", len(generated))
    return 0, generated
