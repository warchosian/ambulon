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
    # Define dummy types for type hinting and instantiation to allow the module
    # to be imported without error even if MCP is not installed.
    class _Dummy:
        def __init__(self, *args, **kwargs): pass
        def list_tools(self): return lambda f: f
        def call_tool(self): return lambda f: f

    Server = _Dummy
    Tool = _Dummy
    CallToolResult = _Dummy
    TextContent = _Dummy
    # Add any other types that might be used in function signatures if needed
    ListToolsResult = _Dummy
    ImageContent = _Dummy
    EmbeddedResource = _Dummy
    InitializationOptions = _Dummy
    stdio_server = _Dummy
    CallToolRequest = _Dummy
    ListToolsRequest = _Dummy


# Imports Ambulon
from app.scan.core.scanning import scan_document
from app.scan.core.ocr import process_existing_files as scan_process_files
from app.ocr.core.ocr_logic import perform_ocr, process_multiple_files as ocr_process_files
from app.conversion.commands.img2pdf import images_to_pdf
from app.conversion.commands.compress_pdf import compress_pdf

# Imports WikiSI
from app.wikisi import scrape_wikisi, process_parkjson2json, process_parkjson2md

# Imports Conversion
from app.conversion import process_html_to_markdown, process_markdown_to_html, process_json_to_markdown

# Imports Processing
from app.processing import add_toc_to_markdown, fusion_markdown_files, flatten_markdown_directory

# Imports Encoding
from app.encoding import check_md_cli, fix_md_cli

# Configuration du logging
def setup_logging():
    """Configure le logging pour le serveur MCP"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(logs_dir / "mcp_server.log"),
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
        ),
        Tool(
            name="images_to_pdf",
            description="Convertir toutes les images d'un répertoire en un seul fichier PDF",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Répertoire contenant les images à convertir"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le PDF (optionnel)"
                    },
                    "compress": {
                        "type": "boolean",
                        "description": "Activer la compression pour réduire la taille",
                        "default": False
                    },
                    "quality": {
                        "type": "integer",
                        "description": "Qualité JPEG pour la compression (1-100)",
                        "default": 85,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="compress_pdf",
            description="Compresser un fichier PDF existant pour réduire sa taille",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier PDF à compresser"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin de sortie pour le PDF compressé (optionnel)"
                    },
                    "quality": {
                        "type": "integer",
                        "description": "Qualité JPEG pour la compression (1-100)",
                        "default": 85,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["input_path"]
            }
        ),
        # WikiSI Tools
        Tool(
            name="wikisi_scrape",
            description="Aspirer récursivement un site web WikiSI et télécharger toutes les pages HTML",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL du site WikiSI à aspirer"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Répertoire de sortie pour les fichiers téléchargés",
                        "default": "./wikisi-downloaded"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Profondeur maximale de récursion (-1 = illimité)",
                        "default": -1
                    },
                    "delay": {
                        "type": "number",
                        "description": "Délai entre requêtes en secondes",
                        "default": 1.0
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="wikisi_extract",
            description="Extraire et filtrer des applications depuis un fichier JSON du parc applicatif WikiSI",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier JSON d'entrée"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier JSON de sortie"
                    },
                    "range_spec": {
                        "type": "string",
                        "description": "Plage d'applications à extraire (ex: '1-10', '-5', '10-')"
                    },
                    "name_filter": {
                        "type": "string",
                        "description": "Filtrer par nom d'application (recherche insensible à la casse)"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        Tool(
            name="wikisi_to_markdown",
            description="Convertir un fichier JSON WikiSI en Markdown structuré pour RAG",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier JSON d'entrée"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown de sortie"
                    },
                    "range_spec": {
                        "type": "string",
                        "description": "Plage d'applications à convertir"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        # Conversion Tools
        Tool(
            name="html_to_markdown",
            description="Convertir un fichier HTML en Markdown lisible",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier HTML d'entrée"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown de sortie"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        Tool(
            name="markdown_to_html",
            description="Convertir un fichier Markdown en HTML",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown d'entrée"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier HTML de sortie"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        Tool(
            name="json_to_markdown",
            description="Convertir un fichier JSON en Markdown structuré",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier JSON d'entrée"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown de sortie"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        # Processing Tools
        Tool(
            name="add_toc_to_markdown",
            description="Ajouter une table des matières à un fichier Markdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown d'entrée"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown de sortie (optionnel, modifie l'original si non spécifié)"
                    },
                    "min_level": {
                        "type": "integer",
                        "description": "Niveau minimum de titre à inclure dans la TOC",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 6
                    },
                    "max_level": {
                        "type": "integer",
                        "description": "Niveau maximum de titre à inclure dans la TOC",
                        "default": 6,
                        "minimum": 1,
                        "maximum": 6
                    }
                },
                "required": ["input_file"]
            }
        ),
        Tool(
            name="merge_markdown_files",
            description="Fusionner plusieurs fichiers Markdown en un seul",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_dir": {
                        "type": "string",
                        "description": "Répertoire contenant les fichiers Markdown à fusionner"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Chemin vers le fichier Markdown fusionné"
                    }
                },
                "required": ["source_dir", "output_file"]
            }
        ),
        Tool(
            name="flatten_markdown_directory",
            description="Aplatir une arborescence de fichiers Markdown en structure plate",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_dir": {
                        "type": "string",
                        "description": "Répertoire source avec arborescence Markdown"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Répertoire de sortie pour la structure plate"
                    }
                },
                "required": ["source_dir", "output_dir"]
            }
        ),
        # Encoding Tools
        Tool(
            name="check_utf8_encoding",
            description="Vérifier l'encodage UTF-8 des fichiers Markdown dans un répertoire",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Répertoire contenant les fichiers Markdown à vérifier"
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="fix_utf8_encoding",
            description="Corriger l'encodage UTF-8 des fichiers Markdown dans un répertoire",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Répertoire contenant les fichiers Markdown à corriger"
                    }
                },
                "required": ["directory"]
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
        elif name == "images_to_pdf":
            return await _handle_images_to_pdf(arguments)
        elif name == "compress_pdf":
            return await _handle_compress_pdf(arguments)
        # WikiSI Tools
        elif name == "wikisi_scrape":
            return await _handle_wikisi_scrape(arguments)
        elif name == "wikisi_extract":
            return await _handle_wikisi_extract(arguments)
        elif name == "wikisi_to_markdown":
            return await _handle_wikisi_to_markdown(arguments)
        # Conversion Tools
        elif name == "html_to_markdown":
            return await _handle_html_to_markdown(arguments)
        elif name == "markdown_to_html":
            return await _handle_markdown_to_html(arguments)
        elif name == "json_to_markdown":
            return await _handle_json_to_markdown(arguments)
        # Processing Tools
        elif name == "add_toc_to_markdown":
            return await _handle_add_toc_to_markdown(arguments)
        elif name == "merge_markdown_files":
            return await _handle_merge_markdown_files(arguments)
        elif name == "flatten_markdown_directory":
            return await _handle_flatten_markdown_directory(arguments)
        # Encoding Tools
        elif name == "check_utf8_encoding":
            return await _handle_check_utf8_encoding(arguments)
        elif name == "fix_utf8_encoding":
            return await _handle_fix_utf8_encoding(arguments)
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


async def _handle_images_to_pdf(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la conversion d'images en PDF."""
    directory = arguments["directory"]
    output_path = arguments.get("output_path")
    compress = arguments.get("compress", False)
    quality = arguments.get("quality", 85)
    
    if not Path(directory).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Répertoire non trouvé: {directory}")],
            isError=True
        )
    
    result = images_to_pdf(directory, output_path, verbose=True, compress=compress, quality=quality)
    
    if result["success"]:
        response_text = f"Conversion images vers PDF réussie !\n"
        response_text += f"Répertoire source: {directory}\n"
        response_text += f"Fichier PDF: {result['output_file']}\n"
        response_text += f"Total de pages: {result['total_pages']}\n"
        response_text += f"Taille du fichier: {result['file_size'] / (1024*1024):.2f} MB\n"
        
        if result['compressed']:
            response_text += f"Compression appliquée (qualité: {result['quality']})"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de conversion: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )


async def _handle_compress_pdf(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la compression de PDF."""
    input_path = arguments["input_path"]
    output_path = arguments.get("output_path")
    quality = arguments.get("quality", 85)
    
    if not Path(input_path).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier PDF non trouvé: {input_path}")],
            isError=True
        )
    
    result = compress_pdf(input_path, output_path, quality, verbose=True)
    
    if result["success"]:
        response_text = f"Compression PDF réussie !\n"
        response_text += f"Fichier d'entrée: {result['input_file']}\n"
        response_text += f"Fichier de sortie: {result['output_file']}\n"
        response_text += f"Taille originale: {result['original_size'] / (1024*1024):.2f} MB\n"
        response_text += f"Taille compressée: {result['compressed_size'] / (1024*1024):.2f} MB\n"
        response_text += f"Réduction: {result['reduction_percent']:.1f}%\n"
        response_text += f"Pages traitées: {result['total_pages']}\n"
        response_text += f"Qualité: {result['quality']}"
        
        return CallToolResult(
            content=[TextContent(type="text", text=response_text)]
        )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur de compression: {result.get('error', 'Erreur inconnue')}")],
            isError=True
        )

# ============================================================================ 
# WikiSI Tools Handlers
# ============================================================================ 

async def _handle_wikisi_scrape(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'aspiration de site WikiSI."""
    url = arguments["url"]
    output_dir = arguments.get("output_dir", "./wikisi-downloaded")
    max_depth = arguments.get("max_depth", -1)
    delay = arguments.get("delay", 1.0)

    try:
        exit_code = scrape_wikisi(
            url=url,
            output_dir=output_dir,
            max_depth=max_depth,
            delay=delay,
            verbose=True
        )

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Site WikiSI aspiré avec succès !\n"
                         f"URL: {url}\n"
                         f"Répertoire de sortie: {output_dir}\n"
                         f"Profondeur maximale: {max_depth}\n"
                         f"Consultez le répertoire {output_dir} pour les fichiers téléchargés."
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de l'aspiration du site WikiSI (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de l'aspiration: {str(e)}")],
            isError=True
        )


async def _handle_wikisi_extract(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'extraction d'applications WikiSI."""
    input_file = arguments["input_file"]
    output_file = arguments["output_file"]
    range_spec = arguments.get("range_spec")
    name_filter = arguments.get("name_filter")

    if not Path(input_file).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier JSON non trouvé: {input_file}")],
            isError=True
        )

    try:
        exit_code = process_parkjson2json(
            input_file=input_file,
            output_file=output_file,
            verbose=True,
            range_spec=range_spec,
            name_filter=name_filter
        )

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Extraction WikiSI réussie !\n"
                         f"Fichier d'entrée: {input_file}\n"
                         f"Fichier de sortie: {output_file}\n"
                         f"Filtres appliqués: {range_spec or name_filter or 'Aucun'}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de l'extraction (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de l'extraction: {str(e)}")],
            isError=True
        )


async def _handle_wikisi_to_markdown(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la conversion WikiSI JSON vers Markdown."""
    input_file = arguments["input_file"]
    output_file = arguments["output_file"]
    range_spec = arguments.get("range_spec")

    if not Path(input_file).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier JSON non trouvé: {input_file}")],
            isError=True
        )

    try:
        exit_code = process_parkjson2md(
            input_file=input_file,
            output_file=output_file,
            verbose=True,
            range_spec=range_spec
        )

        if exit_code == 0:
            # Lire le contenu généré
            md_content = ""
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                    # Limiter à 2000 caractères pour la preview
                    if len(md_content) > 2000:
                        md_content = md_content[:2000] + "\n... (contenu tronqué)"
            except:
                pass

            response_text = f"Conversion WikiSI → Markdown réussie !\n"
            response_text += f"Fichier d'entrée: {input_file}\n"
            response_text += f"Fichier de sortie: {output_file}\n\n"
            if md_content:
                response_text += f"Aperçu du contenu :\n{'-' * 40}\n{md_content}\n{'-' * 40}"

            return CallToolResult(
                content=[TextContent(type="text", text=response_text)]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de la conversion (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la conversion: {str(e)}")],
            isError=True
        )


# ============================================================================ 
# Conversion Tools Handlers
# ============================================================================ 

async def _handle_html_to_markdown(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la conversion HTML vers Markdown."""
    input_file = arguments["input_file"]
    output_file = arguments["output_file"]

    if not Path(input_file).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier HTML non trouvé: {input_file}")],
            isError=True
        )

    try:
        exit_code = process_html_to_markdown(input_file, output_file, verbose=True)

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Conversion HTML → Markdown réussie !\n"
                         f"Fichier d'entrée: {input_file}\n"
                         f"Fichier de sortie: {output_file}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de la conversion (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la conversion: {str(e)}")],
            isError=True
        )


async def _handle_markdown_to_html(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la conversion Markdown vers HTML."""
    input_file = arguments["input_file"]
    output_file = arguments["output_file"]

    if not Path(input_file).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier Markdown non trouvé: {input_file}")],
            isError=True
        )

    try:
        exit_code = process_markdown_to_html(input_file, output_file, verbose=True)

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Conversion Markdown → HTML réussie !\n"
                         f"Fichier d'entrée: {input_file}\n"
                         f"Fichier de sortie: {output_file}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de la conversion (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la conversion: {str(e)}")],
            isError=True
        )


async def _handle_json_to_markdown(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la conversion JSON vers Markdown."""
    input_file = arguments["input_file"]
    output_file = arguments["output_file"]

    if not Path(input_file).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier JSON non trouvé: {input_file}")],
            isError=True
        )

    try:
        exit_code = process_json_to_markdown(input_file, output_file, verbose=True)

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Conversion JSON → Markdown réussie !\n"
                         f"Fichier d'entrée: {input_file}\n"
                         f"Fichier de sortie: {output_file}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de la conversion (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la conversion: {str(e)}")],
            isError=True
        )


# ============================================================================ 
# Processing Tools Handlers
# ============================================================================ 

async def _handle_add_toc_to_markdown(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'ajout de TOC à un fichier Markdown."""
    input_file = arguments["input_file"]
    output_file = arguments.get("output_file")
    min_level = arguments.get("min_level", 1)
    max_level = arguments.get("max_level", 6)

    if not Path(input_file).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Fichier Markdown non trouvé: {input_file}")],
            isError=True
        )

    try:
        exit_code = add_toc_to_markdown(input_file, output_file, min_level, max_level, verbose=True)

        if exit_code == 0:
            target = output_file or input_file
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Table des matières ajoutée avec succès !\n"
                         f"Fichier d'entrée: {input_file}\n"
                         f"Fichier de sortie: {target}\n"
                         f"Niveaux inclus: {min_level} à {max_level}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de l'ajout de la TOC (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de l'ajout de la TOC: {str(e)}")],
            isError=True
        )


async def _handle_merge_markdown_files(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la fusion de fichiers Markdown."""
    source_dir = arguments["source_dir"]
    output_file = arguments["output_file"]

    if not Path(source_dir).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Répertoire source non trouvé: {source_dir}")],
            isError=True
        )

    try:
        exit_code = fusion_markdown_files(source_dir, output_file, verbose=True)

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Fusion des fichiers Markdown réussie !\n"
                         f"Répertoire source: {source_dir}\n"
                         f"Fichier de sortie: {output_file}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de la fusion (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la fusion: {str(e)}")],
            isError=True
        )


async def _handle_flatten_markdown_directory(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère l'aplatissement d'arborescence Markdown."""
    source_dir = arguments["source_dir"]
    output_dir = arguments["output_dir"]

    if not Path(source_dir).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Répertoire source non trouvé: {source_dir}")],
            isError=True
        )

    try:
        exit_code = flatten_markdown_directory(source_dir, output_dir, verbose=True)

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Aplatissement réussi !\n"
                         f"Répertoire source: {source_dir}\n"
                         f"Répertoire de sortie: {output_dir}"
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de l'aplatissement (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de l'aplatissement: {str(e)}")],
            isError=True
        )


# ============================================================================ 
# Encoding Tools Handlers
# ============================================================================ 

async def _handle_check_utf8_encoding(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la vérification de l'encodage UTF-8."""
    directory = arguments["directory"]

    if not Path(directory).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Répertoire non trouvé: {directory}")],
            isError=True
        )

    try:
        # Sauvegarder argv et le modifier pour check_md_cli
        original_argv = sys.argv.copy()
        sys.argv = ['check_md_cli', directory]

        try:
            exit_code = check_md_cli()
        finally:
            sys.argv = original_argv

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Vérification d'encodage terminée !\n"
                         f"Répertoire vérifié: {directory}\n"
                         f"Consultez les logs pour les détails."
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Des problèmes d'encodage ont été détectés dans {directory}")],
                isError=False  # Pas une erreur, juste des problèmes trouvés
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la vérification: {str(e)}")],
            isError=True
        )


async def _handle_fix_utf8_encoding(arguments: Dict[str, Any]) -> CallToolResult:
    """Gère la correction de l'encodage UTF-8."""
    directory = arguments["directory"]

    if not Path(directory).exists():
        return CallToolResult(
            content=[TextContent(type="text", text=f"Répertoire non trouvé: {directory}")],
            isError=True
        )

    try:
        # Sauvegarder argv et le modifier pour fix_md_cli
        original_argv = sys.argv.copy()
        sys.argv = ['fix_md_cli', directory]

        try:
            exit_code = fix_md_cli()
        finally:
            sys.argv = original_argv

        if exit_code == 0:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Correction d'encodage terminée !\n"
                         f"Répertoire traité: {directory}\n"
                         f"Les fichiers ont été corrigés en UTF-8."
                )]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Erreur lors de la correction d'encodage (exit code: {exit_code})")],
                isError=True
            )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Erreur lors de la correction: {str(e)}")],
            isError=True
        )


async def run_server():
    """Lance le serveur MCP."""
    if not MCP_AVAILABLE:
        logger.error("Les dépendances MCP ne sont pas installées. Installez avec: pip install mcp")
        sys.exit(1)
    
    # Configurer le logging
    setup_logging()
    
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