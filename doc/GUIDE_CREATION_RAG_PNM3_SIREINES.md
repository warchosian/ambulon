# Guide Complet : Création RAG PNM3_SIREINES de A à Z

**Date de création** : 2026-03-22
**Version** : 3.1.0+
**Objectif** : Créer une collection RAG complète avec documents SIREINES et interroger via CHAT

---

## 📋 Vue d'ensemble du workflow

Ce guide décrit comment créer de bout en bout un système RAG fonctionnel pour le projet SIREINES :

```
┌─────────────────────────────────────────────────────────────────────┐
│                   WORKFLOW COMPLET RAG SIREINES                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Vérification configuration                                      │
│  2. Création collection PNM3_SIREINES                               │
│  3. Upload documents (applications\sireines.rag\)                   │
│  4. Attente indexation                                              │
│  5. Vérification collection                                         │
│  6. Recherche RAG → chunks\PNM3_SIREINES\chunks.json                │
│  7. Préparation question depuis sireines.dat_c4model.md             │
│  8. Génération réponse CHAT                                         │
│  9. Vérification résultats                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Prérequis

### Structure des répertoires

```
ambulon/
├── applications/
│   └── sireines.rag/              ← Documents sources
│       ├── sireines.dat.md
│       ├── sireines.dat_c4model.md
│       ├── sireines.components.md
│       ├── sireines.wiki.md
│       └── ... (autres fichiers .md et .pdf)
├── chunks/                        ← À créer
│   └── PNM3_SIREINES/             ← Sera créé automatiquement
│       └── chunks.json
├── config/
│   └── piag.yaml                  ← Configuration
└── questions/                     ← À créer
    └── question_dat_c4.txt
```

### Configuration requise (config/piag.yaml)

```yaml
piag:
  rag:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
      timeout: 120
    security:
      token: "eyJhbGci..."  # Votre token JWT RAG
    project:
      project_id: "PnuQzUEmwRDkxZPX"

  chat:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions"
      timeout: 60
    security:
      token: "sk-iyksvRDQanhNZ6O7MJCQbA"  # Votre token LiteLLM
    model: "mte-api-piag-mistral-medium-latest"
```

---

## 🚀 ÉTAPE 1 : Vérification de la configuration

### 1.1 Vérifier que la config est valide

```bash
# Afficher la config actuelle
cat config/piag.yaml
```

**Vérifications** :
- ✅ Token RAG présent (`eyJ...`)
- ✅ Token CHAT présent (`sk-...`)
- ✅ Project ID présent
- ✅ URLs correctes

### 1.2 Vérifier les documents sources

```bash
# Lister les fichiers à indexer
ls -lh applications/sireines.rag/

# Compter les fichiers
ls applications/sireines.rag/*.md | wc -l
ls applications/sireines.rag/*.pdf | wc -l
```

**Attendu** : Au moins 10-30 fichiers (Markdown et PDF)

### 1.3 Tester la connexion API

```bash
# Tester l'API RAG
ambulon piag-rag-collection-list
```

**Sortie attendue** :
```
Collections disponibles dans le projet PnuQzUEmwRDkxZPX:
  1. collection_test (ID: xyz123)
  ...
```

---

## 🏗️ ÉTAPE 2 : Création de la collection RAG

### 2.1 Vérifier si la collection existe déjà

```bash
ambulon piag-rag-collection-list | grep PNM3_SIREINES
```

**Si la collection existe** :
```bash
# Supprimer l'ancienne (optionnel)
ambulon piag-rag-collection-rm --collection-name PNM3_SIREINES
```

### 2.2 Créer la nouvelle collection

```bash
ambulon piag-rag-collection-add \
  --name "PNM3_SIREINES" \
  --description "Documentation complète SIREINES : DAT, C4, Composants, Wiki, ISO25010"
```

**Sortie attendue** :
```
✅ Collection créée avec succès
   Nom : PNM3_SIREINES
   ID  : AbCd1234EfGh5678
   Description : Documentation complète SIREINES...
```

**💾 NOTER L'ID DE LA COLLECTION** pour référence ultérieure

### 2.3 Vérifier la création

```bash
ambulon piag-rag-collection-get --collection-name PNM3_SIREINES
```

**Sortie attendue** :
```json
{
  "id": "AbCd1234EfGh5678",
  "name": "PNM3_SIREINES",
  "description": "Documentation complète SIREINES...",
  "created_at": "2026-03-22T...",
  "document_count": 0
}
```

---

## 📤 ÉTAPE 3 : Upload des documents

### 3.1 Compter les documents à uploader

```bash
ls applications/sireines.rag/*.{md,pdf} 2>/dev/null | wc -l
```

**Attendu** : Exemple : 31 fichiers

### 3.2 Upload de tous les documents

```bash
ambulon piag-rag-doc-upload \
  --collection-name PNM3_SIREINES \
  --folder applications/sireines.rag
```

**Sortie attendue** :
```
Fichiers trouvés dans applications/sireines.rag: 31

Téléversement de: sireines.dat.md... ✓
Téléversement de: sireines.dat_c4model.md... ✓
Téléversement de: sireines.components.md... ✓
...

============================================================
Récapitulatif:
  Fichiers traités: 31
  Succès: 31
  Erreurs: 0
============================================================
```

**⚠️ Si erreur "Document existe déjà"** :

```bash
# Option A : Remplacer tous les documents
ambulon piag-rag-doc-upload \
  --collection-name PNM3_SIREINES \
  --folder applications/sireines.rag \
  --if-exists replace

# Option B : Ignorer les doublons
ambulon piag-rag-doc-upload \
  --collection-name PNM3_SIREINES \
  --folder applications/sireines.rag \
  --if-exists skip
```

### 3.3 Vérifier l'upload

```bash
# Lister les documents uploadés
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES
```

**Sortie attendue** :
```
Documents dans la collection PNM3_SIREINES:
  1. sireines.dat.md (ID: doc_001)
  2. sireines.dat_c4model.md (ID: doc_002)
  3. sireines.components.md (ID: doc_003)
  ...
  31. sireines.wiki.md (ID: doc_031)

Total: 31 documents
```

---

## ⏳ ÉTAPE 4 : Attente de l'indexation

**IMPORTANT** : L'indexation des documents prend du temps (30s à 2 minutes selon le volume)

### 4.1 Attendre l'indexation

```bash
# Attendre 60 secondes
echo "Attente de l'indexation (60 secondes)..."
sleep 60
```

Ou manuellement :
```
⏰ Pause de 1-2 minutes pour laisser l'API indexer les documents
```

### 4.2 Vérifier l'état de la collection

```bash
ambulon piag-rag-collection-get --collection-name PNM3_SIREINES
```

**Vérifier** :
- `"document_count": 31` (ou le nombre attendu)
- `"status": "ready"` (si disponible)

---

## 🔍 ÉTAPE 5 : Vérification de la collection

### 5.1 Compter les documents indexés

```bash
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES | grep "Total:"
```

**Attendu** : `Total: 31 documents`

### 5.2 Vérifier un document spécifique

```bash
ambulon piag-rag-doc-get \
  --collection-name PNM3_SIREINES \
  --doc-name sireines.dat_c4model.md
```

**Sortie attendue** :
```json
{
  "id": "doc_002",
  "name": "sireines.dat_c4model.md",
  "collection_id": "AbCd1234EfGh5678",
  "created_at": "2026-03-22T...",
  "size": 45678,
  "status": "indexed"
}
```

### 5.3 Vérifier les chunks d'un document

```bash
ambulon piag-rag-doc-chunks \
  --collection-name PNM3_SIREINES \
  --doc-name sireines.dat_c4model.md
```

**Sortie attendue** :
```
Chunks du document 'sireines.dat_c4model.md':

[Chunk 1/15]
L'architecture de SIREINES repose sur le modèle C4...

[Chunk 2/15]
Le diagramme de contexte (C4 Level 1) montre...

...

Total: 15 chunks
```

---

## 📦 ÉTAPE 6 : Recherche RAG et création des chunks

### 6.1 Créer le répertoire chunks

```bash
mkdir -p chunks/PNM3_SIREINES
```

### 6.2 Effectuer la recherche RAG

```bash
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  --query "architecture,dat" \
  --top-k 10 \
  -o chunks/PNM3_SIREINES/chunks.json
```

**Sortie attendue** :
```
[INFO] Recherche RAG en cours dans 1 collection(s)...
[INFO] (Cela peut prendre jusqu'à 2 minutes selon le volume de données)
[INFO] Recherche terminée.

✅ Résultats sauvegardés dans: chunks/PNM3_SIREINES/chunks.json
   10 chunk(s) récupéré(s)
```

### 6.3 Vérifier le fichier chunks créé

```bash
# Vérifier l'existence
ls -lh chunks/PNM3_SIREINES/chunks.json

# Afficher un aperçu
head -n 30 chunks/PNM3_SIREINES/chunks.json
```

**Structure attendue** :
```json
{
  "chunks": [
    {
      "text": "L'architecture technique de SIREINES est définie dans le DAT...",
      "score": 0.95,
      "document_id": "doc_002",
      "document_name": "sireines.dat_c4model.md",
      "metadata": {...}
    },
    {
      "text": "Le document d'architecture technique (DAT) décrit...",
      "score": 0.89,
      "document_id": "doc_001",
      "document_name": "sireines.dat.md",
      "metadata": {...}
    },
    ...
  ]
}
```

### 6.4 Compter les chunks récupérés

```bash
# Compter les chunks dans le JSON
cat chunks/PNM3_SIREINES/chunks.json | jq '.chunks | length'
```

**Attendu** : `10` (selon --top-k)

---

## ❓ ÉTAPE 7 : Préparation de la question depuis le fichier

### 7.1 Créer le répertoire questions

```bash
mkdir -p questions
```

### 7.2 Créer la question depuis le contenu du DAT C4

**Option A : Extraire une section du document**

```bash
# Extraire les 20 premières lignes du DAT C4
head -n 20 applications/sireines.rag/sireines.dat_c4model.md > questions/question_dat_c4.txt
```

**Option B : Créer une question personnalisée inspirée du document**

```bash
cat > questions/question_dat_c4.txt <<'EOF'
Analyse détaillée du Dossier d'Architecture Technique (DAT) de SIREINES :

En te basant sur les extraits du DAT et du modèle C4, réponds aux questions suivantes :

1. Quelle est l'architecture globale de SIREINES (pattern architectural, frameworks) ?
2. Quels sont les principaux composants techniques identifiés dans le C4 Level 3 ?
3. Quelles technologies de base de données sont utilisées et pourquoi ?
4. Comment est organisée la couche de présentation (frontend) ?
5. Quelles sont les dépendances externes principales ?
6. Y a-t-il des décisions architecturales critiques documentées (ADR) ?
7. Quels sont les flux de données principaux entre composants ?

Fournis une réponse structurée en te basant UNIQUEMENT sur les informations des extraits fournis.
EOF
```

### 7.3 Vérifier le fichier question

```bash
# Afficher le contenu
cat questions/question_dat_c4.txt

# Vérifier la taille
wc -l questions/question_dat_c4.txt
```

---

## 💬 ÉTAPE 8 : Génération de la réponse CHAT

### 8.1 Créer le répertoire de sortie

```bash
mkdir -p reponses/PNM3_SIREINES
```

### 8.2 Exécuter la requête CHAT

```bash
ambulon piag-chat-query \
  --question-file questions/question_dat_c4.txt \
  --chunks chunks/PNM3_SIREINES/chunks.json \
  -o reponses/PNM3_SIREINES/reponse_architecture_dat.md
```

**Sortie attendue** :
```
Question chargée depuis: questions/question_dat_c4.txt
Chargement des chunks...
10 chunks chargés
Appel de l'API PIAG...
Réponse sauvegardée dans: reponses/PNM3_SIREINES/reponse_architecture_dat.md
```

### 8.3 Vérifier la réponse générée

```bash
# Afficher les premières lignes
head -n 50 reponses/PNM3_SIREINES/reponse_architecture_dat.md
```

**Contenu attendu** :
```markdown
# Analyse Architecture Technique SIREINES

## 1. Architecture globale

SIREINES utilise une architecture MVC basée sur :
- **Framework métier** : Vertigo Framework pour la couche service
- **Frontend** : Struts 2 pour la couche présentation
- **Pattern** : Architecture en couches (Présentation → Métier → Persistance)

Source : [Extrait 1] du document sireines.dat_c4model.md

## 2. Composants techniques (C4 Level 3)

Les composants principaux identifiés sont :
...
```

---

## ✅ ÉTAPE 9 : Vérification des résultats

### 9.1 Vérifier la structure complète

```bash
tree -L 3 --charset ascii
```

**Structure attendue** :
```
ambulon/
├── applications/
│   └── sireines.rag/
│       ├── sireines.dat.md
│       ├── sireines.dat_c4model.md
│       └── ... (31 fichiers)
├── chunks/
│   └── PNM3_SIREINES/
│       └── chunks.json (10 chunks)
├── questions/
│   └── question_dat_c4.txt
└── reponses/
    └── PNM3_SIREINES/
        └── reponse_architecture_dat.md
```

### 9.2 Statistiques finales

```bash
echo "=== STATISTIQUES FINALES ==="
echo ""
echo "Documents sources:"
ls applications/sireines.rag/*.{md,pdf} 2>/dev/null | wc -l

echo ""
echo "Documents indexés:"
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES | grep "Total:"

echo ""
echo "Chunks récupérés:"
cat chunks/PNM3_SIREINES/chunks.json | jq '.chunks | length'

echo ""
echo "Taille de la réponse:"
wc -w reponses/PNM3_SIREINES/reponse_architecture_dat.md
```

### 9.3 Vérifier la qualité de la réponse

**Critères de validation** :

- ✅ La réponse fait référence aux extraits fournis
- ✅ Les informations sont factuelles (pas d'hallucinations)
- ✅ La réponse répond aux questions posées
- ✅ Des numéros d'extraits sont cités (`[Extrait 1]`, etc.)
- ✅ La réponse est structurée et lisible

```bash
# Vérifier les références aux extraits
grep -c "\[Extrait" reponses/PNM3_SIREINES/reponse_architecture_dat.md
```

**Attendu** : Au moins 5-10 références aux extraits

---

## 🔄 Script complet automatisé

Pour rejouer tout le workflow en une seule commande :

```bash
cat > workflow_complet_sireines.sh <<'SCRIPT'
#!/bin/bash
set -e

echo "========================================"
echo "  WORKFLOW COMPLET RAG PNM3_SIREINES"
echo "========================================"
echo ""

# Étape 1
echo "ÉTAPE 1/9 : Vérification configuration"
if [ ! -f config/piag.yaml ]; then
    echo "❌ Fichier config/piag.yaml introuvable"
    exit 1
fi
echo "✓ Configuration OK"
echo ""

# Étape 2
echo "ÉTAPE 2/9 : Création collection"
ambulon piag-rag-collection-add \
  --name "PNM3_SIREINES" \
  --description "Documentation complète SIREINES" 2>/dev/null || echo "Collection existe déjà"
echo ""

# Étape 3
echo "ÉTAPE 3/9 : Upload documents"
ambulon piag-rag-doc-upload \
  --collection-name PNM3_SIREINES \
  --folder applications/sireines.rag \
  --if-exists skip
echo ""

# Étape 4
echo "ÉTAPE 4/9 : Attente indexation (60s)"
sleep 60
echo ""

# Étape 5
echo "ÉTAPE 5/9 : Vérification collection"
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES | grep "Total:"
echo ""

# Étape 6
echo "ÉTAPE 6/9 : Recherche RAG"
mkdir -p chunks/PNM3_SIREINES
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  --query "architecture,dat" \
  --top-k 10 \
  -o chunks/PNM3_SIREINES/chunks.json
echo ""

# Étape 7
echo "ÉTAPE 7/9 : Préparation question"
mkdir -p questions
cat > questions/question_dat_c4.txt <<'EOF'
Analyse l'architecture technique de SIREINES en te basant sur le DAT et le modèle C4.
Décris les composants principaux, les technologies utilisées, et les flux de données.
EOF
echo "✓ Question créée"
echo ""

# Étape 8
echo "ÉTAPE 8/9 : Génération réponse CHAT"
mkdir -p reponses/PNM3_SIREINES
ambulon piag-chat-query \
  --question-file questions/question_dat_c4.txt \
  --chunks chunks/PNM3_SIREINES/chunks.json \
  -o reponses/PNM3_SIREINES/reponse_architecture_dat.md
echo ""

# Étape 9
echo "ÉTAPE 9/9 : Vérifications finales"
echo "Documents sources: $(ls applications/sireines.rag/*.{md,pdf} 2>/dev/null | wc -l)"
echo "Chunks récupérés: $(cat chunks/PNM3_SIREINES/chunks.json | jq '.chunks | length')"
echo "Taille réponse: $(wc -w < reponses/PNM3_SIREINES/reponse_architecture_dat.md) mots"
echo ""

echo "========================================"
echo "  ✅ WORKFLOW TERMINÉ AVEC SUCCÈS"
echo "========================================"
echo ""
echo "Fichiers générés:"
echo "  • chunks/PNM3_SIREINES/chunks.json"
echo "  • questions/question_dat_c4.txt"
echo "  • reponses/PNM3_SIREINES/reponse_architecture_dat.md"
SCRIPT

chmod +x workflow_complet_sireines.sh
```

**Usage** :
```bash
./workflow_complet_sireines.sh
```

---

## 🐛 Dépannage

### Problème : "Collection non trouvée"

```bash
# Lister toutes les collections
ambulon piag-rag-collection-list

# Recréer la collection
ambulon piag-rag-collection-add --name PNM3_SIREINES --description "..."
```

### Problème : "Document existe déjà"

```bash
# Option 1 : Supprimer tous les documents
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES | \
  grep "ID:" | \
  awk '{print $NF}' | \
  xargs -I {} ambulon piag-rag-doc-rm --collection-name PNM3_SIREINES --doc-id {}

# Option 2 : Utiliser --if-exists replace
ambulon piag-rag-doc-upload --folder applications/sireines.rag --if-exists replace
```

### Problème : "Aucun chunk trouvé"

```bash
# Vérifier l'indexation
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES

# Attendre plus longtemps
sleep 120

# Réessayer la recherche
ambulon piag-rag-search --collection-name PNM3_SIREINES -q "architecture,dat" -o chunks.json
```

### Problème : "Token invalide"

```bash
# Vérifier les tokens dans config/piag.yaml
cat config/piag.yaml | grep token

# Format attendu:
# RAG token : eyJhbGci... (JWT)
# CHAT token : sk-... (LiteLLM)
```

---

## 📊 Checklist de validation

Avant de considérer le workflow comme terminé, vérifier :

- [ ] Configuration YAML valide avec tokens corrects
- [ ] Collection `PNM3_SIREINES` créée
- [ ] 31 documents uploadés et indexés
- [ ] Fichier `chunks/PNM3_SIREINES/chunks.json` créé avec 10 chunks
- [ ] Fichier `questions/question_dat_c4.txt` créé
- [ ] Fichier `reponses/PNM3_SIREINES/reponse_architecture_dat.md` créé
- [ ] La réponse contient des références aux extraits (`[Extrait N]`)
- [ ] La réponse est cohérente avec les documents sources
- [ ] Aucune hallucination détectée

---

## 📚 Références

- **Workflow RAG + CHAT** : `doc/PIAG_WORKFLOW_RAG_CHAT.md`
- **API RAG** : `doc/API_PIAG_APPEL_RAG.md`
- **API CHAT** : `doc/API_PIAG_APPEL_CHAT.md`
- **Tests RAG** : `doc/TESTS_PIAG.md`

---

## 🔄 Historique

| Date | Version | Changements |
|------|---------|-------------|
| 2026-03-22 | 1.0 | Création du guide complet étape par étape |

---

**Auteur** : Équipe Ambulon
**Dernière mise à jour** : 2026-03-22
