#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serveur MCP Ambulon - Version Standalone
=========================================

Cette version importe uniquement les outils fonctionnels
et contourne les problèmes d'imports du projet principal.

Usage:
    python mcp_server_standalone.py
"""

import sys
import logging
from pathlib import Path

# Ajouter src au PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Configuration logging (fichier + stderr)
log_file = Path(__file__).parent / "mcp_server.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Import MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    logger.error("MCP SDK not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False
    sys.exit(1)

# Créer le serveur
server = Server("ambulon-standalone")

logger.info("=" * 70)
logger.info("SERVEUR MCP AMBULON - VERSION STANDALONE")
logger.info("=" * 70)

# Import des outils qui fonctionnent
tools_status = {}

# Test Scan
try:
    from app.scan.core.scanning import scan_document
    tools_status['scan'] = True
    logger.info("✓ Scan tools loaded")
except Exception as e:
    tools_status['scan'] = False
    logger.warning(f"✗ Scan tools failed: {e}")

# Test Conversion - Import depuis commands/
try:
    from app.conversion.commands.html2md import process_html_to_markdown
    from app.conversion.commands.md2html import process_markdown_to_html
    tools_status['conversion'] = True
    logger.info("✓ Conversion tools loaded")
except Exception as e:
    tools_status['conversion'] = False
    logger.warning(f"✗ Conversion tools failed: {e}")

# Définir les outils MCP disponibles
@server.list_tools()
async def list_tools():
    """Liste tous les outils MCP disponibles"""
    
    available_tools = []
    
    # Outils de conversion (toujours disponibles via import direct)
    available_tools.extend([
        Tool(
            name="html_to_markdown",
            description="Convertit un fichier HTML en Markdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Chemin du fichier HTML"},
                    "output_file": {"type": "string", "description": "Chemin du fichier Markdown de sortie"}
                },
                "required": ["input_file"]
            }
        ),
        Tool(
            name="markdown_to_html",
            description="Convertit un fichier Markdown en HTML",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string", "description": "Chemin du fichier Markdown"},
                    "output_file": {"type": "string", "description": "Chemin du fichier HTML de sortie"}
                },
                "required": ["input_file"]
            }
        ),
    ])
    
    if tools_status.get('scan'):
        available_tools.append(
            Tool(
                name="scan_document",
                description="Scanner un document avec NAPS2",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dpi": {"type": "integer", "description": "Résolution en DPI"},
                        "output_dir": {"type": "string", "description": "Répertoire de sortie"}
                    },
                    "required": ["dpi"]
                }
            )
        )
    
    logger.info(f"Exposing {len(available_tools)} MCP tools")
    return available_tools

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Exécute un outil MCP"""
    
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    try:
        if name == "html_to_markdown":
            from app.conversion.commands.html2md import process_html_to_markdown
            input_file = arguments["input_file"]
            output_file = arguments.get("output_file")

            exit_code = process_html_to_markdown(input_file, output_file, verbose=False)

            if exit_code == 0:
                result_path = Path(output_file) if output_file else Path(input_file).with_suffix(".md")
                return [TextContent(
                    type="text",
                    text=f"Conversion réussie: {result_path}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Erreur lors de la conversion"
                )]
        
        elif name == "markdown_to_html":
            from app.conversion.commands.md2html import process_markdown_to_html
            input_file = arguments["input_file"]
            output_file = arguments.get("output_file")

            exit_code = process_markdown_to_html(input_file, output_file, verbose=False)

            if exit_code == 0:
                result_path = Path(output_file) if output_file else Path(input_file).with_suffix(".html")
                return [TextContent(
                    type="text",
                    text=f"Conversion réussie: {result_path}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Erreur lors de la conversion"
                )]
        
        elif name == "scan_document":
            if not tools_status.get('scan'):
                return [TextContent(
                    type="text",
                    text="Scan tools not available"
                )]
            
            from app.scan.core.scanning import scan_document
            result = scan_document(
                dpi=arguments["dpi"],
                output_dir=Path(arguments.get("output_dir", "."))
            )
            return [TextContent(
                type="text",
                text=f"Scan réussi: {result}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Erreur: {str(e)}"
        )]

async def main():
    """Point d'entrée principal du serveur MCP"""
    logger.info("\nServeur MCP Ambulon démarré")
    logger.info(f"Outils actifs: {sum(tools_status.values())}/{len(tools_status)}")
    logger.info("En attente de connexions MCP...\n")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
