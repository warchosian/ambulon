# QuickStart RAG SIREINES - 5 Commandes

**Date** : 2026-03-22
**Version** : 3.1.0+

---

## 🎯 Workflow en 5 Commandes

Recréation complète de la collection RAG SIREINES et interrogation sur l'architecture DAT/C4.

---

## ⚡ Commande 0 : Lister les collections existantes

```bash
ambulon piag-rag-collection-list
```

**Résultat** :
- Affiche toutes les collections du projet
- Permet de vérifier si `PNM3_SIREINES` existe déjà avant de la supprimer
- Liste les IDs et descriptions
- **Décision** : Si `PNM3_SIREINES` existe, passez à la commande 1 pour la supprimer. Sinon, passez directement à la commande 2.

**Exemple de sortie** :
```
Collections disponibles dans le projet PnuQzUEmwRDkxZPX:

1. PNM3_SIREINES
   ID: abc123def456
   Description: Documentation complète SIREINES
   Documents: 31
   Créée le: 2026-03-20T10:00:00

2. test_collection
   ID: xyz789uvw123
   Description: Collection de test
   Documents: 5
   Créée le: 2026-03-15T14:30:00

Total: 2 collections
```

---

## ⚡ Commande 1 : Supprimer l'ancienne collection

```bash
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES
```

**Résultat** :
- Collection `PNM3_SIREINES` supprimée (si elle existait)
- Tous les documents associés supprimés

**Note** : Cette commande échouera si la collection n'existe pas (OK, continuez)

---

## ⚡ Commande 2 : Recréer la collection avec tous les documents

```batch
REM Windows : utiliser ^ pour continuer sur plusieurs lignes
ambulon piag-rag-create ^
  --collection-name PNM3_SIREINES ^
  --description "Documentation complète SIREINES : DAT, C4, Composants, Wiki" ^
  --directory applications/PNM3_SIREINES.rag ^
  --extensions md,pdf
```

**Résultat** :
- Collection `PNM3_SIREINES` créée
- Tous les fichiers `.md` et `.pdf` de `applications/PNM3_SIREINES.rag/` uploadés
- Indexation automatique lancée

**⏳ IMPORTANT : Attendre 60-120 secondes pour l'indexation**

```bash
# Attendre l'indexation
sleep 60
```

---

## ⚡ Commande 3 : Créer les chunks sur "Architecture, DAT"

```batch
REM Windows : utiliser ^ pour continuer sur plusieurs lignes
ambulon piag-rag-search ^
  --collection-name PNM3_SIREINES ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --timeout 10s ^
  -o piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
```

**Résultat** :
- Recherche RAG sur les mots-clés "Architecture, DAT"
- 10 chunks les plus pertinents récupérés
- Timeout : **10s** (10000ms) pour requêtes longues
- Sauvegardés dans `piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json`

**Formats de timeout acceptés** :
- `10s` = 10 secondes (recommandé pour lisibilité)
- `10000ms` = 10000 millisecondes
- `10000` = 10000 millisecondes (par défaut si pas d'unité)
- `2m` = 2 minutes

---

## ⚡ Commande 4 : Lancer la recherche CHAT avec le prompt DAT C4

```batch
REM Sous Windows/DOS, utiliser ^ pour les lignes multiples
ambulon piag-chat-query ^
  --question-file .claude/prompts/prompt.dat_c4model.md ^
  --chunks piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json ^
  --timeout 20m ^
  --max-retries 5 ^
  --retry-delay 1m ^
  -o piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
```

**Résultat** :
- Question chargée depuis `.claude/prompts/prompt.dat_c4model.md`
- Réponse générée avec les chunks récupérés
- Timeout : **20m** (20 minutes) par tentative pour génération longue
- **Retry automatique** : Jusqu'à 5 tentatives en cas d'erreur 504 Gateway Timeout
- Délai entre tentatives : **1m** (1 minute)
- Sauvegardée dans `piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md`

**⚠️ IMPORTANT - Retry automatique** :
L'API PIAG peut renvoyer des erreurs 504 Gateway Timeout (~50 secondes) dues à :
- Serveur non prêt (cold start)
- Charge élevée sur le serveur
- Cache non initialisé

Après plusieurs tentatives, le serveur est "chaud" et répond rapidement (<1s).
La commande **réessaie automatiquement jusqu'à 5 fois** avec 1 minute d'attente entre chaque tentative.

**Note** : Sous Windows, utiliser `^` au lieu de `\` pour continuer les commandes sur plusieurs lignes

**Formats de timeout acceptés** :
- `20m` = 20 minutes (recommandé pour génération longue)
- `1m` = 1 minute
- `60s` = 60 secondes
- `60000ms` = 60000 millisecondes
- `60000` = 60000 millisecondes (par défaut si pas d'unité)

---

## 📋 Script Complet Windows (Copier-Coller)

```batch
@echo off
REM Workflow complet RAG SIREINES en 5 commandes (Windows)

echo === WORKFLOW RAG SIREINES - 5 COMMANDES ===
echo.

REM 0. Lister les collections existantes
echo 0/5 - Liste des collections existantes...
ambulon piag-rag-collection-list
echo.
pause
echo.

REM 1. Supprimer l'ancienne collection
echo 1/5 - Suppression collection PNM3_SIREINES...
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES 2>nul || echo Collection n'existait pas (OK)
echo.

REM 2. Recréer la collection avec documents
echo 2/5 - Création collection + upload documents...
ambulon piag-rag-create ^
  --collection-name PNM3_SIREINES ^
  --description "Documentation complète SIREINES : DAT, C4, Composants, Wiki" ^
  --directory applications/PNM3_SIREINES.rag ^
  --extensions md,pdf
echo.

REM Attendre indexation
echo Attente indexation (60 secondes)...
timeout /t 60 /nobreak
echo.

REM 3. Créer les chunks sur "Architecture, DAT"
echo 3/5 - Création chunks Architecture/DAT (timeout 10s)...
if not exist chunks mkdir chunks
ambulon piag-rag-search ^
  --collection-name PNM3_SIREINES ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --timeout 10s ^
  -o piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
echo.

REM 4. Générer la réponse CHAT
echo 4/5 - Génération réponse CHAT (timeout 20m, max 5 retries, délai 1m)...
if not exist reponses mkdir reponses
ambulon piag-chat-query ^
  --question-file .claude/prompts/prompt.dat_c4model.md ^
  --chunks .json ^piag_workplace/chunks/chunk_PNM3_SIREINES_dat_c4model
  --timeout 20m ^
  --max-retries 5 ^
  --retry-delay 1m ^
  -o piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
echo.

REM 5. Vérification finale
echo 5/5 - Vérification finale...
echo Collections après workflow:
ambulon piag-rag-collection-list | findstr PNM3_SIREINES
echo.

echo ✅ WORKFLOW TERMINÉ
echo.
echo Fichiers générés:
echo   - piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
echo   - piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
echo.
echo Lire la réponse:
echo   type reponses\reponse_dat_c4model.md
pause
```

**Sauvegarder ce script** :
```batch
REM Créer le fichier workflow_rag_sireines_5cmd.bat
copy con workflow_rag_sireines_5cmd.bat
[... copier le contenu ci-dessus ...]
^Z

REM Exécuter
workflow_rag_sireines_5cmd.bat
```

---

## 📂 Structure des fichiers

**Avant exécution** (pré-requis) :
```
ambulon/
├── .claude/
│   └── prompts/
│       └── prompt.dat_c4model.md       ← Fichier question (doit exister)
├── applications/
│   └── sireines.rag/                   ← Documents sources (*.md, *.pdf)
└── config/
    └── piag.yaml                       ← Configuration tokens
```

**Après exécution** :
```
ambulon/
└── piag_workplace/
    ├── chunks/
    │   └── chunk.PNM3_SIREINES.dat_c4model.json   ← Créé par commande 3
    └── responses/
        └── response.PNM3_SIREINES.dat_c4model.md  ← Créé par commande 4
```

---

## 🔧 Configuration Requise (config/piag.yaml)

```yaml
piag:
  rag:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
    security:
      token: "eyJhbGci..."  # Token JWT RAG
    project:
      project_id: "PnuQzUEmwRDkxZPX"

  chat:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions"
    security:
      token: "sk-iyksvRDQanhNZ6O7MJCQbA"  # Token LiteLLM
    model: "mte-api-piag-mistral-medium-latest"
```

---

## ⚠️ Points d'attention

### 1. Timeout : Formats acceptés

**Nouveauté** : Vous pouvez maintenant utiliser des suffixes pour plus de lisibilité !

**Formats acceptés** :
| Format | Équivalent | Usage |
|--------|-----------|-------|
| `10s` | 10 secondes | ✅ Recommandé (lisible) |
| `10000ms` | 10000 millisecondes | ✅ OK (explicite) |
| `10000` | 10000 millisecondes | ✅ OK (par défaut) |
| `2m` | 2 minutes | ✅ Recommandé (lisible) |

**Valeurs de référence** :
- `10s` = 10 secondes (rapide, test)
- `30s` = 30 secondes (standard)
- `1m` = 1 minute (recommandé CHAT)
- `2m` = 2 minutes (recommandé RAG)
- `10m` = 10 minutes (maximum autorisé)

**Valeur par défaut (sans --timeout)** :
- RAG : `2m` (2 minutes)
- CHAT : `1m` (1 minute)

**Exemples** :
```bash
# Format avec suffixe (recommandé)
--timeout 10s
--timeout 1m
--timeout 30s

# Format millisecondes explicite
--timeout 10000ms
--timeout 60000ms

# Format millisecondes implicite (ancien format toujours supporté)
--timeout 10000
--timeout 60000
```

### 2. Attente obligatoire entre commande 2 et 3

**IMPORTANT** : L'indexation prend du temps !

```bash
# Après la commande 2, ATTENDRE :
sleep 60  # Minimum 60 secondes
# ou
sleep 120 # Recommandé pour gros volumes
```

Sans attente, la commande 3 ne trouvera aucun chunk.

### 2. Fichier question doit exister

Vérifier avant d'exécuter :
```bash
ls -lh .claude/prompts/prompt.dat_c4model.md
```

**Si le fichier n'existe pas**, créer un fichier question :
```bash
mkdir -p .claude/prompts

cat > .claude/prompts/prompt.dat_c4model.md <<'EOF'
# Analyse Architecture SIREINES - DAT et C4 Model

À partir des extraits du Dossier d'Architecture Technique (DAT) et du modèle C4, fournis une analyse détaillée :

## 1. Architecture Globale
- Pattern architectural utilisé
- Frameworks principaux (Vertigo, Struts, etc.)
- Technologies de base

## 2. Composants C4 Level 3
- Liste des composants identifiés
- Responsabilités de chaque composant
- Relations et dépendances

## 3. Technologies de Persistance
- Bases de données (PostgreSQL, Elasticsearch)
- Justification des choix
- Configuration

## 4. Décisions Architecturales (ADR)
- ADR documentés
- Justifications techniques
- Trade-offs

Base ta réponse UNIQUEMENT sur les extraits fournis.
EOF
```

### 3. Créer les répertoires manquants

```bash
# Avant d'exécuter les commandes
mkdir -p chunks
mkdir -p reponses
mkdir -p .claude/prompts
```

---

## 🐛 Dépannage

### Erreur : "Collection n'existe pas" (Commande 1)

**Normal** : Si c'est la première fois, la collection n'existe pas encore.

```bash
# Ignorer l'erreur et continuer avec commande 2
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES 2>/dev/null || true
```

### Erreur : "Aucun chunk trouvé" (Commande 3)

**Cause** : Indexation pas terminée

**Solution** :
```bash
# Attendre plus longtemps
sleep 120

# Vérifier les documents indexés
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES

# Réessayer la recherche (Windows)
ambulon piag-rag-search ^
  --collection-name PNM3_SIREINES ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --timeout 10s ^
  -o piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
```

### Erreur : "Timeout" (Commande 3 ou 4)

**Cause** : Timeout trop court pour gros volumes

**Solution** : Augmenter le timeout avec suffixes
```batch
REM Commande 3 avec timeout de 30 secondes (Windows)
ambulon piag-rag-search ^
  --collection-name PNM3_SIREINES ^
  --query "Architecture, DAT" ^
  --top-k 10 ^
  --timeout 30s ^
  -o piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json

REM Commande 4 avec timeout de 20 minutes et retry automatique (Windows)
ambulon piag-chat-query ^
  --question-file .claude/prompts/prompt.dat_c4model.md ^
  --chunks piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json ^
  --timeout 20m ^
  --max-retries 5 ^
  --retry-delay 1m ^
  -o piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
```

**Erreur "timeout doesn't fit into C timeval"** :
- Cause : Valeur trop grande (> 10m)
- Solution : Utilisez maximum `10m` (10 minutes)

**Erreur "Format de timeout invalide"** :
- Cause : Suffixe incorrect (ex: `10sec`, `2min`)
- Solution : Utilisez seulement `ms`, `s` ou `m` (ex: `10s`, `2m`)

### Erreur : "Fichier question introuvable" (Commande 4)

**Cause** : `.claude/prompts/prompt.dat_c4model.md` n'existe pas

**Solution** : Créer le fichier (voir section "Points d'attention #2")

### Erreur : "Document existe déjà" (Commande 2)

**Cause** : Collection pas complètement supprimée

**Solution** :
```bash
# Forcer la suppression
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES --force

# Ou utiliser --if-exists dans piag-rag-create (Windows)
ambulon piag-rag-create ^
  --collection-name PNM3_SIREINES ^
  --description "..." ^
  --directory applications/PNM3_SIREINES.rag ^
  --extensions md,pdf ^
  --if-exists replace
```

---

## 📊 Vérifications

### Après commande 2 (Collection créée)
```bash
ambulon piag-rag-collection-get --collection-name PNM3_SIREINES
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES | grep "Total:"
```

**Attendu** : `Total: 31 documents` (ou votre nombre de fichiers)

### Après commande 3 (Chunks créés)
```bash
ls -lh piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json
cat piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json | jq '.chunks | length'
```

**Attendu** : `10` chunks

### Après commande 4 (Réponse générée)
```bash
ls -lh piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
head -n 30 piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
```

**Attendu** : Fichier avec réponse structurée référençant les extraits

---

## 🚀 Exécution Rapide (Ligne de commande unique)

```batch
REM Ligne unique avec timeouts : 10s (RAG) et 20m (CHAT avec retry) - Windows
ambulon piag-rag-collection-list && echo. && ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES 2>nul || echo OK && ambulon piag-rag-create --collection-name PNM3_SIREINES --description "Documentation SIREINES" --directory applications/PNM3_SIREINES.rag --extensions md,pdf && timeout /t 60 /nobreak && mkdir chunks reponses 2>nul & ambulon piag-rag-search --collection-name PNM3_SIREINES --query "Architecture, DAT" --top-k 10 --timeout 10s -o piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json && ambulon piag-chat-query --question-file .claude/prompts/prompt.dat_c4model.md --chunks piag_workplace/chunks/chunk.PNM3_SIREINES.dat_c4model.json --timeout 20m --max-retries 5 --retry-delay 1m -o piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md && echo ✅ TERMINÉ - Voir: piag_workplace/responses/response.PNM3_SIREINES.dat_c4model.md
```

---

## 📚 Documentation

- **Guide détaillé** : `doc/GUIDE_CREATION_RAG_PNM3_SIREINES.md` (9 étapes)
- **Workflow 2 phases** : `doc/PIAG_WORKFLOW_RAG_CHAT.md`
- **API RAG** : `doc/API_PIAG_APPEL_RAG.md`
- **API CHAT** : `doc/API_PIAG_APPEL_CHAT.md`

---

**Auteur** : Équipe Ambulon
**Dernière mise à jour** : 2026-03-22
