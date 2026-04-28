# 📄 Cahier des Charges Fonctionnel (CCF) – **ocr‑api**  
[TOC]

---

## 1️⃣ Introduction et contexte du projet <a id="intro"></a>

### 1.1 Présentation du projet
Le projet **ocr‑api** vise à fournir un service d’OCR (Optical Character Recognition) **conteneurisé** exploitable via une API HTTP REST.  
Le service s’appuie sur :

| Composant | Rôle |
|-----------|------|
| **tesseract‑ocr** (et ses données françaises) | Moteur de reconnaissance de texte |
| **Redis** | Cache de résultats et file d’attente de jobs |
| **MinIO** | Stockage objet des documents source et des résultats OCR |
| **Node.js** (API) | Orchestration des appels, exposition de l’API, gestion de la configuration |

### 1.2 Objectifs stratégiques
| Objectif | Bénéfice métier |
|----------|-----------------|
| Offrir un service OCR fiable, multi‑format (image, PDF, etc.) | Automatisation de la saisie de données, réduction des traitements manuels |
| Déploiement **cloud‑native** (Docker, Docker‑Compose) | Scalabilité, portabilité et intégration CI/CD |
| Sécuriser l’accès via **API‑Key** et chiffrement des données stockées | Conformité RGPD, protection du secret professionnel |
| Garantir la traçabilité et la ré‑exécutabilité des jobs | Auditabilité, reprise après incident |

### 1.3 Périmètre fonctionnel
| Inclus | Exclus |
|--------|--------|
| • API d’ingestion de fichiers<br>• Traitement OCR via Tesseract<br>• Gestion de la file d’attente (Redis)<br>• Stockage des artefacts (MinIO)<br>• Monitoring basique (logs) | • Interface graphique (frontend)<br>• Gestion avancée des droits (IAM complet)<br>• Traduction du texte reconnu<br>• Enrichissement sémantique (NLP) |

---

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) <a id="besoin"></a>

### 2.1 Décomposition en fonctions de service

| # | Fonction de service (Quoi) | Description concise | Critères d’appréciation (mesurables) | Pondération* | Contraintes |
|---|------------------------------|----------------------|--------------------------------------|--------------|--------------|
| **F1** | **Ingestion de documents** | Recevoir un ou plusieurs fichiers (image, PDF, TIFF) via l’API. | • Temps moyen d’upload ≤ 2 s (payload ≤ 10 Mo)<br>• Taux d’erreur HTTP 4xx ≤ 0,5 % | 15% | Taille max 50 Mo, formats autorisés listés dans la config |
| **F2** | **Gestion de la file d’attente** | Enregistrer la demande dans Redis et la rendre disponible pour le worker OCR. | • Latence d’inscription ≤ 200 ms<br>• Fiabilité de la file ≥ 99,9 % (pas de perte de job) | 10% | Utilisation d’un *list* ou *stream* Redis, persistance activée |
| **F3** | **Exécution du traitement OCR** | Lancer Tesseract sur le fichier, extraire le texte et les métadonnées (langue, confidence). | • Taux de reconnaissance ≥ 95 % sur jeux de test standard<br>• Temps moyen de traitement ≤ 5 s (image ≤ 5 Mo) | 25% | Tesseract‑ocr ≥ 4.1, données françaises installées |
| **F4** | **Stockage des artefacts** | Persister le fichier source et le résultat OCR (texte, JSON) dans MinIO. | • Disponibilité MinIO ≥ 99,5 %<br>• Durée de rétention configurée (≥ 30 jours) | 10% | Bucket séparé `ocr-input` / `ocr-output`, chiffrement côté serveur |
| **F5** | **Authentification & autorisation** | Valider l’API‑Key fournie dans le header `X‑API‑KEY`. | • 0,0 % d’accès non autorisé détecté<br>• Rotation des clés possible sans downtime | 10% | Gestion via fichier `.env` ou secret manager |
| **F6** | **Reporting & journalisation** | Générer des logs structurés (JSON) pour chaque étape et un endpoint de statistiques. | • Logs au format `RFC5424`<br>• Temps de génération de stats ≤ 1 s | 5% | Utilisation de `pino` ou équivalent, sortie vers `stdout` |
| **F7** | **Déploiement automatisé** | Fournir les Dockerfiles, Docker‑Compose (dev/prod) et scripts d’initialisation. | • Build Docker < 2 min<br>• Lancement complet (API + Redis + MinIO) < 30 s | 5% | Compatibilité avec Docker ≥ 20.10 |
| **F8** | **Gestion de la configuration** | Lire les variables d’environnement (`API_PORT`, `MINIO_*`, `OCR_TESSERACT_IMAGE`, …). | • Toutes les variables obligatoires détectées au démarrage<br>• Validation de format (ex : port numérique) | 5% | Valeurs par défaut documentées |
| **F9** | **Résilience & reprise** | Redémarrage automatique du worker OCR en cas de crash, persistance des jobs. | • Temps moyen de récupération ≤ 10 s<br>• Aucun job perdu (re‑queue) | 5% | Utilisation de Docker restart policies, Redis AOF |

\* La pondération reflète l’impact métier ; la somme = 100 %.

---

## 3️⃣ Acteurs et parties prenantes <a id="acteurs"></a>

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|--------|------|-----------|----------------------|
| **Développeur intégrateur** | Consomme l’API OCR | Intégrer la reconnaissance texte dans ses applications | Documentation Swagger, réponses rapides, gestion d’erreurs claire |
| **Administrateur système** | Déploie et maintient l’infrastructure | Disponibilité du service, conformité sécurité | Scripts d’orchestration, logs centralisés, rotation des API‑Key |
| **Opérateur de données** | Charge les documents source | Traiter de gros volumes de scans | Gestion de lots, monitoring de la file d’attente |
| **MOA (Maître d’Ouvrage)** | Définit les exigences fonctionnelles | Livraison d’un service conforme aux exigences métier | Traçabilité, reporting d’usage |
| **MOE (Maître d’Œuvre)** | Réalise le développement | Respect des spécifications techniques | Accès au code, environnement de test |
| **RSSI** | Garant de la sécurité | Protection des données sensibles | Chiffrement, contrôle d’accès, conformité RGPD |
| **Utilisateur final** (ex. opérateur de saisie) | Consomme les résultats OCR | Obtenir du texte exploitable rapidement | Qualité du texte, disponibilité du résultat |

---

## 4️⃣ Cas d’usage (Use Cases) <a id="casusages"></a>

### 4.1 Diagramme de cas d’utilisation (UML) – Mermaid

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#fff' }}%%}%%
usecaseDiagram;
    title OCR‑API – Cas d’utilisation;
    actor Développeur intégrateur as Dev;
    actor Opérateur de données as Op;
    actor Administrateur système as Admin;
    rectangle OCR_API {
        Dev --> (Soumettre un document)
        Dev --> (Interroger le statut du job)
        Dev --> (Récupérer le résultat OCR)
        Op --> (Uploader un lot de documents)
        Op --> (Consulter le rapport de traitement)
        Admin --> (Déployer le service)
        Admin --> (Configurer les variables d’environnement)
        Admin --> (Surveiller la santé du service)
    }
```

### 4.2 Liste détaillée des cas d’usage

| N° | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|----|--------------------|--------------------------|-------------------|----------------------------------|----------------|-----------------|
| **CU‑01** | Soumettre un document | Développeur intégrateur | 1. Envoi POST `/v1/ocr` avec fichier + `X‑API‑KEY`<br>2. Service valide la clé, crée un job, renvoie `jobId` (202) | • 401 : clé invalide<br>• 415 : type MIME non supporté<br>• 413 : taille > 50 Mo | API‑Key valide, service en ligne | Job persistant dans Redis, fichier stocké dans MinIO (`ocr-input`) |
| **CU‑02** | Interroger le statut du job | Développeur intégrateur | 1. GET `/v1/ocr/{jobId}` avec `X‑API‑KEY`<br>2. Retour JSON `{status: "pending|running|done|failed"}` (200) | • 404 : jobId inconnu<br>• 403 : clé non autorisée pour ce job | Job créé préalablement | Aucun changement d’état |
| **CU‑03** | Récupérer le résultat OCR | Développeur intégrateur | 1. GET `/v1/ocr/{jobId}/result` avec `X‑API‑KEY`<br>2. Service renvoie le texte + métadonnées (200) | • 404 : résultat indisponible<br>• 410 : résultat expiré (TTL dépassé) | Job en état `done` | Aucun (lecture seule) |
| **CU‑04** | Uploader un lot de documents | Opérateur de données | 1. POST `/v1/ocr/batch` avec archive ZIP<br>2. Service découpe, crée un job par fichier, renvoie liste `jobId[]` (202) | • 422 : archive corrompue<br>• 413 : taille totale > 500 Mo | API‑Key valide, service disponible | Tous les jobs créés, fichiers stockés |
| **CU‑05** | Consulter le rapport de traitement | Opérateur de données | 1. GET `/v1/ocr/report?from=…&to=…`<br>2. Retour JSON agrégé (nombre de jobs, taux de succès, temps moyen) (200) | • 400 : paramètres invalides | Authentification valide | Aucun |
| **CU‑06** | Déployer le service | Administrateur système | 1. Exécuter `docker compose -f docker-compose.prod.yml up -d`<br>2. Vérifier que les containers `ocr-api`, `redis`, `minio` sont *healthy* | • 500 : image Docker non trouvée<br>• 502 : MinIO non accessible | Docker & Docker‑Compose installés | Service opérationnel, logs visibles |
| **CU‑07** | Configurer les variables d’environnement | Administrateur système | 1. Modifier `.env` ou injecter secrets via orchestrateur<br>2. Relancer le container | • 400 : variable manquante<br>• 409 : port déjà utilisé | Container arrêté ou redémarré | Configuration appliquée au démarrage |
| **CU‑08** | Surveiller la santé du service | Administrateur système | 1. GET `/healthz` (ou Docker healthcheck)<br>2. Retour `{"status":"ok"}` (200) | • 503 : dépendances indisponibles | Service en cours d’exécution | Aucune action, alerte possible |

↩ Retour au sommaire

---

## 5️⃣ Processus métier (BPMN) <a id="processus"></a>

### 5.1 Diagramme du flux de traitement OCR (simplifié)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6' }}%%}%%
bpmnDiagram;
    participant Client;
    participant API;
    participant Redis;
    participant Worker;
    participant MinIO;
    Client->>API: POST /v1/ocr (fichier)
    API->>Redis: Enqueue job (jobId)
    API->>MinIO: Store source file (bucket ocr-input)
    API->>Client: 202 Accepted (jobId)

    loop Traitement as Job;
        Redis->>Worker: Pull job;
        Worker->>MinIO: Retrieve source file;
        Worker->>Worker: Execute Tesseract OCR;
        Worker->>MinIO: Store result (bucket ocr-output)
        Worker->>Redis: Update job status = done;
    end;
    Client->>API: GET /v1/ocr/{jobId}
    API->>Redis: Query status;
    API->>Client: Return status / result URL
```

### 5.2 Points de contrôle et règles de gestion
| Point de contrôle | Règle associée |
|-------------------|----------------|
| **Enregistrement du job** | Le job doit être persistant (Redis *AOF* ou *RDB*) avant de renvoyer l’`jobId`. |
| **Traitement OCR** | Le worker ne doit pas dépasser **5 s** par fichier ≤ 5 Mo ; sinon le job passe en `failed`. |
| **Stockage des artefacts** | Les objets sont stockés avec le préfixe `input/` ou `output/` + `jobId`. |
| **Expiration du résultat** | Les objets `output/` sont automatiquement supprimés après **30 jours** (policy MinIO). |
| **Sécurité** | Toutes les communications internes (API ↔ Redis/MinIO) sont chiffrées TLS (optionnelle). |

↩ Retour au sommaire

---

## 6️⃣ Règles métier et contraintes fonctionnelles <a id="regles"></a>

| # | Règle métier (condition → action) | Type | Source / Référence |
|---|--------------------------------------|------|--------------------|
| **R1** | Si `file.type` ∉ {`image/png`, `image/jpeg`, `image/tiff`, `application/pdf`} → **rejeter** la requête avec 415. | Validation d’entrée | .env / spécifications API |
| **R2** | Si `file.size` > **50 Mo** → **rejeter** avec 413. | Validation d’entrée | Documentation |
| **R3** | Si `API_KEY` non trouvé ou désactivé → **refuser** l’accès (401). | Sécurité | Gestion des secrets |
| **R4** | Si le job reste `pending` > **24 h** → **marquer** `failed` et notifier l’opérateur. | Gestion de la file | SLA interne |
| **R5** | Si le taux de reconnaissance (`confidence`) < **80 %** pour un document > **10 pages** → **alerter** l’opérateur pour revue manuelle. | Qualité du résultat | Tests de validation |
| **R6** | Tous les logs doivent être au format JSON et contenir `timestamp`, `level`, `service`, `message`, `jobId`. | Observabilité | ISO/IEC 27001 (audit) |
| **R7** | Les données stockées dans MinIO doivent être chiffrées au repos (SSE‑S3). | Sécurité des données | RGPD, ISO 27701 |
| **R8** | Le conteneur `ocr-api` doit écouter sur le port défini par `API_PORT` (par défaut 3001). | Configuration | .env |
| **R9** | Le service doit être **stateless** – tout l’état persistant réside dans Redis/MinIO. | Architecture | Principes cloud‑native |
| **R10** | Le code doit être formaté selon les règles de Prettier (`.prettierrc.js`). | Qualité du code | CI/CD lint |

↩ Retour au sommaire

---

## 7️⃣ Parcours utilisateurs (User Journey) <a id="journey"></a>

### 7.1 Parcours « Développeur intégrateur »

| Étape | Interaction | Point de contact | Critère d’acceptation (GWT) |
|-------|-------------|------------------|----------------------------|
| 1️⃣ | **Découverte** de l’API (consultation du Swagger) | Documentation en ligne | **Given** la doc disponible **When** le développeur la consulte **Then** il retrouve la description du endpoint `/v1/ocr` |
| 2️⃣ | **Envoi** d’un fichier | POST `/v1/ocr` (HTTP) | **Given** une API‑Key valide **When** il envoie un fichier PNG ≤ 5 Mo **Then** il reçoit `202 Accepted` avec un `jobId` |
| 3️⃣ | **Suivi** du job | GET `/v1/ocr/{jobId}` | **Given** le `jobId` **When** il interroge le statut **Then** il obtient `status: pending|running|done` |
| 4️⃣ | **Récupération** du texte | GET `/v1/ocr/{jobId}/result` | **Given** le job est `done` **When** il récupère le résultat **Then** il reçoit le texte en JSON et le lien vers l’objet MinIO |
| 5️⃣ | **Gestion d’erreur** | Réponse HTTP 4xx/5xx | **Given** un fichier non supporté **When** il le soumet **Then** il reçoit 415 avec message d’erreur clair |

### 7.2 Parcours « Administrateur système »

| Étape | Interaction | Point de contact | Critère d’acceptation |
|-------|------------|------------------|----------------------|
| A1 | **Déploiement** du stack | `docker compose -f docker-compose.prod.yml up -d` | **Given** le fichier compose présent **When** il lance la commande **Then** les containers sont `healthy` en ≤ 30 s |
| A2 | **Vérification** de la configuration | `docker logs ocr-api` | **Given** les variables d’environnement définies **When** le container démarre **Then** il affiche `API listening on port 3001` |
| A3 | **Monitoring** de la santé | GET `/healthz` ou Docker healthcheck | **Given** le service en cours **When** il interroge le health endpoint **Then** il reçoit `{"status":"ok"}` |
| A4 | **Rotation** de l’API‑Key | Mise à jour du `.env` puis `docker restart ocr-api` | **Given** une nouvelle clé définie **When** le container redémarre **Then** les anciennes clés sont refusées et la nouvelle acceptée |

↩ Retour au sommaire

---

## 8️⃣ Modèle Conceptuel de Données (MCD) <a id="mcd"></a>

### 8.1 Diagramme de classes (UML – abstrait)

```mermaid
classdiagram;
    class Job {
        <<entity>>
        +String id;
        +String status;
        +Date createdAt;
        +Date updatedAt;
        +String sourceObjectKey;
        +String resultObjectKey;
        +Float confidence;
    }

    class User {
        <<entity>>
        +String apiKey;
        +String name;
        +String email;
        +Boolean active;
    }

    class Document {
        <<entity>>
        +String bucket;
        +String objectKey;
        +Long size;
        +String mimeType;
        +Date uploadedAt;
    }

    class LogEntry {
        <<entity>>
        +String id;
        +String level;
        +String message;
        +Date timestamp;
        +String jobId;
    }

    User "1" --> "0..*" Job : possèDes;
    Job "1" --> "1" Document : source;
    Job "1" --> "0..1" Document : result;
    Job "1" --> "0..*" LogEntry : génère
```

### 8.2 Description des entités
| Entité | Description | Attributs majeurs |
|--------|-------------|-------------------|
| **Job** | Représente une demande d’OCR. | `id` (UUID), `status` (`pending|running|done|failed`), `sourceObjectKey`, `resultObjectKey`, `confidence` |
| **User** | Entité possédant une `API_KEY`. | `apiKey` (hash), `active` |
| **Document** | Objet stocké dans MinIO. | `bucket` (`ocr-input`/`ocr-output`), `objectKey`, `mimeType`, `size` |
| **LogEntry** | Événement structuré. | `level` (`info|warn|error`), `message`, `jobId` |

↩ Retour au sommaire

---

## 9️⃣ Critères d’acceptation et validation <a id="acceptation"></a>

| Fonction | Critère d’acceptation | Méthode de validation | Responsable | Priorité (MoSCoW) |
|----------|----------------------|----------------------|--------------|------------------|
| **F1** – Ingestion | ≤ 2 s d’upload, 415/413 correctes | Tests fonctionnels automatisés (Postman) | QA | **Must** |
| **F2** – File d’attente | Pas de perte de job, latence ≤ 200 ms | Simulations de charge (k6) + inspection Redis | DevOps | **Must** |
| **F3** – OCR | Taux de reconnaissance ≥ 95 % sur jeu de 100 documents test | Comparaison texte attendu vs OCR (pytest) | QA | **Must** |
| **F4** – Stockage | 99,5 % de disponibilité MinIO, chiffrement activé | Tests d’accès S3, audit de configuration | Sécurité | **Should** |
| **F5** – Auth | 0 % d’accès non autorisé détecté | Pen‑test OWASP ZAP, revue de code | RSSI | **Must** |
| **F6** – Logs | Format JSON conforme, présence `jobId` | Log parser (jq) + pipeline CI | DevOps | **Should** |
| **F7** – Déploiement | Build < 2 min, start < 30 s | CI GitLab pipeline, métriques Docker | DevOps | **Must** |
| **F8** – Config | Tous les env requis détectés au start | Script `check-env.sh` exécuté en entrypoint | DevOps | **Must** |
| **F9** – Résilience | Récupération < 10 s, aucun job perdu | Test de crash du worker, vérif persistance Redis | QA | **Could** |

↩ Retour au sommaire

---

## 🔟 Annexes <a id="annexes"></a>

### A. Glossaire métier
| Terme | Définition |
|-------|------------|
| **OCR** | Reconnaissance Optique de Caractères – conversion d’image en texte. |
| **Job** | Unité de travail représentant une requête d’OCR. |
| **API‑Key** | Token secret permettant l’authentification d’un client. |
| **MinIO** | Service de stockage objet compatible S3. |
| **Redis** | Base de données en mémoire utilisée comme broker/queue. |
| **TTL** | Time‑To‑Live – durée de vie d’un objet avant expiration. |
| **SSE‑S3** | Server‑Side Encryption gérée par MinIO (type S3). |
| **Swagger / OpenAPI** | Spécification contractuelle de l’API HTTP. |

### B. Référentiels et normes applicables
| Référence | Intitulé | Application |
|-----------|----------|-------------|
| NF EN 16271 | Management par la valeur – Expression fonctionnelle du besoin | Structure du CCF, fonctions de service |
| ISO/IEC 29148 | Ingénierie des exigences | Définition des exigences, traçabilité |
| ISO/IEC 19505 | UML 2.x | Diagrammes de cas d’usage, classes |
| ISO/IEC 19510 | BPMN 2.0 | Diagramme de processus métier |
| ISO 27001 / 27701 | Sécurité de l’information, protection des données | Contraintes RGPD, chiffrement, journalisation |
| RGPD (UE) | Règlement Général sur la Protection des Données | Gestion des données personnelles stockées |

### C. Historique des versions du document
| Version | Date | Auteur | Modifications |
|---------|------|--------|----------------|
| 1.0 | 2026‑04‑28 | ChatGPT (OpenAI) | Version initiale – CCF complet conforme aux consignes |
| 1.1 | – | – | – |

---

*Fin du Cahier des Charges Fonctionnel*  

↩ Retour au sommaire  