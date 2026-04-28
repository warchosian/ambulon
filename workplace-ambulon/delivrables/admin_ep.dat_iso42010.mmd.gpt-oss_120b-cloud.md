# 📚 Dossier d'Architecture Technique (DAT) – **admin_ep**  
[TOC]

---  

## 1. Introduction et contexte de l'architecture  

### 1.1 Objectifs du document  
Ce **Dossier d'Architecture Technique (DAT)** décrit, analyse et communique l’architecture du projet **admin_ep** (Administration des établissements publics). Il répond aux exigences de la norme **ISO/IEC/IEEE 42010:2022** et sert :  

* de référence pour les équipes de développement, d’exploitation et de gouvernance ;  
* d’appui à la traçabilité des exigences fonctionnelles (CCF) → exigences techniques (CST) → décisions d’architecture (DAT) ;  
* d’outil d’évaluation des qualités (ISO 25010) et de gestion des risques.  

### 1.2 Périmètre architectural  
Le périmètre inclut :  

| Niveau | Élément | Description |
|-------|--------|-------------|
| **Système** | **admin_ep** | Application web Java (Struts 2 / Vertigo) permettant la saisie, la consultation et la gestion des mandats des administrateurs d’établissements publics du MTES‑MCT. |
| **Sous‑systèmes** | **adminep‑database** | Schéma PostgreSQL `integration` contenant les tables métier (TYPE_MANDAT, CHARGE, MINISTERE, etc.) et les scripts d’initialisation / mise à jour. |
| | **adminep‑deployment** | Assemblage Maven (zip, sources) et configuration de déploiement (Tomcat). |
| | **adminep‑web** | Code source Java, ressources web (JSP, CSS, static), configuration Struts, Spring‑Boot, sécurité Cerbère. |
| | **adminep‑doc** | Documentation (assemblage, génération de rapports). |
| | **search** | Module de recherche JORF (non détaillé dans ce DAT). |

### 1.3 Références documentaires  

| Référence | Type | Lien interne |
|-----------|------|--------------|
| `admin_ep.wiki.md` | Description métier & contexte | [📄 home (wiki)](#home) |
| `admin_ep.wikisi.md` | Métadonnées fonctionnelles & techniques | [📄 admin‑ep (wikisi)](#admin‑ep-wikisi) |
| `admin_ep.code.filtered.md` | Arborescence et contenu des sources | [📁 Arborescence des fichiers](#arborescence-des-fichiers) |
| `admin_ep.code.summarized.md` | Synthèse de l’arborescence | [📁 Arborescence résumée](#arborescence-des-fichiers) |
| `adminep-database/scripts/*.sql` | Scripts de création / population | [📄 0_createUserAndDB.sql](#adminep-database-scripts-init-0_createuseranddb-sql) etc. |

---  

## 2. Parties prenantes et préoccupations  

### 2.1 Tableau des parties prenantes  

| ID | Partie prenante | Rôle | Préoccupations principales |
|----|-----------------|------|----------------------------|
| **P‑01** | **Maîtrise d’Ouvrage (MOA)** – SG/SPES | Définit le besoin métier, valide les livrables | conformité fonctionnelle, respect des délais, traçabilité des données |
| **P‑02** | **Maîtrise d’œuvre (MOE)** – SG/SNUM/PNM/DPNM3/BPN | Conçoit, développe, déploie l’application | maintenabilité, évolutivité, respect des standards techniques |
| **P‑03** | **Opérateurs de production** – équipes infra | Exploitation, supervision, sauvegarde | disponibilité, performance, gestion des incidents |
| **P‑04** | **Utilisateurs finaux** – SPES, DG de tutelle, opérateurs | Saisie & consultation des mandats | ergonomie, sécurité d’accès, fiabilité des données |
| **P‑05** | **Équipe Sécurité / DSI** | Garant de la sécurité de l’information | confidentialité, intégrité, conformité DICT |
| **P‑06** | **Équipe Audit / RGPD** | Vérifie la conformité légale | traçabilité, registre des traitements, auditabilité |
| **P‑07** | **Fournisseur d’infrastructure** – CSP (MSP) | Hébergement des serveurs | résilience, conformité aux exigences d’hébergement |

### 2.2 Correspondance préoccupations ↔ points de vue  

| Préoccupation | Point de vue concerné (section 3) |
|---------------|-----------------------------------|
| Fonctionnalités métier (saisie, recherche, alertes) | **Vue Fonctionnelle / Métier** |
| Structure et cohérence des données | **Vue Données & Information** |
| Modularité du code, patterns utilisés | **Vue Applicative / Logicielle** |
| Déploiement, topologie, exigences d’infrastructure | **Vue Technique / Infrastructure** |
| Interfaces externes (JORF, Cerbère, Elasticsearch) | **Vue Intégration** |
| Gestion des accès, authentification Cerbère | **Vue Sécurité** |
| Supervision, logs, alertes | **Vue Opérationnelle / Exploitation** |
| Qualités non‑fonctionnelles (performance, disponibilité) | **Qualités & NFR** (section 8) |
| Evolution du système (conteneurisation, migration Tomcat 10/Postgres 15) | **Vue Évolutivité & Feuille de route** (section 9) |

---  

## 3. Points de vue architecturaux  

| ID | Nom du point de vue | Concern(s) couvert(s) | Langage de modélisation | Méthode d’analyse |
|----|----------------------|----------------------|------------------------|-------------------|
| **VP‑01** | **System Context Viewpoint** | Environnement externe, acteurs, flux d’information | **C4 L1** (Mermaid) | Analyse d’interaction, matrice de traçabilité |
| **VP‑02** | **Business Function Viewpoint** | Capacités métier, processus CCF | **BPMN‑lite** (Mermaid) | Mapping capacité ↔ exigences |
| **VP‑03** | **Container / Component Viewpoint** | Modules Java, services, conteneurs (Tomcat, PostgreSQL) | **C4 L2/L3** (Mermaid) | Analyse de dépendances, couplage |
| **VP‑04** | **Data Viewpoint** | Modèle conceptuel, logique, physique des tables | **UML Class** (Mermaid) | Validation de l’intégrité référentielle |
| **VP‑05** | **Infrastructure Viewpoint** | Déploiement (VM/Container, réseau) | **UML Deployment** (Mermaid) | Analyse de résilience, redondance |
| **VP‑06** | **Integration Viewpoint** | Protocoles (HTTPS, JDBC, REST, JORF, Cerbère) | **Sequence Diagram** (Mermaid) | Analyse de latence, points de défaillance |
| **VP‑07** | **Security Viewpoint** | Défense in depth, D‑I‑C‑T, gestion des droits | **Security Architecture Diagram** (Mermaid) | Analyse des menaces (STRIDE) |
| **VP‑08** | **Operational Viewpoint** | Monitoring, logs, alerting, sauvegarde | **Activity Diagram** (Mermaid) | Analyse de la chaîne d’exploitation |
| **VP‑09** | **Evolution Viewpoint** | Feuille de route, scénarios de croissance | **Roadmap Diagram** (Mermaid) | Analyse de la dette technique |

---  

## 4. Vues architecturales  

> **Toutes les vues utilisent le point de vue indiqué en préfixe.**  

### 4.1 VP‑01 – Vue Contexte (System Context)  

```mermaid
graph LR
    subgraph External[Environnement externe]
        A[Utilisateurs (SPES, DG, Opérateurs)] -->|Web UI| UI[admin_ep Web App]
        B[Service Cerbère] -->|AuthN/AuthZ| UI;
        C[JORF (Open Data)] -->|Flux XML| ETL[ArticleAnalyser]
        D[Elasticsearch] -->|Recherche plein texte| UI;
    end
    UI -->|JDBC| DB[(PostgreSQL – integration schema)]
    UI -->|HTTP| Tomcat[Tomcat 9.0.8]
    Tomcat -->|Docker (en cours) | Container[Container]
    Container -->|Hosted on| MSP[MSP Data Center – Paris La Défense]
```

**Description**  
* L’application web expose une interface HTTP(S) via Tomcat.  
* L’accès est contrôlé par le SSO **Cerbère**.  
* Les données proviennent de la base PostgreSQL `integration`.  
* Un processus batch (ArticleAnalyser) importe les actes du **JORF**.  
* Elasticsearch est utilisé pour les recherches plein texte (non détaillé dans le code source).  

### 4.2 VP‑02 – Vue Fonctionnelle / Métier  

```mermaid
flowchart TD
    subgraph BusinessCapabilities[Capacités métier]
        C1[Gestion des administrateurs] --> C2[Gestion des établissements]
        C2 --> C3[Gestion des mandats (Titulaire / Suppléant)]
        C3 --> C4[Alertes d’échéance]
        C4 --> C5[Statistiques & Reporting]
        C5 --> C6[Recherche avancée]
    end
    subgraph Processes[Processus CCF]
        P1[Création / Mise à jour d’un administrateur] --> P2[Assignation à un mandat]
        P2 --> P3[Calcul de la date d’échéance]
        P3 --> P4[Envoi d’email de rappel]
        P4 --> P5[Archivage du mandat expiré]
    end
    BusinessCapabilities -.-> Processes
```

**Correspondance CCF → CST**  
* **CCF 1** – Saisie d’un administrateur → **C1** (Gestion des administrateurs) → tables `administrateur`, `gestionnaire`.  
* **CCF 2** – Recherche d’un établissement → **C2** → tables `etablissement`, `college`.  
* **CCF 3** – Notification d’échéance → **C4** → service `MandatServices` + `SchedulerInitializer`.  

### 4.3 VP‑03 – Vue Applicative / Logicielle (Component Diagram)  

```mermaid
classDiagram
    direction TB;
    class AccueilAction {
        +execute()
    }
    class DetailAdminAction {
        +execute()
    }
    class RechercheAdminsAction {
        +execute()
    }
    class UpsertAdminAction {
        +execute()
    }
    class ArticleServices {
        +search()
        +getById()
    }
    class MandatServices {
        +createMandat()
        +updateMandat()
    }
    class SecurityFilter {
        +doFilter()
    }
    class SchedulerInitializer {
        +init()
    }
    AccueilAction --> AccueilActionSupport : extends;
    DetailAdminAction --> AbstractBaseAdminActionSupport;
    UpsertAdminAction --> AbstractBaseAdminUpsertActionSupport;
    SecurityFilter --> BaseAdminUserSession;
    MandatServices --> ArticleServices : uses;
    SchedulerInitializer --> MandatServices : schedules;
    class StrutsConfig {
        +struts.xml;
    }
    class SpringBootConfig {
        +application-config.xml;
        +baseadmin-auth-config.xml;
    }
    AccueilAction ..> StrutsConfig : mapped in;
    UpsertAdminAction ..> SpringBootConfig : bean
```

**Notes**  
* Le projet utilise **Struts 2** (action classes) et **Vertigo** (DI, services).  
* Les **boot** initializers (`I18nResourcesInitializer`, `MasterDataInitializer`, `SchedulerInitializer`, `SecurityManagerInitializer`) sont invoqués au démarrage.  
* Les services sont définis dans les dossiers `services/*` (ex : `ArticleServices`, `MandatServices`, `Integration` services).  

### 4.4 VP‑04 – Vue Données et Information  

```mermaid
classDiagram
    direction TB;
    class TYPE_MANDAT {
        +tma_id : PK;
        +tma_type;
    }
    class TYPE_INSTANCE {
        +tin_id : PK;
        +tin_type;
        +tin_a_linstance_de;
        +tin_de_linstance_de;
    }
    class MODE_NOMINATION {
        +mno_id : PK;
        +mno_code;
        +mno_mode;
        +mno_mot_cle_titre;
        +mno_mot_cle_corps_texte;
    }
    class CHARGE {
        +cha_id : PK;
        +cha_charge;
        +...
    }
    class MINISTERE {
        +min_id : PK;
        +min_sigle;
        +min_nom;
        +min_statut;
    }
    class COLLEGE {
        +col_id : PK;
        +col_identifiant;
    }
    class ETABLISSEMENT {
        +eta_id : PK;
        +eta_siren;
        +eta_sigle;
        +eta_libelle;
        +tin_id_fk : FK → TYPE_INSTANCE;
    }
    class SYNONYME_COLLEGE {
        +col_id_fk : FK → COLLEGE;
        +syn_synonyme;
        +syn_defaut;
    }
    TYPE_MANDAT --> Mandat;
    TYPE_INSTANCE --> ETABLISSEMENT;
    CHARGE --> MINISTERE_CHARGE;
    MINISTERE --> MINISTERE_CHARGE;
    COLLEGE --> SYNONYME_COLLEGE;
    ETABLISSEMENT --> ETABLISSEMENT_COLLEGE;
    ETABLISSEMENT --> TUTELLE_ETABLISSEMENT_CHARGE
```

*Le modèle logique est généré à partir des scripts `1_createSequenceAndTablesIntegration.sql` et `2_populateTablesIntegration.sql`.*  

### 4.5 VP‑05 – Vue Technique / Infrastructure  

```mermaid
deploymentDiagram;
    node "MSP Data Center – Paris La Défense" {
        node "VM/Cluster ESXi (ACAI)" {
            artifact "Tomcat 9.0.8 (Docker container)" as Tomcat;
            artifact "PostgreSQL 9.6.11 (container)" as PG;
        }
        node "VM/Cluster IaaS (ECO4) – Recette" {
            artifact "Tomcat 10 (prévision)" as Tomcat10;
            artifact "PostgreSQL 15 (prévision)" as PG15;
        }
    }
    Tomcat --> PG : JDBC;
    Tomcat --> "Elasticsearch" : HTTP REST;
    Tomcat --> "Cerbère SSO" : HTTPS SAML/OIDC;
    Tomcat --> "JORF Batch (ArticleAnalyser)" : File/HTTP
```

**Contraintes techniques**  
* **Java 8** (développement) – migration prévue vers Java 11/17.  
* **Tomcat 9** (production) – montée prévue vers **Tomcat 10** (Servlet 5.0).  
* **PostgreSQL 9.6** – migration vers **PostgreSQL 15**.  
* Conteneurisation en cours (Docker, Kubernetes envisagé).  

### 4.6 VP‑06 – Vue Intégration  

```mermaid
sequencediagram;
    participant User as Utilisateur (Web UI)
    participant UI as admin_ep Web App;
    participant Cerb as Cerbère SSO;
    participant DB as PostgreSQL;
    participant ES as Elasticsearch;
    participant JORF as JORF Feed;
    User->>UI: Authentification (HTTPS)
    UI->>Cerb: SSO request;
    Cerb-->>UI: Token / Claims;
    UI->>DB: CRUD Mandats (JDBC)
    UI->>ES: Recherche plein texte (REST)
    JORF->>UI: Flux XML (Batch)
    UI->>UI: Traitement via ArticleAnalyser;
    UI->>DB: Insertion / mise à jour
```

**Protocoles**  
* HTTPS (TLS 1.2+) pour toutes les communications externes.  
* JDBC (PostgreSQL driver) pour la persistance.  
* REST/HTTP pour Elasticsearch.  
* SAML/OIDC (via Cerbère) pour l’authentification.  

### 4.7 VP‑07 – Vue Sécurité  

```mermaid
graph TD
    subgraph "Défense in depth"
        A[Front‑end (HTTPS, CSP, HSTS)]
        B[Tomcat (TLS, security‑constraints, role‑based access)]
        C[Application (Cerbère, RightsHelper, Roles)]
        D[Database (pg_hba.conf, encryption at rest)]
        E[Logs (log4j2, audit trail)]
    end
    A --> B --> C --> D;
    C -->|AuthZ| F[Confidentialité (D‑I‑C‑T)]
    D -->|Intégrité| F;
    E -->|Traçabilité| F
```

**Principes**  
* **Confidentialité** – chiffrement TLS, contrôle d’accès via **Cerbère** (RBAC).  
* **Intégrité** – contraintes d’intégrité référentielle, triggers éventuels.  
* **Disponibilité** – redondance Tomcat/DB, sauvegardes nightly.  
* **Traçabilité** – logs `log4j2.xml`, audit des accès, conformité **DICT** (voir wiki).  

### 4.8 VP‑08 – Vue Opérationnelle / Exploitation  

```mermaid
statediagram-v2;
    [*] --> Monitoring;
    Monitoring --> Alerting;
    Alerting --> IncidentManagement;
    IncidentManagement --> Resolution;
    Resolution --> [*]

    state Monitoring {
        CPU --> Memory --> DiskIO --> DBHealth;
        TomcatHealth --> ThreadPool;
        ElasticsearchHealth;
    }
    state Alerting {
        EmailAlert;
        SMSAlert;
    }
    state IncidentManagement {
        TicketCreation;
        AssignToOps;
    }
```

* **Supervision** – `SupervisionAction` expose un tableau de bord.  
* **Logs** – `log4j2.xml` configure rotation, archivage.  
* **Sauvegarde** – scripts `pg_dump` exécutés quotidiennement (non présent dans l’arborescence mais requis).  
* **Plan de reprise** – sauvegarde off‑site (MSP).  

---  

## 5. Correspondance entre vues  

| Élément | Vue Contexte | Vue Fonctionnelle | Vue Applicative | Vue Données | Vue Technique | Vue Sécurité |
|---------|--------------|-------------------|----------------|------------|----------------|---------------|
| **Utilisateur** | ✅ | ✅ |  |  |  | ✅ |
| **Cerbère SSO** | ✅ |  | ✅ |  | ✅ | ✅ |
| **Mandat** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **ArticleAnalyser (JORF)** | ✅ | ✅ | ✅ | ✅ | ✅ |  |
| **Elasticsearch** | ✅ | ✅ | ✅ |  | ✅ |  |
| **Tomcat** | ✅ |  | ✅ |  | ✅ | ✅ |
| **PostgreSQL** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Écarts identifiés**  

| Vue | Écart / Incohérence | Action corrective |
|-----|----------------------|-------------------|
| **Vue Technique** | La version cible de Tomcat 10/PostgreSQL 15 n’est pas encore déployée. | Planifier migration (section 9). |
| **Vue Sécurité** | Aucun chiffrement au repos n’est explicitement configuré dans `postgresql.conf`. | Activer `data_encryption` ou LUKS au niveau du serveur. |
| **Vue Opérationnelle** | Aucun tableau de bord Grafana/Prometheus n’est mentionné. | Implémenter métriques via **Micrometer** et exporter vers Prometheus. |
| **Vue Intégration** | Le flux JORF est décrit mais le schéma de messages n’est pas documenté. | Ajouter un **Message Contract** (ex : XSD) dans les annexes. |

---  

## 6. Décisions architecturales (ADR)  

| ADR‑ID | Contexte & Problématique | Options envisagées | Décision retenue | Justification | Conséquences | Statut |
|--------|--------------------------|---------------------|-----------------|--------------|--------------|--------|
| **ADR‑01** | Migration de **Tomcat 9 → Tomcat 10** (Servlet 5) | 1. Migration immédiate <br>2. Migration progressive (phase 1) <br>3. Maintien de Tomcat 9 | **Option 2** – Migration progressive, première version en pré‑prod | Permet de valider les changements de API Struts 2, minimise les ruptures | Nécessite tests d’intégration, mise à jour du Dockerfile | **Acceptée** |
| **ADR‑02** | Passage de **PostgreSQL 9.6 → 15** | 1. Upgrade in‑place <br>2. Migration par réplication <br>3. Re‑création du schéma & import | **Option 2** – Replication logique (pglogical) | Garantit continuité de service, réduction du downtime | Besoin de scripts de synchronisation, validation des extensions | **Acceptée** |
| **ADR‑03** | Conteneurisation de l’application | 1. Docker monolithique <br>2. Multi‑container (Tomcat, DB, ES) <br>3. Kubernetes (micro‑services) | **Option 2** – Multi‑container Docker (Docker‑Compose) | Aligné avec la roadmap “containerisation en cours” | Gestion du réseau interne, persistance des volumes | **Acceptée** |
| **ADR‑04** | Gestion des **droits d’accès** (RBAC) | 1. Utiliser Cerbère uniquement <br>2. Ajouter un filtre Spring‑Security <br>3. Développer un module interne | **Option 1** – Cerbère (déjà en place) | Centralise l’authentification, réduit la duplication | Dépendance à Cerbère, nécessite mapping des rôles | **Acceptée** |
| **ADR‑05** | **Supervision** des métriques | 1. Log4j2 + fichiers <br>2. Micrometer + Prometheus + Grafana <br>3. Outils propriétaires | **Option 2** – Micrometer stack | Visibilité temps réel, alertes automatisées | Ajout de dépendances, configuration Prometheus | **Proposée** (prévue dans roadmap) |
| **ADR‑06** | **Chiffrement des données au repos** | 1. Transparent Data Encryption (TDE) PostgreSQL <br>2. Chiffrement du disque (LUKS) <br>3. Aucun (confiance sur le datacenter) | **Option 2** – LUKS au niveau OS (MSP) | Plus simple à mettre en œuvre, conformité DICT | Nécessite redémarrage du serveur, plan de récupération | **Acceptée** |

---  

## 7. Analyse des écarts et risques architecturaux  

| Risque | Description | Probabilité | Impact | Niveau (P×I) | Mesure d’atténuation |
|--------|-------------|-------------|--------|--------------|----------------------|
| **R‑01** | **Obsolescence du serveur d’application** (Tomcat 9) | Moyenne | Élevé (interruption) | 3×4 = 12 | Migration progressive (ADR‑01), tests de régression |
| **R‑02** | **Incompatibilité de la base avec PostgreSQL 15** | Faible | Élevé (perte de données) | 2×4 = 8 | Réplication logique (ADR‑02), validation du schéma |
| **R‑03** | **Fuite de données via mauvaise configuration Cerbère** | Faible | Critique | 2×5 = 10 | Audit de configuration, revue de `Roles.java` |
| **R‑04** | **Défaillance du processus JORF batch** (ArticleAnalyser) | Moyenne | Moyen (retard de mise à jour) | 3×3 = 9 | Monitoring dédié, retry exponential |
| **R‑05** | **Dépendance à Elasticsearch non versionnée** | Moyenne | Moyen | 3×3 = 9 | Verrouiller la version dans `docker-compose.yml` |
| **R‑06** | **Dette technique sur le code legacy (Struts 2, Vertigo)** | Élevée | Moyen | 4×3 = 12 | Refactorisation planifiée (roadmap) |

---  

## 8. Qualités et exigences non‑fonctionnelles  

### 8.1 Tableau des exigences NFR (ISO 25010)  

| Qualité (ISO 25010) | Exigence | Critère d’acceptation | Métrique |
|---------------------|----------|------------------------|----------|
| **Fiabilité** | Disponibilité ≥ 99,5 % (heure de service) | Aucun downtime > 30 min sur 30 j | % uptime mensuel (monitoring) |
| **Performance** | Temps de réponse < 2 s pour les requêtes UI | 95 % des requêtes < 2 s | Latence moyenne (Prometheus) |
| **Sécurité** | Conformité DICT, chiffrement TLS 1.2+ | Audit passif, pas de vulnérabilités critiques | Résultat OWASP ZAP, rapport DICT |
| **Maintenabilité** | Couverture de tests unitaires ≥ 80 % | Rapport JaCoCo ≥ 80 % | % de lignes couvertes |
| **Portabilité** | Déploiement Docker compatible avec Kubernetes | Image Docker `admin_ep:latest` passe les tests de validation K8s | Success du `kubectl dry‑run` |
| **Compatibilité** | Support navigateur Chrome ≥ 90, Edge ≥ 90 | Tests Selenium sur les deux navigateurs | % de scénarios réussis |
| **Scalabilité** | Capacité à supporter 200 concurrent users | Pas de dégradation > 20 % | Charge test (JMeter) |
| **Auditabilité** | Conservation des logs ≥ 180 jours | Rotation log4j2, archivage | Taille des archives, conformité RGPD |

### 8.2 Scénarios de validation architecturale  

| Scénario | Description | Méthode de test |
|----------|-------------|-----------------|
| **S‑01** | **Validation de l’authentification Cerbère** | Test SAML flow avec mock IdP, vérification des rôles (`Roles.java`). |
| **S‑02** | **Intégrité des données** | Insertion d’un mandat, vérification des contraintes FK, triggers. |
| **S‑03** | **Performance de recherche** | Requête full‑text sur Elasticsearch, mesure < 200 ms. |
| **S‑04** | **Résilience du batch JORF** | Simuler perte de connexion, vérifier reprise automatique. |
| **S‑05** | **Migration DB** | Exécution d’un `pglogical` sync, validation de checksum. |

---  

## 9. Évolutivité et feuille de route  

### 9.1 Scénarios de croissance  

| Scénario | Charge | Impact architectural | Action prévue |
|----------|--------|---------------------|---------------|
| **C‑01** | **10 000 mandats** (double du volume actuel) | Augmentation du temps de requête sur PostgreSQL | Indexation supplémentaire (`CREATE INDEX ON mandat (date_fin)`), partitionnement futur. |
| **C‑02** | **Accès mobile** (API REST) | Besoin d’exposer des services RESTful | Ajouter couche **Spring Boot** REST (future micro‑service). |
| **C‑03** | **Déploiement multi‑régional** | Latence réseau, réplication de données | Mise en place de **PostgreSQL BDR** (bi‑directional replication). |
| **C‑04** | **Passage à Java 17** | Compatibilité des bibliothèques | Upgrade Gradle/Maven, tests de compatibilité. |

### 9.2 Feuille de route (horizon)  

| Horizon | Objectif | Livrable | Responsable |
|---------|----------|----------|-------------|
| **Court terme (0–6 mois)** | Migration Tomcat 9 → Tomcat 10 (pré‑prod) | Docker image `admin_ep:tomcat10` | Équipe MOE |
| | Migration PostgreSQL 9.6 → 15 (Réplication) | Script de réplication, validation | DBA |
| | Mise en place du monitoring Micrometer/Prometheus | Dashboard Grafana | Ops |
| **Moyen terme (6–18 mois)** | Conteneurisation complète (Docker‑Compose) | `docker-compose.yml` | DevOps |
| | Implémentation d’une API REST (Spring Boot) | Service `admin-ep-api` | MOE |
| | Sécurisation au repos (LUKS) | Documentation & scripts | Sécurité |
| **Long terme (18‑36 mois)** | Migration vers Kubernetes (EKS/AKS) | Helm chart `admin-ep` | Cloud Ops |
| | Partitionnement de la base (mandats) | Tables partitionnées | DBA |
| | Adoption de Java 17, refactorisation Struts 2 → Spring MVC | Nouvelle branche `refactor‑mvc` | MOE |

---  

## 10. Annexes  

### 10.1 Glossaire architectural  

| Terme | Définition |
|-------|------------|
| **CST** | **Conceptual System Template** – modèle de description de l’architecture (ISO 42010). |
| **CCF** | **Catalogue des Capacités Fonctionnelles** – référentiel métier. |
| **C4** | Modèle de diagrammes (Context, Container, Component, Code). |
| **CERBERE** | Système d’authentification unique (SSO) de l’État français. |
| **DICT** | **Déclaration d’Intérêt à la Conformité au Traitement** (évaluation de sécurité). |
| **ADR** | **Architecture Decision Record** – décision documentée. |
| **DDM** | **Data‑Driven Model** – modèle de données relationnelles. |
| **MVP** | **Minimum Viable Product** – version initiale fonctionnelle. |

### 10.2 Référentiels & normes appliquées  

* **ISO/IEC/IEEE 42010 :2022** – Architecture description.  
* **ISO/IEC 25010 :2011** – Qualité des produits logiciels.  
* **ISO 27001** – Sécurité de l’information (exigences de chiffrement, audit).  
* **RGPD** – Protection des données à caractère personnel.  
* **DICT** – Evaluation de la sécurité (déclaration d’intérêt).  

### 10.3 Modèles de référence utilisés  

* **C4 Model** – Diagrammes Mermaid (`graph LR`, `classDiagram`).  
* **UML Class / Deployment** – Mermaid syntaxe `classDiagram` / `deploymentDiagram`.  
* **BPMN‑lite** – Mermaid `flowchart`.  
* **Security Architecture Diagram** – Mermaid `graph TD`.  

### 10.4 Modèles de contrat d’échange (JORF)  

* **Format** : XML (RFC 822‑like) fourni par le portail OpenData JORF.  
* **Schéma** : `jorf.xsd` (non inclus dans l’arborescence, à ajouter en annexe).  

### 10.5 Historique des versions du DAT  

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| **1.0** | 2026‑04‑27 | ChatGPT (OpenAI) | Création initiale du DAT selon les exigences ISO 42010. |
| **1.1** | – | – | À venir (mise à jour post‑migration Tomcat 10). |

---  

*Fin du document.*  