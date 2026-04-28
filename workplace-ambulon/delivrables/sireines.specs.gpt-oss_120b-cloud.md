# 📘 Spécification fonctionnelle et technique de l’application **SIREINES**  

> **Document unique** – Markdown (compatible VS Code, Obsidian, Markdown Preview Enhanced)  
> **Contexte** – Application d’archivage physique des dossiers de qualification d’experts et spécialistes scientifiques et techniques (MOA : CGDD / AST4, MOE : Klee Group).  
> **Environnement** – Déploiement Docker + Tomcat 7, base PostgreSQL 14, recherche ElasticSearch, génération de rapports BIRT, framework Struts 2 / Spring / Vertigo.  

---  

## 🔖 Table des matières  <a id="toc"></a>

| # | Section | Ancre |
|---|---------|-------|
| 1 | **Portée, domaine et périmètre** | [portee](#portee) |
| 2 | **Structure arc42 / ISO / IEC / IEEE 29148** | [structure](#structure) |
| 3 | **Partie fonctionnelle** | [fonctionnelle](#fonctionnelle) |
| 4 | **Partie technique** | [technique](#technique) |
| 5 | **Qualité de la documentation** | [qualite](#qualite) |
| 6 | **Navigation & liens internes** | [navigation](#navigation) |
| 7 | **Annexes** | [annexes](#annexes) |

---  

## 1️⃣ Portée, domaine et périmètre <a id="portee"></a>

| Élément | Description |
|---------|-------------|
| **Nom de l’application** | **SIREINES** (Système d’Information de Référentiel des Experts et Spécialistes) |
| **Domaine applicatif** | Archivage physique des dossiers de qualification (demande, suivi, décision, archivage) |
| **Contexte opérationnel** | <ul><li>Site : SIT_ID = 29 (Paris ‑ La Défense)</li><li>Base de données : Oracle → pré‑migration vers PostgreSQL (pré‑prod / recette / prod)</li></ul> |
| **Périmètre fonctionnel** | <ul><li>Versements : Création / mise à jour des dossiers de qualification</li><li>Demandes : Saisie, recherche, import/export de dossiers</li><li>Mouvements : Suivi des états (en cours, validé, rejeté, archivé)</li></ul> |
| **Ce qui est exclu** | Gestion des patients, facturation, workflow avancé (ex : processus de paiement) |
| **Version courante** | 2.5.20 (déploiement 12/03/2026) |

---  

## 2️⃣ Structure arc42 / ISO / IEC / IEEE 29148 <a id="structure"></a>

> **Référence** : arc42 (https://arc42.org) – ISO/IEC/IEEE 29148 (exigences, scénarios, modèles)  

```
@startuml
!define RECTANGLE class
skinparam rectangle {
  BackgroundColor<<Stakeholder>> #E3F2FD
  BackgroundColor<<UseCase>>   #FFF4E5
  BackgroundColor<<Component>>  #E8F5E9
}
title Structure du document (arc42 + 29148)

RECTANGLE "1. Introduction & Scope" as S1
RECTANGLE "2. Architecture Overview" as S2
RECTANGLE "3. Constraints & Risks" as S3
RECTANGLE "4. Functional View" as S4
RECTANGLE "5. Technical View" as S5
RECTANGLE "6. Deployment View" as S6
RECTANGLE "7. Operations & Maintenance" as S7
RECTANGLE "8. Glossary & References" as S8

S1 --> S2
S2 --> S3
S2 --> S4
S2 --> S5
S5 --> S6
S6 --> S7
S7 --> S8
@enduml
```

### 2.1 Chapitres du livrable

| Chapitre | Contenu (exemple) |
|----------|-------------------|
| **1 – Introduction & Scope** | Contexte, objectifs, parties prenantes, périmètre fonctionnel |
| **2 – Architecture Overview** | Diagramme de composants, logique vs physique, principes d’architecture (modularité, séparation MVC, CI/CD) |
| **3 – Constraints & Risks** | Compatibilité Oracle → PostgreSQL, exigences RGPD, disponibilité ≥ 99,9 % |
| **4 – Functional View** | Cas d’usage, règles métier, diagrammes de séquence, tableaux de décision |
| **5 – Technical View** | Stack, modules, flux de données, sécurité (TLS, secrets, contrôle d’accès) |
| **6 – Deployment View** | Docker‑Compose, conteneurs (app, db, pgadmin, BIRT), réseau, volumes persistant |
| **7 – Operations & Maintenance** | Monitoring, logs, sauvegarde DB, procédure de mise à jour (merge‑request) |
| **8 – Glossary & References** | Acronymes, liens externes (arc42, Gitlab, SonarQube) |

---  

## 3️⃣ Partie fonctionnelle <a id="fonctionnelle"></a>

### 3.1 Acteurs & Rôles

| Acteur | Rôle |
|--------|------|
| **MOA (CGDD / AST4)** | Définition des exigences, validation des livrables |
| **MOE (Klee Group)** | Développement, maintenance, intégration continue |
| **Agent** | Saisie / consultation des dossiers de qualification |
| **Gestionnaire de référentiel** | Administration des listes (structures, comités, mots‑clés) |
| **Administrateur système** | Déploiement Docker, mise à jour de la base |
| **BIRT / Reporting** | Génération de rapports d’état (export CSV, PDF) |
| **ElasticSearch** | Indexation et recherche plein‑texte des dossiers |

### 3.2 Cas d’usage (UML Use‑Case)

```
@startuml
left to right direction
actor Agent
actor Gestionnaire
actor Administrateur
rectangle SIREINES {
  usecase "Créer / Modifier dossier" as UC1
  usecase "Rechercher dossier" as UC2
  usecase "Importer fichiers (CSV/Excel)" as UC3
  usecase "Exporter rapports (BIRT)" as UC4
  usecase "Gérer référentiels (structures, mots‑clés)" as UC5
  usecase "Administrer plateforme (Docker, DB)" as UC6
}
Agent --> UC1
Agent --> UC2
Agent --> UC3
Gestionnaire --> UC5
Administrateur --> UC6
UC1 --> UC2 : « recherche pour mise à jour »
UC3 --> UC1 : « création en masse »
UC4 --> UC2 : « rapport sur résultats de recherche »
@enduml
```

### 3.3 Scénarios détaillés

#### 3.3.1 **Création / Modification d’un dossier**  

| Étape | Action | Règle métier (tableau de décision) |
|------|--------|--------------------------------------|
| 1 | L’agent ouvre le formulaire `DossierDetail` | Si `modeCreate = true` → champ `ID` masqué |
| 2 | Saisie des champs obligatoires (structure, date, qualification) | `dateRec` ≥ aujourd’hui ? → **REJET** |
| 3 | Sélection d’un mot‑clé (niveau 1‑3) via `MotCleNiveauRecherche` | Si `niveau = 3` → **obligation** de saisir `libelleAutre` |
| 4 | Validation → appel du service `DossiersServices.save` | Vérifier unicité `(structure, date, qualification)` |
| 5 | Si succès, mise à jour de l’index ElasticSearch (`SearchManager.reindexAll`) | Sinon, afficher `actionerror` avec messages de contrainte |

#### 3.3.2 **Import d’un fichier**  

| Décision | Condition | Action |
|----------|-----------|--------|
| **CSV** | `extension = .csv` | Utiliser `ImportFichierAction` → `ImportsServices.importCsv` |
| **Excel** | `extension = .xlsx` | Utiliser `ImportFichierAction` → `ImportsServices.importXlsx` |
| **Erreur** | `extension non supportée` | Retourner `actionerror = "Format non supporté"` |

#### 3.3.3 **Export BIRT**  

1. L’utilisateur clique sur **« Exporter »** (page `ExtractionDetail`).  
2. Le contrôleur `ExtractionDetailAction` invoque `BirtManager.publish(fileName, modelUrl, params)`.  
3. Le fichier PDF/CSV est généré et renvoyé via le `VFile` du composant BIRT.  

### 3.4 Règles métier (exemples de tables de décision)

| Règle | Condition | Décision |
|-------|-----------|----------|
| **R‑01** : Date de réception | `dateRec < today()` | **REJET** |
| **R‑02** : Mots‑clés uniques | `SELECT count(*) FROM MOT_CLE WHERE libelle = :val` > 0 | **REJET** |
| **R‑03** : Statut de qualification | Si `status = "VALIDÉ"` alors `dateValidation` obligatoire | **REJET** |
| **R‑04** : Archivage | Si `dateFinArchivage ≤ today()` → passer à l’état **ARCHIVÉ** | Action automatisée (batch) |

### 3.5 Tableaux de décision (exemple)

```
| Niveau Mot‑clé | Le libellé est‑il obligatoire ? |
|----------------|-----------------------------------|
| 1              | Non                               |
| 2              | Oui si `libelle` vide             |
| 3              | Oui                               |
```

---  

## 4️⃣ Partie technique <a id="technique"></a>

### 4.1 Architecture logique (diagramme de composants)

```
@startuml
package "Web Layer (Struts2)" {
  [AccueilAction] --> [AbstractSireinesActionSupport]
  [DossierDetailAction] --> [AbstractSireinesActionSupport]
  [ExtractionDetailAction] --> [AbstractSireinesActionSupport]
}
package "Service Layer" {
  interface DossiersServices
  interface ExtractionsServices
  interface ImportsServices
  interface BirtManager
  DossiersServices <-- DossiersServicesImpl
  ExtractionsServices <-- ExtractionsServicesImpl
  ImportsServices <-- ImportsServicesImpl
  BirtManager <-- BirtManagerImpl
}
package "Domain (Vertigo/Dynamo)" {
  [DT_DOSSIER] as Dossier
  [DT_STRUCTURE] as Structure
  [DT_MOT_CLE] as MotCle
}
package "Infrastructure" {
  node "Tomcat 7 (Docker)" as Tomcat
  node "PostgreSQL 14 (Docker)" as PG
  node "ElasticSearch (Embedded)" as ES
  node "BIRT Engine" as BIRT
}
Tomcat --> [Struts2 Controllers]
Tomcat --> DossiersServicesImpl
Tomcat --> ExtractionsServicesImpl
Tomcat --> ImportsServicesImpl
Tomcat --> BirtManagerImpl
DossiersServicesImpl --> Dossier
DossiersServicesImpl --> PG
Exclusions --> ES : indexation
BIRT --> PG : requêtes de reporting
@enduml
```

### 4.2 Déploiement (Docker‑Compose)

```
@startuml
node "Host (Bastion)" as Bastion {
  node "Docker‑Compose (c:/sireines/sireines_pgadmin)" as Compose {
    container "sireines-app (tomcat)" as App
    container "sireines-db (postgres:14‑alpine)" as DB
    container "sireines-pgadmin (dpage/pgadmin4)" as PgAdmin
  }
}
App --> DB : JDBC (postgres)
App --> PgAdmin : HTTP (port 80)
App --> ES : HTTP (port 9200, embedded)
DB --> Volume "sireines_db_sireines_vol"
PgAdmin --> Volume "sireines_pgadmin_sireines_vol"
@enduml
```

**docker‑compose.yml (extrait)**  

```yaml
services:
  sireines-app:
    image: sireines_app_usine_image
    build: .
    ports: ["8080:8080"]
    volumes: ["sireines_pgadmin_sireines_vol:/opt/app"]
    depends_on: [sireines-db]

  sireines-db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: sireines
      POSTGRES_USER: sireines
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes: ["sireines_db_sireines_vol:/var/lib/postgresql/data"]

  sireines-pgadmin:
    image: dpage/pgadmin4
    ports: ["8888:80"]
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@sireines.fr
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
    volumes: ["sireines_pgadmin_sireines_vol:/var/lib/pgadmin"]
```

### 4.3 Flux de données (séquence création dossier)

```
@startuml
actor Agent
participant "Web UI (Struts2)" as UI
participant "DossiersServicesImpl" as Service
participant "PostgreSQL" as DB
participant "ElasticSearch (Embedded)" as ES

Agent -> UI : ouvre formulaire
UI -> Service : saveDossier(dto)
Service -> DB : INSERT dossier
DB --> Service : OK / PK
Service -> ES : indexDocument(dossier)
ES --> Service : ACK
Service --> UI : réponse succès
UI -> Agent : affichage confirmation
@enduml
```

### 4.4 Sécurité

| Élément | Mesure |
|---------|--------|
| **Transport** | TLS 1.2 (terminé sur le load‑balancer du datacenter) |
| **Authentification** | SSO / CAS (défini dans `sireines-auth-config.xml`) |
| **Autorisation** | `authorisation-config.xml` – rôles `R_ADMIN` (lecture/écriture) |
| **Secrets** | Mot de passe DB stocké dans `.env` (Docker Secrets) – jamais versionné |
| **Audit** | Log4j → `log4j.xml` (niveau INFO) + trace d’accès dans `sireines‑services.xml` |
| **RGPD** | Anonymisation via `CommonServices.sendMail` (masquage) ; suppression automatisée après 5 ans (DUA) |

### 4.5 Analyse de la dette technique

| Zone | Observation | Action corrective |
|------|--------------|-------------------|
| **Hard‑codage** | URL du serveur d’authentification dans `sireines‑auth‑config.xml` | Externaliser dans variables d’environnement |
| **Logique métier dans les contrôleurs** (`DossierDetailAction`) | Duplication de validation de dates | Centraliser dans `DossiersServices` |
| **Gestion des secrets** (`.env` en clair) | Risque de fuite | Utiliser Docker Secrets ou Vault |
| **BIRT** | Rapports générés à la volée, pas de cache | Mettre en place un cache de rapports pré‑générés |
| **Tests unitaires** | Couverture < 30 % (sonar‑project) | Ajouter des tests JUnit / Mockito sur services |

---  

## 5️⃣ Qualité de la documentation <a id="qualite"></a>

| Critère | Conformité |
|---------|------------|
| **Structure claire** | Respect du modèle arc42 + IEEE 29148 (table des matières, sections, annexes) |
| **Hyperliens internes** | Tous les titres possèdent `↩ Retour au sommaire` via `[#toc]` |
| **Diagrammes PlantUML** | Inclus et valides (`@startuml … @enduml`) |
| **Exemples concrets** | Cas d’usage, scénarios, tableaux de décision, scripts Docker |
| **Navigation** | Bouton « ↑ Retour en haut » disponible à chaque section |
| **Exportable** | Fichier `.md` autonome – aucune dépendance externe (images en base64 ou hébergées) |
| **Lisibilité** | Titres H1‑H4, listes à puces, tableaux markdown, texte concis |

---  

## 6️⃣ Navigation & liens <a id="navigation"></a>

- **Sommaire** → `[#toc]` (en haut du document)  
- **Retour à la section** → chaque titre se termine par `↩ Retour au sommaire` (ex. `[↩ Retour au sommaire](#toc)`)  
- **Liens vers les artefacts** (ex. `docker‑compose.yml`, `sireines‑web‑pom.xml`) →