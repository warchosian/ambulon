#!/bin/bash
# regenerate_hallucinated.sh
#
# Régénère les 73 fichiers du corpus contenant des types de diagrammes
# hallucinés par le LLM (componentDiagram, deploymentDiagram, objectDiagram,
# packageDiagram), maintenant que les 4 prompts parents ont été patchés
# avec le garde-fou Mermaid.
#
# Source de la liste : doc/files_to_regenerate.txt
# Prompts patchés : prompt.dat_uml.mmd.md, prompt.cst.mmd.md,
#                   prompt.specs.mmd.md, prompt.dat_iso42010.mmd.md
#
# Usage :
#   ./regenerate_hallucinated.sh                 # exécution
#   ./regenerate_hallucinated.sh --dry-run       # liste sans exécuter
#   ./regenerate_hallucinated.sh --backup        # sauvegarde l'ancien dans delivrables_backup
#
set -euo pipefail

DRY_RUN=false
BACKUP=false
LIST_FILE="doc/files_to_regenerate.txt"
DELIVRABLES_DIR="workplace-ambulon/delivrables"
BACKUP_DIR="workplace-ambulon/delivrables_backup_$(date +%Y%m%d_%H%M%S)"

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --backup)  BACKUP=true ;;
    -h|--help)
      grep -E '^# ' "$0" | sed 's/^# //'
      exit 0
      ;;
  esac
done

if [[ ! -f "$LIST_FILE" ]]; then
  echo "ERREUR : $LIST_FILE introuvable"
  exit 1
fi

# Extraire les paires (app, doc_type) uniques depuis le nom de fichier
# Format observé : <app>.<doc_type>.mmd.<model>.md
declare -A PAIRS
while IFS= read -r filename; do
  base="${filename%.md}"
  base="${base%.gpt-oss_120b-cloud}"
  base="${base%.mmd}"
  app="${base%%.*}"
  doc_type="${base#*.}"
  PAIRS["${app}|${doc_type}"]=1
done < "$LIST_FILE"

echo "═══════════════════════════════════════════════════════════════"
echo "  Régénération ciblée des fichiers à types Mermaid hallucinés"
echo "═══════════════════════════════════════════════════════════════"
echo "  Fichiers source    : $(wc -l < "$LIST_FILE") fichiers"
echo "  Paires uniques     : ${#PAIRS[@]} (app × doc_type)"
echo "  Mode               : $([[ "$DRY_RUN" == true ]] && echo "DRY-RUN" || echo "EXÉCUTION")"
echo "  Backup             : $([[ "$BACKUP" == true ]] && echo "OUI ($BACKUP_DIR)" || echo "NON")"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Backup optionnel
if [[ "$BACKUP" == true && "$DRY_RUN" == false ]]; then
  echo "📦 Backup des 73 fichiers vers $BACKUP_DIR ..."
  mkdir -p "$BACKUP_DIR"
  while IFS= read -r filename; do
    cp "$DELIVRABLES_DIR/$filename" "$BACKUP_DIR/" 2>/dev/null || true
  done < "$LIST_FILE"
  echo "   ✓ Backup terminé"
  echo ""
fi

# Statistiques par doc_type
echo "📊 Répartition par type de document :"
awk -F'|' '{print "  " $2}' <(printf '%s\n' "${!PAIRS[@]}") | sort | uniq -c | sort -rn | sed 's/^/   /'
echo ""

# Régénération paire par paire
total=${#PAIRS[@]}
done_count=0
for pair in "${!PAIRS[@]}"; do
  done_count=$((done_count + 1))
  app="${pair%%|*}"
  doc_type="${pair#*|}"

  echo "[$done_count/$total] $app → $doc_type"

  if [[ "$DRY_RUN" == true ]]; then
    echo "   (dry-run) python -m app.llm.commands.generate_docs --app $app --prompt $doc_type --provider cloud_gpt_oss_120b --skip-errors"
  else
    echo 'y' | python -m app.llm.commands.generate_docs \
      --app "$app" \
      --prompt "$doc_type" \
      --provider cloud_gpt_oss_120b \
      --skip-errors 2>&1 | tail -3
    sleep 2
  fi
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Régénération terminée : $total paires (app × doc_type)"
echo "═══════════════════════════════════════════════════════════════"

if [[ "$DRY_RUN" == false ]]; then
  echo ""
  echo "🔍 Vérification — types hallucinés résiduels :"
  for kw in componentDiagram deploymentDiagram objectDiagram packageDiagram; do
    n=$(grep -lE "^$kw" "$DELIVRABLES_DIR"/*.md 2>/dev/null | wc -l)
    echo "   $kw : $n fichier(s) (attendu : 0)"
  done
fi
