# Sireines – Technical Documentation  

[TOC]  

---  

## 📖 Overview  

> **Purpose** – Sireines is a Java/J2EE web application that records and tracks qualification requests of experts and specialists for the French Ministry of Ecological Transition. It provides a searchable repository, workflow management, and BIRT reporting.  

> **Scope** – National (France).  

> **Status** – In production (version 2.5.20 as of 12‑03‑2024).  

> **Key metrics** – 84 % SELECT, 10 % INSERT, 4 % UPDATE; ~20 screens; 29‑09‑2014 CNIL declaration (n° 1034232).  

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🏗️ Architecture  

| Layer | Technology | Main artefacts | Comments |
|-------|------------|----------------|----------|
| **Presentation** | Struts 2 + FreeMarker ( .ftl ) | `*.jsp`, `*.ftl` | Uses custom themes (`simple`, `xhtml`, `xhtml_read`). |
| **Business** | Java 8, Vertigo, Spring | `i2.application.sireines.*` (controllers, services, filters) | Dependency injection via Spring; search via Vertigo SearchManager. |
| **Reporting** | BIRT 4.3 | `*.rptdesign` in `sireines-talend/reports/` | Generates PDFs/Excel for statistics. |
| **Persistence** | PostgreSQL 14 (Docker) | `sireines-database/*` (SQL scripts, PowerDesigner models) | Scripts for install/alter/drop; index definitions in `ksp` files. |
| **Containerisation** | Docker (Tomcat 7) | `Dockerfile`, `docker‑compose.yml` | Three containers: `sireines‑app`, `sireines‑db`, `sireines‑pgadmin`. |
| **CI/CD** | GitLab CI, Maven | `pom.xml`, `settings.xml`, `.gitlab-ci.yml` | Merge‑request workflow (develop‑cgi → recette → preprod → prod). |
| **Static assets** | Bootstrap 2, custom CSS/JS | `static/css/`, `static/js/` | UI styling and helpers. |

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 📂 Repository Layout  

```
sireines/
├─ .gitignore
├─ pom.xml
├─ settings.xml
├─ sonar‑project.properties
├─ README.md
├─ budget.md / stats.md / mentions‑legales.md / declaration‑rgpd.md
├─ sireines‑database/
│   ├─ assembly.xml
│   ├─ modele/        # PowerDesigner .oom/.pdm + .sql generators
│   └─ script/
│       ├─ install/
│       ├─ alter v1/ … v2/
│       ├─ drop/
│       └─ update/
├─ sireines‑deployment/
│   ├─ assembly‑sources.xml
│   └─ sireines.xml   # Cerbère configuration
├─ sireines‑doc/
├─ sireines‑docker/
│   ├─ Dockerfile
│   ├─ .dockerignore
│   └─ docker‑compose.yml
├─ sireines‑talend/
│   ├─ lib/README.md
│   └─ reports/*.rptdesign
└─ sireines‑web/
    ├─ src/
    │   ├─ main/java/i2/application/sireines/...
    │   └─ main/resources/
    │       ├─ META‑INF/*.xml
    │       ├─ template/ (xhtml, simple, jquery …)
    │       └─ i2/application/sireines/services/*/*.ksp
    └─ src/main/webapp/
        ├─ jsp/… (pages, includes, templates)
        ├─ static/
        └─ WEB‑INF/
```

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## ⚙️ Build & Dependency Management  

| File | Role |
|------|------|
| `pom.xml` (root) | Aggregates modules (`sireines‑web`, `‑database`, `‑talend`, `‑deployment`). |
| `settings.xml` | Maven settings for the internal GitLab Maven repository (authentication via CI job token). |
| `assembly.xml` (multiple) | Packages scripts (`zip`) for DB, docs, Talend reports. |
| `.gitlab-ci.yml` | CI pipeline: compile, test, build Docker image, push artefacts. |
| `build‑mda.properties` | Points to `application‑config.xml` for Vertigo MDA generation. |

**Typical build command (local)**  

```bash
mvn clean install            # builds all modules
mvn -pl sireines-web package # only web module (produces sireines‑web‑*.war)
```

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🐳 Docker & Runtime  

### 1️⃣ Images & Containers  

| Image | Container name | Purpose |
|-------|----------------|---------|
| `sireines‑app‑usine_image` (built from `Dockerfile`) | `sireines‑app` | Tomcat 7 + deployed `sireines‑web-*.war`. |
| `postgres:14.1‑alpine` | `sireines‑db` | PostgreSQL 14 (data persisted in volume `sireines_db_sireines_vol`). |
| `dpage/pgadmin4` | `sireines‑pgadmin` | Admin UI (port 8888) – connects to `sireines‑db`. |

### 2️⃣ Docker‑Compose (excerpt)

```yaml
version: "3.8"
services:
  app:
    image: sireines-app-usine_image
    volumes:
      - ./sireines‑web‑*.war:/usr/local/tomcat/webapps/ROOT.war
    ports: ["8080:8080"]
  db:
    image: postgres:14.1-alpine
    environment: ${POSTGRES_*}
    volumes:
      - sireines_db_sireines_vol:/var/lib/postgresql/data
  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: secret
    ports: ["8888:80"]
    volumes:
      - sireines_pgadmin_sireines_vol:/var/lib/pgadmin
volumes:
  sireines_db_sireines_vol:
  sireines_pgadmin_sireines_vol:
```

### 3️⃣ Common Commands  

| Command | Effect |
|---------|--------|
| `docker-compose up -d` | Start all services. |
| `docker rm -f sireines-app` | Remove the running app container (used before a new version). |
| `docker volume ls` | List persisted volumes. |
| `docker exec -it sireines-db psql -U sireines` | Open a psql shell in the DB container. |

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🚀 Deployment Procedures  

All environments use the same Docker artefacts; only the **docker‑compose.yml** version tag is changed.

### 1️⃣ Production (prod)  

| Step | Action |
|------|--------|
| **Merge** | From `preprod` → `prod` via GitLab MR (un‑check *Delete source branch*). |
| **Validate** | Pipeline must succeed; review *Merge request* page. |
| **SSH** | Connect to Bastion → `ssh sireinesprod`. |
| **Update** | `cd /opt/app`; `cp docker‑compose.yml docker‑compose.yml.<date>`; edit `docker‑compose.yml` to reference the new image tag. |
| **Restart** | `docker rm -f sireines-app`; `docker compose up -d`. |
| **Smoke test** | Browse `https://sireines.e2.rie.gouv.fr/Accueil.do`. Verify version badge and BIRT stats. |
| **Rollback** | Restore previous `docker‑compose.yml.<date>` and repeat restart. |

### 2️⃣ Pre‑Production (preprod)  

Same steps as Production, but the MR source is `recette` → `preprod` and the URL is `https://sireines.preprod.e2.rie.gouv.fr/Accueil.do`.

### 3️⃣ Recette (test)  

MR source: `develop‑cgi` → `recette`. URL: `http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/Accueil.do`.  

*All functional tests* (login, mail, BIRT export) must be executed after each deployment (see *Tests Techniques* section below).

### 4️⃣ Local Docker Delivery (Poste)  

1. Pull the latest `sireines‑web‑*.war` from GitLab Package Registry.  
2. Place it in `c:/sireines/sireines_pgadmin`.  
3. Run `docker-compose up -d` in that folder.  
4. Access the app at `http://localhost:8080/Accueil.do`.  

The **README** in `Recette/LivraisonSurPosteDocker.md` gives a step‑by‑step guide (Docker Desktop, VS Code, volumes creation, etc.).

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🧪 Tests Techniques (Post‑Deployment)  

| Test | Description | Expected outcome |
|------|-------------|------------------|
| **Version badge** | Check footer `v${version} du ${appDate}`. | Matches `2.5.20 (12/03/2024)`. |
| **Mail sending** | Trigger a notification (e.g., new dossier). | Email received by `emailContact` (configured in `settings.xml`). |
| **BIRT reports** | Open any report (e.g., *population‑qualifiée*). | PDF/Excel generated without errors. |
| **Search** | Use the global search bar for a known expert name. | Results returned within 2 seconds. |
| **Database health** | `SELECT 1` via pgAdmin or `psql`. | Returns `1`. |
| **Security** | Attempt to access `/admin` without auth. | Redirected to login page. |

All screenshots from the original *LivraisonSurIAAS* wiki are reproduced in the **Tests** folder for reference.

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🔧 Configuration Details  

### Maven  

* `settings.xml` defines the internal GitLab Maven repository (`${env.CI_REGISTRY_USER}` / `${env.CI_REGISTRY_PASSWORD}`).  
* Profiles: `forge` (GitLab Maven).  

### Spring  

* `applicationContext.xml` (empty) – beans are defined via component scanning (`@Component`).  
* `web.xml` loads the `Struts2` filter and the `ApplicationServletContextListener`.  

### Struts2  

* `struts.xml` (in `src/main/webapp/WEB-INF`) maps actions (e.g., `Accueil.do`, `Contact.do`).  
* Themes (`simple`, `xhtml`, `xhtml_read`) are defined in `template/*/theme.properties`.  

### Vertigo Search  

* `SearchManagerInitializer` re‑indexes all `Dossier` entities at startup.  

### BIRT  

* Reports are stored under `sireines-talend/reports/`.  
* `viewer.properties` configures the BIRT viewer (used by the `/birt` servlet).  

### Environment variables (`.env` for Docker)  

```dotenv
POSTGRES_DB=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SCHEMA=postgres
```

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 📊 Versioning & Release Management  

| Environment | Current version | Release date |
|-------------|-----------------|--------------|
| Production | **2.5.20** | 12 Mar 2024 |
| Pre‑prod   | 2.5.20‑pre | – |
| Recette    | 2.5.20‑rec | – |

*Version numbers are defined in `sireines-web/src/main/resources/version.properties` (`version=${project.sireines.version}`).*  

All releases are built from the **master** branch; feature branches are merged via GitLab Merge Requests following the *develop‑cgi → recette → preprod → prod* flow.

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🌐 URLs & Access Points  

| Environment | URL | Notes |
|------------|-----|-------|
| Production | <https://sireines.e2.rie.gouv.fr/Accueil.do> | Live service. |
| Pre‑prod   | <https://sireines.preprod.e2.rie.gouv.fr/Accueil.do> | Staging, same DB schema. |
| Recette    | <http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/> | Used for functional testing. |
| Docker dev | <http://localhost:8080/Accueil.do> | Local container. |
| pgAdmin    | <http://localhost:8888/> (or `https://sireines‑pgadmin…`) | DB admin UI (user/password as in `.env`). |
| Cerbère    | Recette: <https://cerbere.recette.e2.rie.gouv.fr/administration/> <br> Prod/Pre‑prod: <https://cerbere.e2.rie.gouv.fr/administration/> | Centralised user‑role management. |

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 🔐 Security & Compliance  

* **CNIL declaration** – 29 /09 2014 (n° 1034232).  
* **DACP** – Personal data (expert contact details) are processed; encryption at rest is provided by PostgreSQL.  
* **Authentication** – Managed by Cerbère (SSO).  
* **Authorization** – Struts2 permissions (`PRM_READ_ALL`, `PRM_WRITE_ALL`) defined in `sireines‑auth‑config.xml`.  
* **Backup** – Docker volume `sireines_db_sireines_vol` is scheduled nightly via host cron (`docker run --rm -v sireines_db_sireines_vol:/data postgres:14.1-alpine pg_dumpall -U postgres > /backups/sireines_$(date +%F).sql`).  

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 📚 Documentation & References  

| Resource | Location |
|----------|----------|
| **Project wiki** | `sireines.wiki.md` (merged view). |
| **Installation guide (Docker)** | `Recette/LivraisonSurPosteDocker.md`. |
| **IAAS delivery checklist** | `Recette/LivraisonSurIAAS.md`. |
| **Database connection (Docker)** | `Recette/ConnexionBDD_Docker.md`. |
| **Cerbère admin** | `Sireines/Cerbère.md`. |
| **Version file** | `Sireines/Version.md`. |
| **Technical docs (to be completed)** | `Technique/DocumentationInstallationEtExploitation.md`. |
| **Maven build** | `pom.xml` & module `pom.xml`s. |
| **BIRT reports** | `sireines-talend/reports/*.rptdesign`. |
| **SQL scripts** | `sireines-database/script/**`. |
| **Source code** | `sireines-web/src/main/java/...`. |
| **Contact list** | `Home.md` (section *Contacts*). |

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 👥 Contacts  

| Role | Name | Email |
|------|------|-------|
| **Chef de projet opérationnel (MOA)** | Pascal Zemour | Pascal.Zemour@developpement-durable.gouv.fr |
| **Sponsor (MOA)** | Vincent Letrouit | Vincent.Letrouit@developpement-durable.gouv.fr |
| **MOE – Support** | Infocentre BUN | infocentre.bun.sdsed.cgdd@developpement-durable.gouv.fr |

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 📜 Legal & Governance  

* **Owner** – CGDD / SRI / AST 2.  
* **Regulatory basis** – CNIL declaration 29‑09‑2014 (n° 1034232).  
* **Data retention** – 5 years (DUA) → final elimination.  
* **Criticality** – Low (archival) but **SI à enjeux** (public service).  

↩ [Retour au sommaire](#sireines-technical-documentation)  

---  

## 📦 Appendices  

### A. Key Files (selected)  

| Path | Size | Type |
|------|------|------|
| `sireines-web/src/main/java/i2/application/sireines/controller/accueil/AccueilAction.java` | 717 B | Java controller |
| `sireines-web/src/main/resources/template/xhtml/form.ftl` | 216 B | FreeMarker form template |
| `sireines-database/script/alter sireines v1/alter_post