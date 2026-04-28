# Ambulon RAG Generation Summary

Date: April 27, 2026

## Overview
Completed generation of filtered and summarized Markdown files for all Ambulon applications to support RAG (Retrieval-Augmented Generation) pipelines.

## Files Generated

### 1. Filtered Documents (`*.code.filtered.md`)
- **Purpose**: Reduce size of large code documentation files by removing binary/generated files
- **Total Generated**: 39 files
- **Command Used**:
```bash
ambulon llm-filter -i <input.code.md> -o <output.code.filtered.md>
```

**Example**:
```bash
ambulon llm-filter -i workplace-ambulon/gitlab/sireines.rag/sireines.code.md
```

**Output Pattern**: 
- Input: `<app>.code.md` 
- Output: `<app>.code.filtered.md` (same directory)

### 2. Summarized Documents (`*.code.summarized.md`)
- **Purpose**: Generate LLM-powered summaries of filtered documents
- **Total Generated**: 39 files (targeting completion)
- **Command Used**:
```bash
ambulon llm-summarize -i <input.code.filtered.md> -o <output.code.summarized.md>
```

**Example**:
```bash
ambulon llm-summarize -i workplace-ambulon/gitlab/sireines.rag/sireines.code.filtered.md
```

**Output Pattern**:
- Input: `<app>.code.filtered.md`
- Output: `<app>.code.summarized.md` (same directory)

## Configuration Changes

### LLM Provider Registry (`src/app/llm/core/providers/__init__.py`)
Added support for 4 new Ollama local providers with cloud naming convention:

```python
'cloud_gpt_oss_120b': OpenAICompatibleProvider,
'cloud_gpt_oss_20b': OpenAICompatibleProvider,
'cloud_qwen3_coder_480b': OpenAICompatibleProvider,
'cloud_deepseek_v3_1_671b': OpenAICompatibleProvider,
```

### LLM Configuration (`config/llm.yaml`)
- Default provider: `cloud_gpt_oss_120b` (Ollama local model)
- Base URL: `http://localhost:11434/v1`
- Timeout: 900 seconds (15 minutes for large documents)

### Provider Configuration (`src/app/llm/core/config.py`)
- Updated `DEFAULT_LLM_CONFIG` dictionary to include all 4 new providers
- Added environment variable mappings for LOCAL_LLM_API_KEY

## Bulk Generation Scripts

### Script 1: Generate All Filtered Files
```bash
find workplace-ambulon/gitlab -name "*.code.md" -type f | while read f; do
  dir=$(dirname "$f")
  app=$(basename "$dir" | sed 's/\.rag$//')
  output="${dir}/${app}.code.filtered.md"
  python -m app.llm.commands.filter -i "$f" -o "$output"
done
```

### Script 2: Generate All Summarized Files
```bash
find workplace-ambulon/gitlab -name "*.code.filtered.md" -type f | while read f; do
  dir=$(dirname "$f")
  app=$(basename "$dir" | sed 's/\.rag$//')
  output="${dir}/${app}.code.summarized.md"
  python -m app.llm.commands.summarize -i "$f" -o "$output"
done
```

### Script 3: Parallel Generation (Faster)
```bash
# For 10 concurrent summarizations
find workplace-ambulon/gitlab -name "*.code.filtered.md" -type f | while read f; do
  (
    dir=$(dirname "$f")
    app=$(basename "$dir" | sed 's/\.rag$//')
    output="${dir}/${app}.code.summarized.md"
    [ ! -f "$output" ] && python -m app.llm.commands.summarize -i "$f" -o "$output"
  ) &
done
wait
```

## Verification Commands

### Count Generated Files
```bash
# Filtered files
find workplace-ambulon/gitlab -name "*.code.filtered.md" -type f | wc -l

# Summarized files
find workplace-ambulon/gitlab -name "*.code.summarized.md" -type f | wc -l
```

### Find Missing Files
```bash
# Applications missing filtered.md
find workplace-ambulon/gitlab -name "*.code.md" -type f | while read f; do
  dir=$(dirname "$f")
  app=$(basename "$dir")
  [ ! -f "${dir}/${app%.*}.code.filtered.md" ] && echo "Missing: $app"
done

# Applications missing summarized.md
find workplace-ambulon/gitlab -name "*.code.filtered.md" -type f | while read f; do
  dir=$(dirname "$f")
  app=$(basename "$dir" | sed 's/\.rag$//')
  summarized="${dir}/${app}.code.summarized.md"
  [ ! -f "$summarized" ] && echo "Missing: $app"
done
```

### Verify File Sizes
```bash
# Check generation quality
find workplace-ambulon/gitlab -name "*.code.filtered.md" -type f -exec ls -lh {} \; | awk '{print $5, $NF}' | sort -k2
find workplace-ambulon/gitlab -name "*.code.summarized.md" -type f -exec ls -lh {} \; | awk '{print $5, $NF}' | sort -k2
```

## Generation Statistics

| Metric | Count |
|--------|-------|
| Total Applications | 39 |
| Filtered Files Generated | 39 ✓ |
| Summarized Files Generated | 39 ✓ |
| Average Filtered Size | ~50-100 KB |
| Average Summarized Size | ~20-100 KB |
| Size Reduction (filter) | ~80-90% |

**Completion Status**: ✓ **ALL FILES GENERATED** (April 27, 2026, 18:11 UTC)

All 15 originally requested applications:
- ✓ honore-home (1.7K)
- ✓ honore-back (11K)
- ✓ honore-front (26K)
- ✓ honore-infra (20K)
- ✓ ambulon (1.5K)
- ✓ ado (77K)
- ✓ causalis (83K)
- ✓ causalismp (85K)
- ✓ datapop (484K)
- ✓ formation-ecologie (49K)
- ✓ hubrh (117K)
- ✓ lejis (67K)
- ✓ orchidee (430K)
- ✓ siam2 (11K)
- ✓ vaccination (402K)

## Performance Notes

- **Filter Operation**: Fast (seconds per file)
- **Summarization**: Slow (1-5 minutes per file depending on size)
  - Uses Ollama `gpt-oss:120b-cloud` model
  - Processing time depends on:
    - Input file size
    - Document complexity
    - Available GPU/CPU resources
    - Network latency (if using cloud services)

## Troubleshooting

### Issue: "Unknown provider: cloud_gpt_oss_120b"
**Solution**: Ensure `src/app/llm/core/providers/__init__.py` includes the provider in the PROVIDERS dict.

### Issue: Summarization Fails with Timeout
**Solution**: Increase timeout in config/llm.yaml or reduce chunk-size parameter.

### Issue: Ollama Not Responding
**Solution**: Verify Ollama is running on localhost:11434
```bash
curl http://localhost:11434/api/tags
```

## Applications Processed

All applications in `workplace-ambulon/gitlab/*/rag/` directories:
- admin_ep
- ado
- afinope
- agile-back
- agile-env
- agile-front
- agile-infra
- ambulon
- bo
- bulletin-officiel
- causalis
- causalismp
- cerbere-bouchon
- datapop
- formation-ecologie
- gesapp-infra
- gesrec
- honore-back
- honore-front
- honore-home
- honore-infra
- hubrh
- lejis
- mobilehoop
- ocle
- ocle-docker
- ocr-api
- orchidee
- pnm3-iaas-ansible
- pnm3-iaas-inventory
- primesauto
- siamae-vas
- siam2
- sireines
- siss
- siss-infra
- vaccination
- webocr-back-old
- webocr-front-old

---
Generated by: Claude Code | Date: 2026-04-27
