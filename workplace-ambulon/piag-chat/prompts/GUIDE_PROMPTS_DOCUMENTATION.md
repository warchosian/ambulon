# Guide d'utilisation des prompts de documentation

Ce répertoire contient des prompts spécialisés pour la génération de documents de documentation informatique selon différentes normes et standards.

## Tableau comparatif des prompts

| Prompt | Type de document | Normes / Standards | Contexte d'utilisation | Public cible |
|--------|-----------------|-------------------|----------------------|--------------|
| `_prompt_ccf.md` | **CCF** — Cahier des Charges Fonctionnel | NF EN 16271, ISO/IEC/IEEE 29148, UML, BPMN | Expression du besoin métier | MOA, AMOA, utilisateurs, acheteurs |
| `_prompt_cst.md` | **CST** — Cahier des Spécifications Techniques | ISO/IEC 25010, ISO/IEC/IEEE 29119, ISO/IEC/IEEE 42010, UML | Conception technique | Développeurs, architectes, MOE |
| `_prompt_cctp.md` | **CCTP** — Cahier des Clauses Techniques Particulières | Code de la commande publique, RGS, RGPD, ANSSI | Marchés publics | Prestataires, autorités contractantes |
| `_prompt_dat0.md` | **DAT** — Dossier d'Architecture Technique (Arc42) | Arc42 (structure) | Documentation interne, agile | Équipes de développement |
| `_prompt_c4model.md` | **DAT** — Dossier d'Architecture Technique (C4) | C4 Model, PlantUML C4 | Communication visuelle architecture | Architectes, développeurs, stakeholders |
| `_prompt_dat_iso42010.md` | **DAT** — Dossier d'Architecture Technique (ISO 42010) | ISO/IEC/IEEE 42010:2022 | Systèmes critiques, audits formels | Architectes enterprise, auditeurs |
| `_prompt_dat_adr.md` | **DAT** — Dossier d'Architecture Technique (ADR) | ADR (Architecture Decision Records), C4 Model | Projets agiles, documentation vivante | Tech leads, équipes de développement |
| `_prompt_specs.md` | Spécification fonctionnelle et technique | Arc42, ISO/IEC/IEEE 29148 | Document complet (fonctionnel + technique) | Tous les intervenants |

## Chaîne de traçabilité

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     CCF     │ --> │     CST     │ --> │     DAT     │
│   (Quoi ?)  │     │  (Comment ?)│     │(Quelle      │
│  Fonctionnel│     │  Technique  │     │architecture?)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
   NF EN 16271        ISO 25010           ISO 42010
   ISO 29148          ISO 29119           C4 Model
   BPMN, Use Case     CCTP (public)       ADR
```

## Comment choisir le bon prompt ?

### 1. Selon la phase du projet

| Phase du projet | Document recommandé | Prompt à utiliser |
|----------------|---------------------|-------------------|
| Cadrage / Expression du besoin | CCF | `_prompt_ccf.md` |
| Consultation des entreprises (marché public) | CCTP | `_prompt_cctp.md` |
| Conception technique | CST | `_prompt_cst.md` |
| Architecture et design | DAT | Selon contexte (voir ci-dessous) |
| Mise en œuvre agile | DAT léger | `_prompt_dat_adr.md` ou `_prompt_dat0.md` |

### 2. Selon le contexte DAT

| Contexte | Prompt recommandé | Justification |
|----------|-------------------|---------------|
| Secteur public / Réglementé | `_prompt_dat_iso42010.md` | Conformité ISO, audit formel |
| Équipe agile / Startup | `_prompt_dat_adr.md` | Documentation légère, évolutive |
| Communication avec stakeholders | `_prompt_c4model.md` | Visualisation claire, C4 Model |
| Documentation interne rapide | `_prompt_dat0.md` | Structure Arc42 simplifiée |
| Système critique / Enterprise | `_prompt_dat_iso42010.md` + `_prompt_dat_adr.md` | Combinaison formelle + décisions |

### 3. Selon le public cible

| Public | Documents adaptés |
|--------|-------------------|
| MOA / AMOA / Métier | CCF, C4-L1 (Contexte) |
| Développeurs | CST, C4-L2/L3, ADR |
| Architectes | DAT (tous types) |
| RSSI / Sécurité | CCTP (partie sécurité), DAT (Vue sécurité) |
| Exploitants / Ops | CST (partie déploiement), DAT (Vue déploiement) |
| Prestataires / Fournisseurs | CCTP, CST |
| Auditeurs | DAT ISO 42010 |

## Mapping normes ↔ documents

### NF EN 16271 (CCF)
- Décomposition fonctionnelle du besoin
- Critères d'appréciation et pondération
- Distinction besoin / solution
- **Utiliser** : `_prompt_ccf.md`

### ISO/IEC/IEEE 29148 (Exigences)
- Ingénierie des exigences tout au long du cycle de vie
- Traçabilité des exigences
- Processus de validation
- **Utiliser** : `_prompt_ccf.md`, `_prompt_cst.md`

### ISO/IEC 25010 (Qualité)
- 8 caractéristiques de qualité logicielle
- Évaluation objective de la qualité
- **Utiliser** : `_prompt_cst.md`

### ISO/IEC/IEEE 29119 (Tests)
- Documentation des tests logiciels
- Processus de validation
- **Utiliser** : `_prompt_cst.md`, `_prompt_cctp.md`

### ISO/IEC/IEEE 42010 (Architecture)
- Description formelle d'architecture
- Vues, viewpoints, stakeholders
- **Utiliser** : `_prompt_dat_iso42010.md`

### C4 Model
- Visualisation hiérarchique de l'architecture
- Contexte → Conteneurs → Composants → Code
- **Utiliser** : `_prompt_c4model.md`, `_prompt_dat_adr.md`

### ADR (Architecture Decision Records)
- Documentation structurée des décisions
- Contexte, options, décision, conséquences
- **Utiliser** : `_prompt_dat_adr.md`

## Combinaisons recommandées

### Projet public / Secteur réglementé
```
CCF (NF EN 16271) 
    ↓
CCTP (Code commande publique + RGS)
    ↓
CST (ISO 25010 + ISO 29119)
    ↓
DAT (ISO 42010 + C4 Model)
```

### Projet privé / Agile
```
CCF léger (User Stories + critères d'acceptation)
    ↓
CST (ISO 25010)
    ↓
DAT (C4 Model + ADR)
```

### Système critique / Haute disponibilité
```
CCF (ISO 29148 + traçabilité renforcée)
    ↓
CST (ISO 25010 + ISO 29119 + audits)
    ↓
DAT (ISO 42010 + revue formelle + ADR)
```

## Ressources complémentaires

- `TypesDeDocumentsDAnalyse.md` : Description détaillée des types de documents
- `REGLES_PLANTUML.md` : Règles de syntaxe PlantUML
- `_prompt_reponses.md` : Guide de réponse aux questions
- `_prompt_dat_*.md` : Variantes DAT selon le format de sortie (JSON, Mermaid, etc.)

## Conseils d'utilisation

1. **Commencez par le CCF** : Ne passez à la technique (CST/DAT) qu'après stabilisation fonctionnelle
2. **Maintenez la traçabilité** : Chaque élément technique du CST/DAT doit remonter à un besoin du CCF
3. **Adaptez le niveau de formalisme** : Aucune norme ne doit être appliquée dogmatiquement
4. **Documentez les décisions** : Utilisez les ADR pour capturer le "pourquoi" des choix techniques
5. **Versionnez vos documents** : La documentation doit évoluer avec le projet

---

> 💡 **Bon à savoir** : Ces prompts sont conçus pour être utilisés avec des assistants IA (Claude, GPT, etc.) et générer des documents Markdown prêts à l'emploi dans VS Code ou Obsidian avec support PlantUML.
