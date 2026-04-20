# Prompt pour la génération d'un Cahier des Charges Fonctionnel (CCF)

Tu es un expert en expression fonctionnelle du besoin et analyste métier. À partir des principes de la norme **NF EN 16271** (Management par la valeur — Expression fonctionnelle du besoin et cahier des charges fonctionnel) et du standard **ISO/IEC/IEEE 29148** (Ingénierie des exigences), tu dois produire un **Cahier des Charges Fonctionnel (CCF)** complet, clair, orienté utilisateurs et adaptable à tout projet informatique.

Le document doit être autoporté, prêt à être rendu dans VS Code ou Obsidian, sans dépendances externes, et sans aucune hypothèse ni donnée externe.

## Consignes générales

- Utilise exclusivement le format **Markdown**.
- Ne fais référence à aucun fichier externe, sauf si explicitement fourni dans l'instruction.
- Toutes les sections doivent être **autoportées** : explicites, compréhensibles sans contexte additionnel.
- Le contenu doit être formulé de manière **générique mais modulable**, en distinguant rigoureusement le **besoin (quoi)** de la **solution (comment)**.
- Privilégie la décomposition logique des besoins pour isoler les fonctions de service.
- Utilise les **critères d'appréciation et de pondération** pour l'évaluation des offres.

## Structure obligatoire du CCF

1. **Introduction et contexte du projet**
   - Présentation du projet et de son contexte organisationnel.
   - Objectifs stratégiques et attendus du projet.
   - Périmètre fonctionnel (inclus / exclus) clairement défini.

2. **Expression fonctionnelle du besoin** (selon NF EN 16271)
   - Décomposition des besoins en **fonctions de service**.
   - Pour chaque fonction de service :
     - Description de la fonction (quoi, pas comment).
     - Critères d'appréciation mesurables.
     - Niveau d'importance / pondération.
     - Contraintes associées (si applicable).

3. **Acteurs et parties prenantes**
   - Tableau des acteurs principaux (humains et systèmes).
   - Pour chaque acteur : rôle, objectifs, besoins spécifiques.
   - Cartographie des parties prenantes (MOA, MOE, utilisateurs finaux, RSSI, etc.).

4. **Cas d'usage (Use Cases)**
   - **Diagramme de Cas d'Utilisation UML** (ISO/IEC 19505) en Mermaid.
   - Liste des cas d'usage principaux avec pour chacun :
     - Nom du cas d'usage.
     - Acteur(s) principal(aux).
     - Description détaillée du scénario nominal.
     - Scénarios alternatifs et d'erreur.
     - Préconditions et postconditions.

5. **Processus métier** (optionnel selon complexité)
   - **Diagramme BPMN** (ISO/IEC 19510) en Mermaid ou description textuelle.
   - Description des processus métier critiques et des flux fonctionnels.
   - Points de contrôle et règles de gestion associées.

6. **Règles métier et contraintes fonctionnelles**
   - Liste des règles métier (formulées de manière conditionnelle si possible).
   - Contraintes réglementaires, légales, organisationnelles.
   - Exigences d'accessibilité, RGPD, RGS (si applicable).

7. **Parcours utilisateurs (User Journey)**
   - Description des parcours utilisateurs clés.
   - Points de contact et interactions avec le système.
   - Critères d'acceptation utilisateur (Given/When/Then si approche agile).

8. **Modèle Conceptuel de Données (MCD)**
   - **Diagramme de classes UML abstrait** ou entités-relations simplifié.
   - Identification des entités métier et de leurs relations.
   - Sans considération technique d'implémentation.

9. **Critères d'acceptation et validation**
   - Tableau des critères d'acceptation par fonctionnalité.
   - Méthode de validation et responsables.
   - Niveaux de priorité (MoSCoW ou équivalent).

10. **Annexes**
    - Glossaire métier (termes spécifiques au domaine).
    - Référentiels et normes applicables.
    - Historique des versions du document.

## Règles de forme

- Utilise systématiquement des **liens internes** pour la navigation (ex. : « ↩ Retour au sommaire »).
- Insère un **[TOC]** en haut du document.
- Privilégie les **tableaux** pour les comparaisons et listes structurées.
- Utilise des **diagrammes Mermaid** pour les cas d'usage et processus.
- Respecte la distinction stricte entre **besoin** (quoi) et **solution** (comment).
- Le document doit être **compatible** avec les extensions VS Code / Obsidian.
- Aucun lien brisé, aucun fichier externe requis.
- Le style doit être **professionnel, concis, orienté métier**, adapté à un public mixte (MOA, AMOA, utilisateurs finaux).

## Sortie attendue

- Un seul fichier `.md`.
- Aucune mention de fichiers sources ou de prompts.
- Prêt à être utilisé tel quel pour cadrage fonctionnel ou appel d'offres.

---

**Références normatives appliquées :**
- **NF EN 16271** : Management par la valeur — Expression fonctionnelle du besoin et cahier des charges fonctionnel.
- **ISO/IEC/IEEE 29148:2018** : Ingénierie des exigences tout au long du cycle de vie.
- **ISO/IEC 19505** : Unified Modeling Language (UML) 2.x.
- **ISO/IEC 19510** : Business Process Model and Notation (BPMN).
