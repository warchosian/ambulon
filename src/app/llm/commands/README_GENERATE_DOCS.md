# Module generate-docs - Génération automatique de documentation

## Vue d'ensemble

Le module `generate-docs` permet de générer automatiquement de la documentation pour toutes vos applications en utilisant des prompts prédéfinis et le contenu RAG (Retrieval-Augmented Generation) de chaque application.

## Concept

Pour chaque **prompt** dans `workplace-ambulon/piag-chat/prompts/` et chaque **application** ayant un dossier `.rag`, le module :

1. Charge le prompt (par exemple `prompt.dex.md` pour le Dossier d'Exploitation)
2. Charge le contexte RAG de l'application :
   - `<app-name>.code.filtered.md` (code filtré et allégé)
   - `<app-name>.code.summarized.md` (résumé généré par LLM)
3. Envoie le tout à un LLM (Kimi, Claude, ChatGPT, ou local)
4. Sauvegarde le résultat dans `workplace-ambulon/gitlab/<app-name>.<prompt-name>.md`

## Structure des fichiers

```
workplace-ambulon/
├── piag-chat/
│   └── prompts/
│       ├── prompt.dex.md          # Dossier d'Exploitation
│       ├── prompt.ccf.md          # Cahier des Charges Fonctionnel
│       ├── prompt.dat_c4model.md  # Architecture C4 Model
│       └── ...                     # 24 prompts au total
│
└── gitlab/
    ├── sireines.rag/
    │   ├── sireines.code.filtered.md    # ← Requis
    │   ├── sireines.code.summarized.md  # ← Requis
    │   └── sireines.wikisi.md
    │
    ├── sireines.dex.md              # ← Généré
    ├── sireines.ccf.md              # ← Généré
    ├── sireines.dat_c4model.md      # ← Généré
    └── ...
```

## Utilisation

### 1. Générer tous les documents (dry-run)

Afficher ce qui serait généré sans lancer la génération :

```bash
ambulon generate-docs --dry-run
```

**Sortie :**
```
📋 Generation Plan
   Prompts: 24
   Applications: 42
   Documents to generate: 48
   Provider: kimi

🔍 Dry Run - Documents that would be generated:
   - mobilehoop.ccf.md (prompt: ccf, app: mobilehoop)
   - sireines.ccf.md (prompt: ccf, app: sireines)
   - mobilehoop.dex.md (prompt: dex, app: mobilehoop)
   ...
```

### 2. Générer pour un prompt spécifique

Générer tous les documents pour le prompt "dex" :

```bash
ambulon generate-docs --prompt dex
```

Cela génère :
- `sireines.dex.md`
- `mobilehoop.dex.md`
- ... (pour toutes les apps ayant les fichiers `.code.filtered.md` et `.code.summarized.md`)

### 3. Générer pour une application spécifique

Générer tous les prompts pour l'application "sireines" :

```bash
ambulon generate-docs --app sireines
```

Cela génère :
- `sireines.dex.md`
- `sireines.ccf.md`
- `sireines.dat_c4model.md`
- ... (pour tous les 24 prompts)

### 4. Générer un document spécifique

Combiner `--prompt` et `--app` :

```bash
ambulon generate-docs --prompt dex --app sireines
```

Génère uniquement : `sireines.dex.md`

### 5. Utiliser un provider spécifique

```bash
# Utiliser Claude
ambulon generate-docs --provider claude

# Utiliser un modèle local (Ollama)
ambulon generate-docs --provider local

# Utiliser ChatGPT
ambulon generate-docs --provider chatgpt
```

### 6. Écraser les fichiers existants

Par défaut, les fichiers existants sont ignorés. Pour les régénérer :

```bash
ambulon generate-docs --force
```

### 7. Continuer en cas d'erreur

Par défaut, la génération s'arrête à la première erreur. Pour continuer :

```bash
ambulon generate-docs --skip-errors
```

## Options complètes

```
Options de filtrage:
  --prompt <name>         Générer uniquement pour ce prompt (ex: dex, ccf)
  --app <name>            Générer uniquement pour cette application

Répertoires:
  --prompts-dir <path>    Répertoire des prompts (défaut: workplace-ambulon/piag-chat/prompts)
  --gitlab-dir <path>     Répertoire GitLab (défaut: workplace-ambulon/gitlab)

Provider LLM:
  --provider <name>       Provider à utiliser: kimi|chatgpt|claude|local
  -c, --config <file>     Fichier de configuration YAML

Comportement:
  --dry-run               Afficher le plan sans générer
  --force                 Écraser les fichiers existants
  --skip-errors           Continuer en cas d'erreur

Logging:
  -v, --verbose           Mode verbeux
```

## Prérequis

### 1. Fichiers RAG requis

Pour chaque application, les fichiers suivants doivent exister dans `workplace-ambulon/gitlab/<app-name>.rag/` :

- `<app-name>.code.filtered.md`
- `<app-name>.code.summarized.md`

**Génération automatique :**

Ces fichiers sont générés automatiquement par :

```bash
# Lors du clone GitLab (avec --generate-filtered et --generate-summarized activés par défaut)
ambulon gitlab-clone

# Ou manuellement
ambulon filter workplace-ambulon/gitlab/<app>.rag/<app>.code.md -o <app>.code.filtered.md
ambulon summarize workplace-ambulon/gitlab/<app>.rag/<app>.code.md -o <app>.code.summarized.md
```

### 2. Configuration LLM

Le fichier `config/llm.yaml` doit être configuré avec au moins un provider actif :

```yaml
llm:
  default_provider: "kimi"  # ou claude, chatgpt, local

  providers:
    kimi:
      enabled: true
      api_key: "${KIMI_API_KEY:-votre-clé-ici}"
      model: "moonshot-v1-128k"

    claude:
      enabled: true
      api_key: "${ANTHROPIC_API_KEY:-votre-clé-ici}"
      model: "claude-3-haiku-20240307"
```

**Variables d'environnement :**

```bash
export KIMI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
```

## Exemples d'usage

### Exemple 1 : Générer tous les DEX

```bash
ambulon generate-docs --prompt dex
```

**Résultat :**
```
📋 Generation Plan
   Prompts: 1
   Applications: 42
   Documents to generate: 2
   Provider: kimi

======================================================================
🚀 Starting generation...

[1/2] Generating mobilehoop.dex.md... ✓
[2/2] Generating sireines.dex.md... ✓

======================================================================

✅ Generation completed!
   Success: 2
   Output directory: workplace-ambulon/gitlab
```

### Exemple 2 : Générer toute la documentation pour SIREINES

```bash
ambulon generate-docs --app sireines --skip-errors
```

Génère 24 documents :
- `sireines.ccf.md` (Cahier des Charges Fonctionnel)
- `sireines.cctp.md` (Cahier des Clauses Techniques Particulières)
- `sireines.dex.md` (Dossier d'Exploitation)
- `sireines.dat_c4model.md` (Architecture C4)
- `sireines.mvp.md` (MVP)
- ... et 19 autres

### Exemple 3 : Workflow complet pour une nouvelle application

```bash
# 1. Cloner le dépôt GitLab (génère automatiquement .filtered.md et .summarized.md)
ambulon gitlab-clone

# 2. Vérifier ce qui sera généré
ambulon generate-docs --app monapp --dry-run

# 3. Générer toute la documentation
ambulon generate-docs --app monapp --provider claude -v

# 4. Consulter les résultats
ls workplace-ambulon/gitlab/monapp.*.md
```

## Logs et métadonnées

Chaque génération produit :

1. **Le document Markdown** : `workplace-ambulon/gitlab/<app>.<prompt>.md`
2. **Les métadonnées JSON** : `workplace-ambulon/gitlab/generation_metadata.json`

Exemple de métadonnées :

```json
{
  "timestamp": "2026-04-21T20:35:58",
  "provider": "kimi",
  "model": "moonshot-v1-128k",
  "input_files": [
    "workplace-ambulon/gitlab/sireines.rag/sireines.code.filtered.md",
    "workplace-ambulon/gitlab/sireines.rag/sireines.code.summarized.md"
  ],
  "prompt_file": "workplace-ambulon/piag-chat/prompts/prompt.dex.md",
  "output_file": "workplace-ambulon/gitlab/sireines.dex.md",
  "tokens": {
    "prompt_tokens": 52847,
    "completion_tokens": 8934,
    "total_tokens": 61781
  },
  "duration_seconds": 45.32,
  "streaming": false,
  "success": true
}
```

## Dépannage

### Erreur : "No prompts found"

```bash
❌ No prompts found in workplace-ambulon/piag-chat/prompts
```

**Solution :** Vérifier que le répertoire existe et contient des fichiers `prompt.*.md`

### Erreur : "No .rag directories found"

```bash
❌ No .rag directories found in workplace-ambulon/gitlab
```

**Solution :** Cloner au moins un dépôt GitLab avec `ambulon gitlab-clone`

### Erreur : "API key not found"

```bash
❌ Configuration error: API key for provider 'kimi' not found
```

**Solutions :**
1. Définir la variable d'environnement : `export KIMI_API_KEY="sk-..."`
2. Configurer dans `config/llm.yaml`
3. Utiliser un autre provider : `--provider local`

### Erreur : "model 'xxx' not found" (provider local)

```bash
❌ 404 Client Error: model 'qwen2.5-7b' not found
```

**Solution :** Vérifier que le modèle est bien installé dans Ollama :

```bash
ollama list
ollama pull qwen3.5-7b  # ou le modèle configuré
```

## Performances

- **Génération moyenne** : 30-60 secondes par document (selon le LLM)
- **Coût tokens** (exemple Kimi) :
  - Context : ~50 000 tokens (filtered + summarized + prompt)
  - Réponse : ~5 000-15 000 tokens
  - Total : ~55 000-65 000 tokens par document

**Estimation pour 48 documents :**
- Durée : 24-48 minutes
- Tokens : ~2,6 millions de tokens
- Coût (Kimi @ $0.5/M tokens) : ~$1.30

## Intégration dans un workflow

### Pipeline CI/CD

```yaml
# .gitlab-ci.yml
generate-docs:
  stage: documentation
  script:
    - ambulon gitlab-clone --app $CI_PROJECT_NAME
    - ambulon generate-docs --app $CI_PROJECT_NAME --provider kimi
  artifacts:
    paths:
      - workplace-ambulon/gitlab/*.md
```

### Script bash de génération massive

```bash
#!/bin/bash
# generate_all_docs.sh

APPS=("sireines" "mobilehoop" "ambulon" "balise")
PROMPTS=("dex" "ccf" "dat_c4model" "mvp")

for app in "${APPS[@]}"; do
  for prompt in "${PROMPTS[@]}"; do
    echo "Generating $app.$prompt.md..."
    ambulon generate-docs --app $app --prompt $prompt --skip-errors
  done
done
```

## Voir aussi

- `ambulon llm` - Génération LLM manuelle
- `ambulon filter` - Filtrage de documents code.md
- `ambulon summarize` - Résumé de documents code.md
- `ambulon gitlab-clone` - Clone de dépôts GitLab
- `config/llm.yaml` - Configuration des providers LLM
