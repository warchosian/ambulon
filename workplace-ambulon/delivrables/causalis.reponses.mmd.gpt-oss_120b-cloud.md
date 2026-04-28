# Causalis Project – Technical Documentation  

[TOC]

---  

## 📄 Overview  

The **Causalis** application is a Java‑based solution for the collection, processing and reporting of national statistics on occupational accidents and professional illnesses within the Ministry of Ecological Transition. It provides a web interface (Struts 1.x) for data entry, validation and visualization, as well as a set of web‑service adapters for synchronization with external reference systems.

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🏗️ Architecture Overview  

```mermaid
graph TD
    subgraph Packaging;
    A[Assembly – scripts.zip] --> B[Assembly – sources.zip]
    B --> C[Assembly – docs.zip]
    end
    subgraph Persistence;
    D[Oracle DB] -->|JNDI jdbc/userDScausalis| E[Castor JDO]
    E --> F[DAO Layer]
    end
    subgraph Service;
    F --> G[ReferenceService<T>]
    G --> H[GradeService, StatutService, …]
    end
    subgraph Web_Tier;
    H --> I[Struts 1.x Actions]
    I --> J[Struts Forms]
    J --> K[JSP Views & Fragments]
    K --> L[Custom TagLibs]
    end
    subgraph WS_Adapters;
    M[WS Client Stubs] --> N[Converters & Predicates]
    N --> H;
    end
    subgraph Build;
    O[Maven] --> P[Assembly Plugin]
    O --> Q[Dependencies (Castor, Commons‑Collections, …)]
    end
    Packaging --> Build;
    Persistence --> Service;
    Service --> Web_Tier;
    WS_Adapters --> Service
```

* **Packaging** – Maven Assembly produces three ZIP artifacts: database scripts, source archive, and documentation bundle.  
* **Persistence** – Oracle database accessed through a Castor JDO configuration (`database.xml`). DAO classes expose CRUD operations.  
* **Service layer** – Generic `ReferenceService<T>` provides filtered reads (`util = 1`). Concrete services (e.g., `GradeService`, `StatutService`) extend it.  
* **Web tier** – Struts 1.x controller (`Action` classes) receives `Form` beans, forwards to JSP pages, and uses custom TagLibs (`StrutsOptionTag`, `PutIntoSessionTag`).  
* **Web‑service adapters** – SOAP/REST clients (stub JAR `StubWS.jar`) wrapped by converters (`TrancheAgeHelper`, `EffectifDetailleConverter`) and predicates (`TranscodageGradePredicate`).  

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 📦 Build & Packaging  

| Artifact | Maven Module | Description |
|----------|---------------|-------------|
| `causalis-database/assembly.xml` | `causalis-database` | Generates `scripts.zip` containing all SQL migration scripts (`script/…sql`). |
| `causalis-deployment/assembly-sources.xml` | `causalis-deployment` | Generates `sources.zip` with the full source tree (excludes `target/` directories). |
| `causalis-doc/assembly.xml` | `causalis-doc` | Generates `docs.zip` bundling the installation, DAF, and delivery documents. |
| `causalis-web/pom.xml` | `causalis-web` | Standard Maven POM, includes dependencies (Castor, Struts 1, Commons Collections, etc.) and the `assembly` plugin for the above archives. |

* **Packaging command** (executed from the project root):  

```bash
mvn clean install
```

* The generated WAR contains `WEB-INF/lib/StubWS.jar` (declared in `META-INF/MANIFEST.MF`).  

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🗄️ Persistence Layer  

### Configuration  

* **JNDI datasource** – `java:comp/env/jdbc/userDScausalis` (defined in the application server).  
* **Castor mapping** – `src/main/resources/database.xml` references `mapping.xml` (not shown) which maps Java beans to Oracle tables.  

### DAO hierarchy  

* `GenericDao<T>` – Base class implementing generic CRUD operations via Castor JDO.  
* Concrete DAOs (selected examples):  

| DAO | Entity | Key method |
|-----|--------|------------|
| `GradeDao` | `Grade` | `List<Grade> getAllGrades()` |
| `RechercheDossiersMaladiesDAO` | – | Empty placeholder (to be implemented) |
| `DossierAccidentDAO` | `DossierAccident` | Not shown, follows `GenericDao` pattern. |

### Transaction handling  

All DAO methods rely on Castor’s built‑in transaction management (`begin()`, `commit()`, `rollback()`). Exceptions are wrapped in `TechnicalException` for propagation to the service layer.  

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🧩 Service Layer  

All services extend `ReferenceService<T>` (abstract, provides `dao` field).  

### Common pattern  

```java
public List<T> getAllX() throws TechnicalException {
    Map<String, Object> map = new HashMap<>();
    map.put("util", "1");               // filter only active records
    String[] operators = {"="};
    return dao.getAll("X", map, operators, "tri");
}
```

### Selected services  

| Service | Domain | Notable methods |
|---------|--------|-----------------|
| `DomaineAffectationService` | `DomaineAffectation` | `getAllDomaineAffectation()` |
| `GradeService` | `Grade` | `getAllGrade()` |
| `StatutService` | `Statut` | `getAllStatut()`, `getStatutsMap()` (returns `Map<Integer,String>`) |
| `SynchronizeService` (interface) | Synchronisation | `int synchronize()` – implemented by concrete synchronizers (e.g., grade ↔ transcodage). |
| `TachePrescriteService` | `TachePrescrite` | `getAllTachePrescrite()` |
| `UtilisateurService` | – | Placeholder (empty). |

### Exception handling  

All service methods declare `throws TechnicalException`. The `TechnicalException` wraps the original `Exception` and provides a `printStackTrace()` that prints both stacks.  

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🌐 Web Tier  

### Struts 1.x configuration  

* `WEB-INF/struts-config.xml` – defines action mappings, form beans, and global forwards.  
* `WEB-INF/validation.xml` – currently empty (validation rules are defined in `validator-rules.xml`).  

### Actions & Forms  

| Action | Form | Purpose |
|--------|------|---------|
| `DossiersAction` | `DossiersForm` | CRUD on accident dossiers. |
| `EffectifsAction` | `EffectifsForm` | Manage employee effectif data. |
| `StatistiquesAction` | `StatistiquesForm` | Generate statistical reports. |
| `EditionDossierAction*` | `EditionDossierForm*` | Multi‑step wizard for editing a dossier. |
| `ImpressionDossierAction` | – | Render printable version of a dossier. |
| `IndexAction` | – | Home page redirect (`home.jsp`). |

### JSP Views  

* **Fragments** – `haut.jspf`, `menu.jspf`, `pied.jspf`, `marge.jspf`, `top.jspf`.  
* **Pages** – `home.jsp` (forward to `index.do`), `index.jsp`, `dossiers.jsp`, `effectifs.jsp`, `statistiques.jsp`, etc.  

### Custom Tag Libraries  

| Tag | Class | Description |
|-----|-------|-------------|
| `<c:putIntoSession>` | `PutIntoSessionTag` | Stores an object in the HTTP session (attributes: `clazz`, `attribute`, optional `serviceCode`). |
| `<c:option>` | `StrutsOptionTag` | Extends Struts `OptionTag`; replaces double quotes with single quotes for safe JavaScript usage. |
| Standard Struts tags (`bean:write`, `html:form`, …) are also used. |

### Resources  

* `src/main/resources/ApplicationResources.properties` – UI strings.  
* `project.properties` – pagination size (`pagination.max=30`).  
* `version.properties` – Maven‑injected version and compilation date.  

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🔌 Web‑Service Integration  

### Stub library  

* `WEB-INF/META-INF/MANIFEST.MF` contains `Class-Path: StubWS.jar`. This JAR provides generated SOAP client stubs for external reference services (e.g., grade lookup).  

### Converters & Helpers  

| Component | Package | Role |
|-----------|---------|------|
| `TrancheAgeHelper` | `ws.converter` | Computes age bracket (`'1'`‑`'5'`) from birth year and synchronization year. |
| `EffectifDetailleConverter` | `ws.converter` | Maps external `EffectifDetaille` DTO to internal `EffectifDetaille` bean. |
| `SaveEffectifsConverter` | `ws.converter` | Converts internal effectif data to the format expected by the external WS. |
| `TranscodageGradePredicate` | `ws.filter` | Predicate used to filter grades that are not already present in the local `TranscodageGrade` table. |
| `WSDictionary` | `ws.strategy` | Central repository of WS constants (endpoints, operation names). |

### Synchronisation flow (simplified)  

```mermaid
sequencediagram;
    participant S as GradeService;
    participant P as TranscodageGradeService;
    participant C as WSClientGrade;
    participant WS as External Grade WS;
    S->>P: request synchronize()
    P->>C: fetch grades via WSClientGrade;
    C->>WS: SOAP request (list grades)
    WS-->>C: SOAP response (grade list)
    C->>P: convert & filter (TranscodageGradePredicate)
    P-->>S: insert missing TranscodageGrade rows;
    Note right of S: returns number of inserted rows
```

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🛠️ Utilities  

| Class | Package | Description |
|-------|---------|-------------|
| `DBTools` | `tool` | Converts Castor `QueryResults` to a `List`. |
| `BeanTool` | `tool` | (Not shown) – likely utilities for bean introspection. |
| `DateTool` | `tool` | (Not shown) – date handling helpers. |
| `FormTool` | `tool` | (Not shown) – utilities for Struts form processing. |
| `GenericFetcher` | `tool` | (Not shown) – generic data retrieval helper. |
| `EffectifComparator` | `comparator` | Implements `Comparator<Effectif>` for equality based on year, grade, service and sex. |
| `ActionWarning` | `view` | Simple DTO carrying a warning message for UI display. |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## ⚙️ Configuration Files  

| File | Location | Purpose |
|------|----------|---------|
| `database.xml` | `src/main/resources` | Castor JDO configuration (JNDI datasource, mapping file). |
| `project.properties` | `src/main/resources` | Pagination size (`pagination.max`). |
| `version.properties` | `src/main/resources` | Maven‑injected version (`v${project.causalis.version}`) and compilation date. |
| `applicationResources.properties` | `src/main/resources` | UI text resources (i18n). |
| `log4j.xml` | `src/main/resources` | Log4j logging configuration (not shown in excerpt). |
| `validation.xml` | `WEB-INF` | Placeholder for Struts validation configuration (empty). |
| `validator-rules.xml` | `WEB-INF` | Defines validation rules for Struts forms. |
| `struts-config.xml` | `WEB-INF` | Core Struts action/forward configuration. |
| `web.xml` | `WEB-INF` | Servlet container configuration (Struts filter, session settings). |
| `.gitignore` (root) | Project root | Excludes `causalis.log`. |
| `.gitignore` (WEB‑INF) | `WEB-INF` | Excludes compiled `/classes/` directory from Git. |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 📦 Deployment & Hosting  

| Environment | Location | Platform | Comments |
|-------------|----------|----------|----------|
| Production | Centre‑serveur ministériel **Paris La Défense** | **ACAI – Java ACAI (Clusters ESXi)** | Hosted on a VM cluster; uses Oracle 9i/10g (as per wiki). |
| Production (legacy) | Same data centre | **Tomcat 6** (as per wiki) | Legacy servlet container still referenced. |

* Deployment artifacts (ZIP archives) are produced by Maven Assembly and copied to the production server.  
* The application is packaged as a WAR (`causalis-web.war`) deployed to Tomcat 6.  

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🔐 Security & Risk Management  

| Aspect | Detail |
|--------|--------|
| **Authentication** | Integrated with the Ministry’s SSO solution (`Cerbere`). The `reauth.jsp` invalidates the session and calls `Cerbere.logoff`. |
| **Authorization** | Role‑based access managed in the application (e.g., managers, developers, rapporteurs listed in the wiki). |
| **Data Protection** | Sensitive personal data (accident & health records) stored in Oracle; access filtered by `util = 1` flag. |
| **GDPR** | Archive classification: **Élevée**. An archival plan is defined to ensure compliance with the national data‑protection policy. |
| **Quality Gate** | SonarQube analysis (`sonar.projectKey=CAUSALIS`, `sonar.qualitygate.wait=true`). |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## ✅ Quality Assurance  

| Tool | Usage |
|------|-------|
| **JUnit / TestNG** | Unit tests located under `src/test/java/...` (e.g., `GradeServiceTest`, `BeanToolTest`). |
| **SonarQube** | Continuous inspection; the build fails if the Quality Gate is not passed (`sonar.qualitygate.wait=true`). |
| **Static analysis** | Maven plugins enforce code style and dependency checks. |
| **Coverage** | Not explicitly listed, but test classes indicate an effort to reach reasonable coverage for core services and utilities. |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 👥 Team & Contacts (from Wiki)  

| Role | Names |
|------|-------|
| **Managers** | Adrien DESSARTRE, Anthony BOULOY, Anthony MEAUZOONE, Antoine DUBOIS, Christian ARBOGAST, Jeanne VODUNGBO, Julien GARDIN, Nicolas DEMEY |
| **Developers** | Ayoub CHAKHITE, Cédric CHAPE, Florian GARCIA, Grégoire GUITTET, Hervé MARCHAL, Jenkins CAUSALIS, Marc KANAAN, Maxime Careil, Pascal FORHAN, Songul YESILMEN, Vincent JUSTIN |
| **Reporters** | Chantal CURBET, Christophe LOUVARD, Erwan SALMON, Farmin YARIRAD, Florent CAPPON, Geoffrey ARTHAUD, jenkins robot, Khalid MOKHTARI, Michel GIBELLI, Pascal BASTIEN, Patrick DOS SANTOS, Redouane RABBAH, Sarah MARAIS‑LABALLERY, Thierry SOULABAIL |
| **Contacts (SSO / Support)** | <pspp1.d.drh.sg@developpement-durable.gouv.fr> (Bureau prévention), <dsnumrh2.p.drh.sg@developpement-durable.gouv.fr> (Systèmes d’appui), <dpnm3.pnm.dnum.sg@developpement-durable.gouv.fr> (Support SI) |
| **Active users** | Approx. **170** users per month. |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 📅 Evolution & Roadmap  

| Planned Evolution | Description |
|-------------------|-------------|
| **Technological upgrade** | Migration from Struts 1.x / Castor JDO to modern frameworks (e.g., Spring Boot, JPA/Hibernate) and newer servlet containers (Tomcat 9+). |
| **Archival plan** | Formalize an archive and retention schedule for the high‑criticality data (RGPD compliance). |
| **Web‑service refactoring** | Replace the legacy `StubWS.jar` with generated OpenAPI clients; improve error handling in `WSException`. |
| **UI modernization** | Replace JSP fragments with a responsive front‑end (e.g., Angular/React) while keeping the backend services. |
| **Continuous Delivery** | Extend the existing GitLab CI pipeline (`.gitlab-ci.yml`) to include automated deployment to the production cluster. |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 🗂️ Metadata  

| Item | Value |
|------|-------|
| **Project key** | `CAUSALIS` (Sonar) |
| **Status** | **En production** |
| **Geographic scope** | **National** (including overseas territories) |
| **First production date** | **2004** |
| **Last modification** | **02/03/2026 21:10:29** |
| **Primary technology** | Java 6 (legacy) |
| **Secondary technologies** | HTML/CSS/JavaScript, Oracle 9i, Tomcat 6 |
| **Criticality** | High (archival and GDPR‑related) |
| **Number of source files** | 254 non‑binary files (≈30 KB total) |
| **Version** | Determined at build time (`version=v${project.causalis.version}`) |

↩ [Retour au sommaire](#causalis-project-technical-documentation)

---  

## 📚 References (internal)  

* **Database scripts** – `causalis-database/script/*.sql` (e.g., `20200116-causalis-1.6.sql`).  
* **Assembly descriptors** – `assembly.xml` files in each Maven module.  
* **Source code** – Packages under `src/main/java/i2/application/causalis/**`.  
* **Configuration** – `src/main/resources/*.properties` and XML files in `WEB-INF`.  
* **Wiki pages** – `causalis.wiki.md` and `causalis.wikisi.md` (team, contacts, hosting).  

All referenced files are part of this repository; no external links are required.  

↩ [Retour au sommaire](#causalis-project-technical-documentation)