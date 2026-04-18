# Module LLM - Génération de documents par IA

Module de génération de documents via API LLM externes (Kimi, ChatGPT, Claude).

## 📦 Architecture

```
src/app/llm/
├── core/
│   ├── config.py               # Gestion de la configuration
│   ├── manager.py              # Agrégation de documents
│   └── providers/
│       ├── base.py             # Classe abstraite BaseProvider
│       ├── kimi.py             # Provider Kimi (Moonshot AI)
│       ├── chatgpt.py          # Provider ChatGPT (à venir)
│       └── claude.py           # Provider Claude (à venir)
└── commands/
    └── llm.py                  # CLI: ambulon llm
```

## 🚀 Commande CLI

### **`ambulon llm`** - Générer des documents via LLM

Génère un document en agrégeant plusieurs fichiers .md sources avec un prompt.

```bash
# Génération simple
ambulon llm -i doc1.md -i doc2.md -p prompt.md -o response.md

# Depuis un répertoire
ambulon llm --input-dir ./docs -p prompt.md

# Avec streaming
ambulon llm -i doc.md -p prompt.md --stream

# Provider spécifique
ambulon llm -i doc.md -p prompt.md --provider chatgpt

# Modèle personnalisé
ambulon llm -i doc.md -p prompt.md --model moonshot-v1-32k
```

**Options** :
- `-i, --input FILE` : Fichier .md source (répétable)
- `--input-dir DIR` : Répertoire contenant les .md sources
- `-p, --prompt FILE` : Fichier prompt.md (requis)
- `-o, --output FILE` : Fichier de sortie (défaut: response.md)
- `--provider NAME` : Provider (kimi, chatgpt, claude)
- `--model NAME` : Modèle spécifique
- `--api-key KEY` : Clé API (override config)
- `--stream` : Activer le streaming
- `--temperature FLOAT` : Température (0.0-1.0)
- `--max-tokens INT` : Tokens max de réponse
- `-c, --config FILE` : Fichier de config (défaut: config/llm.yaml)
- `--list-providers` : Lister les providers disponibles
- `-v, --verbose` : Mode verbeux

---

## ⚙️ Configuration

### Fichier `config/llm.yaml`

```yaml
llm:
  # Provider par défaut
  default_provider: "kimi"

  # Configuration générale
  timeout: 120
  max_retries: 3
  enable_streaming: false

  # Providers
  providers:
    kimi:
      enabled: true
      base_url: "https://api.moonshot.cn/v1"
      api_key: "${KIMI_API_KEY:-}"
      model: "moonshot-v1-8k"
      temperature: 0.7
      max_tokens: 4096

    chatgpt:
      enabled: false
      base_url: "https://api.openai.com/v1"
      api_key: "${OPENAI_API_KEY:-}"
      model: "gpt-4-turbo-preview"

    claude:
      enabled: false
      base_url: "https://api.anthropic.com/v1"
      api_key: "${ANTHROPIC_API_KEY:-}"
      model: "claude-3-opus-20240229"

  # Documents
  documents:
    separator: "\n\n---\n\n"
    include_metadata: true

  # Output
  output:
    default_file: "response.md"
    save_metadata: true
```

### Variables d'Environnement

```bash
# Tokens API (RECOMMANDÉ)
export KIMI_API_KEY=sk-...
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-...
```

### Hiérarchie de Configuration

1. **Arguments CLI** (`--api-key`, `--model`, etc.) - Priorité maximale
2. **Fichier YAML** (`-c config/llm.yaml`)
3. **Variables d'environnement** (`KIMI_API_KEY`)
4. **Valeurs par défaut**

---

## 🔑 Obtenir une clé API

### Kimi (Moonshot AI)

1. Créer un compte sur [Moonshot AI Platform](https://platform.moonshot.cn/)
2. Aller dans **API Keys**
3. Créer une nouvelle clé
4. Copier la clé (format: `sk-...`)

**Définir la clé** :
```bash
# Linux / macOS
export KIMI_API_KEY=sk-your_key_here

# Windows PowerShell
$env:KIMI_API_KEY = "sk-your_key_here"

# Windows CMD
set KIMI_API_KEY=sk-your_key_here
```

### ChatGPT (OpenAI)

1. Créer un compte sur [OpenAI Platform](https://platform.openai.com/)
2. Aller dans **API Keys**
3. Créer une nouvelle clé
4. Exporter : `export OPENAI_API_KEY=sk-...`

### Claude (Anthropic)

1. Créer un compte sur [Anthropic Console](https://console.anthropic.com/)
2. Aller dans **API Keys**
3. Créer une nouvelle clé
4. Exporter : `export ANTHROPIC_API_KEY=sk-ant-...`

⚠️ **Sécurité** : Ne jamais commiter les clés API dans Git !

---

## 🎯 Workflow de Génération

### Workflow Basique

```bash
# 1. Préparer les documents sources
docs/
├── introduction.md
├── contexte.md
└── conclusion.md

# 2. Créer un prompt
echo "Génère un rapport technique structuré." > prompt.md

# 3. Générer le document
export KIMI_API_KEY=sk-...
ambulon llm --input-dir docs -p prompt.md -o rapport.md

# 4. Vérifier le résultat
cat rapport.md
cat generation_metadata.json
```

### Avec Streaming (temps réel)

```bash
ambulon llm -i context.md -p prompt.md --stream -o output.md

# Affichage en temps réel pendant la génération
```

### Multi-providers

```bash
# Version Kimi (rapide, économique)
ambulon llm -i doc.md -p prompt.md --provider kimi -o kimi_response.md

# Version ChatGPT (qualité élevée)
ambulon llm -i doc.md -p prompt.md --provider chatgpt -o gpt_response.md

# Version Claude (raisonnement avancé)
ambulon llm -i doc.md -p prompt.md --provider claude -o claude_response.md
```

---

## 📚 API Python

### Utilisation Programmatique

```python
from pathlib import Path
from app.llm.core import load_llm_config, get_provider, DocumentManager

# Charger la configuration
config = load_llm_config()

# Initialiser le provider
provider = get_provider(
    name="kimi",
    api_key="sk-your_key",
    base_url="https://api.moonshot.cn/v1",
    config=config["llm"]["providers"]["kimi"]
)

# Initialiser le manager
manager = DocumentManager(config["llm"])

# Charger les documents
input_files = [Path("doc1.md"), Path("doc2.md")]
documents = manager.load_documents(input_files)

# Charger le prompt
prompt = manager.load_prompt(Path("prompt.md"))

# Agréger le contenu
context = manager.aggregate_content(documents)

# Générer (non-streaming)
result = provider.generate(prompt=prompt, context=context)
print(result["content"])
print(f"Tokens utilisés: {result['tokens']['total_tokens']}")

# Générer (streaming)
for chunk in provider.generate_stream(prompt=prompt, context=context):
    print(chunk, end='', flush=True)

# Sauvegarder
manager.save_response(
    content=result["content"],
    output_path=Path("response.md"),
    metadata=manager.create_metadata(...)
)
```

---

## 🔧 Providers

### Provider Kimi (Moonshot AI)

**Modèles disponibles** :
- `moonshot-v1-8k` : Contexte 8K tokens (défaut)
- `moonshot-v1-32k` : Contexte 32K tokens
- `moonshot-v1-128k` : Contexte 128K tokens

**API** : Compatible OpenAI
**Endpoint** : `https://api.moonshot.cn/v1/chat/completions`
**Auth** : Bearer token

**Exemple** :
```bash
ambulon llm -i large_doc.md -p prompt.md --model moonshot-v1-128k
```

### Provider ChatGPT (OpenAI)

**Modèles** : `gpt-4-turbo-preview`, `gpt-4`, `gpt-3.5-turbo`
**Endpoint** : `https://api.openai.com/v1`

_(À implémenter)_

### Provider Claude (Anthropic)

**Modèles** : `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
**Endpoint** : `https://api.anthropic.com/v1`

_(À implémenter)_

---

## 📊 Métadonnées de Génération

Le module sauvegarde automatiquement les métadonnées dans `generation_metadata.json` :

```json
{
  "timestamp": "2026-04-17T11:30:00Z",
  "provider": "kimi",
  "model": "moonshot-v1-8k",
  "input_files": ["doc1.md", "doc2.md"],
  "prompt_file": "prompt.md",
  "output_file": "response.md",
  "tokens": {
    "prompt_tokens": 1500,
    "completion_tokens": 800,
    "total_tokens": 2300
  },
  "duration_seconds": 12.5,
  "streaming": false,
  "success": true
}
```

---

## 🐛 Dépannage

### Erreur : API key not found

```bash
# Vérifier la variable d'environnement
echo $KIMI_API_KEY

# Définir la clé
export KIMI_API_KEY=sk-your_key

# Ou passer via CLI
ambulon llm -i doc.md -p prompt.md --api-key sk-your_key
```

### Erreur : No input files specified

```bash
# Spécifier au moins un fichier
ambulon llm -i doc.md -p prompt.md

# Ou un répertoire
ambulon llm --input-dir ./docs -p prompt.md
```

### Timeout lors de la génération

```bash
# Augmenter le timeout dans config/llm.yaml
timeout: 300  # 5 minutes

# Ou réduire la taille du contexte
ambulon llm -i doc.md -p prompt.md --max-tokens 2000
```

### Streaming ne fonctionne pas

Le streaming nécessite une connexion stable. En cas de problème :

```bash
# Utiliser le mode non-streaming
ambulon llm -i doc.md -p prompt.md  # Sans --stream
```

---

## 🔒 Sécurité

### Bonnes Pratiques

✅ **À FAIRE** :
- Toujours utiliser `${KIMI_API_KEY}` dans le YAML
- Stocker les clés dans les variables d'environnement
- Ajouter `config/llm.yaml` au `.gitignore` si les clés sont dedans
- Révoquer les clés non utilisées

❌ **À NE PAS FAIRE** :
- Jamais commiter une vraie clé dans Git
- Jamais hardcoder la clé dans le code
- Jamais partager la clé publiquement

---

## 📝 Exemples Complets

### Exemple 1 : Documentation Technique

```bash
# Contexte
docs/
├── specifications.md
├── architecture.md
└── api.md

# Prompt
echo "Génère une documentation technique complète et structurée." > prompt.md

# Génération
ambulon llm --input-dir docs -p prompt.md -o technical_doc.md
```

### Exemple 2 : Résumé Multi-sources

```bash
# Sources
ambulon llm \
  -i article1.md \
  -i article2.md \
  -i article3.md \
  -p "Crée un résumé synthétique." \
  -o summary.md \
  --stream
```

### Exemple 3 : Génération Créative

```bash
# Avec température élevée pour plus de créativité
ambulon llm \
  -i context.md \
  -p story_prompt.md \
  -o story.md \
  --temperature 0.9 \
  --max-tokens 8000
```

---

## 🔗 Liens Utiles

- [Kimi AI Documentation](https://platform.moonshot.cn/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference)
- [Markdown Guide](https://www.markdownguide.org/)

---

## 📄 Licence

Ce module fait partie du projet Ambulon.
