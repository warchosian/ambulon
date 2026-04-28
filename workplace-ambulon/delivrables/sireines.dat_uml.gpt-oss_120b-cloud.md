# 📘 Dossier d’Architecture Technique (DAT) – **SIREINES**  

> **Version du DAT** : 1.0 – 2024‑04‑27  
> **Auteur** : ChatGPT (expert UML ISO/IEC 19505)  

---  

## 1️⃣ Introduction architecturale  

| Élément | Description |
|---|---|
| **Objet** | Système d’information « SIREINES » – répertoire national des experts et spécialistes scientifiques et techniques, gestion des dossiers de qualification et des avis de comités de domaine. |
| **Périmètre** | Application web Java (Struts 2 / Spring / Vertigo), base de données PostgreSQL, génération de rapports BIRT, import/export Talend, déploiement Docker (Tomcat 7 + PostgreSQL 14). |
| **Documents sources** | `sireines.code.filtered.md`, `sireines.code.summarized.md`, `sireines.wiki.md`, `sireines.wikisi.md`, `pom.xml`… |
| **Vue d’ensemble des diagrammes** | 13 diagrammes UML : Class, Component, Deployment, Package, Composite Structure, Use‑Case, Activity, State‑Machine, Sequence, Communication, Interaction‑Overview, Timing, Object (exemple). |
| **Organisation du document** | <br>1️⃣ Introduction – 2️⃣ Vue structurelle – 3️⃣ Vue comportementale – 4️⃣ Vue d’interaction – 5️⃣ Traçabilité – 6️⃣ Profils & stéréotypes – 7️⃣ Contraintes OCL – 8️⃣ Patterns – 9️⃣ Décisions – 🔟 Normes de modélisation |

---  

## 2️⃣ Vue Structurelle  

### 2.1 Diagramme de **Classes** (`ClassDiagram`)  

```plantuml
@startuml ClassDiagram
'--- Stereotypes -------------------------------------------------
skinparam class {
    BackgroundColor<<entity>>    #F8F8F8
    BackgroundColor<<service>>    #E8F5E9
    BackgroundColor<<controller>>#E3F2FD
    BackgroundColor<<repository>>#FFF3E0
    BackgroundColor<<utility>>   #F3E5F5
    BorderColor<<entity>>        #607D8B
    BorderColor<<service>>        #4CAF50
    BorderColor<<controller>>     #2196F3
    BorderColor<<repository>>     #FF9800
    BorderColor<<utility>>        #9C27B0
}
'--- Entities ----------------------------------------------------
class Dossier <<entity>> {
    +Long dosId
    +String libelle
    +Date dateReception
    +String statut
    +Integer anneeQualification
    +String renouvlement
    +Qualification qualification
    +Agent responsable
}
class Agent <<entity>> {
    +Long agtId
    +String nom
    +String prenom
    +String email
    +String fonction
}
class Structure <<entity>> {
    +Long strId
    +String libelleCourt
    +String libelleLong
}
class Comite <<entity>> {
    +Long comId
    +String libelle
}
class Qualification <<entity>> {
    +Long quaId
    +String libelle
}
class MotCle <<entity>> {
    +Long mkId
    +String libelle
    +Integer niveau
}
class Rapporteur <<entity>> {
    +Long rapId
    +String nom
}
class Mail <<utility>> {
    +String to
    +String subject
    +String body
    +File attachment
    +send()
}
'--- Services ----------------------------------------------------
interface DossierService <<service>> {
    +List<Dossier> rechercher(Criteres c)
    +Dossier charger(Long id)
    +void sauvegarder(Dossier d)
    +void supprimer(Long id)
}
interface AgentService <<service>> {
    +List<Agent> lister()
    +Agent charger(Long id)
}
interface QualificationService <<service>> {
    +List<Qualification> lister()
}
interface MotCleService <<service>> {
    +List<MotCle> rechercher(String texte)
}
interface ExportService <<service>> {
    +File exporter(List<Dossier> dossiers, String format)
}
'--- Repositories ------------------------------------------------
interface DossierRepository <<repository>> {
    +List<Dossier> find(Criteres c)
    +Dossier findById(Long id)
    +void save(Dossier d)
    +void delete(Long id)
}
interface AgentRepository <<repository>> { … }
interface QualificationRepository <<repository>> { … }
interface MotCleRepository <<repository>> { … }

'--- Controllers ------------------------------------------------
class DossierController <<controller>> {
    -DossierService ds
    +String liste()
    +String detail()
    +String edit()
}
class AgentController <<controller>> { … }
class ExtractionController <<controller>> { … }

'--- Relations ---------------------------------------------------
Dossier "1" --> "1" Agent : responsable
Dossier "1" --> "1" Qualification : qualification
Dossier "1" --> "0..*" MotCle : motsClés
Agent "1" --> "0..*" Structure : appartientÀ
Comite "1" --> "0..*" Qualification : évalue
Qualification "1" --> "0..*" Rapporteur : attribuéÀ
DossierController --> DossierService
AgentController --> AgentService
ExtractionController --> ExportService
DossierService --> DossierRepository
AgentService --> AgentRepository
QualificationService --> QualificationRepository
MotCleService --> MotCleRepository
ExportService --> Mail

@enduml
```

**Légende**  

| Stéréotype | Signification |
|---|---|
| `<<entity>>` | Table métier persistant (DTO/Entity) |
| `<<service>>` | Business‑logic (Spring `@Service`) |
| `<<controller>>` | Struts 2 Action / Spring MVC Controller |
| `<<repository>>` | DAO (Vertigo/Dynamo) |
| `<<utility>>` | Classe utilitaire (ex. `Mail`) |

### 2.2 Diagramme de **Composants** (`ComponentDiagram`)  

```plantuml
@startuml ComponentDiagram
'--- Packages ----------------------------------------------------
package "sireines-web" <<Component>> {
    [DossierController] as DC
    [AgentController]   as AC
    [ExtractionController] as EC
    [BirtManager]      as BM
    [SearchManager]     as SM
}
package "sireines-service" <<Component>> {
    [DossierService] as DS
    [AgentService]   as AS
    [QualificationService] as QS
    [MotCleService]  as MS
    [ExportService]  as ES
}
package "sireines-repository" <<Component>> {
    [DossierRepository] as DR
    [AgentRepository]   as AR
    [QualificationRepository] as QR
    [MotCleRepository]  as MR
}
package "sireines-database" <<Component>> {
    [PostgreSQL] as PG
}
package "sireines-docker" <<Component>> {
    [Tomcat] as TC
    [Docker‑Compose] as DCMP
}
'--- Interfaces -------------------------------------------------
interface "I_DossierService" as I_DS
interface "I_AgentService"   as I_AS
interface "I_ExportService" as I_ES

'--- Relations -------------------------------------------------
DC ..> I_DS : uses
AC ..> I_AS : uses
EC ..> I_ES : uses
DS ..> DR : uses
AS ..> AR : uses
QS ..> QR : uses
MS ..> MR : uses
DR ..> PG : reads/writes
AR ..> PG : reads/writes
QR ..> PG : reads/writes
MR ..> PG : reads/writes
TC ..> DC : hosts
DCMP ..> TC : compose
DCMP ..> PG : compose
@enduml
```

**Légende**  

| Élément | Description |
|---|---|
| `sireines-web` | Application web (Struts 2 / Spring) |
| `sireines-service` | Couche métier |
| `sireines-repository` | Accès persistant (Vertigo) |
| `sireines-database` | PostgreSQL 14 (Docker) |
| `sireines-docker` | Conteneurs Tomcat 7 & PostgreSQL, orchestrés par `docker‑compose.yml` |

### 2.3 Diagramme de **Déploiement** (`DeploymentDiagram`)  

```plantuml
@startuml DeploymentDiagram
'--- Nodes -------------------------------------------------------
node "Bastion (SSH)" as BASTION {
    artifact "ssh‑key" as SSHKEY
}
node "Serveur Recette (Docker‑Host)" as HOST {
    artifact "docker‑compose.yml"
    node "Container: sireines‑app" as APP {
        component "Tomcat 7 (sireines‑web.war)" as TOMCAT
        artifact "sireines‑web‑*.war"
        artifact "log4j.xml"
    }
    node "Container: sireines‑db" as DB {
        component "PostgreSQL 14 (alpine)" as POSTGRES
        artifact "postgres-data (volume)"
    }
    node "Container: pgadmin" as PGADMIN {
        component "pgAdmin 4"
        artifact "pgadmin‑data (volume)"
    }
}
'--- Communication ------------------------------------------------
BASTION --> HOST : SSH (port 22)
HOST --> APP   : docker‑run (port 8080)
HOST --> DB    : docker‑run (port 5432)
APP  --> DB    : JDBC (postgresql://db:5432/sireines)
APP  --> PGADMIN : HTTP (port 8888)  « admin »
PGADMIN --> DB : JDBC (port 5432)

'--- Physical layout
cloud "Internet" {
    [User Browser] as BROWSER
}
BROWSER --> APP : HTTP/HTTPS (URL https://sireines.recette…/Accueil.do)

@enduml
```

**Légende**  

| Symbole | Signification |
|---|---|
| `node` | Machine physique ou conteneur Docker |
| `artifact` | Fichier déployable (WAR, volume) |
| `component` | Processus ou service exécuté dans le conteneur |
| `cloud` | Internet / navigateur client |

### 2.4 Diagramme de **Paquets** (`PackageDiagram`)  

```plantuml
@startuml PackageDiagram
package "i2.application.sireines" {
    package controller {
        class AccueilAction
        class DossierController
        class AgentController
        class ExtractionController
    }
    package service {
        class DossierService
        class AgentService
        class ExportService
    }
    package domain {
        class Dossier
        class Agent
        class Structure
        class Qualification
        class MotCle
    }
    package repository {
        interface DossierRepository
        interface AgentRepository
    }
}
package "i2.application.sireines.boot" {
    class ApplicationServletContextListener
    class SearchManagerInitializer
}
package "i2.application.sireines.util" {
    class Mail
    class CsvExport
}
@enduml
```

### 2.5 Diagramme **Composite Structure** (optionnel) – Vue du *DossierController*  

```plantuml
@startuml CompositeStructure
skinparam componentStyle rectangle
component "DossierController" as DC <<controller>> {
    port "servicePort" as SP
}
component "DossierService" as DS <<service>> {
    port "repoPort" as RP
}
component "DossierRepository" as DR <<repository>>
DC --> SP : uses
SP --> RP : delegates
RP --> DR : CRUD
@enduml
```

---  

## 3️⃣ Vue Comportementale  

### 3.1 Diagramme de **Cas d’utilisation** (`UseCaseDiagram`)  

```plantuml
@startuml UseCaseDiagram
left to right direction
actor "Agent" as A
actor "Comité de domaine" as C
actor "Administrateur" as Admin

rectangle SIREINES {
    usecase "Consulter dossiers" as UC1
    usecase "Créer / Modifier dossier" as UC2
    usecase "Lancer extraction" as UC3
    usecase "Générer rapport BIRT" as UC4
    usecase "Gérer utilisateurs" as UC5
    usecase "Administrer BDD" as UC6
}
A --> UC1
A --> UC2
C --> UC3
C --> UC4
Admin --> UC5
Admin --> UC6

UC2 .up.> UC1 : <<include>>
UC3 .up.> UC1 : <<extend>>
@enduml
```

### 3.2 Diagramme d’**Activité** (`ActivityDiagram`) – *Flux de création d’un dossier*  

```plantuml
@startuml ActivityDiagram
start
:Authentifier l’agent;
if (Autorisé ?) then (oui)
  :Afficher formulaire “Nouveau Dossier”;
  :Saisir données (Agent, Structure, Mot‑Clé…);
  if (Validation) then (ok)
    :Appeler DossierService.sauvegarder();
    :Indexer le dossier (SearchManager);
    :Envoyer mail de confirmation;
    :Rediriger vers “Détail Dossier”;
  else (erreur)
    :Afficher messages d’erreur;
  endif
else (non)
  :Afficher accès refusé;
endif
stop
@enduml
```

### 3.3 Diagramme d’**État** (`StateMachineDiagram`) – *Cycle de vie d’un **Dossier***  

```plantuml
@startuml StateMachineDiagram
[*] --> Brouillon

Brouillon : saisie initiale
Brouillon --> EnCours : soumission
EnCours : en cours d'évaluation
EnCours --> Validé : décision + « qualifié »
EnCours --> Rejeté : décision + « non‑qualifié »

Validé --> Archivé : fin de cycle (≥4 ans)
Rejeté --> Archivé : fin de cycle (≥4 ans)

Archived --> [*]
@enduml
```

---  

## 4️⃣ Vue d’Interaction  

### 4.1 Diagramme de **Séquence** – *Recherche d’un dossier*  

```plantuml
@startuml SequenceDiagram
actor "Agent" as A
participant "DossierController" as DC
participant "DossierService" as DS
participant "DossierRepository" as DR
participant "PostgreSQL" as DB

A -> DC : GET /dossiers?motCle=...
DC -> DS : rechercher(Critères)
DS -> DR : find(Critères)
DR -> DB : SELECT … FROM dossier WHERE …
DB --> DR : ResultSet
DR --> DS : List<Dossier>
DS --> DC : List<Dossier>
DC --> A : page HTML (liste)

@enduml
```

### 4.2 Diagramme de **Communication** – *Export BIRT*  

```plantuml
@startuml CommunicationDiagram
object "ExtractionController" as EC
object "ExportService" as ES
object "BirtManager" as BM
object "PostgreSQL" as DB

EC -> ES : exporter(dossiers, "PDF")
ES -> BM : generateReport(template, data)
BM -> DB : SELECT … (données rapport)
BM --> ES : File (PDF)
ES --> EC : File (PDF)
@enduml
```

### 4.3 Diagramme d’**Overview d’Interaction** (optionnel) – *Scénario de livraison Docker*  

```plantuml
@startuml InteractionOverview
start
:Se connecter au bastion;
:git pull + docker‑compose.yml;
partition "Docker Host" {
    :docker compose down;
    :docker compose pull;
    :docker compose up -d;
}
:Vérifier http://…/Accueil.do;
stop
@enduml
```

### 4.4 Diagramme de **Timing** (optionnel) – *Délai de mise à jour de l’index*  

```plantuml
@startuml TimingDiagram
title Indexation du dossier après sauvegarde
entity "Sauvegarde" as S
entity "Indexation" as I
S  -> I : 0..1s
I  -> I : 0..2s
@enduml
```

---  

## 5️⃣ Matrice de traçabilité UML  

| Élément | Class Diagram | Component Diagram | Deployment Diagram | Use‑Case | Activity | State‑Machine | Sequence |
|---|---|---|---|---|---|---|---|
| **Dossier** | ✔ | ✔ (DossierRepository) | ✔ (DB) | UC1