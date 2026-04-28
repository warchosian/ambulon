# Documentation technique du projet HubRH  
↩ [Retour au sommaire](#documentation-technique-du-projet-hubrh)

[TOC]

---

## 📖 1. Présentation générale  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

**Nom** : HubRH  
**ID** : 353  
**Statut** : En production (depuis le 01/10/2018)  
**Portée géographique** : Nationale  

Application de suivi des demandes de gestion RH, développée à partir de **Redmine 4.x** (Ruby 2.7, Rails 5.2) et enrichie de plusieurs plugins internes.  
Elle fonctionne en **HTTPS**, est accessible via le web et est hébergée sur le centre‑serveur ministériel de Paris La Défense (VMware ESXi, production).

---

## 🏗️ 2. Architecture fonctionnelle  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

```mermaid
graph TD;
    A[Utilisateurs (agents, services, admin)] -->|HTTPS| B[Load Balancer (reverse‑proxy)]
    B --> C[Conteneur Docker – Redmine Core]
    C --> D[Plugins Ruby (Deface, Select2, CKEditor, Datetime, HubRH, Impersonate, OmniAuth‑CAS)]
    C --> E[PostgreSQL (base de données métier)]
    C --> F[Redis (sessions, cache – optionnel)]
    D --> G[Webservice HubRH (REST, SOAP)]
    D --> H[Authentification CAS (OmniAuth)]
    D --> I[CKEditor (Rich Engine) – gestion des fichiers]
    G --> J[API internes (agents, services, wallets, stocks, etc.)]
    J --> K[Export CSV (stocks)]
```

* **Load Balancer** assure la terminaison TLS et distribue les requêtes vers les conteneurs.  
* **Redmine Core** fournit le moteur de suivi d’incidents et la base de données.  
* **Plugins** ajoutent des fonctionnalités métier :  
  * *redmine_base_deface* – surcharge de vues.  
  * *redmine_base_select2* – champs Select2.  
  * *redmine_ckeditor* – éditeur riche et gestion des pièces jointes.  
  * *redmine_datetime_custom_field* – type de champ DateTime.  
  * *redmine_hub_rh* – API métier, tables `wallet*`, `matricules`, overrides d’issues.  
  * *redmine_impersonate* – connexion en tant qu’autre utilisateur.  
  * *redmine_omniauth_cas* – SSO CAS via OmniAuth.  
* **PostgreSQL** stocke les tables Redmine et les tables ajoutées par les plugins.  
* **Redis** (facultatif) peut être utilisé pour les sessions et le cache.

---

## 🧩 3. Plugins et extensions  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

| Plugin | Fonction principale | Points d’intégration |
|--------|---------------------|----------------------|
| **redmine_base_deface** | Surcharge de vues via *Deface* | `app/overrides/*` – ajout de scripts, suppression de champs. |
| **redmine_base_select2** | Ajout de champs *Select2* | Hook `view_layouts_base_html_head` injecte `select2.css` + `select2.full.min.js`. |
| **redmine_ckeditor** | Éditeur riche *CKEditor* (engine **Rich**) | Routes `/rich`; patches journaux, messages, helpers, thumbnails, gestion des fichiers temporaires. |
| **redmine_datetime_custom_field** | Nouveau type de champ *DateTime* | Assets `jquery.datetimepicker`; patches du helper de formatage, hook d’injection CSS/JS. |
| **redmine_hub_rh** | API métier RH, tables `wallet*`, `matricules`, overrides d’issues | Contrôleurs API JSON, modèles légers (`ActiveModel::Model`), migrations (001‑007), overrides Deface, scripts JS personnalisés. |
| **redmine_impersonate** | Connexion « Impersonate » (admin) | Routes `/admin/impersonation`; patch du contrôleur `ApplicationController` pour rafraîchir la session. |
| **redmine_omniauth_cas** | Authentification SSO via CAS | Hook `view_account_login_top`; dynamique `OmniAuth.config.full_host`; routes `/auth/:provider/...`. |

---

## 🚀 4. Pipeline CI/CD (GitLab)  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

```mermaid
graph LR;
    subgraph CI;
        A[Commit / Tag] --> B[.gitlab-ci.yml]
        B --> C[Kaniko Builder (gcr.io/kaniko-project/executor_debug)]
        C --> D[Build Image Docker]
        D --> E[Push Image to GitLab Registry]
    end;
    subgraph CD;
        E --> F[Deploy on Kubernetes / Docker‑Compose]
        F --> G[Run DB Migrations (rake db_migrate)]
        G --> H[Install Plugin Dependencies (bundle install)]
        H --> I[Run Redmine Plugin Migrations (rake redmine_plugins:migrate)]
        I --> J[Create Sessions Table (rake db_sessions:create)]
    end
```

* **Déclenchement** : le pipeline s’exécute uniquement sur les **tags** (`only: - tags`).  
* **Construction** : l’image Docker est bâtie avec **Kaniko**, sans besoin de Docker daemon.  
* **Déploiement** : l’image est publiée dans le registre GitLab puis déployée via Docker‑Compose (fichiers `docker-compose.*.yml`) ou Kubernetes.  
* **Post‑déploiement** : les scripts de migration (`rake db:migrate`, `rake redmine:plugins:migrate`) sont exécutés dans le conteneur Redmine.

---

## ⚙️ 5. Configuration applicative  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

| Fichier | Type | Rôle | Valeurs clés |
|--------|------|------|--------------|
| `.gitignore` | Texte | Exclut les secrets, bases de données, fichiers temporaires. |
| `linked_configurations/database.yml` | YAML | Connexion PostgreSQL (variables d’environnement `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`). |
| `linked_configurations/secrets.yml` | YAML | `secret_key_base: REDMINE_SECRET_KEY_BASE`. |
| `linked_configurations/session_store.rb` | Ruby | `Rails.application.config.session_store :active_record_store`. |
| `linked_configurations/configuration.yml` | YAML | Paramètres SMTP (host interne, port 25, TLS). |
| `plugins/redmine_hub_rh/config/configuration.yml` | YAML | Chemin du certificat (`certificate_path`), mot de passe (`certificate_pwd`), proxy (`ws_proxy`). |
| `plugins/redmine_omniauth_cas/config/routes.rb` | Ruby | Routes OmniAuth (callback, redirect, LDAP stub, finalisation). |
| `plugins/redmine_impersonate/config/routes.rb` | Ruby | Routes `/admin/impersonation` (POST/DELETE). |
| `Dockerfile` | Docker | Construction de l’image Redmine avec les plugins. |
| `docker-compose*.yml` | Docker‑Compose | Définition des services (`redmine`, `postgres`, `redis`), variables d’environnement, volumes persistant. |

---

## 🗂️ 6. Schéma de la base de données (extraits)  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

```mermaid
erDiagram;
    USERS ||--o{ ISSUES : "creates"
    ISSUES ||--o{ ISSUE_CATEGORIES : "belongs to"
    ISSUE_CATEGORIES {
        integer id PK;
        string name;
        boolean is_multi_agents;
        integer attachments;
        boolean deactivated;
    }
    WALLET {
        integer id PK;
        string title;
        string pole;
        string letters;
        boolean deactivated;
    }
    WALLET_SERVICE {
        integer id PK;
        integer wallet_id FK;
        string service_id;
        string service_name;
    }
    WALLET_CATEGORY {
        integer id PK;
        integer wallet_id FK;
        integer category_id;
        string category_name;
    }
    TPESES {
        integer id PK;
        string matricule;
        string pese;
        unique(matricule, pese)
    }
    TLOTSDEGESTION {
        integer id PK;
        string matricule;
        string lotdegestion;
        unique(matricule, lotdegestion)
    }
    TAFFECTATIONSOP {
        integer id PK;
        string matricule;
        string affectationop;
        unique(matricule, affectationop)
    }
```

* Les tables `tpeses`, `tlotsdegestion` et `taffectationsop` sont créées par les migrations `007_create_matricules_perimeters_tables.rb`.  
* Les tables `wallets`, `wallet_services`, `wallet_admins`, `wallet_corps`, `wallet_categories` proviennent de la migration `005_create_wallets.rb`.  
* Les colonnes supplémentaires sur `issues` (ex. `agent_corps`, `agent_service`, …) sont ajoutées par `004_edit_issues.rb`.  

---

## 🔐 7. Sécurité & conformité  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

| Aspect | Implémentation |
|--------|----------------|
| **HTTPS** | Obligatoire (TLS) sur toutes les communications externes. |
| **Secret management** | `secret_key_base` stocké dans `linked_configurations/secrets.yml` → variable d’environnement `REDMINE_SECRET_KEY_BASE`. |
| **Authentification** | SSO CAS (`redmine_omniauth_cas`) + login standard + impersonation (admin uniquement). |
| **Gestion des sessions** | Stockage en base (`active_record_store`) → table `sessions`. |
| **Contrôle d’accès** | Rôles Redmine + patches `ApplicationController#start_user_session` pour synchroniser les habilitations. |
| **Audit & traçabilité** | `Dict` : disponibilité 2, intégrité 2, traçabilité 2, confidentialité 3. |
| **Données à caractère personnel (DACP)** | Oui – identification des agents, traitements conformes à l’obligation juridique. |
| **Sécurité des uploads** | `TempfilePatch` force le mode binaire, limite la taille via `paperclip`. |
| **Responsable SSI** | SG/DRH/P/DSNUMRH – contact `rssi.drh@developpement-durable.gouv.fr`. |

---

## 🚢 8. Déploiement, restauration et scripts d’opération  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

### 8.1 Déploiement (Docker‑Compose)

```yaml
version: "3.8"
services:
  redmine:
    image: registry.gitlab.com/yourgroup/hubrh:latest
    restart: always
    environment:
      - REDMINE_DB_POSTGRES=postgres
      - REDMINE_DB_DATABASE=${POSTGRES_DB}
      - REDMINE_DB_USERNAME=${POSTGRES_USER}
      - REDMINE_DB_PASSWORD=${POSTGRES_PASSWORD}
      - REDMINE_HTTPS=true
      - REDMINE_SECRET_KEY_BASE=${REDMINE_SECRET_KEY_BASE}
    ports:
      - "443:3000"
    depends_on:
      - postgres
    volumes:
      - redmine_data:/usr/src/redmine/files
  postgres:
    image: postgres:13
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
volumes:
  redmine_data:
  pg_data:
```

### 8.2 Script de restauration (`redmine_restore.sh.save`)

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# Script de restauration d’une instance HubRH
# -------------------------------------------------

# 1️⃣ Migration du schéma Redmine
docker exec ${REDMINE_C_NAME} rake db:migrate RAILS_ENV=production

# 2️⃣ Installation des gems du projet
docker exec ${REDMINE_C_NAME} bundle install

# 3️⃣ Installation des plugins Redmine
docker exec ${REDMINE_C_NAME} rake redmine:plugins RAILS_ENV=production

# 4️⃣ Création de la table de sessions (si absente)
docker exec ${REDMINE_C_NAME} rake db:sessions:create RAILS_ENV=production

# 5️⃣ Migration des plugins (tables spécifiques)
docker exec ${REDMINE_C_NAME} rake redmine:plugins:migrate RAILS_ENV=production

# 6️⃣ Redémarrage des conteneurs
docker-compose restart
```

Ce script est invoqué après la récupération d’un dump PostgreSQL et la restauration du volume `files`.

---

## 🌍 9. Internationalisation (i18n)  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

Chaque plugin possède son propre répertoire `config/locales/*.yml` couvrant les langues : **en, fr, ja, ko, nl, pl, pt, ru, zh, zh‑TW, ca, es**.  
Les clés communes (ex. `label_login_with_cas`, `ckeditor_toolbar_buttons`) sont partagées, ce qui garantit une traduction cohérente dans l’ensemble de l’application.

---

## 🧪 10. Tests et validation  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

| Niveau | Outils | Couverture |
|--------|--------|------------|
| **Unitaires** | RSpec (`spec/*_spec.rb`) | Plugins : Deface, CKEditor, OmniAuth‑CAS, Impersonate. |
| **Fonctionnels** | Test::Unit (`test/functional/*_test.rb`) | Vérifient le chargement des contrôleurs, routes. |
| **Intégration** | RSpec integration (`spec/integration/*`) | Scénarios d’authentification CAS, impersonation. |
| **CI** | GitLab CI exécute les specs après chaque build d’image (non montré dans le `.gitlab-ci.yml` mais pouvant être ajouté). |

Les suites de tests actuelles contiennent principalement des placeholders (`assert true`). Il est recommandé d’enrichir les specs pour couvrir :  
* les overrides Deface,  
* les patches de contrôleurs (`issues_controller_patch.rb`),  
* les appels au web‑service HubRH,  
* la logique d’export CSV des stocks.

---

## 📚 11. Maintenance & évolution  
↩ [↩ Retour au sommaire](#documentation-technique-du-projet-hubrh)

* **Mise à jour des plugins** : exécuter `rake redmine:plugins:migrate` après chaque upgrade du core ou d’un plugin.  
* **Gestion des secrets** : stocker les variables sensibles (`POSTGRES_*`, `REDMINE_SECRET_KEY_BASE`, certificats) dans le *vault* de l’infrastructure (ex. GitLab CI variables).  
* **Surveillance** : monitorer la disponibilité via les endpoints `/healthcheck` (exposer un contrôleur minimal) et les logs Docker (`docker logs`).  
* **Sauvegarde** : planifier un dump quotidien de PostgreSQL (`pg_dump`) et un snapshot du volume `redmine_data`.  
* **Traçabilité RGPD** : conserver le registre des traitements (DI​CT 2232) et mettre à jour les mentions légales lors de toute évolution fonctionnelle.  

---

## 📌 12. Annexes  

### 12.1 Liste exhaustive des fichiers majeurs (extraits)

| Répertoire | Exemple de fichiers clés |
|------------|--------------------------|
| `linked_configurations/` | `database.yml`, `secrets.yml`, `configuration.yml`, `session_store.rb` |
| `plugins/redmine_base_deface/` | `init.rb`, `PluginGemfile`, `app/overrides/README.txt` |
| `plugins/redmine_base_select2/` | `init.rb`, `lib/redmine_base_select2/hooks.rb`, `assets/stylesheets/select2.css` |
| `plugins/redmine_ckeditor/` | `init.rb`, `Gemfile`, `config/routes.rb`, `app/views/...`, `lib/redmine_ckeditor/*_patch.rb` |
| `plugins/redmine_datetime_custom_field/` | `init.rb`, `lib/hooks.rb`, `assets/stylesheets/jquery.datetimepicker.css` |
| `plugins/redmine_hub_rh/` | `init.rb`, `Gemfile`, `config/configuration.yml`, `db/migrate/00*_*.rb`, `app/controllers/*_controller.rb`, `app/models/*.rb`, `app/overrides/*` |
| `plugins/redmine_impersonate/` | `init.rb`, `Gemfile`, `config/routes.rb`, `lib/redmine_impersonate.rb` |
| `plugins/redmine_omniauth_cas/` | `init.rb`, `Gemfile`, `config/routes.rb`, `lib/omniauth/dynamic_full_host.rb`, `lib/redmine_omniauth_cas/hooks.rb` |
| `redmine_overrides/` | `application.rb`, `field_format.rb`, `queries_helper.rb` |
| `themes/circle/` | `stylesheets/application.css` |
| `Dockerfile` | Construction de l’image Redmine + plugins |
| `docker-compose*.yml` | Déploiement multi‑services |
| `redmine_restore.sh.save` | Script de restauration post‑déploiement |

### 12.2 Glossaire

| Terme | Définition |
|-------|------------|
| **Deface** | Bibliothèque Redmine permettant de surcharger des vues sans modifier le code source. |
| **Select2** | Plugin jQuery offrant des listes déroulantes enrichies (recherche, multi‑select). |
| **CKEditor / Rich** | Éditeur WYSIWYG intégré via le moteur *Rich* (Redmine plugin). |
| **OmniAuth‑CAS** | Stratégie d’authentification SSO basée sur le protocole CAS. |
| **Impersonate** | Fonctionnalité d’administration permettant à un super‑admin de se connecter comme un autre utilisateur. |
| **Dict** | Classification de la disponibilité, intégrité, traçabilité et confidentialité (norme interne). |
| **DACP** | Données à caractère personnel, soumises au RGPD. |

---

*Document généré le 27/07/2022 – Dernière mise à jour : 13/03/2026 02:38 UTC*