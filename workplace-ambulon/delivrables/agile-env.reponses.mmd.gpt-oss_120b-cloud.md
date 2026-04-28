# Documentation technique du projet **agile‑env**

[TOC]

---  

## 📋 Présentation générale  
↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

Le répertoire **agile‑env** regroupe l’ensemble des artefacts nécessaires au déploiement d’une application PHP + Apache, soutenue par une base de données PostgreSQL.  
Le projet s’articule autour de deux images Docker :

| Image | Rôle | Source Dockerfile |
|-------|------|-------------------|
| `agile-env-db` | Conteneur PostgreSQL avec scripts d’initialisation | `docker/db/Dockerfile` |
| `agile-env-app` | Application PHP 7.3 + Apache, compilation des dépendances via Composer | `Dockerfile‑app` |

Le **docker‑compose.dev.yml** (non détaillé ici) orchestre ces services en mode développement.

---  

## 📂 Arborescence du dépôt  
↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

```
agile-env
├─ docker
│  ├─ conf
│  │   └─ 000-default.conf          # Config Apache (site par défaut)
│  ├─ db
│  │   └─ Dockerfile                # Image PostgreSQL
│  └─ extra
│      └─ app‑conf
│          ├─ .env                  # Variables d’environnement (exemple)
│          ├─ config_CAS.php        # Configuration CAS (authentification)
│          └─ param.ini             # Paramètres applicatifs
├─ src
│  └─ .gitkeep                     # Placeholder du répertoire source
├─ Dockerfile‑app                  # Image applicative
├─ docker‑compose.dev.yml           # Orchestration (dev)
└─ README.md                      # Description succincte
```

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 🛠️ Construction des images Docker  

### 1️⃣ Image **agile‑env‑db**  

```dockerfile
# docker/db/Dockerfile
FROM postgres:11-alpine
COPY initdb/*.sql /dump.sql
COPY initdb/restore.sh /docker-entrypoint-initdb.d/restore.sh
```

* **Base** : `postgres:11-alpine` (léger, Alpine Linux).  
* **Initialisation** : les scripts SQL et le script `restore.sh` sont injectés dans le répertoire d’entrée de PostgreSQL, exécutés au premier démarrage.

### 2️⃣ Image **agile‑env‑app**  

```dockerfile
# Dockerfile‑app
# ── Étape 1 – Composer (build only) ───────────────────────────────────────
FROM composer:latest AS composer

# ── Étape 2 – Application PHP + Apache ─────────────────────────────────────
FROM php:7.3-apache-buster

# Proxy d’entreprise (à adapter ou supprimer)
ENV http_proxy  "http://pfrie-std.proxy.e2.rie.gouv.fr:8080"
ENV https_proxy "http://pfrie-std.proxy.e2.rie.gouv.fr:8080"

# Installation des dépendances système
RUN apt-get update && \
    apt-get install -y git zip unzip vim \
        libpq-dev libicu-dev && \
    docker-php-ext-install pdo pdo_pgsql intl

# Configuration Apache (site par défaut)
COPY docker/conf/000-default.conf /etc/apache2/sites-available/000-default.conf

# Configuration PHP (production → development)
RUN cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# Récupération de Composer depuis l’étape précédente
COPY --from=composer /usr/bin/composer /usr/bin/composer
ENV COMPOSER_ALLOW_SUPERUSER 1
```

* **Multi‑stage build** : Composer est installé dans une étape séparée, puis copié dans l’image finale pour réduire la taille.  
* **Proxy** : les variables `http_proxy`/`https_proxy` sont définies pour les environnements d’entreprise ; elles peuvent être surchargées à l’exécution.  
* **Extensions PHP** : `pdo`, `pdo_pgsql` (connexion PostgreSQL) et `intl` (gestion Unicode).  
* **Apache** : le fichier `000-default.conf` personnalise le VirtualHost (non fourni ici).  

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 🚀 Procédure de déploiement (développement)  

| Étape | Commande | Description |
|------|----------|-------------|
| 1️⃣ | `docker compose -f docker-compose.dev.yml build` | Construction des deux images (`agile-env-db` & `agile-env-app`). |
| 2️⃣ | `docker compose -f docker-compose.dev.yml up -d` | Lancement des conteneurs en arrière‑plan. |
| 3️⃣ | `docker compose -f docker-compose.dev.yml logs -f app` | Suivi en temps réel des logs de l’application. |
| 4️⃣ | `docker compose -f docker-compose.dev.yml down` | Arrêt et suppression des conteneurs, réseaux et volumes. |

> **Remarque** : le fichier `docker-compose.dev.yml` doit définir les volumes de code source (`src/`) et les variables d’environnement (`.env`) afin de permettre le rechargement à chaud pendant le développement.

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## ⚙️ Configuration applicative  

| Fichier | Rôle | Exemple de contenu (non exhaustif) |
|--------|------|------------------------------------|
| `.env` | Variables d’environnement (DB, API, etc.) | `DB_HOST=db<br>DB_PORT=5432<br>DB_USER=agile<br>DB_PASSWORD=secret` |
| `config_CAS.php` | Paramètres d’authentification CAS | ```php<br>return [<br>  'cas_server' => 'https://cas.example.com',<br>  'cas_version' => '3.0',<br>];<br>``` |
| `param.ini` | Fichier INI générique (ex. : sections `[app]`, `[logging]`) | ```ini<br>[app]<br>debug=true<br>[logging]<br;level=INFO``` |

Ces fichiers sont montés dans le conteneur via le `docker‑compose.dev.yml` (volume ou variable d’environnement).  

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 🏗️ Diagramme d’architecture (Docker)  

```mermaid
graph TD
    subgraph Host;
        A[Docker Engine]
    end
    subgraph Services;
        DB[PostgreSQL<br/>agile-env-db] 
        APP[PHP 7.3 + Apache<br/>agile-env-app]
    end
    A --> DB;
    A --> APP;
    DB -->|postgres://user_pwd@db_5432/dbname| APP;
    APP -->|HTTP 80| Browser[Client Browser]

    classDef db fill:#e8f5e9,stroke:#2e7d32;
    classDef app fill:#e3f2fd,stroke:#1565c0;
    class DB db;
    class APP app;
```

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 🔐 Considérations de sécurité  

| Aspect | Action recommandée |
|--------|-------------------|
| **Secrets** | Ne jamais stocker les mots de passe directement dans le dépôt ; utiliser des variables d’environnement (`.env`) et les injecter via le compose (`env_file`). |
| **Proxy** | Vérifier que les variables `http_proxy`/`https_proxy` ne sont pas propagées en production ; les désactiver (`ENV http_proxy ""`). |
| **Mises à jour** | Mettre à jour régulièrement les images de base (`postgres:11-alpine`, `php:7.3-apache-buster`) pour bénéficier des correctifs de sécurité. |
| **Permissions** | Restreindre les permissions du répertoire `src/` (lecture‑seule en prod) et désactiver le montage de volumes de code source en production. |
| **User non‑root** | Ajouter un utilisateur non‑root dans le Dockerfile‑app et exécuter Apache avec cet utilisateur (`RUN useradd -m appuser && chown -R appuser:www-data /var/www/html`). |

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 📦 Gestion des dépendances  

| Type | Gestionnaire | Exemple de commande |
|------|--------------|---------------------|
| **PHP** | Composer | `composer install --no-dev --optimize-autoloader` (exécuté dans le conteneur). |
| **OS** | APT (Debian) | `apt-get install -y libpq-dev libicu-dev` (déclaré dans le Dockerfile). |
| **JavaScript** | npm / yarn (optionnel) | Les lignes commentées dans le Dockerfile montrent comment installer `yarn` (`npm install -g yarn`). |

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 📄 Licence & contributions  

*Le projet ne comporte pas de fichier de licence dans l’arborescence fournie. Il est recommandé d’ajouter un fichier `LICENSE` (MIT, Apache‑2.0, etc.) afin de clarifier les droits d’utilisation.*  

Les contributions doivent respecter les conventions suivantes :

1. **Branching** : `feature/<nom>` pour les nouvelles fonctionnalités, `bugfix/<nom>` pour les correctifs.  
2. **Commit messages** : format `type(scope): description` (ex. `feat(db): add initial schema`).  
3. **CI** : intégrer une pipeline GitLab CI qui exécute `composer install` et `phpunit` (si des tests existent).  

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

## 📚 Références internes  

| Référence | Description |
|-----------|-------------|
| `docker/db/Dockerfile` | Construction de l’image PostgreSQL. |
| `Dockerfile-app` | Construction de l’image PHP + Apache. |
| `docker/conf/000-default.conf` | Configuration du VirtualHost Apache (non détaillée). |
| `docker/extra/app-conf/.env` | Exemple de variables d’environnement. |
| `docker/extra/app-conf/config_CAS.php` | Configuration CAS (authentification unique). |
| `docker/extra/app-conf/param.ini` | Paramètres généraux de l’application. |
| `docker-compose.dev.yml` | Orchestration des services en mode développement. |

↩ [Retour au sommaire](#documentation-technique-du-projet-agile-env)

---  

*Fin du document*