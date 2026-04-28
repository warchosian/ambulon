# 📘 Dossier d’Architecture Technique (DAT) – **agile‑env**  

[TOC]

---

## 1. Introduction et objectifs  

**Vision fonctionnelle**  
> *agile‑env* est une petite plateforme web destinée à fournir un environnement de configuration et d’orchestration d’applications conteneurisées (Docker) à destination des équipes de développement et d’exploitation. Elle expose une interface web permettant :  

1. la gestion des variables d’environnement,  
2. la configuration du serveur CAS (authentification unique),  
3. le déclenchement de scripts d’initialisation de bases de données.  

**Objectifs qualité orientés utilisateur**  

| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Performance** – temps de réponse < 200 ms pour les pages d’administration | Fluidité de la prise en main par les développeurs |
| 2 | **Sécurité** – authentification via CAS, chiffrement des secrets | Conformité aux exigences de l’État (RGPD, SSI) |
| 3 | **Maintenabilité** – découpage en micro‑services Docker, CI/CD automatisé | Réduction du temps de mise à jour et de correction |
| 4 | **Observabilité** – logs centralisés, métriques exposées | Détection rapide des incidents en production |
| 5 | **Portabilité** – exécution sur tout cluster Docker (local, cloud) | Support des environnements de dev / recette / prod |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 2. Niveau 1 – Vue Contexte (System Context)  

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Context.puml

Person(admin, "Administrateur", "Configure l’application via l’UI")
Person(dev, "Développeur", "Consomme les variables d’environnement via les scripts CI")

System_Boundary(s1, "agile‑env") {
    System(app, "agile‑env", "Plateforme web de gestion d’environnements Docker")

System_Ext(cas, "CAS Server", "Service d’authentification unique (SSO)")
System_Ext(pg, "PostgreSQL", "Base de données métier")

Rel(admin, app, "Utilise")
Rel(dev, app, "Consomme l’API")
Rel(admin, cas, "S’authentifie via")
Rel(app, cas, "Vérifie le ticket SSO")
Rel(app, pg, "Lecture/écriture de configuration")
```

### Acteurs principaux  

| Acteur | Objectif |
|--------|----------|
| **Administrateur** | Configurer, versionner et déployer les variables d’environnement |
| **Développeur** | Récupérer les paramètres d’exécution depuis le dépôt CI/CD |
| **CAS Server** (externe) | Fournir l’authentification SSO |
| **PostgreSQL** (externe) | Persister les données de configuration |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 3. Parties prenantes  

| Rôle | Attente principale |
|------|---------------------|
| **MOA (Maîtrise d’Ouvrage)** | Disponibilité 99 % des services d’administration |
| **RSSI** | Conformité aux exigences D‑I‑C‑T (Disponibilité, Intégrité, Confidentialité, Traçabilité) |
| **Équipe DevOps** | Processus CI/CD simple, conteneurs versionnés |
| **Utilisateurs finaux (Admins/Dev)** | Interface claire, temps de réponse rapide |
| **Direction IT** | Coût d’infrastructure maîtrisé, évolutivité |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 4. Contraintes  

### 4.1 Techniques  

| Type | Description |
|------|-------------|
| **Langage / Framework** | PHP 7.3 + Apache, Composer pour la gestion des dépendances |
| **Base de données** | PostgreSQL 11 (image officielle) |
| **Conteneurisation** | Docker ≥ 20, Docker‑Compose pour le développement |
| **Proxy** | Nginx (cluster) en front‑end, TLS terminée au niveau du load‑balancer |
| **Gestion des secrets** | `.env` + chiffrement AES‑256 lors du backup |
| **CI/CD** | GitLab CI, images construites dans le pipeline `docker‑build` |

### 4.2 Organisationnelles  

* Respect des processus de validation de la DSI (revues de code, tests de sécurité).  
* Déploiement uniquement via les environnements pré‑définis (dev, recette, prod).  

### 4.3 Réglementaires  

| D‑I‑C‑T | Exigence |
|--------|----------|
| **Disponibilité** | SLA ≥ 99 % pour l’UI et l’API |
| **Intégrité** | Vérification d’intégrité des sauvegardes (checksum SHA‑256) |
| **Confidentialité** | Chiffrement des backups, accès restreint aux rôles `admin` |
| **Traçabilité** | Logs d’accès consignés dans Elasticsearch, conservés 180 jours |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 5. Niveau 2 – Vue Conteneurs (Containers)  

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Container.puml

System_Boundary(s1, "agile‑env") {
    Container(web, "WebApp", "PHP 7.3‑Apache (Docker)", "Interface web & API REST")
    ContainerDb(db, "PostgreSQL", "PostgreSQL 11", "Persist la configuration")
    Container(nginx, "Nginx LB", "Nginx", "Reverse‑proxy, TLS termination")

Rel(nginx, web, "HTTP/HTTPS")
Rel(web, db, "JDBC/SQL")
Rel(web, cas, "OAuth2 / SAML (SSO)")

System_Ext(cas, "CAS Server", "Authentification unique")
```

### Description des conteneurs  

| Conteneur | Responsabilité | Technologie | Interactions clés |
|----------|----------------|------------|-------------------|
| **WebApp** | UI, API, logique métier | PHP 7.3, Apache, Composer, `config_CAS.php`, `param.ini` | → PostgreSQL (CRUD), → CAS (auth), ← Nginx (HTTPS) |
| **PostgreSQL** | Persistance des variables d’environnement et métadonnées | PostgreSQL 11‑alpine | ← WebApp (SQL) |
| **Nginx LB** | Load‑balancing, TLS termination, redirection HTTP→HTTPS | Nginx (cluster) | ↔ WebApp (HTTP) |
| **Docker‑Compose (dev)** | Orchestration locale pour le développeur | docker‑compose.yml (non‑fourni) | – |

### Décisions architecturales majeures  

| Décision | Raison |
|----------|--------|
| **Micro‑services Docker** (WebApp + DB séparés) | Isolation des responsabilités, scalabilité indépendante |
| **Reverse‑proxy Nginx dédié** | Gestion centralisée du TLS, possibilité d’ajouter d’autres services |
| **Utilisation de Composer en phase de build** | Réduction du temps de build en cache d’artefacts |
| **Stockage des secrets dans `.env` + chiffrement** | Conformité aux exigences de confidentialité |
| **CI/CD GitLab** | Alignement avec la chaîne d’intégration déjà en place dans l’entreprise |

### Outils de la forge logicielle  

| Outil | Usage |
|------|-------|
| **GitLab** | Gestion du code source, pipelines CI/CD |
| **Docker** | Build et packaging des conteneurs |
| **Docker‑Compose** | Environnements locaux (dev) |
| **Composer** | Gestion des dépendances PHP |
| **Nginx** | Load‑balancing, TLS |
| **PostgreSQL** | Base de données métier |
| **Prometheus / Grafana** | Monitoring (décrit en section *Transverses*) |
| **Portainer** | Gestion des conteneurs en prod |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 6. Niveau 3 – Vue Composants (Components) *(exemple sur le conteneur WebApp)*  

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Component.puml

Container(web, "WebApp", "PHP 7.3‑Apache", "Application principale") {
    Component(ctrl, "FrontController", "PHP", "Routage HTTP → services")
    Component(svc, "ConfigService", "PHP", "Gestion des variables d’environnement")
    Component(repo, "ConfigRepository", "PHP", "Accès aux données PostgreSQL")
    Component(auth, "CASAdapter", "PHP", "Intégration SSO")
    Component(job, "InitJobRunner", "Shell/PHP", "Exécution des scripts d’initialisation")

Rel(ctrl, svc, "Appelle")
Rel(svc, repo, "CRUD")
Rel(ctrl, auth, "Vérifie le ticket")
Rel(ctrl, job, "Déclenche")
Rel(repo, db, "SQL")
```

### Rôles des composants  

| Composant | Responsabilité |
|-----------|----------------|
| **FrontController** | Point d’entrée unique, décodage des routes REST |
| **ConfigService** | Logique métier : validation, transformation des paramètres |
| **ConfigRepository** | Accès bas‑niveau à PostgreSQL (requêtes préparées) |
| **CASAdapter** | Gestion du flux d’authentification SSO (validation du ticket) |
| **InitJobRunner** | Exécution de scripts d’init (`restore.sh`) dans le conteneur DB |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 7. Niveau 4 – Vue Code (Code)  

> Le niveau **Code** (diagrammes de classes UML, ERD) n’est pas détaillé dans ce DAT.  
> Il pourra être ajouté en annexe (ADR #12) si besoin de clarifier les modèles de domaine (ex. : `EnvironmentVariable`, `UserSession`).

↩︎ [Retour au sommaire](#table-of-contents)

---

## 8. Vue Exécution (Scénarios)  

### 8.1 Scénario 1 – Authentification d’un administrateur  

```mermaid
sequencediagram;
    participant Admin as Administrateur;
    participant UI as Navigateur (UI)
    participant Nginx as Nginx LB;
    participant Web as WebApp;
    participant CAS as CAS Server;
    Admin->>UI: Ouvre URL https://agile-env.company;
    UI->>Nginx: GET /
    Nginx->>Web: Forward HTTP;
    Web->>CAS: Redirect /login?service=...
    CAS->>Admin: Formulaire login;
    Admin->>CAS: Identifiants;
    CAS-->>Web: Ticket SSO;
    Web->>Web: CASAdapter valide le ticket;
    Web-->>UI: Page d’accueil (session créée)
```

### 8.2 Scénario 2 – Ajout d’une variable d’environnement  

```mermaid
sequencediagram;
    participant Admin as Administrateur;
    participant UI as UI;
    participant Nginx as Nginx LB;
    participant Web as WebApp;
    participant Repo as ConfigRepository;
    participant DB as PostgreSQL;
    Admin->>UI: Soumet le formulaire « Nouvelle variable »
    UI->>Nginx: POST /api/v1/env;
    Nginx->>Web: Forward request (auth ok)
    Web->>Repo: saveVariable(name, value)
    Repo->>DB: INSERT INTO env (name, value) VALUES (...)
    DB-->>Repo: OK;
    Repo-->>Web: Variable enregistrée;
    Web-->>UI: 201 Created
```

### 8.3 Scénario 3 – Déploiement via CI/CD (GitLab)  

```mermaid
sequencediagram;
    participant CI as GitLab CI;
    participant Docker as Docker Daemon;
    participant Registry as GitLab Registry;
    participant Deploy as Nginx LB / Docker‑Swarm;
    CI->>Docker: docker build -t registry/company/agile-env:$(CI_COMMIT_SHA) .
    Docker->>Registry: push image;
    CI->>Deploy: docker service update --image registry/...:$(CI_COMMIT_SHA) agile-env_web;
    Deploy-->>CI: Service mis à jour, health‑check OK
```

↩︎ [Retour au sommaire](#table-of-contents)

---

## 9. Vue Déploiement *(section standardisée)*  

### Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | À compléter | À compléter | À compléter | Docker‑Compose local, logs en console |
| Recette       | À compléter | À compléter | À compléter | Base de données pré‑remplie, tests d’intégration |
| Production    | À compléter | À compléter | À compléter | Nginx HA, sauvegardes chiffrées, monitoring complet |

### Infrastructure  

Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant `pnm3` du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
    Deployment_Node(nginxCluster, "Nginx Cluster", "Load Balancer") {
    Container(app, "agile‑env WebApp", "Docker", "PHP‑Apache")

    Deployment_Node(dbNode, "Base de données", "PostgreSQL") {
    ContainerDb(database, "agile‑env DB", "PostgreSQL", "Persist la configuration")

Rel(nginxCluster, app, "HTTP/HTTPS")
Rel(app, database, "JDBC/SQL")
```

### Supervision  

Le produit est supervisé via le système standard du GTI :  

* **Portainer** – gestion des conteneurs (stats, logs).  
* **Stack Prometheus / Grafana / Loki / AlertManager** – métriques, dashboards, alertes.  
* **Supervision PSIN** – monitoring de la disponibilité et du temps de réponse.

### Sauvegardes  

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI :  

* Dumps chiffrés AES‑256.  
* Stockage sur :  
  * **Objet B3** du IaaS ministériel,  
  * **Objet Outscale SecNumCloud** (Nuage Public),  
  * **Objet Google Cloud** (Nuage Public).

↩︎ [Retour au sommaire](#table-of-contents)

---

## 10. Sujets transverses  

| Thème | Traitement dans l’architecture |
|-------|---------------------------------|
| **Authentification** | CAS SSO, jetons de session, cookies HttpOnly + Secure |
| **Journalisation** | Logs Apache → stdout → Loki, logs applicatifs → Elasticsearch |
| **Monitoring** | Métriques Prometheus (CPU, RAM, latence HTTP), alertes sur seuils |
| **Gestion des erreurs** | Middleware PHP → réponses JSON normalisées, code 5xx loggués |
| **API** | RESTful, versionnée (`/api/v1/...`), OpenAPI 3.0 (doc générée) |
| **Sécurité des données** | Chiffrement des backups, variables sensibles masquées dans les logs |
| **CI/CD** | GitLab pipelines (build, test, push, déploiement) |
| **Observabilité** | Traces distribuées via OpenTelemetry (future) |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 11. Exigences de qualité  

| Exigence | Critère de validation |
|----------|-----------------------|
| **Performance** | Test de charge (JMeter) : 200 req/s, latence < 200 ms, 95 % des réponses |
| **Sécurité** | Scan OWASP ZAP : aucune vulnérabilité critique, SSO fonctionnelle |
| **Disponibilité** | Tests de basculement Nginx → aucun downtime > 30 s |
| **Intégrité des données** | Vérification checksum des dumps avant/ après restauration |
| **Traçabilité** | Logs d’audit conservés 180 jours, recherche via Kibana validée |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 12. Risques et dettes techniques  

| Risque / Dette | Impact | Mitigation |
|----------------|--------|------------|
| **PHP 7.3 en fin de vie** | Fin de support, vulnérabilités non corrigées | Planifier migration vers PHP 8.2 (ADR #07) |
| **Configuration manuelle du `.env`** | Erreurs humaines, fuite de secrets | Introduire un vault (HashiCorp Vault) et automatiser le chargement |
| **Absence de tests d’intégration** | Régressions non détectées | Ajouter suite de tests d’API (Postman/Newman) dans le pipeline CI |
| **Déploiement monolithique du WebApp** | Limité en scalabilité | Étudier découpage en micro‑services (ex. `AuthService`, `ConfigService`) |
| **Dépendance unique au CAS interne** | Risque de blocage si le service SSO tombe | Implémenter fallback OAuth2 (ex. Keycloak) |

↩︎ [Retour au sommaire](#table-of-contents)

---

## 13. Annexes  

### 13.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **CAS** | Central Authentication Service, protocole SSO utilisé par l’État français |
| **CI/CD** | Intégration continue / Déploiement continu |
| **GTI** | Groupe Technique Informatique (responsable de l’infrastructure) |
| **Nginx LB** | Load‑balancer Nginx en mode HA |
| **Docker‑Compose** | Outil d’orchestration de conteneurs pour les environnements de dev |
| **D‑I‑C‑T** | Acronyme sécurité : Disponibilité, Intégrité, Confidentialité, Traçabilité |

### 13.2 Décisions d’Architecture (ADR)  

| ADR | Sujet | Statut |
|-----|-------|--------|
| ADR‑01 | Choix du conteneur PHP‑Apache + Composer | Accepté |
| ADR‑02 | Utilisation de PostgreSQL comme persistance | Accepté |
| ADR‑03 | Authentification via CAS SSO | Accepté |
| ADR‑04 | Reverse‑proxy Nginx en front‑end | Accepté |
| ADR‑05 | Gestion des secrets via `.env` + chiffrement backups | Accepté |
| ADR‑06 | CI/CD GitLab pipeline standard | Accepté |
| ADR‑07 | Migration prévue vers PHP 8.2 (2025) | En cours de planification |

---

*Document généré automatiquement selon le modèle C4 – prêt à être utilisé dans VS Code ou Obsidian (extension Mermaid activée).*