# Workflow RAG Optimal avec PIAG

Ce document explique comment obtenir une bonne réponse RAG en combinant l'API RAG (recherche) et l'API Chat (génération).

## Architecture du RAG

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   QUESTION      │────▶│  API RAG         │────▶│  CHUNKS          │
│   "Quelle est    │     │  (Recherche      │     │  (Contexte       │
│    la proc?"     │     │   sémantique)    │     │   pertinent)     │
└─────────────────┘     └──────────────────┘     └────────┬─────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   RÉPONSE       │◀────│  API CHAT        │◀────│  CONSTRUCTION    │
│   "Selon doc X, │     │  (LLM avec       │     │  DU PROMPT       │
│    la proc..."   │     │   contexte)      │     │  Question+Chunks │
└─────────────────┘     └──────────────────┘     └──────────────────┘
```

## Étapes du workflow

### Étape 1 : Recherche sémantique (API RAG)

Trouver les chunks pertinents dans la collection :

```bash
# Par ID de collection (rapide, pas de résolution)
ambulon piag-rag-search --collection-id 12345 --query "Quelle est la procédure ?" --top-k 5

# Par NOM de collection (résolution automatique vers ID)
ambulon piag-rag-search --collection-name "Documents Techniques" --query "Quelle est la procédure ?" --top-k 5

# Plusieurs collections par ID
ambulon piag-rag-search --collection-id-list "12345,67890" --query "Question ?"

# Plusieurs collections par NOM
ambulon piag-rag-search --collection-name-list "Docs Tech,Docs Métier" --query "Question ?"

# Avec sortie JSON pour traitement automatique
ambulon piag-rag-search --collection-id 12345 --query "Quelle est la procédure ?" --json -o search_results.json
```

**Paramètres importants :**
- `--collection-id` : ID exact (rapide, recommandé pour les scripts)
- `--collection-name` : Nom de la collection (résolution automatique vers ID)
- `--top-k 5` : Récupère les 5 meilleurs chunks (ajuster selon la taille des chunks)
- `--mode hybrid` : Combine recherche sémantique + keywords (défaut)
- `--rerank true` : Réordonne les résultats pour meilleure pertinence

### Étape 2 : Récupération des chunks (API RAG)

#### Option A : Par ID (rapide)

```bash
# Par ID de document et collection (pas de résolution)
ambulon piag-rag-doc-chunks \
  --document-id 67890 \
  --collection-id 12345 \
  --output chunks.json
```

#### Option B : Par nom (résolution automatique)

```bash
# Par NOM de document et collection (résolution automatique vers ID)
ambulon piag-rag-doc-chunks \
  --document-name "manuel_deploiement.pdf" \
  --collection-name "Documents Techniques" \
  --output chunks.json
```

### Étape 3 : Génération avec contexte (API Chat)

#### Méthode A : Directe avec piag-chat-query (recommandée)

Si vous connaissez le document cible (par ID uniquement pour cette commande) :

```bash
# Par ID (seule option supportée par piag-chat-query)
ambulon piag-chat-query \
  --question "Quelle est la procédure de déploiement ?" \
  --doc-id 67890 \
  --collection-id 12345
```

> **Note** : `piag-chat-query` ne supporte que les IDs. Pour utiliser des noms, utilisez d'abord `piag-rag-doc-chunks` puis `piag-chat-query --chunks`.

#### Méthode B : Avec chunks locaux (flexible)

Si vous avez déjà les chunks (exportés, recherchés, ou récupérés par nom) :

```bash
# Récupérer par NOM puis interroger
ambulon piag-rag-doc-chunks \
  --document-name "manuel.pdf" \
  --collection-name "Docs Tech" > chunks.json

ambulon piag-chat-query \
  --question "Quelle est la procédure ?" \
  --chunks chunks.json

# Ou directement depuis la recherche
ambulon piag-rag-search \
  --collection-name "Docs Tech" \
  --query "procédure déploiement" --json > chunks.json

ambulon piag-chat-query \
  --question "Résume la procédure" \
  --chunks chunks.json
```

#### Méthode C : Workflow complet (scripté)

```bash
#!/bin/bash
# rag_workflow.sh

COLLECTION_ID="12345"
QUESTION="Quelle est la procédure de déploiement ?"
TOP_K=5

# 1. Recherche des chunks pertinents
echo "[1/3] Recherche dans la collection..."
ambulon piag-rag-search \
  --collection-id $COLLECTION_ID \
  --query "$QUESTION" \
  --top-k $TOP_K \
  --json > /tmp/rag_chunks.json

# 2. Interrogation du LLM avec contexte
echo "[2/3] Génération de la réponse..."
ambulon piag-chat-query \
  --question "$QUESTION" \
  --chunks /tmp/rag_chunks.json \
  --output reponse.md

echo "[3/3] Terminé ! Réponse dans reponse.md"
```

## Construction optimale du prompt RAG

### Format des messages pour l'API Chat

```json
[
  {"role": "user", "content": "Quelle est la procédure de déploiement ?"},
  {"role": "user", "content": "Contexte 1: [Contenu du chunk 1]"},
  {"role": "user", "content": "Contexte 2: [Contenu du chunk 2]"},
  {"role": "user", "content": "Contexte 3: [Contenu du chunk 3]"}
]
```

### Bonnes pratiques

1. **Limiter le nombre de chunks** : 
   - Trop peu (1-2) : manque de contexte
   - Trop (>10) : surcharge le contexte, coût élevé
   - Optimal : 3-7 chunks pertinents

2. **Ordre des chunks** :
   - Ordre de pertinence (meilleur d'abord)
   - Ou ordre chronologique si temporalité importante

3. **Formatage du contexte** :
   ```
   Source: [Nom du document]
   ---
   [Contenu du chunk]
   ```

4. **Instruction système (optionnelle)** :
   ```bash
   ambulon piag-chat-basic-query \
     --system "Tu es un assistant technique. Réponds uniquement à partir du contexte fourni." \
     --question "..."
   ```

## Exemples concrets

### Exemple 1 : Question sur une procédure (par ID)

```bash
# Recherche par ID
ambulon piag-rag-search \
  --collection-id "PnuQzUEmwRDkxZPX" \
  --query "procédure déploiement application" \
  --top-k 5 \
  --json > chunks.json

# Génération
ambulon piag-chat-query \
  --question "Résume la procédure de déploiement en 3 étapes" \
  --chunks chunks.json \
  --output procedure.md
```

### Exemple 1b : Question sur une procédure (par nom)

```bash
# Recherche par nom de collection
ambulon piag-rag-search \
  --collection-name "Documents Techniques" \
  --query "procédure déploiement application" \
  --top-k 5 \
  --json > chunks.json

# Génération (même commande)
ambulon piag-chat-query \
  --question "Résume la procédure de déplédure" \
  --chunks chunks.json \
  --output procedure.md
```

### Exemple 2 : Analyse de code

#### Par ID (rapide, pour les scripts)
```bash
# Récupérer les chunks d'un document spécifique
ambulon piag-rag-doc-chunks \
  --document-id "doc_123" \
  --collection-id "col_456" > code_chunks.json

# Poser une question sur le code
ambulon piag-chat-query \
  --question "Explique ce que fait la fonction principale" \
  --chunks code_chunks.json
```

#### Par nom (interactif, plus convivial)
```bash
# Récupérer par nom de fichier et collection
ambulon piag-rag-doc-chunks \
  --document-name "main.py" \
  --collection-name "Code Source API" > code_chunks.json

# Poser une question sur le code
ambulon piag-chat-query \
  --question "Explique ce que fait la fonction principale" \
  --chunks code_chunks.json
```

### Exemple 3 : Comparaison de documents

```bash
# Recherche dans plusieurs collections
ambulon piag-rag-search -c "col_1" -q "architecture" --json > archi_1.json
ambulon piag-rag-search -c "col_2" -q "architecture" --json > archi_2.json

# Combiner les résultats et demander une comparaison
# (nécessite une étape de fusion des JSON)
ambulon piag-chat-basic-query \
  --question "Compare les deux architectures décrites dans le contexte" \
  --system "Tu es un architecte logiciel senior."
```

## Optimisation des résultats

### Si la réponse est imprécise :

1. **Augmenter top-k** : Passer de 5 à 10 chunks
2. **Vérifier la qualité des chunks** : Sont-ils assez grands ? (min 100-200 mots)
3. **Affiner la question** : Plus spécifique = meilleure récupération
4. **Utiliser le reranking** : `--rerank true` dans piag-rag-search

### Si la réponse est trop longue :

```bash
# Limiter dans la question
ambulon piag-chat-query \
  --question "Réponds en 2 phrases max : quelle est la procédure ?" \
  --chunks chunks.json
```

### Si la réponse est hors sujet :

```bash
# Ajouter une instruction système stricte
ambulon piag-chat-basic-query \
  --system "Tu dois répondre UNIQUEMENT à partir des documents fournis. Si tu ne trouves pas la réponse, dis 'Information non trouvée dans le contexte'." \
  --question "..."
```

## Commandes disponibles

| Commande | Rôle | API | Support |
|----------|------|-----|---------|
| `piag-rag-search` | Recherche sémantique | RAG | `--collection-id` ou `--collection-name` (résolution auto) |
| `piag-rag-doc-chunks` | Récupération chunks d'un doc | RAG | `--document-id/--collection-id` ou `--document-name/--collection-name` |
| `piag-chat-query` | Chat avec contexte RAG | Chat | `--doc-id` + `--collection-id` **(ID uniquement)** |
| `piag-chat-basic-query` | Chat simple (sans contexte) | Chat | Pas de référence à collection/document |

### Résumé : ID vs Nom

| Approche | Avantage | Inconvénient | Commandes supportées |
|----------|----------|--------------|-------------------|
| **ID** (`--*-id`) | Rapide, pas de résolution, fiable pour les scripts | Difficile à retenir, nécessite de lister d'abord | Toutes |
| **Nom** (`--*-name`) | Lisible, intuitif, pas besoin de connaître l'ID | Nécessite une requête de résolution supplémentaire | `piag-rag-search`, `piag-rag-doc-chunks` |

> **Astuce** : Pour `piag-chat-query` qui ne supporte que les IDs, utilisez le workflow :
> ```bash
> # 1. Récupérer par NOM avec piag-rag-doc-chunks
> ambulon piag-rag-doc-chunks --document-name "fichier.pdf" --collection-name "Docs" > chunks.json
> # 2. Utiliser --chunks avec piag-chat-query
> ambulon piag-chat-query --question "..." --chunks chunks.json
> ```

## Débogage

### Vérifier les chunks récupérés :

```bash
# Voir les chunks avant envoi au LLM
ambulon piag-rag-search --collection-id X --query "..." --json | jq '.results[].content'
```

### Tester sans RAG (baseline) :

```bash
# Comparer avec et sans contexte
ambulon piag-chat-basic-query --question "Quelle est la procédure ?"
# vs
ambulon piag-chat-query --question "Quelle est la procédure ?" --chunks chunks.json
```

## Astuce : Workflow intégré

### Par ID (rapide)

La commande `piag-chat-query` avec `--doc-id` fait automatiquement les étapes 1 et 2 :

```bash
# Cette commande fait : récupération des chunks + génération
ambulon piag-chat-query \
  --question "Quelle est la procédure ?" \
  --doc-id 67890 \
  --collection-id 12345
```

**Quand l'utiliser ?**
- ✅ Vous connaissez déjà l'ID du document
- ✅ Un seul document contient la réponse

### Par nom (avec résolution automatique)

Comme `piag-chat-query` ne supporte que les IDs, utilisez ce workflow :

```bash
# 1. Récupérer les chunks par nom
ambulon piag-rag-doc-chunks \
  --document-name "manuel_deploiement.pdf" \
  --collection-name "Documents Techniques" \
  --output chunks.json

# 2. Générer la réponse
ambulon piag-chat-query \
  --question "Quelle est la procédure ?" \
  --chunks chunks.json
```

**Quand utiliser le workflow manuel (rag_workflow.bat) ?**
- 🔍 Vous ne savez pas quel document contient la réponse
- 🔍 La réponse est répartie sur plusieurs documents
- 🔍 Besoin de rechercher dans toute la collection
- 🔍 Vous préférez utiliser les noms plutôt que les IDs

## Références

- API RAG : `doc/API_PIAG_APPEL_RAG.md`
- API Chat : `doc/API_PIAG_APPEL_CHAT.md`
- Commandes Chat : `doc/PIAG_CHAT_COMMANDS.md`
