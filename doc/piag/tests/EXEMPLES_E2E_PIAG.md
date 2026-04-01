# Exemples de Workflows End-to-End PIAG

Ce document présente des exemples complets d'utilisation des commandes PIAG RAG et CHAT, étape par étape, avec les commandes complètes et leurs arguments.

## Table des matières

- [Démarrage Rapide avec piag-rag-create](#démarrage-rapide-avec-piag-rag-create)
- [Workflow RAG Complet](#workflow-rag-complet)
- [Workflow CHAT Simple](#workflow-chat-simple)
- [Workflow RAG + CHAT Intégré](#workflow-rag--chat-intégré)
- [Cas d'Usage Avancés](#cas-dusage-avancés)

---

## Démarrage Rapide avec piag-rag-create

La commande `piag-rag-create` est un raccourci puissant qui combine la création d'une collection et l'upload de documents en une seule opération. C'est la méthode la plus rapide pour démarrer avec PIAG RAG.

### Prérequis

```bash
# Configuration
export PIAG_RAG_API_TOKEN="votre-token-ici"
export PIAG_RAG_PROJECT_ID="votre-project-id"
export PIAG_RAG_BASE_URL="https://rag.api.piag.e2.rie.gouv.fr/v1"
```

### Cas 1 : Créer une collection vide

```bash
================================================================================
STEP 1: Créer une collection RAG vide pour SIREINES
================================================================================
Command:
  ambulon piag-rag-create \
    --collection-name "PNM3_SIREINES" \
    --description "Documentation technique et spécifications du système SIREINES"
================================================================================
```

**Résultat :**
```json
{
  "collection": {
    "id": "col_abc123xyz",
    "name": "PNM3_SIREINES",
    "description": "Documentation technique et spécifications du système SIREINES",
    "created_at": "2024-03-20T10:30:00Z",
    "document_count": 0
  },
  "message": "Collection créée avec succès"
}
```

### Cas 2 : Créer une collection et uploader tous les documents d'un répertoire

**Exemple concret avec le projet SIREINES :**

```bash
================================================================================
STEP 1: Créer la collection SIREINES et uploader tous les documents
================================================================================
Command:
  ambulon piag-rag-create \
    --collection-name "PNM3_SIREINES" \
    --description "Documentation complète SIREINES : DAT, CCTP, C4, Composants, ISO25010" \
    --directory applications/sireines.rag \
    --extensions "md,pdf"
================================================================================
```

**Structure du répertoire applications/sireines.rag :**
```
applications/sireines.rag/
├── sireines.dat.md                    # Dossier d'Architecture Technique
├── sireines.dat.pdf
├── sireines.cctp.md                   # Cahier des Clauses Techniques
├── sireines.components.md             # Documentation des composants
├── sireines.components.interactive.html
├── sireines.dat_c4model.md            # Modèle C4
├── sireines.dat_c4model.pdf
├── sireines.cst_iso25010.md           # Spécifications qualité
└── sireines.wiki.md                   # Documentation Wiki
```

**Résultat :**
```json
{
  "collection": {
    "id": "col_sireines_789",
    "name": "PNM3_SIREINES",
    "document_count": 15
  },
  "uploaded_documents": [
    {
      "filename": "sireines.dat.md",
      "id": "doc_001",
      "status": "processing"
    },
    {
      "filename": "sireines.dat.pdf",
      "id": "doc_002",
      "status": "processing"
    },
    {
      "filename": "sireines.cctp.md",
      "id": "doc_003",
      "status": "processing"
    },
    {
      "filename": "sireines.components.md",
      "id": "doc_004",
      "status": "processing"
    },
    {
      "filename": "sireines.dat_c4model.md",
      "id": "doc_005",
      "status": "processing"
    }
    // ... et 10 autres documents
  ],
  "message": "Collection créée et 15 documents uploadés avec succès"
}
```

### Cas 3 : Upload sélectif par extension

```bash
================================================================================
Uploader uniquement certains types de fichiers
================================================================================
Command:
  ambulon piag-rag-create \
    --collection-name "Documents PDF" \
    --directory ./documents \
    --recursive \
    --extensions "pdf,docx"
================================================================================
```

**Résultat :**
```
✓ Collection créée : col_456
✓ Documents uploadés : 2/5 (seuls .pdf et .docx)
  - manuel_deploiement.pdf      [OK]
  - architecture/diagrammes.pdf  [OK]
  - architecture/decisions.md    [IGNORÉ - extension non autorisée]
  - procedures/installation.md   [IGNORÉ - extension non autorisée]
  - procedures/maintenance.md    [IGNORÉ - extension non autorisée]
```

### Workflow complet : Création + Recherche + Chat

Voici un exemple complet qui utilise `piag-rag-create` pour initialiser rapidement un RAG, puis effectue une recherche et génère une réponse.

```bash
#!/bin/bash
# quick_rag_setup.sh - Configuration rapide d'un RAG avec recherche et chat

set -e

COLLECTION_NAME="Docs Techniques $(date +%Y%m%d_%H%M%S)"
DOCS_DIR="./documents"
QUESTION="Quelle est la procédure de déploiement ?"

echo "═══════════════════════════════════════════════════════════════════════"
echo "DÉMARRAGE RAPIDE : RAG + RECHERCHE + CHAT"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# ÉTAPE 1 : Créer le RAG avec tous les documents
echo "[1/3] Création de la collection et upload des documents..."
RESULT=$(ambulon piag-rag-create \
  --collection-name "$COLLECTION_NAME" \
  --description "Collection créée automatiquement" \
  --directory "$DOCS_DIR" \
  --recursive \
  --json)

COLLECTION_ID=$(echo "$RESULT" | jq -r '.collection.id')
DOC_COUNT=$(echo "$RESULT" | jq -r '.collection.document_count')

echo "✓ Collection créée : $COLLECTION_ID"
echo "✓ Documents uploadés : $DOC_COUNT"
echo ""

# Attendre l'indexation
echo "⏳ Attente de l'indexation (30 secondes)..."
sleep 30
echo ""

# ÉTAPE 2 : Rechercher des chunks pertinents
echo "[2/3] Recherche des chunks pertinents..."
ambulon piag-rag-search \
  --collection-id "$COLLECTION_ID" \
  --query "$QUESTION" \
  --top-k 5 \
  --mode hybrid \
  --rerank true \
  --json \
  --output ./rag_results.json

CHUNK_COUNT=$(jq '.chunks | length' ./rag_results.json)
echo "✓ Trouvé $CHUNK_COUNT chunks pertinents"
echo ""

# ÉTAPE 3 : Générer une réponse avec contexte
echo "[3/3] Génération de la réponse avec le LLM..."
ambulon piag-chat-query \
  --question "$QUESTION" \
  --chunks ./rag_results.json \
  --output ./reponse_finale.md

echo "✓ Réponse générée dans reponse_finale.md"
echo ""

echo "═══════════════════════════════════════════════════════════════════════"
echo "WORKFLOW TERMINÉ AVEC SUCCÈS"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Collection ID   : $COLLECTION_ID"
echo "Documents       : $DOC_COUNT"
echo "Chunks trouvés  : $CHUNK_COUNT"
echo ""
echo "Réponse :"
echo "───────────────────────────────────────────────────────────────────────"
cat ./reponse_finale.md
echo "───────────────────────────────────────────────────────────────────────"
```

**Utilisation :**
```bash
chmod +x quick_rag_setup.sh
./quick_rag_setup.sh
```

**Sortie exemple :**
```
═══════════════════════════════════════════════════════════════════════
DÉMARRAGE RAPIDE : RAG + RECHERCHE + CHAT
═══════════════════════════════════════════════════════════════════════

[1/3] Création de la collection et upload des documents...
✓ Collection créée : col_quick_20240320_103045
✓ Documents uploadés : 5

⏳ Attente de l'indexation (30 secondes)...

[2/3] Recherche des chunks pertinents...
✓ Trouvé 5 chunks pertinents

[3/3] Génération de la réponse avec le LLM...
✓ Réponse générée dans reponse_finale.md

═══════════════════════════════════════════════════════════════════════
WORKFLOW TERMINÉ AVEC SUCCÈS
═══════════════════════════════════════════════════════════════════════

Collection ID   : col_quick_20240320_103045
Documents       : 5
Chunks trouvés  : 5

Réponse :
───────────────────────────────────────────────────────────────────────
# Procédure de Déploiement

Selon les documents techniques, la procédure de déploiement comprend :

1. **Préparation de l'environnement**
   - Vérifier la configuration du serveur
   - S'assurer que tous les tests passent

2. **Build de l'application**
   - Compiler le code source
   - Créer les packages de déploiement

3. **Déploiement sur le serveur**
   - Transférer les fichiers via SSH
   - Redémarrer les services

**Important** : Consulter le manuel_deploiement.pdf (page 12-14) pour
les détails complets.
───────────────────────────────────────────────────────────────────────
```

### Avantages de piag-rag-create

| Fonctionnalité | Avantage |
|----------------|----------|
| **Une seule commande** | Crée la collection et uploade tous les documents en une fois |
| **Upload récursif** | Parcourt automatiquement tous les sous-répertoires |
| **Filtrage d'extensions** | Ne téléverse que les types de fichiers souhaités |
| **Gain de temps** | Évite d'avoir à créer la collection puis uploader document par document |
| **Idéal pour CI/CD** | Parfait pour automatiser la création de RAG dans les pipelines |

### Comparaison : méthode manuelle vs piag-rag-create

#### Méthode manuelle (3 étapes minimum)

```bash
# 1. Créer la collection
ambulon piag-rag-collection-add --name "Docs" --description "..."

# 2. Récupérer l'ID
COLLECTION_ID=$(ambulon piag-rag-collection-get --collection "Docs" | jq -r '.id')

# 3. Uploader chaque document individuellement
ambulon piag-rag-doc-upload --collection-id $COLLECTION_ID --file doc1.pdf
ambulon piag-rag-doc-upload --collection-id $COLLECTION_ID --file doc2.pdf
ambulon piag-rag-doc-upload --collection-id $COLLECTION_ID --file doc3.pdf
# ... etc
```

#### Avec piag-rag-create (1 seule étape)

```bash
# Tout en une seule commande !
ambulon piag-rag-create \
  --collection-name "Docs" \
  --description "..." \
  --directory ./documents \
  --recursive
```

**Conclusion** : `piag-rag-create` est **3 à 10 fois plus rapide** pour initialiser un RAG, surtout avec de nombreux documents.

---

## Workflow RAG Complet

Ce workflow montre comment gérer une collection RAG complète : création, upload de documents, recherche et suppression.

### Prérequis

Les exemples ci-dessous utilisent automatiquement la configuration définie dans `config/piag.yaml` :

```yaml
piag:
  rag:
    project:
      project_id: "votre-project-id"
    security:
      token: "votre-token-rag"
    api:
      base_url: "https://rag.api.piag.e2.rie.gouv.fr/v1"
```

Vous pouvez aussi utiliser les variables d'environnement :
```bash
export PIAG_RAG_API_TOKEN="votre-token-ici"
export PIAG_RAG_PROJECT_ID="votre-project-id"
```

**Les commandes ci-dessous ne répètent pas ces paramètres car ils sont déjà configurés.**

### Étape 0 : Créer une collection

```bash
================================================================================
STEP 0: Créer une nouvelle collection pour stocker les documents
================================================================================
Command:
  ambulon piag-rag-collection-add \
    --name "Documents Techniques" \
    --description "Collection de documents techniques du projet"
================================================================================
```

**Résultat :**
```json
{
  "id": "col_abc123xyz",
  "name": "Documents Techniques",
  "description": "Collection de documents techniques du projet",
  "created_at": "2024-03-20T10:30:00Z"
}
```

### Étape 1 : Lister les collections

```bash
================================================================================
STEP 1: Vérifier que la collection a bien été créée
================================================================================
Command:
  ambulon piag-rag-collection-list
================================================================================
```

**Résultat :**
```json
{
  "collections": [
    {
      "id": "col_abc123xyz",
      "name": "Documents Techniques",
      "document_count": 0
    }
  ]
}
```

### Étape 2 : Uploader un document

```bash
================================================================================
STEP 2: Uploader un document dans la collection
================================================================================
Command:
  ambulon piag-rag-doc-upload \
    --collection col_abc123xyz \
    --file manuel_deploiement.pdf
================================================================================
```

**Résultat :**
```json
{
  "id": "doc_xyz789",
  "filename": "manuel_deploiement.pdf",
  "status": "processing",
  "size": 2457600,
  "uploaded_at": "2024-03-20T10:35:00Z"
}
```

### Étape 3 : Vérifier l'indexation du document

```bash
================================================================================
STEP 3: Attendre que le document soit indexé et vérifier son statut
================================================================================
Command:
  ambulon piag-rag-doc-get \
    --collection col_abc123xyz \
    --document-id doc_xyz789
================================================================================
```

**Résultat :**
```json
{
  "id": "doc_xyz789",
  "filename": "manuel_deploiement.pdf",
  "status": "indexed",
  "chunk_count": 47,
  "size": 2457600
}
```

### Étape 4 : Récupérer les chunks d'un document

```bash
================================================================================
STEP 4: Récupérer tous les chunks du document
================================================================================
Command:
  ambulon piag-rag-doc-chunks \
    --collection col_abc123xyz \
    --document-id doc_xyz789 \
    --output chunks.json
================================================================================
```

**Résultat (chunks.json) :**
```json
{
  "document_id": "doc_xyz789",
  "chunks": [
    {
      "id": "chunk_001",
      "content": "La procédure de déploiement se déroule en 3 étapes...",
      "metadata": {
        "page": 12,
        "section": "Déploiement"
      }
    },
    {
      "id": "chunk_002",
      "content": "Avant tout déploiement, vérifier les tests...",
      "metadata": {
        "page": 13,
        "section": "Prérequis"
      }
    }
    // ... 45 autres chunks
  ]
}
```

### Étape 5 : Rechercher dans la collection

```bash
================================================================================
STEP 5: Rechercher des chunks pertinents pour une question
================================================================================
Command:
  ambulon piag-rag-search \
    --collection col_abc123xyz \
    --query "procédure de déploiement" \
    --top-k 5 \
    --json \
    --output search_results.json
================================================================================
```

**Résultat (search_results.json) :**
```json
{
  "query": "procédure de déploiement",
  "chunks": [
    {
      "id": "chunk_001",
      "content": "La procédure de déploiement se déroule en 3 étapes principales...",
      "score": 0.94,
      "document_id": "doc_xyz789",
      "metadata": {
        "filename": "manuel_deploiement.pdf",
        "page": 12
      }
    },
    {
      "id": "chunk_002",
      "content": "Avant tout déploiement, vérifier que tous les tests passent...",
      "score": 0.88,
      "document_id": "doc_xyz789",
      "metadata": {
        "filename": "manuel_deploiement.pdf",
        "page": 13
      }
    }
    // ... 3 autres chunks
  ]
}
```

### Étape 6 : Supprimer un document

```bash
================================================================================
STEP 6: Supprimer le document de la collection
================================================================================
Command:
  ambulon piag-rag-doc-rm \
    --collection col_abc123xyz \
    --document-id doc_xyz789 \
    --force
================================================================================
```

**Résultat :**
```
✓ Document doc_xyz789 supprimé avec succès
```

### Étape 7 : Supprimer la collection

```bash
================================================================================
STEP 7: Supprimer la collection (nettoyage)
================================================================================
Command:
  ambulon piag-rag-collection-rm \
    --collection col_abc123xyz \
    --force
================================================================================
```

---

## Workflow CHAT Simple

Ce workflow montre comment utiliser l'API CHAT de PIAG pour des conversations simples.

### Prérequis

Les exemples utilisent la configuration définie dans `config/piag.yaml` :

```yaml
piag:
  chat:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1"
    security:
      token: "sk-votre-token-chat"
    model: "mte-api-piag-mistral-medium-latest"
```

Ou via variable d'environnement :
```bash
export PIAG_CHAT_API_TOKEN="sk-votre-token-chat"
```

**Les commandes ci-dessous ne répètent pas ces paramètres.**

### Étape 1 : Vérifier les informations du token

```bash
================================================================================
STEP 1: Vérifier le budget et l'utilisation du token API
================================================================================
Command:
  ambulon piag-chat-apikey-info
================================================================================
```

**Résultat :**
```json
{
  "token_id": "tok_abc123",
  "budget_max": 1000.0,
  "budget_used": 234.56,
  "budget_remaining": 765.44,
  "currency": "EUR"
}
```

### Étape 2 : Question simple sans contexte

```bash
================================================================================
STEP 2: Poser une question simple au modèle
================================================================================
Command:
  ambulon piag-chat-basic-query \
    --question "Quelle est la capitale de la France ?"
================================================================================
```

**Résultat :**
```
La capitale de la France est Paris. C'est la ville la plus peuplée du pays
et son centre économique, politique et culturel.
```

### Étape 3 : Question avec message système

```bash
================================================================================
STEP 3: Poser une question avec un rôle système personnalisé
================================================================================
Command:
  ambulon piag-chat-basic-query \
    --question "Explique-moi le concept de CI/CD" \
    --system "Tu es un expert DevOps. Réponds de manière concise et technique."
================================================================================
```

**Résultat :**
```
CI/CD (Continuous Integration/Continuous Deployment) est une pratique DevOps
qui automatise l'intégration et le déploiement du code :

- CI : Intégration fréquente du code dans le dépôt principal avec tests
  automatiques
- CD : Déploiement automatisé en production après validation

Avantages : détection rapide des bugs, déploiements fréquents et fiables,
réduction des risques.
```

### Étape 4 : Sauvegarder la réponse dans un fichier

```bash
================================================================================
STEP 4: Générer une réponse et la sauvegarder en markdown
================================================================================
Command:
  ambulon piag-chat-basic-query \
    --question "Donne-moi un exemple de pipeline CI/CD pour une app Python" \
    --output pipeline_example.md
================================================================================
```

**Résultat (pipeline_example.md) :**
```markdown
# Exemple de Pipeline CI/CD pour Application Python

## Pipeline GitLab CI

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/

build:
  stage: build
  script:
    - python setup.py bdist_wheel

deploy:
  stage: deploy
  script:
    - scp dist/*.whl production:/app/
    - ssh production "pip install /app/*.whl"
```

Ce pipeline effectue les tests, crée un wheel Python et le déploie.
```

---

## Workflow RAG + CHAT Intégré

Ce workflow montre comment combiner la recherche RAG avec la génération CHAT pour créer un assistant intelligent basé sur vos documents.

### Architecture

```
┌─────────────────┐
│   QUESTION      │  "Quelle est la procédure de déploiement ?"
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  ÉTAPE 1 : RECHERCHE RAG (piag-rag-search)             │
│  Trouve les chunks pertinents dans les documents       │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  CHUNKS         │  {chunks: [...], scores: [...]}
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : GÉNÉRATION CHAT (piag-chat-query)           │
│  Génère une réponse basée sur les chunks               │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   RÉPONSE       │  "Selon le manuel de déploiement..."
└─────────────────┘
```

### Workflow complet

#### Étape 1 : Rechercher les chunks pertinents

```bash
================================================================================
STEP 1: Rechercher dans la collection RAG
================================================================================
Command:
  ambulon piag-rag-search \
    --collection col_abc123xyz \
    --query "Quelle est la procédure de déploiement ?" \
    --top-k 5 \
    --mode hybrid \
    --rerank true \
    --json \
    --output rag_results.json
================================================================================
```

**Résultat (rag_results.json) :**
```json
{
  "query": "Quelle est la procédure de déploiement ?",
  "chunks": [
    {
      "content": "La procédure de déploiement se déroule en 3 étapes principales: 1) Préparation de l'environnement, 2) Build de l'application, 3) Déploiement sur le serveur.",
      "score": 0.94,
      "metadata": {"source": "manuel_deploiement.pdf", "page": 12}
    },
    {
      "content": "Avant tout déploiement, vérifier que tous les tests unitaires et d'intégration passent avec succès.",
      "score": 0.88,
      "metadata": {"source": "manuel_deploiement.pdf", "page": 13}
    }
  ]
}
```

#### Étape 2 : Générer une réponse avec le contexte

```bash
================================================================================
STEP 2: Interroger le LLM avec le contexte RAG
================================================================================
Command:
  ambulon piag-chat-query \
    --question "Quelle est la procédure de déploiement ?" \
    --chunks rag_results.json \
    --output reponse_deploiement.md
================================================================================
```

**Résultat (reponse_deploiement.md) :**
```markdown
# Procédure de Déploiement

Selon le manuel de déploiement, la procédure se déroule en 3 étapes principales :

## 1. Préparation de l'environnement
Assurez-vous que l'environnement cible est correctement configuré.

## 2. Build de l'application
Compilez et packagez l'application avec les bonnes dépendances.

## 3. Déploiement sur le serveur
Transférez et installez l'application sur le serveur de production.

**Important** : Avant tout déploiement, vérifiez que tous les tests
unitaires et d'intégration passent avec succès.

---
*Réponse générée à partir du manuel_deploiement.pdf (pages 12-13)*
```

### Script automatisé complet

Voici un script bash qui automatise tout le workflow :

```bash
#!/bin/bash
# rag_chat_workflow.sh - Workflow RAG + CHAT complet

set -e  # Arrêter en cas d'erreur

# Configuration
COLLECTION_ID="col_abc123xyz"
QUESTION="Quelle est la procédure de déploiement ?"
OUTPUT_DIR="./output"
mkdir -p "$OUTPUT_DIR"

echo "═══════════════════════════════════════════════════════════════════════"
echo "WORKFLOW RAG + CHAT : $QUESTION"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Étape 1 : Recherche RAG
echo "[1/2] Recherche des chunks pertinents dans la collection..."
ambulon piag-rag-search \
  --collection-id "$COLLECTION_ID" \
  --query "$QUESTION" \
  --top-k 5 \
  --mode hybrid \
  --rerank true \
  --json \
  --output "$OUTPUT_DIR/rag_chunks.json"

echo "✓ Chunks récupérés et sauvegardés dans $OUTPUT_DIR/rag_chunks.json"
echo ""

# Étape 2 : Génération CHAT
echo "[2/2] Génération de la réponse avec contexte..."
ambulon piag-chat-query \
  --question "$QUESTION" \
  --chunks "$OUTPUT_DIR/rag_chunks.json" \
  --output "$OUTPUT_DIR/reponse.md"

echo "✓ Réponse générée et sauvegardée dans $OUTPUT_DIR/reponse.md"
echo ""

echo "═══════════════════════════════════════════════════════════════════════"
echo "WORKFLOW TERMINÉ AVEC SUCCÈS"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Fichiers générés :"
echo "  - Chunks RAG     : $OUTPUT_DIR/rag_chunks.json"
echo "  - Réponse finale : $OUTPUT_DIR/reponse.md"
echo ""
echo "Affichage de la réponse :"
echo "───────────────────────────────────────────────────────────────────────"
cat "$OUTPUT_DIR/reponse.md"
echo "───────────────────────────────────────────────────────────────────────"
```

**Utilisation :**
```bash
chmod +x rag_chat_workflow.sh
./rag_chat_workflow.sh
```

---

## Cas d'Usage Avancés

### Cas 1 : Recherche multi-collections

Rechercher dans plusieurs collections simultanément :

```bash
# Par IDs
ambulon piag-rag-search \
  --collection-id-list "col_123,col_456,col_789" \
  --query "architecture microservices" \
  --top-k 10 \
  --json \
  --output multi_collection_results.json

# Par noms (plus lisible)
ambulon piag-rag-search \
  --collection-name-list "Docs Techniques,Docs Métier,Archives" \
  --query "architecture microservices" \
  --top-k 10 \
  --json \
  --output multi_collection_results.json
```

### Cas 2 : Utilisation par nom de collection

Utiliser les noms au lieu des IDs (plus lisible) :

```bash
# Recherche par nom de collection
ambulon piag-rag-search \
  --collection-name "Documents Techniques" \
  --query "procédure" \
  --json > results.json

# Récupération de chunks par nom
ambulon piag-rag-doc-chunks \
  --document-name "manuel_deploiement.pdf" \
  --collection-name "Documents Techniques" \
  --output chunks.json

# Utilisation avec CHAT
ambulon piag-chat-query \
  --question "Résume le manuel" \
  --chunks chunks.json
```

### Cas 3 : Pipeline CI/CD avec RAG + CHAT

Intégrer dans un pipeline GitLab CI :

```yaml
# .gitlab-ci.yml
stages:
  - doc-analysis

analyze-documentation:
  stage: doc-analysis
  before_script:
    # Configuration depuis les variables CI/CD GitLab
    - export PIAG_RAG_API_TOKEN=$PIAG_RAG_TOKEN
    - export PIAG_RAG_PROJECT_ID=$PIAG_PROJECT_ID
    - export PIAG_CHAT_API_TOKEN=$PIAG_CHAT_TOKEN
  script:
    # Upload de la documentation mise à jour
    - ambulon piag-rag-doc-upload \
        --collection-name "Docs Projet" \
        --file docs/architecture.md

    # Génération d'un résumé automatique
    - ambulon piag-rag-search \
        --collection-name "Docs Projet" \
        --query "changements architecture" \
        --json > changes.json

    - ambulon piag-chat-query \
        --question "Résume les changements d'architecture" \
        --chunks changes.json \
        --output CHANGELOG_AI.md

    # Publier le résumé
    - cat CHANGELOG_AI.md
  artifacts:
    paths:
      - CHANGELOG_AI.md
```

### Cas 4 : Assistant interactif

Script interactif pour poser plusieurs questions :

```bash
#!/bin/bash
# interactive_assistant.sh

COLLECTION="col_docs_techniques"  # Ou utilisez un nom avec --collection-name

echo "Assistant documentaire interactif"
echo "=================================="
echo ""

while true; do
    echo -n "Votre question (ou 'quit' pour quitter) : "
    read -r QUESTION

    if [ "$QUESTION" = "quit" ]; then
        echo "Au revoir !"
        break
    fi

    echo ""
    echo "🔍 Recherche en cours..."

    # Recherche
    ambulon piag-rag-search \
        --collection-id "$COLLECTION" \
        --query "$QUESTION" \
        --top-k 3 \
        --json > /tmp/chunks.json

    echo "💬 Génération de la réponse..."

    # Génération de la réponse
    ambulon piag-chat-query \
        --question "$QUESTION" \
        --chunks /tmp/chunks.json

    echo ""
    echo "───────────────────────────────────────"
    echo ""
done
```

---

## Questions Techniques Avancées : Projet SIREINES

Cette section présente des exemples de questions techniques spécifiques au projet SIREINES, démontrant comment interroger efficacement la documentation technique avec RAG + CHAT.

### Question 1 : Architecture Technique

```bash
# Rechercher des informations sur l'architecture
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "architecture technique microservices composants API" \
  --top-k 7 \
  --mode hybrid \
  --rerank true \
  --json \
  --output q1_architecture.json

# Générer une réponse structurée
ambulon piag-chat-query \
  --question "Décris l'architecture technique du système SIREINES en détaillant les composants, les technologies utilisées et les patterns architecturaux appliqués." \
  --chunks q1_architecture.json \
  --output reponse_architecture.md
```

**Réponse attendue** : Description de l'architecture microservices, API REST, base PostgreSQL, modules fonctionnels (alertes, traitement, reporting, admin).

### Question 2 : Modèle C4

```bash
# Rechercher sur le modèle C4
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "modèle C4 context container component diagrammes" \
  --top-k 5 \
  --json \
  --output q2_c4.json

# Question technique
ambulon piag-chat-query \
  --question "Explique le modèle C4 appliqué à SIREINES. Quels sont les 4 niveaux et que représentent-ils ?" \
  --chunks q2_c4.json \
  --output reponse_c4.md
```

**Réponse attendue** :
- Context : Système SIREINES dans son écosystème
- Container : Applications (Frontend, Backend API, BDD)
- Component : Modules fonctionnels détaillés
- Code : Implémentation technique

### Question 3 : Module de Gestion des Alertes

```bash
# Rechercher sur le module alertes
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "module gestion alertes fonctionnalités workflow traitement" \
  --top-k 5 \
  --json \
  --output q3_alertes.json

# Question fonctionnelle
ambulon piag-chat-query \
  --question "Comment fonctionne le module de gestion des alertes dans SIREINES ? Quelles sont ses fonctionnalités principales et son workflow ?" \
  --chunks q3_alertes.json \
  --output reponse_alertes.md
```

**Réponse attendue** : Réception, validation, enrichissement, routage et notification des alertes.

### Question 4 : Exigences Qualité ISO 25010

```bash
# Rechercher les critères qualité
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "ISO 25010 exigences qualité performance sécurité maintenabilité" \
  --top-k 6 \
  --json \
  --output q4_iso25010.json

# Question normative
ambulon piag-chat-query \
  --question "Quelles sont les exigences de qualité ISO 25010 définies pour SIREINES ? Détaille les critères de performance, sécurité, maintenabilité et fiabilité." \
  --chunks q4_iso25010.json \
  --output reponse_iso25010.md
```

**Réponse attendue** : Critères fonctionnels (adéquation, performance), de fiabilité, de sécurité, de maintenabilité et de portabilité selon ISO 25010.

### Question 5 : Stack Technique et Dépendances

```bash
# Rechercher les technologies
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "technologies stack technique frameworks bibliothèques dépendances PostgreSQL" \
  --top-k 5 \
  --json \
  --output q5_stack.json

# Question technique détaillée
ambulon piag-chat-query \
  --question "Quelle est la stack technique complète de SIREINES ? Liste les frameworks, bibliothèques et versions utilisées pour le frontend, le backend et la base de données." \
  --chunks q5_stack.json \
  --output reponse_stack.md
```

**Réponse attendue** : Frontend (React/Vue/Angular), Backend (Python/Node/Java), BDD (PostgreSQL version X), frameworks API, ORM, etc.

### Question 6 : Interfaces et API

```bash
# Rechercher les API et interfaces
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "API REST endpoints interfaces externes intégration" \
  --top-k 6 \
  --json \
  --output q6_api.json

# Question d'intégration
ambulon piag-chat-query \
  --question "Décris les API et interfaces exposées par SIREINES. Quels sont les endpoints principaux, les formats de données et les protocoles utilisés ?" \
  --chunks q6_api.json \
  --output reponse_api.md
```

**Réponse attendue** : Endpoints REST, formats JSON, authentification, webhooks, API publiques vs internes.

### Question 7 : Sécurité et Authentification

```bash
# Rechercher les aspects sécurité
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "sécurité authentification autorisation RBAC JWT chiffrement" \
  --top-k 5 \
  --json \
  --output q7_securite.json

# Question sécurité
ambulon piag-chat-query \
  --question "Comment est implémentée la sécurité dans SIREINES ? Décris les mécanismes d'authentification, d'autorisation, de chiffrement et de protection des données." \
  --chunks q7_securite.json \
  --output reponse_securite.md
```

**Réponse attendue** : JWT/OAuth, RBAC, chiffrement des données sensibles, HTTPS, validation des entrées.

### Question 8 : Procédures de Déploiement et Exploitation

```bash
# Rechercher déploiement et exploitation
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "déploiement installation configuration exploitation monitoring" \
  --top-k 6 \
  --json \
  --output q8_deploiement.json

# Question opérationnelle
ambulon piag-chat-query \
  --question "Quelles sont les procédures de déploiement et d'exploitation de SIREINES ? Décris les étapes d'installation, de configuration et de monitoring." \
  --chunks q8_deploiement.json \
  --output reponse_deploiement.md
```

**Réponse attendue** : Procédure d'installation, configuration environnement, déploiement conteneurs/VMs, monitoring et supervision.

### Question 9 : Module de Reporting

```bash
# Rechercher le module reporting
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "module reporting tableaux bord indicateurs exports" \
  --top-k 5 \
  --json \
  --output q9_reporting.json

# Question fonctionnelle avancée
ambulon piag-chat-query \
  --question "Décris le module de reporting de SIREINES. Quels types de rapports peut-il générer ? Quels indicateurs sont disponibles ? Quels formats d'export sont supportés ?" \
  --chunks q9_reporting.json \
  --output reponse_reporting.md
```

**Réponse attendue** : Types de rapports (synthèse, détaillé, temps réel), KPI, exports PDF/Excel/CSV, dashboards interactifs.

### Question 10 : Évolutions et Roadmap

```bash
# Rechercher les évolutions prévues
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "évolutions futures roadmap améliorations fonctionnalités prévues" \
  --top-k 5 \
  --json \
  --output q10_evolutions.json

# Question prospective
ambulon piag-chat-query \
  --question "Quelles sont les évolutions et améliorations prévues pour le système SIREINES ? Y a-t-il une roadmap documentée ?" \
  --chunks q10_evolutions.json \
  --output reponse_evolutions.md
```

**Réponse attendue** : Fonctionnalités à venir, améliorations de performance, nouvelles intégrations, refactoring prévu.

### Script de Questions Multiples

Voici un script qui pose automatiquement toutes les questions techniques :

```bash
#!/bin/bash
# questions_techniques_sireines.sh - Analyse technique complète

set -e

COLLECTION="PNM3_SIREINES"
OUTPUT_DIR="./analyse_technique_sireines"
mkdir -p "$OUTPUT_DIR"

# Liste des questions techniques
declare -A QUESTIONS=(
  ["architecture"]="Décris l'architecture technique du système SIREINES en détail"
  ["c4model"]="Explique le modèle C4 appliqué à SIREINES"
  ["alertes"]="Comment fonctionne le module de gestion des alertes ?"
  ["iso25010"]="Quelles sont les exigences de qualité ISO 25010 ?"
  ["stack"]="Quelle est la stack technique complète utilisée ?"
  ["api"]="Décris les API et interfaces exposées par SIREINES"
  ["securite"]="Comment est implémentée la sécurité ?"
  ["deploiement"]="Quelles sont les procédures de déploiement ?"
  ["reporting"]="Décris le module de reporting et ses fonctionnalités"
  ["evolutions"]="Quelles sont les évolutions prévues ?"
)

echo "═══════════════════════════════════════════════════════════════════════"
echo "ANALYSE TECHNIQUE COMPLÈTE : SIREINES"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Pour chaque question
for topic in "${!QUESTIONS[@]}"; do
  question="${QUESTIONS[$topic]}"

  echo "[$topic] $question"

  # Recherche
  ambulon piag-rag-search \
    --collection "$COLLECTION" \
    --query "$question" \
    --top-k 5 \
    --json \
    --output "$OUTPUT_DIR/${topic}_chunks.json" > /dev/null 2>&1

  # Génération réponse
  ambulon piag-chat-query \
    --question "$question" \
    --chunks "$OUTPUT_DIR/${topic}_chunks.json" \
    --output "$OUTPUT_DIR/${topic}_reponse.md" > /dev/null 2>&1

  echo "✓ Réponse générée : $OUTPUT_DIR/${topic}_reponse.md"
  echo ""
done

echo "═══════════════════════════════════════════════════════════════════════"
echo "ANALYSE TERMINÉE"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Fichiers générés dans : $OUTPUT_DIR/"
ls -lh "$OUTPUT_DIR/"
```

**Utilisation :**
```bash
chmod +x questions_techniques_sireines.sh
./questions_techniques_sireines.sh
```

Ce script génère automatiquement 10 analyses techniques détaillées du projet SIREINES en interrogeant la collection RAG.

---

## Communication entre Collection RAG et CHAT

### Comprendre la distinction

Il existe **deux systèmes PIAG distincts** avec des collections séparées :

| Système | Rôle | Collection | API |
|---------|------|------------|-----|
| **PIAG RAG** | Stockage et recherche de documents | `PNM3_SIREINES` (RAG) | `https://rag.api.piag.e2.rie.gouv.fr/v1` |
| **PIAG CHAT** | Génération de réponses avec LLM | Pas de collection propre | `https://preprod.api.piag.e2.rie.gouv.fr/v1` |

**Important** :
- La collection RAG `PNM3_SIREINES` stocke les **documents** (DAT, CCTP, composants, etc.)
- L'API CHAT n'a **pas de collection**, elle reçoit les chunks trouvés par le RAG comme **contexte**
- Les deux systèmes communiquent via le **workflow RAG → CHAT**

### Workflow de Communication

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. COLLECTION RAG : PNM3_SIREINES                              │
│    - Stocke tous les documents SIREINES                         │
│    - Indexe le contenu en chunks vectorisés                     │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ piag-rag-search --collection PNM3_SIREINES
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. RECHERCHE SÉMANTIQUE                                         │
│    - Trouve les 5 chunks les plus pertinents                    │
│    - Score de similarité pour chaque chunk                      │
└─────────────┬───────────────────────────────────────────────────┘
              │
              │ chunks.json (contexte extrait)
              ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. API CHAT PIAG                                                │
│    - Reçoit les chunks comme CONTEXTE                           │
│    - Génère une réponse basée sur ce contexte                   │
│    - Utilise le LLM (Mistral) pour synthétiser                  │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ▼
         Réponse générée
```

### Exemple Pratique : Connecter RAG et CHAT

```bash
# Étape 1 : Créer et alimenter la collection RAG
ambulon piag-rag-create \
  --collection-name "PNM3_SIREINES" \
  --description "Documentation complète SIREINES" \
  --directory applications/sireines.rag \
  --extensions "md,pdf"

# Attendre l'indexation
sleep 30

# Étape 2 : Rechercher dans le RAG
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "Comment fonctionne le module d'alertes ?" \
  --top-k 5 \
  --json \
  --output context_alertes.json

# Étape 3 : Utiliser le contexte RAG avec CHAT
ambulon piag-chat-query \
  --question "Comment fonctionne le module d'alertes dans SIREINES ?" \
  --chunks context_alertes.json \
  --output reponse_alertes.md

# ✓ La réponse du CHAT est basée sur le contenu de la collection RAG !
```

### Cas d'Usage : Assistant SIREINES Intelligent

Créer un assistant qui répond toujours avec le contexte de la documentation SIREINES :

```bash
#!/bin/bash
# assistant_sireines.sh - Assistant intelligent basé sur la doc SIREINES

COLLECTION_RAG="PNM3_SIREINES"

function ask_sireines() {
  local question="$1"
  local output_file="${2:-reponse.md}"

  echo "🔍 Recherche dans la documentation SIREINES..."

  # Recherche RAG
  ambulon piag-rag-search \
    --collection "$COLLECTION_RAG" \
    --query "$question" \
    --top-k 7 \
    --mode hybrid \
    --rerank true \
    --json \
    --output /tmp/context_sireines.json

  echo "💬 Génération de la réponse..."

  # Génération CHAT avec contexte
  ambulon piag-chat-query \
    --question "$question" \
    --chunks /tmp/context_sireines.json \
    --system "Tu es un expert du système SIREINES. Réponds en te basant uniquement sur la documentation fournie. Si l'information n'est pas dans le contexte, indique-le clairement." \
    --output "$output_file"

  echo "✓ Réponse générée : $output_file"
}

# Exemples d'utilisation
ask_sireines "Quelle est l'architecture de SIREINES ?" "architecture.md"
ask_sireines "Comment configurer le module d'alertes ?" "config_alertes.md"
ask_sireines "Quelles sont les exigences de sécurité ?" "securite.md"
```

### Synchronisation : Mise à Jour de la Collection RAG

Lorsque la documentation SIREINES évolue, il faut mettre à jour la collection RAG :

#### Option 1 : Mise à jour incrémentale (ajouter de nouveaux documents)

```bash
# Ajouter un nouveau document à la collection existante
ambulon piag-rag-doc-upload \
  --collection PNM3_SIREINES \
  --file applications/sireines.rag/sireines.nouveau_module.md

# Le CHAT utilisera automatiquement ce nouveau document dans ses réponses
```

#### Option 2 : Remplacement complet (recréer la collection)

```bash
# 1. Supprimer l'ancienne collection
ambulon piag-rag-collection-rm \
  --collection PNM3_SIREINES \
  --force

# 2. Recréer avec tous les documents à jour
ambulon piag-rag-create \
  --collection-name "PNM3_SIREINES" \
  --description "Documentation SIREINES (version mise à jour)" \
  --directory applications/sireines.rag \
  --extensions "md,pdf"
```

#### Option 3 : Versionning (garder l'historique)

```bash
# Créer une nouvelle version avec timestamp
DATE=$(date +%Y%m%d)
ambulon piag-rag-create \
  --collection-name "PNM3_SIREINES_v${DATE}" \
  --description "Documentation SIREINES - Version $DATE" \
  --directory applications/sireines.rag \
  --extensions "md,pdf"

# Utiliser la version spécifique
ambulon piag-rag-search \
  --collection "PNM3_SIREINES_v20240320" \
  --query "architecture" \
  --json > context.json
```

### Pipeline CI/CD : Synchronisation Automatique

Automatiser la mise à jour de la collection RAG quand la doc change :

```yaml
# .gitlab-ci.yml
stages:
  - doc-update
  - test-qa

# Mise à jour automatique de la collection RAG
update-rag-collection:
  stage: doc-update
  only:
    changes:
      - applications/sireines.rag/**/*
  before_script:
    - export PIAG_RAG_API_TOKEN=$PIAG_RAG_TOKEN
    - export PIAG_RAG_PROJECT_ID=$PIAG_PROJECT_ID
  script:
    # Upload des documents modifiés
    - |
      for file in applications/sireines.rag/*.{md,pdf}; do
        echo "Upload : $file"
        ambulon piag-rag-doc-upload \
          --collection PNM3_SIREINES \
          --file "$file" || true
      done

    # Test : Vérifier que le RAG répond correctement
    - ambulon piag-rag-search \
        --collection PNM3_SIREINES \
        --query "architecture SIREINES" \
        --top-k 3 \
        --json > test_search.json

    - |
      if [ $(jq '.chunks | length' test_search.json) -gt 0 ]; then
        echo "✓ Collection RAG opérationnelle"
      else
        echo "✗ Erreur : Aucun résultat trouvé"
        exit 1
      fi

# Test QA : Vérifier la qualité des réponses
test-qa-responses:
  stage: test-qa
  needs: ["update-rag-collection"]
  script:
    # Liste de questions de test
    - |
      questions=(
        "Quelle est l'architecture de SIREINES ?"
        "Comment fonctionne le module d'alertes ?"
        "Quelles sont les exigences ISO 25010 ?"
      )

    - mkdir -p qa_results

    # Tester chaque question
    - |
      for i in "${!questions[@]}"; do
        q="${questions[$i]}"
        echo "Test Q$i: $q"

        # RAG + CHAT
        ambulon piag-rag-search \
          --collection PNM3_SIREINES \
          --query "$q" \
          --top-k 5 \
          --json > qa_results/q${i}_context.json

        ambulon piag-chat-query \
          --question "$q" \
          --chunks qa_results/q${i}_context.json \
          --output qa_results/q${i}_reponse.md

        echo "✓ Q$i répondu"
      done

  artifacts:
    paths:
      - qa_results/
    expire_in: 7 days
```

### Bonnes Pratiques

| Pratique | Description | Commande |
|----------|-------------|----------|
| **Nommage cohérent** | Utiliser le même préfixe pour identifier le projet | `PNM3_SIREINES` |
| **Extensions filtrées** | Ne charger que les formats pertinents | `--extensions "md,pdf"` |
| **Top-k adaptatif** | 3-5 pour questions simples, 7-10 pour complexes | `--top-k 5` |
| **Reranking** | Améliore la pertinence des résultats | `--rerank true` |
| **Mode hybrid** | Combine recherche sémantique + mots-clés | `--mode hybrid` |
| **Message système** | Guide le comportement du LLM | `--system "Expert SIREINES..."` |

### Debugging : Vérifier la Communication

Si les réponses du CHAT ne sont pas pertinentes :

```bash
# 1. Vérifier que la collection RAG existe et contient des documents
ambulon piag-rag-collection-get --collection PNM3_SIREINES

# 2. Vérifier qu'une recherche retourne des résultats
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "test" \
  --top-k 3

# 3. Vérifier le contenu des chunks retournés
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "architecture" \
  --top-k 3 \
  --json | jq '.chunks[].content'

# 4. Tester le CHAT avec ces chunks
ambulon piag-rag-search \
  --collection PNM3_SIREINES \
  --query "architecture" \
  --json > debug_chunks.json

ambulon piag-chat-query \
  --question "Quelle est l'architecture ?" \
  --chunks debug_chunks.json \
  --output debug_response.md

cat debug_response.md
```

---

## Résumé des commandes

### Commandes RAG

| Commande | Usage | Exemple |
|----------|-------|---------|
| `piag-rag-create` | **Créer collection + uploader documents (RAPIDE)** | `--collection-name "Docs" --directory ./docs --recursive` |
| `piag-rag-collection-add` | Créer une collection | `--name "Docs" --description "..."` |
| `piag-rag-collection-list` | Lister les collections | `--json` |
| `piag-rag-collection-get` | Détails d'une collection | `--collection col_123` |
| `piag-rag-collection-update` | Modifier une collection | `--collection col_123 --description "..."` |
| `piag-rag-collection-rm` | Supprimer une collection | `--collection col_123 --force` |
| `piag-rag-doc-upload` | Uploader un document | `--collection col_123 --file doc.pdf` |
| `piag-rag-doc-list` | Lister les documents | `--collection col_123` |
| `piag-rag-doc-get` | Détails d'un document | `--collection col_123 --document-id doc_456` |
| `piag-rag-doc-chunks` | Récupérer les chunks | `--collection col_123 --document-id doc_456` |
| `piag-rag-doc-rm` | Supprimer un document | `--collection col_123 --document-id doc_456 --force` |
| `piag-rag-search` | Rechercher des chunks | `--collection col_123 --query "..." --top-k 5` |

### Commandes CHAT

| Commande | Usage | Exemple |
|----------|-------|---------|
| `piag-chat-apikey-info` | Infos sur le token | `--chat-token sk-...` |
| `piag-chat-basic-query` | Question simple | `--question "..." --output result.md` |
| `piag-chat-query` | Question avec contexte | `--question "..." --chunks chunks.json` |
| `piag-chat-completion` | Completion legacy | `--prompt "..." --max-tokens 100` |

---

## Liens utiles

- [Documentation API RAG](./API_PIAG_APPEL_RAG.md)
- [Documentation API CHAT](./API_PIAG_APPEL_CHAT.md)
- [Workflow RAG optimal](./PIAG_RAG_WORKFLOW.md)
- [Commandes CHAT détaillées](./PIAG_CHAT_COMMANDS.md)
- [Tests E2E](../tests/integration/)

---

**Note** : Tous les exemples utilisent des IDs et tokens factices. Remplacez-les par vos vraies valeurs de configuration.
