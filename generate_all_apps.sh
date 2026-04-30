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

echo "Generating documentation for ${#apps[@]} applications..."

for app in "${apps[@]}"; do
  echo "=== Starting: $app ==="
  echo 'y' | python -m app.llm.commands.generate_docs --app "$app" --provider cloud_gpt_oss_120b --skip-errors 2>&1 | tail -5
  sleep 2
done

echo "All generations completed!"
