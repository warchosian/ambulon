# 📁 Dossier d’Architecture Technique (DAT) – **SIREINES**  
*Version du DAT : 2024‑03‑15*  

---  

[TOC]

---  

## 1️⃣ Introduction & Vision architecturale  

| Élément | Description |
|---|---|
| **Nom du système** | **SIREINES** – Répertoire national des experts et spécialistes scientifiques et techniques. |
| **Objectif métier** | Collecter, consolider et valoriser les dossiers de qualification d’agents, assurer le suivi des avis des comités de domaine et fournir les rapports BIRT associés. |
| **Environnement** | Application Java /J2EE (Spring + Struts 2 + Vertigo + BIRT) packagée en **WAR** et déployée dans un conteneur **Docker/Tomcat**. |
| **Exigences qualité** | - Disponibilité ≥ 99 % (production) <br> - Temps de réponse ≤ 2 s (pages d’accueil) <br> - Sécurité RGPD (DACP = oui) <br> - Maintenabilité : déploiement automatisé via Docker‑Compose, tests unitaires & d’intégration. |
| **Portée géographique** | Nationale (Ministère de la Transition Écologique). |
| **Statut** | En production (version 2.5.20 – 12 / 03 / 2026). |

### Vision technique  

SIREINES est conçue comme **une application monolithique** (WAR) exécutée dans un **conteneur Docker** avec une base de données PostgreSQL séparée et un moteur de recherche **ElasticSearch** embarqué. Le code est versionné dans GitLab et les livraisons sont automatisées via Docker‑Compose.  

---  

## 2️⃣ Niveau 1 – Vue **Contexte** (C4‑L1)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0066CC', 'edgeLabelBackground':'#f8f8f8' }}%%%%%%%%%%%%%%%%%%%%}%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Model/master/C4_Context.puml

Person(user, "Agent / Utilisateur métier", "Dépose, consulte et suit ses dossiers de qualification.")
Person(admin, "Administrateur MOA", "Déploie, configure, assure la supervision et la maintenance.")
System_Ext(cerbere, "Cerbère", "Gestion des comptes et des habilitations (authentification).")
System_Ext(email, "Serveur mail", "Envoi de notifications (courriels).")
System_Ext(birt, "BIRT Server", "Génération des rapports PDF/Excel.")
System_Ext(es, "ElasticSearch", "Indexation et recherche plein‑texte des dossiers.")
System(sireines, "SIREINES", "Application métier de suivi de qualification d’agents.")
Rel(user, sireines, "Utilise via navigateur Web")
Rel(admin, sireines, "Déploie, configure, surveille")
Rel(sireines, cerbere, "Authentification (SSO)")
Rel(sireines, email, "Envoi de notifications")
Rel(sireines, birt, "Appel de rapports BIRT")
Rel(sireines, es, "Recherche plein‑texte")
Rel(sireines, "PostgreSQL", "Persistance des données")
```

*Le système SIREINES interagit avec les acteurs humains (agents, admin) et les systèmes externes : Cerbère (auth), serveur mail, BIRT, ElasticSearch et PostgreSQL.*

---  

## 3️⃣ Niveau 2 – Vue **Conteneurs** (C4‑L2)

```mermaid
%%{init: {'theme': 'base'}}%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Model/master/C4_Container.puml

System_Boundary(sireines, "SIREINES") {
    Container(app, "SIREINES‑Web", "Java /J2EE (Spring + Struts2)", "WAR exécuté dans Tomcat")
    ContainerDb(db, "PostgreSQL", "PostgreSQL 14", "Base de données relationnelle")
    Container(search, "ElasticSearch (Embedded)", "Java + Elasticsearch", "Indexation plein‑texte")
    Container(admin, "PgAdmin", "Web UI", "Gestion de la BDD")
}
Rel(app, db, "JDBC (DataSource)", "SQL")
Rel(app, search, "API Vertigo Search", "REST/Java")
Rel(app, admin, "Admin UI", "HTTP")
Rel(app, "BIRT", "Appel via HTTP", "REST")
Rel(app, "Mail Server", "SMTP", "Mail")
Rel(app, "Cerbère", "SSO (SAML)", "HTTP")
```

*Conteneurs principaux :*  

| Conteneur | Image Docker | Rôle |
|---|---|---|
| **sireines‑app** | `tomcat:7.0.108-jdk8` + WAR | Exécution du code métier (controllers, services, BIRT manager). |
| **sireines‑db** | `postgres:14.1‑alpine` | Persistance des tables `dossier`, `mot_cle`, … |
| **sireines‑search** | `elasticsearch:7.x` (embeddé) | Indexation / recherche full‑text. |
| **sireines‑pgadmin** | `dpage/pgadmin4` | Administration de la BDD (optionnel). |

---  

## 4️⃣ Niveau 3 – Vue **Composants** (C4‑L3)

```mermaid
%%{init: {'theme': 'base'}}%%%%%%%%%%%%%%%%%%%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Model/master/C4_Component.puml

Container(app, "SIREINES‑Web", "Java /J2EE", "Tomcat") {
    Component(ctrl, "Struts2 Controllers", "Java", "Gestion des actions (ex. AccueilAction, DossierDetailAction).")
    Component(svc, "Business Services", "Java", "AgentsServices, DossiersServices, ExtractionsServices, …")
    Component(repo, "Vertigo Dynamo Repositories", "Java", "Accès aux DT/DAOs (ex. dossiersDao, agentsDao).")
    Component(birt, "BIRT Manager", "Java", "Publication de rapports (PDF/Excel).")
    Component(searchMgr, "SearchManager", "Java", "Re‑indexation & requêtes ElasticSearch.")
    Component(auth, "Auth Config", "XML", "sireines‑auth‑config.xml (Cerbère SSO).")
    Component(cache, "Ehcache", "XML", "Cache de listes de référence.")
}
Rel(ctrl, svc, "Appelle")
Rel(svc, repo, "Utilise")
Rel(svc, searchMgr, "Déclenche (re‑index)")
Rel(svc, birt, "Génère rapports")
Rel(ctrl, auth, "Vérifie habilitations")
Rel(ctrl, cache, "Lecture/écriture")
```

### Principaux packages  

| Package | Description |
|---|---|
| `i2.application.sireines.controller.*` | Struts2 Actions (UI). |
| `i2.application.sireines.service.*` | Services métiers (Agents, Dossiers, Extractions, …). |
| `i2.application.sireines.boot.*` | Initialisation (SearchManagerInitializer, PersistenceManagerInitializer). |
| `i2.application.sireines.boot.manager` | Interface **BirtManager** et implémentation. |
| `i2.application.sireines.util` | Helpers (CsvExport, FormatterAnnee, CerbereUtil). |
| `i2.application.sireines.service.common` | Envoi de mails, utilitaires communs. |
| `i2.application.sireines.service.referentiels` | Gestion des référentiels (mot‑cle, qualification, …). |
| `i2.application.sireines.service.extractions` | Extraction de rapports (SQL + BIRT). |
| `i2.application.sireines.service.seances` | Gestion des séances de comité. |
| `io.vertigo.dynamo.*` | Framework Vertigo (DT, DAO, Search). |

---  

## 5️⃣ Niveau 4 – Vue **Code** (exemple de décision)  

### ADR‑001 – Choix de l’architecture globale  

| **Date** | 2022‑10‑01 |
|---|---|
| **Statut** | Accepté |
| **Décideurs** | PO, Architecte, Lead Dev |
| **Contexte** | Le projet doit être livrable rapidement, disposer d’un environnement de test reproductible et pouvoir être déployé sur des serveurs IaaS (ECO4). |
| **Options** | 1️⃣ Monolithe (WAR/Tomcat) <br> 2️⃣ Micro‑services (Spring Boot) |
| **Option retenue** | **Monolithe** – plus simple à packager, moins de surcharge réseau, compatible avec l’existant (Struts2, Vertigo). |
| **Conséquences** | - Déploiement via un seul conteneur Docker. <br> - Base de données et moteur de recherche séparés. <br> - Évolution future possible vers micro‑services (extraction de BIRT ou du moteur de recherche). |
| **À valider** | Aucun impact sur les SLA. |

### ADR‑002 – Stack technologique principal  

| **Date** | 2022‑09‑15 |
|---|---|
| **Statut** | Accepté |
| **Décideurs** | Architecte, Lead Dev |
| **Contexte** | L’application utilise déjà Struts2, Vertigo et BIRT. |
| **Options** | 1️⃣ Java 8 + Spring 4 + Struts2 (actuel) <br> 2️⃣ Java 11 + Spring Boot <br> 3️⃣ Migration vers Kotlin/Quarkus |
| **Option retenue** | **Java 8 + Spring 4 + Struts2** – stabilité, compatibilité avec le code legacy. |
| **Conséquences** | - Nécessité de maintenir le conteneur Tomcat 7. <br> - Aucun changement de version JDK dans le pipeline CI. |
| **À valider** | Compatibilité avec les futures versions de Tomcat (upgrade plan). |

### ADR‑003 – Persistance des données  

| **Date** | 2022‑08‑10 |
|---|---|
| **Statut** | Accepté |
| **Contexte** | Les scripts d’installation et d’évolution de la base sont fournis en SQL (PowerDesigner). |
| **Options** | 1️⃣ PostgreSQL 14 (actuel) <br> 2️⃣ Oracle 19c <br> 3️⃣ MySQL 8 |
| **Option retenue** | **PostgreSQL 14** – déjà intégrée aux scripts, open‑source, supporte les types JSON et les fonctions PL/pgSQL utilisées. |
| **Conséquences** | - Volume Docker persistant `sireines_db_sireines_vol`. <br> - Sauvegardes réalisées via `pg_dump`. |
| **À valider** | Plan de migration vers PostgreSQL 15 (future). |

### ADR‑004 – Authentification & autorisation  

| **Date** | 2022‑11‑05 |
|---|---|
| **Statut** | Accepté |
| **Contexte** | L’application doit s’intégrer au SSO ministériel (Cerbère). |
| **Options** | 1️⃣ Authentification locale (login/password) <br> 2️⃣ SSO via Cerbère (SAML) <br> 3️⃣ OAuth2 |
| **Option retenue** | **Cerbère SSO (SAML)** – déclarée dans `sireines-auth-config.xml`. |
| **Conséquences** | - Aucun mot de passe stocké dans la BDD. <br> - Gestion des rôles via le fichier d’autorisation (`authorisation-config_1_0.dtd`). |
| **À valider** | Mise à jour du certificat SAML avant expiration. |

### ADR‑005 – Stratégie de déploiement & conteneurisation  

| **Date** | 2023‑01‑12 |
|---|---|
| **Statut** | Accepté |
| **Contexte** | Besoin d’un déploiement reproductible, versionnable et rollback possible. |
| **Options** | 1️⃣ Docker‑Compose (single‑file) <br> 2️⃣ Kubernetes (Helm) <br> 3️⃣ VM manuelle |
| **Option retenue** | **Docker‑Compose** – suffisant pour les trois environnements (recette, pré‑prod, prod). |
| **Conséquences** | - Fichier `docker-compose.yml` versionné dans le repo. <br> - Volumes persistant pour DB & pgAdmin. <br> - Tag de l’image Docker contenant le WAR (`sireines-web-<version>.war`). |
| **À valider** | Passage à Kubernetes (ECO4) prévu pour 2025. |

### ADR‑006 – Intégration avec le moteur de recherche  

| **Date** | 2023‑03‑20 |
|---|---|
| **Statut** | Accepté |
| **Contexte** | Fonctionnalité de recherche plein‑texte sur les dossiers et mots‑clefs. |
| **Options** | 1️⃣ ElasticSearch embarqué (Vertigo) <br> 2️⃣ Solr <br> 3️⃣ PostgreSQL full‑text |
| **Option retenue** | **ElasticSearch embarqué** – déjà implémenté via `io.vertigo.dynamo.search`. |
| **Conséquences** | - Conteneur `sireines‑search` (embedded). <br> - Re‑indexation déclenchée à chaque démarrage (`SearchManagerInitializer`). |
| **À valider** | Monitoring de l’usage disque du nœud ES. |

### ADR‑007 – Cache & performance  

| **Date** | 2023‑04‑05 |
|---|---|
| **Statut** | Accepté |
| **Contexte** | Chargement fréquent de listes de référentiels (structures, comités). |
| **Options** | 1️⃣ Ehcache (XML) <br> 2️⃣ Caffeine <br> 3️⃣ Aucun cache |
| **Option retenue** | **Ehcache** – configuré dans `ehcache.xml`. |
| **Conséquences** | - Gains de latence ≈ 30 % sur les pages de recherche. <br> - Cache persistant en mémoire JVM. |
| **À valider** | Dimensionnement du heap (2 GB) pour éviter OOM. |

### ADR‑008 – Gestion des erreurs & résilience  

| **Date** | 2023‑06‑01 |
|---|---|
| **Statut** | Accepté |
| **Contexte** | L’application doit présenter des pages d’erreur claires et logger les incidents. |
| **Options** | 1️⃣ Struts2 `ErrorHandler` (déjà présent) <br> 2️⃣ Spring Boot ErrorController <br> 3️⃣ Aucun |
| **Option retenue** | **Struts2 `ErrorHandler`** – implémenté dans `i2.application.sireines.errorhandler.ErrorHandler`. |
| **Conséquences** | - Redirection vers `application-error.jsp`. <br> - Log4j 2 pour la journalisation. |
| **À valider** | Centralisation des logs via ELK (prévu 2025). |

---  

## 5️⃣ Qualités architecturales (ISO 25010)  

| Qualité | Niveau actuel | Commentaires / Actions |
|---|---|---|
| **Sécurité** | **Élevée** (SSO Cerbère, HTTPS, pas de mots de passe en clair, BDD protégée) | → Audits annuels, mise à jour du certificat SAML. |
| **Fiabilité** | **Bonne** (Docker‑Compose + rollback, sauvegardes DB quotidiennes) | → Tests de bascule (