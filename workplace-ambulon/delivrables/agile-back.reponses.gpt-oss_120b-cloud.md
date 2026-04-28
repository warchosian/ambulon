# Agile Back Project Documentation  

[TOC]

---  

## 1. Overview  

Agile Back is the back‑office component of the **Agile** application suite. It provides a Symfony‑based API and HTML interface for creating, editing, and managing study records stored in a PostgreSQL database. The system integrates with a CAS (Central Authentication Service) server for single‑sign‑on and is tightly coupled with the front‑office **Agile‑Front**.

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 2. Repository Structure  

The repository follows a conventional Symfony layout. The most relevant top‑level directories are:

| Directory | Purpose |
|-----------|---------|
| `config/` | Environment‑specific configuration files (packages, routes, services). |
| `public/` | Web‑accessible assets (JS, CSS, images, CAS client library). |
| `src/` | Application code (controllers, entities, forms, services, DTOs, utilities). |
| `templates/` | Twig view files for both admin and front‑office pages. |
| `tests/` | PHPUnit bootstrap and test suites. |
| `translations/` | (currently empty) locale files. |
| `.gitignore`, `README.md`, `phpunit.xml.dist` | Project metadata. |

The **`src/`** tree is further divided into:

* **Commandes/** – Symfony console commands.  
* **Controller/** – MVC controllers (admin and public).  
* **DataTransformer/** – Serializers for API output.  
* **Dto/** – Data‑transfer objects used by the API.  
* **Entity/** – Doctrine ORM entities (core data model).  
* **EventListeners/** & **EventSubscriber/** – Hook into the Symfony event system.  
* **Form/** – Symfony form types for CRUD UI.  
* **Repository/** – Custom Doctrine repositories.  
* **Security/** – Voter implementation for fine‑grained access control.  
* **Services/** – Business‑logic services (mailing, updates, valorisation).  
* **util/** – Helper utilities (name conversion, export, security).  

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 3. Configuration Overview  

Configuration files are grouped under `config/packages/` and `config/routes/`. Highlights:

| File | Role |
|------|------|
| `api_platform.yaml` | Enables API Platform, maps entity and DTO namespaces, defines formats (JSON, HTML, CSV). |
| `doctrine.yaml` | Database connection (`pdo_pgsql`) and ORM mapping for `src/Entity`. |
| `security.yaml` | In‑memory user provider (placeholder), dev firewall, and main firewall with anonymous access. |
| `mailer.yaml` | Configures Symfony Mailer DSN (`%env(MAILER_DSN)%`). |
| `nelmio_cors.yaml` | CORS policy allowing credentials and all HTTP methods. |
| `routing.yaml` & `routes/*.yaml` | Routes for controllers, API Platform, and dev tools (Web Profiler, Twig errors). |
| `dev/` & `test/` subfolders | Environment‑specific overrides (debug, monolog, swiftmailer, profiler). |

All configuration files are YAML and respect Symfony’s convention‑over‑configuration approach.

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 4. Core Architecture  

```mermaid
graph TD
    subgraph Front‑End;
    FE[HTML / Twig] -->|Requests| HTTP[Web Server]
    end
    subgraph Symfony;
    HTTP -->|Routing| R[Router]
    R -->|Dispatch| C[Controller]
    C -->|Calls| S[Service Layer]
    C -->|Renders| V[Twig Views]
    S -->|Persists| DB[(PostgreSQL)]
    S -->|Sends| Mail[Mailer]
    C -->|Serialises| API[API Platform]
    end
    subgraph Auth;
    CAS[CAS Server] -->|Ticket| HTTP;
    HTTP -->|Validate| Auth[Security/Voter]
    end
    DB -->|Entity Mapping| E[Doctrine Entities]
    API -->|DTO| D[Data Transfer Objects]
    S -->|Uses| U[Utilities]
    V -->|Includes| I[Templates / Includes]
```

* **Front‑End** – Twig templates rendered by Symfony controllers.  
* **Symfony Core** – Router → Controller → Service → Doctrine Entity ↔ DB.  
* **Authentication** – CAS ticket validation occurs before the request reaches the controller; the security voter (`EtudesVoter`) decides access.  
* **API** – API Platform automatically exposes entities/DTOs as REST endpoints (JSON, CSV).  

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 5. Data Model (Entity Overview)  

```mermaid
erDiagram;
    Utilisateurs ||--o{ Abonnements : "creates"
    Utilisateurs }|..|{ Groupes : "belongs to"
    Groupes ||--o{ Bop : "owns"
    Bop ||--o{ Dotations : "has"
    Dotations ||--o{ Financements : "funds"
    Financements ||--o{ Etudes : "covers"
    Etudes ||--|| Territoires : "located in"
    Etudes ||--|| Themes : "tagged with"
    Etudes ||--|| Profils : "managed by"
    Etudes ||--|| Services : "uses"
    Etudes ||--|| SousActions : "breaks down into"
    Etudes }|..|{ Valorisations : "produces"
    Utilisateurs ||--|| Profils : "has role"
```

### Key Entities  

| Entity | Primary Fields | Relations |
|--------|----------------|-----------|
| **Utilisateurs** | `id`, `nom`, `prenom`, `email` | Belongs to **Groupes**, linked to **Profils** |
| **Groupes** | `id`, `token`, `libelle` | Owns **Bop** records |
| **Bop** | `id`, `libelle_bop`, `commentaires_bop`, `sigle`, `visible` | Has many **Dotations** |
| **Dotations** | `id`, `anneedotation`, `montantdotation`, `groupe`, `bopid`, `sousActions` | Funded by **Financements** |
| **Financements** | `id`, `montant`, `date_comite`, `ae_e`, `cp_e` | Covers **Etudes** |
| **Etudes** | `id`, `titre_etude`, `zone_geographique`, `groupe`, `description` | Linked to **Territoires**, **Themes**, **Profils**, **Services**, **SousActions**, **Valorisations** |
| **Territoires**, **Themes**, **Profils**, **Services**, **SousActions**, **Valorisations** | `id`, `name`/`label` | Simple lookup tables |

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 6. Controllers Summary  

| Controller | Route Prefix | Main Responsibilities |
|------------|--------------|------------------------|
| `AbonnementsAdminController` | `/admin/abonnements` | CRUD for **Abonnements** (admin UI). |
| `BopAdminController` | `/admin/bops` | Manage **Bop** entities. |
| `DotationsAdminController` | `/admin/dotations` | CRUD for **Dotations**. |
| `EtudesController` | `/etudes` | Public view of studies, detail loading via AJAX. |
| `EtudesAdminController` | `/admin/etudes` | Full CRUD for **Etudes** (admin UI). |
| `FinancementsController` | `/admin/financements` | Manage **Financements**. |
| `GroupesAdminController` | `/admin/groupes` | CRUD for **Groupes**. |
| `ProfilsAdminController` | `/admin/profils` | Manage user profiles/roles. |
| `ServicesAdminController` | `/admin/services` | CRUD for **Services**. |
| `ThemesAdminController` | `/admin/themes` | Manage **Themes**. |
| `UtilisateursAdminController` | `/admin/utilisateurs` | Administer user accounts. |
| `SecurityController` | `/security` | Handles login/logout (CAS integration). |
| `ExportOdsDtoController` | `/export/ods` | Generates ODS exports via DTOs. |
| `ValorisationsController` | `/admin/valorisations` | Manage **Valorisations** (value‑added actions). |

All controllers extend `AbstractController` and use Symfony routing annotations. Views are rendered with Twig templates located under `templates/`.

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 7. Forms, DTOs & Data Transformers  

| Component | Target Entity / DTO | Description |
|-----------|--------------------|-------------|
| `AbonnementsType` | **Abonnements** | Form fields: `utilisateur`, `ru`, `perimetre`. |
| `BopType` | **Bop** | Fields: `libelle_bop`, `commentaires_bop`, `sigle`, `visible`. |
| `GroupesType` | **Groupes** | Fields: `token`, `libelle`. |
| `ThemesType` | **Themes** | Field: `theme`. |
| `EtudesType` | **Etudes** | Large form covering study metadata, financing, and valorisation sections. |
| `FinancementsType` | **Financements** | Fields for budget, decision date, AE/CP amounts. |
| `EtudeOutput` (DTO) | **Etudes** | Serialized representation for API output (JSON/CSV). |
| `FinancementOutput` (DTO) | **Financements** | API‑ready view of financing data. |
| `DotationOutput` (DTO) | **Dotations** | API representation of dotation records. |
| **Data Transformers** (`EtudeOutputDataTransformer`, `FinancementOutputDataTransformer`, `DotationOutputDataTransformer`) | DTO ↔ Entity | Convert between Doctrine entities and API Platform DTOs, applying name conversion (`EtudePrefixNameConverter`). |

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 8. Services & Utilities  

| Service | Core Logic |
|---------|------------|
| `SiteUpdateAbonnements` | Batch update of abonnement records (cron‑style). |
| `SiteUpdateAlertes` | Generates email alerts for study status changes. |
| `SiteUpdateMailer` / `SiteUpdateMailerByProfils` | Sends templated emails using Symfony Mailer. |
| `Valorisation` | Handles creation of valorisation records and associated export. |
| `EtudeUtil` | Helper functions for study calculations, date handling, and business rules. |
| `ExportUtil` | Generates CSV/ODS export files from DTO collections. |
| `SecurityUtil` | Centralised security checks (e.g., role validation). |
| `EtudePrefixNameConverter` | Implements `NameConverterInterface` to map API field `titre_etude` → `titreetude`. |

All services are registered in `config/services.yaml` and injected via autowiring.

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 9. Security & CAS Integration  

* **CAS Client** – The `public/cas/CAS_v135` library provides the PHP CAS client. Configuration lives in `public/cas/config_CAS.php`.  
* **Authentication Flow**  
  1. User accesses a protected route.  
  2. Symfony firewall redirects to CAS login (`connexionCAS.php`).  
  3. CAS returns a ticket; `CAS.php` validates it against the CAS server.  
  4. Upon success, Symfony creates a session and the `EtudesVoter` evaluates permissions based on user roles (stored in **Profils**).  

* **Voter** – `EtudesVoter.php` implements fine‑grained access control for study entities, checking the logged‑in user’s profile and group.  

* **Firewall Configuration** – Defined in `security.yaml`; the `dev` firewall bypasses security for static assets, while the `main` firewall enables anonymous access and integrates the CAS login process.

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 10. Front‑End Assets  

| Asset | Type | Usage |
|-------|------|-------|
| `js/detail.js` | JavaScript | AJAX loading of study detail panels. |
| `js/fonct_onglets.js` | JavaScript | Tab navigation logic (`onglet_*` functions). |
| `js/initialisation.js` | JavaScript | Global variables and initial UI state. |
| `js/print.js` | JavaScript | Printable view toggling. |
| `style/agile-composants.css` | CSS | Custom UI components (forms, tables, error messages). |
| `style/main.css` | CSS | Global layout and typography. |
| `lib/jquery-1.12.0.min.js` | Library | jQuery used by legacy scripts. |
| `lib/font-awesome.min.css` | Library | Iconography. |
| `public/cas/...` | PHP library | CAS client implementation and examples. |

All assets are referenced from Twig templates via `asset()` helper, ensuring cache‑busting with Symfony’s asset versioning.

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 11. Testing Setup  

* **PHPUnit** – Configuration in `phpunit.xml.dist`.  
* **Bootstrap** – `tests/bootstrap.php` loads the Composer autoloader and, if present, Symfony’s `config/bootstrap.php` or boots the environment via `Dotenv`.  
* **Test Environment** – Overrides in `config/packages/test/` (e.g., `swiftmailer` disabled, `framework.test` enabled, mock session storage).  

Tests are placed alongside the code they verify (e.g., functional tests for controllers, unit tests for services).  

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 12. Deployment Considerations  

| Aspect | Recommendation |
|--------|----------------|
| **Environment Variables** | Use `.env` files for `DATABASE_URL`, `MAILER_DSN`, `CORS_ALLOW_ORIGIN`. In production, inject via server configuration. |
| **Cache** | Enable Symfony’s HTTP cache (`framework.cache`) and Doctrine result/system caches (`prod/doctrine.yaml`). |
| **Logging** | Production monolog uses a `fingers_crossed` handler with JSON formatting; ensure `php://stderr` is captured by the container or server. |
| **Web Server** | Serve `public/` as the document root. Configure URL rewriting (`mod_rewrite` or equivalent) to forward all requests to `index.php`. |
| **TLS & CAS** | Enforce HTTPS for all CAS interactions. Verify CAS server certificate (`public/cas/certificat/`). |
| **Static Assets** | Leverage Symfony’s `asset` versioning (`asset_version`) for cache busting. |
| **Database Migrations** | Run `php bin/console doctrine:migrations:migrate` after deployment to apply schema changes. |

↩ [Retour au sommaire](#agile-back-project-documentation)  

---  

## 13. Appendix: Selected Key Files  

| File | Path | Size | Brief Content |
|------|------|------|---------------|
| `.gitignore` | `/.gitignore` | 460 B | Excludes env files, vendor, var, generated caches. |
| `config/packages/api_platform.yaml` | `config/packages/api_platform.yaml` | 309 B | API Platform activation, format definitions. |
| `config/packages/doctrine.yaml` | `config/packages/doctrine.yaml` | 919 B | DB connection, ORM mapping. |
| `config/packages/security.yaml` | `config/packages/security.yaml` | 861 B | Firewall and access‑control configuration. |
| `src/Entity/Etudes.php` | `src/Entity/Etudes.php` | 36 KB | Doctrine entity with many relations (themes, services, etc.). |
| `src/Controller/EtudesController.php` | `src/Controller/EtudesController.php` | 25 KB | Public controller for study display, AJAX detail loading. |
| `src/Form/EtudesType.php` | `src/Form/EtudesType.php` | 24 KB | Form definition for creating/editing studies. |
| `src/Services/Valorisation.php` | `src/Services/Valorisation.php` | 4 KB | Business logic for valorisation export. |
| `public/cas/CAS_v135/CAS.php` | `public/cas/CAS_v135/CAS.php` | 138 KB | Core CAS client implementation. |
| `templates/etudes/edit.html.twig` | `templates/etudes/edit.html.twig` | 828 B | Twig view for editing a study, includes CSS/JS assets. |
| `tests/bootstrap.php` | `tests/bootstrap.php` | 320 B | PHPUnit bootstrap loading Symfony environment. |

↩ [Retour au sommaire](#agile-back-project-documentation)  