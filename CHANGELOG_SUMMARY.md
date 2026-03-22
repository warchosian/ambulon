# Résumé des changements pour v3.1.0

## 🆕 Nouvelles fonctionnalités

### Module TOC (Table des matières)
- `add-toc4md` : Ajoute une TOC HTML complète avec ancres aux fichiers Markdown
- `add-itoc4md` : Ajoute des backlinks (↑) vers la TOC sur chaque titre
- `check-toc4md` : Vérifie la présence d'une TOC
- `check-itoc4md` : Vérifie la présence des backlinks

### Module Diagrams
- `md2html-diagrams` : Convertit Markdown en HTML avec conversion PlantUML/Mermaid/Graphviz → SVG
- Génération auto de TOC avec marqueur `[TOC]` ou insertion après H1
- Support des backlinks dans les titres

### Module Processing
- `md2interactive` : **Workflow complet** MD → TOC → iTOC → HTML → Interactif
- `make-html-interactive` : Rend les SVG interactifs (zoom, drag, reset)

### Tests unitaires
- Suite de tests complète pour le module TOC
- Tests de régression pour éviter les doublons de TOC

## 🔧 Corrections majeures
- Correction des doublons de TOC
- Correction des backlinks (correspondance ID correcte)
- Correction de l'encodage UTF-8 (caractères accentués)
- Correction du positionnement de la TOC (après H1 et métadonnées)

## 📁 Structure
```
src/app/
├── toc/              # Nouveau module TOC
├── diagrams/         # Nouveau module Diagrams
├── processing/       # Complété avec md2interactive
└── cli/             # Commandes mises à jour

tests/unit/toc/      # Tests unitaires TOC
```

## 🎯 Exemple d'utilisation
```bash
# Workflow complet
ambulon md2interactive document.md
# Produit: document-itoc.md, document-itoc.html, document-interactive.html

# Ou étape par étape
ambulon add-toc4md doc.md -o doc-toced.md
ambulon add-itoc4md doc-toced.md -o doc-itoced.md
ambulon md2html-diagrams doc-itoced.md -o doc.html
ambulon make-html-interactive doc.html
```
