# Tooling MCP-like

Boîte à outils Python pour opérations sur le système de fichiers, servant de MCP (Model Context Protocol) local.

## Outils disponibles

### rename_files.py
Renomme les fichiers en remplaçant un pattern par un autre.

```bash
python tooling-mcp-like/rename_files.py .claude/prompts "_prompt_" "prompt."
```

Options:
- `--dry-run` : Simulation sans renommage

### find_replace.py
Recherche et remplace du texte dans des fichiers.

```bash
python tooling-mcp-like/find_replace.py "_prompt_" "prompt." doc --glob "*.md"
```

Options:
- `--glob` : Pattern de fichiers (défaut: *)
- `--dry-run` : Simulation
- `--case-insensitive` : Ignorer la casse

### list_files.py
Liste les fichiers avec filtrage.

```bash
python tooling-mcp-like/list_files.py .claude/prompts --pattern "*.md"
```

Options:
- `--pattern` : Pattern de filtrage
- `--recursive` : Récursif

### copy_files.py
Copie des fichiers avec pattern.

```bash
python tooling-mcp-like/copy_files.py source/ dest/ --pattern "*.md"
```

Options:
- `--pattern` : Pattern de fichiers
- `--dry-run` : Simulation

### move_files.py
Déplace des fichiers avec pattern.

```bash
python tooling-mcp-like/move_files.py source/ dest/ --pattern "*.md"
```

Options:
- `--pattern` : Pattern de fichiers
- `--dry-run` : Simulation

### delete_files.py
Supprime des fichiers avec pattern.

```bash
python tooling-mcp-like/delete_files.py temp/ --pattern "*.tmp" --recursive
```

Options:
- `--pattern` : Pattern de fichiers
- `--recursive` : Récursif
- `--dry-run` : Simulation

## Scripts complets

### run_full_rename.py
Script complet pour renommer les prompts et mettre à jour les références.

```bash
python tooling-mcp-like/run_full_rename.py
```

## Exemples d'utilisation

### Renommer les prompts
```bash
# Vérifier ce qui sera renommé
python tooling-mcp-like/rename_files.py .claude/prompts "_prompt_" "prompt." --dry-run

# Effectuer le renommage
python tooling-mcp-like/rename_files.py .claude/prompts "_prompt_" "prompt."
```

### Mettre à jour les références dans doc/
```bash
# Vérifier les modifications
python tooling-mcp-like/find_replace.py "_prompt_" "prompt." doc --glob "*.md" --dry-run

# Effectuer les modifications
python tooling-mcp-like/find_replace.py "_prompt_" "prompt." doc --glob "*.md"
```

### Tout en une commande
```bash
python tooling-mcp-like/run_full_rename.py
```
