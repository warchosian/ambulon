#!/bin/bash
# -*- coding: utf-8 -*-
# Workflow complet RAG PNM3_SIREINES
# Usage: ./workflow_complet_sireines.sh

set -e  # Arrêter en cas d'erreur

echo "========================================"
echo "  WORKFLOW COMPLET RAG PNM3_SIREINES"
echo "========================================"
echo ""
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Étape 1
echo "ÉTAPE 1/9 : Vérification configuration"
echo "----------------------------------------"
if [ ! -f config/piag.yaml ]; then
    echo "❌ Fichier config/piag.yaml introuvable"
    exit 1
fi
echo "✓ Fichier config/piag.yaml trouvé"

if [ ! -d applications/sireines.rag ]; then
    echo "❌ Répertoire applications/sireines.rag introuvable"
    exit 1
fi
echo "✓ Répertoire applications/sireines.rag trouvé"

# Compter les fichiers sources
SOURCE_COUNT=$(ls applications/sireines.rag/*.{md,pdf} 2>/dev/null | wc -l)
echo "✓ Documents sources: $SOURCE_COUNT fichiers"
echo ""

# Étape 2
echo "ÉTAPE 2/9 : Création/Vérification collection"
echo "---------------------------------------------"
ambulon piag-rag-collection-add \
  --name "PNM3_SIREINES" \
  --description "Documentation complète SIREINES : DAT, C4, Composants, Wiki, ISO25010" 2>/dev/null \
  && echo "✓ Collection créée" \
  || echo "⚠️  Collection existe déjà (OK)"
echo ""

# Étape 3
echo "ÉTAPE 3/9 : Upload documents"
echo "-----------------------------"
echo "Upload des $SOURCE_COUNT fichiers depuis applications/sireines.rag/"
ambulon piag-rag-doc-upload \
  --collection-name PNM3_SIREINES \
  --folder applications/sireines.rag \
  --if-exists skip
echo ""

# Étape 4
echo "ÉTAPE 4/9 : Attente indexation"
echo "-------------------------------"
echo "⏳ Attente de 60 secondes pour l'indexation..."
for i in {60..1}; do
    echo -ne "   $i secondes restantes...\r"
    sleep 1
done
echo "   ✓ Attente terminée                    "
echo ""

# Étape 5
echo "ÉTAPE 5/9 : Vérification collection"
echo "------------------------------------"
ambulon piag-rag-doc-list --collection-name PNM3_SIREINES | grep "Total:" || echo "⚠️  Impossible de vérifier"
echo ""

# Étape 6
echo "ÉTAPE 6/9 : Recherche RAG"
echo "-------------------------"
echo "Création du répertoire chunks/PNM3_SIREINES/"
mkdir -p chunks/PNM3_SIREINES

echo "Recherche RAG avec query: 'architecture,dat'"
ambulon piag-rag-search \
  --collection-name PNM3_SIREINES \
  --query "architecture,dat" \
  --top-k 10 \
  -o chunks/PNM3_SIREINES/chunks.json

# Vérifier le fichier chunks
if [ -f chunks/PNM3_SIREINES/chunks.json ]; then
    CHUNK_COUNT=$(cat chunks/PNM3_SIREINES/chunks.json | jq '.chunks | length' 2>/dev/null || echo "?")
    echo "✓ Fichier chunks créé: $CHUNK_COUNT chunks"
else
    echo "❌ Erreur: Fichier chunks non créé"
    exit 1
fi
echo ""

# Étape 7
echo "ÉTAPE 7/9 : Préparation question"
echo "---------------------------------"
mkdir -p questions

# Vérifier si le fichier DAT C4 existe
if [ ! -f applications/sireines.rag/sireines.dat_c4model.md ]; then
    echo "⚠️  Fichier sireines.dat_c4model.md introuvable"
    echo "   Création d'une question générique..."
    cat > questions/question_dat_c4.txt <<'EOF'
Analyse détaillée du Dossier d'Architecture Technique (DAT) de SIREINES :

En te basant sur les extraits fournis, réponds aux questions suivantes :

1. Quelle est l'architecture globale de SIREINES (pattern architectural, frameworks) ?
2. Quels sont les principaux composants techniques identifiés ?
3. Quelles technologies de base de données sont utilisées et pourquoi ?
4. Comment est organisée la couche de présentation (frontend) ?
5. Quelles sont les dépendances externes principales ?
6. Y a-t-il des décisions architecturales critiques documentées (ADR) ?

Fournis une réponse structurée en te basant UNIQUEMENT sur les informations des extraits fournis.
EOF
else
    echo "✓ Fichier sireines.dat_c4model.md trouvé"
    echo "   Extraction des 30 premières lignes comme question..."
    head -n 30 applications/sireines.rag/sireines.dat_c4model.md > questions/question_dat_c4_extract.txt

    # Créer aussi une question d'analyse
    cat > questions/question_dat_c4.txt <<'EOF'
Analyse approfondie de l'architecture SIREINES basée sur le DAT et le modèle C4 :

À partir des extraits du Dossier d'Architecture Technique (DAT) et du modèle C4, fournis une analyse détaillée structurée en sections :

## 1. Architecture Globale
- Pattern architectural utilisé
- Frameworks principaux
- Technologies de base

## 2. Composants Techniques (C4 Level 3)
- Liste et description des composants
- Responsabilités de chaque composant
- Relations entre composants

## 3. Technologies de Données
- Bases de données utilisées
- Justification des choix
- Patterns de persistance

## 4. Décisions Architecturales
- ADR (Architecture Decision Records) identifiés
- Justifications techniques
- Trade-offs documentés

## 5. Flux de Données
- Flux principaux entre composants
- Protocoles de communication
- Patterns d'intégration

Base ta réponse UNIQUEMENT sur les informations présentes dans les extraits fournis.
Ne fais aucune supposition ou extrapolation.
EOF
fi

echo "✓ Question créée: questions/question_dat_c4.txt"
wc -l questions/question_dat_c4.txt
echo ""

# Étape 8
echo "ÉTAPE 8/9 : Génération réponse CHAT"
echo "-----------------------------------"
mkdir -p reponses/PNM3_SIREINES

echo "Appel API CHAT avec les chunks récupérés..."
ambulon piag-chat-query \
  --question-file questions/question_dat_c4.txt \
  --chunks chunks/PNM3_SIREINES/chunks.json \
  -o reponses/PNM3_SIREINES/reponse_architecture_dat.md

if [ -f reponses/PNM3_SIREINES/reponse_architecture_dat.md ]; then
    WORD_COUNT=$(wc -w < reponses/PNM3_SIREINES/reponse_architecture_dat.md)
    echo "✓ Réponse générée: $WORD_COUNT mots"
else
    echo "❌ Erreur: Réponse non générée"
    exit 1
fi
echo ""

# Étape 9
echo "ÉTAPE 9/9 : Vérifications finales"
echo "----------------------------------"
echo "Statistiques:"
echo "  • Documents sources: $SOURCE_COUNT fichiers"
echo "  • Chunks récupérés: $CHUNK_COUNT chunks"
echo "  • Taille réponse: $WORD_COUNT mots"
echo ""

# Vérifier les références aux extraits
EXTRACT_REF=$(grep -c "\[Extrait" reponses/PNM3_SIREINES/reponse_architecture_dat.md 2>/dev/null || echo "0")
echo "  • Références aux extraits: $EXTRACT_REF"
echo ""

echo "Fichiers générés:"
echo "  ✓ chunks/PNM3_SIREINES/chunks.json"
echo "  ✓ questions/question_dat_c4.txt"
echo "  ✓ reponses/PNM3_SIREINES/reponse_architecture_dat.md"
echo ""

echo "========================================"
echo "  ✅ WORKFLOW TERMINÉ AVEC SUCCÈS"
echo "========================================"
echo ""
echo "📄 Consultez la réponse générée:"
echo "   cat reponses/PNM3_SIREINES/reponse_architecture_dat.md"
echo ""
echo "📊 Aperçu de la réponse:"
echo "----------------------------------------"
head -n 20 reponses/PNM3_SIREINES/reponse_architecture_dat.md
echo "----------------------------------------"
echo "(... voir le fichier complet pour plus de détails)"
echo ""
