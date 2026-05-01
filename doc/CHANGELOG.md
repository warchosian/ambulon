# Changelog

Toutes les versions notables d'Ambulon sont consignées ici.

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), versionnage [SemVer](https://semver.org/lang/fr/).

---

## [4.8.0] – 2026-04-30 — Documentation industrielle

Branche : `feature/doc-industrielle` · Commit : `a4b0a02`
Releases : [GitHub](https://github.com/warchosian/ambulon/releases/tag/4.8.0) · [GitLab](https://gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/gti/ambulon/-/releases/4.8.0)

### Ajouté
- **OCR** : modes `text` / `ocr` / `merged` dans `_process_pdf_ocr` et option CLI `--all-modes` (alias `--dual`) qui produit 3 fichiers `<name>.text.md`, `<name>.ocr.md`, `<name>.merged.md`
- **OCR** : heuristique de seuil 50 caractères qui déclenche le fallback OCR si la couche texte du PDF est trop maigre (corrige les pages dont seul un identifiant est extractible)
- **Diagrammes** : extraction des diagrammes en échec dans des fichiers latéraux `<stem>_diagram-fails.<ext>.md` (PlantUML, Mermaid, Graphviz) pour faciliter l'analyse des patterns d'erreur récurrents
- **Diagrammes** : conversion Mermaid via `mmdc` local en complément de Kroki (hors-ligne, vraies erreurs de syntaxe remontées)
- **LLM** : provider `cloud_minimax_2_7` enregistré
- **LLM** : `generate-docs` accepte des templates Jinja2 et normalise les chemins cross-OS
- **LLM** : script `migrate_ollama` déplacé vers `src/app/llm/`
- **Outillage** : scripts shell de génération industrielle (`generate_all_apps.sh`, `generate_remaining.sh`, `generate_parallel.sh`, etc.)
- **Règles** : enrichissement des fichiers `.claude/prompts/REGLES_PLANTUML.md` et `REGLES_MERMAID.md` (C4_Container vs C4_Component, fermeture `@enduml`, profile→rectangle, etc.)
- **fix-diagrams** : nouvelles regex de correction automatique + statistiques de conversion

### Sécurité
- **Critique** : toutes les clés API hardcodées (Anthropic, Kimi/Moonshot, GLM, DeepSeek, Google/Gemini, OpenAI compatibles) ont été retirées de `src/app/llm/core/config.py` ; le fichier lit désormais exclusivement depuis `config/llm.yaml` (en `.gitignore`)
- L'historique git de la branche a été réécrit (`git filter-branch` sur 104 commits) pour purger toutes les clés exposées
- Toutes les clés exposées ont été révoquées chez les providers concernés

### Modifié
- `_diagram-fails.<ext>.md` produit pour chaque type de diagramme indépendamment

### Corrigé
- Lint préexistants dans `ocr_logic.py` : `F401` (probe d'import `pytesseract`), `F841` (variables `result` inutilisées), `F821` (variable `pages_count` non définie avant `doc.close()`)
- Conversion bloquée pour PDFs scannés avec couche texte minimale (cf. heuristique seuil 50)

### Ignoré (gitignore)
- `workplace-ambulon/delivrables/` et `workplace-ambulon/delivrables-v2/` (artefacts générés par la chaîne LLM)
- `valerie/` (documents personnels)

---

## [v4.7.0-opus] – 2026-04 — Architecture Opus 4.7

Branche : `feature/opus-4.7-architecture-reorganization`

### Ajouté
- Réorganisation architecture pour le modèle Opus 4.7
- Corrections diagrammes Mermaid (classDiagram syntax, suppression syntaxe PlantUML détectée dans Mermaid)
- Documentation des fixes appliqués

---

## Versions antérieures

| Tag | Notes |
|---|---|
| `4.1.0` | Cycle 4.x intermédiaire |
| `4.0.0` | Refonte majeure |
| `3.8.0` → `3.0.0` | Évolutions cycle 3.x (build, providers, configuration, etc.) |
| `v3.1.0`, `v3.0.5`, `v3.0.1`, `v3.0.0` | Tags antérieurs au format `vX.Y.Z` |

Voir `git log --tags` pour le détail des commits associés.
