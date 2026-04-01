# Workflow Git - Ambulon

Documentation visuelle du workflow de branches et de release avec diagrammes PlantUML.

---

## Architecture des Branches (Option B - Production First)

### Diagramme de l'Architecture Globale

```plantuml
@startuml
!theme plain

skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial
skinparam ArrowColor #2C3E50
skinparam BoxPadding 10

' Définir les acteurs
actor Développeur as dev
participant "feature/*" as feature #FFE5B4
participant "preprod/vX.X.X-stable" as preprod #FFFACD
participant "prod/vX.X.X-stable" as prod #90EE90
participant "main" as main #87CEEB

title Workflow des Branches Git - Ambulon (Option B)

== Phase 1: Développement ==
dev -> feature: 1. Créer feature branch
activate feature
feature -> feature: Développement\n(commits conventionnels)
feature -> feature: cz bump\n(version 3.0.1 → 3.0.2)
feature -> feature: poetry build
feature -> feature: build_offline_package.py

== Phase 2: Pré-Production ==
feature -> preprod: 2. Créer preprod/v3.0.2-stable
deactivate feature
activate preprod
preprod -> preprod: Tests & Validation
note right of preprod
  - Installation offline
  - Tests fonctionnels
  - Vérification docs
  - Tests d'intégration
end note

== Phase 3: Production ==
preprod -> prod: 3. Créer prod/v3.0.2-stable\n(si validation OK)
deactivate preprod
activate prod
prod -> prod: Tag v3.0.2
note right of prod
  Branche immuable
  Ne reçoit JAMAIS
  de commits directs
end note

== Phase 4: Mise à jour Main ==
prod -> main: 4. Sync main avec prod\n(git reset --hard)
activate main
note right of main
  main = miroir de prod
  Branche par défaut GitHub
  Toujours à jour avec
  la dernière prod stable
end note

@enduml
```

---

## Cycle de Vie Détaillé des Branches

### Diagramme d'État

```plantuml
@startuml
!theme plain

skinparam state {
  BackgroundColor<<Feature>> #FFE5B4
  BackgroundColor<<Preprod>> #FFFACD
  BackgroundColor<<Prod>> #90EE90
  BackgroundColor<<Main>> #87CEEB
  BorderColor #2C3E50
  ArrowColor #2C3E50
}

title Cycle de Vie des Branches - Ambulon

[*] --> Development

state Development <<Feature>> {
  [*] --> CreateFeature : git checkout -b\nfeature/ma-fonctionnalite
  CreateFeature --> Coding : Développement
  Coding --> Committing : git add .\ncz commit
  Committing --> Coding : Nouvelles modifications
  Committing --> Bumping : Fonctionnalité terminée
  Bumping --> Building : cz bump\n(3.0.1 → 3.0.2)
  Building --> ReadyForPreprod : poetry build\nbuild_offline_package.py
}

state PreProduction <<Preprod>> {
  ReadyForPreprod --> CreatePreprod : git checkout -b\npreprod/v3.0.2-stable
  CreatePreprod --> Testing : Tests & Validation
  Testing --> BugFound : Bug détecté
  BugFound --> FixBug : Correction
  FixBug --> NewVersion : cz bump\n(3.0.2 → 3.0.3)
  NewVersion --> Testing : Re-test
  Testing --> Validated : ✅ Tous les tests OK
}

state Production <<Prod>> {
  Validated --> CreateProd : git checkout -b\nprod/v3.0.2-stable
  CreateProd --> TagRelease : git tag -a 3.0.2
  TagRelease --> PushProd : git push --tags
  PushProd --> Immutable : 🔒 Branche immuable
}

state MainBranch <<Main>> {
  Immutable --> SyncMain : git checkout main\ngit reset --hard\nprod/v3.0.2-stable
  SyncMain --> UpdatedMain : git push origin main
  UpdatedMain --> [*] : ✅ Release terminée
}

note right of Development
  Branches feature/* :
  - Développement actif
  - Commits conventionnels
  - Supprimées après merge
end note

note right of PreProduction
  Branches preprod/* :
  - Tests et validation
  - Corrections de bugs
  - Package offline généré
  - Conservées sur GitHub
end note

note right of Production
  Branches prod/* :
  - Version déployée
  - Immuable (aucun commit)
  - Tagguée (vX.X.X)
  - Conservée indéfiniment
end note

note right of MainBranch
  Branche main :
  - Miroir de prod
  - Branche par défaut GitHub
  - Jamais de développement direct
  - Toujours stable
end note

@enduml
```

---

## Processus de Release Complet

### Diagramme de Séquence

```plantuml
@startuml
!theme plain

skinparam ParticipantBackgroundColor #F0F0F0
skinparam ParticipantBorderColor #2C3E50
skinparam SequenceArrowColor #2C3E50
skinparam BoxPadding 20

title Processus de Release - Ambulon v3.0.2

actor "Développeur" as dev
participant "Git Repo" as git
participant "feature/\nma-fonctionnalite" as feature
participant "preprod/\nv3.0.2-stable" as preprod
participant "prod/\nv3.0.2-stable" as prod
participant "main" as main
participant "GitHub" as github

== Étape 1: Développement ==
dev -> git: git checkout -b\nfeature/ma-fonctionnalite
activate feature
dev -> feature: Développement du code
dev -> feature: cz commit (plusieurs fois)
note right of dev
  Commits conventionnels:
  - feat: nouvelle fonctionnalité
  - fix: correction de bug
  - docs: documentation
end note

== Étape 2: Version Bump & Build ==
dev -> feature: cz bump
note right of dev
  Analyse des commits
  3.0.1 → 3.0.2
  Mise à jour:
  - pyproject.toml
  - src/app/__init__.py
  - CHANGELOG.md
end note

dev -> feature: poetry build
dev -> feature: python scripts/\nbuild_offline_package.py
note right of dev
  Génère:
  - dist/ambulon-3.0.2*.whl
  - dist-offline/ambulon-3.0.2-offline-install.zip
end note

== Étape 3: Création Preprod ==
dev -> git: git checkout -b\npreprod/v3.0.2-stable
activate preprod
deactivate feature
dev -> preprod: git add dist/ dist-offline/\npyproject.toml CHANGELOG.md
dev -> preprod: git commit -m\n"bump: version 3.0.1 → 3.0.2"
dev -> preprod: git tag -a 3.0.2
dev -> github: git push origin\npreprod/v3.0.2-stable --tags
github --> dev: ✅ Branche et tag créés

== Étape 4: Tests & Validation ==
dev -> preprod: Tests installation offline
dev -> preprod: Tests fonctionnels
dev -> preprod: Vérification documentation
dev -> preprod: Tests d'intégration

alt Validation réussie
  note right of dev: ✅ Tous les tests passent
else Bug détecté
  dev -> preprod: Correction du bug
  dev -> preprod: cz bump (3.0.2 → 3.0.3)
  dev -> preprod: Re-build & re-test
  note right of dev: Recommencer validation
end

== Étape 5: Promotion Production ==
dev -> git: git checkout\npreprod/v3.0.2-stable
dev -> git: git checkout -b\nprod/v3.0.2-stable
activate prod
deactivate preprod
dev -> github: git push origin\nprod/v3.0.2-stable --tags
github --> dev: ✅ Branche prod créée
note right of prod
  🔒 Branche immuable
  Ne recevra jamais
  de commits directs
end note

== Étape 6: Mise à jour Main ==
dev -> git: git checkout main
activate main
dev -> main: git reset --hard\nprod/v3.0.2-stable
note right of dev
  Force sync:
  main devient exactement
  identique à prod/v3.0.2-stable
end note
dev -> github: git push origin main
github --> dev: ✅ main mis à jour
deactivate main

== Finalisation ==
dev -> github: Supprimer ancienne preprod\n(optionnel)
note over github
  Sur GitHub, les utilisateurs voient:
  - main (= prod/v3.0.2-stable)
  - prod/v3.0.2-stable
  - preprod/v3.0.2-stable
  - Tag: v3.0.2

  Package téléchargeable:
  github.com/.../preprod/v3.0.2-stable/
  dist-offline/ambulon-3.0.2-offline-install.zip
end note

@enduml
```

---

## Diagramme de Décision - Gestion des Bugs

### Que faire quand un bug est détecté ?

```plantuml
@startuml
!theme plain

skinparam ActivityBackgroundColor #F0F0F0
skinparam ActivityBorderColor #2C3E50
skinparam ArrowColor #2C3E50
skinparam DiamondBackgroundColor #FFFACD
skinparam DiamondBorderColor #2C3E50

title Gestion des Bugs - Arbre de Décision

start

:Bug détecté;

if (Où est le bug ?) then (En développement\nsur feature branch)
  #FFE5B4:Corriger sur\nfeature branch;
  :cz commit (fix: ...);
  :Continuer développement;
  stop

elseif (En preprod) then (oui)
  #FFFACD:Corriger sur\npreprod/vX.X.X-stable;
  :cz commit (fix: ...);
  :cz bump\n(patch: X.X.X → X.X.X+1);
  :poetry build;
  :build_offline_package.py;
  :Re-tester;

  if (Tests OK ?) then (✅ oui)
    :Continuer vers prod;
  else (❌ non)
    :Retour correction;
    backward:Re-fix;
  endif
  stop

elseif (En prod) then (🔒 IMMUTABLE)
  #90EE90:**JAMAIS** corriger\ndirectement sur prod;

  :Créer nouvelle\npreprod/vX.X.X+1-stable;
  note right
    Créer depuis prod/vX.X.X-stable
    et appliquer le fix
  end note

  :Suivre workflow complet;
  :preprod → tests → prod → main;
  stop

else (Sur main)
  #87CEEB:**JAMAIS** corriger\ndirectement sur main;

  :Identifier version prod\ncorrespondante;
  :Créer preprod depuis prod;
  :Appliquer le fix;
  :Workflow complet;
  stop
endif

@enduml
```

---

## Structure des Commits Conventionnels

### Types de Commits et Impact Version

```plantuml
@startuml
!theme plain

skinparam rectangle {
  BackgroundColor<<Major>> #FF6B6B
  BackgroundColor<<Minor>> #4ECDC4
  BackgroundColor<<Patch>> #95E1D3
  BackgroundColor<<NoVersion>> #F0F0F0
  BorderColor #2C3E50
}

title Types de Commits Conventionnels et Versioning

package "Commits qui BUMP la version" {
  rectangle "feat: Nouvelle fonctionnalité" as feat <<Minor>> {
    note bottom
      Version: 3.0.1 → 3.1.0
      Exemple:
      feat(piag): Add RAG search timeout configuration
    end note
  }

  rectangle "fix: Correction de bug" as fix <<Patch>> {
    note bottom
      Version: 3.0.1 → 3.0.2
      Exemple:
      fix(offline): Install deps before ambulon
    end note
  }

  rectangle "feat!: BREAKING CHANGE" as breaking <<Major>> {
    note bottom
      Version: 3.0.1 → 4.0.0
      Exemple:
      feat!: Refactor PIAG API (BREAKING CHANGE)
    end note
  }
}

package "Commits qui NE BUMP PAS la version" {
  rectangle "docs: Documentation" as docs <<NoVersion>>
  rectangle "style: Formatage" as style <<NoVersion>>
  rectangle "refactor: Refactoring" as refactor <<NoVersion>>
  rectangle "test: Tests" as test <<NoVersion>>
  rectangle "chore: Maintenance" as chore <<NoVersion>>
  rectangle "perf: Performance" as perf <<NoVersion>>
}

note right of breaking
  Le "!" après le type
  ou "BREAKING CHANGE:"
  dans le footer indique
  un changement majeur
end note

note right of docs
  Ces commits sont
  inclus dans le CHANGELOG
  mais ne modifient pas
  le numéro de version
end note

@enduml
```

---

## Règles Strictes - Matrice Autorisé/Interdit

### Ce qu'on PEUT et NE PEUT PAS faire

```plantuml
@startuml
!theme plain

skinparam rectangle {
  BackgroundColor<<Allowed>> #90EE90
  BackgroundColor<<Forbidden>> #FF6B6B
  BorderColor #2C3E50
}

title Règles Git - Matrice Autorisé/Interdit

rectangle "✅ AUTORISÉ" <<Allowed>> {
  card "Sur feature/*" {
    - Commiter du code
    - cz commit
    - cz bump
    - poetry build
    - build_offline_package.py
    - Merge dans preprod
  }

  card "Sur preprod/*" {
    - Créer depuis feature
    - Tester et valider
    - Corriger des bugs
    - cz bump (si bug)
    - Rebuild packages
    - Créer prod depuis preprod
  }

  card "Sur prod/*" {
    - Créer depuis preprod validée
    - git tag -a vX.X.X
    - Conserver indéfiniment
    - Sync avec main
  }

  card "Sur main" {
    - git reset --hard prod/vX.X.X
    - git merge --ff-only prod/vX.X.X
    - Lecture seule pour visiteurs
  }
}

rectangle "❌ INTERDIT" <<Forbidden>> {
  card "Sur feature/*" {
    ⛔ Pusher des secrets/tokens
    ⛔ Skip tests avant preprod
    ⛔ Bumper sans commits conventionnels
  }

  card "Sur preprod/*" {
    ⛔ Créer prod sans validation
    ⛔ Pusher avec tests qui échouent
    ⛔ Sauter l'étape de build offline
  }

  card "Sur prod/*" {
    🔒 Commiter directement
    🔒 Modifier après création
    🔒 Supprimer la branche
    🔒 Force push
  }

  card "Sur main" {
    🚫 Développer directement
    🚫 Commiter du code
    🚫 Créer depuis feature
    🚫 MAJ avant création de prod
  }
}

note bottom of "✅ AUTORISÉ"
  Suivre ces règles garantit:
  - Traçabilité complète
  - Versions stables
  - Rollback possible
  - Historique propre
end note

note bottom of "❌ INTERDIT"
  Violer ces règles cause:
  - Confusion dans l'historique
  - Versions instables
  - Difficultés de rollback
  - Perte de traçabilité
end note

@enduml
```

---

## Timeline Exemple - Release 3.0.2

### Chronologie Réelle d'une Release

```plantuml
@startuml
!theme plain

skinparam timeline {
  BackgroundColor #F0F0F0
  BorderColor #2C3E50
}

title Timeline Release Ambulon v3.0.2

concise "Développeur" as dev
concise "feature/gitlab-piag-v1" as feature
concise "preprod/v3.0.2-stable" as preprod
concise "prod/v3.0.2-stable" as prod
concise "main" as main

@0
dev is "Démarre"
feature is "Créée"
preprod is "N/A"
prod is "N/A"
main is "v3.0.1"

@1
dev is "Code"
feature is "Commits"

@2
dev is "Tests"
feature is "Ready"

@3
dev is "Bump"
feature is "v3.0.2"

@4
dev is "Build"
feature is "Packages"

@5
dev is "Create\npreprod"
preprod is "Créée"
feature is "Mergée"

@6
dev is "Validation"
preprod is "Tests"

@7
dev is "Bug fix"
preprod is "Corrigée"

@8
dev is "Re-test"
preprod is "v3.0.2"

@9
dev is "Validation\nOK ✅"
preprod is "Validée"

@10
dev is "Create\nprod"
prod is "Créée\nv3.0.2"
preprod is "Stable"

@11
dev is "Sync\nmain"
main is "v3.0.2"

@12
dev is "Push\nGitHub"
prod is "Online"
main is "Online"

@13
dev is "Release\nterminée ✅"

highlight 0 to 5 #FFE5B4 : Développement (feature)
highlight 5 to 10 #FFFACD : Validation (preprod)
highlight 10 to 11 #90EE90 : Production (prod)
highlight 11 to 13 #87CEEB : Publication (main)

@enduml
```

---

## FAQ - Questions Fréquentes

### Q1: Pourquoi ne pas développer sur `main` ?

```plantuml
@startuml
!theme plain

title Pourquoi main est en lecture seule ?

package "❌ Développement sur main (Mauvais)" {
  rectangle "main" as main1 #FF6B6B
  note right of main1
    Problèmes:
    - Confusion dev/stable
    - Commits accidentels
    - Rollback difficile
    - Visiteurs GitHub voient
      du code non testé
  end note
}

package "✅ main = miroir prod (Bon)" {
  rectangle "prod/v3.0.2" as prod2 #90EE90
  rectangle "main" as main2 #87CEEB

  prod2 -down-> main2 : sync

  note right of main2
    Avantages:
    - Toujours stable
    - Historique propre
    - Rollback facile
    - Visiteurs voient
      la dernière version stable
  end note
}

@enduml
```

### Q2: Que faire si un bug est en production ?

```plantuml
@startuml
!theme plain

title Hotfix en Production

start

:Bug critique\ndétecté en prod;

:Identifier version\nprod/v3.0.2-stable;

:git checkout\nprod/v3.0.2-stable;

:git checkout -b\npreprod/v3.0.3-stable;

:Corriger le bug;

:cz commit (fix: ...);

:cz bump\n(3.0.2 → 3.0.3);

:poetry build;

:build_offline_package.py;

:Tests complets;

if (Tests OK ?) then (✅ oui)
  :git checkout -b\nprod/v3.0.3-stable;
  :git push --tags;
  :sync main;
  :✅ Hotfix déployé;
  stop
else (❌ non)
  :Continuer corrections;
  backward:Re-fix;
endif

note right
  JAMAIS corriger
  directement sur prod !

  Toujours passer par:
  preprod → validation
  → prod → main
end note

@enduml
```

---

## Résumé Visuel

### Workflow Complet en un Coup d'Œil

```plantuml
@startuml
!theme plain

skinparam ArrowColor #2C3E50
skinparam rectangle {
  BackgroundColor #F0F0F0
  BorderColor #2C3E50
}

title Workflow Git Ambulon - Vue d'Ensemble

rectangle "1. DÉVELOPPEMENT" #FFE5B4 {
  (feature/ma-fonctionnalite)
  note bottom
    - git checkout -b feature/...
    - Commits conventionnels
    - cz bump
    - poetry build
    - build_offline_package.py
  end note
}

rectangle "2. PRÉ-PRODUCTION" #FFFACD {
  (preprod/v3.0.2-stable)
  note bottom
    - Tests & validation
    - Corrections si nécessaire
    - Package offline généré
    - Validation finale ✅
  end note
}

rectangle "3. PRODUCTION" #90EE90 {
  (prod/v3.0.2-stable)
  note bottom
    - Branche immuable 🔒
    - Tag v3.0.2
    - Conservée indéfiniment
    - Source de vérité
  end note
}

rectangle "4. MAIN" #87CEEB {
  (main)
  note bottom
    - Miroir de prod
    - Branche par défaut GitHub
    - Lecture seule
    - Toujours stable
  end note
}

(feature/ma-fonctionnalite) -down-> (preprod/v3.0.2-stable) : créer\npreprod
(preprod/v3.0.2-stable) -down-> (prod/v3.0.2-stable) : validation\nOK
(prod/v3.0.2-stable) -down-> (main) : sync\nmain

note right of (feature/ma-fonctionnalite)
  Durée: quelques jours
  Supprimée après merge
end note

note right of (preprod/v3.0.2-stable)
  Durée: quelques heures/jours
  Conservée sur GitHub
end note

note right of (prod/v3.0.2-stable)
  Permanente
  Immuable
end note

note right of (main)
  Toujours à jour
  avec dernière prod
end note

@enduml
```

---

## Checklist Avant Release

### Points de Contrôle Obligatoires

```plantuml
@startuml
!theme plain

title Checklist Release - Points de Contrôle

skinparam activityBackgroundColor #F0F0F0
skinparam activityBorderColor #2C3E50
skinparam activityDiamondBackgroundColor #FFFACD

|Développement|
start
:Tous les commits\nsont conventionnels ?;
note right: cz commit obligatoire

:Tests unitaires\npassent ?;

:cz bump exécuté ?;
note right: Version bumpée correctement

:poetry build\nréussi ?;

:build_offline_package.py\nréussi ?;
note right: Package de 80MB généré

|Preprod|
:Branche preprod créée ?;

:Installation offline\ntestée ?;
note right
  Test critique:
  Installation sans Internet
  dans environnement vierge
end note

:Toutes les fonctionnalités\ntestées ?;

:Documentation\nà jour ?;

if (Bugs détectés ?) then (oui)
  :Corriger sur preprod;
  :cz bump (patch);
  :Rebuild;
  backward:Re-tester;
else (non)
  :Validation preprod ✅;
endif

|Production|
:Branche prod créée\ndepuis preprod ?;

:Tag vX.X.X créé ?;

:Branche prod\npushée sur GitHub ?;

|Main|
:main synchronisé\navec prod ?;

:Vérification\nGitHub ?;
note right
  - Tag visible
  - Package téléchargeable
  - README à jour
end note

stop

@enduml
```

---

## Génération des Diagrammes

Pour générer les images PNG/SVG des diagrammes PlantUML :

```bash
# Installer PlantUML
sudo apt-get install plantuml  # Linux
brew install plantuml          # macOS

# Générer tous les diagrammes
plantuml doc/git-workflow.md

# Ou utiliser le service en ligne
# https://www.plantuml.com/plantuml/uml/
```

---

**Auteur**: Hervé Marchal <herve.marchal@hotmail.fr>
**Version**: 3.0.2
**Date**: 2026-01-31
**Licence**: MIT
