"""Module de gestion de la configuration MCP pour Ambulon."""

import json
from pathlib import Path
from typing import Dict, Any

try:
    from importlib.resources import files
except ImportError:
    # Fallback pour Python < 3.9
    from importlib_resources import files


def get_mcp_config() -> Dict[str, Any]:
    """
    Récupère la configuration MCP depuis les ressources du package.
    
    Returns:
        Dict contenant la configuration MCP
    """
    try:
        # Accès au fichier via les ressources du package
        config_file = files("ambulon").parent / "config" / "mcp-config.json"
        with config_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback vers le fichier local si disponible
        local_config = Path("config/mcp-config.json")
        if local_config.exists():
            with local_config.open("r", encoding="utf-8") as f:
                return json.load(f)
        raise FileNotFoundError("Configuration MCP introuvable")


def export_mcp_config(output_path: Path = None) -> Path:
    """
    Exporte le fichier de configuration MCP vers un répertoire spécifié.
    
    Args:
        output_path: Chemin de destination (par défaut: ./mcp-config.json)
        
    Returns:
        Path vers le fichier exporté
    """
    if output_path is None:
        output_path = Path("mcp-config.json")
    
    config = get_mcp_config()
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return output_path


def get_claude_config_path() -> Path:
    """
    Retourne le chemin vers le fichier de configuration Claude Desktop.
    
    Returns:
        Path vers claude_desktop_config.json
    """
    import os
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":  # macOS
        home = Path.home()
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:  # Linux
        home = Path.home()
        return home / ".config" / "Claude" / "claude_desktop_config.json"
