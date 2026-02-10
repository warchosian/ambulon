# 🚀 Serveur MCP Ambulon - Démarrage Rapide

## ✅ Ce qui a été fait

### 1. **Réparation du projet après GEMINI** ✓
- ✅ 6 fichiers avec erreurs de syntaxe corrigés
- ✅ 97 fichiers Python validés (0 erreur)
- ✅ Architecture GEMINI préservée (commands/ + core/)
- ✅ Imports en cours de correction

### 2. **Documentation MCP créée** ✓
- ✅ `mcp-server-for-gemini.md` - Guide complet
- ✅ `exemple_gemini_mcp.py` - Exemples d'utilisation
- ✅ `README-MCP.md` - Ce fichier

### 3. **22 Outils MCP disponibles** ✓

```
Scan & OCR (5):      scan_document, ocr_image, ocr_batch, scan_with_ocr, process_existing_scans
Conversion (5):      html_to_markdown, markdown_to_html, json_to_markdown, images_to_pdf, compress_pdf
WikiSI (3):          wikisi_scrape, wikisi_extract_json, wikisi_json_to_md
Processing (6):      add_toc_html, add_toc_md, merge_html, merge_md, flatten_html, flatten_md
Encoding (2):        check_encoding, fix_encoding
GitLab (1):          gitlab_clone_group
```

---

## 🎯 Démarrage Ultra-Rapide (3 commandes)

```bash
# 1. Activer l'environnement
conda activate ambulon

# 2. Installer les dépendances (si pas déjà fait)
pip install typer pyyaml requests beautifulsoup4 lxml markdown python-slugify mcp

# 3. Lancer le serveur MCP
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
python -m app.mcp.commands.run_server
```

Le serveur écoute sur `stdio` et est prêt à recevoir des commandes MCP.

---

## 📝 Utilisation avec votre projet Gemini

### Option 1 : SDK Python MCP (Recommandé)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def use_ambulon_with_gemini():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.commands.run_server"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon",
        env={"PYTHONPATH": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon/src"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Lister les outils
            tools = await session.list_tools()
            print(f"{len(tools.tools)} outils disponibles")
            
            # Utiliser un outil
            result = await session.call_tool(
                "html_to_markdown",
                arguments={"input_file": "document.html"}
            )
            print(result.content)

asyncio.run(use_ambulon_with_gemini())
```

### Option 2 : Claude Desktop / Continue.dev

Ajoutez dans votre configuration:

```json
{
  "mcpServers": {
    "ambulon": {
      "command": "python",
      "args": ["-m", "app.mcp.commands.run_server"],
      "cwd": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon",
      "env": {
        "PYTHONPATH": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon/src"
      }
    }
  }
}
```

---

## 🧪 Tester le serveur

### Test 1 : Lister les outils disponibles

```bash
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
python exemple_gemini_mcp.py mcp
```

### Test 2 : Appel direct (sans MCP)

```bash
python exemple_gemini_mcp.py direct
```

### Test 3 : Avec un vrai fichier

```bash
# Créez un fichier HTML
echo "<h1>Test</h1><p>Contenu</p>" > test.html

# Convertissez-le en Markdown via MCP
# (Utilisez le script exemple_gemini_mcp.py)
```

---

## 📚 Documentation Complète

- **Guide complet** : `mcp-server-for-gemini.md`
- **Architecture GEMINI** : `GEMINI.md`
- **Guidelines projet** : `CLAUDE.md`
- **Exemples** : `exemple_gemini_mcp.py`

---

## 🔧 Dépannage

### Erreur : "No module named 'typer'"

```bash
conda activate ambulon
pip install typer pyyaml requests beautifulsoup4 lxml markdown python-slugify
```

### Erreur : Imports cassés

Les imports sont en cours de correction. Pour l'instant, le serveur MCP peut avoir des problèmes.

**Solution temporaire** : Utiliser les fonctions directement depuis Python (voir `exemple_gemini_mcp.py direct`)

### Serveur ne démarre pas

```bash
# Vérifier PYTHONPATH
cd G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon
export PYTHONPATH=./src  # Linux/Mac
set PYTHONPATH=./src     # Windows CMD
$env:PYTHONPATH="./src"  # Windows PowerShell

python -m app.mcp.commands.run_server
```

---

## 🎉 Prochaines Étapes

1. ✅ Les outils MCP sont documentés
2. ✅ Les exemples sont créés
3. ⏳ Correction des derniers imports en cours
4. ⏳ Test complet du serveur MCP

Une fois les imports corrigés, vous aurez **22 outils MCP** prêts pour votre projet Gemini !

---

## 💡 Cas d'usage typiques

### Workflow 1 : Numérisation de documents

```
scan_document(dpi=300) 
  → ocr_image(lang="fra") 
  → html_to_markdown() 
  → [Analyse avec Gemini]
```

### Workflow 2 : Extraction WikiSI pour RAG

```
wikisi_scrape(url=...) 
  → wikisi_extract_json(filter=...) 
  → wikisi_json_to_md() 
  → [Indexation RAG]
```

### Workflow 3 : Traitement documentation

```
merge_md(dir="./docs") 
  → add_toc_md() 
  → [Génération finale]
```

---

**Bon développement avec Gemini + Ambulon MCP ! 🚀**
