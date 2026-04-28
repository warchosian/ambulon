# 📘 Cahier des Charges Fonctionnel (CCF) – Projet **ocle‑docker**  

[TOC]

---

## 1️⃣ Introduction et contexte du projet <a id="intro"></a>

| Élément | Description |
|---|---|
| **Nom du projet** | **ocle‑docker** – mise à disposition d’une application web Java (WAR) via conteneurs Docker, avec persistance PostgreSQL. |
| **Contexte organisationnel** | Le projet s’inscrit dans la modernisation des services internes d’un ministère : déploiement automatisé, isolation des dépendances et amélioration de la maintenabilité. |
| **Objectifs stratégiques** | 1. **Réduction du temps de mise en production** grâce à l’infrastructure as code (Docker, Docker‑Compose).<br>2. **Fiabilité** du service (redémarrage automatique, persistance des données).<br>3. **Scalabilité** éventuelle (possibilité de répliquer les conteneurs). |
| **Périmètre fonctionnel** | **Inclus** :<br>• Construction d’une image Docker contenant le serveur Tomcat et le WAR `ocle‑web‑1.0.8.war`.<br>• Déploiement d’une base PostgreSQL pré‑configurée.<br>• Gestion des uploads (répertoire `/uploads`, limites de taille).<br>• Orchestration via `docker‑compose.yml` (ports, dépendances, volumes).<br>**Exclus** :<br>• Développement de la logique métier de l’application web (hors du CCF).<br>• Gestion du réseau externe (ex. : reverse‑proxy, certificats SSL). |
| **Livrables attendus** | - Fichiers d’infrastructure (Dockerfile, docker‑compose.yml, configuration).<br>- Documentation d’exploitation (procédures de déploiement, critères d’acceptation).<br>- Rapport de validation fonctionnelle. |

↩︎ [Retour au sommaire](#toc)

---

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) <a id="needs"></a>

| **N°** | **Fonction de service** (Quoi) | **Description** | **Critères d’appréciation** | **Pondération** | **Contraintes** |
|---|---|---|---|---|---|
| **F1** | **Héberger l’application web** | Mettre à disposition le WAR `ocle‑web‑1.0.8.war` sur un serveur d’applications Tomcat accessible via HTTP/HTTPS. | - Temps de mise en route ≤ 30 s après `docker compose up`.<br>- Disponibilité ≥ 99,5 % sur 30 jours.<br>- URL `http://<host>:8080/` renvoie le code HTTP 200. | 30 % | - Utiliser l’image officielle `tomcat:9.0.46‑jdk11‑openjdk‑slim‑buster`.<br>- Le conteneur doit être nommé `ocle-app`. |
| **F2** | **Persister les données métier** | Fournir une base PostgreSQL 12.7 avec les schémas requis, accessible depuis le conteneur applicatif. | - Connexion JDBC réussie au démarrage de Tomcat.<br>- Temps moyen de réponse ≤ 200 ms pour les requêtes simples.<br>- Sauvegarde quotidienne du volume `pgdata`. | 25 % | - Variables d’environnement `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` fixes (`ocle`).<br>- Volume persistant `./db/pgdata`. |
| **F3** | **Gérer les téléchargements de fichiers** | Autoriser l’upload de fichiers depuis l’application vers le répertoire partagé `/uploads`. | - Taille maximale d’un fichier acceptée : 100 MB.<br>- Taille maximale de la requête HTTP : 25 MB.<br>- Le répertoire `/uploads` est créé et possède les droits d’écriture pour l’utilisateur Tomcat. | 15 % | - Paramètres Spring `spring.servlet.multipart.max‑file‑size` et `max‑request‑size` configurés.<br>- Le répertoire doit être monté hors du conteneur (volume partagé). |
| **F4** | **Orchestrer le déploiement** | Utiliser Docker‑Compose pour lancer les deux services (app + DB) avec leurs dépendances. | - `docker compose up -d` démarre les deux conteneurs sans erreur.<br>- Le service `ocle` ne démarre qu’après que le service `db` signale son état “healthy”. | 15 % | - `depends_on` déclaré dans `docker‑compose.yml`.<br>- Exposition du port 8080 (host) → 8080 (container). |
| **F5** | **Assurer la traçabilité de la configuration** | Versionner les fichiers de configuration et les scripts d’initialisation. | - Chaque commit possède un identifiant Git unique.<br>- Le Dockerfile indique le maintainer et la version de l’image. | 10 % | - `LABEL maintainer` présent dans le Dockerfile.<br>- Aucun fichier binaire n’est versionné. |
| **F6** | **Sécuriser les accès** | Restreindre l’accès aux conteneurs aux seules machines autorisées. | - Le port 5432 n’est pas exposé à l’extérieur (seulement à l’intérieur du réseau Docker).<br>- Le conteneur DB accepte uniquement les connexions depuis le conteneur `ocle`. | 5 % | - `expose: "5432"` (pas `ports`).<br>- `listen_addresses='*'` uniquement au sein du réseau Docker. |

↩︎ [Retour au sommaire](#toc)

---

## 3️⃣ Acteurs et parties prenantes <a id="actors"></a>

| **Acteur** | **Rôle** | **Objectifs** | **Besoins spécifiques** |
|---|---|---|---|
| **MOA** (Maîtrise d’Ouvrage) | Commanditaire métier | Garantir la disponibilité du service pour les usagers finaux. | - Respect des SLA (temps de réponse, disponibilité).<br>- Documentation d’exploitation claire. |
| **MOE** (Maîtrise d’Œuvre) | Équipe DevOps / Développeurs | Concevoir, tester et livrer l’infrastructure Docker. | - Scripts de build reproductibles.<br>- Possibilité de mise à jour de l’image (nouvelle version du WAR). |
| **Utilisateurs finaux** | Agents métier qui utilisent l’interface web | Accéder aux fonctionnalités métier (non détaillées dans ce CCF). | - Interface web disponible 24/7.<br>- Upload de documents jusqu’à 100 MB. |
| **Administrateur base de données** | Gestionnaire PostgreSQL | Assurer l’intégrité et la sauvegarde des données. | - Accès aux volumes `pgdata` et `pglogs`.<br>- Procédures de backup/restauration. |
| **RSSI** (Responsable Sécurité des Systèmes d’Information) | Garant de la sécurité | Limiter la surface d’exposition. | - Aucun port DB ouvert à l’extérieur.<br>- Gestion des secrets (passwords) via variables d’environnement. |
| **Plateforme CI/CD** | Système d’intégration continue | Automatiser le build & le déploiement. | - Dockerfile doit être “build‑able” sans interaction manuelle.<br>- Tag d’image versionné. |

↩︎ [Retour au sommaire](#toc)

---

## 4️⃣ Cas d’usage (Use Cases) <a id="usecases"></a>

### 4.1 Diagramme de cas d’utilisation (UML)  

```mermaid
%%{init: {'theme':'default'}}%%%%
usecaseDiagram;
    actor MOE / DevOps as DevOps;
    actor Utilisateurs finaux as Users;
    actor Administrateur DB as DBA;
    actor RSSI as Sec;
    rectangle "Système ocle‑docker" {
        usecase "Déployer l’application" as UC1;
        usecase "Démarrer/Arrêter les conteneurs" as UC2;
        usecase "Uploader un fichier" as UC3;
        usecase "Sauvegarder la base" as UC4;
        usecase "Mettre à jour le WAR" as UC5;
        usecase "Vérifier la conformité sécurité" as UC6;
    }

    DevOps --> UC1;
    DevOps --> UC2;
    Users --> UC3;
    DBA --> UC4;
    DevOps --> UC5;
    Sec --> UC6
```

### 4.2 Tableau détaillé des cas d’usage  

| **N°** | **Nom du cas d’usage** | **Acteur(s) principal(aux)** | **Scénario nominal** | **Scénarios alternatifs / d’erreur** | **Pré‑conditions** | **Post‑conditions** |
|---|---|---|---|---|---|---|
| **UC1** | Déployer l’application | MOE / DevOps | 1. Exécuter `docker compose up -d`.<br>2. Docker crée le réseau, les volumes et les conteneurs.<br>3. Tomcat démarre, déploie le WAR.<br>4. L’application répond sur `http://localhost:8080/`. | - Si le port 8080 est déjà occupé → affichage d’une erreur et arrêt du conteneur.<br>- Si la construction de l’image échoue → rollback du compose. | Docker installé, fichiers source présents. | Conteneurs `ocle-app` et `ocle-db` en état **running**. |
| **UC2** | Démarrer/Arrêter les conteneurs | MOE / DevOps | 1. `docker compose start` → tous les services démarrent.<br>2. `docker compose stop` → arrêt gracieux. | - Si le conteneur ne répond pas au stop → `docker compose kill`. | Services déjà créés (via `up`). | État des services conforme à la commande. |
| **UC3** | Uploader un fichier | Utilisateur final | 1. L’utilisateur sélectionne un fichier via l’interface web.<br>2. Le serveur accepte le fichier (≤ 100 MB).<br>3. Le fichier est stocké dans `/uploads`. | - Fichier > 100 MB → message d’erreur “Taille maximale dépassée”.<br>- Échec d’écriture → message d’erreur “Impossible d’enregistrer”. | Session utilisateur active, répertoire `/uploads` accessible en écriture. | Le fichier est présent dans le répertoire partagé et son nom est enregistré en base si nécessaire. |
| **UC4** | Sauvegarder la base | Administrateur DB | 1. Exécuter le script `pg_dump` sur le volume `pgdata`.<br>2. Archive stockée dans un répertoire de backup. | - Espace disque insuffisant → alerte et abort. | Accès au conteneur `ocle-db`. | Backup complet disponible, journal de backup mis à jour. |
| **UC5** | Mettre à jour le WAR | MOE / DevOps | 1. Remplacer `ocle-web-1.0.8.war` par la nouvelle version.<br>2. Relancer le service `ocle` (`docker compose restart ocle`). | - Si le WAR est corrompu → Tomcat ne démarre pas → rollback à la version précédente. | Nouvelle version du WAR testée hors production. | Application redémarrée avec le nouveau WAR, aucune perte de données. |
| **UC6** | Vérifier la conformité sécurité | RSSI | 1. Scanner les conteneurs (ex. : Trivy).<br>2. Vérifier que le port 5432 n’est pas publié. | - Vulnérabilité critique détectée → blocage du déploiement et remontée. | Environnement de test disponible. | Rapport de conformité signé, déploiement autorisé. |

↩︎ [Retour au sommaire](#toc)

---

## 5️⃣ Processus métier (BPMN) <a id="processes"></a>

> **Processus clé** : *Déploiement continu de l’application*  

```mermaid
%%{init: {'theme':'default'}}%%%%
bpmnDiagram;
    participant DevOps;
    participant DockerEngine as "Docker Engine"
    participant Registry as "Registry (optionnel)"
    participant DB as "PostgreSQL"
    participant Tomcat as "Tomcat (app)"

    DevOps->>DockerEngine: git pull + docker compose build;
    DockerEngine-->>DevOps: Image construite;
    DevOps->>DockerEngine: docker compose up -d;
    DockerEngine->>DB: create container + volume;
    DockerEngine->>Tomcat: create container + copy WAR;
    Tomcat->>DB: test connexion JDBC;
    alt Connexion OK;
        Tomcat->>DevOps: Application ready (HTTP 200)
    else Connexion KO;
        Tomcat->>DevOps: Erreur de démarrage;
        DevOps->>DockerEngine: docker compose down;
    end
```

*Ce diagramme décrit les étapes automatisées du build jusqu’à la mise en production, incluant la validation de la connexion à la base.*

↩︎ [Retour au sommaire](#toc)

---

## 6️⃣ Règles métier et contraintes fonctionnelles <a id="rules"></a>

| **ID** | **Règle / Contrainte** | **Formulation** | **Source** |
|---|---|---|---|
| **R1** | Taille maximale d’un fichier uploadé | `if (file.size > 100 MB) then reject with error "Taille maximale dépassée"` | `application.properties` (`spring.servlet.multipart.max-file-size`) |
| **R2** | Taille maximale de la requête HTTP | `if (request.contentLength > 25 MB) then reject` | `application.properties` (`spring.servlet.multipart.max-request-size`) |
| **R3** | Accès à la base de données | `DB connection string = "jdbc:postgresql://db:5432/ocle"` | `application.properties` (`spring.datasource.url`) |
| **R4** | Authentification DB | `username = "ocle"` **AND** `password = "ocle"` | `application.properties` (`spring.datasource.username/password`) |
| **R5** | Persistance des données | `volume "./db/pgdata"` doit être monté en lecture‑écriture | `docker-compose.yml` |
| **R6** | Sécurité du port DB | Le port 5432 n’est **pas** exposé à l’hôte (`expose` seulement). | `docker-compose.yml` |
| **R7** | Dossier d’upload partagé | Le répertoire `/uploads` doit être présent dans le conteneur et posséder les droits `rw` pour l’utilisateur Tomcat. | `Dockerfile` (`RUN mkdir -p /uploads`) |
| **R8** | Gestion des logs DB | Les logs sont redirigés vers le volume `./db/pglogs`. | `docker-compose.yml` |
| **R9** | Conformité RGPD (si applicable) | Toute donnée personnelle stockée doit être chiffrée au repos (hors périmètre technique du CCF). | Norme interne RGPD |
| **R10** | Traçabilité des builds | Chaque image Docker doit porter le label `maintainer` avec l’adresse mail du responsable. | `Dockerfile` (`LABEL maintainer`) |

↩︎ [Retour au sommaire](#toc)

---

## 7️⃣ Parcours utilisateurs (User Journey) <a id="journey"></a>

| **Étape** | **Acteur** | **Interaction avec le système** | **Critère d’acceptation (Given/When/Then)** |
|---|---|---|---|
| **1. Accès à l’application** | Utilisateur | Ouvre le navigateur et saisit `http://<host>:8080/`. | **Given** le service `ocle-app` est `running` <br> **When** l’utilisateur charge l’URL <br> **Then** le serveur renvoie un code HTTP 200 et la page d’accueil s’affiche. |
| **2. Authentification (si applicable)** | Utilisateur | Saisit ses identifiants dans le formulaire de login. | **Given** l’utilisateur possède un compte valide <br> **When** il soumet le formulaire <br> **Then** il est redirigé vers son tableau de bord. |
| **3. Upload d’un document** | Utilisateur | Clique sur “Ajouter un fichier”, sélectionne un fichier (≤ 100 MB). | **Given** le fichier respecte la taille maximale <br> **When** il confirme l’upload <br> **Then** le fichier apparaît dans la liste et est physiquement présent dans `/uploads`. |
| **4. Consultation d’un document** | Utilisateur | Sélectionne un fichier dans la liste, le télécharge. | **Given** le fichier existe dans `/uploads` <br> **When** il clique sur “Télécharger” <br> **Then** le navigateur déclenche le téléchargement du fichier. |
| **5. Gestion de l’incident** | Administrateur | Consulte les logs via le volume `./db/pglogs` ou le conteneur Tomcat. | **Given** un incident détecté <br> **When** l’administrateur ouvre le fichier de log <br> **Then** il identifie la cause et applique la résolution (restart, rollback). |

↩︎ [Retour au sommaire](#toc)

---

## 8️⃣ Modèle Conceptuel de Données (MCD) <a id="mcd"></a>

> **Note** : Le modèle ci‑dessous ne décrit que les entités liées à la **gestion des uploads** (exemple simplifié). Les tables métiers propres à l’application sont hors périmètre du présent CCF.

```mermaid
classdiagram;
    class Upload {
        +String id {PK}
        +String filename;
        +Long size;
        +DateTime uploadedAt;
        +String path;
    }
    class User {
        +String id {PK}
        +String login;
        +String email;
    }
    class Role {
        +String name {PK}
    }

    User "1" --> "*" Upload : owns;
    User "1" --> "*" Role : has
```

*Entités* :

| **Entité** | **Attributs clés** | **Description** |
|---|---|---|
| **Upload** | `id` (UUID), `filename`, `size`, `uploadedAt`, `path` | Représente un fichier stocké dans `/uploads`. |
| **User** | `id`, `login`, `email` | Compte utilisateur de l’application (hors du CCF). |
| **Role** | `name` | Rôle de sécurité (ex. : `ADMIN`, `USER`). |

↩︎ [Retour au sommaire](#toc)

---

## 9️⃣ Critères d’acceptation et validation <a id="validation"></a>

| **Fonction** | **Critère d’acceptation** | **Méthode de validation** | **Responsable** | **Priorité** |
|---|---|---|---|---|
| **F1 – Hébergement** | L’application répond HTTP 200 sur `http://localhost:8080/` en < 30 s. | Test fonctionnel automatisé (curl) après `docker compose up`. | MOE | **M** (Must) |
| **F2 – Persistance DB** | Connexion JDBC réussie et temps de réponse ≤ 200 ms. | Script JUnit / Postman avec requête `SELECT 1`. | MOE | **M** |
| **F3 – Upload** | Rejet des fichiers > 100 MB, acceptation ≤ 100 MB. | Tests d’API (Postman) avec fichiers de tailles limites. | MOE | **M** |
| **F4 – Orchestration** | `docker compose up -d` démarre les deux services sans erreur. | Observation du log `docker compose ps`. | MOE | **M** |
| **F5 – Traçabilité** | Dockerfile contient le label `maintainer`. | Revue du Dockerfile (code review). | MOE | **S** (Should) |
| **F6 – Sécurité DB** | Le port 5432 n’est pas visible depuis l’hôte (`netstat -tln`). | Scan réseau local. | RSSI | **M** |
| **F7 – Backup DB** | Backup quotidien généré, taille ≤ 80 % de l’espace disque disponible. | Script de backup + vérification du disque. | DBA | **C** (Could) |
| **F8 – Documentation** | Guide d’exploitation (déploiement, rollback) disponible en Markdown. | Relecture par le MOA. | MOA | **S** |

**Notation MoSCoW** :  
- **M** = Must (obligatoire)  
- **S** = Should (souhaitable)  
- **C** = Could (optionnel)  
- **W** = Won’t (hors périmètre)

↩︎ [Retour au sommaire](#toc)

---

## 🔟 Annexes <a id="annexes"></a>

### 10.1 Glossaire métier

| **Terme** | **Définition** |
|---|---|
| **WAR** | Web Application Archive – paquet contenant les classes, bibliothèques et ressources d’une application Java EE. |
| **Tomcat** | Serveur d’applications Java implémentant les spécifications Servlet/JSP. |
| **Docker Compose** | Outil de définition et d’orchestration de multi‑conteneurs Docker via un fichier YAML. |
| **Upload** | Action de transférer un fichier depuis le client vers le serveur. |
| **Volume** | Stockage persistant partagé entre le conteneur et l’hôte. |
| **Maintainer** | Personne responsable de la maintenance de l’image Docker (adresse email fournie dans le label). |

### 10.2 Référentiels et normes applicables

| **Référence** | **Intitulé** |
|---|---|
| NF EN 16271 | Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel. |
| ISO/IEC/IEEE 29148:2018 | Ingénierie des exigences – Cycle de vie. |
| ISO/IEC 19505 | UML 2.x – Notation et diagrammes. |
| ISO/IEC 19510 | BPMN – Modélisation des processus métier. |
| RGPD (art. 32) | Sécurité du traitement des données à caractère personnel. |
| RGS (Référentiel Général de Sécurité) | Exigences de sécurité applicables aux systèmes d’information de l’État français. |

### 10.3 Historique des versions du document

| **Version** | **Date** | **Auteur** | **Modifications** |
|---|---|---|---|
| 1.0 | 2026‑04‑28 | ChatGPT (OpenAI) | Création du CCF complet (sections 1‑10). |
| 1.1 | – | – | – (future évolution) |

↩︎ [Retour au sommaire](#toc)

--- 

*Document généré automatiquement, prêt à être utilisé dans VS Code ou Obsidian.*