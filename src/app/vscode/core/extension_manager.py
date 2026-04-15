"""
VS Code extension management module.

This module provides functions to install, uninstall, and list VS Code extensions.
"""

import subprocess
import logging
from typing import Set, Tuple

logger = logging.getLogger(__name__)


def get_installed_extensions(vscode_cmd: str) -> Set[str]:
    """
    Get the list of installed extensions.

    Args:
        vscode_cmd: Path or command to VS Code/VSCodium

    Returns:
        Set of installed extension IDs

    Raises:
        RuntimeError: If the command fails or times out
        FileNotFoundError: If the VS Code command doesn't exist
    """
    try:
        result = subprocess.run(
            [vscode_cmd, "--list-extensions"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        extensions = set(
            ext.strip()
            for ext in result.stdout.strip().split('\n')
            if ext.strip()
        )
        logger.debug(f"Found {len(extensions)} installed extensions")
        return extensions
    except FileNotFoundError:
        logger.error(f"VS Code command not found: {vscode_cmd}")
        raise FileNotFoundError(
            f"VS Code/VSCodium command not found: '{vscode_cmd}'. "
            f"Please verify the installation or specify --editor code/codium."
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        logger.error(f"Failed to list extensions: {error_msg}")
        raise RuntimeError(
            f"Failed to list extensions. Command '{vscode_cmd} --list-extensions' failed: {error_msg}"
        )
    except subprocess.TimeoutExpired:
        logger.error("Timeout while listing extensions (>30s)")
        raise RuntimeError(
            f"Timeout while listing extensions. Command '{vscode_cmd} --list-extensions' took more than 30 seconds."
        )


def install_extension(extension_id: str, vscode_cmd: str) -> Tuple[bool, str]:
    """
    Install a VS Code extension.

    Args:
        extension_id: Extension ID (e.g., "jebbs.plantuml")
        vscode_cmd: Path or command to VS Code/VSCodium

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        result = subprocess.run(
            [vscode_cmd, "--install-extension", extension_id],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        message = result.stdout.strip() or "Installed successfully"
        logger.info(f"Installed extension: {extension_id}")
        return True, message
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or str(e)
        logger.warning(f"Failed to install {extension_id}: {error_msg}")
        return False, error_msg
    except subprocess.TimeoutExpired:
        error_msg = "Installation timeout (>2 minutes)"
        logger.error(f"Timeout installing {extension_id}")
        return False, error_msg


def uninstall_extension(extension_id: str, vscode_cmd: str) -> bool:
    """
    Uninstall a VS Code extension.

    Args:
        extension_id: Extension ID to uninstall
        vscode_cmd: Path or command to VS Code/VSCodium

    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(
            [vscode_cmd, "--uninstall-extension", extension_id],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        logger.info(f"Uninstalled extension: {extension_id}")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Failed to uninstall {extension_id}: {e}")
        return False


def check_extension_installed(extension_id: str, vscode_cmd: str) -> bool:
    """
    Check if a specific extension is installed.

    Args:
        extension_id: Extension ID to check
        vscode_cmd: Path or command to VS Code/VSCodium

    Returns:
        True if installed, False otherwise
    """
    try:
        installed = get_installed_extensions(vscode_cmd)
        return extension_id in installed
    except subprocess.CalledProcessError:
        logger.warning(f"Failed to check if {extension_id} is installed")
        return False
