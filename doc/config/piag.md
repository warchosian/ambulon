# Configuration PIAG

Configuration pour les commandes d'interaction avec l'API PIAG (RAG et Chat).

## 📋 Vue d'ensemble

Le module PIAG gère :
- 🤖 **Chat** : Interaction avec le modèle IA
- 📚 **RAG** : Retrieval-Augmented Generation (collections, documents, recherche)
- 🔄 **Pipeline** : Workflow complet RAG → Chat → Publication

## 🎯 Hiérarchie de configuration

```
CLI Arguments    (priorité 1 - maximale)
    ↓
YAML File        (priorité 2)
    ↓
ENV Variables    (priorité 3)
    ↓
Defaults         (priorité 4 - minimale)
```

### Exemple de résolution

```bash
# Scénario : Configurer l'URL de l'API PIAG

# Défaut
url: https://piag.e2.rie.gouv.fr

# ENV écrase le défaut
export PIAG_API_URL=https://piag-dev.e2.rie.gouv.fr

# YAML écrase ENV
# config/piag.yaml:
piag:
  api:
    url: https://piag-prod.e2.rie.gouv.fr

# CLI écrase tout
ambulon piag-chat-query --api-url https://piag-test.e2.rie.gouv.fr

# Résultat : https://piag-test.e2.rie.gouv.fr (CLI gagne)
```

## 📄 Structure du fichier YAML

### Fichier complet

```yaml
# config/piag.yaml
piag:
  api:
    # URL de l'API PIAG
    url: ${PIAG_API_URL:-https://piag.e2.rie.gouv.fr}

    # Token d'authentification (SENSIBLE)
    token: ${PIAG_API_TOKEN}

    # Timeout des requêtes (format: 10s, 5m, 1h)
    timeout: ${PIAG_TIMEOUT:-30s}

    # Nombre de retries en cas d'échec
    max_retries: ${PIAG_MAX_RETRIES:-3}

    # Délai entre retries
    retry_delay: ${PIAG_RETRY_DELAY:-1m}

  rag:
    # Nombre de chunks à récupérer
    top_k: ${PIAG_RAG_TOP_K:-10}

    # Timeout pour la recherche RAG
    search_timeout: ${PIAG_RAG_SEARCH_TIMEOUT:-10s}

  output:
    # Répertoire de sortie
    directory: ${PIAG_OUTPUT_DIR:-./piag_workplace}

    # Sous-répertoires
    chunks_dir: ${PIAG_CHUNKS_DIR:-chunks}
    responses_dir: ${PIAG_RESPONSES_DIR:-responses}

  logging:
    # Niveau de log (debug, info, warning, error)
    level: ${PIAG_LOG_LEVEL:-info}

    # Activer les logs fichier
    log_to_file: ${PIAG_LOG_TO_FILE:-true}

    # Fichier de log (si log_to_file=true)
    log_file: ${PIAG_LOG_FILE:-./piag.log}
```

### Fichier minimal

```yaml
# config/piag.yaml (minimal)
piag:
  api:
    token: ${PIAG_API_TOKEN}  # REQUIS
```

Tous les autres paramètres utiliseront les valeurs par défaut.

## 🔐 Variables d'environnement

### Variables requises

| Variable | Description | Exemple |
|----------|-------------|---------|
| `PIAG_API_TOKEN` | Token d'authentification API | `Bearer abcd1234...` |

### Variables optionnelles

| Variable | Description | Défaut | Format |
|----------|-------------|--------|--------|
| `PIAG_API_URL` | URL de l'API | `https://piag.e2.rie.gouv.fr` | URL |
| `PIAG_TIMEOUT` | Timeout requêtes | `30s` | `10s`, `5m`, `1h` |
| `PIAG_MAX_RETRIES` | Nombre de retries | `3` | Entier |
| `PIAG_RETRY_DELAY` | Délai entre retries | `1m` | `10s`, `1m`, `5m` |
| `PIAG_RAG_TOP_K` | Nombre de chunks RAG | `10` | Entier |
| `PIAG_RAG_SEARCH_TIMEOUT` | Timeout recherche RAG | `10s` | `5s`, `10s`, `30s` |
| `PIAG_OUTPUT_DIR` | Répertoire de sortie | `./piag_workplace` | Chemin |
| `PIAG_LOG_LEVEL` | Niveau de log | `info` | `debug`, `info`, `warning`, `error` |

### Définir les variables

**Linux/macOS :**
```bash
export PIAG_API_TOKEN="your_token_here"
export PIAG_API_URL="https://piag.e2.rie.gouv.fr"
export PIAG_TIMEOUT="60s"
```

**Windows (PowerShell) :**
```powershell
$env:PIAG_API_TOKEN = "your_token_here"
$env:PIAG_API_URL = "https://piag.e2.rie.gouv.fr"
$env:PIAG_TIMEOUT = "60s"
```

**Windows (CMD) :**
```cmd
set PIAG_API_TOKEN=your_token_here
set PIAG_API_URL=https://piag.e2.rie.gouv.fr
set PIAG_TIMEOUT=60s
```

## 🖥️ Arguments CLI

### Commandes supportant la configuration

| Commande | Support config | Options CLI |
|----------|----------------|-------------|
| `piag-chat-query` | ✅ | `--api-url`, `--timeout`, `--max-retries`, etc. |
| `piag-chat-completion` | ✅ | `--api-url`, `--timeout` |
| `piag-rag-create` | ✅ | `--api-url`, `--timeout` |
| `piag-rag-search` | ✅ | `--api-url`, `--timeout`, `--top-k` |
| `piag-rag-then-chat` | ✅ | Toutes les options |

### Arguments CLI communs

```bash
# URL de l'API
--api-url URL

# Token d'authentification
--api-token TOKEN

# Timeout
--timeout DURATION     # Ex: 30s, 5m, 1h

# Retries
--max-retries N
--retry-delay DURATION

# RAG
--top-k N
--search-timeout DURATION

# Output
--output-dir DIR
-o, --output FILE

# Diagnostic
-S, --show-config-sources
--check-config

# Verbosité
-v, --verbose          # Debug
-q, --quiet            # Warnings only
```

## 📊 Diagnostic de configuration

### Afficher toutes les sources

```bash
ambulon piag-chat-query -S
```

**Sortie exemple :**
```
Configuration Sources Report - piag-chat-query
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Parameter                  Value                          Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
piag.api.url              https://piag.e2.rie.gouv.fr    Default
piag.api.token            ****** (masked)                Environment
piag.api.timeout          60s                            CLI Argument
piag.api.max_retries      3                              Default
piag.rag.top_k            10                             YAML File
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Vérification rapide

```bash
ambulon piag-chat-query --check-config
```

## 🔒 Sécurité

### ✅ Bonnes pratiques

1. **Jamais de token dans le fichier YAML**
   ```yaml
   # ❌ MAUVAIS
   piag:
     api:
       token: Bearer abcd1234...

   # ✅ BON
   piag:
     api:
       token: ${PIAG_API_TOKEN}
   ```

2. **Utiliser les variables d'environnement**
   ```bash
   export PIAG_API_TOKEN="your_token"
   ```

3. **Fichier .env pour le développement local**
   ```bash
   # .env (gitignored)
   PIAG_API_TOKEN=dev_token_here
   PIAG_API_URL=https://piag-dev.e2.rie.gouv.fr
   ```

4. **Vérifier que les tokens ne sont pas dans l'historique**
   ```bash
   # ❌ MAUVAIS - token visible dans l'historique
   ambulon piag-chat-query --api-token secret123

   # ✅ BON - token depuis ENV
   export PIAG_API_TOKEN=secret123
   ambulon piag-chat-query
   ```

### Masquage automatique

Les paramètres contenant ces mots-clés sont automatiquement masqués :
- `token`
- `password`
- `secret`
- `key`
- `credential`

Dans les rapports `-S`, ils apparaissent comme : `****** (masked)`

## 🔄 Workflow pipeline complet

Le pipeline `piag-rag-then-chat` supporte la configuration hiérarchique complète.

### Configuration du pipeline

```bash
# Via fichier YAML
ambulon piag-rag-then-chat run \
  --config config/piag.yaml \
  --source applications/projet.rag \
  --prompt prompts/prompt.dat.md

# Via ENV + CLI override
export PIAG_API_TOKEN=token123
export PIAG_TIMEOUT=20m
ambulon piag-rag-then-chat run \
  --source applications/projet.rag \
  --prompt prompts/prompt.dat.md \
  --timeout-generate 30m  # Override du timeout
```

## 📝 Exemples pratiques

### Exemple 1 : Développement local

```yaml
# config/piag.dev.yaml
piag:
  api:
    url: https://piag-dev.e2.rie.gouv.fr
    token: ${PIAG_API_TOKEN}
    timeout: 10s  # Timeout court pour dev
    max_retries: 1

  logging:
    level: debug  # Logs détaillés
    log_to_file: true
```

```bash
export PIAG_API_TOKEN=dev_token
ambulon piag-chat-query --config config/piag.dev.yaml --query "test"
```

### Exemple 2 : Production

```yaml
# config/piag.prod.yaml
piag:
  api:
    url: https://piag.e2.rie.gouv.fr
    token: ${PIAG_API_TOKEN}
    timeout: 120s  # Timeout long
    max_retries: 5
    retry_delay: 2m

  logging:
    level: info
    log_to_file: true
    log_file: /var/log/ambulon/piag.log
```

```bash
export PIAG_API_TOKEN=$PROD_TOKEN
ambulon piag-chat-query --config config/piag.prod.yaml --query "production"
```

### Exemple 3 : CI/CD

```bash
# Pas de fichier YAML - tout en ENV
export PIAG_API_URL=https://piag-ci.e2.rie.gouv.fr
export PIAG_API_TOKEN=$CI_PIAG_TOKEN
export PIAG_TIMEOUT=180s
export PIAG_OUTPUT_DIR=/ci/output

ambulon piag-chat-query --query "ci test"
```

## 🐛 Résolution de problèmes

### Token non détecté

```bash
# Vérifier la variable
echo $PIAG_API_TOKEN

# Vérifier la configuration
ambulon piag-chat-query -S | grep token

# Si vide, définir
export PIAG_API_TOKEN=your_token
```

### Timeout trop court

```bash
# Vérifier le timeout actuel
ambulon piag-chat-query -S | grep timeout

# Override temporaire
ambulon piag-chat-query --timeout 10m --query "test"
```

### URL incorrecte

```bash
# Vérifier l'URL
ambulon piag-chat-query -S | grep url

# Tester la connexion
curl -I https://piag.e2.rie.gouv.fr
```

## 🔗 Voir aussi

- [Configuration générale](README.md)
- [Configuration GitLab](gitlab.md)
- [Configuration WikiSI](wikisi.md)
- [Pipeline RAG](../piag/PIAG_RAG_PIPELINE.md)
