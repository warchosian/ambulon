"""
VS Code / VSCodium detection module.

This module handles automatic detection of VS Code and VSCodium installations
on Windows, Linux, and macOS.
"""

import os
import subprocess
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def find_vscode_command(preferred_editor: Optional[str] = None) -> str:
    """
    Find VS Code or VSCodium command on the system.

    Args:
        preferred_editor: 'code', 'codium', or None for auto-detection

    Returns:
        Path or command to the VS Code/VSCodium executable

    Raises:
        FileNotFoundError: If no VS Code/VSCodium installation is found
        ValueError: If preferred_editor is invalid
    """
    # If a specific editor is requested
    if preferred_editor:
        return _find_specific_editor(preferred_editor)

    # Auto-detection: try 'code' first, then 'codium' in PATH
    for cmd in ["code", "codium"]:
        if _is_command_available(cmd):
            logger.info(f"Using {cmd} (auto-detected in PATH)")
            return cmd

    # Try common installation paths
    checked_paths = []
    for cmd, paths in _get_common_paths().items():
        for path in paths:
            checked_paths.append(path)
            if os.path.exists(path):
                logger.info(f"Using {path} (auto-detected)")
                return path

    # Build detailed error message
    error_msg = (
        "Neither VS Code nor VSCodium found on this system.\n\n"
        "Checked locations:\n"
    )
    for path in checked_paths[:10]:  # Show first 10 paths
        error_msg += f"  - {path}\n"
    if len(checked_paths) > 10:
        error_msg += f"  ... and {len(checked_paths) - 10} more\n"

    error_msg += (
        "\nPlease:\n"
        "  1. Install VS Code (https://code.visualstudio.com/) or\n"
        "     VSCodium (https://vscodium.com/), or\n"
        "  2. Add 'code' or 'codium' command to your system PATH, or\n"
        "  3. Specify the editor explicitly with --editor code/codium"
    )
    raise FileNotFoundError(error_msg)


def get_vscode_version(vscode_cmd: str) -> str:
    """
    Get the version of VS Code/VSCodium.

    Args:
        vscode_cmd: Path or command to VS Code/VSCodium

    Returns:
        Version string (e.g., "1.85.0") or "unknown" if it fails
    """
    try:
        result = subprocess.run(
            [vscode_cmd, "--version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        # First line is the version
        lines = result.stdout.strip().split('\n')
        if lines:
            version = lines[0].strip()
            logger.debug(f"Detected version: {version}")
            return version
        else:
            logger.warning("Version command returned empty output")
            return "unknown"
    except FileNotFoundError:
        logger.warning(f"Command not found: {vscode_cmd}")
        return "unknown"
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to get version (command failed): {e}")
        return "unknown"
    except subprocess.TimeoutExpired:
        logger.warning(f"Version check timed out for: {vscode_cmd}")
        return "unknown"
    except (IndexError, AttributeError) as e:
        logger.warning(f"Failed to parse version output: {e}")
        return "unknown"
    except Exception as e:
        logger.warning(f"Unexpected error getting version: {e}")
        return "unknown"


def is_vscode_installed(preferred_editor: Optional[str] = None) -> bool:
    """
    Check if VS Code or VSCodium is installed.

    Args:
        preferred_editor: 'code', 'codium', or None for any

    Returns:
        True if installed, False otherwise
    """
    try:
        find_vscode_command(preferred_editor)
        return True
    except FileNotFoundError:
        return False


# Private helper functions

def _find_specific_editor(editor: str) -> str:
    """Find a specific editor (code or codium)."""
    # Validate editor choice
    if editor not in ["code", "codium"]:
        raise ValueError(f"Invalid editor '{editor}'. Must be 'code' or 'codium'.")

    # Try command in PATH
    if _is_command_available(editor):
        logger.info(f"Using {editor} (specified, found in PATH)")
        return editor

    # Try common installation paths
    paths = _get_common_paths().get(editor, [])
    checked_paths = []
    for path in paths:
        checked_paths.append(path)
        if os.path.exists(path):
            logger.info(f"Using {path} (specified)")
            return path

    # Build helpful error message
    editor_name = "VS Code" if editor == "code" else "VSCodium"
    error_msg = (
        f"{editor_name} ('{editor}') not found on this system.\n"
        f"Checked locations:\n"
    )
    for path in checked_paths:
        error_msg += f"  - {path}\n"
    error_msg += (
        f"\nPlease:\n"
        f"  1. Install {editor_name}, or\n"
        f"  2. Add '{editor}' command to your system PATH, or\n"
        f"  3. Use the other editor (--editor {'codium' if editor == 'code' else 'code'})"
    )
    raise FileNotFoundError(error_msg)


def _is_command_available(cmd: str) -> bool:
    """Check if a command is available in PATH."""
    try:
        subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _get_common_paths() -> dict[str, list[str]]:
    """Get common installation paths for VS Code and VSCodium."""
    paths = {
        "code": [],
        "codium": []
    }

    if os.name == "nt":  # Windows
        paths["code"] = [
            r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
            r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
        ]
        paths["codium"] = [
            r"C:\Program Files\VSCodium\bin\codium.cmd",
            r"C:\Program Files (x86)\VSCodium\bin\codium.cmd",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\VSCodium\bin\codium.cmd"),
            # Custom portable path (from original script)
            r"G:\WarchoLife\WarchoPortable\PortableCommon\VSCodium\vscodium-1.109.41146\bin\codium.cmd",
        ]
    elif os.name == "posix":  # Linux/macOS
        paths["code"] = [
            "/usr/bin/code",
            "/usr/local/bin/code",
            os.path.expanduser("~/.local/bin/code"),
        ]
        paths["codium"] = [
            "/usr/bin/codium",
            "/usr/local/bin/codium",
            os.path.expanduser("~/.local/bin/codium"),
        ]

        # macOS specific paths
        if os.uname().sysname == "Darwin":
            paths["code"].append("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code")
            paths["codium"].append("/Applications/VSCodium.app/Contents/Resources/app/bin/codium")

    return paths
