# Cahier des Charges Fonctionnel (CCF) – Projet **ambulon**  
*Conforme à la norme ISO/IEC/IEEE 29148 : 2018 – Ingénierie des exigences*  

> **⚠️ NOTE** – Le présent document constitue une **structure déclarative** du CCF.  
> Les exigences fonctionnelles et non‑fonctionnelles sont pour l’instant indiquées sous forme de **place‑holders** (ex. `[TODO]`). Elles devront être complétées dès que les informations métier, techniques et les attentes des parties prenantes seront disponibles.  

---  

## 1. Identification et contexte du document  

| Élément | Valeur |
|---------|--------|
| **Identifiant du document** | CCF‑AMB‑001 |
| **Version** | 0.1 (draft) |
| **Date** | 2026‑04‑27 |
| **Auteur(s)** | <ins>Nom·Prénom – Ingénieur exigences</ins> |
| **Historique des modifications** | 0.1 – Création du squelette (2026‑04‑27) |
| **Références** | • Vision du projet *ambulon* (document à fournir) <br>• Business case *ambulon* (document à fournir) <br>• ISO/IEC/IEEE 29148 : 2018 <br>• ISO/IEC/IEEE 15288 : 2015 (cycle de vie système) <br>• ISO/IEC/IEEE 12207 : 2017 (cycle de vie logiciel) |
| **Portée** | Définir les exigences fonctionnelles, non‑fonctionnelles, les modèles de données et de comportement ainsi que la traçabilité requise pour le **système ambulon** (application web/mobile de gestion d’ambulances). |
| **Objectifs** | • Garantir la conformité aux besoins métier et aux exigences légales (ex. RGPD, normes de santé). <br>• Fournir une base exploitable pour la conception, le développement, les tests et la validation. <br>• Assurer la traçabilité complète du besoin à la mise en production. |

---  

## 2. Description de l’écosystème (System/Software Context)  

```mermaid
graph LR
    subgraph "Système ambulon"
    A[Application Front‑end] 
    B[API / Service Back‑end] 
    C[Base de données (PostgreSQL)] 
    D[Service de messagerie (RabbitMQ / Kafka)] 
    E[Service d’authentification (OAuth2/OIDC)] 
    end
    subgraph "Systèmes externes"
    X[Plateforme de cartographie (OSM / Google Maps)] 
    Y[ERP Hospitalier] 
    Z[Service de notification (SMS/Email)] 
    end
    A --> B;
    B --> C;
    B --> D;
    B --> E;
    B --> X;
    B --> Y;
    B --> Z
```

| Élément | Description |
|--------|-------------|
| **Frontières du système** | Le système ambulon comprend le **front‑end** (web & mobile), le **back‑end** (API REST/GraphQL), la **base de données** et les **services d’infrastructure** (messagerie, authentification). Tout ce qui se trouve hors de ces blocs (ex. systèmes hospitaliers, services de cartographie) est considéré comme **externe**. |
| **Interfaces externes** | • API de cartographie (GET / routes, géocodage) <br>• API de l’ERP hospitalier (REST / FHIR) <br>• Service de notification (SMTP, Twilio) <br>• Portail de paiement (si facturation) |
| **Acteurs / Utilisateurs** | • **Dispatcheur** – crée, suit et assigne les missions d’ambulance. <br>• **Conducteur / Personnel médical** – consulte les missions, met à jour le statut, envoie des données de télémétrie. <br>• **Administrateur système** – gère les comptes, les configurations, les logs. <br>• **Patient** (via portail) – visualise l’état d’une mission (optionnel). |
| **Environnement opérationnel** | • Hébergement cloud (AWS / Azure) – conteneurs Docker, Kubernetes. <br>• Accès via Internet (HTTPS, TLS 1.3). <br>• Conformité aux exigences de disponibilité (99,5 % Uptime) et de sécurité (RGPD, ISO 27001). |

---  

## 3. Exigences fonctionnelles (Functional Requirements)  

> **Convention d’identifiant** : `EXG‑FCT‑NNN` (exemple `EXG‑FCT‑001`).  
> Chaque exigence doit être complétée avec les attributs décrits en § 7.  

| ID | Titre | Description | Rationale | Source | Priority | Verification | Dependencies |
|----|-------|-------------|-----------|--------|----------|---------------|--------------|
| **EXG‑FCT‑001** | Authentification des utilisateurs | Le système doit permettre aux utilisateurs de s’authentifier via OAuth 2.0 / OIDC. | Sécuriser l’accès aux données sensibles | Atelier MOA – 2025‑12‑10 | Mandatory | Test d’intégration (login/logout) | – |
| **EXG‑FCT‑002** | Gestion des comptes | Un administrateur doit pouvoir créer, modifier, désactiver des comptes utilisateurs. | Gestion des droits d’accès | Spécification métier | Mandatory | Inspection du UI + tests fonctionnels | EXG‑FCT‑001 |
| **EXG‑FCT‑003** | Création d’une mission d’ambulance | Le dispatcheur peut créer une nouvelle mission en renseignant le patient, le point de prise en charge et la destination. | Répondre aux besoins opérationnels | Business case | Mandatory | Test fonctionnel (scenario “CreateMission”) | EXG‑FCT‑001 |
| **EXG‑FCT‑004** | Attribution automatique d’ambulance | Le système propose automatiquement l’ambulance la plus proche (via géolocalisation) et la met à disposition du conducteur. | Optimiser le temps de réponse | Analyse de process | Desirable | Test de simulation (distance, disponibilité) | EXG‑FCT‑003 |
| **EXG‑FCT‑005** | Suivi en temps réel | Le conducteur doit pouvoir mettre à jour le statut de la mission (en‑route, arrivée, transport, terminé). | Visibilité pour le dispatcheur | Atelier opérationnel | Mandatory | Test d’API (PUT / mission/status) | EXG‑FCT‑003 |
| **EXG‑FCT‑006** | Historique des missions | Le système conserve un historique complet (timestamp, statut, localisation) de chaque mission pendant 5 ans. | Traçabilité / audit légal | Réglementation santé | Mandatory | Inspection de la base + requêtes de recherche | EXG‑FCT‑005 |
| **EXG‑FCT‑007** | Notification aux parties prenantes | En fonction des changements de statut, le système envoie des notifications (SMS, email, push) aux parties concernées. | Améliorer la coordination | Besoin utilisateur | Desirable | Test d’envoi de notifications (mock) | EXG‑FCT‑005 |
| **EXG‑FCT‑008** | Export de rapports | L’administrateur peut exporter des rapports (CSV, PDF) sur les missions, les temps d’intervention, etc. | Reporting décisionnel | Business case | Optional | Test d’export + validation du format | EXG‑FCT‑006 |
| **EXG‑FCT‑009** | Gestion des zones de couverture | Le système doit permettre la définition de zones géographiques (polygones) pour la répartition des ambulances. | Optimiser la répartition | Analyse de terrain | Desirable | Test d’édition de zone + calcul de distance | – |
| **EXG‑FCT‑010** | Interface cartographique interactive | Le front‑end doit afficher une carte interactive avec la position en temps réel des ambulances et des missions. | Visualisation ergonomique | Atelier UI/UX | Mandatory | Test UI (Leaflet/Mapbox) | EXG‑FCT‑005 |

> **À compléter** – Les exigences ci‑dessus sont des **exemples illustratifs**. Chaque exigence devra être enrichie avec les champs **Rationale**, **Source**, **Priority**, **Verification**, **Dependencies**, **Status**, **Risk**, **Stability** conformément à la § 7 de la norme.  

---  

## 4. Exigences non‑fonctionnelles (Non‑Functional Requirements)  

### 4.1 Exigences de performance  

| ID | Titre | Description | Rationale | Priority | Verification |
|----|-------|-------------|-----------|----------|---------------|
| **EXG‑NFR‑001** | Temps de réponse UI | Le temps moyen de chargement d’une page du tableau de bord doit être ≤ 2 s (connexion 4G). | Satisfaction utilisateur | Mandatory | Test de charge (JMeter) |
| **EXG‑NFR‑002** | Débit API | L’API doit supporter **500 requêtes /s** en pic avec un taux d’erreur ≤ 0,1 %. | Dimensionnement infrastructure | Mandatory | Test de performance (k6) |
| **EXG‑NFR‑003** | Utilisation mémoire serveur | La consommation maximale de mémoire du service back‑end ne doit pas dépasser **2 GiB**. | Stabilité du service | Mandatory | Monitoring (Prometheus) |
| **EXG‑NFR‑004** | Disponibilité | Le système doit garantir une disponibilité de **99,5 %** sur une période de 30 jours. | Continuité de service | Mandatory | Analyse des logs + SLA |

### 4.2 Exigences d’interface externe  

| ID | Interface | Description | Rationale | Priority | Verification |
|----|----------|-------------|-----------|----------|---------------|
| **EXG‑INT‑001** | Cartographie | Utiliser l’API **OpenStreetMap** (ou Google Maps) en mode **HTTPS** avec clé d’accès. | Géolocalisation fiable | Mandatory | Test d’appel d’API (status 200) |
| **EXG‑INT‑002** | Notification SMS | Intégrer le service **Twilio** (ou équivalent) via REST / HTTPS. | Communication temps réel | Desirable | Test d’envoi (sandbox) |
| **EXG‑INT‑003** | ERP Hospitalier | Consommer les endpoints FHIR / REST exposés par l’ERP pour récupérer les dossiers patients. | Cohérence des données | Mandatory | Test d’interopérabilité (FHIR validation) |
| **EXG‑INT‑004** | Authentification tierce | Support SAML 2.0 ou Azure AD en plus d’OAuth2. | Flexibilité d’intégration | Optional | Test d’authentification SAML |

### 4.3 Exigences de qualité  

| ID | Qualité | Description | Rationale | Priority | Verification |
|----|---------|-------------|-----------|----------|---------------|
| **EXG‑QLT‑001** | Maintenabilité | Le code doit respecter le **standard PSR‑12** (PHP) / **ESLint** (JS) et être couvert **≥ 80 %** par des tests unitaires. | Réduction du coût de maintenance | Mandatory | Analyse de couverture (SonarQube) |
| **EXG‑QLT‑002** | Portabilité | Le système doit pouvoir être déployé sur **AWS** et **Azure** sans modification du code. | Flexibilité d’infrastructure | Desirable | Test de déploiement IaC (Terraform) |
| **EXG‑QLT‑003** | Testabilité | Chaque fonction métier doit être découpée en modules testables isolément (mocking des dépendances). | Faciliter les tests automatisés | Mandatory | Inspection du design + revue de code |
| **EXG‑QLT‑004** | Fiabilité | MTBF (Mean Time Between Failures) ≥ 200 h. | Confiance opérationnelle | Mandatory | Analyse de logs post‑déploiement |

### 4.4 Exigences de conception et contraintes  

| ID | Contrainte | Description | Rationale | Priority | Verification |
|----|------------|-------------|-----------|----------|---------------|
| **EXG‑DES‑001** | Langage | Le back‑end doit être développé en **Node.js (v18 LTS)** ou **Java 17**. | Uniformité technologique | Mandatory | Inspection du repo |
| **EXG‑DES‑002** | Framework UI | Le front‑end doit utiliser **React 18** + **TypeScript**. | Cohérence UI | Mandatory | Inspection du code |
| **EXG‑DES‑003** | Standards | Respect du **RGPD** pour la gestion des données personnelles. | Conformité légale | Mandatory | Revue juridique + tests de conformité |
| **EXG‑DES‑004** | Outils CI/CD | Utiliser **GitLab‑CI** avec pipelines de lint, test, build, déploiement. | Automatisation du flux | Mandatory | Vérification du fichier `.gitlab-ci.yml` |

### 4.5 Exigences de sécurité  

| ID | Sécurité | Description | Rationale | Priority | Verification |
|----|----------|-------------|-----------|----------|---------------|
| **EXG‑SEC‑001** | Confidentialité | Toutes les communications doivent être chiffrées **TLS 1.3**. | Protection des données en transit | Mandatory | Scan SSL (Qualys) |
| **EXG‑SEC‑002** | Intégrité | Les messages via la file de messagerie doivent être signés (HMAC). | Prévention de la falsification | Mandatory | Tests d’intégrité |
| **EXG‑SEC‑003** | Disponibilité | Mise en place d’un **load‑balancer** et de **auto‑scaling**. | Résilience aux pics de charge | Mandatory | Tests de charge + failover |
| **EXG‑SEC‑004** | Authentification forte | Support de **MFA** (TOTP ou SMS) pour les comptes administrateur. | Réduction du risque d’accès non autorisé | Desirable | Test d’authentification MFA |
| **EXG‑SEC‑005** | Gestion des secrets | Utiliser **Vault** ou **AWS Secrets Manager** pour stocker les clés API. | Sécurisation des secrets | Mandatory | Audit de configuration |

---  

## 5. Modèle de données conceptuel  

```mermaid
classDiagram
    class Patient {
    +String id;
    +String firstName;
    +String lastName;
    +Date   birthDate;
    +String gender;
    +String phone;
    +String address;

    class Ambulance {
    +String id;
    +String licensePlate;
    +String model;
    +String status   // AVAILABLE, EN_ROUTE, MAINTENANCE;
    +String driverId;

    class Mission {
    +String id;
    +DateTime requestTime;
    +DateTime startTime;
    +DateTime endTime;
    +String status   // PENDING, ASSIGNED, EN_ROUTE, ARRIVED, COMPLETED, CANCELED;
    +String patientId;
    +String ambulanceId;
    +String pickupLocation;
    +String destinationLocation;
    +String notes;

    class User {
    +String id;
    +String email;
    +String role   // DISPATCHER, DRIVER, ADMIN, PATIENT;
    +String passwordHash;
    +Boolean active;

    class Notification {
    +String id;
    +String missionId;
    +String recipientId;
    +String channel   // EMAIL, SMS, PUSH;
    +String status    // SENT, FAILED, PENDING;
    +DateTime sentAt;

    Patient "1" <-- "0..*" Mission : patient;
    Ambulance "1" <-- "0..*" Mission : ambulance;
    User "1" <-- "0..*" Mission : dispatcher;
    User "1" <-- "0..*" Ambulance : driver;
    Mission "1" <-- "0..*" Notification : mission
```

| Entité | Description | Principaux attributs |
|--------|-------------|----------------------|
| **Patient** | Données d’identité du patient transporté. | `id`, `firstName`, `lastName`, `birthDate`, `gender`, `phone`, `address` |
| **Ambulance** | Véhicule d’intervention. | `id`, `licensePlate`, `model`, `status`, `driverId` |
| **Mission** | Demande d’intervention d’une ambulance. | `id`, `requestTime`, `status`, `patientId`, `ambulanceId`, `pickupLocation`, `destinationLocation` |
| **User** | Compte utilisateur (dispatcher, driver, admin). | `id`, `email`, `role`, `passwordHash`, `active` |
| **Notification** | Message envoyé à un destinataire (SMS, email, push). | `id`, `missionId`, `recipientId`, `channel`, `status`, `sentAt` |

---  

## 6. Modélisation des comportements  

### 6.1 Diagrammes de cas d’utilisation (UML)  

```mermaid
%%{init: {'theme':'default'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
usecaseDiagram;
    actor Dispatcher as D;
    actor Driver as DR;
    actor Admin as A;
    actor Patient as P;
    D --> (Créer une mission)
    D --> (Assigner une ambulance)
    D --> (Consulter l’historique)
    DR --> (Mettre à jour le statut)
    DR --> (Visualiser la mission)
    A --> (Gérer les comptes)
    A --> (Configurer les zones)
    P --> (Consulter le statut de sa mission) 
```

### 6.2 Diagrammes d’activités (processus de création d’une mission)  

```mermaid
statediagram-v2;
    [*] --> SaisieDemande;
    SaisieDemande --> Validation : Données valides ?
    Validation --> [*] : Rejet (erreurs)
    Validation --> Attribution : OK;
    Attribution --> NotifierDispatcher;
    NotifierDispatcher --> [*]
```

### 6.3 Diagrammes d’états (Cycle de vie d’une mission)  

```mermaid
statediagram-v2;
    [*] --> PENDING;
    PENDING --> ASSIGNED : Ambulance assignée;
    ASSIGNED --> EN_ROUTE : Conducteur accepte;
    EN_ROUTE --> ARRIVED : Arrivée sur site;
    ARRIVED --> TRANSPORT : Transport du patient;
    TRANSPORT --> COMPLETED : Arrivée à l’hôpital;
    COMPLETED --> [*]
    PENDING --> CANCELED : Annulation client;
    ASSIGNED --> CANCELED : Annulation;
    EN_ROUTE --> CANCELED : Annulation d’urgence
```

### 6.4 Diagrammes de séquence (Scénario « Création + Attribution »)  

```mermaid
sequencediagram;
    participant D as Dispatcher;
    participant API as API;
    participant DB as DB;
    participant MAP as Cartographie;
    participant NOTIF as Service Notification;
    D->>API: POST /missions (payload)
    API->>DB: INSERT mission (status=PENDING)
    API->>MAP: GET nearest ambulance;
    MAP-->>API: ambulanceId;
    API->>DB: UPDATE mission (ambulanceId, status=ASSIGNED)
    API->>NOTIF: send notification (driver, dispatcher)
    NOTIF-->>D: ACK;
    Note right of API: Retour 201 Created
```

---  

## 7. Attributs d’exigences (Requirements Attributes)  

| Attribut | Exemple (EXG‑FCT‑001) |
|----------|------------------------|
| **Identifiant** | EXG‑FCT‑001 |
| **Description** | Le système doit permettre aux utilisateurs de s’authentifier via OAuth 2.0 / OIDC. |
| **Rationale** | Sécuriser l’accès aux données sensibles et garantir la conformité RGPD. |
| **Source** | Atelier MOA du 10/12/2025 – Responsable Sécurité. |
| **Priority** | Mandatory |
| **Status** | Draft |
| **Verification Method** | Test d’intégration (login/logout) – Test automatisé avec Cypress. |
| **Risk** | High (si non‑implémenté, fuite de données). |
| **Stability** | Stable (norme OAuth2 largement adoptée). |
| **Owner** | Squad Auth (team‑auth). |
| **Created On** | 2026‑04‑27 |
| **Last Modified** | 2026‑04‑27 |

*(Tous les items du tableau § 3 et § 4 devront être enrichis de ces attributs.)*  

---  

## 8. Traçabilité des exigences  

### 8.1 Matrice de traçabilité (Requirements Traceability Matrix – RTM)

| ID Exigence | Besoin métier (ID) | Objectif système (ID) | Cas d’utilisation | Scénario de test (ID) | Implémentation (module) |
|-------------|--------------------|-----------------------|-----------------|-----------------------|------------------------|
| EXG‑FCT‑001 | BM‑001 (Authentification sécurisée) | SYS‑001 (Gestion des identités) | UC‑01 (S’authentifier) | TC‑FCT‑001‑Login | auth-service |
| EXG‑FCT‑003 | BM‑003 (Gestion des missions) | SYS‑003 (Gestion des interventions) | UC‑03 (Créer mission) | TC‑FCT‑003‑CreateMission | mission‑controller |
| EXG‑NFR‑001 | BM‑005 (Expérience utilisateur) | SYS‑005 (Performance UI) | UC‑01, UC‑03 | TC‑NFR‑001‑PageLoad | front‑app |
| EXG‑SEC‑001 | BM‑010 (Conformité RGPD) | SYS‑010 (Sécurité des communications) | UC‑01, UC‑04 | TC‑SEC‑001‑TLS | gateway‑api |
| … | … | … | … | … | … |

> **Action requise** – Fournir les identifiants des besoins métier (ex. `BM‑001`) et des objectifs système afin de finaliser la RTM.

### 8.2 Liens vers les tests de validation  

| Test ID | Description | Type | Couverture exigence |
|---------|-------------|------|----------------------|
| TC‑FCT‑001‑Login | Vérifie que l’utilisateur peut se connecter avec credentials valides. | Fonctionnel | EXG‑FCT‑001 |
| TC‑FCT‑003‑CreateMission | Simule la création d’une mission via l’API. | Fonctionnel | EXG‑FCT‑003 |
| TC‑NFR‑001‑PageLoad | Mesure le temps de chargement de la page tableau de bord. | Performance | EXG‑NFR‑001 |
| TC‑SEC‑001‑TLS | Scanne le serveur pour vérifier la présence de TLS 1.3 uniquement. | Sécurité | EXG‑SEC‑001 |
| … | … | … | … |

---  

## 9. Gestion des exigences  

| Processus | Description | Responsable | Outil(s) recommandé(s) |
|-----------|-------------|--------------|------------------------|
| **Capture** | Recueil des besoins via ateliers, interviews, analyse documentaire. | Business Analyst | Confluence, Miro |
| **Analyse & Classification** | Décomposition en exigences fonctionnelles / non‑fonctionnelles, attribution de priorité. | Ingénieur exigences | IBM DOORS, Jira + Requirements Plugin |
| **Validation** | Revues formelles (peer‑review, revue de conformité). | Comité de pilotage | Review Board (Confluence) |
| **Gestion du changement** | Processus de demande de modification (CR), impact analysis, approbation. | Change Manager | ServiceNow Change, Jira Workflow |
| **Traçabilité** | Mise à jour continue de la RTM, liens entre exigences, design, tests. | Gestionnaire de configuration | DOORS, Jama Connect |
| **Publication** | Diffusion du CCF (PDF/Markdown) aux parties prenantes. | Responsable documentation | GitLab‑Pages, SharePoint |
| **Audit** | Vérification périodique de la conformité ISO 29148. | Auditeur interne | Checklist ISO 29148 |

---  

## 10. Validation et vérification  

| Phase | Activité | Méthode | Responsable | Entrée | Sortie |
|-------|----------|---------|-------------|--------|--------|
| **Vérification (développement)** | Revue de conception (design review) | Inspection | Architecte | CCF, Modèles UML | Rapport de revue |
| **Vérification (intégration)** | Exécution des tests unitaires & d’intégration | Test automatisé (Jest, Mocha, JUnit) | Développeur | Code, Tests | Rapport de couverture ≥ 80 % |
| **Validation (système)** | Tests d’acceptation utilisateur (UAT) | BDD (Cucumber) – scénarios Given/When/Then | PO / Utilisateur final | CCF, RTM, Scénarios de test | Sign‑off UAT |
| **Validation (déploiement)** | Test de charge & résilience | k6 + chaos‑monkey | Ops / SRE | Environnements pré‑prod | Rapport de performance |
| **Validation (sécurité)** | Scan de vulnérabilités & audit RGPD | OWASP ZAP, Qualys, DPO review | Sécurité | CCF, Code | Rapport de conformité |
| **Clôture** | Acceptance final du produit | Comité de pilotage | Sponsor | Tous les rapports | Baseline du produit, mise en production |

---  

# 📌 Prochaines étapes (à planifier avec le commanditaire)  

1. **Collecte détaillée des besoins métier** – fournir la liste des `BM‑XXX` (besoins) ainsi que les priorités business.  
2. **Attribution des parties prenantes** – identifier les responsables pour chaque domaine (authentification, cartographie, notifications, etc.).  
3. **Enrichissement des exigences** – compléter les champs **Rationale**, **Source**, **Risk**, **Stability**, **Owner** pour chaque exigence.  
4. **Validation du modèle de données** – confirmer les entités, attributs et contraintes (ex. RGPD, anonymisation).  
5. **Planification des revues** – organiser les revues de CCF (ex. sprint 0, sprint 2, etc.) et définir les critères d’acceptation.  

---  

*Ce document est fourni à titre de **squelette fonctionnel**. Il doit être itéré, enrichi et approuvé conformément aux processus de gouvernance de votre organisation.*  