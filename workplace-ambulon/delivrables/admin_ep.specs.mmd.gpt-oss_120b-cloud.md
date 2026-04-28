# 📘 **Spécification fonctionnelle et technique de l’application admin_ep**

> **Nom de l’application** : **admin_ep** (Administration des établissements publics)  
> **Version** : 1.3.3 (Production)  
> **Date** : 27‑04‑2026  

---

## 📑 Table des matières  

| # | Section | Lien |
|---|---------|------|
| 1 | **1️⃣ Portée, domaine et périmètre** | [⮕](#11-portée-domaine-et-périmètre) |
| 2 | **2️⃣ Architecture fonctionnelle (arc42 – partie fonctionnelle)** | [⮕](#2-architecture-fonctionnelle) |
| 3 | **3️⃣ Architecture technique (arc42 – partie technique)** | [⮕](#3-architecture-technique) |
| 4 | **4️⃣ Analyse de la sécurité** | [⮕](#4-analyse-de-la-sécurité) |
| 5 | **5️⃣ Dette technique** | [⮕](#5-dette-technique) |
| 6 | **6️⃣ Annexes** | [⮕](#6-annexes) |

> **Note** : Tous les diagrammes sont au format **Mermaid** et fonctionnent dans VS Code (extension *Markdown Preview Enhanced*) ou Obsidian. Aucun fichier externe n’est requis.  
> **Documentation arc42** : <https://arc42.org> (lien externe uniquement à titre de référence).

---

## 1️⃣ **Portée, domaine et périmètre** <a id="11-portée-domaine-et-périmètre"></a>

### 1.1 Domaine applicatif  
> **Archivage physique** des mandats et pièces associées des membres des conseils d’administration des établissements publics placés sous la tutelle du ministère de la Transition Écologique et Solidaire (MTES‑MCT).

### 1.2 Contexte opérationnel  

| Élément | Valeur |
|---------|--------|
| **Site (SIT_ID)** | `29` |
| **Base de données** | Oracle / PostgreSQL (schema *integration* dans la base `prep37`) |
| **Environnement d’exécution** | Tomcat 9 (production) → conteneurisation en cours (Docker) |
| **Hébergement** | Centre‑serveur ministériel Paris La Défense (Production, Pré‑production, Recette) |

### 1.3 Périmètre fonctionnel  

| Inclus | Exclu |
|--------|-------|
| • **Versements** (saisie / mise à jour de mandats) <br>• **Demandes** (recherche, consultation) <br>• **Mouvements** (alerte d’échéance, archivage) <br>• Gestion des **établissements**, **colleges**, **charges** et **directions** <br>• Import automatisé du **JO** (Journal Officiel) <br>• Authentification / autorisation via **Cerbère** <br>• Statistiques globales <br>• Export PDF/CSV | • Gestion des **patients** <br>• **Facturation** <br>• Workflow avancé (ex. BPMN complet) <br>• Gestion des **documents légaux** hors mandats (ex. contrats) |

### 1.4 Acteurs & rôles  

| Acteur | Rôle métier | Rôle applicatif (Arc42) |
|--------|--------------|------------------------|
| **Maîtrise d’ouvrage (MOA)** – SG/SPES | Définition des besoins, validation | Stakeholder |
| **Maîtrise d’œuvre (MOE)** – SG/SNUM/PNM/DPNM3/BPN | Conception, développement, support | Architecture Team |
| **Prestataire** – CGI | Développement, maintenance | Supplier |
| **Utilisateurs finaux** – SPES, DG de tutelle, opérateurs | Saisie, consultation, suivi d’échéances | End‑User |
| **Gestionnaire** (profil Cerbère) | Gestion des droits d’accès | Security Manager |
| **Service JORF** (script d’import) | Extraction des articles JORF | External System |

---

## 2️⃣ **Architecture fonctionnelle** <a id="2-architecture-fonctionnelle"></a>

### 2.1 Acteurs & cas d’usage (Use‑Case)  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#004080', 'secondaryColor': '#cce6ff'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
usecaseDiagram;
    actor Gestionnaire (Cerbère) as G;
    actor Opérateur as O;
    actor Service JORF (Automatisé) as J;
    rectangle AdminEP {
    G --> (Authentifier l’utilisateur)
    G --> (Consulter la liste des administrateurs)
    G --> (Créer / Mettre à jour un administrateur)
    G --> (Gérer les établissements / colleges)
    G --> (Définir les mandats (Titulaire / Suppléant))
    G --> (Configurer les alertes d’échéance)
    G --> (Consulter les statistiques)

    O --> (Rechercher un établissement ou un administrateur)
    O --> (Visualiser les mandats en cours)

    J --> (Importer les articles JORF)
    J --> (Enrichir la base de données)

```

> **Lien de navigation** :  
> - Retour au [sommaire](#📑-table-des-matières)  
> - Retour à la **section 2** – [Architecture fonctionnelle](#2-architecture-fonctionnelle)

### 2.2 Règles métier (extraits)  

| Règle | Description | Implémentation (exemple) |
|-------|-------------|--------------------------|
| **R‑01 Format de date** | Les dates de mandat sont au format `yyyy‑MM‑dd`. | `FormatterDateRange` (classe Java) |
| **R‑02 Type de mandat** | Deux types : `Titulaire` (ID = 1) et `Suppléant` (ID = 2). | Table `TYPE_MANDAT` |
| **R‑03 Mapping charge ↔ ministère** | Une charge peut être rattachée à plusieurs ministères via `MINISTERE_CHARGE`. | Table `MINISTERE_CHARGE` (N‑N) |
| **R‑04 Mode de nomination** | 3 modes (Arrêté, Décret, Décret Président) – recherche par mots‑clés. | Table `MODE_NOMINATION` |
| **R‑05 Alertes d’échéance** | Un mail est envoyé 30 jours avant la fin du mandat. | `SchedulerInitializer` + `MandatsResolver` |
| **R‑06 Import JORF** | L’import ne s’exécute que si le titre de l’article contient un **code établissement** ou un **nom d’administrateur** déjà présent. | `ArticleAnalyser` → `StepAnalyseRechercheColleges` / `StepAnalyseRechercheNominations` |

### 2.3 Tableaux de décision (exemple)  

#### Table de décision – Type de mandat selon la durée  

| Durée du mandat (mois) | > 12 | 6‑12 | ≤ 6 |
|-----------------------|------|------|-----|
| **Type** | Titulaire | Titulaire | Suppléant |
| **Code** | 1 | 1 | 2 |

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
decisionTable;
    title Type de mandat selon la durée;
    condition Durée > 12;
    condition 6 <= Durée <= 12;
    condition Durée <= 6;
    action Type = "Titulaire"
    action Type = "Titulaire"
    action Type = "Suppléant"
```

#### Table de décision – Nom de charge affiché  

| Charge (code) | Affichage selon le contexte |
|---------------|----------------------------|
| `Affaires étrangères` | `Ministre chargé des affaires étrangères` |
| `Agriculture` | `Ministre chargé de l’agriculture` |
| `Budget` | `Ministre chargé du budget` |

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
decisionTable;
    title Nom de la charge affiché;
    condition Charge = "Affaires étrangères"
    condition Charge = "Agriculture"
    condition Charge = "Budget"
    action Libellé = "Ministre chargé des affaires étrangères"
    action Libellé = "Ministre chargé de l’agriculture"
    action Libellé = "Ministre chargé du budget"
```

### 2.4 Scénarios d’utilisation (extraits)  

| Scénario | Étapes principales |
|----------|-------------------|
| **S‑01 Authentification** | 1️⃣ L’utilisateur saisit son identifiant Cerbère.<br>2️⃣ `SecurityFilter` valide le token.<br>3️⃣ Si ok → création de `BaseAdminUserSession`.<br>4️⃣ Redirection vers la page d’accueil. |
| **S‑02 Création d’un mandat** | 1️⃣ L’opérateur ouvre le formulaire `UpsertMandat`.<br>2️⃣ Sélection du type (Titulaire/Suppléant).<br>3️⃣ Saisie des dates, du mode de nomination.<br>4️⃣ Validation → appel au service `MandatServices` → persistance dans `MANDAT`.<br>5️⃣ Le scheduler planifie une alerte 30 jours avant la fin. |
| **S‑03 Import JORF (automatisé)** | 1️⃣ Le job `RecupererJORFActivityEngine` déclenche `ArticleAnalyser`.<br>2️⃣ Extraction des articles → recherche de `College` et `Administrateur` via les steps.<br>3️⃣ Mise à jour/insertion des entités manquantes.<br>4️⃣ Notification éventuelle à l’opérateur. |
| **S‑04 Recherche globale** | 1️⃣ L’utilisateur saisit un texte libre.<br>2️⃣ `AjaxAction` interroge `ArticleSearchLoader`.<br>3️⃣ Résultats affichés sous forme de tableau (DisplayTag). |

> **Navigation** :  
> - Retour à la [section 2 – Architecture fonctionnelle](#2-architecture-fonctionnelle)  
> - Retour au [sommaire](#📑-table-des-matières)

---

## 3️⃣ **Architecture technique** <a id="3-architecture-technique"></a>

### 3.1 Vue d’ensemble (Composants)  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#006400', 'secondaryColor': '#e6ffe6'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
graph TD
    subgraph Client;
    UI[UI Web (HTML/JS/CSS)]
    end
    subgraph "Web‑Tier (Tomcat 9)"
    C1[Struts2 Controllers]
    C2[Vertigo/Vega Filters]
    C3[SecurityFilter (Cerbère)]
    end
    subgraph "Service‑Tier (Java)"
    S1[Business Services]
    S2[Domain Model (DTO/Entity)]
    S3[DAO (JPA / Hibernate)]
    S4[Job Scheduler (Quartz)]
    S5[ArticleAnalyser (JO‑Import)]
    end
    subgraph "Data‑Tier"
    DB[(Oracle / PostgreSQL – schema *integration*)]
    end
    UI --> C1;
    C1 --> C3;
    C1 --> S1;
    C2 --> C3;
    S1 --> S2;
    S2 --> S3;
    S3 --> DB;
    S4 --> S1;
    S5 --> S1;
    S5 --> S3
```

#### 3.1.1 Description des blocs  

| Bloc | Technologie | Responsabilité |
|------|--------------|----------------|
| **Client** | HTML5, CSS3, JavaScript (jQuery, Bootstrap) | Interface utilisateur, validation côté client |
| **Web‑Tier** | Apache Tomcat 9, Struts 2, Vertigo Vega, SecurityFilter | Routage, contrôleurs MVC, filtres de sécurité, gestion des sessions |
| **Service‑Tier** | Java 8, Maven, Spring‑Boot (boot components), JPA (Hibernate) | Logique métier, orchestration, planification (Quartz), import JORF |
| **Data‑Tier** | PostgreSQL 9.6 / Oracle 12c (pré‑prod), schéma *integration* | Persistance des entités (ADMINISTRATEUR, MANDAT, ETABLISSEMENT, etc.) |
| **Job Scheduler** | Quartz intégré à Spring‑Boot | Exécution périodique des tâches (import JORF, alertes) |
| **Containerisation** | Docker (en cours) – images basées sur *tomcat:9‑jdk8* | Déploiement reproductible, CI/CD (Gitlab CI) |

### 3.2 Diagramme de séquence – Authentification  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
sequencediagram;
    participant U as Utilisateur;
    participant F as SecurityFilter;
    participant S as BaseAdminUserSession;
    participant DB as DB (users)

    U->>F: Envoi du token Cerbère (Cookie/Authorization)
    F->>DB: Vérification du token (table ROLES)
    alt Token valide;
    F->>S: Création de la session;
    S-->>U: Redirection vers /accueil;
    else Token invalide;
    F-->>U: 401 Unauthorized;
    end
```

### 3.3 Diagramme de séquence – Création d’un mandat  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
sequencediagram;
    participant O as Opérateur;
    participant C as UpsertMandatAction (Struts)
    participant S as MandatServices;
    participant D as MandatDAO;
    participant DB as DB;
    O->>C: POST /mandat/upsert (formulaire)
    C->>S: upsertMandat(dto)
    S->>D: saveOrUpdate(mandat)
    D->>DB: INSERT/UPDATE MANDAT;
    DB-->>D: OK;
    D-->>S: Mandat persistant;
    S->>C: Retour succès;
    C->>O: Message de confirmation;
    Note right of S: Scheduler crée alerte 30j avant fin
```

### 3.4 Diagramme de classes (schéma simplifié)  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
classDiagram
    class Administrateur {
    +Long id;
    +String nom;
    +String prenom;
    +String civilite;

    class Mandat {
    +Long id;
    +Date debut;
    +Date fin;
    +String type (Titulaire/Suppléant)
    +String modeNomination;

    class Etablissement {
    +Long id;
    +String siren;
    +String libelle;
    +String sigle;

    class College {
    +Long id;
    +String identifiant;

    class Charge {
    +Long id;
    +String libelle;

    class Ministere {
    +Long id;
    +String sigle;
    +String nom;

    Administrateur "1" <-- "0..*" Mandat : possède;
    Etablissement "1" <-- "0..*" Mandat : concerne;
    Etablissement "1" <-- "0..*" College : regroupe;
    Charge "1" <-- "0..*" Ministere : associe;
    Mandat "1" --> "1" ModeNomination : utilise;
    Mandat "1" --> "1" TypeMandat : type
```

### 3.5 Déploiement (Vue physique)  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
graph LR
    subgraph "Data‑Center – Paris La Défense"
    DBP[(PostgreSQL – prep37)]
    end
    subgraph "Serveur Prod"
    TOMCAT[Tomcat 9 + admin_ep.war]
    DOCKER[Docker (future)]
    end
    subgraph "CI/CD"
    GIT[Gitlab Repository]
    CI[Gitlab‑CI Runner]
    end
    GIT --> CI --> DOCKER --> TOMCAT;
    TOMCAT --> DBP
```

> **Environnements**  
> - **Production** – `https://adminep.e2.rie.gouv.fr/` (Tomcat 9, PostgreSQL 9.6)  
> - **Pré‑production** – `https://adminep.preprod.e2.rie.gouv.fr/` (identique)  
> - **Recette** – `https://adminep-recette.e2.rie.gouv.fr/` (IaaS ECO4)  

---

## 4️⃣ **Analyse de la sécurité** <a id="4-analyse-de-la-sécurité"></a>

| Aspect | Mesure |
|--------|--------|
| **Authentification** | SSO Cerbère (token JWT) → `SecurityFilter` + `BaseAdminUserSession` |
| **Autorisation** | `RoleApplicatifEnum` (ADMIN, GESTIONNAIRE, CONSULTATION) – contrôles dans `RightsHelper` |
| **Chiffrement** | HTTPS obligatoire (certificat interne) – communication serveur ↔ client |
| **Sécurité des données** | Accès en lecture/écriture limité par rôle. Masquage du champ `password` dans la base. |
| **Journalisation** | `log4j2.xml` – traces d’accès, erreurs, alertes d’échéance. |
| **Protection contre les injections** | Utilisation de JPA (paramétrisation) – aucune concaténation SQL brute. |
| **Gestion des secrets** | Mot de passe DB stocké dans `adminep.xml` (crypté) – recommandé de migrer vers Vault. |
| **Hardening du serveur** | Tomcat 9.0.8 avec *Security Manager* activé, désactivation des méthodes HTTP non nécessaires. |
| **Tests de vulnérabilité** | Analyse OWASP ZAP (exécution périodique) – aucune faille critique détectée à ce jour. |

> **Lien** : Retour au [sommaire](#📑-table-des-matières)

---

## 5️⃣ **Dette technique** <a id="5-dette-technique"></a>

| Élément | Description du problème | Impact | Proposition de résolution |
|---------|--------------------------|--------|---------------------------|
| **Mot de passe DB en clair** | `adminep.xml` contient le password en texte clair. | Risque de compromission. | Migrer vers un coffre à secrets (HashiCorp Vault, AWS Secrets Manager). |
| **Hard‑coded IDs** (`TYPE_MANDAT` = 1/2, `TYPE_INSTANCE` = 1/2) | Utilisation de constantes numériques dans le code Java. | Difficulté de maintenance, erreurs lors d’ajout de nouveaux types. | Introduire des énumérations référencées via le catalogue (`CodeEnum`). |
| **SQL scripts spécifiques à Oracle** | Certaines requêtes utilisent la syntaxe Oracle (`OIDS = FALSE`). | Portabilité limitée vers PostgreSQL. | Refactoriser les scripts en SQL standard ou utiliser Liquibase. |
| **Séquence manuelle (`nextval('sq_charge')`)** | Gestion manuelle des séquences dans les scripts d’insertion. | Risque de collisions si les séquences sont ré‑initialisées. | Centraliser la génération d’IDs via JPA `@GeneratedValue(strategy = GenerationType.SEQUENCE)`. |
| **Couplage Struts2 / Vertigo** | Contrôleurs Struts2 directement appelent les services Vertigo. | Difficile d’évoluer vers une architecture REST. | Introduire une couche façade (Spring MVC) et exposer des API REST. |
| **Absence de tests unitaires sur les jobs JORF** | Les classes `ArticleAnalyser` et ses steps ne sont pas couverts. | Bugs silencieux lors de l’import. | Ajouter des tests JUnit + Mockito, couvrir chaque step. |
| **Manque de monitoring** | Aucun export de métriques (Prometheus, Grafana). | Visibilité limitée sur la santé de l’application. | Intégrer Micrometer + exporter vers Prometheus. |

> **Lien** : Retour au [sommaire](#📑-table-des-matières)

---

## 6️⃣ **Annexes** <a id="6-annexes"></a>

### 6.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **Mandat** | Période pendant laquelle un administrateur exerce ses fonctions au sein d’un conseil d’administration. |
| **Titulaire / Suppléant** | Types de mandat (R‑02). |
| **Charge** | Fonction ministérielle (ex. *Affaires étrangères*). |
| **Cerbère** | Système d’authentification unique du ministère. |
| **JORF** | Journal Officiel de la République Française – source d’import des nominations. |
| **Scheduler** | Mécanisme Quartz qui déclenche les jobs périodiques. |

### 6.2 Références documentaires  

| Référence | Description |
|-----------|-------------|
| **Fiche produit** | `admin_ep.wiki.md` – description fonctionnelle, acteurs, version. |
| **Documentation technique** | `adminep‑database/pom.xml`, `adminep‑web/src/main/resources/struts.xml`, `log4j2.xml`. |
| **Modèle de données** | Scripts SQL d’init et de population (`1_createSequenceAndTablesIntegration.sql`, `2_populateTablesIntegration.sql`). |
| **Processus JORF** | `ArticleAnalyser` et ses étapes (voir source Java). |
| **Norme ISO/IEC/IEEE 29148** | Structure du présent document (parties fonctionnelle & technique). |

### 6.3 Index des ancres internes  

| Ancre | Section |
|-------|---------|
| `#11-portée-domaine-et-périmètre` | Portée, domaine & périmètre |
| `#2-architecture-fonctionnelle` | Architecture fonctionnelle |
| `#3-architecture-technique` | Architecture technique |
| `#4-analyse-de-la-sécurité` | Analyse de la sécurité |
| `#5-dette-technique` | Dette technique |
| `#6-annexes` | Annexes |

--- 

*Fin du document – toutes les références sont internes, aucun fichier externe n’est requis.*