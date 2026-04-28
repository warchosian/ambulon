# 📘 Cahier des Spécifications Techniques (CST) – SIREINES  

[TOC]

---  

## 1️⃣ Introduction et objectifs techniques  

**1.1 Contexte**  
SIREINES est l’application métier du **CGDD / DRI / AST4** qui centralise les demandes de qualification des agents, suit leur évolution et assure la diffusion des résultats.  
Le système est en production depuis 2024 (v 2.5.20) et repose sur une architecture Java /J2EE, Tomcat 7 et PostgreSQL 14, déployée dans un environnement IaaS (ECO4 – Paris La Défense).  

**1.2 Objectifs de qualité (ISO 25010)**  

| Caractéristique | Niveau cible | Justification |
|------------------|--------------|---------------|
| **Aptitude fonctionnelle** | ✅ 100 % des exigences fonctionnelles couvertes | Couverture fonctionnelle via tests unitaires, d’intégration et E2E. |
| **Performance** | ⏱️ Temps de réponse < 2 s (consultation dossier) ; débit ≥ 200 req/s en pic | Optimisations SQL, caches (Ehcache) et mise en place d’index Elasticsearch. |
| **Compatibilité** | 🌐 Navigateur Chrome ≥ 90, Firefox ≥ 88, Edge ≥ 90 | UI Struts2/FreeMarker responsive (Bootstrap). |
| **Utilisabilité** | 🧭 Navigation intuitive, conformité WCAG 2.1 AA | Templates Struts2 avec libellés accessibles, validation côté serveur et client. |
| **Fiabilité** | 📈 Disponibilité ≥ 99,9 % (SLA) | Redondance Docker, health‑checks, retry & circuit‑breaker. |
| **Sécurité** | 🔐 Conformité RGPD, chiffrement TLS 1.2+, contrôle d’accès basé sur rôles (R_ADMIN) | Authentification via SSO, mots de passe hachés, audit OWASP Top 10. |
| **Maintenabilité** | 🛠️ Couverture de tests unitaires ≥ 80 % ; documentation auto‑générée | Maven Surefire, JaCoCo, SonarQube, conventions de code. |
| **Portabilité** | 📦 Déploiement Docker‑Compose, Helm possible | Isolation des dépendances, paramétrage via *.env*. |

**1.3 Conformité réglementaire**  
- **RGPD** – registre des traitements, DPO désigné, chiffrement des données sensibles.  
- **RGS** – authentification forte (SSO), protocole HTTPS, journalisation.  
- **Déclaration CNIL** n° 1034232 (29/09/2014).  

---  

## 2️⃣ Architecture logicielle  

### 2.1 Diagramme de composants (UML)  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#2A9D8F', 'edgeLabelBackground':'#F4A261' }}%%%%%%%%%%%%%%%%%%%%%%%%}%%
classDiagram
    direction TB;
    class WebApp {
        +Spring MVC + Struts2 Controllers;
        +BirtReportEngine;

    class ServiceLayer {
        +AgentsService;
        +DossiersService;
        +ExtractionsService;
        +CourriersService;
        +ReferentielsService;
        +SearchService (Elasticsearch)

    class Persistence {
        +JPA (Hibernate)
        +PostgreSQL;
        +Vertigo Dynamo (DTO/KSP)

    class Integration {
        +SSO (SAML2/OIDC)
        +Mail (SMTP)
        +Birt (PDF/Excel)

    class DockerRuntime {
        +Tomcat7;
        +Postgres14;
        +PgAdmin4;
        +BirtServlet;

    WebApp --> ServiceLayer : appels métier;
    ServiceLayer --> Persistence : DAO / JPA;
    ServiceLayer --> Integration : services externes;
    DockerRuntime --> WebApp : déploiement .war;
    DockerRuntime --> Persistence : conteneur DB
```

### 2.2 Principes architecturaux  

| Aspect | Décision | Raison |
|--------|----------|--------|
| **Pattern** | **Hexagonal (Ports & Adapters)** + **MVC** | Séparer le domaine métier (services) des I/O (Web, DB, BIRT). |
| **Modularité** | Modules Maven : `sireines-web`, `sireines-database`, `sireines-talend` | Isolation des responsabilités, versionning indépendant. |
| **Gestion des dépendances** | **Maven 3.8** + **Spring DI** | Résolution claire, version lock (see `pom.xml`). |
| **Conteneurisation** | **Docker‑Compose** (3 services) | Reproductibilité, scalabilité via Docker Swarm/K8s. |
| **Recherche** | **Elasticsearch (embedded)** via Vertigo Search | Performances sur les filtres de dossiers. |
| **Reporting** | **BIRT 4.3** intégré via `BirtManager` | Génération de PDF/Excel sur serveur. |

---  

## 3️⃣ Stack technique détaillée  

| Niveau | Technologie | Version | Rôle |
|--------|--------------|---------|------|
| **Langage** | Java | 1.8 (compatible 1.7) | Code métier |
| **Framework Web** | Spring Core, Struts2, Vertigo | 5.x / 2.5 | DI, MVC, Search |
| **Serveur d’app** | Tomcat | 7.0.108‑JDK8 | Hébergement .war |
| **Base de données** | PostgreSQL | 14.1‑alpine | Persistance |
| **ORM** | Hibernate (JPA) | 5.4 | Mapping DTO |
| **Recherche** | Elasticsearch (embedded) | 7.x | Indexation dossiers |
| **Reporting** | BIRT | 4.3 | Rapports PDF/Excel |
| **Conteneurisation** | Docker | 24.0+ | Isolation |
| **Orchestration** | Docker‑Compose | 2.27 | Déploiement multi‑service |
| **CI/CD** | GitLab CI | – | Pipelines (build, test, deploy) |
| **Qualité** | SonarQube, JaCoCo, Checkstyle | – | Analyse statique, couverture |
| **Sécurité** | Spring Security, OWASP‑Encoder | – | AuthN/Z, protection XSS/CSRF |
| **Cache** | Ehcache | 3.x | Caching de listes statiques |
| **Gestion des logs** | Log4j 2 | – | Centralisation logs |
| **Frontend** | Bootstrap 3, jQuery, Struts‑tags | – | UI responsive |
| **Scripting** | Bash, Docker‑Compose CLI | – | Opérations d’infra |

---  

## 4️⃣ Modélisation statique  

### 4.1 Diagramme de classes (UML) – vue simplifiée du domaine  

```mermaid
classDiagram
    direction LR;
    class Dossier {
        +Long dosId;
        +String titre;
        +Date dateReception;
        +String statut;
        +List<MotCle> motsCles;
        +Qualification qualification;

    class Agent {
        +Long agentId;
        +String nom;
        +String prenom;
        +String email;

    class Qualification {
        +Long quaId;
        +String libelle;
        +Date dateQualification;

    class MotCle {
        +Long mclId;
        +String libelle;

    class Comite {
        +Long comId;
        +String libelle;

    Dossier "1" --> "*" MotCle : contient;
    Dossier "1" --> "0..1" Qualification : a;
    Dossier "*" --> "1" Agent : soumisPar;
    Qualification "*" --> "1" Comite : validéPar
```

> **Note** : Les classes `Dossier`, `Agent`, `Qualification`, `MotCle` et `Comite` sont générées à partir des `DtDefinition` du répertoire `resources/i2/application/sireines/services/...`.  

---  

## 5️⃣ Modélisation dynamique  

### 5.1 Diagramme de séquence – recherche de dossiers (filtre mots‑clefs)  

```mermaid
sequencediagram;
    participant UI as UI (Struts2 page)
    participant Ctrl as DossierRechercheAction;
    participant Svc as DossiersService;
    participant Search as SearchManager (Elasticsearch)
    participant DB as PostgreSQL;
    UI->>Ctrl: submit(formulaire)
    Ctrl->>Svc: searchDossiers(criteria)
    Svc->>Search: query(criteria)
    Search-->>Svc: résultats (ids)
    loop for each id;
        Svc->>DB: SELECT * FROM Dossier WHERE dosId = ?
        DB-->>Svc: Dossier DTO;
    end
    Svc-->>Ctrl: List<DossierDTO>
    Ctrl->>UI: render(list)
```

*Le flux utilise le **circuit‑breaker** (Resilience4j) autour du call Elasticsearch ; en cas de panne, le service retourne les dernières données en cache.*  

---  

## 6️⃣ Interfaces et intégrations  

| Interface | Type | Description | Technologie | Sécurité |
|----------|------|-------------|-------------|----------|
| **REST / JSON** | API interne | Recherche dossiers, création/édition, export | Spring MVC (`@RestController`) | JWT + HTTPS |
| **BIRT Report** | Service | Génération PDF/Excel des extractions | BirtManager (VFile) | AuthN via session Tomcat |
| **SMTP** | Sortant | Envoi de mails (notification) | JavaMail | TLS, auth. |
| **SSO** | Authentification | SAML2 / OIDC (intra‑gouv) | Spring‑Security SAML | Assertion signed, HTTPS |
| **PostgreSQL** | DB | Persistance relationnelle | JDBC / JPA | Passwords chiffrés, réseau privé Docker |
| **Elasticsearch** | Search | Indexation dossiers | Vertigo Search (embedded) | Local container, no external exposure |
| **PgAdmin** | Admin UI | Gestion DB (dev) | Docker image dpage/pgadmin4 | Authentification locale |

---  

## 7️⃣ Architecture de déploiement  

### 7.1 Diagramme de déploiement (Docker‑Compose)  

```mermaid
%%{init: {'theme':'neutral'}}%%%%%%%%%%%%%%%%%%%%%%%%%%
graph TD
    subgraph Host (VM – IaaS ECO4)
        N1[Docker Engine]
    end
    subgraph Services;
        A[Tomcat7 – sireines_app_usine_container]:::app;
        B[Postgres 14 – sireines_db_usine_container]:::db;
        C[PgAdmin4 – sireines_pgadmin_container]:::admin;
    end
    N1 --> A;
    N1 --> B;
    N1 --> C;
    A -->|JDBC| B;
    A -->|HTTP| C;
    A -->|Elasticsearch (embedded)| B;
    C -->|HTTP| B;
    classDef app fill:#2A9D8F,color:#fff;
    classDef db fill:#E9C46A,color:#000;
    classDef admin fill:#F4A261,color:#000;
```

*Le fichier `docker-compose.yml` version 2.27 définit les volumes persistants `sireines_db_sireines_vol` et `sireines_pgadmin_sireines_vol`.*  

### 7.2 Environnements  

| Environnement | URL | Docker‑Compose version | Tag image |
|---------------|-----|-----------------------|------------|
| **Recette** | `http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr` | `docker-compose.yml` (branch `recette`) | `sireines-web:2.5.20` |
| **Pré‑prod** | `https://sireines.preprod.e2.rie.gouv.fr` | idem | idem |
| **Production** | `https://sireines.e2.rie.gouv.fr` | idem | `sireines-web:2.5.20` |
| **Local (Docker)** | `http://localhost:8080` | `docker-compose.yml` (branch `dev`) | `sireines-web:latest` |

---  

## 8️⃣ Sécurité technique  

| Contrôle | Implémentation | Référence |
|----------|----------------|-----------|
| **Authentification** | SSO (SAML2) via `spring-security-saml2` | ISO 27001, RGS |
| **Autorisation** | Rôles (`R_ADMIN`) définis dans `sireines-auth-config.xml` | ISO 25010 – Sécurité |
| **Chiffrement** | TLS 1.2+ (nginx reverse‑proxy optionnel) ; mots de passe BCrypt | RGPD |
| **Protection OWASP Top 10** | - XSS : encodeur OWASP <br> - CSRF : token Struts2 <br> - Injection : JPA parametrised queries <br> - Sécurité des headers (HSTS, CSP) | OWASP |
| **Gestion des secrets** | `.env` (Docker) + GitLab CI variables (no commit) | DevSecOps |
| **Audit & logs** | Log4j2 → `logs/` ; `audit.log` (actions critiques) | ISO 25012 – Confidentialité |
| **Sauvegarde DB** | pg_dump quotidien, stockage chiffré sur S3 interne | RGPD – Droit à l’oubli |
| **Résilience** | Circuit‑breaker (Resilience4j) sur Elasticsearch & mail ; retry policies | ISO 25010 – Fiabilité |
| **Hardening Docker** | USER non‑root, read‑only filesystem, seccomp profile | CIS Docker Benchmark |

---  

## 9️⃣ Qualité et tests (ISO 29119)  

### 9.1 Stratégie de tests  

| Niveau | Type | Outils | Objectif |
|--------|------|--------|----------|
| **Unitaire** | JUnit 5 + Mockito | Maven Surefire | ≥ 80 % de couverture (JaCoCo) |
| **Intégration** | Spring Boot Test, DB‑Unit (Postgres) | Maven Failsafe | Vérifier DAO, services, BIRT export |
| **Fonctionnel (E2E)** | Selenium WebDriver (Chrome) + Cucumber | GitLab CI | Scénarios critiques (login, recherche dossier, export) |
| **Performance** | JMeter (scripts search, export) | GitLab CI | < 2 s temps réponse, 200 req/s |
| **Sécurité** | OWASP ZAP, Snyk | GitLab CI | Pas de vulnérabilités critiques (OWASP Top 10) |
| **Static analysis** | SonarQube, SpotBugs, Checkstyle | SonarCloud | Qualité code, dettes ≤ 5 % |

### 9.2 Critères d’acceptation techniques  

- **Build** : `mvn clean verify` passe sans erreur.  
- **Coverage** : `JaCoCo` ≥ 80 % (line), ≥ 70 % (branch).  
- **Static analysis** : SonarQube **Quality Gate** = PASS.  
- **Performance** : 95 % des requêtes < 2 s sous charge 200 RPS.  
- **Sécurité** : Aucun **High** / **Critical** dans OWASP ZAP.  

---  

## 🔟 Performance et scalabilité  

| KPI | Valeur cible | Méthode de mesure |
|-----|--------------|-------------------|
| **Temps moyen de recherche dossier** | < 2 s | JMeter (10 000 requêtes) |
| **Débit maximal** | ≥ 200 req/s | JMeter + Grafana (CPU < 70 %) |
| **Latence BIRT export** | < 5 s (PDF) | Test fonctionnel automatisé |
| **Scalabilité horizontale** | Ajouter un conteneur `sireines_app_usine_container` sans downtime (Docker Swarm) | Test de rolling‑update |
| **Utilisation mémoire** | ≤ 512 Mo / conteneur | Docker stats + Prometheus |

*Cache Ehcache* : 95 % des listes de référentiels (structures, comités) en < 50 ms.  

---  

## 1️⃣1️⃣ Maintenabilité et exploitation  

| Aspect | Description | Outils |
|--------|-------------|--------|
| **Convention de code** | Google Java Style, imports ordonnés, Javadoc obligatoire | Checkstyle |
| **Gestion des versions** | GitLab CI tags `v<MAJOR>.<MINOR>.<PATCH>` | GitLab Release |
| **Documentation** | Javadoc → `site` (Maven site), README, wiki (CST) | Maven Site, Asciidoctor |
| **Journalisation** | Log4j2 → `logs/app.log` (rolling 10 Mo) | ELK stack (Filebeat) |
| **Monitoring** | Prometheus (docker‑stats) + Grafana dashboards (CPU, RAM, DB latency) | Alertmanager (email) |
| **Déploiement** | `docker-compose up -d` ; rollback via `docker-compose down && docker-compose up -d` | GitLab CI |
| **Gestion des erreurs** | `ErrorHandler` (Struts2) centralise les exceptions, renvoie page `application-error.jsp` | Sentry (optional) |
| **Sauvegarde DB** | `docker exec sireines-db pg_dumpall -U postgres > backup.sql` (daily) | Cron + GPG encryption |

---  

## 1️⃣2️⃣ Gestion des erreurs et résilience  

| Situation | Mécanisme | Détails |
|-----------|------------|---------|
| **Erreur Elasticsearch** | Circuit‑breaker (Resilience4j) | Après 5 échecs consécutifs, bascule sur cache Ehcache pendant 30 s. |
| **Timeout DB** | Retry (3×, back‑off exponentiel) | Si la connexion échoue, nouvelle tentative après 1 s, 2 s, 4 s. |
| **Échec BIRT** | Fallback PDF (template vide) | L’utilisateur reçoit un PDF “rapport indisponible”. |
| **Crash conteneur** | Docker health‑check + auto‑restart | `restart: always` dans `docker-compose.yml`. |
| **Défaillance réseau** | Redondance réseau du datacenter (Paris La Défense) | SLA 99,9 % (infrastructure IaaS). |

---  

## 1️⃣3️⃣ Contraintes et dépendances  

| Élément | Version / Contraintes | Impact |
|---------|----------------------|--------|
| **Java** | 1.8 (compatible 1.7) | Nécessite JDK 8, pas de modules Java 9+. |
| **Tomcat** | 7.0.108 | Limité à Servlet 3.0, pas de HTTP/2 natif. |
| **PostgreSQL** | 14.1‑alpine | Utilise `postgres` user/password définis dans `.env`. |
| **BIRT** | 4.3 | Génération PDF nécessite Java 8. |
| **Docker** | 24+ | Must support `docker compose` v2. |
| **Licence** | GPL 3 (Klee‑Group) + propriétaire | Vérifier conformité avant redistribution. |
| **RGPD** | Données personnelles (experts) | Obligation de purge après 5 ans (DUA). |
| **RGS** | Authentification forte | SSO obligatoire, aucune authentification locale. |

---  

## 1️⃣4️⃣ Annexes  

### 📚 Glossaire  

| Terme | Définition |
|-------|------------|
| **Dossier** | Enregistrement d’une demande de qualification. |
| **Qualification** | Décision du comité de domaine (valeur `QUA_ID`). |
| **MotCle** | Tag de thématique attaché à un dossier. |
| **Comité** | Organe d’évaluation (ex : “Comité de Domaine”). |
| **BIRT** | Business Intelligence and Reporting Tools (Apache). |
| **Vertigo** | Framework interne (Dynamo, Search) utilisé par Klee‑Group. |
| **Cerbère** | Gestion des habilitations (ID 546/564). |
| **IaC** | Infrastructure as Code – Docker‑Compose, GitLab CI. |

### 📄 Architecture Decision Records (ADRs) (extraits)  

| # | Décision | Raison | Statut |
|---|----------|--------|--------|
| **ADR‑001** | Utiliser **Docker‑Compose** plutôt que **Kubernetes** en phase 1 | Simplicité de mise en place, équipe déjà formée | ✅ Implémenté |
| **ADR‑002** | Choisir **Elasticsearch embedded** au lieu d’un cluster externe | Volume de recherche modéré, réduction de la surface d’attaque | ✅ Implémenté |
| **ADR‑003** | Déployer **Tomcat 7** (legacy) au lieu de **Tomcat 9** | Compatibilité BIRT 4.3 et jars Klee‑Group | ✅ Contrainte maintenue |
| **ADR‑004** | Utiliser **Spring Security + SAML2** comme point d’entrée SSO | Conformité RGS & exigences ministérielles | ✅ Implémenté |
| **ADR‑005** | Centraliser les rapports BIRT via **BirtManager** | Découplage du code métier et du rendu | ✅ Implémenté |

---  

## 📌 Conclusion  

Ce CST formalise la **réalisation technique** de SIREINES : architecture hexagonale, stack Java /J2EE, conteneurisation Docker, recherche Elasticsearch, reporting BIRT, et conformité aux exigences **ISO 25010**, **ISO 29119**, **ISO 42010**.  

Le modèle proposé garantit la **qualité**, la **sécurité** et la **maintenabilité** requises pour un service public en production nationale, tout en conservant la capacité d’évoluer (scalabilité horizontale, mise à jour des conteneurs) et de répondre aux exigences réglementaires (RGPD, RGS, CNIL).  

---  

*Document généré le **27 / 04 / 2026** – Version 1.0*  