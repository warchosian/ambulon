# Dossier d’Architecture Technique – **agile‑back**  
*Back‑office de l’application Agile*  

[TOC]

---

## 1. Introduction et objectifs  <a id="intro"></a>

**Vue fonctionnelle**  
`agile‑back` est le module back‑office de la plateforme *Agile*.  
Il permet aux agents de :

* créer, modifier et suivre des **études** (définies dans la base PostgreSQL)  
* gérer les **abonnements**, **dotations**, **financements** et **valorisations** associées  
* exporter les données (CSV, ODS) via l’API REST exposée  

**C4 – Niveau 1 (System Context)**  

```mermaid
graph TB;
    subgraph Utilisateurs;
        U[Agents / Utilisateurs finaux]
    end;
    subgraph Systèmes;
        B[agile‑back] 
        F[agile‑front] 
        C[CAS (authentification)] 
        DB[(PostgreSQL)] 
        M[SMTP / Mailer] 
        P[Prometheus / Grafana] 
    end;
    U -->|HTTP(S) + session CAS| B;
    B -->|API REST (JSON/CSV)| F;
    B -->|Auth via CAS| C;
    B -->|Lecture/Écriture| DB;
    B -->|Envoi mails| M;
    B -->|Métriques| P
```

### Objectifs de qualité orientés utilisateur  

| # | Objectif | Raison métier |
|---|----------|----------------|
| 1️⃣ | **Performance** – réponses ≤ 200 ms pour les écrans de création/modification | Fluidité de la saisie, réduction du temps d’attente |
| 2️⃣ | **Sécurité** – conformité OWASP Top 10, chiffrement des données sensibles | Protection des données d’études et des informations personnelles |
| 3️⃣ | **Disponibilité** – 99,9 % de temps de service (SLA) | Accès permanent aux études, même en période de forte charge |
| 4️⃣ | **Maintenabilité** – couverture de tests unitaires ≥ 80 % et documentation à jour | Faciliter l’évolution fonctionnelle et la correction de bugs |
| 5️⃣ | **Scalabilité** – capacité à ajouter des instances web sans interruption | Anticiper la montée en charge (nouveaux projets, pics d’usage) |

↩ [Retour au sommaire](#toc)

---

## 2. Parties prenantes  <a id="stakeholders"></a>

| Rôle | Attente principale |
|------|-------------------|
| **Maîtrise d’Ouvrage (MOA)** | Livraison fonctionnelle dans les délais, respect du périmètre métier |
| **Maîtrise d’Œuvre (MOE) – Équipe dev** | Architecture claire, stack stable, CI/CD fiable |
| **Utilisateurs finaux (agents)** | Interface ergonomique, temps de réponse rapide, fiabilité des données |
| **RSSI / Responsable Sécurité** | Conformité aux exigences de sécurité, traçabilité des accès |
| **Administrateur systèmes & exploitation** | Déploiement simple, monitoring complet, procédures de backup/restauration |
| **Support / Help‑desk** | Outils de diagnostic (logs, traces) et documentation d’incident |
| **Équipe Front‑office (agile‑front)** | API stable, contrats de service clairement définis |

*Pas de contacts individuels fournis → aucune section “Contacts”.*  

↩ [Retour au sommaire](#toc)

---

## 3. Contraintes  <a id="constraints"></a>

### 3.1 Techniques  

| Contrainte | Détails |
|------------|---------|
| **Langage / Framework** | PHP ≥ 7.4, Symfony 5.x (MVC, API Platform) |
| **Base de données** | PostgreSQL 13, schéma défini via Doctrine ORM |
| **Serveur web** | Nginx + PHP‑FPM (version 7.4) |
| **Authentification** | CAS (Central Authentication Service) – protocole SAML 1.1/2.0 |
| **Messagerie** | SMTP (configuration via `swiftmailer.yaml`) |
| **Conteneurisation** | Docker (images officielles PHP‑FPM, Nginx, Postgres) – orchestré par GitLab CI |
| **Monitoring** | Prometheus/Grafana + Loki/AlertManager (stack GTI) |
| **Gestion de logs** | Monolog (JSON formatter en prod) |
| **Gestion des dépendances** | Composer, lockfile `composer.lock` |

### 3.2 Organisationnelles  

* Respect du **processus Agile** (sprints 2 semaines).  
* Déploiement automatisé via **GitLab CI/CD** (jobs `build`, `test`, `deploy`).  
* Documentation versionnée dans le dépôt (Markdown, diagrammes Mermaid).  

### 3.3 Réglementaires  

| Domaine | Exigence |
|---------|----------|
| **RGPD** | Confidentialité & droit d’accès sur les données personnelles (email, nom). |
| **DSSI** | Traçabilité des accès (logs CAS, logs applicatifs). |
| **Archivage** | Sauvegardes chiffrées AES‑256, rétention 30 jours minimum. |

### 3.4 Sécurité – Modèle D‑I‑C‑T  

| Aspect | Exigence |
|--------|----------|
| **Disponibilité** | Redondance du reverse‑proxy Nginx, health‑checks, bascule automatique. |
| **Intégrité** | Contrôle d’intégrité des paquets (hashes) et validation côté serveur (CSRF, contraintes ORM). |
| **Confidentialité** | TLS 1.2+ sur toutes les communications, chiffrement des mots de passe (bcrypt). |
| **Traçabilité** | Journalisation détaillée des actions critiques (création/édition d’études). |

↩ [Retour au sommaire](#toc)

---

## 4. Contexte et périmètre  <a id="context"></a>

### 4.1 Systèmes partenaires  

| Système | Type d’interaction | Protocole / Fréquence |
|---------|-------------------|----------------------|
| **agile‑front** | Consommation de l’API REST (CRUD études, export) | HTTP / HTTPS, on‑demand |
| **CAS** | Authentification unique des agents | CAS protocol (HTTPS) |
| **SMTP server** | Envoi de notifications (mail d’alerte, mail de création) | SMTP (TLS) |
| **Prometheus/Grafana** | Export de métriques d’application | HTTP / HTTPS, pull (30 s) |
| **Backup storage (B3, Outscale, GCP)** | Sauvegarde des dumps PostgreSQL | Scripts nightly (cron) |
| **GitLab** | Gestion du code source et pipelines CI/CD | HTTPS, API GitLab |

### 4.2 Interfaces techniques  

| Interface | Description | Exemple de payload |
|-----------|-------------|----------------------|
| **API Platform** (REST) | End‑points JSON/CSV pour études, dotations, etc. | `POST /api/etudes` – { "titre_etude": "...", "zone_geographique": "..." } |
| **CAS** | Redirection vers `/public/cas/connexionCAS.php`, ticket validation | `GET /cas/validate?ticket=ST-...` |
| **SMTP** | Envoi d’e‑mail via `swiftmailer.yaml` | `From: no-reply@agile.local` |
| **Database** | Accès via Doctrine (SQL généré) | `SELECT * FROM etudes WHERE id = ?` |
| **Metrics** | `/metrics` exposé par Symfony exporter | `http_requests_total{method="GET",code="200"} 12345` |

↩ [Retour au sommaire](#toc)

---

## 5. Stratégie de solution  <a id="strategy"></a>

### 5.1 Décisions architecturales majeures  

| Décision | Raison |
|----------|--------|
| **Monolithe Symfony** (MVC + API Platform) | Cohérence fonctionnelle, rapidité de mise en œuvre, réutilisation du même code base pour UI et API. |
| **Utilisation de Doctrine ORM** | Gestion déclarative du schéma, migrations versionnées (`doctrine_migrations.yaml`). |
| **Reverse‑proxy Nginx en HA** | Séparation du trafic HTTP/HTTPS du processus PHP‑FPM, mise en place de load‑balancing. |
| **Conteneurisation Docker** | Reproductibilité des environnements (dev, test, prod). |
| **CI/CD GitLab** | Automatisation des tests, des builds et du déploiement. |
| **API Platform** | Standardisation des API REST, génération automatique de documentation OpenAPI. |

### 5.2 Stack technologique  

| Couche | Technologie |
|--------|--------------|
| **Front** | Twig templates, JavaScript (jQuery), CSS (Agile‑composants) |
| **Application** | PHP 7.4, Symfony 5.x, API Platform, Doctrine, Monolog, Nelmio CORS |
| **Auth** | phpCAS (CAS client) – `public/cas/` |
| **DB** | PostgreSQL 13, migrations Doctrine |
| **Mail** | SwiftMailer (configurable via env `MAILER_DSN`) |
| **Infra** | Docker, Nginx, PHP‑FPM, PostgreSQL, Prometheus, Grafana, Loki |
| **CI** | GitLab CI, PHPUnit, PHPStan (analyse statique) |
| **Monitoring** | Prometheus exporter, Grafana dashboards, AlertManager |

### 5.3 Outils de la forge logicielle  

* **Versionnage** – GitLab (repo `agile-back`)  
* **Intégration continue** – `.gitlab-ci.yml` (build, test, security scan)  
* **Tests** – PHPUnit (exemple `tests/bootstrap.php`)  
* **Analyse statique** – PHPStan, PHP_CodeSniffer  
* **Déploiement** – GitLab Runner → Docker registry → Kubernetes (ou VM OpenStack)  

↩ [Retour au sommaire](#toc)

---

## 6. Vue en Briques (C4 – Niveau 2)  <a id="container-view"></a>

```mermaid
graph TD;
    %% Conteneurs internes;
    subgraph "Infrastructure"
        Nginx[Nginx (reverse‑proxy, load‑balancing)]
        PHPFPM[PHP‑FPM (Symfony app)]
        PG[PostgreSQL]
        CAS[CAS Server (auth)]
        Mail[SMTP / SwiftMailer]
        Metrics[Prometheus Exporter]
    end;
    %% Flux;
    User[Agent / Navigateur] -->|HTTPS| Nginx;
    Nginx -->|FastCGI| PHPFPM;
    PHPFPM -->|SQL| PG;
    PHPFPM -->|CAS ticket validation| CAS;
    PHPFPM -->|SMTP| Mail;
    PHPFPM -->|Metrics| Metrics;
    Metrics -->|Pull| Prometheus
```

**Descriptions rapides**  

| Conteneur | Rôle |
|-----------|------|
| **Nginx** | Point d’entrée unique, gère TLS, répartit le trafic entre les workers PHP‑FPM. |
| **PHP‑FPM** | Héberge le code Symfony : contrôleurs, services, formulaires, API Platform. |
| **PostgreSQL** | Persistance des études, dotations, financements, utilisateurs, etc. |
| **CAS** | Authentification unique, délivre les tickets utilisés par le module `public/cas/`. |
| **Mail (SwiftMailer)** | Envoi de notifications (création, alerte, valorisation). |
| **Prometheus Exporter** | Expose les métriques `http_requests_total`, `db_query_time`, etc. |

↩ [Retour au sommaire](#toc)

---

## 7. Vue Exécution (Scénarios critiques)  <a id="execution-view"></a>

### 7.1 Scénario 1 – Création d’une étude (via UI)  

```mermaid
sequencediagram;
    participant User as Agent;
    participant Browser as Navigateur;
    participant Nginx as Nginx;
    participant PHP as PHP‑FPM (Symfony)
    participant CAS as CAS;
    participant DB as PostgreSQL;
    participant Mail as SwiftMailer;
    User->>Browser: Ouvre page “Nouvelle étude”
    Browser->>Nginx: GET /etudes/new (HTTPS)
    Nginx->>PHP: Forward request;
    PHP->>CAS: Vérifie session CAS (ticket)
    CAS-->>PHP: OK (user_id)
    PHP->>Browser: Render form (Twig)
    User->>Browser: Remplit et soumet le formulaire;
    Browser->>Nginx: POST /etudes (HTTPS)
    Nginx->>PHP: Forward POST;
    PHP->>DB: INSERT étude (Doctrine)
    DB-->>PHP: OK (id)
    PHP->>Mail: sendMail(creation)
    Mail-->>PHP: Mail sent;
    PHP->>Browser: Redirige vers /etudes/{id}
    Browser->>User: Confirmation création
```

**Validation** : vérifier la présence d’un en‑tête `X-Forwarded-For`, le ticket CAS valide, le `INSERT` réussi et l’envoi d’e‑mail (log `mail.sent`).

---

### 7.2 Scénario 2 – Job planifié d’envoi d’alertes (cron)  

```mermaid
sequencediagram;
    participant Scheduler as Cron (SiteUpdateAlertesRunner)
    participant PHP as PHP‑FPM (Command)
    participant DB as PostgreSQL;
    participant Mail as SwiftMailer;
    Scheduler->>PHP: php bin/console app_send-alertes;
    PHP->>DB: SELECT études WHERE date_alerte <= now()
    DB-->>PHP: Liste d’études;
    loop for each étude;
        PHP->>Mail: sendMail(alerte, étude)
        Mail-->>PHP: Mail sent;
    end;
    PHP->>Scheduler: Retour code 0
```

**Validation** : log `alertes.sent` avec le nombre d’e‑mails, statut de chaque envoi, et monitoring du job (`/metrics`).

---

### 7.3 Scénario 3 – Export CSV via API  

```mermaid
sequencediagram;
    participant Client as Application tierce;
    participant Nginx as Nginx;
    participant PHP as PHP‑FPM (API Platform)
    participant DB as PostgreSQL;
    Client->>Nginx: GET /api/etudes.csv?format=csv;
    Nginx->>PHP: Forward request;
    PHP->>DB: SELECT * FROM etudes;
    DB-->>PHP: ResultSet;
    PHP->>Client: Stream CSV (application/csv)
```

**Validation** : le header `Content-Type: text/csv` est présent, le corps correspond à la structure attendue, le temps de réponse < 500 ms pour < 10 000 lignes.

↩ [Retour au sommaire](#toc)

---

## 8. Vue Déploiement *(section standardisée)*  <a id="deployment-view"></a>

### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Docker‑Compose local | 1× Nginx, 1× PHP‑FPM, 1× PostgreSQL | Loopback | Hot‑reload, DB en mode *dev* (`DATABASE_URL=postgresql://dev`) |
| **Recette** | OpenStack (VM) | 2× Nginx (HA), 2× PHP‑FPM, 1× PostgreSQL (replication) | VLAN interne, accès restreint | Jeux de données anonymisés, tests d’intégration automatisés |
| **Production** | OpenStack (cluster) | 2× Nginx (load‑balancing), 4× PHP‑FPM, 2× PostgreSQL (HA, streaming replication) | VLAN DMZ + VLAN interne, TLS terminée au niveau Nginx | Sauvegardes chiffrées, monitoring Prometheus, alerting via AlertManager |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant **`pnm3`** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD;
    A[Nginx (HA)] --> B[PHP‑FPM (4 instances)]
    B --> C[PostgreSQL (HA)]
    B --> D[CAS (auth)]
    B --> E[SwiftMailer]
    B --> F[Prometheus Exporter]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :

* via **Portainer** pour la partie purement conteneurisée,  
* via la stack **Prometheus/Grafana/Loki/AlertManager**,  
* le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

* le stockage objet **B3** du IaaS ministériel,  
* le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché "Nuage Public"),  
* le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché "Nuage Public").

↩ [Retour au sommaire](#toc)

---

## 9. Sujets transverses  <a id="cross-cutting"></a>

| Sujet | Implémentation |
|-------|----------------|
| **Authentification** | `phpCAS` – SSO via CAS, ticket validation dans `public/cas/connexionCAS.php`. |
| **Autorisation** | Voter `EtudesVoter` (security/voter) ; rôles `ROLE_ADMIN`, `ROLE_USER`. |
| **Journalisation** | Monolog avec deux handlers (console en dev, JSON sur `stderr` en prod). |
| **Monitoring** | Exporter `symfony/mercure` → `/metrics`; dashboards Grafana pré‑configurés. |
| **Gestion des erreurs** | Exception listeners, page d’erreur custom (`error.html.twig`). |
| **API** | API Platform, support JSON, CSV, ODS ; CORS configuré (`nelmio_cors.yaml`). |
| **Validation des données** | Symfony Validator (annotations dans les Form Types). |
| **Sécurité HTTP** | `Content‑Security‑Policy`, `X‑Frame‑Options`, `X‑Content‑Type‑Options` via headers Nginx. |
| **CI/CD** | Pipelines GitLab : `test` (PHPUnit, PHPStan), `security` (SensioLabs, Dependency‑Check), `deploy`. |
| **Internationalisation** | `translations/` (vide pour l’instant) – prêt pour i18n. |

↩ [Retour au sommaire](#toc)

---

## 10. Exigences de qualité  <a id="quality-requirements"></a>

| Exigence | Critère d’acceptation | Scénario de validation |
|----------|----------------------|------------------------|
| **Performance – temps de réponse** | ≤ 200 ms pour les pages de création/édition (mesure via k6) | Test de charge `k6 run load-test.js` → vérifier le percentile 95 % < 200 ms |
| **Sécurité – protection XSS/CSRF** | Aucun flux XSS détecté, token CSRF présent sur chaque formulaire | Analyse OWASP ZAP automatisée, vérification du header `X‑CSRF‑Token` |
| **Disponibilité** | Uptime ≥ 99,9 % sur le mois (monitoring) | AlertManager déclenche alerte si downtime > 5 min |
| **Maintenabilité – couverture de tests** | Couverture unitaires ≥ 80 % (PHPUnit + Xdebug) | Rapport `phpunit --coverage-html` → seuil > 80 % |
| **Scalabilité** | Ajout d’une instance PHP‑FPM sans downtime (rolling update) | Déploiement blue‑green via GitLab → vérifier l’absence d’erreur 502 |
| **Traçabilité** | Tous les accès et modifications logués avec `user_id`, `timestamp` | Requête log `SELECT * FROM monolog WHERE level='INFO' AND message LIKE '%etude%';` |

↩ [Retour au sommaire](#toc)

---

## 11. Risques et dettes techniques  <a id="risks-debt"></a>

| Risque / Dette | Impact | Probabilité | Mesure corrective / atténuation |
|----------------|--------|--------------|-----------------------------------|
| **Version PHP vieillissante** (≥ 7.4) | Incompatibilité future, fin de support | Moyenne | Planifier migration vers PHP 8.1 dans le prochain sprint de refactor. |
| **Absence de tests d’intégration** | Bugs fonctionnels non détectés | Haute | Introduire des tests d’API avec `symfony/test-pack`. |
| **Single point of failure du Nginx** (pas de HA en dev) | Indisponibilité locale | Faible | Utiliser Docker‑Compose avec deux services Nginx en dev. |
| **Dépendance CAS externe** | Blocage si le serveur CAS tombe | Moyenne | Cache du ticket CAS (TTL 5 min) et fallback en mode “offline” pour les fonctions non‑critiques. |
| **Base de données monolithique** | Difficulté à partitionner à grande échelle | Moyenne | Étudier l’introduction de sharding ou de micro‑services pour les exports lourds. |
| **Scripts de backup manuels** | Risque de perte de données | Faible | Automatiser les dumps via cron et intégrer les tests de restauration dans CI. |

↩ [Retour au sommaire](#toc)

---

## 12. Annexes  <a id="annexes"></a>

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **CAS** | Central Authentication Service – protocole SSO utilisé pour l’authentification unique. |
| **API Platform** | Bibliothèque Symfony qui crée automatiquement des API REST/GraphQL à partir des entités. |
| **Doctrine ORM** | Mapper objet‑relationnel qui traduit les entités PHP en tables SQL. |
| **C4** | Modèle de visualisation d’architecture (Context, Containers, Components, Code). |
| **Prometheus** | Système de collecte de métriques pull‑based. |
| **Loki** | Agrégateur de logs compatible avec Grafana. |
| **ADR** | Architecture Decision Record – décision documentée. |
| **CI/CD** | Intégration continue / Déploiement continu. |
| **RGPD** | Règlement général sur la protection des données personnelles. |

### 12.2 Décisions d’architecture (ADR)  

| ADR | Titre | Décision | Statut |
|-----|-------|----------|--------|
| **ADR‑001** | Choix du framework | Adoption de **Symfony** (stable, riche en composants) | Implémenté |
| **ADR‑002** | Persistance des données | Utilisation de **PostgreSQL** + Doctrine Migrations | Implémenté |
| **ADR‑003** | Exposition d’API | **API Platform** pour générer les endpoints REST/CSV/ODS | Implémenté |
| **ADR‑004** | Authentification | **CAS** via phpCAS, centralisation SSO | Implémenté |
| **ADR‑005** | Monitoring | Stack **Prometheus/Grafana/Loki** (standard GTI) | Implémenté |
| **ADR‑006** | Conteneurisation | Docker + GitLab CI pour tous les environnements | Implémenté |
| **ADR‑007** | Gestion des logs | **Monolog** JSON en prod, console en dev | Implémenté |
| **ADR‑008** | Gestion des sauvegardes | Scripts de dump chiffrés, stockage multi‑cloud | Implémenté |

---

*Document généré le **28 avril 2026** – prêt à être intégré dans le dépôt GitLab et visualisé sous VS Code ou Obsidian (support Mermaid activé).*  

↩ [Retour au sommaire](#toc)