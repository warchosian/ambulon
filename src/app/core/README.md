# app.core

Utilitaires transverses utilisés par tous les autres modules.

## Modules

| Fichier | Rôle |
| --- | --- |
| `config_loader.py`   | Localisation + chargement de fichiers YAML avec substitution de variables d'environnement (`${VAR}` ou `${VAR:-default}`), fallback sur `.example`. Point d'entrée : `load_config(name, default_config=...)`. |
| `config_manager.py`  | `ConfigManager` avec tracking de la source de chaque valeur (pour `ambulon --config-source`). Fondation d'une unification future des multiples chargeurs par module (P1-6 dans `doc/amendements.md`). |
| `config_tracker.py`  | `ConfigTracker` / `is_sensitive_key()` — warn si un secret est chargé depuis un YAML au lieu d'une env var. |
| `logging_config.py`  | `setup_logging(level, log_to_file=True)` — configure les loggers (console + `logs/ambulon.log`). Respecte `AMBULON_NO_FILE_LOGS`. |
| `output_paths.py`    | Résolution des chemins de sortie relatifs à `AMBULON_HOME`. |
| `pathglob.py`        | `resolve_path_patterns()` — glob récursif avec support des `.gitignore`. |
| `timeout_parser.py`  | `parse_timeout(value)` — accepte `30`, `"30s"`, `"2m"`, `"1h"`. |

## Hiérarchie de recherche des configs

`config_loader.find_config_file("<name>")` cherche `<name>.yaml` dans l'ordre :

1. `$AMBULON_HOME/config/<name>.yaml`
2. `./config/<name>.yaml` (répertoire courant)
3. `$AMBULON_CONFIG_DIR/<name>.yaml` (si défini)
4. Même liste avec suffixe `.yaml.example` (fallback lecture seule)

## Substitution d'environnement

Dans un YAML, on peut écrire :

```yaml
token: "${GITLAB_PRIVATE_TOKEN}"
url:   "${GITLAB_URL:-https://gitlab.com}"
```

`load_config()` remplace ces patterns juste avant le `yaml.safe_load`.

## Variables d'environnement transverses

| Variable | Rôle |
| --- | --- |
| `AMBULON_HOME`        | Racine de la hiérarchie de configuration |
| `AMBULON_CONFIG_DIR`  | Dossier `config/` alternatif |
| `AMBULON_NO_FILE_LOGS`| `1` pour désactiver `logs/ambulon.log` |

## Dette technique

- **P1-6** : plusieurs modules (`piag`, `github`, `gitlab`, `zip`, `vscode`,
  `wikisi`, `llm`) ré-implémentent leur propre `load_X_config` + `_deep_merge`
  + `_substitute_env_vars`. L'objectif est de faire converger tout le monde vers
  `config_manager.ConfigManager` qui fournit déjà cette logique avec tracking.
