# app.llm

Intégration **LLM** pour la génération de documentation via API IA (Kimi,
ChatGPT, Claude, Ollama / LM Studio / vLLM local).

## Architecture

- **`core/providers/base.py`** : `BaseProvider` — interface abstraite
  (`generate`, `generate_stream`, `validate_connection`, `get_provider_name`).
- **`core/providers/openai_compatible.py`** : `OpenAICompatibleProvider` —
  implémentation générique pour toute API compatible OpenAI. Gère retry,
  streaming SSE, logging.
- **`core/providers/kimi.py`** : `KimiProvider` (Moonshot AI) — sous-classe
  de `OpenAICompatibleProvider`.
- **`core/providers/chatgpt.py`** : `ChatGPTProvider` — sous-classe, endpoint
  par défaut `https://api.openai.com/v1`.
- **`core/providers/claude.py`** : `ClaudeProvider` — client Anthropic natif
  (schéma d'API différent).
- **`core/providers/local.py`** : `LocalProvider` — Ollama / LM Studio / vLLM
  via le protocole OpenAI-compatible (`http://localhost:11434/v1` par défaut).
- **`core/providers/__init__.py`** : registre `PROVIDERS: dict[str, Type]`.
- **`core/config.py`** : `load_llm_config()`, `get_api_key()` — lit
  `config/llm.yaml` et résout les tokens depuis les variables d'environnement.
- **`preprocessing/`** : utilitaires de pré-traitement documentaire :
  - `document_filter.py` — filtre des fichiers volumineux/non pertinents avant LLM.
  - `document_summarizer.py` — découpe et résume de gros documents en chunks.
- **`commands/`** :
  - `llm` — génération de documentation (prompt + contexte)
  - `filter` — pré-filtrage d'un monofile `code.md`
  - `summarize` — résumé d'un gros document par chunks
  - `convert_plantuml_to_mermaid` (`plantuml2mermaid`) — conversion de diagrammes.

## Configuration

Voir `config/llm.yaml.example`. Variables d'environnement reconnues :

| Variable | Provider |
| --- | --- |
| `KIMI_API_KEY`     | Kimi |
| `OPENAI_API_KEY`   | ChatGPT |
| `ANTHROPIC_API_KEY`| Claude |
| `LOCAL_LLM_API_KEY`| Local (souvent inutile) |

## Exemples

```bash
# Génération avec prompt + contexte (Kimi par défaut)
ambulon llm --prompt prompts/system.md --context context.md -o result.md

# Forcer un provider spécifique
ambulon llm --provider claude --prompt p.md --context c.md

# Pré-traitement d'un gros code.md avant LLM
ambulon filter code.md --output code.filtered.md --max-file-size 5000
ambulon summarize code.md --output code.summarized.md --chunk-size 50000

# Conversion PlantUML -> Mermaid
ambulon plantuml2mermaid diagram.puml
```

## Provider local (Ollama)

```bash
# Démarrer Ollama
ollama serve
ollama pull qwen2.5:7b

# Configurer dans config/llm.yaml
# llm:
#   providers:
#     local:
#       enabled: true
#       base_url: "http://localhost:11434/v1"
#       model: "qwen2.5:7b"

ambulon llm --provider local --prompt p.md --context c.md
```
