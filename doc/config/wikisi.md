# Configuration WikiSI

Configuration pour la synchronisation avec l'API WikiSI.

## 📋 Vue d'ensemble

Le module WikiSI gère la synchronisation des données du parc applicatif depuis l'API WikiSI.

### Fonctionnalités

- 📥 Synchronisation énumérations et applications
- 🤖 Génération formats IA-ready
- 📄 Export JSON et Markdown
- 🔄 Mise à jour automatique des données

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
token: "" (vide - erreur si l'API nécessite auth)

# ENV définit le token
export WIKISI_API_TOKEN="Bearer xyz789..."

# YAML avec substitution ENV
# config/wikisi.yaml:
wikisi:
  api:
    token: ${WIKISI_API_TOKEN}  # Utilise la variable ENV

# CLI override (⚠️ DANGEREUX - visible dans l'historique)
ambulon wikisi-sync-api --api-token "Bearer override..."

# Résultat : "Bearer override..." (CLI gagne, mais DÉCONSEILLÉ)
```

## 📄 Structure du fichier YAML

### Fichier complet

```yaml
# config/wikisi.yaml
wikisi:
  api:
    # URL de l'API WikiSI
    url: ${WIKISI_API_URL:-https://wikisi.e2.rie.gouv.fr/wikisi/api}

    # ⚠️ TOKEN WIKISI (CRITIQUE - NE JAMAIS COMMITER)
    # TOUJOURS utiliser ${WIKISI_API_TOKEN} pour référencer une variable ENV
    token: ${WIKISI_API_TOKEN}

    # User-Agent pour les requêtes
    user_agent: ${WIKISI_API_USER_AGENT:-Ambulon Wiki SI Sync API/1.0}

    # Limite d'éléments par page pour les requêtes paginées
    page_limit: ${WIKISI_API_PAGE_LIMIT:-25}

  output:
    # Répertoire de sortie pour les fichiers JSON
    directory: ${WIKISI_OUTPUT_DIR:-./wikisi-data}

    # Noms des fichiers de sortie
    enumerations_file: ${WIKISI_ENUMERATIONS_FILE:-enumerations.json}
    applications_file: ${WIKISI_APPLICATIONS_FILE:-applications.json}
    applications_ia_file: ${WIKISI_APPLICATIONS_IA_FILE:-applicationsIA.json}
    applications_ia_mini_file: ${WIKISI_APPLICATIONS_IA_MINI_FILE:-applicationsIA_mini.json}

  logging:
    # Niveau de journalisation
    level: ${WIKISI_LOG_LEVEL:-info}

    # Activer la journalisation vers un fichier
    log_to_file: ${WIKISI_LOG_TO_FILE:-true}

    # Chemin du fichier de journalisation
    log_file: ${WIKISI_LOG_FILE:-./wikisi-sync-api.log}
```

### Fichier minimal

```yaml
# config/wikisi.yaml (minimal)
wikisi:
  api:
    url: ${WIKISI_API_URL}
    token: ${WIKISI_API_TOKEN}  # ⚠️ TOUJOURS via ENV
```

## 🔐 Token WikiSI (CRITIQUE)

### ⚠️ Sécurité du token

Le token WikiSI donne accès aux données du parc applicatif de l'entreprise.

#### ❌ CE QU'IL NE FAUT **JAMAIS** FAIRE

```yaml
# ❌ DANGER : Token en clair dans le fichier
wikisi:
  api:
    token: Bearer abc123xyz456...  # NE JAMAIS FAIRE ÇA
```

```bash
# ❌ DANGER : Token dans la ligne de commande
ambulon wikisi-sync-api --api-token "Bearer xyz..."
```

```bash
# ❌ DANGER : Token dans un fichier versionné
cat >> config/wikisi.yaml << EOF
wikisi:
  api:
    token: Bearer secret123  # ❌ DANGEREUX
EOF
git add config/wikisi.yaml
git commit  # ❌ Token maintenant dans git !
```

#### ✅ CE QU'IL FAUT FAIRE

```bash
# ✅ BON : Définir la variable d'environnement
export WIKISI_API_TOKEN="Bearer your-token-here"

# ✅ BON : Référencer la variable dans le YAML
# config/wikisi.yaml
wikisi:
  api:
    token: ${WIKISI_API_TOKEN}
```

```bash
# ✅ BON : Utiliser un fichier .env local (gitignored)
# .env
WIKISI_API_TOKEN="Bearer your-token-here"

# .gitignore
.env
```

```bash
# ✅ BON : Utiliser un gestionnaire de secrets d'entreprise
export WIKISI_API_TOKEN=$(vault read -field=token secret/wikisi)
```

### Obtenir un token WikiSI

1. **Contacter l'administrateur WikiSI** de votre entreprise
2. **Demander un token d'API** avec les droits :
   - Lecture des énumérations
   - Lecture des applications
3. **Stocker de manière sécurisée** :
   ```bash
   # Linux/macOS - ajouter à ~/.bashrc ou ~/.zshrc
   export WIKISI_API_TOKEN="Bearer votre-token-ici"

   # Recharger la config
   source ~/.bashrc
   ```

4. **Vérifier** :
   ```bash
   # Vérifier que le token est défini (masqué)
   echo ${WIKISI_API_TOKEN:0:15}...  # Affiche seulement "Bearer xyz..."

   # Tester avec WikiSI
   ambulon wikisi-sync-api --check-config
   ```

### Format du token WikiSI

Le token WikiSI est généralement au format :

```
Bearer <token_value>
```

**Exemple** :
```bash
export WIKISI_API_TOKEN="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Expiration et rotation

- **Vérifier la date d'expiration** du token auprès de votre admin
- **Régénérer avant expiration** pour éviter les interruptions
- **Tester le nouveau token** avant de révoquer l'ancien

```bash
# 1. Obtenir nouveau token
# 2. Définir temporairement
export WIKISI_API_TOKEN_NEW="Bearer new-token..."

# 3. Tester
WIKISI_API_TOKEN=$WIKISI_API_TOKEN_NEW ambulon wikisi-sync-api --check-config

# 4. Si OK, remplacer définitivement
export WIKISI_API_TOKEN="$WIKISI_API_TOKEN_NEW"
```

## 🔐 Variables d'environnement

### Variables critiques (sensibles)

| Variable | Description | Exemple | Sensibilité |
|----------|-------------|---------|-------------|
| `WIKISI_API_TOKEN` | Token d'authentification API | `Bearer abc...` | 🔴 **CRITIQUE** |

### Variables optionnelles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `WIKISI_API_URL` | URL de l'API | `https://wikisi.e2.rie.gouv.fr/wikisi/api` |
| `WIKISI_API_USER_AGENT` | User-Agent HTTP | `Ambulon Wiki SI Sync API/1.0` |
| `WIKISI_API_PAGE_LIMIT` | Limite pagination | `25` |
| `WIKISI_OUTPUT_DIR` | Répertoire de sortie | `./wikisi-data` |
| `WIKISI_LOG_LEVEL` | Niveau de log | `info` |

### Définir les variables

**Linux/macOS :**
```bash
export WIKISI_API_URL="https://wikisi.e2.rie.gouv.fr/wikisi/api"
export WIKISI_API_TOKEN="Bearer your-token-here"
export WIKISI_OUTPUT_DIR="./data"
```

**Windows (PowerShell) :**
```powershell
$env:WIKISI_API_URL = "https://wikisi.e2.rie.gouv.fr/wikisi/api"
$env:WIKISI_API_TOKEN = "Bearer your-token-here"
$env:WIKISI_OUTPUT_DIR = ".\data"
```

## 🖥️ Arguments CLI

```bash
# URL de l'API
--api-url URL

# Token d'authentification (⚠️ DÉCONSEILLÉ - utiliser ENV)
--api-token TOKEN

# User-Agent
--api-user-agent STRING

# Limite de pagination
--api-page-limit N

# Répertoire de sortie
--output-dir DIR

# Diagnostic
-S, --show-config-sources
--check-config

# Verbosité
-v, --verbose
-q, --quiet
```

## 📊 Diagnostic de configuration

### Vérifier la configuration (avec masquage du token)

```bash
ambulon wikisi-sync-api -S
```

**Sortie exemple :**
```
Configuration Sources Report - wikisi-sync-api
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Parameter                         Value                          Source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
wikisi.api.url                   https://wikisi.e2.rie...       Default
wikisi.api.token                 ****** (masked)                Environment
wikisi.api.page_limit            25                             Default
wikisi.output.directory          ./wikisi-data                  Default
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ WARNINGS:
  • wikisi.api.token comes from Environment (recommended for security)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Vérification rapide

```bash
ambulon wikisi-sync-api --check-config
```

## 🌐 Accès réseau VPN

⚠️ **Important** : L'API WikiSI est généralement accessible uniquement via **VPN d'entreprise**.

### Vérifier la connectivité

```bash
# Tester la connexion à WikiSI (nécessite VPN)
curl -I https://wikisi.e2.rie.gouv.fr

# Si erreur de résolution DNS :
# → Connectez-vous au VPN

# Si erreur 401 (Unauthorized) :
# → Vérifier le token
```

### Workflow avec VPN

1. **Connecter au VPN**
2. **Vérifier la connexion** : `curl -I https://wikisi.e2.rie.gouv.fr`
3. **Exécuter la synchronisation** : `ambulon wikisi-sync-api`

## 📝 Exemples pratiques

### Exemple 1 : Synchronisation simple

```yaml
# config/wikisi.yaml
wikisi:
  api:
    url: ${WIKISI_API_URL}
    token: ${WIKISI_API_TOKEN}  # ⚠️ TOUJOURS via ENV
  output:
    directory: ./wikisi-data
```

```bash
# Connecter au VPN
# Définir le token
export WIKISI_API_TOKEN="Bearer your-token"

# Synchroniser
ambulon wikisi-sync-api
```

### Exemple 2 : Sortie personnalisée

```bash
export WIKISI_API_TOKEN="Bearer token123"
export WIKISI_OUTPUT_DIR="./data/wikisi"
export WIKISI_LOG_LEVEL="debug"

ambulon wikisi-sync-api --verbose
```

### Exemple 3 : CI/CD

```yaml
# .gitlab-ci.yml
sync_wikisi:
  only:
    - schedules  # Exécution planifiée (ex: chaque nuit)
  script:
    - openvpn --config vpn.conf &  # Connexion VPN
    - sleep 10  # Attendre connexion VPN
    - export WIKISI_API_TOKEN=$CI_WIKISI_TOKEN
    - ambulon wikisi-sync-api --output-dir $CI_PROJECT_DIR/data
  artifacts:
    paths:
      - data/wikisi-data/
```

## 🔒 Checklist de sécurité

Avant de lancer `wikisi-sync-api`, vérifier :

- [ ] Le token WikiSI est défini dans une **variable d'environnement**
- [ ] Le token n'est **PAS** dans le fichier YAML en clair
- [ ] Le token n'est **PAS** passé via argument CLI
- [ ] Le fichier `.env` (si utilisé) est dans `.gitignore`
- [ ] Le **VPN est connecté** (si requis)
- [ ] Les fichiers de config ne sont **PAS** commitées avec des secrets
- [ ] Les fichiers de sortie JSON ne contiennent **PAS** de données sensibles

### Audit rapide

```bash
# Vérifier qu'aucun token n'est dans les fichiers versionnés
git grep -i "bearer" config/
git grep -i "token.*=" config/*.yaml

# Doit retourner : config/wikisi.yaml:  token: ${WIKISI_API_TOKEN}
# NE DOIT PAS retourner de token en clair
```

## 🐛 Résolution de problèmes

### Token non détecté

```bash
# Vérifier la variable
echo ${WIKISI_API_TOKEN:0:15}...  # Affiche seulement "Bearer xyz..."

# Vérifier la configuration
ambulon wikisi-sync-api -S | grep token

# Si vide, définir
export WIKISI_API_TOKEN="Bearer your-token"
```

### Erreur de connexion (VPN requis)

```bash
# Erreur typique
# ConnectionError: Failed to resolve 'wikisi.e2.rie.gouv.fr'

# Solution :
# 1. Connecter au VPN
# 2. Vérifier : ping wikisi.e2.rie.gouv.fr
# 3. Relancer : ambulon wikisi-sync-api
```

### Token invalide ou expiré

```bash
# Tester le token
curl -H "Authorization: $WIKISI_API_TOKEN" \
     "https://wikisi.e2.rie.gouv.fr/wikisi/api/enumerations"

# Si erreur 401 ou 403 :
# → Contacter votre admin WikiSI pour régénérer le token
```

### Token exposé accidentellement

**⚠️ ACTION IMMÉDIATE REQUISE :**

1. **Contacter votre administrateur WikiSI** immédiatement
2. **Demander la révocation** du token exposé
3. **Obtenir un nouveau token**
4. **Mettre à jour** la variable d'environnement
5. **Vérifier l'historique git** :
   ```bash
   # Chercher dans l'historique
   git log -p | grep -i "bearer"

   # Si trouvé, nettoyer l'historique
   # Contacter votre admin sécurité
   ```

## 🔗 Voir aussi

- [Configuration générale](README.md)
- [Configuration PIAG](piag.md)
- [Configuration GitLab](gitlab.md)
- [Sécurité des tokens](../securite/tokens.md) (TODO)
- [Guide WikiSI](../wikisi/README.md) (TODO)
