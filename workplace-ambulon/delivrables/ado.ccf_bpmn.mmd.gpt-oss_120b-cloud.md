# 📄 Cahier des Charges Fonctionnel (CCF) – **ADO**  
*Modélisation BPMN conforme à la norme ISO/IEC 19510 (BPMN 2.0)*  

---

## 1️⃣ Introduction et contexte processus  

| Élément | Description |
|---------|-------------|
| **Nom de l’application** | **ADO** – Consultation des données RH archivées de ReHucit (snapshot du 30/05/2019). |
| **Environnement** | Application **Java Spring Boot** (web + REST) déployée sur **IaaS ECO4 – Paris La Défense** (HTTPS). |
| **Objectifs de la modélisation** | • Formaliser les processus métier exposés aux usagers ; <br>• Garantir la traçabilité, la conformité DICT/ DACP et la sécurité ; <br>• Servir de base à la création de tests fonctionnels, de KPI et d’une éventuelle automatisation (exécution moteur BPMN). |
| **Périmètre** | Tous les services accessibles depuis l’interface web : <br>1. Recherche d’agents ; <br>2. Consultation du **Mini‑CV** et du **Détail agent** ; <br>3. Génération des différents **rapports** (5, Acte, 19‑22, Enfant, … ) ; <br>4. Historisation (journal) et suivi d’utilisation ; <br>5. Purge des journaux ; <br>6. Authentification/autorisation via le filtre **FiltreCerbere**. |
| **Glossaire métier (extraits)** | • **Agent** – salarié du ministère dont les données RH sont archivées dans ReHucit. <br>• **Mini‑CV** – vue synthétique du dossier (identité, situation familiale, affectations, etc.). <br>• **Rapport 5** – conjoint de l’agent. <br>• **Rapport Acte** – acte administratif (nature, état, visas…). <br>• **Journal** – trace d’accès (date/heure, matricule, rapport consulté, paramètres). |
| **Conformité** | • **DICT 1332** (Disponibilité 1, Intégrité 3, Traçabilité 2, Confidentialité 3). <br>• **DACP** – traitement de données à caractère personnel (NIR, etc.). <br>• **RGPD** – registre des traitements, consentement implicite, sécurité renforcée. |

---

## 2️⃣ Cartographie des processus (Process Map)

### 2.1 Nomenclature hiérarchique  

| Niveau | Type | Exemple |
|--------|------|----------|
| **P‑001** | **Processus métier stratégique** | Gestion de la consultation historique des dossiers RH. |
| **P‑101** | **Processus métier opérationnel** | Recherche d’agents. |
| **P‑102** | **Processus métier opérationnel** | Détail d’un agent (Mini‑CV, historiques, affectations). |
| **P‑103** | **Processus métier opérationnel** | Génération de rapports (5, Acte, 19‑22, Enfant, …). |
| **P‑104** | **Processus de support** | Journalisation & suivi d’utilisation. |
| **P‑105** | **Processus de support** | Purge périodique du journal. |
| **P‑106** | **Processus de management** | Authentification & contrôle d’accès (FiltreCerbere). |

### 2.2 Matrice de processus  

| ID Processus | Nom | Type | Propriétaire | Priorité |
|--------------|-----|------|--------------|----------|
| **P‑101** | Recherche d’agents | Opérationnel | **SG/DRH** (MOA) | Critique |
| **P‑102** | Consultation du détail agent | Opérationnel | **SG/DRH** | Critique |
| **P‑103** | Génération de rapports | Opérationnel | **SG/DRH** | Important |
| **P‑104** | Journalisation d’accès | Support | **SG/DRH** | Important |
| **P‑105** | Purge du journal | Support | **SG/DRH** | Moyen |
| **P‑106** | Authentification & autorisation | Management | **SG/DRH** | Critique |

---

## 3️⃣ Modélisation BPMN détaillée  

> **Convention** : chaque diagramme est présenté en syntaxe **Mermaid bpmn** (compatible avec le rendu Mermaid v10+).  
> Les **Pools** représentent les acteurs externes : **Utilisateur**, **ADO‑WebApp**, **PostgreSQL‑DB**.  
> Les **Lanes** à l’intérieur du pool **ADO‑WebApp** découpent les couches *Controller → Service → Repository*.

### 3.1 Diagramme de collaboration – Recherche d’agents (P‑101)

```mermaid
bpmn
  participant User
  participant ADO_WebApp
  participant PostgreSQL_DB

  User->>ADO_WebApp: HTTP GET /agents?criteria=…
  ADO_WebApp->>ADO_WebApp: FiltreCerbere (authz)
  ADO_WebApp->>ADO_WebApp: Parse critères (motif, bornAfter, bornBefore)
  ADO_WebApp->>PostgreSQL_DB: CALL get_agents(motif, bornAfter, bornBefore)
  PostgreSQL_DB-->>ADO_WebApp: List<Agent>
  ADO_WebApp->>User: JSON List<Agent>
```

#### 3.1.1 Process Diagram (P‑101)

```mermaid
bpmn
  startEvent(start) --> taskParse[Parse critères de recherche]
  taskParse --> gatewayAuth{FiltreCerbere autorise ?}
  gatewayAuth -->|Oui| taskQuery[DAO.getAgents(...)]
  gatewayAuth -->|Non| endEventUnauthorized[401 Unauthorized]
  taskQuery --> taskMap[Map Entity → DTO (AgentDto)]
  taskMap --> endEventSuccess[200 OK + JSON]
```

### 3.2 Diagramme de collaboration – Consultation du détail agent (Mini‑CV) (P‑102)

```mermaid
bpmn
  participant User
  participant ADO_WebApp
  participant PostgreSQL_DB

  User->>ADO_WebApp: HTTP GET /agents/{matricule}
  ADO_WebApp->>ADO_WebApp: FiltreCerbere (authz)
  ADO_WebApp->>ADO_WebApp: Validate matricule format
  ADO_WebApp->>PostgreSQL_DB: CALL getAgent(matricule)
  PostgreSQL_DB-->>ADO_WebApp: AgentEntity
  ADO_WebApp->>ADO_WebApp: Assemble MiniCV (multiple adapters)
  ADO_WebApp->>User: HTML / JSON MiniCV
```

#### 3.2.1 Process Diagram (P‑102)

```mermaid
bpmn
  startEvent(start) --> taskValidate[Validate matricule]
  taskValidate --> gatewayAuth{FiltreCerbere autorise ?}
  gatewayAuth -->|Oui| taskGet[DAO.getAgent(matricule)]
  gatewayAuth -->|Non| endEventUnauthorized[401 Unauthorized]
  taskGet --> taskAdapters[Run *ToArrayAdapter* (MiniCV, ...)]
  taskAdapters --> taskRender[Render Thymeleaf / JSON]
  taskRender --> endEventSuccess[200 OK]
```

### 3.3 Diagramme de collaboration – Génération d’un rapport (ex. Rapport 5) (P‑103)

```mermaid
bpmn
  participant User
  participant ADO_WebApp
  participant JasperService
  participant PostgreSQL_DB

  User->>ADO_WebApp: HTTP GET /reports/5?matricule=…
  ADO_WebApp->>ADO_WebApp: FiltreCerbere (authz)
  ADO_WebApp->>PostgreSQL_DB: CALL getRapport5(matricule)
  PostgreSQL_DB-->>ADO_WebApp: Rapport5Entity
  ADO_WebApp->>ADO_WebApp: Rapport5ToArrayAdapter → String[]
  ADO_WebApp->>JasperService: runReportOutputFile("rapport5", params, PDF, destFile)
  JasperService-->>ADO_WebApp: PDF file
  ADO_WebApp->>User: HTTP 200 + PDF
```

#### 3.3.1 Process Diagram (P‑103 – Rapport 5)

```mermaid
bpmn
  startEvent(start) --> gatewayAuth{FiltreCerbere autorise ?}
  gatewayAuth -->|Oui| taskFetch[DAO.getRapport5(matricule)]
  gatewayAuth -->|Non| endEventUnauthorized[401 Unauthorized]
  taskFetch --> taskAdapter[Rapport5ToArrayAdapter]
  taskAdapter --> taskJasper[IJasperService.runReportOutputFile]
  taskJasper --> endEventSuccess[200 OK + PDF]
```

### 3.4 Diagramme de collaboration – Journalisation & suivi d’utilisation (P‑104)

```mermaid
bpmn
  participant ADO_WebApp
  participant PostgreSQL_DB

  ADO_WebApp->>ADO_WebApp: Before response → create JournalEntry
  ADO_WebApp->>PostgreSQL_DB: INSERT journal (date,heure,matricule,rapport,parametres,email)
  PostgreSQL_DB-->>ADO_WebApp: OK

  User->>ADO_WebApp: HTTP GET /journal?email=…
  ADO_WebApp->>PostgreSQL_DB: SELECT * FROM journal WHERE user_email=…
  PostgreSQL_DB-->>ADO_WebApp: List<Journal>
  ADO_WebApp->>User: JSON List<Journal>
```

#### 3.4.1 Process Diagram (P‑104)

```mermaid
bpmn
  startEvent(start) --> taskCreate[Create JournalEntry]
  taskCreate --> taskInsert[INSERT journal]
  taskInsert --> endEventLogged[Entry persisted]
  --- 
  startEvent(startSearch) --> taskQuery[SELECT journal BY email]
  taskQuery --> endEventResult[200 OK + JSON]
```

### 3.5 Diagramme de collaboration – Purge périodique du journal (P‑105)

```mermaid
bpmn
  participant Scheduler
  participant ADO_WebApp
  participant PostgreSQL_DB

  Scheduler->>ADO_WebApp: Trigger purge (cron 00_00)
  ADO_WebApp->>ADO_WebApp: Compute purgeDate (now‑90 jours)
  ADO_WebApp->>PostgreSQL_DB: DELETE FROM journal WHERE date_access <= purgeDate
  PostgreSQL_DB-->>ADO_WebApp: rowsDeleted
  ADO_WebApp->>Scheduler: ACK
```

#### 3.5.1 Process Diagram (P‑105)

```mermaid
bpmn
  startEvent(start) --> taskCalc[Compute purgeDate = today‑90]
  taskCalc --> taskDelete[DELETE journal WHERE date <= purgeDate]
  taskDelete --> endEventDone[Purged rows logged]
```

### 3.6 Diagramme de collaboration – Authentification / Autorisation (P‑106)

```mermaid
bpmn
  participant User
  participant FiltreCerbere
  participant ADO_WebApp

  User->>FiltreCerbere: HTTP request + cookies / token
  FiltreCerbere->>FiltreCerbere: Validate SSO token (Cerbere)
  FiltreCerbere --> ADO_WebApp: Forward request if OK
  FiltreCerbere-->>User: 401 if KO
```

#### 3.6.1 Process Diagram (P‑106)

```mermaid
bpmn
  startEvent(start) --> taskValidate[Validate SSO token]
  taskValidate --> gatewayOK{Token valide ?}
  gatewayOK -->|Oui| endEventPass[Forward to Controller]
  gatewayOK -->|Non| endEventReject[401 Unauthorized]
```

---

## 4️⃣ Règles de gestion métier  

| Point de décision | Condition | Règle métier | Source |
|-------------------|-----------|--------------|--------|
| **RG‑001** | `matricule` fourni | L’agent doit appartenir au **snapshot ReHucit du 30/05/2019** (exclusion des agents déjà importés dans RenoiRH). | Spécifications fonctionnelles (doc ADO‑Documentation‑technique). |
| **RG‑002** | `bornAfter` / `bornBefore` non‑null | Filtrer les agents dont `date_naissance` ∈ `[bornAfter, bornBefore]`. Si paramètre vide → pas de filtre. | Requête SQL `get_agents`. |
| **RG‑003** | Recherche texte (wildcard) | La comparaison porte sur **UPPER + UNACCENT** de tous les champs (nom, prénom, matricules, ville, pays, commune). | Requête `get_agents`. |
| **RG‑004** | Accès à un rapport | L’utilisateur doit posséder le **profil unique** autorisé (vérifié par `FiltreCerbere`). | FiltreCerbere / contrat de service. |
| **RG‑005** | Journalisation | Chaque appel de rapport ou de consultation doit créer une ligne `journal` contenant : date, heure, matricule, nom du rapport, paramètres, email de l’utilisateur. | Implémentation `IJournalService`. |
| **RG‑006** | Purge du journal | Les entrées antérieures à **90 jours** sont supprimées automatiquement chaque jour à 00 h. | `P‑105` (processus de purge). |
| **RG‑007** | Sécurité des données DACP | Le NIR (numéro de sécurité sociale) n’est jamais exposé dans les réponses HTML/JSON ; il est masqué ou hashé. | Politique DACP / RGPD. |
| **RG‑008** | Génération de rapport Jasper | Avant l’appel, le tableau `String[]` fourni à Jasper doit contenir **exactement** le nombre de colonnes attendu par le template (`*.jrxml`). Sinon lancer `JReportExportException`. | `JasperServiceImpl`. |

---

## 5️⃣ Données et documents  

| Type | Description | Exemple |
|------|-------------|----------|
| **Data Object** | `Agent` (matricule, nom, prénom, NIR, etc.) | Table `etat_civil`. |
| **Data Object** | `MiniCV` (agrégat d’affectations, situation familiale, etc.) | Assemblage via plusieurs adapters. |
| **Data Object** | `Rapport5`, `RapportActe`, `Rapport19‑22` | Modèles POJO + `*ToArrayAdapter`. |
| **Data Store** | PostgreSQL 9+ (schéma `ado_recette`) | Scripts `ado_create_table_1.0.0.sql`, index `nudoss`. |
| **Data Store** | `journal` (historisation) | Table `journal`. |
| **Artifact** | `JRXML` templates (ex. `ZQ11_Mouvement01.jrxml`) | Ressources `src/main/resources/jreports`. |
| **Artifact** | `Assembly ZIP` (scripts, docs) | `ado-database/assembly.xml`, `ado-doc/assembly.xml`. |

---

## 6️⃣ Acteurs et rôles  

| Lane (BPMN) | Rôle métier | Responsabilités | Compétences |
|-------------|-------------|----------------|-------------|
| **Utilisateur** | Agent‑public / fonctionnaire | Saisir critères, consulter dossiers, télécharger rapports. | Connaissance du SIRH, exigences de confidentialité. |
| **FiltreCerbere** | Service d’authentification (SSO) | Authentifier l’utilisateur, vérifier le profil unique. | Gestion des tokens SAML/OIDC, mapping LDAP. |
| **Controller** | `*Controller` (Spring MVC) | Recevoir la requête, valider les paramètres, appeler le service. | Java Spring, validation (`@Valid`). |
| **Service** | `*ServiceImpl` (ex. `AgentServiceImpl`) | Appliquer la logique métier, orchestrer les adapters, gérer les exceptions. | Java, Spring, connaissance du domaine RH. |
| **Repository** | Spring Data JPA (`*RepositoryI`) | Accéder aux tables PostgreSQL, exécuter les requêtes SQL. | JPA, optimisation de requêtes. |
| **JasperService** | Service de génération de rapports | Convertir les objets en tableaux, appeler JasperReports, gérer les flux de sortie. | JasperReports, gestion de fichiers binaires. |
| **Database** | PostgreSQL | Stocker les entités, garantir l’intégrité référentielle, fournir les index. | Administration PostgreSQL, optimisation d’index. |

---

## 7️⃣ Performances et indicateurs (KPIs)

| Indicateur | Formule | Objectif | Seuil d’alerte |
|------------|---------|----------|----------------|
| **Temps moyen de réponse (TMR)** | Σ (duration de toutes les requêtes) / N | < 2 s (hors génération PDF) | > 5 s |
| **Taux d’erreur HTTP** | (nb 5xx / total req) × 100 | < 0,5 % | > 2 % |
| **Nombre de recherches d’agents/jour** | nb `GET /agents` | ≥ 200 | < 50 |
| **Durée de génération PDF** | temps entre appel Jasper et fin de stream | < 3 s | > 10 s |
| **Taux de conformité journalisation** | (nb requêtes avec journal / total requêtes) × 100 | 100 % | < 100 % |
| **Espace journal (GB)** | Σ taille entries | ≤ 5 GB (90 jours) | > 5 GB → déclencher purge anticipée |

*Les KPI seront mesurés via **Spring Actuator** + **Prometheus/Grafana**.*

---

## 8️⃣ Gestion des exceptions  

| Événement de bordure | Type | Scénario | Action |
|------------------------|------|----------|--------|
| **Boundary Timer** (rapport > 10 s) | `Timer` | Timeout du service Jasper | Retourner `504 Gateway Timeout` + message « Report generation timeout ». |
| **Boundary Error** (DAO exception) | `Error` | Erreur SQL / violation contrainte | Log `ERROR`, lancer `RuntimeException` → HTTP `500`. |
| **Boundary Escalation** (profil multiple) | `Escalation` | `MultipleProfilsException` détectée | Retourner `403 Forbidden` avec texte explicite. |
| **Boundary Cancel** (user abort) | `Cancel` | Client annule la requête (Ctrl‑C) | Fermer les streams, nettoyer les ressources temporaires. |
| **Boundary Compensation** (purge partielle) | `Compensation` | Erreur lors de la purge (verrou) | Rollback transaction, notifier l’administrateur (email). |

---

## 9️⃣ Sous‑processus et réutilisation  

| Sous‑processus | Description | Points d’appel |
|----------------|-------------|----------------|
| **SP‑Adaptateur MiniCV** | Convertit l’ensemble des entités liées (affectations, enfants, quotités…) en tableau `String[]`. | `P‑102` (detail agent), `P‑103` (rapports). |
| **SP‑Journalisation** | Création d’une entrée `Journal` avant chaque réponse. | `P‑101`, `P‑102`, `P‑103`. |
| **SP‑Authentification** | FiltreCerbere – vérification du token SSO. | Tous les processus (gateways d’autorisation). |
| **SP‑Purge** | Suppression périodique des logs > 90 jours. | Scheduler (`P‑105`). |

> **Call‑Activity** : `Call Activity` dans les diagrammes (ex. `SP‑Authentification`).

---

## 🔟 Matrice de traçabilité  

| Exigence CCF | Processus BPMN | Tâche(s) | Scénario de test |
|--------------|----------------|----------|-------------------|
| **EX‑001** – Recherche agents selon critères | **P‑101** | `taskParse`, `taskQuery` | Recherche avec `motif='M'`, `bornAfter='1970-01-01'`. |
| **EX‑002** – Accès détaillé uniquement aux agents du snapshot | **P‑102** | `taskValidate`, `taskGet` | Recherche matricule présent dans `etat_civil` mais absent de `renoirh`. |
| **EX‑003** – Génération PDF du Rapport 5 | **P‑103** | `taskFetch`, `taskAdapter`, `taskJasper` | Appel `/reports/5?matricule=12345` → PDF non‑vide. |
| **EX‑004** – Journalisation systématique | **P‑104** | `taskCreate`, `taskInsert` | Vérifier que chaque appel crée une ligne dans `journal`. |
| **EX‑005** – Purge des entrées > 90 j | **P‑105** | `taskCalc`, `taskDelete` | Simuler date = 2026‑04‑27, vérifier suppression des lignes antérieures à 2025‑01‑27. |
| **EX‑006** – Refus d’accès si profil multiple | **P‑106** | `taskValidate` (FiltreCerbere) | Simuler token avec deux profils → 403. |

---

## 1️⃣1️⃣ Validation et conformité  

### 11.1 Checklist BPMN  

- [x] Tous les flux ont une source et une cible.  
- [x] Une unique activité de début (`Start Event`) par processus.  
- [x] Au moins une activité de fin (`End Event`).  
- [x] Aucun **gateway** orphelin (tous les chemins convergent).  
- [x] Labels des passerelles explicites (`FiltreCerbere autorise ?`).  
- [x] Nomenclature cohérente (`P‑xxx`, `EX‑xxx`).  

### 11.2 Niveaux de conformité BPMN  

| Niveau | Caractéristiques | BPMN applicable |
|--------|------------------|-----------------|
| **Descriptive** | Diagrammes simples (Recherche, Détail). | ✅ |
| **Analytic** | Inclusion des sous‑processus (Adapters, Journal). | ✅ |
| **Common Executable** | Tous les modèles utilisent des **Message Events** (`HTTP GET/POST`) et **Service Tasks** (DAO, Jasper). | ✅ (exécutable par moteur Camunda, Flowable…). |

---

## 1️⃣2️⃣ Implémentation et exécution  

### 12.1 Maturité processus  

| Niveau | Caractéristiques | BPMN applicable |
|--------|------------------|-----------------|
| 1 – Initial | Ad‑hoc, pas de doc. | – |
| 2 – Managed | Documenté, scripts SQL versionnés. | ✅ (Descriptive). |
| 3 – Defined | Standardisé, sous‑processus réutilisables. | ✅ (Analytic). |
| 4 – Quantified | Mesure KPI, monitoring. | ✅ (Common Executable). |
| 5 – Optimized | Boucle d’amélioration continue (CI/CD, tests de charge). | ✅ (Common Executable + automatisation). |

### 12.2 Intégration système  

| Élément | Technologie cible | Points d’intégration |
|---------|-------------------|----------------------|
| **Moteur BPMN** | **Camunda 7.x** (ou **Flowable**) | Déploiement des diagrammes BPMN (`*.bpmn.xml`). |
| **Base de données** | PostgreSQL 9+ (script d’assemblage). | `flyway` ou `liquibase` pour appliquer les scripts. |
| **JasperReports** | `jasperreports‑6.x` | `IJasperService` expose les API BPMN `Service Task`. |
| **Sécurité** | SSO Cerbere (SAML) | `FiltreCerbere` intégré comme **Task** « Validate Token ». |
| **Monitoring** | Spring Actuator + Prometheus | Exposition des métriques KPI. |
| **CI/CD** | GitLab CI (fichier `.gitlab-ci.yml` déjà présent) | Build Maven, tests, déploiement Docker + Helm (K8s). |

---

## 1️⃣3️⃣ Annexes  

### 13.1 Glossaire (complément)  

| Terme | Définition |
|-------|------------|
| **ReHucit** | Système d’information RH historique (avant RenoiRH). |
| **RenoiRH** | Nouveau SIRH du ministère, successeur de ReHucit. |
| **Cerbere** | Service d’authentification interne (SSO). |
| **JasperReports** | Moteur de génération de rapports (PDF, XLS, …). |
| **Mini‑CV** | Vue synthétique du dossier agent (identité, affectations, quotités). |
| **DACP** | Données à caractère personnel (RGPD). |
| **DICT** | Disponibilité, Intégrité, Confidentialité, Traçabilité. |
| **NIR** | Numéro d’Inscription au Répertoire (sécurité sociale). |

### 13.2 Références  

| Document | Lien / Référence |
|----------|------------------|
| **ADO‑Documentation‑technique.md** | Description fonctionnelle, requêtes SQL. |
| **ADO‑wiki.md** (home, DAT, etc.) | Contexte métier, exigences de sécurité. |
| **ADO‑wikisi.md** | Fiche d’application, métadonnées, contact. |
| **scripts SQL** (`ado‑database/scripts/*.sql`) | Modélisation du schéma et fonctions. |
| **JasperTemplates** (`src/main/resources/jreports/*.jrxml`) | Modèles de rapports. |
| **.gitlab-ci.yml** | Pipeline CI/CD. |
| **pom.xml** (multi‑module) | Gestion des dépendances, plugins Maven. |

---

> **Ce CCF** fournit la description fonctionnelle, les règles métier, les KPI, la matrice de traçabilité ainsi que les diagrammes BPMN nécessaires à la mise en œuvre, la validation et l’évolution de l’application **ADO** dans le respect des exigences de la norme ISO/IEC 19510 et des contraintes de sécurité, de confidentialité et de traçabilité.