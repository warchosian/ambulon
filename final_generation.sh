#!/bin/bash

# Applications with 0 files
apps="bo causalis causalismp datapop gesapp-infra gesrec honore-back honore-home honore-infra lejis mobilehoop ocle ocle-docker ocr-api orchidee pnm3-iaas-ansible pnm3-iaas-inventory primesauto siamae-vas siam2 siss siss-infra vaccination webocr-back-old webocr-front-old"

# Generate for each app sequentially
for app in $apps; do
  count_before=$(find workplace-ambulon/delivrables -name "${app}.*.gpt-oss_120b-cloud.md" -type f 2>/dev/null | wc -l)
  echo "[$(date +'%H:%M:%S')] Generating: $app (before: $count_before files)"
  
  timeout 300 bash -c "echo 'y' | python -m app.llm.commands.generate_docs --app '$app' --provider cloud_gpt_oss_120b --skip-errors" >/dev/null 2>&1
  
  count_after=$(find workplace-ambulon/delivrables -name "${app}.*.gpt-oss_120b-cloud.md" -type f 2>/dev/null | wc -l)
  generated=$((count_after - count_before))
  echo "[$(date +'%H:%M:%S')] $app: $generated new files (total: $count_after)"
  
  sleep 2
done

echo "Batch complete. Total files:" 
find workplace-ambulon/delivrables -name "*.gpt-oss_120b-cloud.md" -type f | wc -l
