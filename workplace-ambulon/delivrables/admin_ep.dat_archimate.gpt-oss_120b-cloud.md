# 📂 Dossier d’Architecture Technique (DAT) – **admin_ep**  
*Version : 1.0 – 27 avril 2026*  

> **Objet** – Ce DAT décrit l’architecture du projet **admin_ep** (Administration des établissements publics) en conformité avec le cadre **ArchiMate 3.2** et la norme **ISO/IEC/IEEE 42010:2022**. Il couvre les couches **Métier**, **Application** et **Technologie**, ainsi que les points de vue stratégiques, de migration et de traçabilité.  

---  

## 1️⃣ Vue d’ensemble ArchiMate  

| Élément | Description |
|---|---|
| **Framework** | ArchiMate 3.2 – couches Métier, Application, Technologie, Stratégie, Implémentation & Migration. |
| **Préoccupations du projet** | Gestion des administrateurs et mandats d’établissements publics, import automatisé des données JORF, notification d’échéance, reporting statistique, authentification via Cerbère. |
| **Modèle de référence** | *Layered Viewpoint* (Métier ⇢ Application ⇢ Technologie) avec *Realization Overlay* et *Migration Viewpoint* pour la montée de version Tomcat 10 / PostgreSQL 15. |
| **Outils conseillés** | **Archi** (modélisation), **PlantUML** (diagrammes), **GitLab CI/CD**, **Maven**, **Docker**, **Kubernetes** (future). |

---  

## 2️⃣ Couche Métier (Business Layer)

### 2.1 Acteurs, rôles et collaborations  

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/ArchiMate-PlantUML/master
!include Archimate
' Business Actors
actor "Ministère MTES‑MCT" as MIN <<Business Actor>>
actor "SPES – Service de Pilotage" as SPES <<Business Actor>>
actor "DG de tutelle" as DG <<Business Actor>>
actor "Opérateurs (Gestionnaires)" as OP <<Business Actor>>

' Business Roles
rectangle "Chef de produit\n(Christian Arbogast)" as CP <<Business Role>>
rectangle "Développeurs CGI" as DEV <<Business Role>>
rectangle "Gestionnaire d’établissement" as GEST <<Business Role>>
rectangle "Utilisateur Cerbère" as USER <<Business Role>>

' Collaborations
MIN -[#0000FF]-> CP : définit les exigences
SPES -[#0000FF]-> CP : priorise les évolutions
DG -[#0000FF]-> OP : supervise la production
OP -[#0000FF]-> USER : utilise l’application

@enduml
```  

| **Business Actor** | **Rôle(s) Métier** | **Responsabilité(s)** |
|---|---|---|
| Ministère MTES‑MCT | **Maîtrise d’ouvrage** | Définir le périmètre fonctionnel, valider les livrables. |
| SPES (Service de Pilotage) | **Maîtrise d’œuvre** | Piloter les développements, prioriser les back‑logs. |
| DG de tutelle | **Supervision** | Assurer la conformité et la continuité de service. |
| Opérateurs (Gestionnaires) | **Gestionnaires** | Saisir, mettre à jour les administrateurs, valider les mandats. |
| Utilisateur Cerbère | **Usager** | Authentifier, consulter les données, recevoir les notifications. |

### 2.2 Services métier  

| **Business Service** | **Description** | **Processus(s) qui le réalisent** |
|---|---|---|
| **Gestion des administrateurs** | CRUD des administrateurs et leurs mandats. | Saisie manuelle, import JORF, validation. |
| **Recherche d’établissements** | Recherche full‑text sur les établissements, administrateurs, mandats. | Recherche via moteur JORF & index ElasticSearch. |
| **Notification d’échéance** | Envoi d’emails aux référents avant la fin d’un mandat. | Scheduler → Notification Service. |
| **Statistiques & reporting** | Tableaux de bord (nombre d’établissements, mandats actifs, etc.). | Extraction → Service de statistiques. |
| **Authentification Cerbère** | Gestion des habilitations via le SSO Cerbère. | Authentification Session Action. |
| **Import JORF** | Lecture automatisée des flux JORF et mise à jour des données. | Orchestration → JORF Extractor → Service d’intégration. |

### 2.3 Processus métier (extraits)  

```plantuml
@startuml
!include Archimate
' Business Processes
rectangle "Saisie manuelle d’un administrateur" as Saisie <<Business Process>>
rectangle "Import JORF (batch)" as Import <<Business Process>>
rectangle "Gestion des mandats" as Mandat <<Business Process>>
rectangle "Envoi de notification d’échéance" as Notif <<Business Process>>
rectangle "Consultation & reporting" as Report <<Business Process>>

' Flow
Saisie --> Mandat : crée/actualise
Import --> Mandat : enrichit
Mandat --> Notif : déclenche
Report --> Mandat : agrège
@enduml
```  

| Processus | Entrées | Sorties | Acteur principal |
|---|---|---|---|
| Saisie manuelle d’un administrateur | Formulaire UI | Enregistrement DB, événement `AdminCreated` | Gestionnaire |
| Import JORF (batch) | Flux JORF (XML/ZIP) | Mise à jour tables `ETABLISSEMENT`, `ADMIN` | Scheduler |
| Gestion des mandats | Données admin, établissements | Historique mandats, état `actif/suppléant` | Gestionnaire |
| Envoi de notification d’échéance | Mandats proches de fin | Emails de rappel | Scheduler |
| Consultation & reporting | Tables de référence | Dashboards, export CSV | Utilisateur |

### 2.4 Objets métier (extraits)  

| **Business Object** | **Description** |
|---|---|
| `Administrateur` | Personne physique, possède un ou plusieurs mandats. |
| `Mandat` | Relation entre un administrateur et un établissement (type : titulaire ou suppléant). |
| `Etablissement` | Entité publique sous tutelle du ministère. |
| `Charge` | Ministère ou direction responsable d’un établissement. |
| `College` | Groupe d’établissements (ex : “college de santé”). |
| `Direction` | Niveau hiérarchique entre ministère et établissements. |
| `ModeNomination` | Mode juridique de nomination (arrêté, décret). |

---  

## 3️⃣ Couche Application (Application Layer)

### 3.1 Composants applicatifs  

```plantuml
@startuml
!include Archimate
' Application Components
rectangle "Web UI (adminep‑web)" as UI <<Application Component>>
rectangle "Core Services\n(adminep‑services)" as CORE <<Application Component>>
rectangle "Integration Services\n(adminep‑integration)" as INTEG <<Application Component>>
rectangle "Search Service\n(ElasticSearch)" as SEARCH <<Application Component>>
rectangle "Scheduler / Jobs" as SCHED <<Application Component>>
rectangle "Security Manager\n(Cerbère)" as SEC <<Application Component>>
rectangle "Database\n(PostgreSQL)" as DB <<Application Component>>

UI -[#green]-> CORE : invoque
CORE -[#green]-> INTEG : délègue
INTEG -[#green]-> SEARCH : indexe / recherche
CORE -[#green]-> SCHED : planifie tâches
CORE -[#green]-> SEC : authentifie
CORE -[#green]-> DB : persiste / lit

@enduml
```  

| **Composant** | **Rôle** | **Principaux packages / classes** |
|---|---|---|
| **adminep‑web** | Interface Web (Struts2, JSP, Bootstrap) | `controller.*`, `boot.*`, `security.*` |
| **adminep‑services** | Logique métier (services, DAO) | `services.article.*`, `services.baseadmin.*`, `services.integration.*` |
| **adminep‑integration** | Connecteurs JORF, import CSV, synchronisation | `orchestra.*`, `util.articleanalyser.*` |
| **Search Service** | Indexation et recherche plein‑texte (ElasticSearch) | `ArticleSearchLoader`, `recherche*` |
| **Scheduler** | Jobs récurrents (cron) – notifications, imports | `SchedulerInitializer`, `ReindexArticlesByArtiIDTask` |
| **Security Manager** | Gestion des sessions Cerbère, droits | `BaseAdminUserSession`, `RightsHelper`, `Roles` |
| **Database** | Persistance PostgreSQL (schéma `integration`) | Tables `ADMIN`, `ETABLISSEMENT`, `CHARGE`, … |

### 3.2 Services applicatifs (extraits)  

| **Application Service** | **Responsabilité** | **Implémentation** |
|---|---|---|
| `AdminManagementService` | CRUD administrateurs & mandats | `AdministrateurServicesImpl` |
| `MandateService` | Gestion du cycle de vie des mandats | `MandatServicesImpl` |
| `SearchService` | Recherche full‑text sur administrateurs/établissements | `ArticleSearchLoader` |
| `JorfImportService` | Lecture & transformation des flux JORF | `RecupererJORFActivityEngine` |
| `NotificationService` | Envoi d’emails d’avertissement | `SchedulerInitializer` + `MailSender` (non‑décrit) |
| `AuthService` | Authentification via Cerbère | `SecurityManagerInitializer` |
| `StatisticsService` | Calcul de métriques & export | `StatistiquesAction` |

### 3.3 Données applicatives (Data Objects)  

| **Data Object** | **Table(s) source** | **Utilisation** |
|---|---|---|
| `AdminDO` | `ADMINISTRATEUR` (non listé mais présent) | Manipulé par `AdministrateurServices`. |
| `MandatDO` | `TYPE_MANDAT`, `ADMIN_MANDAT` | Gestion des mandats. |
| `EtablissementDO` | `ETABLISSEMENT` | Recherche & affichage. |
| `ChargeDO` | `CHARGE` | Utilisé par `ChargeServices`. |
| `CollegeDO` | `COLLEGE` | Filtrage par groupe. |
| `DirectionDO` | `DIRECTION` | Hiérarchie administrative. |
| `ModeNominationDO` | `MODE_NOMINATION` | Historique juridique. |
| `SearchIndex` | ElasticSearch | Accélère les requêtes de recherche. |

---  

## 4️⃣ Couche Technologie (Technology Layer)

### 4.1 Infrastructure (Nodes, Devices, System Software)  

```plantuml
@startuml
!include Archimate
' Nodes
node "Load‑Balancer (HAProxy)" as LB <<Node>>
node "App‑Server Cluster\n(Tomcat 9 → 10)" as APP <<Node>>
node "DB‑Server\n(PostgreSQL 9.6 → 15)" as DB <<Node>>
node "CI/CD Runner (GitLab)" as CI <<Node>>
node "ESXi / Docker Host" as HOST <<Node>>

' Devices
device "Network Switch" as SW <<Device>>
device "Storage (NFS)" as FS <<Device>>

' System Software
artifact "OS – Linux (RHEL 8)" as OS <<System Software>>
artifact "JVM – OpenJDK 8/11" as JVM <<System Software>>
artifact "Tomcat 9/10" as TOMCAT <<System Software>>
artifact "PostgreSQL 9.6/15" as PG <<System Software>>
artifact "ElasticSearch 7.x" as ES <<System Software>>
artifact "Docker Engine" as DOCKER <<System Software>>

' Relationships
LB -[#blue]-> APP : balance les requêtes HTTP
APP -[#blue]-> DB : JDBC
APP -[#blue]-> ES : REST API
APP -[#blue]-> DOCKER : déploie containers (future)
CI -[#blue]-> APP : déploiement CI/CD
HOST -[#blue]-> SW : connecte
SW -[#blue]-> LB
SW -[#blue]-> APP
SW -[#blue]-> DB
FS -[#blue]-> DB : stockage persistant

@enduml
```  

| **Élément** | **Version / Type** | **Rôle** |
|---|---|---|
| **Load‑Balancer** | HAProxy 2.6 | Répartition du trafic HTTP/HTTPS. |
| **App‑Server Cluster** | Tomcat 9.0.8 → 10.0.0 (migration) | Hébergement du WAR `adminep‑web`. |
| **DB‑Server** | PostgreSQL 9.6.11 → 15 (migration) | Persistance des schémas `integration`. |
| **ElasticSearch** | 7.10.x | Indexation des contenus JORF et recherche. |
| **CI/CD Runner** | GitLab 15.x | Build Maven, tests, packaging, déploiement. |
| **OS** | RHEL 8 (CentOS) | Plate‑forme système. |
| **JVM** | OpenJDK 8 (migration vers 11) | Exécution Java. |
| **Docker / Kubernetes** | En cours de containerisation (future) | Isolation & scalabilité. |
| **Network** | VLAN 10 (DMZ) | Sécurisation du périmètre. |
| **Storage** | NFS partagé | Persistance des bases de données. |

### 4.2 Services technologiques  

| **Technology Service** | **Description** |
|---|---|
| `HTTP(S) Service` | Exposé par le Load‑Balancer → Tomcat. |
| `JDBC Service` | Connexion DB PostgreSQL depuis Tomcat. |
| `REST Search Service` | API ElasticSearch (port 9200). |
| `Scheduler Service` | Cron via Spring Scheduler (Tomcat). |
| `Security Service` | SSO Cerbère (OAuth2/OpenID‑Connect). |
| `Logging Service` | Log4j2 → fichiers `baseadmin.log`. |
| `Monitoring Service` | Prometheus + Grafana (non‑décrit) pour supervision. |

### 4.3 Artifacts  

- **WAR** : `adminep-web‑1.2.3.war` (déployé dans Tomcat).  
- **SQL Scripts** : `scripts/init/*.sql`, `scripts/update/*.sql` (assembly zip).  
- **Dockerfile** (prévu) – conteneur Java + Tomcat.  
- **Helm Chart** (prévu) – déploiement Kubernetes.  

---  

## 5️⃣ Couche Stratégique (Strategy Layer) – *Optionnelle*  

| **Element** | **Détails** |
|---|---|
| **Goal** | *Assurer la transparence* des administrateurs publics et la conformité aux exigences légales (JORF). |
| **Outcome** | Accès en temps réel aux mandats, notification d’échéance, auditabilité. |
| **Capability** | Gestion des mandats, Import JORF, Notification, Reporting. |
| **Value Stream** | *Collecte → Traitement → Publication → Supervision*. |
| **Course of Action** | Migration vers micro‑services (Docker/K8s), mise à jour des versions (Tomcat 10, PostgreSQL 15). |
| **Stakeholder** | Ministère MTES‑MCT, SPES, DG de tutelle, Opérateurs. |
| **Driver** | Sécurité (DI‑CT), conformité juridique, besoins d’évolutivité. |
| **Requirement** | Support HTTPS, SSO Cerbère, disponibilité ≥ 99,5 %. |
| **Constraint** | Hébergement dans le datacenter **Paris La Défense** (Legacy LDF). |
| **Principle** | *“Security‑by‑Design”* – toutes les communications chiffrées, authentification forte. |

---  

## 6️⃣ Implémentation & Migration (Implementation & Migration Layer) – *Optionnel*  

| **Work Package** | **Livrable** | **Plateau** | **Gap** |
|---|---|---|---|
| **WP‑01** – *Migration Tomcat* | Tomcat 10‑compatible WAR | `adminep‑web‑1.2.3‑tomcat10.war` | Adaptation du `web.xml` (Servlet 4.0). |
| **WP‑02** – *Migration PostgreSQL* | Base PostgreSQL 15 | Scripts `upgrade_9.6_to_15.sql` | Vérification des extensions (plpgsql). |
| **WP‑03** – *Containerisation* | Docker image `adminep:1.2.3` | Docker Hub (private) | Création du Dockerfile, tests d’intégration. |
| **WP‑04** – *CI/CD Pipeline* | Pipeline GitLab (build‑test‑deploy) | `.gitlab-ci.yml` | Ajout des étapes de sécurité (SAST, DAST). |
| **WP‑05** – *Observabilité* | Prometheus + Grafana dashboards | Exporters (JMX, PostgreSQL) | Déploiement et alerting. |
| **WP‑06** – *Sécurisation HTTPS* | Certificats TLS via Let’s Encrypt / ACME | Load‑Balancer TLS termination | Renouvellement automatique. |

### 6.1 Roadmap (high‑level)

| **Sprint** | **Objectif** |
|---|---|
| **S‑01** | Analyse d’impact Tomcat 10, mise à jour du descripteur `web.xml`. |
| **S‑02** | Création du Dockerfile, build & test local. |
| **S‑03** | Migration de la base de données vers PostgreSQL 15 (scripts, tests). |
| **S‑04** | Implémentation du pipeline GitLab CI/CD (Maven, Sonar, SAST). |
| **S‑05** | Déploiement en pré‑production, validation fonctionnelle. |
| **S‑06** | Passage en production, monitoring & audit. |

---  

## 7️⃣ Aspects transverses (Cross‑layer Relationships)

| **Relation** | **Source** | **Target** | **Type (ArchiMate)** |
|---|---|---|---|
| `Notification Service` **realise** `Envoi de notification d’échéance` | Application Service | Business Process | **Realisation** |
| `Search Service` **réalise** `Recherche d’établissements` | Application Service | Business Service | **Realisation** |
| `Web UI` **sert** `Gestion des administrateurs` | Application Interface | Business Service | **Serving** |
| `Tomcat` **expose** `HTTP(S) Service` | Technology Component | Technology Service | **Realisation** |
| `JDBC Service` **utilise** `PostgreSQL` | Technology Service | Node (DB‑Server) | **Assignment** |
| `Security Manager` **contrôle** `Authentification Cerbère` | Application Component | Business Process (Authentification) | **Access** |
| `Scheduler` **déclenche** `Import JORF` | Application Component | Business Process | **Triggering** (extension) |
| `Load‑Balancer` **assure la disponibilité** `Web UI` | Technology Component | Application Component | **Serving** |
| `Docker Engine` **déploie** `adminep‑web` | Technology Component | Application Component | **Realisation** |

---  

## 8️⃣ Vues architecturales ArchiMate  

### 8.1 Vue Organisation (Organization Viewpoint)  

```plantuml
@startuml
!include Archimate
' Business Actors & Roles
actor "Ministère MTES‑MCT" as MIN <<Business Actor>>
actor "SPES" as SPES <<Business Actor>>
actor "DG de tutelle" as DG <<Business Actor>>
actor "Gestionnaires" as GEST <<Business Actor>>

' Business Roles
rectangle "Chef de produit" as CP <<Business Role>>
rectangle "Développeur CGI" as DEV <<Business Role>>
rectangle "Utilisateur Cerbère" as USER <<Business Role>>

' Assignments
MIN -[#green]-> CP
SPES -[#green]-> DEV
DG -[#green]-> GEST
GEST -[#green]-> USER

@enduml
```  

### 8.2 Vue Processus Métier (Business Process Viewpoint)  

```plantuml
@startuml
!include Archimate
' Business Processes
rectangle "Saisie manuelle d’un administrateur" as P1 <<Business Process>>
rectangle "Import JORF (batch)" as P2 <<Business Process>>
rectangle "Gestion des mandats" as P3 <<Business Process>>
rectangle "Envoi de notification d’échéance" as P4 <<Business Process>>
rectangle "Consultation & reporting" as P5 <<Business Process>>

' Flow
P1 --> P3 : crée/actualise
P2 --> P3 : enrichit
P3 --> P4 : déclenche
P5 --> P3 : agrège

@enduml
```  

### 8.3 Vue Application (Application Cooperation Viewpoint)  

```plantuml
@startuml
!include Archimate
' Application Components
rectangle "adminep‑web (WAR)" as WEB <<Application Component>>
rectangle "Core Services\n(adminep‑services)" as CORE <<Application Component>>
rectangle "Integration Services\n(adminep‑integration)" as INTEG <<Application Component>>
rectangle "ElasticSearch" as ES <<Application Component>>
rectangle "Scheduler" as SCHED <<Application Component>>
rectangle "Security Manager\n(Cerbère)" as SEC <<Application Component>>
rectangle "PostgreSQL\nDB" as DB <<Application Component>>

' Interactions
WEB -[#green]-> CORE : invoke
CORE -[#green]-> INTEG : delegate
INTEG -[#green]-> ES : index/search
CORE -[#green]-> SCHED : schedule jobs
CORE -[#green]-> SEC : authenticate
CORE -[#green]-> DB : read/write

@enduml
```  

### 8.4 Vue Infrastructure (Infrastructure Viewpoint)  

```plantuml
@startuml
!include Archimate
node "Load‑Balancer (HAProxy)" as LB <<Node>>
node "App‑Server Cluster\n(Tomcat 10)" as APP <<Node>>
node "DB‑Server\n(PostgreSQL 15)" as DB <<Node>>
node "ElasticSearch Cluster" as ES <<Node>>
node "CI/CD Runner (GitLab)" as CI <<Node>>

' Connections
LB -[#blue]-> APP : HTTP/HTTPS
APP -[#blue]-> DB : JDBC
APP -[#blue]-> ES : REST
CI -[#blue]-> APP : Deploy

@enduml
```  

### 8.5 Vue Réalisation (Realization Viewpoint)  

```plantuml
@startuml
!include Archimate
' Business Services
rectangle "Gestion des administrateurs" as BS1 <<Business Service>>
rectangle "Recherche d’établissements" as BS2 <<Business Service>>
rectangle "Notification d’échéance" as BS3 <<Business Service>>

' Application Services
rectangle "AdminManagementService" as AS1 <<Application Service>>
rectangle "SearchService" as AS2 <<Application Service>>
rectangle "NotificationService" as AS3 <<Application Service>>

' Technology Services
rectangle "HTTP(S) Service" as TS1 <<Technology Service>>
rectangle "JDBC Service" as TS2 <<Technology Service>>
rectangle "REST Search Service" as TS3 <<Technology Service>>

' Realisations
BS1 -[#darkgreen]-> AS1 : realise
BS2 -[#darkgreen]-> AS2 : realise
BS3 -[#darkgreen]-> AS3 : realise
AS1 -[#darkgreen]-> TS1 : realise
AS2 -[#darkgreen]-> TS3 : realise
AS3 -[#darkgreen]-> TS2 : utilise

@enduml
```  

---  

## 9️⃣ Vue de traçabilité complète  

| **Élément Métier** | **Service métier** | **Composant appli** | **Service appli** | **Service technologique** |
|---|---|---|---|---|
| `Saisie manuelle d’un administrateur` | Gestion des administrateurs | `adminep‑web` (Struts2) | `AdminManagementService` | `HTTP(S) Service` (Tomcat) |
| `Import JORF (batch)` | Import JORF | `adminep‑integration` | `JorfImportService` | `Scheduler Service` (cron) |
| `Gestion des mandats` | Gestion des mandats | `adminep‑services` | `MandateService` | `JDBC Service` (PostgreSQL) |
| `Envoi de notification d’échéance` | Notification d’échéance | `Scheduler` + `NotificationService` | `NotificationService` | `SMTP Service` (external) |
| `Recherche d’établissements` | Recherche d’établissements | `adminep‑services` + `ElasticSearch` | `SearchService` | `REST Search Service` (ElasticSearch) |
| `Authentification Cerbère` | Authentification | `Security Manager` | `AuthService` | `HTTPS Service` (TLS) |

---  

## 🔧 Métamodele ArchiMate du projet  

| **Type personnalisé** | **Spécialisation** | **Usage** |
|---|---|---|
| `« Database »` | `Data Object` | Représente les tables du schéma `integration`. |
| `« Scheduler »` | `Technology Function` | Gestion des jobs récurrents. |
| `« JORF »` | `Business Object` | Source d’alimentation externe. |
| `« Cerbère »` | `Technology Service` | Service SSO. |
| `« Docker »` | `Technology Component` | Conteneur d’exécution (future). |

---  

## 📏 Standards et conventions  

| **Aspect** | **Convention** |
|---|---|
| **Palette de couleurs** | Métier : `#FFFF00` (jaune) ; Application : `#99CCFF` (bleu) ; Technologie : `#99FF99` (vert) ; Stratégie : `#FFCC99` (orange) ; Implémentation : `#CCCCCC` (gris). |
| **Nomination** | `CamelCase` pour les classes Java, `snake_case` pour les tables SQL, `kebab-case` pour les artefacts Docker. |
| **Niveaux de détail** | Diagrammes de haut niveau (couche) – 1 page ; diagrammes détaillés (processus, composants) – 1 page chacun. |
| **Documentation** | Chaque composant possède un `README.md` et un `javadoc` (Java). |
| **Gestion des versions** | Maven `pom.xml` – version `1.2.3`. |
| **Sécurité** | Tous les flux externes via TLS 1.2+, authentification via Cerbère, secrets gérés par **GitLab CI variables**. |
| **Déploiement** | `helm chart` (future) – version `0.1.0`. |

---  

## 📚 Glossaire ArchiMate  

| **Terme** | **Définition (ArchiMate)** |
|---|---|
| **Business Actor** | Entité organisationnelle qui interagit avec le système (ex : Ministère MTES‑MCT). |
| **Business Role** | Fonction ou responsabilité attribuée à un acteur (ex : Chef de produit). |
| **Business Service** | Service offert aux parties prenantes (ex : Gestion des administrateurs). |
| **Business Process** | Suite d’activités coordonnées (ex : Import JORF). |
| **Application Component** | Unité encapsulée de code exécutable (ex : `adminep‑web`). |
| **Application Service** | Fonctionnalité exposée par un composant (ex : `SearchService`). |
| **Data Object** | Information manipulée (ex : `AdminDO`). |
| **Node** | Ressource d’exécution (ex : serveur Tomcat). |
| **Technology Service** | Service offert par l’infrastructure (ex : HTTP(S) Service). |
| **Artifact** | Produit tangible (ex : WAR, SQL script). |
| **Realisation** | Relation « réalise » entre un élément de niveau supérieur et un élément de niveau inférieur. |
| **Assignment** | Relation d’affectation d’un rôle ou d’un service à un acteur ou un composant. |
| **Serving** | Relation « sert » entre un service et un acteur/une fonction qui le consomme. |
| **Influence** | Relation de dépendance ou d’impact (ex : driver → goal). |

---  

## 📎 Références  

* **ArchiMate 3.2 Specification** – The Open Group, 2022.  
* **ISO/IEC/IEEE 42010:2022** – Architecture description.  
* **TOGAF 9.2** – Architecture Development Method (ADM).  
* **admin_ep.wiki.md** – Documentation produit (section “Fiche‑Produit”).  
* **admin_ep.wikisi.md** – Données de contexte (acteurs, hébergement, version).  
* **admin_ep.code.filtered.md** – Arborescence du code source et scripts SQL.  

---  

### 📌 Conclusion  

Le DAT ci‑dessus fournit une vision complète et cohérente de l’architecture **admin_ep** selon le métamodèle **ArchiMate**. Il met en évidence :

* La **cohérence** entre les exigences métier (gestion des administrateurs, notification) et les services applicatifs (CRUD, import JORF, recherche).  
* La **traçabilité** des éléments métier jusqu’aux artefacts techniques (WAR, scripts SQL, conteneurs).  
* Les **gaps** à combler pour la migration vers les versions récentes (Tomcat 10, PostgreSQL 15) et la **containerisation** future.  

Ce document constitue la base de communication entre les parties prenantes (MOA, MOE, exploitation) et le socle de suivi des évolutions architecturales du système.  

---  

*Fin du Dossier d’Architecture Technique*  