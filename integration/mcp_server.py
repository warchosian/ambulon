#!/usr/bin/env python3
"""
MCP Server for dyag - Allows AI assistants to use dyag tools directly.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from dyag.commands.img2pdf import images_to_pdf
from dyag.commands.compresspdf import compress_pdf
from dyag.commands.md2html import process_markdown_to_html
from dyag.commands.analyze_training import analyze_training_coverage
from dyag.rag_query import RAGQuerySystem
from dyag.commands.evaluate_rag import load_dataset, evaluate_rag
from dyag.commands.index_rag import ChunkIndexer


class MCPServer:
    """MCP Server implementation for dyag."""

    def __init__(self):
        self.tools = {
            "dyag_img2pdf": {
                "description": "Convert images in a directory to a PDF file. Images are sorted alphabetically by filename.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Path to directory containing images"
                        },
                        "output": {
                            "type": "string",
                            "description": "Optional output PDF path. If not specified, creates PDF in source directory with directory name"
                        },
                        "compress": {
                            "type": "boolean",
                            "description": "Enable compression to reduce PDF size",
                            "default": False
                        },
                        "quality": {
                            "type": "integer",
                            "description": "JPEG quality for compression (1-100, default 85)",
                            "default": 85,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed progress",
                            "default": False
                        }
                    },
                    "required": ["directory"]
                }
            },
            "dyag_compresspdf": {
                "description": "Compress an existing PDF file by reprocessing its images with JPEG compression.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Path to input PDF file to compress"
                        },
                        "output": {
                            "type": "string",
                            "description": "Optional output PDF path. If not specified, adds '_compressed' suffix"
                        },
                        "quality": {
                            "type": "integer",
                            "description": "JPEG quality for compression (1-100, default 85). Lower values = smaller file size but lower quality",
                            "default": 85,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed progress",
                            "default": False
                        }
                    },
                    "required": ["input"]
                }
            },
            "dyag_md2html": {
                "description": "Convert Markdown files with diagrams (Graphviz, PlantUML, Mermaid) to HTML with embedded SVG graphics. Supports tables, code blocks, and standard markdown formatting.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "markdown": {
                            "type": "string",
                            "description": "Path to input Markdown file to convert"
                        },
                        "output": {
                            "type": "string",
                            "description": "Optional output HTML path. If not specified, uses same name with .html extension"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Show detailed conversion progress including diagram conversion status",
                            "default": False
                        },
                        "standalone": {
                            "type": "boolean",
                            "description": "Generate standalone HTML with CSS and full page structure (default true)",
                            "default": True
                        }
                    },
                    "required": ["markdown"]
                }
            },
            "dyag_analyze_training": {
                "description": "Analyze training data coverage for applications. Compares an applications file with training data to calculate which applications are covered and coverage statistics.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "applications": {
                            "type": "string",
                            "description": "Path to applications file (JSON or Markdown format)"
                        },
                        "training": {
                            "type": "string",
                            "description": "Path to training data file (JSONL format)"
                        }
                    },
                    "required": ["applications", "training"]
                }
            },
            "dyag_rag_query": {
                "description": "Query the RAG (Retrieval Augmented Generation) system with a question. Searches relevant chunks from the indexed knowledge base and generates an answer using an LLM.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Question to ask the RAG system"
                        },
                        "n_chunks": {
                            "type": "integer",
                            "description": "Number of context chunks to retrieve (default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "collection": {
                            "type": "string",
                            "description": "ChromaDB collection name (default: applications)",
                            "default": "applications"
                        },
                        "chroma_path": {
                            "type": "string",
                            "description": "Path to ChromaDB database (default: ./chroma_db)",
                            "default": "./chroma_db"
                        }
                    },
                    "required": ["question"]
                }
            },
            "dyag_evaluate_rag": {
                "description": "Evaluate the RAG system using a dataset of question/answer pairs. Tests accuracy, performance, and generates detailed evaluation report.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset": {
                            "type": "string",
                            "description": "Path to JSONL dataset file with question/answer pairs"
                        },
                        "n_chunks": {
                            "type": "integer",
                            "description": "Number of context chunks per question (default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "max_questions": {
                            "type": "integer",
                            "description": "Max number of questions to test (default: all)",
                            "minimum": 1
                        },
                        "output": {
                            "type": "string",
                            "description": "Output JSON file for detailed results"
                        },
                        "collection": {
                            "type": "string",
                            "description": "ChromaDB collection name (default: applications)",
                            "default": "applications"
                        },
                        "chroma_path": {
                            "type": "string",
                            "description": "Path to ChromaDB database (default: ./chroma_db)",
                            "default": "./chroma_db"
                        }
                    },
                    "required": ["dataset"]
                }
            },
            "dyag_index_rag": {
                "description": "Index chunks into ChromaDB for RAG (Retrieval Augmented Generation). Creates a vector database from JSON/JSONL chunk files for semantic search.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Path to JSONL or JSON file containing chunks to index"
                        },
                        "collection": {
                            "type": "string",
                            "description": "ChromaDB collection name (default: applications)",
                            "default": "applications"
                        },
                        "chroma_path": {
                            "type": "string",
                            "description": "Path to ChromaDB database (default: ./chroma_db)",
                            "default": "./chroma_db"
                        },
                        "embedding_model": {
                            "type": "string",
                            "description": "Sentence transformer model for embeddings (default: all-MiniLM-L6-v2)",
                            "default": "all-MiniLM-L6-v2"
                        },
                        "batch_size": {
                            "type": "integer",
                            "description": "Batch size for indexing (default: 100)",
                            "default": 100,
                            "minimum": 1
                        },
                        "reset": {
                            "type": "boolean",
                            "description": "Reset collection before indexing (deletes existing data)",
                            "default": False
                        }
                    },
                    "required": ["input"]
                }
            }
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return [
            {
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            }
            for name, info in self.tools.items()
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        try:
            if name == "dyag_img2pdf":
                result_code = images_to_pdf(
                    directory=arguments["directory"],
                    output_path=arguments.get("output"),
                    verbose=arguments.get("verbose", False),
                    compress=arguments.get("compress", False),
                    quality=arguments.get("quality", 85)
                )

                if result_code == 0:
                    output_path = arguments.get("output")
                    if output_path is None:
                        dir_path = Path(arguments["directory"]).resolve()
                        output_path = str(dir_path / (dir_path.name + ".pdf"))

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully created PDF: {output_path}"
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Failed to create PDF"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_compresspdf":
                result_code = compress_pdf(
                    input_path=arguments["input"],
                    output_path=arguments.get("output"),
                    quality=arguments.get("quality", 85),
                    verbose=arguments.get("verbose", False)
                )

                if result_code == 0:
                    output_path = arguments.get("output")
                    if output_path is None:
                        pdf_path = Path(arguments["input"]).resolve()
                        output_path = str(pdf_path.parent / f"{pdf_path.stem}_compressed{pdf_path.suffix}")

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully compressed PDF: {output_path}"
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Failed to compress PDF"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_md2html":
                result_code = process_markdown_to_html(
                    markdown_path=arguments["markdown"],
                    output_path=arguments.get("output"),
                    verbose=arguments.get("verbose", False),
                    standalone=arguments.get("standalone", True)
                )

                if result_code == 0:
                    output_path = arguments.get("output")
                    if output_path is None:
                        md_path = Path(arguments["markdown"]).resolve()
                        output_path = str(md_path.parent / (md_path.stem + ".html"))

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Successfully converted Markdown to HTML: {output_path}\nDiagrams (Graphviz, PlantUML, Mermaid) have been converted to embedded SVG graphics."
                            }
                        ]
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "Failed to convert Markdown to HTML"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_analyze_training":
                # Capture stdout to return as MCP response
                import io
                from contextlib import redirect_stdout, redirect_stderr

                stdout_buffer = io.StringIO()
                stderr_buffer = io.StringIO()

                with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                    result_code = analyze_training_coverage(
                        app_file=arguments["applications"],
                        training_file=arguments["training"]
                    )

                output = stdout_buffer.getvalue()
                errors = stderr_buffer.getvalue()

                if result_code == 0:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Training coverage analysis completed successfully.\n\n{output}"
                            }
                        ]
                    }
                else:
                    error_text = errors if errors else "Failed to analyze training coverage"
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analysis failed:\n{error_text}\n\nOutput:\n{output}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_rag_query":
                try:
                    # Initialize RAG system
                    rag = RAGQuerySystem(
                        chroma_path=arguments.get("chroma_path", "./chroma_db"),
                        collection_name=arguments.get("collection", "applications")
                    )

                    # Query RAG
                    result = rag.ask(
                        question=arguments["question"],
                        n_chunks=arguments.get("n_chunks", 5)
                    )

                    # Format response
                    response_text = f"**Question:** {arguments['question']}\n\n"
                    response_text += f"**Réponse:**\n{result['answer']}\n\n"
                    response_text += f"**Sources:** {len(result['sources'])} chunks\n"
                    response_text += f"**Tokens:** {result.get('tokens_used', 0)}\n"
                    response_text += f"**Chunk IDs:** {', '.join(result['sources'][:5])}"
                    if len(result['sources']) > 5:
                        response_text += f"... (+{len(result['sources'])-5} more)"

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error querying RAG: {str(e)}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_evaluate_rag":
                try:
                    # Load dataset
                    questions = load_dataset(arguments["dataset"])
                    if not questions:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "No questions found in dataset"
                                }
                            ],
                            "isError": True
                        }

                    # Initialize RAG
                    rag = RAGQuerySystem(
                        chroma_path=arguments.get("chroma_path", "./chroma_db"),
                        collection_name=arguments.get("collection", "applications")
                    )

                    # Evaluate
                    stats = evaluate_rag(
                        rag=rag,
                        questions=questions,
                        n_chunks=arguments.get("n_chunks", 5),
                        max_questions=arguments.get("max_questions"),
                        output_file=arguments.get("output")
                    )

                    # Format response
                    response_text = "**RAG Evaluation Results**\n\n"
                    response_text += f"Questions tested: {stats['total']}\n"
                    response_text += f"✓ Success: {stats['successful']} ({stats['successful']/stats['total']*100:.1f}%)\n"
                    response_text += f"✗ Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)\n\n"

                    if stats['successful'] > 0:
                        avg_time = stats['total_time'] / stats['successful']
                        avg_tokens = stats['total_tokens'] / stats['successful']
                        response_text += f"**Performance:**\n"
                        response_text += f"Avg time: {avg_time:.1f}s\n"
                        response_text += f"Avg tokens: {avg_tokens:.0f}\n\n"

                    response_text += f"Total time: {stats['total_time']:.1f}s ({stats['total_time']/60:.1f} min)\n"
                    response_text += f"Total tokens: {stats['total_tokens']}\n"

                    if arguments.get("output"):
                        response_text += f"\n✓ Detailed results saved to: {arguments['output']}"

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error evaluating RAG: {str(e)}"
                            }
                        ],
                        "isError": True
                    }

            elif name == "dyag_index_rag":
                try:
                    # Verify input file exists
                    input_path = Path(arguments["input"])
                    if not input_path.exists():
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Input file not found: {arguments['input']}"
                                }
                            ],
                            "isError": True
                        }

                    # Create indexer
                    indexer = ChunkIndexer(
                        chroma_path=arguments.get("chroma_path", "./chroma_db"),
                        collection_name=arguments.get("collection", "applications"),
                        embedding_model=arguments.get("embedding_model", "all-MiniLM-L6-v2"),
                        reset_collection=arguments.get("reset", False)
                    )

                    # Load chunks
                    if input_path.suffix == '.jsonl':
                        chunks = indexer.load_chunks_from_jsonl(input_path)
                    elif input_path.suffix == '.json':
                        chunks = indexer.load_chunks_from_json(input_path)
                    else:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Unsupported file format: {input_path.suffix}. Use .jsonl or .json"
                                }
                            ],
                            "isError": True
                        }

                    if not chunks:
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": "No chunks found in file"
                                }
                            ],
                            "isError": True
                        }

                    # Index chunks
                    stats = indexer.index_chunks(
                        chunks,
                        batch_size=arguments.get("batch_size", 100),
                        show_progress=False  # Disable progress bar for MCP
                    )

                    # Get collection stats
                    collection_stats = indexer.get_stats()

                    # Format response
                    response_text = "**RAG Indexing Complete**\n\n"
                    response_text += f"File: {input_path.name}\n"
                    response_text += f"Collection: {arguments.get('collection', 'applications')}\n"
                    response_text += f"Embedding model: {arguments.get('embedding_model', 'all-MiniLM-L6-v2')}\n\n"
                    response_text += f"**Results:**\n"
                    response_text += f"✓ Indexed: {stats['indexed']} chunks\n"
                    response_text += f"✗ Errors: {stats['errors']}\n"
                    response_text += f"Success rate: {stats['success_rate']:.1f}%\n\n"
                    response_text += f"Total chunks in collection: {collection_stats['total_chunks']}"

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": response_text
                            }
                        ]
                    }
                except Exception as e:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error indexing RAG: {str(e)}"
                            }
                        ],
                        "isError": True
                    }

            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {name}"
                        }
                    ],
                    "isError": True
                }

        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return {
                "tools": self.list_tools()
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return self.call_tool(tool_name, arguments)
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

    def run(self):
        """Run the MCP server in stdio mode."""
        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point for MCP server."""
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()
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
