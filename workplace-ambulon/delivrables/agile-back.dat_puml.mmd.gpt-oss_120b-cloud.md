# 📘 Dossier d’Architecture Technique (DAT) – **agile‑back**  

> **Version** : 1.0 – 2024‑04‑28  
> **Auteur** : Équipe d’architecture – Projet Agile  

[TOC]

---  

## 1️⃣ Introduction et objectifs {#introduction}

**Agile‑back** est le back‑office de la solution *Agile* : il permet la création, la modification et le suivi d’études stockées dans une base PostgreSQL. L’application est développée en PHP / Symfony (MVC) et expose des API REST via API Platform pour le front‑office *Agile‑front*.  

### 1.1 Vue fonctionnelle (C4‑L1)

```mermaid
graph LR
    subgraph Utilisateurs;
        U1[Administrateur] 
        U2[Utilisateur métier] 
        U3[Auditeur / RSSI]
    end
    subgraph Systèmes externes;
        CAS[CAS Authentication Server]
        SMTP[Serveur SMTP (mail)]
        DB[PostgreSQL DB]
        FE[Agile‑front (Angular/React)]
    end
    NGINX[Nginx Reverse‑Proxy] --> PHP[Symfony (agile‑back)]
    PHP --> DB;
    PHP --> CAS;
    PHP --> SMTP;
    PHP --> FE;
    U1 -->|Navigue UI| NGINX;
    U2 -->|Navigue UI| NGINX;
    U3 -->|Audit & supervision| NGINX;
    FE -->|Appels API| NGINX
```

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif | Indicateur |
|---|-----------|------------|
| 1 | **Performance** – temps de réponse < 200 ms pour les écrans de saisie | Tests de charge (JMeter) |
| 2 | **Sécurité** – conformité RGPD & OWASP Top 10 | Audits trimestriels, D‑I‑C‑T |
| 3 | **Disponibilité** – 99,9 % de disponibilité mensuelle | Monitoring (Prometheus) |
| 4 | **Maintenabilité** – couverture de tests unitaires ≥ 80 % | SonarQube |
| 5 | **Évolutivité** – capacité à ajouter 2 000 études/jour sans dégradation | Tests de scalabilité |

↩︎ [Retour au sommaire](#toc)

---  

## 2️⃣ Parties prenantes {#parties-prenantes}

| Rôle | Attente principale |
|------|--------------------|
| **MOA (Maître d’Ouvrage)** | Fonctionnalités métier conformes aux processus d’études |
| **Développeurs** | Code lisible, tests automatisés, CI/CD fiable |
| **Administrateurs système** | Installation simple, monitoring, sauvegardes automatisées |
| **Utilisateurs métier** | Interface réactive, accès aux données en temps réel |
| **RSSI / Auditeur sécurité** | Traçabilité, contrôle d’accès, conformité RGPD |
| **Équipe DevOps** | Pipeline GitLab CI, déploiement automatisé sur OpenStack |
| **Support fonctionnel** | Documentation claire, FAQ intégrée |

> Aucun fichier `applicationsIA_mini_agile-back.md` n’est fourni ; aucune section « Contacts » n’est ajoutée.

↩︎ [Retour au sommaire](#toc)

---  

## 3️⃣ Contraintes {#contraintes}

### 3.1 Techniques  

| Type | Description |
|------|-------------|
| **Langage** | PHP ≥ 8.1, Symfony 5.4 (LTS) |
| **Base de données** | PostgreSQL 13 + extensions `uuid-ossp` |
| **Authentification** | CAS (phpCAS) – fédération avec le serveur d’identité du ministère |
| **Messagerie** | Swiftmailer → SMTP (TLS) |
| **Cache** | Doctrine 2nd‑level cache (Redis) – optionnel |
| **Conteneurisation** | Docker (Docker‑Compose) – images officielles php‑fpm, nginx, postgres, redis |
| **CI/CD** | GitLab CI, tests PHPUnit, linting PHP‑CS-Fixer, SonarQube |
| **Infrastructure** | OpenStack (tenant `pnm3`), reverse‑proxy Nginx load‑balanced |

### 3.2 Organisationnelles  

* Respect du planning de mise en production mensuel.  
* Processus de revue de code obligatoire (Merge Request).  

### 3.3 Réglementaires  

* **RGPD** – anonymisation des données personnelles (email, nom).  
* **ISO 27001** – exigences de traçabilité (journalisation).  

### 3.4 Sécurité (modèle D‑I‑C‑T)

| Aspect | Exigence |
|--------|----------|
| **Disponibilité** | Redondance du reverse‑proxy (2 instances Nginx) |
| **Intégrité** | Signatures numériques sur les artefacts de déploiement |
| **Confidentialité** | TLS 1.2+ sur toutes les communications (HTTPS, LDAPS) |
| **Traçabilité** | Logs centralisés (ELK) – chaque action utilisateur inclut `user_id`, `action`, `timestamp` |

↩︎ [Retour au sommaire](#toc)

---  

## 4️⃣ Contexte et périmètre {#contexte}

### 4.1 Systèmes partenaires  

| Système | Type d’interaction | Protocole / Fréquence |
|---------|-------------------|------------------------|
| **Agile‑front** | Consommation d’API REST (CRUD études) | HTTP/HTTPS – à la demande |
| **CAS Server** | Authentification unique | HTTP/HTTPS – flux de login/logout |
| **SMTP** | Envoi de notifications | SMTP/TLS – événementiel |
| **PostgreSQL** | Persistance des entités métier | JDBC (Doctrine) – transactionnelle |
| **GitLab CI** | Build & déploiement automatisés | API GitLab – pipeline déclenché à chaque commit |
| **Monitoring (Prometheus/Grafana)** | Collecte métriques | Pull (scrape) – chaque minute |

### 4.2 Périmètre fonctionnel  

* Gestion des **Études** (CRUD, import/export CSV/ODS).  
* Gestion des **Financements**, **Dotations**, **BOP**, **Groupes**, **Thèmes**, **Profils**.  
* Gestion des **Utilisateurs** et de leurs **rôles**.  
* Envoi d’emails de notification (création/modification d’étude).  
* Export de rapports (CSV, ODS).  

↩︎ [Retour au sommaire](#toc)

---  

## 5️⃣ Stratégie de solution {#strategie}

| Décision | Raison |
|----------|--------|
| **Monolithe Symfony** (bundles) | Simplicité de déploiement, cohérence du modèle MVC, riche écosystème (API Platform, Doctrine). |
| **API Platform** pour l’exposition des API | Génération automatique de la documentation OpenAPI, pagination, filtres. |
| **phpCAS** comme client d’authentification | Conformité aux exigences ministérielles d’authentification unique. |
| **Docker** (Docker‑Compose) | Isolation des dépendances, portabilité entre environnements (dev, test, prod). |
| **PostgreSQL** comme SGBD | Fiabilité, support des contraintes d’intégrité référentielle, performances de requêtes complexes. |
| **CI/CD GitLab** | Automatisation du build, des tests, du scan de sécurité (SAST) et du déploiement. |
| **Monitoring standard GTI** (Prometheus/Grafana/Loki) | Visibilité opérationnelle et alerte en temps réel. |
| **Sauvegardes chiffrées AES‑256** | Conformité RGPD et exigences de continuité d’activité. |

### 5.1 Stack technique  

| Couche | Technologie |
|--------|-------------|
| **Web** | Nginx (reverse‑proxy) + PHP‑FPM (Symfony) |
| **Application** | Symfony 5.4, API Platform, Doctrine ORM, Twig, Swiftmailer |
| **Authentification** | phpCAS (CAS v1.3.5) |
| **Base de données** | PostgreSQL 13 |
| **Cache** | Redis (optionnel) |
| **Message Queue** | Aucun (synchronisation) |
| **CI/CD** | GitLab CI, Docker, Composer, PHPUnit, SonarQube |
| **Infrastructure** | OpenStack (tenant `pnm3`), stockage objet B3, Outscale SecNumCloud, Google Cloud |

↩︎ [Retour au sommaire](#toc)

---  

## 6️⃣ Vue en Briques (C4‑L2) {#vue-briques}

```mermaid
graph TB
    subgraph "Infrastructure OpenStack"
        NGINX[Nginx Load‑Balancer] 
        PHPFPM[PHP‑FPM (Symfony)] 
        POSTGRES[PostgreSQL] 
        REDIS[Redis] 
        SMTP[SMTP Relay] 
        CAS[CAS Server (ext.)]
    end
    NGINX --> PHPFPM;
    PHPFPM --> POSTGRES;
    PHPFPM --> REDIS;
    PHPFPM --> SMTP;
    PHPFPM --> CAS;
    NGINX -->|HTTPS| Users[Utilisateurs / Admins]
    Users -->|API calls| NGINX
```

### 6.1 Description des conteneurs  

| Conteneur | Rôle | Principaux artefacts |
|-----------|------|----------------------|
| **Nginx** | Point d’entrée unique, TLS termination, load‑balancing | `nginx.conf`, certificats |
| **PHP‑FPM (Symfony)** | Logique métier, API, rendu Twig | `src/`, `config/`, `templates/` |
| **PostgreSQL** | Persistance des entités | Schéma généré par Doctrine Migrations |
| **Redis** (optionnel) | Cache de requêtes Doctrine, session store | `redis.conf` |
| **SMTP** | Envoi d’emails transactionnels | `swiftmailer.yaml` |
| **CAS** | Authentification SSO via phpCAS | Bibliothèque `public/cas/` |

↩︎ [Retour au sommaire](#toc)

---  

## 7️⃣ Vue Exécution {#vue-execution}

### 7.1 Scénario 1 – Authentification & création d’une étude  

```mermaid
sequencediagram;
    participant User as Utilisateur;
    participant Nginx as Nginx LB;
    participant App as Symfony (agile-back)
    participant CAS as CAS Server;
    participant DB as PostgreSQL;
    participant Mail as SMTP;
    User->>Nginx: GET /etudes (HTTPS)
    Nginx->>App: Forward request;
    App->>CAS: Redirect to login (CAS ticket request)
    CAS-->>User: Formulaire login;
    User->>CAS: Submit credentials;
    CAS-->>App: Ticket + user attributes;
    App->>App: Validation du ticket (phpCAS)
    App->>DB: INSERT new Etude;
    App->>Mail: SEND notification;
    Mail-->>User: Email de confirmation;
    App-->>Nginx: 200 OK + page;
    Nginx-->>User: Rendered page
```

### 7.2 Scénario 2 – Job de mise à jour des abonnements (commande console)  

```mermaid
sequencediagram;
    participant Scheduler as Cron / GitLab Runner;
    participant Cmd as SiteUpdateAbonnementsRunner;
    participant App as Symfony (service)
    participant DB as PostgreSQL;
    Scheduler->>Cmd: exec every 00_00;
    Cmd->>App: invoke SiteUpdateAbonnements;
    App->>DB: SELECT abonnements en attente;
    App->>DB: UPDATE statut / dates;
    App->>App: Log opération
```

### 7.3 Scénario 3 – Consommation d’API depuis *Agile‑front*  

```mermaid
sequencediagram;
    participant Front as Agile‑front (SPA)
    participant Nginx as Nginx LB;
    participant API as Symfony API (API‑Platform)
    participant DB as PostgreSQL;
    Front->>Nginx: GET /api/etudes?per_page=20;
    Nginx->>API: Forward request (Bearer token)
    API->>DB: SELECT * FROM etudes LIMIT 20;
    DB-->>API: Result set;
    API-->>Nginx: JSON payload;
    Nginx-->>Front: 200 OK + data
```

↩︎ [Retour au sommaire](#toc)

---  

## 8️⃣ Vue Déploiement *(section standardisée)* {#vue-deploiement}

### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|------------|----------|--------|------------------|
| Développement | Docker‑Compose local | 1 x Nginx, 1 x PHP‑FPM, 1 x Postgres, 1 x Redis | localhost | Hot‑reload, fixtures de test |
| Recette | OpenStack – tenant `pnm3` | 2 x Nginx HA, 2 x PHP‑FPM, 1 x Postgres, 1 x Redis | VLAN interne | Jeux de données anonymisées |
| Production | OpenStack – tenant `pnm3` | 2 x Nginx LB, 4 x PHP‑FPM, 2 x Postgres en réplication, 1 x Redis | VLAN dédié, DMZ | TLS 1.3, sauvegardes chiffrées, monitoring |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant **`pnm3`** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
@startuml
node "Nginx (LB)" as A
component "Application (Symfony)" as B
database "Base de données (PostgreSQL)" as C
component "Cache (Redis)" as D
component "SMTP Relay" as E
component "CAS Client (phpCAS)" as F

A --> B
B --> C
B --> D
B --> E
B --> F
@enduml
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :

- via **Portainer** pour la partie purement conteneurisée,  
- via la stack **Prometheus/Grafana/Loki/AlertManager**,  
- Le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

- le stockage objet **B3** du IaaS ministériel,  
- le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché « Nuage Public »),  
- le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché « Nuage Public »).

↩︎ [Retour au sommaire](#toc)

---  

## 9️⃣ Sujets transverses {#transverses}

| Thématique | Implémentation |
|------------|----------------|
| **Authentification** | phpCAS, tickets CAS, session Symfony, durée de session 30 min, renouvellement SSO. |
| **Journalisation** | Monolog (handler `stream` en dev, `fingers_crossed` + `json` en prod), champs `user_id`, `action`, `ip`, `request_id`. |
| **Monitoring** | Exporter metrics (`prometheus_bundle`), alertes sur latence > 500 ms, erreurs 5xx, utilisation CPU. |
| **Gestion des erreurs** | Exceptions personnalisées (`App\Exception\*`), `ExceptionListener` → réponses JSON standardisées. |
| **API** | API Platform, pagination, filtres, versionnage (`/api/v1/`), documentation OpenAPI auto‑générée. |
| **Sécurité** | CSP, HSTS, X‑Content‑Type‑Options, CSRF tokens (Twig), validation des entrées (Symfony Validator). |
| **Internationalisation** | `translations/` (messages.fr.yaml, messages.en.yaml), support UTF‑8. |
| **Tests** | PHPUnit (unit + functional), Behat (BDD) pour scénarios métier, coverage > 80 %. |
| **CI/CD** | GitLab CI pipelines : `lint`, `test`, `security:sast`, `docker:build`, `deploy`. |
| **Gestion de la configuration** | Variables d’environnement (`.env`), secrets via GitLab CI variables, `config/packages/*.yaml`. |

↩︎ [Retour au sommaire](#toc)

---  

## 🔟 Exigences de qualité {#exigences-qualite}

| Exigence | Critère d’acceptation | Méthode de validation |
|----------|----------------------|------------------------|
| **Performance** | Temps de réponse < 200 ms (95 % des requêtes) | Tests de charge JMeter, monitoring temps réel |
| **Sécurité** | Pas de vulnérabilités OWASP Top 10 détectées | Scan SAST (GitLab), tests d’intrusion annuels |
| **Disponibilité** | 99,9 % de disponibilité mensuelle | KPI Prometheus `up{job="agile-back"}` |
| **Scalabilité** | Gestion de 2 000 études/jour sans dépassement de 70 % CPU | Tests de montée en charge, simulation de pic |
| **Maintenabilité** | Couverture de tests ≥ 80 % | Rapport SonarQube |
| **Traçabilité** | Chaque action utilisateur journalisée avec `user_id` | Requête d’audit sur les logs |
| **Conformité RGPD** | Données personnelles chiffrées au repos, droit à l’oubli implémenté | Tests fonctionnels sur anonymisation |
| **Portabilité** | Déploiement identique sur dev, recette, prod via Docker‑Compose | Validation du pipeline CI/CD |

↩︎ [Retour au sommaire](#toc)

---  

## 1️⃣1️⃣ Risques et dettes techniques {#risques}

| Risque / Dette | Impact | Mesure corrective / atténuation |
|----------------|--------|---------------------------------|
| **Dépendance phpCAS** (bibliothèque peu maintenue) | Risque de vulnérabilité ou incompatibilité future | Plan de migration vers **OAuth2 / OpenID Connect** (Keycloak) dans 12 mois. |
| **Couverture de tests insuffisante** (legacy code) | Régression fonctionnelle | Augmenter la couverture à 80 % via tests unitaires et fonctionnels. |
| **Monolithe difficile à scaler** | Saturation du serveur PHP‑FPM | Introduire le découpage en micro‑services pour les traitements batch (ex. : export CSV). |
| **Migrations de schéma DB** (absence de versionnage strict) | Perte de données en prod | Utiliser **Doctrine Migrations** systématiquement, CI vérifiant les migrations. |
| **Configuration manuelle du reverse‑proxy** | Erreurs de routage en prod | Automatiser via **Ansible** ou **Terraform** le provisioning Nginx. |
| **Stockage des secrets en clair** | Violation de la politique de sécurité | Centraliser les secrets dans **GitLab CI variables** et **HashiCorp Vault**. |
| **Obsolescence de PHP 7.x** (si migration tardive) | Fin de support, failles non corrigées | Plan de migration vers PHP 8.2 avant fin 2025. |

↩︎ [Retour au sommaire](#toc)

---  

## 1️⃣2️⃣ Annexes {#annexes}

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **CAS** | Central Authentication Service – protocole d’authentification unique. |
| **API Platform** | Framework Symfony pour la création d’API REST/GraphQL. |
| **DTO** | Data Transfer Object – objets de transport de données (ex. : `EtudeOutput`). |
| **ADR** | Architectural Decision Record – décision d’architecture formalisée. |
| **RGPD** | Règlement Général sur la Protection des Données. |
| **GTI** | Groupe Technique Informatique (responsable de l’infrastructure). |
| **SAST** | Static Application Security Testing. |
| **CI/CD** | Intégration Continue / Déploiement Continu. |

### 12.2 Décisions d’Architecture (ADR)  

| ADR # | Décision | Contexte | Conséquence |
|-------|----------|----------|-------------|
| **ADR‑001** | Utiliser **Symfony 5.4 LTS** comme framework principal. | Besoin d’un framework mature, riche ecosysteme. | Garantie de support long terme, facilité d’intégration de bundles. |
| **ADR‑002** | Exposer les services métier via **API Platform**. | Nécessité d’un front‑office moderne (Agile‑front). | Documentation OpenAPI automatique, pagination et filtres out‑of‑the‑box. |
| **ADR‑003** | Authentifier les utilisateurs via **CAS** (phpCAS). | Conformité aux exigences ministérielles d’authentification unique. | Dépendance à une bibliothèque externe, futur plan de migration envisagé. |
| **ADR‑004** | Conteneuriser l’application avec **Docker** et **Docker‑Compose**. | Environnements multiples (dev, test, prod) doivent être reproductibles. | Simplifie le déploiement, nécessite la gestion du réseau Docker. |
| **ADR‑005** | Centraliser la journalisation avec **Monolog** + **ELK**. | Besoin de traçabilité et d’audit. | Logs structurés, coût de gestion de la stack ELK. |

---  

*Fin du Dossier d’Architecture Technique – agile‑back*  



↩︎ [Retour au sommaire](#toc)  



---  



**Note** : Ce DAT a été rédigé de façon générique à partir de l’arborescence du projet et des conventions Symfony. Toute information supplémentaire (ex. : diagrammes détaillés, paramètres d’infrastructure) pourra être ajoutée en fonction des besoins spécifiques du projet.  



---  



*Document compatible avec VS Code, Obsidian et tout visualiseur Markdown supportant Mermaid.*