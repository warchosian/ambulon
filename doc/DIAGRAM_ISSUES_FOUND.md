# Issues Found in Diagram Generation

**Date:** 2026-04-28  
**Issue Type:** Generation Logic Error

---

## Summary

Some Mermaid diagram files (`.mmd.gpt-oss_120b-cloud.md`) contain **PlantUML syntax instead of Mermaid syntax**.

---

## Affected Files

### Files with @startuml (4 files)
- admin_ep.dat_uml.mmd.gpt-oss_120b-cloud.md
- agile-back.dat_uml.mmd.gpt-oss_120b-cloud.md
- causalis.dat_uml.mmd.gpt-oss_120b-cloud.md
- (likely others)

### Files with PlantUML package syntax (2+ files)
- causalis.dat_uml.mmd.gpt-oss_120b-cloud.md
- (contains `package i2.application.causalis {...}`)

---

## Root Cause

The LLM generation prompt for Mermaid diagrams (`prompt.dat_uml.mmd.md`) is generating PlantUML syntax instead of Mermaid syntax for class diagrams with package structure.

**Example Error:**
```
Error: Lexical error on line 2. Unrecognized text
classDiagram
    %% Packages;
    package i2.application.causalis {  <-- PlantUML syntax
        class Constantes <<interface>>
    }
```

Mermaid `classDiagram` does NOT support:
- `package` declarations
- `<<interface>>`, `<<entity>>` stereotypes (partially)
- Complex nesting structures

These are PlantUML features.

---

## Solutions

### Option 1: Fix Prompt (Recommended)
Update `prompt.dat_uml.mmd.md` to request:
- Pure Mermaid classDiagram syntax (without packages)
- Simpler class definitions without PlantUML stereotypes
- Alternative: Use composition/relationships instead of packages

### Option 2: Convert Content Type
Change `.mmd` files with PlantUML to `.plantuml` format:
```bash
# Files to convert:
- admin_ep.dat_uml.mmd.gpt-oss_120b-cloud.md → admin_ep.dat_uml.plantuml.gpt-oss_120b-cloud.md
```

### Option 3: Post-Processing Conversion
Create script to:
1. Detect PlantUML syntax in Mermaid files
2. Convert to proper Mermaid or PlantUML blocks
3. Update file names accordingly

---

## Impact

- ❌ 4-6 Mermaid diagram files have invalid syntax
- ✅ PlantUML files (105+) are correct
- ⚠️ Mermaid validation will fail on affected files

---

## Recommendation

**Implement Option 1:** Improve the generation prompt to generate **valid Mermaid syntax** instead of PlantUML.

The prompt should:
1. Explicitly request Mermaid class diagrams
2. Avoid PlantUML-specific features
3. Use Mermaid relationships instead of packages
4. Test with a simple example first

---

*Documented by Claude Code - 2026-04-28*
