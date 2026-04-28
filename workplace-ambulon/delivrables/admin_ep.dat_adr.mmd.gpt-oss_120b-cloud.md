# 📘 Dossier d’Architecture Technique (DAT) – **admin_ep**  

[TOC]

---  

## 1️⃣ Introduction & Vision architecturale  

**Projet** : admin_ep – Administration des établissements publics (MTES‑MCT)  

**Objectif principal** :  
- Gérer le référentiel partagé des membres des conseils d’administration des établissements publics placés sous la tutelle du ministère.  
- Assurer la saisie, la consultation, la recherche, la génération de statistiques et la notification des échéances de mandat.  

**Valeurs métier** : fiabilité des données, traçabilité des mandats, conformité aux exigences d’accessibilité et de sécurité (DI‑CT).  

**Qualités prioritaires (ISO/IEC‑25010)**  

| Qualité | Niveau cible | Raison |
|---|---|---|
| **Fiabilité** | ★★★★★ | Gestion d’informations juridiques sensibles. |
| **Sécurité** | ★★★★★ | Authentification Cerbère, données publiques. |
| **Performance** | ★★★★☆ | Recherche multi‑critères, tableau de bord. |
| **Maintenabilité** | ★★★★☆ | Architecture monolithique mais modulaire. |
| **Portabilité** | ★★★★☆ | Conteneurisation en cours (Docker). |
| **Scalabilité** | ★★★☆☆ | Prévision d’évolution vers micro‑services. |

**Documents associés**  

| Document | Lien |
|---|---|
| **Cahier des Charges Fonctionnel (CCF)** | – |
| **Cahier des Spécifications Techniques (CST)** | – |
| **Wiki projet** | `admin_ep.wiki.md` |
| **Fiche produit** | `admin_ep.wiki.si.md` |

---  

## 2️⃣ Niveau 1 – Vue **Contexte** (C4‑L1)  

```mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Context.puml

System_Boundary(admin_ep, "admin_ep") {
    Person(user, "Utilisateur métier", "Opérateur, DG de tutelle, SPES")
    System_Ext(jorf, "Service JORF", "Flux RSS / archives .tar.gz")
    System_Ext(cerbere, "Service d’authentification Cerbère")
    System_Ext(email, "Système de messagerie", "Envoi de notifications")
    System(web, "Application web admin_ep", "Gestion des données administratives")
    SystemDb(db, "PostgreSQL", "Base de données métier")
    Rel(user, web, "Utilise")
    Rel(web, db, "Lit / écrit")
    Rel(web, jorf, "Consomme (RSS / .tar.gz)", "HTTPS")
    Rel(web, cerbere, "Vérifie les droits", "OAuth2 / SAML")
    Rel(web, email, "Envoie les alertes", "SMTP")
}
```  

**Description**  
- **admin_ep** est le système central de gestion.  
- Il s’appuie sur le **service d’authentification Cerbère** pour la gestion des habilitations.  
- Les données sont enrichies automatiquement à partir du **service JORF** (flux RSS, archives).  
- Les notifications d’échéance sont transmises par le **système de messagerie** interne.  

**Objectifs métier adressés**  

| Acteur | Besoin | Réponse du système |
|---|---|---|
| Opérateur | Saisie manuelle des mandats | Interface web (CRUD) |
| DG de tutelle | Suivi des mandats, alertes | Tableau de bord, email d’alerte |
| SPES | Recherche globale | Moteur de recherche plein texte |
| Cerbère | Gestion des habilitations | Authentification RBAC |

---  

## 3️⃣ Niveau 2 – Vue **Conteneurs** (C4‑L2)  

```mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Container.puml

System_Boundary(admin_ep, "admin_ep") {
    Container(web_app, "Web Application", "Java 8, Spring MVC / Struts2", "Interface utilisateur, API REST")
    Container(batch_job, "Batch JORF Importer", "Java 8, Quartz Scheduler", "Extraction, parsing JORF")
    ContainerDb(db, "PostgreSQL", "9.6.11 (upgrade to 15 envisagée)", "Persist les référentiels")
    Container(email_srv, "Mail Server", "SMTP", "Envoi de notifications")
}
Rel(web_app, db, "JDBC", "SQL")
Rel(batch_job, db, "JDBC", "SQL")
Rel(web_app, batch_job, "Déclenche (cron)", "Quartz")
Rel(web_app, email_srv, "SMTP", "Alertes")
Rel(web_app, "Cerbère", "OAuth2 / SAML", "AuthN/AuthZ")
Rel(web_app, "JORF", "HTTPS (RSS)", "Import")
```

### 3.1 Descriptions des conteneurs  

| Conteneur | Responsabilité | Technologie |
|---|---|---|
| **Web Application** | UI, services REST, contrôleurs MVC, sécurité | Java 8, Tomcat 9.0.8, Struts 2, Vertigo, Maven |
| **Batch JORF Importer** | Extraction périodique du JORF, mise à jour des entités | Java 8, Quartz, HTTP client |
| **PostgreSQL** | Persistance relationnelle, contraintes d’intégrité | PostgreSQL 9.6.11 (cible 15) |
| **Mail Server** | Envoi d’emails d’alerte (mandats à échéance) | SMTP (ex. Postfix) |
| **Cerbère** | Authentification unique et gestion des profils | SAML 2.0 / OAuth2 (externe) |

### 3.2 Décisions architecturales majeures (ADRs)  

| ADR | Sujet |
|---|---|
| **ADR‑001** | Choix de l’architecture globale (Monolithe) |
| **ADR‑002** | Stack technologique principal (Java 8 + Tomcat 9 + PostgreSQL 9.6) |
| **ADR‑003** | Stratégie de persistance (PostgreSQL, schéma *integration*) |
| **ADR‑004** | Authentification & sécurité (Cerbère, RBAC) |
| **ADR‑005** | Stratégie de déploiement & conteneurisation (Docker) |
| **ADR‑006** | Intégration JORF (RSS + archives) |
| **ADR‑007** | Cache & performance (Cache 2‑niveau, Spring Cache) |
| **ADR‑008** | Gestion des erreurs & résilience (ErrorHandler, logging) |

---  

## 4️⃣ Architecture Decision Records (ADRs)  

> Les ADRs sont numérotées séquentiellement. Chaque ADR suit le format **Problème → Options → Décision → Conséquences**.  

---  

### ADR‑001 – Architecture globale  

- **Statut** : Accepté  
- **Date** : 2023‑02‑15  
- **Décideurs** : Architecte, Chef de produit, Équipe MOE  

#### Contexte  
Le projet doit être livré rapidement, avec une équipe déjà experte sur les technologies Java/Struts2. Le périmètre fonctionnel (CRUD, recherche, reporting) est cohérent avec une approche monolithique.  

#### Options considérées  

| Option | Avantages | Inconvénients |
|---|---|---|
| **Monolithe** (une seule application web) | Simplicité de développement, déploiement rapide, moindre overhead de communication | Risque de scalabilité limitée, gros temps de build |
| **Micro‑services** (services dédiés : UI, API, import, auth) | Scalabilité fine, indépendance des équipes | Complexité d’infrastructure, besoin de service mesh, surcharge de gouvernance |
| **Hybrid (modulaire monolithe)** | Possibilité d’extraire plus tard, découpage logique interne | Nécessite une bonne structuration du code dès le départ |

#### Décision  
**Monolithe** retenu. Le projet démarre comme une application unique, découpée en modules internes (controllers, services, batch). La modularité du code (packages Java) facilitera une éventuelle migration vers micro‑services.  

#### Conséquences  

- **Positives** : Délai de mise en production réduit, moindre coût d’infrastructure.  
- **Négatives** : Scalabilité verticale uniquement, besoin de surveiller la taille du JAR/WAR.  
- **À valider** : Plan de migration future (extraction du batch JORF en micro‑service).  

---  

### ADR‑002 – Stack technologique principal  

- **Statut** : Accepté  
- **Date** : 2023‑02‑15  
- **Décideurs** : Architecte, Responsable technique  

#### Contexte  
Le code existant repose sur Java 8, Tomcat 9, Struts 2 et PostgreSQL 9.6. Les équipes maîtrisent ces technologies.  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **Java 8 + Tomcat 9** (stabilité, compatibilité) | Réutilisation du code existant, low risk | Fin de support à moyen terme, manque de fonctionnalités modernes |
| **Java 11 + Tomcat 10** (Jakarta EE) | LTS, meilleures performances, préparation à la migration | Nécessite refactoring du code Struts (migration vers Jakarta) |
| **Java 17 + Spring Boot** | Modernité, auto‑configuration, support cloud‑native | Refactor complet du projet, coût de migration élevé |

#### Décision  
**Java 8 + Tomcat 9** conservé pour la version 1.3.x. Un **plan de migration** vers Java 11 / Tomcat 10 sera défini pour les versions futures (v2.0).  

#### Conséquences  

- **Positives** : Pas de rupture de compatibilité immédiate.  
- **Négatives** : Endettement technique lié à la fin de support de Java 8.  
- **À valider** : Planning de migration, tests de compatibilité.  

---  

### ADR‑003 – Persistance des données  

- **Statut** : Accepté  
- **Date** : 2023‑02‑16  
- **Décideurs** : DBA, Architecte  

#### Contexte  
Les scripts d’initialisation et de migration sont déjà disponibles (scripts SQL sous `adminep-database/scripts`). Le modèle de données est fortement relationnel (mandats, établissements, charges).  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **PostgreSQL 9.6** (actuel) | Fonctionnalités déjà utilisées, scripts compatibles | Fin de vie prévue 2024, manque de performances comparées à 15 |
| **PostgreSQL 15** (upgrade) | Améliorations de performances, support prolongé | Migration de données, adaptation des scripts (type `OID` désactivé) |
| **NoSQL (MongoDB)** | Flexibilité de schéma, requêtes JSON | Perte de contraintes d’intégrité, réécriture complète du modèle |

#### Décision  
Conserver **PostgreSQL 9.6** pour la version actuelle, mais **planifier une migration** vers **PostgreSQL 15** dans la prochaine release (v2.0).  

#### Conséquences  

- **Positives** : Continuité de l’exploitation, aucun impact immédiat.  
- **Négatives** : Besoin de tests de migration, mise à jour des drivers JDBC.  
- **À valider** : Stratégie de migration (dump/restore vs réplication).  

---  

### ADR‑004 – Authentification & Sécurité  

- **Statut** : Accepté  
- **Date** : 2023‑02‑17  
- **Décideurs** : Responsable sécurité, Architecte  

#### Contexte  
Le projet doit respecter les exigences de **DI‑CT** et garantir que chaque utilisateur ne voit que les données autorisées. Le service **Cerbère** fournit l’authentification unique (SSO) et les profils (ex. `BaseAdminUserSession`).  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **Intégration Cerbère (OAuth2 / SAML)** | Centralisation, conformité, aucune gestion de mots de passe interne | Dépendance à un service externe, besoin de mapping des rôles |
| **Gestion interne (Spring Security + DB)** | Autonomie, contrôle total | Duplication de l’effort, maintenance supplémentaire |
| **Hybrid (Cerbère + fallback interne)** | Redondance, continuité en cas d’indisponibilité | Complexité d’implémentation |

#### Décision  
**Intégration Cerbère** uniquement (option 1). Le module `SecurityManagerInitializer` charge les filtres Cerbère, le `RightsHelper` réalise le mapping des rôles (`RoleApplicatifEnum`, `RoleVertigoEnum`).  

#### Conséquences  

- **Positives** : Gestion centralisée des habilitations, auditabilité.  
- **Négatives** : Nécessité de maintenir la synchronisation des profils.  
- **À valider** : Tests d’intégration SSO, plan de continuité d’activité (BIA).  

---  

### ADR‑005 – Déploiement & Conteneurisation  

- **Statut** : Accepté  
- **Date** : 2023‑03‑01  
- **Décideurs** : DevOps, Architecte  

#### Contexte  
Le projet évolue vers la **containerisation** (Docker) pour faciliter le déploiement sur les environnements IaaS (ECO4) et faciliter la montée de version.  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **Docker + Docker‑Compose** (déploiement simple) | Isolation, reproductibilité, versionning des images | Gestion du réseau, volume persistant DB séparé |
| **Kubernetes** (full orchestration) | Scalabilité, self‑healing, déploiement blue‑green | Complexité d’infrastructure, besoin de cluster |
| **VM traditionnelle** (sans conteneur) | Simplicité d’exploitation actuelle | Moins portable, lourde à mettre à jour |

#### Décision  
Adoption de **Docker + Docker‑Compose** pour la version 1.4.x (pré‑prod). Le `adminep-deployment` contient les fichiers `assembly‑sources.xml` et `assembly‑zip.xml` qui seront utilisés pour générer les artefacts Docker.  

#### Conséquences  

- **Positives** : Déploiement automatisé, environnement de test identique à la prod.  
- **Négatives** : Gestion des volumes pour PostgreSQL, monitoring des conteneurs.  
- **À valider** : Pipeline CI/CD (GitLab CI) pour build et push des images.  

---  

### ADR‑006 – Intégration JORF  

- **Statut** : Accepté  
- **Date** : 2023‑03‑02  
- **Décideurs** : PO, Architecte, Développeur batch  

#### Contexte  
Les mentions légales et les mandats sont publiés dans le **Journal Officiel de la République Française (JORF)**. Le projet doit automatiser l’import de ces données.  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **RSS + téléchargement .tar.gz** (actuel) | Simplicité, déjà implémenté (`JORFExtractor`) | Parsing lourd, dépendance à la structure du .tar.gz |
| **API officielle JORF (si disponible)** | Données structurées, moins de parsing | Pas d’API publique fiable à ce jour |
| **Web‑scraping** | Contrôle total sur le contenu | Fragile aux changements de l’interface web |

#### Décision  
Conserver le **processus RSS + .tar.gz** via le batch `ArticleAnalyser`. Le `ArticleAnalyser` orchestre les étapes de parsing (`StepAnalyse*`).  

#### Conséquences  

- **Positives** : Solution déjà fonctionnelle, aucune dépendance externe supplémentaire.  
- **Négatives** : Risque de rupture si le format du .tar.gz change.  
- **À valider** : Monitoring du job batch, alertes en cas d’échec.  

---  

### ADR‑007 – Cache & Performance  

- **Statut** : Accepté  
- **Date** : 2023‑03‑05  
- **Décideurs** : Architecte, Développeur  

#### Contexte  
Les recherches multi‑critères (nom, mandat, établissement) sont gourmandes.  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **Cache 2‑niveau (EhCache / Caffeine)** | Réduction du nombre de requêtes DB, configurable TTL | Complexité de configuration, invalidation |
| **ElasticSearch** (indexation) | Recherche full‑text ultra‑rapide | Coût d’infrastructure, synchronisation |
| **Pas de cache** (DB uniquement) | Simplicité | Performances insuffisantes à forte charge |

#### Décision  
Implémenter **Caffeine** (cache 2‑niveau) pour les listes de référence (charges, ministères, types de mandat). Les recherches métier restent sur PostgreSQL.  

#### Conséquences  

- **Positives** : Amélioration notable du temps de réponse.  
- **Négatives** : Gestion du cycle de vie du cache (invalidations).  
- **À valider** : Monitoring du hit‑ratio, dimensionnement du cache.  

---  

### ADR‑008 – Gestion des erreurs & Résilience  

- **Statut** : Accepté  
- **Date** : 2023‑03‑07  
- **Décideurs** : Architecte, Responsable qualité  

#### Contexte  
Le système doit être robuste face aux erreurs d’import JORF, aux problèmes de connexion DB et aux incidents de sécurité.  

#### Options  

| Option | Avantages | Inconvénients |
|---|---|---|
| **ErrorHandler centralisé** (classe `ErrorHandler`) | Uniformisation des réponses, logging structuré | Nécessite adaptation des actions existantes |
| **Circuit Breaker (Resilience4j)** | Protection contre les appels défaillants (ex. JORF) | Complexité de configuration |
| **Aucun** (propagation d’exception) | Simplicité | Risque de crash, mauvaise expérience utilisateur |

#### Décision  
Utiliser **ErrorHandler** pour capturer les exceptions au niveau du contrôleur et renvoyer une page d’erreur générique (`application-error.jsp`). En complément, **Resilience4j** sera ajouté sur les appels externes (JORF, Cerbère).  

#### Conséquences  

- **Positives** : Expérience utilisateur préservée, logs centralisés (`log4j2.xml`).  
- **Négatives** : Besoin d’écrire des wrappers autour des appels externes.  
- **À valider** : Tests d’endurance, seuils du circuit‑breaker.  

---  

## 5️⃣ Niveau 3 – Vue **Composants** (C4‑L3)  

> Diagrammes pour les conteneurs critiques : **Web Application**, **Batch JORF Importer**.  

```mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Component.puml

Container(web_app, "Web Application", "Java 8 / Tomcat 9") {
    Component(controller_pkg, "Controllers", "Struts2 MVC", "Gestion des actions HTTP")
    Component(service_pkg, "Services", "Business logic", "Orchestration, validation, droits")
    Component(repo_pkg, "Repositories", "DAO", "Accès JDBC à PostgreSQL")
    Component(security_pkg, "Security", "Cerbère integration", "AuthN/Z, RightsHelper")
    Component(scheduler_pkg, "Scheduler", "Quartz", "Planification des tâches (ex. import JORF)")
    Component(error_pkg, "Error handling", "ErrorHandler", "Gestion centralisée des exceptions")
}
Rel(controller_pkg, service_pkg, "Appelle")
Rel(service_pkg, repo_pkg, "Accède")
Rel(service_pkg, security_pkg, "Vérifie les droits")
Rel(controller_pkg, error_pkg, "Propagate exceptions")
Rel(scheduler_pkg, service_pkg, "Déclenche import")
```

### 5.1 Composants principaux  

| Package | Rôle | Principales classes |
|---|---|---|
| `fr.gouv.e2.baseadmin.controller.*` | Contrôleurs MVC (Accueil, Admins, Etablissements, Mandats, Statistiques) | `AccueilAction`, `DetailAdminAction`, `RechercheAdminsAction`, `UpsertAdminAction`, … |
| `fr.gouv.e2.baseadmin.services.*` | Services métiers (CRUD, logique de mandat) | `AdministrateurServicesImpl`, `GestionnaireServicesImpl`, `MandatServicesImpl`, `ArticleServicesImpl` |
| `fr.gouv.e2.baseadmin.model.*` | Entités métier (POJO) | `RoleApplicatifEnum`, `RoleVertigoEnum`, `CodeEnum` |
| `fr.gouv.e2.baseadmin.security.*` | Sécurité (session, droits) | `BaseAdminUserSession`, `RightsHelper`, `SecurityHelper` |
| `fr.gouv.e2.baseadmin.util.articleanalyser.*` | Import JORF (pipeline) | `ArticleAnalyser`, `StepAnalyseRechercheNominations`, `StepAnalyseVerifierAutresNominations` |
| `fr.gouv.e2.baseadmin.orchestra.*` | Orchestration (activity engine) | `RecupererJORFActivityEngine`, `TraitementRecuperationJORF` |
| `fr.gouv.e2.baseadmin.errorhandler.ErrorHandler` | Gestion centralisée des erreurs | – |
| `fr.gouv.e2.baseadmin.dynamo.search.ReindexArticlesByArtiIDTask` | Re‑indexation (ElasticSearch future) | – |

---  

## 6️⃣ Niveau 4 – Vue **Code** (optionnel)  

- **Pattern de code** : DAO, Service, Controller (MVC).  
- **Convention** : Google Java Style, `checkstyle` via Maven.  
- **Tests** : JUnit 5, Mockito, integration tests (Spring Test).  
- **Build** : Maven (`pom.xml` à la racine, modules `adminep‑database`, `adminep‑web`, `adminep‑deployment`).  

---  

## 7️⃣ Scénarios critiques – Diagrammes de séquence  

### 7.1 Mise à jour d’un mandat et notification d’échéance  

```mermaid
sequencediagram;
    participant UI as Utilisateur;
    participant C as Controller (UpsertMandatAction)
    participant S as Service (MandatServices)
    participant R as Repository (MandatDAO)
    participant DB as PostgreSQL;
    participant N as NotificationService (Email)
    participant Scheduler as Quartz Scheduler;
    UI->>C: POST /mandats/upsert (données mandat)
    C->>S: upsertMandat()
    S->>R: saveOrUpdate()
    R->>DB: INSERT/UPDATE;
    DB-->>R: OK;
    R-->>S: OK;
    S->>N: scheduleAlertIfNearExpiry()
    N->>Scheduler: scheduleJob(dateEcheance-30j)
    Scheduler-->>N: Job programmé;
    Note right of UI: L’utilisateur voit la confirmation
```

### 7.2 Import JORF (batch)  

```mermaid
sequencediagram;
    participant Scheduler as Quartz (Batch)
    participant Extractor as JORFExtractor;
    participant Analyzer as ArticleAnalyser;
    participant DB as PostgreSQL;
    participant Logger as Log4j2;
    Scheduler->>Extractor: fetchRSS()
    Extractor->>Extractor: download .tar.gz;
    Extractor-->>Scheduler: stream d’articles;
    Scheduler->>Analyzer: analyse(articles)
    Analyzer->>Analyzer: StepAnalyse* (pipeline)
    Analyzer->>DB: upsertEntités()
    DB-->>Analyzer: OK;
    Analyzer-->>Scheduler: Résultat;
    Scheduler->>Logger: log "Import JORF terminé"
```

---  

## 8️⃣ Vue **Déploiement** (C4‑Deployment)  

```mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Deployment.puml

Deployment_Node(prod, "Environnement Production", "Data Center – Paris La Défense") {
    ContainerDb(pg, "PostgreSQL 15", "DB", "Persist les référentiels")
    Container(web, "admin_ep Web", "Docker (Tomcat 9)", "Application Java")
    Container(batch, "Batch JORF Importer", "Docker (Java)", "Quartz Scheduler")
    Container(email, "Mail Server", "Postfix", "SMTP")
}
Rel(web, pg, "JDBC")
Rel(batch, pg, "JDBC")
Rel(web, email, "SMTP")
Rel(web, "Cerbère", "OAuth2/SAML")
Rel(batch, "JORF", "HTTPS (RSS)")
```

### 8.1 Environnements  

| Environnement | Type | Artefacts | Observations |
|---|---|---|---|
| **Développement** | Docker‑Compose (local) | `admin_ep-web:latest`, `postgres:9.6` | Hot‑reload via Maven |
| **Pré‑production** | Docker‑Compose (cluster) | Images versionnées (v1.3.3) | Tests d’intégration, monitoring |
| **Production** | Docker (Docker‑Swarm) | Images signées, registre interne | HA, sauvegarde nightly DB |

---  

## 9️⃣ Sujets transverses & Qualités  

| Sujet | Décision / Action | Responsable |
|---|---|---|
| **Sécurité** | Utilisation de Cerbère, chiffrement TLS, audit de code | Responsable Sécurité |
| **Performance** | Cache Caffeine, index DB (type_mandat, charge) | DBA |
| **Monitoring** | Log4j2 + Prometheus JMX exporter, alertes sur batch JORF | DevOps |
| **Testabilité** | Couverture unitaires ≥ 80 %, tests d’intégration CI | QA |
| **Accessibilité** | Conformité WCAG 2.1 (pages JSP) | UI/UX |
| **GDPR / DI‑CT** | Documentation DSI, registre des traitements | DPO |

---  

## 🔟 Risques & Dettes techniques  

| Risque | Impact | Probabilité | Mitigation |
|---|---|---|---|
| **Fin de support Java 8 / Tomcat 9** | Perte de correctifs sécurité | Haute | Plan de migration v2.0 (Java 11, Tomcat 10) |
| **Changement du format JORF** | Batch JORF en échec | Moyen | Tests de parsing automatisés, fallback sur archive précédente |
| **Endettement du monolithe** | Difficulté à scaler | Moyen | Refactorisation modulaire, découpage en micro‑services futur |
| **Défaillance Cerbère** | Blocage des utilisateurs | Faible | Mode “maintenance” avec comptes locaux temporaires |
| **Cache incohérent** | Données affichées obsolètes | Moyen | TTL courte (5 min) pour les listes de référence, purge on write |

---  

## 1️⃣1️⃣ Feuille de route & Évolutivité  

| Version cible | Objectif | Action principale |
|---|---|---|
| **v1.4.x** (2023‑Q4) | Containerisation, CI/CD | Docker, GitLab CI pipelines, monitoring |
| **v2.0.0** (2024‑H1) | Migration technologique | Java 11, Tomcat 10, PostgreSQL 15, découpage micro‑services (Batch JORF) |
| **v2.1.0** (2024‑H2) | Recherche avancée | Intégration ElasticSearch (indexation JORF) |
| **v3.0.0** (2025) | Cloud‑native | Migration vers Kubernetes, Helm charts, observabilité (OpenTelemetry) |

---  

## 1️⃣2️⃣ Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|---|---|
| **Mandat** | Période d’occupation d’un poste au sein d’un conseil d’administration. |
| **Charge** | Ministère ou entité responsable d’un établissement public. |
| **Cerbère** | Service d’authentification unique (SSO) du ministère. |
| **JORF** | Journal Officiel de la République Française (source légale). |
| **RBAC** | Role‑Based Access Control (contrôle d’accès basé sur les rôles). |
| **ADRs** | Architecture Decision Records, décisions documentées. |

### 12.2 Index des ADRs  

| ADR | Titre | Statut |
|---|---|---|
| ADR‑001 | Choix de l’architecture globale | Accepté |
| ADR‑002 | Stack technologique principal | Accepté |
| ADR‑003 | Stratégie de persistance des données | Accepté |
| ADR‑004 | Pattern d’authentification et sécurité | Accepté |
| ADR‑005 | Stratégie de déploiement et conteneurisation | Accepté |
| ADR‑006 | Approche d’intégration avec systèmes externes (JORF) | Accepté |
| ADR‑007 | Stratégie de cache et performance | Accepté |
| ADR‑008 | Gestion des erreurs et résilience | Accepté |

### 12.3 Références & Ressources  

| Ressource | URL |
|---|---|
| **Code source** | `gitlab/ambulon/workplace-ambulon/gitlab/admin_ep` |
| **Documentation JORF** | <https://echanges.dila.gouv.fr/OPENDATA/JORF/> |
| **Service Cerbère** | <https://cerbere.gouv.fr> |
| **C4‑Model** | <https://c4model.com/> |
| **Mermaid‑C4** | <https://github.com/Mermaid-stdlib/C4-Mermaid> |
| **ISO/IEC‑25010** | <https://iso25010.com> |

---  

*Ce DAT est vivant : chaque décision, diagramme ou contrainte doit être revu à chaque itération du projet et versionné dans le dépôt Git.*  