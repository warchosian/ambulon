# 📄 Cahier des Charges Fonctionnel (CCF) – **Projet afinope**  
**Conforme à ISO/IEC/IEEE 29148 : 2018**  

> **Version** : 1.0 – 2024‑04‑28  
> **Auteur** : Équipe d’ingénierie exigences – afinope  
> **Document référencé** : Vision & Business‑Case (non fourni – voir annexes)  

---

## 1️⃣ Identification et Contexte du Document  

| Élément | Valeur |
|---|---|
| **Identifiant du CCF** | CCF‑AFINOPE‑001 |
| **Version** | 1.0 |
| **Historique** | 2024‑04‑28 : Création initiale (v1.0) |
| **Références** | - README.md (description projet)  <br> - flux.txt (définition des flux métiers) <br> - pyproject.toml (stack technique) <br> - docker‑compose.yml (déploiement) |
| **Portée** | Spécifie les exigences fonctionnelles et non‑fonctionnelles du système **afinope**, qui assure : <br>1. L’ingestion, la validation et le chargement des fichiers CSV de données financières ; <br>2. La mise à disposition d’un référentiel PostgreSQL contenant les tables de référence et d’exécution ; <br>3. L’exposition d’un graphe Dagster pour orchestrer les pipelines et fournir des tableaux de bord Superset. |
| **Objectifs** | - Garantir la **qualité** et la **traçabilité** des données financières de l’État. <br> - Permettre une **exploitation automatisée** (ETL) des flux d’entrée. <br> - Assurer la **conformité** aux exigences de sécurité, de performance et de maintenabilité. |

---

## 2️⃣ Description de l’Écosystème (System/Software Context)

```mermaid
graph LR
    subgraph "Utilisateurs / Acteurs"
        OP[Opérateur (chargement CSV)]
        ADM[Administrateur (déploiement & configuration)]
        DB[Base de données PostgreSQL]
        SUP[Superset (visualisation)]
        DAG[Dagster Web‑Server]
    end
    subgraph "Système afinope"
        APP[Application Python (afinope)]
        PIPE[Pipeline Dagster]
        CFG[Config JSON]
        CONTAINER[Docker]
    end
    OP -->|dépose CSV| APP;
    ADM -->|déploie / configure| CONTAINER;
    APP -->|lit configuration| CFG;
    APP -->|orchestration| PIPE;
    PIPE -->|écrit / lit| DB;
    PIPE -->|publie métriques| DAG;
    DAG -->|expose UI| OP;
    DB -->|source de données| SUP
```

* **Frontières du système** : le périmètre fonctionnel s’étend du répertoire d’entrée (`flux.entree`) jusqu’à la persistance dans PostgreSQL et la mise à disposition des vues Superset.  
* **Interfaces externes** :  
  * **Fichiers CSV** (entrée, sortie, erreur) – système de fichiers partagé.  
  * **PostgreSQL** (port 5432) – stockage persistant.  
  * **Dagster Web‑Server** (port 4400) – orchestration et monitoring.  
  * **Superset** (via Docker) – visualisation des vues SQL.  
* **Environnement opérationnel** : conteneurs Docker sur Linux, Python 3.11, PostgreSQL 13+, réseau interne Docker.

---

## 3️⃣ Exigences Fonctionnelles (Functional Requirements)

> **Notation** : `[ID] Titre` – chaque exigence suit le modèle ISO 29148.  
> **Priorité** : **M** = Mandatory, **D** = Desirable, **O** = Optional.

| ID | Titre | Description | Rationale | Source | Priorité | Vérif. | Dépendances |
|---|---|---|---|---|---|---|---|
| **EXG‑FCT‑001** | Ingestion des fichiers CSV | Le système doit détecter automatiquement tout fichier *.csv* présent dans le répertoire `flux.entree` et le mettre en file d’attente pour traitement. | Permet la collecte automatisée des données financières. | `flux.txt`, `GestionnaireFichiersCSV` | M | Test d’intégration (détection + queue) | – |
| **EXG‑FCT‑002** | Validation syntaxique du CSV | Chaque fichier CSV doit être validé (colonnes attendues, types, contraintes de nullité) avant tout chargement. | Garantit la **qualité** des données. | `known_issue.txt`, `helper.py` | M | Unit‑test + jeu de données invalide | EXG‑FCT‑001 |
| **EXG‑FCT‑003** | Transformation des valeurs | Les fonctions `na_to_empty`, `int_to_bool`, `str_to_float` doivent être appliquées à chaque champ conformément aux règles métier. | Normalise les données pour le stockage. | `helper.py` | M | Test de transformation (exemple) | EXG‑FCT‑002 |
| **EXG‑FCT‑004** | Stockage dans PostgreSQL | Le DataFrame validé doit être inséré dans la table cible (ex. `NOMENC`, `BAL`, `ABE`…) via SQLAlchemy. | Persistance durable et requêtable. | `GestionnaireBaseDonnees`, `AfinopeBase` | M | Vérification du nombre de lignes insérées | EXG‑FCT‑003 |
| **EXG‑FCT‑005** | Gestion des erreurs | En cas d’erreur (validation ou DB), le fichier doit être déplacé vers `flux.erreur` avec un log détaillé. | Traçabilité et reprise possible. | `GestionnaireFichiersCSV` | M | Vérification du déplacement + log | EXG‑FCT‑002 |
| **EXG‑FCT‑006** | Publication de vues agrégées | Le pipeline doit créer ou rafraîchir les vues `tdb_view`, `tdb_abe_view`, `tdb_abp_view` (définies dans `sql/06_superset/...`). | Supporte les tableaux de bord Superset. | `sql/06_superset` | D | Inspection du schéma DB après exécution | EXG‑FCT‑004 |
| **EXG‑FCT‑007** | Orchestration Dagster | Le graphe Dagster (`graphe_alimentation.py`) doit exposer un pipeline complet : *Lister → Valider → Transformer → Charger → Archiver*. | Centralise la logique ETL et fournit monitoring. | `resources.py`, `Dockerfile.app` | M | Exécution du pipeline via UI Dagster | EXG‑FCT‑001‑006 |
| **EXG‑FCT‑008** | Configuration externalisée | Tous les paramètres (répertoires `entree`, `sortie`, `erreur`, connexion DB) doivent être lus depuis `config.json`. | Facilite le déploiement multi‑environnements. | `app/flux.py` | M | Test de lecture du fichier JSON | – |
| **EXG‑FCT‑009** | Export CSV de sortie | Après chargement, le fichier source doit être copié vers `flux.sortie` (archive). | Historisation des sources. | `GestionnaireFichiersCSV` | D | Vérification de la présence du fichier archivé | EXG‑FCT‑004 |
| **EXG‑FCT‑010** | Gestion des dépendances de tables | Le pipeline doit respecter les contraintes d’intégrité référentielle (ex. `codeOrganisme` présent dans `ORGANISME`). | Évite les violations de clés étrangères. | `sql/00_referentiel` | M | Tests d’insertion avec violations contrôlées | EXG‑FCT‑004 |

### 3.1 Classification des exigences fonctionnelles  

| Catégorie | Exigences associées |
|---|---|
| **Capacités** | EXG‑FCT‑001, EXG‑FCT‑008, EXG‑FCT‑007 |
| **Fonctions** | EXG‑FCT‑002, EXG‑FCT‑003, EXG‑FCT‑004, EXG‑FCT‑005, EXG‑FCT‑009 |
| **Traitements** | EXG‑FCT‑006, EXG‑FCT‑010 |

---

## 4️⃣ Exigences Non‑Fonctionnelles (Non‑Functional Requirements)

| ID | Catégorie | Description | Rationale | Source | Priorité | Vérif. |
|---|---|---|---|---|---|---|
| **EXG‑NFR‑001** | Performance – Temps de réponse | Le pipeline doit ingérer et charger un fichier CSV de ≤ 10 Mo en ≤ 30 s (hors temps réseau DB). | Garantit la réactivité des traitements batch. | `flux.txt` | M | Benchmark automatisé |
| **EXG‑NFR‑002** | Performance – Débit | Le système doit pouvoir traiter **au moins 20 fichiers simultanément** (parallelisme via Dagster). | Supporte les pics d’arrivée de données. | Architecture Dagster | D | Test de charge |
| **EXG‑NFR‑003** | Ressources – Mémoire | Le conteneur Python ne doit pas dépasser **800 MiB** de RAM pendant le traitement. | Limite l’impact sur l’hôte Docker. | Dockerfile / Poetry | M | Monitoring Docker (`docker stats`) |
| **EXG‑NFR‑004** | Interface externe – UI Dagster | L’interface web Dagster doit être disponible via `http://<host>:4400/afinope` et compatible Chrome ≥ 90. | Accessibilité des opérateurs. | Dockerfile, `docker‑compose.yml` | M | Test d’accès HTTP |
| **EXG‑NFR‑005** | Interface externe – API DB | La connexion PostgreSQL doit être sécurisée via **TLS** et authentifiée par mot de passe stocké dans `.env`. | Conformité sécurité. | `docker‑compose.yml` | M | Scan de connexion (SSL) |
| **EXG‑NFR‑006** | Qualité – Maintenabilité | Le code doit respecter **PEP 8**, être couvert à **≥ 80 %** par des tests unitaires (pytest). | Facilite l’évolution. | `pyproject.toml` (dev‑deps) | M | Rapport de couverture |
| **EXG‑NFR‑007** | Qualité – Testabilité | Chaque fonction de `helper.py` doit être testable de façon isolée (no external I/O). | Permet CI/CD fiable. | `pyproject.toml` | M | Unit‑tests |
| **EXG‑NFR‑008** | Qualité – Fiabilité | Le taux d’échec du pipeline (fichiers rejetés) doit rester **< 2 %** sur 30 jours d’opération. | Garantit la disponibilité des données. | KPI métier | D | Monitoring journaux |
| **EXG‑NFR‑009** | Conception – Langage | Le projet doit être développé exclusivement en **Python 3.11**. | Cohérence de l’environnement. | `pyproject.toml` | M | Version Python au runtime |
| **EXG‑NFR‑010** | Conception – Standards | Utilisation obligatoire de **SQLAlchemy 2.x**, **Dagster 1.8**, **Poetry** pour gestion des dépendances. | Uniformité technologique. | `pyproject.toml` | M | Vérification de versions |
| **EXG‑NFR‑011** | Sécurité – Confidentialité | Les fichiers CSV contenant des données financières doivent être stockés avec **permissions 0600** (owner‑only). | Protection des données sensibles. | `GestionnaireFichiersCSV` | M | Test de permissions |
| **EXG‑NFR‑012** | Sécurité – Intégrité | Chaque fichier CSV doit être signé (SHA‑256) et la signature stockée dans la table `hashes` (nouvelle table). | Détection de corruptions. | Extension future | O | Vérification de hash |
| **EXG‑NFR‑013** | Sécurité – Disponibilité | Le service DB doit être redondant (Docker restart policy `unless‑stopped`). | Haute disponibilité. | `docker‑compose.yml` | D | Test de redémarrage |
| **EXG‑NFR‑014** | Portabilité | Le conteneur doit fonctionner sur **Linux x86_64** et **ARM64** (multi‑arch). | Prépare le déploiement sur serveurs variés. | Dockerfile | O | Build multi‑arch |
| **EXG‑NFR‑015** | Documentation – Traçabilité | Chaque exigence doit être traçable vers les artefacts de code (fichiers source) et les tests. | Conformité ISO 29148. | Ce CCF | M | Matrice de traçabilité |

---

## 5️⃣ Modèle de Données Conceptuel  

```mermaid
classDiagram
    class ORGANISME {
        +char[10] codeOrganisme;
        +varchar[150] libelleOrganisme;
        +char[14] siret;
        +date dateJuridique;
        +date dateCreation;
        +date dateCloture;
        +date dateLiquidation;
        +date dateDocument;

    class STRUCTURE {
        +char[10] codeOrganisme;
        +char[2] codeBudget;
        +varchar[120] libelleBudget;
        +date dateCreation;
        +date dateCloture;
        +date dateDocument;

    class NOMENC {
        +int exercice;
        +char[2] typeNomenclature;
        +varchar[20] libelleNomenclature;
        +bigint numeroCompte;
        +char[1] sens;
        +varchar[200] libelleCompte;
        +date dateDocument;

    class BAL {
        +bigint codeCompte;
        +varchar[200] libelleCompte;
        +numeric debitEntree;
        +numeric debitCumul;
        +numeric debitTotal;
        +numeric creditEntree;
        +numeric creditCumul;
        +numeric creditTotal;
        +numeric soldeDebiteur;
        +numeric soldeCrediteur;
        +char[10] codeOrganisme;
        +int exercice;
        +char[2] typeNomenclature;
        +char[2] typeDocument;
        +char[2] typeBudget;
        +char[2] typeRang;
        +char[3] codeDevise;
        +date dateDocument;
        +char[1] typeSequence;

    class ABE {
        +char[2] codeLibelle;
        +char[2] impact;
        +char[10] codeRecherche;
        +numeric montant;
        +char[10] codeOrganisme;
        +int exercice;
        +char[2] typeDocument;
        +char[2] typeBudget;
        +char[2] typeRang;
        +char[3] codeDevise;
        +date dateDocument;
        +char[1] typeSequence;

    ORGANISME "1" --> "0..*" STRUCTURE : possède;
    ORGANISME "1" --> "0..*" NOMENC : référence;
    ORGANISME "1" --> "0..*" BAL : possède;
    ORGANISME "1" --> "0..*" ABE : possède
```

*Les tables référentielles (`ORGANISME`, `STRUCTURE`, `NOMENC`, …) sont créées via les scripts SQL du répertoire `sql/00_referentiel`.*  

---

## 6️⃣ Modélisation des Comportements  

### 6.1 Diagramme de cas d’utilisation  

```mermaid
useCaseDiagram;
    actor Opérateur as OP;
    actor Administrateur as ADM;
    OP --> (Déposer CSV)
    OP --> (Consulter état du pipeline)
    ADM --> (Configurer le système)
    ADM --> (Déployer / Mettre à jour les conteneurs)
    (Déposer CSV) --> \(Ingestion)
    (Ingestion) --> \(Validation)
    (Validation) --> \(Transformation)
    (Transformation) --> \(Chargement BD)
    (Chargement BD) --> \(Publication vues)
    (Publication vues) --> \(Visualiser tableau de bord)
```

### 6.2 Diagramme d’activité (pipeline d’ingestion)

```mermaid
statediagram-v2;
    [*] --> DetecterCSV;
    DetecterCSV --> ValiderCSV;
    ValiderCSV -->|OK| Transformer;
    ValiderCSV -->|Erreur| GérerErreur;
    Transformer --> ChargerBD;
    ChargerBD --> PublierVues;
    PublierVues --> Archiver;
    GérerErreur --> ArchiverErreur;
    Archiver --> [*]
    ArchiverErreur --> [*]
```

### 6.3 Diagramme d’états (Fichier CSV)

```mermaid
statediagram;
    [*] --> Nouveau;
    Nouveau --> Validé : validation OK;
    Nouveau --> Rejeté : validation KO;
    Validé --> Chargé : insertion réussie;
    Chargé --> Archivé : déplacement vers sortie;
    Rejeté --> ErreurArchivé : déplacement vers erreur
```

### 6.4 Diagramme de séquence (traitement d’un fichier)

```mermaid
sequencediagram;
    participant OP as Opérateur;
    participant APP as afinope (Python)
    participant DAG as Dagster;
    participant DB as PostgreSQL;
    participant FS as Filesystem;
    OP->>FS: Dépose file.csv dans flux.entree;
    APP->>APP: DetecterCSV()
    APP->>APP: ValiderCSV(file.csv)
    alt Validation OK;
        APP->>APP: Transformer(file.csv)
        APP->>DB: INSERT INTO target_table;
        DB-->>APP: OK / rows inserted;
        APP->>FS: Move file.csv -> flux.sortie;
    else Validation KO;
        APP->>FS: Move file.csv -> flux.erreur;
        APP->>APP: Log error;
    end
    APP->>DAG: Notify status
```

---

## 7️⃣ Attributs d’Exigences (Requirements Attributes)

> Exemple détaillé pour **EXG‑FCT‑001** (les autres suivent le même modèle).  

| Attribut | Valeur |
|---|---|
| **Identifiant** | EXG‑FCT‑001 |
| **Description** | Le système doit détecter automatiquement tout fichier *.csv* présent dans le répertoire `flux.entree` et le mettre en file d’attente pour traitement. |
| **Rationale** | Permet la collecte automatisée des données financières. |
| **Source** | `flux.txt`, classe `GestionnaireFichiersCSV` |
| **Priority** | Mandatory |
| **Status** | Approved (Baseline) |
| **Verification** | Test d’intégration : dépôt de 5 fichiers CSV → le pipeline les détecte et les inscrit dans la file d’attente (log “queued”). |
| **Risk** | Medium (détection dépend du montage du volume partagé) |
| **Stability** | Stable |
| **Dependencies** | – |
| **Owner** | équipe développement |

*(Un tableau similaire est fourni en annexe A pour chaque exigence.)*  

---

## 8️⃣ Traçabilité des Exigences  

### 8.1 Matrice de traçabilité (Exigences ↔ Artefacts)

| Exigence | Source code / artefact | Test(s) | Business Objective |
|---|---|---|---|
| EXG‑FCT‑001 | `app/gestionnaire_fichier_csv.py` (lister_les_fichiers) | TC‑FCT‑001 (détection) | **OBJ‑01** : Collecter les flux entrants |
| EXG‑FCT‑002 | `app/helper.py` (na_to_empty, int_to_bool, str_to_float) | TC‑FCT‑002 (validation de colonnes) | **OBJ‑02** : Garantir la qualité des données |
| EXG‑FCT‑003 | `app/helper.py` (fonctions) | TC‑FCT‑003 (transformation) | **OBJ‑02** |
| EXG‑FCT‑004 | `app/gestionnaire_base_donnees.py` (stocker_dataframe) | TC‑FCT‑004 (insertion DB) | **OBJ‑03** : Persister les données |
| EXG‑FCT‑005 | `app/gestionnaire_fichier_csv.py` (deplacer_fichier) | TC‑FCT‑005 (déplacement erreur) | **OBJ‑04** : Traçabilité des anomalies |
| EXG‑FCT‑006 | `sql/06_superset/01_tdb/tdb_view.sql` et vues associées | TC‑NFR‑006 (inspection vues) | **OBJ‑05** : Alimenter les tableaux de bord |
| EXG‑FCT‑007 | `app/graphe_alimentation.py` (Dagster pipeline) | TC‑FCT‑007 (exécution Dagster) | **OBJ‑01**, **OBJ‑05** |
| EXG‑FCT‑008 | `app/flux.py` (lecture config) | TC‑FCT‑008 (lecture JSON) | **OBJ‑01** |
| EXG‑FCT‑009 | `app/gestionnaire_fichier_csv.py` (deplacer_fichier) | TC‑FCT‑009 (archivage) | **OBJ‑04** |
| EXG‑FCT‑010 | `sql/00_referentiel/*` (contraintes FK) | TC‑FCT‑010 (intégrité) | **OBJ‑03** |
| EXG‑NFR‑001 | Benchmarks (pytest‑bench) | TC‑NFR‑001 (temps) | **OBJ‑06** (Performance) |
| EXG‑NFR‑004 | `docker‑compose.yml` + `Dockerfile.app` | TC‑NFR‑004 (accessibilité UI) | **OBJ‑07** (Usabilité) |
| … | … | … | … |

### 8.2 Mapping Objectifs Métier → Exigences  

| Objectif Métier (extrait du Business‑Case) | Exigences associées |
|---|---|
| **OBJ‑01** : Collecter les flux entrants de façon automatisée | EXG‑FCT‑001, EXG‑FCT‑008, EXG‑FCT‑007 |
| **OBJ‑02** : Garantir la qualité et la conformité des données | EXG‑FCT‑002, EXG‑FCT‑003, EXG‑NFR‑001, EXG‑NFR‑008 |
| **OBJ‑03** : Persister les données dans un référentiel fiable | EXG‑FCT‑004, EXG‑FCT‑010, EXG‑NFR‑005 |
| **OBJ‑04** : Assurer la traçabilité des erreurs et l’archivage | EXG‑FCT‑005, EXG‑FCT‑009, EXG‑NFR‑011 |
| **OBJ‑05** : Mettre à disposition des tableaux de bord décisionnels | EXG‑FCT‑006, EXG‑FCT‑007, EXG‑NFR‑004 |
| **OBJ‑06** : Respecter les exigences de performance | EXG‑NFR‑001, EXG‑NFR‑002, EXG‑NFR‑003 |
| **OBJ‑07** : Offrir une interface simple aux opérateurs | EXG‑NFR‑004, EXG‑NFR‑007 |
| **OBJ‑08** : Sécuriser les données financières | EXG‑NFR‑011, EXG‑NFR‑012, EXG‑NFR‑013 |

---

## 9️⃣ Gestion des Exigences  

| Processus | Description | Responsable | Outil recommandé |
|---|---|---|---|
| **Identification & Capture** | Collecte via ateliers, revue du Business‑Case, analyse du code source. | PO / Analyste | **Jira / Azure Boards** (issues type “Requirement”) |
| **Analyse & Priorisation** | Utilisation de la matrice **MoSCoW** + analyse de risques. | PO / Architecte | **Jira** (champ “Priority”) |
| **Documentation** | Rédaction dans ce CCF (Markdown) et synchronisation dans le repo (`docs/CCF.md`). | Analyste | **Git** (pull‑request pour validation) |
| **Traçabilité** | Matrice (section 8) maintenue automatiquement via **traceability‑plugin** ou script Python. | QA | **Jama Connect**, **Polarion** ou **ReqIF** export |
| **Gestion du changement** | Toute modification → *Change Request* → impact analysis → mise à jour CCF → approbation. | Change Manager | **Jira Service Management** |
| **Vérification & Validation** | Revues d’exigences, tests d’acceptation, audits qualité. | QA / Test Lead | **TestRail**, **pytest**, **Cucumber** (BDD) |
| **Gestion des conflits** | Priorisation par business value + risque, médiation par Architecture Review Board. | ARB | N/A |
| **Outils de suivi** | - **Dagster** (pipeline monitoring) <br> - **GitLab CI** (pipeline CI/CD) <br> - **Prometheus/Grafana** (KPIs) | DevOps | – |

---

## 🔟 Validation et Vérification  

| Niveau | Activité | Méthode | Critères d’acceptation |
|---|---|---|---|
| **Revue** | Inspection du CCF | Walk‑through avec parties prenantes | 100 % des exigences signées |
| **Unité** | Tests unitaires (pytest) | Coverage ≥ 80 % | Tous les modules (`helper`, `flux`, `gestionnaire_*`) passent |
| **Intégration** | Pipeline Dagster complet sur environnement de test | Exécution du DAG « Ingestion » | Tous les fichiers CSV d’un lot (≥ 5) sont traités sans erreur |
| **Performance** | Benchmark (pytest‑bench) | Temps moyen ≤ 30 s / fichier 10 Mo | 95 % des runs respectent la limite |
| **Sécurité** | Analyse statique (Bandit, SonarQube) | Aucun “high” issue | Passes audit |
| **Acceptation** | Tests d’acceptation (Cucumber/BDD) | Scénario “Given … When … Then …” – ex : *Given* un CSV valide, *When* le pipeline démarre, *Then* la table cible contient les lignes attendues. | Tous les scénarios passent |
| **Production** | Monitoring continu (Prometheus) | KPI : taux d’erreur < 2 % | Alerte déclenchée si dépassement |

---

## 📎 Annexes  

### A – Table détaillée des exigences (extraits)  

| ID | Titre | Owner | Test ID |
|---|---|---|---|
| EXG‑FCT‑001 | Ingestion des fichiers CSV | Dev Team | TC‑FCT‑001 |
| EXG‑FCT‑002 | Validation syntaxique du CSV | QA | TC‑FCT‑002 |
| EXG‑FCT‑003 | Transformation des valeurs | Dev Team | TC‑FCT‑003 |
| EXG‑FCT‑004 | Stockage dans PostgreSQL | DB‑Admin | TC‑FCT‑004 |
| EXG‑FCT‑005 | Gestion des erreurs | Dev Team | TC‑FCT‑005 |
| EXG‑FCT‑006 | Publication de vues agrégées | BI‑Team | TC‑NFR‑006 |
| EXG‑FCT‑007 | Orchestration Dagster | DevOps | TC‑FCT‑007 |
| EXG‑FCT‑008 | Configuration externalisée | Dev Team | TC‑FCT‑008 |
| EXG‑FCT‑009 | Export CSV de sortie | Ops | TC‑FCT‑009 |
| EXG‑FCT‑010 | Gestion des dépendances de tables | DB‑Admin | TC‑FCT‑010 |
| EXG‑NFR‑001 | Temps de réponse du pipeline | QA | TC‑NFR‑001 |
| EXG‑NFR‑004 | UI Dagster disponible | Ops | TC‑NFR‑004 |
| … | … | … | … |

*(la liste complète (≈ 30 exigences) est disponible dans le dépôt sous `docs/requirements.xlsx`).*  

### B – Glossaire  

| Terme | Définition |
|---|---|
| **Flux** | Ensemble de répertoires (`entree`, `sortie`, `erreur`) définis dans `config.json`. |
| **Dagster** | Framework d’orchestration de pipelines de données utilisé par afinope. |
| **Superset** | Plate‑forme de visualisation de données qui consomme les vues SQL du projet. |
| **Dag** | Acronyme de *Directed Acyclic Graph* – représentation d’un pipeline Dagster. |
| **Hash SHA‑256** | Somme de contrôle cryptographique pour garantir l’intégrité d’un fichier. |

### C – Bibliographie & Références  

1. ISO/IEC/IEEE 29148 : 2018 – *Systems and software engineering – Life cycle processes – Requirements engineering*.  
2. ISO/IEC/IEEE 15288 : 2015 – *System life cycle processes*.  
3. ISO/IEC/IEEE 12207 : 2017 – *Software life cycle processes*.  
4. Documentation officielle Dagster 1.8 (https://docs.dagster.io).  
5. PostgreSQL 13 Documentation (https://www.postgresql.org/docs/13/).  

---

## ✅ Conclusion  

Le présent Cahier des Charges Fonctionnel formalise, de façon **traçable**, **complète** et **conforme** à la norme ISO 29148, l’ensemble des exigences du projet **afinope**. Il constitue la base contractuelle entre les parties prenantes (MOA, MOE, exploitation) et guidera la conception, le développement, les tests et la mise en production du système d’ingestion et de pilotage des données financières de l’État.  

> **Prochaine étape** : Validation formelle du CCF par le comité de pilotage (signature) puis découpage en *backlog* de travaux (user stories) dans l’outil de suivi choisi.  