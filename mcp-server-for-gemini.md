# Configuration Serveur MCP Ambulon pour Gemini

## 📋 Outils MCP Disponibles (26 outils)

### 🔍 **Scan & OCR** (5 outils)
1. `scan_document` - Scanner un document avec NAPS2 et profils DPI
2. `ocr_image` - OCR sur une image individuelle
3. `ocr_batch` - OCR en lot sur plusieurs images/PDFs
4. `scan_with_ocr` - Scanner + OCR en une opération
5. `process_existing_scans` - Traiter des scans existants

### 📑 **Conversion** (5 outils)
6. `html_to_markdown` - Convertir HTML vers Markdown
7. `markdown_to_html` - Convertir Markdown vers HTML
8. `json_to_markdown` - Convertir JSON vers Markdown
9. `images_to_pdf` - Assembler images en PDF
10. `compress_pdf` - Compresser un fichier PDF

### 🌐 **WikiSI - Parc Applicatif** (3 outils)
11. `wikisi_scrape` - Aspirer un site WikiSI complet
12. `wikisi_extract_json` - Extraire et filtrer applications du JSON
13. `wikisi_json_to_md` - Convertir données WikiSI en Markdown pour RAG

### 📝 **Processing - Traitement Documents** (6 outils)
14. `add_toc_html` - Ajouter table des matières à un HTML
15. `add_toc_md` - Ajouter table des matières à un Markdown
16. `merge_html` - Fusionner plusieurs HTML en un seul
17. `merge_md` - Fusionner plusieurs Markdown en un seul
18. `flatten_html` - Aplatir arborescence HTML
19. `flatten_md` - Aplatir arborescence Markdown

### 🔤 **Encoding - UTF-8** (2 outils)
20. `check_encoding` - Vérifier encodage de fichiers Markdown
21. `fix_encoding` - Corriger encodage UTF-8 des fichiers

### 🦊 **GitLab** (1 outil)
22. `gitlab_clone_group` - Cloner tous les projets d'un groupe GitLab

### 🤖 **RAG PIAG** (4 outils)
23. `piag_create_collection` - Créer une collection RAG
24. `piag_upload_document` - Uploader un document dans une collection
25. `piag_search` - Rechercher dans les collections RAG
26. `piag_list_collections` - Lister les collections disponibles

---

## 🚀 Démarrage du Serveur MCP

### Méthode 1 : Via Python (Direct)

```bash
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
python -m app.mcp.commands.run_server
```

### Méthode 2 : Via Poetry (Recommandé)

```bash
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
poetry shell
poetry install
ambulon mcp-server
```

Le serveur écoute sur `stdio` (entrée/sortie standard) selon le protocole MCP.

---

## 🔗 Configuration pour Gemini

### Option A : Configuration JSON pour Claude Desktop (compatible Gemini)

Créez ou modifiez `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "ambulon": {
      "command": "python",
      "args": [
        "-m",
        "app.mcp.commands.run_server"
      ],
      "cwd": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon",
      "env": {
        "PYTHONPATH": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon/src"
      }
    }
  }
}
```

### Option B : Configuration pour Gemini API (via Python SDK)

Si vous utilisez le SDK Python de Gemini avec MCP :

```python
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configuration du serveur MCP Ambulon
server_params = StdioServerParameters(
    command="python",
    args=["-m", "app.mcp.commands.run_server"],
    cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon",
    env={"PYTHONPATH": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon/src"}
)

# Connexion au serveur MCP
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # Lister les outils disponibles
        tools = await session.list_tools()
        print(f"Outils MCP disponibles : {len(tools.tools)}")

        # Utiliser un outil
        result = await session.call_tool(
            "html_to_markdown",
            arguments={"input_file": "document.html"}
        )
        print(result.content)
```

### Option C : Configuration pour Continue.dev ou Aider

**`~/.continue/config.json` :**

```json
{
  "mcpServers": [
    {
      "name": "ambulon",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["-m", "app.mcp.commands.run_server"],
        "cwd": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"
      }
    }
  ]
}
```

---

## 📦 Installation en Mode Développement

Pour que `ambulon` soit accessible globalement :

```bash
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
poetry install
```

Ensuite, activez l'environnement :

```bash
poetry shell
# Maintenant 'ambulon' fonctionne partout
ambulon --help
ambulon mcp-server
```

---

## 🔧 Variables d'Environnement (Optionnel)

Créez un fichier `.env` à la racine du projet :

```env
# Scan
NAPS2_COMMAND=G:/WarchoLife/WarchoPortable/PortableCommon/Naps2/NAPS2.Console.exe

# OCR
TESSERACT_COMMAND=tesseract
TESSERACT_ENABLED=True

# WikiSI
WIKISI_BASE_URL=https://wikisi.example.gouv.fr
WIKISI_OUTPUT_DIR=./wikisi_data

# PIAG (RAG)
PIAG_API_URL=https://piag.example.fr/api
PIAG_API_TOKEN=votre_token_ici

# GitLab
GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=votre_token_ici
```

---

## 🧪 Test Rapide

```bash
# Depuis votre projet Gemini
curl -X POST http://localhost:3000/mcp/tools/list

# Ou via Python
python << EOF
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.commands.run_server"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()

            for tool in tools.tools:
                print(f"✓ {tool.name} - {tool.description}")

asyncio.run(test())
EOF
```

---

## 📚 Documentation des Outils

Chaque outil MCP expose sa propre documentation via le protocole MCP. Pour voir les détails :

```python
# Lister les outils avec descriptions
tools = await session.list_tools()
for tool in tools.tools:
    print(f"\n{'='*60}")
    print(f"Nom: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Schéma JSON: {tool.inputSchema}")
```

---

## 🎯 Exemples d'Utilisation depuis Gemini

### Exemple 1 : Scan + OCR + Conversion Markdown

```python
# 1. Scanner un document
scan_result = await session.call_tool("scan_document", {
    "dpi": 300,
    "output_path": "facture.jpg"
})

# 2. OCR de l'image
ocr_result = await session.call_tool("ocr_image", {
    "image_path": "facture.jpg",
    "language": "fra"
})

# 3. Convertir en Markdown pour analyse RAG
# (le contenu OCR est déjà en texte, pas besoin de conversion)
```

### Exemple 2 : Aspirer WikiSI + Convertir en RAG

```python
# 1. Aspirer le site WikiSI
scrape_result = await session.call_tool("wikisi_scrape", {
    "url": "https://wikisi.example.gouv.fr",
    "output_dir": "./wikisi_data"
})

# 2. Extraire applications filtrées
extract_result = await session.call_tool("wikisi_extract_json", {
    "input_file": "./wikisi_data/applications.json",
    "filter_range": "1-100"
})

# 3. Convertir en Markdown optimisé RAG
md_result = await session.call_tool("wikisi_json_to_md", {
    "input_file": "./wikisi_data/applications_filtered.json",
    "output_file": "./wikisi_data/apps.md"
})
```

### Exemple 3 : Traitement de Documentation

```python
# 1. Fusionner plusieurs Markdown
merge_result = await session.call_tool("merge_md", {
    "input_dir": "./docs",
    "output_file": "./docs_merged.md"
})

# 2. Ajouter table des matières
toc_result = await session.call_tool("add_toc_md", {
    "input_file": "./docs_merged.md",
    "output_file": "./docs_final.md"
})
```

---

## ⚠️ Notes Importantes

1. **Chemin Python** : Assurez-vous que `PYTHONPATH` pointe vers `ambulon/src`
2. **Dépendances** : Installez avec `poetry install` avant le premier lancement
3. **Logs** : Les logs sont dans `logs/mcp_server_*.log`
4. **Sécurité** : Ne commitez JAMAIS les tokens dans `.env`

---

## 🆘 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier l'installation
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
poetry install
poetry run python -c "from app.mcp.mcp_server import main; print('Import OK')"
```

### Les outils ne sont pas listés

```bash
# Vérifier la configuration MCP
python -m app.mcp.commands.run_server --help
```

### Erreurs d'import

```bash
# Réinstaller les dépendances
poetry install --no-cache
```

---

## 📞 Support

- Documentation complète : `GEMINI.md` et `CLAUDE.md`
- Issues GitHub : https://github.com/votre-repo/ambulon/issues
- Configuration MCP : `config/mcp-config.json`
