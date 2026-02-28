#!/usr/bin/env python
"""
Clear Python cache files (__pycache__ directories and .pyc files)
for the Ambulon project.

Usage:
    python tools/clear_pycache.py
"""

import os
import shutil
from pathlib import Path


def clear_pycache(directory: str = "src") -> int:
    """
    Remove all __pycache__ directories and .pyc files recursively.
    
    Args:
        directory: Root directory to start cleaning from
        
    Returns:
        Number of directories/files removed
    """
    count = 0
    root_path = Path(directory)
    
    if not root_path.exists():
        print(f"Directory not found: {directory}")
        return 0
    
    # Walk through directory tree
    for path in root_path.rglob("*"):
        if path.is_dir() and path.name == "__pycache__":
            try:
                shutil.rmtree(path)
                print(f"Removed: {path}")
                count += 1
            except Exception as e:
                print(f"Error removing {path}: {e}")
        elif path.is_file() and path.suffix == ".pyc":
            try:
                path.unlink()
                print(f"Removed: {path}")
                count += 1
            except Exception as e:
                print(f"Error removing {path}: {e}")
    
    return count


def main():
    """Main entry point."""
    # Get project root (parent of tools directory)
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    
    print(f"Clearing Python cache in: {project_root}")
    print("-" * 50)
    
    # Clear cache in src directory
    src_dir = project_root / "src"
    if src_dir.exists():
        count = clear_pycache(str(src_dir))
        print(f"\nRemoved {count} cache items from src/")
    else:
        print("src/ directory not found")
    
    # Also check tests directory if it exists
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        count = clear_pycache(str(tests_dir))
        print(f"Removed {count} cache items from tests/")
    
    print("\n✓ Cache cleared!")
    return 0


if __name__ == "__main__":
    exit(main())
