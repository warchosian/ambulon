# Index des Exemples - Option `--show-config-sources`

Ce répertoire contient tous les exemples et démonstrations de l'option `-S, --show-config-sources` pour la traçabilité de configuration.

## 📁 Structure des Fichiers

```
.claude/examples/
├── INDEX.md                              # Ce fichier (vue d'ensemble)
├── README.md                             # Guide d'utilisation principal
│
├── config_tracking_example.py            # Implémentation de référence (générique)
├── config_example.yaml                   # Fichier YAML d'exemple
│
├── gitlab_clone_with_tracking.py         # Intégration dans gitlab-clone
│
├── DEMO_CONFIG_SOURCES.md                # Démos wikisi-sync-api & piag-chat-query
└── DEMO_GITLAB_CLONE_CONFIG_SOURCES.md   # Démo gitlab-clone complète
```

---

## 📚 Fichiers de Documentation

### 1. **INDEX.md** (ce fichier)
Vue d'ensemble de tous les fichiers d'exemples avec descriptions.

### 2. **README.md**
Guide principal d'utilisation avec :
- Présentation de `--show-config-sources`
- 5 scénarios de test détaillés
- Instructions d'intégration dans vos projets
- FAQ et bonnes pratiques

### 3. **DEMO_CONFIG_SOURCES.md**
Démonstrations pour modules génériques :
- **wikisi-sync-api** : 5 scénarios (defaults, YAML, ENV, CLI, hiérarchie complète)
- **piag-chat-query** : Configuration production avec secrets sécurisés
- Cas d'usage : Debugging, validation CI/CD, audit
- Comparaison avant/après

### 4. **DEMO_GITLAB_CLONE_CONFIG_SOURCES.md**
Démonstration spécifique `gitlab-clone` :
- 5 scénarios de configuration
- Cas d'usage pratiques (debugging, CI/CD, documentation)
- 3 erreurs courantes avec solutions
- 4 tests de l'implémentation

---

## 🐍 Fichiers Python

### 1. **config_tracking_example.py** (Implémentation de référence)

**Rôle** : Exemple générique complet et autonome

**Contenu :**
- Classes `ConfigSource`, `ConfigValue`, `ConfigTracker`
- Fonction `load_config_with_tracking()`
- Pattern complet main() avec argparse
- Support des 4 niveaux de hiérarchie

**Usage :**
```bash
python config_tracking_example.py -S
python config_tracking_example.py --config config_example.yaml -S
MY_MODULE_URL=https://test.com python config_tracking_example.py -S
```

**Paramètres trackés :**
- `url`
- `timeout`
- `output`
- `api_token` (sensible, masqué)
- `max_retries`

---

### 2. **gitlab_clone_with_tracking.py** (Intégration réelle)

**Rôle** : Démonstration d'intégration dans un module ambulon réel

**Contenu :**
- Intégration avec gitlab-clone
- Tracking de la configuration GitLab
- Simulation de chargement YAML
- Validation de configuration

**Usage :**
```bash
python gitlab_clone_with_tracking.py -S
GITLAB_PRIVATE_TOKEN=xxx python gitlab_clone_with_tracking.py -S
python gitlab_clone_with_tracking.py --token xxx --repositories https://... -S
```

**Paramètres trackés :**
- `gitlab.token` (sensible, masqué)
- `gitlab.username`
- `gitlab.base_clone_dir`
- `gitlab.repositories`

---

## 📄 Fichiers de Configuration

### **config_example.yaml**

Fichier YAML d'exemple avec :
- Substitution de variables d'environnement (`${VAR:-default}`)
- Sections main, auth, behavior
- Commentaires explicatifs
- Valeurs d'exemple (pas de vrais tokens)

**Usage :**
```bash
python config_tracking_example.py --config config_example.yaml -S
```

---

## 🎯 Guide de Démarrage Rapide

### Étape 1 : Tester l'implémentation générique

```bash
cd .claude/examples

# Test 1 : Defaults uniquement
python config_tracking_example.py -S

# Test 2 : Avec YAML
python config_tracking_example.py --config config_example.yaml -S

# Test 3 : Avec ENV
MY_MODULE_URL=https://test.com python config_tracking_example.py -S

# Test 4 : Avec CLI
python config_tracking_example.py --url https://test.com --timeout 60 -S
```

### Étape 2 : Tester gitlab-clone

```bash
# Test 1 : Configuration par défaut
python gitlab_clone_with_tracking.py -S

# Test 2 : Avec token d'environnement
GITLAB_PRIVATE_TOKEN=test_token python gitlab_clone_with_tracking.py -S

# Test 3 : Avec arguments CLI
python gitlab_clone_with_tracking.py \
  --token cli_token \
  --username oauth2 \
  --output ./repos \
  --repositories https://gitlab.com/project.git \
  -S
```

### Étape 3 : Lire les démonstrations

```bash
# Ouvrir dans un éditeur Markdown
code DEMO_CONFIG_SOURCES.md
code DEMO_GITLAB_CLONE_CONFIG_SOURCES.md
```

---

## 📖 Par Cas d'Usage

### Cas 1 : Je veux comprendre le concept

**Fichiers à lire dans l'ordre :**
1. `README.md` - Comprendre `--show-config-sources`
2. `DEMO_CONFIG_SOURCES.md` - Voir des exemples concrets
3. Exécuter `python config_tracking_example.py -S`

### Cas 2 : Je veux intégrer dans mon module

**Fichiers à utiliser :**
1. `config_tracking_example.py` - Copier les classes ConfigTracker
2. `README.md` section "Intégration dans Vos Projets"
3. `.claude/GUIDELINES.md` section "Traçabilité de Configuration"

### Cas 3 : Je veux voir un exemple réel

**Fichiers à consulter :**
1. `gitlab_clone_with_tracking.py` - Code complet
2. `DEMO_GITLAB_CLONE_CONFIG_SOURCES.md` - Scénarios d'utilisation
3. Exécuter les tests de démonstration

### Cas 4 : Je veux debugger ma configuration

**Fichiers utiles :**
1. `DEMO_CONFIG_SOURCES.md` section "Debugging d'un Problème"
2. `DEMO_GITLAB_CLONE_CONFIG_SOURCES.md` section "Cas d'Erreurs Courantes"
3. Exécuter votre commande avec `-S`

### Cas 5 : Je veux valider mon CI/CD

**Fichiers à consulter :**
1. `DEMO_CONFIG_SOURCES.md` section "Validation CI/CD"
2. `DEMO_GITLAB_CLONE_CONFIG_SOURCES.md` section "Validation CI/CD"
3. Adapter le script de validation à votre pipeline

---

## 🔍 Recherche Rapide

### Je cherche...

**...un exemple d'utilisation** → `README.md`

**...comment intégrer dans mon code** → `config_tracking_example.py`

**...des scénarios de test** → `DEMO_CONFIG_SOURCES.md` ou `DEMO_GITLAB_CLONE_CONFIG_SOURCES.md`

**...la spécification complète** → `.claude/GUIDELINES.md` section "Traçabilité"

**...un cas d'usage spécifique** → Chercher dans `DEMO_*.md`

**...comment gérer les secrets** → Chercher "masked" ou "sensitive" dans les fichiers

**...comment debugger** → `DEMO_*_CONFIG_SOURCES.md` sections "Debugging" ou "Erreurs"

---

## ✅ Checklist d'Intégration

Avant d'intégrer `-S, --show-config-sources` dans votre module :

### Phase 1 : Préparation
- [ ] Lire `README.md` en entier
- [ ] Tester `config_tracking_example.py` avec les 5 scénarios
- [ ] Comprendre les classes `ConfigSource`, `ConfigValue`, `ConfigTracker`

### Phase 2 : Intégration
- [ ] Copier les classes dans votre module
- [ ] Modifier `load_config()` pour accepter `tracker`
- [ ] Ajouter `-S, --show-config-sources` au parser
- [ ] Tracker les defaults avec `ConfigSource.DEFAULT`
- [ ] Tracker les args CLI avec `ConfigSource.CLI`

### Phase 3 : Tests
- [ ] Test 1 : Defaults uniquement
- [ ] Test 2 : Avec YAML
- [ ] Test 3 : Avec ENV
- [ ] Test 4 : Avec CLI
- [ ] Test 5 : Hiérarchie complète

### Phase 4 : Validation
- [ ] Vérifier que les secrets sont masqués
- [ ] Vérifier la hiérarchie (CLI > YAML > ENV > Default)
- [ ] Documenter dans `--help`
- [ ] Ajouter des exemples dans la documentation

---

## 📊 Statistiques

**Nombre de fichiers** : 7 (3 docs, 2 Python, 1 YAML, 1 index)

**Lignes de code** :
- `config_tracking_example.py` : ~230 lignes
- `gitlab_clone_with_tracking.py` : ~300 lignes
- Total Python : ~530 lignes

**Lignes de documentation** :
- `README.md` : ~400 lignes
- `DEMO_CONFIG_SOURCES.md` : ~700 lignes
- `DEMO_GITLAB_CLONE_CONFIG_SOURCES.md` : ~800 lignes
- Total docs : ~1900 lignes

**Scénarios de test** : 15+ scénarios complets

**Cas d'usage documentés** : 8+

---

## 🔗 Liens Utiles

### Documentation Principale
- **`.claude/GUIDELINES.md`** : Spécification complète de la hiérarchie de configuration

### Exemples de Code
- **`config_tracking_example.py`** : Implémentation de référence
- **`gitlab_clone_with_tracking.py`** : Intégration réelle

### Démonstrations
- **`DEMO_CONFIG_SOURCES.md`** : wikisi-sync-api, piag-chat-query
- **`DEMO_GITLAB_CLONE_CONFIG_SOURCES.md`** : gitlab-clone

### Guides
- **`README.md`** : Guide d'utilisation et d'intégration

---

## 📞 Support

**Questions ?** Consultez :
1. `README.md` section "Questions Fréquentes"
2. `DEMO_*.md` sections "Cas d'Erreurs Courantes"
3. `.claude/GUIDELINES.md` pour les spécifications

**Problèmes ?**
- Vérifier que `-S` est bien ajouté au parser
- Vérifier que `ConfigTracker` est instancié
- Exécuter les tests de démonstration pour comparer

**Améliorations ?**
- Proposer de nouveaux exemples
- Ajouter des cas d'usage
- Documenter des patterns avancés

---

## 🎓 Prochaines Étapes

Après avoir exploré ces exemples :

1. **Intégrer dans votre module** en suivant le guide du `README.md`
2. **Tester avec vos données** en utilisant `-S`
3. **Documenter dans --help** les variables d'environnement supportées
4. **Créer un fichier .example** pour votre configuration YAML
5. **Valider en CI/CD** avec un script de test automatique

**Bonne intégration ! 🚀**
