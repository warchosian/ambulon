# VSCode Extension Management Module

Module de gestion des extensions VS Code / VSCodium pour la visualisation de diagrammes (PlantUML, Mermaid, Graphviz).

## 📦 Architecture

```
src/app/vscode/
├── core/
│   ├── detector.py           # Détection VS Code/VSCodium
│   ├── extension_manager.py  # CRUD sur les extensions
│   └── extension_config.py   # Configuration des extensions (charge config/vscode.yaml)
├── commands/
│   ├── vscode_install.py     # CLI: ambulon vscode-install
│   ├── vscode_uninstall.py   # CLI: ambulon vscode-uninstall
│   └── vscode_list.py        # CLI: ambulon vscode-list

config/vscode.yaml             # Configuration des extensions recommandées et redondantes
```

## 🚀 Commandes CLI

### **`ambulon vscode-install`** - Installer les extensions recommandées

Installe les extensions VS Code recommandées pour la visualisation de diagrammes.

```bash
# Mode interactif
ambulon vscode-install

# Installer uniquement les extensions ESSENTIELLES
ambulon vscode-install --mode 1

# Installer ESSENTIELLES + FORTEMENT RECOMMANDÉES (par défaut)
ambulon vscode-install --mode 2

# Installer TOUTES les extensions
ambulon vscode-install --mode 3

# Auto-confirmer l'installation
ambulon vscode-install --mode 2 --yes

# Spécifier l'éditeur
ambulon vscode-install --editor codium
ambulon vscode-install --editor cursor
ambulon vscode-install --editor code-insiders
```

**Options :**
- `--mode 1|2|3` : Mode d'installation (1=Essentielles, 2=Essentielles+Recommandées, 3=Toutes)
- `--editor code|codium|cursor|code-insiders` : Spécifier l'éditeur
  - `code` : VS Code
  - `codium` : VSCodium
  - `cursor` : Cursor
  - `code-insiders` : VS Code Insiders
- `-y, --yes` : Auto-confirmer sans prompt
- `-v, --verbose` : Mode verbeux

---

### **`ambulon vscode-uninstall`** - Désinstaller les extensions redondantes

Désinstalle les extensions redondantes ou inutiles détectées.

```bash
# Mode interactif
ambulon vscode-uninstall

# Auto-confirmer la désinstallation
ambulon vscode-uninstall --yes

# Spécifier l'éditeur
ambulon vscode-uninstall --editor code
```

**Options :**
- `--editor code|codium|cursor|code-insiders` : Spécifier l'éditeur
- `-y, --yes` : Auto-confirmer sans prompt
- `-v, --verbose` : Mode verbeux

---

### **`ambulon vscode-list`** - Lister les extensions installées

Affiche la liste des extensions installées avec comparaison aux extensions recommandées.

```bash
# Liste simple
ambulon vscode-list

# Comparer avec les extensions recommandées
ambulon vscode-list --show-recommended

# Spécifier l'éditeur
ambulon vscode-list --editor codium
```

**Options :**
- `--show-recommended` : Afficher la comparaison avec les extensions recommandées
- `--editor code|codium|cursor|code-insiders` : Spécifier l'éditeur
- `-v, --verbose` : Mode verbeux

---

## 🔀 Éditeurs supportés

Le module supporte 4 éditeurs compatibles avec les extensions VS Code :

- **VS Code (`--editor code`)** : Microsoft Visual Studio Code - version officielle avec télémétrie Microsoft
- **VSCodium (`--editor codium`)** : Version open-source de VS Code sans télémétrie ni tracking
- **Cursor (`--editor cursor`)** : Fork de VS Code avec IA intégrée (GPT-4, Claude, etc.)
- **VS Code Insiders (`--editor code-insiders`)** : Version preview/beta de VS Code avec nouvelles fonctionnalités

### Pourquoi plusieurs options ?

**Ce sont des applications distinctes avec des installations séparées** :

1. **Répertoires d'extensions différents** :
   - VS Code : `%USERPROFILE%\.vscode\extensions` (Windows) ou `~/.vscode/extensions` (Linux/macOS)
   - VSCodium : `%USERPROFILE%\.vscode-oss\extensions` (Windows) ou `~/.vscode-oss/extensions` (Linux/macOS)
   - Cursor : `%APPDATA%\Cursor\extensions` (Windows) ou `~/.cursor/extensions` (Linux/macOS)
   - VS Code Insiders : `%USERPROFILE%\.vscode-insiders\extensions` (Windows) ou `~/.vscode-insiders/extensions` (Linux/macOS)

2. **Extensions installées indépendamment** :
   - Les extensions installées dans un éditeur ne sont **pas** disponibles dans les autres
   - Chaque éditeur maintient sa propre liste d'extensions

3. **Marketplaces** :
   - VS Code / Cursor / Insiders : Visual Studio Marketplace (Microsoft)
   - VSCodium : Open VSX Registry par défaut (open-source)

### Exemples pratiques

```bash
# Lister les extensions de VS Code
ambulon vscode-list --editor code --show-recommended

# Lister les extensions de VSCodium
ambulon vscode-list --editor codium --show-recommended

# Lister les extensions de Cursor
ambulon vscode-list --editor cursor --show-recommended

# Lister les extensions de VS Code Insiders
ambulon vscode-list --editor code-insiders --show-recommended

# Installer dans VS Code
ambulon vscode-install --editor code --mode 2

# Installer dans Cursor (populaire avec IA intégrée)
ambulon vscode-install --editor cursor --mode 2
```

### Auto-détection

Si vous n'utilisez pas `--editor`, le module détecte automatiquement l'éditeur disponible (ordre de priorité) :
1. `code` (VS Code)
2. `cursor` (Cursor)
3. `code-insiders` (VS Code Insiders)
4. `codium` (VSCodium)

Si aucun n'est trouvé, affiche une erreur avec les chemins vérifiés.

**Important** : Si vous utilisez plusieurs éditeurs, vous devrez gérer les extensions séparément pour chacun en spécifiant `--editor code/codium/cursor/code-insiders`.

---

## 📚 Extensions recommandées

### ⭐ ESSENTIELLES

| Extension | Description | Catégorie |
|-----------|-------------|-----------|
| `jebbs.plantuml` | Le meilleur plugin pour PlantUML | 🌿 PlantUML |
| `bierner.markdown-mermaid` | Support Mermaid officiel Microsoft | 🌊 Mermaid |
| `tintinweb.graphviz-interactive-preview` | Preview interactif pour Graphviz/DOT | 🔗 Graphviz |
| `geeklearningio.graphviz-markdown-preview` | Support Graphviz dans Markdown | 🔗 Graphviz |

### 💡 FORTEMENT RECOMMANDÉES

| Extension | Description | Catégorie |
|-----------|-------------|-----------|
| `shd101wyy.markdown-preview-enhanced` | Markdown Preview tout-en-un (PlantUML + Mermaid + Graphviz) | 📝 Markdown |

### 🔧 OPTIONNELLES

| Extension | Description | Catégorie |
|-----------|-------------|-----------|
| `vstirbu.vscode-mermaid-preview` | Preview dédié Mermaid | 🌊 Mermaid |
| `gruntfuggly.mermaid-export` | Export de diagrammes Mermaid | 🌊 Mermaid |
| `hediet.vscode-drawio` | Éditeur de diagrammes visuel | 🎨 Éditeur visuel |
| `gera2ld.markmap-vscode` | Mind maps depuis Markdown | 🧠 Mind Map |

---

## 🗑️ Extensions redondantes détectées

Le module détecte et propose de désinstaller les extensions suivantes (doublons pour la visualisation de diagrammes) :

### Doublons PlantUML
- `clysto.plantuml` - Doublon PlantUML (garder `jebbs.plantuml`)
- `mebrahtom.plantumlpreviewer` - Doublon PlantUML (garder `jebbs.plantuml`)
- `well-ar.plantuml` - Doublon PlantUML - version ancienne

### Doublons Graphviz
- `prinorange.markdown-graphviz-preview` - Redondant avec `geeklearningio.graphviz-markdown-preview`

### Doublons Mind Map
- `souche.vscode-mindmap` - Mind map redondant (garder `gera2ld.markmap-vscode`)
- `season-studio.vsc-nano-mindmap` - Mind map redondant (garder `gera2ld.markmap-vscode`)

### Autres
- `nopeslide.vscode-drawio-plugin-mermaid` - Plugin DrawIO Mermaid peu utile

---

## 🔧 API Python

### Exemple d'utilisation programmatique

```python
from app.vscode.core import (
    find_vscode_command,
    get_installed_extensions,
    install_extension,
    RECOMMENDED_EXTENSIONS
)

# Détecter VS Code
vscode_cmd = find_vscode_command()  # Auto-détection
# ou
vscode_cmd = find_vscode_command("codium")  # VSCodium spécifique

# Lister les extensions installées
installed = get_installed_extensions(vscode_cmd)
print(f"Extensions installées : {len(installed)}")

# Installer une extension
success, message = install_extension("jebbs.plantuml", vscode_cmd)
if success:
    print("Installation réussie !")

# Accéder aux extensions recommandées
for ext_id, info in RECOMMENDED_EXTENSIONS.items():
    print(f"{ext_id}: {info['description']} ({info['priority']})")
```

---

## ⚙️ Configuration personnalisée

Les extensions recommandées et redondantes sont définies dans `config/vscode.yaml`. Vous pouvez personnaliser ce fichier selon vos besoins.

### Structure du fichier

```yaml
recommended_extensions:
  extension.id:
    description: "Description de l'extension"
    category: "🔗 Catégorie"
    priority: "ESSENTIEL"  # ou "FORTEMENT RECOMMANDÉ" ou "OPTIONNEL"

extensions_to_remove:
  extension.id: "Raison de la suppression"
```

### Exemple de personnalisation

```yaml
recommended_extensions:
  # Ajouter votre propre extension favorite
  custom.diagram-tool:
    description: "Mon outil de diagrammes préféré"
    category: "🎨 Custom"
    priority: "ESSENTIEL"

extensions_to_remove:
  # Ajouter une extension à supprimer
  unwanted.extension: "Cette extension est obsolète"
```

### Priorités disponibles

- **`ESSENTIEL`** : Installé avec `--mode 1`, `--mode 2` et `--mode 3`
- **`FORTEMENT RECOMMANDÉ`** : Installé avec `--mode 2` et `--mode 3`
- **`OPTIONNEL`** : Installé uniquement avec `--mode 3`

Après modification du fichier, les commandes `vscode-install`, `vscode-uninstall` et `vscode-list` utiliseront automatiquement la nouvelle configuration.

---

## 🎯 Workflow recommandé

1. **Nettoyer les extensions redondantes** :
   ```bash
   ambulon vscode-uninstall --yes
   ```

2. **Installer les extensions essentielles + recommandées** :
   ```bash
   ambulon vscode-install --mode 2 --yes
   ```

3. **Vérifier l'installation** :
   ```bash
   ambulon vscode-list --show-recommended
   ```

4. **Redémarrer VS Code** pour activer les extensions

5. **Tester** avec un fichier de diagrammes :
   - Ouvrir `_diagrams/multidiagrams.md` (s'il existe)
   - Utiliser `Ctrl+K V` pour ouvrir le preview Markdown

---

## 🐛 Dépannage

### VS Code/VSCodium non détecté

**Erreur** : `VS Code/VSCodium not found`

**Solution** :
1. Vérifier que VS Code/VSCodium est installé
2. Ajouter `code` ou `codium` au PATH système
3. Ou spécifier l'éditeur avec `--editor code` ou `--editor codium`

### Extensions non installées

**Erreur** : `Failed to install extension`

**Solutions** :
1. Vérifier la connexion Internet (téléchargement depuis le Marketplace)
2. Vérifier les permissions d'écriture sur le répertoire des extensions
3. Essayer de lancer VS Code en mode administrateur (Windows)
4. Consulter les logs avec `-v` pour plus de détails

### Chemins personnalisés

Si votre éditeur est dans un emplacement non-standard, le module vérifie ces emplacements :

**Windows** :
- VS Code : `C:\Program Files\Microsoft VS Code\bin\code.cmd` ou `%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd`
- VSCodium : `C:\Program Files\VSCodium\bin\codium.cmd` ou `%LOCALAPPDATA%\Programs\VSCodium\bin\codium.cmd`
- Cursor : `%LOCALAPPDATA%\Programs\Cursor\resources\app\bin\cursor.cmd`
- VS Code Insiders : `C:\Program Files\Microsoft VS Code Insiders\bin\code-insiders.cmd` ou `%LOCALAPPDATA%\Programs\Microsoft VS Code Insiders\bin\code-insiders.cmd`

**Linux** :
- `/usr/bin/{code,codium,cursor,code-insiders}`
- `/usr/local/bin/{code,codium,cursor,code-insiders}`
- `~/.local/bin/{code,codium,cursor,code-insiders}`

**macOS** :
- VS Code : `/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code`
- VSCodium : `/Applications/VSCodium.app/Contents/Resources/app/bin/codium`
- Cursor : `/Applications/Cursor.app/Contents/Resources/app/bin/cursor`
- VS Code Insiders : `/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code-insiders`

---

## 📝 Migration depuis `scripts/vscode/`

Ce module remplace les scripts Python dans `scripts/vscode/` :

| Ancien script | Nouvelle commande |
|---------------|-------------------|
| `python scripts/vscode/install_vscode_extensions.py` | `ambulon vscode-install` |
| `python scripts/vscode/uninstall_vscode_extensions.py` | `ambulon vscode-uninstall` |
| `scripts/manage_vscode_extensions.bat` | Interface CLI directe |

**Avantages de la nouvelle architecture** :
- ✅ Intégré dans le CLI Ambulon unifié
- ✅ Logging centralisé
- ✅ Code modulaire et testable
- ✅ API Python réutilisable
- ✅ Support multi-plateforme amélioré

---

## 🧪 Tests

```bash
# Tester la détection VS Code
python -m app.vscode.core.detector

# Tester la gestion des extensions
python -m app.vscode.core.extension_manager

# Tester les commandes CLI
ambulon vscode-list --help
ambulon vscode-install --help
ambulon vscode-uninstall --help
```

---

## 📄 Licence

Ce module fait partie du projet Ambulon.
