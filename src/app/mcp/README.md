# app.mcp

Serveur **Model Context Protocol (MCP)** qui expose les fonctionnalités d'Ambulon
aux assistants IA compatibles (Claude Desktop, Cursor, Continue.dev, Aider,
OpenRouter…).

## Architecture

- **`core/server.py`** : implémentation du serveur MCP (`run_server()`,
  `handle_list_tools()`, `handle_call_tool()`, et les ~15 handlers
  `_handle_scan_document`, `_handle_ocr_image`, `_handle_wikisi_scrape`, etc.).
- **`core/config.py`** : helpers pour générer les fichiers de configuration
  d'intégration (`create_claude_config`, `create_openrouter_config`,
  `create_aider_config`, `create_continue_config`), et tester l'installation
  (`test_mcp_server`, `get_installation_status`).
- **`commands/run_server.py`** : `main()` utilisé par `ambulon mcp` pour démarrer
  le serveur en mode stdio.
- **`mcp_server.py` / `mcp_config.py`** : shims de rétrocompatibilité qui
  ré-exportent depuis `core/`. À terme, tous les imports externes doivent
  passer par `app.mcp.core.*`.

## Démarrage

```bash
ambulon mcp          # démarre le serveur MCP sur stdio
ambulon mcp -v       # mode verbeux
```

## Intégration client

Utiliser `ambulon config` pour générer les fichiers de configuration :

```bash
ambulon config claude        # Claude Desktop
ambulon config openrouter    # OpenRouter
ambulon config aider         # Aider
ambulon config continue      # Continue.dev
```

## Outils MCP exposés

- Scan / OCR : `scan_document`, `ocr_image`, `ocr_batch`, `scan_with_ocr`,
  `process_existing_scans`
- Conversion : `images_to_pdf`, `compress_pdf`, `html_to_markdown`,
  `markdown_to_html`, `json_to_markdown`
- WikiSI : `wikisi_scrape`, `wikisi_extract`, `wikisi_to_markdown`
- Traitement : `add_toc_to_markdown`, `merge_markdown_files`,
  `flatten_markdown_directory`
- Encoding : `check_utf8_encoding`, `fix_utf8_encoding`

Consulter `core/server.py::handle_list_tools()` pour la liste exhaustive et les
schémas JSON d'arguments.
