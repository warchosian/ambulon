"Module de gestion de la configuration MCP pour Ambulon."

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    from importlib.resources import files
except ImportError:
    # Fallback pour Python < 3.9
    from importlib_resources import files


# The content of mcp-config.json is embedded here to ensure it's always included.
_MCP_CONFIG_DATA = {
  "mcpServers": {
    "ambulon": {
      "command": "python",
      "args": ["-m", "ambulon.mcp"],
      "cwd": ".",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  },
  "server": {
    "name": "ambulon",
    "version": "0.3.0",
    "description": "Serveur MCP pour Ambulon - Scanner et OCR via assistant IA",
    "capabilities": {
      "tools": {
        "listChanged": True
      }
    }
  },
  "tools": [
    {
      "name": "scan_document",
      "description": "Scanner un document avec NAPS2 et profils DPI configurables",
      "category": "scan",
      "examples": [
        {
          "description": "Scanner un document A4 en 300 DPI",
          "arguments": {
            "dpi": 300,
            "output_path": "scans/document.jpg",
            "format": "jpg",
            "paper_size": "A4"
          }
        },
        {
          "description": "Scanner avec nom de fichier exact (sans auto-incrémentation)",
          "arguments": {
            "dpi": 300,
            "output_path": "documents/rapport.jpg",
            "format": "jpg",
            "no_increment": True
          }
        },
        {
          "description": "Scanner plusieurs pages avec OCR",
          "arguments": {
            "dpi": 300,
            "output_path": "scans/multi_page.pdf",
            "format": "pdf",
            "number": 3,
            "ocr": True,
            "ocr_lang": "fra"
          }
        }
      ]
    },
    {
      "name": "ocr_image",
      "description": "Effectuer une reconnaissance optique de caractères (OCR) sur une image",
      "category": "ocr",
      "examples": [
        {
          "description": "OCR d'une image en français",
          "arguments": {
            "image_path": "scans/document.jpg",
            "language": "fra"
          }
        },
        {
          "description": "OCR multilingue français-anglais",
          "arguments": {
            "image_path": "scans/document.jpg",
            "language": "fra+eng",
            "output_path": "textes/document.txt"
          }
        }
      ]
    },
    {
      "name": "ocr_batch",
      "description": "Effectuer l'OCR sur plusieurs images en lot",
      "category": "ocr",
      "examples": [
        {
          "description": "OCR de tous les JPG d'un dossier",
          "arguments": {
            "pattern": "scans/*.jpg",
            "language": "fra",
            "output_dir": "textes/"
          }
        }
      ]
    },
    {
      "name": "scan_with_ocr",
      "description": "Scanner un document et effectuer l'OCR en une seule opération",
      "category": "scan+ocr",
      "examples": [
        {
          "description": "Scanner et extraire le texte directement",
          "arguments": {
            "dpi": 300,
            "output_path": "scans/document_with_text.jpg",
            "ocr_lang": "fra"
          }
        },
        {
          "description": "Scanner avec nom exact et OCR",
          "arguments": {
            "dpi": 300,
            "output_path": "documents/contrat.jpg",
            "ocr_lang": "fra",
            "no_increment": True
          }
        }
      ]
    },
    {
      "name": "process_existing_scans",
      "description": "Traiter des fichiers de scan existants (ex: pour ajouter l'OCR)",
      "category": "processing",
      "examples": [
        {
          "description": "Ajouter l'OCR à des scans existants",
          "arguments": {
            "pattern": "scans/*.jpg",
            "ocr": True,
            "ocr_lang": "fra"
          }
        }
      ]
    }
  ],
  "installation": {
    "requirements": [
      "mcp",
      "ambulon"
    ],
    "setup_commands": [
      "pip install mcp",
      "poetry install"
    ]
  },
  "usage": {
    "description": "Ce serveur MCP permet à un assistant IA d'utiliser les fonctionnalités de scan et d'OCR d'Ambulon",
    "integration_examples": [
      {
        "assistant": "Claude Desktop",
        "config_locations": {
          "Windows": "%APPDATA%\Claude\claude_desktop_config.json",
          "macOS": "~/Library/Application Support/Claude/claude_desktop_config.json",
          "Linux": "~/.config/Claude/claude_desktop_config.json"
        },
        "config_snippet": {
          "mcpServers": {
            "ambulon": {
              "command": "python",
              "args": ["-m", "ambulon.mcp"]
            }
          }
        }
      },
      {
        "assistant": "Cline VSCode",
        "config_location": ".vscode/settings.json",
        "config_snippet": {
          "cline.mcp.servers": [
            {
              "name": "ambulon",
              "command": "python",
              "args": ["-m", "ambulon.mcp"]
            }
          ]
        }
      }
    ]
  }
}

def get_mcp_config() -> Dict[str, Any]:
    """
    Récupère la configuration MCP embarquée dans le package.
    
    Returns:
        Dict contenant la configuration MCP
    """
    return _MCP_CONFIG_DATA


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


def get_config_paths() -> Dict[str, Dict[str, Path]]:
    """
    Retourne les chemins de configuration pour tous les assistants supportés.
    
    Returns:
        Dict avec les chemins pour chaque assistant
    """
    system = platform.system()
    home = Path.home()
    
    paths = {
        "claude": {},
        "openrouter": {},
        "aider": {},
        "continue": {}
    }
    
    if system == "Windows":
        appdata = Path(os.environ.get("APPDATA", ""))
        localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
        
        paths["claude"]["config"] = appdata / "Claude" / "claude_desktop_config.json"
        paths["openrouter"]["config"] = appdata / "OpenRouter" / "config.json"
        paths["aider"]["config"] = home / ".aider" / "config.json"
        paths["continue"]["config"] = appdata / "Code" / "User" / "settings.json"
        
    elif system == "Darwin":  # macOS
        paths["claude"]["config"] = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        paths["openrouter"]["config"] = home / "Library" / "Application Support" / "OpenRouter" / "config.json"
        paths["aider"]["config"] = home / ".aider" / "config.json"
        paths["continue"]["config"] = home / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        
    else:  # Linux
        paths["claude"]["config"] = home / ".config" / "Claude" / "claude_desktop_config.json"
        paths["openrouter"]["config"] = home / ".config" / "openrouter" / "config.json"
        paths["aider"]["config"] = home / ".aider" / "config.json"
        paths["continue"]["config"] = home / ".config" / "Code" / "User" / "settings.json"
    
    return paths


def get_claude_config_path() -> Path:
    """
    Retourne le chemin vers le fichier de configuration Claude Desktop.
    
    Returns:
        Path vers claude_desktop_config.json
    """
    return get_config_paths()["claude"]["config"]


def create_claude_config(force: bool = False) -> Dict[str, Any]:
    """
    Crée la configuration Claude Desktop avec le serveur Ambulon.
    
    Args:
        force: Forcer l'écrasement si le fichier existe
        
    Returns:
        Configuration créée
    """
    config_path = get_claude_config_path()
    
    # Créer le répertoire parent si nécessaire
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configuration de base pour Claude
    claude_config = {
        "mcpServers": {
            "ambulon": {
                "command": "python",
                "args": ["-m", "ambulon.mcp"],
                "cwd": str(Path.cwd()),
                "env": {
                    "PYTHONPATH": str(Path.cwd() / "src")
                }
            }
        }
    }
    
    # Si le fichier existe, fusionner avec la config existante
    if config_path.exists() and not force:
        try:
            with config_path.open("r", encoding="utf-8") as f:
                existing_config = json.load(f)
            
            # Fusionner les serveurs MCP
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            
            existing_config["mcpServers"]["ambulon"] = claude_config["mcpServers"]["ambulon"]
            claude_config = existing_config
            
        except (json.JSONDecodeError, Exception):
            # Si erreur de lecture, utiliser la nouvelle config
            pass
    
    # Écrire la configuration
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(claude_config, f, indent=2, ensure_ascii=False)
    
    return claude_config


def create_openrouter_config(force: bool = False) -> Dict[str, Any]:
    """
    Crée la configuration OpenRouter avec le serveur Ambulon.
    
    Args:
        force: Forcer l'écrasement si le fichier existe
        
    Returns:
        Configuration créée
    """
    config_path = get_config_paths()["openrouter"]["config"]
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    openrouter_config = {
        "mcp_servers": {
            "ambulon": {
                "command": "python",
                "args": ["-m", "ambulon.mcp"],
                "working_directory": str(Path.cwd()),
                "environment": {
                    "PYTHONPATH": str(Path.cwd() / "src")
                }
            }
        }
    }
    
    if config_path.exists() and not force:
        try:
            with config_path.open("r", encoding="utf-8") as f:
                existing_config = json.load(f)
            
            if "mcp_servers" not in existing_config:
                existing_config["mcp_servers"] = {}
            
            existing_config["mcp_servers"]["ambulon"] = openrouter_config["mcp_servers"]["ambulon"]
            openrouter_config = existing_config
            
        except (json.JSONDecodeError, Exception):
            pass
    
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(openrouter_config, f, indent=2, ensure_ascii=False)
    
    return openrouter_config


def create_aider_config(force: bool = False) -> Dict[str, Any]:
    """
    Crée la configuration Aider avec le serveur Ambulon.
    
    Args:
        force: Forcer l'écrasement si le fichier existe
        
    Returns:
        Configuration créée
    """
    config_path = get_config_paths()["aider"]["config"]
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    aider_config = {
        "mcp": {
            "servers": {
                "ambulon": {
                    "command": "python",
                    "args": ["-m", "ambulon.mcp"],
                    "cwd": str(Path.cwd()),
                    "env": {
                        "PYTHONPATH": str(Path.cwd() / "src")
                    }
                }
            }
        }
    }
    
    if config_path.exists() and not force:
        try:
            with config_path.open("r", encoding="utf-8") as f:
                existing_config = json.load(f)
            
            if "mcp" not in existing_config:
                existing_config["mcp"] = {}
            if "servers" not in existing_config["mcp"]:
                existing_config["mcp"]["servers"] = {}
            
            existing_config["mcp"]["servers"]["ambulon"] = aider_config["mcp"]["servers"]["ambulon"]
            aider_config = existing_config
            
        except (json.JSONDecodeError, Exception):
            pass
    
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(aider_config, f, indent=2, ensure_ascii=False)
    
    return aider_config


def create_continue_config(force: bool = False) -> Dict[str, Any]:
    """
    Crée la configuration Continue (VSCode) avec le serveur Ambulon.
    
    Args:
        force: Forcer l'écrasement si le fichier existe
        
    Returns:
        Configuration créée
    """
    config_path = get_config_paths()["continue"]["config"]
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    continue_mcp_config = {
        "name": "ambulon",
        "command": "python",
        "args": ["-m", "ambulon.mcp"],
        "cwd": str(Path.cwd()),
        "env": {
            "PYTHONPATH": str(Path.cwd() / "src")
        }
    }
    
    vscode_config = {}
    
    if config_path.exists() and not force:
        try:
            with config_path.open("r", encoding="utf-8") as f:
                vscode_config = json.load(f)
        except (json.JSONDecodeError, Exception):
            pass
    
    # Ajouter la configuration MCP pour Continue
    if "continue.mcp.servers" not in vscode_config:
        vscode_config["continue.mcp.servers"] = []
    
    # Supprimer l'ancienne config ambulon si elle existe
    vscode_config["continue.mcp.servers"] = [
        server for server in vscode_config["continue.mcp.servers"] 
        if server.get("name") != "ambulon"
    ]
    
    # Ajouter la nouvelle config
    vscode_config["continue.mcp.servers"].append(continue_mcp_config)
    
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(vscode_config, f, indent=2, ensure_ascii=False)
    
    return vscode_config


def test_mcp_server() -> Dict[str, Any]:
    """
    Teste si le serveur MCP Ambulon fonctionne correctement.
    
    Returns:
        Résultats des tests
    """
    results = {
        "server_accessible": False,
        "tools_available": False,
        "tools_count": 0,
        "error": None
    }
    
    try:
        # Tester l'import du module MCP
        import ambulon.mcp
        results["server_accessible"] = True
        
        # Tester l'accès aux outils (simulation)
        from ambulon.mcp import server
        if hasattr(server, '_tools'):
            results["tools_available"] = True
            results["tools_count"] = len(server._tools) if server._tools else 0
        
    except ImportError as e:
        results["error"] = f"Module MCP non accessible: {e}"
    except Exception as e:
        results["error"] = f"Erreur lors du test: {e}"
    
    return results


def get_installation_status() -> Dict[str, Dict[str, Any]]:
    """
    Vérifie le statut d'installation pour tous les assistants.
    
    Returns:
        Statut pour chaque assistant
    """
    paths = get_config_paths()
    status = {}
    
    for assistant, assistant_paths in paths.items():
        config_path = assistant_paths["config"]
        
        status[assistant] = {
            "config_exists": config_path.exists(),
            "config_path": str(config_path),
            "directory_exists": config_path.parent.exists(),
            "ambulon_configured": False
        }
        
        # Vérifier si Ambulon est configuré
        if config_path.exists():
            try:
                with config_path.open("r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # Vérifier selon le format de chaque assistant
                if assistant == "claude":
                    status[assistant]["ambulon_configured"] = (
                        "mcpServers" in config and 
                        "ambulon" in config["mcpServers"]
                    )
                elif assistant == "openrouter":
                    status[assistant]["ambulon_configured"] = (
                        "mcp_servers" in config and 
                        "ambulon" in config["mcp_servers"]
                    )
                elif assistant == "aider":
                    status[assistant]["ambulon_configured"] = (
                        "mcp" in config and 
                        "servers" in config["mcp"] and
                        "ambulon" in config["mcp"]["servers"]
                    )
                elif assistant == "continue":
                    servers = config.get("continue.mcp.servers", [])
                    status[assistant]["ambulon_configured"] = any(
                        server.get("name") == "ambulon" for server in servers
                    )
                    
            except (json.JSONDecodeError, Exception):
                pass
    
    return status
