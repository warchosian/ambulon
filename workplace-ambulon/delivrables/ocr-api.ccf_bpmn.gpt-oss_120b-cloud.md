# Cahier des Charges Fonctionnel (CCF) – **ocr‑api**  
**Norme** : ISO/IEC 19510:2013 – Business Process Model and Notation (BPMN)  
**Version** : 1.0 – 2026‑04‑28  

---  

## 1. Introduction et contexte processus  

| Élément | Description |
|---------|-------------|
| **Organisation** | *WarchoLife* – équipe *Ambulon* developpeur d’applications cloud‑native. |
| **Environnement** | Déploiement Docker (dev & prod) sur serveurs Linux, orchestration via `docker‑compose`. Services : <br>• **ocr‑api** (Node.js) <br>• **Redis** (cache & queue) <br>• **MinIO** (stockage d’objets) |
| **Objectifs de la modélisation BPMN** | - Formaliser le **flux métier** de la prise en charge d’une image OCR. <br>- Garantir la **traçabilité** des exigences fonctionnelles. <br>- Servir de base à l’**exécution** sur un moteur BPMN (Camunda, Activiti…). |
| **Périmètre** | - **Processus métier** de la requête OCR (ingestion, traitement, stockage, réponse). <br>- **Processus de support** d’infrastructure (déploiement, mise à jour, monitoring). |
| **Glossaire métier** | <ul><li>**Client** : application ou service appelant l’API REST `/ocr`.</li><li>**Image** : fichier (pdf, jpg, png) envoyé pour reconnaissance.</li><li>**Job OCR** : unité de travail traitée par Tesseract.</li><li>**Cache** : entrée Redis contenant le résultat déjà calculé.</li><li>**Bucket** : espace MinIO où sont stockées les images et les résultats.</li></ul> |

---  

## 2. Cartographie des processus (Process Map)  

### 2.1 Nomenclature des processus  

| Niveau | Classification | Exemple |
|--------|----------------|---------|
| **N1** | Processus métier **stratégiques** | Gestion du cycle de vie du produit OCR‑API |
| **N2** | Processus métier **opérationnels** | *P‑001 – Traitement d’une requête OCR* |
| **N2** | Processus **de support** | *P‑002 – Provisionnement de l’infrastructure Docker* |
| **N2** | Processus **de management** | *P‑003 – Monitoring & alerting* |

### 2.2 Matrice de processus  

| ID Processus | Nom | Type | Propriétaire | Priorité |
|--------------|-----|------|--------------|----------|
| **P‑001** | Traitement d’une requête OCR | Opérationnel | Lead Dév : Alex Dupont | Critique |
| **P‑002** | Provisionnement & mise à jour Docker | Support | Ops : Mia Leroy | Important |
| **P‑003** | Monitoring & alerting (Redis/MinIO) | Management | Ops : Mia Leroy | Moyen |
| **P‑004** | Gestion des secrets & variables d’environnement | Support | Sécurité : Nicolas Kahn | Important |

---  

## 3. Modélisation BPMN détaillée  

> **Convention** : chaque diagramme est exprimé en PlantUML (compatible BPMN 2.0).  
> Les **Pools** représentent les participants externes (Client, OCR‑API, Redis, MinIO).  

### 3.1 Diagramme de collaboration – *P‑001 – Traitement d’une requête OCR*  

```plantuml
@startuml
!define BPMN2 https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/BPMN2.puml
!includeurl BPMN2

title Collaboration – Traitement d’une requête OCR (P‑001)

|#LightBlue|Client|
|#LightGreen|OCR‑API|
|#LightYellow|Redis|
|#LightCoral|MinIO|

'--- Client → OCR‑API -------------------------------------------------
|Client|
start
:Envoi requête HTTP /ocr (image);
:Attendre réponse;
stop

'--- OCR‑API reçoit -------------------------------------------------
|OCR‑API|
start
:Receive HTTP request;
:Validate payload;
if (Image déjà en cache ?) then (yes)
  :Read result from Redis;
else (no)
  :Store image in MinIO (bucket “incoming”);
  :Create Job ID;
  :Publish Job ID to Redis (queue);
endif

:Wait for OCR result (Message Event);
:Return OCR JSON response;
stop

'--- Redis (queue / cache) -----------------------------------------
|Redis|
:Queue Job ID;
:Store result (key=JobID);
note right: Cache TTL = 24 h
stop

'--- MinIO (storage) -----------------------------------------------
|MinIO|
:Persist image;
:Persist OCR output (PDF/texte);
stop
@enduml
```

### 3.2 Diagramme de processus – *P‑001* (détail du flux interne OCR‑API)  

```plantuml
@startuml
!define BPMN2 https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/BPMN2.puml
!includeurl BPMN2

title Processus – Traitement interne OCR‑API (P‑001)

start
:Receive HTTP POST /ocr;
:Parse multipart/form‑data;
:Validate image format (pdf|jpg|png);
if (Image valide ?) then (yes)
  :Compute SHA‑256 hash;
else (no)
  :Throw Error (InvalidPayload);
  stop
endif

:Check Redis cache (hash);
if (Cache hit ?) then (yes)
  :Read OCR result from cache;
  :Send HTTP 200 (cached result);
  stop
else (no)
  :Upload image to MinIO (bucket “incoming”);
  :Create Job UUID;
  :Enqueue Job UUID in Redis (list “ocr‑jobs”);
  :Add Boundary Timer (30 s) **[Warning]**;
  :Wait for Message (Result) **[Message Event]**;
endif

:Receive Message “OCR‑Result” (payload);
:Persist result in Redis (cache);
:Send HTTP 200 (result);
stop

@enduml
```

### 3.3 Diagramme de choreography (optionnel) – *Interaction client ↔ OCR‑API*  

```plantuml
@startuml
!define BPMN2 https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/BPMN2.puml
!includeurl BPMN2

title Choreography – OCR Request / Response

participant Client
participant OCR_API
participant Redis
participant MinIO

Client -> OCR_API : POST /ocr (image)
OCR_API -> Redis : Check cache / enqueue job
OCR_API -> MinIO : Store image (if needed)
OCR_API -> Client : (Message) “Result” (async) 
@enduml
```

### 3.4 Diagramme de conversation (optionnel) – *Flux de messages*  

```plantuml
@startuml
!define BPMN2 https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/BPMN2.puml
!includeurl BPMN2

title Conversation – Messages entre participants

conversation "OCR Request" {
  message "POST /ocr" from Client to OCR_API
  message "Cache‑Check / Job‑Enqueue" from OCR_API to Redis
  message "Store‑Image" from OCR_API to MinIO
  message "OCR‑Result" from Redis to OCR_API
  message "HTTP 200 (JSON)" from OCR_API to Client
}
@enduml
```

---  

## 4. Règles de gestion métier  

| Point de décision | Condition | Règle métier (RB‑xxx) | Source |
|-------------------|-----------|------------------------|--------|
| **Gateway 1** (Cache hit ?) | `hash ∈ Redis` | **RB‑001** : Si le hash de l’image existe dans le cache, renvoyer le résultat sans traitement supplémentaire. | Spécif. fonctionnelle |
| **Gateway 2** (Image valide ?) | `mime ∈ {image/jpeg, image/png, application/pdf}` | **RB‑002** : Refuser toute autre extension avec code 400. | API‑Spec |
| **Gateway 3** (Timeout) | `elapsed > 30 s` | **RB‑003** : Générer un warning `OCR_TIMEOUT` et retourner le statut `202 Accepted` avec ID de job. | SLA interne |
| **Boundary Event** (Error) | `tesseract` renvoie code != 0 | **RB‑004** : Mapper l’erreur Tesseract → `500 Internal Server Error` + log détaillé. | Mapping d’erreur |
| **Gateway 4** (Result size) | `result.size > 5 Mo` | **RB‑005** : Stocker le résultat uniquement dans MinIO, renvoyer un lien pré‑signé. | Policy de stockage |

---  

## 5. Données et documents  

### 5.1 Objets de données  

| Data Object | Description | Persistance |
|-------------|-------------|-------------|
| **ImageBlob** | Fichier binaire reçu (PDF/JPG/PNG) | MinIO (bucket `incoming`) |
| **OCRResult** | JSON contenant texte, bounding‑boxes, confidence | Redis (cache) + MinIO (bucket `results`) |
| **JobID** | UUID du job OCR | Redis (liste `ocr‑jobs`) |
| **ImageHash** | SHA‑256 de l’image (clé de cache) | Redis (string) |
| **API‑Log** | Trace d’appels (timestamp, IP, status) | Fichier log (`/app/logs`) |

### 5.2 Artifacts  

| Artifact | Usage |
|----------|-------|
| **Group “Cache‑Management”** | Regroupe les tâches de lecture/écriture Redis. |
| **Annotation “Boundary Timer 30 s”** | Indique le délai maximal d’attente du résultat. |
| **Association** | Lie le **JobID** aux **Message Events** (Result). |

---  

## 6. Acteurs et rôles  

### 6.1 Mapping Rôles ↔ Lanes  

| Lane BPMN | Rôle métier | Responsabilités | Compétences |
|-----------|-------------|-----------------|-------------|
| **Client** | Consommateur API | Envoi image, réception résultat | HTTP/REST, Auth (API‑KEY) |
| **OCR‑API** | Service métier | Validation, orchestration, appel Tesseract, gestion cache | Node.js, Express, Tesseract CLI |
| **Redis** | Cache / Queue | Stockage temporaire, file d’attente | Redis‑CLI, TTL, Pub/Sub |
| **MinIO** | Stockage d’objets | Persistance d’images & résultats | S3‑compatible API, policies IAM |

### 6.2 Répartition des tâches  

| Tâche | Type BPMN | Exécution |
|-------|-----------|-----------|
| **Validate payload** | **User Task** (automatisé) | Service Node.js |
| **Upload image** | **Service Task** | MinIO client SDK |
| **Enqueue job** | **Send Task** (Message) | Redis `LPUSH` |
| **Wait for OCR result** | **Intermediate Catch Event** (Message) | Bus interne (Redis Pub/Sub) |
| **Persist result** | **Service Task** | Redis `SETEX` + MinIO upload |
| **Return response** | **User Task** | Express `res.json()` |

---  

## 7. Performances et indicateurs (KPIs)  

### 7.1 Métriques de processus  

| Indicateur | Formule | Objectif | Seuil d’alerte |
|------------|---------|----------|----------------|
| **Durée moyenne de traitement** | Σ (temps fin − temps début) / N | < 4 s (cache) < 12 s (nouveau) | > 15 s |
| **Taux de cache‑hit** | # hits / # total requests | > 60 % | < 40 % |
| **Taux d’erreur Tesseract** | # tesseract error / # jobs | < 2 % | > 5 % |
| **Utilisation CPU OCR‑API** | CPU % (processus node) | < 70 % | > 85 % |
| **Coût stockage MinIO / jour** | (GB * price) | < 0.10 € | > 0.30 € |

### 7.2 Points de mesure BPMN  

| Point BPMN | Type d’événement | Métrique collectée |
|------------|----------------|--------------------|
| **Start Event** | Timer (début) | Timestamp `t0` |
| **Boundary Timer** | Timer (30 s) | Durée d’attente (`t_wait`) |
| **End Event** | Message (Result) | Timestamp `t_end` |
| **Intermediate Message Catch** | Message | Latence de queue (`t_queue`) |

---  

## 8. Gestion des exceptions  

### 8.1 Événements de bordure (Boundary Events)  

| Événement | Type | Action métier |
|-----------|------|--------------|
| **Boundary Timer (30 s)** | Timer | Retourner `202 Accepted` + `JobID`; notifier via webhook si configuré. |
| **Error (validation)** | Error | Retour `400 Bad Request` avec détail `InvalidPayload`. |
| **Error (Tesseract)** | Error | Retour `500 Internal Server Error`; log `tesseract_error`. |
| **Escalation (Cache miss)** | Escalation | Notifier l’équipe Ops si le taux de miss dépasse 40 % (alerting). |
| **Compensation (Rollback)** | Compensation | Supprimer l’image stockée si le job échoue après upload. |

### 8.2 Scénarios d’erreur documentés  

| Scénario | Déclencheur | Gestion | Conséquence |
|----------|-------------|---------|-------------|
| **Timeout OCR** | Aucun résultat sous 30 s | Envoi `202 Accepted` + `JobID` ; création d’un job de suivi. | Client doit interroger `/ocr/status/:id`. |
| **Image non supportée** | MIME non autorisé | `400 Bad Request` + message `Unsupported Media Type`. | Aucun traitement. |
| **Redis indisponible** | Connection error | Retour `503 Service Unavailable`; mise en file d’attente locale (fallback). | Réessai automatique après 10 s. |
| **MinIO write error** | Disk full / permission | `500 Internal Server Error`; suppression du job de la queue. | Notification Ops. |

---  

## 9. Sous‑processus et réutilisation  

### 9.1 Identification des sous‑processus  

| Sous‑processus | Description | Réutilisation |
|----------------|-------------|---------------|
| **SP‑001 – Validation du payload** | Vérification MIME, taille, calcul hash. | Appelé par API publique (POST `/ocr`) et par API interne (batch). |
| **SP‑002 – Stockage d’objet** | Upload vers MinIO (image + résultat). | Utilisé par OCR‑API et par processus de backup. |
| **SP‑003 – Gestion du cache** | Read/Write dans Redis (TTL, list queue). | Centralisé pour tous les services (OCR, PDF‑gen, etc.). |
| **SP‑004 – Notification de résultat** | Publication du message `OCR‑Result` sur Redis Pub/Sub. | Partagé avec worker de post‑processing. |

### 9.2 Processus appelés (Call Activities)  

- **Call Activity “SP‑001 – Validation”** dans le diagramme *P‑001* (User Task → Call Activity).  
- **Call Activity “SP‑002 – Upload”** dans le diagramme *P‑001* (Service Task).  

---  

## 10. Matrice de traçabilité  

| Exigence CCF | Processus BPMN | Tâche(s) concernées | Scénario de test |
|--------------|----------------|----------------------|-------------------|
| **EXG‑001** – Traiter une image valide, retourner texte | **P‑001** | `Validate payload`, `Upload image`, `Wait for OCR result` | Nominal (image JPEG, cache miss) |
| **EXG‑002** – Retourner résultat depuis cache | **P‑001** | `Check Redis cache`, `Read result from Redis` | Cache‑hit (hash déjà présent) |
| **EXG‑003** – Gérer image non supportée | **P‑001** | `Validate payload` (Error) | Invalid MIME → 400 |
| **EXG‑004** – Timeout de traitement >30 s | **P‑001** | Boundary Timer (30 s) | Simuler retard worker → 202 + JobID |
| **EXG‑005** – Persistance du résultat | **P‑001** | `Persist result in Redis`, `Upload result to MinIO` | Vérifier présence dans les deux stores |
| **EXG‑006** – Mise à jour du conteneur Docker | **P‑002** | `docker‑compose up --build` (procédure) | Déploiement en dev & prod |
| **EXG‑007** – Monitoring du health‑check Redis | **P‑003** | `PING` périodique | Alert si > 2 s de latence |

---  

## 11. Validation et conformité  

### 11.1 Checklist BPMN  

- [x] Tous les flux ont une source et une cible.  
- [x] Une et une seule activité de **Start Event** par processus.  
- [x] Au moins une **End Event** (Normal et/ou Message).  
- [x] Aucun **Gateway** orphelin (tous les XOR/AND/OR ont des branches équilibrées).  
- [x] Labels des passerelles explicites (ex. *Cache hit ?*).  
- [x] Nomenclature cohérente (P‑001, SP‑001, RB‑001).  
- [x] Utilisation de **Boundary Events** pour la gestion des délais et erreurs.  

### 11.2 Niveaux de conformité BPMN  

| Niveau | Description | Couverture dans le CCF |
|--------|-------------|------------------------|
| **Descriptive** | Diagrammes simples, lisibles, sans détails d’exécution. | Processus **P‑001** (vue haute) – *Descriptive*. |
| **Analytic** | Inclut sous‑processus, événements, règles métier. | Processus **P‑001** complet + **SP‑001/002** – *Analytic*. |
| **Common Executable** | Tous les éléments exécutables (tasks, message flows, data objects). | Tous les diagrammes contiennent des **Service Tasks**, **Message Events**, **Data Objects** – prêts pour Camunda/Activiti. |

---  

## 12. Implémentation et exécution  

### 12.1 Maturité processus  

| Niveau | Caractéristiques | BPMN applicable |
|--------|------------------|-----------------|
| **1 – Initial** | Processus ad‑hoc, pas de documentation. | – |
| **2 – Managé** | Processus documentés, pas d’automatisation. | *Descriptive* |
| **3 – Défini** | Standardisation, utilisation de sous‑processus. | *Analytic* |
| **4 – Quantifié** | Mesure KPI, monitoring actif. | *Analytic* + *Common Executable* |
| **5 – Optimisé** | Boucles d’amélioration continue, CI/CD. | *Common Executable* (déploiement automatisé) |

> Le projet **ocr‑api** se situe actuellement entre **Niveau 3** et **Niveau 4** (processus définis, KPI mesurés, exécution possible sur moteur BPMN).  

### 12.2 Intégration système  

| Composant | Technologie cible | Points d’intégration BPMN |
|-----------|-------------------|--------------------------|
| **OCR‑API** | Node.js 15 (Alpine), Express, Tesseract‑CLI | **Service Tasks** (appel `tesseract`) |
| **Redis** | redis:alpine3.12 | **Message Queues** (LPUSH/LPOP), **Data Store** (cache) |
| **MinIO** | minio/minio:latest (S3‑compatible) | **Data Store** (objet) |
| **Moteur BPMN** | Camunda 7 (Spring Boot) ou Activiti | Déploiement des **BPMN XML** générés à partir des diagrammes PlantUML. |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`) | Build Docker images, tester diagrammes (bpmn‑lint), déployer sur environnement `dev` puis `prod`. |
| **Monitoring** | Prometheus + Grafana (Redis, MinIO, Node) | **Intermediate Timer** & **Error Events** déclenchent alertes via exporter. |

---  

## Annexes  

### A. Glossaire complet (aligné BPMN)  

| Terme | Définition BPMN | Description métier |
|-------|----------------|--------------------|
| **Pool** | Conteneur de participants (organisation). | Représente un système autonome (ex. OCR‑API, Redis). |
| **Lane** | Sous‑division d’un pool (rôle ou unité). | Rôle métier (Client, Service, Stockage). |
| **Message Flow** | Flèche pointillée entre pools. | Échange d’informations (requête, résultat). |
| **Sequence Flow** | Flèche pleine à l’intérieur d’un pool. | Ordre d’exécution des activités. |
| **Boundary Event** | Événement attaché à une activité. | Gestion du timeout, erreurs. |
| **Data Object** | Icône rectangle avec coin plié. | Données manipulées (ImageBlob, OCRResult). |
| **Data Store** | Icône cylindre. | Stockage persistant (Redis, MinIO). |
| **Gateway** | Losange, décision ou synchronisation. | Décisions « Cache hit ? », fork/join parallèles. |
| **Sub‑process** | Rectangle avec +. | Regroupe tâches réutilisables (validation, upload). |
| **Call Activity** | Rectangle avec icône « call ». | Invocation d’un sous‑processus externe. |
| **Timer Event** | Cercle avec horloge. | Déclencheur de timeout ou de planification. |
| **Error Event** | Cercle avec éclat. | Capture d’erreurs techniques. |

### B. Références documentaires  

1. **ISO/IEC 19510:2013** – Business Process Model and Notation (BPMN) – OMG.  
2. **Camunda BPMN 8.0 Documentation** – Modélisation & exécution.  
3. **Redis 6.2 Documentation** – Persistence & Pub/Sub.  
4. **MinIO Object Storage** – S3‑compatible API.  
5. **Tesseract OCR 5.x** – CLI options, language packs (`tesseract‑ocr-data‑fra`).  

---  

*Fin du Cahier des Charges Fonctionnel – ocr‑api*  