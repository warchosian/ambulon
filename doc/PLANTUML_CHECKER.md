# PlantUML Checker - Validateur de Conformité

Module de vérification automatique de la conformité des diagrammes PlantUML dans les documents Markdown selon les règles définies dans `REGLES_PLANTUML.md`.

## 🎯 Objectif

Le PlantUML Checker analyse vos fichiers Markdown contenant des diagrammes PlantUML et génère un rapport détaillé listant toutes les violations des règles de qualité.

## 📦 Installation

Le checker est inclus dans ambulon. Aucune installation supplémentaire n'est nécessaire.

## 🚀 Utilisation

### En ligne de commande

```bash
# Analyser un fichier et générer un rapport
python src/app/encoding/core/plantuml_checker.py doc/mon-document.md

# Spécifier le nom du rapport
python src/app/encoding/core/plantuml_checker.py doc/mon-document.md doc/rapport.md
```

### Depuis Python

```python
from src.app.encoding.core.plantuml_checker import PlantUMLChecker

# Créer un checker
checker = PlantUMLChecker('doc/mon-document.md')

# Vérifier toutes les règles
checker.check_all_rules()

# Générer le rapport
rapport = checker.generate_report('doc/rapport.md')

# Nombre de violations
print(f"{len(checker.violations)} violations détectées")
```

## 📋 Règles Vérifiées

Le checker vérifie actuellement **10 règles** :

### Règles critiques (erreurs 🔴)

| Règle | Description | Détection |
|-------|-------------|-----------|
| **#21-22** | @startuml/@enduml obligatoires | Vérifie la présence des balises de début/fin |
| **#2-6** | Ordre alias/couleur correct | Détecte `#COLOR as alias` (incorrect) |
| **#23** | Rectangles non vides | Détecte `{ }` sans ligne vide |
| **#24** | Mindmaps avec @startmindmap | Détecte mindmaps avec @startuml |
| **#25** | Pas d'emojis dans labels | Détecte ✅❌ dans `is`/`then`/`else`/`not` |
| **#27** | Pas de commentaires EVITER | Détecte `<!-- EVITER ` + balises |

### Règles recommandées (warnings 🟡)

| Règle | Description | Détection |
|-------|-------------|-----------|
| **#3** | Pas de listes à tirets dans rectangles | Détecte `- item` dans `rectangle { }` |
| **#12** | Utiliser `<b>` au lieu de `**` | Détecte `**` dans les notes |
| **#17** | Pas de caractères spéciaux | Détecte `=>`, `--` dans les noms |
| **#26** | Identification des diagrammes | Vérifie présence de `<figcaption>` |
| **#26** | Éviter `<figure markdown>` | Détecte les balises `<figure>` |

## 📝 Format du Rapport

Le rapport généré est un fichier Markdown structuré :

```markdown
# Rapport de Conformité PlantUML

**Fichier analysé** : `mon-document.md`
**Blocs PlantUML trouvés** : 18
**Violations détectées** : 21

---

## 📋 Résumé par Règle
- 🔴 **Règle #23 - Rectangle vide** : 2 violation(s)
- 🟡 **Règle #26 - Diagramme non identifié** : 18 violation(s)

---

## 📝 Détails des Violations

### Règle #23 - Rectangle vide

🔴 **Ligne 76** : Rectangle avec braces vides. Ajouter au moins une ligne vide entre { et }

### Règle #26 - Diagramme non identifié

🟡 **Ligne 26** : Diagramme sans <figcaption>. Ajouter une légende après le bloc

---

## 📚 Références

Consultez `doc/REGLES_PLANTUML.md` pour les détails de chaque règle.
```

## 🎨 Niveaux de Sévérité

- 🔴 **Erreur** : Violation critique qui peut empêcher le rendu ou causer des bugs
- 🟡 **Warning** : Recommandation de bonne pratique, le rendu fonctionne mais peut être amélioré

## ⚠️ Limitations Connues

### Mauvais Exemples Pédagogiques

Le checker détecte **toutes** les violations, y compris dans les blocs marqués comme "mauvais exemples" pédagogiques.

**Exemple** : Dans `REGLES_PLANTUML.md`, les mauvais exemples sont volontairement incorrects et seront détectés comme violations.

**Solution** : Examinez le rapport pour distinguer :
- Les **vraies violations** dans votre code de production
- Les **faux positifs** dans les exemples pédagogiques (sections "❌ Mauvais exemple")

### Faux Positifs Possibles

| Situation | Cause | Solution |
|-----------|-------|----------|
| Diagrammes sans `<figcaption>` | Document d'exemples de code | Normal pour docs techniques, ignorez le warning |
| Emojis détectés dans mauvais exemples | Exemples volontaires | Normal dans REGLES_PLANTUML.md |
| `<figure markdown>` détecté | Exemples montrant ce qu'il ne faut pas faire | Normal dans la documentation |

## 🔧 Code de Retour

Le checker retourne un code d'erreur si des violations **critiques** (🔴) sont détectées :

```bash
python plantuml_checker.py doc/mon-document.md
echo $?  # 1 si erreurs critiques, 0 sinon
```

Intégration dans un pipeline CI/CD :

```bash
# Échouer le build si violations critiques
python plantuml_checker.py doc/*.md || exit 1
```

## 📊 Exemples de Résultats

### Document conforme

```
Analyse terminee : 0 violations detectees
Rapport genere : doc/mon-document.violations.md
```

### Document avec violations

```
Analyse terminee : 21 violations detectees
Rapport genere : doc/guidelines-illustrated.violations.md
```

- **2 erreurs** (🔴) : Rectangles vides, emojis dans labels
- **19 warnings** (🟡) : Diagrammes sans légende

## 🚦 Intégration CI/CD

### GitHub Actions

```yaml
- name: Check PlantUML conformity
  run: |
    python src/app/encoding/core/plantuml_checker.py doc/**/*.md
    if [ $? -eq 1 ]; then
      echo "❌ Violations critiques détectées"
      exit 1
    fi
```

### GitLab CI

```yaml
plantuml_check:
  script:
    - python src/app/encoding/core/plantuml_checker.py doc/*.md
  artifacts:
    paths:
      - doc/*.violations.md
    when: always
```

## 📚 Références

- **Règles complètes** : `doc/REGLES_PLANTUML.md`
- **Guidelines Claude** : `doc/GUIDELINES_CLAUDE_PLANTUML.md`
- **Exemples** : `doc/figures.md`

## 🤝 Contribution

Pour ajouter une nouvelle règle au checker :

1. Ajouter la règle dans `doc/REGLES_PLANTUML.md`
2. Implémenter la méthode `check_rule_XX()` dans `plantuml_checker.py`
3. Appeler la méthode dans `check_all_rules()`
4. Tester sur les documents existants
5. Mettre à jour cette documentation

## 📝 Changelog

### v1.0.0 (2026-02-03)

- ✅ Vérification de 10 règles (21-27, 3, 12, 17, 26)
- ✅ Génération de rapports Markdown
- ✅ Support CLI et API Python
- ✅ Codes de retour pour CI/CD
- ✅ Détection de 37 blocs PlantUML dans REGLES_PLANTUML.md
- ✅ Détection de 18 blocs PlantUML dans guidelines-illustrated.md

---

**Auteur** : Projet Ambulon
**Licence** : Selon licence du projet
