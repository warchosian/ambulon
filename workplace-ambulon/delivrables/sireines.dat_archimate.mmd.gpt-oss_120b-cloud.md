# 📐 Dossier d’Architecture Technique (DAT) – **SIREINES**  

*Version : 2.5.20 (12 mars 2024) – 2024‑04‑27*  

---  

## 1️⃣ Vue d’ensemble ArchiMate  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#FFCC00', 'edgeLabelBackground':'#FFFFFF'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
archimateDiagram;
    title SIREINES – Couches Métier / Application / Technologie;
    BusinessActor "MOA CGDD/DRI/AST4" as MOA;
    BusinessActor "MOE Klee Group / SSI" as MOE;
    BusinessActor "Agent public" as Agent;
    BusinessActor "Comité de domaine" as Comité;
    BusinessRole "Chef de Produit" as ChefProd;
    BusinessRole "Développeur" as Dev;
    BusinessRole "Administrateur Système" as Ops;
    BusinessProcess "Gestion du dossier" as GP_Dossier;
    BusinessProcess "Qualification par comité" as GP_Qualif;
    BusinessProcess "Extraction de rapports" as GP_Export;
    BusinessProcess "Import de fichiers" as GP_Import;
    BusinessProcess "Gestion des contacts" as GP_Contact;
    BusinessService "Service Dossier" as BS_Dossier;
    BusinessService "Service Qualification" as BS_Qualif;
    BusinessService "Service Extraction" as BS_Export;
    BusinessService "Service Import" as BS_Import;
    BusinessService "Service Contact" as BS_Contact;
    ApplicationComponent "sireines‑web (WAR)" as AC_War;
    ApplicationComponent "BIRT Report Engine" as AC_BIRT;
    ApplicationComponent "Vertigo Search (ES)" as AC_Search;
    ApplicationComponent "Moteur Spring IoC" as AC_Spring;
    ApplicationInterface "Struts2 Web‑UI" as AI_UI;
    ApplicationInterface "REST / Elasticsearch" as AI_Elastic;
    ApplicationInterface "BIRT Templates" as AI_BIRT;
    Node "Docker‑Host (ECO4 IaaS)" as N_Host;
    Node "Container sireines‑app" as N_App;
    Node "Container PostgreSQL 14‑alpine" as N_DB;
    Node "Container pgAdmin4" as N_PgAdmin;
    Artifact "sireines‑web‑*.war" as Art_War;
    Artifact "scripts SQL / DDL" as Art_SQL;
    Artifact "docker‑compose.yml" as Art_Docker;
    Rel MOA "définit" --> ChefProd;
    Rel MOE "déploie" --> Dev;
    Rel Ops "administre" --> N_Host;
    Rel ChefProd "oriente" --> GP_Dossier;
    Rel ChefProd "oriente" --> GP_Qualif;
    Rel ChefProd "oriente" --> GP_Export;
    Rel ChefProd "oriente" --> GP_Import;
    Rel ChefProd "oriente" --> GP_Contact;
    Rel GP_Dossier "expose" --> BS_Dossier;
    Rel GP_Qualif "expose" --> BS_Qualif;
    Rel GP_Export "expose" --> BS_Export;
    Rel GP_Import "expose" --> BS_Import;
    Rel GP_Contact "expose" --> BS_Contact;
    Rel BS_Dossier "réalisé par" --> AC_War;
    Rel BS_Qualif "réalisé par" --> AC_War;
    Rel BS_Export "réalisé par" --> AC_War;
    Rel BS_Import "réalisé par" --> AC_War;
    Rel BS_Contact "réalisé par" --> AC_War;
    Rel AC_War "utilise" --> AI_UI;
    Rel AC_War "utilise" --> AC_Spring;
    Rel AC_War "publie" --> AC_BIRT;
    Rel AC_War "intègre" --> AC_Search;
    Rel AC_Search "expose" --> AI_Elastic;
    Rel AC_BIRT "expose" --> AI_BIRT;
    Rel N_Host "hoste" --> N_App;
    Rel N_Host "hoste" --> N_DB;
    Rel N_Host "hoste" --> N_PgAdmin;
    Rel N_App "déploie" --> Art_War;
    Rel N_DB "contient" --> Art_SQL;
    Rel N_App "déploie" --> Art_Docker;
    Rel N_App "se connecte à" --> N_DB;
    Rel N_PgAdmin "se connecte à" --> N_DB
```

*Cette vue globale montre les trois couches ArchiMate (Métier ↔ Application ↔ Technologie) et leurs relations de réalisation, d’utilisation et d’hébergement.*

---  

## 2️⃣ Couche Métier  

| **Élément** | **Description** | **ArchiMate** |
|--------------|----------------|---------------|
| **Business Actors** | • **MOA CGDD/DRI/AST4** (maîtrise d’ouvrage)  <br>• **MOE Klee Group / SSI** (maîtrise d’œuvre) <br>• **Agent public** (utilisateur final) <br>• **Comité de domaine** (expertise) | `BusinessActor` |
| **Business Roles** | • **Chef de Produit** <br>• **Développeur** <br>• **Administrateur Système** | `BusinessRole` |
| **Business Services** | • **Service Dossier** (création / suivi d’un dossier) <br>• **Service Qualification** (détermination du statut par le comité) <br>• **Service Extraction** (génération de rapports) <br>• **Service Import** (chargement de fichiers) <br>• **Service Contact** (affichage des coordonnées) | `BusinessService` |
| **Business Processes** | • **Gestion du dossier** (saisie → validation → archivage) <br>• **Qualification par comité** (évaluation → décision) <br>• **Extraction de rapports** (sélection → génération BIRT) <br>• **Import de fichiers** (upload → traitement) <br>• **Gestion du contact** (consultation des mails) | `BusinessProcess` |
| **Business Objects** | • **Dossier** (identifiant, métadonnées, pièces jointes) <br>• **Qualification** (statut, comité, date) <br>• **Rapport** (BIRT PDF/HTML) <br>• **Fichier import** (CSV, XML) <br>• **Agent** (identité, coordonnées) | `BusinessObject` |
| **Business Event** | • **Nouveau dossier créé** <br>• **Qualification demandée** <br>• **Extraction déclenchée** <br>• **Fichier importé** | `BusinessEvent` |
| **Product** | **SIREINES v2.5.20** – plateforme métier de recensement des experts | `Product` |
| **Contract** | **Déclaration CNIL n°1034232** (29/09/2014) | `Contract` |

### 2.1 Diagramme de la Vue Organisationnelle (Métier)

```mermaid
archimateDiagram;
    title Métier – Vue Organisationnelle;
    BusinessActor "MOA (CGDD/DRI/AST4)" as MOA;
    BusinessActor "MOE (Klee Group)" as MOE;
    BusinessActor "Agent public" as Agent;
    BusinessActor "Comité de domaine" as Comité;
    BusinessRole "Chef de produit" as ChefProd;
    BusinessRole "Développeur" as Dev;
    BusinessRole "Administrateur Système" as Ops;
    BusinessProcess "Gestion du dossier" as GP_Dossier;
    BusinessProcess "Qualification" as GP_Qualif;
    BusinessProcess "Extraction de rapports" as GP_Export;
    BusinessProcess "Import de fichiers" as GP_Import;
    BusinessProcess "Gestion du contact" as GP_Contact;
    BusinessService "Service Dossier" as BS_Dossier;
    BusinessService "Service Qualification" as BS_Qualif;
    BusinessService "Service Extraction" as BS_Export;
    BusinessService "Service Import" as BS_Import;
    BusinessService "Service Contact" as BS_Contact;
    MOA --> ChefProd;
    MOE --> Dev;
    Ops --> "Opérations infra" as OpsInfra;
    ChefProd --> GP_Dossier;
    ChefProd --> GP_Qualif;
    ChefProd --> GP_Export;
    ChefProd --> GP_Import;
    ChefProd --> GP_Contact;
    GP_Dossier --> BS_Dossier;
    GP_Qualif --> BS_Qualif;
    GP_Export --> BS_Export;
    GP_Import --> BS_Import;
    GP_Contact --> BS_Contact;
    Agent --> GP_Dossier;
    Agent --> GP_Contact;
    Comité --> GP_Qualif
```

---  

## 3️⃣ Couche Application  

### 3.1 Principaux **Application Components**

| Composant | Rôle | Implémentation |
|-----------|------|----------------|
| **sireines‑web (WAR)** | Point d’entrée web, orchestre les contrôleurs Struts2, expose les services métier | Java 8, Maven, Tomcat 7 |
| **BIRT Report Engine** | Génération de rapports (PDF/HTML) à partir des modèles *.rptdesign* | BIRT 4.3 (bundlé dans le WAR) |
| **Vertigo Search (Elasticsearch Embedded)** | Indexation et recherche plein‑texte sur les mots‑clés des dossiers | Plugin `ESEmbeddedSearchServicesPlugin` |
| **Spring IoC** | Injection de dépendances, configuration des beans | `applicationContext.xml` (vide – configuration via annotations) |
| **Struts2** | Framework MVC, gestion des actions, validation, tags UI | `struts.xml` (définit les namespaces) |
| **Talend Job** (import) | Job d’import de fichiers CSV/XLS, générateur de rapports Talend | Bibliothèques dans `sireines-talend/lib` |
| **Elasticsearch 7.x** (embedded) | Index et recherche de mots‑clés | Config `search/config/elasticsearch.yml` |
| **PostgreSQL 14‑alpine** | SGBD relationnel, stockage des tables métier | Scripts `sireines-database/script/*` |
| **pgAdmin4** | Console d’administration DB (facultatif) | Docker image `dpage/pgadmin4` |

### 3.2 **Application Services** (Java Interfaces)

| Service Interface | Description | Implémentation |
|-------------------|-------------|----------------|
| `AgentsServices` | Gestion CRUD des agents | `AgentsServicesImpl` |
| `DossiersServices` | CRUD + recherche dossiers, création index | `DossiersServicesImpl` |
| `ExtractionsServices` | Génération de rapports d’extraction | `ExtractionsServicesImpl` |
| `ImportsServices` | Traitement des fichiers d’import | `ImportsServicesImpl` |
| `ReferentielsServices` | Accès aux référentiels (mot‑cle, corps, etc.) | `ReferentielsServicesImpl` |
| `SeancesServices` | Gestion des séances de comité | `SeancesServicesImpl` |
| `CommonServices` | Envoi de mails, utilitaires | `CommonServicesImpl` |
| `BirtManager` | Publication de rapports BIRT | `BirtManagerImpl` |
| `SearchManager` (Vertigo) | Re‑indexation complète | `SearchManagerInitializer` (ComponentInitializer) |

### 3.3 **Application Interfaces (Ports)**  

| Interface | Technologie | Exemple |
|-----------|--------------|---------|
| **Struts2 UI** | HTTP / HTML + Freemarker (`*.ftl`) | `Accueil.do`, `DossierDetail.do` |
| **BIRT Templates** | `.rptdesign` (Talend) | `01_gestion_seances.rptdesign` |
| **REST / Elasticsearch** | HTTP GET/POST sur `/_search` | `search/config/elasticsearch.yml` |
| **SQL DDL** | PostgreSQL scripts | `crebas.sql`, `creuser.sql` |
| **Docker Compose** | YAML | `docker-compose.yml` |
| **JDBC** | JDBC URL `jdbc:postgresql://db:5432/postgres` | `application-config.xml` |

### 3.4 Diagramme d’Application (Vue de Réalisation)

```mermaid
archimateDiagram;
    title Application – Réalisation;
    ApplicationComponent "sireines‑web (WAR)" as AC_War;
    ApplicationComponent "BIRT Engine" as AC_BIRT;
    ApplicationComponent "Vertigo Search" as AC_Search;
    ApplicationComponent "Struts2 MVC" as AC_Struts;
    ApplicationComponent "Spring IoC" as AC_Spring;
    ApplicationComponent "Talend Import Job" as AC_Talend;
    ApplicationInterface "Struts2 UI" as AI_UI;
    ApplicationInterface "BIRT Templates" as AI_BIRT;
    ApplicationInterface "Elasticsearch API" as AI_ES;
    Rel AC_War "expose" --> AI_UI;
    Rel AC_War "publie" --> AI_BIRT;
    Rel AC_War "intègre" --> AC_Struts;
    Rel AC_War "utilise" --> AC_Spring;
    Rel AC_War "intègre" --> AC_Search;
    Rel AC_War "déclenche" --> AC_Talend;
    Rel AC_Search "expose" --> AI_ES;
    Rel AC_BIRT "expose" --> AI_BIRT
```

---  

## 4️⃣ Couche Technologie  

| Élément | Type ArchiMate | Détails |
|--------|----------------|--------|
| **Node** `Docker‑Host (ECO4 IaaS)` | `Node` | Serveur virtuel (VM) fourni par la plateforme IaaS (ECO4), OS Linux (Ubuntu 20.04). |
| **Container** `sireines‑app` | `Node` (type = Container) | Image `sireines‑app‑usine_image` (tomcat 7 + WAR). |
| **Container** `sireines‑db` | `Node` (type = Container) | Image `postgres:14.1‑alpine`. |
| **Container** `sireines‑pgadmin` | `Node` (type = Container) | Image `dpage/pgadmin4`. |
| **Artifact** `sireines‑web‑*.war` | `Artifact` | Build Maven (`sireines-web/pom.xml`). |
| **Artifact** `docker‑compose.yml` | `Artifact` | Orchestration Docker‑Compose. |
| **Artifact** `scripts SQL` | `Artifact` | DDL/DML (`sireines-database/script/*`). |
| **System Software** `Tomcat 7.0.108‑JDK8` | `SystemSoftware` | Conteneur d’exécution du WAR. |
| **System Software** `PostgreSQL 14` | `SystemSoftware` | SGBD. |
| **System Software** `Elasticsearch 7.x (embedded)` | `SystemSoftware` | Indexation. |
| **System Software** `BIRT 4.3` | `SystemSoftware` | Génération de rapports. |
| **Communication Network** `Docker Network sireines‑net` | `Network` | Bridge réseau interne (ports 8080, 5432, 8888). |
| **Technology Service** `Search Service` | `TechnologyService` | Exposé via API REST. |
| **Technology Service** `Report Generation Service` | `TechnologyService` | BIRT / PDF. |
| **Technology Interface** `HTTP/HTTPS` | `TechnologyInterface` | Port 8080 (Tomcat). |
| **Technology Interface** `JDBC` | `TechnologyInterface` | Port 5432 (PostgreSQL). |

### 4.1 Diagramme d’Infrastructure (Technologie)

```mermaid
archimateDiagram
    title Infrastructure – Docker/IaaS
    Node "Docker‑Host (ECO4 I