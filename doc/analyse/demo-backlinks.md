# Guide Ambulon - Conversion de Documents

[TOC]

## Introduction

Ambulon est un outil puissant pour la conversion de documents entre différents formats. Ce guide vous présente les principales fonctionnalités.

## Conversion Markdown vers HTML

La commande `md2html` permet de convertir des fichiers Markdown en HTML avec support des diagrammes.

### Diagrammes supportés

Ambulon supporte plusieurs types de diagrammes :

- **PlantUML** : diagrammes UML complets
- **Graphviz** : graphes et diagrammes de flux
- **Mermaid** : diagrammes simples et légers

### Options de conversion

Plusieurs options sont disponibles pour personnaliser la conversion :

#### Orientation de page

L'option `-p` ou `--page-orientation` permet d'optimiser pour la génération PDF :
- `portrait` : Format A4 vertical (700px)
- `landscape` : Format A4 horizontal (900px)

#### Mode standalone

Par défaut, md2html génère un document HTML complet avec CSS. L'option `--no-standalone` génère uniquement un fragment HTML.

## Table des matières

### Génération automatique

Utilisez le marqueur `[TOC]` dans votre Markdown pour générer automatiquement une table des matières.

### Liens de retour

L'option `--toc-backlinks` ajoute des flèches ↑ après chaque titre pour revenir facilement à la table des matières.

## Module add-toc-backlinks-md

Ce module permet d'ajouter des liens retour à des fichiers Markdown existants.

### Utilisation de base

```bash
ambulon add-toc-backlinks-md document.md
```

### Options avancées

- `--toc-id` : ID de l'ancre TOC (défaut: table-of-contents)
- `--link-text` : Texte du lien retour (défaut: ↑)
- `--min-level` : Niveau minimum des titres (1-6)
- `--max-level` : Niveau maximum des titres (1-6)

## Conversion HTML vers PDF

La commande `html2pdf` utilise Playwright pour générer des PDFs de haute qualité.

### Configuration

Assurez-vous que Chromium est installé :

```bash
playwright install chromium
```

### Workflow recommandé

Pour un rendu optimal :

1. Convertir Markdown en HTML avec orientation
2. Convertir HTML en PDF avec la même orientation

```bash
ambulon md2html doc.md -p landscape
ambulon html2pdf doc.html -p landscape
```

## Traitement des tableaux

Les tableaux Markdown sont convertis avec support du formatage inline :

| Fonctionnalité | Support |
|---------------|---------|
| **Gras** | ✓ |
| *Italique* | ✓ |
| `Code` | ✓ |

## Conclusion

Ambulon offre une suite complète d'outils pour la conversion et le traitement de documents. Consultez l'aide de chaque commande pour plus de détails.
