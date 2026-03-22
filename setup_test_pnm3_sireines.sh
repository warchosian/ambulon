#!/bin/bash
################################################################################
# setup_test_pnm3_sireines.sh
#
# Script complet pour créer et tester la collection RAG PNM3_SIREINES
# avec les documents du projet SIREINES, puis tester le workflow RAG + CHAT
#
# Prérequis :
# - Accès réseau aux API PIAG RAG et CHAT
# - Configuration dans config/piag.yaml ou variables d'environnement
# - Répertoire applications/sireines.rag avec les documents
#
# Usage : ./setup_test_pnm3_sireines.sh
################################################################################

set -e  # Arrêter en cas d'erreur

# Configuration
COLLECTION_NAME="PNM3_SIREINES"
DOCS_DIR="applications/sireines.rag"
OUTPUT_DIR="./output_test_pnm3_sireines"
LOG_FILE="$OUTPUT_DIR/test_execution.log"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction pour logger
log() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}✗ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}ℹ $1${NC}" | tee -a "$LOG_FILE"
}

# Créer le répertoire de sortie
mkdir -p "$OUTPUT_DIR"

# En-tête
clear
echo "================================================================================"
echo "    CRÉATION ET TEST DE LA COLLECTION PNM3_SIREINES"
echo "================================================================================"
echo ""
log "Début de l'exécution du script"

################################################################################
# ÉTAPE 1 : Vérification des prérequis
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 1 : VÉRIFICATION DES PRÉREQUIS"
echo "================================================================================"
echo ""

log "Vérification de l'existence du répertoire $DOCS_DIR"
if [ ! -d "$DOCS_DIR" ]; then
    log_error "Le répertoire $DOCS_DIR n'existe pas"
    exit 1
fi
log_success "Répertoire $DOCS_DIR trouvé"

log "Comptage des documents disponibles"
MD_COUNT=$(find "$DOCS_DIR" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
PDF_COUNT=$(find "$DOCS_DIR" -maxdepth 1 -name "*.pdf" 2>/dev/null | wc -l)
TOTAL_COUNT=$((MD_COUNT + PDF_COUNT))

log_info "Documents trouvés : $MD_COUNT fichiers .md, $PDF_COUNT fichiers .pdf (Total: $TOTAL_COUNT)"

if [ $TOTAL_COUNT -eq 0 ]; then
    log_error "Aucun document .md ou .pdf trouvé dans $DOCS_DIR"
    exit 1
fi

log_success "Prérequis validés"

################################################################################
# ÉTAPE 2 : Création de la collection avec piag-rag-create
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 2 : CRÉATION DE LA COLLECTION $COLLECTION_NAME"
echo "================================================================================"
echo ""

log "Création de la collection et upload des documents..."
log_info "Collection : $COLLECTION_NAME"
log_info "Répertoire : $DOCS_DIR"
log_info "Extensions : md,pdf"

ambulon piag-rag-create \
  --collection-name "$COLLECTION_NAME" \
  --description "Documentation complète SIREINES : DAT, CCTP, C4, Composants, ISO25010" \
  --directory "$DOCS_DIR" \
  --extensions "md,pdf" \
  --json > "$OUTPUT_DIR/collection_creation.json" 2>&1

if [ $? -eq 0 ]; then
    log_success "Collection créée avec succès"

    # Extraire l'ID de la collection
    COLLECTION_ID=$(jq -r '.collection.id // .id // "unknown"' "$OUTPUT_DIR/collection_creation.json" 2>/dev/null)
    DOC_COUNT=$(jq -r '.collection.document_count // .uploaded_documents | length // 0' "$OUTPUT_DIR/collection_creation.json" 2>/dev/null)

    log_info "Collection ID : $COLLECTION_ID"
    log_info "Documents uploadés : $DOC_COUNT"

    cat "$OUTPUT_DIR/collection_creation.json" | jq '.' > "$OUTPUT_DIR/collection_creation_formatted.json" 2>/dev/null
else
    log_error "Échec de la création de la collection"
    cat "$OUTPUT_DIR/collection_creation.json"
    exit 1
fi

################################################################################
# ÉTAPE 3 : Attente de l'indexation
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 3 : ATTENTE DE L'INDEXATION DES DOCUMENTS"
echo "================================================================================"
echo ""

log "Attente de l'indexation (30 secondes)..."
for i in {30..1}; do
    echo -ne "\rTemps restant : ${i}s  "
    sleep 1
done
echo ""
log_success "Indexation supposée terminée"

################################################################################
# ÉTAPE 4 : Vérification de la collection
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 4 : VÉRIFICATION DE LA COLLECTION"
echo "================================================================================"
echo ""

log "Récupération des informations de la collection..."
ambulon piag-rag-collection-get \
  --collection "$COLLECTION_NAME" \
  --json > "$OUTPUT_DIR/collection_info.json" 2>&1

if [ $? -eq 0 ]; then
    log_success "Informations récupérées"
    cat "$OUTPUT_DIR/collection_info.json" | jq '.'
else
    log_error "Impossible de récupérer les informations"
fi

log "Liste des documents dans la collection..."
ambulon piag-rag-doc-list \
  --collection "$COLLECTION_NAME" \
  --json > "$OUTPUT_DIR/documents_list.json" 2>&1

if [ $? -eq 0 ]; then
    INDEXED_COUNT=$(jq '.items | length // 0' "$OUTPUT_DIR/documents_list.json" 2>/dev/null)
    log_success "Documents indexés : $INDEXED_COUNT"

    log_info "Liste des documents :"
    jq -r '.items[] | "  - \(.filename) (ID: \(.id))"' "$OUTPUT_DIR/documents_list.json" 2>/dev/null | tee -a "$LOG_FILE"
else
    log_error "Impossible de lister les documents"
fi

################################################################################
# ÉTAPE 5 : Tests de recherche RAG
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 5 : TESTS DE RECHERCHE RAG"
echo "================================================================================"
echo ""

# Définir les questions de test
declare -a TEST_QUERIES=(
    "architecture technique SIREINES"
    "module gestion alertes"
    "modèle C4"
    "exigences qualité ISO 25010"
    "sécurité authentification"
)

log "Exécution de ${#TEST_QUERIES[@]} recherches de test..."

for i in "${!TEST_QUERIES[@]}"; do
    query="${TEST_QUERIES[$i]}"
    query_num=$((i + 1))

    echo ""
    log "[$query_num/${#TEST_QUERIES[@]}] Recherche : \"$query\""

    ambulon piag-rag-search \
      --collection "$COLLECTION_NAME" \
      --query "$query" \
      --top-k 5 \
      --mode hybrid \
      --rerank true \
      --json > "$OUTPUT_DIR/search_${query_num}.json" 2>&1

    if [ $? -eq 0 ]; then
        CHUNK_COUNT=$(jq '.chunks | length // 0' "$OUTPUT_DIR/search_${query_num}.json" 2>/dev/null)
        log_success "Trouvé $CHUNK_COUNT chunks pertinents"

        # Afficher le premier chunk
        FIRST_CHUNK=$(jq -r '.chunks[0].content // "N/A"' "$OUTPUT_DIR/search_${query_num}.json" 2>/dev/null | head -c 150)
        log_info "Extrait : ${FIRST_CHUNK}..."
    else
        log_error "Échec de la recherche"
    fi
done

################################################################################
# ÉTAPE 6 : Tests RAG + CHAT
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 6 : TESTS RAG + CHAT (Questions Techniques)"
echo "================================================================================"
echo ""

# Questions techniques détaillées
declare -A TECHNICAL_QUESTIONS=(
    ["architecture"]="Décris l'architecture technique du système SIREINES en détaillant les composants, les technologies utilisées et les patterns architecturaux."
    ["c4model"]="Explique le modèle C4 appliqué à SIREINES. Quels sont les 4 niveaux et que représentent-ils ?"
    ["alertes"]="Comment fonctionne le module de gestion des alertes dans SIREINES ? Quelles sont ses fonctionnalités principales ?"
    ["iso25010"]="Quelles sont les exigences de qualité ISO 25010 définies pour SIREINES ?"
    ["securite"]="Comment est implémentée la sécurité dans SIREINES ? Décris les mécanismes d'authentification et d'autorisation."
)

log "Génération de ${#TECHNICAL_QUESTIONS[@]} réponses techniques avec RAG + CHAT..."

for topic in "${!TECHNICAL_QUESTIONS[@]}"; do
    question="${TECHNICAL_QUESTIONS[$topic]}"

    echo ""
    log "Traitement : $topic"
    log_info "Question : $question"

    # Étape 1 : Recherche RAG
    log "  [1/2] Recherche des chunks pertinents..."
    ambulon piag-rag-search \
      --collection "$COLLECTION_NAME" \
      --query "$question" \
      --top-k 7 \
      --mode hybrid \
      --rerank true \
      --json > "$OUTPUT_DIR/${topic}_chunks.json" 2>&1

    if [ $? -eq 0 ]; then
        CHUNK_COUNT=$(jq '.chunks | length // 0' "$OUTPUT_DIR/${topic}_chunks.json" 2>/dev/null)
        log_success "  Trouvé $CHUNK_COUNT chunks"
    else
        log_error "  Échec de la recherche"
        continue
    fi

    # Étape 2 : Génération CHAT
    log "  [2/2] Génération de la réponse avec le LLM..."
    ambulon piag-chat-query \
      --question "$question" \
      --chunks "$OUTPUT_DIR/${topic}_chunks.json" \
      --system "Tu es un expert du système SIREINES. Réponds de manière détaillée et technique en te basant sur la documentation fournie." \
      --output "$OUTPUT_DIR/${topic}_reponse.md" 2>&1

    if [ $? -eq 0 ]; then
        RESPONSE_LENGTH=$(wc -c < "$OUTPUT_DIR/${topic}_reponse.md")
        log_success "  Réponse générée (${RESPONSE_LENGTH} octets)"
    else
        log_error "  Échec de la génération"
    fi
done

################################################################################
# ÉTAPE 7 : Génération du rapport final
################################################################################
echo ""
echo "================================================================================"
echo " ÉTAPE 7 : GÉNÉRATION DU RAPPORT FINAL"
echo "================================================================================"
echo ""

log "Génération du rapport de synthèse..."

REPORT_FILE="$OUTPUT_DIR/RAPPORT_FINAL.md"

cat > "$REPORT_FILE" << EOF
# Rapport de Test : Collection PNM3_SIREINES

**Date d'exécution** : $(date +'%Y-%m-%d %H:%M:%S')
**Collection** : $COLLECTION_NAME
**Collection ID** : $COLLECTION_ID

---

## 1. Résumé de la Collection

- **Documents sources** : $TOTAL_COUNT fichiers ($MD_COUNT .md, $PDF_COUNT .pdf)
- **Documents indexés** : $INDEXED_COUNT
- **Répertoire** : $DOCS_DIR

## 2. Tests de Recherche RAG

Nombre de recherches effectuées : ${#TEST_QUERIES[@]}

| # | Requête | Chunks trouvés |
|---|---------|----------------|
EOF

# Ajouter les résultats de recherche au rapport
for i in "${!TEST_QUERIES[@]}"; do
    query="${TEST_QUERIES[$i]}"
    query_num=$((i + 1))
    chunk_count=$(jq '.chunks | length // 0' "$OUTPUT_DIR/search_${query_num}.json" 2>/dev/null || echo "0")
    echo "| $query_num | ${query} | ${chunk_count} |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOF

## 3. Tests RAG + CHAT

Nombre de questions techniques traitées : ${#TECHNICAL_QUESTIONS[@]}

### Questions posées :

EOF

# Ajouter les questions techniques au rapport
question_num=1
for topic in "${!TECHNICAL_QUESTIONS[@]}"; do
    question="${TECHNICAL_QUESTIONS[$topic]}"
    echo "**${question_num}. ${topic}** : ${question}" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    # Ajouter un extrait de la réponse
    if [ -f "$OUTPUT_DIR/${topic}_reponse.md" ]; then
        echo "<details>" >> "$REPORT_FILE"
        echo "<summary>Voir la réponse</summary>" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        head -20 "$OUTPUT_DIR/${topic}_reponse.md" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"
        echo "</details>" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi

    question_num=$((question_num + 1))
done

cat >> "$REPORT_FILE" << EOF

## 4. Fichiers Générés

\`\`\`
$(ls -lh "$OUTPUT_DIR" | tail -n +2)
\`\`\`

## 5. Conclusion

✅ Collection $COLLECTION_NAME créée et testée avec succès

**Prochaines étapes** :
- Interroger la collection avec des questions spécifiques
- Mettre à jour la collection quand la documentation évolue
- Intégrer dans un assistant intelligent

---

*Rapport généré automatiquement par setup_test_pnm3_sireines.sh*
EOF

log_success "Rapport généré : $REPORT_FILE"

################################################################################
# RÉSUMÉ FINAL
################################################################################
echo ""
echo "================================================================================"
echo " RÉSUMÉ DE L'EXÉCUTION"
echo "================================================================================"
echo ""

log_success "Script exécuté avec succès !"
echo ""
log_info "Collection créée : $COLLECTION_NAME (ID: $COLLECTION_ID)"
log_info "Documents indexés : $INDEXED_COUNT"
log_info "Recherches effectuées : ${#TEST_QUERIES[@]}"
log_info "Questions techniques traitées : ${#TECHNICAL_QUESTIONS[@]}"
echo ""
log_info "Fichiers générés dans : $OUTPUT_DIR/"
log_info "  - Rapport final : $REPORT_FILE"
log_info "  - Log complet : $LOG_FILE"
log_info "  - ${#TECHNICAL_QUESTIONS[@]} réponses techniques : *_reponse.md"
echo ""

echo "================================================================================"
echo " COMMANDES UTILES"
echo "================================================================================"
echo ""
echo "# Voir le rapport final"
echo "cat $REPORT_FILE"
echo ""
echo "# Rechercher dans la collection"
echo "ambulon piag-rag-search --collection $COLLECTION_NAME --query \"votre question\" --top-k 5"
echo ""
echo "# Poser une question avec contexte"
echo "ambulon piag-rag-search --collection $COLLECTION_NAME --query \"question\" --json > chunks.json"
echo "ambulon piag-chat-query --question \"question\" --chunks chunks.json"
echo ""
echo "================================================================================"

log "Fin de l'exécution du script"
