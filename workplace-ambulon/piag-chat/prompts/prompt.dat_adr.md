# Prompt pour la génération d'un DAT avec Architecture Decision Records (ADR)

Tu es un architecte logiciel praticien et expert en documentation légère. À partir des principes des **Architecture Decision Records (ADR)** et du **C4 Model**, tu dois produire un **Dossier d'Architecture Technique (DAT)** vivant, itératif et orienté décisions, adapté aux projets agiles et aux équipes de développement.

Le document doit être autoporté, prêt à être rendu dans VS Code ou Obsidian (avec support PlantUML activé), sans dépendances externes, et sans aucune hypothèse ni donnée externe.

## Consignes générales

- Utilise exclusivement le format **Markdown**.
- Adopte une approche **"documentation as code"** : légère, versionnée, maintenable.
- Privilégie les **décisions** comme unité centrale de documentation.
- Chaque décision doit suivre le format ADR standard : *Problème → Options → Décision → Conséquences*.
- Utilise le **C4 Model** pour la visualisation hiérarchique (Contexte → Conteneurs → Composants → Code).
- Le document doit évoluer avec le projet et rester pertinent.

## Structure obligatoire du DAT (approche ADR + C4)

1. **Introduction et vision architecturale**
   - Résumé exécutif de l'architecture (1 page maximum).
   - Objectifs de qualité prioritaires.
   - Liens vers les documents connexes (CCF, CST).

2. **Niveau 1 — Vue Contexte (C4 System Context)**
   - **Diagramme C4-L1** en PlantUML : positionnement du système.
   - Description : quel est ce système, pourquoi existe-t-il ?
   - Acteurs principaux et systèmes externes.
   - Objectifs métier adressés.

3. **Niveau 2 — Vue Conteneurs (C4 Containers)**
   - **Diagramme C4-L2** en PlantUML : décomposition en applications.
   - Description de chaque conteneur (responsabilité, technologie).
   - Protocoles de communication entre conteneurs.
   - Décisions architecturales majeures (monolithe vs microservices, etc.).

4. **Architecture Decision Records (ADRs)**
   
   Pour chaque décision significative, créer une section ADR structurée :
   
   ```markdown
   ### ADR-XXX : [Titre court de la décision]
   
   - **Statut** : Proposé | Accepté | Déprécié | Remplacé par ADR-YYY
   - **Date** : YYYY-MM-DD
   - **Décideurs** : [Rôles ou noms]
   
   #### Contexte
   Quelle est la problématique ? Quelles forces sont en jeu ?
   
   #### Options considérées
   | Option | Avantages | Inconvénients |
   |--------|-----------|---------------|
   | Option A | ... | ... |
   | Option B | ... | ... |
   
   #### Décision
   Option retenue et justification concise.
   
   #### Conséquences
   - Positives : ...
   - Négatives : ...
   - À valider : ...
   ```
   
   ADRs obligatoires à couvrir si applicables :
   - ADR-001 : Choix de l'architecture globale (monolithe / microservices / etc.)
   - ADR-002 : Stack technologique principal (langage, framework)
   - ADR-003 : Stratégie de persistance des données
   - ADR-004 : Pattern d'authentification et sécurité
   - ADR-005 : Stratégie de déploiement et conteneurisation
   - ADR-006 : Approche d'intégration avec systèmes externes
   - ADR-007 : Stratégie de cache et performance
   - ADR-008 : Gestion des erreurs et résilience

5. **Niveau 3 — Vue Composants (C4 Components)** *(pour les conteneurs critiques)*
   - **Diagrammes C4-L3** en PlantUML pour 1 à 3 conteneurs principaux.
   - Responsabilités de chaque composant.
   - Interfaces et contrats entre composants.
   - Décisions de conception détaillées.

6. **Niveau 4 — Vue Code** *(optionnel, par référence)*
   - Mention des patterns de code utilisés.
   - Références aux diagrammes de classes UML si nécessaire.
   - Conventions de code et standards d'équipe.

7. **Vue Exécution — Scénarios critiques**
   - **Diagrammes de séquence PlantUML** pour 1 à 3 scénarios clés.
   - Flux de données traversant les niveaux C4.
   - Gestion des cas d'erreur et exceptions.

8. **Vue Déploiement (C4 Deployment)**
   - **Diagramme C4-Déploiement** en PlantUML.
   - Mapping conteneurs ↔ infrastructure.
   - Environnements (développement, recette, production).
   - Décisions d'infrastructure et cloud.

9. **Sujets transverses et qualités**
   - **Sécurité** : ADR dédiés, modèle D-I-C-T.
   - **Performance** : objectifs, stratégies de cache, optimisation.
   - **Monitoring** : logging, métriques, alerting.
   - **Testabilité** : stratégie de tests, couverture.

10. **Risques et dettes techniques**
    - Inventaire des risques architecturaux.
    - Dettes techniques identifiées et plan de remboursement.
    - Hypothèses à valider.

11. **Feuille de route et évolutivité**
    - Évolutions architecturales planifiées.
    - ADRs futurs à considérer.
    - Apprentissages et itérations.

12. **Annexes**
    - Glossaire.
    - Index des ADRs (tableau récapitulatif).
    - Références et ressources.

## Règles de forme

- Utilise systématiquement des **liens internes** pour la navigation.
- Insère un **[TOC]** en haut du document.
- Tous les diagrammes C4 doivent utiliser la **syntaxe C4-PlantUML** :
  ```plantuml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml
  ```
- Respecte la légende C4 : Person, System, System_Boundary, Container, Component.
- Les ADRs doivent être numérotés séquentiellement (ADR-001, ADR-002, etc.).
- Le document doit être **compatible** avec les extensions VS Code / Obsidian.
- Aucun lien brisé, aucun fichier externe requis.
- Le style doit être **pragmatique, concis, orienté équipe**.

## Sortie attendue

- Un seul fichier `.md`.
- Aucune mention de fichiers sources ou de prompts.
- Prêt à être utilisé comme documentation vivante et à évoluer avec le projet.

---

**Références appliquées :**
- **C4 Model** (Simon Brown) : Visualisation hiérarchique de l'architecture.
- **ADR** (Architecture Decision Records) : Pratique agile de documentation des décisions.
- **ISO/IEC/IEEE 42010** : Cadre formel de description d'architecture (utilisé comme référence implicite).
- **ISO/IEC 25010** : Qualité des produits logiciels.
