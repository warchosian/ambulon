# app.cli

Point d'entrée CLI d'Ambulon (`ambulon ...`).

## Architecture

- **`cli.py`** : fonction `main()`, aide globale (`show_help`), commandes « spéciales »
  (`--version`, `config`, `test`, `init`) et commandes au parsing inline (`html2md`,
  `md2html`, `html2pdf`, `json2jsonl`, `json2md`, `add-toc`, `add-itoc`,
  `wikisi-flatten`, `augment`, `md2interactive`).
- **`registry.py`** : table `STANDARD_COMMANDS: dict[str, (module_path, func_name)]`.
  Chaque entrée décrit une commande dont le handler est un
  `def main(argv: list[str] | None = None) -> int` standard. **Ajouter une commande
  = ajouter une ligne** ici.
- **`dispatch.py`** : `dispatch_standard(command) -> int | None`. Fait le lookup dans
  le registry, importe paresseusement le module cible, réécrit `sys.argv` pour
  masquer le nom de la commande au handler, puis appelle `main()`.
- **`commands/init.py`** : `ambulon init <module>` (écrit les fichiers
  `config/*.yaml` à partir des templates embarqués).

## Flux d'exécution

```
ambulon <cmd> <args>
        │
        ▼
   cli.main()
        │
        ├── cmd in {-h, --help}        → show_help()
        ├── cmd == "--version"         → print version + config dir
        ├── dispatch_standard(cmd)     → 42 commandes standard (registry)
        ├── cmd.startswith("piag-")    → handle_rag_module()
        ├── cmd == "html2md" ...       → parsing inline
        └── sinon                       → "Module inconnu"
```

## Ajouter une commande

### Commande standard (`main(argv=None) -> int`)

1. Créer `src/app/<module>/commands/<cmd>.py` avec un `def main(argv=None) -> int`.
2. Ajouter une ligne dans `registry.STANDARD_COMMANDS` :
   ```python
   "my-command": ("app.mymodule.commands.my_command", "main"),
   ```
3. Optionnel : mettre à jour `show_help()` pour documenter la commande.

Aucune modification de `cli.py::main()` n'est nécessaire.

### Commande avec parsing inline

Uniquement si le handler a une signature non standard (ex. `fn(input, output, verbose)`
directement). Ajouter la branche `elif command == "..."` dans `cli.py::main()`.

## Variables d'environnement

| Nom | Rôle |
| --- | --- |
| `AMBULON_HOME` | Racine de la hiérarchie de configuration (remplace `cwd`) |
| `AMBULON_CONFIG_DIR` | Dossier où chercher les `*.yaml` de configuration |
| `AMBULON_NO_FILE_LOGS` | Désactive l'écriture des logs dans `logs/` |
