# Plan: Integrate dyag webchat into ambulon

## Context
The repository `ambulon` currently has no `src/app/webchat` component. The DYAG project provides a functional webchat server under `dyag/src/dyag/webchat`. It starts a FastAPI server via `uvicorn` and reads LLM‑related configuration (model, provider) from environment variables, but does **not** import any concrete LLM client. Ambulon already contains a full LLM abstraction in `src/app/llm` (providers, manager, CLI commands) and a PIAG (RAG) layer in `src/app/piag`.

The goal is to copy the DYAG webchat code into `ambulon/src/app/webchat`, adapt it to use Ambulon’s LLM services (provider abstraction, token handling) and optionally to call PIAG for knowledge‑base retrieval/augmentation.

## High‑level steps
1. **Create target package** – Add directory `src/app/webchat` with an `__init__.py` that mirrors DYAG’s init (exposes version).
2. **Copy source files** – Bring over the three DYAG files shown in the exploration result:
   - `commands/__init__.py`
   - `commands/webchat_server.py`
   - (optional) any additional utilities under `webchat` (none currently).
3. **Adjust imports** – Replace any DYAG‑specific imports (`uvicorn`, `pathlib`, etc.) with the equivalent within Ambulon if needed. Add imports from `app.llm.core.manager` and `app.llm.core.providers` so the server can instantiate the LLM client based on the same environment variables used by other CLI commands.
4. **Expose LLM client to FastAPI** – Create a small helper (`app/webchat/llm_adapter.py`) that:
   - Calls `get_provider()` from `app.llm.core.providers`.
   - Returns an async `chat(messages)` function compatible with the existing FastAPI route.
   - Handles streaming if the chosen provider supports it (e.g., OpenAI, Claude). This mirrors the logic used in `app/llm/commands/llm.py`.
5. **Optional PIAG hook** – If the user wants PIAG integration, add a dependency in the request handling flow:
   - Import `PIAGClient` from `app.piag.core`.
   - Before calling the LLM, optionally run a retrieval step (`PIAGClient.search(query)`) and prepend the retrieved context to the user prompt.
   - Make this behaviour togglable via a CLI flag `--use-piag` or an env var `AMBULON_WEBCHAT_PIAG=1`.
6. **Update CLI registration** – In `src/app/cli/cli.py` (or the appropriate command registration file), add a sub‑command `webchat` that delegates to the new `run_webchat_server` function.
7. **Configuration** – Ensure the environment‑variable names used by the existing LLM system (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, etc.) are honoured by the webchat server. Add a README snippet in the new package documenting required vars.
8. **Tests** – Add integration tests under `test_webchat/` that:
   - Spin up the FastAPI app with `TestClient`.
   - Send a simple chat request and verify a non‑empty response.
   - Verify that the `--use-piag` flag adds retrieved context (mock `PIAGClient`).
9. **Documentation** – Add a short section in `doc/generate_docs.md` (or the appropriate docs file) describing how to start the webchat server: `poetry run python -m ambulon.webchat --host 0.0.0.0 --port 8000`.
10. **Cleanup** – Remove any DYAG‑specific dead code, update `setup.cfg`/`pyproject.toml` if new package needs to be included in the distribution, and run the full test suite.

## Critical files to modify
- `src/app/webchat/__init__.py` (new)
- `src/app/webchat/commands/__init__.py` (copied)
- `src/app/webchat/commands/webchat_server.py` (copied & edited)
- `src/app/webchat/llm_adapter.py` (new)
- `src/app/cli/cli.py` (add sub‑command registration)
- `src/app/llm/core/manager.py` (no change, just imported)
- `src/app/piag/core/__init__.py` (imported only if PIAG integration enabled)
- Test files under `test_webchat/` (new)
- Documentation files (updated)

## Verification plan
1. Run `poetry install` to ensure dependencies are resolved.
2. Execute `poetry run python -m ambulon.webchat --host 127.0.0.1 --port 8001` and confirm the server starts without import errors.
3. Use the test client to post a JSON payload `{"messages": [{"role": "user", "content": "Hello"}]}` and assert a `200` response containing a `assistant` message.
4. Enable PIAG (`AMBULON_WEBCHAT_PIAG=1`) and mock `PIAGClient.search` to return a known string; verify the response contains that string.
5. Run the full repository test suite (`poetry run pytest -q`) to ensure no regressions.

## Risks & mitigations
- **Import collisions** – DYAG code may reference modules with the same name as Ambulon’s. Mitigation: rename the copied package to `ambulon.webchat` and adjust relative imports.
- **Environment variable mismatch** – Ensure the webchat server reads the exact same variables as other LLM commands; otherwise the provider may be mis‑configured. Add a small wrapper that re‑uses `app.llm.core.config.get_llm_config()`.
- **PIAG optionality** – If PIAG is not installed, importing it would raise `ImportError`. Wrap the import in a try/except and disable the flag.
- **Testing FastAPI server** – Starting an actual `uvicorn` process is heavy; use `FastAPI`’s `TestClient` for unit tests.

---
*Plan file created for review. Please approve or request changes.*