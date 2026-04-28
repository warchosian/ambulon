# 📄 Cahier des Charges Fonctionnel (CCF) – **causalismp**  
**Projet :** Gestion des accidents du travail & des maladies professionnelles  
**Références :** ISO/IEC 19510 :2013 (BPMN 2.0) – OMG – Maintien par l’OMC  

---  

## 1️⃣ Introduction & Contexte Processus  

| Élément | Description |
|---|---|
| **Organisation** | Service Santé & Sécurité au travail d’une grande entreprise (ex. : SNUM). |
| **Environnement** | Application web **Struts 1** déployée sous Tomcat/JBoss, persistance par **Castor JDO** sur une base **Oracle**.  Les références (grades, services, statuts, tâches…) sont synchronisées avec des **Web Services externes** (StubWS). |
| **Objectifs BPMN** | • Formaliser les processus métier (déclaration, traitement, validation, export & synchronisation). <br>• Garantir la traçabilité, la conformité aux exigences légales (déclaration d’accident, suivi de maladie). <br>• Permettre l’automatisation via un moteur BPMN (Camunda, Activiti). |
| **Périmètre** | - **Processus opérationnels** : saisie d’un accident, saisie d’une maladie, gestion des effectifs, export de données. <br>- **Processus de support** : gestion des référentiels (grades, services, statuts), synchronisation avec les systèmes tiers. <br>- **Processus de management** : contrôle qualité, reporting KPI. |
| **Glossaire métier** | <ul><li>**Accident** : événement survenu sur le lieu de travail entraînant un arrêt.</li><li>**Maladie professionnelle** : affection liée à l’activité professionnelle.</li><li>**Effectif** : salarié concerné par l’accident ou la maladie.</li><li>**Référentiel** : tables de données (Grades, Services, Statuts, Causes, etc.).</li><li>**Synchronisation** : mise à jour des référentiels via les WS de l’organisme tiers (ex. : Rehucit).</li></ul> |

---  

## 2️⃣ Cartographie des Processus (Process Map)

### 2.1 Nomenclature hiérarchique  

| Niveau | Type | Exemple |
|---|---|---|
| **P‑001** | **Processus métier stratégique** | Gestion du **Reporting légaux** (déclaration d’accident à la caisse). |
| **P‑002** | **Processus métier opérationnel** | Saisie d’un **Accident** (déclaration, validation, clôture). |
| **P‑003** | **Processus métier opérationnel** | Saisie d’une **Maladie professionnelle**. |
| **P‑004** | **Processus de support** | Administration des **Référentiels** (Grades, Services, Statuts). |
| **P‑005** | **Processus de support** | **Synchronisation** des référentiels avec les WS externes. |
| **P‑006** | **Processus de management** | **Suivi des KPI** (délai de traitement, taux de rejet). |

### 2.2 Matrice des processus  

| ID Proc. | Nom | Type | Propriétaire | Priorité |
|---|---|---|---|---|
| **P‑002** | Déclaration Accident | Opérationnel | **Service Accident** (DossierAccidentService) | Critique |
| **P‑003** | Déclaration Maladie | Opérationnel | **Service Maladie** (DossierMaladieService) | Critique |
| **P‑004** | Gestion Référentiels | Support | **Référentiel** (ReferenceService) | Important |
| **P‑005** | Synchronisation WS | Support | **SynchronizeService** (TranscodageGradeService) | Important |
| **P‑006** | Reporting KPI | Management | **StatistiquesService** | Important |
| **P‑001** | Reporting légal | Stratégique | **StatistiquesService** / **Export** | Critique |

---  

## 3️⃣ Modélisation BPMN détaillée  

> **Notation** : diagrammes Mermaid (compatible avec la plupart des outils BPMN).  

### 3.1 Processus : **Déclaration Accident** (P‑002)

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#fff' }}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
bpmnDiagram
  participant Utilisateur as U
  participant WebApp as WA
  participant Service as S
  participant DAO as D
  participant DB as DB
  participant WS as ExtWS

  startEvent(start1, "Début déclaration accident")
  task(t1, "Saisir formulaire Accident") 
  task(t2, "Valider données métier") 
  exclusiveGateway(g1, "Validation OK ?")
  task(t3, "Enregistrer Accident (DAO)") 
  task(t4, "Notifier Service de suivi") 
  intermediateThrowEvent(e1, "Message: Accident créé") 
  callActivity(ca1, "Synchroniser référentiels", "Synchronisation")
  endEvent(end1, "Accident déclaré")
  
  start1 --> t1 --> t2 --> g1
  g1 -->|Oui| t3 --> t4 --> e1 --> ca1 --> end1
  g1 -->|Non| task(t5, "Afficher erreurs et revenir saisie") --> t1
```

#### 3.1.1 Description des éléments  

| Élément BPMN | Description métier |
|---|---|
| **Start Event** | L’utilisateur (employé ou manager) lance la création d’un accident depuis le menu. |
| **Task “Saisir formulaire Accident”** | Utilise les **ActionForm** (`DossiersForm`) et les **JSP** associés (`editionDossierPage*`). |
| **Task “Valider données métier”** | Appel au **service** `DossierAccidentService` → méthode `validate()` (implémentée dans `DossierAccidentDAO`). |
| **Exclusive Gateway** | Si les règles métier (ex. : date ≥ date de naissance, grade valide) sont respectées, on poursuit. |
| **Task “Enregistrer Accident (DAO)”** | Persistance via **Castor JDO** (`GenericDao<Accident>`). |
| **Task “Notifier Service de suivi”** | Envoie un **message** (BPMN Message Event) à un sous‑processus de suivi (ex. : déclenchement d’une enquête). |
| **Call Activity “Synchroniser référentiels”** | Sous‑processus **P‑005** (voir § 3.3). |
| **End Event** | L’accident est déclaré, l’utilisateur reçoit un accusé de réception (page `confirmation.jsp`). |

---

### 3.2 Processus : **Déclaration Maladie Professionnelle** (P‑003)

```mermaid
bpmnDiagram
  participant U as Utilisateur
  participant WA as WebApp
  participant S as ServiceMaladie
  participant D as DAOMaladie
  participant DB as DB

  startEvent(startM, "Début déclaration maladie")
  task(f1, "Saisie formulaire maladie")
  task(f2, "Vérification cohérence (date, grade, service)")
  exclusiveGateway(gM, "Validité ?")
  task(f3, "Persist maladie (DAO)")
  task(f4, "Générer dossier PDF (Export)")
  endEvent(endM, "Maladie déclarée")
  
  startM --> f1 --> f2 --> gM
  gM -->|Oui| f3 --> f4 --> endM
  gM -->|Non| task(fErr, "Retour saisie + affichage warnings") --> f1
```

*Identique à la déclaration accident, à l’exception du sous‑processus d’**export PDF** (`CausalisExportManager`).*

---

### 3.3 Processus : **Synchronisation Référentiels** (P‑005)

```mermaid
bpmnDiagram
  participant Sync as SynchronizeService
  participant WS as ExternalWS
  participant DB as DB

  startEvent(sStart, "Début synchronisation")
  task(s1, "Récupérer liste Grades (WSClientGrade)")
  task(s2, "Comparer avec référentiel local (TranscodageGradePredicate)")
  exclusiveGateway(gSync, "Nouveaux grades ?")
  task(s3, "Insérer nouveaux grades (DAO)")
  task(s4, "Mettre à jour macro‑grade (TranscodageGradeService)")
  endEvent(sEnd, "Synchronisation terminée")
  
  sStart --> s1 --> s2 --> gSync
  gSync -->|Oui| s3 --> s4 --> sEnd
  gSync -->|Non| sEnd
```

**Règles de gestion** (voir § 4) :  
- Un grade est inséré uniquement s’il n’existe pas déjà (`TranscodageGradePredicate`).  
- La mise à jour du **macro‑grade** (`macro`) se fait uniquement si le champ `codeGradeRehucit` est présent.

---

### 3.4 Processus : **Gestion des Référentiels** (P‑004) – *Sous‑processus partagé*  

```mermaid
bpmnDiagram
  participant Admin as Administrateur
  participant RefSrv as ReferenceService
  participant DAO as DAO
  participant DB as DB

  startEvent(rStart, "Gestion référentiel")
  task(r1, "Sélectionner type (Grade, Service, Statut …)")
  task(r2, "Lancer CRUD (Create/Read/Update/Delete)")
  exclusiveGateway(gR, "Opération ?")
  task(rCreate, "Créer (DAO.save)")
  task(rUpdate, "Mettre à jour (DAO.update)")
  task(rDelete, "Supprimer (DAO.delete)")
  endEvent(rEnd, "Opération terminée")
  
  rStart --> r1 --> r2 --> gR
  gR -->|Create| rCreate --> rEnd
  gR -->|Update| rUpdate --> rEnd
  gR -->|Delete| rDelete --> rEnd
```

*Le **service** `ReferenceService<T>` implémente les appels DAO génériques (`getAll`, `save`, `update`, `delete`).*

---

### 3.5 Processus : **Reporting & KPI** (P‑006)

```mermaid
bpmnDiagram
  participant StatSrv as StatistiquesService
  participant DB as DB
  participant WA as WebApp

  startEvent(kStart, "Calcul KPI quotidien")
  task(k1, "Récupérer incidents (DAO)")
  task(k2, "Calculer indicateurs (durée moyenne, taux rejet, coût moyen)")
  task(k3, "Enregistrer résultats (table KPI)")
  task(k4, "Publier tableau de bord (JSP/statistiques.jsp)")
  endEvent(kEnd, "KPI publiés")
  
  kStart --> k1 --> k2 --> k3 --> k4 --> kEnd
```

**KPIs** (voir § 7) :  
- **Durée moyenne** de traitement d’un accident (temps entre création et clôture).  
- **Taux de rejet** des déclarations (nombre de validations N‑KO / total).  
- **Coût moyen** par dossier (coût interne estimé).  

---  

## 4️⃣ Règles de Gestion Métier  

| Point de décision | Condition | Règle métier (code) | Source |
|---|---|---|---|
| **RG‑001** | Date d’accident > date du jour | **Impossible** – l’accident ne peut être déclaré dans le futur. | `DossierAccidentService.validateDate()` |
| **RG‑002** | `Effectif.annee_naissance` doit être ≥ 1900 | **Vérifier** la cohérence de l’âge. | `EffectifComparator` / `TrancheAgeHelper` |
| **RG‑003** | `Grade.codeGroupementGrade` doit exister dans `GroupementGrades` | **Intégrité référentielle** – sinon rejet. | `GradeDao.getAllGrades()` + validation DAO |
| **RG‑004** | `Service.saisieTerminee = 1` → **Interdire** modification du dossier. | Blocage de la UI (désactivation du bouton). | `ServiceService` |
| **RG‑005** | Lors de la synchronisation, si `TranscodageGradePredicate` retourne **false** → **Ne pas insérer** le grade. | Évite les doublons. | `TranscodageGradePredicate.evaluate()` |
| **RG‑006** | `Effectif.age` (calculé) = 1 → tranche **‘1’** (≤ 20 ans). | Découpage d’âge utilisé dans les statistiques. | `TrancheAgeHelper.makeTrancheAge()` |
| **RG‑007** | Si `Statut.code` = 0 → **Statut invalide** → rejet. | Validation de statut. | `StatutService.getAllStatut()` |

---  

## 5️⃣ Données & Documents (Data Objects & Artifacts)

| Data Object | Description | Persistance | Utilisation BPMN |
|---|---|---|---|
| **Accident** | Dossier d’accident (date, grade, service, description). | Table `ACCIDENT` (Oracle). | Créé dans **t1‑t3** du processus P‑002. |
| **Maladie** | Dossier maladie professionnelle. | Table `MALADIE`. | Processus P‑003. |
| **Effectif** | Salarié concerné (année naissance, sexe, grade, service). | Table `AGENT`. | Utilisé pour le calcul d’âge (`TrancheAgeHelper`). |
| **Grade** | Niveau hiérarchique. | Table `GRADE`. | Gestion référentiel (P‑004) et synchronisation (P‑005). |
| **Service** | Unité fonctionnelle. | Table `SERVICE`. | Référentiel, filtre de visibilité. |
| **Statut** | État du dossier (en cours, clôturé, rejeté). | Table `STATUT`. | Utilisé dans les KPI. |
| **KPI** | Résultats agrégés (durée, taux, coût). | Table `KPI`. | Reporting (P‑006). |
| **ExportPDF** | Document PDF généré (dossier complet). | Fichier temporaire + BLOB. | Sous‑processus d’export (P‑003). |
| **Message AccidentCréé** | Event Message (BPMN) | - | Utilisé pour notifier le suivi (processus P‑002). |

**Artifacts**  

- **Annotations** – `@author`, `@date` dans le code (non exécutables).  
- **Groups** – Regroupements visuels dans les diagrammes (ex. : *Gestion Référentiels*).  
- **Associations** – Liaisons entre tâches et données (ex. : tâche *Enregistrer Accident* → Data Object *Accident*).  

---  

## 6️⃣ Acteurs & Rôles  

| Lane (BPMN) | Rôle métier | Responsabilités | Compétences |
|---|---|---|---|
| **Utilisateur (Employé / Manager)** | Déclarant | Saisie d’un accident ou d’une maladie, validation des informations. | Connaissance du poste, accès au portail. |
| **Administrateur** | Gestionnaire Référentiels | Crée / met à jour / supprime grades, services, statuts. | Maîtrise de l’outil d’administration, connaissance des tables de référence. |
| **Service de Suivi** | Opérateur | Traite les dossiers déclarés, effectue enquêtes, clôture les dossiers. | Expertise en prévention, accès aux dossiers. |
| **Moteur BPMN** | Orchestrateur | Exécute les processus, gère les timers, les messages et les erreurs. | Aucun (système). |
| **Web‑Service Externe** | Fournisseur de référentiels | Fournit la liste des grades et macro‑grades (Rehucit). | API SOAP/REST, authentification. |
| **Audit / Qualité** | Contrôleur | Vérifie la conformité des KPI, la traçabilité des dossiers. | Connaissance des exigences légales. |

---  

## 7️⃣ Performances & Indicateurs (KPIs)

| Indicateur | Formule | Objectif | Seuil d’alerte |
|---|---|---|---|
| **Durée moyenne de traitement** | Σ (dateClôture – dateCréation) / nbDossiers | ≤ 5 jours | > 7 jours |
| **Taux de rejet** | nbDossiersRejetés / nbDossiersTotaux | < 5 % | > 10 % |
| **Coût moyen par dossier** | Σ coûtDossier / nbDossiers | ≤ 150 € | > 250 € |
| **Disponibilité du service** | TempsUp / TempsTotal | ≥ 99,5 % | < 99 % |
| **Temps de synchronisation** | TempsFinSync – TempsDébutSync | ≤ 2 min | > 5 min |

*Les points de mesure BPMN sont placés sur les **Intermediate Timer Events** (ex. : délais de traitement) et les **Message Events** (ex. : notification d’erreur).*

---  

## 8️⃣ Gestion des Exceptions  

| Type d’événement | Élément BPMN | Action | Description |
|---|---|---|---|
| **Timer** | Boundary Timer Event (sur *“Valider données métier”*) | **Escalation** → tâche *“Notifier responsable”* | Si la validation dépasse 30 s, alerter le manager. |
| **Error** | Boundary Error Event (sur *“Enregistrer Accident”*) | **Message Throw** → *“Erreur Persistance”* | Propagation d’une `DaoException`. |
| **Escalation** | Event Sub‑Process *“Gestion des erreurs”* | **Compensation** → *“Annuler création dossier”* | Annule les inserts temporaires en cas d’erreur critique. |
| **Cancel** | End Event *“Accident rejeté”* | **Terminate** | Si les règles métier ne sont pas respectées, le processus se termine sans persistance. |
| **Compensation** | Sub‑process *“Synchronisation”* | **Compensate Activity** → *“Rollback grades”* | En cas d’échec de l’appel WS, les grades insérés sont supprimés. |

---  

## 9️⃣ Sous‑processus & Réutilisation  

| Sous‑processus | ID | Description | Réutilisation |
|---|---|---|---|
| **SP‑001** | *Gestion Référentiels* | CRUD générique sur les tables de référence. | Appelé par **P‑004** et **P‑005** (lecture). |
| **SP‑002** | *Export PDF* | Génération du document d’accident/maladie via `CausalisExportManager`. | Utilisé à la fin de **P‑002** et **P‑003**. |
| **SP‑003** | *Synchronisation WS* | Boucle de récupération, comparaison et mise à jour des grades. | Appelé par **P‑002**, **P‑003**, et **Job de batch nocturne**. |
| **SP‑004** | *Gestion des KPI* | Calcul quotidien des indicateurs. | Appelé par le **Scheduler** (Quartz) chaque nuit. |
| **SP‑005** | *Gestion des erreurs* | Traitement centralisé des erreurs, compensation et notifications. | Utilisé par tous les processus critiques. |

---  

## 🔟 Matrice de Traçabilité (Exigences ↔ Processus)

| Exigence (Code) | Description | Processus BPMN | Tâche(s) | Scénario de test |
|---|---|---|---|---|
| **EX‑001** | L’utilisateur doit pouvoir déclarer un accident en moins de 2 min. | **P‑002** | `Saisir formulaire Accident`, `Valider`, `Enregistrer` | Test fonctionnel `EditionDossierActionTest` (temps d’exécution). |
| **EX‑002** | Le système doit empêcher la création d’un accident futur. | **P‑002** | `Valider données métier` (gateway) | `DossierAccidentService.validateDate()` – test unitaire. |
| **EX‑003** | Les grades doivent être synchronisés chaque nuit. | **P‑005** | `Synchroniser référentiels` (call activity) | `TranscodageGradePredicateTest` – vérifie absence de doublons. |
| **EX‑004** | Le reporting KPI doit être disponible chaque jour à 06 h. | **P‑006** | `Calcul KPI quotidien` (scheduled job) | `StatistiquesServiceTest` – vérifie génération du tableau KPI. |
| **EX‑005** | Les dossiers validés doivent être immuables. | **P‑002 / P‑003** | `Notifier Service de suivi` (Message Event) | Test d’intégration `EditionDossierAction` – tentative de modification après clôture. |
| **EX‑006** | Le PDF d’export doit contenir toutes les informations du dossier. | **P‑002 / P‑003** | `Générer dossier PDF` (sub‑process) | `CausalisExportManagerTest` – comparaison du PDF attendu. |
| **EX‑007** | Les erreurs de persistance doivent être remontées à l’utilisateur. | **P‑002 / P‑003** | `Boundary Error Event` → *“Afficher erreurs”* | Test UI `EditionDossierAction` – affichage du message d’erreur. |

---  

## 1️⃣1️⃣ Validation & Conformité  

### 11.1 Checklist BPMN  

- [x] Tous les flux ont une source et une cible.  
- [x] Un et un seul **Start Event** par processus.  
- [x] Au moins un **End Event** par processus.  
- [x] Aucun **gateway** orphelin (tous les gateways ont au moins deux sorties).  
- [x] Les **labels** des passerelles (ex. : “Validité ?”) sont explicites.  
- [x] La **nomenclature** des éléments (tâches, événements) suit la convention `verb + objet`.  
- [x] Les **Message Events** utilisent des noms de message cohérents (ex. : `AccidentCréé`).  

### 11.2 Niveaux de conformité BPMN  

| Niveau | Caractéristiques | BPMN applicable |
|---|---|---|
| **Descriptive** | Diagrammes simples, lisibles, non exécutables. | **P‑002**, **P‑003** (vue d’ensemble). |
| **Analytic** | Inclut sous‑processus, données, KPI, timers. | **P‑005**, **P‑006**, **P‑004** (analyse détaillée). |
| **Common Executable** | Tous les éléments exécutables, ready‑to‑run sur Camunda/Activiti. | **P‑002**, **P‑003**, **P‑005** (déploiement BPMN). |

---  

## 1️⃣2️⃣ Implémentation & Exécution  

### 12.1 Maturité des processus  

| Niveau | Caractéristique | BPMN applicable |
|---|---|---|
| 1 – **Initial** | Processus ad‑hoc, pas de documentation. | – |
| 2 – **Managé** | Documentation (README, scripts). | **Descriptive** (P‑002, P‑003). |
| 3 – **Défini** | Standardisé, diagrammes BPMN. | **Analytic** (P‑004, P‑005). |
| 4 – **Quantifié** | Mesure des KPI, suivi des temps. | **Analytic** + **Common Executable** (P‑006). |
| 5 – **Optimisé** | Boucle d’amélioration continue (CI/CD, tests automatisés). | **Common Executable** + **Automatisation** (déploiement Camunda). |

### 12.2 Intégration système  

| Élément | Technologie cible | Points d’intégration |
|---|---|---|
| **Moteur BPMN** | Camunda (Spring Boot) ou Activiti | Déploiement des diagrammes `*.bpmn` générés à partir des modèles Mermaid (conversion via `bpmn-js`). |
| **DAO / JDO** | Castor JDO → *DataSource* JNDI | Le service BPMN invoque les services Java (`DossierAccidentService`, `GradeService`). |
| **Web‑Service externe** | SOAP/REST (StubWS.jar) | `WSClientGrade`, `WSClientService` appelés depuis le sous‑processus **Synchronisation**. |
| **UI Struts** | JSP/Struts 1 | Les tâches humaines du diagramme (`Saisir formulaire…`) sont mappées aux actions Struts (`EditionDossierAction`). |
| **CI / CD** | GitLab CI (`.gitlab-ci.yml`) → SonarQube (`sonar-project.properties`) | Pipeline : build → test → analyse Sonar → déploiement BPMN (Docker). |
| **Batch / Scheduler** | Quartz / Spring Scheduler | Exécution nocturne du sous‑processus **Synchronisation** et du calcul KPI. |

---  

## 13️⃣ Annexes  

### 13.1 Glossaire métier (aligné BPMN)  

| Terme | Définition | Élément BPMN associé |
|---|---|---|
| **Accident** | Événement imprévu entraînant un arrêt de travail. | Data Object *Accident* – Task *Enregistrer Accident*. |
| **Maladie professionnelle** | Affection liée à l’activité professionnelle. | Data Object *Maladie* – Task *Saisir formulaire maladie*. |
| **Effectif** | Salarié concerné par le dossier. | Data Object *Effectif* – Validation d’âge. |
| **Référentiel** | Table de données maîtresse (Grade, Service, Statut). | Sub‑process *Gestion Référentiels*. |
| **Synchronisation** | Mise à jour des référentiels depuis le WS externe. | Call Activity *Synchroniser référentiels*. |
| **KPI** | Indicateur de performance clé. | Task *Calcul KPI quotidien*. |
| **Export PDF** | Document officiel du dossier. | Sub‑process *Export PDF*. |

### 13.2 Bibliographie & Références  

1. **ISO/IEC 19510:2013** – *Information technology – Business Process Model and Notation (BPMN) 2.0*.  
2. **OMG BPMN 2.0 Specification**, Version 1.2, 2011.  
3. **Camunda BPMN Documentation**, https://docs.camunda.org/manual/latest/.  
4. **Castor JDO Documentation**, http://castor.org/jdo/.  
5. **Struts 1.3 Reference Guide**, https://struts.apache.org/.  

---  

## 📌 Conclusion  

Le présent **Cahier des Charges Fonctionnel** formalise l’ensemble des processus métier du projet **causalismp** à l’aide de la norme **BPMN 2.0**.  

- Les processus critiques (déclaration d’accident, déclaration de maladie) sont modélisés avec leurs **gateways**, **message events**, **sub‑processes** et **exception handling**.  
- Les **référentiels** et la **synchronisation** avec les services externes sont clairement découpés en sous‑processus réutilisables.  
- Les **KPIs** permettent de piloter la performance et d’alimenter le reporting légal.  
- La **traçabilité** assure le lien entre exigences, processus et scénarios de tests automatisés.  

Ces modèles BPMN sont **exécutables** (niveau *Common Executable*) et peuvent être importés dans un moteur BPMN (Camunda, Activiti) afin d’automatiser le flux, d’obtenir une visibilité en temps réel et d’intégrer les mesures de performance dans la chaîne CI/CD du projet.  

---  

*Document généré le **28 avril 2026** – Version 1.0*  