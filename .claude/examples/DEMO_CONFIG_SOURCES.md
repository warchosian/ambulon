# Démonstration : Option `-S, --show-config-sources`

Ce document présente des exemples concrets d'utilisation de l'option de traçabilité de configuration dans les modules ambulon.

## Option Abrégée

**Format** : `-S` (majuscule)
**Équivalent** : `--show-config-sources`
**Action** : Affiche la provenance de chaque paramètre et quitte (exit code 0)

**Pourquoi `-S` ?**
- `S` majuscule = **S**ources de configuration
- Évite conflit avec `-s` (souvent `--silent`, `--size`, etc.)
- Convention : options importantes en majuscule

---

## Exemple 1 : Module `wikisi-sync-api`

### Configuration du Module

**Hiérarchie supportée :**
1. Arguments CLI (`--output`, `--base-url`, etc.)
2. Fichier YAML (`config/wikisi.yaml`)
3. Variables d'environnement (`WIKISI_*`)
4. Valeurs par défaut

### Fichier de Configuration

**`config/wikisi.yaml`**
```yaml
api:
  base_url: "${WIKISI_BASE_URL:-https://wikisi.default.fr}"
  timeout: 30
  auth_token: "${WIKISI_TOKEN:-}"

output:
  directory: "./wikisi-data"
  format: "json"

scraping:
  max_depth: 3
  follow_links: true
```

### Scénario 1 : Configuration par défaut uniquement

```bash
ambulon wikisi-sync-api -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         Default              https://wikisi.default.fr
api.timeout          Default              30
api.auth_token       Default              ****** (masked)
output.directory     Default              ./wikisi-data
output.format        Default              json
scraping.max_depth   Default              3
scraping.follow_links Default             true

Summary:
  - Default:           7 parameter(s)

✓ Configuration sources displayed successfully
```

---

### Scénario 2 : Avec fichier YAML

```bash
ambulon wikisi-sync-api --config config/wikisi.yaml -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         YAML File            https://wikisi.default.fr
api.timeout          YAML File            30
api.auth_token       YAML File            ****** (masked)
output.directory     YAML File            ./wikisi-data
output.format        YAML File            json
scraping.max_depth   YAML File            3
scraping.follow_links YAML File           true

Summary:
  - YAML File:         7 parameter(s)

Config file: G:/WarchoLife/config/wikisi.yaml

✓ Configuration sources displayed successfully
```

---

### Scénario 3 : Avec variables d'environnement

```bash
# Définir les variables d'environnement
export WIKISI_BASE_URL="https://wikisi.production.fr"
export WIKISI_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
export WIKISI_MAX_DEPTH="5"

# Exécuter avec -S
ambulon wikisi-sync-api -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         Environment          https://wikisi.production.fr
api.timeout          Default              30
api.auth_token       Environment          ****** (masked)
output.directory     Default              ./wikisi-data
output.format        Default              json
scraping.max_depth   Environment          5
scraping.follow_links Default             true

Summary:
  - Environment:       3 parameter(s)
  - Default:           4 parameter(s)

✓ Configuration sources displayed successfully
```

**Observation** : Les variables d'environnement ont correctement écrasé les valeurs par défaut.

---

### Scénario 4 : Arguments CLI (priorité maximale)

```bash
ambulon wikisi-sync-api \
  --output ./custom-output \
  --base-url https://wikisi.dev.fr \
  --max-depth 10 \
  -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         CLI Argument         https://wikisi.dev.fr
api.timeout          Default              30
api.auth_token       Default              ****** (masked)
output.directory     CLI Argument         ./custom-output
output.format        Default              json
scraping.max_depth   CLI Argument         10
scraping.follow_links Default             true

Summary:
  - CLI Argument:      3 parameter(s)
  - Default:           4 parameter(s)

✓ Configuration sources displayed successfully
```

**Observation** : Les arguments CLI ont la priorité absolue.

---

### Scénario 5 : Hiérarchie complète (4 niveaux)

```bash
# Variables d'environnement
export WIKISI_BASE_URL="https://wikisi.env.fr"
export WIKISI_TOKEN="env_token_123"
export WIKISI_MAX_DEPTH="7"

# Exécution avec YAML + CLI
ambulon wikisi-sync-api \
  --config config/wikisi.yaml \
  --output ./cli-output \
  --timeout 60 \
  -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         Environment          https://wikisi.env.fr
api.timeout          CLI Argument         60
api.auth_token       Environment          ****** (masked)
output.directory     CLI Argument         ./cli-output
output.format        YAML File            json
scraping.max_depth   Environment          7
scraping.follow_links YAML File           true

Summary:
  - CLI Argument:      2 parameter(s)
  - Environment:       3 parameter(s)
  - YAML File:         2 parameter(s)

Config file: G:/WarchoLife/config/wikisi.yaml

✓ Configuration sources displayed successfully
```

**Vérification de la hiérarchie :**

| Paramètre | CLI | ENV | YAML | Default | Source Finale |
|-----------|-----|-----|------|---------|---------------|
| `api.base_url` | ❌ | ✅ | ✅ | ✅ | **Environment** ✓ |
| `api.timeout` | ✅ | ❌ | ✅ | ✅ | **CLI Argument** ✓ |
| `api.auth_token` | ❌ | ✅ | ✅ | ✅ | **Environment** ✓ |
| `output.directory` | ✅ | ❌ | ✅ | ✅ | **CLI Argument** ✓ |
| `output.format` | ❌ | ❌ | ✅ | ✅ | **YAML File** ✓ |
| `scraping.max_depth` | ❌ | ✅ | ✅ | ✅ | **Environment** ✓ |
| `scraping.follow_links` | ❌ | ❌ | ✅ | ✅ | **YAML File** ✓ |

**✓ Hiérarchie respectée : CLI > ENV > YAML > Default**

---

## Exemple 2 : Module `piag-chat-query`

### Configuration du Module

**Hiérarchie supportée :**
1. Arguments CLI (`--question-file`, `--chunks`, `--timeout`, etc.)
2. Fichier YAML (`config/piag.yaml`)
3. Variables d'environnement (`PIAG_*`)
4. Valeurs par défaut

### Fichier de Configuration

**`config/piag.yaml`**
```yaml
api:
  base_url: "${PIAG_BASE_URL:-https://piag.default.fr}"
  token: "${PIAG_TOKEN:-}"
  timeout: 300  # 5 minutes

chat:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 4000

retry:
  max_retries: 5
  retry_delay: 60  # 1 minute
  backoff_factor: 2
```

### Scénario : Production avec secrets sécurisés

```bash
# Variables d'environnement (secrets)
export PIAG_BASE_URL="https://piag.production.fr"
export PIAG_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0..."

# Fichier YAML pour config non sensible
cat > config/piag-prod.yaml <<EOF
chat:
  model: "gpt-4-turbo"
  temperature: 0.5
  max_tokens: 8000

retry:
  max_retries: 10
  retry_delay: 120
EOF

# Arguments CLI pour override ponctuel
ambulon piag-chat-query \
  --question-file prompts/query.md \
  --chunks chunks/data.json \
  --timeout 1200 \
  --max-retries 3 \
  --config config/piag-prod.yaml \
  -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         Environment          https://piag.production.fr
api.token            Environment          ****** (masked)
api.timeout          CLI Argument         1200
chat.model           YAML File            gpt-4-turbo
chat.temperature     YAML File            0.5
chat.max_tokens      YAML File            8000
retry.max_retries    CLI Argument         3
retry.retry_delay    YAML File            120
retry.backoff_factor Default              2
question_file        CLI Argument         prompts/query.md
chunks_file          CLI Argument         chunks/data.json

Summary:
  - CLI Argument:      4 parameter(s)
  - Environment:       2 parameter(s)
  - YAML File:         4 parameter(s)
  - Default:           1 parameter(s)

Config file: G:/WarchoLife/config/piag-prod.yaml

✓ Configuration sources displayed successfully
```

**Analyse de Sécurité :**
- ✅ Token masqué (`****** (masked)`)
- ✅ Token provient de variable d'environnement (pas hardcodé)
- ✅ Fichier YAML ne contient aucun secret
- ✅ Configuration traçable et auditable

---

## Exemple 3 : Debugging d'un Problème de Configuration

### Problème Reporté

**Utilisateur** : "La commande `wikisi-sync-api` utilise la mauvaise URL, je ne comprends pas pourquoi."

### Investigation avec `-S`

```bash
ambulon wikisi-sync-api --config config/wikisi.yaml -S
```

**Sortie :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         Environment          https://wikisi.old-server.fr
api.timeout          YAML File            30
...

Summary:
  - Environment:       1 parameter(s)
  - YAML File:         6 parameter(s)

Config file: G:/WarchoLife/config/wikisi.yaml

✓ Configuration sources displayed successfully
```

**Diagnostic** :
- La base_url vient de `Environment` au lieu de `YAML File`
- Variable d'environnement `WIKISI_BASE_URL` définie quelque part
- Solution : `unset WIKISI_BASE_URL` ou utiliser `--base-url` en CLI

**Résolution :**
```bash
# Vérifier la variable
echo $WIKISI_BASE_URL
# Output: https://wikisi.old-server.fr

# Supprimer la variable obsolète
unset WIKISI_BASE_URL

# Re-vérifier
ambulon wikisi-sync-api --config config/wikisi.yaml -S
```

**Nouvelle sortie :**
```
Parameter            Source               Value
-------------------- -------------------- ------------------------------
api.base_url         YAML File            https://wikisi.production.fr
...
```

**✓ Problème résolu grâce à `-S` !**

---

## Exemple 4 : Validation d'Environnement CI/CD

### Pipeline GitLab CI

```yaml
# .gitlab-ci.yml
test_config:
  stage: test
  script:
    # Vérifier que les variables d'env CI sont bien utilisées
    - ambulon piag-chat-query -S | tee config_report.txt

    # Valider que le token vient bien de l'environnement
    - grep "api.token.*Environment" config_report.txt || exit 1

    # Valider que le token est masqué
    - grep "api.token.*masked" config_report.txt || exit 1

    # Valider la base_url de production
    - grep "api.base_url.*Environment.*piag.production.fr" config_report.txt || exit 1

    - echo "✓ Configuration CI/CD validée"
  artifacts:
    paths:
      - config_report.txt
    expire_in: 1 week
```

**Avantages :**
- ✅ Validation automatique de la configuration
- ✅ Détection de secrets hardcodés (fail si token pas masqué)
- ✅ Traçabilité des sources dans les artifacts
- ✅ Debugging facilité en cas d'échec

---

## Comparaison Avant/Après

### ❌ Avant (sans `-S`)

**Problème** : Configuration incorrecte, impossible de savoir d'où vient la valeur.

```bash
ambulon wikisi-sync-api --output ./data

# Erreur : "Connection failed to https://wikisi.old-server.fr"
# Question : D'où vient cette URL ???
# Debugging : 30 minutes à chercher dans le code, config, env vars...
```

### ✅ Après (avec `-S`)

**Solution** : Diagnostic immédiat en 10 secondes.

```bash
ambulon wikisi-sync-api --output ./data -S

# Sortie claire :
# api.base_url    Environment    https://wikisi.old-server.fr
#
# Action : unset WIKISI_BASE_URL
# Temps de résolution : 10 secondes
```

---

## Bonnes Pratiques d'Utilisation

### 1. Debugging Rapide

```bash
# Avant d'exécuter une commande importante
ambulon ma-commande [args] -S

# Vérifier la configuration
# Si OK → Relancer sans -S pour exécution réelle
```

### 2. Documentation d'Exécution

```bash
# Sauvegarder la configuration utilisée
ambulon piag-chat-query \
  --question-file prompts/query.md \
  -S > execution_config_$(date +%Y%m%d_%H%M%S).txt

# Joindre au rapport d'exécution
```

### 3. Validation de Sécurité

```bash
# Vérifier qu'aucun secret n'est hardcodé
ambulon ma-commande -S | grep -i "token\|password\|secret"

# Doit afficher "****** (masked)"
# Si valeur en clair → PROBLÈME DE SÉCURITÉ
```

### 4. Onboarding Nouveaux Développeurs

```bash
# Montrer la configuration active
ambulon wikisi-sync-api -S

# Expliquer :
# - Quelles variables d'env définir
# - Où placer le fichier config
# - Quels arguments CLI utiliser
```

---

## Résumé des Options

| Option | Équivalent | Description |
|--------|-----------|-------------|
| `-S` | `--show-config-sources` | Affiche la provenance de la configuration |
| `-c FILE` | `--config FILE` | Fichier YAML de configuration |
| `-v` | `--verbose` | Mode verbeux (logs détaillés) |
| `-h` | `--help` | Aide de la commande |

**Combinaisons utiles :**
- `-S` : Diagnostic configuration uniquement
- `-c config.yaml -S` : Tester un fichier de config
- `-v` : Exécution avec logs détaillés
- `-c config.yaml` : Exécution avec config

---

## Questions Fréquentes

**Q: `-S` exécute-t-il la commande ?**
R: Non, `-S` affiche la configuration et quitte (exit code 0). C'est un mode diagnostic.

**Q: Peut-on combiner `-S` avec `-v` ?**
R: Oui, mais `-S` quitte avant l'exécution, donc `-v` n'aura pas d'effet.

**Q: Comment exécuter APRÈS avoir vérifié avec `-S` ?**
R: Relancer la même commande sans `-S`.

**Q: Les secrets sont-ils vraiment masqués ?**
R: Oui, tout paramètre contenant `token`, `password`, `secret`, `key`, ou `credential` est masqué automatiquement.

**Q: Que faire si un secret apparaît en clair ?**
R: **PROBLÈME CRITIQUE** - Le paramètre n'est pas détecté comme sensible. Reporter immédiatement.

---

## Voir Aussi

- **`.claude/GUIDELINES.md`** : Spécification complète de la hiérarchie
- **`.claude/examples/config_tracking_example.py`** : Implémentation de référence
- **`.claude/examples/README.md`** : Guide d'intégration
