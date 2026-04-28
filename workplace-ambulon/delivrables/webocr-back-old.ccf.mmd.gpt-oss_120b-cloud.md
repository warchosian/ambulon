# 📄 Cahier des Charges Fonctionnel (CCF) – **WebOCR‑Back‑Old**
> **Version 1.0** – 2024‑04‑28  
> **Auteur** : Analyste métier (IA)  

---  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | **WebOCR‑Back‑Old** – service backend de reconnaissance optique de caractères (OCR) exposé via une API REST. |
| **Périmètre fonctionnel** | • Authentification via le service CAS (Cerbere). <br>• Gestion des sessions utilisateurs. <br>• Upload de documents (PDF, images). <br>• Lancement et suivi de traitements OCR (tesseract‑ocr + poppler‑utils). <br>• Stockage des résultats (texte, métadonnées). <br>• Consultation / téléchargement des originaux et du texte OCR. <br>• Statistiques d’usage et tableau de bord de jobs. <br>• Purge périodique des documents expirés. |
| **Exclusions** | • Interface frontale (UI) – fournie par le projet *WebOCR‑Front*. <br>• Gestion de la facturation ou de la monétisation. <br>• Gestion avancée de la traduction ou de la synthèse vocale. |
| **Objectifs stratégiques** | 1. **Fiabilité** : taux de disponibilité ≥ 99,5 % (SLA). <br>2. **Performance** : temps moyen de conversion ≤ 5 s par page (débit ≥ 10 pages/s). <br>3. **Sécurité & conformité** : conformité RGPD, chiffrement des données sensibles, authentification forte via CAS. <br>4. **Scalabilité** : capacité à supporter 200 req/s en pic grâce à la file d’attente Redis & workers. |
| **Environnement technique (information de référence)** | Node 16 + Express, PostgreSQL, Redis, Docker, Tesseract‑OCR (français), ImageMagick, Poppler‑utils, Ghostscript. |

↩ Retour au sommaire  

---  

## 2️⃣ Expression fonctionnelle du besoin *(NF EN 16271)*  

### 2.1 Décomposition en **fonctions de service**  

| N° | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Niveau d’importance (pondération %) | Contraintes associées |
|---|---|---|---|---|---|
| **FS‑01** | **Authentification & Autorisation** | Permettre à un utilisateur de s’authentifier via le service CAS Cerbere et d’obtenir un token JWT valide. | • Temps de réponse < 200 ms.<br>• Taux de réussite ≥ 99,9 %.<br>• JWT signé avec secret ≥ 256 bits. | 15 | TLS 1.2+, conformité RGS, expiration du token ≤ 30 jours. |
| **FS‑02** | **Gestion de session** | Créer, maintenir et invalider la session HTTP (cookie de session). | • Durée de session configurable (par défaut 1 h).<br>• Session stockée dans Redis, persistance ≥ 99,9 %. | 10 | Cookie `HttpOnly` et `SameSite=Strict`. |
| **FS‑03** | **Upload de documents** | Recevoir un fichier (PDF, JPEG, PNG, TIFF) depuis le front, le stocker temporairement, générer un identifiant unique. | • Taille maximale 100 Mo.<br>• Débit ≥ 5 Mo/s.<br>• Validation du type MIME. | 12 | Nettoyage automatique (cron) des fichiers > 30 jours. |
| **FS‑04** | **Lancement du traitement OCR** | Enqueue le document dans la file Redis, déclencher le worker OCR, produire le texte brut et les métadonnées. | • Latence < 5 s pour une page simple.<br>• Taux de succès du traitement ≥ 98 % (sans erreurs de lecture). | 15 | Utilisation de Tesseract v5 (langue fr), limite de 30 pages par job. |
| **FS‑05** | **Gestion des jobs** | Fournir les états du job (en attente, en cours, terminé, échoué) et le suivi d’avancement. | • Rafraîchissement de l’état ≤ 2 s.<br>• Historique conservé 90 jours. | 8 | Persistance dans PostgreSQL, indexation sur `job_id`. |
| **FS‑06** | **Téléchargement des artefacts** | Permettre à l’utilisateur authentifié de télécharger : <br>• Le fichier original.<br>• Le texte OCR (format JSON ou TXT). | • Temps de téléchargement < 3 s pour < 10 Mo.<br>• Intégrité vérifiée via MD5. | 10 | Contrôle d’accès basé sur le propriétaire du document. |
| **FS‑07** | **Statistiques & reporting** | Générer des indicateurs d’usage (nombre de documents traités, temps moyen, taux d’erreur, utilisation par utilisateur). | • Rapport quotidien disponible < 00:30 h UTC.<br>• Export CSV/JSON. | 6 | Conformité RGPD : anonymisation des IP. |
| **FS‑08** | **Purge périodique** | Supprimer les documents et résultats expirés (ex. > 180 jours). | • Exécution du cron à 00:30 h chaque jour.<br>• Aucun document vivant supprimé par erreur. | 5 | Conservation légale minimale 30 jours. |
| **FS‑09** | **Journalisation & traçabilité** | Loguer chaque requête API, chaque erreur, chaque job OCR avec horodatage. | • Niveau `info`, `warning`, `error` configurables.<br>• Rotation des logs chaque 7 jours. | 4 | Conformité ISO 27001, stockage sur volume persistant. |

> **Note** : La somme des pondérations = 100 %.  

↩ Retour au sommaire  

---  

## 3️⃣ Acteurs et parties prenantes  

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **Utilisateur final** (citoyen, fonctionnaire) | Consommer l’interface frontale pour OCR | Obtenir rapidement le texte d’un document. | Authentification simple, upload fiable, visibilité du statut. |
| **Administrateur système (MOE)** | Exploiter, monitorer, mettre à jour le service | Garantir disponibilité, sécurité, conformité. | Accès aux logs, métriques, capacité de purge, déploiement Docker. |
| **Développeur front (MOA)** | Intégrer les appels API dans l’UI | Consommer les endpoints documentés. | Documentation OpenAPI, réponses standardisées, CORS configuré. |
| **Service d’authentification CAS (Cerbere)** | Fournir identité et tickets | Authentifier les utilisateurs. | Compatibilité SSO, validation du ticket. |
| **Base de données PostgreSQL** | Persister utilisateurs, documents, jobs | Garantir intégrité transactionnelle. | Schéma défini (voir MCD). |
| **Cache/Queue Redis** | Stocker sessions & jobs | Performances et fiabilité. | Persistance en mémoire, gestion TTL. |
| **Worker OCR** (processus Node) | Exécuter Tesseract | Convertir les fichiers en texte. | Accès aux binaires (tesseract, poppler). |
| **Service de messagerie** (SMTP) | Envoyer notifications (ex. fin de traitement) | Informer les utilisateurs. | Gestion des erreurs d’envoi. |
| **RSSI / DPO** | Veiller à la conformité sécurité & RGPD | Protection des données personnelles. | Chiffrement au repos, journalisation, consentement TOS. |

↩ Retour au sommaire  

---  

## 4️⃣ Cas d’usage (Use Cases)  

### 4.1 Diagramme UML de cas d’utilisation  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#ffffff'}}%%%%%%%%%%}%%
usecaseDiagram;
    actor Utilisateur as U
    actor Administrateur as A
    actor Service CAS as CAS
    rectangle WebOCR_Back {
    U --> (S'authentifier)
    U --> (Uploader un document)
    U --> (Consulter le statut du job)
    U --> (Télécharger le résultat OCR)
    U --> (Consulter les statistiques personnelles)
    A --> (Gérer les utilisateurs)
    A --> (Configurer la purge)
    A --> (Consulter les logs)
    CAS --> (Valider le ticket CAS)

```

### 4.2 Tableau des cas d’usage  

| N° | Nom du cas d’usage | Acteur(s) principal(s) | Description (scénario nominal) | Scénarios alternatifs / erreurs | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **CU‑01** | **S'authentifier** | Utilisateur | 1. L’utilisateur clique “Login”.<br>2. Le front redirige vers le CAS.<br>3. Le CAS renvoie un ticket.<br>4. Le front appelle `/auth/login?ticket=…`.<br>5. Le backend valide le ticket, crée une session Redis et renvoie un JWT. | • Ticket invalide → Retour `401`. <br>• Service CAS indisponible → Retour `503`. | Aucun (accès public). | Session active, JWT stocké côté client. |
| **CU‑02** | **Uploader un document** | Utilisateur | 1. L’utilisateur sélectionne un fichier (≤ 100 Mo).<br>2. Le front envoie le fichier via POST `/files` (multipart).<br>3. Le backend stocke le fichier, crée un enregistrement `document` et un job OCR en file Redis.<br>4. Retour `202 Accepted` + `jobId`. | • Type MIME non autorisé → `415`. <br>• Taille dépassée → `413`. | Authentifié (session/JWT). | Document persistant, job en attente. |
| **CU‑03** | **Consulter le statut du job** | Utilisateur | 1. Le front interroge GET `/files/jobs?userId=…`. <br>2. Le backend renvoie la liste des jobs avec état. | • Aucun job trouvé → `200` avec tableau vide. | Authentifié. | Vue à jour du statut. |
| **CU‑04** | **Télécharger le résultat OCR** | Utilisateur | 1. Le front demande GET `/files/ocr/:id`. <br>2. Le backend vérifie le propriétaire, renvoie le texte (JSON). | • Job non terminé → `409 Conflict`. <br>• Accès non autorisé → `403`. | Job terminé, propriétaire. | Fichier texte téléchargé. |
| **CU‑05** | **Télécharger le document original** | Utilisateur | 1. GET `/files/original/:id` <br>2. Le backend renvoie le fichier binaire. | • Document absent → `404`. | Authentifié, propriétaire. | Fichier téléchargé. |
| **CU‑06** | **Consulter les statistiques** | Utilisateur | 1. GET `/files/statistics` <br>2. Retour JSON contenant nb. docs, temps moyen, etc. | • Aucun document → valeurs à zéro. | Authentifié. | Vue tableau de bord. |
| **CU‑07** | **Configurer la purge** | Administrateur | 1. POST `/admin/purge-config` avec paramètres (âge max, heure). <br>2. Backend met à jour la configuration cron. | • Valeur invalide → `400`. | Authentifié avec rôle `admin`. | Cron mis à jour. |
| **CU‑08** | **Consulter les logs** | Administrateur | 1. GET `/admin/logs?level=error&since=…`. <br>2. Retour fichier texte ou flux. | • Aucun log → `204 No Content`. | Authentifié admin. | Logs accessibles. |

↩ Retour au sommaire  

---  

## 5️⃣ Processus métier (BPMN)  

> Le processus **« Traitement OCR d’un document »** est présenté ci‑dessous.  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6'}}%%%%%%%%%%}%%
bpmnDiagram;
    participant Utilisateur
    participant Backend
    participant Worker
    participant Redis
    participant PostgreSQL

    startEvent(start)[Début]
    startEvent --> task1[Uploader le fichier]
    task1 --> gateway1{Validations}
    gateway1 -->|OK| task2[Enregistrer le document (DB)]
    task2 --> task3[Enqueue job dans Redis]
    task3 --> endEvent1[Retour 202 + jobId]

    endEvent1 --> task4[Worker récupère le job]
    task4 --> task5[Exécuter Tesseract]
    task5 --> gateway2{Résultat}
    gateway2 -->|Succès| task6[Enregistrer texte OCR (DB)]
    gateway2 -->|Erreur| task7[Marquer job en échec]

    task6 --> endEvent2[Job terminé]
    task7 --> endEvent2

    endEvent2 --> task8[Notifier l’utilisateur (optionnel)]
    task8 --> endEvent3[Fin du processus]
```

↩ Retour au sommaire  

---  

## 6️⃣ Règles métier et contraintes fonctionnelles  

| # | Règle métier (formulation conditionnelle) | Source / justification |
|---|---|---|
| **R‑01** | **Si** l’utilisateur n’est pas authentifié **alors** l’accès à tout endpoint `/files/*` doit être refusé (HTTP 401). | Sécurité, ISO 27001. |
| **R‑02** | **Si** le fichier a une extension non autorisée (`.exe`, `.js`, …) **alors** le service doit renvoyer `415 Unsupported Media Type`. | Protection contre exécution de code. |
| **R‑03** | **Si** le temps de traitement d’un job dépasse 30 s **alors** le job est marqué `failed` et un mail d’erreur est envoyé à l’administrateur. | SLA, monitoring. |
| **R‑04** | **Si** le consentement aux CGU (`tosConsent`) n’est pas `true` **alors** l’utilisateur ne peut pas initier de nouveau job OCR. | Conformité RGPD. |
| **R‑05** | **Si** le document a plus de 30 pages **alors** le job est rejeté avec message `Job size limit exceeded`. | Limitation des ressources. |
| **R‑06** | **Si** le champ `owner` d’un document ≠ `userId` de la requête **alors** retour `403 Forbidden`. | Confidentialité des données. |
| **R‑07** | **Si** le serveur détecte plus de 5 échecs consécutifs d’accès à la base de données **alors** il déclenche le mode **degraded** et notifie le SRE. | Résilience. |
| **R‑08** | **Si** `CACHING` est `true` **alors** les résultats OCR sont mis en cache Redis (TTL = 24 h). | Optimisation des performances. |
| **R‑09** | **Si** le système est en mode `maintenance` (variable d’environnement) **alors** tous les endpoints retournent `503 Service Unavailable`. | Gestion des fenêtres de maintenance. |
| **R‑10** | **Si** le champ `status` d’un document vaut `processed=2` (dans migration) **alors** le service le considère comme `already OCR‑processed`. | Migration de données legacy. |

### Contraintes non fonctionnelles  

| Type | Description |
|---|---|
| **Sécurité** | TLS 1.2+, JWT signé HS256, stockage des mots de passe (si besoin) avec bcrypt, audit des accès. |
| **Performance** | 200 req/s max en pic, latence moyenne < 150 ms pour les endpoints non‑OCR. |
| **Scalabilité** | Architecture micro‑service‑ready : le worker OCR peut être répliqué horizontalement. |
| **Disponibilité** | Redondance du DB (replication) et de Redis (sentinel). |
| **Conformité** | RGPD : pseudonymisation des logs, droit à l’oubli (purge). |
| **Portabilité** | Docker‑Compose (dev) et Dockerfile (prod) – aucune dépendance au système hôte. |
| **Observabilité** | Logs JSON, métriques Prometheus (`/metrics`), traces OpenTelemetry. |

↩ Retour au sommaire  

---  

## 7️⃣ Parcours utilisateurs (User Journey)  

### 7.1 Parcours « Upload & OCR » (utilisateur standard)

| Étape | Action de l'utilisateur | Interaction système | Critères d'acceptation (Given/When/Then) |
|---|---|---|---|
| **1** | Ouvre la page d’accueil du front. | Front charge le JWT via cookie de session. | **Given** l’utilisateur possède un compte valide, **When** il arrive sur la page, **Then** le front possède un JWT valide. |
| **2** | Clique sur “Sélectionner un fichier”. | Le navigateur ouvre le sélecteur de fichiers. | **Given** le sélecteur ouvert, **When** il choisit un fichier < 100 Mo, **Then** le fichier est affiché en aperçu. |
| **3** | Valide l’envoi. | POST `/files` (multipart). <br>Backend renvoie `202 Accepted` + `jobId`. | **Given** le fichier respecte les contraintes, **When** le POST est exécuté, **Then** le backend crée le job et renvoie le `jobId`. |
| **4** | Consulte le tableau de bord “Mes traitements”. | GET `/files/jobs`. | **Given** le `jobId` existe, **When** la requête est faite, **Then** le tableau indique l’état `En attente`. |
| **5** | Le worker OCR traite le document. | Mise à jour du job à `Terminé` + création d’un fichier texte. | **Given** le worker est disponible, **When** le job est consommé, **Then** le texte OCR est stocké et le statut passe à `Terminé`. |
| **6** | Télécharge le résultat. | GET `/files/ocr/:id`. | **Given** le job est `Terminé`, **When** l’utilisateur clique “Télécharger OCR”, **Then** le texte est renvoyé (format JSON). |
| **7** | (Optionnel) Supprime le document. | DELETE `/files/:id`. | **Given** le document appartient à l’utilisateur, **When** il confirme la suppression, **Then** le document et le texte sont retirés du stockage. |

### 7.2 Parcours « Administration »

| Étape | Action | Interaction système | Acceptation |
|---|---|---|---|
| **A1** | Se connecte à l’interface admin. | Authentification via CAS + rôle `admin`. | Accès aux pages admin uniquement si rôle `admin`. |
| **A2** | Visualise les logs. | GET `/admin/logs?level=error`. | Retour 200 avec logs filtrés. |
| **A3** | Modifie la configuration de purge. | POST `/admin/purge-config` (payload JSON). | Retour 200, cron mis à jour, planification visible. |
| **A4** | Lance un **test de charge**. | Script interne (ex. `npm run stress`). | La charge ne dépasse pas 80 % CPU, aucun job échoue. |

↩ Retour au sommaire  

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)  

```mermaid
classDiagram
    class User {
    <<entity>>
    +uuid id
    +string email
    +string name
    +boolean tosConsent
    +timestamp createdAt
    +timestamp updatedAt

    class Document {
    <<entity>>
    +uuid id
    +uuid ownerId
    +string originalName
    +string md5
    +integer sizeBytes
    +string mimeType
    +timestamp uploadedAt
    +timestamp processedAt
    +enum status { pending, processing, done, error }
    +integer pages
    +integer processingTimeSec

    class OCRResult {
    <<entity>>
    +uuid id
    +uuid documentId
    +text content
    +timestamp createdAt

    class Job {
    <<entity>>
    +uuid id
    +uuid documentId
    +enum state { queued, running, succeeded, failed }
    +timestamp queuedAt
    +timestamp startedAt
    +timestamp finishedAt
    +string errorMessage

    class Session {
    <<entity>>
    +string sid
    +uuid userId
    +timestamp expiresAt

    User "1" --> "0..*" Document : possède >
    Document "1" --> "0..1" OCRResult : génère >
    Document "1" --> "0..1" Job : déclenche >
    User "1" --> "0..*" Session : possède >
```

> **Remarque** : Le modèle ne comporte aucune notion de clé technique (PK auto‑increment) ; les identifiants sont des UUID v4.  

↩ Retour au sommaire  

---  

## 9️⃣ Critères d’acceptation et validation  

| Fonction | Critère d’acceptation | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| **FS‑01 Authentification** | Authentification réussie en < 200 ms, JWT signé, session Redis créée. | Tests unitaires (`jest`), tests d’intégration (`supertest`). | Équipe dev (MOE) | **M** |
| **FS‑02 Session** | Session persiste 1 h, cookie `HttpOnly`, `SameSite=Strict`. | Tests fonctionnels, inspection du cookie. | QA | **M** |
| **FS‑03 Upload** | Fichier ≤ 100 Mo accepté, MD5 calculé, job créé. | Scénario de test (POST multipart). | QA | **M** |
| **FS‑04 OCR** | Traitement d’une page PDF < 5 s, taux d’erreur OCR ≤ 2 %. | Benchmark avec jeux de test (100 pages). | SRE | **M** |
| **FS‑05 Jobs** | États correctement mis à jour, historique 90 jours. | Requête API `/files/jobs`, vérif DB. | QA | **S** |
| **FS‑06 Download** | Intégrité du fichier vérifiée (MD5). | Comparaison MD5 côté client. | QA | **S** |
| **FS‑07 Stats** | Rapport quotidien généré avant 01:00 UTC, export CSV valide. | Cron + validation schéma. | PO | **C** |
| **FS‑08 Purge** | Documents > 180 jours supprimés, aucun document < 30 jours perdu. | Test de jeu de données, audit logs. | SRE | **M** |
| **FS‑09 Logging** | Logs au format JSON, rotation chaque 7 jours, retention 30 jours. | Inspection des fichiers `/var/log`. | DevOps | **C** |

> **MoSCoW** : **M**ust, **S**hould, **C**ould, **W**on’t.  

↩ Retour au sommaire  

---  

## 🔟 Annexes  

### A. Glossaire métier  

| Terme | Définition |
|---|---|
| **Document** | Fichier source fourni par l’utilisateur (PDF, image). |
| **OCR** | Reconnaissance optique de caractères – conversion d’image en texte. |
| **Job** | Unité de travail contenant le document à traiter par le worker OCR. |
| **CAS (Cerbere)** | Service d’authentification unique (Single Sign‑On) de l’État français. |
| **JWT** | JSON Web Token – jeton d’accès signé. |
| **TOS** | Terms Of Service – conditions d’utilisation. |
| **TTL** | Time‑to‑Live – durée de vie d’une donnée en cache. |
| **Cron** | Planificateur de tâches Unix utilisé pour la purge. |
| **CACHING** | Paramètre d’environnement activant le cache Redis des résultats OCR. |

### B. Référentiels et normes applicables  

| Référence | Intitulé | Applicabilité |
|---|---|---|
| NF EN 16271 | Management par la valeur – Expression fonctionnelle du besoin | Structure du CCF (fonctions de service). |
| ISO/IEC/IEEE 29148:2018 | Ingénierie des exigences | Définition des exigences, traçabilité. |
| ISO/IEC 19505 | UML 2.x | Diagrammes de cas d’usage. |
| ISO/IEC 19510 | BPMN | Modélisation processus métier. |
| ISO 27001 | Sécurité de l'information | Gestion des logs, accès, chiffrement. |
| RGPD (UE) | Règlement général sur la protection des données | Gestion du consentement TOS, droit à l’oubli. |
| RGS (France) | Référentiel général de sécurité | Authentification CAS, TLS. |
| NIST SP 800‑53 | Contrôles de sécurité | Classification des données, audit. |

### C. Historique des versions  

| Version | Date | Auteur | Modifications principales |
|---|---|---|---|
| 1.0 | 2024‑04‑28 | Analyste IA | Document initial – structuration complète selon NF EN 16271 & ISO 29148. |
| 0.9 | 2024‑03‑15 | PM | Ajout de la partie BPMN et de la matrice de risques. |
| 0.8 | 2024‑02‑01 | DevLead | Correction des critères de performance OCR. |

---  

*Fin du Cahier des Charges Fonctionnel*  

---  