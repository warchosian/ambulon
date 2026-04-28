# 📘 Dossier d’Architecture Technique (DAT) – **SIREINES**

> **Version du DAT** : 2024‑03‑15 | **Auteur** : ChatGPT (OpenAI)  
> **Référentiel** : `sireines` – GitLab ( `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\sireines` )  

---

## 📑 Table des matières  
[TOC]

1. [Introduction & objectifs](#introduction--objectifs)  
2. [Parties prenantes](#parties-prenantes)  
3. [Contraintes](#contraintes)  
4. [Contexte & périmètre](#contexte--périmètre)  
5. [Stratégie de solution](#stratégie-de-solution)  
6. [Vue en briques (C4‑L2)](#vue-en-briques)  
7. [Vue exécution (scénarios)](#vue-exécution)  
8. [Vue déploiement (standardisée)](#vue-déploiement)  
9. [Sujets transverses](#sujets-transverses)  
10. [Exigences de qualité](#exigences-de-qualité)  
11. [Risques & dettes techniques](#risques--dettes-techniques)  
12. [Annexes](#annexes)  

---

## 1️⃣ Introduction & objectifs <a id="introduction--objectifs"></a>

**Vue d’ensemble fonctionnelle**  
SIREINES (Système d’Information de Référentiel des Experts et Spécialistes) recense les demandes de qualification des agents, assure le suivi des comités de domaine, produit les rapports BIRT et notifie les agents par courriel.

```mermaid
flowchart LR
    A[Agent/Utilisateur] --> B[Web UI (Struts2)]
    B --> C[Controller (Spring/Vertigo)]
    C --> D[Service Layer]
    D --> E[DAO (JPA/SQL)]
    E --> F[(PostgreSQL)]
    C --> G[Reporting (BIRT)]
    G --> H[PDF/Excel]
    C --> I[Mail (SMTP)]
```

**Objectifs qualité orientés utilisateur**  

| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Performance** : temps de réponse < 2 s pour les recherches de dossiers | Faciliter la prise de décision des experts |
| 2 | **Disponibilité** : 99,5 % (MTBF ≥ 30 jours) | Garantir l’accès continu aux qualifications |
| 3 | **Sécurité / Confidentialité** : chiffrement des données sensibles, conformité RGPD | Protection des données personnelles des experts |
| 4 | **Maintenabilité** : couverture de tests unitaires ≥ 70 % | Réduction du coût de maintenance et d’évolution |
| 5 | **Scalabilité** : capacité à doubler le nombre d’utilisateurs sans changement d’infrastructure | Anticiper la croissance du répertoire d’experts |

---

## 2️⃣ Parties prenantes <a id="parties-prenantes"></a>

| Rôle | Responsable | Attente principale |
|------|--------------|--------------------|
| **MOA** (Maîtrise d’Ouvrage) | Pascal Zemour – CGDD/DRI/AST4 | Livraison conforme aux besoins fonctionnels, respect des délais |
| **MOE** (Maîtrise d’Œuvre) | Vincent Letrouit – CGDD/DRI/AST4 | Architecture évolutive, documentation à jour |
| **Équipe de développement** | Klee Group (historique) / équipes internes | Qualité du code, automatisation CI/CD |
| **Exploitation / Ops** | Service TI (ECO4) | Disponibilité, monitoring, sauvegardes |
| **Utilisateurs finaux** (agents, experts) | Ministère de la Transition Écologique | Accès fiable aux dossiers, notifications par mail |
| **RSSI** (Sécurité) | CGDD/SRI/AST2 | Conformité CNIL, DICP (Disponibilité, Intégrité, Confidentialité, Traçabilité) |
| **Support** | Portail‑support DIN | Gestion des incidents et demandes d’évolution |

---

## 3️⃣ Contraintes <a id="contraintes"></a>

| Type | Description | Référence |
|------|-------------|-----------|
| **Techniques** | Java 8, Tomcat 7, PostgreSQL 14 (alpine), Docker Compose, Maven 3.6+ | `Dockerfile`, `pom.xml` |
| **Réglementaires** | CNIL (déclaration 29/09/2014 n°1034232), RGPD – DACP (données à caractère personnel) | `Home.md`, `SIREINES.wiki.md` |
| **Opérationnelles** | Hébergement IaaS (ECO4) – centre Paris La Défense, sauvegarde AES‑256, réplication | Section *Vue Déploiement* |
| **Organisationnelles** | Processus de mise en production via *Merge Request* (preprod → prod) | `DeploiementApplicatif.md` |
| **Performance** | Temps de réponse < 2 s, charge maximale 200 req/s | Objectif 1 |
| **Sécurité** | Authentification via Cerbère, chiffrement TLS 1.2+, mots de passe stockés en hash BCrypt | `sireines-auth-config.xml` |
| **Disponibilité** | SLA 99,5 % (MTTR ≤ 4 h) | Objectif 2 |

---

## 4️⃣ Contexte & périmètre <a id="contexte--périmètre"></a>

### 4.1 Interfaces fonctionnelles  

| Système | Protocole | Fréquence | Type de données |
|---------|-----------|------------|-----------------|
| **Cerbère** (auth) | HTTP / HTTPS | À chaque login | Jeton JWT |
| **BIRT** (reporting) | HTTP (REST) | À la demande | PDF / Excel |
| **SMTP** (mail) | SMTP TLS | À chaque notification | Courriel texte/HTML |
| **PgAdmin** (admin DB) | HTTP / HTTPS | Occasionnelle | Métadonnées DB |
| **Portail‑support** | HTTP / HTTPS | Incident/Change | Tickets JIRA‑like |

### 4.2 Interfaces techniques  

* **Web** : Struts2 actions, JSP/FTL vues, CSS Bootstrap 4, JavaScript (jQuery)  
* **Service** : Spring beans, Vertigo *SearchManager*, *BirtManager* (VFile)  
* **Persistance** : JPA (Hibernate) sur PostgreSQL, scripts SQL versionnés (`sireines-database/script/*`)  
* **Reporting** : BIRT 4.3, fichiers `.rptdesign` (Talend)  
* **Conteneurisation** : Docker Compose (app, db, pgadmin, nginx) – voir vue déploiement  

---

## 5️⃣ Stratégie de solution <a id="stratégie-de-solution"></a>

| Décision | Motif |
|----------|------|
| **Architecture monolithique** (WAR) | Simplicité de déploiement, faible latence intra‑processus, historique existant |
| **Frameworks** : Struts2 (MVC), Spring (DI, AOP, TX), Vertigo (search) | Réutilisation du code existant, robustesse |
| **Base de données** : PostgreSQL 14 (alpine) | Licence libre, performances, support JSONB pour les extractions |
| **Conteneurisation** : Docker Compose (4 containers) | Isolation, réplication d’environnements (recette, pre‑prod, prod) |
| **Reverse‑proxy** : Nginx (2 instances en load‑balancing) | Haute disponibilité, TLS termination |
| **CI/CD** : GitLab CI, Maven, SonarQube | Qualité du code, automatisation des builds & tests |
| **Reporting** : BIRT intégré via *BirtManager* | Génération de PDF/Excel à la volée |
| **Gestion des identités** : Cerbère (OAuth2/JWT) | Centralisation, conformité sécurité |
| **Sauvegarde** : Scripts `pg_dump` chiffrés AES‑256, stockage multi‑site (B3, Outscale, Google Cloud) | Résilience et conformité RGPD |
| **Monitoring** : Prometheus + Grafana + AlertManager, Portainer pour Docker | Visibilité opérationnelle, alertes SLA |

---

## 6️⃣ Vue en briques (C4‑L2) <a id="vue-en-briques"></a>

```mermaid
graph TD
    subgraph "Docker‑Compose"
        A[nginx‑lb] --> B[sireines_app_usine_container]
        B --> C[(PostgreSQL)]
        B --> D[sireines_pgadmin_container]
    end
    B -->|REST/HTML| UI[Browser (HTML/JS)]
    UI -->|Auth JWT| Cerb[Cerbère (OAuth2)]
    B -->|BIRT| RPT[BIRT Engine]
    B -->|Mail| SMTP[SMTP Server]
    C -->|JDBC| DAO[DAO (JPA/Hibernate)]
    DAO -->|Domain| Service[Service Layer (Spring/Vertigo)]
    Service -->|Business| Controller[Struts2 Controllers]

    classDef infra fill:#f9f,stroke:#333,stroke-width_1px;
    class A,B,C,D infra;
```

**Descriptions rapides**  

| Brique | Rôle | Technologies |
|--------|------|--------------|
| **nginx‑lb** | Load‑balancing + TLS termination | Nginx 1.23 |
| **sireines_app_usine_container** | Application Java (WAR) | Tomcat 7, Struts2, Spring, Vertigo |
| **PostgreSQL** | Persistance des dossiers | PostgreSQL 14‑alpine |
| **sireines_pgadmin_container** | Administration DB (facultatif) | pgAdmin 4 |
| **Cerbère** | Authentification unique (JWT) | OAuth2, RSA‑256 |
| **BIRT Engine** | Génération de rapports | BIRT 4.3 |
| **SMTP** | Envoi de courriels | Postfix/Exim (TLS) |
| **Service Layer** | Logique métier, recherche, email | Spring, Vertigo Search, JavaMail |
| **DAO** | Accès aux tables, scripts d’index | JPA (Hibernate) |
| **Controller** | Gestion des requêtes HTTP | Struts2 actions, JSP/FTL vues |

---

## 7️⃣ Vue exécution (scénarios critiques) <a id="vue-exécution"></a>

### 7.1 Authentification & accès à la liste des dossiers  

```mermaid
sequencediagram;
    participant User as Agent;
    participant UI as Browser;
    participant Nginx as Nginx‑LB;
    participant App as SIREINES‑App;
    participant Cerb as Cerbère;
    participant DB as PostgreSQL;
    User->>UI: Ouvre https://sireines.recette…
    UI->>Nginx: GET /Login.do;
    Nginx->>App: Forward request;
    App->>Cerb: POST /auth (credentials)
    Cerb-->>App: JWT (validité 2 h)
    App-->>UI: Page d’accueil + JWT (cookie)
    UI->>App: GET /Dossiers.do (avec JWT)
    App->>DB: SELECT dossiers WHERE user_id=…
    DB-->>App: Résultat;
    App-->>UI: Liste dossiers (HTML)
```

*Points de contrôle* : validation du JWT, logs d’audit (`sireines-auth-config.xml`), timing < 500 ms.

### 7.2 Génération d’un rapport BIRT  

```mermaid
sequencediagram;
    participant User;
    participant UI;
    participant App;
    participant Birt as BIRT Engine;
    participant DB;
    participant Mail as SMTP;
    User->>UI: Clique « Export PDF »
    UI->>App: POST /ExportRapport.do (dossierId)
    App->>DB: SELECT * FROM dossier WHERE id=…
    DB-->>App: Données;
    App->>Birt: generateReport(données)
    Birt-->>App: PDF (VFile)
    App->>UI: Download PDF;
    App->>Mail: sendMail(to, subject, PDF)
    Mail-->>User: Courriel de notification
```

*Points de contrôle* : taille PDF < 5 Mo, durée < 3 s, trace d’envoi (`log4j.xml`).

### 7.3 Sauvegarde programmée (cron Docker)  

```mermaid
sequencediagram;
    participant Docker as Docker‑Host;
    participant DB as PostgreSQL;
    participant Script as backup.sh;
    participant Store as Object‑Storage;
    Docker->>Script: every 24 h (cron)
    Script->>DB: pg_dump -U sireines -Fc > dump.sql;
    Script->>Script: openssl enc -aes-256-cbc -salt -in dump.sql -out dump.enc;
    Script->>Store: upload(dump.enc)  (B3, Outscale, GCP)
    Store-->>Script: ACK
```

*Points de contrôle* : chiffrement AES‑256, vérification d’intégrité (SHA‑256), rétention 30 jours.

---

## 8️⃣ Vue Déploiement *(section standardisée)* <a id="vue-déploiement"></a>

### Environnements

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Poste développeur (Docker Desktop) | `sireines_app_dev`, `sireines_db_dev` | Loopback / Docker bridge | Volumes locaux, logs à la console |
| **Recette** | ECO4 (IaaS) – Bastion `ssh bastion` → `sireinesrec` | `sireines_app_usine_container`, `sireines_db_usine_container` | VPC 10.0.0.0/16, TLS 1.2, Nginx LB (2 instances) | Sauvegarde quotidienne, monitoring Prometheus |
| **Pré‑production** | ECO4 (IaaS) – Bastion `ssh bastion` → `sireinesppr` | Identique à Recette | Identique | Tests de charge avant prod |
| **Production** | ECO4 (IaaS) – Data‑Center Paris La Défense | `sireines_app_prod`, `sireines_db_prod`, `nginx‑lb‑prod` (2 instances) | VPC 10.100.0.0/16, TLS 1.2, firewall strict | SLA 99,5 %, sauvegarde chiffrée, alerting |

### Infrastructure

```mermaid
graph LR
    subgraph "ECO4 – IaaS"
        LB[nginx (2×) LB] -->|HTTPS| APP[Tomcat (sireines_app)]
        APP --> DB[PostgreSQL]
        APP --> BIRT[BIRT Engine]
        APP --> SMTP[SMTP (TLS)]
    end
    subgraph "Docker‑Host"
        DB -->|pg_dump| Backup[Backup Service]
    end
```

*Notes* : Le `Docker‑compose.yml` (dans `sireines-docker/`) définit les images : `tomcat:7.0.108-jdk8`, `postgres:14.1-alpine`, `dpage/pgadmin4`.  
Le reverse‑proxy Nginx est **pair‑wise** en haute disponibilité (voir `sireines-docker/Dockerfile` et `docker‑compose.yml`).

### Supervision

* **Portainer** – gestion des containers (Docker UI)  
* **Prometheus / Grafana / AlertManager** – collecte métriques (CPU, RAM, latence HTTP, DB)  
* **PSIN** – supervision ministérielle (logs agrégés)  

### Sauvegardes

| Source | Méthode | Destination | Chiffrement |
|--------|---------|-------------|-------------|
| `sireines-db` (PostgreSQL) | `pg_dump -Fc` (cron) | B3 (OVH), Outscale (SecNumCloud), Google Cloud Storage | AES