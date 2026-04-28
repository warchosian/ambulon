# Hub RH - Technical Documentation

[TOC]

---

## 📖 Overview

Hub RH is a Redmine‑based application used by the French Ministry of Ecological Transition to **track and manage human‑resources requests** submitted by employer services to the DRH (Direction des Ressources Humaines). The platform is in production since 01/10/2018 and is hosted on a VMware ESXi cluster at the Paris La Défense data centre.

| Item | Value |
|------|-------|
| **Application ID** | 353 |
| **Status** | Production |
| **Geographical scope** | National |
| **Primary technology** | Redmine (Ruby 2.7, Rails 5.2) |
| **Access protocol** | HTTPS (Web) |
| **Hosting** | VMware ESXi, Production |
| **Main URL** | <https://hub.rh.e2.rie.gouv.fr> |
| **Release date** | 01/10/2018 |
| **Last modification** | 13/03/2026 02:38:25 |

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 🏗️ System Architecture

The architecture combines a **core Redmine instance**, a set of **custom plugins**, a **PostgreSQL** database, and a **Docker‑based CI/CD pipeline** that builds and publishes the application image.

```mermaid
graph TD
    subgraph CI/CD;
    CI[GitLab CI] -->|Build image| Kaniko[Kaniko Executor]
    Kaniko -->|Push| Registry[Docker Registry]
    end
    subgraph Runtime;
    DB[(PostgreSQL)]
    App[Redmine Core]
    Plugins[Custom Plugins]
    Assets[Static Assets (CSS/JS)]
    Web[HTTPS Endpoint]
    end
    Registry -->|Deploy| Docker[Docker Container]
    Docker --> App;
    App -->|uses| DB;
    App --> Plugins;
    Plugins --> Assets;
    Web -->|serves| Docker;
    style CI fill:#f9f,stroke:#333,stroke-width_2px;
    style DB fill:#bbf,stroke:#333,stroke-width_2px;
    style App fill:#bfb,stroke:#333,stroke-width_2px;
    style Plugins fill:#ffb,stroke:#333,stroke-width_2px
```

**Key components**

| Component | Description |
|-----------|-------------|
| **Redmine Core** | Provides issue tracking, wiki, authentication, and the base data model. |
| **Custom Plugins** | `redmine_base_deface`, `redmine_base_select2`, `redmine_ckeditor`, `redmine_datetime_custom_field`, `redmine_hub_rh`, `redmine_impersonate`, `redmine_omniauth_cas`. |
| **PostgreSQL** | Stores all application data, including plugin‑specific tables (`wallet_*`, `matricules_*`). |
| **Docker** | Container runtime for reproducible environments; built by Kaniko. |
| **GitLab CI** | Executes the pipeline defined in `.gitlab-ci.yml`. |
| **HTTPS Front‑end** | Terminates TLS at the web server (NGINX/Apache) before forwarding to the container. |

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 🚀 Deployment & CI/CD Pipeline

The pipeline is defined in **`.gitlab-ci.yml`** and runs only on tags. It uses **Kaniko** to build a Docker image and pushes it to the GitLab Container Registry.

| Stage | Job | Image | Commands |
|-------|-----|-------|----------|
| **build_and_publish** | `build_and_publish` | `gcr.io/kaniko-project/executor:debug` | 1. Set `GOOGLE_APPLICATION_CREDENTIALS`.<br>2. Run Kaniko with `--dockerfile Dockerfile`.<br>3. Publish image with tags `$CI_COMMIT_TAG` and `latest`. |
| **only** | Tags | – | Prevents execution on branch pushes. |
| **tags** | `gcp` | – | Ensures the job runs on a runner with GCP access. |

**Dockerfile (excerpt)**  

```Dockerfile
FROM ruby:2.7-alpine
# System packages
RUN apk add --no-cache postgresql-dev build-base nodejs npm
# Application code
COPY . /app
WORKDIR /app
RUN bundle install --without development test
EXPOSE 3000
CMD ["bundle", "exec", "rails", "server", "-e", "production"]
```

**Deployment steps (manual)**  

1. Pull the image from the registry.  
2. Run the container with environment variables for `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `REDMINE_SECRET_KEY_BASE`.  
3. Execute database migrations: `docker exec <container> rake db:migrate RAILS_ENV=production`.  
4. Install plugin assets: `docker exec <container> rake redmine:plugins RAILS_ENV=production`.  
5. Restart the container (or the whole stack via `docker‑compose restart`).  

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## ⚙️ Configuration Management

All runtime parameters are stored in **YAML** files under `linked_configurations/` and are injected through environment variables.

| File | Purpose | Key variables |
|------|---------|----------------|
| `database.yml` | PostgreSQL connection | `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| `secrets.yml` | Rails secret key | `REDMINE_SECRET_KEY_BASE` |
| `configuration.yml` | SMTP settings (TLS) | Uses internal mail server `mail.ac.centre-serveur.i2`, port 25 |
| `session_store.rb` | Session persistence | `:active_record_store` |
| `.gitignore` | Prevents committing secrets, DB dumps, and local certificates | – |
| `livraison-continue-kpi.yml` | KPI toggles for continuous delivery tools | Boolean flags for HTTP, testssl, lighthouse, etc. |

**Example of environment injection (Docker `-e` flags)**  

```bash
-e POSTGRES_HOST=postgres.internal \
-e POSTGRES_PORT=5432 \
-e POSTGRES_USER=hubrh \
-e POSTGRES_PASSWORD=******** \
-e POSTGRES_DB=hubrh_prod \
-e REDMINE_SECRET_KEY_BASE=xxxxxxxxxxxxxx
```

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 🗄️ Database & Data Model

The core Redmine schema is extended by **`redmine_hub_rh`** migrations. The following tables are added:

| Table | Description |
|-------|-------------|
| `categories` | Stores custom request categories (`title`, `description`). |
| `logins` | Stores login metadata for external services. |
| `issue_categories` (patched) | Adds `is_multi_agents`, `attachments`, `deactivated`. |
| `issues` (patched) | Adds fields `agent_corps`, `agent_service`, `admi_pole`, `admi_desk`, `asker_service`, `agent_department`. |
| `wallets` | Central wallet entity (`title`, `pole`, `letters`, `deactivated`). |
| `wallet_services`, `wallet_admins`, `wallet_corps`, `wallet_categories` | Junction tables linking wallets to services, admins, corps, and categories. |
| `tpeses`, `tlotsdegestion`, `taffectationsop` | Matricule‑related tables with unique constraints for PERIMETER data. |
| `sessions` (via `session_store.rb`) | Stores user sessions in the DB. |

**Sample migration snippet**

```ruby
class CreateWallets < ActiveRecord::Migration[4.2]
  def change
    create_table :wallets do |t|
      t.string  :title
      t.string  :pole
      t.string  :letters
      t.boolean :deactivated
    end
    # Junction tables follow …
  end
end
```

All tables are versioned with ActiveRecord migrations and are applied during the **deployment** phase (`rake db:migrate`).

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 🔌 Plugins & Extensions

Hub RH relies on a collection of **Redmine plugins** that add UI components, authentication methods, and business‑logic extensions.

| Plugin | Core purpose | Main files / Hooks |
|--------|---------------|--------------------|
| **redmine_base_deface** | View overrides via **Deface** (removes tracker selector from context menu). | `app/overrides/README.txt`, `lib/applicator_patch.rb`, `spec/models/*_spec.rb`. |
| **redmine_base_select2** | Provides **Select2** dropdowns for enhanced UI fields. | `hooks.rb` (injects `select2.css` + `select2.full.min.js`). |
| **redmine_ckeditor** | Embeds **CKEditor** through the **Rich** engine (`/rich`). Handles journal/issue editing, file thumbnails, mail formatting. | `init.rb`, `Gemfile`, `lib/redmine_ckeditor/*_patch.rb`, `assets/ckeditor/*`, `config/routes.rb`. |
| **redmine_datetime_custom_field** | Adds a **DateTime** custom field type with `jquery.datetimepicker`. | `init.rb`, `hooks.rb`, `lib/datetime_custom_field_*_patch.rb`. |
| **redmine_hub_rh** | Core business plugin: API web‑service, additional issue fields, wallet management, stock export, and custom overrides. | `app/controllers/*_controller.rb`, `app/models/*`, `app/overrides/*`, `db/migrate/*`, `lib/redmine_hub_rh/*`. |
| **redmine_impersonate** | Allows administrators to **impersonate** any user (single click). | `init.rb`, `config/routes.rb`, locale files. |
| **redmine_omniauth_cas** | Enables **CAS** single‑sign‑on via **OmniAuth**. | `Gemfile`, `config/routes.rb`, `lib/omniauth/dynamic_full_host.rb`, `hooks.rb`. |

**Integration pattern**

All plugins follow Redmine’s standard registration:

```ruby
Redmine::Plugin.register :plugin_name do
  name 'Plugin Name'
  author 'Author'
  description '...'
  version 'x.y.z'
  requires_redmine version_or_higher: '4.0.0'
  # optional settings, routes, hooks
end
```

Patches are loaded in each plugin’s `init.rb` using `require_dependency` or `Rails.application.config.to_prepare` to guarantee reloading in development.

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 🔐 Security & Compliance

Hub RH processes **personally identifiable data (DACP)** and must comply with French **RGPD** and internal **DICT** requirements.

| Aspect | Requirement | Implementation |
|--------|--------------|----------------|
| **Confidentiality** | DICT level 3 | TLS termination (HTTPS) for all traffic; secret key stored in `secrets.yml`. |
| **Integrity** | DICT level 2 | Database transactions via PostgreSQL; ActiveRecord validations; Deface overrides are version‑controlled. |
| **Availability** | DICT level 2 | Hosted on a production‑grade VMware ESXi cluster with HA; Docker containers managed by orchestration (Docker‑Compose). |
| **Traceability** | DICT level 2 | Rails logs, Redmine audit trail, and custom `hub_rh_webservice.rb` include request identifiers. |
| **Access control** | Role‑based (Redmine roles + custom `users_helper_patch.rb`) | Plugins (`redmine_impersonate`, `redmine_hub_rh`) enforce `authorize` callbacks. |
| **Data protection** | DACP = yes | All personal data (agent identifiers, request details) encrypted at rest by PostgreSQL default encryption (if enabled) and transmitted over TLS. |
| **Security contacts** | R‑SSI DRH (`rssi.drh@developpement-durable.gouv.fr`) | Responsible for security incident handling. |

**Operational hardening**

- `session_store.rb` stores sessions in the DB to avoid client‑side tampering.  
- `redmine_omniauth_cas/lib/omniauth/dynamic_full_host.rb` builds the correct host URL even behind multiple reverse proxies.  
- `redmine_hub_rh/patch/controllers/application_controller_patch.rb` overrides `start_user_session` to reset session tokens when impersonating.  

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 🛠️ Operational Scripts

| Script | Purpose | Execution context |
|--------|---------|---------------------|
| `redmine_restore.sh.save` | Automates database migration, bundle install, plugin installation, session creation, and container restart. | Run inside the Docker host after a restore or new deployment. |
| `docker-compose.yml` (not shown) | Defines services: `redmine`, `postgres`, optional `nginx`. | Used for local development and staging. |
| `Dockerfile` | Builds the Ruby/Redmine container with required system packages. | Invoked by Kaniko during CI. |

**Example of using `redmine_restore.sh.save`**

```bash
chmod +x redmine_restore.sh.save
./redmine_restore.sh.save   # Executes the sequence of rake tasks and restarts containers
```

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 📊 Monitoring & KPI

The file **`livraison-continue-kpi.yml`** defines which monitoring tools are enabled for the continuous‑delivery pipeline.

| Tool | Enabled (default) | Description |
|------|-------------------|-------------|
| **http** | true | Basic HTTP health‑check. |
| **testssl** | true | SSL/TLS certificate validation. |
| **thirdparties** | true | Checks for external dependencies. |
| **404‑check** | false | Scans for broken links (depth 2). |
| **dependency‑check** | false | Scans for vulnerable dependencies (optional). |
| **lighthouse** | false | Front‑end performance audit. |
| **sonarcloud** | false | Static code analysis. |
| **trivy** | false | Container image vulnerability scan. |

KPI configuration is consumed by external CI tools (e.g., Jenkins, GitLab CI) to generate dashboards for availability, security, and performance.

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---

## 📞 Contact & Governance

| Role | Team / Person | Email |
|------|----------------|-------|
| **Product Owner / Business Analyst** | Pôle analyse de données RH et DIA – SG/DRH/CMGP/ATC/BEAPG | pole-analyse-de-donnees-rh-et-dia.beapg.atc.cmgp.drh.sg@developpement-durable.gouv.fr |
| **Security Officer (MOA SSI)** | SG/DRH/P/DSNUMRH | rssi.drh@developpement-durable.gouv.fr |
| **Technical Lead (MOE)** | SG/DNUM/PNM/DPNM3 | dpnm3.pnm.dnum.sg@developpement-durable.gouv.fr |
| **Support Portal** | DIN – Portail support | <https://portail-support.din.developpement-durable.gouv.fr/projects/hubrh> |
| **Production Hosting** | Centre‑serveur ministériel Paris La Défense (VMware ESXi) | – |

**Governance notes**

- The application complies with the **DICT** code 2232 (Availability 2, Integrity 2, Traceability 2, Confidentiality 3).  
- Legal basis: **Obligation juridique du responsable du traitement**.  
- Primary purpose: **Gestion RH des agents du pôle ministériel**.  

↩ [Retour au sommaire](#hub-rh---technical-documentation)

---