# 🚀 Installation Rapide - Serveur MCP Ambulon

## Étape 1 : Installer les dépendances

```cmd
conda activate ambulon
pip install typer pyyaml requests beautifulsoup4 lxml markdown python-slugify mcp
```

**OU** double-cliquez sur `install_deps.bat`

## Étape 2 : Vérifier l'installation

```cmd
python -c "import typer; print('OK - typer installe')"
```

## Étape 3 : Démarrer le serveur MCP

```cmd
cd G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon
set PYTHONPATH=src
python -m app.mcp.commands.run_server
```

**Si ça ne marche pas** (imports cassés), utilisez la **version standalone** :

```cmd
python mcp_server_standalone.py
```

Cette version charge uniquement les outils qui fonctionnent.

---

## 🎯 Pour votre projet Gemini

Une fois le serveur qui tourne, utilisez ce code :

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def connect_to_ambulon():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.commands.run_server"],
        cwd="G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon",
        env={"PYTHONPATH": "G:/WarchoLife/WarchoDevplace/Gitlab_Applications/ambulon/src"}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            
            # Vos appels aux outils ici
            result = await session.call_tool("html_to_markdown", {
                "input_file": "test.html"
            })
            print(result.content)

asyncio.run(connect_to_ambulon())
```

---

## 🆘 Dépannage

### Erreur : "ModuleNotFoundError: No module named 'typer'"

→ Vous n'êtes pas dans le bon environnement conda

```cmd
conda activate ambulon
pip install typer
```

### Erreur : Imports cassés dans mcp_server.py

→ Utilisez la version standalone :

```cmd
python mcp_server_standalone.py
```

### Le serveur démarre mais ne répond pas

→ Vérifiez les logs dans `logs/mcp_server_*.log`

---

## 📞 Fichiers de référence

- `README-MCP.md` - Ce guide
- `mcp-server-for-gemini.md` - Documentation complète  
- `exemple_gemini_mcp.py` - Exemples de code
- `install_deps.bat` - Installation automatique
