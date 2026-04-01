# Démonstration : gitlab-clone avec `-S, --show-config-sources`

Ce document présente des exemples concrets d'utilisation de l'option de traçabilité de configuration pour la commande `gitlab-clone`.

## Vue d'ensemble

La commande `gitlab-clone` utilise la hiérarchie de configuration standardisée :

1. **Arguments CLI** (`--token`, `--username`, `--output`, `--repositories`)
2. **Fichier YAML** (`--config config/gitlab.yaml`)
3. **Variables d'environnement** (`GITLAB_PRIVATE_TOKEN`, `GITLAB_USERNAME`)
4. **Valeurs par défaut** (codées en dur)

L'option `-S` permet de visualiser d'où provient chaque paramètre **avant** l'exécution.

---

## Configuration par Défaut

### Scénario 1 : Aucune configuration fournie

```bash
ambulon gitlab-clone -S
```

**Sortie :**
```
Configuration Sources Report - gitlab-clone
======================================================================

Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Default              (empty)
gitlab.username           Default              oauth2
gitlab.base_clone_dir     Default              ./gitlab_clones
gitlab.repositories       Default              (empty)

Summary:
  - Default:           4 parameter(s)

✓ Configuration sources displayed successfully
```

**Analyse :**
- ❌ `token` vide → Erreur si on exécute sans `-S`
- ❌ `repositories` vide → Erreur si on exécute sans `-S`
- ✅ `username` et `base_clone_dir` ont des valeurs par défaut utilisables
- **Action** : Fournir token et repositories via CLI, YAML ou ENV

---

## Configuration via Fichier YAML

### Scénario 2 : Fichier de configuration complet

**Fichier : `config/gitlab.yaml`**
```yaml
gitlab:
  # Token via variable d'environnement (sécurisé)
  token: "${GITLAB_PRIVATE_TOKEN}"

  # Username avec valeur par défaut
  username: "${GITLAB_USERNAME:-oauth2}"

  # Répertoire de clonage
  base_clone_dir: "./my-gitlab-projects"

  # Liste des repositories
  repositories:
    - "https://gitlab.example.com/team/project-backend.git"
    - "https://gitlab.example.com/team/project-frontend.git"
    - "https://gitlab.example.com/team/project-docs.git"
```

**Commande :**
```bash
ambulon gitlab-clone --config config/gitlab.yaml -S
```

**Sortie :**
```
Configuration Sources Report - gitlab-clone
======================================================================

Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              YAML File            ****** (masked)
gitlab.username           YAML File            oauth2
gitlab.base_clone_dir     YAML File            ./my-gitlab-projects
gitlab.repositories       YAML File            3 repositories

Summary:
  - YAML File:         4 parameter(s)

Config file: G:/WarchoLife/config/gitlab.yaml

✓ Configuration sources displayed successfully
```

**Analyse :**
- ✅ Toutes les valeurs proviennent du YAML
- ✅ Token correctement masqué
- ✅ 3 repositories détectés
- **Prêt à exécuter** : Retirer `-S` pour cloner effectivement

---

## Configuration via Variables d'Environnement

### Scénario 3 : Token via variable d'environnement

**Commande :**
```bash
# Définir les variables d'environnement
export GITLAB_PRIVATE_TOKEN="glpat-aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"
export GITLAB_USERNAME="myuser"

# Vérifier la configuration
ambulon gitlab-clone \
  --config config/gitlab.yaml \
  -S
```

**Sortie :**
```
Configuration Sources Report - gitlab-clone
======================================================================

Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Environment          ****** (masked)
gitlab.username           Environment          myuser
gitlab.base_clone_dir     YAML File            ./my-gitlab-projects
gitlab.repositories       YAML File            3 repositories

Summary:
  - Environment:       2 parameter(s)
  - YAML File:         2 parameter(s)

Config file: G:/WarchoLife/config/gitlab.yaml

✓ Configuration sources displayed successfully
```

**Analyse :**
- ✅ Token et username proviennent de l'environnement (écrasent le YAML)
- ✅ Base dir et repos restent du YAML
- ✅ Hiérarchie respectée : ENV > YAML
- **Sécurité** : Token jamais affiché en clair

---

## Configuration via Arguments CLI

### Scénario 4 : Override complet par CLI

**Commande :**
```bash
ambulon gitlab-clone \
  --token glpat-123456789abcdefghijk \
  --username oauth2 \
  --output ./custom-output \
  --repositories https://gitlab.example.com/user/project1.git \
  --repositories https://gitlab.example.com/user/project2.git \
  -S
```

**Sortie :**
```
Configuration Sources Report - gitlab-clone
======================================================================

Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              CLI Argument         ****** (masked)
gitlab.username           CLI Argument         oauth2
gitlab.base_clone_dir     CLI Argument         ./custom-output
gitlab.repositories       CLI Argument         2 repositories

Summary:
  - CLI Argument:      4 parameter(s)

✓ Configuration sources displayed successfully
```

**Analyse :**
- ✅ Tous les paramètres viennent de la CLI
- ✅ Aucun fichier de config nécessaire
- ✅ Override total des defaults
- **Cas d'usage** : Test rapide, CI/CD, scripts

---

## Hiérarchie Complète (4 Niveaux)

### Scénario 5 : Combinaison CLI + ENV + YAML + Defaults

**Setup :**
```bash
# 1. Variables d'environnement
export GITLAB_PRIVATE_TOKEN="glpat-env-token-123"
export GITLAB_USERNAME="envuser"

# 2. Fichier YAML existe avec base_clone_dir et repositories

# 3. Arguments CLI pour override ponctuel
ambulon gitlab-clone \
  --config config/gitlab.yaml \
  --output ./cli-override-dir \
  -S
```

**Sortie :**
```
Configuration Sources Report - gitlab-clone
======================================================================

Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Environment          ****** (masked)
gitlab.username           Environment          envuser
gitlab.base_clone_dir     CLI Argument         ./cli-override-dir
gitlab.repositories       YAML File            3 repositories

Summary:
  - CLI Argument:      1 parameter(s)
  - Environment:       2 parameter(s)
  - YAML File:         1 parameter(s)

Config file: G:/WarchoLife/config/gitlab.yaml

✓ Configuration sources displayed successfully
```

**Vérification de la hiérarchie :**

| Paramètre | CLI | ENV | YAML | Default | Source Finale | ✓ |
|-----------|-----|-----|------|---------|---------------|---|
| `token` | ❌ | ✅ | ✅ | ✅ | **Environment** | ✓ |
| `username` | ❌ | ✅ | ✅ | ✅ | **Environment** | ✓ |
| `base_clone_dir` | ✅ | ❌ | ✅ | ✅ | **CLI Argument** | ✓ |
| `repositories` | ❌ | ❌ | ✅ | ✅ | **YAML File** | ✓ |

**Conclusion** : Hiérarchie parfaitement respectée (CLI > ENV > YAML > Default)

---

## Cas d'Usage Pratiques

### Cas 1 : Debugging - Pourquoi mon token ne fonctionne pas ?

**Problème** : L'utilisateur obtient "401 Unauthorized"

**Diagnostic :**
```bash
ambulon gitlab-clone --config config/gitlab.yaml -S
```

**Sortie révélatrice :**
```
Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Default              (empty)
```

**Diagnostic** : Le token est vide !

**Causes possibles :**
1. Variable `GITLAB_PRIVATE_TOKEN` non définie
2. Fichier YAML ne contient pas le token
3. Fichier YAML ne fait pas la substitution `${GITLAB_PRIVATE_TOKEN}`

**Solution :**
```bash
# Vérifier la variable
echo $GITLAB_PRIVATE_TOKEN

# Si vide, la définir
export GITLAB_PRIVATE_TOKEN="glpat-your-token-here"

# Re-vérifier
ambulon gitlab-clone --config config/gitlab.yaml -S
```

**Nouvelle sortie :**
```
gitlab.token              Environment          ****** (masked)
```

**✓ Problème résolu !**

---

### Cas 2 : Validation CI/CD

**Contexte** : Pipeline GitLab CI qui clone des repositories automatiquement

**Script de validation :**
```yaml
# .gitlab-ci.yml
test:config:
  stage: test
  script:
    # Vérifier que le token vient bien de l'environnement CI
    - ambulon gitlab-clone -S | tee config_report.txt

    # Validation : token doit être masqué
    - grep "gitlab.token.*masked" config_report.txt || exit 1

    # Validation : token doit venir de l'environnement
    - grep "gitlab.token.*Environment" config_report.txt || exit 1

    # Validation : pas de valeur par défaut vide pour le token
    - grep "gitlab.token.*Default.*(empty)" config_report.txt && exit 1 || true

    - echo "✓ Configuration CI/CD validée"
  artifacts:
    paths:
      - config_report.txt
    expire_in: 1 day
```

**Avantages :**
- ✅ Détection automatique de config incorrecte
- ✅ Échec rapide si token non fourni
- ✅ Traçabilité de la config dans les artifacts
- ✅ Audit de sécurité (token jamais exposé)

---

### Cas 3 : Documentation d'Exécution

**Scénario** : Générer un rapport de configuration pour audit

**Commande :**
```bash
# Capturer la config effective
ambulon gitlab-clone \
  --config config/gitlab-prod.yaml \
  -S > audit/gitlab_config_$(date +%Y%m%d_%H%M%S).txt

# Exécuter effectivement (sans -S)
ambulon gitlab-clone \
  --config config/gitlab-prod.yaml
```

**Résultat :**
- Fichier `audit/gitlab_config_20260401_143022.txt` :
  ```
  Configuration Sources Report - gitlab-clone
  ======================================================================

  Parameter                 Source               Value
  ------------------------- -------------------- -------------------------
  gitlab.token              Environment          ****** (masked)
  gitlab.username           Environment          oauth2
  gitlab.base_clone_dir     YAML File            ./production-repos
  gitlab.repositories       YAML File            15 repositories

  Config file: /srv/ambulon/config/gitlab-prod.yaml
  ```

**Usage** :
- Audit de conformité
- Documentation d'exécution
- Debugging post-mortem
- Validation des procédures

---

## Cas d'Erreurs Courantes

### Erreur 1 : Token vide

**Symptôme :**
```bash
ambulon gitlab-clone -S
```

```
gitlab.token              Default              (empty)
```

**Solution :**
```bash
export GITLAB_PRIVATE_TOKEN="glpat-your-token"
```

---

### Erreur 2 : Mauvais fichier de configuration

**Symptôme :**
```bash
ambulon gitlab-clone --config config/wrong.yaml -S
```

```
Config file: G:/config/wrong.yaml
  ⚠️  File not found (using defaults)
```

**Solution :**
```bash
# Vérifier le chemin
ls -l config/gitlab.yaml

# Corriger le chemin
ambulon gitlab-clone --config config/gitlab.yaml -S
```

---

### Erreur 3 : Variable d'environnement obsolète

**Symptôme :**
```bash
ambulon gitlab-clone --config config/gitlab.yaml -S
```

```
gitlab.base_clone_dir     Environment          ./old-folder
```

**Diagnostic** : Variable `GITLAB_BASE_CLONE_DIR` définie dans `.bashrc` ou similaire

**Solution :**
```bash
# Identifier la variable
env | grep GITLAB

# Supprimer si obsolète
unset GITLAB_BASE_CLONE_DIR

# Re-vérifier
ambulon gitlab-clone --config config/gitlab.yaml -S
```

---

## Test de l'Exemple

### Prérequis

```bash
cd .claude/examples
```

### Test 1 : Configuration par défaut

```bash
python gitlab_clone_with_tracking.py -S
```

**Résultat attendu :**
```
Configuration Sources Report - gitlab-clone
======================================================================

Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Default              (empty)
gitlab.username           Default              oauth2
gitlab.base_clone_dir     Default              ./gitlab_clones
gitlab.repositories       Default              (empty)

Summary:
  - Default:           4 parameter(s)

✓ Configuration sources displayed successfully
```

---

### Test 2 : Avec variables d'environnement

```bash
GITLAB_PRIVATE_TOKEN=test_token_123 \
GITLAB_USERNAME=testuser \
python gitlab_clone_with_tracking.py -S
```

**Résultat attendu :**
```
Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Environment          ****** (masked)
gitlab.username           Environment          testuser
gitlab.base_clone_dir     Default              ./gitlab_clones
gitlab.repositories       Default              (empty)

Summary:
  - Environment:       2 parameter(s)
  - Default:           2 parameter(s)
```

---

### Test 3 : Avec arguments CLI

```bash
python gitlab_clone_with_tracking.py \
  --token cli_token_456 \
  --username cliuser \
  --output ./custom \
  --repositories https://gitlab.com/project1.git \
  --repositories https://gitlab.com/project2.git \
  -S
```

**Résultat attendu :**
```
Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              CLI Argument         ****** (masked)
gitlab.username           CLI Argument         cliuser
gitlab.base_clone_dir     CLI Argument         ./custom
gitlab.repositories       CLI Argument         2 repositories

Summary:
  - CLI Argument:      4 parameter(s)
```

---

### Test 4 : Hiérarchie complète

```bash
GITLAB_PRIVATE_TOKEN=env_token \
GITLAB_USERNAME=envuser \
python gitlab_clone_with_tracking.py \
  --output ./cli-output \
  --repositories https://gitlab.com/project.git \
  -S
```

**Résultat attendu :**
```
Parameter                 Source               Value
------------------------- -------------------- -------------------------
gitlab.token              Environment          ****** (masked)
gitlab.username           Environment          envuser
gitlab.base_clone_dir     CLI Argument         ./cli-output
gitlab.repositories       CLI Argument         1 repositories

Summary:
  - CLI Argument:      2 parameter(s)
  - Environment:       2 parameter(s)
```

**✓ Hiérarchie respectée : CLI > ENV > Default**

---

## Résumé

### Option Abrégée

**`-S`** = `--show-config-sources`

### Paramètres Trackés

| Paramètre | Sensible | Masqué |
|-----------|----------|--------|
| `gitlab.token` | ✅ | ✅ |
| `gitlab.username` | ❌ | ❌ |
| `gitlab.base_clone_dir` | ❌ | ❌ |
| `gitlab.repositories` | ❌ | ❌ |

### Sources Possibles

1. **CLI Argument** (priorité maximale)
2. **Environment** (variables d'env)
3. **YAML File** (fichier de config)
4. **Default** (valeurs codées)

### Avantages

✅ **Debugging instantané** : Voir d'où vient chaque valeur
✅ **Sécurité** : Tokens toujours masqués
✅ **Validation** : Confirmer la hiérarchie
✅ **Audit** : Traçabilité complète
✅ **CI/CD** : Validation automatique

---

## Voir Aussi

- **`.claude/GUIDELINES.md`** : Spécification complète
- **`.claude/examples/config_tracking_example.py`** : Implémentation générique
- **`.claude/examples/gitlab_clone_with_tracking.py`** : Implémentation gitlab-clone
- **`DEMO_CONFIG_SOURCES.md`** : Exemples wikisi-sync-api et piag-chat-query
