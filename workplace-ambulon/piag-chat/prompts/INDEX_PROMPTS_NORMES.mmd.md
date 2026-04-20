# Index des Prompts par Type de Document et Norme

## Vue matricielle : Document × Norme

### CCF — Cahier des Charges Fonctionnel

| Document | Norme | Fichier | Usage principal |
|----------|-------|---------|-----------------|
| CCF | **NF EN 16271** (Management par la valeur) | `_prompt_ccf_nfen16271.md` | Marchés publics français, pondération des critères |
| CCF | **ISO/IEC/IEEE 29148** (Ingénierie des exigences) | `_prompt_ccf_iso29148.md` | International, traçabilité complète |
| CCF | **BPMN / ISO 19510** (Processus métier) | `_prompt_ccf_bpmn.md` | Modélisation workflow, passerelle vers implémentation |
| CCF | UML Use Case / ISO 19505 | `_prompt_ccf.md` (section 4) | Cas d'utilisation |
| CCF | *Générique* | `_prompt_ccf.md` | Vue d'ensemble des normes CCF |

### CST — Cahier des Spécifications Techniques

| Document | Norme | Fichier | Usage principal |
|----------|-------|---------|-----------------|
| CST | **ISO/IEC 25010** (Modèle de qualité) | `_prompt_cst_iso25010.md` | Définition des 8 caractéristiques de qualité |
| CST | **ISO/IEC/IEEE 29119** (Tests) | `_prompt_cst_iso29119.md` | Stratégie et documentation des tests |
| CST | UML / ISO 19505 | `_prompt_cst.md` (sections 4-6) | Modélisation technique |
| CST | CCTP (Marchés publics FR) | `_prompt_cctp.md` | Cadre contractuel réglementé |
| CST | *Générique* | `_prompt_cst.md` | Vue d'ensemble des normes CST |

### DAT — Dossier d'Architecture Technique

| Document | Norme | Fichier | Usage principal |
|----------|-------|---------|-----------------|
| DAT | **ISO/IEC/IEEE 42010** (Description d'architecture) | `_prompt_dat_iso42010.md` | Cadre formel, audits, systèmes critiques |
| DAT | **C4 Model** (Simon Brown) | `_prompt_c4model.md` | Communication visuelle, équipes agiles |
| DAT | **ADR** (Architecture Decision Records) | `_prompt_dat_adr.md` | Documentation légère, décisions techniques |
| DAT | **UML 2.x / ISO 19505** | `_prompt_dat_uml.md` | 13 diagrammes UML complets |
| DAT | **ArchiMate 3.x** (The Open Group) | `_prompt_dat_archimate.md` | Architecture d'entreprise, alignement IT/Métier |
| DAT | Arc42 (Structure) | `_prompt_dat0.md` | Template européen, documentation structurée |
| DAT | *Générique* | `_prompt_dat_*.md` (variants format) | Formats de sortie (JSON, Mermaid, etc.) |

### CCTP — Cahier des Clauses Techniques Particulières

| Document | Norme | Fichier | Usage principal |
|----------|-------|---------|-----------------|
| CCTP | **Code de la commande publique** | `_prompt_cctp.md` | Cadre juridique marchés publics |
| CCTP | **RGS / ANSSI** (Sécurité) | `_prompt_cctp.md` (section 4) | Référentiel général de sécurité |
| CCTP | **RGPD** (Protection données) | `_prompt_cctp.md` (section 4) | Conformité données personnelles |

## Arborescence des prompts

```
.claude/prompts/
│
├── TypesDeDocumentsDAnalyse.md          ← Référence descriptive
├── GUIDE_PROMPTS_DOCUMENTATION.md       ← Guide d'utilisation
├── INDEX_PROMPTS_NORMES.md              ← Ce fichier
│
├── CCF — Cahier des Charges Fonctionnel
│   ├── _prompt_ccf.md                   ← Vue d'ensemble
│   ├── _prompt_ccf_nfen16271.md         ← NF EN 16271 (FR)
│   ├── _prompt_ccf_iso29148.md          ← ISO/IEC/IEEE 29148
│   └── _prompt_ccf_bpmn.md              ← BPMN / ISO 19510
│
├── CST — Cahier des Spécifications Techniques
│   ├── _prompt_cst.md                   ← Vue d'ensemble
│   ├── _prompt_cst_iso25010.md          ← ISO/IEC 25010 (Qualité)
│   └── _prompt_cst_iso29119.md          ← ISO/IEC/IEEE 29119 (Tests)
│
├── DAT — Dossier d'Architecture Technique
│   ├── _prompt_dat0.md                  ← Arc42
│   ├── _prompt_c4model.md               ← C4 Model
│   ├── _prompt_dat_iso42010.md          ← ISO/IEC/IEEE 42010
│   ├── _prompt_dat_adr.md               ← ADR + C4
│   ├── _prompt_dat_uml.md               ← UML / ISO 19505
│   └── _prompt_dat_archimate.md         ← ArchiMate
│
├── CCTP — Cahier des Clauses Techniques Particulières
│   └── _prompt_cctp.md                  ← Marchés publics FR
│
├── Formats de sortie DAT
│   ├── _prompt_dat_json.md
│   ├── _prompt_dat_mermaid.md
│   ├── _prompt_dat_plantuml.md
│   └── _prompt_dat_puml.md
│
└── Règles et réponses
    ├── _prompt_reponses.md
    └── REGLES_MERMAID.md
```

## Sélection rapide par contexte

### Contexte : Marché public français
```
CCF     → _prompt_ccf_nfen16271.md
CCTP    → _prompt_cctp.md
CST     → _prompt_cst.md + référentiels État
DAT     → _prompt_dat_iso42010.md (pour conformité audit)
```

### Contexte : Projet international / Multinational
```
CCF     → _prompt_ccf_iso29148.md
CST     → _prompt_cst_iso25010.md + _prompt_cst_iso29119.md
DAT     → _prompt_dat_uml.md ou _prompt_dat_archimate.md
```

### Contexte : Startup / Projet agile
```
CCF     → _prompt_ccf_bpmn.md (léger) ou User Stories
CST     → _prompt_cst_iso25010.md (essentiel)
DAT     → _prompt_dat_adr.md ou _prompt_c4model.md
```

### Contexte : Système critique (santé, finance, aéronautique)
```
CCF     → _prompt_ccf_iso29148.md (traçabilité renforcée)
CST     → _prompt_cst_iso29119.md (tests formels)
DAT     → _prompt_dat_iso42010.md (documentation formelle)
        + _prompt_dat_uml.md (modélisation complète)
```

### Contexte : Architecture d'entreprise
```
DAT     → _prompt_dat_archimate.md (multi-couches)
        + _prompt_dat_iso42010.md (cadre formel)
```

### Contexte : Communication technique
```
DAT     → _prompt_c4model.md (stakeholders techniques)
        + _prompt_dat_uml.md (développeurs)
```

## Correspondance normes ISO ↔ Documents

| Norme ISO/IEC | Domaine | Documents concernés | Prompt dédié |
|---------------|---------|---------------------|--------------|
| **NF EN 16271** | Expression du besoin (FR) | CCF | `_prompt_ccf_nfen16271.md` |
| **ISO/IEC/IEEE 29148** | Ingénierie des exigences | CCF | `_prompt_ccf_iso29148.md` |
| **ISO/IEC 19510** | BPMN | CCF | `_prompt_ccf_bpmn.md` |
| **ISO/IEC 25010** | Qualité logicielle | CST | `_prompt_cst_iso25010.md` |
| **ISO/IEC/IEEE 29119** | Tests | CST | `_prompt_cst_iso29119.md` |
| **ISO/IEC 19505** | UML | CST, DAT | `_prompt_cst.md`, `_prompt_dat_uml.md` |
| **ISO/IEC/IEEE 42010** | Architecture | DAT | `_prompt_dat_iso42010.md` |

## Normes réglementaires françaises

| Référentiel | Domaine | Document | Section |
|-------------|---------|----------|---------|
| **Code de la commande publique** | Marchés publics | CCTP | Tout le document |
| **RGS** (Référentiel Général de Sécurité) | Sécurité SI | CCTP, CST, DAT | Sections sécurité |
| **RGPD** | Protection données | CCTP, CCF | Traitement données personnelles |
| **RGI** (Référentiel Général d'Interopérabilité) | Interopérabilité | CST | Interfaces |
| **RGAA** | Accessibilité | CST | Utilisabilité/Accessibilité |

## Bonnes pratiques de sélection

1. **Un seul prompt CCF** : Choisir entre NF EN 16271 (FR public) ou ISO 29148 (international)
2. **CST complémentaires** : ISO 25010 (qualité) + ISO 29119 (tests) peuvent être combinés
3. **DAT selon l'audience** :
   - Direction/Métier → ArchiMate
   - Équipe technique → C4 Model ou UML
   - Audit/Conformité → ISO 42010
4. **Ajouter ADR** : Toujours compléter avec `_prompt_dat_adr.md` pour documenter les décisions

## Métriques de couverture

| Type | Normes couvertes | Prompts créés | Couverture |
|------|-----------------|---------------|------------|
| CCF | 3+ | 4 | 100% |
| CST | 3+ | 3 | 100% |
| DAT | 5+ | 6 | 100% |
| CCTP | 3+ | 1 | 100% |

---

*Dernière mise à jour : Analyse complète de `TypesDeDocumentsDAnalyse.md`*
