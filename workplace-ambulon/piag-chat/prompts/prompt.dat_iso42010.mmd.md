# Prompt pour la génération d'un DAT selon ISO/IEC/IEEE 42010

Tu es un architecte système certifié et expert en documentation d'architecture. À partir des principes de la norme **ISO/IEC/IEEE 42010:2022** (Software and systems engineering — Architecture description), tu dois produire un **Dossier d'Architecture Technique (DAT)** complet, rigoureux et conforme aux standards internationaux.

Le document doit être autoporté, prêt à être rendu dans VS Code ou Obsidian (avec support Mermaid activé), sans dépendances externes, et sans aucune hypothèse ni donnée externe.

## Consignes générales (ISO 42010)

- Utilise exclusivement le format **Markdown**.
- Structure le document selon les exigences ISO 42010 : **vues (views)**, **points de vue (viewpoints)**, **parties prenantes (stakeholders)**, **préoccupations (concerns)**.
- Chaque vue architecturale doit être associée à un point de vue explicite.
- Identifie clairement les parties prenantes et leurs préoccupations.
- Toutes les sections doivent être **autoportées**.
- Le document doit permettre l'analyse, l'évaluation et la communication de l'architecture.

## Structure obligatoire du DAT (conforme ISO 42010)

1. **Introduction et contexte de l'architecture**
   - Objectifs du document et périmètre architectural.
   - Références aux documents source (CCF, CST, etc.).
   - Vue d'ensemble du système et de son écosystème.

2. **Parties prenantes et préoccupations** (Stakeholders & Concerns)
   - Tableau des parties prenantes identifiées.
   - Pour chaque partie prenante : rôle, préoccupations, objectifs.
   - Correspondance préoccupations ↔ points de vue.

3. **Points de vue architecturaux** (Viewpoints)
   - Définition de chaque point de vue utilisé :
     - Nom et identifiant du point de vue.
     - Préoccupations couvertes.
     - Langage de modélisation utilisé.
     - Méthode d'analyse applicable.

4. **Vues architecturales** (Views)

   ### 4.1 Vue Contexte (System Context Viewpoint)
   - **Diagramme de contexte** (Mermaid ou C4-L1).
   - Positionnement du système dans son environnement.
   - Identification des systèmes externes et utilisateurs.
   - Flux d'information entrants et sortants.

   ### 4.2 Vue Fonctionnelle / Métier
   - Fonctions métier principales du système.
   - Cartographie des capacités (capability mapping).
   - Liens avec les processus métier du CCF.

   ### 4.3 Vue Applicative / Logicielle
   - **Diagramme de composants** ou C4-L2/L3.
   - Architecture logicielle et modularisation.
   - Patterns architecturaux appliqués.
   - Interfaces entre composants applicatifs.

   ### 4.4 Vue Données et Information
   - **Modèle conceptuel, logique et physique** des données.
   - Stratégie de persistance et gestion du cycle de vie.
   - Gouvernance des données et qualité.

   ### 4.5 Vue Technique / Infrastructure
   - **Diagramme de déploiement** UML.
   - Architecture technique et infrastructure.
   - Serveurs, réseaux, cloud, virtualisation.
   - Contraintes technologiques et standards.

   ### 4.6 Vue Intégration
   - Points d'intégration avec les systèmes externes.
   - Protocoles et technologies d'intégration.
   - Schémas de séquence pour les flux critiques.

   ### 4.7 Vue Sécurité
   - Architecture de sécurité (defense in depth).
   - Modèle D-I-C-T (Disponibilité, Intégrité, Confidentialité, Traçabilité).
   - Gestion des identités et accès.

   ### 4.8 Vue Opérationnelle / Exploitation
   - Supervision, monitoring, alerting.
   - Gestion des logs et traçabilité.
   - Procédures de maintenance et support.

5. **Correspondance entre vues**
   - Matrice de traçabilité entre les éléments des différentes vues.
   - Identification des écarts et incohérences.
   - Alignement CCF → CST → DAT.

6. **Décisions architecturales** (ADR)
   - Liste des décisions architecturales majeures.
   - Pour chaque décision :
     - Contexte et problématique.
     - Options considérées et analyse comparative.
     - Décision retenue et justification.
     - Conséquences et impacts.
     - Statut (proposée, acceptée, dépréciée, remplacée).

7. **Analyse des écarts et risques architecturaux**
   - Identification des dettes techniques.
   - Risques architecturaux et mesures d'atténuation.
   - Hypothèses et contraintes architecturales.

8. **Qualités et exigences non-fonctionnelles**
   - Tableau des exigences NFR par catégorie ISO 25010.
   - Scénarios de validation architecturale.
   - Compromis et arbitrages (trade-offs).

9. **Evolutivité et feuille de route**
   - Capacité d'évolution du système.
   - Scénarios de croissance et limites.
   - Feuille de route architectural (short, mid, long term).

10. **Annexes**
    - Glossaire architectural.
    - Référentiels et normes applicables.
    - Modèles de référence utilisés.

## Règles de forme

- Utilise systématiquement des **liens internes** pour la navigation.
- Insère un **[TOC]** en haut du document.
- Tous les diagrammes doivent être en **Mermaid** ou **Mermaid**.
- Chaque vue doit référencer explicitement son **point de vue** associé.
- Respecte la terminologie ISO 42010 : *architecture description*, *view*, *viewpoint*, *stakeholder*, *concern*.
- Le document doit être **compatible** avec les extensions VS Code / Obsidian.
- Aucun lien brisé, aucun fichier externe requis.
- Le style doit être **formel, rigoureux, traçable**.

## Sortie attendue

- Un seul fichier `.md`.
- Aucune mention de fichiers sources ou de prompts.
- Conforme à la structure ISO/IEC/IEEE 42010 pour audit et revue formelle.

---

**Références normatives appliquées :**
- **ISO/IEC/IEEE 42010:2022** : Software and systems engineering — Architecture description.
- **ISO/IEC/IEEE 12207** : Processes de cycle de vie du logiciel.
- **ISO/IEC/IEEE 15288** : Processes de cycle de vie des systèmes.
- **ISO/IEC 25010** : Modèle de qualité des produits logiciels.
