# Configuration Ambulon

Guide complet de configuration pour les modules Ambulon.

## Vue d'ensemble

Ambulon utilise un système de configuration hiérarchique flexible qui permet de configurer chaque module via plusieurs sources. Les configurations sont situées dans le répertoire `config/` à la racine du projet.

### Fichiers de configuration disponibles

| Fichier | Module | Description |
|---------|--------|-------------|
| `config/piag.yaml` | PIAG | Configuration pour l'API PIAG (RAG, Chat) |
| `config/gitlab.yaml` | GitLab | Configuration pour le clonage de repositories GitLab |
| `config/wikisi.yaml` | WikiSI | Configuration pour la synchronisation WikiSI API |

## 🎯 Hiérarchie de configuration

**Principe fondamental** : Chaque paramètre peut être défini à plusieurs niveaux, la **priorité décroissante** étant :

```
1. CLI (Arguments en ligne de commande)    ← Priorité maximale
2. YAML (Fichier de configuration)
3. ENV (Variables d'environnement)
4. DEFAULT (Valeurs par défaut)             ← Priorité minimale
```

### Exemple de résolution

Pour le paramètre `api.url` du module PIAG :

```bash
# Si fourni via CLI : utilise la valeur CLI
ambulon piag-chat-query --api-url https://cli.example.com

# Sinon, si défini dans config/piag.yaml : utilise YAML
api:
  url: https://yaml.example.com

# Sinon, si variable ENV existe : utilise ENV
export PIAG_API_URL=https://env.example.com

# Sinon : utilise la valeur par défaut
DEFAULT: https://piag.e2.rie.gouv.fr
```

**Résultat** : La valeur CLI écrase toutes les autres.

## 📋 Diagnostic de configuration

Tous les modules supportent les options de diagnostic pour vérifier la provenance des paramètres :

### Option `-S / --show-config-sources`

Affiche un rapport détaillé de tous les paramètres avec leur source.

```bash
# Pour PIAG
ambulon piag-chat-query -S

# Pour WikiSI
ambulon wikisi-sync-api -S

# Pour GitLab
ambulon gitlab-clone -S
```

**Exemple de sortie :**

```
Configuration Sources Report - piag-chat-query
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Parameter                  Value                          Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
piag.api.url              https://cli.example.com        CLI Argument
piag.api.token            ****** (masked)                Environment
piag.api.timeout          30                             YAML File
piag.output.directory     ./output                       Default
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  • CLI Argument: 1
  • Environment: 1
  • YAML File: 1
  • Default: 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Configuration sources displayed successfully
```

### Option `--check-config`

Affiche un résumé condensé de la configuration.

```bash
ambulon piag-chat-query --check-config
```

**Exemple de sortie :**

```
Configuration Check - piag-chat-query
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Configuration hierarchy:
  1. CLI Arguments (highest priority)
  2. YAML File
  3. Environment Variables
  4. Defaults (lowest priority)

Sources distribution:
  • CLI Argument: 1 parameter(s)
  • Environment: 1 parameter(s)
  • YAML File: 1 parameter(s)
  • Default: 1 parameter(s)

Total parameters: 4

Use -S/--show-config-sources for detailed view.
```

## 🔐 Gestion des valeurs sensibles

Les paramètres sensibles (tokens, mots de passe, clés API) sont **automatiquement masqués** dans les rapports.

### Détection automatique

Les clés suivantes sont considérées comme sensibles :
- `*token*`
- `*password*`
- `*secret*`
- `*key*`
- `*credential*`

### Bonnes pratiques

✅ **Recommandé** :
```bash
# Utiliser les variables d'environnement pour les tokens
export PIAG_API_TOKEN=your_secret_token
ambulon piag-chat-query
```

⚠️ **Éviter** :
```bash
# NE PAS passer les tokens via CLI (visible dans l'historique)
ambulon piag-chat-query --api-token your_secret_token
```

❌ **À ne jamais faire** :
```yaml
# NE JAMAIS commiter les tokens dans les fichiers YAML
api:
  token: ghp_your_secret_token_here  # ❌ DANGEREUX
```

### Fichiers d'exemple

Les fichiers `.example` dans `config/` montrent la structure sans valeurs sensibles :

```
config/
├── piag.yaml.example      # Template PIAG
├── gitlab.yaml.example    # Template GitLab
└── wikisi.yaml.example    # Template WikiSI
```

**Usage** :
```bash
# Copier le template
cp config/piag.yaml.example config/piag.yaml

# Éditer et remplacer ${ENV_VAR} par les vraies valeurs
nano config/piag.yaml
```

## 🔄 Substitution de variables d'environnement

Les fichiers YAML supportent la substitution de variables d'environnement avec valeur par défaut.

### Syntaxe

```yaml
api:
  url: ${PIAG_API_URL:-https://default.example.com}
  token: ${PIAG_API_TOKEN}
  timeout: ${PIAG_TIMEOUT:-30}
```

### Comportement

- `${VAR}` : Utilise la valeur de `$VAR`, erreur si non définie
- `${VAR:-default}` : Utilise `$VAR` si définie, sinon `default`

### Exemple complet

```yaml
# config/piag.yaml
piag:
  api:
    url: ${PIAG_API_URL:-https://piag.e2.rie.gouv.fr}
    token: ${PIAG_API_TOKEN}
    timeout: ${PIAG_TIMEOUT:-30}

  output:
    directory: ${PIAG_OUTPUT_DIR:-./piag_workplace}
```

Avec les variables :
```bash
export PIAG_API_TOKEN=secret123
export PIAG_TIMEOUT=60
# PIAG_API_URL et PIAG_OUTPUT_DIR non définis → valeurs par défaut
```

Résultat :
```
url: https://piag.e2.rie.gouv.fr  (défaut car $PIAG_API_URL absent)
token: secret123                   (depuis $PIAG_API_TOKEN)
timeout: 60                        (depuis $PIAG_TIMEOUT)
directory: ./piag_workplace        (défaut car $PIAG_OUTPUT_DIR absent)
```

## 📚 Documentation par module

Pour des informations détaillées sur chaque module :

- [Configuration PIAG](piag.md) - API PIAG, RAG, Chat
- [Configuration GitLab](gitlab.md) - Clonage repositories
- [Configuration WikiSI](wikisi.md) - Synchronisation API WikiSI

## ⚙️ Configuration avancée

### Fichiers multiples

Vous pouvez avoir plusieurs fichiers de configuration :

```bash
# Environnement de développement
ambulon piag-chat-query --config config/piag.dev.yaml

# Environnement de production
ambulon piag-chat-query --config config/piag.prod.yaml
```

### Profils par environnement

```
config/
├── piag.dev.yaml       # Dev : timeouts courts, debug
├── piag.prod.yaml      # Prod : timeouts longs, pas de debug
└── piag.test.yaml      # Tests : mocks, données factices
```

### Variables d'environnement par profil

```bash
# Développement
export PIAG_API_URL=https://piag-dev.e2.rie.gouv.fr
export PIAG_TIMEOUT=10

# Production
export PIAG_API_URL=https://piag.e2.rie.gouv.fr
export PIAG_TIMEOUT=120
```

## 🐛 Résolution de problèmes

### Problème : Configuration non prise en compte

**Solution** : Vérifier la hiérarchie avec `-S`

```bash
ambulon piag-chat-query -S
# Regarder quelle source a la priorité
```

### Problème : Token non détecté

**Solution** : Vérifier la variable d'environnement

```bash
# Afficher la variable (attention : sensible)
echo $PIAG_API_TOKEN

# Vérifier qu'elle est exportée
export | grep PIAG
```

### Problème : Fichier YAML non trouvé

**Solution** : Vérifier le chemin

```bash
# Chemin par défaut
ls -l config/piag.yaml

# Chemin personnalisé
ambulon piag-chat-query --config /path/to/config.yaml -S
```

## 📖 Exemples pratiques

### Exemple 1 : Développement local

```bash
# Créer config local
cp config/piag.yaml.example config/piag.dev.yaml

# Définir token
export PIAG_API_TOKEN=dev_token_123

# Utiliser config dev
ambulon piag-chat-query --config config/piag.dev.yaml --query "test"
```

### Exemple 2 : CI/CD

```bash
# Variables d'environnement uniquement (pas de fichier YAML)
export PIAG_API_URL=https://piag.ci.example.com
export PIAG_API_TOKEN=$CI_PIAG_TOKEN
export PIAG_TIMEOUT=180

# Exécuter sans fichier config
ambulon piag-chat-query --query "test"
```

### Exemple 3 : Override ponctuel

```bash
# Config normale via YAML
# Mais override ponctuel du timeout
ambulon piag-chat-query --timeout 5m --query "test"
```

## 🔗 Références

- [ConfigManager](../../src/app/core/config_manager.py) - Gestionnaire de configuration
- [ConfigTracker](../../src/app/core/config_tracker.py) - Tracking des sources
- [Exemples](../../.claude/examples/) - Exemples d'utilisation
