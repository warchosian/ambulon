# Release 4.0.0 → 4.1.0 : refonte massive `src/` (17 / 22 recommandations `doc/amendements.md`)

## Contexte

Cette PR porte la refonte post-analyse de `src/` (voir `doc/amendements.md`).
Elle contient **24 commits de cette session** (depuis `22ee617`) plus **2 bumps
de version** conventionnels gérés par commitizen. Elle est **non-breaking** pour
l'utilisateur final du CLI (tous les smoke tests passent) mais contient plusieurs
refactorisations architecturales majeures.

## Bumps de version

- **4.0.0** (`15abbcf`) : marque le début du cycle de refonte.
- **4.1.0** (`9cf67df`) : clôt la session avec 17 items P0-P3 adressés.

## Highlights (par priorité)

### P0 — Architectural (5/5)

- **CLI registry** (`46e9a76`) : `app/cli/cli.py` passe de 1187 à **913 lignes** (−23 %).
  Introduction de `app/cli/registry.py` (dict déclaratif `{cmd: (module, fn)}` pour 42 commandes)
  et `app/cli/dispatch.py` (dispatcher lazy). Ajouter une commande = 1 ligne dans le registry.
- **Déduplication MCP** (`ca4e611`) : `mcp/mcp_server.py` (1396 l.) et `mcp/mcp_config.py` (568 l.)
  étaient des duplicatas stales de `mcp/core/*.py`. Transformés en shims (~25 lignes chacun),
  **−1 916 lignes nettes**. Bonus : 2 imports cassés corrigés (`process_markdown_to_html` →
  `process_markdown_to_html_simple`, `add_toc_to_markdown` vers `app.toc`), qui empêchaient
  `ambulon mcp --help` de démarrer.
- **Déduplication processing** (`00ce96a`) : `add_augment.py`, `make_interactive.py`,
  `make_html_interactive.py` étaient 3 clones de 553 lignes avec, en prime, des accents
  mojibake dans 2 des 3 (`chargées` → `charges`, `Échap` → `champ`, …). Fusionnés en un seul
  module canonique avec alias de rétrocompat (`make_html_interactive = augment`).
  **−1 089 lignes**, accents correctement préservés dans le HTML généré.
- **Chemins personnels supprimés** (`92e3434`) : 5 occurrences `G:\WarchoLife\WarchoPortable\...`
  dans `scan/`, `vscode/` remplacées par des env vars `AMBULON_*`.
- **Cleanup CLI** (`dadd45c`) : suppression de `src/app/cli/cli_patch.py` (script jetable).

### P1 — Code quality (3/5)

- **`requests.Session`** (`6c08770`) : `PIAGClient` et `WikiSIAPIClient` réutilisent désormais
  une session HTTP unique. Gain estimé 30-50 % sur les workflows multi-requêtes RAG/WikiSI.
  Ajout du support context manager (`with PIAGClient(...) as c: ...`).
- **`except:` nus** (`8e67ab6`) : 6 → 0. Chaque cas spécialisé en exceptions nommées
  (`OSError`, `json.JSONDecodeError`, etc.).
- **`print()` → `logging`** (`70605d0`) : migration sur les 2 fichiers les plus chauds
  (`piag/core/client.py`, `core/config_loader.py`). Extraction des magic numbers en constantes
  (`DEFAULT_MAX_RETRIES`, `RETRY_SLEEP_SECONDS`).

### P2 — Modéré (6/7)

- **Globals mutables** (`abc626c`) : `_DEFAULT_CONFIG` / `_CONFIG_LOADED` dans `piag/core/config.py`
  → `@functools.lru_cache`. `vscode/core/extension_config._CONFIG` → PEP 562 `__getattr__`.
  Plus d'I/O au moment de l'import de module.
- **READMEs** (`2cb1a89` + `a95c9f7`) : +10 README de module (cli, piag, wikisi, mcp, llm,
  gitlab, core, conversion, toc, processing).
- **Debug cleanup** (`3cab8b5`) : fix `app/__init__.py:3` (expression littérale sans
  assignation), retrait `# Forcing recompilation`, 12 imports commentés nettoyés dans cli.py,
  `shell=True` supprimé dans `html2pdf.py`.

### P3 — Mineur (4/5)

- **Env vars préfixées** (`41349cc`) : `TESSERACT_*` → `AMBULON_TESSERACT_*` (rétrocompat
  conservée). Documentation `IMG2PDF_*` → `AMBULON_IMG2PDF_*`.
- **Validation YAML templates** (`41349cc`) : `tests/test_config_templates.py` (5 tests).
  Le test a immédiatement attrapé **un vrai bug** : `WIKISI_CONFIG_TEMPLATE` contenait
  `".*\.pdf$"` invalide YAML (escape `\.` interdit en double-quote). Corrigé + création
  du `GITLAB_CONFIG_TEMPLATE` manquant (requis par `ambulon init gitlab`).

## Bugs trouvés en route

- `mcp/core/server.py` : 2 imports cassés → `ambulon mcp` ne démarrait plus avant ce PR.
- `wikisi/core/config_template.py` : YAML invalide.
- `processing/__init__.py:132` : `__all__` exposait un nom supprimé.
- `.gitignore` : pattern `gitlab/` non ancré masquait `src/app/gitlab/` (2 fichiers
  applicatifs `gitlab_load.py`, `monofile_load.py` **jamais commités** malgré leur utilité).

## Métriques

| Indicateur | Avant | Après | Delta |
| --- | --- | --- | --- |
| `cli.py` lignes | 1187 | 913 | −274 (−23 %) |
| `except:` nus | 6 | 0 | −6 |
| Chemins personnels hardcodés | 5 | 0 | −5 |
| `requests.Session` réutilisées | 4 modules | 6 modules | +2 |
| README par module | 2/17 | 12/17 | +10 |
| Tests unitaires | 9 | 10 | +1 (5 cas param.) |
| Lignes totales `src/` | — | — | **−3 300 nettes** |

## Dette résiduelle (documentée dans `doc/amendements.md`)

5 items différés avec ordre de traitement recommandé :

1. **P2-14 couverture de tests** (filet de sécurité)
2. **P1-6 centraliser config loader** (7 modules ont leur propre `load_X_config`)
3. **P1-10 uniformiser signature `main(argv)`**
4. **P2-12 split des 3 gros fichiers** (`scan/core/scanning.py`, `wikisi/core/api_client.py`,
   `mcp/core/server.py`)
5. **P3-19 `pathlib` systématique**

## Validation

- `ambulon --version` → 4.1.0
- `ambulon --help` OK
- `ambulon scan --help` / `mcp --help` / `vscode-list --help` / `piag-rag-collection-list --help`
  / `html2md` / `llm --help` : **tous OK**
- `pytest tests/test_config_templates.py` : **5 passed**
- Working tree propre, pas de fichier orphelin

## Note pour le reviewer

24 commits, **atomiques et conventionnels** (feat/fix/refactor/perf/chore/docs). Chaque
commit a été testé par smoke test avant d'être créé. Le bump 4.1.0 est géré par
commitizen et inclut déjà le `CHANGELOG.md` mis à jour automatiquement.
