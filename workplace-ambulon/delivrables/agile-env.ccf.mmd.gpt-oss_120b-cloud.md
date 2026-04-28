# 📄 Cahier des Charges Fonctionnel (CCF) – **agile‑env**  

[TOC]

---

## 1️⃣ Introduction et contexte du projet {#intro}

| Élément | Description |
|---|---|
| **Nom du projet** | **agile‑env** – Environnement de développement agile basé sur Docker |
| **Organisation** | *WarchoLife / Gitlab_Applications / ambulon* |
| **Objectif stratégique** | Fournir, via une stack Docker, un **environnement reproductible, isolé et configurable** permettant aux équipes de développement de **développer, tester et livrer** rapidement des applications PHP/Apache avec une base de données PostgreSQL. |
| **Périmètre fonctionnel** | <ul><li>🟢 **Inclus** : création d’images Docker (PHP‑Apache, PostgreSQL), configuration réseau & proxy, scripts d’initialisation DB, fichiers de configuration Apache/PHP, gestion des variables d’environnement.</li><li>🔴 **Exclus** : développement de l’application métier, orchestration de production, monitoring avancé, gestion du scaling horizontal.</li></ul> |
| **Livrables attendus** | <ul><li>Documentation technique (Dockerfiles, docker‑compose, scripts d’initialisation).</li><li>Environnement Docker fonctionnel (docker‑compose.yml).</li><li>Guide d’utilisation pour les développeurs.</li></ul> |
| **Contraintes majeures** | <ul><li>Compatibilité avec les **proxy d’entreprise** (`http_proxy`/`https_proxy`).</li><li>Utilisation d’**images officielles** (php:7.3‑apache‑buster, postgres:11‑alpine, composer:latest).</li><li>Respect des bonnes pratiques de **sécurité** (réduction des droits root, variables sensibles hors code).</li></ul> |

---

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) {#needs}

| Fonction de service (FS) | Description (quoi) | Critères d’appréciation | Pondération | Contraintes associées |
|---|---|---|---|---|
| **FS‑01** – Provisionner un conteneur **PostgreSQL** | Mettre à disposition une base de données PostgreSQL 11 prête à être initialisée via des scripts SQL. | <ul><li>Temps de démarrage ≤ 30 s.</li><li>Base accessible sur `localhost:5432`.</li><li>Initialisation réussie du schéma (`initdb/*.sql`).</li></ul> | 20 % | Image officielle `postgres:11-alpine`; volume persistant optionnel. |
| **FS‑02** – Provisionner un conteneur **PHP‑Apache** | Fournir un serveur web Apache avec PHP 7.3, extensions requises (pdo_pgsql, intl) et configuration personnalisée. | <ul><li>Port 80 exposé, page test accessible.</li><li>Extensions `pdo`, `pdo_pgsql`, `intl` installées.</li><li>Fichier `000-default.conf` appliqué.</li></ul> | 25 % | Utilisation de l’image `php:7.3-apache-buster`; respect du proxy d’entreprise. |
| **FS‑03** – Gestion des **dépendances Composer** | Permettre l’installation des dépendances PHP via Composer sans besoin d’accès internet direct (via le proxy). | <ul><li>Commande `composer install` s’exécute sans erreur.</li><li>Cache Composer persistant entre builds.</li></ul> | 15 % | Conteneur `composer:latest` utilisé en étape de build (`multi‑stage`). |
| **FS‑04** – Centraliser la **configuration** | Centraliser les paramètres d’environnement, les variables de connexion et les paramètres d’application dans des fichiers versionnés (`.env`, `config_CAS.php`, `param.ini`). | <ul><li>Variables disponibles dans le conteneur (`printenv`).</li><li>Fichier `config_CAS.php` chargé par l’application.</li></ul> | 10 % | Les fichiers ne contiennent pas de secrets en clair (ex. : usage de variables d’environnement). |
| **FS‑05** – Orchestrer le **déploiement** via `docker‑compose` | Lancer l’ensemble des services (db, app) avec un seul fichier `docker‑compose.dev.yml`. | <ul><li>Commande `docker compose up -d` démarre les deux services.</li><li>Les logs montrent la séquence correcte (db → app).</li></ul> | 15 % | Dépendances de réseau (`depends_on`), version du compose ≥ 2.0. |
| **FS‑06** – **Proxy** d’entreprise | Autoriser le conteneur à accéder à internet via les proxies d’entreprise. | <ul><li>Variables `http_proxy`/`https_proxy` injectées et reconnues par `apt-get` et `composer`.</li></ul> | 5 % | Valeurs de proxy configurables via le Dockerfile. |
| **FS‑07** – **Extensibilité** du stack | Permettre l’ajout futur de services (ex. : Redis, tests unitaires) sans refonte majeure. | <ul><li>Structure de dossiers (`docker/extra/…`) clairement séparée.</li></ul> | 5 % | Utilisation de dossiers modulaires, documentation. |

---

## 3️⃣ Acteurs et parties prenantes {#actors}

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **Développeur** | Utilisateur final du stack | Lancer rapidement un environnement de dev, tester localement. | Documentation claire, scripts `docker compose up/down`, accès aux logs. |
| **MOA (Maîtrise d’Ouvrage)** | Commanditaire | Garantir que l’environnement répond aux exigences de sécurité et de conformité. | Traçabilité des configurations, respect des proxies, aucune donnée sensible dans le repo. |
| **MOE (Maîtrise d’Œuvre)** | Responsable technique | Construire, maintenir et faire évoluer le stack. | Dockerfiles, scripts d’initialisation, CI/CD possible. |
| **CI/CD System** | Automatisation des builds/tests | Construire les images, exécuter les tests unitaires. | Étape « composer », accès aux variables d’environnement, artefacts Docker. |
| **Base de données (PostgreSQL)** | Service | Stocker les données de l’application. | Initialisation via scripts, persistance optionnelle. |
| **Serveur Web (PHP‑Apache)** | Service | Exposer l’application au développeur. | Extensions PHP, configuration Apache, accès aux variables d’environnement. |
| **RSSI (Responsable Sécurité des Systèmes d’Information)** | Supervision sécurité | S’assurer du respect des politiques de sécurité (proxy, secrets). | Analyse des Dockerfiles, audit des variables d’environnement. |

---

## 4️⃣ Cas d’usage (Use Cases) {#usecases}

### 4.1 Diagramme de cas d’utilisation (UML)  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#4B8BBE', 'edgeLabelBackground':'#FFF', 'fontSize': '12px' }}%%%%%%%%%%%%%%%%%%%%%%}%%
usecaseDiagram;
    actor Developer as Dev;
    actor CI/CD System as CICD;
    rectangle "Environnement agile‑env" {
        Dev --> (Lancer l’environnement)
        Dev --> (Accéder à l’application)
        Dev --> (Modifier la configuration)
        CICD --> (Construire les images)
        CICD --> (Exécuter les tests)
        (Lancer l’environnement) --> \(Initialiser la DB)
        (Initialiser la DB) --> \(Appliquer les scripts SQL)
        (Construire les images) --> \(Installer les dépendances Composer)
        (Accéder à l’application) --> \(Consulter l’UI via navigateur)

```

### 4.2 Table des cas d’usage

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **CU‑01** | Lancer l’environnement | Développeur | 1. Exécuter `docker compose up -d`.<br>2. Docker crée `db` puis `app`.<br>3. L’application répond sur `http://localhost`. | **AE‑01** : Port déjà utilisé → affichage d’erreur, arrêt du démarrage.<br>**AE‑02** : Proxy non accessible → `apt-get` échoue, logs d’erreur. | Docker et Docker‑Compose installés, fichier `docker‑compose.dev.yml` présent. | Services `db` et `app` en état **running**. |
| **CU‑02** | Initialiser la base de données | Docker (DB) | 1. Conteneur PostgreSQL démarre.<br>2. Script `initdb/*.sql` copié en `/dump.sql`.<br>3. `restore.sh` exécute le script. | **AE‑03** : Script SQL erroné → rollback, logs d’erreur.<br>**AE‑04** : Volume persistant manquant → perte de données. | Image `postgres:11-alpine` disponible. | Schéma DB créé, tables prêtes. |
| **CU‑03** | Installer les dépendances Composer | CI/CD System / Développeur | 1. Étape `composer` récupère le binaire.<br>2. `composer install` s’exécute dans le conteneur `app`. | **AE‑05** : Proxy non configuré → échec de téléchargement des paquets. | Variable `COMPOSER_ALLOW_SUPERUSER=1` définie. | `vendor/` présent, dépendances résolues. |
| **CU‑04** | Accéder à l’application | Développeur | 1. Ouvrir un navigateur à `http://localhost`.<br>2. Page d’accueil s’affiche. | **AE‑06** : Configuration Apache erronée → 404/500. | Conteneur `app` en cours d’exécution, port 80 exposé. | Interface fonctionnelle, logs sans erreur critique. |
| **CU‑05** | Modifier la configuration | Développeur | 1. Editer `.env` ou `config_CAS.php`.<br>2. Redémarrer le conteneur (`docker compose restart`). | **AE‑07** : Variable mal formatée → service ne démarre pas. | Accès en écriture aux fichiers de config. | Nouvelle configuration appliquée, services redémarrés. |

---

## 5️⃣ Processus métier (BPMN) {#process}

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#4B8BBE', 'edgeLabelBackground':'#FFF', 'fontSize': '12px' }}%%%%%%%%%%%%%%%%%%%%%%}%%
bpmnDiagram;
    participant Dev as "Développeur"
    participant Docker as "Docker Engine"
    participant DB as "PostgreSQL"
    participant App as "PHP‑Apache"

    Dev->>Docker: docker compose up -d;
    Docker->>DB: Crée conteneur DB;
    DB->>DB: Exécute restore.sh (init SQL)
    DB-->>Docker: Retour OK;
    Docker->>App: Crée conteneur App;
    App->>App: Installe extensions, copie config;
    App-->>Docker: Retour OK;
    Docker-->>Dev: Environnement prêt;
    Dev->>Dev: Teste l’application (browser)
    alt Erreur de démarrage;
        Docker->>Dev: Log d’erreur;
    end
```

*Description* : Le processus **« Déploiement d’un environnement de dev »** débute par le développeur qui lance `docker compose`. Le moteur Docker orchestre la création du conteneur DB, son initialisation, puis le conteneur PHP‑Apache. En cas d’erreur, les logs sont renvoyés immédiatement au développeur.

---

## 6️⃣ Règles métier et contraintes fonctionnelles {#rules}

| # | Règle métier (IF…THEN) | Source / Référence |
|---|---|---|
| **R‑01** | **IF** le fichier `.env` contient la variable `APP_ENV=production` **THEN** le conteneur `app` doit désactiver le mode debug Apache. | NF EN 16271 – Sécurité |
| **R‑02** | **IF** le proxy n’est pas reachable **THEN** le build `composer` doit échouer avec un message explicite. | ISO 29148 – Robustesse |
| **R‑03** | **IF** le script `initdb/*.sql` échoue **THEN** le conteneur DB doit être arrêté et le code d’erreur retourné. | ISO 29148 – Gestion des erreurs |
| **R‑04** | **IF** le port 80 est déjà utilisé sur l’hôte **THEN** le compose doit lever une exception et proposer le port alternatif 8080. | ISO 29148 – Disponibilité |
| **R‑05** | **IF** une variable sensible (ex. `DB_PASSWORD`) est stockée dans le dépôt **THEN** le pipeline CI doit bloquer le commit. | RGPD / Politique interne |
| **R‑06** | **IF** le conteneur `app` démarre **THEN** le fichier `000-default.conf` doit être chargé et les logs Apache doivent indiquer “Listening on 0.0.0.0:80”. | ISO 29148 – Vérifiabilité |
| **R‑07** | **IF** un développeur modifie `config_CAS.php` **THEN** le conteneur doit être redémarré pour prendre en compte les changements. | Bonnes pratiques de configuration |

---

## 7️⃣ Parcours utilisateurs (User Journey) {#journey}

| Étape | Action du développeur | Interaction système | Critères d’acceptation (GWT) |
|---|---|---|---|
| **1. Démarrage** | Ouvre le terminal, lance `docker compose up -d`. | Docker crée les conteneurs, initialise la DB. | **Given** le dépôt cloné, **When** la commande est exécutée, **Then** les deux services sont en `running` en < 30 s. |
| **2. Vérification** | Ouvre `http://localhost` dans le navigateur. | Le serveur Apache répond avec la page d’accueil. | **Given** les services en cours, **When** la page est demandée, **Then** le code HTTP = 200 et le contenu attendu s’affiche. |
| **3. Configuration** | Modifie `.env` (ex. `APP_DEBUG=false`). | Le conteneur `app` doit être redémarré (`docker compose restart app`). | **Given** le fichier modifié, **When** le redémarrage est lancé, **Then** l’application reflète la nouvelle configuration. |
| **4. Tests unitaires (CI)** | Le pipeline CI déclenche `docker compose up -d` puis `composer install` et `phpunit`. | Les dépendances sont installées, les tests s’exécutent. | **Given** le pipeline, **When** la phase d’installation est terminée, **Then** le taux de succès des tests ≥ 95 %. |
| **5. Nettoyage** | Exécute `docker compose down -v`. | Tous les conteneurs sont arrêtés, les volumes supprimés. | **Given** l’environnement en cours, **When** la commande est lancée, **Then** aucune ressource Docker ne reste active. |

---

## 8️⃣ Modèle Conceptuel de Données (MCD) {#mcd}

```mermaid
classDiagram
    class Application {
        +string name;
        +string version;
        +string entry_point;

    class Database {
        +string engine;
        +string version;
        +string host;
        +int    port;
        +string name;

    class ConfigFile {
        +string path;
        +string type;

    class EnvVariable {
        +string key;
        +string value;

    Application "1" --> "1" Database : uses;
    Application "1" --> "*" ConfigFile : reads;
    Application "1" --> "*" EnvVariable : reads;
    Database "1" --> "*" EnvVariable : reads
```

*Notes* : Le modèle reste **abstrait** (pas de type SQL). Il décrit les concepts métier : **Application**, **Database**, **Configuration files**, **Variables d’environnement**.

---

## 9️⃣ Critères d’acceptation et validation {#acceptance}

| Fonction (FS) | Critère d’acceptation | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| **FS‑01** | DB démarre en ≤ 30 s, schéma créé. | Test automatisé `docker compose up` + script de ping DB. | MOE | **Must** |
| **FS‑02** | Apache écoute sur le port 80, extensions installées. | `curl http://localhost` → code 200, `php -m` dans le conteneur. | MOE | **Must** |
| **FS‑03** | `composer install` aboutit sans erreur proxy. | Pipeline CI, logs Composer. | CI/CD | **Must** |
| **FS‑04** | Variables d’environnement accessibles via `printenv`. | `docker exec app env | grep VAR`. | MOE | **Should** |
| **FS‑05** | `docker compose up -d` lance les deux services. | Inspection `docker ps`. | Développeur | **Must** |
| **FS‑06** | Proxy appliqué aux appels `apt-get`. | `apt-get update` log → utilisation du proxy. | MOE | **Could** |
| **FS‑07** | Ajout d’un nouveau service (`redis`) ne modifie pas la structure existante. | Ajout d’un service test, exécution du compose. | MOE | **Could** |

---

## 🔟 Annexes {#annexes}

### A. Glossaire {#glossary}

| Terme | Définition |
|---|---|
| **Dockerfile** | Fichier texte décrivant les étapes de construction d’une image Docker. |
| **docker‑compose** | Outil permettant d’orchestrer plusieurs conteneurs à partir d’un fichier YAML. |
| **Multi‑stage build** | Technique Docker permettant de séparer les étapes de build et de runtime pour réduire la taille de l’image finale. |
| **Proxy d’entreprise** | Serveur intermédiaire (HTTP/HTTPS) imposé par le réseau interne pour filtrer le trafic sortant. |
| **Composer** | Gestionnaire de dépendances pour le langage PHP. |
| **BPMN** | Notation standard pour modéliser les processus métier. |
| **MoSCoW** | Méthode de priorisation : Must, Should, Could, Won’t. |
| **RGPD** | Règlement Général sur la Protection des Données (UE). |

### B. Référentiels et normes applicables {#normes}

| Référence | Intitulé | Application |
|---|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin | Définition des fonctions de service (FS). |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences | Structuration des exigences, critères d’acceptation. |
| **ISO/IEC 19505** | UML 2.x | Diagrammes de cas d’usage. |
| **ISO/IEC 19510** | BPMN | Modélisation du processus de déploiement. |
| **RGPD** | Règlement UE 2016/679 | Gestion des données personnelles (ex. : variables d’environnement). |
| **RGS** | Référentiel Général de Sécurité (France) | Utilisation de proxy, gestion des secrets. |

### C. Historique des versions du document {#history}

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| **1.0** | 2026‑04‑28 | ChatGPT (OpenAI) | Création du CCF complet (structure NF EN 16271, ISO 29148). |
| **1.1** | – | – | À venir – mise à jour après validation MOE. |

---

*Fin du Cahier des Charges Fonctionnel – **agile‑env**.*  

↩ Retour au **sommaire**.  