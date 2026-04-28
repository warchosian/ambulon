# Règles de Rédaction Mermaid - Ambulon

**Document de référence:** Bonnes pratiques pour écrire des diagrammes Mermaid sans erreurs

**Version:** 1.0  
**Dernière mise à jour:** 2026-04-28  
**Source:** Synthèse des pratiques du projet + corrections LLM

---

## 📋 Règles Principales

### ✅ Règle #1: Alias avant couleur
**Format correct:** `node "Label" as alias #COULEUR`

```
❌ graph TB
    cli(("CLI")) #FF6B6B as cli_node
    
✅ graph TB
    cli_node(("CLI")) as cli #FF6B6B
```

### ✅ Règle #2: Éviter caractères spéciaux dans IDs
**Interdits dans les identifiants:**
- `:` (interprété comme stéréotype)
- `\n` (newline)
- `*` ou `**` (conflits markdown)
- `/` dans les noms (confusion avec chemins)

```
❌ node1["feat:implementation"]
❌ node2["item/sub-item"]

✅ node1["Feature Implementation"]
✅ node2["item sub-item"]
```

### ✅ Règle #3: Fermer les blocs Mermaid
**Vérifier:** Chaque ` ```mermaid` doit avoir son ` ``` ` de fermeture

```
❌ ```mermaid
   graph TB
   A --> B
   (pas de fermeture!)

✅ ```mermaid
   graph TB
   A --> B
   ```
```

### ✅ Règle #4: Guillemets pour labels complexes
**Labels avec espaces ou caractères spéciaux doivent être guillemettés**

```
❌ graph TB
    A[My Node Name]
    
✅ graph TB
    A["My Node Name"]
```

### ✅ Règle #5: Parenthèses appairées
**Vérifier:** Tous les `(`, `[`, `{` ont leur fermeture

```
❌ graph TB
    A["open bracket
    B --> C]

✅ graph TB
    A["open bracket"]
    B --> C
```

### ✅ Règle #6: Arrows uniformes
**Format standard:** `-->` (tirets + chevron)

```
❌ A -> B
❌ A => B
❌ A ---> B (trop de tirets)

✅ A --> B
```

### ✅ Règle #7: Subgraphs bien fermés
**Format:** `subgraph id["Label"] ... end`

```
❌ subgraph group1 "Group Name"
   A --> B
   (pas de end)

✅ subgraph group1["Group Name"]
   A --> B
   end
```

### ✅ Règle #8: Init blocks valides
**Format:** `%%{init: {...}}%%`

```
❌ %%{init: {theme: dark}
❌ %%init: {theme: dark}%%

✅ %%{init: {'theme':'dark'}}%%
```

### ✅ Règle #9: Indentation cohérente
**Norme:** 4 espaces pour les niveaux imbriqués

```
❌ subgraph group1["Group"]
   A --> B
  C --> D
   end

✅ subgraph group1["Group"]
    A --> B
    C --> D
end
```

### ✅ Règle #10: Types de diagrammes valides
**Écriture lowercase:** `graph`, `flowchart`, `classDiagram`, `sequenceDiagram`, `usecaseDiagram`, `stateDiagram`, `gantt`, `pie`, `mindmap`

```
❌ GRAPH TD
❌ FlowChart LR

✅ graph TD
✅ flowchart LR
```

### ✅ Règle #11: Fermer TOUS les blocs de code
**CRITIQUE:** Tous les blocs (mermaid, plantuml, python, bash, etc.) doivent être fermés avec ` ``` ` sur sa propre ligne.

```
❌ ```mermaid
   graph TB
   A --> B
   (pas de fermeture!)
   
❌ ```plantuml
   @startuml
   :Activity:
   (pas de fermeture!)

✅ ```mermaid
   graph TB
   A --> B
   ```

✅ ```plantuml
   @startuml
   :Activity:
   @enduml
   ```
```

**Pourquoi:** Les blocs non fermés causent des erreurs de parsing et peuvent corrompre le reste du document. Chaque ouverture ` ```type` doit avoir sa fermeture ` ``` ` correspondante.

---

## 🆕 Nouvelles Règles Détectées par Analyse

Cette section est mise à jour lorsque de nouvelles règles ou corrections sont détectées.

**Dernière analyse:** 2026-04-28 08:11 UTC
**Fichiers analysés:** 217 (tous les fichiers générés)
**Nouvelles règles trouvées:** 1

### Règle #11: Fermer TOUS les blocs de code ✅ AJOUTÉE
- **Détectée par:** Validation DiagramValidator + inspection manuelle de admin_ep.ccf.gpt-oss_120b-cloud.md
- **Problème:** Blocs PlantUML et Markdown non fermés dans les fichiers générés
- **Solution:** Vérifier que chaque ` ```type` a sa fermeture ` ``` `
- **Impact:** CRITIQUE - Affecte 14+ fichiers dans l'échantillon testé

---

## 📊 Checklist de Validation

Avant de générer un diagramme Mermaid, vérifier:

- [ ] Bloc ` ```mermaid ... ``` ` correctement fermé
- [ ] Pas de caractères spéciaux (`:`, `*`, `/`) dans les IDs
- [ ] Alias avant couleur: `as alias #COULEUR`
- [ ] Guillemets autour des labels complexes
- [ ] Parenthèses/crochets/accolades appairés
- [ ] Arrows uniformes: `-->`
- [ ] Subgraphs avec `end`
- [ ] Init blocks: `%%{init: {...}}%%`
- [ ] Indentation 4 espaces
- [ ] Types diagrammes en lowercase

---

## 🔗 Références

- [Documentation Mermaid Officielle](https://mermaid-js.github.io/)
- [Syntax Reference](https://mermaid-js.github.io/syntax/syntax.html)
- Projet Ambulon: Règles complètes en `workplace-ambulon/piag-chat/prompts/REGLES_MERMAID.mmd.md`
