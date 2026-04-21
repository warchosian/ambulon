"""Utilities for formatting output file paths."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike]


def format_output_path(path: PathLike) -> str:
    """
    Return a relative path (to cwd) using native OS separators.
    Falls back to the original path if relativization fails.
    """
    try:
        path_obj = Path(path)
        cwd = Path.cwd()
        return str(path_obj.relative_to(cwd))
    except (ValueError, Exception):
        # ValueError: path is not relative to cwd (different drives on Windows, etc.)
        # Fallback to absolute or original path
        return str(Path(path))
