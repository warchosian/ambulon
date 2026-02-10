# Codex CLI - Ambulon (Operational Rules)

Short, actionable rules for Codex on this repo. These are mandatory.

---

## 1) Non negotiable rules

- No Typer. Always use argparse.
- Config priority: CLI > YAML > ENV > Defaults.
- Always log via logger (no print for normal flow).
- Any generated file must print a clickable relative path.
- No secrets in code, logs, docs, or examples.
- Tests required for any new or changed behavior. Min coverage 80%.

---

## 2) CLI pattern (mandatory)

- `main(argv=None)` returning exit code.
- `if __name__ == "__main__": sys.exit(main())`
- `--help` must document config hierarchy + env vars.

---

## 3) Config rules (mandatory)

- YAML uses `${VAR:-default}` substitution.
- Provide `config/<module>.yaml.example` (tracked).
- Ignore `config/<module>.yaml` (real secrets).
- Resolve config paths from `Path.cwd()`, not package location.

---

## 4) Logging rules

- Central logger, file in `logs/` with timestamp.
- On success with output file:
  ```
  ✓ <Operation> reussie !
  Fichier produit : <chemin/relatif/vers/fichier.ext>
  ```

---

## 5) Tests and coverage

- Use pytest.
- Cover CLI config hierarchy: CLI overrides YAML, YAML overrides ENV, ENV overrides defaults.
- Coverage target: 80% minimum (higher on critical modules).

---

## 6) Packaging and release

- Poetry only: `poetry install`, `poetry shell`, `poetry build`.
- Conventional Commits with Commitizen.
- Release flow: `cz commit` -> `cz bump --changelog` -> `poetry build`.
- Verify wheel contents and scan for secrets before push.

---

## 7) Claude hooks note

Claude hooks do not run in Codex. If needed, run equivalent scripts manually.

---

## 8) Project architecture (Ambulon)

```
src/
└── app/
    ├── cli/
    ├── piag/
    ├── ocr/
    ├── scan/
    ├── conversion/
    ├── processing/
    ├── encoding/
    ├── wikisi/
    └── gitlab/
```

Each module:

```
app/<module>/
├── commands/   # argparse CLI
├── core/       # business logic
└── __init__.py
```

Rules:
- No cross module imports between categories.
- Shared utilities go in a shared core module if needed.

---

## 9) Module configuration map

With YAML + ENV:
- PIAG: `config/piag.yaml`, `PIAG_RAG_*`
- WikiSI: `config/wikisi.yaml`, `WIKISI_*`
- GitLab: `config/gitlab.yaml`, `GITLAB_*`

CLI only (no YAML):
- conversion, processing, encoding, ocr, scan

---

## 10) Entry point and versioning

- Entry point: `src/app/cli/main.py` -> `ambulon` command.
- Version in `src/app/__init__.py`; import it, do not hardcode elsewhere.

---

## 11) Before commit checklist

- Tests green: `pytest`
- Coverage >= 80%: `pytest --cov=app --cov-report=term`
- No secrets in staged changes:
  - `git diff --staged`
  - `git diff HEAD | rg -i "token|secret|password|api_key|credential"`
- Docs/config scan for secrets:
  - `rg -i "token|secret|password|api_key|project_id" doc/ -g "*.md"`
  - `rg -i "token|secret|password|api_key" config/ -g "*.yaml" -g "*.example"`

---

## 12) Critical modules and coverage targets

- `app/piag/`: min 85%, target 95%
- `app/wikisi/`: min 80%, target 90%
- `app/gitlab/`: min 80%, target 90%
- `app/conversion/`: min 80%, target 90%
- `app/processing/`: min 75%, target 85%
- `app/encoding/`: min 90%, target 95%
- `app/ocr/`: min 70%, target 85%
- `app/scan/`: min 70%, target 85%
- `app/cli/`: min 70%, target 85%

---

## 13) Post-commit and release (step by step)

1) Commit with Commitizen:
   - `cz commit`

2) Bump version + changelog:
   - `cz bump --changelog`

3) Build artifacts:
   - `poetry build`

4) Verify wheel contents:
   - `python -m zipfile -l dist/*.whl`

5) Push commits + tags:
   - `git push --follow-tags`
