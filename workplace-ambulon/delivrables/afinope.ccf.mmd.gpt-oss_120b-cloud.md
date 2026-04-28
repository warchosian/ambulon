# 📄 Cahier des Charges Fonctionnel (CCF) – **Projet : afinope**  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | **afinope** – Application financière des opérateurs de l’État. |
| **Objectif principal** | Centraliser, transformer et rendre exploitable l’ensemble des flux financiers (référentiels, exécutoires, d’exécution) provenant de la DGFIP afin de produire des tableaux de bord (Superset) et des exports compatibles avec les exigences de pilotage budgétaire. |
| **Environnement** | - **Docker** (services `db` PostgreSQL + `app` Dagster). <br>- **Python 3.11** (pandas, SQLAlchemy, Dagster). <br>- **Superset** (visualisation). |
| **Périmètre fonctionnel** | **Inclus** : <br>• Lecture de fichiers CSV entrants (référentiels, exécutoires, exécution). <br>• Validation et nettoyage des données. <br>• Chargement dans la base de données PostgreSQL. <br>• Orchestration des pipelines (Dagster). <br>• Mise à disposition de vues SQL exploitées par Superset. <br>**Exclus** : <br>• Gestion des droits d’accès utilisateurs (hors scope du moteur de traitement). <br>• Interface graphique de saisie (seulement les API/Dagster). |
| **Enjeux stratégiques** | - **Valeur** : Fiabiliser les données financières pour un pilotage fiable des budgets. <br>- **Conformité** : Respecter les normes RGPD (traçabilité des traitements) et les exigences comptables de l’État. <br>- **Scalabilité** : Architecture containerisée permettant le déploiement en environnement de production ou de pré‑production. |

---  

## 2️⃣ Expression fonctionnelle du besoin *(NF EN 16271)*  

> **Principe** : chaque fonction de service décrit **le quoi** (besoin) sans préciser le comment.  

| # | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Niveau d’importance / Pondération* | Contraintes |
|---|---|---|---|---|---|
| **FS‑01** | **Collecte des flux entrants** | Récupérer les fichiers CSV déposés dans le répertoire `input/` et les classer par type (référentiel, exécutoires, exécution). | - Temps de détection ≤ 5 s après dépôt. <br>- Aucun fichier CSV ignoré. | 10 % | - Le répertoire d’entrée est configurable via le fichier `config.json`. |
| **FS‑02** | **Validation de la structure des fichiers** | Vérifier que chaque CSV possède les colonnes attendues (voir schémas SQL) et que les types de données sont conformes. | - Taux de conformité ≥ 99 % des lignes. <br>- Rapport d’erreurs généré (< 1 Mo). | 15 % | - Les règles de validation sont définies dans `app/helper.py`. |
| **FS‑03** | **Nettoyage & normalisation** | Appliquer les transformations : conversion des valeurs « NA », normalisation des décimaux, transformation des booléens, etc. | - Aucun champ `NULL` non intentionnel dans la table cible. <br>- Conversion correcte des séparateurs décimaux. | 12 % | - Utilise les fonctions `na_to_empty`, `int_to_bool`, `str_to_float`. |
| **FS‑04** | **Enrichissement des données** | Ajouter les métadonnées de traitement (date de chargement, source du fichier). | - Champ `dateChargement` renseigné pour 100 % des lignes. | 8 % | - Date au format ISO 8601. |
| **FS‑05** | **Stockage dans PostgreSQL** | Insérer les data‑frames validées dans les tables correspondantes (`ORGANISME`, `DESP`, `ABE`, …). | - Nombre d’enregistrements insérés = nombre de lignes valides. <br>- Temps d’insertion ≤ 30 s pour 100 k lignes. | 15 % | - Utilisation de SQLAlchemy (`AfinopeBase.metadata.create_all`). |
| **FS‑06** | **Gestion des erreurs et archivage** | Déplacer les fichiers erronés vers le répertoire `error/` avec un rapport détaillé. | - 100 % des fichiers rejetés sont archivés. <br>- Rapport d’erreur disponible dans les 10 s suivant le rejet. | 7 % | - Les logs sont écrits dans `logs/csv-validation.log`. |
| **FS‑07** | **Orchestration des pipelines** | Exécuter les étapes de collecte → validation → stockage en chaîne via Dagster. | - Succès du pipeline ≥ 98 % des runs. <br>- Re‑exécution possible en cas d’échec (idempotence). | 13 % | - Définition dans `app/graphe_alimentation.py`. |
| **FS‑08** | **Exposition de vues d’analyse** | Fournir des vues SQL (`tdb_view`, `tdb_abe_view`, etc.) prêtes à être consommées par Superset. | - Disponibilité 24/7 des vues. <br>- Temps de réponse ≤ 2 s pour les requêtes de tableau de bord. | 10 % | - Les vues sont créées dans le répertoire `sql/06_superset/01_tdb/`. |
| **FS‑09** | **Traçabilité & audit** | Conserver l’historique des traitements (fichier source, date, statut). | - Audit complet disponible dans la table `audit_log`. <br>- Conservation ≥ 180 jours. | 5 % | - Respect du RGPD (anonymisation si besoin). |
| **FS‑10** | **Déploiement reproductible** | Construire les images Docker (app + db) et les lancer via `docker‑compose`. | - Build complet ≤ 5 min. <br>- Démarrage complet du stack ≤ 30 s. | 5 % | - Utilise le `Dockerfile.app` et le `docker-compose.yml`. |

\* La somme des pondérations = 100 %.  

---  

## 3️⃣ Acteurs et parties prenantes  

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **MOA (Maîtrise d’Ouvrage)** | Commanditaire fonctionnel | Garantir la conformité des données financières. | Rapports d’erreurs détaillés, visibilité sur la qualité des flux. |
| **MOE (Maîtrise d’Œuvre)** | Équipe dev / Ops | Implémenter, tester et déployer la solution. | Documentation technique, scripts d’infrastructure, logs de pipeline. |
| **Data Analyst** | Exploitation des données | Produire des tableaux de bord de suivi budgétaire. | Vues SQL stables, temps de réponse rapide, métadonnées de version. |
| **Responsable Sécurité (RSSI)** | Sécurité des traitements | Assurer la conformité RGPD & RGS. | Traçabilité, chiffrement des variables d’environnement, audit. |
| **Opérateur DGFIP** | Fournisseur de flux CSV | Transmettre les fichiers de façon fiable. | Répertoire d’entrée stable, retour d’erreur en cas de rejet. |
| **Administrateur Système** | Gestion de l’infrastructure | Assurer la disponibilité du service. | Conteneurs Docker, sauvegarde de la base, monitoring. |
| **Utilisateur final (Direction financière)** | Consommateur des rapports | Décider sur la base de données fiables. | Accès aux tableaux de bord Superset, indicateurs de performance. |

---  

## 4️⃣ Cas d’usage (Use Cases)  

### 4.1 Diagramme de cas d’utilisation (Mermaid)

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#2F80ED','edgeLabelBackground':'#fff','fontFamily':'Helvetica'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
usecaseDiagram;
    actor Opérateur DGFIP as Op;
    actor Data Analyst as DA;
    actor Administrateur Système as AS;
    actor MOA as MOA;
    rectangle "Système afinope" {
    (UC‑01 Collecter fichiers) as UC1;
    (UC‑02 Valider & nettoyer) as UC2;
    (UC‑03 Charger en BDD) as UC3;
    (UC‑04 Générer vues d’analyse) as UC4;
    (UC‑05 Produire rapports d’erreurs) as UC5;
    (UC‑06 Orchestrer pipelines) as UC6;
    (UC‑07 Déployer stack) as UC7;
    (UC‑08 Auditer traitements) as UC8;

    Op --> UC1;
    UC1 --> UC2;
    UC2 --> UC3;
    UC3 --> UC4;
    UC2 --> UC5;
    UC6 --> UC1;
    UC6 --> UC2;
    UC6 --> UC3;
    UC6 --> UC4;
    AS --> UC7;
    MOA --> UC8;
    DA --> UC4
```

### 4.2 Description détaillée des cas d’usage  

| UC | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|
| **UC‑01** Collecter fichiers | Opérateur DGFIP | 1. L’opérateur dépose un CSV dans le répertoire `input/`. <br>2. Le service `GestionnaireFichiersCSV.lister_les_fichiers()` détecte le nouveau fichier. | - Aucun fichier trouvé → attente (polling). <br>- Le fichier n’est pas un CSV → fichier ignoré, log d’avertissement. | Le répertoire `input/` est accessible. | Le fichier est listé et son chemin transmis à l’étape de validation. |
| **UC‑02** Valider & nettoyer | MOA / MOE | 1. Le pipeline lit le CSV via pandas. <br>2. Chaque colonne est comparée aux spécifications SQL (ex. `codeOrganisme` CHAR(10)). <br>3. Les fonctions `na_to_empty`, `int_to_bool`, `str_to_float` sont appliquées. | - Erreur de type → le fichier est déplacé vers `error/` avec un rapport (UC‑05). <br>- Ligne partielle invalide → ligne rejetée, les autres sont conservées. | Le fichier CSV est présent et lisible. | Data‑frame nettoyée, prête à être stockée. |
| **UC‑03** Charger en BDD | MOE | 1. `GestionnaireBaseDonnees.stocker_dataframe()` insère le DataFrame dans la table cible via `to_sql`. <br>2. En cas de succès, le fichier est déplacé vers `processed/`. | - Exception SQL (ex. contrainte d’unicité) → rollback, le fichier est déplacé vers `error/`. | Table cible déjà créée (`AfinopeBase.metadata.create_all`). | Données persistées, fichier archivé, log de succès. |
| **UC‑04** Générer vues d’analyse | Data Analyst | 1. Les vues SQL (`tdb_view`, `tdb_abe_view`, …) sont créées automatiquement par les scripts `sql/06_superset/...`. <br>2. Superset lit les vues pour les tableaux de bord. | - Vue manquante → alerte dans le pipeline (UC‑06). | Base de données opérationnelle. | Vues disponibles, tableau de bord actualisé. |
| **UC‑05** Produire rapports d’erreurs | MOA | 1. En cas d’échec de validation ou de chargement, `GestionnaireFichiersCSV.deplacer_fichier()` déplace le fichier vers `error/`. <br>2. Un fichier `error_report_<timestamp>.txt` est créé avec le détail. | - Échec d’écriture du rapport → log critique. | Un fichier a été rejeté. | Rapport d’erreur accessible, trace dans `logs/csv-validation.log`. |
| **UC‑06** Orchestrer pipelines | MOE | 1. Dagster charge le **circuit d’alimentation** (`circuit_alimentation.py`). <br>2. Chaque étape (UC‑01 → UC‑05) est définie comme un *solid*. <br>3. Le pipeline s’exécute à la demande ou via schedule. | - Crash d’un solid → pipeline en état `FAILED`, notification Slack (ou email). | Dagster installé et configuré. | Pipeline terminé (`SUCCESS` ou `FAILED`). |
| **UC‑07** Déployer stack | Administrateur Système | 1. `docker-compose up -d` lance `db` et `app`. <br>2. Le conteneur `app` démarre le serveur Dagster (`dagster-webserver`). | - Image non‑buildée → `docker compose build` requis. <br>- Port 4400 occupé → choisir un autre port. | Docker et Docker‑Compose installés. | Stack fonctionnelle, UI Dagster accessible. |
| **UC‑08** Auditer traitements | RSSI / MOA | 1. Chaque exécution crée une entrée `audit_log` (table fictive). <br>2. Les métadonnées (fichier source, date, statut) sont enregistrées. | - Table d’audit indisponible → alerte opérationnelle. | Table `audit_log` créée. | Historique complet consultable, rétention conforme RGPD. |

---  

## 5️⃣ Processus métier (BPMN)  

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#2F80ED','edgeLabelBackground':'#fff','fontFamily':'Helvetica'}}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
bpmnDiagram;
    participant Opérateur as OP;
    participant Système as SYS;
    participant Analyste as AN;
    startEvent(id="start", name="Début du traitement")
    task(id="t1", name="Détection du fichier CSV")
    exclusiveGateway(id="gw1", name="Fichier valide ?")
    task(id="t2", name="Validation & Nettoyage")
    task(id="t3", name="Chargement BDD")
    task(id="t4", name="Génération vues")
    endEvent(id="end_success", name="Traitement terminé")
    endEvent(id="end_error", name="Erreur & archivage")

    startEvent --> t1;
    t1 --> gw1;
    gw1 -->|Oui| t2;
    gw1 -->|Non| end_error;
    t2 --> t3;
    t3 --> t4;
    t4 --> end_success
```

*Ce processus décrit le flux de traitement d’un fichier depuis son dépôt jusqu’à la mise à jour des vues d’analyse, avec gestion d’erreur intégrée.*

---  

## 6️⃣ Règles métier et contraintes fonctionnelles  

| # | Règle métier (IF … THEN) | Source / Référence |
|---|---|---|
| **R‑01** | **IF** le champ `codeOrganisme` est vide **THEN** l’enregistrement est rejeté. | Table `ORGANISME` – PK non‑null. |
| **R‑02** | **IF** `exercice` < 1900 **OR** > 2999 **THEN** l’enregistrement est invalide. | Toutes les tables contenant `exercice`. |
| **R‑03** | **IF** le type de la colonne est `numeric(17,2)` **THEN** la valeur doit être convertible en décimal avec deux décimales. | Colonnes `montant`, `debit*`, `credit*`. |
| **R‑04** | **IF** `codeDevise` est renseigné **THEN** il doit être l’un des codes ISO 4217 supportés (EUR, USD, …). | Contrôle métier dans `helper.py`. |
| **R‑05** | **IF** le champ `typeDocument` = `'AB'` **THEN** la table cible est `ABE`. | Mapping du fichier d’exécution. |
| **R‑06** | **IF** le fichier contient la chaîne `''` dans un champ `bigint` **THEN** le traitement doit nettoyer la chaîne avant insertion. | Constat dans `dgfip/processing/known_issues/known_issue.txt`. |
| **R‑07** | **IF** le pipeline échoue à un *solid* **THEN** le statut global du run = `FAILED` et un mail de notification est envoyé. | Dagster `circuit_alimentation`. |
| **R‑08** | **IF** la donnée est stockée **THEN** la date de chargement (`dateChargement`) doit être enregistrée au format ISO 8601. | Table d’audit. |
| **R‑09** | **IF** le volume de lignes > 1 000 000 **THEN** le batch doit être découpé en sous‑lots de 250 000 lignes. | Optimisation performances. |
| **R‑10** | **IF** la base de données est restaurée **THEN** les vues `tdb_*` doivent être recréées automatiquement. | Script de migration. |

### Contraintes non fonctionnelles  

| # | Contraintes |
|---|---|
| **C‑01** | **Sécurité** : Les variables d’environnement (ex. mots‑de‑passe DB) sont stockées dans le fichier `.env` et ne sont jamais versionnées. |
| **C‑02** | **Performance** : Le pipeline complet doit traiter 1 M lignes en ≤ 5 minutes (hardware standard = 4 CPU, 8 Go RAM). |
| **C‑03** | **Disponibilité** : Service `app` doit être disponible 99,5 % sur une base mensuelle. |
| **C‑04** | **Scalabilité** : Le conteneur `app` doit pouvoir être répliqué (Docker Swarm/K8s) sans modification du code. |
| **C‑05** | **Portabilité** : Le projet doit fonctionner sous Linux (Ubuntu 22.04) et Windows 10/11 (via WSL). |
| **C‑06** | **Traçabilité** : Tous les logs sont centralisés dans `logs/` et au format JSON pour ingestion ELK. |
| **C‑07** | **Conformité RGPD** : Aucun PII (données personnelles) n’est stocké dans les tables financières. |
| **C‑08** | **Interopérabilité** : Les vues SQL sont compatibles avec PostgreSQL 13+. |

---  

## 7️⃣ Parcours utilisateurs (User Journey)  

| Étape | Action utilisateur | Interaction système | Critères d’acceptation (Gherkin) |
|---|---|---|---|
| **J‑01** | L’opérateur dépose un fichier CSV dans le répertoire d’entrée. | Le service de *watcher* détecte le nouveau fichier. | `Given` le répertoire `input/` existe `When` un fichier `REF_ORGANISME_20240901.csv` est copié `Then` le système doit lister le fichier dans les 5 s. |
| **J‑02** | L’opérateur consulte le journal d’erreurs. | Le système génère `error_report_20240901.txt` si le fichier est invalide. | `Given` le fichier contient une colonne manquante `When` le pipeline s’exécute `Then` un fichier d’erreur doit être créé avec le détail de la colonne manquante. |
| **J‑03** | Le data analyst ouvre Superset et sélectionne le tableau de bord « Pilotage ». | Les vues `tdb_view` sont rafraîchies automatiquement. | `Given` le pipeline a terminé avec succès `When` le data analyst rafraîchit le tableau de bord `Then` les indicateurs affichent les données du jour. |
| **J‑04** | L’administrateur redémarre le service après une mise à jour. | Docker compose relance les containers. | `Given` une nouvelle image Docker disponible `When` `docker compose up -d` est exécuté `Then` le service `app` doit répondre sur le port 4400 en < 10 s. |
| **J‑05** | Le RSSI extrait le rapport d’audit mensuel. | Le système interroge la table `audit_log`. | `Given` le mois de septembre 2024 `When` le RSSI lance la requête `SELECT … FROM audit_log WHERE dateChargement BETWEEN …` `Then` le résultat doit contenir ≥ 95 % des fichiers traités. |

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)  

> **Note** : Le diagramme ci‑dessous est une version **abstraite** (pas de types SQL) afin de rester indépendant de l’implémentation technique.  

```mermaid
classDiagram
    class Organisme {
    +codeOrganisme : string;
    +libelleOrganisme : string;
    +siret : string;
    +dateJuridique : date;
    +dateCreation : date;
    +dateCloture : date;
    +dateLiquidation : date;
    +dateDocument : date;

    class Structure {
    +codeOrganisme : string;
    +codeBudget : string;
    +libelleBudget : string;
    +dateCreation : date;
    +dateCloture : date;
    +dateDocument : date;

    class Nomenc {
    +exercice : int;
    +typeNomenclature : string;
    +libelleNomenclature : string;
    +numeroCompte : bigint;
    +sens : string;
    +libelleCompte : string;
    +dateDocument : date;

    class Tiers {
    +codeOrganisme : string;
    +codeBudget : string;
    +exercice : int;
    +codeTiers : string;
    +libelleTiers : string;
    +dateDocument : date;

    class Nature {
    +codeOrganisme : string;
    +codeBudget : string;
    +exercice : int;
    +codeNature : string;
    +libelleNature : string;
    +dateDocument : date;

    class Destination {
    +codeOrganisme : string;
    +codeBudget : string;
    +exercice : int;
    +codeDestination : string;
    +libelleDestination : string;
    +dateDocument : date;

    class Origine {
    +codeOrganisme : string;
    +codeBudget : string;
    +exercice : int;
    +codeOrigine : string;
    +libelleOrigine : string;
    +dateDocument : date;

    class Pluriannuel {
    +codeOrganisme : string;
    +codeBudget : string;
    +exercice : int;
    +codePluriannuel : string;
    +libellePluriannuel : string;
    +typologieOperation : string;
    +codeOperationFlechee : bool;
    +debutOperationPluri : date;
    +finOperationPluri : date;
    +dateDocument : date;

    class Executoire {
    <<abstract>>
    +dateExecutoire : date;
    +codeLibelle : string;
    +codeOrganisme : string;
    +exercice : int;
    +typeDocument : string;
    +typeBudget : string;
    +typeRang : string;
    +codeDevise : string;
    +montant : decimal;
    +dateDocument : date;

    class DESP {
    +codeDestination : string;
    +codeOrigine : string;
    +impact : string;
    +typeBudget : string;
    +typeRang : string;
    +typeDocument : string;

    class EFP {
    +codePrevisionExecution : bool;
    +codeCompteFinancier : bool;

    class Execution {
    <<abstract>>
    +codeLibelle : string;
    +codeOrganisme : string;
    +exercice : int;
    +typeDocument : string;
    +typeBudget : string;
    +typeRang : string;
    +codeDevise : string;
    +montant : decimal;
    +dateDocument : date;

    class ABE {
    +impact : string;
    +codeRecherche : string;
    +typeSequence : string;

    class BAL {
    +codeCompte : bigint;
    +libelleCompte : string;
    +debitEntree : decimal;
    +debitCumul : decimal;
    +debitTotal : decimal;
    +creditEntree : decimal;
    +creditCumul : decimal;
    +creditTotal : decimal;
    +soldeDebiteur : decimal;
    +soldeCrediteur : decimal;
    +typeNomenclature : string;
    +typeSequence : string;

    class BIL {
    +codeLibelle : string;
    +typeSequence : string;

    class CR {
    +codeLibelle : string;
    +typeSequence : string;

    Organisme "1" --> "0..*" Structure : possède;
    Organisme "1" --> "0..*" Nomenc : référence;
    Organisme "1" --> "0..*" Tiers : référence;
    Organisme "1" --> "0..*" Nature : référence;
    Organisme "1" --> "0..*" Destination : référence;
    Organisme "1" --> "0..*" Origine : référence;
    Organisme "1" --> "0..*" Pluriannuel : référence;
    Executoire <|-- DESP
    Executoire <|-- EFP
    Execution <|-- ABE
    Execution <|-- BAL
    Execution <|-- BIL
    Execution <|-- CR
```

---  

## 9️⃣ Critères d’acceptation et validation  

| Fonction de service | Critère d’acceptation | Méthode de validation | Responsable |
|---|---|---|---|
| **FS‑01** Collecte | Le fichier est détecté en < 5 s. | Test d’intégration (déploiement local). | MOE |
| **FS‑02** Validation | ≥ 99 % des lignes valides, rapport d’erreurs généré. | Jeu de données de test (valides + invalides). | MOA |
| **FS‑03** Nettoyage | Aucun champ `NULL` inattendu après transformation. | Comparaison avant/après (pandas). | MOE |
| **FS‑04** Enrichissement | Champ `dateChargement` présent et ISO‑8601. | Requête SQL sur table cible. | MOA |
| **FS‑05** Stockage | Nombre d’enregistrements insérés = lignes valides. | `SELECT COUNT(*)` avant/after. | MOE |
| **FS‑06** Gestion erreurs | 100 % des fichiers rejetés sont dans `error/` avec rapport. | Inspection du répertoire `error/`. | MOA |
| **FS‑07** Orchestration | Run Dagster `SUCCESS` ≥ 98 % des exécutions. | Dashboard Dagster + métriques. | MOE |
| **FS‑08** Vues d’analyse | Temps de réponse ≤ 2 s sur les vues de tableau de bord. | Tests de charge (JMeter). | Data Analyst |
| **FS‑09** Traçabilité | Table `audit_log` conserve 180 jours. | Requête de vérification de rétention. | RSSI |
| **FS‑10** Déploiement | Build ≤ 5 min, stack prête en ≤ 30 s. | Script CI/CD + mesure temps. | Administrateur Système |

---  

## 10️⃣ Annexes  

### 10.1 Glossaire métier  

| Terme | Définition |
|---|---|
| **Référentiel** | Table de référence (ex. `ORGANISME`, `NOMENC`) contenant les métadonnées comptables. |
| **Exécutoires** | Données budgétaires avec dates d’exécution (ex. `DESP`, `EFP`). |
| **Exécution** | Données réelles de mouvements comptables (ex. `ABE`, `BAL`). |
| **Piloter** | Suivre l’évolution des engagements et dépenses à travers les vues `tdb_*`. |
| **Circuit d’alimentation** | Ensemble des *solids* Dagster orchestrant le flux de données. |
| **Superset** | Plateforme de visualisation BI qui consomme les vues PostgreSQL. |
| **Dagster** | Framework d’orchestration de pipelines de données. |
| **Audit log** | Historique détaillé de chaque traitement (fichier, date, statut). |

### 10.2 Référentiels et normes applicables  

| Référence | Intitulé |
|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel. |
| **ISO/IEC/IEEE 29148 :2018** | Ingénierie des exigences – Processus de spécification et de gestion. |
| **ISO/IEC 19505** | UML 2.x – Notation et diagrammes. |
| **ISO/IEC 19510** | BPMN – Modélisation des processus métier. |
| **RGPD** | Règlement général sur la protection des données – Traçabilité et minimisation. |
| **RGS** | Référentiel Général de Sécurité – Sécurité des systèmes d’information de l’État. |

### 10.3 Historique des versions du document  

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 2026‑04‑27 | ChatGPT (assistant) | Création du CCF complet à partir des sources du projet afinope. |
| 1.1 | 2026‑04‑28 | — | Ajout du diagramme BPMN et mise à jour des critères d’acceptation (retour MOA). |

---  

*Fin du Cahier des Charges Fonctionnel – Projet **afinope**.*  