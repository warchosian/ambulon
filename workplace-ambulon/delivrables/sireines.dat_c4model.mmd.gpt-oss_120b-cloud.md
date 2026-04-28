**SIREINES – Dossier d’Architecture Technique (DAT)**  
*Version : 2.5.20 – 12 mars 2026*  
*Document : `SIREINES-DAT.md`*  

---  

# 📑 Table des matières  

[TOC]

---  

## 1️⃣ Introduction & objectifs  

| | |
|---|---|
| **Vue d’ensemble fonctionnelle** | SIREINES est une application métier : elle recense les demandes de qualification des experts et spécialistes scientifiques et techniques, assure le suivi des dossiers, la coordination des comités de domaine et la diffusion des décisions aux agents. |
| **Objectifs de qualité orientés utilisateur** | 1️⃣ **Performance** – réponses < 2 s pour les écrans de recherche.  <br>2️⃣ **Sécurité** – conformité D‑I‑C‑T (Disponibilité, Intégrité, Confidentialité, Traçabilité). <br>3️⃣ **Maintenabilité** – architecture modulaire (C4) + tests unitaires ≥ 80 %. <br>4️⃣ **Observabilité** – logs, métriques (Prometheus/Grafana) et alerting. <br>5️⃣ **Portabilité** – déploiement via Docker / Docker‑Compose, compatible IaaS (ECO4). |

---  

## 2️⃣ Niveau 1 – Vue *Contexte* (C4‑L1)

```mermaid
%%{init: {'theme':'default'}}%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Context.puml

Person(admin, "Administrateur fonctionnel", "Gestion des paramètres, versionnage, supervision")
Person(agent, "Agent expert", "Consultation, création et suivi de dossiers")
System_Ext(cerbere, "Cerbère", "Gestion des habilitations")
System_Ext(birt, "BIRT 4.3", "Reporting & export PDF")
System_Ext(gitlab, "GitLab", "Gestion du code source, CI/CD")
System_Ext(sonarqube, "SonarQube", "Qualité du code")
System(sireines, "SIREINES", "Application de suivi des qualifications")
Rel(admin, sireines, "Utilise")
Rel(agent, sireines, "Utilise")
Rel(sireines, cerbere, "Vérifie les droits", "REST/HTTPS")
Rel(sireines, birt, "Génère les rapports", "Web‑service")
Rel(sireines, gitlab, "Déclenche pipelines CI", "Web‑hook")
Rel(sireines, sonarqube, "Envoie métriques qualité", "API")
```

### 2.1 Acteurs principaux  

| Rôle | Objectif | Besoin fonctionnel |
|------|----------|-------------------|
| **Agent** | Saisir, consulter et suivre un dossier | Authentification, formulaire de création, recherche, export BIRT |
| **Administrateur fonctionnel** | Gérer la configuration, les paramètres d’envoi de mail, les listes de références | Accès aux écrans d’administration, gestion des droits (via Cerbère) |
| **Superviseur / Exploitant** | Veiller à la disponibilité, aux logs et alertes | Dashboard Prometheus, alertes, sauvegardes automatiques |
| **Développeur / CI** | Livrer de nouvelles versions | GitLab, pipeline CI, tests automatisés, SonarQube |

### 2.2 Systèmes externes  

| Système | Type | Interface |
|---------|------|-----------|
| **Cerbère** | Service d’habilitation | REST / HTTPS (token JWT) |
| **BIRT** | Moteur de reporting | HTTP / Web‑service (PDF, XLS) |
| **PostgreSQL** | SGBD | JDBC |
| **GitLab** | SCM & CI | API / Web‑hook |
| **SonarQube** | Qualité du code | API / HTTPS |
| **ECO4 (IaaS)** | Infrastructure cloud | OpenStack tenant *pnm3* (VM, stockage, réseau) |
| **Nginx** | Reverse‑proxy / Load‑balancer | TCP / HTTP / HTTPS |

---  

## 3️⃣ Niveau 2 – Vue *Conteneurs* (C4‑L2)

```mermaid
%%{init: {'theme':'default'}}%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Container.puml

System_Boundary(sireines, "SIREINES") {
    Container(web_app, "SIREINES‑Web", "Java / Spring + Struts2", "Application métier (MVC) – exécutée sous Tomcat")
    ContainerDb(postgres, "PostgreSQL 14‑alpine", "SQL", "Base de données métier")
    Container(birt_srv, "BIRT Server", "Java / BIRT 4.3", "Moteur de reporting")
    Container(docker_compose, "Docker‑Compose", "YAML", "Orchestre les conteneurs (web, db, pgAdmin)")
}

Rel(web_app, postgres, "JDBC", "postgres")
Rel(web_app, birt_srv, "Web‑service", "HTTP/HTTPS")
Rel(docker_compose, web_app, "Démarre")
Rel(docker_compose, postgres, "Démarre")
Rel(docker_compose, birt_srv, "Démarre")
```

### 3.1 Conteneur **SIREINES‑Web**  

| Élément | Technologie | Rôle | Principaux packages |
|---------|-------------|------|----------------------|
| **Tomcat 7.0.108‑JDK8** | Servlet container | Héberge le WAR `sireines‑web‑*.war` |
| **Spring Framework** | IoC, transactions | Gestion des beans, AOP |
| **Vertigo / Dynamo** | DDD, recherche | `SearchManager`, indexation Elasticsearch |
| **Struts2** | MVC, tags UI | Formulaires, navigation |
| **BIRT Manager** (interface) | Génération PDF/Excel | `BirtManager` |
| **Talend libs** | Import / Export | `importfichiersirene_0_1.jar`, `systemRoutines.jar` |
| **Log4j 2** | Logging | Configurable via `log4j.xml` |
| **Prometheus client** | Métriques | `/actuator/prometheus` |
| **Dockerfile** | Build | Copie du WAR, unzip, entrypoint script |

### 3.2 Conteneur **PostgreSQL**  

| Élément | Version | Rôle |
|---------|---------|------|
| **postgres:14.1‑alpine** | 14.1 | Base de données métier, persistance via volume `sireines_db_sireines_vol` |
| **Schemas** | `public` + `sireines` | Tables : `DOSSIER`, `AGENT`, `COMITE`, … (modélisation PowerDesigner) |
| **Sauvegardes** | Script `pg_dump` (AES‑256) | Stockage sur B3, Outscale SecNumCloud, Google Cloud |

### 3.3 Conteneur **BIRT Server**  

| Élément | Version | Rôle |
|---------|---------|------|
| **BIRT 4.3** (embedded) | 4.3 | Génération de rapports (ex. « Statistiques », « Pyramide d’âge ») à partir de templates `.rptdesign` |
| **Volumes** | `birt_reports` | Stockage des modèles et des rapports générés |

### 3.4 Conteneur **Docker‑Compose**  

*Fichier : `docker-compose.yml`* – définit les 3 conteneurs + **pgAdmin** (outil d’administration).  
Volumes persistants :  

* `sireines_db_sireines_vol` → données PostgreSQL  
* `sireines_pgadmin_sireines_vol` → configuration pgAdmin  

---  

## 4️⃣ Niveau 3 – Vue *Composants* (C4‑L3) – **SIREINES‑Web** (exemple)  

```mermaid
%%{init: {'theme':'default'}}%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Component.puml

Container(web_app, "SIREINES‑Web", "Java / Spring + Struts2", "Conteneur d’application")
Component(controller_pkg, "Controllers", "Struts2 actions", "Gestion des flux UI")
Component(service_pkg, "Services", "Business logic", "AgentsService, DossiersService, ExtractionsService …")
Component(birt_mgr, "BIRT Manager", "Facade", "Publication PDF/Excel")
Component(search_mgr, "Search Manager", "Vertigo‑Elasticsearch", "Indexation dossiers")
Component(persistence, "Persistence", "JPA/Hibernate", "Accès aux tables PostgreSQL")
Rel(controller_pkg, service_pkg, "Appelle")
Rel(service_pkg, persistence, "Utilise")
Rel(service_pkg, birt_mgr, "Génère rapports")
Rel(service_pkg, search_mgr, "Indexe / Recherche")
```

### 4.1 Principaux packages / classes  

| Package | Exemple de classe | Responsabilité |
|---------|-------------------|----------------|
| `i2.application.sireines.controller.*` | `AccueilAction`, `ContactAction` | Entrées Struts2, navigation, validation |
| `i2.application.sireines.service.*` | `AgentsServicesImpl`, `DossiersServicesImpl` | Logique métier, transactions |
| `i2.application.sireines.boot.manager.BirtManager` | Implémentation `BirtManagerImpl` | Appel à BIRT pour production de rapports |
| `i2.application.sireines.boot.initializer.SearchManagerInitializer` | `SearchManagerInitializer` | Re‑indexation Elasticsearch au démarrage |
| `i2.application.sireines.util.CsvExport` | `CsvExport` | Export CSV personnalisé (gestion des balises HTML) |
| `i2.application.sireines.boot.ApplicationServletContextListener` | `ApplicationServletContextListener` | Initialisation du contexte Spring/Vertigo |

---  

## 5️⃣ Niveau 4 – Vue *Code* (optionnel)  

> **Remarque** : les diagrammes de classe UML sont trop nombreux pour être affichés intégralement.  
> Un diagramme de séquence illustrant le **processus d’extraction d’un rapport** est présenté ci‑dessous (section 6).  

---  

## 6️⃣ Scénarios d’exécution (Vue *Séquence*)  

### 6.1 Extraction d’un rapport BIRT (exemple)  

```mermaid
%%{init: {'theme':'default'}}%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Sequence.puml

Title Extraction d’un rapport de “Pyramide d’âge”

Participant Agent as "Agent (Web UI)"
Participant Web as "SIREINES‑Web (Struts2)"
Participant Service as "ReportService"
Participant Birt as "BIRT Server"
Participant DB as "PostgreSQL"

Agent ->> Web: Request /extraction08.do
Web ->> Service: generateReport(params)
Service ->> DB: SELECT * FROM DOSSIER … (filtrage)
DB -->> Service: ResultSet
Service ->> Birt: HTTP POST /runReport (template .rptdesign, data)
Birt -->> Service: PDF (binary)
Service ->> Web: stream PDF
Web ->> Agent: download / display
```

### 6.2 Authentification / Vérification des droits (Cerbère)  

```mermaid
%%{init: {'theme':'default'}}%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Sequence.puml

Title Authentification d’un agent

Participant Agent as "Agent (Browser)"
Participant Web as "SIREINES‑Web (Struts2)"
Participant Cerb as "Cerbère (IAM)"
Participant DB as "PostgreSQL"

Agent ->> Web: POST /login (username, pwd)
Web ->> Cerb: GET /auth?user=… (JWT)
Cerb -->> Web: token + groups
Web ->> DB: SELECT * FROM AGENT WHERE login=…
DB -->> Web: Agent profile
Web ->> Agent: Session cookie + UI
```

---  

## 7️⃣ Vue *Déploiement* (section standardisée)  

```mermaid
%%{init: {'theme':'default'}}%%%%
!include https://raw.githubusercontent.com/Mermaid-stdlib/C4-Mermaid/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack tenant *pnm3*") {
    Deployment_Node(nginx, "Nginx Cluster", "Load‑balancer") {
        Container(app, "SIREINES‑Web", "Docker container (Tomcat)", "Application métier")
    }
    Deployment_Node(db, "PostgreSQL", "Docker container") {
        ContainerDb(database, "SIREINES‑DB", "PostgreSQL", "Données métier")
    }
    Deployment_Node(birt, "BIRT Server", "Docker container") {
        Container(birt_srv, "BIRT", "Java / BIRT 4.3", "Moteur de reporting")
    }
}
Rel(nginx, app, "HTTP/HTTPS")
Rel(app, database, "JDBC")
Rel(app, birt_srv, "REST / HTTP")
```

### 7.1 Tableau des environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Laptop / Docker‑Desktop | `sireines_app_dev`, `sireines_db_dev` | Bridge (docker0) | Volume local `./data` |
| **Recette** | Serveur *sireinesrec* (ECO4) | `sireines_app_usine_container`, `sireines_db_usine_container` | VLAN *pnm3‑recette* | Accès via Bastion, Nginx LB, sauvegarde quotidienne |
| **Pré‑production** | Serveur *sireinesppr* | idem Recette | VLAN *pnm3‑preprod* | Tests de charge avant prod |
| **Production** | Serveur *sireinesprod* | idem Recette | VLAN *pnm3‑prod* | Monitoring Prometheus + Alertmanager, sauvegarde chiffrée (AES‑256) sur B3, Outscale, GCP |

### 7.2 Supervision & Sauvegarde (extraits du texte)  

* **Supervision** – Portainer (Docker), stack **Prometheus / Grafana / Loki / AlertManager**, supervision **PSIN**.  
* **Sauvegarde DB** – `pg_dump` → fichier `.sql` chiffré → stockage sur :  
  - **B3** (objets ministériels)  
  - **Outscale SecNumCloud** (IAAS)  
  - **Google Cloud** (bucket)  

---  

## 8️⃣ Sujets transverses  

| Thème | Décisions / Contrainte |
|-------|-----------------------|
| **Authentification / Autorisation** | Utilisation de **Cerbère** (JWT) pour la gestion des rôles (R‑ADMIN, R‑USER). |
| **Journalisation** | Log4j 2 → `log4j.xml` ; logs agrégés dans **Loki**. |
| **Monitoring** | Métriques Prometheus (`/actuator/prometheus`), tableau de bord Grafana, alertes sur latence > 2 s ou erreurs 5xx. |
| **Gestion des erreurs** | Struts2 → `actionerror.ftl`, `actionmessage.ftl`. |
| **API** | BIRT (REST), Cerbère (REST), Elasticsearch (REST). |
| **Gestion des dépendances** | Maven 3 + `settings.xml` (serveur interne gitlab‑maven). |
| **CI/CD** | GitLab CI → pipeline **build‑docker**, **sonar‑scan**, **deployment** via Docker‑Compose. |
| **Sécurité** | Conteneurs en mode non‑root (`USER 1000` dans Dockerfile), secrets via `.env` (non versionnés). |
| **Internationalisation** | Pas de localisation prévue (uniquement FR). |
| **Gestion des fichiers temporaires** | `/tmp` nettoyé à chaque démarrage du conteneur (entrypoint script). |

---  

## 9️⃣ Exigences de qualité  

| Qualité | Scénario de validation |
|---------|------------------------|
| **Performance** | Test de charge JMeter : 100 utilisateurs simultanés, temps moyen < 2 s sur la recherche de dossiers. |
| **Disponibilité** | Test de bascule Nginx → un