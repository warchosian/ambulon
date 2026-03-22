Voici le Dossier d'Architecture Technique (DAT) complet pour l'application **SIREINES**, généré selon le modèle Arc42 et basé sur l'analyse du fichier source fourni.

---

# Dossier d'Architecture Technique (DAT) - SIREINES

**Version** : 2.5.12  
**Date** : 23 février 2026  
**Statut** : Finalisé  

[TOC]

---

## 1. Introduction et objectifs {#introduction}

### 1.1 Vue d'ensemble fonctionnelle

SIREINES (Système d'Information pour la Recherche et l'Évaluation des compétences scientifiques et techniques) est une application métier dédiée à la gestion des évaluations des compétences scientifiques et techniques au sein de l'administration française. L'application permet :

- La gestion des dossiers d'évaluation des agents (création, suivi, qualification)
- L'organisation des séances de comités d'évaluation
- La gestion des rapporteurs et des gestionnaires
- L'import/export de données et la génération de rapports statistiques
- La gestion des référentiels (corps, grades, structures, mots-clés, thésaurus)

### 1.2 Architecture C4 - Niveau 1 (Système)

```plantuml
@startuml
!define RECTANGLE class

skinparam backgroundColor #FEFEFE
skinparam componentStyle rectangle

title SIREINES - Vue Système (C4-L1)

rectangle "Utilisateurs\n(Agents, Gestionnaires,\nRapporteurs)" as Users #LightBlue
rectangle "Administrateurs\nTechniques" as Admins #LightGreen

rectangle "SIREINES\n[Gestion des évaluations\nscientifiques et techniques]" as Sireines #Gold

rectangle "Systèmes Externes" as Ext #LightGray {
    rectangle "Cerbère\n[Authentification]" as Cerbere #LightGray
    rectangle "Annuaire\n[RH/Agents]" as Annuaire #LightGray
    rectangle "Services d'impression\net rapports" as Print #LightGray
}

Users --> Sireines : Utilise\n(HTTPS)
Admins --> Sireines : Administre\n(SSH/HTTPS)
Sireines --> Cerbere : Authentifie\n(SAML/CAS)
Sireines --> Annuaire : Importe données\n(CSV/API)
Sireines --> Print : Génère rapports\n(BIRT/PDF)

@enduml
```

### 1.3 Objectifs de qualité orientés utilisateur

| ID | Objectif | Description | Priorité |
|----|----------|-------------|----------|
| Q1 | **Disponibilité** | L'application doit être accessible 99% du temps ouvré pour permettre la gestion continue des évaluations | Haute |
| Q2 | **Intégrité des données** | Garantir la cohérence et la traçabilité des dossiers d'évaluation (historique complet des modifications) | Critique |
| Q3 | **Confidentialité** | Protection des données personnelles des agents conformément au RGPD et aux exigences de la fonction publique | Critique |
| Q4 | **Maintenabilité** | Faciliter les évolutions métier et correctifs via une architecture modulaire et documentée | Moyenne |
| Q5 | **Performance** | Temps de réponse < 3s pour les recherches et génération de rapports standards | Moyenne |

[↩ Retour au sommaire](#introduction)

---

## 2. Parties prenantes {#parties-prenantes}

| Rôle | Attente principale | Intérêt |
|------|-------------------|---------|
| **MOA (Maîtrise d'Ouvrage)** | Disposer d'un outil fiable pour piloter les processus d'évaluation et produire des statistiques | Fonctionnalités métier complètes, reporting |
| **Utilisateurs métier (Gestionnaires)** | Interface intuitive pour gérer les dossiers et séances efficacement | Ergonomie, rapidité d'exécution |
| **Rapporteurs** | Accès simplifié aux dossiers à évaluer et outils de saisie des conclusions | Accessibilité, clarté des informations |
| **Agents évalués** | Traitement équitable et confidentiel de leur dossier | Sécurité, confidentialité |
| **RSSI** | Conformité aux référentiels de sécurité de l'État (ANSSI, RGPD) | Auditabilité, contrôles d'accès |
| **Exploitants (GTI)** | Déploiement et supervision simplifiés, documentation technique complète | Containerisation, monitoring, sauvegardes |
| **Équipe de développement** | Code maintenable, tests automatisés, CI/CD efficace | Qualité du code, automatisation |

[↩ Retour au sommaire](#introduction)

---

## 3. Contraintes {#contraintes}

### 3.1 Contraintes techniques

| Type | Contrainte | Impact |
|------|-----------|--------|
| **Legacy** | Application Java 7 (JDK 1.7) avec framework Vertigo/Struts 2 | Maintenance technique, sécurité des dépendances |
| **Base de données** | PostgreSQL 15.2 obligatoire pour la persistance | Compatibilité ascendante à prévoir |
| **Reporting** | Dépendance à BIRT (Business Intelligence and Reporting Tools) pour les rapports | Migration complexe si évolution |
| **Authentification** | Intégration obligatoire avec Cerbère (SSO de l'État) | Dépendance à l'infrastructure d'authentification ministérielle |

### 3.2 Contraintes organisationnelles

- **Hébergement** : Cloud interne ECO4 (OpenStack) du Ministère de la Transition Écologique
- **Forge logicielle** : GitLab interne (gitlab-forge.din.developpement-durable.gouv.fr)
- **Registry** : Google Cloud Registry (GCR) du département
- **CI/CD** : GitLab CI avec runners internes

### 3.3 Exigences de sécurité (Modèle D-I-C-T)

| Dimension | Exigence | Mesure technique |
|-----------|----------|------------------|
| **D - Disponibilité** | RTO < 4h, RPO < 1h | Sauvegardes automatisées, réplication BDD, conteneurisation |
| **I - Intégrité** | Traçabilité des modifications sur les dossiers | Audit trail complet, checksums des documents |
| **C - Confidentialité** | Chiffrement des données sensibles | Chiffrement AES-256 des dumps, HTTPS obligatoire, contrôles d'accès RBAC |
| **T - Traçabilité** | Logs d'accès et d'actions conservés 1 an | Centralisation des logs (Loki), supervision PSIN |

### 3.4 Contraintes réglementaires

- **RGPD** : Déclaration enregistrée, droit à l'effacement et à la portabilité
- **RGS (Référentiel Général de Sécurité)** : Niveau "standard" requis
- **Accessibilité** : Engagement de conformité RGAA (audit prévu)

[↩ Retour au sommaire](#introduction)

---

## 4. Contexte et périmètre {#contexte}

### 4.1 Partenaires fonctionnels

| Système/Acteur | Rôle | Type d'interaction |
|----------------|------|-------------------|
| **Cerbère** | Authentification centralisée des agents de l'État | SAML/CAS - À chaque connexion |
| **Système RH (import)** | Alimentation des données agents, corps, grades | Import CSV/Excel - Quotidien ou sur demande |
| **BIRT Engine** | Génération des rapports statistiques et fiches | Intégration embarquée - À la demande |
| **Elasticsearch** | Indexation et recherche full-text des dossiers | API REST - En temps réel |
| **PostgreSQL** | Persistance des données métier | JDBC - En temps réel |
| **Services d'impression** | Génération PDF des courriers et décisions | Export PDF - À la demande |

### 4.2 Interfaces techniques

```plantuml
@startuml
skinparam componentStyle rectangle

title Interfaces Techniques - SIREINES

package "Frontend" {
    [Navigateur Web] as Browser
}

package "Application SIREINES" {
    [Struts 2 Actions] as Struts
    [Services Métier] as Services
    [DAO/MDA] as DAO
}

package "Backend" {
    [PostgreSQL] as DB #LightBlue
    [Elasticsearch] as ES #LightYellow
    [BIRT Engine] as BIRT #LightGray
}

package "Externes" {
    [Cerbère SSO] as Cerbere #LightGreen
    [Système RH] as RH #LightPink
}

Browser --> Struts : HTTPS/443\n(Utilisateurs)
Struts --> Services : Appels internes
Services --> DAO : Transactions
DAO --> DB : JDBC/5432
Services --> ES : HTTP/9200\n(Recherche)
Services --> BIRT : API interne\n(Rapports)
Services --> Cerbere : HTTPS/443\n(Authentification)
Services --> RH : Import fichiers\n(CSV/Excel)

@enduml
```

| Interface | Protocole | Fréquence | Données échangées |
|-----------|-----------|-----------|-------------------|
| Authentification | HTTPS/SAML | À chaque session | Identité, rôles, habilitations |
| Import agents | Fichier CSV | Quotidien | Matricule, nom, prénom, grade, structure |
| Recherche dossiers | HTTP/REST | En temps réel | Requêtes Lucène, résultats JSON |
| Génération rapports | API Java interne | À la demande | Templates .rptdesign, données filtrées |
| Base de données | JDBC | En temps réel | Transactions SQL |

[↩ Retour au sommaire](#introduction)

---

## 5. Stratégie de solution {#strategie}

### 5.1 Décisions architecturales majeures

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Architecture** | Monolithe web Java | Simplicité de déploiement, cohérence avec le legacy, équipe réduite |
| **Pattern MVC** | Struts 2 + Vertigo Framework | Standard historique, génération de code MDA, productivité |
| **Persistance** | SQL natif + MDA (KSP) | Performance, contrôle fin des requêtes métier complexes |
| **Recherche** | Elasticsearch embarqué | Recherche full-text performante sur les dossiers |
| **Reporting** | BIRT intégré | Exigence métier de rapports complexes et paramétrables |
| **Conteneurisation** | Docker + Docker Compose | Portabilité, reproductibilité des environnements |

### 5.2 Environnement technologique

```plantuml
@startuml
skinparam componentStyle rectangle

title Stack Technique SIREINES

package "Langages" {
    [Java 7] as Java
    [SQL] as SQL
    [JavaScript] as JS
    [FreeMarker] as FTL
}

package "Frameworks" {
    [Struts 2] as Struts
    [Vertigo] as Vertigo
    [Spring] as Spring
    [Hibernate] as Hibernate
}

package "Données" {
    [PostgreSQL 15.2] as PG
    [Elasticsearch] as ES
}

package "Outils" {
    [Maven 3.6] as Maven
    [GitLab CI] as CI
    [SonarQube] as Sonar
    [Docker] as Docker
}

Java --> Struts
Java --> Vertigo
Struts --> Spring
Vertigo --> Hibernate
Hibernate --> PG
Vertigo --> ES
Maven --> Java
CI --> Maven
CI --> Sonar
CI --> Docker

@enduml
```

| Couche | Technologie | Version | Rôle |
|--------|-------------|---------|------|
| **Langage** | Java | 1.7 | Logique métier |
| **Framework Web** | Struts 2 | 2.x | Couche présentation MVC |
| **Framework Métier** | Vertigo | - | Services, DAO, ORM léger |
| **Base de données** | PostgreSQL | 15.2 | Persistance relationnelle |
| **Moteur de recherche** | Elasticsearch | 7.x (embarqué) | Indexation full-text |
| **Reporting** | BIRT | 4.x | Génération de rapports |
| **Frontend** | Bootstrap 2/3 | - | UI responsive |
| **Template Engine** | FreeMarker | - | Génération vues |
| **Build** | Maven | 3.6 | Compilation, packaging |
| **Conteneur** | Tomcat | 9.x (embarqué) | Serveur d'applications |

### 5.3 Forge logicielle

| Outil | Usage | Configuration |
|-------|-------|---------------|
| **GitLab** | Gestion de sources, CI/CD | Forge interne du MTE |
| **Maven** | Build, gestion des dépendances | `pom.xml` parent avec modules |
| **SonarQube** | Analyse qualité de code | Scan manuel dans CI |
| **Docker** | Conteneurisation applicative | Multi-stage build, images Alpine |
| **Registry** | GCR (Google Cloud Registry) | `eu.gcr.io/dpnm3-lab/sireines` |

[↩ Retour au sommaire](#introduction)

---

## 6. Vue en Briques (C4-L2) {#briques}

### 6.1 Vue Conteneur

```plantuml
@startuml
!define RECTANGLE class

skinparam backgroundColor #FEFEFE
skinparam componentStyle rectangle

title SIREINES - Vue Conteneurs (C4-L2)

rectangle "Utilisateur\n(Agent/Gestionnaire)" as User #LightBlue

package "Système SIREINES" {
    
    rectangle "Application Web\nSIREINES\n[Java 7, Struts 2, Vertigo]\nPort: 8080" as App #Gold {
        rectangle "Couche Présentation\n(JSP, Actions Struts)" as Pres
        rectangle "Couche Service\n(Services métier)" as Service
        rectangle "Couche Accès Données\n(DAO, MDA)" as DAO
    }
    
    rectangle "Moteur de Recherche\nElasticsearch\n[Embarqué]\nPort: 9200" as Search #LightYellow
    
    rectangle "Générateur de Rapports\nBIRT Engine\n[Intégré à l'app]" as Report #LightGray
    
    rectangle "Base de Données\nPostgreSQL\n[Container]\nPort: 5432" as DB #LightBlue
}

rectangle "Cerbère\n[SSO État]" as SSO #LightGreen

User --> Pres : HTTPS/443\n[Authentifié via Cerbère]
Pres --> Service : Appels internes
Service --> DAO : Transactions
DAO --> DB : JDBC\n[Dossiers, Agents, Référentiels]
Service --> Search : HTTP\n[Indexation, Recherche]
Service --> Report : API interne\n[Génération rapports]
App --> SSO : SAML/CAS\n[Authentification]

@enduml
```

### 6.2 Description des conteneurs

| Conteneur | Technologie | Responsabilité | Interfaces |
|-----------|-------------|----------------|------------|
| **Application Web SIREINES** | Java 7, Struts 2, Vertigo, Tomcat embarqué | Orchestration des flux métier, présentation web, gestion des sessions | HTTP 8080 (interne), exposé via Nginx |
| **Base de données PostgreSQL** | PostgreSQL 15.2 Alpine | Persistance des données métier, référentiels, historique | JDBC 5432 |
| **Elasticsearch** | ES 7.x (mode embedded via Vertigo) | Indexation des dossiers pour recherche full-text | HTTP 9200 (localhost uniquement) |
| **BIRT Engine** | Bibliothèque Java intégrée | Génération des rapports statistiques et fiches PDF | API interne Java |

### 6.3 Structure des modules

```
sireines-web/
├── src/main/java/
│   ├── i2/application/sireines/
│   │   ├── boot/          # Initialisation (Persistence, Search)
│   │   ├── controller/    # Actions Struts (MVC)
│   │   ├── service/       # Services métier (Agents, Dossiers, etc.)
│   │   ├── filter/        # Filtres HTTP (Encoding, Session)
│   │   └── util/          # Utilitaires
│   └── resources/
│       ├── i2/application/sireines/services/  # Modèles MDA (.ksp)
│       ├── META-INF/      # Configuration Spring/Vertigo
│       └── template/      # Templates FreeMarker
└── src/main/webapp/
    ├── jsp/               # Vues JSP
    ├── static/            # CSS, JS, images
    └── WEB-INF/           # Configuration web
```

[↩ Retour au sommaire](#introduction)

---

## 7. Vue Exécution {#execution}

### 7.1 Scénario : Création d'un dossier d'évaluation

```plantuml
@startuml
skinparam sequenceMessageAlign center

title Séquence - Création d'un Dossier d'Évaluation

actor "Gestionnaire" as User
participant "AgentRechercheAction" as Action
participant "AgentsServices" as Service
participant "DossiersServices" as DossierSvc
participant "DossierDAO" as DAO
participant "PostgreSQL" as DB
participant "Elasticsearch" as ES

User -> Action : 1. Rechercher agent (nom/matricule)
activate Action
Action -> Service : findAgentByCriteria()
activate Service
Service -> DAO : selectAgents()
DAO -> DB : SQL Query
DB --> DAO : Résultats
DAO --> Service : Liste agents
Service --> Action : AgentsDTO
Action --> User : Afficher résultats
deactivate Service
deactivate Action

User -> Action : 2. Sélectionner agent + Créer dossier
activate Action
Action -> DossierSvc : createDossier(agentId, params)
activate DossierSvc

DossierSvc -> DossierSvc : Valider données métier

DossierSvc -> DAO : insertDossier(dossier)
activate DAO
DAO -> DB : INSERT INTO DOSSIER...
DB --> DAO : ID généré
DAO --> DossierSvc : Dossier créé
deactivate DAO

DossierSvc -> ES : indexDossier(dossier)
activate ES
ES --> DossierSvc : OK indexé
deactivate ES

DossierSvc --> Action : DossierDTO
deactivate DossierSvc
Action --> User : Redirection fiche dossier
deactivate Action

@enduml
```

### 7.2 Scénario : Génération d'un rapport statistique

```plantuml
@startuml
skinparam sequenceMessageAlign center

title Séquence - Génération Rapport BIRT

actor "Utilisateur" as User
participant "ExtractionAction" as Action
participant "ExtractionsServices" as Service
participant "BirtManager" as Birt
participant "BIRT Engine" as Engine
database "PostgreSQL" as DB

User -> Action : 1. Sélectionner type d'extraction + paramètres
activate Action
Action -> Service : generateReport(type, params)
activate Service

Service -> Birt : runReport(reportId, parameters)
activate Birt

Birt -> Engine : Ouvrir rapport .rptdesign
activate Engine
Engine --> Birt : Rapport chargé

Birt -> Engine : Définir paramètres (dates, filtres)
Engine -> DB : Exécuter requêtes SQL du rapport
DB --> Engine : Jeux de données

Engine -> Engine : Générer PDF/Excel/HTML
Engine --> Birt : Fichier généré
deactivate Engine

Birt --> Service : Chemin fichier résultat
deactivate Birt

Service --> Action : ReportDTO (métadonnées + URL)
deactivate Service

Action --> User : 2. Téléchargement fichier
deactivate Action

@enduml
```

### 7.3 Scénario : Import de données agents (batch)

```plantuml
@startuml
skinparam sequenceMessageAlign center

title Séquence - Import Fichier Agents

actor "Administrateur" as Admin
participant "ImportFichierAction" as Action
participant "ImportsServices" as Service
participant "SAS_IMPORT" as SAS
participant "PostgreSQL" as DB

Admin -> Action : 1. Uploader fichier CSV/Excel
activate Action
Action -> Service : processImport(file)
activate Service

Service -> Service : Valider format fichier

Service -> DB : 2. TRUNCATE SAS_IMPORT
activate DB
DB --> Service : OK
deactivate DB

loop Pour chaque ligne valide
    Service -> DB : INSERT INTO SAS_IMPORT...
    activate DB
    DB --> Service : OK
    deactivate DB
end

Service -> DB : 3. Appeler procédure reprise\n(Merge SAS_IMPORT vers tables métier)
activate DB
DB -> DB : Validation métier\n(Doublons, cohérence)
DB -> DB : INSERT/UPDATE AGENT, DOSSIER...
DB --> Service : Rapport d'import (OK/KO)
deactivate DB

Service --> Action : ImportResultDTO (stats, erreurs)
deactivate Service

Action --> Admin : 4. Afficher synthèse import
deactivate Action

@enduml
```

[↩ Retour au sommaire](#introduction)

---

## 8. Vue Déploiement {#deploiement}

### 8.1 Environnements

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Cloud ECO4 (OpenStack) - Tenant pnm3 | 1 VM / 1 conteneur app + 1 conteneur BDD | Réseau interne MTE | Données de test, Cerbère bouchonné possible |
| **Recette** | Cloud ECO4 (OpenStack) - Tenant pnm3 | 2 VMs (HAProxy) + cluster applicatif | Réseau interne MTE | Données anonymisées, tests d'intégration |
| **Production** | Cloud ECO4 (OpenStack) - Tenant pnm3 | 2 VMs (HAProxy) + cluster applicatif (2+ nœuds) + PostgreSQL primary/standby | Réseau interne MTE + DMZ | Données réelles, supervision renforcée, backups automatiques |

### 8.2 Infrastructure

Le produit est hébergé sur le cloud interne ECO4 basé sur Openstack, dans le tenant 'pnm3' du département.  
Le reverse-proxy Nginx du schéma ci-dessous est en fait une paire de Nginx load-balancés en frontal des produits hébergés sur le tenant.

```plantuml
@startuml
skinparam componentStyle rectangle

title Architecture de Déploiement SIREINES

package "DMZ / Frontal" {
    [Nginx Load Balancer\n(Paire HA)] as Nginx #LightGreen
}

package "Tenant PNM3 - ECO4" {
    
    package "Cluster Application" {
        [SIREINES App 1\nDocker Container] as App1 #Gold
        [SIREINES App 2\nDocker Container] as App2 #Gold
    }
    
    package "Data Layer" {
        [PostgreSQL Primary] as PGPrimary #LightBlue
        [PostgreSQL Standby] as PGStandby #LightBlue
        [Elasticsearch\n(Embedded)] as ES #LightYellow
    }
    
    package "Shared Services" {
        [Portainer\n(Gestion containers)] as Portainer #LightGray
        [Prometheus\n(Metrics)] as Prom #LightGray
        [Grafana\n(Dashboards)] as Grafana #LightGray
    }
}

cloud "Services Externes" {
    [Cerbère SSO] as Cerbere #LightPink
    [Registry GCR] as GCR #LightPink
}

Nginx --> App1 : Load Balancing\n(Round Robin)
Nginx --> App2 : Load Balancing\n(Round Robin)
App1 --> PGPrimary : JDBC/5432
App2 --> PGPrimary : JDBC/5432
PGPrimary --> PGStandby : Réplication\n(Streaming)
App1 --> ES : HTTP/9200 (local)
App2 --> ES : HTTP/9200 (local)
App1 --> Cerbere : HTTPS/443
App2 --> Cerbere : HTTPS/443
Portainer --> App1 : Management
Portainer --> App2 : Management
Prom --> App1 : Scraping metrics
Prom --> App2 : Scraping metrics
Grafana --> Prom : Visualisation

@enduml
```

### 8.3 Supervision

Le produit est supervisé via le système standard du GTI pour ce faire :
- via Portainer pour la partie purement conteneurisée,
- via la stack Prometheus/Grafana/Loki/AlertManager,
- Le produit dispose également d'une supervision PSIN.

### 8.4 Sauvegardes

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
- le stockage objet B3 du IaaS ministériel,
- le stockage objet Outscale SecNumCloud (via la prestation qu'a le GTI sur le marché "Nuage Public"),
- le stockage objet standard de Google Cloud (via la prestation qu'a le GTI sur le marché "Nuage Public").

[↩ Retour au sommaire](#introduction)

---

## 9. Sujets transverses {#transverses}

### 9.1 Authentification et autorisation

| Aspect | Implémentation |
|--------|---------------|
| **Protocole** | SAML 2.0 / CAS via Cerbère |
| **Gestion des sessions** | Sessions HTTP côté serveur (Struts 2) |
| **Contrôles d'accès** | RBAC basé sur les rôles Cerbère (gestionnaire, rapporteur, admin) |
| **Déconnexion** | SSO logout redirect vers Cerbère |

### 9.2 Journalisation et traçabilité

| Type de log | Destination | Format |
|-------------|-------------|--------|
| **Logs applicatifs** | Stdout/Stderr (Docker) → Loki | Log4j XML |
| **Audit métier** | Table `historique` en BDD | JSON structuré (action, utilisateur, timestamp, données) |
| **Accès HTTP** | Nginx access logs | Standard Nginx |
| **Erreurs** | Fichier + BDD (table `import_erreur`) | Stack trace + contexte |

### 9.3 Gestion des erreurs

| Niveau | Stratégie |
|--------|-----------|
| **UI** | Messages utilisateur internationalisés (FR), pas de stack trace exposée |
| **Application** | Catch global via `ErrorHandler` Struts, log détaillé, rollback transactionnel |
| **Base de données** | Contraintes d'intégrité référentielle, transactions ACID |
| **Import de données** | Table `SAS_IMPORT` avec statut par ligne, rapport d'erreur détaillé |

### 9.4 API et intégrations

L'application ne propose pas d'API REST publique. Les intégrations se font via :
- **Import de fichiers** : CSV, Excel (via formulaires web)
- **Export de rapports** : PDF, Excel, HTML (via BIRT)
- **Recherche interne** : Elasticsearch (non exposé externement)

[↩ Retour au sommaire](#introduction)

---

## 10. Exigences de qualité {#qualite}

| ID | Exigence | Scénario de validation | Critère d'acceptation |
|----|----------|------------------------|----------------------|
| Q1 | Temps de réponse recherche | Recherche full-text sur 100k dossiers | < 3 secondes |
| Q2 | Disponibilité service | Mesure sur 1 mois d'exploitation | > 99% du temps ouvré |
| Q3 | Récupération incident | Simulation panne BDD primaire | Basculement < 5 min, perte données < 1h |
| Q4 | Sécurité authentification | Test intrusion (pentest) | Aucun contournement Cerbère possible |
| Q5 | Cohérence données import | Import fichier 10k lignes avec 5% erreurs | Rollback complet, rapport erreur précis |

[↩ Retour au sommaire](#introduction)

---

## 11. Risques et dettes techniques {#risques}

| Risque / Dette | Sévérité | Mesure d'atténuation | Échéance |
|----------------|----------|---------------------|----------|
| **Java 7 obsolète** (fin de support) | 🔴 Critique | Plan de migration Java 11/17, audit compatibilité Vertigo | 2026-2027 |
| **Struts 2 vulnérabilités** | 🔴 Critique | Mise à jour dernière version 2.5.x, monitoring CVE | Continu |
| **BIRT déprécié** (Eclipse) | 🟡 Majeur | Évaluation JasperReports ou solutions alternatives | 2027 |
| **Monolithe difficile à scaler** | 🟡 Majeur | Containerisation OK, étude microservices si besoin | Selon charge |
| **Elasticsearch embarqué** | 🟡 Majeur | Passage à cluster ES dédié si volumétrie augmente | Selon volumétrie |
| **Documentation technique** | 🟢 Mineur | Maintenance DAT, ADR, commentaires code | Continu |

[↩ Retour au sommaire](#introduction)

---

## 12. Annexes {#annexes}

### 12.1 Glossaire

| Terme | Définition |
|-------|------------|
| **Arc42** | Standard de documentation d'architecture logicielle |
| **BIRT** | Business Intelligence and Reporting Tools (Eclipse) |
| **C4 Model** | Modèle de visualisation d'architecture (Context, Containers, Components, Code) |
| **Cerbère** | SSO (Single Sign-On) de l'État français |
| **ECO4** | Cloud privé du Ministère de la Transition Écologique (OpenStack) |
| **GTI** | Groupement de Travail Informatique (équipe exploitation) |
| **KSP** | Vertigo Keyword Scripting Language (MDA) |
| **MDA** | Model Driven Architecture |
| **RGS** | Référentiel Général de Sécurité |
| **SAML** | Security Assertion Markup Language (protocole SSO) |
| **SAS_IMPORT** | Table de staging pour imports de données |
| **Vertigo** | Framework Java développé par Klee Group |

### 12.2 Décisions d'Architecture (ADR)

#### ADR-001 : Maintien de Java 7 pour compatibilité legacy
**Contexte** : Application historique, migration coûteuse  
**Décision** : Conserver Java 7 en production, préparer migration Java 11  
**Conséquences** : Dette technique, vigilance sécurité  

#### ADR-002 : Elasticsearch embarqué vs cluster dédié
**Contexte** : Besoin de recherche full-text, contraintes d'infrastructure  
**Décision** : Utiliser le mode embedded d'Elasticsearch via Vertigo  
**Conséquences** : Simplicité de déploiement, limite de scalabilité horizontale  

#### ADR-003 : Conservation de BIRT pour les rapports
**Contexte** : Exigence métier de rapports complexes existants  
**Décision** : Maintenir BIRT malgré son déclin, évaluer migration à moyen terme  
**Conséquences** : Dépendance à une technologie legacy, formation nécessaire  

#### ADR-004 : Architecture monolithique conteneurisée
**Contexte** : Équipe réduite, besoin de simplicité opérationnelle  
**Décision** : Dockerisation du monolithe existant sans découpage microservices  
**Conséquences** : Facilité de déploiement, limites de scalabilité fine  

---

**Fin du document**

*Document généré automatiquement selon le modèle Arc42 - Compatible VS Code / Obsidian*
```

---

Ce DAT est **autoporté**, prêt à être utilisé dans VS Code ou Obsidian avec l'extension PlantUML activée. Toutes les sections sont complètes et basées sur l'analyse du fichier source fourni, sans dépendances externes.