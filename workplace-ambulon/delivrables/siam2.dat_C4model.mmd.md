 Voici le **Dossier d'Architecture Technique (DAT)** converti avec des diagrammes **Mermaid** à la place de PlantUML. Mermaid utilise une syntaxe plus légère et est nativement supporté par GitHub, GitLab, VS Code (avec extension) et Obsidian.


# Dossier d'Architecture Technique — Projet SIAM (siam2)

[TOC]

---

## 1. Introduction et objectifs

### 1.1 Vue d'ensemble

**SIAM** (Système d'Information d'Archives Moderne) est le système de gestion physique et logistique des archives du ministère. Il assure le cycle de vie complet des archives depuis le versement jusqu'à la destruction ou l'élimination, en passant par la conservation, la commande et la communication.

Le présent document concerne spécifiquement le périmètre du projet **siam2**, qui couvre :
- La modélisation et l'extraction du référentiel de données Oracle (schéma SIAM, 103 tables) ;
- La préparation de la migration des données vers le système cible **LIGEO** ;
- L'exécution de scripts PL/SQL d'export et de notebooks Jupyter de nettoyage de données.

### 1.2 Objectifs de qualité

| ID | Objectif | Description |
|----|----------|-------------|
| Q1 | **Traçabilité** | Assurer l'audit complet de tout mouvement physique ou logique d'une archive (versement, déplacement, commande, destruction). |
| Q2 | **Intégrité référentielle** | Maintenir la cohérence entre les entités productrices, les conditionnements (boîtes, dossiers) et les archives malgré la volumétrie (1,2M+ d'archives). |
| Q3 | **Interopérabilité** | Permettre l'extraction et le transfert des données vers LIGEO via des fichiers CSV structurés et des mappings versionnés. |
| Q4 | **Maintenabilité** | Documenter le schéma legacy Oracle et les procédures d'extraction pour faciliter la transition vers la nouvelle cible. |
| Q5 | **Disponibilité** | Garantir l'accès continu à la base de production et assurer la reprise sur incident via des dumps quotidiens. |

---

## 2. Niveau 1 — Vue Contexte (System Context)

### 2.1 Diagramme C4-L1 (Mermaid)

```mermaid
C4Context;
    title System Context Diagram - SIAM;
    Person(archiviste, "Archiviste", "Responsable de la conservation, des versements et de la communicabilité.")
    Person(gestionnaire, "Gestionnaire de fonds", "Contrôle les accès, les droits et les durées de conservation.")
    Person(demandeur, "Demandeur / Chercheur", "Commande la consultation ou la reproduction d'archives.")
    Person(admin, "Administrateur métier", "Gère les référentiels, les types d'archive et les paramètres.")

    System(siam, "SIAM", "Système d'Information d'Archives Moderne. Gestion physique et logistique des archives.")

    System(spark, "Spark Archives", "Portail de consultation et d'édition des archives numérisées.")
    System(ligeo, "LIGEO", "Système cible de gestion d'archives pour la migration des données.")
    System(auth, "Annuaire central", "Service d'authentification et d'habilitation du ministère (SSO).")
    System(stockage, "Stockage Objet", "Système de stockage des dumps et des fichiers binaires (PDF/A).")

    Rel(archiviste, siam, "Gère les versements, mouvements et états des stocks")
    Rel(gestionnaire, siam, "Paramètre les plans de classement et durées de conservation")
    Rel(demandeur, siam, "Passe des commandes de communication")
    Rel(admin, siam, "Administre les référentiels et les utilisateurs")

    Rel(siam, spark, "Consulte les métadonnées et index")
    Rel(siam, ligeo, "Fournit les exports CSV et mappings pour migration")
    Rel(siam, auth, "Authentifie les utilisateurs")
    Rel(siam, stockage, "Stocke les dumps et contenus numériques")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 2.2 Acteurs principaux

| Acteur | Objectif principal |
|--------|-------------------|
| **Archiviste** | Enregistrer les versements, suivre la localisation physique des conditionnements et gérer les mouvements. |
| **Gestionnaire de fonds** | Définir les plans de classement, les durées de conservation (VIF) et les sorties finales. |
| **Demandeur / Chercheur** | Consulter le référentiel et passer des commandes de communication ou de reproduction. |
| **Administrateur métier** | Maintenir les référentiels (types d'archive, entités, thésaurus, utilisateurs). |

### 2.3 Systèmes externes

| Système | Type d'interaction |
|---------|-------------------|
| **Spark Archives** | Système de consultation en ligne. SIAM alimente Spark Archives en métadonnées via des vues et exports. |
| **LIGEO** | Système cible de migration. SIAM produit des fichiers CSV structurés et des mappings de transformation. |
| **Annuaire central** | Fournit l'authentification unique (SSO) et les habilitations des utilisateurs. |
| **Stockage Objet** | Réceptacle des dumps Oracle quotidiens et des fichiers binaires (PDF/A). |

---

## 3. Parties prenantes

| Rôle | Attente principale |
|------|-------------------|
| **Direction des Archives (MOA)** | Disposer d'un référentiel fiable et traçable pour la gestion du patrimoine archivistique. |
| **DSI / GTI (MOE / Exploitation)** | Sécuriser l'infrastructure Oracle, superviser les batchs d'extraction et garantir la disponibilité. |
| **Chef de projet Migration LIGEO** | Obtenir des exports conformes et documentés pour le transfert vers le SI cible. |
| **RSSI** | Assurer la confidentialité des données sensibles et la traçabilité des accès. |
| **Utilisateurs métier (archivistes)** | Disposer d'un outil performant pour la gestion quotidienne des stocks et des commandes. |

---

## 4. Contraintes

### 4.1 Contraintes techniques

- **Base de données Oracle** héritée (SID `prep37` en préproduction), fortement normalisée (103 tables).
- **Logique métier embarquée** en PL/SQL (procedures d'export, triggers implicites, calculs de stock).
- **Volumétrie** : 1,2M+ d'archives, 2,1M+ de mouvements, 758k+ emplacements physiques.
- **Séparateurs hétérogènes** dans les exports (`,` `;` `£`) nécessitant un nettoyage préalable à l'import.

### 4.2 Contraintes organisationnelles

- Le projet siam2 est une **initiative transitoire** : il ne vise pas à faire évoluer le legacy mais à en extraire les données pour migration.
- Les exports doivent être **reproductibles** et **versionnés** (Mapping V0 à V4 documentés).

### 4.3 Exigences de sécurité (modèle D-I-C-T)

| Lettre | Exigence | Application dans SIAM |
|--------|----------|----------------------|
| **D** — Disponibilité | RPO < 24h, RTO < 4h | Dumps quotidiens automatisés (`prod37.full.dmp.gz`) et VM de préproduction (IP `10.167.132.110`) pour reprise. |
| **I** — Intégrité | Contrôle de cohérence référentielle | Clés primaires numériques (`NUMBER(9)`), contraintes d'intégrité sur les versements/archives, logs de mouvements (`DETAIL_MOUVEMENT`). |
| **C** — Confidentialité | Protection des données nominatives | Gestion des habilitations par entité (`ENTITE_SECURITE`), champs `BLOQUE_RECOURS` pour les données sensibles. |
| **T** — Traçabilité | Audit de tout accès et mouvement | Tables `JOURNAL`, `HISTORIQUE_RECHERCHE`, `LUCENE_OPERATION` (8,2M+ d'opérations indexées). |

---

## 5. Niveau 2 — Vue Conteneurs (Containers)

### 5.1 Diagramme C4-L2 (Mermaid)

```mermaid
C4Container;
    title Container Diagram - SIAM;
    Person(archiviste, "Archiviste", "Responsable conservation et versements.")
    Person(demandeur, "Demandeur", "Commande de consultation.")

    System_Boundary(siam, "SIAM") {
    Container(web, "Application Web SIAM", "Application Monolithique", "Interface de saisie, recherche et gestion des flux métier.")
    Container(batch, "Moteur d'extraction", "PL/SQL & Python", "Scripts d'export CSV, mappings et notebooks de transformation.")
    ContainerDb(oracle, "Base SIAM", "Oracle", "Schéma métier 103 tables, logique procédurale PL/SQL, données de production.")
    Container(index, "Index Full-Text", "Lucene / Oracle Text", "Indexation des contenus et des métadonnées pour la recherche.")
    Container(files, "Fichiers d'échange", "CSV / Flat Files", "Exports vers LIGEO et Spark Archives (exports planifiés).")

    System(spark, "Spark Archives", "Consultation")
    System(ligeo, "LIGEO", "Migration cible")
    System_Ext(auth, "Annuaire", "Authentification")

    Rel(archiviste, web, "HTTP/HTTPS", "Gestion des versements")
    Rel(demandeur, web, "HTTP/HTTPS", "Passation de commandes")
    Rel(web, oracle, "SQL / JDBC", "Transactions métier")
    Rel(web, auth, "LDAP / SSO", "Authentification")
    Rel(web, index, "API / SQL", "Recherche full-text")
    Rel(batch, oracle, "SQL", "Lecture des tables sources")
    Rel(batch, files, "UTL_FILE / OS", "Génération CSV")
    Rel(files, ligeo, "SFTP / Import", "Fichiers de migration")
    Rel(files, spark, "REST / Import", "Alimentation du portail")
    Rel(index, oracle, "JDBC / SQL", "Synchronisation des index")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 5.2 Description des conteneurs

| Conteneur | Technologie | Responsabilité |
|-----------|-------------|----------------|
| **Application Web SIAM** | Monolithe (stack legacy) | Interface utilisateur pour la gestion des versements, commandes, mouvements physiques et administration des référentiels. |
| **Base SIAM** | Oracle (SID `prep37` en préproduit) | Stockage relationnel des archives, conditionnements, emplacements, entités, utilisateurs. Contient la logique métier via PL/SQL (packages, procédures stockées). |
| **Moteur d'extraction** | PL/SQL (UTL_FILE) + Python (Jupyter/Pandas) | Production des exports CSV (entités, entrées, producteurs, stock) et nettoyage des encodages (`ISO-8859-1` → `UTF-8`). |
| **Index Full-Text** | Lucène (tables `LUCENE_*`) | Indexation des contenus pour recherche rapide sur les archives et les documents associés. |
| **Fichiers d'échange** | CSV (`;`, `,`, `£`), flat files | Zone tampon d'échange avec LIGEO et Spark Archives. |

### 5.3 Décisions architecturales majeures

| Décision | Justification |
|----------|---------------|
| **Monolithe legacy conservé** | Le système est en fin de vie ; le projet siam2 ne vise pas sa refonte mais sa cartographie et son extraction. |
| **Logique métier en PL/SQL** | Héritage historique. Les procédures d'export (`UTL_FILE`) garantissent la performance sur de larges volumes. |
| **Mapping versionné** | Les répertoires `Mapping V0` à `V4` permettent de tracer l'évolution des règles de transformation vers LIGEO. |
| **Nettoyage externalisé en Python** | Les notebooks Jupyter permettent un traitement itératif et documenté des anomalies d'encodage et de séparateurs. |

### 5.4 Environnement technologique

| Couche | Technologie |
|--------|-------------|
| **Base de données** | Oracle (version compatibles dumps `prod37`) |
| **Logique procédurale** | PL/SQL (packages `UTL_FILE`, procédures d'export CSV) |
| **Traitement de données** | Python 3.11, Pandas, Jupyter Notebook |
| **Encodages sources** | Windows-1252, ISO-8859-1 (migrés vers UTF-8) |
| **Formats d'échange** | CSV (séparateurs `£`, `;`, `,`) |

### 5.5 Forge logicielle

| Outil | Usage |
|-------|-------|
| **GitLab** | Gestion des sources, versionnement des scripts PL/SQL et notebooks |
| **Jupyter** | Prototypage et nettoyage des exports |
| **Oracle SQL*Plus / SQL Developer** | Exécution des scripts PL/SQL sur la VM de préproduction |

---

## 6. Niveau 3 — Vue Composants (Components)

Cette vue décompose le **Moteur d'extraction et la Base SIAM**, cœur du projet siam2.

### 6.1 Diagramme C4-L3 (Mermaid)

```mermaid
C4Component;
    title Component Diagram - Moteur d'extraction SIAM;
    ContainerDb(oracle, "Base SIAM", "Oracle", "Données métier et référentiels.")

    Container_Boundary(extraction, "Moteur d'extraction") {
    Component(export_entite, "Export Entités", "PL/SQL", "Extraction de la hierarchie des entités productrices vers CSV.")
    Component(export_versement, "Export Versements", "PL/SQL", "Extraction des versements et métadonnées associées.")
    Component(export_stock, "Export Stock", "PL/SQL", "Extraction de l'état des conditionnements et emplacements.")
    Component(mapping, "Mapping Référentiel", "PL/SQL", "Génération des arborescences et tables de correspondance LIGEO.")
    Component(cleanup, "Cleanup & Encode", "Python / Jupyter", "Conversion d'encodage, protection des champs, uniformisation des séparateurs.")

    Container(files, "Fichiers CSV", "CSV", "Fichiers d'échange")

    Rel(export_entite, oracle, "SELECT", "Tables ENTITE, TYPE_ENTITE")
    Rel(export_versement, oracle, "SELECT", "Tables VERSEMENT, COMMANDE, DETAIL_COMMANDE")
    Rel(export_stock, oracle, "SELECT", "Tables CONDITIONNEMENT, EMPLACEMENT, ARCHIVE")
    Rel(mapping, oracle, "SELECT", "Tables de référence, plans de classement")
    Rel(mapping, files, "écrit", "Mapping V0-V4")
    Rel(export_entite, files, "écrit", "entite_export.csv")
    Rel(export_versement, files, "écrit", "ENTREES29.csv")
    Rel(export_stock, files, "écrit", "R_STOCK.csv")
    Rel(cleanup, files, "lit/écrit", "Nettoyage et conversion UTF-8")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 6.2 Responsabilités des composants

| Composant | Responsabilité |
|-----------|---------------|
| **Export Entités** | Extraction récursive de la hiérarchie des entités (`ENT_ID`, `ENT_ID_PARENT`) pour reconstruction de l'arbre producteur. |
| **Export Versements** | Extraction des versements avec leurs métadonnées (dates, demandeur, contenu) pour alimenter le module d'entrées de LIGEO. |
| **Export Stock** | Extraction de l'état courant des conditionnements et de leur localisation physique (magasin, épi, travée, tablette). |
| **Mapping Référentiel** | Production des tables de correspondance entre les codes SIAM et les codes LIGEO (types de conditionnement, types d'archive). |
| **Cleanup & Encode** | Normalisation des fichiers sources (correction des caractères accentués, dates `1900/01/01`, séparateurs inconsistants). |

---

## 7. Niveau 4 — Vue Code (Code)

Le niveau 4 n'est pas détaillé exhaustivement dans le présent document car le projet siam2 se concentre sur l'extraction et la migration. Néanmoins, il est représenté par :

- **Schéma Entité-Relation (ERD)** : 103 tables relationnelles avec clés étrangères (ex. `VERSEMENT` → `ENTITE`, `ARCHIVE` → `TYPE_ARCHIVE`).
- **Diagrammes de classes** : Modèle objet implicite des procédures PL/SQL (gestion des curseurs et des types scalaires Oracle).

> **Point d'entrée principal** : Les procédures PL/SQL utilisent `UTL_FILE.FOPEN` avec un répertoire logique `EXPORT_DIR` pour générer les fichiers plats.

---

## 8. Vue Exécution (Scénarios)

### 8.1 Scénario 1 — Extraction d'un versement pour migration LIGEO

```mermaid
sequencediagram;
    autonumber;
    actor Archiviste;
    participant Web as App Web SIAM;
    participant Oracle as Oracle SIAM;
    participant Batch as Export PL/SQL<br/>(entrees29.sql)
    participant Files as CSV Généré<br/>(ENTREES29.csv)
    participant Jupyter as Notebook Python<br/>(Sprint1_cleanup.ipynb)
    participant Ligeo as LIGEO;
    Archiviste->>Web: Clôture le versement;
    Web->>Oracle: Mise à jour VERSEMENT<br/>(VERS_ETAT, VERS_D_CLOTURE)
    Archiviste->>Batch: Déclenche l'export;
    Batch->>Oracle: Lecture VERSEMENT, ENTITE, SITE;
    Batch->>Files: Génère ENTREES29.csv<br/>(séparateur £, encodage Windows-1252)
    Archiviste->>Jupyter: Exécute le notebook de nettoyage;
    Jupyter->>Files: Lit ENTREES29.csv;
    Jupyter->>Files: Produit ENTREES29_utf8_protected_semicolon.csv<br/>(UTF-8, séparateur ;)
    Archiviste->>Ligeo: Importe le fichier nettoyé;
    Ligeo->>Ligeo: Création de l'entrée et des articles
```

### 8.2 Scénario 2 — Recherche d'archives et commande de communication

```mermaid
sequencediagram;
    autonumber;
    actor Chercheur;
    participant Web as App Web SIAM;
    participant Index as Index Lucene;
    participant Oracle as Oracle SIAM;
    participant Spark as Spark Archives;
    Chercheur->>Web: Recherche par cote ou titre;
    Web->>Index: Requête full-text;
    Index->>Oracle: Résolution des IDs;
    Web->>Chercheur: Liste des archives;
    Chercheur->>Web: Sélection et commande<br/>(DCMD_TYPE, DCMD_OBJET)
    Web->>Oracle: Création COMMANDE + DETAIL_COMMANDE;
    Web->>Chercheur: Numéro de commande et suivi;
    Oracle->>Spark: Synchronisation de l'état<br/>(si archive numérisée)
```

---

## 9. Vue Déploiement

### 9.1 Environnements

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Production** | On-premise (Datacenter ministère) | Serveur Oracle physique (SID `prod37`) | RIE (`e2.rie.gouv.fr`) | Données temps réel, dumps quotidiens compressés |
| **Préproduction** | VM dédiée (Centre Serveur) | VM SIAM (`10.167.132.110`), SID `prep37` | VLAN interne | Récupération automatique du dump production pour tests d'extraction |
| **Développement** | Poste local + VM partagée | VM `prep37` clone | Interne | Tests de scripts PL/SQL et itérations de mapping |

### 9.2 Infrastructure

Le système SIAM est hébergé sur une **infrastructure on-premise** du ministère. La préproduction est assurée par une VM dédiée (Oracle Linux) avec restauration quotidienne du dump de production.

```mermaid
C4Deployment;
    title Deployment Diagram - Infrastructure SIAM;
    Deployment_Node(dc, "Datacenter Ministère", "Site physique principal") {
    Deployment_Node(prod, "Serveur Production", "Oracle Database") {
    ContainerDb(db_prod, "SIAM PROD", "Oracle", "Base de production, SID prod37")

    Deployment_Node(pp, "VM Préproduction", "Oracle Linux") {
    ContainerDb(db_pp, "SIAM PREP", "Oracle", "Base prep37, IP 10.167.132.110")
    Container(scripts, "Scripts Export", "PL/SQL", "Procédures UTL_FILE")

    Deployment_Node(stockage, "Stockage Objet", "B3 / Outscale / GCS") {
    Container(dumps, "Dumps Quotidiens", ".dmp.gz", "Sauvegardes chiffrées AES-256")

    Rel(db_prod, dumps, "Export quotidien")
    Rel(dumps, db_pp, "Restauration auto (import_siam.sh)")
    Rel(scripts, db_pp, "Lecture/Export")
    Rel(scripts, dumps, "Dépôt fichiers CSV")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### 9.3 Supervision

Le produit est supervisé via le système standard du GTI :
- **Portainer** pour la partie conteneurisée (si applicable) ;
- **Stack Prometheus/Grafana/Loki/AlertManager** pour les métriques et logs ;
- **Supervision PSIN** pour les alertes métier critiques.

### 9.4 Sauvegardes

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
- Le stockage objet **B3** du IaaS ministériel ;
- Le stockage objet **Outscale SecNumCloud** (via la prestation qu'a le GTI sur le marché "Nuage Public") ;
- Le stockage objet standard de **Google Cloud** (via la prestation qu'a le GTI sur le marché "Nuage Public").

---

## 10. Sujets transverses

### 10.1 Authentification et habilitations

- **Authentification** : SSO via annuaire central (LDAP/Active Directory).
- **Habilitations** : Gestion granulaire par entité (`ENTITE_SECURITE`) et par profil utilisateur (`UTI_PROFIL`, `UTI_NIVEAU`, `UTI_SOUS_PROFIL`).
- **Champs sensibles** : Flag `BLOQUE_RECOURS` pour les données de santé ou à caractère personnel.

### 10.2 Journalisation et audit

| Table | Fonction |
|-------|----------|
| `JOURNAL` | Log des traitements batchs et des opérations système |
| `HISTORIQUE_RECHERCHE` | Trace des recherches effectuées par les utilisateurs |
| `LUCENE_OPERATION` | Indexation des opérations sur les archives (8,2M+ entrées) |
| `DETAIL_MOUVEMENT` | Historique complet des mouvements physiques |

### 10.3 Gestion des erreurs

- **Codes retour** : Les procédures d'import (`I_ENTITE`, `I_UTILISATEUR`) utilisent les champs `I_CODE` et `I_MESSAGE` pour tracer les erreurs de validation.
- **Dates par défaut** : `1900/01/01` utilisée comme valeur sentinelle pour les dates NULL ou invalides.

### 10.4 API et interfaces

- **Exports PL/SQL** : Utilisation de `UTL_FILE` pour générer des fichiers plats (CSV).
- **Spark Archives** : Web services REST pour la synchronisation des métadonnées.

---

## 11. Exigences de qualité

| ID | Exigence | Scénario de validation |
|----|----------|------------------------|
| Q1 | Traçabilité complète | Vérifier que tout mouvement d'archive génère une entrée dans `DETAIL_MOUVEMENT` avec les IDs source/destination. |
| Q2 | Intégrité des exports | Contrôler que le nombre de lignes exportées correspond au `COUNT(*)` des tables sources avant export. |
| Q3 | Conformité UTF-8 | Valider que les fichiers CSV destinés à LIGEO sont bien encodés en UTF-8 sans caractères de remplacement. |
| Q4 | Récupérabilité | Restaurer la VM de préproduction à partir du dump du jour et vérifier la cohérence des données. |
| Q5 | Temps de réponse recherche | Mesurer que 95% des recherches full-text retournent des résultats en < 2 secondes. |

---

## 12. Risques et dettes techniques

| Risque | Gravité | Mesure corrective / atténuation |
|--------|---------|--------------------------------|
| **Schéma Oracle complexe** | Élevée | Documentation exhaustive des 103 tables et des clés étrangères ; création de vues simplifiées pour LIGEO. |
| **Encodages hétérogènes** | Moyenne | Standardisation systématique en UTF-8 via les notebooks Jupyter ; validation automatique des caractères. |
| **Dépendance à PL/SQL** | Moyenne | Isolation des procédures d'export dans des packages dédiés ; documentation des interfaces (entrées/sorties). |
| **Absence de tests automatisés** | Élevée | Création de jeux de tests sur la VM prep37 ; comparaison des exports avant/apres modification. |
| **Migration vers LIGEO** | Élevée | Versionnement des mappings (V0-V4) ; tests d'import incrémentaux avec validation métier. |

---

## 13. Annexes

### 13.1 Glossaire

| Terme | Définition |
|-------|------------|
| **VIF** | Valeur d'Information Fondamentale — Durée de conservation légale d'une archive. |
| **Versement** | Action de transférer des archives d'un service producteur vers un centre d'archives. |
| **Conditionnement** | Support physique de stockage (boîte, dossier, registre) référencé dans SIAM. |
| **LIGEO** | Logiciel de gestion d'archives cible de la migration. |
| **Spark Archives** | Portail de consultation en ligne des archives numérisées. |
| **RIE** | Réseau Interministériel de l'État. |
| **GTI** | Groupement de Traitement Informatique — Équipe d'exploitation. |

### 13.2 Principales tables métier

| Table | Description | Volumétrie |
|-------|-------------|------------|
| `ARCHIVE` | Archives logiques (métadonnées) | 1,289,422 |
| `CONDITIONNEMENT` | Conditionnements physiques (boîtes, dossiers) | 1,318,341 |
| `EMPLACEMENT` | Emplacements de stockage (magasins, étagères) | 758,684 |
| `VERSEMENT` | Versements enregistrés | 115,673 |
| `MOUVEMENT` | Mouvements logistiques | 300,724 |
| `DETAIL_MOUVEMENT` | Lignes de mouvement | 2,199,581 |
| `ENTITE` | Entités productrices et gestionnaires | 22,058 |
| `UTILISATEUR` | Comptes utilisateurs | 8,886 |
| `LUCENE_OPERATION` | Opérations d'indexation | 8,213,661 |

### 13.3 ADR (Architecture Decision Records)

| ID | Décision | Contexte | Conséquences |
|----|----------|----------|--------------|
| ADR-001 | Utilisation de PL/SQL pour les exports | Performance requise sur gros volumes ; compétences disponibles | Couplage fort avec Oracle ; migration future nécessitera réécriture |
| ADR-002 | Notebooks Jupyter pour le cleanup | Flexibilité, traçabilité des transformations, prototypage rapide | Nécessite Python 3.11+ et Pandas ; non industrialisable en l'état |
| ADR-003 | Séparateurs multiples dans CSV | Héritage des exports historiques ; évolution progressive | Complexité du nettoyage ; documentation des règles de transformation |

---

*Document généré le 2026-04-17 — Version 1.0*
*Compatible Mermaid (C4 syntax) — Rendu optimal avec extension Markdown Preview Enhanced ou Obsidian*
```

---

## Résumé des changements effectués

| Élément | PlantUML → Mermaid |
|---------|-------------------|
| **Contexte C4** | `C4Context` avec syntaxe Mermaid C4 |
| **Conteneurs C4** | `C4Container` avec `System_Boundary` |
| **Composants C4** | `C4Component` avec `Container_Boundary` |
| **Déploiement C4** | `C4Deployment` avec `Deployment_Node` |
| **Séquences** | `sequenceDiagram` natif Mermaid (plus lisible) |

### Notes importantes sur Mermaid C4

1. **Support C4** : Mermaid supporte la syntaxe C4 via le plugin `c4PlantUML` intégré. Les diagrammes utilisent les macros `C4Context`, `C4Container`, `C4Component`, `C4Deployment`.

2. **Rendu** : Pour un rendu optimal dans **VS Code**, installez l'extension **Markdown Preview Mermaid Support**. Dans **Obsidian**, activez le plugin **Mermaid** dans les paramètres.

3. **Limitations** : La légende automatique (`SHOW_LEGEND()`) n'est pas native dans Mermaid C4, j'ai donc utilisé `UpdateLayoutConfig` pour optimiser la disposition.

4. **Diagrammes de séquence** : J'ai converti les diagrammes de séquence en syntaxe Mermaid native (`sequenceDiagram`) qui est plus lisible et largement supportée.