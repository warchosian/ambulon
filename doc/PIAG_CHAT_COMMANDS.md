# Commandes PIAG Chat

Ce document liste toutes les commandes CLI pour interagir avec l'API PIAG Chat.

## Vue d'ensemble

| Commande | Description | Endpoint API |
|----------|-------------|--------------|
| `piag-chat-apikey-info` | Infos sur le token (budget, dépenses) | `GET /apikey/info` |
| `piag-chat-basic-query` | Chat simple sans contexte | `POST /chat/completions` |
| `piag-chat-completion` | Complétion legacy (prompt/completion) | `POST /completions` |
| `piag-chat-query` | Chat avec contexte RAG | `POST /chat/completions` |

---

## `piag-chat-apikey-info`

Récupère les informations sur le token API (budget maximum, dépenses, etc.)

```bash
# Utiliser le token de la configuration
ambulon piag-chat-apikey-info

# Spécifier un token différent
ambulon piag-chat-apikey-info --chat-token sk-xxxxx

# Sortie JSON brute
ambulon piag-chat-apikey-info --json
```

---

## `piag-chat-basic-query`

Interroge l'API Chat en mode basique (conversation simple sans contexte).

```bash
# Question simple
ambulon piag-chat-basic-query --question "Quelle est la capitale de la France ?"

# Avec message système
ambulon piag-chat-basic-query --question "Bonjour" --system "Tu es un expert en histoire"

# Avec sortie fichier
ambulon piag-chat-basic-query -q "Explique la photosynthèse" -o reponse.md

# Modèle différent
ambulon piag-chat-basic-query -q "Question" --model mte-api-piag-mistral-large-latest
```

---

## `piag-chat-completion`

Utilise l'endpoint legacy `/completions` (format prompt/completion).

```bash
# Complétion simple
ambulon piag-chat-completion --prompt "Bonjour"

# Avec paramètres
ambulon piag-chat-completion --prompt "Ecris un poème" --max-tokens 100 --temperature 0.8

# Complétion de code
ambulon piag-chat-completion --prompt "def factorial(n):" --max-tokens 50
```

---

## `piag-chat-query`

Interroge l'API Chat avec un contexte RAG (chunks de documents).

```bash
# Avec des chunks locaux
ambulon piag-chat-query --question "Quelle est la procédure ?" --chunks chunks.json

# Avec récupération automatique depuis PIAG RAG
ambulon piag-chat-query --question "Résume ce document" --doc-id 12345 --collection-id 678

# Avec répertoire de chunks
ambulon piag-chat-query -q "Analyse" --chunks-dir ./rag/chunks/
```

---

## Configuration

Toutes les commandes utilisent la section `piag:` de `config/piag.yaml` :

```yaml
piag:
  chat_api_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1"
  chat_token: "sk-xxxxx"
  chat_token_env_var: "PIAG_CHAT_API_TOKEN"
  model: "mte-api-piag-mistral-medium-latest"
  timeout: 60
```

Ou la variable d'environnement :
```bash
set PIAG_CHAT_API_TOKEN=sk-xxxxx
```

---

## Hiérarchie de configuration

Pour toutes les commandes, la priorité est :

1. **Arguments CLI** (`--chat-token`, `--api-url`)
2. **Fichier YAML** (`config/piag.yaml`)
3. **Variables d'environnement** (`PIAG_CHAT_API_TOKEN`)
4. **Valeurs par défaut**
