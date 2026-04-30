#!/bin/bash

# Get list of apps without files
existing=$(find workplace-ambulon/delivrables -name "*.gpt-oss_120b-cloud.md" -type f | sed 's/.*\///' | sed 's/\.gpt-oss.*//' | cut -d. -f1 | sort -u)

apps="bo causalis datapop gesrec honore-home honore-infra lejis mobilehoop ocle ocle-docker ocr-api orchidee pnm3-iaas-ansible pnm3-iaas-inventory primesauto siamae-vas siam2 siss siss-infra vaccination webocr-back-old webocr-front-old"

echo "Starting final generation for remaining apps..."
for app in $apps; do
  if echo "$existing" | grep -q "^$app\$"; then
    continue
  fi
  
  echo "[$(date +'%H:%M:%S')] $app"
  timeout 600 bash -c "echo 'y' | python -m app.llm.commands.generate_docs --app '$app' --provider cloud_gpt_oss_120b --skip-errors" 2>/dev/null &
  sleep 5
done

wait
echo "All jobs submitted. Final count:"
find workplace-ambulon/delivrables -name "*.gpt-oss_120b-cloud.md" -type f | wc -l
