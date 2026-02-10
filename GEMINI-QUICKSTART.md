# 🚀 Quickstart - Utiliser Ambulon MCP avec votre projet Gemini

## Étape 1 : Installer le SDK MCP

Dans votre projet Gemini, installez le SDK MCP :

```bash
pip install mcp
```

## Étape 2 : Copier le script de test

Copiez le fichier `test_list_tools_gemini.py` dans votre projet Gemini, ou créez un nouveau fichier avec ce contenu :

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def list_ambulon_tools():
    # Connexion au serveur MCP Ambulon
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_standalone.py"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Lister les outils
            tools = await session.list_tools()
            
            print(f"Outils disponibles : {len(tools.tools)}\n")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

# Exécuter
asyncio.run(list_ambulon_tools())
```

## Étape 3 : Exécuter le script

```bash
python test_list_tools_gemini.py
```

**Résultat attendu :**

```
======================================================================
CONNEXION AU SERVEUR MCP AMBULON DEPUIS GEMINI
======================================================================

[1/3] Démarrage du serveur MCP...
[2/3] Connexion établie
[3/3] Session initialisée

======================================================================
OUTILS MCP DISPONIBLES
======================================================================

Total: 3 outil(s)

1. html_to_markdown
   Description: Convertit un fichier HTML en Markdown
   Paramètres:
     - input_file: string (obligatoire)
       Chemin du fichier HTML
     - output_file: string (optionnel)
       Chemin du fichier Markdown de sortie

2. markdown_to_html
   Description: Convertit un fichier Markdown en HTML
   Paramètres:
     - input_file: string (obligatoire)
       Chemin du fichier Markdown
     - output_file: string (optionnel)
       Chemin du fichier HTML de sortie

3. scan_document
   Description: Scanner un document avec NAPS2
   Paramètres:
     - dpi: integer (obligatoire)
       Résolution en DPI
     - output_dir: string (optionnel)
       Répertoire de sortie
```

---

## Utiliser un outil depuis Gemini

Une fois que vous avez listé les outils, voici comment les utiliser :

### Exemple 1 : Convertir HTML → Markdown

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def convert_html_to_markdown():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_standalone.py"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Appeler l'outil html_to_markdown
            result = await session.call_tool(
                "html_to_markdown",
                arguments={
                    "input_file": "document.html",
                    "output_file": "document.md"
                }
            )
            
            # Afficher le résultat
            print(result.content[0].text)

asyncio.run(convert_html_to_markdown())
```

### Exemple 2 : Scanner un document

```python
async def scan_document():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_standalone.py"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Scanner à 300 DPI
            result = await session.call_tool(
                "scan_document",
                arguments={
                    "dpi": 300,
                    "output_dir": "./scans"
                }
            )
            
            print(result.content[0].text)

asyncio.run(scan_document())
```

---

## Intégration avec Gemini API

Si vous utilisez l'API Gemini de Google, vous pouvez combiner les outils MCP avec Gemini :

```python
import asyncio
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configurer Gemini
genai.configure(api_key="VOTRE_CLE_API")
model = genai.GenerativeModel('gemini-pro')

async def workflow_gemini_mcp():
    # 1. Utiliser un outil MCP pour convertir HTML en Markdown
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_standalone.py"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Convertir HTML en Markdown
            result = await session.call_tool(
                "html_to_markdown",
                arguments={"input_file": "document.html"}
            )
            
            markdown_content = result.content[0].text
            
            # 2. Analyser le contenu avec Gemini
            prompt = f"Résume ce document Markdown:\n\n{markdown_content}"
            response = model.generate_content(prompt)
            
            print("Résumé Gemini:")
            print(response.text)

asyncio.run(workflow_gemini_mcp())
```

---

## Workflows typiques

### Workflow 1 : Numérisation + Analyse

```
1. scan_document (MCP Ambulon)
   ↓
2. ocr_image (MCP Ambulon) 
   ↓
3. Analyse du texte (Gemini API)
```

### Workflow 2 : Extraction web + RAG

```
1. html_to_markdown (MCP Ambulon)
   ↓
2. Indexation RAG (Gemini)
   ↓
3. Recherche sémantique (Gemini)
```

---

## Dépannage

### Erreur : "ModuleNotFoundError: No module named 'mcp'"

```bash
pip install mcp
```

### Erreur : "FileNotFoundError: mcp_server_standalone.py"

Vérifiez que le chemin `cwd` pointe vers le bon dossier Ambulon :

```python
cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon"  # Ajustez si nécessaire
```

### Le serveur ne répond pas

Testez le serveur manuellement :

```bash
cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
python mcp_server_standalone.py
```

Si vous voyez des erreurs, installez les dépendances :

```bash
pip install typer pyyaml requests beautifulsoup4 lxml markdown
```

---

## Fichiers utiles

- `test_list_tools_gemini.py` - Script de test pour lister les outils
- `mcp-server-for-gemini.md` - Documentation complète
- `exemple_gemini_mcp.py` - Plus d'exemples de code
- `DEMARRAGE-MCP.txt` - Guide de démarrage

---

## Prochaines étapes

1. ✅ Testez `test_list_tools_gemini.py`
2. ✅ Essayez les exemples ci-dessus
3. ✅ Intégrez dans votre workflow Gemini
4. 📖 Consultez `mcp-server-for-gemini.md` pour les 22 outils complets

**Bon développement avec Gemini + Ambulon ! 🚀**
