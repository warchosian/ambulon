# agile‑env

[TOC]

---  

## 📄 Introduction  
Ce document décrit l’ensemble du dépôt **agile‑env**, son organisation, ses artefacts Docker et les étapes nécessaires pour construire et exécuter l’environnement de développement. Il est autonome : aucune connaissance préalable du dépôt n’est requise.

↩ [Retour au sommaire](#agile-env)

---  

## 🎯 Objectif du projet  
Le projet **agile‑env** fournit une stack Docker :

* **PHP 7.3 + Apache** – serveur d’applications web.  
* **PostgreSQL 11** – base de données.  
* Scripts d’initialisation et de configuration (variables d’environnement, paramètres d’authentification CAS, etc.).

Cette stack est destinée aux développeurs travaillant sur les applications du groupe *ambulon* et doit pouvoir être lancée rapidement en local via `docker‑compose`.

↩ [Retour au sommaire](#agile-env)

---  

## 🗂️ Arborescence du dépôt  

```text
agile-env/
├─ docker/
│  ├─ conf/
│  │  └─ 000-default.conf          # configuration Apache du site
│  ├─ db/
│  │  └─ Dockerfile                  # image PostgreSQL avec scripts d’init
│  └─ extra/
│     └─ app‑conf/
│        ├─ .env                     # variables d’environnement (dev)
│        ├─ config_CAS.php           # configuration du SSO CAS
│        └─ param.ini                # paramètres généraux de l’application
├─ src/                              # répertoire source (vide, placeholder .gitkeep)
│  └─ .gitkeep
├─ Dockerfile‑app                     # Dockerfile multi‑stage pour le conteneur PHP/Apache
├─ docker‑compose.dev.yml             # service de composition (développement)
└─ README.md                         # méta‑information du projet
```

↩ [Retour au sommaire](#agile-env)

---  

## 🐳 Description des Dockerfiles  

### 1️⃣ `docker/db/Dockerfile`  

```dockerfile
FROM postgres:11-alpine
COPY initdb/*.sql /dump.sql
COPY initdb/restore.sh /docker-entrypoint-initdb.d/restore.sh
```

* **Base** : `postgres:11-alpine` (léger).  
* **Fonction** : copie les scripts d’initialisation (SQL + script de restauration) dans le répertoire d’entrée de PostgreSQL afin qu’ils soient exécutés au premier démarrage du conteneur.

### 2️⃣ `Dockerfile‑app` (multi‑stage)  

```dockerfile
# Étape 1 – Composer
FROM composer:latest AS composer

# Étape 2 – Application PHP/Apache
FROM php:7.3-apache-buster

# Dépendances système
ENV http_proxy  "http://pfrie-std.proxy.e2.rie.gouv.fr:8080"
ENV https_proxy "http://pfrie-std.proxy.e2.rie.gouv.fr:8080"
RUN apt-get update && \
    apt-get install -y git zip unzip vim \
    && apt-get install -y --no-install-recommends libpq-dev \
    && apt-get install -y libicu-dev \
    && docker-php-ext-install pdo pdo_pgsql intl

# Configuration Apache
COPY docker/conf/000-default.conf /etc/apache2/sites-available/000-default.conf

# Configuration PHP (production → development)
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# Composer
COPY --from=composer /usr/bin/composer /usr/bin/composer
ENV COMPOSER_ALLOW_SUPERUSER 1
```

| Élément | Rôle |
|--------|------|
| **Stage 1** (`composer`) | Fournit l’exécutable `composer` sans alourdir l’image finale. |
| **Stage 2** (`php:7.3-apache-buster`) | Base d’exécution du serveur web. |
| **Extensions PHP** | `pdo`, `pdo_pgsql` (accès PostgreSQL) et `intl` (support i18n). |
| **Proxy** | Variables `http_proxy`/`https_proxy` utiles dans le réseau interne de l’entreprise. |
| **Apache** | Copie du fichier `000-default.conf` (définit le DocumentRoot, les modules, etc.). |
| **Composer** | Disponible dans le conteneur, autorise l’installation de dépendances PHP au runtime. |

↩ [Retour au sommaire](#agile-env)

---  

## 🛠️ Configuration Apache (`docker/conf/000-default.conf`)  

> *Le fichier n’est pas affiché dans les extraits fournis, mais il est référencé par le Dockerfile.  
> Son rôle typique consiste à :*
* définir `DocumentRoot` (`/var/www/html` par défaut).  
* activer les modules `rewrite` et `headers`.  
* configurer les directives de sécurité (ex. : `AllowOverride All` pour les `.htaccess`).  

↩ [Retour au sommaire](#agile-env)

---  

## ⚙️ Variables d’environnement (`docker/extra/app‑conf/.env`)  

Le fichier `.env` (non affiché) doit contenir :  

| Variable | Exemple | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Indique l’environnement d’exécution. |
| `DB_HOST` | `postgres` | Nom du service PostgreSQL dans le compose. |
| `DB_PORT` | `5432` | Port du serveur PostgreSQL. |
| `DB_USER` | `agile_user` | Utilisateur de la base. |
| `DB_PASSWORD` | `secret` | Mot de passe (à sécuriser). |
| `DB_NAME` | `agile_db` | Nom de la base. |

Ces variables sont injectées dans le conteneur via le champ `environment` du `docker‑compose.dev.yml`.

↩ [Retour au sommaire](#agile-env)

---  

## 📦 Docker‑Compose – Architecture de développement  

```yaml
# docker-compose.dev.yml (extrait simplifié)
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile-app
    ports:
      - "8080:80"
    volumes:
      - ./src:/var/www/html
    env_file:
      - docker/extra/app-conf/.env
    depends_on:
      - db

  db:
    build:
      context: ./docker/db
    environment:
      POSTGRES_USER: agile_user
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: agile_db
    ports:
      - "5432:5432"
```

### Diagramme d’interaction  

```mermaid
graph LR
    A[Développeur] -->|docker‑compose up| W[Conteneur web (PHP/Apache)]
    A -->|docker‑compose up| D[Conteneur db (PostgreSQL)]
    W -->|requêtes HTTP| B[Application PHP]
    B -->|requêtes SQL| D;
    D -->|initialisation| S[Scripts init (SQL, restore.sh)]
    style A fill:#f9f,stroke:#333,stroke-width_2px;
    style W fill:#bbf,stroke:#333,stroke-width_2px;
    style D fill:#bbf,stroke:#333,stroke-width_2px
```

*Le diagramme montre les flux principaux : le développeur lance les services, le conteneur web sert l’application qui interroge la base de données. Le conteneur `db` exécute les scripts d’initialisation au premier démarrage.*

↩ [Retour au sommaire](#agile-env)

---  

## 🚀 Procédure de build & lancement  

| Étape | Commande | Description |
|------|----------|-------------|
| 1️⃣ Cloner le dépôt | `git clone <repo‑url> && cd agile-env` | Récupérer le code. |
| 2️⃣ Construire les images | `docker compose -f docker-compose.dev.yml build` | Compile les Dockerfiles (`web` et `db`). |
| 3️⃣ Démarrer les services | `docker compose -f docker-compose.dev.yml up -d` | Lance les conteneurs en arrière‑plan. |
| 4️⃣ Vérifier | `docker compose -f docker-compose.dev.yml ps` | S’assure que les conteneurs sont **Up**. |
| 5️⃣ Accéder à l’app | Ouvrir `http://localhost:8080` dans le navigateur. |
| 6️⃣ (Optionnel) Entrer dans le conteneur web | `docker exec -it <web_container_id> bash` | Pour installer des dépendances ou déboguer. |
| 7️⃣ Arrêter | `docker compose -f docker-compose.dev.yml down` | Nettoyer l’environnement. |

> **Remarque** : le fichier `.env` doit être correctement renseigné avant le lancement, notamment les mots de passe et le nom de la base.

↩ [Retour au sommaire](#agile-env)

---  

## 🔐 Sécurité & bonnes pratiques  

| Aspect | Recommandation |
|-------|----------------|
| **Variables sensibles** | Ne jamais versionner le fichier `.env` contenant les mots de passe ; l’ajouter à `.gitignore`. |
| **Images de base** | Mettre à jour régulièrement les images (`php:7.3-apache-buster`, `postgres:11-alpine`) via `docker compose pull`. |
| **Proxy** | Vérifier que les variables `http_proxy`/`https_proxy` sont appropriées au réseau interne ; les supprimer en production. |
| **Permissions** | Le répertoire `src/` doit être monté en lecture‑écriture uniquement pour l’utilisateur `www-data` à l’intérieur du conteneur. |
| **Docker‑Compose** | Utiliser le flag `--no-deps` ou `--force-recreate` uniquement quand cela est nécessaire. |
| **Logs** | Rediriger les logs Apache et PostgreSQL vers `stdout`/`stderr` (déjà le cas avec les images officielles) pour les exploiter via `docker logs`. |

↩ [Retour au sommaire](#agile-env)

---  

## ❓ FAQ  

**Q1 – Pourquoi deux étapes dans le Dockerfile ?**  
*R* : La première étape (`composer`) fournit l’outil `composer` sans alourdir l’image finale. Le résultat (`/usr/bin/composer`) est copié dans l’image de production, ce qui évite d’inclure toute la couche de construction.

**Q2 – Le projet ne comporte pas de code source PHP, comment le lancer ?**  
*R* : Le répertoire `src/` est prévu comme point de montage pour le code de l’application. L’utilisateur doit y placer ses fichiers PHP (ou monter un volume Git). Le Dockerfile ne dépend pas du contenu à ce stade.

**Q3 – Puis‑je utiliser ce projet en production ?**  
*R* : Ce dépôt est destiné à un **environnement de développement** (ex. : ports exposés, variables de proxy). Pour la production, il faut :  
* Utiliser des images non‑débug (`php:7.3-apache` sans outils de dev).  
* Désactiver le proxy.  
* Sécuriser les variables d’environnement via Docker secrets ou un gestionnaire de secrets.  

↩ [Retour au sommaire](#agile-env)

---  

## 📚 Références  

| Ressource | Description |
|-----------|-------------|
| `docker/db/Dockerfile` | Construction de l’image PostgreSQL avec scripts d’initialisation. |
| `Dockerfile-app` | Multi‑stage build pour le conteneur PHP/Apache. |
| `docker-compose.dev.yml` | Orchestration des services `web` et `db`. |
| `docker/conf/000-default.conf` | Configuration Apache du site (DocumentRoot, modules). |
| `docker/extra/app-conf/.env` | Variables d’environnement pour le conteneur web. |

↩ [Retour au sommaire](#agile-env)