# Configuration GitLab

Configuration pour le clonage automatique de repositories GitLab.

## 📋 Vue d'ensemble

Le module GitLab gère le clonage automatique de projets depuis une instance GitLab (auto-hébergée ou GitLab.com).

### Fonctionnalités

- 🔄 Clonage automatique de multiples repositories
- 📁 Organisation des projets clonés
- 🔑 Authentification par token GitLab
- 🌐 Support instances GitLab privées

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

### Exemple de résolution pour le token

```bash
# Défaut
token: "" (vide - non recommandé)

# ENV définit le token
export GITLAB_TOKEN=glpat-abc123xyz

# YAML avec substitution ENV
# config/gitlab.yaml:
gitlab:
  token: ${GITLAB_TOKEN}  # Utilise la variable ENV

# CLI override (⚠️ DANGEREUX - visible dans l'historique)
ambulon gitlab-clone --token glpat-override

# Résultat : glpat-override (CLI gagne, mais DÉCONSEILLÉ)
```

## 📄 Structure du fichier YAML

### Fichier complet

```yaml
# config/gitlab.yaml
gitlab:
  # URL de l'instance GitLab
  url: ${GITLAB_URL:-https://gitlab.example.com}

  # ⚠️ TOKEN GITLAB (CRITIQUE - NE JAMAIS COMMITER)
  # TOUJOURS utiliser ${GITLAB_TOKEN} pour référencer une variable ENV
  token: ${GITLAB_TOKEN}

  # Liste des projets à cloner
  projects:
    - group: mygroup
      name: project1
      branch: main

    - group: mygroup
      name: project2
      branch: develop

    - group: anothergroup
      name: lib-common
      branch: main

  # Répertoire de destination pour les clones
  workspace: ${GITLAB_WORKSPACE:-./workplace-ambulon/gitlab}

  # Options de clonage
  clone:
    # Depth du clone (0 = historique complet)
    depth: ${GITLAB_CLONE_DEPTH:-1}

    # Cloner les sous-modules
    submodules: ${GITLAB_CLONE_SUBMODULES:-false}

  logging:
    level: ${GITLAB_LOG_LEVEL:-info}
    log_to_file: ${GITLAB_LOG_TO_FILE:-true}
    log_file: ${GITLAB_LOG_FILE:-./gitlab-clone.log}
```

### Fichier minimal

```yaml
# config/gitlab.yaml (minimal)
gitlab:
  url: ${GITLAB_URL}
  token: ${GITLAB_TOKEN}  # ⚠️ TOUJOURS via ENV
  projects:
    - group: mygroup
      name: myproject
```

## 🔐 Token GitLab (CRITIQUE)

### ⚠️ Sécurité du token

Le token GitLab est **CRITIQUE** car il donne accès à vos repositories privés.

#### ❌ CE QU'IL NE FAUT **JAMAIS** FAIRE

```yaml
# ❌ DANGER : Token en clair dans le fichier
gitlab:
  token: glpat-abc123xyz456  # NE JAMAIS FAIRE ÇA
```

```bash
# ❌ DANGER : Token dans la ligne de commande (historique bash)
ambulon gitlab-clone --token glpat-abc123xyz456
```

```bash
# ❌ DANGER : Token dans un fichier versionné
echo "GITLAB_TOKEN=glpat-abc123xyz456" >> .env
git add .env
git commit -m "add config"  # ❌ Le token est maintenant dans git !
```

#### ✅ CE QU'IL FAUT FAIRE

```bash
# ✅ BON : Définir la variable d'environnement
export GITLAB_TOKEN=glpat-abc123xyz456

# ✅ BON : Référencer la variable dans le YAML
# config/gitlab.yaml
gitlab:
  token: ${GITLAB_TOKEN}
```

```bash
# ✅ BON : Utiliser un fichier .env local (gitignored)
# .env
GITLAB_TOKEN=glpat-abc123xyz456

# .gitignore
.env
```

```bash
# ✅ BON : Utiliser un gestionnaire de secrets
# Vault, AWS Secrets Manager, etc.
export GITLAB_TOKEN=$(vault read -field=token secret/gitlab)
```

### Obtenir un token GitLab

1. **GitLab.com ou instance privée** :
   - Aller sur : https://gitlab.example.com/-/profile/personal_access_tokens
   - Cliquer : "Add new token"
   - Nom : `ambulon-clone`
   - Scopes : Cocher `read_repository`
   - Expiration : Définir une date (recommandé : 90 jours)
   - Générer et **copier immédiatement** (ne sera plus affiché)

2. **Stocker de manière sécurisée** :
   ```bash
   # Linux/macOS - ajouter à ~/.bashrc ou ~/.zshrc
   export GITLAB_TOKEN="glpat-votre-token-ici"

   # Ou utiliser un gestionnaire de mots de passe
   ```

3. **Vérifier** :
   ```bash
   # Vérifier que le token est défini
   echo ${GITLAB_TOKEN:0:10}...  # Affiche seulement le début

   # Tester avec GitLab
   curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        "https://gitlab.example.com/api/v4/user"
   ```

### Rotation des tokens

**Bonne pratique** : Régénérer les tokens régulièrement

```bash
# 1. Créer un nouveau token sur GitLab
# 2. Mettre à jour la variable ENV
export GITLAB_TOKEN=glpat-nouveau-token

# 3. Tester
ambulon gitlab-clone --check-config

# 4. Révoquer l'ancien token sur GitLab
```

## 🔐 Variables d'environnement

### Variables critiques (sensibles)

| Variable | Description | Exemple | Sensibilité |
|----------|-------------|---------|-------------|
| `GITLAB_TOKEN` | Token d'accès personnel | `glpat-abc123xyz` | 🔴 **CRITIQUE** |

### Variables optionnelles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `GITLAB_URL` | URL de l'instance | `https://gitlab.example.com` |
| `GITLAB_WORKSPACE` | Répertoire de destination | `./workplace-ambulon/gitlab` |
| `GITLAB_CLONE_DEPTH` | Profondeur du clone | `1` |
| `GITLAB_CLONE_SUBMODULES` | Cloner les sous-modules | `false` |
| `GITLAB_LOG_LEVEL` | Niveau de log | `info` |

### Définir les variables

**Linux/macOS :**
```bash
export GITLAB_URL="https://gitlab.mycompany.com"
export GITLAB_TOKEN="glpat-your-token-here"
export GITLAB_WORKSPACE="./projects"
```

**Windows (PowerShell) :**
```powershell
$env:GITLAB_URL = "https://gitlab.mycompany.com"
$env:GITLAB_TOKEN = "glpat-your-token-here"
$env:GITLAB_WORKSPACE = ".\projects"
```

## 🖥️ Arguments CLI

```bash
# URL de l'instance GitLab
--gitlab-url URL

# Token d'authentification (⚠️ DÉCONSEILLÉ - utiliser ENV)
--token TOKEN

# Workspace de destination
--workspace DIR

# Diagnostic
-S, --show-config-sources
--check-config
```

## 📊 Diagnostic de configuration

### Vérifier la configuration (avec masquage du token)

```bash
ambulon gitlab-clone -S
```

**Sortie exemple :**
```
Configuration Sources Report - gitlab-clone
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Parameter                  Value                          Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
gitlab.url                https://gitlab.example.com     YAML File
gitlab.token              ****** (masked)                Environment
gitlab.workspace          ./workplace-ambulon/gitlab     Default
gitlab.clone.depth        1                              Default
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ WARNINGS:
  • gitlab.token comes from Environment (recommended for security)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Vérification rapide

```bash
ambulon gitlab-clone --check-config
```

## 📝 Exemples pratiques

### Exemple 1 : Développement local

```yaml
# config/gitlab.dev.yaml
gitlab:
  url: https://gitlab.dev.mycompany.com
  token: ${GITLAB_TOKEN}  # ⚠️ TOUJOURS via ENV
  workspace: ./dev-projects
  projects:
    - group: team-dev
      name: backend-api
      branch: develop
```

```bash
export GITLAB_TOKEN="glpat-dev-token"
ambulon gitlab-clone --config config/gitlab.dev.yaml
```

### Exemple 2 : Production

```yaml
# config/gitlab.prod.yaml
gitlab:
  url: https://gitlab.mycompany.com
  token: ${GITLAB_TOKEN}  # ⚠️ TOUJOURS via ENV
  workspace: /opt/projects
  clone:
    depth: 0  # Historique complet
    submodules: true
  projects:
    - group: prod
      name: main-app
      branch: main
    - group: prod
      name: libs
      branch: release
```

```bash
export GITLAB_TOKEN=$(vault read -field=token secret/gitlab/prod)
ambulon gitlab-clone --config config/gitlab.prod.yaml
```

### Exemple 3 : CI/CD

```bash
# .gitlab-ci.yml
clone_repos:
  script:
    - export GITLAB_TOKEN=$CI_JOB_TOKEN
    - export GITLAB_WORKSPACE=$CI_PROJECT_DIR/cloned
    - ambulon gitlab-clone
```

## 🔒 Checklist de sécurité

Avant de lancer `gitlab-clone`, vérifier :

- [ ] Le token GitLab est défini dans une **variable d'environnement**
- [ ] Le token n'est **PAS** dans le fichier YAML en clair
- [ ] Le token n'est **PAS** passé via argument CLI
- [ ] Le fichier `.env` (si utilisé) est dans `.gitignore`
- [ ] Le token a les **permissions minimales** (`read_repository` uniquement)
- [ ] Le token a une **date d'expiration** définie
- [ ] Les fichiers de config ne sont **PAS** commitées avec des secrets

### Audit rapide

```bash
# Vérifier qu'aucun token n'est dans les fichiers versionnés
git grep -i "glpat-" config/
git grep -i "token.*=" config/*.yaml

# Doit retourner : config/gitlab.yaml:  token: ${GITLAB_TOKEN}
# NE DOIT PAS retourner de token en clair
```

## 🐛 Résolution de problèmes

### Token non détecté

```bash
# Vérifier la variable
echo ${GITLAB_TOKEN:0:10}...  # Affiche seulement le début

# Vérifier la configuration
ambulon gitlab-clone -S | grep token

# Si vide, définir
export GITLAB_TOKEN="glpat-your-token"
```

### Erreur d'authentification

```bash
# Tester le token directement
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
     "https://gitlab.example.com/api/v4/user"

# Si erreur 401 : token invalide ou expiré
# → Régénérer un nouveau token
```

### Token exposé accidentellement

**⚠️ ACTION IMMÉDIATE REQUISE :**

1. **Révoquer le token** immédiatement sur GitLab
2. **Générer un nouveau token**
3. **Mettre à jour** la variable d'environnement
4. **Vérifier l'historique git** :
   ```bash
   # Chercher dans l'historique
   git log -p | grep -i "glpat-"

   # Si trouvé, nettoyer l'historique (DANGEREUX)
   # Contacter votre admin GitLab
   ```

## 🔗 Voir aussi

- [Configuration générale](README.md)
- [Configuration PIAG](piag.md)
- [Configuration WikiSI](wikisi.md)
- [Sécurité des tokens](../securite/tokens.md) (TODO)
