# 📘 Dossier d'Architecture Technique (DAT) – **agile‑back**  
*Projet : back‑office de l’application Agile*  

[TOC]

---

## 1️⃣ Introduction & objectifs  

**Vue fonctionnelle**  
`agile‑back` est le module back‑office de la solution Agile. Il permet la création, la modification et le suivi des **études** (définition de projets, budgets, dotations, valorisation, etc.) et expose ces données via une API REST (API Platform). L’interface est rendue en Twig et le système s’appuie sur un serveur **CAS** pour l’authentification unique (SSO).  

**Objectifs de qualité orientés utilisateur**  

| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Réactivité** – temps de réponse ≤ 200 ms pour les pages de gestion d’étude | Garantir une expérience fluide aux agents métier |
| 2 | **Sécurité** – authentification CAS + contrôles d’accès RBAC, journalisation complète | Protéger les données sensibles (budgets, décisions) |
| 3 | **Disponibilité** – 99,5 % de disponibilité mensuelle, redondance du service web | Assurer la continuité des opérations de suivi |
| 4 | **Maintenabilité** – couverture de tests unitaires ≥ 80 % & conventions de code PSR‑12 | Réduire les coûts de maintenance et faciliter les évolutions |
| 5 | **Scalabilité** – capacité à ajouter facilement des conteneurs Docker | Répondre à la hausse du nombre d’utilisateurs et de requêtes API |

↩︎ [Retour au sommaire](#toc)

---

## 2️⃣ Niveau 1 – Vue Contexte (C4 L1)

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Context.puml

Person(user, "Agent métier", "Utilise l’interface back‑office pour gérer les études")
Person(admin, "Administrateur", "Configure le système, crée les comptes")
System_Boundary(agile_back, "agile‑back") {
    System(app, "agile‑back (Symfony)", "Back‑office + API")

System_Ext(cas, "CAS serveur", "Gestion d’authentification SSO")
System_Ext(pg, "PostgreSQL", "Base de données métier")
System_Ext(mail, "Serveur de mail", "Envoi de notifications")
System_Ext(front, "agile‑front", "Front‑office (UI)")

Rel(user, app, "Utilise")
Rel(admin, app, "Administre")
Rel(app, cas, "Authentifie via")
Rel(app, pg, "Persiste les données")
Rel(app, mail, "Envoie mails")
Rel(front, app, "Consomme l’API")
```

### Acteurs principaux  

| Acteur | Objectif | Besoin |
|--------|----------|--------|
| **Agent métier** | Créer / modifier / suivre les études | Interface ergonomique, réponses rapides |
| **Administrateur** | Gérer les droits, la configuration, les sauvegardes | Accès complet, visibilité sur logs |
| **Front‑office (agile‑front)** | Consommer les données d’étude via l’API | API stable, sécurisée et documentée |

### Systèmes externes  

| Système | Rôle |
|---------|------|
| **CAS serveur** | Authentification unique (SSO) |
| **PostgreSQL** | Persistance des entités métier (Etudes, Dotations, etc.) |
| **Serveur de mail** | Envoi de notifications (alertes, validation) |
| **agile‑front** | Consommation de l’API (REST/JSON) pour affichage côté client |

↩︎ [Retour au sommaire](#toc)

---

## 3️⃣ Parties prenantes  

| Rôle | Attente principale |
|------|---------------------|
| **MOA (Maître d’Ouvrage)** | Fonctionnalités métier complètes, respect des processus Agiles |
| **Développeurs** | Code lisible, tests automatisés, CI/CD fiable |
| **Opérateurs / Exploitants** | Déploiement sans interruption, monitoring, sauvegardes |
| **RSSI** | Conformité aux exigences de sécurité (D‑I‑C‑T) |
| **Utilisateurs finaux (agents)** | Interface réactive, ergonomie, disponibilité |

↩︎ [Retour au sommaire](#toc)

---

## 4️⃣ Contraintes  

### Techniques  
* **Langage / Framework** – PHP 8.x, Symfony 5.4 (LTS) + API Platform.  
* **Base de données** – PostgreSQL 13, accès via Doctrine ORM.  
* **Authentification** – CAS (phpCAS) intégré, sessions HTTPOnly, SameSite.  
* **Infrastructure** – Conteneurs Docker orchestrés par Docker‑Compose (déploiement local) → Kubernetes (en prod).  
* **CI/CD** – GitLab CI, tests PHPUnit, linting PHP‑CS‑Fixer.  

### Organisationnelles  
* Doit être **aligné** avec le front‑office *agile‑front* (même domaine métier).  
* Respect du **processus de gouvernance** du GTI (supervision, sauvegarde).  

### Réglementaires & Sécurité (modèle D‑I‑C‑T)  

| Dimension | Exigence | Implémentation |
|-----------|----------|----------------|
| **Disponibilité** | 99,5 % / mois | Redondance Nginx + Docker Swarm, health‑checks |
| **Intégrité** | Protection contre altération des données | Transactions Doctrine, contraintes DB, contrôles d’accès RBAC |
| **Confidentialité** | Accès limité aux données sensibles | Authentification CAS, chiffrement TLS, masquage des champs dans les logs |
| **Traçabilité** | Historisation des actions | Monolog (fichiers + syslog), audit table `audit_log` (custom) |

↩︎ [Retour au sommaire](#toc)

---

## 5️⃣ Niveau 2 – Vue Conteneurs (C4 L2)

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Container.puml

System_Boundary(agile_back, "agile‑back") {
    Container(web, "Web App (Symfony)", "PHP‑FPM", "Gestion du back‑office et API REST")
    Container(db, "PostgreSQL", "PostgreSQL", "Base de données métier")
    Container(cas_client, "CAS Client (phpCAS)", "PHP library", "Gestion SSO")
    Container(mail, "Mailer", "SwiftMailer / Symfony Mailer", "Envoi de notifications")

Person(user, "Agent métier")
Person(admin, "Administrateur")
System_Ext(cas, "CAS serveur")
System_Ext(front, "agile‑front (UI)")

Rel(user, web, "Navigue / saisit")
Rel(admin, web, "Administre")
Rel(web, cas_client, "Utilise")
Rel(cas_client, cas, "Authentifie via SSO")
Rel(web, db, "Lect./Écrit")
Rel(web, mail, "Envoie mails")
Rel(front, web, "Consomme API")
```

### Description des conteneurs  

| Conteneur | Responsabilité | Technologie | Interactions clés |
|----------|----------------|-------------|-------------------|
| **Web App (Symfony)** | Contrôleurs, services métier, rendu Twig, API Platform | PHP 8, Symfony 5.4, Twig, API Platform | ↔ CAS Client, ↔ PostgreSQL, ↔ Mailer, ↔ Front‑office |
| **PostgreSQL** | Persistance des entités (`Etudes`, `Dotations`, `Financements`, etc.) | PostgreSQL 13, Docker image `postgres:13` | ↔ Web App (via Doctrine) |
| **CAS Client** | Authentifie les utilisateurs via le serveur CAS | phpCAS lib, intégré au Web App | ↔ CAS serveur |
| **Mailer** | Envoi de notifications (alertes, validation) | Symfony Mailer / SwiftMailer, DSN configuré | ↔ Web App |

### Décisions architecturales majeures  

* **Monolithe Symfony** – Tous les modules (controllers, services, repository) sont empaquetés dans le même conteneur Docker, simplifiant le déploiement initial.  
* **API Platform** – Expose les entités `Etudes`, `Financements` via un endpoint `/api`.  
* **Dockerisation** – Chaque conteneur possède son `Dockerfile`; la stack est orchestrée via `docker‑compose.yml` en dev et via Helm/K8s en prod.  

### Environnement technologique  

| Élément | Version / Stack |
|---------|-----------------|
| PHP | 8.1 |
| Symfony | 5.4 (LTS) |
| Doctrine ORM | 2.10 |
| PostgreSQL | 13 |
| Nginx (reverse‑proxy) | 1.21 |
| Docker | 20.10 |
| CI/CD | GitLab CI (pipeline, tests, lint) |

### Outils de la forge logicielle  

* **CI** – GitLab CI (`.gitlab-ci.yml`) : lint, tests, build image, déploiement.  
* **Gestion de versions** – GitLab repository, tags semver.  
* **Tests** – PHPUnit 9, tests fonctionnels (WebTestCase).  
* **Qualité** – PHP‑CS‑Fixer, PHPStan (niveau max).  

↩︎ [Retour au sommaire](#toc)

---

## 6️⃣ Niveau 3 – Vue Composants (C4 L3)  

**Conteneur ciblé** : *Web App (Symfony)*  

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Component.puml

Container(web, "Web App (Symfony)", "PHP‑FPM") {
    Component(controller, "Controllers", "Symfony", "Gestion des requêtes HTTP (UI + API)")
    Component(service, "Services", "PHP", "Logique métier (études, dotations, valorisation)")
    Component(repo, "Repositories", "Doctrine", "Accès aux entités persistées")
    Component(form, "Form Types", "Symfony Forms", "Construction & validation des formulaires")
    Component(security, "Security", "Symfony Security", "Voter, firewall, rôle‑based access")
    Component(event, "Event Listeners", "Symfony EventDispatcher", "Gestion d’évènements (ex: notifications)")

Person(user, "Agent métier")
Person(admin, "Administrateur")
System_Ext(cas, "CAS serveur")

Rel(user, controller, "Saisit / consulte")
Rel(admin, controller, "Administre")
Rel(controller, service, "Oriente les appels")
Rel(service, repo, "Persiste / lit")
Rel(service, mail, "Envoie notifications")
Rel(controller, security, "Vérifie les droits")
Rel(security, cas, "Authentifie via SSO")
```

### Logique interne & responsabilités  

| Composant | Responsabilité principale |
|-----------|----------------------------|
| **Controllers** | Point d’entrée HTTP, routage, sérialisation API, rendu Twig. |
| **Services** | Coordination des règles métier (calculs de dotation, export CSV/ODS, valorisation). |
| **Repositories** | Accès aux entités via Doctrine, requêtes personnalisées. |
| **Form Types** | Construction dynamique des formulaires (abonnements, études, etc.). |
| **Security** | Voter (`EtudesVoter`) pour contrôle d’accès granulaire, firewall CAS. |
| **Event Listeners** | Envoi d’emails après création/modification (`EtudesListener`). |

↩︎ [Retour au sommaire](#toc)

---

## 7️⃣ Niveau 4 – Vue Code (C4 L4)  

> **Remarque** : Les diagrammes de classes UML et le schéma ERD (Entity‑Relationship) existent dans le répertoire `src/Entity` et les fichiers `*.php`. Ils ne sont pas détaillés ici mais peuvent être générés à la demande (ex. : `phpstan analyse`, `doctrine:mapping:info`).  

↩︎ [Retour au sommaire](#toc)

---

## 8️⃣ Vue Exécution – Scénarios critiques  

### 8.1 Authentification SSO via CAS  

```mermaid
sequencediagram;
    participant User as Agent métier;
    participant Browser as Navigateur;
    participant App as agile‑back (Web)
    participant CAS as CAS serveur;
    User->>Browser: Accède à /login;
    Browser->>App: GET /login;
    App->>CAS: Redirige vers /cas/login?service=...
    Browser->>CAS: Authentifie (login+pwd)
    CAS-->>Browser: Ticket CAS;
    Browser->>App: GET /login?ticket=XYZ;
    App->>CAS: validate(ticket)
    CAS-->>App: Validation OK + attributs;
    App->>Browser: Session créée, redirection vers tableau de bord
```

### 8.2 Création d’une **Étude** (flux métier)  

```mermaid
sequencediagram;
    participant User as Agent métier;
    participant UI as UI (Twig)
    participant Ctrl as EtudesController;
    participant Svc as EtudesService;
    participant Repo as EtudesRepository;
    participant DB as PostgreSQL;
    participant Mail as Mailer;
    User->>UI: Ouvre formulaire "Nouvelle étude"
    UI->>Ctrl: POST /etudes (payload)
    Ctrl->>Svc: createEtude(payload)
    Svc->>Repo: persist(etude)
    Repo->>DB: INSERT;
    DB-->>Repo: OK;
    Repo-->>Svc: Entity;
    Svc->>Mail: sendCreationNotification(etude)
    Mail-->>User: Email de confirmation;
    Svc-->>Ctrl: Retour succès;
    Ctrl->>UI: Redirige vers page étude
```

### 8.3 Export global des **Valorisations** (CSV)  

```mermaid
sequencediagram;
    participant Admin as Administrateur;
    participant UI as UI;
    participant Ctrl as ValorisationController;
    participant Svc as ValorisationService;
    participant Export as ExportUtil;
    participant File as Système de fichiers;
    Admin->>UI: Clique "Export CSV"
    UI->>Ctrl: GET /valorisations/export;
    Ctrl->>Svc: exportAll()
    Svc->>Export: generateCsv(data)
    Export-->>File: crée /tmp/valorisations.csv;
    Export-->>Svc: chemin fichier;
    Svc->>Ctrl: Retourne fichier;
    Ctrl->>UI: Téléchargement du CSV
```

↩︎ [Retour au sommaire](#toc)

---

## 9️⃣ Vue Déploiement *(section standardisée)*  

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
    Deployment_Node(nginx, "Nginx Cluster", "Load‑Balancer") {
    Container(app, "agile‑back (Docker)", "PHP‑FPM")

    Deployment_Node(db, "Base de données", "PostgreSQL") {
    ContainerDb(database, "PostgreSQL", "PostgreSQL")

    Deployment_Node(cas, "CAS serveur", "phpCAS") {
    Container(cas_srv, "CAS", "Java / PHP")

    Deployment_Node(mail, "Serveur mail", "SMTP") {
    Container(smtp, "Mail Relay", "Postfix")

Rel(nginx, app, "HTTP/HTTPS")
Rel(app, database, "JDBC/SQL")
Rel(app, cas_srv, "CAS ticket validation (HTTPS)")
Rel(app, smtp, "SMTP")
```

### Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | Docker‑Desktop | 1 x Nginx, 1 x PHP‑FPM, 1 x PostgreSQL | Bridge Docker | Hot‑reload, logs en console |
| Recette | VM interne (OpenStack) | 2 x Nginx (LB), 1 x PHP‑FPM, 1 x PostgreSQL | VLAN isolé | Jeux de données anonymisées |
| Production | Cloud ECO4 (OpenStack) | 2 x Nginx (HA), 3 x PHP‑FPM, 2 x PostgreSQL (replication) | VLAN sécurisé, TLS mutual | Monitoring Prometheus, sauvegardes journalières chiffrées |

### Infrastructure (texte)  

Le produit est hébergé sur le cloud interne **ECO4** (OpenStack tenant `pnm3`).  
Le reverse‑proxy Nginx du schéma ci‑dessus est en fait une paire de Nginx load‑balanced en frontal des produits hébergés sur le tenant.

### Supervision  

Le produit est supervisé via le système standard du GTI :  

* **Portainer** pour la partie purement conteneurisée,  
* **Stack Prometheus / Grafana / Loki / AlertManager**,  
* Supervision **PSIN** (Processus de Sécurité et d’Intégrité).

### Sauvegardes  

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES‑256 et déposés sur :  

* le stockage objet **B3** du IaaS ministériel,  
* le stockage objet **Outscale SecNumCloud** (via la prestation du GTI “Nuage Public”),  
* le stockage objet standard de **Google Cloud** (via la même prestation “Nuage Public”).

↩︎ [Retour au sommaire](#toc)

---

## 🔟 Sujets transverses  

| Thématique | Implémentation |
|------------|----------------|
| **Authentification** | CAS + Symfony Security firewall, `remember_me` désactivé, session HTTPOnly, SameSite=Lax. |
| **Journalisation** | Monolog → `php://stderr` (prod), fichiers rotatifs (dev). Niveau configurable (`debug` / `error`). |
| **Monitoring** | Prometheus exporter (`symfony/prometheus-metrics`), alertes sur latence > 200 ms, taux d’erreur 5 %. |
| **Gestion des erreurs** | `ExceptionListener` centralisé, réponses JSON normalisées pour l’API, pages d’erreur Twig personnalisées. |
| **API** | API Platform, OpenAPI 3 spec auto‑générée, authentification via JWT (optionnel) en plus du CAS. |
| **CI/CD** | GitLab CI → lint, tests, build image, déploiement Helm (prod). |
| **Sécurité des données** | TLS 1.3 partout, chiffrement des backups, masquage des champs sensibles dans les logs. |

↩︎ [Retour au sommaire](#toc)

---

## 1️⃣1️⃣ Exigences de qualité  

| Exigence | Critère de validation |
|----------|----------------------|
| **Performance** | Temps moyen de réponse < 200 ms sur 95 % des requêtes (tests Gatling). |
| **Sécurité** | Aucun test d’injection SQL/XXS détecté (OWASP ZAP). |
| **Disponibilité** | Uptime ≥ 99,5 % mesuré sur Prometheus (`up` metric). |
| **Maintenabilité** | Couverture de tests unitaires ≥ 80 % (PHPUnit + coverage). |
| **Scalabilité** | Le service supporte le scaling horizontal (Docker Swarm/K8s) sans perte de session (sticky‑session via Nginx). |

↩︎ [Retour au sommaire](#toc)

---

## 1️⃣2️⃣ Risques & dettes techniques  

| Risque / Dette | Impact | Atténuation |
|----------------|--------|-------------|
| **Dépendance au CAS** | Si le serveur CAS devient indisponible, aucune authentification possible. | Mise en place d’un **fallback** (mode maintenance) & monitoring du service CAS. |
| **Architecture monolithique** | Difficulté à isoler des parties pour le scaling ou le refactoring. | Road‑map vers une architecture **micro‑services** (ex. extraction du module export). |
| **Absence de tests fonctionnels complets** | Risque de régression lors de changements. | Augmenter la couverture fonctionnelle (Behat, Symfony Panther). |
| **Gestion des migrations DB** | Risque de perte de données en production. | Utiliser `doctrine:migrations` avec validation en pré‑prod, sauvegarde avant chaque migration. |
| **Configuration de l’environnement** (variables d’environnement, secrets) | Fuite de credentials ou mauvaise configuration. | Centraliser les secrets dans **Vault** et appliquer le principe du moindre privilège. |

↩︎ [Retour au sommaire](#toc)

---

## 1️⃣3️⃣ Annexes  

### 📚 Glossaire  

| Terme | Définition |
|-------|------------|
| **CAS** | Central Authentication Service – protocole SSO. |
| **DTO** | Data Transfer Object – structure légère pour les API. |
| **API Platform** | Framework Symfony pour exposer des API REST/GraphQL. |
| **GTI** | Groupe Technique Informatique – responsable de l’infrastructure et de la supervision. |
| **PSIN** | Processus de Sécurité et d’Intégrité – supervision de la sécurité. |
| **C4** | Modèle de visualisation d’architecture (Context, Container, Component, Code). |

### 📄 Décisions d’Architecture (ADR) – Exemple  

| ADR # | Décision | Contexte | Conséquence |
|------|----------|----------|-------------|
| 1 | Utiliser **phpCAS** pour l’authentification | SSO déjà déployé dans l’infrastructure | Centralisation des identités, dépendance au serveur CAS |
| 2 | Exposer les entités métier via **API Platform** | Besoin d’un accès front‑office et d’échanges externes | API auto‑documentée, surcharge de configuration possible |
| 3 | Dockeriser chaque composant | Uniformité des environnements dev/prod | Simplifie le déploiement, nécessite une orchestration (Docker‑Compose / K8s) |

↩︎ [Retour au sommaire](#toc)

---  

**Fin du Dossier d’Architecture Technique**.  