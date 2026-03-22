# Workflow PIAG : Recherche RAG + Génération CHAT (2 phases)

**Date de création** : 2026-03-22
**Version** : 3.1.0+

---

## 📋 Vue d'ensemble

Ce document décrit le workflow rigoureux en **2 phases distinctes** pour utiliser les APIs PIAG RAG et CHAT de manière conforme aux spécifications officielles.

**Principe fondamental** : Les APIs RAG et CHAT sont **séparées** et **indépendantes**. L'API CHAT ne connaît pas la notion de "collection" - cette fonctionnalité appartient exclusivement à l'API RAG.

---

## 🔄 Architecture du Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 1 : RAG SEARCH                     │
├─────────────────────────────────────────────────────────────┤
│  Commande : ambulon piag-rag-search                         │
│  API      : https://preprod.api.piag.e2.rie.gouv.fr/rag/   │
│  Token    : JWT (eyJhbGci...)                               │
│  Input    : --collection-name + --query                     │
│  Output   : chunks.json (fichier JSON avec les extraits)    │
└─────────────────────────────────────────────────────────────┘
                              ↓
                     chunks.json (fichier)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2 : CHAT QUERY                     │
├─────────────────────────────────────────────────────────────┤
│  Commande : ambulon piag-chat-query                         │
│  API      : .../v1/chat/completions                         │
│  Token    : LiteLLM (sk-...)                                │
│  Input    : --question + --chunks chunks.json               │
│  Output   : reponse.md (réponse du LLM avec contexte RAG)   │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Phase 1 : Recherche RAG

### Commande

```bash
ambulon piag-rag-search \
  --collection-name <NOM_COLLECTION> \
  --query "<question_de_recherche>" \
  --output <fichier_sortie.json>
```

### Arguments principaux

| Argument | Alias | Description | Obligatoire |
|----------|-------|-------------|-------------|
| `--collection-name` | - | Nom de la collection RAG | Oui (ou --collection-id) |
| `--collection-id` | - | ID exact de la collection (plus rapide) | Oui (ou --collection-name) |
| `--query` | `-q` | Question de recherche | Oui |
| `--output` | `-o` | Fichier JSON de sortie pour les chunks | Recommandé |
| `--top-k` | - | Nombre de résultats (défaut: 10) | Non |
| `--project-id` | - | ID du projet (depuis config sinon) | Non |
| `--token` | - | Token API RAG (depuis config sinon) | Non |
| `--format` | - | Format de sortie: json ou text (défaut: text) | Non |

### Exemple complet

```bash
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  -q "architecture technique et composants" \
  -o chunks.json \
  --top-k 5
```

### Sortie attendue

```
[INFO] Recherche RAG en cours dans 1 collection(s)...
[INFO] (Cela peut prendre jusqu'à 2 minutes selon le volume de données)
[INFO] Recherche terminée.

✅ Résultats sauvegardés dans: chunks.json
   5 chunk(s) récupéré(s)
```

### Format du fichier chunks.json

```json
{
  "chunks": [
    {
      "text": "SIREINES utilise le framework Vertigo pour la couche métier...",
      "score": 0.95,
      "document_id": "doc_123",
      "metadata": {...}
    },
    {
      "text": "L'architecture repose sur PostgreSQL 15.2 et Elasticsearch 7.x...",
      "score": 0.89,
      "document_id": "doc_456",
      "metadata": {...}
    }
  ]
}
```

---

## 💬 Phase 2 : Génération CHAT

### Commande

```bash
ambulon piag-chat-query \
  --question "<question_utilisateur>" \
  --chunks <fichier_chunks.json> \
  --output <fichier_reponse.md>
```

### Arguments principaux

| Argument | Alias | Description | Obligatoire |
|----------|-------|-------------|-------------|
| `--question` | `-q`, `--query` | Question en texte direct | Oui (ou --question-file) |
| `--question-file` | - | Fichier texte contenant la question | Oui (ou --question) |
| `--chunks` | `-c` | Fichier JSON de chunks (depuis RAG) | Oui (ou --chunks-dir) |
| `--chunks-dir` | `-d` | Répertoire contenant des fichiers de chunks | Oui (ou --chunks) |
| `--output` | `-o` | Fichier de sortie pour la réponse | Recommandé |
| `--model` | - | Modèle LLM (défaut: mistral-medium) | Non |
| `--chat-token` | - | Token API CHAT (depuis config sinon) | Non |

### Exemple avec question directe

```bash
ambulon piag-chat-query \
  -q "Quelle est l'architecture de SIREINES ?" \
  --chunks chunks.json \
  -o reponse.md
```

### Exemple avec fichier de question

**1. Créer le fichier question :**
```bash
echo "Quelle est l'architecture technique de SIREINES et quels sont ses principaux composants ?" > question.txt
```

**2. Exécuter la requête :**
```bash
ambulon piag-chat-query \
  --question-file question.txt \
  --chunks chunks.json \
  -o reponse.md
```

### Sortie attendue

```
Question chargée depuis: question.txt
Chargement des chunks...
5 chunks chargés
Appel de l'API PIAG...
Réponse sauvegardée dans: reponse.md
```

---

## 🚀 Workflow Complet : Exemples Pratiques

### Exemple 1 : Question simple

```bash
# Phase 1: Récupérer les chunks
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  -q "architecture" \
  -o chunks.json

# Phase 2: Générer la réponse
ambulon piag-chat-query \
  -q "Quelle est l'architecture de SIREINES ?" \
  -c chunks.json \
  -o reponse.md
```

### Exemple 2 : Question complexe avec fichier

```bash
# Créer le fichier de question
cat > question_complexe.txt <<EOF
Analyse l'architecture technique de SIREINES en détaillant :
1. Les composants Java principaux
2. Les technologies de base de données
3. Les frameworks utilisés
4. Les vulnérabilités CVE identifiées
EOF

# Phase 1: Récupérer plus de chunks (top-10)
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  -q "architecture composants CVE" \
  --top-k 10 \
  -o chunks_complets.json

# Phase 2: Générer la réponse
ambulon piag-chat-query \
  --question-file question_complexe.txt \
  -c chunks_complets.json \
  -o analyse_complete.md
```

### Exemple 3 : Utiliser un modèle différent

```bash
# Phase 1: RAG (identique)
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  -q "sécurité STRIDE" \
  -o chunks.json

# Phase 2: CHAT avec modèle Large
ambulon piag-chat-query \
  -q "Analyse les vulnérabilités STRIDE de SIREINES" \
  -c chunks.json \
  --model mte-api-piag-mistral-large-latest \
  -o analyse_securite.md
```

### Exemple 4 : Plusieurs questions sur les mêmes chunks

```bash
# Phase 1: Récupérer les chunks UNE SEULE FOIS
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  -q "architecture sécurité performance" \
  --top-k 15 \
  -o chunks_generaux.json

# Phase 2a: Question architecture
ambulon piag-chat-query \
  -q "Quelle est l'architecture ?" \
  -c chunks_generaux.json \
  -o reponse_archi.md

# Phase 2b: Question sécurité
ambulon piag-chat-query \
  -q "Quelles sont les vulnérabilités ?" \
  -c chunks_generaux.json \
  -o reponse_secu.md

# Phase 2c: Question performance
ambulon piag-chat-query \
  -q "Quelles sont les optimisations de performance ?" \
  -c chunks_generaux.json \
  -o reponse_perf.md
```

---

## 🔧 Configuration

### Fichier config/piag.yaml

```yaml
piag:
  rag:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/rag/"
      timeout: 120
    security:
      token: "eyJhbGci..."  # Token JWT pour RAG
    project:
      project_id: "PnuQzUEmwRDkxZPX"
      collection_name: "PNM3_SIREINES"
    search:
      top_k: 10
      mode: "hybrid"

  chat:
    api:
      base_url: "https://preprod.api.piag.e2.rie.gouv.fr/v1/chat/completions"
      timeout: 60
    security:
      token: "sk-iyksvRDQanhNZ6O7MJCQbA"  # Token LiteLLM pour CHAT
    model: "mte-api-piag-mistral-medium-latest"
```

### Variables d'environnement

**Pour RAG :**
- `PIAG_RAG_API_TOKEN` : Token API RAG
- `PIAG_RAG_PROJECT_ID` : ID du projet
- `PIAG_RAG_COLLECTION_NAME` : Nom de collection par défaut
- `PIAG_RAG_BASE_URL` : URL de base API RAG

**Pour CHAT :**
- `PIAG_CHAT_API_TOKEN` : Token API CHAT (format `sk-...`)

---

## ⚠️ Points d'attention

### 1. Séparation rigoureuse RAG / CHAT

❌ **N'existe PAS** :
```bash
# Cette commande n'existe pas et ne doit pas exister
ambulon piag-chat-query --collection-name PNM3_SIREINES -q "question"
```

✅ **Correct** :
```bash
# 2 phases distinctes
ambulon piag-rag-search --collection-name PNM3_SIREINES -q "question" -o chunks.json
ambulon piag-chat-query -q "question" --chunks chunks.json
```

### 2. Tokens différents

- **API RAG** : Token JWT (commence par `eyJ...`)
- **API CHAT** : Token LiteLLM (commence par `sk-...`)

Ne pas les confondre !

### 3. Format des chunks

Le fichier `chunks.json` produit par `piag-rag-search` est **directement compatible** avec `piag-chat-query`.

### 4. Réutilisation des chunks

Les chunks récupérés peuvent être réutilisés pour **plusieurs questions** différentes (voir Exemple 4).

---

## 📊 Avantages de ce workflow

### Clarté architecturale
- Chaque API reste dans son périmètre fonctionnel
- Conformité totale avec la documentation officielle PIAG
- Traçabilité complète des étapes

### Performance
- Les chunks peuvent être réutilisés
- Pas de recherche RAG inutile si les chunks sont déjà disponibles
- Possibilité de paralléliser les requêtes CHAT

### Flexibilité
- Plusieurs questions sur les mêmes chunks
- Changement de modèle LLM sans refaire le RAG
- Modification de la question sans refaire la recherche

### Débogage
- Inspection facile des chunks intermédiaires
- Logs séparés pour chaque phase
- Possibilité de rejouer une phase sans l'autre

---

## 📝 Scripts d'automatisation

### Script Bash complet

```bash
#!/bin/bash
# workflow_rag_chat.sh

COLLECTION="PNM3_SIREINES"
SEARCH_QUERY="$1"
QUESTION="$2"
OUTPUT="${3:-reponse.md}"

if [ -z "$SEARCH_QUERY" ] || [ -z "$QUESTION" ]; then
    echo "Usage: $0 <search_query> <question> [output_file]"
    echo "Exemple: $0 'architecture' 'Quelle est l'architecture ?' reponse.md"
    exit 1
fi

echo "Phase 1/2 : Recherche RAG..."
ambulon piag-rag-search \
    --collection-name "$COLLECTION" \
    -q "$SEARCH_QUERY" \
    -o chunks.json

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la recherche RAG"
    exit 1
fi

echo ""
echo "Phase 2/2 : Génération CHAT..."
ambulon piag-chat-query \
    -q "$QUESTION" \
    -c chunks.json \
    -o "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Workflow terminé avec succès"
    echo "📄 Réponse disponible dans: $OUTPUT"
else
    echo "❌ Erreur lors de la génération CHAT"
    exit 1
fi
```

**Usage :**
```bash
chmod +x workflow_rag_chat.sh
./workflow_rag_chat.sh "architecture" "Quelle est l'architecture de SIREINES ?"
```

### Script Python complet

```python
#!/usr/bin/env python3
"""
workflow_rag_chat.py - Workflow automatisé RAG + CHAT
"""
import subprocess
import sys
from pathlib import Path

def run_rag_search(collection: str, query: str, output: str = "chunks.json") -> bool:
    """Phase 1: Recherche RAG"""
    print("Phase 1/2 : Recherche RAG...")

    cmd = [
        "ambulon", "piag-rag-search",
        "--collection-name", collection,
        "-q", query,
        "-o", output
    ]

    result = subprocess.run(cmd)
    return result.returncode == 0

def run_chat_query(question: str, chunks: str = "chunks.json", output: str = "reponse.md") -> bool:
    """Phase 2: Génération CHAT"""
    print("\nPhase 2/2 : Génération CHAT...")

    cmd = [
        "ambulon", "piag-chat-query",
        "-q", question,
        "-c", chunks,
        "-o", output
    ]

    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    if len(sys.argv) < 3:
        print("Usage: python workflow_rag_chat.py <search_query> <question> [output_file]")
        print("Exemple: python workflow_rag_chat.py 'architecture' 'Quelle est l'architecture ?' reponse.md")
        sys.exit(1)

    search_query = sys.argv[1]
    question = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "reponse.md"

    # Phase 1: RAG
    if not run_rag_search("PNM3_SIREINES", search_query):
        print("❌ Erreur lors de la recherche RAG")
        sys.exit(1)

    # Phase 2: CHAT
    if not run_chat_query(question, output=output):
        print("❌ Erreur lors de la génération CHAT")
        sys.exit(1)

    print(f"\n✅ Workflow terminé avec succès")
    print(f"📄 Réponse disponible dans: {output}")

if __name__ == "__main__":
    main()
```

**Usage :**
```bash
python workflow_rag_chat.py "architecture" "Quelle est l'architecture de SIREINES ?"
```

---

## 📚 Références

- **API RAG** : `doc/API_PIAG_APPEL_RAG.md`
- **API CHAT** : `doc/API_PIAG_APPEL_CHAT.md`
- **Tests RAG** : `doc/PIAG_RAG_WORKFLOW.md`
- **Tests CHAT** : `doc/PIAG_CHAT_COMMANDS.md`

---

## 🔄 Historique

| Date | Version | Changements |
|------|---------|-------------|
| 2026-03-22 | 1.0 | Création du document - Workflow en 2 phases rigoureuses |
| 2026-03-22 | 1.1 | Ajout de `--question-file` et `-o` pour piag-rag-search |

---

**Auteur** : Équipe Ambulon
**Dernière mise à jour** : 2026-03-22
