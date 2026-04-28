# 📚 Dossier d’Architecture Technique – **admin_ep**  

[TOC]

---  

## 1️⃣ Introduction et objectifs  

**admin_ep** est l’application de gestion des établissements publics du ministère de la Transition écologique et solidaire. Elle centralise les listes des membres des conseils d’administration, assure la traçabilité des mandats, propose des statistiques et signale les échéances.  

### Objectifs de qualité (orientés utilisateur)  

| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Performance** – temps de réponse < 2 s pour les recherches | Garantir une expérience fluide aux opérateurs et à la MOA |
| 2 | **Sécurité** – conformité D‑I‑C‑T, authentification via Cerbère | Protéger les données personnelles des administrateurs |
| 3 | **Disponibilité** – 99,5 % en production | Assurer la continuité du service (alertes mandat) |
| 4 | **Maintenabilité** – architecture modulaire, tests unitaires > 80 % | Faciliter les évolutions (ex. Tomcat 10, Postgres 15) |
| 5 | **Traçabilité** – journalisation exhaustive des accès et modifications | Répondre aux exigences d’audit et de supervision PSIN |

↩︎ Retour au sommaire  

---  

## 2️⃣ Niveau 1 – Vue Contexte (System Context)  

```Mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Context.puml

Person(admin, "Opérateur / Gestionnaire", "Utilise l’interface web pour saisir, consulter et rechercher des administrateurs")
Person(moA, "Maîtrise d’Ouvrage (SG/SPES)", "Pilote les évolutions fonctionnelles")
System_Ext(jorf, "JO RF (OpenData)", "Flux RSS quotidien des arrêtés")
System_Ext(cerbere, "Cerbère (SSO)", "Gestion des habilitations")
System_Ext(prometheus, "Prometheus/Grafana/Loki", "Supervision et alerting")
System_Ext(psin, "Supervision PSIN", "Tableau de bord de production")

System_Boundary(admin_ep, "admin_ep") {
    System(web, "admin_ep‑web", "Application Java (Struts2/Vertigo)", "Interface web")
    System(db, "admin_ep‑database", "PostgreSQL 9.6.11 → 15", "Stockage des référentiels")
}

Rel(admin, web, "Utilise")
Rel(moA, web, "Exprime les besoins")
Rel(web, db, "JDBC/SQL")
Rel(web, cerbere, "Authentification SSO")
Rel(web, jorf, "Lecture du flux RSS (import JORF)")
Rel(web, prometheus, "Export métriques")
Rel(web, psin, "Envoi d’alertes de mandat")
```

### Acteurs principaux  

| Acteur | Objectif |
|--------|----------|
| **Opérateur / Gestionnaire** | Saisir, mettre à jour et rechercher les administrateurs |
| **Maîtrise d’Ouvrage (SG/SPES)** | Piloter les évolutions fonctionnelles et valider les livrables |
| **Cerbère** | Authentifier les utilisateurs et appliquer les habilitations |
| **JO RF** | Alimenter automatiquement la base avec les nouveaux mandats |
| **Prometheus / Grafana** | Suivre les indicateurs de santé et déclencher les alertes |
| **Supervision PSIN** | Centraliser la surveillance de production |

↩︎ Retour au sommaire  

---  

## 3️⃣ Parties prenantes  

| Rôle | Attente principale |
|------|---------------------|
| **Chef de produit** (Christian Arbogast) | Livraison continue, conformité sécurité |
| **Développeur CGI** | Architecture claire, CI/CD fiable |
| **DSI / PNM3** | Exploitation stable, monitoring intégré |
| **MOA – SG/SPES** | Fonctionnalités métier (recherche, alertes) |
| **Utilisateurs finaux** (Gestionnaires, SPES) | Interface ergonomique, temps de réponse rapide |
| **Auditeur sécurité** | Conformité D‑I‑C‑T, traçabilité complète |

↩︎ Retour au sommaire  

---  

## 4️⃣ Contraintes  

| Type | Description |
|------|-------------|
| **Techniques** | Java 8 (prévu migration Tomcat 10, Postgres 15), Docker, Nginx reverse‑proxy, Struts 2, Vertigo, PostgreSQL |
| **Organisationnelles** | Processus de mise à jour via *gitlab* (CI / CD), livraisons en lot (version 1.3.3 en prod) |
| **Réglementaires** | D‑I‑C‑T (Disponibilité, Intégrité, Confidentialité, Traçabilité) – audit annuel |
| **Sécurité** | Authentification via Cerbère, chiffrement TLS, mots de passe baseadmin en base (script `0_createUserAndDB.sql`) |
| **Performance** | Indexation des tables `TYPE_MANDAT`, `CHARGE`, `ETABLISSEMENT` (scripts `1_index_and_pk.sql`) |
| **Interopérabilité** | Consommation du flux RSS JORF (HTTPS), échanges avec le portail support DIN via API REST (non détaillé) |

↩︎ Retour au sommaire  

---  

## 5️⃣ Niveau 2 – Vue Conteneurs (Containers)  

```Mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Container.puml

System_Boundary(admin_ep, "admin_ep") {
    Container(web, "admin_ep‑web", "Docker (Java 8, Tomcat 9)", "Application web Struts2/Vertigo")
    Container(db, "admin_ep‑database", "Docker (PostgreSQL 9.6 → 15)", "Base de données référentiels")
    Container(nginx, "Nginx LB", "Docker (Nginx)", "Reverse‑proxy, load‑balancing")
    Container(jorfJob, "JORF Import Job", "Java (Scheduler)", "Lecture du flux RSS JORF, mise à jour DB")
    Container(prom, "Prometheus / Grafana", "Docker", "Collecte métriques, alertes")
}
Rel(admin, web, "HTTPS")
Rel(web, db, "JDBC")
Rel(web, cerbere, "SAML/SSO")
Rel(web, jorfJob, "Déclenchement (cron)")
Rel(jorfJob, db, "JDBC")
Rel(web, prometheus, "Export métriques")
Rel(nginx, web, "HTTP/HTTPS")
Rel(nginx, db, "TCP")
```

### Description des conteneurs  

| Conteneur | Responsabilité | Technologie | Points d’interaction clés |
|-----------|----------------|-------------|---------------------------|
| **admin_ep‑web** | Interface utilisateur, logique métier, contrôleurs Struts2 | Java 8, Tomcat 9, Vertigo, Struts2, Maven | DB (JDBC), Cerbère (SSO), JORF Job (scheduler), Prometheus (metrics) |
| **admin_ep‑database** | Persistance des référentiels (TYPE_MANDAT, CHARGE, ETABLISSEMENT…) | PostgreSQL 9.6 → 15, scripts d’init & d’update (see `adminep-database/scripts`) | Web (JDBC), JORF Job (JDBC) |
| **Nginx LB** | Répartition de charge, terminaison TLS | Nginx (Docker) | Front‑end HTTP → Web, TCP → DB (option “direct DB access” en interne) |
| **JORF Import Job** | Extraction quotidienne du flux JORF, enrichissement DB | Java Scheduler (Spring/Quartz) | DB (JDBC), RSS JORF (HTTPS) |
| **Prometheus / Grafana** | Supervision, alertes de disponibilité/mandats | Prometheus, Grafana, Loki, AlertManager | Web (metrics endpoint `/actuator/metrics`) |

### Décisions architecturales majeures  

* **Monolithe web** – Tous les modules (admin, établissements, mandats, statistiques) sont déployés dans le même conteneur *admin_ep‑web* (facilité de mise à jour).  
* **Pattern MVC** – Struts2 + Vertigo assure la séparation contrôleur / service / modèle.  
* **CI/CD** – GitLab CI construit les images Docker, exécute les tests unitaires (JUnit) et déploie via *GitLab‑Runner* sur le tenant `pnm3` (ECO4).  

↩︎ Retour au sommaire  

---  

## 6️⃣ Niveau 3 – Vue Composants (Components) *(exemple : conteneur `admin_ep‑web`)*  

```Mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Component.puml

Container(web, "admin_ep‑web", "Java 8 / Tomcat 9") {
    Component(controller, "Controllers", "Struts2 actions", "Gestion des flux UI")
    Component(service, "Services", "Business logic (administrateurs, établissements, mandats)", "Implémentations Java")
    Component(security, "Security Layer", "Cerbère SSO, droits", "RightsHelper, SecurityHelper")
    Component(job, "Scheduler", "Import JORF", "Quartz Scheduler")
    Component(monitor, "Monitoring", "Exposition métriques", "Micrometer / Prometheus exporter")
}
Rel(controller, service, "Appelle")
Rel(service, db, "JDBC")
Rel(controller, security, "Vérifie droits")
Rel(job, service, "Trigger import")
Rel(monitor, controller, "Collecte métriques")
```

#### Principaux composants  

| Composant | Responsabilité | Classes clés (extraits) |
|-----------|----------------|------------------------|
| **Controllers** | Gestion des UI (accueil, admins, établissements, mandats, statistiques) | `AccueilAction`, `DetailAdminAction`, `RechercheAdminsAction`, `UpsertAdminAction`, `DetailEPAction`, `RechercheEPAction` |
| **Services** | Logique métier, accès aux DAO | `AdministrateurServicesImpl`, `EtablissementServicesImpl`, `MandatServicesImpl`, `ArticleSearchLoader` |
| **Security Layer** | Authentification Cerbère, droits d’accès | `BaseAdminUserSession`, `RightsHelper`, `Roles` |
| **Scheduler** | Job d’import JORF (cron quotidien) | `RecupererJORFActivityEngine`, `TraitementRecuperationJORF` |
| **Monitoring** | Export métriques vers Prometheus | `MetricsConfigurer`, endpoints `/actuator/metrics` |

↩︎ Retour au sommaire  

---  

## 7️⃣ Niveau 4 – Vue Code (Code)  

> **Note** : Les diagrammes de classes UML sont disponibles dans le dépôt `adminep-web/src/main/java/...`. Pour ce DAT, on indique que le niveau 4 existe et que les diagrammes sont générés à partir des sources (ex. : PlantUML).  

↩︎ Retour au sommaire  

---  

## 8️⃣ Vue Exécution (Scénarios)  

### 8.1 Scénario : **Recherche d’un établissement**  

```Mermaid
sequenceDiagram
    participant U as Opérateur
    participant WB as Web Browser
    participant WS as admin_ep‑web
    participant DB as admin_ep‑database
    U->>WB: Saisit le nom d’établissement
    WB->>WS: HTTP GET /etablissements/recherche?query=...
    WS->>DB: SELECT * FROM ETABLISSEMENT WHERE ... (via DAO)
    DB-->>WS: Résultat (JSON/HTML)
    WS-->>WB: Page résultat
    WB->>U: Affiche la liste
```

### 8.2 Scénario : **Import quotidien du flux JORF**  

```Mermaid
sequenceDiagram
    participant Scheduler as JORF Import Job
    participant RSS as JORF RSS (HTTPS)
    participant WS as admin_ep‑web
    participant DB as admin_ep‑database
    Scheduler->>RSS: GET /rss/jorf.xml
    RSS-->>Scheduler: XML du jour
    Scheduler->>WS: Parse & crée/maj mandats
    WS->>DB: INSERT/UPDATE (transaction)
    DB-->>WS: OK
    WS->>Scheduler: Retour statut
    Scheduler->>Prometheus: pushMetric(import_success=1)
```

### 8.3 Scénario : **Alerte d’échéance de mandat**  

```Mermaid
sequenceDiagram
    participant WS as admin_ep‑web
    participant DB as admin_ep‑database
    participant PSIN as Supervision PSIN
    WS->>DB: SELECT mandats WHERE date_fin < now()+30days
    DB-->>WS: Liste des mandats à échéance
    WS->>PSIN: POST /alertes (mail + dashboard)
    PSIN-->>WS: Ack
```

↩︎ Retour au sommaire  

---  

## 9️⃣ Vue Déploiement *(section standardisée)*  

```Mermaid
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
    Deployment_Node(nginx, "Nginx Cluster", "Load Balancer") {
        Container(app, "admin_ep‑web", "Docker (Tomcat 9)", "Application principale")
        Container(job, "JORF Import Job", "Docker (Java Scheduler)", "Job d’import JORF")
    }
    Deployment_Node(db, "Base de données", "PostgreSQL 15") {
        ContainerDb(database, "admin_ep‑database", "Docker", "Données métier")
    }
}
Rel(nginx, app, "HTTP/HTTPS")
Rel(app, database, "JDBC")
Rel(job, database, "JDBC")
Rel(app, job, "Trigger (cron)")
```

### Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|-----------------|
| Développement | Docker‑Compose local | 1 × Web, 1 × DB | Bridge Docker | Logs en console, DB en mémoire |
| Recette | Cloud ECO4 (OpenStack) | 2 × Web (HA), 1 × DB | VPC privé, SG ouvert 443/8080 | Jeux de données anonymisées |
| Production | Cloud ECO4 (OpenStack) | 4 × Web (LB), 2 × DB (replication) | VPC privé, SG ouvert 443 | Monitoring Prometheus, alertes PSIN |

### Infrastructure (texte)  

Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant **pnm3** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessus est une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```Mermaid
@startuml
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
    Deployment_Node(nginx, "Nginx Cluster", "Load Balancer") {
        Container(app, "Application", "Docker", "Application principale")
    }
    Deployment_Node(db, "Base de données", "PostgreSQL") {
        ContainerDb(database, "Database", "PostgreSQL", "Données métier")
    }
}

Rel(nginx, app, "HTTP/HTTPS")
Rel(app, database, "JDBC/SQL")
@enduml
```

### Supervision  

Le produit est supervisé via le système standard du GTI pour ce faire :

- via **Portainer** pour la partie purement conteneurisée,
- via la stack **Prometheus / Grafana / Loki / AlertManager**,
- le produit dispose également d’une supervision **PSIN**.

### Sauvegardes  

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

- le stockage objet **B3** du IaaS ministériel,
- le stockage objet **Outscale SecNumCloud** (Nuage Public),
- le stockage objet standard de **Google Cloud** (Nuage Public).

↩︎ Retour au sommaire  

---  

## 🔧 Sujets transverses  

| Sujet | Traitement |
|-------|-------------|
| **Authentification** | SSO Cerbère, jeton SAML, mapping des profils (`TypeProfilBaseAdmin`, `TypeProfilCerbere`) |
| **Journalisation** | Log4j2 (`log4j2.xml`), MDC avec `SessionAction`, centralisation via Loki |
| **Monitoring** | Export métriques Micrometer → Prometheus, alertes sur latence > 2 s, disponibilité DB |
| **Gestion des erreurs** | `ErrorHandler` global, pages d’erreur (`application-error.jsp`, `error_auth.jsp`) |
| **API interne** | Exposition de services REST (ex. : `/api/v1/etablissements`) via Struts2 REST plugin |
| **Sécurité des données** | Chiffrement des dumps, règles de rétention, contrôle d’accès au niveau DAO (`RightsHelper`) |
| **CI/CD** | GitLab CI pipelines : `mvn test`, `docker build`, `helm upgrade` sur le tenant ECO4 |
| **Gestion des versions** | `pom.xml` version `1.2.3`, packaging `docker`, tags Git correspondant aux releases |

↩︎ Retour au sommaire  

---  

## 📈 Exigences de qualité  

| Exigence | Critère d’acceptation | Scénario de validation |
|----------|----------------------|------------------------|
| **Performance** | 95 % des requêtes < 2 s en charge normale | Test de charge JMeter (100 utilisateurs simultanés) |
| **Disponibilité** | Uptime ≥ 99,5 % sur 30 jours | Monitoring Prometheus + alertes `up{job="admin_ep-web"} == 0` |
| **Sécurité** | Pas de fuite de donnée sensible (DLP) | Scan OWASP ZAP, test de pénétration annuel |
| **Traçabilité** | Tous les accès enregistrés avec `userId`, `action`, `timestamp` | Vérification des logs dans Loki, recherche `operation="login"` |
| **Scalabilité** | Ajout d’un nœud Web augmente le débit de 30 % | Test de scaling horizontal via Kubernetes HPA (replicas 2 → 4) |

↩︎ Retour au sommaire  

---  

## ⚠️ Risques et dettes techniques  

| Risque / Dette | Impact | Mitigation |
|----------------|--------|------------|
| **Obsolescence Tomcat 9** | Fin de support, incompatibilité avec Java 11+ | Planifier migration vers Tomcat 10 (Spring Boot) d’ici Q4 2026 |
| **PostgreSQL 9.6** → 15 | Risque de rupture de compatibilité des scripts | Automatiser les tests d’upgrade DB dans l’environnement de recette |
| **Couplage monolithique** (Web + logique métier) | Difficile d’introduire de nouveaux micro‑services | Refactoriser les services en modules séparés (Spring Boot) |
| **Dépendance Cerbère** (SSO propriétaire) | Risque de blocage en cas d’indisponibilité | Implémenter fallback JWT local pour les tests |
| **Scripts d’import JORF** peu testés | Erreurs de parsing → données corrompues | Ajouter des jeux de tests unitaires pour chaque version de flux JORF |

↩︎ Retour au sommaire  

---  

## 📚 Annexes  

### A. Glossaire  

| Terme | Définition |
|-------|------------|
| **CERBERE** | Système d’authentification unique (SSO) du ministère |
| **JORF** | Journal officiel de la République française – source officielle des arrêtés |
| **PROMETHEUS** | Système de collecte de métriques et d’alertes |
| **PSIN** | Plateforme de supervision interne (Supervision PSIN) |
| **ACAI** | Plateforme d’hébergement Java (clusters ESXi) |

### B. Décisions d’Architecture (ADR)  

| # | Décision | Contexte | Conséquence |
|---|----------|----------|-------------|
| **ADR‑001** | Utiliser Docker + Nginx LB | Besoin de haute disponibilité et de déploiement automatisé | Simplifie le scaling, facilite le CI/CD |
| **ADR‑002** | Conserver le monolithe Struts2 | Coût de refactorisation trop élevé à court terme | Permet une mise en production rapide, mais crée une dette technique |
| **ADR‑003** | SSO via Cerbère | Exigence de conformité aux habilitations ministérielles | Centralise la gestion des droits, dépendance à Cerbère |
| **ADR‑004** | Exporter les métriques via Micrometer | Besoin de visibilité opérationnelle | Intégration native à Prometheus, tableau de bord Grafana existant |

---  

*Document généré automatiquement le **27 avril 2026** à partir des sources du dépôt `admin_ep`. Toutes les références (fichiers, classes, scripts) sont internes au projet et accessibles via les ancres du texte.*  