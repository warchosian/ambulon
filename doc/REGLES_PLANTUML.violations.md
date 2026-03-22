# Rapport de Conformité PlantUML
**Fichier analysé** : `REGLES_PLANTUML.md`
**Date** : 1770114914.6547904
**Blocs PlantUML trouvés** : 37
**Violations détectées** : 69

---

## 📋 Résumé par Règle
- 🟡 **Règle #17 - Caractères spéciaux** : 1 violation(s)
- 🔴 **Règle #2/#6 - Ordre alias/couleur incorrect** : 3 violation(s)
- 🔴 **Règle #22 - @enduml obligatoire** : 1 violation(s)
- 🔴 **Règle #23 - Rectangle vide** : 2 violation(s)
- 🔴 **Règle #25 - Emojis dans labels** : 4 violation(s)
- 🟡 **Règle #26 - Diagramme non identifié** : 33 violation(s)
- 🟡 **Règle #26 - Utilisation de <figure>** : 15 violation(s)
- 🔴 **Règle #27 - Commentaire problématique** : 3 violation(s)
- 🟡 **Règle #3 - Liste à tirets dans rectangle** : 7 violation(s)

---

## 📝 Détails des Violations

### Règle #17 - Caractères spéciaux

🟡 **Ligne 520** : Caractère spécial '=>' peut causer des problèmes
```plantuml
rectangle "Ma Fonction => Resultat" {
```

### Règle #2/#6 - Ordre alias/couleur incorrect

🔴 **Ligne 111** : L'alias doit être AVANT la couleur : 'as alias #COULEUR' et non '#COULEUR as alias'
```plantuml
rectangle "1. Arguments CLI" #FF6B6B as cli
```

🔴 **Ligne 223** : L'alias doit être AVANT la couleur : 'as alias #COULEUR' et non '#COULEUR as alias'
```plantuml
rectangle "Container" #LIGHTBLUE as container
```

🔴 **Ligne 276** : L'alias doit être AVANT la couleur : 'as alias #COULEUR' et non '#COULEUR as alias'
```plantuml
rectangle "Config" #LIGHTYELLOW as config {
```

### Règle #22 - @enduml obligatoire

🔴 **Ligne 348** : Bloc PlantUML sans @enduml ou @endmindmap
```plantuml
@startuml
if (Validation OK ?) then (✅ oui)
  :Continuer;
else (❌ non)
  :Corriger;
  backward :Re-t
```

### Règle #23 - Rectangle vide

🔴 **Ligne 668** : Rectangle avec braces vides. Ajouter au moins une ligne vide entre { et }

🔴 **Ligne 686** : Rectangle avec braces vides. Ajouter au moins une ligne vide entre { et }

### Règle #25 - Emojis dans labels

🔴 **Ligne 350** : Ne pas utiliser d'emojis dans les labels is/then/else/not
```plantuml
if (Validation OK ?) then (✅ oui)
```

🔴 **Ligne 352** : Ne pas utiliser d'emojis dans les labels is/then/else/not
```plantuml
else (❌ non)
```

🔴 **Ligne 843** : Ne pas utiliser d'emojis dans les labels is/then/else/not
```plantuml
if (Validation OK ?) then (✅ oui)
```

🔴 **Ligne 845** : Ne pas utiliser d'emojis dans les labels is/then/else/not
```plantuml
else (❌ non)
```

### Règle #26 - Diagramme non identifié

🟡 **Ligne 48** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 78** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 109** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 132** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 171** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 189** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 221** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 247** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 274** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 297** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 348** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 374** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 411** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 447** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 485** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 518** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 537** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 578** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 593** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 627** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 648** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 668** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 686** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 702** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 716** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 755** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 779** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 841** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 863** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 920** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 1017** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 1077** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

🟡 **Ligne 1108** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

### Règle #26 - Utilisation de <figure>

🟡 **Ligne 981** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
**IMPORTANT** : **Éviter les balises `<figure markdown>` et `</figure>`** qui causent des problèmes de compatibilité entre les convertisseurs Markdown.
```

🟡 **Ligne 1031** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
#### ❌ Mauvais exemple 2 (utilisation de `<figure markdown>`)
```

🟡 **Ligne 1034** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
<figure markdown>
```

🟡 **Ligne 1045** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
- Balises `<figure markdown>` et `</figure>` causent des problèmes de compatibilité
```

🟡 **Ligne 1049** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
**Pourquoi éviter `<figure markdown>` ?**
```

🟡 **Ligne 1065** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
**Ne PAS utiliser de commentaires HTML contenant des balises Markdown (` ```markdown `) ou des balises HTML (`<figure>`, `</figure>`) car ils empêchent le rendu correct des diagrammes.**
```

🟡 **Ligne 1076** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
<figure markdown>
```

🟡 **Ligne 1090** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
<figure markdown>
```

🟡 **Ligne 1103** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
**Problème** : Les balises `<figure>` et `</figure>` commentées désynchronisent le parsing HTML.
```

🟡 **Ligne 1107** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
'EVITER <figure markdown>
```

🟡 **Ligne 1123** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
<figure markdown>
```

🟡 **Ligne 1142** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
- `<!-- EVITER <figure> -->`
```

🟡 **Ligne 1161** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
<figure markdown>
```

🟡 **Ligne 1167** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
<figure markdown>
```

🟡 **Ligne 1195** : Éviter les balises <figure markdown> et </figure> (problèmes de compatibilité)
```plantuml
- [ ] **Éviter `<figure markdown>` et `</figure>`** (Règle #26)
```

### Règle #27 - Commentaire problématique

🔴 **Ligne 1107** : Commentaire EVITER avec balises Markdown/HTML casse le rendu
```plantuml
'EVITER <figure markdown>
```

🔴 **Ligne 1142** : Commentaire EVITER avec balises Markdown/HTML casse le rendu
```plantuml
- `<!-- EVITER <figure> -->`
```

🔴 **Ligne 1143** : Commentaire EVITER avec balises Markdown/HTML casse le rendu
```plantuml
- `'EVITER <balise-html>`
```

### Règle #3 - Liste à tirets dans rectangle

🟡 **Ligne 83** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Item 1
```

🟡 **Ligne 84** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Item 2
```

🟡 **Ligne 251** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Action 1
```

🟡 **Ligne 252** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Action 2
```

🟡 **Ligne 253** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Action 3
```

🟡 **Ligne 705** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Item 1
```

🟡 **Ligne 706** : Les listes à tirets dans rectangles peuvent causer des problèmes de rendu
```plantuml
- Item 2
```

---

## 📚 Références

Consultez `doc/REGLES_PLANTUML.md` pour les détails de chaque règle.
