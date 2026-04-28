# 📘 Dossier d’Architecture Technique (DAT) – **agile‑env**  

[TOC]

---  

## 1️⃣ Introduction et objectifs <a id="section-intro"></a>

**Vue d’ensemble fonctionnelle**  
*agile‑env* est une application web PHP 7.3, servie par Apache et persistant les données dans PostgreSQL 11. Elle est packagée et déployée via Docker (images séparées pour l’application et la base de données) et orchestrée en local avec un `docker‑compose.dev.yml`.  

```mermaid
C4Context;
    title Contexte C4 – Niveau 1 (Vue système)
    Person(user, "Utilisateur", "Consomme les services web de l’application")
    System_Boundary(agileEnv, "agile‑env") {
        Container(app, "Application PHP/Apache", "Docker", "Expose les APIs et l’interface web")
        Container(db, "Base de données PostgreSQL", "Docker", "Stocke les données métier")
    }
    System_Ext(externalCAS, "CAS (Central Authentication Service)", "Service d’authentification externe")
    Rel(user, app, "Utilise")
    Rel(app, db, "Lit/écrit des données")
    Rel(app, externalCAS, "Authentifie les utilisateurs via")
```

### Objectifs de qualité orientés utilisateur  

| # | Objectif | Raison d’usage |
|---|----------|----------------|
| 1 | **Performance** – temps de réponse < 2 s pour les pages critiques | Garantir une expérience fluide |
| 2 | **Sécurité** – authentification forte, chiffrement des communications | Protéger les données sensibles et se conformer aux exigences D‑I‑C‑T |
| 3 | **Disponibilité** – 99,5 % de disponibilité en production | Assurer la continuité de service |
| 4 | **Maintenabilité** – code découpé en conteneurs, CI/CD automatisée | Faciliter les évolutions et corrections |
| 5 | **Observabilité** – métriques, logs et traces centralisés | Détecter rapidement les incidents |

↩ [Retour au sommaire](#table-of-contents)

---  

## 2️⃣ Parties prenantes <a id="section-stakeholders"></a>

| Rôle | Attente principale |
|------|---------------------|
| **Maîtrise d’Ouvrage (MOA)** | Fonctionnalités métier conformes aux besoins utilisateurs |
| **Développeur·euse(s)** | Environnement de dev reproductible, pipeline CI/CD fiable |
| **Exploiteur·trice(s) (Ops)** | Déploiement sans friction, monitoring et sauvegarde automatisés |
| **Responsable Sécurité (RSSI)** | Conformité aux exigences de sécurité (D‑I‑C‑T) |
| **Utilisateur·trice(s) final(e)s** | Interface réactive, expérience utilisateur stable |

> Aucun contact nommé n’est présent dans les sources ; la section **Contacts** reste vide.

↩ [Retour au sommaire](#table-of-contents)

---  

## 3️⃣ Contraintes <a id="section-constraints"></a>

### 3.1 Contraintes techniques  

| Domaine | Description |
|---------|-------------|
| **Plateforme** | Docker ≥ 20.10, Docker‑Compose ≥ 1.29 |
| **Langage** | PHP 7.3 (EOL 2022 → maintenance uniquement) |
| **Web‑server** | Apache 2.4 avec configuration `000-default.conf` |
| **Base de données** | PostgreSQL 11‑alpine |
| **Proxy** | Nginx en front (load‑balancing) – décrit dans la Vue Déploiement |
| **CI/CD** | GitLab CI (pipeline → build, test, push) |
| **Gestion des secrets** | Fichier `.env` (non versionné) + variables d’environnement Docker |
| **Proxy d’entreprise** | `http_proxy` / `https_proxy` configurés dans le Dockerfile |

### 3.2 Contraintes organisationnelles  

* Déploiement uniquement sur le cloud interne **ECO4** (OpenStack).  
* Respect du processus de mise en production du GTI (validation, recette).  

### 3.3 Contraintes réglementaires  

| Référence | Exigence |
|-----------|----------|
| **RGPD** | Protection des données à caractère personnel (confidentialité) |
| **D‑I‑C‑T** | <ul><li>**Disponibilité** : SLA 99,5 % en prod</li><li>**Intégrité** : sauvegarde et vérification des dumps</li><li>**Confidentialité** : chiffrement AES‑256 des sauvegardes</li><li>**Traçabilité** : logs centralisés via Loki/Prometheus</li></ul> |

↩ [Retour au sommaire](#table-of-contents)

---  

## 4️⃣ Contexte et périmètre <a id="section-context"></a>

### 4.1 Partenaires fonctionnels  

| Nom | Type | Rôle |
|-----|------|------|
| **CAS** | Service d’authentification externe | Authentifie les utilisateurs via le fichier `config_CAS.php` |
| **Système de supervision GTI** | Outil de monitoring | Collecte métriques, logs et alertes |
| **Stockage objet B3 / Outscale / GCP** | Services de sauvegarde | Cible de stockage des dumps chiffrés |

### 4.2 Interfaces techniques  

| Interface | Protocole | Fréquence | Données |
|----------|-----------|-----------|---------|
| **App ↔ DB** | TCP (PostgreSQL) | À chaque requête | SQL (CRUD) |
| **App ↔ CAS** | HTTPS (REST) | À chaque login | Jetons SAML / JWT |
| **App ↔ Nginx** | HTTP/HTTPS | Continu | Requêtes HTTP |
| **App ↔ Supervision** | HTTP (Prometheus scrape) | 15 s | Métriques (CPU, RAM, latence) |
| **Backup ↔ Stockage** | SFTP/HTTPS | Quotidien | Dump SQL chiffré (AES‑256) |

↩ [Retour au sommaire](#table-of-contents)

---  

## 5️⃣ Stratégie de solution <a id="section-strategy"></a>

### 5.1 Décisions architecturales majeures  

| Décision | Raison |
|----------|--------|
| **Conteneurisation (Docker)** | Isolation, portabilité, reproducibilité |
| **Séparation des responsabilités** – un conteneur *app* (PHP/Apache) et un conteneur *db* (PostgreSQL) | Facilite le scaling et la maintenance |
| **Utilisation de Composer** (stage `composer`) | Gestion fiable des dépendances PHP |
| **Proxy Nginx en front** | Load‑balancing, terminaison TLS, centralisation du point d’entrée |
| **CI/CD GitLab** | Automatisation du build, tests unitaires, déploiement |

### 5.2 Environnement technologique  

| Couche | Technologie | Version / Détails |
|--------|--------------|--------------------|
| **Frontend** | HTML + CSS + JS (aucun framework spécifique) | – |
| **Backend** | PHP 7.3, Apache 2.4, Composer | Extensions : `pdo`, `pdo_pgsql`, `intl` |
| **DB** | PostgreSQL 11‑alpine | Scripts d’initialisation `initdb/*.sql` |
| **Conteneurs** | Docker 20.10+, Docker‑Compose | `docker-compose.dev.yml` (dev), `docker-compose.prod.yml` (non fourni) |
| **CI/CD** | GitLab CI | Jobs : `build`, `test`, `push`, `deploy` |
| **Monitoring** | Prometheus + Grafana + Loki + Alertmanager | Exporters intégrés dans les images |
| **Sauvegarde** | Scripts POSIX `restore.sh` + `pg_dump` | Chiffrement AES‑256, stockage multi‑cloud |

### 5.3 Outils de la forge logicielle  

| Outil | Usage |
|-------|-------|
| **GitLab** | Repos Git, gestion des merge‑requests, CI/CD |
| **Dockerfile‑app** | Build de l’image application |
| **Dockerfile‑db** | Build de l’image PostgreSQL avec scripts d’initialisation |
| **docker‑compose.dev.yml** | Orchestration locale (dev) |
| **Composer** | Gestion des dépendances PHP |
| **Portainer** | Gestion/visualisation des conteneurs en production |
| **Prometheus / Grafana** | Monitoring et dashboards |
| **Loki** | Agrégation des logs |
| **Alertmanager** | Gestion des alertes |

↩ [Retour au sommaire](#table-of-contents)

---  

## 6️⃣ Vue en Briques (C4‑L2) <a id="section-containers"></a>

```mermaid
C4Container;
    title Vue Conteneurs – Niveau 2 (C4)
    Container(app, "agile‑env‑app", "Docker (php_7.3‑apache)", "Serveur web PHP/Apache")
    ContainerDb(db, "agile‑env‑db", "Docker (postgres_11‑alpine)", "Base de données PostgreSQL")
    Container_Ext(cas, "CAS", "External Service", "Authentification SSO")
    Container_Ext(nginx, "Nginx Load‑Balancer", "Docker / VM", "Reverse‑proxy, TLS termination")
    Rel(app, db, "JDBC/SQL")
    Rel(app, cas, "HTTPS (SAML/JWT)")
    Rel(nginx, app, "HTTP")
    Rel(nginx, db, "TCP (optional health‑check)")
```

### Description des conteneurs  

| Conteneur | Responsabilité principale |
|-----------|---------------------------|
| **agile‑env‑app** | Serveur web Apache, exécution du code PHP, gestion des requêtes HTTP, connexion à la DB, appel au CAS |
| **agile‑env‑db** | Instance PostgreSQL 11, persistance des données métier, scripts d’initialisation (`initdb/*.sql`) |
| **Nginx** (front) | Load‑balancing, terminaison TLS, redirection vers le conteneur `app` |
| **CAS** (externe) | Authentification unique (SSO) via le module `config_CAS.php` |

↩ [Retour au sommaire](#table-of-contents)

---  

## 7️⃣ Vue Exécution <a id="section-runtime"></a>

### Scénario critique 1 – Authentification utilisateur  

```mermaid
sequencediagram;
    participant User as Utilisateur;
    participant Nginx as Nginx LB;
    participant App as agile‑env‑app;
    participant CAS as CAS (SSO)

    User->>Nginx: GET /login;
    Nginx->>App: Forward request;
    App->>CAS: Redirige vers /cas/login (SAML request)
    CAS-->>User: Formulaire d’authentification;
    User->>CAS: Credentials;
    CAS-->>App: Assertion SAML (token)
    App->>App: Crée session PHP;
    App-->>User: Page d’accueil (cookie de session)
```

### Scénario critique 2 – Enregistrement d’un nouveau formulaire  

```mermaid
sequencediagram;
    participant User as Utilisateur;
    participant Nginx as Nginx LB;
    participant App as agile‑env‑app;
    participant DB as PostgreSQL;
    User->>Nginx: POST /formulaire;
    Nginx->>App: Forward request;
    App->>App: Validation des données;
    App->>DB: INSERT INTO table_formulaire (...)
    DB-->>App: OK / ID généré;
    App-->>User: Confirmation (200)
```

### Scénario critique 3 – Sauvegarde quotidienne (automatisée)  

```mermaid
sequencediagram;
    participant Scheduler as Cron (container)
    participant DB as PostgreSQL;
    participant Script as restore.sh;
    participant Storage as Object Store (B3/Outscale/GCP)

    Scheduler->>DB: pg_dump --format=custom > dump.sql;
    DB-->>Scheduler: dump.sql;
    Scheduler->>Script: encrypt AES‑256 (dump.sql)
    Script-->>Scheduler: dump.sql.enc;
    Scheduler->>Storage: upload dump.sql.enc;
    Storage-->>Scheduler: ACK
```

↩ [Retour au sommaire](#table-of-contents)

---  

## 8️⃣ Vue Déploiement *(section standardisée)* <a id="section-deployment"></a>

### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | Cloud interne ECO4 (tenant `pnm3`) | 1 x Nginx LB, 1 x conteneur app, 1 x conteneur db | VLAN dev | Docker‑Compose local, logs en mode debug |
| Recette       | Cloud interne ECO4 (tenant `pnm3`) | 2 x Nginx LB (HA), 2 x conteneur app, 1 x conteneur db | VLAN recette | Jeux de données anonymisées, tests d’intégration automatisés |
| Production    | Cloud interne ECO4 (tenant `pnm3`) | 2 x Nginx LB (HA), 3 x conteneur app, 2 x conteneur db (replication) | VLAN prod | TLS 1.3, sauvegardes chiffrées, monitoring complet |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **Openstack**, dans le tenant `pnm3` du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD;
    A[Nginx Load‑Balancer] --> B[agile‑env‑app]
    B --> C[PostgreSQL DB]
    B --> D[Autres services (ex. job‑scheduler)]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :
- via **Portainer** pour la partie purement conteneurisée,
- via la stack **Prometheus / Grafana / Loki / AlertManager**,
- Le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :
- le stockage objet **B3** du IaaS ministériel,
- le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché « Nuage Public »),
- le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché « Nuage Public »).

↩ [Retour au sommaire](#table-of-contents)

---  

## 9️⃣ Sujets transverses <a id="section-crosscutting"></a>

| Sujet | Description | Implémentation |
|-------|-------------|----------------|
| **Authentification** | SSO via CAS, jetons SAML/JWT | `config_CAS.php`, session PHP sécurisée |
| **Autorisation** | Rôles simples (admin, user) stockés en DB | Middleware PHP |
| **Journalisation** | Logs d’accès Apache, logs applicatifs via Monolog | Export vers Loki |
| **Monitoring** | Métriques Prometheus (CPU, RAM, latence HTTP) | Exporter intégré dans les images |
| **Gestion des erreurs** | Gestion centralisée via `error_handler.php` (non fourni) | Retour HTTP 4xx/5xx + logs |
| **API** | Endpoints RESTful (ex. `/api/v1/...`) | Documentés via OpenAPI (à venir) |
| **Sécurité réseau** | TLS terminée au Nginx, firewall OpenStack | SG OpenStack, liste blanche IP interne |
| **CI/CD** | Pipelines GitLab automatisés (build, test, scan SAST) | `.gitlab-ci.yml` (non fourni) |
| **Configuration** | Variables d’environnement (`.env`) – non versionnées | Montées dans Docker Compose |
| **Internationalisation** | Support `intl` PHP, fichiers de traduction | `locale/` (à implémenter) |

↩ [Retour au sommaire](#table-of-contents)

---  

## 🔟 Exigences de qualité <a id="section-quality"></a>

| Exigence | Critère d’acceptation | Scénario de validation |
|----------|----------------------|-------------------------|
| **Performance** | ≤ 2 s de temps de réponse pour 95 % des requêtes HTTP | Tests de charge (`k6` ou `JMeter`) sur l’environnement de recette |
| **Sécurité – Confidentialité** | Données en transit chiffrées TLS 1.3 ; sauvegardes AES‑256 | Analyse SSL Labs, vérification du script de backup (checksum + déchiffrement test) |
| **Disponibilité** | SLA ≥ 99,5 % sur les 30 jours glissants | Monitoring uptime via Prometheus + alertes d’indisponibilité |
| **Intégrité** | Vérification des checksums des dumps après restauration | Test de restauration automatisé dans l’environnement de pré‑prod |
| **Traçabilité** | Log complet de chaque action critique (login, écriture DB) | Requête Grafana/Loki pour trace d’un scénario de création d’enregistrement |
| **Scalabilité** | Possibilité d’ajouter un conteneur `app` sans downtime | Déploiement d’un 3ᵉ conteneur en prod, mesure du temps de mise à jour du load‑balancer |
| **Maintenabilité** | Couverture de tests unitaires ≥ 70 % | Exécution du job `test` dans GitLab CI, rapport de couverture |

↩ [Retour au sommaire](#table-of-contents)

---  

## 1️⃣1️⃣ Risques et dettes techniques <a id="section-risks"></a>

| Risque / Dette | Impact | Probabilité | Action corrective / atténuation |
|----------------|--------|-------------|---------------------------------|
| **Fin de vie PHP 7.3** | Vulnerabilités non corrigées, incompatibilité future | Élevée | Plan de migration vers PHP 8.2 (pilote) |
| **Configuration Nginx non versionnée** | Divergence entre dev / prod | Moyenne | Stocker le fichier de config Nginx dans le repo Git |
| **Absence de tests d’intégration** | Régressions fonctionnelles | Moyenne | Ajouter des scénarios Cypress/Playwright dans CI |
| **Gestion des secrets via `.env`** | Risque de fuite si le fichier est accidentellement versionné | Faible | Utiliser Vault ou GitLab CI variables, `.gitignore` strict |
| **Monolithe PHP** | Difficulté à scaler certaines parties | Moyenne | Étudier découpage en micro‑services (ex. API séparée) |
| **Performances du conteneur DB** | Saturation en charge élevée | Faible | Activer le monitoring de `pg_stat_activity`, ajuster `shared_buffers` |

↩ [Retour au sommaire](#table-of-contents)

---  

## 1️⃣2️⃣ Annexes <a id="section-appendix"></a>

### Glossaire  

| Terme | Définition |
|-------|------------|
| **C4** | Modèle de visualisation d’architecture (Context, Containers, Components, Code) |
| **CAS** | Central Authentication Service – protocole SSO |
| **ECO4** | Cloud interne du ministère, basé sur OpenStack |
| **GTI** | Groupe Technique Informatique – équipe d’exploitation |
| **PSIN** | Plateforme de Supervision d’Infrastructure Nationale |
| **D‑I‑C‑T** | Disponibilité, Intégrité, Confidentialité, Traçabilité – exigences de sécurité |
| **CI/CD** | Intégration continue / Déploiement continu |
| **SLA** | Service Level Agreement – niveau d’engagement de service |

### Décisions d’Architecture (ADR)  

| # | Décision | Contexte | Conséquence |
|---|----------|----------|-------------|
| ADR‑001 | **Utiliser Docker** pour l’ensemble des composants | Besoin d’isolation et de déploiement multi‑environnements | Simplifie la portabilité, nécessite la gestion des images |
| ADR‑002 | **Séparer app / db** en conteneurs distincts | Respect du principe de séparation des responsabilités | Permet le scaling indépendant, ajoute la complexité d’orchestration |
| ADR‑003 | **Nginx comme reverse‑proxy** | Nécessité d’un point d’entrée unique, TLS termination | Centralise la gestion du trafic, ajoute un composant HA |
| ADR‑004 | **Sauvegardes chiffrées AES‑256** | Conformité RGPD & exigences de confidentialité | Sécurise les données de sauvegarde, nécessite la gestion des clés |
| ADR‑005 | **CI avec GitLab** | Pipeline déjà disponible dans l’infrastructure | Automatisation du build/test, dépendance au serveur GitLab |

↩ [Retour au sommaire](#table-of-contents)

---  

*Document généré automatiquement à partir des sources du projet **agile‑env** et conforme au modèle **Arc42**.*