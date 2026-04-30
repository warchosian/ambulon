#!/bin/bash

apps=(
  "admin_ep" "ado" "afinope" "agile-back" "agile-env" "agile-front" "agile-infra"
  "ambulon" "bo" "bulletin-officiel" "causalis" "causalismp" "cerbere-bouchon"
  "datapop" "formation-ecologie" "gesapp-infra" "gesrec" "honore-back"
  "honore-front" "honore-home" "honore-infra" "hubrh" "lejis" "mobilehoop"
  "ocle" "ocle-docker" "ocr-api" "orchidee" "pnm3-iaas-ansible"
  "pnm3-iaas-inventory" "primesauto" "siamae-vas" "siam2" "sireines" "siss"
  "siss-infra" "vaccination" "webocr-back-old" "webocr-front-old"
)

echo "Generating for ${#apps[@]} applications in parallel (max 2 concurrent)..."
sem --timeout 120 -j 2 

for app in "${apps[@]}"; do
  (
    echo "[$app] Starting..."
    count_before=$(find workplace-ambulon/delivrables -name "${app}.*.gpt-oss_120b-cloud.md" -type f 2>/dev/null | wc -l)
    echo 'y' | python -m app.llm.commands.generate_docs --app "$app" --provider cloud_gpt_oss_120b --skip-errors >/dev/null 2>&1
    count_after=$(find workplace-ambulon/delivrables -name "${app}.*.gpt-oss_120b-cloud.md" -type f 2>/dev/null | wc -l)
    echo "[$app] Generated $((count_after - count_before)) files"
  ) &
  sleep 0.5
done

wait
echo "All generations completed!"
