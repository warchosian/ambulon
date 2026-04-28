# 📘 Cahier des Spécifications Techniques (CST) – **admin_ep**  
**Version** : 1.0.0  
**Date** : 2026‑04‑27  

[TOC]

---  

## 1️⃣ Introduction et objectifs techniques  

| Élément | Description |
|---|---|
| **Projet** | admin_ep – Administration des établissements publics du ministère de la Transition écologique |
| **Contexte** | Application métier Java (Struts 2 / Vertigo) déployée sur Tomcat 9 (migration prévue vers Tomcat 10) et PostgreSQL 9.6 (migration prévue vers PostgreSQL 15). |
| **Objectifs de qualité (ISO 25010)** | <ul><li>**Aptitude fonctionnelle** – Gestion complète des mandats, administrateurs, gestionnaires, établissements, recherche et reporting.</li><li>**Performance** – Temps de réponse < 2 s pour les requêtes de recherche et < 5 s pour les traitements batch d’alimentation JORF.</li><li>**Compatibilité** – API REST/JSON exposées aux services internes (SSO, LDAP).</li><li>**Utilisabilité** – UI web ergonomique, conformité WCAG 2.1 AA.</li><li>**Fiabilité** – Disponibilité ≥ 99,9 % (HA + réplication DB).</li><li>**Sécurité** – Authentification OIDC via Cerbère, chiffrement TLS 1.2+, audit OWASP Top 10.</li><li>**Maintenabilité** – Architecture hexagonale, code Java 8, tests > 80 % de couverture.</li><li>**Portabilité** – Conteneurisation Docker + Helm chart, exécution sur Kubernetes (IaaS).</li></ul> |
| **Conformité réglementaire** | <ul><li>RGPD – Gestion des données à caractère personnel (profil utilisateur, contacts).</li><li>RGS – Authentification forte via Cerbère, exigences SSI.</li><li>Référentiel CCTP / SSI du ministère (mise à jour Tomcat 10, PostgreSQL 15).</li></ul> |

---  

## 2️⃣ Architecture logicielle  

### 2.1 Diagramme de composants (UML)  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#2B6A9B', 'edgeLabelBackground':'#E8F1FA'}}%%%%%%%%%%%%%%%%%%%%%%%%}%%
componentDiagram;
    direction TB;
    component "Web UI (Struts2 / V‑ega)" as UI;
    component "Core Services (Hexagonal)" as Core;
    component "Persistence (JPA / Hibernate)" as Persistence;
    component "Database (PostgreSQL)" as DB;
    component "Batch JORF Loader" as JORF;
    component "Security (Cerbère OIDC)" as Sec;
    component "Search Engine (Elasticsearch)" as ES;
    UI --> Core : appels MVC;
    Core --> Persistence : DAO / Repository;
    Persistence --> DB : JDBC;
    JORF --> DB : INSERT / UPDATE;
    UI --> Sec : OIDC flow;
    Core --> ES : indexation / recherche;
    ES --> UI : résultats JSON
```

### 2.2 Description modulaire  

| Module | Responsabilité | Principaux packages |
|---|---|---|
| **Web UI** | Gestion des actions Struts2, JSP, filtres de sécurité. | `fr.gouv.e2.baseadmin.controller.*`, `fr.gouv.e2.baseadmin.decorator.*` |
| **Core (Hexagonal)** | Logique métier, orchestrations, validation. | `fr.gouv.e2.baseadmin.service.*`, `fr.gouv.e2.baseadmin.util.*` |
| **Persistence** | Accès aux tables `integration.*`, DAO générés via KSP. | `fr.gouv.e2.baseadmin.persistence.*` |
| **Batch JORF Loader** | Extraction, analyse et import des articles JORF. | `fr.gouv.e2.baseadmin.util.jorf.*`, `fr.gouv.e2.baseadmin.dynamo.search.*` |
| **Security** | Gestion des sessions, droits, intégration Cerbère. | `fr.gouv.e2.baseadmin.security.*` |
| **Search** | Indexation et recherche plein‑texte (Elasticsearch). | `fr.gouv.e2.baseadmin.services.article.*` (SearchLoader) |
| **Deployment** | Scripts Maven, assembly, Dockerfile, Helm chart. | `adminep-deployment/*` |

### 2.3 Patterns architecturaux  

| Pattern | Usage |
|---|---|
| **Hexagonal (Ports & Adapters)** | Sépare le cœur métier (services) des dépendances externes (DB, ES, JORF, sécurité). |
| **MVC (Struts2)** | Contrôleurs (`*Action`), vues JSP, modèles POJO. |
| **DAO / Repository** | Accès aux tables via JPA + KSP‑generated DAOs. |
| **Factory & Builder** | `TableCellStyleBuilder` (PDF export), `TrustManagerAllCertificates`. |
| **Decorator** | `ActifDecorator` pour enrichir les modèles d’entité. |
| **Strategy** | `OperationSecurite` pour différents types d’opérations (lecture/écriture). |
| **Singleton** | `SecurityHelper` (gestion du contexte sécurisé). |

### 2.4 Justifications  

* **Hexagonal** → facilite les tests unitaires (mocks) et la migration vers d’autres bases (ex. PostgreSQL 15).  
* **Struts2 MVC** → stack déjà maîtrisée, intégration avec le moteur de templating `displaytag`.  
* **Elasticsearch** → besoin de recherche full‑text sur les noms d’établissements et les mandats.  
* **Docker/Kubernetes** → répond aux exigences de portabilité et de scalabilité horizontale.  

---  

## 3️⃣ Stack technique détaillée  

| Catégorie | Technologie | Version | Raison |
|---|---|---|---|
| **Langage** | Java | 8 (prévu 11) | Compatibilité avec l’existant, migration future pour support long terme. |
| **Framework Web** | Struts 2 (core) + Vertigo (V‑ega) | 2.5.x | MVC éprouvé, intégration V‑ega pour filtres sécurité. |
| **DI / IoC** | Spring (boot) | 4.3.x | Configuration déclarative (`boot/components/*.xml`). |
| **ORM** | JPA (Hibernate) | 5.2.x | Mapping des tables `integration.*`, support PostgreSQL. |
| **Base de données** | PostgreSQL | 9.6 (migration 15) | Conformité aux exigences ministérielles. |
| **Search Engine** | Elasticsearch | 7.10.x | Recherche plein texte, agrégation pour les stats. |
| **Containerisation** | Docker | 20.10 | Packaging reproducible, isolation. |
| **Orchestration** | Kubernetes (Helm) | 1.26 | Déploiement multi‑environnements (prod, preprod). |
| **CI/CD** | GitLab CI | – | Pipelines build, test, scan, déploiement. |
| **Gestion des secrets** | HashiCorp Vault / Kubernetes Secrets | – | Stockage sécurisé des credentials DB & API. |
| **Monitoring** | Prometheus + Grafana | – | Métriques JVM, DB, ES, health‑checks. |
| **Logging** | Log4j2 | 2.17 | Centralisation JSON, rotation via Log4j2. |
| **Tests** | JUnit 5, Mockito, JaCoCo, Selenium | – | Couverture > 80 %, tests fonctionnels UI. |
| **Analyse statique** | SonarQube | – | Qualité code, duplication, vulnérabilités. |
| **Documentation** | Asciidoctor, Swagger‑OpenAPI | – | API REST, génération de docs. |

---  

## 4️⃣ Modélisation statique  

### 4.1 Diagramme de classes (UML)  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%
classDiagram
    direction TB;
    class Administrateur {
        +Long id;
        +String nom;
        +String prenom;
        +String email;
        +List<Mandat> mandats;
        +RoleApplicatifEnum role;

    class Gestionnaire {
        +Long id;
        +String nom;
        +String prenom;
        +String email;

    class Etablissement {
        +Long id;
        +String siren;
        +String libelle;
        +TypeInstance typeInstance;
        +List<College> colleges;

    class College {
        +Long id;
        +String identifiant;
        +List<Synonyme> synonymes;

    class Mandat {
        +Long id;
        +TypeMandat type;
        +Date debut;
        +Date fin;
        +Administrateur titulaire;
        +Administrateur suppleant;

    class Charge {
        +Long id;
        +String libelle;
        +Ministre ministreCharge;

    class Ministere {
        +Long id;
        +String sigle;
        +String nom;

    class RoleApplicatifEnum {
        <<enumeration>>
        ADMIN;
        GESTIONNAIRE;
        CONSULTANT;

    class TypeMandat {
        <<enumeration>>
        TITULAIRE;
        SUPPLEANT;

    Administrateur "1" --> "*" Mandat : possède;
    Etablissement "1" --> "*" College : regroupe;
    College "1" --> "*" Synonyme : possède;
    Charge "1" --> "*" Ministere : charge de;
    Mandat "1" --> "1" Administrateur : titulaire;
    Mandat "1" --> "0..1" Administrateur : suppleant
```

### 4.2 Relations  

* **Héritage** – `AbstractBaseAdminActionSupport` → `ActionSupport` (Struts).  
* **Composition** – `Etablissement` possède `TypeInstance`.  
* **Agrégation** – `Mandat` agrège deux `Administrateur` (titulaire & suppléant).  

### 4.3 Modèle physique de données (MPD)  

| Table | PK | FK | Description |
|---|---|---|---|
| `integration.TYPE_MANDAT` | `tma_id` | – | Types de mandat (Titulaire / Suppléant). |
| `integration.TYPE_INSTANCE` | `tin_id` | – | Types d’instance (Conseil d’administration, Conseil de surveillance). |
| `integration.COLLEGE` | `col_id` | – | Identifiants des collèges. |
| `integration.ETABLISSEMENT` | `eta_id` | `tin_id_fK` → `TYPE_INSTANCE` | Établissements publics. |
| `integration.SYNONYME_COLLEGE` | – | `col_id_fK` → `COLLEGE` | Synonymes de collèges. |
| `integration.CHARGE` | `cha_id` | – | Charges ministérielles. |
| `integration.MINISTERE_CHARGE` | (`cha_id_fK`,`min_id_fK`) | `CHA_ID_FK` → `CHARGE`, `MIN_ID_FK` → `MINISTERE` | Liaison charge‑ministère. |
| `integration.TUTELLE_ETABLISSEMENT_CHARGE` | (`eta_id_fK`,`cha_id_fK`) | `ETA_ID_FK` → `ETABLISSEMENT`, `CHA_ID_FK` → `CHARGE` | Tutelle d’établissements. |
| `integration.DIRECTION` | `dir_id` | – | Directions ministérielles. |
| `integration.DIRECTION_MINISTERE` | (`dir_id_fK`,`min_id_fK`) | `DIR_ID_FK` → `DIRECTION`, `MIN_ID_FK` → `MINISTERE` | Liaison direction‑ministère. |

---  

## 5️⃣ Modélisation dynamique  

### 5.1 Diagramme de séquence (exemple : création d’un mandat)  

```mermaid
sequencediagram;
    participant UI as Web UI (Struts2)
    participant Ctrl as UpsertMandatAction;
    participant Svc as MandatServices;
    participant DAO as MandatDao;
    participant DB as PostgreSQL;
    participant Mail as NotificationService;
    UI->>Ctrl: POST /mandat/upsert;
    Ctrl->>Svc: createMandat(dto)
    Svc->>DAO: persist(mandat)
    DAO->>DB: INSERT INTO mandat …
    DB-->>DAO: OK (id)
    DAO-->>Svc: mandatPersisted;
    Svc->>Mail: sendReminderIfSoon(mandat)
    Mail-->>Svc: OK;
    Svc-->>Ctrl: mandatId;
    Ctrl->>UI: redirect to detail page
```

### 5.2 Diagramme d’états‑transitions (Mandat)  

```mermaid
statediagram-v2;
    [*] --> EnCours;
    EnCours --> Echu : dateFin dépassée;
    EnCours --> ProchainEcheance : dateFin - 30j;
    ProchainEcheance --> NotificationEnvoyée : mail envoyé;
    Echu --> Archivé : archivage manuel;
    Archivé --> [*]
```

### 5.3 Diagramme d’activités (Batch JORF)  

```mermaid
flowchart TD
    A[Scheduler (Quartz)] --> B[Download JORF .tar.gz]
    B --> C[Extract articles]
    C --> D[Parse XML (JORFExtractor)]
    D --> E[Analyse (ArticleAnalyser)]
    E --> F{Nouveau article ?}
    F -- Oui --> G[Persist dans DB (ArticleServices)]
    F -- Non --> H[Ignorer]
    G --> I[Indexer dans Elasticsearch]
    I --> J[Envoyer notifications (Mandats à échéance)]
    H --> J;
    J --> K[Fin du cycle]
```

---  

## 6️⃣ Interfaces et intégrations  

| Interface | Type | Description | Contrat |
|---|---|---|---|
| **API REST** (admin_ep) | HTTP / JSON | CRUD sur administrateurs, établissements, mandats, recherche. | OpenAPI 3.0 (`admin_ep.yaml`) |
| **SSO Cerbère** | OIDC (OAuth 2.0) | Authentification unique, gestion des rôles (`ROLE_ADMIN`, `ROLE_GESTIONNAIRE`). | `/.well-known/openid-configuration` |
| **Elasticsearch** | REST | Indexation des établissements, mandats, articles JORF. | Index `admin_ep_*`, mapping JSON. |
| **LDAP (optionnel)** | LDAP / SASL | Récupération d’attributs utilisateurs (email, unité). | `uid={username},ou=people,dc=gouv,dc=fr` |
| **Batch JORF** | HTTP GET (tar.gz) | Source officielle : <https://echanges.dila.gouv.fr/OPENDATA/JORF/> | Aucun, téléchargement public. |
| **Monitoring** | Prometheus | Exporter métriques via `micrometer-registry-prometheus`. | `/actuator/prometheus` |
| **Logging centralisé** | Log4j2 (JSON) → Elastic Stack | Envoi logs vers Elasticsearch / Kibana. | `log4j2.xml` (JSON layout). |

---  

## 7️⃣ Architecture de déploiement  

### 7.1 Diagramme de déploiement (UML)  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%
deploymentDiagram;
    node "Kubernetes Cluster (ECO4)" {
        component "Ingress (TLS)" as Ingress;
        component "admin_ep‑web (Tomcat 9/10)" as WebPod;
        component "admin_ep‑batch (CronJob)" as BatchPod;
        component "PostgreSQL 15 (StatefulSet)" as DB;
        component "Elasticsearch 7.x (StatefulSet)" as ES;
        component "Vault (Secrets)" as Vault;
        component "Prometheus / Grafana" as Monitoring;

    Ingress --> WebPod : HTTPS;
    Ingress --> BatchPod : HTTPS (API interne)
    WebPod --> DB : JDBC (TLS)
    WebPod --> ES : REST (TLS)
    BatchPod --> DB : JDBC;
    BatchPod --> ES : REST;
    WebPod --> Vault : secrets API;
    BatchPod --> Vault : secrets API;
    Monitoring --> WebPod : scrape metrics;
    Monitoring --> DB : node exporter
```

### 7.2 Environnements  

| Environnement | Namespace | Base de données | URL d’accès | Particularités |
|---|---|---|---|---|
| **Production** | `admin-ep-prod` | PostgreSQL 15 (HA, réplication) | `https://adminep.e2.rie.gouv.fr` | TLS 1.2+, certificats internes, sauvegarde quotidienne. |
| **Pré‑production** | `admin-ep-preprod` | PostgreSQL 15 (single) | `https://adminep.preprod.e2.rie.gouv.fr` | Tests de montée de version Tomcat 10. |
| **Recette** | `admin-ep-recette` | PostgreSQL 15 (single) | `https://adminep-recette.e2.rie.gouv.fr` | Jeux de données anonymisés. |
| **Dev (Docker‑Compose)** | – | PostgreSQL 9.6 (legacy) | `http://localhost:8080` | Chargement rapide, logs en console. |

### 7.3 Haute disponibilité & failover  

* **Web tier** – Réplicas = 3 pods, service `ClusterIP` + `Ingress`.  
* **DB** – Patroni + etcd pour failover automatique, réplication asynchrone.  
* **ES** – 3‑node cluster, shards = 1, réplication = 1.  
* **Batch** – CronJob avec `restartPolicy: OnFailure`, `backoffLimit: 3`.  

---  

## 8️⃣ Sécurité technique  

| Aspect | Implémentation | Référence |
|---|---|---|
| **Authentification** | OIDC via Cerbère (client `spring-security-oauth2-client`) | ISO 27001, RGS SSI |
| **Autorisation** | RBAC (annotations `@RolesAllowed`) – `ADMIN`, `GESTIONNAIRE`, `CONSULTANT` | ISO 25010 → Sécurité |
| **Chiffrement en transit** | TLS 1.2+ (Ingress, JDBC TLS, ES HTTPS) | NIST SP 800‑52 |
| **Chiffrement au repos** | PostgreSQL 15 → pgcrypto (`pgp_sym_encrypt` pour champs sensibles) | RGPD Art. 32 |
| **Gestion des secrets** | Vault + Kubernetes Secrets (DB password, JWT secret) | ISO 27002 §9.2 |
| **Protection OWASP Top 10** | <ul><li>Input validation via Bean Validation (JSR‑380).</li><li>CSRF token (`<s:token/>`).</li><li>Headers `X‑Content‑Type‑Options`, `X‑Frame‑Options`, `Content‑Security‑Policy`.</li><li>Paramètres de connexion limités (max‑connections, fail2ban). </li></ul> | OWASP 2021 |
| **Audit & logs** | Log4j2 JSON → Elastic Stack, enrichi avec `userId`, `traceId`. | ISO 27001 → Journalisation |
| **Gestion des vulnérabilités** | Dependabot + Snyk scan, mise à jour mensuelle. | ISO 25010 → Fiabilité |
| **Hardening OS** | Images Docker basées sur `openjdk:8-jre-slim`, désactivation des services inutiles. | CIS Docker Benchmark |

---  

## 9️⃣ Qualité et tests (ISO 29119)  

### 9.1 Stratégie de test  

| Niveau | Type de test | Outils | Objectif |
|---|---|---|---|
| **Unitaire** | JUnit 5 + Mockito | JaCoCo | ≥ 80 % de couverture, validation de chaque service/DAO. |
| **Intégration** | Spring Test (DB H2), Testcontainers (PostgreSQL 15) | Testcontainers | Vérifier les flux DAO‑DB, indexation ES. |
| **Fonctionnel** | Selenium WebDriver + Cucumber | ChromeDriver | Scénarios UI (création/édition mandat). |
| **Performance** | JMeter, Gatling | – | 200 RPS, temps moyen < 2 s. |
| **Sécurité** | OWASP ZAP, SonarQube | – | Pas de vulnérabilité critique. |
| **Acceptation** | Tests d’acceptation (Cucumber) | – | Conformité au cahier des charges fonctionnel. |

### 9.2 Couverture de code cible  

* **Unitaire** : 85 % (branches)  
* **Intégration** : 75 % (scénarios)  

### 9.3 Outils d’analyse statique  

* **SonarQube** – règles Java 8, duplication < 3 %.  
* **SpotBugs** – détection de bugs potentiels.  

### 9.4 Critères d’acceptation techniques  

* Tous les tests passent (`mvn verify`).  
* Aucun défaut de sécurité de sévérité **high** ou **critical** détecté.  
* Temps de réponse moyen < 2 s sous charge 100 concurrent users.  
* Déploiement automatisé sans intervention manuelle.  

---  

## 🔟 Performance et scalabilité  

| KPI | Valeur cible | Méthode de mesure |
|---|---|---|
| **Temps de réponse moyen** (recherche) | ≤ 2 s | Gatling script `search_scenario`. |
| **Throughput** (API CRUD) | ≥ 200 req/s | JMeter `admin_ep_api`. |
| **Latence DB** | ≤ 10 ms (simple SELECT) | pg_stat_statements. |
| **Cache** | 2 min (Redis) pour listes statiques (type‑mandat, type‑instance). | Spring Cache abstraction. |
| **Scalabilité horizontale** | Ajout de pods sans impact (> 99 % disponibilité) | Test de scaling `kubectl scale deployment admin-ep-web --replicas=5`. |
| **Gestion de la charge** | Auto‑scale basé sur CPU > 70 % | HPA (Horizontal Pod Autoscaler). |

### Optimisations prévues  

* **Indexation DB** – B‑tree sur colonnes `siren`, `nom`, `date_fin`.  
* **Cache** – Redis pour tables de référence (`TYPE_MANDAT`, `TYPE_INSTANCE`).  
* **Batch parallélisation** – Partitionnement des fichiers JORF, exécution concurrente via `ExecutorService`.  

---  

## 1️⃣1️⃣ Maintenabilité et exploitation  

| Aspect | Pratique |
|---|---|
| **Standards de code** | Google Java Style Guide, Checkstyle. |
| **Convention de nommage** | `CamelCase` pour classes, `camelCase` pour méthodes, `snake_case` pour tables SQL. |
| **Documentation** | Javadoc (`/** … */`), Asciidoc dans `adminep-doc/`. |
| **Logging** | Log4j2 JSON, MDC `traceId`, `userId`. |
| **Monitoring** | Prometheus metrics (`jvm_memory_used_bytes`, `http_server_requests_seconds`). |
| **Déploiement** | Helm chart `admin-ep`, versionning sémantique, canary releases. |
| **Rollback** | `helm rollback <release> <revision>` ; snapshots DB via `pg_dump`. |
| **Gestion des incidents** | Playbook incident (Kafka → Alertmanager → Slack). |
| **Gestion de configuration** | Spring `application.yml` + `ConfigMap` Kubernetes. |
| **Gestion des dépendances** | Maven 3, version lock via `dependencyManagement`. |

---  

## 1️⃣2️⃣ Gestion des erreurs et résilience  

| Situation | Stratégie |
|---|---|
| **Erreur DB (timeout, deadlock)** | `@Transactional(retryFor = {PessimisticLockException.class})`, fallback à message d’erreur utilisateur. |
| **Erreur ES (unavailable)** | Circuit breaker (Resilience4j) → mise en cache locale, retry 3× avec back‑off exponentiel. |
| **Échec batch JORF** | Retry via Quartz, stockage de l’état dans table `batch_job_execution`. |
| **Circuit breaker** | `failureRateThreshold: 50%`, `waitDurationInOpenState: 30s`. |
| **Timeouts** | HTTP client timeout 10 s, DB query timeout 5 s. |
| **Plan de reprise d’activité (PRA)** | Restauration point‑in‑time (PITR) à partir des WAL, bascule sur site secondaire (Paris La Défense ↔ Lyon). |
| **Continuité** | Replication asynchrone PostgreSQL, sauvegarde incrémentale toutes les 4 h. |

---  

## 1️⃣3️⃣ Contraintes et dépendances  

| Contraine | Détails |
|---|---|
| **Legacy** | Base de données initiale sous PostgreSQL 9.6, scripts SQL existants (`adminep-database/scripts/*`). |
| **Intégrations imposées** | Cerbère (SSO), Elasticsearch (search), JORF (source officielle). |
| **Licences** | Java 8 (Oracle Binary Code License), Struts 2 (Apache 2.0), PostgreSQL (PostgreSQL License), Elasticsearch (Elastic License v2). |
| **Dépendances externes** | `org.apache.struts:struts2-core:2.5.26`, `org.hibernate:hibernate-core:5.2.17.Final`, `org.elasticsearch.client:elasticsearch-rest-high-level-client:7.10.2`. |
| **Contraintes de conformité** | Migration obligatoire vers Tomcat 10 (Servlet 4.0) d’ici Q4 2026. |
| **Environnement de build** | GitLab Runner (Docker‑in‑Docker), Maven 3.6.3, JDK 8. |

---  

## 1️⃣4️⃣ Annexes techniques  

### 14.1 Glossaire  

| Terme | Définition |
|---|---|
| **Mandat** | Période d’occupation d’un poste d’administrateur (titulaire ou suppléant). |
| **Charge** | Responsable ministériel d’un établissement (ex. « Affaires étrangères »). |
| **College** | Groupe d’établissements partageant un même identifiant (ex. colleges de type SPEC). |
| **JORF** | Journal officiel de la République française, source d’alimentation automatique. |
| **Cerbère** | Plateforme d’authentification unique du ministère (OIDC). |
| **ACAI** | Plateforme d’hébergement Java du ministère (clusters ESXi). |

### 14.2 Références des frameworks & bibliothèques  

| Bibliothèque | Version | Licence |
|---|---|---|
| Struts 2 | 2.5.26 | Apache 2.0 |
| Spring Framework | 4.3.25 | Apache 2.0 |
| Hibernate | 5.2.17.Final | LGPL 2.1 |
| Log4j2 | 2.17.2 | Apache 2.0 |
| Elasticsearch client | 7.10.2 | Elastic v2 |
| JUnit 5 | 5.8.2 | Eclipse Public |
| Mockito | 4.2.0 | MIT |
| SonarQube | 9.6 | GNU LGPL v3 |
| Docker | 20.10 | Apache 2.0 |
| Kubernetes | 1.26 | Apache 2.0 |

### 14.3 Architecture Decision Records (ADR)  

| ADR | Décision | Raison |
|---|---|---|
| **ADR‑001** – Choix de **Struts 2** | Conserver l’existant pour limiter le coût de migration immédiate. | Connaissance interne, faible risque de régression. |
| **ADR‑002** – Passage à **Spring Boot 2** (future) | Migration progressive vers Spring Boot 2 pour simplifier la configuration. | Alignement avec les standards modernes, facilité de tests. |
| **ADR‑003** – Utilisation de **Docker + Helm** | Containeriser l’application pour portabilité. | Réduction des écarts d’environnement, support CI/CD. |
| **ADR‑004** – Adoption de **Elasticsearch** pour la recherche | Nécessité d’une recherche full‑text performante. | Indexation flexible, agrégations pour les statistiques. |
| **ADR‑005** – Gestion des secrets avec **Vault** | Centraliser les credentials, conformité SSI. | Sécurité renforcée, rotation automatisée. |

---  

## 📌 Conclusion  

Le présent **Cahier des Spécifications Techniques** décrit l’ensemble des choix d’architecture, des composants, des exigences de qualité et des mesures de sécurité applicables au projet **admin_ep**. Il repose sur les standards ISO 25010, ISO 29119 et ISO 42010, garantissant la conformité aux exigences fonctionnelles, réglementaires et opérationnelles du ministère.  

> **Prochaine étape** : validation du CST par les parties prenantes (MOA, MOE, RSSI) → intégration dans le backlog de sprint pour la migration Tomcat 10 / PostgreSQL 15.  

---  

*Document généré le 27 avril 2026 – prêt à être versionné dans le dépôt GitLab du projet.*  