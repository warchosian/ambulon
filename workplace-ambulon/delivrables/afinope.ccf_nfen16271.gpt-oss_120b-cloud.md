# Cahier des Charges Fonctionnel (CCF) – Projet **afinope**  
*Conforme à la norme NF EN 16271 :2013 – Management par la valeur*  

> **Version** : 1.0 – 28 avril 2026  
> **Auteur** : Équipe projet afinope (M. Khalid EL‑OUSAMI – référent fonctionnel)  

---  

## 1. Présentation du projet  

| Élément | Description |
|---|---|
| **Intitulé** | afinope – Application financière des opérateurs de l’État |
| **Contexte** | Le ministère de la Transition Écologique et Solidaire (DGFiP) doit collecter, valider, stocker et piloter les flux financiers (référentiels, exécutoires, exécutions) provenant de multiples sources CSV. L’existant repose sur des scripts ad‑hoc ; le projet vise à industrialiser le traitement, garantir la traçabilité et offrir des tableaux de bord décisionnels (Superset). |
| **Enjeux stratégiques** | - Conformité aux exigences légales (RGPD, RGS, archivage)  <br> - Fiabilité et exhaustivité des données budgétaires  <br> - Réduction des délais de mise à disposition des indicateurs de pilotage  <br> - Mutualisation de la chaîne de traitement (Docker, Dagster) pour faciliter la maintenance et la montée en charge |
| **Objectifs du projet** | 1. **Ingestion** automatisée des fichiers CSV (entrée, sortie, erreur). <br> 2. **Validation** et normalisation des données conformément aux référentiels (organisme, nature, destination, …). <br> 3. **Stockage** fiable dans une base PostgreSQL. <br> 4. **Exposition** des jeux de données via vues SQL et tableau de bord Superset. <br> 5. **Pérennité** grâce à une chaîne d’orchestration (Dagster) et à la conteneurisation (Docker). |
| **Périmètre fonctionnel** | **Inclus** : <br> • Tous les fichiers CSV listés dans `analyse/flux.txt` (référentiel, executoire, exécution). <br> • Le pipeline d’ingestion, validation, transformation, stockage. <br> • Les API REST internes (Dagster) et les vues SQL de pilotage. <br> • L’infrastructure Docker (app + db). <br> **Exclus** : <br> • Gestion des accès utilisateurs (IAM) – hors du périmètre technique. <br> • Reporting externe (export PDF, emailing). <br> • Gestion des sauvegardes de la base (hors du scope de l’application). |

---  

## 2. Analyse de la valeur  

### 2.1 Fonctions de service (FS) – Niveau système  

| N° | Fonction de service | Type | Description (QUOI) | Critères de performance (mesurables) |
|---|---|---|---|---|
| **FS‑01** | **Ingestion des fichiers CSV** | **FP** (Fonction Principale) | Recevoir les fichiers CSV déposés dans le répertoire *entrée*, les copier vers *sortie* ou *erreur* selon le résultat du traitement. | • Temps moyen d’acquisition ≤ 5 s par fichier (mesuré par log). <br> • Taux de perte de fichier = 0 % (audit quotidien). |
| **FS‑02** | **Validation de la conformité des données** | **FC** (Fonction Contraint) | Vérifier la présence, le type et la cohérence des colonnes (ex. `exercice` entre 1900‑2999, `codeOrganisme` 10 caractères). | • Taux de rejet ≤ 2 % du volume total (rapport journalier). <br> • Détection d’erreurs critiques (ex. champ obligatoire vide) = 100 % (pas de faux‑négatifs). |
| **FS‑03** | **Transformation / Normalisation** | **FC** | Appliquer les règles métier (ex. conversion « , » → « . » pour les décimaux, mise en booléen, nettoyage des espaces). | • Erreurs de transformation < 0,1 % (audit aléatoire 100 lignes). |
| **FS‑04** | **Stockage persistant** | **FC** | Persister les données validées dans les tables PostgreSQL définies sous `sql/`. | • Durée d’insertion ≤ 3 s par 10 000 lignes (benchmark). <br> • Intégrité référentielle (FK) = 100 % (test de contrainte). |
| **FS‑05** | **Mise à disposition des vues de pilotage** | **FC** | Générer les vues SQL (ex. `tdb_view`, `tdb_abe_view`) et les rendre accessibles à Superset. | • Temps de rafraîchissement ≤ 30 min après dépôt du dernier fichier. |
| **FS‑06** | **Orchestration et monitoring** | **FC** | Exécuter les pipelines Dagster, collecter les métriques d’exécution et alerter en cas d’échec. | • Disponibilité du scheduler ≥ 99,5 % (mesure mensuelle). <br> • Temps moyen de détection d’anomalie ≤ 2 min. |
| **FS‑07** | **Conteneurisation & déploiement** | **FC** | Fournir les images Docker (`Dockerfile.app`, `docker‑compose.yml`) pour l’app et la base de données. | • Build Docker ≤ 5 min (CI). <br> • Démarrage complet du stack ≤ 2 min. |

> **Note** : La fonction **FP** (FS‑01) justifie l’existence du produit : sans ingestion de fichiers, aucune donnée ne peut être traitée. Toutes les autres fonctions sont **FC**, imposées par le contexte réglementaire, technique et métier.  

### 2.2 Pondération des critères (Valeur)  

| Fonction | Critère | Niveau d’importance | Flexibilité | Type de critère |
|---|---|---|---|---|
| FS‑01 | Temps moyen d’acquisition ≤ 5 s | Obligatoire | Fixe | Performance |
| FS‑01 | Taux de perte de fichier = 0 % | Obligatoire | Fixe | Qualité |
| FS‑02 | Taux de rejet ≤ 2 % | Souhaitable | Négociable | Qualité |
| FS‑02 | Détection d’erreurs critiques = 100 % | Obligatoire | Fixe | Sécurité |
| FS‑03 | Erreurs de transformation < 0,1 % | Souhaitable | Négociable | Qualité |
| FS‑04 | Durée d’insertion ≤ 3 s/10 k lignes | Obligatoire | Fixe | Performance |
| FS‑04 | Intégrité référentielle = 100 % | Obligatoire | Fixe | Sécurité |
| FS‑05 | Temps de rafraîchissement ≤ 30 min | Souhaitable | Négociable | Performance |
| FS‑06 | Disponibilité du scheduler ≥ 99,5 % | Obligatoire | Fixe | Fiabilité |
| FS‑06 | Détection d’anomalie ≤ 2 min | Souhaitable | Négociable | Réactivité |
| FS‑07 | Build Docker ≤ 5 min | Souhaitable | Négociable | Productivité |
| FS‑07 | Démarrage stack ≤ 2 min | Souhaitable | Négociable | Productivité |

---  

## 3. Expression fonctionnelle du besoin  

### 3.1 Niveau **Système** (B‑01) – Besoin global  

| ID | Description fonctionnelle (QUOI) | Critère d’appréciation (mesurable) | Niveau d’importance | Flexibilité |
|---|---|---|---|---|
| **B‑01** | **Acquisition, validation, transformation, stockage et diffusion des flux financiers** | • Temps total du cycle (ingestion → vue) ≤ 45 min pour un lot de 500 000 lignes. <br> • Taux d’erreur global ≤ 0,5 % (défauts détectés vs lignes traitées). | Obligatoire | Fixe |

### 3.2 Niveau **Sous‑système** (B‑01‑xx) – Référentiel, Executoire, Exécution  

| ID | Description fonctionnelle | Critère d’appréciation | Niveau d’importance | Flexibilité |
|---|---|---|---|---|
| **B‑01‑01** | **Gestion du référentiel** (tables `ORGANISME`, `STRUCTURE`, `NOMENC`, …) | • Exhaustivité : 100 % des lignes du référentiel présentes dans la table. <br> • Intégrité : aucune violation de contrainte PK/FK. | Obligatoire | Fixe |
| **B‑01‑02** | **Gestion des exécutoires** (`DESP`, `EFP`) | • Taux de rejet ≤ 1 % (défauts de format). <br> • Respect du schéma (`dateExecutoire` date, `montant` numeric(17,2)). | Obligatoire | Fixe |
| **B‑01‑03** | **Gestion des exécutions** (`ABE`, `BAL`, `BIL`, `CR`) | • Temps moyen d’insertion ≤ 3 s/10 k lignes. <br> • Vérification de la cohérence des montants (somme = total budget). | Obligatoire | Fixe |
| **B‑01‑04** | **Production des vues de pilotage** (`tdb_view`, `tdb_abe_view`, …) | • Latence de rafraîchissement ≤ 30 min après le dernier fichier. <br> • Disponibilité de la vue ≥ 99,5 % (période de monitoring). | Souhaitable | Négociable |

### 3.3 Niveau **Élémentaire** (B‑01‑xx‑yy) – Exemple de besoin élémentaire  

| ID | Description fonctionnelle | Critère d’appréciation | Niveau d’importance | Flexibilité |
|---|---|---|---|---|
| **B‑01‑01‑01** | **Lecture du répertoire d’entrée** | • Détection de tout nouveau fichier CSV dans ≤ 2 s (polling). | Obligatoire | Fixe |
| **B‑01‑01‑02** | **Conversion du séparateur décimal** | • 99,9 % des valeurs numériques converties correctement (test aléatoire 1000 lignes). | Souhaitable | Négociable |
| **B‑01‑02‑01** | **Contrôle de la colonne `exercice`** | • Valeur comprise entre 1900 et 2999 pour 100 % des lignes. | Obligatoire | Fixe |
| **B‑01‑03‑01** | **Insertion en mode `append`** | • Aucun doublon PK détecté après insertion (vérif. PK). | Obligatoire | Fixe |
| **B‑01‑04‑01** | **Publication de la vue `tdb_view`** | • Vue rafraîchie et visible dans Superset sous 30 min. | Souhaitable | Négociable |

> **Identifiant unique** : chaque besoin possède un identifiant hiérarchique (B‑xx‑xx‑xx) garantissant la traçabilité dans le suivi de projet.  

---  

## 4. Caractérisation des besoins  

| Fonction | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|
| **FS‑01 – Ingestion** | Temps moyen d’acquisition ≤ 5 s | Obligatoire | Fixe | Aucun fichier ne doit être modifié avant validation. |
| **FS‑01 – Ingestion** | Taux de perte de fichier = 0 % | Obligatoire | Fixe | Conformité RGPD – traçabilité du traitement. |
| **FS‑02 – Validation** | Détection d’erreurs critiques = 100 % | Obligatoire | Fixe | Respect des règles métier décrites dans `analyse/flux.txt`. |
| **FS‑02 – Validation** | Taux de rejet ≤ 2 % | Souhaitable | Négociable | Peut être ajusté selon la qualité des sources externes. |
| **FS‑03 – Transformation** | Erreurs de transformation < 0,1 % | Souhaitable | Négociable | Utilisation de fonctions `helper.py` (na_to_empty, int_to_bool, str_to_float). |
| **FS‑04 – Stockage** | Durée d’insertion ≤ 3 s/10 k lignes | Obligatoire | Fixe | Base PostgreSQL 13+, contraintes FK/PK déjà définies. |
| **FS‑04 – Stockage** | Intégrité référentielle = 100 % | Obligatoire | Fixe | Respect des types (`bigint`, `numeric(17,2)`). |
| **FS‑05 – Vues** | Temps de rafraîchissement ≤ 30 min | Souhaitable | Négociable | Dépend du volume quotidien (≈ 500 k lignes). |
| **FS‑06 – Orchestration** | Disponibilité du scheduler ≥ 99,5 % | Obligatoire | Fixe | Dagster version 1.8.9, logs via `docker-compose`. |
| **FS‑07 – Conteneurisation** | Build Docker ≤ 5 min | Souhaitable | Négociable | CI via GitLab (`.gitlab-ci.yml`). |

---  

## 5. Validation de l’expression du besoin  

| Étape | Méthode | Participants | Livrables | Traçabilité |
|---|---|---|---|---|
| **5.1** | Atelier de cadrage (2 jours) – revue du flux métier et des exigences légales | Chef de projet, Responsable fonction finance, Architecte SI, DSI, Responsable RGPD | Document de cadrage, matrice des exigences | Numéro d’identifiant B‑xx‑xx‑xx ↔️ tableau de suivi (Jira/Redmine). |
| **5.2** | Validation technique (prototype Dagster) | Développeurs, Ops, QA | Rapport de preuve de concept (temps d’insertion, vue). | Lié aux exigences B‑01‑xx. |
| **5.3** | Recette fonctionnelle (UAT) – jeux de données réels (exemple `flux.txt`) | Utilisateurs métier (contrôleurs budgétaires) | Rapport de recette, liste des écarts, plan de correction. | Chaque défaut référencé à l’exigence concernée. |
| **5.4** | Validation finale et approbation | Comité de pilotage (MOA, MOE, DAF) | Signature du CCF, mise en production planifiée. | Historique complet dans le registre de configuration. |

---  

## 6. Scénarios d’usage  

| Type | Description | Conditions | Résultat attendu |
|---|---|---|---|
| **Scénario nominal** | Un lot quotidien de 20 CSV référentiels arrive dans le répertoire *entrée*. | Aucun fichier corrompu, connexion DB OK. | Tous les fichiers sont ingérés, validés, transformés, stockés, les vues sont rafraîchies en ≤ 45 min. |
| **Scénario d’erreur – format** | Un fichier `REF_NOMENC_20240522.csv` contient une valeur non‑numérique dans la colonne `numeroCompte`. | Validation détecte l’erreur, le fichier est déplacé vers *erreur*. | Le fichier est signalé dans le log, aucune donnée n’est insérée. |
| **Scénario d’erreur – DB indisponible** | La base PostgreSQL est redémarrée pendant le traitement. | Le pipeline Dagster détecte l’échec de connexion. | Le job est relancé automatiquement (retry = 3). Si l’échec persiste, alerte par e‑mail. |
| **Scénario limite – gros volume** | 1 million de lignes CSV (bal.csv) déposées en une fois. | Ressources CPU/Mémoire suffisantes (Docker + 2 vCPU, 4 Go RAM). | Temps d’insertion ≤ 30 s, le job ne dépasse pas le timeout (5 min). |
| **Scénario de reprise** | Suite à une coupure réseau, le répertoire *entrée* contient des fichiers déjà partiellement traités. | Le pipeline utilise le flag `déjà‑traité` (nom de fichier avec suffixe `.done`). | Les fichiers déjà traités sont ignorés, le reste est repris. |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|---|---|---|---|
| **MOA – Direction Financière** | Responsable métier | Fiabilité des indicateurs budgétaires, traçabilité, conformité RGPD. | Valeur élevée – condition de succès du projet. |
| **MOE – Équipe de développement** | Conception & implémentation | Environnement de dev stable, documentation claire, tests automatisés. | Valeur moyenne – assure la qualité technique. |
| **DSI – Opérations** | Exploitation & maintenance | Conteneurisation, monitoring, sauvegarde, haute disponibilité. | Valeur élevée – garantit la continuité de service. |
| **Contrôleurs budgétaires** | Utilisateurs finaux | Accès aux tableaux de bord Superset, export CSV fiable. | Valeur élevée – satisfaction fonctionnelle. |
| **Auditeur interne** | Contrôle conformité | Historique complet des traitements, logs d’erreurs, traçabilité RGPD. | Valeur critique – conformité légale. |
| **Fournisseur d’infrastructure (Cloud/On‑Prem)** | Hébergement | Compatibilité Docker, ports ouverts (4400, 5432), gestion des secrets. | Valeur moyenne – impact sur la disponibilité. |

---  

## 8. Contraintes et environnement  

| Domaine | Contraintes |
|---|---|
| **Organisationnelles** | – Validation du CCF par le comité de pilotage avant le 30 mai 2026.<br>– Respect du planning de livrables (MVP = 30 juillet 2026). |
| **Réglementaires** | – RGPD : anonymisation des données personnelles (ex. `siret`).<br>– RGS : hébergement des données dans un datacenter certifié. |
| **Techniques** | – Base de données PostgreSQL 13+ (Docker image `postgres:13`).<br>– Langage Python 3.11, dépendances listées dans `pyproject.toml`.<br>– Orchestration Dagster 1.8.9.<br>– Tableau de bord Superset (version compatible). |
| **Temporelles** | – Cycle de traitement quotidien < 45 min.<br>– Temps de mise à jour des vues < 30 min. |
| **Budgétaires** | – Budget total du projet : 150 k € HT (développement + infrastructure).<br>– Coût d’exploitation mensuel estimé : 2 k € (cloud + licences). |

---  

## 9. Critères de sélection et pondération (marchés publics)  

| Critère | Sous‑critère | Pondération | Modalité de notation (0‑5) |
|---|---|---|---|
| **C‑01** | **Coût total** (CAPEX + OPEX) | 30 % | 0 = > 150 k €, 5 = ≤ 80 k € |
| **C‑02** | **Compétences techniques** | 20 % | 0 = aucune expérience Dagster, 5 = ≥ 3 projets similaires livrés |
| **C‑03** | **Conformité réglementaire** (RGPD, RGS) | 15 % | 0 = non‑conforme, 5 = certifié RGS, DPO dédié |
| **C‑04** | **Qualité du livrable** (respect des critères de performance) | 20 % | 0 = non‑respect, 5 = tous les KPI atteints |
| **C‑05** | **Plan de maintenance & support** (SLA, garantie) | 10 % | 0 = < 6 mois, 5 = > 24 mois, support 24/7 |
| **C‑06** | **Méthodologie AGILE / Gestion de projet** | 5 % | 0 = pas de roadmap, 5 = sprints définis, backlog traçable |

> **Note** : La somme des pondérations = 100 %. Les offres seront notées sur 5 points par sous‑critère, puis la note finale sera calculée en appliquant les pondérations.  

---  

## 10. Glossaire et acronymes  

| Acronyme / Terme | Définition |
|---|---|
| **AFINOPE** | Application Financière des Opérateurs de l’État (nom du projet). |
| **CSV** | *Comma‑Separated Values* – format de fichiers source. |
| **Dagster** | Plateforme d’orchestration de pipelines de données. |
| **RGPD** | Règlement Général sur la Protection des Données (UE). |
| **RGS** | Référentiel Général de Sécurité (France). |
| **FP** | Fonction Principale – indispensable à la justification du produit. |
| **FC** | Fonction Contraint – imposée par le contexte (réglementaire, technique, métier). |
| **FP‑/FC‑** | Préfixe utilisé dans la table des fonctions de service. |
| **B‑xx‑xx‑xx** | Identifiant hiérarchique d’un besoin (système, sous‑système, élémentaire). |
| **Superset** | Outil de visualisation et de tableau de bord open‑source. |
| **CI** | *Continuous Integration* – processus d’intégration continue (GitLab CI). |
| **SLA** | *Service Level Agreement* – accord de niveau de service. |
| **PK / FK** | Primary Key / Foreign Key – contraintes d’intégrité de base de données. |
| **SQL** | Structured Query Language – langage de requête relationnelle. |
| **Docker** | Plateforme de conteneurisation d’applications. |
| **MVP** | *Minimum Viable Product* – version fonctionnelle minimale. |
| **UAT** | *User Acceptance Testing* – test d’acceptation utilisateur. |
| **MOA / MOE** | Maîtrise d’Ouvrage / Maîtrise d’Œuvre. |
| **DGFiP** | Direction Générale des Finances Publiques. |

---  

## 11. Annexes (non exhaustives)  

1. **Diagramme de flux métier** – fichier `analyse/flux.txt` (décrit les flux REF, EXECUTOIRE, EXECUTION).  
2. **Modèle conceptuel de données** – tables SQL (voir répertoire `sql/`).  
3. **Exemple de fichier CSV** – `donnees-financieres-referentielles-ro.excalidraw` (schéma).  
4. **Plan de projet** – Gantt (hors du présent CCF).  

---  

*Fin du Cahier des Charges Fonctionnel – Projet **afinope**.*  