# Analyse approfondie du code Python — `src/` du projet Ambulon

**Périmètre analysé** : 202 fichiers `.py` répartis dans 17 modules métier (`app/{module}/commands`, `app/{module}/core`), plus le point d'entrée CLI `app/cli/cli.py`.

**Verdict global** : le projet souffre principalement d'un **point d'entrée CLI monolithique**, d'une **duplication massive** (fichiers entiers dupliqués, patterns de `commands` copiés-collés), d'une **gestion d'erreurs trop laxiste** (222 `except Exception`, 6 `except:` nus), d'un **usage de `print()` au lieu de `logging`** (1705 `print()` vs 185 `logger`), et de **chemins locaux personnels hardcodés** dans le code source.

---

## 1. CRITIQUE — Problèmes architecturaux majeurs

### 1.1 Point d'entrée CLI monolithique de 1187 lignes

`src/app/cli/cli.py:1-1186` est un anti-pattern : une fonction `main()` et une cascade `if/elif` géante sur 40+ commandes (`main()` s'étend de la ligne 591 à la ligne 1182).

- `src/app/cli/cli.py:607-1179` : cascade `if/elif command == '...'`.
- Chaque branche réimplémente manuellement le parsing : `src/app/cli/cli.py:683-691`, `723-738`, `784-807`, `862-879`, `891-903`, `918-926`, `1037-1046`, `1057-1066` répètent toutes le même idiome de `while i < len(sys.argv)`.
- `show_help()` fait 147 lignes de `print()` (cli.py:38-184) — non testable, non traductible.
- La manipulation de `sys.argv` global est massivement dupliquée (`original_argv = sys.argv; sys.argv = [sys.argv[0]] + sys.argv[2:]; try/finally`) : cli.py:631-636, 640-645, 649-654, 658-663, 667-672, 931-936, 940-945, 968-974, 977-983, 1122-1128, 1131-1136, 1139-1144 — **12 occurrences** du même pattern.
- Code mort commenté : cli.py:9-34 (une dizaine d'imports commentés avec label "LAZY LOADING").
- La fonction `handle_config_command()` (cli.py:186-409) dédouble l'aide : `cli.py:186-208` et `cli.py:213-233` sont presque identiques.

**Impact** : ajout d'une commande = modification du fichier central ; aucun dispatch registry-based ; testabilité nulle.

### 1.2 Fichiers quasi-dupliqués (triple ou double)

- `src/app/processing/commands/add_augment.py` (553 lignes), `make_interactive.py` (553 lignes) et `make_html_interactive.py` (553 lignes) : **triple clone** qui n'est différent que par 1-2 commentaires. Vérifié : les entêtes et CSS sont strictement identiques. 3 × ~18 KB.
- `src/app/mcp/mcp_server.py` (1397 l., 54 KB) vs `src/app/mcp/core/server.py` (1343 l., 51 KB) : quasi-doublons, mêmes outils MCP déclarés.
- `src/app/mcp/mcp_config.py` (568 l.) vs `src/app/mcp/core/config.py` (568 l.) : idem. Seuls les hashes MD5 diffèrent faiblement.
- Les deux configurations globales `_MCP_CONFIG_DATA` (mcp_config.py:19 et mcp/core/config.py:19) ont le même schéma.

**Impact** : toute correction doit être appliquée 2 ou 3 fois. Risque majeur de divergence silencieuse.

### 1.3 Duplication de la logique "load config" dans chaque module

Le chargeur générique `src/app/core/config_loader.py:load_config` existe, mais il est réimplémenté dans :

- `src/app/piag/core/config.py:14-51` (`load_config`)
- `src/app/github/core/config.py:18-91` (`load_github_config`, avec son propre `_deep_merge` et `_substitute_env_vars` — duplication de `config_loader._replace_env_var`)
- `src/app/gitlab/releases/core/config.py` (estimé — charge GitLab de manière indépendante)
- `src/app/vscode/core/extension_config.py:26-76` (`_load_vscode_config`)
- `src/app/zip/core/config.py:load_zip_config`
- `src/app/wikisi/core/scraper.py` (`load_config` mentionnée dans l'import `wikisi_scraper.py:14`)
- `src/app/llm/core/config.py`

Chaque module a son propre `_deep_merge`, son propre `_substitute_env_vars`, son propre fallback. Le module `core/config_manager.py` (330 lignes, classe `ConfigManager` avec tracking) existe mais **n'est utilisé par presque personne** — il apparaît seulement dans `app/gitlab/commands/gitlab_clone.py` via `ConfigTracker`.

### 1.4 Pattern CLI commands incohérent entre modules

On trouve 3 conventions différentes pour la signature du main d'une commande :

| Module | Signature | Exemple |
|---|---|---|
| `piag` | `def main(argv=None)` + `sys.argv[2:]` passé | `piag_rag_collection_add.py:9` |
| `wikisi` | `def main(argv=None)` | `wikisi_scraper.py:19` |
| `toc` | `def main(argv=None)` + `def add_toc_cli` non-standard | `add_toc.py:17` |
| `vscode/github/zip` | `def main(argv=None)` + `setup_logging` + `logger` | `zip_create.py:27` |
| `conversion` | `def main(argv=None)` + `argparse` direct | `img2pdf.py:124` |
| `scan` | `def main(argv=None)` + dict `DEFAULT_CONFIG` inline | `scan.py:64` |
| `conversion/commands/html2pdf.py` | `def main()` sans argv | html2pdf.py:500 |
| `cli.py::handle_rag_module` | `main_func(args)` dynamique | cli.py:583 |

Le nommage des exports CLI est également incohérent : `add_toc_cli` vs `main`, `wikisi_extract_json_cli` (alias) vs `main`.

### 1.5 Hiérarchie répertoires `commands/core` incohérente

- `src/app/mcp/` : garde `mcp_server.py` **et** `mcp_config.py` à la racine du module, mais a aussi `mcp/core/server.py` et `mcp/core/config.py` (duplication, voir 1.2).
- `src/app/conversion/core/__init__.py:1` est un **seul commentaire** — pas de core réel, toute la logique est dans `commands/`.
- `src/app/processing/commands/` mélange **logique métier et CLI** (ex. `make_html_interactive.py` contient 550 lignes de JavaScript/CSS embarqués), là où d'autres modules extraient le métier dans `core/`.
- `src/app/toc/` a un `core/` propre (bon) mais `src/app/cli/commands/init.py` vit à un autre niveau.
- `src/app/gitlab/` a une sous-arborescence imbriquée `gitlab/releases/commands/` & `gitlab/releases/core/` qui rompt la convention plate des autres modules.

### 1.6 Dualité `app.piag.commands.X` vs `app.piag.X`

`src/app/piag/__init__.py:34-158` réexpose toutes les opérations du `PIAGClient` comme fonctions libres (`create_collection`, `list_collections`, ...), chacune crée un nouveau `PIAGClient` à chaque appel. Cela ajoute 10 wrappers redondants (ligne 42, 58, 65, 77, 83, 95, 108, 121, 131, 143, 157) : un client par appel = pas de pool de connexions HTTP, pas de réutilisation de session. Voir §6.

---

## 2. GRAVE — Qualité du code Python

### 2.1 Gestion d'erreurs excessivement large

**222 occurrences** de `except Exception` détectées, dont beaucoup masquent des erreurs. 6 `except:` **nus** (anti-pattern PEP 8 E722) :

- `src/app/processing/core/project_to_md_converter.py:117`
- `src/app/piag/commands/piag_rag_then_chat.py:419`
- `src/app/piag/core/client.py:66` (dans `_log_response` — avale **toute** erreur de logging)
- `src/app/processing/commands/code2md.py:111`
- `src/app/mcp/mcp_server.py:986`
- `src/app/mcp/core/server.py:987`

Exemples d'`except Exception` trop larges qui devraient être spécifiques :
- `src/app/core/config_loader.py:186-189` : avale silencieusement toute erreur YAML avec `pass`.
- `src/app/core/config_loader.py:158, 171` : `except Exception: pass` avec commentaire "en cas d'erreur on stick avec les defaults" — tue les erreurs utiles (erreur de parsing, permission denied, etc.).
- `src/app/conversion/commands/html2pdf.py:68-69, 102-103` : `except Exception: pass / return None` sans logger.
- `src/app/diagrams/core/converters.py:48, 92, 104` : plusieurs `except Exception:` sans logger ni re-raise.
- `src/app/piag/core/config.py:68` : `except (FileNotFoundError, KeyError, yaml.YAMLError)` — correcte, bon contre-exemple.

### 2.2 Usage massif de `print()` vs `logging`

**1705 appels à `print()` vs 185 imports/instanciations de `logger`**. Le logger est configuré dans `core/logging_config.py:setup_logging`, mais la plupart des commandes utilisent `print(file=sys.stderr)` :

- `src/app/piag/commands/piag_rag_collection_add.py:41, 43, 72, 82, 92, 104, 121, 123, 127` — 9 `print` dont 5 `print(..., file=sys.stderr)` au lieu de `logger.error/info`.
- `src/app/piag/core/client.py:55, 57, 59, 65, 67, 103, 126, 128, 134, 136, 140` : `print("[DEBUG] ...")` alors qu'un `logger.debug()` serait adapté.
- `src/app/core/config_loader.py:87, 102, 127, 165, 172, 187` : `print("[CONFIG] ...", file=sys.stderr)` au lieu de `logger.info`.

Le commentaire en ligne 163 l'avoue : *"Message visible même sans logging activé pour aider au débogage"* — c'est le symptôme d'un `logging` mal configuré.

### 2.3 Type hints absents ou inconsistants

- `src/app/cli/cli.py` entier : **aucun type hint** sur les 3 fonctions principales (`show_help`, `handle_config_command`, `handle_test_command`, `main`).
- `src/app/mcp/mcp_server.py:73` : `def setup_logging():` pas de type de retour, aucun typing dans le fichier.
- `src/app/piag/core/client.py:402-411` : `def search(self, collection_id: str = None, collections: list = None, query: str = None, ...)` — `Optional` manquant, `list` non paramétré.
- `src/app/core/timeout_parser.py:15` : `def parse_timeout(value) -> int:` — `value` non typé.
- `src/app/vscode/core/extension_manager.py:14, 62, 94, 120` : usage correct de `Set[str]`, `Tuple[bool, str]` — bon contre-exemple.

### 2.4 Variables globales / état mutable

- `src/app/piag/core/config.py:55-56` : `_DEFAULT_CONFIG = None`, `_CONFIG_LOADED = False` + `global` (ligne 62) — état caché entre appels.
- `src/app/vscode/core/extension_config.py:80` : `_CONFIG = _load_vscode_config()` **au moment de l'import** — I/O au chargement de module, crée des side-effects à l'import.
- `src/app/mcp/mcp_config.py:19` (et `mcp/core/config.py:19`) : `_MCP_CONFIG_DATA` = gigantesque dict littéral de 400+ lignes mutable au niveau module.
- `src/app/mcp/mcp_server.py:90` : `server = Server("ambulon")` — instance globale.

### 2.5 Fonctions trop longues

- `src/app/cli/cli.py::main()` : 592 lignes (591-1182).
- `src/app/cli/cli.py::show_help()` : 147 lignes (38-184).
- `src/app/cli/cli.py::handle_config_command()` : 223 lignes (186-409).
- `src/app/mcp/mcp_server.py::handle_list_tools()` : s'étend sur plusieurs centaines de lignes (toutes les Tool déclarées inline).
- `src/app/scan/core/scanning.py` : 1302 lignes, la majorité dans une fonction géante de génération de commande NAPS2.
- `src/app/wikisi/core/api_client.py` : 1821 lignes dans un seul fichier avec plusieurs responsabilités (HTTP client + transformation + fichier I/O).

### 2.6 Magic numbers / strings hardcodés

- `src/app/conversion/commands/html2pdf.py:150` : `"3000"` (javascript-delay en ms) — magic number.
- `src/app/conversion/commands/html2pdf.py:237, 246, 264` : `page.wait_for_timeout(3000)`, `1000`, `500` — pas de constantes.
- `src/app/piag/core/client.py:49` : `self.max_retries = ... .get(..., 3)` — la valeur par défaut `3` est aussi dans `piag/core/config_template.py:39`, `conversion/commands/html2pdf.py`, `wikisi/config_template.py:76`.
- `src/app/piag/core/client.py:129` : `time.sleep(2)` — `2` hardcodé.
- `src/app/piag/core/config.py:120` : `timeout=30` par défaut différent du YAML (`120`) — incohérence.
- `src/app/piag/core/client.py:234-240` : heuristique "10 <= len <= 20 et isalnum" pour détecter un ID vs un nom — devrait être extrait/documenté.
- `src/app/core/config_loader.py:24` : `logger = logging.getLogger(__name__)` mais pas de `DEFAULT_CONFIG_NAME` constant.

---

## 3. GRAVE — Sécurité & credentials

### 3.1 Chemins personnels hardcodés dans le code source

Fuite du chemin local du développeur :

- `src/app/vscode/core/detector.py:220` : `r"G:\WarchoLife\WarchoPortable\PortableCommon\VSCodium\vscodium-1.109.41146\bin\codium.cmd"`.
- `src/app/scan/core/scanning.py:347` : `r'G:\WarchoLife\WarchoPortable\PortableCommon\Naps2\NAPS2.Console.exe'`.
- `src/app/scan/core/scanning.py:922` : `r'G:\WarchoLife\WarchoPortable\PortableCommon\Naps2\NAPS2.exe'`.
- `src/app/scan/commands/scan.py:54` : idem NAPS2 Console.
- `src/app/scan/commands/scan.py:55` : idem NAPS2 GUI.

Ces chemins ne fonctionnent que sur la machine de l'auteur. Même avec `os.getenv` en fallback, avoir ces chemins dans un repo public/partagé divulgue l'arborescence locale.

### 3.2 Subprocess — risques limités mais présents

- `src/app/conversion/commands/html2pdf.py:163-171` : **`shell=True` conditionnel sur Windows**. Le commentaire dit "better compatibility with paths" mais avec `check=True`, si un path contient des caractères shell (`&`, `|`, `$(`), c'est potentiellement injectable. Les paths viennent d'argparse donc relativement contrôlés, mais c'est inutile et risqué.
- Les autres subprocess utilisent correctement `shell=False` + liste d'arguments (ex. `src/app/vscode/core/extension_manager.py:29-35`).

### 3.3 Tokens/secrets — gestion

- `src/app/piag/core/config_template.py:101` : bonne pratique documentée (`# token: "VOTRE_TOKEN_ICI"` commenté + recommandation env var).
- `src/app/piag/commands/piag_rag_collection_add.py:98-99` : commentaire "YAML (priorité 2) - NON RECOMMANDÉ" — OK mais la lecture reste implémentée.
- `src/app/core/config_tracker.py:186-193` : le tracker émet un warning si un secret vient du YAML. Bien.
- `src/app/piag/__init__.py:12` : `client = PIAGClient(api_token="your_token")` dans un docstring — pas sensible mais pourrait être mis en `<your_token>` pour éviter confusion.
- Aucun secret réel détecté dans le code (grep sur pattern typique token négatif).

### 3.4 Pas de validation des inputs utilisateur

- `src/app/piag/commands/piag_rag_collection_add.py:115-119` : `name` et `description` passés sans sanitization ni validation de longueur.
- `src/app/wikisi/core/scraper.py` : URL de base est validée seulement contre `"https://wikisi.example.gouv.fr"` (wikisi_scraper.py:77) — pas de validation schéma.
- `src/app/zip/commands/zip_create.py:181-186` : le chemin du password file vient de CLI sans vérification anti traversal (mineur, puisque l'user a déjà accès à son FS).

---

## 4. MODÉRÉ — Performance & I/O

### 4.1 Requêtes HTTP non mutualisées (pas de Session)

Seulement 4 fichiers utilisent `requests.Session()` :
- `src/app/llm/core/providers/openai_compatible.py:33`
- `src/app/llm/core/providers/claude.py:36`
- `src/app/github/core/client.py:40`
- `src/app/wikisi/core/scraper.py:77`

Mais **pas** `src/app/piag/core/client.py` qui fait pourtant **toutes les requêtes PIAG** : `requests.request(method, url, ...)` à la ligne 105, sans session. Sur des dizaines de requêtes RAG, c'est un handshake TLS refait à chaque appel.

De même `src/app/wikisi/core/api_client.py:80, 86` : `requests.get(URL, headers=self.headers)` sans session dans une boucle (`for enumeration_nom in enumeration_noms:` ligne 84) — **N requêtes HTTP séquentielles sans pool**.

### 4.2 I/O synchrone partout où async serait bénéfique

- `src/app/wikisi/core/scraper.py` : scraper récursif synchrone d'un site web entier, une requête à la fois (`delay: 1.0s` configuré). Migration vers `aiohttp` / `httpx.AsyncClient` accélérerait 10-100x.
- `src/app/piag/commands/piag_rag_doc_upload.py` : upload séquentiel de documents dans une collection.
- `src/app/piag/commands/piag_rag_create.py` : même problème pour un workflow "rag_create" qui crée collection + upload tous les docs.

### 4.3 Lectures de fichiers non optimisées

- `src/app/wikisi/core/api_client.py:54-56, 69-70, 97-100` : `open + json.load + json.dump` répétés, cache inexistant entre commandes. Les énumérations sont rechargées à chaque instanciation `WikiSIAPIClient`.
- `src/app/piag/core/config.py:48-51` : lit le YAML à chaque `load_config()` sans cache (le cache existe via `_CONFIG_LOADED` mais uniquement pour `_load_default_config`, pas pour `load_config(path)` explicite).
- `src/app/vscode/core/extension_config.py:80` : YAML lu **au moment de l'import du module** — même si `vscode list` n'est pas la commande invoquée.

### 4.4 Imports coûteux non lazy partout

Le `cli.py` fait du lazy-loading **manuel** (cli.py:630, 639, 648, 657, etc.) par `from ... import ... as ...` dans chaque branche — bonne idée pour le démarrage CLI, mais incompatible avec l'approche du `conversion/__init__.py:4-19` qui importe tout en haut.

---

## 5. MODÉRÉ — Conventions et nommage

### 5.1 Nommage incohérent

- Commandes dans `cli.py` : `img2pdf`, `pdf2md`, `md2html` (sans tiret) vs `check-utf8`, `fix-utf8`, `add-toc`, `wikisi-extract-apps` (avec tirets). Les fichiers correspondants utilisent tantôt snake_case (`wikisi_extract_apps.py`) tantôt aussi (`check_utf8.py`). Cohérent mais la convention commands CLI "kebab-case" vs fichier "snake_case" n'est pas documentée.
- Exports alias : `wikisi_extract_json_cli`, `add_toc_cli` vs juste `main` pour d'autres modules — mix discret de conventions.
- `piag-rag-then-chat` utilise des tirets internes, `piag-chat-apikey-info` aussi (cli.py:558) — forme cohérente.
- `src/app/scan/core/scanning.py` fonction `scan_document` mais fichier `scanning.py` : OK.

### 5.2 pathlib vs os.path

Mix non systématique :
- `src/app/core/output_paths.py:19` utilise `os.path.relpath` alors que `Path` est déjà importé.
- `src/app/cli/cli.py:458, 468, 476, 498, 507, 512` : `os.path.exists`, `os.getcwd()` mélangé à `pathlib`.
- `src/app/core/config_loader.py` : bon usage de `pathlib` partout.
- `src/app/scan/commands/scan.py:54-55` : usage raw-string Windows + `os.getenv` sans `Path`.

### 5.3 Imports relatifs vs absolus mélangés

- `src/app/encoding/core/fixer.py:13` : `from ...core.pathglob import resolve_path_patterns` (triple-dot) — fragile.
- `src/app/toc/commands/add_toc.py:89` : `from ..core.markdown_toc_generator` (double-dot) — OK.
- `src/app/wikisi/commands/wikisi_scraper.py:14` : `from ..core.scraper import WikiSIScraper` — OK.
- `src/app/piag/commands/piag_rag_collection_add.py:6` : `from app.piag.core import PIAGClient, load_config` — absolu.

Pas de convention unique.

### 5.4 Imports commentés / code mort

- `src/app/cli/cli.py:9-34` : 12 imports commentés (voir §1.1).
- `src/app/processing/__init__.py:11-12, 131-132` : `add_toc_to_html` et `add_toc_to_markdown` marqués `TODO` et commentés. Ligne 131-132 du `__all__` conserve l'entrée commentée ; ligne 132 de processing/__init__.py référence `add_toc_to_markdown` **non commenté** alors qu'il l'est à l'import (ligne 11-12). **Bug potentiel : `__all__` expose un nom qui ne sera pas résolu**.
- `src/app/processing/commands/__init__.py:4-8` : `add_toc_to_html = None`, `add_toc_to_markdown = None` — exports volontairement None.
- `src/app/cli/cli_patch.py` : script jetable de patch (34 lignes) laissé dans `src/`. **N'a rien à faire dans le package installable**.

### 5.5 TODO / FIXME

- `src/app/piag/commands/piag_rag_create.py:443` : `# TODO: Implémenter le filtrage par exclude_pattern si nécessaire`
- `src/app/processing/commands/__init__.py:4, 22, 23` : 3 TODO sur modules manquants
- `src/app/processing/__init__.py:11, 12, 131` : 3 TODO supplémentaires

---

## 6. MODÉRÉ — Configuration

### 6.1 `config_template.py` embarqués dans le code

- `src/app/piag/core/config_template.py` (188 lignes) : template YAML stocké comme string Python.
- `src/app/wikisi/core/config_template.py` (100 lignes) : idem.
- `src/app/gitlab/core/config_template.py` : idem.

Bonne intention (template embarqué pour `ambulon init`), mais :
- La syntaxe YAML dans une docstring Python n'est pas linted/validée.
- Maintenir ces templates synchronisés avec les vrais fichiers `config/*.yaml.example` (listés dans `pyproject.toml:10-13`) est source de divergence. Il vaudrait mieux importer via `importlib.resources.files()`.

### 6.2 Multiples hiérarchies de configuration

Trois systèmes coexistent :
1. `app.core.config_loader.load_config` (générique, avec env substitution)
2. `app.core.config_manager.ConfigManager` (avec tracker, non adopté)
3. `app.{module}.core.config.load_X_config` (une par module — voir §1.3)

Cette fragmentation est la principale source de duplication.

### 6.3 Variables d'environnement non préfixées uniformément

- `AMBULON_HOME`, `AMBULON_NO_FILE_LOGS`, `AMBULON_CONFIG_DIR` (préfixe Ambulon)
- `PIAG_RAG_API_TOKEN`, `PIAG_RAG_PROJECT_ID` (préfixe module)
- `GITLAB_PRIVATE_TOKEN`, `GITLAB_USERNAME`
- `GITHUB_TOKEN`, `GITHUB_OWNER`
- `NAPS2_CONSOLE_COMMAND`, `TESSERACT_COMMAND`, `TESSERACT_TIMEOUT` (`scan/commands/scan.py:54-60`) — pas de préfixe Ambulon, collision possible avec d'autres outils.
- `IMG2PDF_COMPRESS`, `IMG2PDF_QUALITY` (img2pdf.py:131) — pas de préfixe Ambulon.

---

## 7. MINEUR — Tests

### 7.1 Couverture squelettique

Seulement **9 fichiers de tests** (`tests/test_*.py`) pour **202 fichiers source** :
- `test_cli.py`, `test_config.py`, `test_config_loader_cross_platform.py`, `test_config_manager.py`, `test_config_tracker.py`, `test_mcp.py`, `test_mcp_integration.py`, `test_ocr.py`, `test_scan.py`.

Modules **non testés** : `piag` (pourtant 18 commandes, 1 client), `wikisi`, `gitlab`, `github`, `llm`, `zip`, `toc`, `diagrams`, `conversion`, `processing`, `vscode`, `encoding`.

### 7.2 Testabilité médiocre

- `app.cli.cli.main()` accède directement à `sys.argv` (`cli.py:595, 597, 598, 608, ...`) — non testable sans monkey-patching global.
- `app.piag.core.config.load_config()` a un effet de bord global via `_DEFAULT_CONFIG` → pollue les tests.
- `app.vscode.core.extension_config._CONFIG` est chargé à l'import → impossible de tester sans mocker la lecture YAML avant l'import.
- `app.piag.core.client.PIAGClient._request` fait des `print(file=sys.stderr)` (client.py:103, 126, 134) — difficile à capturer en test sans rediriger stderr.

### 7.3 Tests d'intégration exécutés via subprocess

- `src/app/cli/cli.py:455-515` : `handle_test_command` lance `pytest` via `subprocess.run` — anti-pattern dans un code source production, dépendance à un cwd particulier (`cwd=os.getcwd()`).

---

## 8. MINEUR — Documentation et maintenabilité

### 8.1 README par module : quasi-absents

Sur 17 modules, seulement **2 README.md** :
- `src/app/encoding/README.md`
- `src/app/diagrams/README.md`

Modules sans README : `cli`, `conversion`, `core`, `github`, `gitlab`, `llm`, `mcp`, `ocr`, `piag`, `processing`, `scan`, `toc`, `vscode`, `wikisi`, `zip`.

### 8.2 Docstrings

- Bon : `src/app/core/config_loader.py`, `src/app/core/config_manager.py`, `src/app/core/config_tracker.py` — docstrings complètes avec `Args/Returns/Raises`.
- Moyen : `src/app/piag/core/client.py` — une ligne par méthode (client.py:151, 169, 182, 208).
- Manquant : `src/app/cli/cli.py` — les 592 lignes de `main()` n'ont qu'une docstring d'une ligne (cli.py:592).

### 8.3 Éléments divers

- `src/app/__init__.py` (3 lignes) : `"Ambulon v" + __version__` : **expression literal non assignée** en ligne 3 — bug silencieux, ne fait rien.
- `src/app/__install_message__.py` : existe, contenu non examiné mais nom inhabituel.
- `src/app/mcp/mcp_server.py:3` : `# Forcing recompilation` — commentaire "magique" laissé après debug.
- `src/app/cli/cli_patch.py` : script jetable (voir §5.4).

---

## Synthèse quantitative

| Indicateur | Valeur |
|---|---|
| Fichiers `.py` dans `src/` | 202 |
| Lignes cli.py (point d'entrée monolithique) | 1 187 |
| Fichiers > 1 000 lignes | 7 |
| Fichiers triples-dupliqués | 3 (processing) + 2 doublés (mcp) |
| `except Exception` | 222 |
| `except:` nus | 6 |
| Appels `print()` | 1 705 |
| Usages de `logger` | 185 |
| `subprocess.run` / `Popen` | 27 |
| `shell=True` | 1 (html2pdf.py) |
| README par module | 2 / 17 |
| Fichiers de test | 9 / 202 |
| Chemins personnels hardcodés | 5 occurrences `G:\WarchoLife\...` |
| TODO / FIXME | 7 |
| Imports commentés dans cli.py | 12 |

---

## Recommandations priorisées

### P0 — À faire en priorité absolue (dette bloquante)

1. **Découper `app/cli/cli.py`** : remplacer la cascade `if/elif` par un **registry pattern** (dict `{command_name: (module_path, function_name)}` comme déjà présent partiellement en `handle_rag_module`, cli.py:540-563) ou un `argparse` avec sous-parsers. Objectif : un fichier cli.py < 200 lignes, chaque commande auto-enregistrée via un décorateur ou via un plugin system basé sur `entry_points`.

2. **Supprimer la triple duplication** : `processing/commands/add_augment.py`, `make_interactive.py`, `make_html_interactive.py` → un seul fichier, avec constantes CSS/JS externalisées dans un `.css` / `.js` chargés via `importlib.resources`.

3. **Résoudre la dualité `mcp/mcp_server.py` ↔ `mcp/core/server.py`** (et `mcp_config.py` ↔ `core/config.py`) : supprimer les doublons, garder uniquement `mcp/core/`, faire pointer `mcp/__init__.py` vers `core`.

4. **Retirer les chemins personnels hardcodés** (`G:\WarchoLife\WarchoPortable\...`) des 5 lignes identifiées. Ne laisser que les variables d'environnement + chemins "common" (`C:\Program Files\...`).

5. **Supprimer `src/app/cli/cli_patch.py`** (script jetable, ne doit pas être dans le package installable).

### P1 — Grave, à adresser rapidement

6. **Centraliser le chargement de configuration** : imposer `app.core.config_manager.ConfigManager` à tous les modules. Supprimer les variantes `load_github_config`, `load_zip_config`, `load_config` dans `piag/core/config.py`, `extension_config._load_vscode_config`, etc. Objectif : un seul `_deep_merge` et un seul `_substitute_env_vars` dans le codebase.

7. **Migrer `print()` → `logging`** dans tout le codebase, en priorité dans `app/piag/core/client.py`, `app/core/config_loader.py`, `app/cli/cli.py`, et toutes les `commands/`. Règle : `print` réservé à la sortie utilisateur finale (résultats, JSON). Tout le reste (debug, warnings, erreurs) → `logger`.

8. **Remplacer les 6 `except:` nus** par `except Exception:` + log + re-raise si pertinent. Auditer les 222 `except Exception` : spécialiser en `except (FileNotFoundError, yaml.YAMLError)` ou équivalents.

9. **Introduire `requests.Session`** dans `app/piag/core/client.py` (ligne 105) et `app/wikisi/core/api_client.py`. Gain estimé : 30-50 % sur les workflows multi-requêtes.

10. **Uniformiser la signature des commands** : imposer `def main(argv: list[str] | None = None) -> int:` partout. Supprimer les variantes `add_toc_cli`, `wikisi_extract_json_cli` en faveur de `main`.

### P2 — Modéré, à planifier

11. **Ajouter un README.md par module** (15 manquants). Template court : rôle, commandes exposées, config associée, exemples.

12. **Extraire les 3 grands fichiers** :
    - `scan/core/scanning.py` (1302 l.) → split en `scanning_command_builder.py`, `scanning_executor.py`.
    - `wikisi/core/api_client.py` (1822 l.) → séparer `api_client.py`, `enumerations_loader.py`, `applications_store.py`.
    - `mcp/core/server.py` (1343 l.) → tools déclarés dans des modules séparés + registre.

13. **Supprimer les exports globaux mutables** : `app.piag.core.config._DEFAULT_CONFIG`, `app.vscode.core.extension_config._CONFIG`. Charger à la demande via un `@lru_cache` de fonction.

14. **Écrire des tests** pour les modules non testés, en priorité `piag/core/client.py` (API critique) et `core/config_loader.py` (logique transverse).

15. **Extraire les magic numbers** en constantes (`DEFAULT_MAX_RETRIES = 3`, `PLAYWRIGHT_SVG_RENDER_DELAY_MS = 3000`, `PLAYWRIGHT_SCROLL_DELAY_MS = 1000`).

16. **Corriger `app/__init__.py:3`** : expression littérale sans assignation (`"Ambulon v" + __version__`) — supprimer ou assigner à une variable.

17. **Enlever le `shell=True` dans `html2pdf.py:164`** : tester le passage en liste d'arguments sans shell. Si le path cause problème, normaliser via `str(Path(src).resolve())`.

### P3 — Mineur, nettoyage

18. **Nettoyer les imports commentés** dans `cli.py:9-34`, `processing/__init__.py:11-12, 131`.

19. **Adopter `pathlib` systématiquement** ou documenter quand `os.path` est acceptable. Le module `output_paths.py:19` peut passer à `Path.relative_to()`.

20. **Préfixer les variables d'environnement non-Ambulon** : `AMBULON_NAPS2_CONSOLE_COMMAND` au lieu de `NAPS2_CONSOLE_COMMAND`, idem Tesseract/IMG2PDF. Maintenir la rétrocompat via fallback.

21. **Retirer `# Forcing recompilation`** de `mcp_server.py:3` et autres commentaires de debug.

22. **Valider le YAML embarqué** (`config_template.py`) : ajouter un test unitaire qui fait `yaml.safe_load(WIKISI_CONFIG_TEMPLATE)` pour éviter la régression silencieuse.
