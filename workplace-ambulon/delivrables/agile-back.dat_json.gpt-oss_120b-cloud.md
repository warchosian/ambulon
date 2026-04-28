# 📘 Dossier d’Architecture Technique (DAT) – **agile‑back**  

[TOC]

---

## 1️⃣ Introduction et objectifs <a id="introduction-et-objectifs"></a>

**Agile‑back** est le back‑office de l’application *Agile* qui permet la création, la modification et le suivi d’études stockées dans une base PostgreSQL.  
Le projet est développé en **PHP 8** avec le framework **Symfony 5/6** et suit l’architecture **MVC** enrichie d’**API Platform** pour les services REST/CSV.

### Vue d’ensemble (C4‑L1)

```mermaid
graph TD
    %% System Context;
    A[Utilisateurs (front‑office)] -->|HTTP| B[Agile‑front]
    B -->|API JSON/CSV| C[agile‑back]
    C -->|JDBC| D[(PostgreSQL DB)]
    C -->|CAS auth| E[(CAS Server)]
    C -->|SMTP| F[(Mail Server)]
    C -->|Prometheus/Grafana| G[Supervision]
    style A fill:#bbf,stroke:#333,stroke-width_2px;
    style C fill:#f9f,stroke:#333,stroke-width_2px
```

### Objectifs de qualité orientés utilisateur  

| # | Objectif | Raison métier |
|---|----------|----------------|
| 1️⃣ | **Performance** – temps de réponse < 200 ms pour les écrans de création/modification d’étude | Fluidité de la saisie et satisfaction utilisateur |
| 2️⃣ | **Sécurité** – authentification CAS + protection CSRF/XSS, conformité RGPD | Protection des données sensibles de recherche |
| 3️⃣ | **Disponibilité** – 99,5 % de disponibilité mensuelle | Accès continu aux études pour les équipes opérationnelles |
| 4️⃣ | **Maintenabilité** – couverture de tests unitaires ≥ 80 % et documentation à jour | Réduction du coût de l’évolution fonctionnelle |
| 5️⃣ | **Traçabilité** – journalisation complète des actions (création, modification, suppression) | Auditabilité et conformité aux exigences réglementaires |

↩ [Retour au sommaire](#toc)

---

## 2️⃣ Parties prenantes <a id="parties-prenantes"></a>

| Rôle | Attente principale |
|------|--------------------|
| **Maîtrise d’Ouvrage (MOA)** | Livraison fonctionnelle conforme aux besoins métier (création d’études, export CSV/ODS). |
| **Maîtrise d’Œuvre (MOE)** | Architecture stable, facilité de maintenance et de déploiement continu. |
| **Utilisateurs finaux (agents, analystes)** | Interface réactive, ergonomique et fiable pour saisir et consulter les études. |
| **Administrateurs système** | Installation, mise à jour et supervision simples (Nginx, PostgreSQL, Prometheus). |
| **RSSI / DPO** | Conformité RGPD, gestion des accès, traçabilité et protection des données. |
| **Équipe Front‑office (agile‑front)** | API stable, documentation Swagger/OpenAPI à jour. |
| **Équipe de support** | Outils de diagnostic et logs détaillés pour résolution d’incidents. |

> **Contacts** – Aucun fichier JSON ne fournit de contacts nommés. La section “Contacts” reste vide pour le moment.  

↩ [Retour au sommaire](#toc)

---

## 3️⃣ Contraintes <a id="contraintes"></a>

### 3.1 Contraintes techniques  

| Type | Description |
|------|-------------|
| **Langage / Framework** | PHP 8, Symfony 5/6, Doctrine ORM, API Platform. |
| **Base de données** | PostgreSQL 13+, connexion via `DATABASE_URL`. |
| **Authentification** | CAS (phpCAS) via le composant `Security`. |
| **Serveur web** | Nginx en reverse‑proxy, PHP‑FPM. |
| **Conteneurisation** | Docker / docker‑compose (optionnel) pour dev & test. |
| **CI/CD** | GitLab CI avec stages *build*, *test*, *deploy*. |
| **Tests** | PHPUnit + Symfony Test Client, couverture ≥ 80 %. |
| **Monitoring** | Prometheus, Grafana, Loki, Alertmanager, Portainer. |
| **Sauvegarde** | Dumps PostgreSQL chiffrés AES‑256 vers B3, Outscale SecNumCloud, Google Cloud. |

### 3.2 Contraintes organisationnelles  

| Type | Description |
|------|-------------|
| **Méthodologie** | Agile (scrum) – sprints de 2 semaines, backlog partagé avec agile‑front. |
| **Livraison** | Environnements *dev*, *recette*, *production* séparés, validation manuelle en recette. |
| **Interopérabilité** | API partagée avec agile‑front, conformité OpenAPI. |
| **Gestion des versions** | GitLab monorepo, tags semver. |

### 3.3 Contraintes réglementaires  

| Type | Description |
|------|-------------|
| **RGPD** | Données à caractère personnel (email, nom) anonymisées ou chiffrées, droit à l’oubli. |
| **Sécurité** | Conformité D‑I‑C‑T (Disponibilité, Intégrité, Confidentialité, Traçabilité). |
| **Archivage** | Sauvegardes conservées 12 mois, archivage légaux. |

#### Modèle D‑I‑C‑T  

| Exigence | Implémentation |
|----------|----------------|
| **Disponibilité** | Load‑balancing Nginx, `fingers_crossed` monolog, health‑checks Prometheus. |
| **Intégrité** | Transactions Doctrine, contraintes DB (PK/FK), validation Symfony. |
| **Confidentialité** | TLS 1.2+ sur toutes les communications, chiffrement des dumps, stockage minimal des données sensibles. |
| **Traçabilité** | `AddPaginationHeaders` listener, `EtudesListener` audit, logs JSON via Monolog. |

↩ [Retour au sommaire](#toc)

---

## 4️⃣ Contexte et périmètre <a id="contexte-perimetre"></a>

### 4.1 Partenaires fonctionnels  

| Système / acteur | Rôle |
|-----------------|------|
| **agile‑front** | Consomme les API REST/CSV pour affichage UI. |
| **CAS Server** | Authentifie les utilisateurs via SSO. |
| **Mail Server** (SMTP) | Envoi de notifications d’évènements (création, modification). |
| **Supervision GTI** | Collecte métriques, alertes et logs. |
| **Stockage objet** (B3, Outscale, GCP) | Cible de sauvegarde des bases. |

### 4.2 Interfaces techniques  

| Interface | Protocole | Fréquence | Type de données |
|-----------|----------|------------|------------------|
| API agile‑back ↔ agile‑front | HTTPS/REST (JSON, CSV) | On‑demand (CRUD) | Études, métadonnées, export |
| Application ↔ CAS | HTTPS (CAS protocol) | On‑demand (login) | Ticket, attributs utilisateur |
| Application ↔ PostgreSQL | TCP (5432) | Persistant | Tables métier |
| Application ↔ Mail Server | SMTP (TLS) | Event‑driven | Emails de notification |
| Application ↔ Prometheus | HTTP (scrape) | 15 s | Métriques d’application |
| Application ↔ Loki | HTTP (push) | Asynchrone | Logs JSON |
| Application ↔ Backup scripts | Bash/PGDump | Nightly | Dumps chiffrés |

↩ [Retour au sommaire](#toc)

---

## 5️⃣ Stratégie de solution <a id="strategie-de-solution"></a>

### 5.1 Décisions architecturales majeures  

| Décision | Raison |
|----------|--------|
| **Monolithe Symfony** (pas de micro‑services) | Simplicité de déploiement, cohérence du modèle de données, faible besoin de scalabilité horizontale. |
| **API Platform** pour exposition REST/CSV | Génération automatique de documentation OpenAPI, pagination, filtres. |
| **phpCAS** pour SSO | Centralisation de l’authentification, conformité avec les exigences du ministère. |
| **Docker** en dev & test | Environnements reproductibles, isolation des dépendances. |
| **CI/CD GitLab** avec pipelines parallèles | Qualité (tests, lint), rapidité de mise en production. |
| **Prometheus + Grafana** pour métriques | Observabilité native, alerting configurable. |

### 5.2 Environnement technologique  

| Couche | Technologie |
|--------|-------------|
| **Langage** | PHP 8.2 |
| **Framework** | Symfony 5.4 / 6.x, API Platform |
| **ORM** | Doctrine ORM (PostgreSQL) |
| **Base de données** | PostgreSQL 13 (ou supérieur) |
| **Front‑end** | Twig templates + assets JS (jQuery, custom scripts) |
| **Authentification** | phpCAS + Symfony Security (firewall `main`) |
| **Web Server** | Nginx (reverse‑proxy) → PHP‑FPM |
| **CI/CD** | GitLab CI (Docker‑in‑Docker, PHPUnit, PHPStan) |
| **Tests** | PHPUnit, Symfony Test Client, Behat (optionnel) |
| **Conteneurisation** | Docker, docker‑compose (dev) |
| **Supervision** | Prometheus, Grafana, Loki, Alertmanager, Portainer |
| **Sauvegarde** | `pg_dump` + AES‑256 → B3 / Outscale SecNumCloud / GCP |

### 5.3 Outils de la forge logicielle  

| Outil | Usage |
|------|------|
| **GitLab** | Gestion du code, merge‑requests, CI/CD. |
| **Composer** | Gestion des dépendances PHP. |
| **PHPStan / Psalm** | Analyse statique. |
| **PHPUnit** | Tests unitaires & fonctionnels. |
| **Docker / docker‑compose** | Environnements isolés. |
| **Makefile** | Raccourcis de build, test, lint. |
| **Swagger UI** (via API Platform) | Documentation interactive des API. |
| **SonarQube** (optionnel) | Qualité du code et couverture. |

↩ [Retour au sommaire](#toc)

---

## 6️⃣ Vue en briques (C4‑L2) <a id="vue-en-briques"></a>

```mermaid
graph TB
    subgraph "Infrastructure"
    NGINX[Nginx (reverse‑proxy)]
    PHPFPM[PHP‑FPM (Symfony)]
    DB[(PostgreSQL)]
    CAS[(CAS Server)]
    MAIL[(SMTP Mail Server)]
    PROM[Prometheus / Grafana]
    end
    NGINX --> PHPFPM;
    PHPFPM --> DB;
    PHPFPM --> CAS;
    PHPFPM --> MAIL;
    PHPFPM --> PROM;
    subgraph "Utilisateurs"
    UI[Utilisateurs (navigateurs)]
    end
    UI --> NGINX
```

### Description des conteneurs principaux  

| Conteneur | Rôle | Principaux composants |
|-----------|------|------------------------|
| **NGINX** | Point d’entrée HTTP/HTTPS, load‑balancing, terminates TLS. | `nginx.conf` (proxy_pass → php‑fpm). |
| **PHP‑FPM (Symfony)** | Logique métier, API, rendu Twig. | `Kernel.php`, `Controller/*`, `Entity/*`, `Service/*`, `EventListener/*`. |
| **PostgreSQL** | Persistance des études, utilisateurs, référentiels. | Schéma généré par Doctrine Migrations. |
| **CAS Server** | Authentification SSO unique. | Bibliothèque `phpCAS`. |
| **SMTP Mail Server** | Envoi de notifications (création/modif d’étude). | Config `mailer.yaml`. |
| **Prometheus / Grafana** | Collecte métriques, visualisation et alertes. | Exporters `symfony/mercure`, `php-fpm-exporter`. |
| **Portainer** | Gestion des conteneurs Docker (dev/recette). | UI web. |

↩ [Retour au sommaire](#toc)

---

## 7️⃣ Vue Exécution (scénarios critiques) <a id="vue-execution"></a>

### 7.1 Scénario 1 – Authentification SSO via CAS  

```mermaid
sequencediagram;
    participant User as Utilisateur (Browser)
    participant Nginx as Nginx;
    participant PHP as PHP‑FPM (Symfony)
    participant CAS as CAS Server;
    User->>Nginx: GET /login;
    Nginx->>PHP: Forward request;
    PHP->>CAS: Redirect to CAS (service URL)
    CAS->>User: Login page;
    User->>CAS: Credentials;
    CAS->>User: Ticket (service ticket)
    User->>Nginx: GET /login?ticket=ST-xxxx;
    Nginx->>PHP: Forward ticket;
    PHP->>CAS: Validate ticket;
    CAS->>PHP: User attributes (email, name)
    PHP->>PHP: Création session Symfony;
    PHP->>User: 302 → /admin (authenticated)
```

**Points de contrôle**  
* Validation du ticket via `phpCAS`.  
* Enregistrement d’un log `security` (`INFO`) avec l’email.  
* Gestion d’erreur : ticket invalide → affichage page d’erreur.

---

### 7.2 Scénario 2 – Création d’une étude (front‑office)  

```mermaid
sequencediagram;
    participant UI as Front‑office (Angular / Twig)
    participant Nginx as Nginx;
    participant PHP as PHP‑FPM (Symfony)
    participant DB as PostgreSQL;
    participant Mail as SMTP;
    UI->>Nginx: POST /etudes (JSON)
    Nginx->>PHP: Forward request + Auth token;
    PHP->>PHP: Validation formulaire (Symfony Validator)
    PHP->>DB: INSERT Etude + relations;
    DB-->>PHP: OK (ID)
    PHP->>Mail: Send notification (new study)
    Mail-->>PHP: ACK;
    PHP->>UI: 201 Created + payload (ID)
```

**Points de contrôle**  
* Transaction Doctrine (`beginTransaction` / `commit`).  
* Enregistrement d’un audit (`EtudesListener`).  
* Retour HTTP 201 avec `Location` header.  

---

### 7.3 Scénario 3 – Export CSV d’études (API Platform)  

```mermaid
sequencediagram;
    participant UI as Client (curl / front)
    participant Nginx as Nginx;
    participant PHP as PHP‑FPM (API Platform)
    participant DB as PostgreSQL;
    UI->>Nginx: GET /api/etudes.csv?format=csv;
    Nginx->>PHP: Forward request;
    PHP->>DB: SELECT * FROM etudes …
    DB-->>PHP: Result set;
    PHP->>PHP: Serialisation CSV (DataTransformer)
    PHP->>UI: 200 OK + CSV payload
```

**Points de contrôle**  
* Limitation de taille (`max_items_per_page`).  
* Header `Content‑Disposition: attachment; filename="etudes.csv"`.  
* Log d’audit (`export_csv`).

↩ [Retour au sommaire](#toc)

---

## 8️⃣ Vue Déploiement (standardisée) <a id="vue-deploiement"></a>

### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Docker‑Compose local | 1 × Nginx, 1 × PHP‑FPM, 1 × PostgreSQL | LAN interne, ports 8080‑8082 | Hot‑reload, fixtures de test. |
| **Recette** | Cloud interne (OpenStack) | 2 × Nginx (HA), 2 × PHP‑FPM, 1 × PostgreSQL | VLAN `recette`, TLS auto‑signé | Jeux de données anonymisées, validation MOA. |
| **Production** | Cloud interne (OpenStack) | 2 × Nginx (load‑balanced), 4 × PHP‑FPM, 2 × PostgreSQL (replication) | VLAN `prod`, TLS ACM, WAF | Monitoring complet, sauvegardes cryptées, haute disponibilité. |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **Openstack**, dans le tenant **'pnm3'** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx] --> B[Application (PHP‑FPM / Symfony)]
    B --> C[Base de données (PostgreSQL)]
    B --> D[Autres services (CAS client, Mailer)]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :

- via **Portainer** pour la partie purement conteneurisée,
- via la stack **Prometheus/Grafana/Loki/AlertManager**,
- Le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

- le stockage objet **B3** du IaaS ministériel,
- le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché "Nuage Public"),
- le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché "Nuage Public").

↩ [Retour au sommaire](#toc)

---

## 9️⃣ Sujets transverses <a id="sujets-transverses"></a>

| Sujet | Traitement dans l’application |
|-------|-------------------------------|
| **Authentification** | CAS + Symfony `security.yaml` (firewall `main`, `anonymous: true`). |
| **Autorisation** | Voter `EtudesVoter` (rôles `ROLE_ADMIN`, `ROLE_USER`). |
| **Journalisation** | Monolog `handlers.main` (file en dev, `fingers_crossed` en prod), format JSON. |
| **Monitoring** | Exporter Symfony → Prometheus (`symfony/mercure`), logs vers Loki. |
| **Gestion des erreurs** | `ExceptionListener`, pages d’erreur personnalisées, logs `error`. |
| **API** | API Platform auto‑génère OpenAPI, pagination, filtres, formats JSON/CSV/HTML. |
| **Sécurité des données** | Validation des entrées, CSRF tokens (`form_start`), sanitisation Twig (`{{ var|e }}`). |
| **Internationalisation** | Bundle `translation`, fichiers `.yaml` pour messages. |
| **Export** | DataTransformers (`EtudeOutputDataTransformer`, etc.) → CSV/ODS. |
| **Déploiement** | Pipelines GitLab: `docker build`, `docker push`, `helm upgrade` (optionnel). |
| **Tests** | PHPUnit + Symfony `WebTestCase`, couverture via `phpcov`. |

↩ [Retour au sommaire](#toc)

---

## 🔟 Exigences de qualité <a id="exigences-de-qualite"></a>

| Exigence | Critère d’acceptation | Scénario de validation |
|----------|----------------------|--------------------------|
| **Performance** | Temps moyen de réponse < 200 ms pour les écrans de création/modif. | Test de charge (`k6`) sur `/etudes/new` avec 50 concurrents, mesure < 200 ms. |
| **Sécurité – CSRF** | Tous les formulaires POST possèdent un token valide. | Test fonctionnel Selenium qui soumet un formulaire sans token → 403. |
| **Sécurité – XSS** | Aucun rendu de donnée brute sans échappement. | Scan OWASP ZAP sur `/etudes/*` → aucune alerte XSS. |
| **Disponibilité** | Uptime ≥ 99,5 % sur le mois. | Monitoring Prometheus `up{job="agile-back"}` → alertes uniquement < 0,5 % du temps. |
| **Traçabilité** | Chaque action CRUD loguée avec `user`, `action`, `timestamp`. | Vérification dans Loki d’un log `action=CREATE` après création d’une étude. |
| **Maintenabilité** | Couverture de tests unitaires ≥ 80 %. | Rapport `phpcov` > 80 % sur le pipeline CI. |
| **Scalabilité** | Le service supporte le scaling horizontal (Nginx LB). | Déploiement de 4 réplicas PHP‑FPM, test de montée en charge sans perte de sessions. |
| **Conformité RGPD** | Données personnelles chiffrées en repos et en transit. | Analyse des dumps : champs `email` hashés, TLS sur toutes les connexions. |

↩ [Retour au sommaire](#toc)

---

## 1️⃣1️⃣ Risques et dettes techniques <a id="risques-et-dettes"></a>

| Risque / Dette | Impact | Probabilité | Mesure d’atténuation |
|----------------|--------|--------------|----------------------|
| **Dépendance au serveur CAS** | Indisponibilité de l’authentification. | Moyenne | Cache du ticket (TTL 5 min), fallback vers authentification locale en cas d’échec. |
| **Code legacy non testé** (ex. `public/cas/*`, scripts JS) | Bugs en production, difficultés de maintenance. | Élevée | Ajouter des tests unitaires et d’intégration, refactoriser les scripts en modules ES6. |
| **Monolithe difficile à scaler** | Saturation sous forte charge. | Faible‑Moyenne | Préparer une stratégie de découpage (ex. service Export) en micro‑service si besoin. |
| **Manque de couverture de tests** | Régression non détectée. | Moyenne | Obligation de 80 % de couverture, gate de pipeline. |
| **Mise à jour de dépendances (Symfony, phpCAS)** | Breakage de compatibilité. | Moyenne | Utiliser `composer.lock`, tests de migration automatisés. |
| **Sauvegardes non vérifiées** | Perte de données. | Faible | Tests de restauration mensuels automatisés. |
| **Exposition de logs sensibles** | Fuite d’informations. | Faible | Masquage des champs sensibles dans Monolog (`mask_fields`). |

↩ [Retour au sommaire](#toc)

---

## 1️⃣2️⃣ Annexes <a id="annexes"></a>

### 📚 Glossaire  

| Terme | Définition |
|-------|------------|
| **CAS** | Central Authentication Service – protocole SSO. |
| **API Platform** | Extension Symfony générant automatiquement des API REST/GraphQL. |
| **Doctrine Migrations** | Gestion versionnée du schéma de base de données. |
| **PSIN** | Plateforme de Supervision Interne du GTI. |
| **B3** | Stockage objet du IaaS ministériel (backup). |
| **Outscale SecNumCloud** | Service de stockage certifié pour les données sensibles. |
| **Prometheus** | Système de collecte de métriques time‑series. |
| **Loki** | Agrégateur de logs compatible Grafana. |
| **ADR** | Architecture Decision Record – décision enregistrée. |

### 📄 Décisions d’architecture (ADR) – Extraits  

| # | Décision | Statut |
|---|----------|--------|
| **ADR‑001** | Adoption de Symfony 5.4 comme framework principal (LTS). | ✅ Adoptée |
| **ADR‑002** | Utilisation de **phpCAS** pour SSO au lieu d’un JWT interne. | ✅ Adoptée |
| **ADR‑003** | Choix d’un **monolithe** plutôt que micro‑services. | ✅ Adoptée |
| **ADR‑004** | Export CSV via **API Platform** DataTransformer. | ✅ Adoptée |
| **ADR‑005** | Backup automatisé avec `pg_dump` + AES‑256. | ✅ Adoptée |
| **ADR‑006** | Monitoring via **Prometheus + Grafana** (standard GTI). | ✅ Adoptée |
| **ADR‑007** | Utilisation de **Docker‑compose** en dev uniquement. | ✅ Adoptée |

---

*Document généré le **28 avril 2026** – prêt à être versionné dans le dépôt GitLab du projet.*  

↩ [Retour au sommaire](#toc)