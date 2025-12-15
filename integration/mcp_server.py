#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serveur MCP pour Ambulon - Permet à un assistant IA d'utiliser les fonctionnalités d'Ambulon
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Imports MCP
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Imports Ambulon
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from ambulon.scan import scan_document, process_existing_files as scan_process_files
from ambulon.ocr import perform_ocr, process_multiple_files as ocr_process_files

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ambulon-mcp")

# Créer le serveur MCP
server = Server("ambulon")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Liste tous les outils disponibles via Ambulon."""
    return [
        Tool(
            name="scan_document",
            description="Scanner un document avec NAPS2 et profils DPI configurables",
            inputSchema={
                "type": "object",
                "properties": {
                    "dpi": {
                        "type": "integer",
                        "enum": [100, 150, 200, 300, 600, 1200],
                        "description": "Résolution de scan en DPI",
                        "default": 300
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le fichier scanné (ex: 'scans/document.jpg')"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "png", "jpg", "jpeg", "tiff"],
                        "description": "Format de sortie",
                        "default": "jpg"
                    },
                    "color_mode": {
                        "type": "string",
                        "enum": ["color", "grayscale", "bw"],
                        "description": "Mode couleur",
                        "default": "color"
                    },
                    "paper_size": {
                        "type": "string",
                        "enum": ["A4", "A3", "Letter", "Legal"],
                        "description": "Taille du papier",
                        "default": "A4"
                    },
                    "number": {
                        "type": "integer",
                        "description": "Nombre de scans à effectuer",
                        "default": 1,
                        "minimum": 1
                    },
                    "ocr": {
                        "type": "boolean",
                        "description": "Activer l'OCR après le scan",
                        "default": False
                    },
                    "ocr_lang": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    },
                    "no_increment": {
                        "type": "boolean",
                        "description": "Utiliser le nom de fichier tel quel sans auto-incrémentation",
                        "default": False
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="ocr_image",
            description="Effectuer une reconnaissance optique de caractères (OCR) sur une image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier image à traiter"
                    },
                    "language": {
                        "type": "string",
                        "description": "Langue pour l'OCR (ex: 'fra', 'eng', 'fra+eng')",
                        "default": "fra"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le fichier texte (optionnel)"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="ocr_batch",
            description="Effectuer l'OCR sur plusieurs images en lot",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Pattern de fichiers (ex: 'scans/*.jpg', '*.png')"
                    },
                    "language": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Répertoire de sortie pour les fichiers texte (optionnel)"
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="scan_with_ocr",
            description="Scanner un document et effectuer l'OCR en une seule opération",
            inputSchema={
                "type": "object",
                "properties": {
                    "dpi": {
                        "type": "integer",
                        "enum": [100, 150, 200, 300, 600, 1200],
                        "description": "Résolution de scan en DPI",
                        "default": 300
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le fichier scanné"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "png", "jpg", "jpeg", "tiff"],
                        "description": "Format de sortie",
                        "default": "jpg"
                    },
                    "ocr_lang": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    },
                    "color_mode": {
                        "type": "string",
                        "enum": ["color", "grayscale", "bw"],
                        "description": "Mode couleur",
                        "default": "color"
                    },
                    "no_increment": {
                        "type": "boolean",
                        "description": "Utiliser le nom de fichier tel quel sans auto-incrémentation",
                        "default": False
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="process_existing_scans",
            description="Traiter des fichiers de scan existants (ex: pour ajouter l'OCR)",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Pattern de fichiers existants (ex: 'scans/*.jpg')"
                    },
                    "ocr": {
                        "type": "boolean",
                        "description": "Activer l'OCR",
                        "default": True
                    },
                    "ocr_lang": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    }
                },
                "required": ["pattern"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Gère les appels d'outils."""
    try:
        logger.info(f"Appel de l'outil: {name} avec arguments: {arguments}")
        
        if name == "scan_document":
            return await _handle_scan_document(arguments)
        elif name == "ocr_image":
            return await _handle_ocr_image(arguments)
        elif name == "ocr_batch":
            return await _handle_ocr_batch(arguments)
        elif name == "scan_with_ocr":
            return await _handle_scan_with_ocr(arguments)
        elif name == "process_existing_scans":
            return await _handle_process_existing_scans(arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Outil inconnu: {name}")],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Erreur lors de l'appel de l'outil {name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur: {str(e)}")],
            isError=True
        )

async def _handle_scan_document(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère le scan de document."""
    dpi = arguments.get("dpi", 300)
    output_path = Path(arguments["output_path"])
    
    scan_options = {
        "format": arguments.get("format", "jpg"),
        "color_mode": arguments.get("color_mode", "color"),
        "paper_size": arguments.get("paper_size", "A4"),
        "number": arguments.get("number", 1),
        "ocr": arguments.get("ocr", False),
        "lang": arguments.get("ocr_lang", "fra"),
        "no_increment": arguments.get("no_increment", False)
    }
    
    # Effectuer le scan
    result = scan_document(dpi, output_path.parent, **scan_options)
    
    if result["success"]:
        content = [TextContent(
            type="text",
            text=f"Scan réussi !\n"
                 f"DPI: {result['dpi']}\n"
                 f"Fichier: {result.get('output_file', 'Multiple files')}\n"
                 f"Options: {scan_options}"
        )]
        
        # Ajouter les informations sur les scans multiples si applicable
        if "multiple_scans" in result:
            files_info = "\n".join([f"- {r['output_file']}" for r in result['results']])
            content[0].text += f"\n\nFichiers générés ({result['successful_scans']}/{result['total_scans']}):\n{files_info}"
        
        return CallToolResult(content=content)
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de scan: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_ocr_image(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'OCR d'une image."""
    image_path = Path(arguments["image_path"])
    language = arguments.get("language", "fra")
    output_path = Path(arguments["output_path"]) if arguments.get("output_path") else None
    
    if not image_path.exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier image non trouvé: {image_path}")],
            isError=True
        )
    
    result = perform_ocr(image_path, language, output_path)
    
    if result["success"]:
        # Lire le contenu du fichier OCR pour l'inclure dans la réponse
        ocr_content = ""
        try:
            with open(result["output_file"], 'r', encoding='utf-8') as f:
                ocr_content = f.read()
        except Exception as e:
            logger.warning(f"Impossible de lire le fichier OCR: {e}")
        
        response_text = f"OCR réussi !\n"
        response_text += f"Fichier d'entrée: {result['input_file']}\n"
        response_text += f"Fichier de sortie: {result['output_file']}\n"
        response_text += f"Langue: {result['language']}\n"
        response_text += f"Taille: {result['file_size']} octets\n"
        
        if ocr_content:
            response_text += f"\nContenu extrait:\n{'-' * 40}\n{ocr_content}\n{'-' * 40}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur OCR: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_ocr_batch(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'OCR en lot."""
    pattern = arguments["pattern"]
    language = arguments.get("language", "fra")
    output_dir = Path(arguments["output_dir"]) if arguments.get("output_dir") else None
    
    result = ocr_process_files(pattern, language, output_dir, verbose=False)
    
    if result["success"]:
        files_info = []
        for file_info in result["processed_files"]:
            files_info.append(f"- {file_info['input_file']} → {file_info['output_file']} ({file_info['file_size']} octets)")
        
        response_text = f"OCR en lot réussi !\n"
        response_text += f"Fichiers traités: {result['successful_files']}/{result['total_files']}\n"
        response_text += f"Langue: {language}\n\n"
        response_text += "Fichiers traités:\n" + "\n".join(files_info)
        
        if result.get("errors"):
            response_text += f"\n\nErreurs:\n" + "\n".join([f"- {error}" for error in result["errors"]])
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur OCR en lot: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_scan_with_ocr(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère le scan avec OCR intégré."""
    dpi = arguments.get("dpi", 300)
    output_path = Path(arguments["output_path"])
    
    scan_options = {
        "format": arguments.get("format", "jpg"),
        "color_mode": arguments.get("color_mode", "color"),
        "ocr": True,
        "lang": arguments.get("ocr_lang", "fra"),
        "no_increment": arguments.get("no_increment", False)
    }
    
    result = scan_document(dpi, output_path.parent, **scan_options)
    
    if result["success"]:
        response_text = f"Scan avec OCR réussi !\n"
        response_text += f"DPI: {result['dpi']}\n"
        response_text += f"Fichier image: {result['output_file']}\n"
        response_text += f"Langue OCR: {scan_options['lang']}\n"
        
        # Essayer de lire le contenu OCR
        ocr_file = result['output_file'].with_suffix('.txt')
        if ocr_file.exists():
            try:
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    ocr_content = f.read()
                response_text += f"Fichier OCR: {ocr_file}\n"
                response_text += f"\nContenu extrait:\n{'-' * 40}\n{ocr_content}\n{'-' * 40}"
            except Exception as e:
                response_text += f"Fichier OCR créé mais impossible à lire: {e}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de scan avec OCR: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_process_existing_scans(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère le traitement de fichiers de scan existants."""
    pattern = arguments["pattern"]
    ocr_enabled = arguments.get("ocr", True)
    ocr_lang = arguments.get("ocr_lang", "fra")
    
    result = scan_process_files(pattern, ocr_enabled, ocr_lang, verbose=False)
    
    if result["success"]:
        files_info = []
        for file_info in result["processed_files"]:
            info = f"- {file_info['file']}"
            if 'ocr_file' in file_info:
                info += f" → OCR: {file_info['ocr_file']}"
            files_info.append(info)
        
        response_text = f"Traitement de fichiers existants réussi !\n"
        response_text += f"Fichiers traités: {result['successful_files']}/{result['total_files']}\n"
        
        if ocr_enabled:
            response_text += f"Langue OCR: {ocr_lang}\n"
        
        response_text += "\nFichiers traités:\n" + "\n".join(files_info)
        
        if result.get("errors"):
            response_text += f"\n\nErreurs:\n" + "\n".join([f"- {error}" for error in result["errors"]])
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de traitement: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def main():
    """Point d'entrée principal du serveur MCP."""
    if not MCP_AVAILABLE:
        logger.error("Les dépendances MCP ne sont pas installées. Installez avec: pip install mcp")
        sys.exit(1)
    
    # Créer le répertoire de logs si nécessaire
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("Démarrage du serveur MCP Ambulon...")
    
    # Lancer le serveur via stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ambulon",
                server_version="0.3.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serveur MCP pour Ambulon - Permet à un assistant IA d'utiliser les fonctionnalités d'Ambulon
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Imports MCP
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Imports Ambulon
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from ambulon.scan import scan_document, process_existing_files as scan_process_files
from ambulon.ocr import perform_ocr, process_multiple_files as ocr_process_files

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/mcp_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ambulon-mcp")

# Créer le serveur MCP
server = Server("ambulon")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Liste tous les outils disponibles via Ambulon."""
    return [
        Tool(
            name="scan_document",
            description="Scanner un document avec NAPS2 et profils DPI configurables",
            inputSchema={
                "type": "object",
                "properties": {
                    "dpi": {
                        "type": "integer",
                        "enum": [100, 150, 200, 300, 600, 1200],
                        "description": "Résolution de scan en DPI",
                        "default": 300
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le fichier scanné (ex: 'scans/document.jpg')"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "png", "jpg", "jpeg", "tiff"],
                        "description": "Format de sortie",
                        "default": "jpg"
                    },
                    "color_mode": {
                        "type": "string",
                        "enum": ["color", "grayscale", "bw"],
                        "description": "Mode couleur",
                        "default": "color"
                    },
                    "paper_size": {
                        "type": "string",
                        "enum": ["A4", "A3", "Letter", "Legal"],
                        "description": "Taille du papier",
                        "default": "A4"
                    },
                    "number": {
                        "type": "integer",
                        "description": "Nombre de scans à effectuer",
                        "default": 1,
                        "minimum": 1
                    },
                    "ocr": {
                        "type": "boolean",
                        "description": "Activer l'OCR après le scan",
                        "default": False
                    },
                    "ocr_lang": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="ocr_image",
            description="Effectuer une reconnaissance optique de caractères (OCR) sur une image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier image à traiter"
                    },
                    "language": {
                        "type": "string",
                        "description": "Langue pour l'OCR (ex: 'fra', 'eng', 'fra+eng')",
                        "default": "fra"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le fichier texte (optionnel)"
                    }
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="ocr_batch",
            description="Effectuer l'OCR sur plusieurs images en lot",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Pattern de fichiers (ex: 'scans/*.jpg', '*.png')"
                    },
                    "language": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Répertoire de sortie pour les fichiers texte (optionnel)"
                    }
                },
                "required": ["pattern"]
            }
        ),
        Tool(
            name="scan_with_ocr",
            description="Scanner un document et effectuer l'OCR en une seule opération",
            inputSchema={
                "type": "object",
                "properties": {
                    "dpi": {
                        "type": "integer",
                        "enum": [100, 150, 200, 300, 600, 1200],
                        "description": "Résolution de scan en DPI",
                        "default": 300
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le fichier scanné"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "png", "jpg", "jpeg", "tiff"],
                        "description": "Format de sortie",
                        "default": "jpg"
                    },
                    "ocr_lang": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    },
                    "color_mode": {
                        "type": "string",
                        "enum": ["color", "grayscale", "bw"],
                        "description": "Mode couleur",
                        "default": "color"
                    }
                },
                "required": ["output_path"]
            }
        ),
        Tool(
            name="process_existing_scans",
            description="Traiter des fichiers de scan existants (ex: pour ajouter l'OCR)",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Pattern de fichiers existants (ex: 'scans/*.jpg')"
                    },
                    "ocr": {
                        "type": "boolean",
                        "description": "Activer l'OCR",
                        "default": True
                    },
                    "ocr_lang": {
                        "type": "string",
                        "description": "Langue pour l'OCR",
                        "default": "fra"
                    }
                },
                "required": ["pattern"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Gère les appels d'outils."""
    try:
        logger.info(f"Appel de l'outil: {name} avec arguments: {arguments}")
        
        if name == "scan_document":
            return await _handle_scan_document(arguments)
        elif name == "ocr_image":
            return await _handle_ocr_image(arguments)
        elif name == "ocr_batch":
            return await _handle_ocr_batch(arguments)
        elif name == "scan_with_ocr":
            return await _handle_scan_with_ocr(arguments)
        elif name == "process_existing_scans":
            return await _handle_process_existing_scans(arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Outil inconnu: {name}")],
                isError=True
            )
    
    except Exception as e:
        logger.error(f"Erreur lors de l'appel de l'outil {name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur: {str(e)}")],
            isError=True
        )

async def _handle_scan_document(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère le scan de document."""
    dpi = arguments.get("dpi", 300)
    output_path = Path(arguments["output_path"])
    
    scan_options = {
        "format": arguments.get("format", "jpg"),
        "color_mode": arguments.get("color_mode", "color"),
        "paper_size": arguments.get("paper_size", "A4"),
        "number": arguments.get("number", 1),
        "ocr": arguments.get("ocr", False),
        "lang": arguments.get("ocr_lang", "fra")
    }
    
    # Effectuer le scan
    result = scan_document(dpi, output_path.parent, **scan_options)
    
    if result["success"]:
        content = [TextContent(
            type="text",
            text=f"Scan réussi !\n"
                 f"DPI: {result['dpi']}\n"
                 f"Fichier: {result.get('output_file', 'Multiple files')}\n"
                 f"Options: {scan_options}"
        )]
        
        # Ajouter les informations sur les scans multiples si applicable
        if "multiple_scans" in result:
            files_info = "\n".join([f"- {r['output_file']}" for r in result['results']])
            content[0].text += f"\n\nFichiers générés ({result['successful_scans']}/{result['total_scans']}):\n{files_info}"
        
        return CallToolResult(content=content)
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de scan: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_ocr_image(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'OCR d'une image."""
    image_path = Path(arguments["image_path"])
    language = arguments.get("language", "fra")
    output_path = Path(arguments["output_path"]) if arguments.get("output_path") else None
    
    if not image_path.exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier image non trouvé: {image_path}")],
            isError=True
        )
    
    result = perform_ocr(image_path, language, output_path)
    
    if result["success"]:
        # Lire le contenu du fichier OCR pour l'inclure dans la réponse
        ocr_content = ""
        try:
            with open(result["output_file"], 'r', encoding='utf-8') as f:
                ocr_content = f.read()
        except Exception as e:
            logger.warning(f"Impossible de lire le fichier OCR: {e}")
        
        response_text = f"OCR réussi !\n"
        response_text += f"Fichier d'entrée: {result['input_file']}\n"
        response_text += f"Fichier de sortie: {result['output_file']}\n"
        response_text += f"Langue: {result['language']}\n"
        response_text += f"Taille: {result['file_size']} octets\n"
        
        if ocr_content:
            response_text += f"\nContenu extrait:\n{'-' * 40}\n{ocr_content}\n{'-' * 40}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur OCR: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_ocr_batch(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'OCR en lot."""
    pattern = arguments["pattern"]
    language = arguments.get("language", "fra")
    output_dir = Path(arguments["output_dir"]) if arguments.get("output_dir") else None
    
    result = ocr_process_files(pattern, language, output_dir, verbose=False)
    
    if result["success"]:
        files_info = []
        for file_info in result["processed_files"]:
            files_info.append(f"- {file_info['input_file']} → {file_info['output_file']} ({file_info['file_size']} octets)")
        
        response_text = f"OCR en lot réussi !\n"
        response_text += f"Fichiers traités: {result['successful_files']}/{result['total_files']}\n"
        response_text += f"Langue: {language}\n\n"
        response_text += "Fichiers traités:\n" + "\n".join(files_info)
        
        if result.get("errors"):
            response_text += f"\n\nErreurs:\n" + "\n".join([f"- {error}" for error in result["errors"]])
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur OCR en lot: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_scan_with_ocr(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère le scan avec OCR intégré."""
    dpi = arguments.get("dpi", 300)
    output_path = Path(arguments["output_path"])
    
    scan_options = {
        "format": arguments.get("format", "jpg"),
        "color_mode": arguments.get("color_mode", "color"),
        "ocr": True,
        "lang": arguments.get("ocr_lang", "fra")
    }
    
    result = scan_document(dpi, output_path.parent, **scan_options)
    
    if result["success"]:
        response_text = f"Scan avec OCR réussi !\n"
        response_text += f"DPI: {result['dpi']}\n"
        response_text += f"Fichier image: {result['output_file']}\n"
        response_text += f"Langue OCR: {scan_options['lang']}\n"
        
        # Essayer de lire le contenu OCR
        ocr_file = result['output_file'].with_suffix('.txt')
        if ocr_file.exists():
            try:
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    ocr_content = f.read()
                response_text += f"Fichier OCR: {ocr_file}\n"
                response_text += f"\nContenu extrait:\n{'-' * 40}\n{ocr_content}\n{'-' * 40}"
            except Exception as e:
                response_text += f"Fichier OCR créé mais impossible à lire: {e}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de scan avec OCR: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def _handle_process_existing_scans(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère le traitement de fichiers de scan existants."""
    pattern = arguments["pattern"]
    ocr_enabled = arguments.get("ocr", True)
    ocr_lang = arguments.get("ocr_lang", "fra")
    
    result = scan_process_files(pattern, ocr_enabled, ocr_lang, verbose=False)
    
    if result["success"]:
        files_info = []
        for file_info in result["processed_files"]:
            info = f"- {file_info['file']}"
            if 'ocr_file' in file_info:
                info += f" → OCR: {file_info['ocr_file']}"
            files_info.append(info)
        
        response_text = f"Traitement de fichiers existants réussi !\n"
        response_text += f"Fichiers traités: {result['successful_files']}/{result['total_files']}\n"
        
        if ocr_enabled:
            response_text += f"Langue OCR: {ocr_lang}\n"
        
        response_text += "\nFichiers traités:\n" + "\n".join(files_info)
        
        if result.get("errors"):
            response_text += f"\n\nErreurs:\n" + "\n".join([f"- {error}" for error in result["errors"]])
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de traitement: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

async def main():
    """Point d'entrée principal du serveur MCP."""
    if not MCP_AVAILABLE:
        logger.error("Les dépendances MCP ne sont pas installées. Installez avec: pip install mcp")
        sys.exit(1)
    
    # Créer le répertoire de logs si nécessaire
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("Démarrage du serveur MCP Ambulon...")
    
    # Lancer le serveur via stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ambulon",
                server_version="0.3.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
