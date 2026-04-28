# Cahier des Charges Fonctionnel (CCF) – **agile‑back**  
*Conforme à la norme ISO/IEC/IEEE 29148 :2018*  

---  

## 1️⃣ Identification et contexte du document  

| Élément | Valeur |
|---|---|
| **Identifiant du document** | **CCF‑AGILE‑BACK‑V1.0** |
| **Version** | 1.0 (2024‑04‑27) |
| **Historique des modifications** | 2024‑04‑27 – création (v1.0) |
| **Références** | • `README.md` – description du projet <br>• Vision du produit (non fournie – à compléter) <br>• Business case (à créer) |
| **Portée** | Ce CCF décrit les exigences fonctionnelles et non‑fonctionnelles du **back‑office** de l’application *Agile* (module *agile‑back*). Il couvre la partie serveur (PHP / Symfony 5+, API Platform, PostgreSQL) ainsi que les interfaces web et API exposées aux applications *Agile‑front* et aux services externes (CAS). |
| **Objectifs** | • Permettre la création, la modification, la consultation et la suppression (CRUD) d’études, de dotations, de financements, de groupes, de profils, de services, etc. <br>• Assurer l’authentification unique via CAS et la gestion fine des droits (RBAC). <br>• Exposer des API REST conformes à OpenAPI pour la consommation par le front‑office et d’éventuels systèmes tiers. <br>• Garantir la traçabilité, la maintenabilité et la sécurité du système tout au long de son cycle de vie. |

---  

## 2️⃣ Description de l’écosystème (System/Software Context)

```mermaid
graph LR;
    subgraph "Utilisateur"
        U1[Utilisateur (admin)]
        U2[Utilisateur (consultant)]
    end;
    subgraph "Système agile‑back"
        B[agile‑back (Symfony/PHP)]
        DB[(PostgreSQL DB)]
        CAS[CAS (phpCAS)]
        API[API Platform (REST/JSON)]
        UI[Interface web (Twig)]
    end;
    subgraph "Systèmes externes"
        FE[agile‑front (Vue/JS)]
        ES[Services d’e‑mail (SMTP)]
    end;
    U1 -->|login| B;
    U2 -->|login| B;
    B -->|authentification| CAS;
    B -->|lecture/écriture| DB;
    B -->|expose| API;
    B -->|rend| UI;
    UI --> FE;
    API --> FE;
    B -->|envoi| ES
```

* **Frontières du système** : Le périmètre *agile‑back* inclut le code source sous `src/`, les configurations Symfony (`config/`), les templates Twig (`templates/`) et les assets web (`public/`).  
* **Interfaces externes** :  
  * **CAS** – authentification unique (SSO) via le composant `phpCAS`.  
  * **API Platform** – point d’entrée REST (`/api/*`).  
  * **SMTP** – envoi de notifications e‑mail (`swiftmailer`).  
  * **agile‑front** – consomme les API et les pages HTML.  
* **Acteurs** :  
  * **Administrateur** – crée, modifie, supprime toutes les entités, configure les droits.  
  * **Consultant / Utilisateur métier** – crée et édite ses propres études, visualise les dotations, etc.  
* **Environnement opérationnel** : Serveur web (Apache/Nginx), PHP 8.x, Symfony 5+, PostgreSQL 13+, conteneurisation possible (Docker).  

---  

## 3️⃣ Exigences fonctionnelles (Functional Requirements)  

> **Notation** : `[ID] Titre` – chaque exigence suit le format ISO 29148.  

| ID | Titre | Description | Rationale | Source | Priority | Verification | Dependencies |
|---|---|---|---|---|---|---|---|
| **EXG‑FCT‑001** | Authentification SSO via CAS | Le système doit authentifier tout utilisateur en le redirigeant vers le serveur CAS et accepter le ticket CAS valide. | Conformité aux exigences de sécurité du ministère | Atelier MOA 2024‑03‑15 | Mandatory | Test d’intégration (login → CAS → redirection) | – |
| **EXG‑FCT‑002** | Gestion des rôles (RBAC) | L’administrateur doit pouvoir assigner les rôles **ROLE_ADMIN**, **ROLE_USER**, **ROLE_VIEWER** à chaque compte. | Besoin de contrôle d’accès granulaire | Spécifications fonctionnelles | Mandatory | Inspection du tableau `roles` dans la base + tests unitaires | EXG‑FCT‑001 |
| **EXG‑FCT‑003** | CRUD Études | Les utilisateurs avec le rôle adéquat peuvent créer, lire, mettre à jour et supprimer des études (`Etudes` entity). | Gestion du cœur métier (études) | Analyse de code (src/Entity/Etudes.php) | Mandatory | Tests fonctionnels (POST/GET/PUT/DELETE) | EXG‑FCT‑002 |
| **EXG‑FCT‑004** | Export études au format CSV/ODS | L’utilisateur peut déclencher l’export des études sélectionnées au format CSV ou ODS via `/exports`. | Faciliter les traitements hors‑ligne | User story US‑EXPORT‑01 | Desirable | Vérification du fichier généré (contenu, format) | EXG‑FCT‑003 |
| **EXG‑FCT‑005** | Gestion des Dotations | CRUD complet sur l’entité `Dotations` (année, montant, groupe, bop, sous‑action). | Suivi budgétaire | Analyse de code (src/Entity/Dotations.php) | Mandatory | Tests fonctionnels + validation de contraintes DB | EXG‑FCT‑002 |
| **EXG‑FCT‑006** | Gestion des Financements | CRUD complet sur l’entité `Financements` (demande, date comité, AE, CP). | Gestion financière des études | Analyse de code (src/Entity/Financements.php) | Mandatory | Tests fonctionnels + règles métier (ex. montant > 0) | EXG‑FCT‑002 |
| **EXG‑FCT‑007** | Gestion des référentiels (Groupes, Bop, Themes, Types) | CRUD sur les entités de référence utilisées dans les études. | Centraliser les référentiels | Analyse de code (src/Entity/*.php) | Mandatory | Tests unitaires | EXG‑FCT‑002 |
| **EXG‑FCT‑008** | API REST conformes à OpenAPI | Le module `api_platform` doit exposer les ressources `Etudes`, `Dotations`, `Financements`, `Groupes`, etc. avec les opérations CRUD. | Interopérabilité avec *agile‑front* et d’autres systèmes | Architecture technique | Mandatory | Inspection du fichier `openapi.yaml` généré | EXG‑FCT‑001 |
| **EXG‑FCT‑009** | Envoi de notifications e‑mail | À chaque création/modification d’une étude, un e‑mail doit être envoyé aux parties prenantes (via `swiftmailer`). | Traçabilité et communication | User story US‑MAIL‑02 | Desirable | Test d’envoi (mailtrap / mock) | EXG‑FCT‑003 |
| **EXG‑FCT‑010** | Gestion des états d’une étude | Une étude passe par les états **Brouillon → En cours → Validée → Archivée**. Les transitions sont contrôlées par le service `Valorisation`. | Suivi du cycle de vie | Analyse métier | Mandatory | Tests de state‑machine + diagramme d’états | EXG‑FCT‑003 |
| **EXG‑FCT‑011** | Historisation des modifications | Chaque modification d’une entité doit être journalisée (table `audit_log`). | Conformité aux exigences d’audit | Spécifications de sécurité | Optional | Inspection de la table `audit_log` + tests | EXG‑FCT‑002 |
| **EXG‑FCT‑012** | Recherche plein texte sur les études | L’interface doit permettre de rechercher les études par titre, zone géographique, groupe, etc. | Améliorer l’expérience utilisateur | User story US‑SEARCH‑01 | Desirable | Test d’intégration (requête Elasticsearch ou PostgreSQL full‑text) | EXG‑FCT‑003 |

> **Remarque** : La liste ci‑dessus n’est pas exhaustive ; d’autres exigences peuvent être ajoutées lors de la phase d’analyse détaillée.

---  

## 4️⃣ Exigences non‑fonctionnelles (Non‑Functional Requirements)

### 4.1 Performance  

| ID | Description |
|---|---|
| **EXG‑NFR‑001** | Temps de réponse < 2 s pour toutes les requêtes UI (pages list, formulaire) en environnement de production. |
| **EXG‑NFR‑002** | Temps de réponse < 500 ms pour les appels API REST (GET/POST) en charge normale (≤ 200 req/s). |
| **EXG‑NFR‑003** | Capacité de traitement d’au moins 1 000 études créées par jour sans dégradation. |
| **EXG‑NFR‑004** | Utilisation maximale de la RAM du processus PHP ≤ 256 Mo sous charge maximale. |

### 4.2 Exigences d’interface externe  

| ID | Description |
|---|---|
| **EXG‑INT‑001** | **Interface web** – pages rendues avec Twig, compatibles navigateur Chrome/Firefox ≥ 90 % et responsive (≥ 768 px). |
| **EXG‑INT‑002** | **API** – conformité OpenAPI 3.0, support JSON (`application/json`) et CSV (`text/csv`). |
| **EXG‑INT‑003** | **CAS** – protocole CAS 3.0, connexion sécurisée TLS 1.2+. |
| **EXG‑INT‑004** | **SMTP** – serveur configurable via `MAILER_DSN`, authentification TLS obligatoire. |

### 4.3 Qualité  

| ID | Description |
|---|---|
| **EXG‑QLT‑001** | **Maintenabilité** – code conforme à PSR‑12, couverture de tests unitaires ≥ 80 %. |
| **EXG‑QLT‑002** | **Portabilité** – le projet doit fonctionner sous Linux (Ubuntu 22.04) et Windows (WSL). |
| **EXG‑QLT‑003** | **Testabilité** – chaque composant (controller, service, repository) doit être testable isolément (mockable). |
| **EXG‑QLT‑004** | **Fiabilité** – taux d’erreur serveur < 0,1 % en production, redémarrage sans perte de donnée (transactions). |

### 4.4 Conception et contraintes  

| ID | Description |
|---|---|
| **EXG‑DES‑001** | **Langage** – PHP 8.1 minimum. |
| **EXG‑DES‑002** | **Framework** – Symfony 5.4 LTS, API Platform 2.6+. |
| **EXG‑DES‑003** | **Base de données** – PostgreSQL 13+, schéma versionné via Doctrine Migrations. |
| **EXG‑DES‑004** | **Outils obligatoires** – Composer, Git, Docker (optionnel). |
| **EXG‑DES‑005** | **Gestion de configuration** – variables d’environnement via `.env` (Dotenv). |

### 4.5 Sécurité  

| ID | Description |
|---|---|
| **EXG‑SEC‑001** | **Confidentialité** – toutes les communications HTTP/HTTPS doivent être chiffrées (TLS 1.2+). |
| **EXG‑SEC‑002** | **Intégrité** – validation du ticket CAS, protection CSRF sur les formulaires (`csrf_token`). |
| **EXG‑SEC‑003** | **Disponibilité** – le service doit être disponible 99,5 % (MTBF ≥ 30 jours). |
| **EXG‑SEC‑004** | **Authentification** – uniquement via CAS, aucune authentification locale. |
| **EXG‑SEC‑005** | **Autorisation** – contrôle d’accès basé sur les rôles (RBAC) implémenté dans les Voter Symfony. |
| **EXG‑SEC‑006** | **Journalisation** – les événements de sécurité (login, échec, accès admin) doivent être consignés dans le logger `security`. |
| **EXG‑SEC‑007** | **Protection contre les injections** – utilisation de Doctrine ORM avec paramètres liés, validation des entrées (Symfony Validator). |

---  

## 5️⃣ Modèle de données conceptuel  

```mermaid
classdiagram;
    class Etudes {
        +int id;
        +string titreEtude;
        +string zoneGeographique;
        +string contexte;
        +string problematique;
        +string resultatsAttendus;
        +string objectifs;
        +string methode;
        +string valorisationComment;
        +string valorisationUrl;
        +DateTime createdAt;
        +DateTime updatedAt;
    }
    class Bop {
        +int id;
        +string libelleBop;
        +string commentairesBop;
        +string sigle;
        +bool visible;
    }
    class Dotations {
        +int id;
        +int anneeDotation;
        +float montantDotation;
        +string sousAction;
        +bool visible;
    }
    class Financements {
        +int id;
        +float demandeE;
        +DateTime dateComite;
        +float aeE;
        +float cpE;
    }
    class Groupes {
        +int id;
        +string token;
        +string libelle;
    }
    class Profils {
        +int id;
        +string libelle;
    }
    class Services {
        +int id;
        +string service;
        +string direction;
        +bool visible;
        +string region;
    }
    class Utilisateurs {
        +int id;
        +string email;
        +string nom;
        +string prenom;
        +string ru;
        +bool actif;
    }
    class Territoires {
        +int id;
        +string territoire;
    }
    class Themes {
        +int id;
        +string theme;
    }
    class Types {
        +int id;
        +string type;
    }

    Etudes --> "1" Bop : bopId;
    Etudes --> "1..*" Dotations : dotations;
    Etudes --> "1..*" Financements : financements;
    Etudes --> "1" Groupes : groupe;
    Etudes --> "1" Profils : profil;
    Etudes --> "1" Services : service;
    Etudes --> "1" Territoires : territoire;
    Etudes --> "1" Themes : theme;
    Etudes --> "1" Types : type;
    Utilisateurs --> "1" Groupes : groupe;
    Utilisateurs --> "1" Profils : profil
```

---  

## 6️⃣ Modélisation des comportements  

### 6.1 Diagramme de cas d’utilisation  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#fff' }}%%}%%
usecaseDiagram;
    actor Admin as A;
    actor Utilisateur as U;
    A --> (Authentifier via CAS)
    A --> (Gérer les études)
    A --> (Gérer les référentiels)
    A --> (Exporter les données)
    A --> (Configurer les rôles)

    U --> (Authentifier via CAS)
    U --> (Consulter ses études)
    U --> (Créer/Modifier une étude)
    U --> (Exporter ses études)
```

### 6.2 Diagramme d’activité – Création d’une étude  

```mermaid
statediagram-v2;
    [*] --> Authentifié;
    Authentifié --> Vérifier_Rôle;
    Vérifier_Rôle --> Formulaire;
    Formulaire --> Saisie_Données;
    Saisie_Données --> Validation;
    Validation -->[valid] Persistance;
    Persistance --> Notification_E_mail;
    Notification_E_mail --> [*]
    Validation -->[invalid] Erreur_Formulaire;
    Erreur_Formulaire --> Formulaire
```

### 6.3 Diagramme d’états – Cycle de vie d’une étude  

```mermaid
statediagram-v2;
    [*] --> Brouillon;
    Brouillon --> EnCours : submit()
    EnCours --> Validée : approve()
    Validée --> Archivée : archive()
    Validée --> Rejetée : reject()
    Rejetée --> Brouillon : edit()
```

### 6.4 Diagramme de séquence – Authentification CAS  

```mermaid
sequencediagram;
    participant User as Utilisateur;
    participant Web as navigateur;
    participant App as agile‑back;
    participant CAS as serveur CAS;
    User->>Web: Accès à /login;
    Web->>App: GET /login;
    App->>Web: Redirige vers CAS (serviceURL)
    Web->>CAS: GET /login?service=...
    CAS->>Web: Formulaire login;
    User->>Web: saisit identifiants;
    Web->>CAS: POST credentials;
    CAS->>CAS: Vérifie credentials;
    CAS->>Web: Ticket CAS (ticket=ST-xxxx)
    Web->>App: GET /login?ticket=ST-xxxx;
    App->>CAS: Validation ticket;
    CAS-->>App: Réponse OK + attributs utilisateur;
    App->>Web: Session créée, redirection vers page d’accueil
```

---  

## 7️⃣ Attributs d’exigences (Requirements Attributes)

| Identifiant | Description | Exemple |
|---|---|---|
| **Identifiant** | Code unique (préfixe catégorie + séquence) | `EXG‑FCT‑001` |
| **Description** | Énoncé complet de l’exigence | « Le système doit authentifier l’utilisateur via CAS » |
| **Rationale** | Pourquoi l’exigence est requise | Conformité à la politique de sécurité du ministère |
| **Source** | Origine de l’exigence | Atelier MOA 2024‑03‑15 |
| **Priority** | Niveau de priorité (Mandatory / Desirable / Optional) | Mandatory |
| **Status** | État actuel (Draft / Approved / Baseline) | Approved |
| **Verification Method** | Méthode de vérification (Inspection / Test / Analyse) | Test d’intégration |
| **Risk** | Niveau de risque (High / Medium / Low) | Low |
| **Stability** | Probabilité de changement (Stable / Volatile) | Stable |

---  

## 8️⃣ Traçabilité des exigences  

| Exigence | Objectif métier | Cas d’utilisation | Test(s) |
|---|---|---|---|
| EXG‑FCT‑001 | Sécuriser l’accès aux données | Authentifier via CAS | TC‑AUTH‑01 (login OK) |
| EXG‑FCT‑003 | Permettre la saisie d’études | Créer/Modifier une étude | TC‑ETUDE‑01 (POST /etudes) |
| EXG‑FCT‑004 | Exporter les données pour analyse | Export études | TC‑EXPORT‑01 (CSV) |
| EXG‑NFR‑001 | Garantir expérience utilisateur | Toutes les pages UI | TC‑PERF‑01 (Page load <2 s) |
| EXG‑SEC‑001 | Protéger la confidentialité | Toutes les communications | TC‑SEC‑01 (TLS check) |
| EXG‑DES‑001 | Alignement technologique | Tous les développements | TC‑CODE‑01 (PHP 8.1) |

*La matrice complète (exigences → exigences de haut niveau → scénarios de test) sera maintenue dans l’outil **Jira / GitLab Issues** et synchronisée avec les commits.*

---  

## 9️⃣ Gestion des exigences  

| Processus | Description | Responsable | Outils |
|---|---|---|---|
| **Gestion du changement** | Toute modification d’une exigence doit passer par une *Change Request* (CR) évaluée en impact, priorité et coût. | Chef de projet / PO | Jira (Issue type = Change Request) |
| **Résolution des conflits** | Conflits entre exigences fonctionnelles et non‑fonctionnelles sont résolus en réunion de pilotage (bi‑hebdomadaire). | PO + Architecte | Confluence (Registre de décision) |
| **Priorisation** | Méthode MoSCoW (Must, Should, Could, Won’t) appliquée à chaque sprint. | PO | Jira (Backlog) |
| **Outils de suivi** | - **Jira** : backlog, exigences, tests <br> - **GitLab CI** : automatisation des tests <br> - **Confluence** : documentation CCF | Équipe projet | – |
| **Versionnage** | Le CCF est versionné dans le dépôt Git (`docs/CCF_agile-back_vX.Y.md`). | PO | GitLab |

---  

## 🔟 Validation et vérification  

| Critère d’acceptation | Méthode de validation | Responsable |
|---|---|---|
| **Authentification CAS fonctionnelle** | Test d’intégration automatisé (cURL) + test manuel de login | QA |
| **CRUD Études conforme** | Tests fonctionnels (PHPUnit + Behat) couvrant 100 % des routes | Développeur |
| **Export CSV** | Vérification du format et des données exportées (tests d’intégration) | QA |
| **Temps de réponse < 2 s** | Tests de charge (JMeter) sur environnement staging | Performance Engineer |
| **Sécurité TLS** | Scan SSL (Qualys SSL Labs) | Security Engineer |
| **Contrôle RBAC** | Tests d’autorisation (Voter) pour chaque rôle | QA |
| **Documentation OpenAPI** | Validation du fichier `openapi.yaml` via *swagger-cli* | Architecte |
| **Audit log** | Vérification de l’insertion d’une ligne dans `audit_log` pour chaque modification | QA |

*Tous les tests sont automatisés et exécutés à chaque pipeline CI / CD. Le passage de la **gate de qualité** (≥ 80 % de couverture, aucune faille de sécurité critique) est conditionnant la mise en production.*

---  

## 📎 Annexes  

* **Annexe A – Glossaire** (CAS, RBAC, DTO, API Platform, etc.)  
* **Annexe B – Modèle de données détaillé** (fichiers `src/Entity/*.php`).  
* **Annexe C – Table de correspondance des rôles** (`ROLE_ADMIN`, `ROLE_USER`, `ROLE_VIEWER`).  
* **Annexe D – Scripts de migration Doctrine** (`src/Migrations/`).  

---  

*Document préparé par l’équipe d’ingénierie exigences – certifiée ISO 29148, le 27 avril 2026.*  