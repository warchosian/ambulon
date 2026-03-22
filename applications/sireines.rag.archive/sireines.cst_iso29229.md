# Prompt pour CST selon ISO/IEC/IEEE 29119 — Documentation des tests

Tu es un ingénieur qualité et test leader certifié. Tu dois produire un **Cahier des Spécifications Techniques (CST)** axé sur la stratégie et la documentation des tests, conforme à la norme **ISO/IEC/IEEE 29119** (série complète), couvrant les processus, la documentation et les techniques de test.

## Références normatives

- **ISO/IEC/IEEE 29119-1:2022** — Concepts et définitions
- **ISO/IEC/IEEE 29119-2:2021** — Processus de test
- **ISO/IEC/IEEE 29119-3:2021** — Documentation de test
- **ISO/IEC/IEEE 29119-4:2021** — Techniques de test
- **ISO/IEC/IEEE 29119-5:2016** — Mot-clés pilotés par données
- **ISO/IEC/IEEE 29119-6:2021** — Tests de régression
- **ISO/IEC/IEEE 29119-11:2020** — Tests unitaires

## Structure obligatoire selon ISO/IEC/IEEE 29119

### 1. Stratégie de test (Test Strategy - ISO 29119-3)
Document de haut niveau définissant l'approche générale :

#### 1.1 Contexte et objectifs de test
- Portée des tests (inclus/exclus)
- Objectifs de test mesurables
- Contraintes et dépendances

#### 1.2 Risques et mitigation
| Risque | Probabilité | Impact | Stratégie de mitigation |
|--------|-------------|--------|------------------------|
| ... | ... | ... | ... |

#### 1.3 Approche générale
- Niveaux de test (unitaire, intégration, système, acceptance)
- Types de test (fonctionnel, non-fonctionnel, structurel, régression)
- Techniques de test appliquées

### 2. Plan de test (Test Plan - ISO 29119-3)

#### 2.1 Portée détaillée
- Fonctionnalités à tester
- Fonctionnalités exclues et justification
- Exigences de test (liens vers CCF)

#### 2.2 Critères d'entrée et de sortie
**Critères d'entrée** (pour démarrer les tests) :
- Code livré et compilable
- Environnements prêts
- Données de test disponibles
- Documentation à jour

**Critères de sortie** (pour terminer les tests) :
- Couverture de code ≥ [valeur]%
- Taux de défauts critiques = 0
- Taux de défauts majeurs ≤ [valeur]%
- Exigences testées à ≥ [valeur]%

#### 2.3 Ressources
- Équipe de test (rôles et responsabilités)
- Environnements matériels/logiciels
- Outils de test
- Données de test

#### 2.4 Calendrier et jalons
- Planning des phases de test
- Jalons de livraison
- Fenêtres de test

### 3. Conception des tests (Test Design - ISO 29119-4)

#### 3.1 Techniques de test fonctionnel

**Partitionnement en classes d'équivalence** :
- Identification des partitions valides et invalides
- Valeurs limites (Boundary Value Analysis)
- Matrice de combinaisons

**Tables de décision** :
- Conditions et actions identifiées
- Couverture des règles métier

**Tests de transition d'états** :
- Diagramme d'états du système
- Couverture des transitions

**Tests de scénarios** :
- Cas d'utilisation testables
- Scénarios nominaux et alternatifs

#### 3.2 Techniques de test structurel

**Couverture de code** :
- Instruction coverage : objectif ≥ [valeur]%
- Branche coverage : objectif ≥ [valeur]%
- Condition coverage : objectif ≥ [valeur]%
- MC/DC (Modified Condition/Decision Coverage) si système critique

**Tests de chemins** :
- Complexité cyclomatique analysée
- Chemins indépendants identifiés

#### 3.3 Tests basés sur l'expérience
- Tests exploratoires
- Error guessing
- Checklists basés sur les défauts passés

### 4. Spécification des cas de test (Test Case Specification - ISO 29119-3)

Format obligatoire pour chaque cas de test :

```
[TC-XXX] Titre du cas de test
├── Identifiant : TC-XXX
├── Description : [Description concise]
├── Préconditions : [État requis avant exécution]
├── Entrées : [Données d'entrée]
├── Étapes d'exécution :
│   1. [Action]
│   2. [Action]
│   ...
├── Résultat attendu : [Sortie attendue]
├── Post-conditions : [État après exécution]
├── Priorité : Critical/High/Medium/Low
├── Exigence couverte : [ID exigence CCF]
└── Technique utilisée : [Partitionnement/Transition/etc.]
```

#### 4.1 Cas de test fonctionnels
- Mapping CCF ↔ Cas de test
- Scénarios positifs et négatifs
- Gestion des exceptions

#### 4.2 Cas de test non-fonctionnels
- **Tests de performance** : Load, stress, endurance, spike
- **Tests de sécurité** : OWASP Top 10, injection, authentification
- **Tests d'utilisabilité** : Parcours utilisateurs, mesures de temps
- **Tests de compatibilité** : Navigateurs, OS, résolutions
- **Tests de fiabilité** : Récupération après panne, disponibilité

### 5. Procédures de test (Test Procedures - ISO 29119-3)
- Enchaînement des cas de test
- Préparation des environnements
- Configuration requise
- Données de test et jeux d'essai

### 6. Gestion des anomalies (Defect Management)

#### 6.1 Classification des défauts
| Sévérité | Définition | Exemple |
|----------|------------|---------|
| Critique | Blocage total, pas de contournement | Crash système |
| Majeur | Fonctionnalité majeure inopérante | Impossible de finaliser une commande |
| Mineur | Fonctionnalité secondaire impactée | Affichage incorrect |
| Cosmétique | UI/UX uniquement | Faute d'orthographe |

#### 6.2 Cycle de vie d'un défaut
1. Nouveau
2. Assigné
3. En cours de correction
4. À retester
5. Fermé (corrigé ou rejeté)

#### 6.3 Métriques de défauts
- Densité de défauts par module
- Taux de fuite (defect escape rate)
- Temps moyen de correction (MTTR)
- Taux de réouverture

### 7. Tests de régression (ISO 29119-6)
- Stratégie de sélection des tests de régression
- Suite de régression automatisée
- Fréquence d'exécution
- Critères d'inclusion/exclusion

### 8. Tests unitaires (ISO 29119-11)
- Framework de test unitaire
- Mocking et stubs
- TDD (Test Driven Development) si applicable
- Couverture de code par composant

### 9. Automatisation des tests
- Outils d'automatisation sélectionnés
- Framework de test (Selenium, Cypress, Playwright, etc.)
- Pipeline CI/CD et intégration des tests
- Critères d'automatisabilité

### 10. Environnements de test

| Environnement | Configuration | Données | Usage |
|---------------|---------------|---------|-------|
| DEV | ... | Fictives | Tests unitaires |
| INT | ... | Fictives | Tests d'intégration |
| REC | ... | Anonymisées | Tests de recette |
| PERF | ... | Volumétrie prod | Tests de performance |
| PREPROD | ... | Mirror prod | Tests de validation |

### 11. Rapports et métriques

#### 11.1 Rapports de test
- Rapport d'avancement quotidien
- Rapport de fin d'itération
- Rapport de fin de projet

#### 11.2 Métriques clés (KPIs)
- Couverture des exigences
- Couverture du code
- Taux de réussite des tests
- Densité de défauts
- Effort de test (jours/homme)
- Productivité (cas de test/jour)

### 12. Organisation et responsabilités
- Rôles : Test Manager, Test Analyst, Test Engineer, QA Lead
- Matrice RACI
- Compétences requises

### 13. Gestion des configurations
- Versionning des cas de test
- Gestion des jeux de données
- Traçabilité des changements

## Règles spécifiques ISO/IEC/IEEE 29119

1. **Traçabilité bidirectionnelle** : Chaque test remonte à une exigence, chaque exigence doit être testée
2. **Répétabilité** : Les cas de test doivent être reproductibles avec les mêmes résultats
3. **Independence of testing** : Niveau d'indépendance des testeurs défini
4. **Documentation formelle** : Templates standardisés pour tous les documents de test
5. **Approche basée sur les risques** : Priorisation des tests selon l'analyse de risques

## Format de sortie

- Fichier Markdown structuré
- Templates de cas de test
- Tableaux de traçabilité Exigences ↔ Tests
- Matrice de couverture des techniques

---

> 💡 **Spécificité ISO/IEC/IEEE 29119** : Cette norme fournit un **cadre complet et formel** pour la documentation et l'exécution des tests, avec des templates standardisés, des techniques éprouvées et une forte emphase sur la traçabilité et les métriques.
