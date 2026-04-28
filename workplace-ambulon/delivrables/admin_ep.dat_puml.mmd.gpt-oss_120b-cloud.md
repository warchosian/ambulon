# 📘 Dossier d’Architecture Technique (DAT) – **admin_ep**  

[TOC]

---  

## 1️⃣ Introduction et objectifs  

**Vue d’ensemble fonctionnelle**  
L’application **admin_ep** (Administration des établissements publics) centralise les listes des membres des conseils d’administration des établissements publics placés sous la tutelle du ministère de la Transition écologique. Elle permet :  

* la saisie manuelle des administrateurs,  
* l’alimentation automatique à partir des publications du **JORF**,  
* la consultation, la recherche et la visualisation de statistiques,  
* la génération d’alertes de fin de mandat.  

### C4 – Niveau 1 – Contexte système (Mermaid)  

```mermaid
flowchart LR;
    subgraph Users;
        U1[SPES / DG de tutelle] 
        U2[Opérateurs] 
        U3[Auditeurs / RSSI] 
    end;
    subgraph External;
        Ext1[JORF (OpenData)] 
        Ext2[Cerbère (authentification)] 
        Ext3[ElasticSearch] 
    end;
    subgraph System;
        Nginx[Nginx (reverse‑proxy)]
        App[admin_ep (Tomcat 9, Struts2, Java 8)]
        DB[(PostgreSQL 9.6)]
        Monitoring[Prometheus + Grafana]
    end;
    U1 -->|HTTPS| Nginx;
    U2 -->|HTTPS| Nginx;
    U3 -->|HTTPS| Nginx;
    Nginx -->|HTTP| App;
    App -->|JDBC| DB;
    App -->|REST/HTTPS| Ext2;
    App -->|Batch/HTTPS| Ext1;
    App -->|REST| Ext3;
    Monitoring -->|scrape| App;
    Monitoring -->|scrape| DB
```

### Objectifs de qualité (orientés utilisateur)  

| # | Objectif | Mesure cible |
|---|----------|--------------|
| 1 | **Performance** – temps de réponse des écrans de recherche < 2 s (95 % des requêtes) |
| 2 | **Sécurité** – conformité DICT, chiffrement TLS 1.2+, traçabilité des actions critiques |
| 3 | **Disponibilité** – 99,5 % de disponibilité mensuelle (excluant maintenances planifiées) |
| 4 | **Maintenabilité** – couverture de tests unitaires ≥ 80 %, builds automatisés via CI/CD |
| 5 | **Scalabilité** – capacité à ajouter des réplicas d’application et de DB sans interruption |

---  

## 2️⃣ Parties prenantes  

| Rôle | Attente principale |
|------|--------------------|
| **Maîtrise d’ouvrage (MOA)** – SG/SPES | Livraison d’une solution fiable, conforme aux exigences fonctionnelles et réglementaires (DICT, RGPD) |
| **Maîtrise d’œuvre (MOE)** – SG/DNUM/PNM/DPNM3/BPN (CGI) | Respect du planning, réutilisation de la stack ACAI, documentation technique à jour |
| **Utilisateurs finaux** – SPES, DG de tutelle, opérateurs | Interface ergonomique, recherche rapide, alertes de fin de mandat fiables |
| **RSSI / Sécurité** – SG/DNUM | Confidentialité des données personnelles, traçabilité, auditabilité |
| **Équipe de supervision** – PSIN | Visibilité complète sur la santé de l’application (metrics, logs, alerts) |
| **Équipe de support** – CGI | Outils de diagnostic (Portainer, logs) pour résolution rapide des incidents |

### Contacts (extraits du fichier `admin_ep.wikisi.md`)  

| Nom complet | Rôle | Courriel |
|-------------|------|----------|
| **Christian ARBOGAST** | Chef de produit (PNM3) | <Christian.Arbogast@developpement-durable.gouv.fr> |
| **Céline GILLIARD** | Directrice de produit (PNM3) | <celine.gilliard@developpement-durable.gouv.fr> |

---  

## 3️⃣ Contraintes  

### 3.1 Contraintes techniques  

| Domaine | Contraintes |
|---------|-------------|
| **Plateforme** | Java 8, Tomcat 9.0.8, Struts 2, Vertigo, ACAI (clusters ESXi) |
| **Base de données** | PostgreSQL 9.6 / 11 (actuellement 9.6.11) |
| **Conteneurisation** | Docker, Docker‑Compose, déploiement sur IaaS (ECO4) |
| **Intégration continue** | GitLab CI, Maven, SonarQube (qualité code) |
| **Supervision** | Prometheus, Grafana, Loki, AlertManager, Portainer |
| **Sécurité** | TLS 1.2+, authentification Cerbère, logs immuables, sauvegardes chiffrées AES‑256 |
| **Interopérabilité** | Consommation du flux JORF (HTTPS, RSS) |

### 3.2 Contraintes organisationnelles  

* Gestion de projet en mode **PI** (Programme d’Intégration) avec exigences de livrables formels.  
* Hébergement dans le **data‑center ministériel Paris La Défense** (Production, Pré‑production, Recette).  
* Respect de la **charte de nommage** et des référentiels d’artefacts (Maven, GitLab).  

### 3.3 Contraintes réglementaires  

| Référentiel | Exigence |
|--------------|----------|
| **DICT** (Délégation à l’Information et à la Communication) | Evaluation positive (07/09/2018) – exigences D‑I‑C‑T |
| **RGPD** | Traçabilité des accès, droit d’accès, de rectification, de suppression |
| **Sécurité du SI** | Confidentialité (chiffrement), Intégrité (hashes), Disponibilité (plan de reprise), Traçabilité (audit logs) |

#### Modèle D‑I‑C‑T appliqué  

| Axe | Implémentation |
|-----|----------------|
| **Disponibilité** | Architecture redondante (Nginx en HA, réplicas Tomcat), sauvegardes automatisées |
| **Intégrité** | Contrôle de version des scripts SQL, checksums sur les paquets JORF |
| **Confidentialité** | TLS, chiffrement AES‑256 des dumps, politiques de privilèges DB |
| **Traçabilité** | Log4j2 → Loki, tables d’audit (date, user, action) |

---  

## 4️⃣ Contexte et périmètre  

| Entité | Interaction | Interface |
|--------|--------------|-----------|
| **Utilisateurs** | Consultation / saisie via navigateur | HTTPS (Nginx → Tomcat) |
| **Cerbère** | Authentification et autorisations | REST / HTTPS (token JWT) |
| **JORF (OpenData)** | Ingestion quotidienne des arrêtés | HTTPS (RSS, fichiers .tar.gz) |
| **ElasticSearch** | Indexation des textes JORF pour recherche plein texte | REST / HTTPS |
| **Base PostgreSQL** | Persistance des données métier | JDBC |
| **Supervision PSIN** | Tableau de bord de santé applicative | HTTP (Grafana) |
| **Portainer** | Gestion des conteneurs Docker | HTTP (Web UI) |

Le **périmètre fonctionnel** inclut : saisie manuelle, ingestion JORF, recherche, visualisation statistique, gestion des mandats, envoi de notifications e‑mail, administration (CRUD des entités).  

---  

## 5️⃣ Stratégie de solution  

| Décision | Justification |
|----------|--------------|
| **Monolithe Java (Struts2 + Vertigo)** | Réutilisation du code existant, faible complexité de mise en œuvre, cohérence avec les autres applications du ministère |
| **Conteneurisation Docker** | Uniformité d’environnement, scalabilité, alignement avec la politique « IaaS » (ECO4) |
| **Maven multi‑module** | Gestion claire des dépendances entre *adminep‑database*, *adminep‑deployment*, *adminep‑web* |
| **CI/CD GitLab** | Pipelines automatisés (build, tests, packaging, déploiement) |
| **Nginx comme reverse‑proxy** | Gestion du TLS, équilibrage de charge, découplage front‑back |
| **Sauvegardes chiffrées** | Conformité DICT / RGPD |
| **Monitoring stack** (Prometheus / Grafana / Loki) | Visibilité opérationnelle, alertes proactives |

### Stack technologique (extraits du fichier `admin_ep.wikisi.md`)  

| Couche | Technologie / Version |
|--------|-----------------------|
| **Langage** | Java 8 |
| **Web** | Tomcat 9.0.8, Struts 2, Vertigo |
| **Base** | PostgreSQL 9.6 / 11 |
| **Conteneur** | Docker, Docker‑Compose |
| **CI** | GitLab CI, Maven |
| **Auth** | Cerbère (SSO) |
| **Supervision** | Prometheus, Grafana, Loki, AlertManager, Portainer |
| **Search** | ElasticSearch (pour JORF) |
| **Gestion de configuration** | ACAI (clusters ESXi) |
| **Sécurité** | TLS 1.2+, log4j2, chiffrement AES‑256 |

---  

## 6️⃣ Vue en Briques (C4 – Niveau 2)  

```mermaid
graph TB;
    subgraph "Infrastructure"
        Nginx[Nginx (LB/Reverse‑proxy)]
        Tomcat[Tomcat 9 (admin_ep WAR)]
        DB[(PostgreSQL)]
        ES[ElasticSearch]
        Prom[Prometheus]
        Graf[Grafana]
        Loki[Loki]
        Port[Portainer]
    end;
    Nginx --> Tomcat;
    Tomcat --> DB;
    Tomcat --> ES;
    Tomcat --> Prom;
    Prom --> Graf;
    Prom --> Loki;
    Port --> Tomcat;
    Port --> DB
```

### Description des conteneurs principaux  

| Conteneur | Rôle | Principaux artefacts |
|-----------|------|----------------------|
| **Nginx** | Point d’entrée HTTPS, équilibrage de charge, terminaison TLS | `nginx.conf` (HA) |
| **Tomcat** | Héberge le WAR `admin_ep.war` (Struts2, Vertigo) | `admin_ep-web‑<version>.war` |
| **PostgreSQL** | Persistance des entités métier (admins, mandats, établissements) | Schéma `integration` + scripts d’init |
| **ElasticSearch** | Indexation plein texte des documents JORF | `jorf‑index` |
| **Prometheus / Grafana / Loki** | Collecte métriques, visualisation, logs centralisés | Exporters JMX, log4j2‑appender |
| **Portainer** | Gestion de l’orchestration Docker (déploiement, mise à jour) | UI web |

---  

## 7️⃣ Vue Exécution (Scénarios critiques)  

### 7.1 Scénario 1 – Recherche d’un administrateur  

```mermaid
sequencediagram;
    participant User as Utilisateur (Browser)
    participant Nginx;
    participant App as admin_ep (Tomcat)
    participant DB as PostgreSQL;
    participant Auth as Cerbère;
    User->>Nginx: HTTPS GET /admin/search?query=Dupont;
    Nginx->>Auth: Validate JWT (session)
    Auth-->>Nginx: OK;
    Nginx->>App: HTTP GET /search?query=Dupont;
    App->>DB: SELECT … FROM admins WHERE name ILIKE '%Dupont%'
    DB-->>App: Resultset;
    App->>Nginx: HTTP 200 + HTML page;
    Nginx->>User: HTTPS 200 (liste admins)
```  

*Critères de validation* : temps de réponse < 2 s, logs d’audit créés, aucune fuite d’informations sensibles.

### 7.2 Scénario 2 – Ingestion JORF (batch)  

```mermaid
sequencediagram;
    participant Scheduler as Scheduler (Quartz)
    participant App as admin_ep;
    participant JORF as JORF (RSS/HTTPS)
    participant ES as ElasticSearch;
    participant DB as PostgreSQL;
    Scheduler->>App: Trigger Job "Ingestion JORF"
    App->>JORF: GET https://echanges.dila.gouv.fr/OPENDATA/JORF/rss;
    JORF-->>App: XML feed;
    App->>App: Parse, extract articles;
    App->>ES: Index article (full‑text)
    App->>DB: INSERT/UPDATE tables (mandats, établissements)
    App-->>Scheduler: Job completed
```  

*Critères* : aucun doublon, intégrité des données, logs d’exécution, alerte en cas d’échec.

### 7.3 Scénario 3 – Notification d’échéance de mandat  

```mermaid
sequencediagram;
    participant Scheduler as Scheduler (Quartz)
    participant App as admin_ep;
    participant DB as PostgreSQL;
    participant Mail as SMTP;
    Scheduler->>App: Trigger "MandateAlert"
    App->>DB: SELECT mandates WHERE end_date BETWEEN now() AND now()+7;
    DB-->>App: Resultset;
    loop for each mandate;
        App->>Mail: Send e‑mail to référent;
    end;
    App-->>Scheduler: Alerts sent
```  

*Critères* : e‑mail délivré, accusé de réception, trace dans table `mandate_alert_log`.

---  

## 8️⃣ Vue Déploiement *(section standardisée)*  

```markdown
### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | Docker‑Compose local | 1 x Tomcat, 1 x PostgreSQL | LAN | Debug activé, logs verbeux |
| Recette       | IaaS ECO4 (VM) | 2 x Tomcat (HA), 1 x PostgreSQL (standby) | VLAN dédié | Jeux de données anonymisés |
| Production    | IaaS ECO4 (clusters) | 4 x Tomcat (load‑balanced), 2 x PostgreSQL (primary/replica) | DMZ + VLAN interne | TLS 1.2, sauvegardes chiffrées, monitoring complet |
```

```mermaid
@startuml;
    node "Nginx" as N;
    component "Application" as A;
    database "Base de données" as DB;
    component "ElasticSearch" as ES;
    component "Prometheus/Grafana/Loki" as MON;
    N --> A;
    A --> DB;
    A --> ES;
    A --> MON
@enduml
```

### Supervision  

Le produit est supervisé via le système standard du GTI pour ce faire :  

* **Portainer** – gestion des conteneurs Docker, état des services, mise à jour en rolling‑update.  
* **Stack Prometheus / Grafana / Loki / AlertManager** – métriques (CPU, mémoire, latence HTTP), dashboards, logs centralisés, alertes (disponibilité, erreurs 5xx, dépassement de seuils).  
* **Supervision PSIN** – tableau de bord dédié (Système d’Information du Ministère).  

### Sauvegardes  

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES‑256 et déposés sur :  

* le stockage objet **B3** du IaaS ministériel,  
* le stockage objet **Outscale SecNumCloud** (via la prestation « Nuage Public »),  
* le stockage objet standard de **Google Cloud** (via la prestation « Nuage Public »).  

---  

## 9️⃣ Sujets transverses  

| Thème | Implémentation dans admin_ep |
|-------|------------------------------|
| **Authentification** | Filtre `SecurityFilter` (Vertigo) → validation token Cerbère, mapping des rôles (`Roles.java`) |
| **Journalisation** | Log4j2 avec appender `LokiAppender`, fichiers de logs rotatifs (`log4j2.xml`) |
| **Monitoring** | JMX exporter (Tomcat), métriques custom (temps de traitement des jobs) |
| **Gestion des erreurs** | `ErrorHandler.java` centralise les erreurs HTTP/Exception, page `application-error.jsp` |
| **API interne** | Services Java (`*Service.java`) exposés via Struts actions, appelables par batch ou UI |
| **Sécurité** | `SecurityHelper`, `RightsHelper`, chiffrement des mots de passe (BCrypt), politique de mots de passe forte |
| **Internationalisation** | `I18nResourcesInitializer` charge les bundles de messages |
| **Gestion des dépendances** | Maven `pom.xml` avec plugin `maven-assembly-plugin` pour packaging ZIP des scripts SQL |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`) : stages *build → test → package → deploy* |
| **Sauvegarde & restauration** | Scripts `backup.sh` / `restore.sh` (AES‑256, versionning) |
| **Documentation** | `adminep-doc` module (assembly, Javadoc) |

---  

## 🔟 Exigences de qualité  

| Exigence | Description | Scénario de validation |
|----------|-------------|------------------------|
| **Performance** | Réponse < 2 s pour les requêtes de recherche | Exécution du scénario 1 avec charge de 100 concurrentes (JMeter) – mesure < 2 s |
| **Sécurité – Confidentialité** | Toutes les communications chiffrées TLS 1.2+ | Scan SSL Labs, test de pénétration OWASP ZAP, vérification du chiffrement des dumps |
| **Disponibilité** | 99,5 % de disponibilité mensuelle | Monitoring Prometheus → alertes sur downtime > 30 min, calcul du SLA sur le mois |
| **Intégrité des données** | Aucun doublon d’administrateur après ingestion JORF | Exécution du scénario 2, vérification du nombre d’enregistrements avant/après (checksum) |
| **Traçabilité** | Journalisation de chaque action critique (CRUD) | Requête dans Loki pour un `admin_id` donné, présence d’un `audit` record |
| **Scalabilité** | Ajout d’un réplicas Tomcat sans interruption | Test de rolling‑update via Portainer, aucune perte de session |
| **Maintenabilité** | Couverture de tests unitaires ≥ 80 % | Rapport SonarQube, seuil de couverture atteint |

---  

## 1️⃣1️⃣ Risques et dettes techniques  

| Risque / Dette | Impact | Probabilité | Mesure corrective / atténuation |
|----------------|--------|-------------|--------------------------------|
| **Obsolescence du stack** (Java 8, Tomcat 9) | vulnérabilités non corrigées, fin de support | Moyen | Plan de migration vers Java 11 / Tomcat 10 dans le prochain sprint PI |
| **Dépendance au flux JORF** (format variable) | rupture d’alimentation, données incohérentes | Moyen | Implémenter un parseur tolerant, tests de régression sur les schémas JORF |
| **Version de PostgreSQL 9.6** (EOL) | manque de correctifs, incompatibilité futures | Élevé | Prévoir migration vers PostgreSQL 13 (script de migration) |
| **Gestion manuelle des scripts SQL** | risque de divergence entre environnements | Moyen | Utiliser Flyway/Liquibase pour versionner les migrations |
| **Charge de recherche élevée** (full‑text) | latence, surcharge du serveur | Faible | Indexer les champs critiques, mettre en cache les résultats fréquents |
| **Mise à jour du certificat TLS** | interruption de service si non synchronisé | Faible | Automatiser le renouvellement via Let's Encrypt ou ACME interne |

---  

## 1️⃣2️⃣ Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **ACAI** | Plateforme d’hébergement de l’État basée sur des clusters ESXi (virtualisation) |
| **Cerbère** | Service d’authentification centralisé (SSO) du ministère |
| **ECO4** | Cloud interne du ministère (IaaS) hébergeant les environnements de recette et de production |
| **JORF** | Journal Officiel de la République Française – source officielle des arrêtés et décrets |
| **Vertigo** | Framework interne de l’État facilitant la construction d’applications Java (DI, MVC) |
| **DI‑C‑T** | Modèle de sécurité : Disponibilité, Intégrité, Confidentialité, Traçabilité |
| **Portainer** | Interface de gestion Docker (déploiement, surveillance) |
| **Prometheus / Grafana / Loki** | Stack de monitoring (metrics, dashboards, logs) |
| **Struts 2** | Framework MVC Java utilisé pour le rendu des pages JSP |
| **Tomcat** | Serveur d’applications Java (container de servlets) |
| **IaaS** | Infrastructure as a Service – fourniture de machines virtuelles, stockage, réseau |

### 12.2 Décisions d’Architecture (ADR)  

| # | Décision | Contexte | Alternatives | Raison |
|---|----------|----------|--------------|---------|
| ADR‑001 | **Utiliser Struts 2 + Vertigo** | Application existante en Struts 2 | Spring MVC, Micronaut | Réduction du coût de migration, expertise interne, conformité aux standards ministériels |
| ADR‑002 | **Conteneuriser avec Docker** | Besoin de portabilité entre dev, recette, prod | VM uniquement | Docker simplifie le packaging, facilite le scaling, cohérence avec la politique IaaS |
| ADR‑003 | **Base de données PostgreSQL** | Données relationnelles, exigences de transaction | Oracle, MySQL | PostgreSQL open‑source, déjà utilisé dans d’autres SI ministériels, support des extensions géographiques si besoin futur |
| ADR‑004 | **Sauvegardes chiffrées AES‑256** | Conformité DICT, RGPD | Sauvegarde non chiffrée, chiffrement propriétaire | AES‑256 reconnu, compatibilité avec les solutions de stockage du ministère |
| ADR‑005 | **Monitoring avec Prometheus/Grafana/Loki** | Besoin de métriques et logs centralisés | Zabbix, ELK complet | Stack légère, intégration native avec Kubernetes/Docker, déjà adoptée par le GTI |

---  

*Document généré le 27/04/2026 – Version 1.0*  

---  

**Fin du DAT**  



---  



**Liens internes rapides**  

* [Vue d’ensemble fonctionnelle (section 1)](#1️⃣-introduction-et-objectifs)  
* [Parties prenantes (section 2)](#2️⃣-parties-prenantes)  
* [Contraintes (section 3)](#3️⃣-contraintes)  
* [Contexte et périmètre (section 4)](#4️⃣-contexte-et-périmètre)  
* [Stratégie de solution (section 5)](#5️⃣-stratégie-de-solution)  
* [Vue en Briques (section 6)](#6️⃣-vue-en-briques-c4‑niveau 2)  
* [Vue Exécution (section 7)](#7️⃣-vue-exécution-scenarios-critiques)  
* [Vue Déploiement (section 8)](#8️⃣-vue-déploiement‑section‑standardisée)  
* [Sujets transverses (section 9)](#9️⃣-sujets-transverses)  
* [Exigences de qualité (section 10)](#🔟-exigences-de-qualité)  
* [Risques et dettes (section 11)](#1️⃣1️⃣-risques-et-dettes-techniques)  
* [Annexes (section 12)](#12️⃣-annexes)  



---  



↩ Retour au sommaire  