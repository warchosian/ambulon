# Exemples de Configuration avec Tracking des Sources

Ce répertoire contient des exemples d'implémentation de l'option `--show-config-sources` pour tracer la provenance des paramètres de configuration.

## Fichiers

- **`config_tracking_example.py`** : Exemple complet d'implémentation
- **`config_example.yaml`** : Fichier de configuration YAML d'exemple
- **`README.md`** : Ce fichier

## Qu'est-ce que `--show-config-sources` ?

Une option CLI qui affiche un rapport détaillé montrant d'où vient chaque paramètre de configuration utilisé par la commande :

- **CLI Argument** : Passé en ligne de commande (`--url https://...`)
- **YAML File** : Défini dans le fichier de configuration
- **Environment** : Variable d'environnement (`MY_MODULE_URL=...`)
- **Default** : Valeur par défaut codée en dur

## Tests de l'Exemple

### Prérequis

```bash
pip install pyyaml
```

### 1. Configuration par défaut uniquement

```bash
# Option abrégée (recommandé)
python config_tracking_example.py -S

# ou version longue
python config_tracking_example.py --show-config-sources
```

**Sortie attendue :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
url                  Default              https://default.example.com
timeout              Default              30
output               Default              ./output
api_token            Default              ****** (masked)
max_retries          Default              3

Summary:
  - Default:           5 parameter(s)

✓ Configuration sources displayed successfully
```

---

### 2. Avec fichier YAML

```bash
python config_tracking_example.py \
  --config config_example.yaml \
  --show-config-sources
```

**Sortie attendue :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
url                  YAML File            https://yaml-default.example.com
timeout              YAML File            60
output               YAML File            ./data/output
api_token            YAML File            ****** (masked)
auth_type            YAML File            bearer
max_retries          YAML File            5
retry_delay          YAML File            2

Summary:
  - YAML File:         7 parameter(s)

Config file: /path/to/config_example.yaml

✓ Configuration sources displayed successfully
```

---

### 3. Avec variables d'environnement

```bash
MY_MODULE_URL=https://from-env.com \
MY_MODULE_API_TOKEN=secret_token_123 \
python config_tracking_example.py \
  --show-config-sources
```

**Sortie attendue :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
url                  Environment          https://from-env.com
timeout              Default              30
output               Default              ./output
api_token            Default              ****** (masked)
max_retries          Default              3

Summary:
  - Environment:       1 parameter(s)
  - Default:           4 parameter(s)

✓ Configuration sources displayed successfully
```

---

### 4. Avec arguments CLI (priorité maximale)

```bash
python config_tracking_example.py \
  --url https://from-cli.com \
  --timeout 120 \
  --show-config-sources
```

**Sortie attendue :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
url                  CLI Argument         https://from-cli.com
timeout              CLI Argument         120
output               Default              ./output
api_token            Default              ****** (masked)
max_retries          Default              3

Summary:
  - CLI Argument:      2 parameter(s)
  - Default:           3 parameter(s)

✓ Configuration sources displayed successfully
```

---

### 5. Combinaison complète (vérification de la hiérarchie)

```bash
MY_MODULE_URL=https://from-env.com \
MY_MODULE_TIMEOUT=90 \
python config_tracking_example.py \
  --url https://from-cli.com \
  --config config_example.yaml \
  --show-config-sources
```

**Sortie attendue (hiérarchie correcte) :**
```
Configuration Sources Report
======================================================================

Parameter            Source               Value
-------------------- -------------------- ------------------------------
url                  CLI Argument         https://from-cli.com
timeout              Environment          90
output               YAML File            ./data/output
api_token            YAML File            ****** (masked)
auth_type            YAML File            bearer
max_retries          YAML File            5
retry_delay          YAML File            2

Summary:
  - CLI Argument:      1 parameter(s)
  - Environment:       1 parameter(s)
  - YAML File:         5 parameter(s)

Config file: /path/to/config_example.yaml

✓ Configuration sources displayed successfully
```

**Explication de la hiérarchie :**
- `url` : **CLI** écrase ENV, YAML et Default ✓
- `timeout` : **ENV** écrase YAML et Default (pas d'arg CLI) ✓
- `output` : **YAML** écrase Default (pas d'arg CLI ni ENV) ✓
- `api_token` : **YAML** écrase Default ✓
- Autres : **YAML** uniquement ✓

---

## Vérification de Sécurité

Les valeurs sensibles (contenant `token`, `password`, `secret`, `key`) sont automatiquement masquées :

```bash
python config_tracking_example.py --show-config-sources
```

```
Parameter            Source               Value
-------------------- -------------------- ------------------------------
api_token            Default              ****** (masked)
```

**Jamais affiché en clair**, même en mode `--verbose`.

---

## Utilisation Sans `--show-config-sources`

La commande fonctionne normalement sans cette option :

```bash
python config_tracking_example.py --url https://example.com --verbose
```

**Sortie :**
```
URL: https://example.com
Timeout: 30s
Output: ./output

✓ Commande exécutée avec succès !
(Utilisez --show-config-sources pour voir la provenance de la config)
```

---

## Intégration dans Vos Projets

### Étape 1 : Copier les classes

Copiez `ConfigSource`, `ConfigValue` et `ConfigTracker` depuis `config_tracking_example.py` dans votre module de configuration.

### Étape 2 : Modifier `load_config()`

Ajoutez le paramètre `tracker` et enregistrez les sources :

```python
def load_config(config_path=None, default_config=None, tracker=None):
    config = {}

    # Defaults
    if default_config:
        for key, value in default_config.items():
            config[key] = value
            if tracker:
                tracker.set(key, value, ConfigSource.DEFAULT)

    # YAML
    if config_path:
        yaml_config = load_yaml(config_path)
        for key, value in yaml_config.items():
            config[key] = value
            if tracker:
                tracker.set(key, value, ConfigSource.YAML)

    return config
```

### Étape 3 : Ajouter l'option au parser

```python
# Ajouter l'option avec version abrégée -S
parser.add_argument(
    "-S", "--show-config-sources",
    action="store_true",
    help="Affiche la provenance de chaque paramètre de configuration et quitte"
)
```

### Étape 4 : Afficher le rapport

```python
tracker = ConfigTracker()
config = load_config(args.config, defaults, tracker)

# Appliquer CLI args
if args.url:
    config['url'] = args.url
    tracker.set('url', args.url, ConfigSource.CLI)

# Afficher si demandé
if args.show_config_sources:
    print(tracker.get_report())
    return 0
```

---

## Avantages

✅ **Debugging rapide** : Identifier immédiatement les conflits de configuration
✅ **Transparence** : Confirmer que la hiérarchie fonctionne correctement
✅ **Sécurité** : Masquage automatique des secrets
✅ **Documentation** : Montre concrètement la configuration effective
✅ **Validation** : Vérifier que les variables d'env sont bien appliquées

---

## Bonnes Pratiques

1. **Toujours masquer les secrets** : Utilisez `is_sensitive=True` pour tokens/passwords
2. **Documenter dans --help** : Expliquer l'option dans l'aide de la commande
3. **Exit code 0** : Sortir proprement après affichage du rapport
4. **Trier par source** : Facilite la lecture (CLI → YAML → ENV → Default)
5. **Afficher le chemin du config** : Utile pour vérifier quel fichier est chargé

---

## Questions Fréquentes

**Q: Pourquoi l'option quitte après affichage ?**
R: C'est un diagnostic, pas une exécution. L'utilisateur veut juste voir la config, pas lancer la commande.

**Q: Peut-on afficher la config ET exécuter ?**
R: Oui, mais créez une option séparée `--verbose-config` qui affiche puis continue.

**Q: Comment tracker les variables d'env dans YAML ?**
R: Capturez les substitutions `${VAR}` et enregistrez `ConfigSource.ENV` au lieu de `YAML`.

**Q: Les valeurs sensibles sont-elles totalement sécurisées ?**
R: Oui, tant que `is_sensitive=True` est utilisé. Elles ne sont jamais affichées en clair.

---

## Intégration dans Modules Réels

### gitlab-clone

Voir **`DEMO_GITLAB_CLONE_CONFIG_SOURCES.md`** pour une démonstration complète de l'intégration dans la commande `gitlab-clone`.

**Fichiers d'exemple :**
- `gitlab_clone_with_tracking.py` : Implémentation complète avec ConfigTracker
- Scénarios de test : Defaults, ENV, YAML, CLI, hiérarchie complète
- Cas d'usage : Debugging, validation CI/CD, audit

**Paramètres trackés :**
- `gitlab.token` (sensible, masqué)
- `gitlab.username`
- `gitlab.base_clone_dir`
- `gitlab.repositories`

**Commande rapide :**
```bash
cd .claude/examples
python gitlab_clone_with_tracking.py -S
```

---

## Voir Aussi

- **`.claude/GUIDELINES.md`** : Documentation complète de la hiérarchie de configuration
- **Section "Traçabilité de Configuration"** : Spécifications détaillées
- **`DEMO_CONFIG_SOURCES.md`** : Exemples wikisi-sync-api et piag-chat-query
- **`DEMO_GITLAB_CLONE_CONFIG_SOURCES.md`** : Exemple gitlab-clone complet
