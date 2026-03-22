# Prompt pour la génération d'un Cahier des Spécifications Techniques (CST)

Tu es un expert en ingénierie logicielle et architecte technique. À partir des principes des standards **ISO/IEC 25010** (Modèle de qualité des produits logiciels), **ISO/IEC/IEEE 29119** (Documentation des tests), et **ISO/IEC/IEEE 42010** (Description d'architecture), tu dois produire un **Cahier des Spécifications Techniques (CST)** complet, précis et adaptable à tout projet de développement logiciel.

Le document doit être autoporté, prêt à être rendu dans VS Code ou Obsidian (avec support PlantUML activé), sans dépendances externes, et sans aucune hypothèse ni donnée externe.

## Consignes générales

- Utilise exclusivement le format **Markdown**.
- Ne fais référence à aucun fichier externe, sauf si explicitement fourni dans l'instruction.
- Toutes les sections doivent être **autoportées** : explicites, compréhensibles sans contexte additionnel.
- Le contenu doit définir **COMMENT** le système sera réalisé (pas CE QU'IL FAIT — c'est le rôle du CCF).
- Cible un public technique : développeurs, architectes, intégrateurs, DevOps.
- Intègre les **8 caractéristiques de qualité ISO 25010** : aptitude fonctionnelle, performance, compatibilité, utilisabilité, fiabilité, sécurité, maintenabilité, portabilité.

## Structure obligatoire du CST

1. **Introduction et objectifs techniques**
   - Vue d'ensemble technique du système.
   - Objectifs de qualité prioritaires (selon ISO 25010).
   - Conformité réglementaire (RGS, RGPD, référentiels État si secteur public).

2. **Architecture logicielle**
   - **Diagramme de Composants UML** (ISO/IEC 19505) en PlantUML.
   - Description de l'architecture modulaire et des dépendances.
   - Patterns architecturaux utilisés (MVC, microservices, hexagonale, etc.).
   - Justification des choix architecturaux majeurs.

3. **Stack technique détaillée**
   - Langages de programmation et versions.
   - Frameworks et bibliothèques principaux.
   - Bases de données et systèmes de stockage.
   - Serveurs d'application et conteneurs.
   - Outils de développement et environnements.

4. **Modélisation statique**
   - **Diagramme de Classes UML** (ISO/IEC 19505-2) en PlantUML.
   - Structure des données et objets techniques.
   - Relations d'héritage, composition, agrégation.
   - Modèle physique de données (MPD) si applicable.

5. **Modélisation dynamique**
   - **Diagrammes de Séquence UML** pour les flux critiques.
   - **Diagrammes d'États-Transitions** pour les cycles de vie d'objets.
   - **Diagrammes d'Activités UML** pour les processus techniques.
   - Description des interactions temporelles entre composants.

6. **Interfaces et intégrations**
   - **Schémas d'API** (OpenAPI/Swagger) ou description des contrats d'interface.
   - Protocoles de communication (REST, GraphQL, SOAP, gRPC, etc.).
   - Intégrations externes : SSO, LDAP, services tiers.
   - Formats d'échange de données (JSON, XML, etc.).

7. **Architecture de déploiement**
   - **Diagramme de Déploiement UML** (ISO/IEC 19505) en PlantUML.
   - Description des environnements (développement, recette, production).
   - Configuration réseau et topologie.
   - Haute disponibilité et stratégies de failover.

8. **Sécurité technique**
   - Authentification et autorisation (OAuth2, OIDC, SAML, etc.).
   - Chiffrement des données (en transit et au repos).
   - Gestion des secrets et credentials.
   - Protection contre les vulnérabilités courantes (OWASP Top 10).

9. **Qualité et tests** (selon ISO/IEC/IEEE 29119)
   - Stratégie de test (unitaire, intégration, E2E, performance).
   - Couverture de code cible.
   - Outils de test et d'analyse statique.
   - Critères d'acceptation techniques.

10. **Performance et scalabilité**
    - Objectifs de performance (temps de réponse, throughput).
    - Stratégies de cache et d'optimisation.
    - Scalabilité horizontale/verticale.
    - Gestion de la charge et limites du système.

11. **Maintenabilité et exploitation**
    - Standards de code et conventions de nommage.
    - Documentation du code et patterns de commentaires.
    - Journalisation (logging) et monitoring.
    - Procédures de déploiement et rollback.

12. **Gestion des erreurs et résilience**
    - Stratégies de gestion des erreurs.
    - Circuit breakers, retries, timeouts.
    - Plan de reprise d'activité (PRA) et continuité.

13. **Contraintes et dépendances**
    - Contraintes techniques (legacy, intégrations imposées).
    - Dépendances externes et leurs versions.
    - Licences et aspects juridiques des composants.

14. **Annexes techniques**
    - Glossaire technique.
    - Références des frameworks et bibliothèques.
    - Architecture Decision Records (ADR) pertinents.

## Règles de forme

- Utilise systématiquement des **liens internes** pour la navigation (ex. : « ↩ Retour au sommaire »).
- Insère un **[TOC]** en haut du document.
- Tous les diagrammes UML doivent utiliser la syntaxe **PlantUML** valide.
- Privilégie les **tableaux** pour les spécifications détaillées.
- Le document doit être **compatible** avec les extensions VS Code / Obsidian.
- Aucun lien brisé, aucun fichier externe requis.
- Le style doit être **technique, précis, orienté développement**.

## Sortie attendue

- Un seul fichier `.md`.
- Aucune mention de fichiers sources ou de prompts.
- Prêt à être utilisé tel quel par les équipes de développement.

---

**Références normatives appliquées :**
- **ISO/IEC 25010:2023** : Modèle de qualité des produits logiciels.
- **ISO/IEC/IEEE 29119** (série) : Documentation et processus de test logiciel.
- **ISO/IEC/IEEE 42010:2022** : Description d'architecture des systèmes logiciels.
- **ISO/IEC 19505** : Unified Modeling Language (UML) 2.x.
- **CCTP** : Cadre réglementaire pour les marchés publics français (si applicable).
- **RGS / SSI / RGPD** : Référentiels de sécurité et protection des données.
