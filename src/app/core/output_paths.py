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
    path_str = os.fspath(path)
    try:
        return os.path.relpath(path_str, start=os.fspath(Path.cwd()))
    except Exception:
        return path_str
