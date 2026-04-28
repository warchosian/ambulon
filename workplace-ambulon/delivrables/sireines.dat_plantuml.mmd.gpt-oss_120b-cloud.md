# 📄 **Dossier d’Architecture Technique – SIREINES**  

> **Version du DAT** : 1.0 – 2024‑04‑27  
> **Application** : **SIREINES** – Système d’information de recensement des experts et spécialistes scientifiques et techniques.  

---  

## 📚 Table des matières  
[TOC]

---  

## 1️⃣ Introduction & objectifs  

### 1.1 Vue fonctionnelle (C4‑L1)  

```mermaid
graph LR;
    %% System Context;
    subgraph Ext[Environnements externes]
        MOA[MOA – CGDD/DRI/AST4] 
        MOE[MOE – Klee Group / SG‑DNUM] 
        Users[Utilisateurs (agents, experts, référentiels)] 
        BIRT[BIRT Reporting] 
        Email[Serveur de mail] 
        DB[Base PostgreSQL] 
        Docker[Docker / Docker‑Compose] 
        Cerbere[Cerbère (Gestion des droits)] 
    end;
    subgraph SIREINES[Application SIREINES]
        WebApp[WebApp (Struts2 / Tomcat 7)] 
        Search[Recherche (Vertigo‑Elasticsearch)] 
        Service[Services métiers (Java 8, Maven)] 
        UI[Interface utilisateur (HTML/FTL)] 
    end;
    Users -->|utilise| UI;
    UI -->|appel| WebApp;
    WebApp -->|appelle| Service;
    Service -->|requête| DB;
    Service -->|indexe| Search;
    Search -->|recherche| DB;
    BIRT -->|génère rapports| Service;
    Email -->|envoie notifications| Service;
    Cerbere -->|détermine droits| Service;
    Docker -->|déploie| WebApp
```

> **Description** :  
Le système SIREINES regroupe un front‑end web (Struts2, FreeMarker) hébergé sur Tomcat, un cœur métier Java (Maven) exposant des services (CRUD, recherche, génération de rapports BIRT) et une base de données PostgreSQL. La recherche full‑text est assurée par Vertigo/Elasticsearch. Le tout est packagé dans des conteneurs Docker et déployé sur l’infrastructure IaaS ECO4 (Paris La Défense).

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif (qualité) | Raison métier |
|---|-------------------|---------------|
| Q‑01 | **Performance** – temps de réponse < 2 s pour les écrans de recherche. | Les agents consultent souvent les dossiers ; la rapidité impacte la productivité. |
| Q‑02 | **Disponibilité** – 99,5 % (MTBF ≥ 30 jours). | Le service est critique pour la validation des qualifications. |
| Q‑03 | **Sécurité** – conformité DPD / RGPD, traçabilité des accès. | Gestion de données à caractère personnel (experts). |
| Q‑04 | **Maintenabilité** – couverture de tests unitaires ≥ 70 % et documentation à jour. | Garantir l’évolution fonctionnelle (ex : nouveaux champs). |
| Q‑05 | **Scalabilité** – capacité à gérer + 20 % de trafic annuel sans refonte. | Augmentation du nombre d’experts et de dossiers. |

---  

## 2️⃣ Parties prenantes  

| Rôle | Responsable | Attente principale |
|------|-------------|---------------------|
| **MOA** (CGDD/DRI/AST4) | Pascal Zémour, Vincent Letrouit | Livrer les évolutions fonctionnelles dans les délais, visibilité sur les versions. |
| **MOE** (Klee Group / SG‑DNUM) | Matthieu Georges, Olivier Venot | Plateforme stable, CI/CD fiable, respect des contraintes techniques. |
| **Utilisateurs finaux** (agents, experts) | Services métiers | Interface ergonomique, accès aux dossiers, notifications email. |
| **RSSI** (Sécurité) | Service Sécurité DGSI | Conformité RGPD, journalisation, contrôle d’accès. |
| **Support / Exploitation** (GTI) | Équipe GTI | Supervision (Prometheus/Grafana), sauvegardes, récupération. |
| **Gestionnaire de droits** (Cerbère) | équipe Cerbère | Gestion fine des permissions (PRM_READ_ALL, PRM_WRITE_ALL). |
| **Architecte** | Vous (expert Arc42) | Documentation, cohérence technique, évolution. |

---  

## 3️⃣ Contraintes  

| Type | Description (D‑I‑C‑T) |
|------|------------------------|
| **Techniques** | • Java 8, Tomcat 7, Struts2, Vertigo, BIRT 4.3, PostgreSQL 14, Docker Compose 1.29.<br>• Méta‑données de version dans `version.properties`.<br>• Build Maven, assembly ZIP (scripts DB, war). |
| **Organisationnelles** | • Processus GitLab : Merge‑Request **develop‑cgi → recette**, **recette → preprod**, **preprod → prod**.<br>• Validation pipeline obligatoire avant merge.<br>• Documentation obligatoire (README, budget, déclarations RGPD). |
| **Réglementaires** | • Déclaration CNIL (n°1034232).<br>• RGPD – traçabilité, chiffrement des sauvegardes (AES‑256). |
| **Sécurité (D‑I‑C‑T)** | **Disponibilité** – HA via Docker‑restart, sauvegardes automatisées.<br>**Intégrité** – contraintes DB, triggers.<br>**Confidentialité** – accès via Cerbère, logs d’audit.<br>**Traçabilité** – logs Syslog, Prometheus, alertes. |
| **Performance** | Temps de réponse < 2 s sur les requêtes de recherche (Elasticsearch). |
| **Scalabilité** | Possibilité d’ajouter des réplicas Elasticsearch via variables Docker‑Compose. |

---  

## 4️⃣ Contexte & périmètre  

### 4.1 Partenaires fonctionnels  

| Système / acteur | Interaction | Protocole / fréquence |
|------------------|-------------|-----------------------|
| **Portail SIREINES** (Web) | Utilisateurs interagissent (CRUD dossiers, rapports) | HTTP/HTTPS, session JSESSIONID |
| **BIRT** (Reporting) | Génération de rapports PDF/Excel | HTTP, appels internes via `BirtManager` |
| **Cerbère** (Gestion des droits) | Vérification des permissions (PRM_READ_ALL, PRM_WRITE_ALL) | API interne (XML) |
| **GTI** (Supervision) | Collecte métriques, alertes | Prometheus / Grafana, port 9090 |
| **PostgreSQL** | Persistance des données | JDBC (PostgreSQL) |
| **Elasticsearch** (Vertigo) | Indexation/recherche plein‑texte | REST (9200) |
| **Mail** (SMTP) | Envoi de notifications | SMTP (TLS) |
| **Docker‑Compose** | Orchestration des conteneurs (app, DB, pgAdmin) | Docker API |

### 4.2 Interfaces techniques  

| Interface | Description | Format |
|----------|-------------|--------|
| `sireines-web.war` → Tomcat | Déploiement du WAR | WAR |
| `application-config.xml` | Paramètres généraux (version, nbRowPage) | XML |
| `sireines-auth-config.xml` | Permissions Cerbère | XML |
| `elasticsearch.yml` | Configuration d’analyse | YAML |
| `docker-compose.yml` | Définition des services (app, db, pgadmin) | YAML |
| `pom.xml` (modules) | Gestion des dépendances Maven | XML |
| `search/config/elasticsearch.yml` | Analyseur français, tokenizers | YAML |
| `log4j.xml` | Logging application | XML |
| `ehcache.xml` | Caching (Struts2) | XML |
| `version.properties` | Version + date de compilation | key/value |

---  

## 5️⃣ Stratégie de solution  

| Décision | Raison |
|----------|--------|
| **Architecture monolithique** (un seul WAR) | Simplicité de déploiement sur Tomcat, historique du projet. |
| **Conteneurisation Docker** | Isolation, reproductibilité, versionning des images (war + DB). |
| **Elasticsearch intégré (Vertigo)** | Recherche full‑text performante sur les mots‑clés. |
| **BIRT 4.3** pour les rapports | Framework déjà présent, génération PDF/Excel. |
| **Maven + Assembly** | Packaging automatisé (scripts DB, war). |
| **CI/CD GitLab** | Pipelines de build, tests, déploiement automatisé (merge‑request). |
| **Supervision Prometheus/Grafana** | Métriques temps réel, alertes sur disponibilité. |
| **Sauvegarde AES‑256** (scripts `dump` + stockage objet) | Conformité RGPD, résilience. |
| **Gestion des droits via Cerbère** | Centralisation des ACL, conformité sécurité. |
| **Utilisation de Struts2 + FreeMarker** | UI déjà existante, support de thèmes (`xhtml`, `simple`). |

### 5.1 Environnement technologique  

| Couche | Technologie | Version |
|--------|--------------|---------|
| **Langage** | Java | 8 (compatibilité JDK 8) |
| **Serveur d’app** | Tomcat | 7.0.108 |
| **Framework Web** | Struts2 | 2.x |
| **Templates** | FreeMarker | 2.x |
| **ORM / Persistence** | JPA (Vertigo) | – |
| **Recherche** | Vertigo‑Elasticsearch | – |
| **Base de données** | PostgreSQL | 14.1‑alpine |
| **Reporting** | BIRT | 4.3 |
| **Conteneurisation** | Docker, Docker‑Compose | 20.10 / 1.29 |
| **CI** | GitLab CI | – |
| **Supervision** | Prometheus / Grafana | – |
| **Gestion des droits** | Cerbère (authorisation‑config) | – |
| **Gestion des logs** | Log4j + SLF4J | – |
| **Gestion du cache** | Ehcache | – |

---  

## 6️⃣ Vue en Briques (C4‑L2)  

```mermaid
C4Container;
    title SIREINES – Conteneurs;
    Container_Boundary(sireines, "SIREINES") {
        Container(web, "WebApp (Struts2 / Tomcat)", "Java", "Interface utilisateur (HTML/FTL)")
        Container(service, "Service Métiers", "Java (Maven)", "Gestion des dossiers, recherche, BIRT, email")
        Container(db, "PostgreSQL", "PostgreSQL 14", "Persistance des données")
        Container(search, "Vertigo‑Elasticsearch", "Java / ES", "Indexation & recherche plein‑texte")
        Container(birt, "BIRT Engine", "Java", "Génération de rapports PDF/Excel")
    }
    System_Ext(ldap, "Cerbère", "Authorisation‑config XML", "Gestion des droits")
    System_Ext(email, "Serveur Mail", "SMTP", "Envoi de notifications")
    Rel(web, service, "Appel HTTP/Servlet")
    Rel(service, db, "JDBC")
    Rel(service, search, "API Vertigo")
    Rel(service, birt, "API BIRT")
    Rel(service, email, "SMTP")
    Rel(service, ldap, "Vérification des ACL")
```

---  

## 7️⃣ Vue d’exécution  

### 7.1 Scénario 1 – **Création d’un dossier et notification**  

```mermaid
sequencediagram;
    participant U as Agent (UI)
    participant W as WebApp (Struts2)
    participant S as Service Métiers;
    participant DB as PostgreSQL;
    participant M as Mail Server;
    participant C as Cerbère;
    U->>W: Soumet formulaire « Nouveau dossier »
    W->>S: POST /dossier/create;
    S->>C: Vérifie droits (PRM_WRITE_ALL)
    C-->>S: OK;
    S->>DB: INSERT dossier;
    DB-->>S: OK (id=123)
    S->>M: Envoie mail de confirmation;
    M-->>U: Mail envoyé;
    S-->>W: Retour UI (succès)
    W-->>U: Affiche confirmation
```

### 7.2 Scénario 2 – **Recherche de dossiers par mots‑clé**  

```mermaid
sequencediagram;
    participant U as Agent;
    participant W as WebApp;
    participant S as Service Métiers;
    participant ES as Elasticsearch;
    participant DB as PostgreSQL;
    U->>W: Saisie mots‑clé → Submit;
    W->>S: GET /dossier/search?kw=...
    S->>ES: Query index (full‑text)
    ES-->>S: IDs [45,78,102]
    S->>DB: SELECT dossiers WHERE id IN (...)
    DB-->>S: Dossiers;
    S-->>W: Résultats;
    W-->>U: Affiche tableau
```

### 7.3 Scénario 3 – **Génération d’un rapport BIRT**  

```mermaid
sequencediagram;
    participant U as Responsable;
    participant W as WebApp;
    participant S as Service Métiers;
    participant B as BIRT Engine;
    U->>W: Clique “Export PDF”
    W->>S: POST /rapport/generate;
    S->>B: Request report (params)
    B-->>S: PDF (bytes)
    S-->>W: Retour fichier;
    W-->>U: Téléchargement PDF
```

---  

## 8️⃣ Vue Déploiement *(section standardisée)*  

### 8.1 Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|-----------------|
| **Développement** | Poste local (Docker Desktop) | `sireines_app_usine_container` (Tomcat) | Bridge Docker | Volumes `sireines_db_sireines_vol` (dev) |
| **Recette** | Serveur `sireinesrec` (Bastion) | `sireines-app` (Docker) | VLAN Recette ECO4 | Accès via Bastion, logs Prometheus, sauvegarde quotidienne |
| **Pré‑production** | Serveur `sireinesppr` | `sireines-app` (Docker) | VLAN Pre‑prod ECO4 | Test de charge, validation avant prod |
| **Production** | Serveur `sireinesprod` (IaaS ECO4) | `sireines-app` (Docker) | VLAN Prod ECO4 | HA (restart policy), sauvegarde chiffrée AES‑256, monitoring complet |

> **Remarque** : Tous les environnements utilisent le même `docker-compose.yml` (version 2025‑xx‑xx) avec le même jeu de volumes (`sireines_db_sireines_vol`, `sireines_pgadmin_sireines_vol`).  

### 8.2 Infrastructure  

```mermaid
graph TD;
    subgraph ECO4_IaaS["ECO4 – IaaS (Paris La Défense)"]
        LB[Load‑Balancer (HAProxy)]
        APP[Docker‑Host (Tomcat + App)]
        DB[Docker‑Host (PostgreSQL + pgAdmin)]
        MON[Prometheus/Grafana]
        BACKUP[Backup Service (AES‑256, Object Storage B3, SecNumCloud, GCP)]
    end;
    User[Utilisateurs] --> LB;
    LB --> APP;
    APP --> DB;
    APP --> MON;
    DB --> MON;
    MON --> BACKUP
```

- **Reverse‑proxy Nginx** (2 instances) en front du conteneur `sireines-app`.  
- **Supervision** : Prometheus → Grafana, alertes via Alertmanager, tableau de bord PSIN.  
- **Sauvegarde** : scripts `dump` (PostgreSQL) → chiffrement AES‑256 → stockage multi‑site (B3, SecNumCloud, GCP).  

### 8.3 Supervision  

| Outil | Usage |
|-------|-------|
| **Portainer** | Gestion des conteneurs Docker (Vue Web). |
| **Prometheus / Grafana** | Métriques CPU, RAM, latence HTTP, taille des files d’attente, état du cluster ES. |
| **AlertManager** | Notifications Slack / e‑mail en cas d’incident. |
| **PSIN** | Dashboard centralisé des applications ministérielles. |

### 8.4 Sauvegardes  

- **Base** : `pg_dump` quotidien, compressé, chiffré AES‑256.  
- **Stockage** :  
  - `B3` (object storage interne)  
  - `SecNumCloud` (offre « Nuage Public »)  
  - `Google Cloud Storage` (offre « Nuage Public »)  
- **Restauration** : procédure documentée dans le répertoire `sireines-d