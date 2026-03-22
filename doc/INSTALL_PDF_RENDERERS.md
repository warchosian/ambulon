# Installation des moteurs de rendu PDF

## Prérequis

La conversion HTML → PDF nécessite un moteur de rendu. Deux options sont disponibles :

| Option | Avantage | Inconvénient | Taille |
|--------|----------|--------------|--------|
| **Chromium** | ✅ Excellent support SVG | ⚠️ Installation séparée (~100 MB) | ~100 MB |
| **wkhtmltopdf** | ✅ Déjà présent sur le système | ⚠️ Support SVG limité | ~50 MB |

## Chromium (recommandé pour les diagrammes)

### ⚠️ Important

Le **package Python Playwright** est inclus dans la wheel, mais le **navigateur Chromium** doit être installé séparément car il fait ~100 MB et ne peut pas être embarqué dans la wheel.

### Installation

```bash
# Une seule fois par machine (après installation de la wheel)
python -m playwright install chromium
```

### Utilisation

```bash
ambulon html2pdf document.html --method chromium
```

### Support SVG

- ✅ Diagrammes PlantUML parfaitement rendus
- ✅ Diagrammes Mermaid parfaitement rendus  
- ✅ Graphiques SVG complexes supportés

---

## wkhtmltopdf (alternative)

Si vous préférez ne pas installer Chromium, utilisez wkhtmltopdf qui est déjà présent sur votre système.

### Utilisation

```bash
ambulon html2pdf document.html --method wkhtmltopdf
```

### Limitations SVG

- ⚠️ wkhtmltopdf 0.12.4 (votre version) : support SVG très limité
- ⚠️ Diagrammes complexes peuvent ne pas apparaître
- ⚠️ Recommandé uniquement pour documents sans diagrammes

Pour un meilleur support SVG avec wkhtmltopdf, mettez à jour vers 0.12.6+ :
https://wkhtmltopdf.org/downloads.html

---

## Workflow recommandé

### Pour documents avec diagrammes (PlantUML/Mermaid)

```bash
# 1. Installer Chromium (une seule fois)
python -m playwright install chromium

# 2. Convertir Markdown → HTML avec diagrammes
ambulon md2html-diagrams document.md -o document.html

# 3. Convertir HTML → PDF avec Chromium
ambulon html2pdf document.html --method chromium
```

### Pour documents simples (sans diagrammes)

```bash
# Utiliser wkhtmltopdf directement
ambulon html2pdf document.html --method wkhtmltopdf
```

---

## Dépannage

### "Chromium not available"

Le navigateur Chromium n'est pas installé. Exécutez :

```bash
python -m playwright install chromium
```

### "wkhtmltopdf not found"

wkhtmltopdf n'est pas dans le PATH. Spécifiez le chemin :

```bash
ambulon html2pdf doc.html --method wkhtmltopdf --wkhtmltopdf-path "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
```

### Les diagrammes n'apparaissent pas dans le PDF

C'est normal avec wkhtmltopdf < 0.12.6. Solutions :

1. **Utilisez Chromium** (recommandé) :
   ```bash
   python -m playwright install chromium
   ambulon html2pdf doc.html --method chromium
   ```

2. **Mettez à jour wkhtmltopdf** vers 0.12.6+ :
   https://wkhtmltopdf.org/downloads.html

---

## Résumé

| Besoin | Commande |
|--------|----------|
| Installation Chromium | `python -m playwright install chromium` |
| PDF avec diagrammes | `ambulon html2pdf doc.html --method chromium` |
| PDF sans diagrammes | `ambulon html2pdf doc.html --method wkhtmltopdf` |

**Note technique** : Playwright (package Python) est dans la wheel, mais Chromium (navigateur) est un binaire séparé que vous devez installer une fois par machine.
