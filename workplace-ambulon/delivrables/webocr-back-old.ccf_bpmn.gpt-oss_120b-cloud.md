# 📄 Cahier des Charges Fonctionnel (CCF) – **webocr‑back‑old**  
*Modélisation BPMN – ISO/IEC 19510 :2013*  

> **Objectif** : Formaliser, structurer et rendre exécutable les processus métier du service back‑end OCR (extraction de texte à partir de documents PDF/Image) afin d’assurer la continuité, la traçabilité et la mesurabilité du système.  

---  

## 1️⃣ Introduction et contexte processus  

| Élément | Description |
|---|---|
| **Organisation** | Application **webocr‑back‑old** – service Node.js exposant une API REST utilisée par le front‑end *webocr‑front* et par le service d’authentification centralisé **CERBERE** (CAS). |
| **Environnement technique** | Docker‑Compose (PostgreSQL 13, Redis alpine), Node 16, Tesseract‑OCR (FR), ImageMagick, Poppler, Ghostscript. |
| **Objectifs de la modélisation BPMN** | • Uniformiser la compréhension fonctionnelle (développeurs, PO, auditeurs). <br>• Garantir la conformité aux exigences de sécurité (auth, session). <br>• Définir les points d’intégration (Redis, DB, CERBERE). <br>• Préparer la migration vers un moteur d’exécution BPMN (Camunda/Activiti). |
| **Périmètre** | Tous les points d’entrée de l’API : authentification, gestion de session, upload de fichiers, déclenchement OCR, récupération de documents, statistiques, planification du purge. Les scripts de build, CI/CD et la configuration Docker sont hors‑périmètre. |
| **Glossaire métier (extraits)** | <ul><li>**Document** – fichier PDF ou image stocké dans *uploads*.</li><li>**OCR Job** – tâche asynchrone qui transforme le document en texte.</li><li>**Statistiques** – agrégats (nb documents, nb jobs, temps moyen de traitement).</li><li>**Consentement TOS** – accord de l’utilisateur aux conditions d’utilisation.</li></ul> |

---  

## 2️⃣ Cartographie des processus (Process Map)

### 2.1 Nomenclature hiérarchique  

| Niveau | Type | Exemple de processus |
|---|---|---|
| **1** | **Stratégique** | *Gestion du service OCR* (définir SLA, gouvernance des données). |
| **2** | **Opérationnel** | *Authentification utilisateur*, *Upload & OCR*, *Téléchargement documents*, *Statistiques*, *Purge périodique*. |
| **2** | **Support** | *Gestion de session*, *Gestion des erreurs*, *Logging*. |
| **2** | **Management** | *Planification du cron*, *Supervision des workers*. |

### 2.2 Matrice de processus  

| ID Proc. | Nom | Type | Propriétaire | Priorité |
|---|---|---|---|---|
| **P‑001** | Authentification & Gestion du ticket CAS | Opérationnel | **Team Backend** | Critique |
| **P‑002** | Upload de fichier & lancement OCR | Opérationnel | **Team Backend** | Critique |
| **P‑003** | Téléchargement du document original | Opérationnel | **Team Backend** | Important |
| **P‑004** | Téléchargement du texte OCR | Opérationnel | **Team Backend** | Important |
| **P‑005** | Consultation des statistiques | Opérationnel | **Team BI** | Moyen |
| **P‑006** | Purge périodique des documents expirés | Support | **Team Ops** | Moyen |
| **P‑007** | Gestion de session (Redis) | Support | **Team Infra** | Important |
| **P‑008** | Gestion des erreurs & logging | Support | **Team Backend** | Important |
| **P‑009** | Planification du cron (purge) | Management | **Team Ops** | Moyen |

---  

## 3️⃣ Modélisation BPMN détaillée  

> **Notation** : PlantUML (BPMN) – compatible avec les moteurs Camunda/Activiti.  
> **Convention** : chaque diagramme représente un **niveau d’abstraction unique** (règle 1).  

### 3.1 Diagramme de collaboration – **P‑002 : Upload & OCR**  

```plantuml
@startuml
!define BPMN https://raw.githubusercontent.com/plantuml-stdlib/Cicon-PlantUML/master/bpmn
!includeurl BPMN

title Processus P‑002 – Upload de fichier & lancement OCR (Collaboration)

' Participants
|#LightBlue|Client Web (Front)|
|#LightGreen|WebOCR‑Back (API)|
|#LightYellow|Redis (Cache)|
|#LightCoral|PostgreSQL (DB)|
|#LightGray|Tesseract OCR Service|

'--- Client → API (Upload) -------------------------------------------------
|Client Web|
:POST /files (multipart)|
->|WebOCR‑Back| : uploadFile(file)

'--- API → Redis (Session check) -----------------------------------------
|WebOCR‑Back|
:validateSession()|
->|Redis| : GET sessionId

'--- API → DB (Persist metadata) -----------------------------------------
|WebOCR‑Back|
:storeDocumentMeta()|
->|PostgreSQL| : INSERT document (path, owner, status=QUEUED)

'--- API → OCR Service (Async) --------------------------------------------
|WebOCR‑Back|
:enqueueOCRJob()|
->|Tesseract OCR Service| : startJob(documentPath)

'--- OCR Service → DB (Result) ---------------------------------------------
|Tesseract OCR Service|
:process()|
->|PostgreSQL| : UPDATE document SET status=PROCESSED, ocrText=...

'--- API → Client (Response) -----------------------------------------------
|WebOCR‑Back|
:return 202 Accepted (jobId)|
->|Client Web|

@enduml
```

> **Notes**  
> * La tâche *enqueueOCRJob* est implémentée via **Bull / Kue** (non visible dans le code source mais présupposée).  
> * Les messages *GET/SET* vers Redis sont des **Message Events** (déclencheurs).  

---

### 3.2 Diagramme de processus – **P‑001 : Authentification**  

```plantuml
@startuml
!define BPMN https://raw.githubusercontent.com/plantuml-stdlib/Cicon-PlantUML/master/bpmn
!includeurl BPMN

title Processus P‑001 – Authentification CAS (Process Diagram)

start

:GET /auth/login;
:auth.validateTicket(ticket);
if (Ticket valide ?) then (yes)
  :Créer / rafraîchir session Redis;
  :Set cookie SESSION_COOKIE;
  :return 200 OK;
else (no)
  :return 401 Unauthorized;
endif

:GET /auth/ping;
if (session valide ?) then (yes)
  :return 200 OK;
else (no)
  :return 401 Unauthorized;
endif

:GET /auth/logout;
:Supprimer session Redis;
:Clear cookie;
:return 200 OK;

:GET /auth/consentToTos;
:Mettre à jour users.tosConsent = true;
:return 200 OK;

stop
@enduml
```

> **Règles métier** (voir § 4) :  
> *RB‑001* – Le ticket CAS doit être vérifié via le service **CERBERE_URL**.  
> *RB‑002* – Le consentement TOS ne peut être mis à jour que si la session est active.  

---

### 3.3 Diagramme de processus – **P‑006 : Purge périodique**  

```plantuml
@startuml
!define BPMN https://raw.githubusercontent.com/plantuml-stdlib/Cicon-PlantUML/master/bpmn
!includeurl BPMN

title Processus P‑006 – Purge des documents expirés (Cron)

start

:Timer Event (cron = PURGING_CRON);
:purgeOldDocuments() (src/scripts/purge.js);
partition DB {
  :SELECT id FROM documents WHERE processed=2 AND createdAt < NOW() - INTERVAL '30 days';
  :DELETE FROM documents WHERE id IN (...);
}
partition FS {
  :Supprimer fichiers physiques du répertoire uploads/ & converted/;
}
:Log résultat (nbDocsPurged);
stop
@enduml
```

> **Exception** : Si la connexion DB échoue → **Boundary Error Event** → notifier admin (mail).  

---

### 3.4 Diagramme de processus – **P‑005 : Statistiques**  

```plantuml
@startuml
!define BPMN https://raw.githubusercontent.com/plantuml-stdlib/Cicon-PlantUML/master/bpmn
!includeurl BPMN

title Processus P‑005 – Consultation des statistiques

start

:GET /files/statistics;
:service.getStatistics();
partition DB {
  :SELECT COUNT(*) AS totalDocs FROM documents;
  :SELECT COUNT(*) FILTER (WHERE status='PROCESSED') AS processedDocs;
  :SELECT AVG(processingTime) AS avgTime;
}
:Return JSON {totalDocs, processedDocs, avgTime};
stop
@enduml
```

---

### 3.5 Diagramme de collaboration – **P‑007 : Gestion de session (Redis)**  

```plantuml
@startuml
!define BPMN https://raw.githubusercontent.com/plantuml-stdlib/Cicon-PlantUML/master/bpmn
!includeurl BPMN

title Collaboration – Session Management (Redis)

|#LightBlue|Client|
|#LightGreen|WebOCR‑Back|
|#LightYellow|Redis|

Client -> WebOCR‑Back : Request (any endpoint, cookie)
WebOCR‑Back -> Redis : GET sessionId
alt Session exists
    Redis --> WebOCR‑Back : session data
    WebOCR‑Back --> Client : 200/OK
else Session missing
    Redis --> WebOCR‑Back : null
    WebOCR‑Back --> Client : 401 Unauthorized
end
@enduml
```

---  

## 4️⃣ Règles de gestion métier  

| Point de décision (Gateway) | Condition | Règle métier (RB‑xxx) | Source |
|---|---|---|---|
| **RB‑001** (Auth) | `ticket` reçu du client | Le ticket doit être validé via **CERBERE_URL** (CAS). | CERBERE spec |
| **RB‑002** (Consent) | Session active **AND** `userId` présent | Mettre à jour `users.tosConsent = true`. | Business rules |
| **RB‑003** (Upload) | Extension du fichier **IN** {`.pdf`, `.png`, `.jpg`} | Accepter upload, sinon `400 Bad Request`. | Documentation `helpers.getFileExtension` |
| **RB‑004** (OCR) | `document.status = QUEUED` | Lancer job OCR, passer `status = PROCESSING`. | Service `ocr.js` (non affiché) |
| **RB‑005** (Purge) | `document.createdAt < now - 30d` **AND** `status = PROCESSED` | Supprimer le document et ses fichiers associés. | `src/scripts/purge.js` |
| **RB‑006** (Statistiques) | Aucun filtre | Retourner agrégats globaux (`totalDocs`, `processedDocs`, `avgTime`). | `service.getStatistics` |

---  

## 5️⃣ Données et documents  

### 5.1 Objets de données (Data Objects)

| Data Object | Description | Persistance |
|---|---|---|
| **User** | `id`, `owner`, `tosConsent`, `sessionId` | **PostgreSQL** (`users` table) |
| **Document** | `id`, `originalName`, `path`, `status` (0 = queued, 1 = processing, 2 = processed), `ocrText`, `pages`, `processingTime`, `createdAt`, `owner` | **PostgreSQL** (`documents` table) |
| **OCRJob** | `jobId`, `documentId`, `state`, `startedAt`, `endedAt` | **Redis** (queue) + **PostgreSQL** (log) |
| **Session** | `sessionId`, `userId`, `expiresAt` | **Redis** (`connect-redis` store) |
| **Statistiques** | `totalDocs`, `processedDocs`, `avgProcessingTime` | Calculé à la volée (DB) |
| **LogEntry** | `timestamp`, `level`, `component`, `message` | **File** (`logs/`), éventuellement **ELK** |

### 5.2 Artifacts  

| Artifact | Usage |
|---|---|
| **Group** “Upload flow” | Regroupe les tâches d’upload, validation, persistance. |
| **Annotation** “Boundary Error – DB” | Sur le sous‑processus *Persist metadata*. |
| **Association** entre *Document* et *File System* (path) | Indique le lien physique. |

---  

## 6️⃣ Acteurs et rôles  

| Lane (BPMN) | Rôle métier | Responsabilités | Compétences |
|---|---|---|---|
| **End‑User** | Utilisateur final | Authentifier, uploader, consulter OCR | Navigation web |
| **Front‑End (WebOCR‑Front)** | Client HTTP | Envoi de requêtes, gestion du cookie | JavaScript/React |
| **WebOCR‑Back (API)** | Service back‑end | Orchestration des processus, appels aux services externes | Node.js, Express |
| **Auth Service (CERBERE)** | Service d’authentification CAS | Validation du ticket, génération de token | CAS / SSO |
| **Redis** | Cache de session | Stockage & récupération de sessions | In‑memory, TTL |
| **PostgreSQL** | DB relationnelle | Persistance des métadonnées, statistiques | SQL, transactions |
| **Tesseract OCR** | Moteur de reconnaissance | Extraction texte à partir d’images/PDF | OCR, français |

---  

## 7️⃣ Performances et indicateurs (KPIs)  

| Indicateur | Formule | Objectif | Seuil d’alerte |
|---|---|---|---|
| **Temps moyen de traitement OCR** | `AVG(processingTime)` (sec) | `< 15 s` | `> 30 s` |
| **Taux de succès d’upload** | `Nb uploads acceptés / Nb uploads totaux` | `≥ 99 %` | `< 95 %` |
| **Taux de rejet de ticket CAS** | `Nb tickets invalides / Nb tickets reçus` | `< 1 %` | `> 5 %` |
| **Durée du purge** | `Temps d’exécution du script purge` | `< 2 min` | `> 5 min` |
| **Disponibilité API** | `Uptime (minutes / total minutes)` | `≥ 99,5 %` | `< 99 %` |

### Points de mesure BPMN  

* **Time Event** (début du cron) → mesure `purgeDuration`.  
* **Message Event** (début OCR) → mesure `ocrStart‑>ocrEnd`.  
* **Boundary Error Event** (DB) → compteur `dbErrorCount`.  

---  

## 8️⃣ Gestion des exceptions  

| Scénario | Déclencheur | Événement de bordure (Boundary) | Gestion | Conséquence |
|---|---|---|---|---|
| **Timeout OCR** | Job > 5 min sans résultat | **Timer Boundary** sur *enqueueOCRJob* | Marquer le document `status = ERROR`; notifier admin | Re‑try possible |
| **Erreur DB** | `INSERT`/`UPDATE` échoue | **Error Boundary** sur *storeDocumentMeta* | Log `ERROR`; retourner `500`; rollback transaction | Transaction annulée |
| **Session expirée** | Cookie présent mais TTL dépassé | **Message Boundary** sur *validateSession* | Retour `401`; supprimer session Redis | Re‑login requis |
| **Fichier non supporté** | Extension non autorisée | **Error Boundary** sur *uploadFile* | Retour `400 Bad Request` avec message | Aucun stockage |
| **Purge échouée** | Connexion Redis/DB perdue | **Escalation Boundary** sur *purgeOldDocuments* | Envoi mail d’alerte; planifier retry | Purge reportée |

---  

## 9️⃣ Sous‑processus et réutilisation  

| Sous‑processus | Description | Réutilisé dans |
|---|---|---|
| **Validate Session** | Vérifie la présence et la validité d’une session Redis | Auth, Upload, Statistiques, Download |
| **Store Document Metadata** | Persistance du document + création d’un job OCR | Upload, Retry OCR |
| **Generate Statistics** | Agrégation des métriques | Dashboard, Reporting |
| **Purge Old Documents** | Suppression des documents expirés | Cron, Script `purge.js` |
| **Error Handling** | Capture, log et conversion en réponse HTTP | Tous les endpoints |

---  

## 🔟 Matrice de traçabilité (Exigences ↔ Processus)  

| Exigence CCF | Processus BPMN | Tâche(s) concernée(s) | Scénario de test |
|---|---|---|---|
| **EX‑AUTH‑001** – Authentifier via CAS | P‑001 | `auth.validateTicket` | Ticket valide → 200 OK |
| **EX‑UPLOAD‑001** – Accepter uniquement PDF/IMG | P‑002 | `upload.single` + `helpers.getFileExtension` | Upload .pdf → 202 ; .exe → 400 |
| **EX‑OCR‑001** – Lancer OCR dès upload | P‑002 | `enqueueOCRJob` | Vérifier `status=PROCESSING` dans DB |
| **EX‑STAT‑001** – Retourner statistiques agrégées | P‑005 | `service.getStatistics` | Vérifier JSON avec champs attendus |
| **EX‑PURGE‑001** – Supprimer documents > 30 j | P‑006 | `purgeOldDocuments` | Après 31 j, le doc n’est plus présent dans DB/FS |
| **EX‑SESSION‑001** – Timeout session 1 h | P‑007 | `session` middleware | Après 61 min, l’API renvoie 401 |
| **EX‑ERROR‑001** – Gestion centralisée des erreurs | P‑008 | `error-handler.js` | Provoquer une exception, vérifier log & code 500 |

---  

## 1️⃣1️⃣ Validation et conformité  

### 11.1 Checklist BPMN (avant livrable)  

- [ ] Tous les flux ont une source **et** une cible.  
- [ ] Un **et un seul** événement de début par diagramme.  
- [ ] Au moins **un** événement de fin par diagramme.  
- [ ] Pas de **gateway** orphelin (tout gateway a au moins deux sorties).  
- [ ] Libellés des passerelles explicites et alignés avec les règles métier (RB‑xxx).  
- [ ] Nomenclature des éléments (tasks, events) cohérente avec le glossaire.  
- [ ] Utilisation des **sub‑process** pour les parties récurrentes (Validate Session, Store Metadata).  

### 11.2 Niveaux de conformité BPMN  

| Niveau | Couverture | Exemple dans le CCF |
|---|---|---|
| **Descriptive** | Diagrammes simples, pas de données d’exécution. | `P‑001 Authentification` (événements, tâches). |
| **Analytic** | Ajout de **Data Objects**, **Gateways** conditionnelles, **Boundary Events**. | `P‑002 Upload & OCR` (Boundary Timer, Error). |
| **Common Executable** | Tous les éléments exécutables (Service Tasks, Message Flows) compatibles Camunda. | `P‑006 Purge` (Service Task *purgeOldDocuments*). |

---  

## 1️⃣2️⃣ Implémentation et exécution  

### 12.1 Maturité processus (CMMI‑like)  

| Niveau | Caractéristiques | BPMN applicable |
|---|---|---|
| 1 – **Initial** | Processus ad‑hoc, pas de doc. | – |
| 2 – **Managed** | Documentation basique (CCF). | **Descriptive** |
| 3 – **Defined** | Standardisation, réutilisation. | **Analytic** |
| 4 – **Quantified** | Mesure KPIs, monitoring. | **Analytic** + **Common Executable** (monitoring). |
| 5 – **Optimized** | Amélioration continue, automatisation complète. | **Common Executable** (déploiement Camunda). |

### 12.2 Intégration système  

| Composant | Technologie | Points d’intégration BPMN |
|---|---|---|
| **Moteur BPMN** | Camunda 7 (Spring Boot) ou Activiti | Déploiement des diagrammes `*.bpmn` (ex. `upload_ocr.bpmn`). |
| **Service REST** | Express / Node.js | **Service Tasks** (`service.getStatistics`, `ocr.startJob`). |
| **Redis** | `connect-redis` | **Message Events** (GET/SET session). |
| **PostgreSQL** | `pg` driver | **Data Store** (`documents`, `users`). |
| **Tesseract** | CLI via `child_process.exec` | **Service Task** `ocr.processDocument`. |
| **Cron** | `node-cron` (PURGING_CRON) | **Timer Event** (déclencheur périodique). |
| **Logging** | Winston (ou `logger.js`) | **Message Event** `logEntry`. |

> **Déploiement recommandé** :  
> 1. Convertir chaque sous‑processus en fichier BPMN séparé (ex. `upload_ocr.bpmn`).  
> 2. Utiliser **Camunda Modeler** pour ajouter **DMN** (rules RB‑001…RB‑006).  
> 3. Configurer les **connectors** HTTP/REST pour les appels externes (CERBERE, Tesseract).  
> 4. Activer **Process Engine Plugins** pour la collecte de métriques (KPIs).  

---  

## 📎 Annexes  

### A. Glossaire métier complet (extraits)  

| Terme | Définition |
|---|---|
| **Ticket CAS** | Jeton d’authentification fourni par le serveur SSO CERBERE. |
| **Job OCR** | Unité de travail asynchrone qui exécute Tesseract sur un document. |
| **Consentement TOS** | Accord explicite de l’utilisateur aux Conditions Générales d’Utilisation. |
| **Purge** | Suppression automatisée des documents traités depuis plus de 30 jours. |
| **Session Redis** | Identifiant de session stocké dans Redis avec TTL 1 h. |

### B. Références  

* ISO/IEC 19510 :2013 – Business Process Model and Notation (BPMN)  
* Camunda BPMN Execution Reference (v7) – https://docs.camunda.org/manual/latest/reference/bpmn20/  
* Node‑Express v4.x – https://expressjs.com/  
* Tesseract‑OCR – https://github.com/tesseract-ocr/tesseract  

---  

*Ce CCF est rédigé en conformité avec la norme ISO/IEC 19510 :2013 et prêt à être importé dans un moteur BPMN pour exécution ou analyse.*