# Dossier d’Architecture Technique (DAT) – **agile‑infra**  
*Version 1.0 – 27 avril 2026*  

---  

## 1. Vue d’ensemble ArchiMate  

| Élément | Description |
|--------|-------------|
| **Framework** | ArchiMate 3.2 (The Open Group) – utilisation des *layers* **Business**, **Application**, **Technology** et des *cross‑layer relationships* (realisation, serving, assignment, access, influence). |
| **Préoccupations du projet** | - Fournir un **service de déploiement automatisé** (recette) pour les environnements de test. <br> - Garantir la traçabilité du *pipeline* CI/CD jusqu’à l’infrastructure d’exécution. |
| **Couverture** | - **Business** : acteurs, rôles, services, processus de déploiement. <br> - **Application** : CI‑pipeline (GitLab CI), moteur Ansible, outil *pasta‑cooker*, template Docker‑Compose. <br> - **Technology** : nœuds d’exécution Docker, registre d’images, réseau HTTP, OS Linux. |
| **Modèle de référence** | Le modèle **Layered Viewpoint** (Business → Application → Technology) est enrichi par les vues **Cooperation**, **Realisation** et **Migration**. |

---  

## 2. Couche Métier (Business Layer)

### 2.1 Acteurs & Rôles

| ArchiMate Element | Nom | Rôle / Responsabilité |
|-------------------|-----|-----------------------|
| **Business Actor** | **DevOps Team** | Responsable du maintien du pipeline et du déploiement. |
| **Business Actor** | **Client (équipe produit)** | Consomme le *service de déploiement* (recette) pour valider les livrables. |
| **Business Role** | **CI/CD Operator** | Exécute les pipelines, surveille les environnements. |
| **Business Role** | **Deployment Engineer** | Conçoit les playbooks Ansible, assure la conformité des secrets. |
| **Business Collaboration** | **Deployment Collaboration** | Interaction entre *CI/CD Operator* et *Deployment Engineer* pour livrer le service. |
| **Business Interface** | **Recette API** | Point d’accès (GitLab CI) exposé aux *clients* via l’environnement *recette*. |

### 2.2 Services Métier

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Business Service** | **Déploiement Recette** | Service de mise à jour d’un environnement de test (docker‑compose). |
| **Business Service** | **Gestion des Secrets** | Service de récupération et de déchiffrement des secrets (via `secrets.yml`). |
| **Business Process** | **Run Recette** | Processus déclenché par modification du répertoire `recette/`. |
| **Business Process** | **Pré‑préparation du Playbook** | Chargement des variables, génération du `docker‑compose.yml`. |
| **Business Function** | **Orchestration Conteneurs** | Fonctionnalité métier qui lance `docker compose up`. |
| **Business Interaction** | **Notification Déploiement** | Interaction entre le playbook et le handler qui démarre les conteneurs. |

### 2.3 Objets & Événements Métier

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Business Object** | **Docker‑Compose File** | Artefact généré (`docker-compose.yml`). |
| **Business Object** | **Secrets Bundle** | Données sensibles importées depuis `vars/secrets.yml`. |
| **Business Event** | **Modification Recette** | Trigger GitLab CI lorsqu’un changement apparaît dans `recette/**`. |
| **Product** | **Environnement Recette** | Environnement de test mis à disposition du client. |
| **Contract** | **Accord de Déploiement** | Contrat implicite entre *DevOps* et *Client* (déploiement à jour). |

### 2.4 Diagramme Organisationnel (Business View)

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master
!include Archimate

' Actors & roles
actor "DevOps Team" as DevOps <<Business Actor>>
actor "Client (Produit)" as Client <<Business Actor>>
role "CI/CD Operator" as Operator <<Business Role>>
role "Deployment Engineer" as Engineer <<Business Role>>

' Collaboration
collaboration "Deployment Collaboration" as Collab <<Business Collaboration>>

' Interfaces & services
interface "Recette API" as RecAPI <<Business Interface>>
service "Déploiement Recette" as DeployRec <<Business Service>>
service "Gestion des Secrets" as SecretsSrv <<Business Service>>

' Relationships
DevOps --> Operator : joue le rôle
DevOps --> Engineer : joue le rôle
Client --> RecAPI : utilise
Operator --> RecAPI : sert
Engineer --> RecAPI : sert
Collab --> Operator : collabore
Collab --> Engineer : collabore
RecAPI --> DeployRec : réalise
RecAPI --> SecretsSrv : réalise
@enduml
```

---  

## 3. Couche Application (Application Layer)

### 3.1 Composants applicatifs

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Application Component** | **GitLab CI Runner** | Exécute le job `run_recette`. |
| **Application Component** | **Pasta‑Cooker Client** | Image Docker `pasta-cooker-client:v1.0.6` – exécute la commande `pasta‑cooker`. |
| **Application Component** | **Ansible Engine** | Interpréteur du playbook `recette/main.yml`. |
| **Application Component** | **Docker‑Compose** | Outil CLI utilisé par le handler pour lancer les conteneurs. |
| **Application Collaboration** | **CI‑Ansible Collaboration** | Interaction entre *GitLab CI Runner* et *Ansible Engine*. |
| **Application Interface** | **CI Job Interface** | Point d’entrée du job (`script:`). |
| **Application Interface** | **Ansible Playbook Interface** | Point d’entrée du playbook (`hosts`, `tasks`). |
| **Application Service** | **Pipeline Service** | Service CI qui orchestre le flux `run_recette`. |
| **Application Service** | **Configuration Management Service** | Service fourni par Ansible (templates, vars). |
| **Application Service** | **Container Orchestration Service** | Service exposé par Docker‑Compose (up/down). |

### 3.2 Fonctions & Interactions applicatives

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Application Function** | **Render Docker‑Compose** | Génération du fichier `docker‑compose.yml` via le template Jinja2. |
| **Application Function** | **Load Secrets & Versions** | Chargement des variables `secrets.yml` et `versions.yml`. |
| **Application Interaction** | **Notify Handler** | Notification (`notify:`) vers le handler qui lance `docker compose up`. |
| **Application Process** | **Run Recette Process** | Processus complet du job CI (pré‑préparation → exécution → notification). |

### 3.3 Données applicatives

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Data Object** | **Playbook Variables** | Données provenant de `vars/*.yml`. |
| **Data Object** | **Docker‑Compose Template** | Fichier Jinja2 `docker-compose.yml.j2`. |
| **Data Object** | **Generated Docker‑Compose** | Artefact produit par la fonction *Render Docker‑Compose*. |

### 3.4 Diagramme Vue Applicative

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master
!include Archimate

' Components
applicationComponent "GitLab CI Runner" as GitLabCI <<Application Component>>
applicationComponent "Pasta‑Cooker Client" as Pasta <<Application Component>>
applicationComponent "Ansible Engine" as Ansible <<Application Component>>
applicationComponent "Docker‑Compose" as DockerCompose <<Application Component>>

' Services
applicationService "Pipeline Service" as PipeSrv <<Application Service>>
applicationService "Configuration Management Service" as ConfigSrv <<Application Service>>
applicationService "Container Orchestration Service" as ContSrv <<Application Service>>

' Interfaces
applicationInterface "CI Job Interface" as CIJob <<Application Interface>>
applicationInterface "Ansible Playbook Interface" as AnsiInt <<Application Interface>>

' Data Objects
dataObject "Docker‑Compose Template" as Template <<Data Object>>
dataObject "Generated Docker‑Compose" as GenDocker <<Data Object>>
dataObject "Playbook Variables" as Vars <<Data Object>>

' Relationships
GitLabCI -[#realization]-> PipeSrv
PipeSrv -[#serving]-> CIJob
CIJob -[#realization]-> Pasta
Pasta -[#serving]-> ContSrv
Ansible -[#realization]-> ConfigSrv
ConfigSrv -[#serving]-> AnsiInt
Ansible --> Template : utilise
Ansible --> Vars : charge
Ansible --> GenDocker : crée
GenDocker --> DockerCompose : déploie
DockerCompose -[#realization]-> ContSrv
@enduml
```

---  

## 4. Couche Technologie (Technology Layer)

### 4.1 Infrastructure

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Node** | **GitLab Runner VM** | Machine virtuelle hébergeant le Docker container du Runner. |
| **Node** | **Execution Container** | Container Docker `pasta‑cooker-client:v1.0.6`. |
| **Device** | **Linux Host** | OS sous‑jacent (Ubuntu 22.04 LTS). |
| **System Software** | **Docker Engine** | Runtime qui exécute les conteneurs Docker. |
| **System Software** | **Docker‑Compose** | Orchestrateur de services multi‑container. |
| **Technology Collaboration** | **Docker Swarm Cluster** *(optionnel)* | Groupe de nœuds pour haute disponibilité. |
| **Communication Network** | **HTTP / WebSocket** | Protocole utilisé par `pasta‑cooker` pour parler au CD URL. |
| **Technology Service** | **Container Runtime Service** | Service d’exécution de conteneurs (Docker). |
| **Technology Service** | **Network Service** | Service réseau (HTTP). |
| **Artifact** | **Docker Image – pasta‑cooker-client** | Artefact stocké dans le registre `europe‑west9‑docker.pkg.dev/...`. |
| **Artifact** | **docker‑compose.yml** | Fichier généré et déployé sur le nœud cible. |

### 4.2 Diagramme Vue Infrastructure

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master
!include Archimate

node "GitLab Runner VM" as RunnerVM <<Node>>
node "Execution Container" as ExecCont <<Node>>
device "Linux Host" as Linux <<Device>>
systemSoftware "Docker Engine" as DockerEng <<System Software>>
systemSoftware "Docker‑Compose" as DockerComp <<System Software>>
technologyService "Container Runtime Service" as ContRT <<Technology Service>>
technologyService "Network Service (HTTP)" as NetSrv <<Technology Service>>
artifact "pasta‑cooker-client Image" as Image <<Artifact>>
artifact "docker‑compose.yml" as CompFile <<Artifact>>
communicationNetwork "HTTP Network" as HTTPNet <<Communication Network>>

' Placement
RunnerVM --> Linux
ExecCont --> RunnerVM
DockerEng --> ExecCont
DockerComp --> ExecCont
Image --> ExecCont : déployé dans
CompFile --> ExecCont : copie

' Services
DockerEng -[#realization]-> ContRT
DockerComp -[#realization]-> ContRT
NetSrv -[#realization]-> HTTPNet

' Relations
ContRT -[#serving]-> Image
ContRT -[#serving]-> CompFile
@enduml
```

---  

## 5. Couche Stratégique (Strategy Layer) – *optionnelle mais présentée pour traçabilité*

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Stakeholder** | **Direction IT** | Porteur de la stratégie d’automatisation. |
| **Driver** | **Agilité Opérationnelle** | Nécessité de livrer rapidement des environnements de test. |
| **Goal** | **Déploiement Continu en Recette** | Objectif de fournir un environnement à chaque commit. |
| **Capability** | **CI/CD Automation** | Capacité clé pour atteindre le *Goal*. |
| **Value Stream** | **Livraison de Valeur Produit** | Chaîne du code source à l’environnement de test. |
| **Course of Action** | **Adoption de GitLab CI + Ansible** | Approche retenue pour automatiser le déploiement. |
| **Requirement** | **Sécurité des Secrets** | Exigence de chiffrer/déchiffrer les secrets (`secrets.yml`). |
| **Constraint** | **Conformité RGPD** | Contraintes légales sur la gestion des données personnelles. |
| **Principle** | **Infrastructure as Code** | Principe directeur du projet. |
| **Outcome** | **Environnement Recette Fiable** | Résultat attendu. |
| **Value** | **Réduction du Time‑to‑Market** | Valeur business générée. |

---  

## 6. Couche de Mise en Œuvre & Migration (Implementation & Migration) – *optionnelle*

| ArchiMate Element | Nom | Description |
|-------------------|-----|-------------|
| **Plateau** | **Baseline (v1.0)** | Architecture actuelle (CI avec `pasta‑cooker`). |
| **Plateau** | **Target (v2.0)** | Ajout d’un *GitOps* (ArgoCD) et d’un *service mesh* pour la recette. |
| **Gap** | **Manque de Monitoring** | Absence de métriques sur le déploiement. |
| **Work Package** | **WP‑01 – Monitoring** | Implémenter Prometheus + Grafana. |
| **Deliverable** | **Doc Monitoring** | Documentation et dashboards. |

---  

## 7. Aspects Transverses (Cross‑layer Relationships)

| Type de relation | Exemple de réalisation |
|-------------------|------------------------|
| **Realization** | *Technology Service → Application Service* : `Container Runtime Service` réalise le `Container Orchestration Service`. |
| **Realization** | *Application Service → Business Service* : `Pipeline Service` réalise le `Déploiement Recette`. |
| **Serving** | *Application Component → Business Process* : `Ansible Engine` sert le processus `Run Recette`. |
| **Assignment** | *Business Role → Business Process* : `CI/CD Operator` assigné au processus `Run Recette`. |
| **Access** | *Application Function → Data Object* : `Render Docker‑Compose` accède à `Docker‑Compose Template`. |
| **Influence** | *Driver → Goal* : `Agilité Opérationnelle` influence le `Déploiement Continu en Recette`. |
| **Realization (Artifact)** | `pasta‑cooker-client Image` réalise le `GitLab CI Runner`. |
| **Assignment (Technology)** | `Docker Engine` assigné à `Execution Container`. |

---  

## 8. Vues Architecturales ArchiMate

### 8.1 Vue de Coopération (Cooperation View)

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master
!include Archimate

' Business collaboration
collaboration "Run Recette Collaboration" as RunCollab <<Business Collaboration>>
role "CI/CD Operator" as Op <<Business Role>>
role "Deployment Engineer" as Eng <<Business Role>>
service "Déploiement Recette" as DeploySrv <<Business Service>>

' Application collaboration
collaboration "CI‑Ansible Collaboration" as CIAnsi <<Application Collaboration>>
applicationComponent "GitLab CI Runner" as GitLabCI <<Application Component>>
applicationComponent "Ansible Engine" as Ansible <<Application Component>>

' Technology collaboration
collaboration "Docker Runtime Collaboration" as DockerCollab <<Technology Collaboration>>
node "Execution Container" as ExecCont <<Node>>
systemSoftware "Docker Engine" as DockerEng <<System Software>>

' Relations
RunCollab --> Op : collabore
RunCollab --> Eng : collabore
Op --> DeploySrv : sert
Eng --> DeploySrv : sert

DeploySrv --> GitLabCI : réalise
GitLabCI --> Ansible : orchestre
Ansible --> ExecCont : déploie
ExecCont --> DockerEng : utilise

@enduml
```

### 8.2 Vue de Réalisation (Realization View)

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master
!include Archimate

' Business Service
service "Déploiement Recette" as BService <<Business Service>>

' Application Service
applicationService "Pipeline Service" as AService <<Application Service>>
applicationService "Container Orchestration Service" as ContSrv <<Application Service>>

' Technology Service
technologyService "Container Runtime Service" as TService <<Technology Service>>

' Realisation chain
BService -[#realization]-> AService
AService -[#realization]-> ContSrv
ContSrv -[#realization]-> TService

@enduml
```

### 8.3 Vue de Migration (Migration View)

```plantuml
@startuml
!define Archimate https://raw.githubusercontent.com/plantuml-stdlib/Archimate-PlantUML/master
!include Archimate

' Plateaux
plateau "Baseline v1.0" as Base <<Plateau>>
plateau "Target v2.0 – GitOps + Service Mesh" as Target <<Plateau>>

' Gap
gap "Monitoring & Observability" as GapMon <<Gap>>

' Work Package
workPackage "WP‑01 – Monitoring" as WPMon <<Work Package>>

' Relations
Base --> GapMon : identifie
GapMon --> WPMon : résout
WPMon --> Target : contribue à

@enduml
```

---  

## 9. Vue de Traçabilité Complète  

| **Élément Métier** | **Service Métier** | **Application** | **Service App** | **Technologie** |
|---------------------|--------------------|----------------|----------------|-----------------|
| *Run Recette* (processus) | Déploiement Recette | GitLab CI Runner | Pipeline Service | Container Runtime Service |
| *Gestion des Secrets* | Gestion des Secrets | Ansible Engine | Configuration Management Service | Docker Engine |
| *Orchestration Conteneurs* | Orchestration Conteneurs | Docker‑Compose | Container Orchestration Service | Docker Engine |
| *Notification Déploiement* | Notification Déploiement | Handler (main.yml) | – (handler) – | – |
| *Environnement Recette* (Produit) | – | docker‑compose.yml (artifact) | – | Execution Container (Node) |

---  

## 10. Métamodele ArchiMate du projet  

Aucun type **personnalisé** n’a été introduit. Le modèle utilise uniquement les concepts standards d’ArchiMate 3.2. Les conventions suivantes ont été adoptées :

| Couche | Couleur (hex) | Exemple d’utilisation |
|--------|---------------|-----------------------|
| **Business** | `#FFFF00` (jaune) | Services, rôles, processus. |
| **Application** | `#99CCFF` (bleu) | Composants, services, fonctions. |
| **Technology** | `#99FF99` (vert) | Nodes, devices, systèmes. |
| **Strategy** | `#FFCC99` (orange) | Goals, drivers, capabilities. |
| **Implementation** | `#CCCCCC` (gris) | Work Packages, plateaux. |

Les diagrammes PlantUML respectent ces couleurs via les stéréotypes ArchiMate (ex. `<<Business Service>>`).  

---  

## 11. Standards & Conventions  

| Aspect | Règle |
|--------|-------|
| **Palette de couleurs** | Voir tableau 10. |
| **Nomage** | *CamelCase* pour les éléments ArchiMate, préfixe de couche (`B_`, `A_`, `T_`) lorsqu’il faut désambiguïser dans les scripts. |
| **Niveaux de détail** | - **Vue Organisationnelle** : haut niveau (acteurs, services). <br> - **Vue Processus** : détails des tâches Ansible. <br> - **Vue Technique** : infrastructure et artefacts. |
| **Outils de modélisation** | - **Archi** (open‑source) – export PlantUML via plugin. <br> - **Enterprise Architect** – prise en charge native d’ArchiMate. |
| **Gestion des versions** | Le DAT est versionné dans le même dépôt (`docs/DAT/agile-infra-DAT-v1.0.md`). |
| **Traçabilité** | Matrice (section 9) maintenue à chaque évolution majeure du pipeline. |
| **Documentation des exigences** | Références aux exigences ISO/IEC/IEEE 42010 dans le dossier `requirements/`. |

---  

## 12. Références  

1. **The Open Group**, *ArchiMate® 3.2 Specification*, 2022.  
2. **ISO/IEC/IEEE 42010:2022**, *Architecture description*.  
3. **The Open Group**, *TOGAF® Standard, Version 10*, 2022 – méthodologie d’élaboration du DAT.  
4. **GitLab CI Documentation**, <https://docs.gitlab.com/ee/ci/>.  
5. **Ansible Documentation**, <https://docs.ansible.com/>.  
6. **Docker Compose Reference**, <https://docs.docker.com/compose/>.  

---  

## 13. Conclusion  

Le **DAT** présenté décrit de façon exhaustive le système **agile‑infra** à travers les couches *Business → Application → Technology*.  
Il montre clairement comment le **service métier** *Déploiement Recette* est réalisé par le **pipeline CI** (GitLab CI + Ansible) et comment ce pipeline repose sur une **infrastructure Docker**.  

Les vues de coopération, de réalisation et de migration offrent aux parties prenantes (direction IT, équipes DevOps, équipes sécurité) une compréhension partagée, tout en assurant la traçabilité requise par les standards d’architecture d’entreprise.  

Le document constitue une base solide pour :

* **Évolution** (intégration d’un GitOps avec ArgoCD, ajout de monitoring).  
* **Audit de conformité** (sécurité des secrets, RGPD).  
* **Communication** avec les décideurs (alignement stratégie → implémentation).  

---  

*Fin du Dossier d’Architecture Technique – agile‑infra*  