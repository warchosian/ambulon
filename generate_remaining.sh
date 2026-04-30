#!/bin/bash

apps=(
  "bo" "causalis" "causalismp" "datapop" "gesapp-infra" "gesrec" "honore-back"
  "honore-home" "honore-infra" "lejis" "mobilehoop" "ocle" "ocle-docker"
  "ocr-api" "orchidee" "pnm3-iaas-ansible" "pnm3-iaas-inventory" "primesauto"
  "siamae-vas" "siam2" "siss" "siss-infra" "vaccination" "webocr-back-old"
  "webocr-front-old"
)

echo "Generating for ${#apps[@]} remaining applications..."
for app in "${apps[@]}"; do
  echo "[$(date +'%H:%M:%S')] Processing: $app"
  echo 'y' | python -m app.llm.commands.generate_docs --app "$app" --provider cloud_gpt_oss_120b --skip-errors 2>&1 | grep -E "Success|Errors|Generated" | head -3
  sleep 3
done

echo "Batch generation complete!"
