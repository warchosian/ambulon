# 📘 Dossier d’Architecture Technique (DAT) – **SIREINES**  

> **Projet** : SIREINES – Répertoire national des experts et spécialistes scientifiques et techniques  
> **Version du DAT** : 1.0 – 2024‑04‑27  
> **Auteur** : ChatGPT (OpenAI) – basé sur les livrables fournis (code source, scripts, documentation, wiki)  
> **Références** :  
> * `sireines.code.filtered.md` – arborescence du dépôt GitLab  
> * `sireines.code.summarized.md` – résumé du dépôt  
> * `sireines.wiki.md` – procédures de déploiement, recettes, organisation, versionnage  
> * `sireines.wikisi.md` – description métier et gouvernance  
> * Spécifications ArchiMate 3.2 – The Open Group  
> * ISO/IEC/IEEE 42010 :2022 – Cadre d’architecture d’entreprise  

---  

## 1️⃣ Vue d’ensemble ArchiMate  

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/ArchiMate-PlantUML/master/Archimate.puml

'=== Business Layer ===
BusinessActor(moa, "MOA (CGDD‑DRI‑AST4)", "Maître d’Ouvrage – pilotage fonctionnel") 
BusinessActor(moe, "MOE (Klee Group / prestataire)", "Maître d’Œuvre – développement & exploitation")
BusinessActor(utilisateur, "Utilisateurs finaux (agents, experts)", "Saisie, consultation, suivi des dossiers")

BusinessProcess(gp, "Gestion du processus qualification") 
BusinessFunction(bfCollecte, "Collecte des dossiers")
BusinessFunction(bfEvaluation, "Évaluation par les comités")
BusinessFunction(bfStatistiques, "Statistiques & reporting BIRT")
BusinessService(bsDossiers, "Gestion des dossiers de qualification")
BusinessService(bsExports, "Exportations (CSV, BIRT)")
BusinessService(bsImports, "Import de fichiers (Talend)")

'=== Application Layer ===
ApplicationComponent(appWeb, "sireines‑web", "Application Java/J2EE – Struts2/Tomcat")
ApplicationComponent(appDB, "sireines‑database", "PostgreSQL – schéma métier")
ApplicationComponent(appSearch, "SearchManager (Elasticsearch)", "Recherche plein‑texte")
ApplicationComponent(appTalend, "Talend jobs", "Import & génération de rapports")
ApplicationComponent(appBIRT, "BIRT Engine", "Reporting")

ApplicationService(asWeb, "Service Web", "REST/Struts actions")
ApplicationService(asSearch, "Service Recherche", "API Vertigo Search")
ApplicationService(asImport, "Service Import", "Job Talend")
ApplicationService(asReport, "Service Reporting", "BIRT")

'=== Technology Layer ===
Node(dockerHost, "Docker Host (Linux/WSL2)")
Node(tomcat, "Tomcat 7.0.108‑JDK8", "Container")
Node(postgres, "PostgreSQL 14‑alpine", "Container")
Node(es, "Elasticsearch (embedded)", "Container")
Node(pgadmin, "pgAdmin4", "Container")
Artifact(war, "sireines‑web‑*.war")
Artifact(sqlScripts, "Scripts SQL (install/alter/update)")

'=== Relationships ===
' Business → Application
utilisateur --> bsDossiers : "Utilise"
bsDossiers --> asWeb : "Réalisé par"
bsExports --> asReport : "Réalisé par"
bsImports --> asImport : "Réalisé par"

' Application → Technology
asWeb --> tomcat : "Déployé sur"
asWeb --> war : "Déploie"
asReport --> war : "Utilise"
asImport --> sqlScripts : "Accède"
asSearch --> es : "Utilise"
appDB --> postgres : "Déployé sur"
appDB --> sqlScripts : "Initialise"

' Technology connections
tomcat --> dockerHost : "Exécuté sur"
postgres --> dockerHost : "Exécuté sur"
es --> dockerHost : "Exécuté sur"
pgadmin --> dockerHost : "Exécuté sur"

' Cross‑layer (realisation) links
bsDossiers -[#Realization]-> asWeb
bsExports  -[#Realization]-> asReport
bsImports  -[#Realization]-> asImport
asWeb -[#Realization]-> tomcat
appDB -[#Realization]-> postgres
asSearch -[#Realization]-> es

@enduml
```  

*Ce diagramme donne une vue « Layered » (Business → Application → Technology) : les services métier sont réalisés par les services applicatifs qui eux‑mêmes sont déployés sur les composants technologiques.*  

---  

## 2️⃣ Couche **Métier** (Business Layer)  

### 2.1 Acteurs & Rôles  

| Élément | Type | Description |
|---|---|---|
| **MOA (CGDD‑DRI‑AST4)** | Business Actor | Pilotage fonctionnel, exigences métier, validation des livrables. |
| **MOE (Klee Group / prestataire)** | Business Actor | Conception, développement, tests, mise en production. |
| **Utilisateurs finaux** | Business Actor | Agents, experts, services RH qui saisissent et consultent les dossiers. |
| **Comité de domaine** | Business Role | Décideurs de la qualification, membres des commissions. |

### 2‑2 Services métier  

| Service | Description | Processus associés |
|---|---|---|
| **Gestion des dossiers** (`bsDossiers`) | Création, mise à jour, suivi, recherche des dossiers de qualification. | `Collecte des dossiers → Evaluation → Validation → Suivi`. |
| **Exportations** (`bsExports`) | Génération de fichiers CSV, PDF, rapports BIRT (pyramide d’âge, fréquence mots‑clés, etc.). | Export “Etat complet”, “Pyramide des âges”, “Fréquence mots‑clés”. |
| **Import de fichiers** (`bsImports`) | Chargement de jeux de données externes (via Talend) – ex : import de fichiers CSV. | `ImportFichier → Validation → Enrichissement`. |
| **Statistiques & Reporting** (`bsStatistiques`) | Tableaux de bord, indicateurs de suivi (nombre dossiers, taux de qualification). | `Statistiques BIRT`. |

### 2‑3 Processus métier (extraits)  

| Processus | Description | Événements déclencheurs |
|---|---|---|
| **Collecte d’un dossier** | L’agent crée un nouveau dossier via le formulaire `DossierDetail`. | Action `CréerDossier`. |
| **Évaluation par le comité** | Le comité consulte le dossier, saisit la décision, le système calcule le résultat. | Action `LancerEvaluation`. |
| **Exportation d’un rapport** | L’administrateur déclenche l’export d’un rapport BIRT. | Action `ExporterRapport`. |
| **Import d’un fichier** | Un opérateur lance le job Talend `ImportFichier`. | Action `ImportFichier`. |
| **Recherche plein‑texte** | L’utilisateur utilise le champ de recherche libre (Elasticsearch). | Action `Rechercher`. |

### 2‑4 Objets métier  

| Objet | Type | Description |
|---|---|---|
| **Dossier** | Business Object | Enregistrement central contenant les champs : `dos_id`, `agent_id`, `com_id`, `qual_status`, etc. |
| **Comité** | Business Object | Liste des membres, règles de décision. |
| **Rapport BIRT** | Business Object | Fichier PDF/HTML généré à partir des modèles `*.rptdesign`. |
| **Fichier d’import** | Business Object | CSV, XML, etc. importés par Talend. |

---  

## 3️⃣ Couche **Application** (Application Layer)  

### 3.1 Composants applicatifs  

| Composant | Type | Description | Artifacts |
|---|---|---|---|
| **sireines‑web** | Application Component | Application Java/J2EE (Struts2, Spring, Vertigo) – expose les actions Struts (`AccueilAction`, `DossierDetailAction`, …). | `sireines‑web‑*.war` |
| **sireines‑database** | Application Component | Scripts SQL (install, alter, update) + modèle PowerDesigner (`Sireines.oom`). | `*.sql`, `Sireines.oom` |
| **SearchManager** | Application Component | Vertigo Search – indexation ElasticSearch des dossiers (ex : `DossierMotsClefsSearchLoader`). | `SearchManagerInitializer.java` |
| **Talend jobs** | Application Component | Jobs d’import (`ImportFichier`, `ImportSynthese`) + génération de rapports. | `*.jar` (ex : `importfichiersirene_0_1.jar`) |
| **BIRT Engine** | Application Component | Moteur de rendu de rapports (`*.rptdesign`). | `BIRT` libs |
| **Docker‑compose** | Application Component | Orchestration des conteneurs (`docker-compose.yml`). | `docker-compose.yml` |

### 3.2 Services applicatifs  

| Service | Réalise | Implémentation |
|---|---|---|
| **Service Web** (`asWeb`) | `Business Service bsDossiers` | Struts 2 actions (`DossierDetailAction`, `Extraction01Action`, …). |
| **Service Recherche** (`asSearch`) | Indexation et recherche plein‑texte | `SearchManagerInitializer` + `ESEmbeddedSearchServicesPlugin`. |
| **Service Import** (`asImport`) | Traitement des fichiers d’import | Talend job `ImportFichier`. |
| **Service Reporting** (`asReport`) | Génération de rapports BIRT | `BirtManagerImpl`, modèles `.rptdesign`. |
| **Service Notification** (`asMail`) | Envoi de courriels (ex : notifications d’état) | `CommonServices.sendMail`. |

### 3.3 Fonctions & Interactions  

| Fonction | Description | Interaction |
|---|---|---|
| **`PersistenceManagerInitializer`** | Initialise le moteur JPA/Hibernate au démarrage. | `ApplicationServletContextListener` → `EntityManagerFactory`. |
| **`SearchManagerInitializer`** | Re‑indexe tous les dossiers au démarrage. | `SearchManager.reindexAll(...)`. |
| **`BirtManager.publish`** | Fusionne un modèle BIRT avec des données et renvoie un `VFile`. | `BirtManagerImpl` → `BIRT Engine`. |
| **`CommonServices.sendMail`** | Envoi de mails avec pièces jointes. | `JavaMailSender`. |
| **`DossierMotsClefsSearchLoader`** | Charge les mots‑clés associés à chaque dossier dans l’index ElasticSearch. | `SearchManager`. |

---  

## 4️⃣ Couche **Technologie** (Technology Layer)  

### 4.1 Infrastructure  

| Élément | Type | Description |
|---|---|---|
| **Docker Host** (`dockerHost`) | Node | Machine Linux (WSL2 sous Windows ou serveur IaaS ECO4). |
| **Tomcat Container** (`tomcat`) | Node | `tomcat:7.0.108‑jre8` – déploie le WAR `sireines‑web`. |
| **PostgreSQL Container** (`postgres`) | Node | Image `postgres:14.1‑alpine` – base de données relationnelle. |
| **Elasticsearch Container** (`es`) | Node | Embedded ES (via Vertigo) – indexation texte. |
| **pgAdmin Container** (`pgadmin`) | Node | UI d’administration PostgreSQL (port 8888). |
| **Volumes Docker** | Artifact | `sireines_db_sireines_vol` (BDD) & `sireines_pgadmin_sireines_vol` (config pgAdmin). |
| **Network** | Communication‑Network | Bridge network `sireines_net` (défini dans `docker‑compose.yml`). |

### 4.2 Services technologiques  

| Service | Réalise | Implémentation |
|---|---|---|
| **`Tomcat`** | Hébergement du WAR Java | `Dockerfile` copie `ROOT.war` → `/usr/local/tomcat/webapps/ROOT`. |
| **`PostgreSQL`** | Persistance des entités métier | Scripts SQL (`crebas.sql`, `alter_*.sql`, …). |
| **`Elasticsearch`** | Recherche plein‑texte | Config `elasticsearch.yml` (analyseur `code`, `text_fr`). |
| **`pgAdmin`** | Administration BDD | Port `8888`, volume persistant. |
| **`Docker‑Compose`** | Orchestration des conteneurs | `docker-compose up -d`. |
| **`BIRT Engine`** | Génération de rapports PDF/HTML | Déployé dans le conteneur `tomcat` via le WAR. |

### 4.3 Artifacts  

| Artifact | Description |
|---|---|
| `sireines‑web‑*.war` | Package déployable (Struts2, Vertigo, BIRT). |
| `docker-compose.yml` | Définition des services, volumes, réseaux. |
| `Dockerfile` | Construction de l’image Tomcat avec le WAR. |
| `*.sql` (install/alter/update) | Scripts de création, migration et nettoyage de la BDD. |
| `*.rptdesign` | Modèles de rapports BIRT. |
| `importfichiersirene_0_1.jar` | Bibliothèque Talend d’import. |
| `application‑config.xml`, `sireines‑auth‑config.xml` | Configuration Spring & sécurité. |

---  

## 5️⃣ Couche **Stratégique** (optional)  

| Élément | Type | Description |
|---|---|---|
| **Capability “Gestion du répertoire d’experts”** | Capability | Permet de recenser, qualifier et suivre les experts. |
| **Value Stream “Qualification des dossiers”** | Value‑Stream | Capture les étapes de la demande → évaluation → décision → archivage. |
| **Goal “Conformité RGPD”** | Goal | Respecter la déclaration CNIL (29/09/2014 n°1034232). |
| **Driver “Amélioration de la traçabilité”** | Driver | Besoin de suivi des dossiers et d’audit. |
| **Requirement “Export CSV”** | Requirement | Exporter les dossiers au format CSV (extraction01‑10). |
| **Constraint “Environnement de production IaaS”** | Constraint | Déploiement uniquement sur la plateforme ECO4 (Paris‑La Défense). |

---  

## 6️⃣ Couche **Mise en Œuvre & Migration** (optional)  

| Plateau | Description | Gap |
|---|---|---|
| **Baseline v2.5.6** | Version actuelle en recette (15/09/2024). | - |
| **Target v2.5.20** | Version en production (12/03/2024). | Migration des scripts `alter_*` et mise à jour du WAR. |
| **Work Package WP‑DB‑MIG** | Exécuter `alter_0.7.sql`, `alter_0.8.sql`, `alter_post_init.sql` sur le volume DB. | Aucun impact fonctionnel. |
| **Work Package WP‑APP‑DEPLOY** | Re‑build du WAR, mise à jour du `docker‑compose.yml` (image tag). | Redémarrage du conteneur `sireines_app_usine_container`. |
| **Work Package WP‑REPORT‑BIRT** | Déployer les nouveaux modèles BIRT (`*.rptdesign`). | Validation visuelle des rapports. |

---  

## 7️⃣ Aspects **Transverses** (Cross‑layer Relationships)  

| Relation | Source (Business) | Target (Application) | Target (Technology) | Commentaire |
|---|---|---|---|---|
| **Realisation** | `bsDossiers` | `asWeb` | `tomcat` | Le service métier « Gestion des dossiers » est réalisé par le service web déployé sur Tomcat. |
| **Realisation** | `bsExports` | `asReport` | `BIRT Engine` | Exportations BIRT réalisées via le moteur BIRT. |
| **Realisation** | `bsImports` | `asImport` | `Talend` | Import de fichiers exécuté par les jobs Talend. |
| **Serving** | `asSearch` | `es` | – | Le service de recherche utilise Elasticsearch. |
| **Assignment** | `Dossier` (Business Object) | `appDB` (Application Component) | `postgres` (Technology Node) | Le modèle de données est assigné à la base PostgreSQL. |
| **Access** | `asWeb` → `Dossier` | `asWeb` → `postgres` | `asWeb` lit/écrit les objets métier dans la BDD. |
| **Influence** | `Goal “Conformité RGPD