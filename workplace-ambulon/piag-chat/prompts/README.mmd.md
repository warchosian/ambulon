# Prompts de Documentation Technique

Ce répertoire contient l'ensemble des prompts pour générer des documents de documentation technique conformes aux normes et standards internationaux.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [**GUIDE_COMPLET_PROMPTS.md**](GUIDE_COMPLET_PROMPTS.md) | Guide exhaustif avec tous les prompts, matrice de sélection, exemples d'utilisation |
| [GUIDE_PROMPTS_DOCUMENTATION.md](GUIDE_PROMPTS_DOCUMENTATION.md) | Guide de sélection par contexte |
| [INDEX_PROMPTS_NORMES.md](INDEX_PROMPTS_NORMES.md) | Index matriciel Document × Norme |
| [TypesDeDocumentsDAnalyse.md](TypesDeDocumentsDAnalyse.md) | Description détaillée des types de documents (CCF, CST, DAT, CCTP) |
| [REGLES_MERMAID.md](REGLES_MERMAID.md) | Règles de syntaxe Mermaid |

## 🚀 Démarrage rapide

### 1. Identifier le type de document nécessaire

```
Besoin fonctionnel (QUOI)      → CCF
Spécification technique (COMMENT) → CST
Architecture (STRUCTURE)       → DAT
Marché public (CONTRACTUEL)    → CCTP
```

### 2. Choisir le prompt approprié

**Pour un projet public français :**
- CCF : `_prompt_ccf_nfen16271.md` (NF EN 16271)
- CST : `_prompt_cctp.md` (Cahier des Clauses Techniques Particulières)
- DAT : `_prompt_dat_iso42010.md` (ISO 42010)

**Pour un projet agile :**
- CCF : `_prompt_ccf_bpmn.md` (Processus métier)
- CST : `_prompt_cst_iso25010.md` (Qualité)
- DAT : `_prompt_dat_adr.md` (Architecture Decision Records)

**Pour un projet international :**
- CCF : `_prompt_ccf_iso29148.md` (Ingénierie des exigences)
- CST : `_prompt_cst_iso25010.md` + `_prompt_cst_iso29119.md`
- DAT : `_prompt_dat_uml.md` ou `_prompt_dat_archimate.md`

### 3. Utiliser le prompt

Copier le contenu du fichier prompt et le soumettre à votre assistant IA (Claude, GPT, etc.) avec les informations spécifiques à votre projet.

## 📁 Catalogue des prompts

### CCF — Cahier des Charges Fonctionnel

| Fichier | Norme | Contexte |
|---------|-------|----------|
| `_prompt_ccf.md` | Vue d'ensemble | Découverte |
| `_prompt_ccf_nfen16271.md` | NF EN 16271 | Marchés publics FR |
| `_prompt_ccf_iso29148.md` | ISO/IEC/IEEE 29148 | International, traçabilité |
| `_prompt_ccf_bpmn.md` | BPMN / ISO 19510 | Processus, workflow |

### CST — Cahier des Spécifications Techniques

| Fichier | Norme | Focus |
|---------|-------|-------|
| `_prompt_cst.md` | Vue d'ensemble | Découverte |
| `_prompt_cst_iso25010.md` | ISO/IEC 25010 | Qualité logicielle (8 caractéristiques) |
| `_prompt_cst_iso29119.md` | ISO/IEC/IEEE 29119 | Tests logiciels |

### DAT — Dossier d'Architecture Technique

| Fichier | Standard | Usage |
|---------|----------|-------|
| `_prompt_dat_iso42010.md` | ISO/IEC/IEEE 42010 | Formel, audits |
| `_prompt_dat_adr.md` | ADR + C4 Model | Agile, documentation vivante |
| `_prompt_dat_uml.md` | UML / ISO 19505 | Modélisation objet complète |
| `_prompt_dat_archimate.md` | ArchiMate 3.x | Architecture d'entreprise |
| `_prompt_c4model.md` | C4 Model | Communication technique |
| `_prompt_dat0.md` | Arc42 | Structure européenne |

### CCTP — Cahier des Clauses Techniques Particulières

| Fichier | Références | Usage |
|---------|------------|-------|
| `_prompt_cctp.md` | Code commande publique, RGS, RGPD | Marchés publics |

### Formats de sortie (DAT)

| Fichier | Format |
|---------|--------|
| `_prompt_dat_json.md` | JSON |
| `_prompt_dat_mermaid.md` | Mermaid |
| `_prompt_dat_plantuml.md` | Mermaid |
| `_prompt_dat_puml.md` | Mermaid (variant) |

## 🎯 Chaîne documentaire recommandée

```
CCF (Expression du besoin)
    ↓
CST (Spécifications techniques)
    ↓
DAT (Architecture technique)
```

Chaque document doit référencer le précédent et maintenir la traçabilité.

## 📊 Matrice de sélection rapide

| Contexte | CCF | CST | DAT |
|----------|-----|-----|-----|
| Marché public FR | `_ccf_nfen16271` | `_cctp` | `_iso42010` |
| Projet international | `_ccf_iso29148` | `_iso25010` + `_iso29119` | `_uml` |
| Projet agile | `_ccf_bpmn` | `_iso25010` | `_adr` |
| Système critique | `_ccf_iso29148` | `_iso29119` | `_iso42010` + `_uml` |
| Architecture d'entreprise | — | — | `_archimate` |

## 🔧 Conventions

### Format de sortie
Tous les prompts produisent des documents en **Markdown (.md)** avec :
- Table des matières cliquable `[TOC]`
- Diagrammes en **Mermaid**
- Tableaux structurés
- Liens internes de navigation
- Compatible **VS Code** et **Obsidian**

### Nomenclature des fichiers
```
_prompt_[type]_[norme].md

Type : ccf | cst | dat | cctp
Norme : nfen16271 | iso29148 | iso25010 | iso29119 | iso42010 | 
        uml | archimate | adr | c4model | bpmn | ...
```

## 📖 Ressources externes

- [Normes ISO](https://www.iso.org/)
- [AFNOR](https://www.afnor.org/)
- [The Open Group - ArchiMate](https://www.opengroup.org/archimate)
- [C4 Model](https://c4model.com/)
- [Arc42](https://arc42.org/)
- [SemVer](https://semver.org/)

---

*Repository : Ambulon*  
*Dernière mise à jour : 2026-03-19*
