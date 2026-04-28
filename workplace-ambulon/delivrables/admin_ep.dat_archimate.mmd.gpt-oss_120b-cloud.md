# Dossier d’Architecture Technique (DAT) – **admin_ep**  
*Projet : Administration des établissements publics (admin_ep)*  

> **Version :** 1.3.3 – 12/2021 (baseline) → 1.4.0 (cible)  
> **Date :** 27 avril 2026  
> **Auteur :** Architecte EA – certification ArchiMate 3.2  

---  

## 1. Vue d’ensemble ArchiMate  

| Élément | Description |
|---|---|
| **Cadre** | ArchiMate 3.2 (The Open Group) – alignement avec ISO/IEC/IEEE 42010 :2022 et TOGAF 9.2. |
| **Préoccupations** | - **Fonctionnelle** : gestion des administrateurs, mandats, recherche, reporting. <br>- **Qualité** : sécurité (HTTPS, Cerbère), disponibilité, maintenabilité. <br>- **Evolution** : migration Tomcat 10 / PostgreSQL 15, conteneurisation. |
| **Couches couvertes** | Métier, Application, Technologie (plus optionnel : Stratégie, Migration). |
| **Viewpoints utilisés** | Organization, Business‑Process‑Cooperation, Application‑Structure, Infrastructure, Realisation‑Overlay, Layered, Migration. |
| **Modèle de référence** | <img src="https://www.archimatetool.com/assets/img/archimate_3.2.png" width="600"/> (adapté aux modules *admin_ep*). |

---  

## 2. Couche Métier  

### 2.1 Acteurs & Rôles  

| Business Actor | Business Role | Commentaire |
|---|---|---|
| **SG/STMAR/STAR3** | *Maîtrise d’ouvrage* | Pilotage fonctionnel (SG / SPES). |
| **SG/DNUM/PNM/DPNM3/BPN** | *Maîtrise d’œuvre* | Développement & exploitation (CGI, équipes internes). |
| **Utilisateurs** (SPES, DG de tutelle, opérateurs) | *Utilisateur final* | Accès via Cerbère. |
| **Administrateur technique** | *Opérateur de production* | Gestion des serveurs Tomcat / PostgreSQL. |

### 2.2 Services métier  

| Business Service | Description |
|---|---|
| **Gestion des administrateurs** | CRUD sur les administrateurs, affectation à des établissements. |
| **Gestion des mandats** | Création, mise à jour, suivi d’échéance, archivage. |
| **Alimentation automatique JORF** | Extraction quotidienne des arrêtés JORF → mise à jour des mandats. |
| **Authentification Cerbère** | Validation des droits d’accès selon les profils. |
| **Recherche & Consultation** | Recherche multi‑critères (établissement, nom, mandat). |
| **Statistiques & Reporting** | Tableaux de bord, indicateurs de périmètre et d’échéance. |
| **Notification d’échéance** | Envoi d’emails aux référents lorsqu’un mandat approche de sa fin. |

### 2.3 Processus métier (extraits)  

```mermaid
graph TB
  subgraph "Processus de gestion d’un mandat"
    A[Création du mandat (admin)] --> B[Enregistrement en base]
    B --> C[Déclenchement du job JORF (quotidien)]
    C --> D[Analyse JORF → mise à jour mandat]
    D --> E[Contrôle d’échéance (batch nocturne)]
    E --> F[Envoi de notification (mail)]
  end
```

### 2.4 Objets & événements métier  

| Business Object | Exemple |
|---|---|
| **Administrateur** | `id`, `nom`, `prénom`, `profilCerbère`. |
| **Etablissement** | `id`, `siren`, `libellé`, `typeInstance`. |
| **Mandat** | `id`, `type (Titulaire/Suppléant)`, `dateDébut`, `dateFin`. |
| **Charge** | Ministère ou ministère‑charge. |
| **Event : MandatCréé** | Publication dans le journal officiel. |
| **Event : MandatÉchu** | Trigger du job de notification. |

### 2.5 Diagramme de Vue Organisationnelle  

```mermaid
graph LR
    classDef actor fill:#FFCC99,stroke:#333,stroke-width_2px;
    classDef role fill:#FFFF99,stroke:#333,stroke-width_2px;
    classDef service fill:#FFFF66,stroke:#333,stroke-width_2px;
    SG[SG/STMAR/STAR3]:::actor -->|MAÎTRISE| MOA[Maîtrise d’Ouvrage]:::role;
    SG_DNUM[SG/DNUM/PNM/DPNM3/BPN]:::actor -->|MAÎTRISE| MOE[Maîtrise d’Œuvre]:::role;
    Users[Utilisateurs (SPES, DG)]:::actor -->|UTILISE| UI[Interface Utilisateur]:::service;
    MOA -->|DEFINIT| GEST_ADM[Gestion des administrateurs]:::service;
    MOA -->|DEFINIT| GEST_MAND[Gestion des mandats]:::service;
    MOE -->|FOURNIT| APP[Application admin_ep]:::service;
    APP -->|EXPLOITE| DB[Base de données PostgreSQL]:::service
```

---  

## 3. Couche Application  

### 3.1 Composants applicatifs  

| Application Component | Description | Artefacts |
|---|---|---|
| **admin_ep‑web** (WAR) | Front‑end Struts2 / Vertigo, contrôleurs MVC. | `admin_ep‑web‑*.war` |
| **boot‑initializer** | Initialisation Spring‑Boot (I18n, MasterData, Scheduler, Security). | `boot‑*.jar` |
| **services‑baseadmin** | Implémentations métier (Administrateur, Gestionnaire, Mandat, etc.). | `baseadmin‑services‑*.jar` |
| **services‑integration** | Connecteurs vers les tables d’intégration (charge, collège, direction…). | `integration‑services‑*.jar` |
| **security‑filter** | Filtre servlet Cerbère & JWT. | `security‑filter‑*.jar` |
| **article‑analyser** | Extraction et indexation JORF (Elasticsearch). | `article‑analyser‑*.jar` |
| **persistence** | JPA / Hibernate (persistence.xml). | `persistence‑*.jar` |
| **utils** | Fonctions génériques (StringUtil, OdsUtil, NomPrenomUtil). | `utils‑*.jar` |

### 3.2 Services applicatifs (mapping B‑S)  

| Application Service | Business Service réalisé | Application Component |
|---|---|---|
| **AdminManagementService** | Gestion des administrateurs | `services‑baseadmin` |
| **MandatService** | Gestion des mandats, archivage | `services‑baseadmin` |
| **JORFIngestionService** | Alimentation automatique JORF | `article‑analyser` |
| **AuthCerbèreService** | Authentification Cerbère | `security‑filter` |
| **SearchService** | Recherche multi‑critères | `services‑integration` |
| **NotificationService** | Notification d’échéance | `services‑baseadmin` + Scheduler |

### 3.3 Fonctions & interactions applicatives  

```mermaid
graph TD
    classDef comp fill:#99CCFF,stroke:#333,stroke-width_2px;
    classDef srv fill:#99FF99,stroke:#333,stroke-width_2px;
    UI[UI Struts2]:::comp -->|Appel| AdminCtrl[AdminController]:::comp;
    AdminCtrl -->|Utilise| AdminService[AdminManagementService]:::srv;
    AdminService -->|Persiste| JPA[Persistence (Hibernate)]:::comp;
    JORFJob[Job JORF (Scheduler)]:::comp -->|Appel| JORFIngest[JORFIngestionService]:::srv;
    JORFIngest -->|Indexe| ES[Elasticsearch]:::comp;
    MandatCtrl[MandatController]:::comp -->|Appel| MandatSrv[MandatService]:::srv;
    MandatSrv -->|Vérifie| NotificationJob[Job Notification]:::comp;
    NotificationJob -->|Envoie| MailSrv[Mail Service]:::srv
```

### 3.4 Diagramme de Vue Applicative  

```mermaid
graph LR
    classDef app fill:#99CCFF,stroke:#333,stroke-width_2px;
    classDef srv fill:#99FF99,stroke:#333,stroke-width_2px;
    Web[admin_ep‑web (WAR)]:::app -->|Expose| AdminAPI[AdminManagementService]:::srv;
    Web -->|Expose| MandatAPI[MandatService]:::srv;
    Web -->|Expose| SearchAPI[SearchService]:::srv;
    Web -->|Expose| AuthAPI[AuthCerbèreService]:::srv;
    JORF[article‑analyser]:::app -->|Expose| JORFAPI[JORFIngestionService]:::srv;
    JORFAPI -->|Persiste| DB[PostgreSQL]:::app;
    JORFAPI -->|Indexe| ES[Elasticsearch]:::app
```

---  

## 4. Couche Technologie  

### 4.1 Infrastructure  

| Technology Node | Rôle | Système Software | Artefacts |
|---|---|---|---|
| **Node 1 – Tomcat 9 (Production)** | Hébergement du WAR | Java 8, Tomcat 9.0.8, Linux RHEL 7 | `admin_ep‑web‑*.war` |
| **Node 2 – PostgreSQL 9.6 (Production)** | Base de données relationnelle | PostgreSQL 9.6.11, Linux RHEL 7 | Scripts `*.sql` (init, update) |
| **Node 3 – Elasticsearch 7.x** | Indexation JORF | Java 8, Linux RHEL 7 | `article‑analyser‑*.jar` |
| **Node 4 – Load‑Balancer (HAProxy)** | Répartition du trafic HTTPS | HAProxy 2.x, Linux | – |
| **Node 5 – Serveur de batch (Cron)** | Exécution des jobs (JORF, notification) | Java 8, Linux | `scheduler‑*.jar` |

### 4.2 Services technologiques  

| Technology Service | Description |
|---|---|
| **WebServerService** | Tomcat 9 (HTTPS, servlet container). |
| **DatabaseService** | PostgreSQL 9.6 (SQL, ACID). |
| **SearchEngineService** | Elasticsearch 7 (full‑text, analyzers). |
| **MessagingService** | SMTP (envoi de notification). |
| **LoadBalancingService** | HAProxy (SSL termination, round‑robin). |

### 4.3 Artifacts & Communication  

| Artifact | Stocké sur | Utilisé par |
|---|---|---|
| `admin_ep‑web‑*.war` | Repository Maven (`adminep-web`) | Tomcat (Node 1) |
| `*.sql` (assembly) | `adminep-database/target/*.zip` | PostgreSQL (Node 2) |
| `article‑analyser‑*.jar` | Maven (`adminep‑article‑analyser`) | Tomcat (Node 1) + Elasticsearch (Node 3) |
| `log4j2.xml`, `struts.xml` | Classpath du WAR | Application (runtime) |
| `application‑config.xml` | Classpath du WAR | Spring‑Boot initialisation |

### 4.4 Diagramme d’Infrastructure  

```mermaid
graph TB
    classDef node fill:#99FF99,stroke:#333,stroke-width_2px;
    classDef svc fill:#99CCFF,stroke:#333,stroke-width_2px;
    LB[Load‑Balancer (HAProxy)]:::node -->|HTTPS| Tomcat[Tomcat 9 (Node 1)]:::node;
    Tomcat -->|Déploie| WAR[admin_ep‑web.war]:::svc;
    Tomcat -->|Accède| PG[PostgreSQL 9.6 (Node 2)]:::node;
    Tomcat -->|Envoie| ES[Elasticsearch 7 (Node 3)]:::node;
    Tomcat -->|Envoie| Mail[SMTP (Node 4)]:::svc;
    Cron[Batch Scheduler (Node 5)]:::node -->|Trigger| JORFJob[JORF Ingestion]:::svc;
    JORFJob -->|Écrit| PG;
    JORFJob -->|Indexe| ES
```

---  

## 5. Couche Stratégique (optionnelle)  

### 5.1 Drivers & Principes  

| Driver | Influence |
|---|---|
| **Conformité réglementaire (JORF)** | → Besoin d’alimentation automatisée, traçabilité. |
| **Sécurité des données** | → HTTPS obligatoire, authentification Cerbère, chiffrement DB. |
| **Disponibilité** | → Architecture en haute disponibilité (LB + Tomcat cluster). |
| **Évolutivité** | → Conteneurisation prévue (Docker/K8s). |
| **Interopérabilité** | → Exposition d’APIs REST (future). |

### 5.2 Objectifs (Goals)  

| Goal | Raison |
|---|---|
| **G‑01** : Mettre à jour les mandats en temps réel (≤ 24 h). | Respect des obligations légales. |
| **G‑02** : Garantir la disponibilité ≥ 99,5 % en production. | Service aux utilisateurs internes. |
| **G‑03** : Assurer la sécurisation du trafic (TLS 1.2+) et des accès (Cerbère). | Protection des données personnelles. |
| **G‑04** : Migrer vers Tomcat 10 & PostgreSQL 15 d’ici Q4 2026. | Modernisation de la stack. |
| **G‑05** : Conteneuriser l’application pour CI/CD automatisé. | Accélérer les livraisons. |

### 5.3 Contraintes & Requirements  

| Constraint | Impact |
|---|---|
| **C‑01** : Version actuelle Tomcat 9 / PostgreSQL 9.6 (legacy). | Nécessité de migration progressive. |
| **C‑02** : Authentification unique via Cerbère (LDAP). | Liaisons d’identité à maintenir. |
| **R‑01** : HTTPS obligatoire sur toutes les URL. | Configurer le LB + Tomcat. |
| **R‑02** : Conservation des archives (mandats échus) ≥ 5 ans. | Politique de rétention DB + stockage. |
| **R‑03** : Interface accessible depuis Intranet uniquement. | Filtrage réseau. |

### 5.4 Value Stream  

```mermaid
graph LR
    VS[Value Stream – Gestion des mandats] --> B1[Création mandat (admin)]
    B1 --> B2[Stockage DB]
    B2 --> B3[Publication JORF]
    B3 --> B4[Analyse JORF (batch)]
    B4 --> B5[Notification d’échéance]
```

---  

## 6. Couche de Mise en Œuvre & Migration (optionnelle)  

| Work Package | Description | Plateau (baseline → target) | Gap |
|---|---|---|---|
| **WP‑01** : Déploiement DB 9.6 → 15 | Scripts de migration, sauvegarde, tests. | Baseline : 9.6 → Target : 15 |
| **WP‑02** : Migration Tomcat 9 → 10 | Refonte des dépendances Servlet 4.0, adaptation Struts2. | Modifications de `web.xml`, `servlet‑api`. |
| **WP‑03** : Conteneurisation (Docker) | Création d’images Docker pour Tomcat + PostgreSQL, CI/CD GitLab. | Aucun conteneur à ce jour. |
| **WP‑04** : Sécurisation TLS 1.3 | Mise à jour du LB, certificats Let's Encrypt. | Certificats auto‑signés en place. |
| **WP‑05** : Automatisation du job JORF | Passage de cron → Spring‑Batch + Kubernetes CronJob. | Cron Linux uniquement. |
| **WP‑06** : Documentation & formation | Mise à jour des fiches produit, guides d’exploitation. | Documentation partielle. |

### 6.1 Plateaux  

| Plateau | Description |
|---|---|
| **Baseline** | Version 1.2.3 (Tomcat 9, PostgreSQL 9.6, WAR monolithique). |
| **Target** | Version 1.4.0 (Tomcat 10, PostgreSQL 15, Docker/K8s, TLS 1.3). |

---  

## 7. Aspects Transverses (Cross‑layer Relationships)  

| Relation | Source (couche) | Destination (couche) | Exemple |
|---|---|---|---|
| **Realization** | Technology Service *DatabaseService* | Application Service *MandatService* | `MandatService` utilise les tables `mandat`. |
| **Realization** | Application Service *JORFIngestionService* | Business Service *Alimentation automatique JORF* | Job JORF réalise le service métier. |
| **Serving** | Business Service *Gestion des administrateurs* | Application Service *AdminManagementService* | Le service applicatif sert le service métier. |
| **Assignment** | Business Role *Développeur* | Application Component *admin_ep‑web* | Les développeurs sont assignés à la composante. |
| **Access** | Business Process *Création mandat* | Data Object *Mandat* | Le processus accède à l’objet mandat. |
| **Influence** | Driver *Conformité JORF* | Goal *G‑01* (mise à jour en temps réel) | Le driver influence l’objectif. |

---  

## 8. Vues Architecturales ArchiMate  

| Vue | Contenu | Viewpoint |
|---|---|---|
| **Cooperation View** | Collaboration entre `AdminController`, `MandatController`, `JORFJob`. | Business‑Process‑Cooperation. |
| **Realisation View** | Chaîne de réalisation : Business Service → Application Service → Technology Service. | Realisation‑Overlay. |
| **Migration View** | Roadmap 2026 Q1–Q4 : WP‑01 → WP‑06. | Migration. |
| **Layered View** | Vue globale (Business → Application → Technology). | Layered. |

---  

## 9. Vue de Traçabilité Complète  

| Élément Métier | Service Métier | Application Component | Application Service | Technology Node |
|---|---|---|---|---|
| **Création d’un administrateur** | Gestion des administrateurs | `admin_ep‑web` (WAR) | `AdminManagementService` | Tomcat 9 |
| **Mise à jour d’un mandat** | Gestion des mandats | `services‑baseadmin` | `MandatService` | PostgreSQL 9.6 |
| **Extraction JORF** | Alimentation automatique JORF | `article‑analyser` | `JORFIngestionService` | Elasticsearch 7 + PostgreSQL 9.6 |
| **Authentification** | Authentification Cerbère | `security‑filter` | `AuthCerbèreService` | Tomcat 9 (HTTPS) |
| **Job de notification** | Notification d’échéance | `scheduler‑batch` | `NotificationService` | Cron (Node 5) |
| **Recherche multi‑critères** | Recherche & Consultation | `services‑integration` | `SearchService` | PostgreSQL 9.6 + Elasticsearch 7 |

---  

## 10. Métamodel ArchiMate du projet  

*Spécialisation*  

| ArchiMate Element | Spécialisation | Raison |
|---|---|---|
| **Business Role** | `Gestionnaire de Mandat` (spécialisation de Business Role) | Rôle fonctionnel spécifique. |
| **Application Component** | `admin_ep‑web‑war` (spécialisation de Application Component) | Artefact déployable. |
| **Technology Node** | `TomcatClusterNode` (spécialisation de Node) | Représente le cluster HA. |
| **Data Object** | `MandatDTO` (spécialisation de Data Object) | DTO utilisé dans les APIs REST (future). |

---  

## 11. Standards et Conventions  

| Aspect | Convention |
|---|---|
| **Palette de couleurs** | Business = #FFFF00, Application = #99CCFF, Technology = #99FF99, Strategy = #FFCC99, Migration = #CCCCCC. |
| **Nommage** | `CamelCase` pour les éléments ArchiMate (ex : `AdminManagementService`). <br>`snake_case` pour les artefacts (ex : `admin_ep-web.war`). |
| **Niveau de détail** | - **Business** : processus de haut niveau. <br>- **Application** : composants et services majeurs. <br>- **Technology** : nœuds, systèmes d’exploitation, bases de données. |
| **Outils recommandés** | Archi (5.7+), Enterprise Architect, Visual Paradigm, ou tout outil supportant ArchiMate 3.2 + export Mermaid. |
| **Documentation** | - Fiches produit (wiki) → **admin_ep.wiki.md**. <br>- Scripts SQL versionnés dans `adminep-database`. <br>- Code source versionné sous GitLab (Maven multi‑module). |
| **Gestion des versions** | Maven `groupId: fr.gouv.e2.adminep`, `artifactId` = module, `version` = release. |
| **Sécurité** | - TLS ≥ 1.2, certificats internes. <br>- Auth Cerbère via LDAP/SSO. <br>- Logs centralisés (log4j2). |

---  

## 12. Conclusion  

Le **DAT admin_ep** décrit l’architecture actuelle (baseline 1.2.3) et la cible prévue pour 2026 (Q4).  

*Points clés* :  

* La couche métier est clairement découpée en services (gestion administrateurs, mandats, JORF, notification).  
* La couche applicative repose sur un monolithe Java 8 / Struts2, découpé en modules Maven clairement identifiables.  
* La couche technologique utilise Tomcat 9, PostgreSQL 9.6 et Elasticsearch 7, mais la roadmap prévoit la migration vers Tomcat 10, PostgreSQL 15 et la conteneurisation Docker/Kubernetes.  
* Les exigences de conformité (JORF), de sécurité (HTTPS, Cerbère) et de disponibilité sont intégrées dans les drivers, goals et contraintes.  

Le **plan de migration** (WP‑01 à WP‑06) assure une transition progressive, avec des work‑packages clairement balisés, la continuité de service garantie par le load‑balancer et le clustering, et la traçabilité assurée par le **matrix de traçabilité**.  

> **Prochaine étape** : Validation du **Roadmap Migration** avec les parties prenantes (MOA, MOE, exploitation) et mise en place du **pipeline CI/CD** (GitLab CI → Docker‑registry → Kubernetes).  

---  

*Fin du DAT*  