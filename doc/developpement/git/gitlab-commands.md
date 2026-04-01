# Commandes GitLab

## Vue d'ensemble

Deux commandes sont disponibles pour cloner et traiter des dépôts GitLab :

| Commande | Module utilisé | Type de HTML généré |
|----------|---------------|---------------------|
| `gitlab-clone` | `monofile.py` | HTML simple (basique) |
| `gitlab-load` | `monofile_load.py` | **HTML interactif** (avec TOC + backlinks) |

---

## `gitlab-clone` (Version simple)

Génère un HTML statique basique à partir du Markdown.

### Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Repo cloné │────▶│  Monofile   │────▶│    HTML     │
│             │     │     MD      │     │   simple    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ md2html     │
                    │ (basique)   │
                    └─────────────┘
```

### Fichiers générés
- `<repo>.code.md` - Code consolidé
- `<repo>.code.html` - **HTML simple**

---

## `gitlab-load` (Version interactive)

Génère un HTML **interactif** avec table des matières cliquable et backlinks.

### Workflow complet

```
┌─────────────┐
│  Repo cloné │
│  (code.md)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      add-toc4md (Étape 1)                           │
│                    Génère: <repo>-toced.md                          │
│                         (avec TOC)                                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     add-itoc4md (Étape 2)                           │
│                  Génère: <repo>-itoced.md                           │
│         Ajoute les backlinks [↑] vers la table des matières         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       md2html (Étape 3)                             │
│            Convertit <repo>-itoced.md → <repo>-itoced.html          │
│                  (HTML avec diagrammes SVG)                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    augment (Étape 4)                                │
│         Transforme <repo>-itoced.html → <repo>-augmented.html       │
│            (rend le TOC cliquable/collapsible)                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Étapes détaillées

| Étape | Commande | Fichier produit | Description |
|-------|----------|-----------------|-------------|
| 1 | `add-toc4md` | `<repo>-toced.md` | Génère le Markdown avec **Table des Matières** (TOC) |
| 2 | `add-itoc4md` | `<repo>-itoced.md` | Ajoute les **backlinks** [↑] vers la TOC |
| 3 | `md2html` | `<repo>-itoced.html` | Convertit en HTML avec **diagrammes SVG** |
| 4 | `augment` | `<repo>-augmented.html` | Ajoute l'**interactivité** (TOC repliable/collapsible) |

### Fichiers générés

| Fichier | Description |
|---------|-------------|
| `<repo>.code.md` | Code consolidé (source) |
| `<repo>.code-toced.md` | Markdown avec **TOC** (étape 1) |
| `<repo>.code-itoced.md` | Markdown avec **TOC + backlinks [↑]** (étape 2) |
| `<repo>.code-itoced.html` | HTML avec diagrammes (étape 3) |
| `<repo>.code-augmented.html` | **HTML final augmenté** (étape 4) |

### Fonctionnalités de l'HTML interactif

- ✅ **Table des matières cliquable** - Navigation rapide
- ✅ **Backlinks [↑]** - Retour à la TOC depuis chaque titre
- ✅ **TOC repliable** - Interface épurée
- ✅ **Support des diagrammes** - Rendu Kroki/SVG

---

## Quand utiliser quelle commande ?

| Cas d'usage | Commande recommandée |
|-------------|---------------------|
| HTML simple, rapide | `gitlab-clone` |
| **Documentation navigable** | `gitlab-load` |
| Partage avec équipe | `gitlab-load` |
| Archive/PDF | `gitlab-clone` |

---

## Configuration

Les deux commandes utilisent le même fichier de configuration `config/gitlab.yaml` :

```yaml
gitlab:
  token: "${GITLAB_PRIVATE_TOKEN}"
  username: "oauth2"
  base_clone_dir: "./gitlab_clones"
  automation:
    enabled: true
    output_mode: "separate"  # ou "shared"
    code_monofile:
      enabled: true
      templates:
        - "{project}.code.md"
        - "{project}.code.html"      # gitlab-clone
        # - "{project}-interactive.html"  # gitlab-load
  repositories:
    - "https://gitlab.example.com/group/project.git"
```

---

## Architecture des modules

```
src/app/gitlab/
├── commands/
│   ├── gitlab_clone.py      # → utilise monofile.py
│   └── gitlab_load.py       # → utilise monofile_load.py
└── core/
    ├── monofile.py          # HTML simple (md2html-diagrams)
    └── monofile_load.py     # HTML interactif (md2interactive)
```
