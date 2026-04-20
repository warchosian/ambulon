# Règles de Rédaction Mermaid

**Document de référence** : Bonnes pratiques pour écrire des diagrammes Mermaid sans erreurs

**Date de création** : 2026-02-02
**Auteur** : Hervé Marchal <herve.marchal@hotmail.fr>
**Version** : 1.0

---

## Table des Matières

1. [Principes Généraux](#principes-generaux)
2. [Rectangles et Composants](#rectangles-et-composants)
3. [Diagrammes d'Objets](#diagrammes-objets)
4. [Diagrammes d'Activité](#diagrammes-activite)
5. [Notes et Documentation](#notes-et-documentation)
6. [Commentaires et Symboles](#commentaires-symboles)
7. [Mindmaps](#mindmaps)
8. [Compatibilité Slinky vs Graphviz](#compatibilite)
9. [Checklist de Validation](#checklist)

---

<a name="principes-generaux"></a>
## 1. Principes Généraux

### ✅ Règle #1 : Privilégier la Complexité

**TOUJOURS préférer les structures complexes aux structures simples.**

#### ❌ Mauvais exemple (simplicité + notes)

```text
rectangle "Level 1" as level1

note right of level1
  <b>Level 2</b>
  • Item 1
  • Item 2

  <b>Level 3</b>
  • Détail 1
  • Détail 2
end note
```

```mermaid
graph TB
    level1["Level 1"]
    note2["<b>Level 2</b><br>• Item 1<br>• Item 2<br><br><b>Level 3</b><br>• Détail 1<br>• Détail 2"]
    level1 --> note2
```
**Pourquoi** : L'utilisation de notes peut masquer la structure réelle du diagramme et le rendre moins détaillé.

#### ✅ Bon exemple (structure complexe)

```text
rectangle "Level 1" {
  rectangle "Level 2" {
    rectangle "Level 3" {
      - Item 1
      - Item 2
    }
  }
}
```

```mermaid
graph TD
    A["Level 1"]
    B["Level 2"]
    C["Level 3"]
    D["Item 1"]
    E["Item 2"]
    A --> B
    B --> C
    C --> D
    C --> E
```
**Pourquoi** : Les structures imbriquées reflètent mieux la complexité du système.

---

### ✅ Règle #2 : Mettre l'alias avant la couleur

**L'alias doit être défini AVANT la couleur pour éviter les erreurs de référence.**

#### ❌ Mauvais exemple (couleur avant alias)

```text
rectangle "1. Arguments CLI" #FF6B6B as cli

note bottom of cli
  <b>Priorité MAXIMALE</b>
  Contenu de la note
end note
```

```mermaid
graph TB
    cli(("1. Arguments CLI")) ==> "Priorité MAXIMALE\nContenu de la note"
    style cli fill:#FF6B6B
```
**Pourquoi** : Mettre la couleur (#FF6B6B) AVANT l'alias (as cli) peut causer des problèmes de parsing. L'alias risque de ne pas être reconnu correctement.

#### ✅ Bon exemple (alias avant couleur)

```text
rectangle "1. Arguments CLI" as cli #FF6B6B

note bottom of cli
  <b>Priorité MAXIMALE</b>
  Contenu de la note
end note
```

```mermaid
graph TB
    cli(("1. Arguments CLI"))[#FF6B6B]
    click cli href "javascript:void(0);" "1. Arguments CLI"
    cli:::note
    cli --> "Priorité MAXIMALE\nContenu de la note"
```

**Pourquoi** : L'ordre correct est : `nom as alias #couleur`. L'alias vient immédiatement après le nom, puis la couleur.

#### 🔧 Comment corriger

**Transformation** : `rectangle "Nom" #COULEUR as alias` → `rectangle "Nom" as alias #COULEUR`

1. Placer `as alias` juste après le nom de l'élément
2. Placer la couleur `#COULEUR` en dernier
3. Ordre correct : **nom → alias → couleur**

---

### ✅ Règle #3 : Éviter les Caractères Spéciaux dans les Noms

**Liste des caractères à éviter dans les identifiants** :
- `:` (deux-points) - interprété comme séparateur de stéréotype
- `\n` (newline) - cause des erreurs de référence
- `*` (astérisque) - conflit avec le markdown Mermaid
- `**` (double astérisque) - conflit avec le bold dans mindmaps

#### ❌ Mauvais exemple

```text
object "feat:" {
  Impact = MINOR
}
```

```mermaid
graph TB
    object("feat:") --> Impact("Impact = MINOR")
```
**Pourquoi** : L'utilisation de `:` dans le nom de l'objet est interprétée comme un séparateur de stéréotype et peut causer des erreurs.

#### ✅ Bon exemple

```text
object feat {
  Type = "feat:"
  Impact = MINOR
}
```

```mermaid
graph TB
    feat[feat:<br/>Type = "feat:"<br/>Impact = MINOR]
```
**Pourquoi** : Le nom de l'objet est un identifiant simple, et le type est défini comme un attribut, ce qui est la syntaxe correcte.

---

<a name="rectangles-et-composants"></a>
## 2. Rectangles et Composants

### ✅ Règle #5 : Utiliser les Listes à Tirets dans les Rectangles Imbriqués

**TOUJOURS privilégier les listes à tirets dans les rectangles imbriqués pour une meilleure lisibilité.**

#### ❌ Mauvais exemple (utiliser des notes)

```text
rectangle "Container" #LIGHTBLUE as container

note right of container
  <b>Actions:</b>
  • Action 1
  • Action 2
  • Action 3
end note
```

```mermaid
graph TB
    container("Container"):::lightblue
    note_right[Actions:<br>• Action 1<br>• Action 2<br>• Action 3]
```
**Pourquoi** : L'utilisation de notes pour de courtes listes peut être verbeuse et moins directe.

#### ✅ Bon exemple

```text
rectangle "Container" {
  rectangle "Actions" {
    - Action 1
    - Action 2
    - Action 3
  }
}
```

```mermaid
graph TD
    Container("Container")
    Actions("Actions")
    Actions --> "Action 1"
    Actions --> "Action 2"
    Actions --> "Action 3"
```
**Pourquoi** : C'est une syntaxe plus compacte et lisible pour les listes simples.

---

### ✅ Règle #6 : Indenter les Packages sur Plusieurs Lignes

**TOUJOURS formater les packages avec accolades sur plusieurs lignes avec indentation correcte.**

#### ❌ Mauvais exemple (tout sur une ligne)

```text
package "controller" {
    package "accueil" { [AccueilAction] }
    package "agents" { [AgentRechercheAction] }
}
```

```mermaid
graph TB
    subgraph controller
        subgraph accueil
            AccueilAction
        end
        subgraph agents
            AgentRechercheAction
        end
    end
```

**Pourquoi** : Le formatage sur une seule ligne rend le code difficile à lire et à maintenir, surtout avec plusieurs niveaux d'imbrication.

#### ✅ Bon exemple (indentation sur plusieurs lignes)

```text
package "controller" {
    package "accueil" {
        [AccueilAction]
    }
    package "agents" {
        [AgentRechercheAction]
    }
}
```

```mermaid
graph TB
    subgraph controller
        subgraph accueil
            A[AccueilAction]
        end
        subgraph agents
            B[AgentRechercheAction]
        end
    end
```

**Pourquoi** :
- Meilleure lisibilité du code
- Structure hiérarchique claire
- Facilite les modifications et la maintenance
- Permet d'ajouter facilement du contenu dans les packages

#### 🔧 Comment corriger

**Transformation** : `package "nom" { [Element] }` → formatter sur plusieurs lignes

**Avant** :
```text
package "services" { package "auth" { [AuthService] } }
```

**Après** :
```text
package "services" {
    package "auth" {
        [AuthService]
    }
}
```

**Règles d'indentation** :
- Utiliser 4 espaces par niveau d'indentation (ou 2 espaces de manière cohérente)
- Accolade ouvrante `{` à la fin de la ligne du package
- Contenu indenté d'un niveau
- Accolade fermante `}` alignée avec le début du package parent

---

### ✅ Règle #7 : Mettre la couleur après l'alias

#### ❌ Mauvais exemple

```text
rectangle "Config" {
  config/piag.yaml:
    timeout: 120
    retries: 3
}
```

```mermaid
graph TB
    config(("Config" #FFFFE0))
    config --> piagyaml
    style config fill:#FFFFE0
    piagyaml[piag.yaml: timeout: 120 retries: 3]
```
**Pourquoi** : L'indentation YAML/JSON à l'intérieur du rectangle est mal interprétée par Mermaid. Le contenu ne s'affiche pas comme prévu.

#### ✅ Bon exemple (utiliser des notes)

```text
rectangle "Config" #LIGHTYELLOW as config

note right of config
  <b>config/piag.yaml:</b>
  timeout: 120
  retries: 3
end note
```

```mermaid
graph LR
    config("Config"):::lightyellow
    config -->|<b>config/piag.yaml:</b>| note1
    note1 -->|timeout: 120| note2
    note1 -->|retries: 3| note3
```
**Pourquoi** : Les notes préservent le formatage du texte pré-formaté et sont le conteneur approprié pour des extraits de code ou de configuration.

#### 🔧 Comment corriger

**Transformation** : Contenu indenté dans rectangle → Note avec contenu pré-formaté

1. Créer un rectangle simple avec un alias : `rectangle "Config" as config`
2. Ajouter une couleur pour distinguer : `#LIGHTYELLOW`
3. Créer une note attachée : `note right of config`
4. Mettre le contenu YAML/JSON dans la note (l'indentation est préservée)
5. Utiliser `<b>...</b>` pour les titres dans la note
6. Fermer avec `end note`

---

<a name="diagrammes-objets"></a>
## 3. Diagrammes d'Objets

_Note : Les bonnes pratiques de style pour les objets Mermaid sont documentées dans le guide des guidelines Claude._

---

<a name="diagrammes-activite"></a>
## 4. Diagrammes d'Activité

### ✅ Règle #9 : `backward` Uniquement dans `repeat...repeat while`

**NE JAMAIS utiliser `backward` en dehors d'une structure `repeat`.**

#### ❌ Mauvais exemple (backward sans repeat)

```text
if (Validation OK ?) then (✅ oui)
  :Continuer;
else (❌ non)
  :Corriger;
  backward :Re-tester;  # ❌ ERREUR
endif
```

```mermaid
graph TD
    A[(Validation OK ?)] -->|✅ oui| B[Continuer]
    A -->|❌ non| C[Corriger]
    C --> D[Re-tester] # ❌ ERREUR
```
**Pourquoi** : `backward` est un mot-clé réservé pour les boucles `repeat`.

#### ✅ Bon exemple (repeat...repeat while)

```text
repeat
  :Tests & validation;

  if (Validation OK ?) then (oui)
  else (non)
    :Corriger;
    :Rebuild;
  endif

repeat while (Validation OK ?) is (non) not (oui)
```

```mermaid
graph TD
    A[Tests & validation] -->|Validation OK ?| B((oui))
    A -->|non| C[Corriger]
    C --> D[Rebuild]
    D --> E{Validation OK ?}
    E -- oui --> B
    E -- non --> C
```
**Pourquoi** : La structure `repeat...repeat while` est la manière correcte d'implémenter des boucles qui peuvent nécessiter de revenir en arrière.

---



<a name="notes-et-documentation"></a>
## 5. Notes et Documentation

### ✅ Règle #12 : Utiliser `<b>` pour le Bold dans les Notes

**Utiliser les balises HTML pour le formatage dans les notes.**

```text
note right of element
  <b>Titre en Gras</b>
  <i>Texte en italique</i>
  <u>Texte souligné</u>

  Texte normal
end note
```

```mermaid
graph TB
    element("Element")::box
    note_right(element) "Titre en Gras\nTexte en italique\nTexte souligné\nTexte normal"
```

**Balises supportées** :
- `<b>texte</b>` - gras
- `<i>texte</i>` - italique
- `<u>texte</u>` - souligné
- `<color:red>texte</color>` - couleur

---

### ✅ Règle #13 : Échapper les Caractères Spéciaux dans les Notes

**Utiliser `<` et `>` pour les chevrons dans les notes.**

```text
note right of element
  Format: <source>2<dest>

  Fichiers:
  - commands/<name>.py
  - core/<name>_converter.py
end note
```

```mermaid
graph LR
    element(("Element"))
    noteRight[Format: <source>2<dest>\n\nFichiers:\n- commands/<name>.py\n- core/<name>_converter.py]
    element --> noteRight
```

---

<a name="commentaires-symboles"></a>
## 6. Commentaires et Symboles

### ✅ Règle #19 : Utiliser les Commentaires Correctement

**Utiliser les commentaires Mermaid pour documenter le code du diagramme.**

```text
' Commentaire sur une seule ligne (apostrophe)

/'
  Ceci est un commentaire
  sur plusieurs lignes.
  Il explique une section complexe du diagramme.
'/

actor Utilisateur
participant Système

Utilisateur -> Système : Fait une requête ' Description de la requête
```

```mermaid
sequenceDiagram
    participant Utilisateur
    participant Système
    Utilisateur->>Système: Fait une requête ' Description de la requête
```

**Pourquoi** : Les commentaires aident à la compréhension et à la maintenance des diagrammes, surtout pour les sections complexes ou les choix de conception.

---

### ✅ Règle #20 : Éviter les Caractères Spéciaux non Supportés

**Éviter l'utilisation de symboles qui peuvent être interprétés comme des éléments Mermaid.**

#### ❌ Mauvais exemple (peut causer des problèmes de parsing)

```text
rectangle "Ma Fonction => Resultat" {
  -- Option 1 --
}
```

```mermaid
graph TD
    A[Ma Fonction => Resultat] --> B[Option 1]
```
**Pourquoi** : Certains symboles (comme `=>`, `--`, `->`) ont une signification spéciale en Mermaid et peuvent perturber le parsing s'ils sont utilisés hors de leur contexte.

#### ✅ Bon exemple (Utiliser des noms descriptifs sans symboles spéciaux ou notes)

```text
rectangle "Ma Fonction et son Résultat" as funcResult

note bottom of funcResult
  Option 1 : Description
end note
```

```mermaid
graph TB
    funcResult("Ma Fonction et son Résultat")
    funcResult --> "Option 1 : Description"
```
**Pourquoi** : En évitant les symboles réservés, on garantit que le diagramme sera parsé correctement.

---

### ✅ Règle #21 : Balises @startuml et @enduml Obligatoires

**TOUJOURS encadrer les diagrammes Mermaid avec les balises `@startuml` et `@enduml`.**

#### ❌ Mauvais exemple (sans balises)

```text
rectangle "Element" as elem

note right of elem
  Description
end note
```

**Pourquoi** : Sans ces balises, Mermaid ne peut pas identifier le début et la fin du diagramme. Le code ne sera pas converti en image.

#### ✅ Bon exemple (avec balises)

```text
@startuml
rectangle "Element" as elem

note right of elem
  Description
end note
@enduml
```

```mermaid
graph LR
  elem("Element")
  noteRight("Description")
  elem --> noteRight
```

**Pourquoi** : Les balises `@startuml` et `@enduml` délimitent le code Mermaid et permettent sa conversion en SVG/image.

**Note importante** : Dans un fichier Markdown, ces balises doivent être à l'intérieur du bloc ` ```Mermaid ` :

```markdown
\```mermaid
graph TB
    A["Test"]
```

---

### ✅ Règle #22 : Toujours Fermer avec @enduml

**TOUJOURS terminer un diagramme Mermaid par `@enduml`, sinon le diagramme ne sera pas converti.**

#### ❌ Mauvais exemple (oubli de @enduml)

```text
@startuml
object nomObjet
nomObjet : attribut1 = valeur1
nomObjet : attribut2 = valeur2
```

**Erreur** : Le diagramme n'est jamais fermé. Mermaid ne sait pas où se termine le code.

#### ✅ Bon exemple (avec @enduml)

```text
@startuml
object nomObjet
nomObjet : attribut1 = valeur1
nomObjet : attribut2 = valeur2
@enduml
```

```mermaid
nomObjet[("nomObjet\nattribut1 = valeur1\nattribut2 = valeur2")]
```

**Pourquoi** : `@enduml` ferme le bloc Mermaid et indique que le diagramme est complet. Sans cette balise, le rendu échoue.

#### 🔧 Comment corriger

**Symptôme** : Diagramme non converti en image, code source affiché tel quel

**Solution** :
1. Vérifier que chaque `@startuml` a son `@enduml` correspondant
2. Placer `@enduml` à la fin du code Mermaid, juste avant ` ``` `
3. Ne PAS oublier le `@` devant `enduml`

**Pattern correct** :
```
```mermaid
graph TB
    A[Hard Drive] -->|SATA| B((Motherboard))
    B -->|USB| C[Keyboard]
    B -->|PS/2| D[Mouse]
    B -->|Ethernet| E[Router]
    B -->|Wi-Fi| F[Router]
    B -->|HDMI| G[Monitor]
    B -->|Audio| H[Speakers]
```
```

---

### ✅ Règle #23 : Rectangles avec Accolades Non Vides

**Les rectangles avec accolades `{ }` doivent contenir au moins une ligne (même vide).**

#### ❌ Mauvais exemple (rectangle vide)

```text
rectangle "Mon Element" as elem #LIGHTBLUE {
}
```

```mermaid
graph TB
    elem("Mon Element")::lightblue
```

**Erreur** : Le rectangle avec accolades est complètement vide. Mermaid peut mal interpréter cette syntaxe et produire un rendu incorrect.

#### ✅ Bon exemple (avec au moins une ligne)

**Option 1** : Ajouter une ligne vide à l'intérieur
```text
rectangle "Mon Element" as elem #LIGHTBLUE {

}
```

```mermaid
graph TB
    elem["Mon Element"]("Mon Element") style elem fill:#add8e6,stroke:#000000,stroke-width:2px
```

**Option 2** : Ajouter du contenu
```text
rectangle "Mon Element" as elem #LIGHTBLUE {
  - Item 1
  - Item 2
}
```

```mermaid
graph TB
    elem("Mon Element")::lightblue
    elem --> "Item 1"
    elem --> "Item 2"
```

**Option 3** : Utiliser un rectangle sans accolades
```text
rectangle "Mon Element" as elem #LIGHTBLUE
```

```mermaid
graph TB
    elem("Mon Element")::lightblue
```

**Pourquoi** : Les accolades vides `{ }` peuvent causer des problèmes de parsing. Si le rectangle n'a pas de contenu, soit ajouter une ligne vide, soit ne pas utiliser d'accolades.

#### 🔧 Comment corriger

**Transformation** : `rectangle "Nom" { }` → `rectangle "Nom" { <ligne vide> }` ou `rectangle "Nom"`

1. Si le rectangle doit rester vide : ajouter une ligne vide entre les accolades
2. Si possible : ajouter du contenu (liste, texte)
3. Alternative : supprimer les accolades si pas de contenu

**Pattern recommandé** :
- Avec contenu : `rectangle "Nom" { - Item }`
- Sans contenu : `rectangle "Nom"` (pas d'accolades)
- Vide temporaire : `rectangle "Nom" { <espace> }`

---

### ✅ Règle #24 : Utiliser @startmindmap pour les Mindmaps

**Les mindmaps doivent utiliser `@startmindmap`/`@endmindmap`, PAS `mermaid` code blocks.**

#### ❌ Mauvais exemple (utilise @startuml)

```text
@startuml
@startmindmap
* Racine
** Branche 1
*** Sous-branche
@endmindmap
@enduml
```

```mermaid
graph TB
Racine --> Branche_1
Branche_1 --> Sous_branche
```

**Erreur** : Utiliser `@startuml` avec `@startmindmap` est redondant et incorrect. Les mindmaps ont leurs propres balises.

#### ✅ Bon exemple (utilise @startmindmap)

```text
@startmindmap
* Racine
** Branche 1
*** Sous-branche 1.1
*** Sous-branche 1.2
** Branche 2
@endmindmap
```

```mermaid
graph TD
    Racine --> Branche_1
    Racine --> Branche_2
    Branche_1 --> Sous-branche_1.1
    Branche_1 --> Sous-branche_1.2
```

**Pourquoi** : Les mindmaps sont un type spécial de diagramme Mermaid qui utilise sa propre syntaxe de délimitation.

#### 🔧 Comment corriger

**Transformation** :
```
❌ @startuml              ✅ @startmindmap
   @startmindmap             * Racine
   * Racine                  ** Branche
   @endmindmap               @endmindmap
   @enduml
```

**Solution** :
1. Remplacer `@startuml` par `@startmindmap` au début
2. Remplacer `@enduml` par `@endmindmap` à la fin
3. Supprimer `@startmindmap` et `@endmindmap` internes si présents

**Pattern correct pour mindmap** :
```
@startmindmap
* Nœud racine
** Niveau 1
*** Niveau 2
@endmindmap
```

**Pattern incorrect** :
```
@startuml
@startmindmap
...
@endmindmap
@enduml
```

---

### ✅ Règle #25 : Pas d'Emojis dans les Labels

**Ne PAS utiliser d'emojis (✅, ❌, etc.) dans les labels de diagrammes d'activité (`is`, `then`, `else`).**

#### ❌ Mauvais exemple (emojis dans labels)

```text
if (Validation OK ?) then (✅ oui)
  :Continuer;
else (❌ non)
  :Corriger;
endif
```

```mermaid
graph TD
    A[(Validation OK ?)] -->|✅ oui| B[Continuer]
    A -->|❌ non| C[Corriger]
```

**Erreur** : Les emojis/icônes (✅, ❌, 🚀, etc.) dans les labels peuvent causer des problèmes d'encodage et de rendu selon l'environnement Mermaid.

#### ✅ Bon exemple (texte simple)

```text
if (Validation OK ?) then (oui)
  :Continuer;
else (non)
  :Corriger;
endif
```

```mermaid
graph TD
    A[(Validation OK ?)] -->|oui| B[Continuer]
    A -->|non| C[Corriger]
```

**Pourquoi** : Les labels textuels simples garantissent un rendu cohérent sur tous les environnements (terminal, PDF, HTML, etc.).

#### 🔧 Comment corriger

**Transformation** : Retirer les emojis des labels `is`, `then`, `else`, `not`

**Exemples de corrections** :
- `is (✅ oui)` → `is (oui)`
- `is (❌ non)` → `is (non)`
- `then (✅ succès)` → `then (succès)`
- `else (❌ échec)` → `else (échec)`

**Note** : Les emojis restent acceptables dans :
- Les titres (`title 🚀 Mon Diagramme`)
- Le contenu des notes
- Le texte des rectangles
- Les noms d'éléments (mais déconseillé)

**Zones à éviter pour les emojis** :
- Labels `is (...)`, `then (...)`, `else (...)`, `not (...)`
- Labels de boucles `repeat while (...)`
- Identifiants d'alias

---

<a name="mindmaps"></a>
## 7. Mindmaps

### ✅ Règle #16 : Respecter la Hiérarchie des Mindmaps

**Structure hiérarchique stricte** :
- `*` - Nœud racine (1 seul)
- `**` - Niveau 1 (enfants de la racine)
- `***` - Niveau 2 (petits-enfants)
- `****` - Niveau 3 (arrière-petits-enfants)

```text
@startmindmap
* Racine
** Branche 1
*** Sous-branche 1.1
*** Sous-branche 1.2
** Branche 2
*** Sous-branche 2.1
@endmindmap
```

```mermaid
graph TB
Racine --> Branche1
Racine --> Branche2
Branche1 --> SousBranche1.1
Branche1 --> SousBranche1.2
Branche2 --> SousBranche2.1
```

---

<a name="compatibilite"></a>
## 8. Compatibilité Slinky vs Graphviz

### Comprendre les Deux Moteurs de Rendu Mermaid

**Mermaid utilise deux moteurs de rendu** :

1. **Slinky (moteur natif Java)** - Pas besoin de Graphviz
   - Activity diagrams
   - Sequence diagrams
   - State diagrams
   - Object diagrams simples
   - Mindmaps
   - Rectangles avec flèches simples

2. **Graphviz (moteur externe)** - Nécessite installation de Graphviz
   - Class diagrams avec relations
   - Component diagrams avec imbrication
   - Package diagrams
   - Deployment diagrams

---

### ✅ Règle #18 : Privilégier les Diagrammes Compatibles Slinky

**Pour une portabilité maximale, utiliser les types de diagrammes qui fonctionnent sans Graphviz.**

**Diagrammes recommandés (Slinky)** :
- Activity diagrams pour les workflows
- Sequence diagrams pour les interactions
- Rectangles simples pour les architectures
- Object diagrams pour les données
- Mindmaps pour les concepts

**Diagrammes à éviter (Graphviz requis)** :
- Class diagrams avec relations `-->`
- Component diagrams avec imbrication
- Package diagrams

---

<a name="documentation"></a>
## 9. Documentation et Formatage Markdown

### ✅ Règle #26 : Identifier Chaque Diagramme (Sans Balises HTML Complexes)

**Au-delà du code Mermaid lui-même, dans le document Markdown contenant les diagrammes, chaque diagramme doit être identifié de manière simple et portable.**

**IMPORTANT** : **Éviter les balises `<figure markdown>` et `</figure>`** qui causent des problèmes de compatibilité entre les convertisseurs Markdown.

#### ✅ Bon exemple (identification simple et portable)

```markdown
Comme illustré à la **Figure 1.1**, l'architecture repose sur trois couches principales.

```mermaid
graph TB
    style CouchePrésentation fill:#FFA07A,stroke:#333333,stroke-width:2px
    subgraph Couche Présentation
    FrontendReact[Frontend React]
    end
    style CoucheServices fill:#FFA07A,stroke:#333333,stroke-width:2px
    subgraph Couche Services
    AuthService[Auth Service]
    end
    FrontendReact --> AuthService : HTTPS / JSON
```
<figcaption>Figure 1.1 – Architecture globale à trois couches</figcaption>

> ℹ️ *Source : Conception équipe DevOps, février 2026.*
```

**Éléments recommandés** :
1. **Référence dans le texte** : `**Figure X.Y**` mentionnée AVANT le diagramme
2. **Bloc Mermaid** : Directement avec ` ```Mermaid ` (sans balise HTML)
3. **Légende** : `<figcaption>Figure X.Y – Description</figcaption>` SOUS le diagramme
4. **Source** (optionnel) : Note informative avec `> ℹ️ *Source: ...*`

#### ❌ Mauvais exemple 1 (diagramme nu sans identification)

```markdown
```mermaid
graph TB
    subgraph "Services"
        AuthService["Auth Service"]
    end
```
```

**Problèmes** :
- Pas de référence dans le texte
- Pas de légende
- Impossible de référencer dans le document

#### ❌ Mauvais exemple 2 (utilisation de `<figure markdown>`)

```markdown
<figure markdown>
```mermaid
graph LR
    A["Test"]
```
<figcaption>Figure 1 – Test</figcaption>
</figure>
```

**Problèmes** :
- Balises `<figure markdown>` et `</figure>` causent des problèmes de compatibilité
- Non supporté par tous les convertisseurs Markdown (GitHub, certains parsers)
- Peut casser le rendu lors de conversion MD → HTML → PDF

**Pourquoi éviter `<figure markdown>` ?**
- ❌ Incompatibilité avec GitHub/GitLab Markdown
- ❌ Problèmes avec certains convertisseurs (Pandoc, ambulon)
- ❌ Balises HTML mixées avec Markdown = parsing fragile
- ✅ Approche simple avec `<figcaption>` seul = plus robuste et portable

**Pourquoi identifier les diagrammes ?**
- Référencement croisé dans le document
- Traçabilité et professionnalisme
- Conformité aux standards de documentation technique
- Facilite la maintenance et les mises à jour

---

### ✅ Règle #27 : Éviter les Commentaires qui Cassent le Rendu

**Ne PAS utiliser de commentaires HTML contenant des balises Markdown (` ```markdown `) ou des balises HTML (`<figure>`, `</figure>`) car ils empêchent le rendu correct des diagrammes.**

#### ❌ Mauvais exemples (commentaires problématiques)

**Exemple 1 : Commentaire avec \`\`\`markdown**
```markdown
<!-- EVITER
```markdown
-->
# Mon document

<figure markdown>
```mermaid
graph LR
    A["Test"]
```
</figure>
```

**Problème** : Le ` ```markdown ` dans le commentaire casse le parsing Markdown.

**Exemple 2 : Commentaire avec balises HTML**
```markdown
<!-- EVITER
<figure markdown>
-->
```mermaid
graph TB
    rectangle("Test")
```
<figcaption>Figure 1 – Test</figcaption>
<!-- EVITER
</figure>
-->
```

**Problème** : Les balises `<figure>` et `</figure>` commentées désynchronisent le parsing HTML.

**Exemple 3 : Commentaire quote avec EVITER**
```markdown
'EVITER <figure markdown>
```mermaid
graph TB
    A["Test"]
```
</figure>
```

**Problème** : Le `'EVITER` avec balise HTML perturbe le rendu.

#### ✅ Bon exemple (commentaires corrects)

```markdown
<!-- Note: Ce diagramme illustre l'architecture -->

<figure markdown>
```mermaid
graph TB
    rectangle("Test")
```
<figcaption>Figure 1 – Test</figcaption>
</figure>

<!-- TODO: Ajouter une note sur les performances -->
```

**Commentaires acceptables** :
- `<!-- Note simple sans balises Markdown/HTML -->`
- `<!-- TODO: Description de tâche -->`
- `<!-- FIXME: Problème à corriger -->`

**Commentaires à ÉVITER** :
- `<!-- EVITER ` suivi de ` ```markdown `
- `<!-- EVITER <figure> -->`
- `'EVITER <balise-html>`
- Tout commentaire contenant des délimiteurs de code ou balises

**Pourquoi** : Les commentaires avec balises Markdown/HTML perturbent le parsing et causent :
- Non-rendu des diagrammes
- Désynchronisation des balises ouvrantes/fermantes
- Échec de conversion MD → HTML → PDF
- Problèmes d'affichage dans les éditeurs (Obsidian, VSCode)

#### 🔧 Comment corriger

**Transformation** : Supprimer ou simplifier les commentaires problématiques

**Avant** :
```markdown
<!-- EVITER
```markdown
-->
<figure markdown>
```

**Après** :
```markdown
<!-- Exemple de figure avec diagramme -->
<figure markdown>
```

**Ou encore mieux** : Supprimer complètement les commentaires `EVITER` si ce sont des exemples de ce qu'il ne faut pas faire. Dans ce cas, documenter dans une section séparée avec des blocs de code texte.

---

<a name="checklist"></a>
## 10. Checklist de Validation

### Avant de Générer un PDF Mermaid

**Vérifier les points suivants** :

- [ ] **Pas de nesting > 2 niveaux** de rectangles
- [ ] **Pas de listes à tirets** dans des rectangles imbriqués
- [ ] **Pas de YAML/JSON indenté** dans des rectangles
- [ ] **Tous les éléments ont des alias simples** (pas de `\n`, `:`, etc.)
- [ ] **Notes utilisées** pour les contenus complexes
- [ ] **Syntaxe object correcte** : `object nom` puis `nom : attr = val`
- [ ] **Pas de `:` dans les noms** d'objets ou rectangles
- [ ] **`backward` uniquement dans `repeat...repeat while`**

- [ ] **Tous les blocs ont `@startuml` et `@enduml`** (Règle #21, #22)
- [ ] **Rectangles avec braces `{ }` ont au moins une ligne** (Règle #23)
- [ ] **Mindmaps utilisent `@startmindmap`/`@endmindmap`** (Règle #24)
- [ ] **Pas d'emojis dans les labels** `is`, `then`, `else`, `not` (Règle #25)
- [ ] **Diagrammes identifiés avec référence + `<figcaption>`** (Règle #26)
- [ ] **Éviter `<figure markdown>` et `</figure>`** (Règle #26)
- [ ] **Pas de commentaires `<!-- EVITER ` avec balises MD/HTML** (Règle #27)

- [ ] **Pas de `**` dans les mindmaps** (sauf pour hiérarchie)
- [ ] **Class diagrams convertis en rectangles** si pas de Graphviz
- [ ] **Utilisation de `<b>` au lieu de `**`** pour le bold dans les notes
- [ ] **Commentaires utilisés** pour documenter le code du diagramme
- [ ] **Pas de caractères spéciaux non supportés** dans les noms d'éléments (ex: `=>`, `--`, `->`)

