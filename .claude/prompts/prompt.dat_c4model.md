Voici le prompt adapté au **modèle C4** (Simon Brown), en conservant votre structure Markdown allégée et en alignant les sections sur les niveaux C4 (Contexte, Conteneurs, Composants, Code) :

---

# Prompt générique pour la génération d'un Dossier d'Architecture Technique (DAT) — Modèle C4

Tu es un expert en architecture logicielle. À partir des principes du **modèle C4** (Simon Brown), tu dois produire un **Dossier d'Architecture Technique (DAT)** complet, clair, orienté utilisateurs et adaptable à toute application logicielle.

Le document doit être autoporté, prêt à être rendu dans VS Code ou Obsidian (avec support PlantUML activé), sans dépendances externes, et sans aucune hypothèse ni donnée externe.

## Consignes générales

- Utilise exclusivement le format **Markdown**.
- Ne fais référence à aucun fichier externe, sauf si explicitement fourni dans l'instruction.
- Toutes les sections doivent être **autoportées** : explicites, compréhensibles sans contexte additionnel.
- La section **Vue Déploiement** est **standardisée** : reproduis-la telle quelle, sauf le tableau « Environnements » qui peut être personnalisé.
- Le reste du contenu doit être formulé de manière **générique mais modulable**, en s'appuyant sur les données structurées fournies par un fichier `applicationsIA_mini_[nom].md` (si fourni).
- Ce fichier contient toujours les mêmes champs : nom de l'application, domaine métier, stack technique, parties prenantes, environnements cibles, contraintes spécifiques, etc.
- **Tous les diagrammes architecturaux doivent suivre la notation C4** (personnes, systèmes logiciels, conteneurs, composants) avec la syntaxe PlantUML C4.

## Structure obligatoire du DAT

1. **Introduction et objectifs**
   - Donne une vue d'ensemble fonctionnelle courte.
   - Liste 3 à 5 objectifs de qualité orientés utilisateur (ex. : performance, sécurité, maintenabilité).

2. **Niveau 1 — Vue Contexte (System Context)**
   - **Diagramme C4-L1** en PlantUML : montre le système à architecturer au centre, les utilisateurs humains et les systèmes externes autour.
   - Liste les **acteurs principaux** (utilisateurs humains) avec leurs objectifs.
   - Liste les **systèmes externes** (systèmes logiciels existants avec lesquels on interagit).

3. **Parties prenantes**
   - Énumère les rôles pertinents.
   - Pour chaque rôle, indique son attente principale (pas de contact fictif si non fourni).

4. **Contraintes**
   - Liste les contraintes techniques, organisationnelles et réglementaires.
   - Précise les exigences de sécurité selon le modèle D-I-C-T (Disponibilité, Intégrité, Confidentialité, Traçabilité).

5. **Niveau 2 — Vue Conteneurs (Containers)**
   - **Diagramme C4-L2** en PlantUML : décompose le système en applications/conteneurs (applications web, mobiles, bases de données, fichiers, etc.).
   - Décris brièvement chaque conteneur (responsabilité, technologie, interactions clés).
   - Mentionne les décisions architecturales majeures (ex. : monolithe vs microservices, pattern choisi).
   - Détaille l'environnement technologique (langage, framework, base de données, frontend, infra).
   - Indique les outils de la forge logicielle (CI/CD, tests, dépôt).

6. **Niveau 3 — Vue Composants (Components)** *(optionnel selon complexité)*
   - **Diagramme C4-L3** en PlantUML pour 1 à 3 conteneurs principaux : décompose un conteneur en composants (contrôleurs, services, repositories, etc.).
   - Explique la logique interne et les responsabilités de chaque composant.

7. **Niveau 4 — Vue Code (Code)** *(optionnel, par référence)*
   - Mentionne que ce niveau existe (diagrammes de classes UML, ERD) mais n'est pas détaillé ici sauf besoin spécifique.
   - Peut être remplacé par des **diagrammes de séquence** pour illustrer des scénarios critiques.

8. **Vue Exécution (Scénarios)**
   - Illustre 1 à 3 scénarios critiques ou complexes.
   - Utilise des **diagrammes de séquence PlantUML** ou une description textuelle claire.
   - Montre le flux traversant les différents niveaux C4.

9. **Vue Déploiement** *(section standardisée)*
   - **Diagramme C4-Déploiement** en PlantUML : montre l'allocation des conteneurs sur les infrastructures (serveurs, cloud, on-premise).
   - Reproduis exactement ce qui suit, sauf le tableau « Environnements » que tu peux adapter :

   ```markdown
   ### Environnements
   | Environnement | Hébergement | Serveurs | Réseau | Particularités |
   |---------------|-------------|----------|--------|----------------|
   | Développement | À compléter | À compléter | À compléter | À compléter |
   | Recette       | À compléter | À compléter | À compléter | À compléter |
   | Production    | À compléter | À compléter | À compléter | À compléter |

   ### Infrastructure
   Le produit est hébergé sur le cloud interne ECO4 basé sur Openstack, dans le tenant 'pnm3' du département.  
   Le reverse-proxy Nginx du schéma ci-dessous est en fait une paire de Nginx load-balancés en frontal des produits hébergés sur le tenant.

   ```Plantuml
   @startuml
   !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

   Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
       Deployment_Node(nginx, "Nginx Cluster", "Load Balancer") {
           Container(app, "Application", "Docker", "Application principale")
       }
       Deployment_Node(db, "Base de données", "PostgreSQL") {
           ContainerDb(database, "Database", "PostgreSQL", "Données métier")
       }
   }

   Rel(nginx, app, "HTTP/HTTPS")
   Rel(app, database, "JDBC/SQL")
   @enduml
   ```

   ### Supervision
   Le produit est supervisé via le système standard du GTI pour ce faire :
   - via Portainer pour la partie purement conteneurisée,
   - via la stack Prometheus/Grafana/Loki/AlertManager,
   - Le produit dispose également d'une supervision PSIN.

   ### Sauvegardes
   Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
   - le stockage objet B3 du IaaS ministériel,
   - le stockage objet Outscale SecNumCloud (via la prestation qu'a le GTI sur le marché "Nuage Public"),
   - le stockage objet standard de Google Cloud (via la prestation qu'a le GTI sur le marché "Nuage Public").
   ```

10. **Sujets transverses**
    - Couvre les aspects communs à tous les composants : authentification, journalisation, monitoring, gestion des erreurs, API, etc.

11. **Exigences de qualité**
    - Liste les exigences critiques.
    - Pour chacune, donne un scénario de validation concret.

12. **Risques et dettes techniques**
    - Identifie les risques majeurs ou dettes existantes.
    - Propose une mesure corrective ou d'atténuation.

13. **Annexes**
    - Fournis un glossaire des termes techniques.
    - Inclus les décisions d'architecture (ADR) pertinentes.

## Règles de forme et notation C4

- Utilise systématiquement des **liens internes** pour la navigation (ex. : « ↩ Retour au sommaire »).
- Insère un **[TOC]** en haut du document.
- **Tous les diagrammes architecturaux doivent utiliser la bibliothèque C4-PlantUML** avec l'inclusion :
  ```plantuml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
  !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml
  ```
- Respecte la **légende C4** : Person (utilisateur), System (système existant), System_Boundary (frontière), Container (application/bd), Component (module interne).
- Le document doit être **compatible** avec les extensions VS Code / Obsidian (ex. : Markdown Preview Enhanced, PlantUML).
- Aucun lien brisé, aucun fichier externe requis.
- Le style doit être **professionnel, concis, orienté action**, adapté à un public mixte (développeurs, exploitants, MOA, RSSI).

## Sortie attendue

- Un seul fichier `.md`.
- Aucune mention de fichiers sources ou de prompts.
- Prêt à être utilisé tel quel dans un environnement de documentation technique avec support C4-PlantUML activé.

---

**Principaux changements C4 appliqués :**
- Remplacement des "Vues" génériques par les **4 niveaux C4** (Contexte, Conteneurs, Composants, Code)
- Ajout de la **Vue Déploiement C4** (niveau infrastructure)
- Standardisation sur la **syntaxe C4-PlantUML** avec inclusion des bibliothèques officielles
- Conservation de votre section Déploiement standardisée mais enrichie d'un exemple C4
- Maintien de la compatibilité VS Code/Obsidian