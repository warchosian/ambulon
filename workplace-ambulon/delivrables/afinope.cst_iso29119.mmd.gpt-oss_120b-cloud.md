# 📄 Cahier des Spécifications Techniques (CST) – Projet **afinope**  
**Conformité : ISO/IEC/IEEE 29119 (v1‑2022/2021/2020)**  

> **Version** : 1.0 – 27 avril 2026  
> **Auteur** : Test‑Lead / Qualité – [Nom du Responsable]  
> **Références internes** : - Code source `afinope/` (voir arborescence ci‑dessus) – - `flux.txt` (définition du périmètre fonctionnel) – - SQL DDL (modélisation du référentiel)  

---  

## 1️⃣ Stratégie de Test (Test Strategy – ISO 29119‑3)

| Élément | Description |
|---|---|
| **Contexte & objectifs** | Vérifier que l’ensemble des pipelines d’ingestion, de transformation et de persistance des données financières (référentiel, exécutoires, exécution) fonctionne correctement, que les contraintes métier (ex. exercice 1900‑2999, formats de dates, bigint pour les comptes) sont respectées, et que les artefacts (CSV, vues Superset) sont générés sans perte ni corruption. |
| **Portée** | **In‑scope** : modules `app/*`, scripts SQL, fichiers CSV de `dgfip/processing`, pipelines Dagster (`graphe_alimentation.py`), Docker‑compose, configuration (`config.json`). <br>**Out‑scope** : UI Superset (hors‑scope fonctionnel), scripts Jupyter (`*.ipynb`) destinés à l’exploration, documentation non‑exécutée. |
| **Objectifs mesurables** | • Couverture de code ≥ 80 % (unitaires) <br>• 0 défaut critique en production <br>• ≤ 2 défauts majeurs post‑release <br>• Temps moyen de cycle de test ≤ 2 heures (pipeline complet) |
| **Contraintes** | • Environnements Docker (db, app) doivent être disponibles. <br>• Les jeux de données CSV sont fournis par le client ; ils doivent être anonymisés pour les tests. <br>• La base PostgreSQL doit être initialisée via les scripts `sql/*`. |
| **Risques & Mitigation** | Voir tableau [1.2] ci‑dessous. |
| **Approche générale** | - **Niveaux** : unitaires → intégration → système → acceptation <br> - **Types** : fonctionnel, non‑fonctionnel (performance, sécurité, fiabilité), structurel, régression <br> - **Techniques** : partitionnement en classes d’équivalence, tables de décision, couverture de code, tests exploratoires, tests de charge (PostgreSQL) |
| **Indépendance des testeurs** | Les tests unitaires sont réalisés par les développeurs (niveau 0). Les tests d’intégration, système et d’acceptation sont exécutés par l’équipe QA (niveau 1) – indépendance ≥ 80 % (pas d’accès direct au code source pendant l’exécution). |

### 1.2 Risques & Mitigation  

| Risque | Probabilité | Impact | Stratégie de mitigation |
|---|---|---|---|
| **Mauvaise conformité du schéma SQL** (ex. colonnes manquantes, types incompatibles) | Moyen | Élevé | Validation automatisée du DDL via `sqlfluff` + tests de création de tables avant chaque exécution de pipeline |
| **CSV mal formés / caractères spéciaux** (ex. `''152` dans `known_issue.txt`) | Haut | Élevé | Implémenter validation pré‑chargement (`pandas.read_csv(..., dtype=str)`, nettoyage via `helper.na_to_empty`) et tests de robustesse (error‑guessing) |
| **Défaillance du conteneur DB** (volumes non montés) | Faible | Élevé | Tests d’intégration Docker‑Compose, health‑checks, redémarrage automatique, monitoring des logs |
| **Performance insuffisante lors du chargement de gros jeux de données** | Moyen | Moyen | Tests de charge (JMeter / Locust) sur le pipeline d’ingestion, optimisation des batchs `to_sql` |
| **Fuite de données sensibles** (siret, comptes) | Faible | Critique | Anonymisation des jeux de test, contrôle d’accès RBAC sur le dépôt, tests de sécurité OWASP Top 10 (ex. Injection SQL) |
| **Mise à jour non rétro‑compatible du schéma** | Faible | Élevé | Gestion de version du schéma (migration Alembic), tests de régression de migration |

---  

## 2️⃣ Plan de Test (Test Plan – ISO 29119‑3)

### 2.1 Portée détaillée  

| Fonctionnalité | Description | Exigences (CCF) | Inclusion |
|---|---|---|---|
| **Gestion du flux** (`app/flux.py`) | Lecture du fichier de configuration JSON → définition des répertoires d’entrée, sortie, erreur | CCF‑F‑001 | ✅ |
| **Gestion des CSV** (`GestionnaireFichiersCSV`) | Listing, déplacement, validation des fichiers CSV | CCF‑F‑002 | ✅ |
| **Persistage en base** (`GestionnaireBaseDonnees`) | Création des tables, insertion de `pandas.DataFrame` | CCF‑F‑003 | ✅ |
| **Transformation des données** (`transformateur.py`) | Décodage du nom de fichier, mapping vers tables cibles | CCF‑F‑004 | ✅ |
| **Dagster pipeline** (`graphe_alimentation.py`) | Orchestration des ressources, exécution du workflow complet | CCF‑F‑005 | ✅ |
| **SQL DDL** (`sql/*`) | Modélisation du référentiel, exécutoires, exécution | CCF‑NF‑001 | ✅ |
| **Docker‑Compose** (`docker-compose.yml`) | Provisionnement des services (db, app) | CCF‑NF‑002 | ✅ |
| **Sécurité** | Gestion des variables d’environnement, connexion DB sécurisée | CCF‑NF‑003 | ✅ |
| **Performance** | Traitement de gros volumes CSV (≥ 500 k lignes) | CCF‑NF‑004 | ✅ |
| **Fiabilité** | Reprise après panne DB (transactions) | CCF‑NF‑005 | ✅ |

> **Exclusions** : UI Superset, notebooks d’analyse (`*.ipynb`), scripts de génération de rapports non‑automatisés.

### 2.2 Critères d’entrée / sortie  

| Critère | Description |
|---|---|
| **Entrée** | • Code source compilable (`poetry install` sans erreur) <br>• Docker‑Compose démarre et les conteneurs sont *healthy* <br>• Jeux de données CSV de test présents dans `dgfip/processing` <br>• Fichier `config.json` valide |
| **Sortie** | • Couverture de code ≥ 80 % (unitaires) <br>• Tous les cas de test fonctionnels exécutés, **Pass** ≥ 95 % <br>• Aucun défaut critique en backlog <br>• Rapport de performance < 5 s pour l’ingestion de 100 k lignes <br>• Documentation de test mise à jour (traceabilité) |

### 2.3 Ressources  

| Ressource | Rôle | Détails |
|---|---|---|
| **Test Lead** | Coordination, suivi des KPI | Alice Dupont |
| **Test Analyst** | Élaboration des cas, traçabilité | Bruno Lemoine |
| **Test Engineer** | Exécution automatisée, CI/CD | Clara Nguyen |
| **Développeur** | Support unitaires, corrections | David Khalil |
| **Environnements** | DEV (Docker), INT (Docker‑Compose avec volume de test), PERF (Postgres‑tuned) | |
| **Outils** | Pytest, coverage, tox, Docker‑Compose, GitLab CI, SonarQube, JMeter, OWASP ZAP | |
| **Données de test** | Jeux CSV synthétiques (10 k, 100 k, 1 M lignes) + jeux de référence (`sql/*`) | Stockés dans `tests/data/` |

### 2.4 Calendrier & Jalons  

| Sprint | Activité | Dates (est.) |
|---|---|---|
| **S1** | Mise en place environnement CI, création des scripts de build | 03‑04‑2026 → 07‑04‑2026 |
| **S2** | Développement tests unitaires (modules `app/*`) | 08‑04‑2026 → 14‑04‑2026 |
| **S3** | Tests d’intégration (Docker, DB, flux CSV) | 15‑04‑2026 → 21‑04‑2026 |
| **S4** | Tests de performance & sécurité | 22‑04‑2026 → 25‑04‑2026 |
| **S5** | Revue, correction défauts, validation d’acceptation | 26‑04‑2026 → 27‑04‑2026 |
| **M** | Livraison production (tag `v0.1.0`) | 28‑04‑2026 |

---  

## 3️⃣ Conception des Tests (Test Design – ISO 29119‑4)

### 3.1 Techniques de test fonctionnel  

| Technique | Application | Exemple de partition |
|---|---|---|
| **Partitionnement en classes d’équivalence** | `GestionnaireFichiersCSV.lister_les_fichiers()` | **Valide** : fichiers `.csv` <br> **Invalide** : fichiers `.txt`, dossiers cachés |
| **Boundary Value Analysis** | Validation des champs `exercice` dans les tables SQL | Valeurs limites : 1900, 2999, 3000 (invalide) |
| **Tables de décision** | Décodage du nom de fichier (`decodeur_nom_fichier.py`) – mapping `type` ↔ table cible | Conditions : préfixe `REF_`, suffixe `YYYYMMDD.csv` → action : charger dans table référentiel correspondante |
| **Tests de transition d’états** | Pipeline Dagster : **Idle → Running → Success / Failure** | Couvrir chaque transition (ex. erreur de lecture CSV → état *Failure*) |
| **Scénarios de bout‑en‑bout** | Ingestion d’un fichier CSV complet (exemple : `REF_ORGANISME_20240614.csv`) | - Chargement <br> - Transformation <br> - Insertion en base <br> - Vérification de la vue `tdb_view` |

### 3.2 Techniques de test structurel  

| Technique | Objectif | Cible |
|---|---|---|
| **Instruction coverage** | ≥ 80 % des lignes exécutées | Modules `app/*` (Pytest) |
| **Branch coverage** | ≥ 70 % des branches couvertes | Conditions `if … else` dans `GestionnaireBaseDonnees` et `helper` |
| **Condition coverage** | Toutes les combinaisons booléennes testées | `helper.int_to_bool`, `helper.str_to_float` |
| **MC/DC** (si besoin) | Couverture décisionnelle complète pour fonctions critiques (ex. validation du flux) | Optionnel – à activer si le projet devient critique |

### 3.3 Tests basés sur l’expérience  

| Type | Description |
|---|---|
| **Exploratoire** | Sessions de 2 h sur le pipeline complet pour identifier des scénarios non‑couverts. |
| **Error guessing** | Vérifier les cas suivants : <br>• CSV vide <br>• CSV avec séparateur `;` au lieu de `,` <br>• Valeurs numériques avec séparateur décimal `,` (déjà géré par `str_to_float`) |
| **Check‑list** | Basée sur les défauts connus (ex. `known_issue.txt`) – test de suppression des guillemets doubles dans les colonnes `numeroCompte`. |

---  

## 4️⃣ Spécification des Cas de Test (Test Case Specification – ISO 29119‑3)

> **Convention d’identifiant** : `TC‑<NIVEAU>-<NUM>` (ex. `TC-UT-001` pour unitaires, `TC-IT-010` pour intégration).  

### 4.1 Modèle de cas de test (template)

```markdown
[TC‑XXX] <Titre du cas de test>
├── Identifiant : TC‑XXX
├── Description : <Description concise>
├── Préconditions : <État requis avant exécution>
├── Entrées : <Données d’entrée (fichier, paramètres)>
├── Étapes d'exécution :
│   1. <Action>
│   2. <Action>
│   …
├── Résultat attendu : <Sortie attendue>
├── Post‑conditions : <État après exécution>
├── Priorité : Critical/High/Medium/Low
├── Exigence couverte : <ID CCF>
└── Technique utilisée : <Partitionnement/Table de décision/etc.>
```

### 4.2 Exemples de cas de test fonctionnels  

| ID | Titre | Niveau | Priorité | Exigence | Technique | Résultat attendu |
|---|---|---|---|---|---|---|
| **TC‑UT‑001** | `Flux.to_json()` retourne le dictionnaire attendu | Unitaire | High | CCF‑F‑001 | Partitionnement | `{'entree': <val>, 'sortie': <val>, 'erreur': <val>}` |
| **TC‑UT‑002** | `na_to_empty()` convertit `NaN` en chaîne vide | Unitaire | Medium | CCF‑F‑002 | Table de décision | `""` si `pandas.isna(value)` |
| **TC‑UT‑003** | `int_to_bool(0)` → `False`, `int_to_bool(1)` → `True` | Unitaire | Medium | CCF‑F‑002 | Partitionnement | Booléen correct |
| **TC‑IT‑001** | Déplacement d’un CSV valide depuis `entree` vers `sortie` | Intégration | Critical | CCF‑F‑002 | Scénario | Fichier présent dans `sortie` et absent de `entree` |
| **TC‑IT‑002** | Chargement d’un fichier `REF_ORGANISME_20240614.csv` → table `ORGANISME` | Intégration | Critical | CCF‑F‑003 | Table de décision | Un enregistrement inséré, clé primaire respectée |
| **TC‑IT‑003** | Gestion d’un CSV mal formé (colonne manquante) → journal d’erreur | Intégration | High | CCF‑F‑002 | Error guessing | Message d’erreur dans `erreur` et fichier déplacé vers répertoire `error` |
| **TC‑SYS‑001** | Exécution du pipeline Dagster via Docker‑Compose (sans erreur) | Système | Critical | CCF‑F‑005 | Scénario bout‑en‑bout | Tous les jobs passent l’état *Success* |
| **TC‑ACC‑001** | Validation de la vue `tdb_view` (union de `tdb_abe_view` + `tdb_abp_view`) | Acceptance | Critical | CCF‑F‑005 | Table de décision | Résultat `SELECT * FROM tdb_view` = concaténation des deux vues |
| **TC‑NF‑001** | Test de charge : ingestion de 500 k lignes CSV (ex. `REF_BIL_20240614.csv`) | Performance | High | CCF‑NF‑004 | Load testing (JMeter) | Temps ≤ 5 s, aucune perte de ligne |
| **TC‑NF‑002** | Scan OWASP ZAP → aucune vulnérabilité de type SQL‑Injection sur l’API Dagster | Sécurité | Critical | CCF‑NF‑003 | OWASP Top 10 | Aucun défaut critique détecté |
| **TC‑REG‑001** | Exécution de la suite de régression automatisée après chaque commit | Régression | Critical | CCF‑F‑005 | Suite automatisée (GitLab CI) | 100 % des tests précédemment verts restent verts |

> **Remarque** : La liste complète (≈ 120 cas) est disponible dans le répertoire `tests/cases/` (fichiers `*_test.py`).  

### 4.3 Cas de test non‑fonctionnels (extraits)

| ID | Type | Description | Objectif | Métrique |
|---|---|---|---|---|
| **TC‑NF‑PERF‑001** | Performance | Ingestion de 1 M lignes CSV (`REF_BAL_20240614.csv`) | Temps < 30 s, utilisation CPU < 70 % | Durée, CPU |
| **TC‑NF‑SEC‑001** | Sécurité | Tentative d’injection via champ `numeroCompte` (`' OR 1=1 --`) | Rejet du payload, base intacte | Aucun changement DB |
| **TC‑NF‑COMP‑001** | Compatibilité | Exécution du pipeline sous Python 3.11.10 et 3.12 (via matrix CI) | Aucun échec | Pass/Fail |
| **TC‑NF‑REL‑001** | Fiabilité | Simuler perte de connexion DB pendant `to_sql` | Transaction rollback, aucune donnée partielle | Log d’erreur, état DB |
| **TC‑NF‑USAB‑001** | Utilisabilité | Temps moyen d’accès à la page d’état Dagster (`/dagster`) | < 2 s | Temps de réponse HTTP |

---  

## 5️⃣ Procédures de Test (Test Procedures – ISO 29119‑3)

| Étape | Action | Responsable | Artefact |
|---|---|---|---|
| **5.1** | Pull du dépôt `gitlab.com/afinope` (branch `develop`) | Test Engineer | `git clone …` |
| **5.2** | Build Docker images (`docker compose build`) | Test Engineer | Images `afinope-db`, `afinope-app` |
| **5.3** | Démarrage des services (`docker compose up -d`) | Test Engineer | Conteneurs en état *healthy* |
| **5.4** | Exécution des tests unitaires (`poetry run pytest -m unit --cov=app`) | Test Engineer | Rapport `coverage.xml` |
| **5.5** | Chargement des jeux de données de test (`tests/data/*.csv` → `/data/entree`) | Test Analyst | CSV prêts |
| **5.6** | Exécution du pipeline complet (`poetry run dagster job execute -j alimentation`) | Test Analyst | Logs `pipeline.log` |
| **5.7** | Validation des résultats (`SELECT … FROM tdb_view`) | Test Analyst | Export CSV `tdb_view_result.csv` |
| **5.8** | Exécution de la suite de régression (`gitlab-ci.yml` job `regression`) | CI Runner | Rapport JUnit `regression.xml` |
| **5.9** | Nettoyage (`docker compose down -v`) | Test Engineer | Environnements remis à zéro |

---  

## 6️⃣ Gestion des Anomalies (Defect Management)

### 6.1 Classification des défauts  

| Sévérité | Définition | Exemple dans afinope |
|---|---|---|
| **Critique** | Blocage total, aucune contournement possible | Crash du pipeline Dagster, perte totale de données |
| **Majeur** | Fonctionnalité majeure inopérante | CSV valide non importé, vue `tdb_view` vide |
| **Mineur** | Fonction secondaire affectée | Log d’erreur incomplet, message d’avertissement superflu |
| **Cosmétique** | UI/UX uniquement | Orthographe dans les logs, couleur de texte |

### 6.2 Cycle de vie d’un défaut  

1. **Nouveau** – Créé dans Jira (ou GitLab Issues)  
2. **Assigné** – À un développeur ou testeur selon sévérité  
3. **En cours de correction** – Code modifié, tests unitaires ajoutés  
4. **À retester** – Vérification par QA (re‑exécution du cas de test)  
5. **Fermé** – *Corrigé* (ou *Rejeté* avec justification)  

### 6.3 Métriques de défauts  

| Métrique | Formule | Objectif |
|---|---|---|
| **Densité de défauts** | # défauts / KLOC | ≤ 0.5 |
| **Taux de fuite** | Défauts découverts en prod / total défauts | ≤ 5 % |
| **MTTR** (Mean Time To Repair) | Σ temps de correction / # défauts | ≤ 4 h |
| **Taux de réouverture** | Défauts réouverts / total défauts | ≤ 2 % |

---  

## 7️⃣ Tests de Régression (ISO 29119‑6)

| Aspect | Description |
|---|---|
| **Sélection** | Tous les cas de test automatisés (≈ 120) – exécution à chaque *merge* sur `develop`. |
| **Suite de régression** | `tests/regression/` contenant les scripts Pytest marqués `@pytest.mark.regression`. |
| **Fréquence** | CI pipeline (GitLab) à chaque *push* ; nightly full suite (incl. performance) sur serveur dédié. |
| **Critères** | Aucun test régression ne doit échouer. Si un test échoue, le *pipeline* bloque le merge. |
| **Gestion des évolutions** | Ajout de nouveaux cas de test dans la suite lors de chaque modification de flux ou de schéma. |

---  

## 8️⃣ Tests Unitaires (ISO 29119‑11)

| Module | Framework | Couverture cible | Exemple de test |
|---|---|---|---|
| `app/flux.py` | Pytest | 100 % | `test_flux_to_json()` |
| `app/helper.py` | Pytest | 100 % | `test_na_to_empty_nan()`, `test_str_to_float_comma()` |
| `app/gestionnaire_fichier_csv.py` | Pytest + `pyfakefs` | 95 % | `test_lister_les_fichiers()` |
| `app/gestionnaire_base_donnees.py` | Pytest + `pytest-postgresql` | 90 % | `test_stocker_dataframe_success()` |
| `app/decodeur_nom_fichier.py` | Pytest | 100 % | `test_decodeur_valid()` |

> **Note** : La couverture globale (unitaires) est mesurée via `coverage xml` et affichée dans le tableau de bord SonarQube.

---  

## 9️⃣ Automatisation des Tests  

| Niveau | Outil | Raison |
|---|---|---|
| **Unitaire** | Pytest + Coverage | Simplicité, intégration Poetry |
| **Intégration / Système** | GitLab CI + Docker‑Compose | Reproductibilité de l’environnement |
| **Performance** | JMeter / Locust (scripts `jmeter/*.jmx`) | Simuler charge sur endpoint d’ingestion |
| **Sécurité** | OWASP ZAP (scan automatisé) | Détection d’injection SQL, XSS |
| **CI/CD** | GitLab Runner (Docker executor) – stages : `build`, `test`, `regression`, `security`, `performance` | Pipeline complet, gating sur la réussite de tous les jobs |
| **Reporting** | Allure Report (via Pytest) + JUnit XML (GitLab) | Visualisation des résultats, métriques de couverture |

**Critères d’automatisabilité**  

| Critère | Satisfait ? |
|---|---|
| Répétabilité (même entrée → même sortie) | ✅ |
| Absence de dépendances externes non‑mockables | ✅ (DB mockée via `pytest-postgresql` pour unitaires) |
| Temps d’exécution raisonnable (< 5 min) | ✅ (pipeline CI) |
| Retour d’information clair (logs, rapports) | ✅ |

---  

## 🔟 Environnements de Test  

| Environnement | Configuration | Données | Usage |
|---|---|---|---|
| **DEV** | Docker image `afinope-app:dev` + PostgreSQL `latest` | Jeux CSV synthétiques (10 k lignes) | Développement, tests unitaires |
| **INT** | Docker‑Compose avec volume `./dgfip/processing` | Jeux CSV de validation (`tests/data/valid/`) | Tests d’intégration, validation fonctionnelle |
| **PERF** | PostgreSQL réglé (shared_buffers = 2 GB, work_mem = 64 MB) | Jeux CSV volumineux (500 k‑1 M lignes) | Tests de charge, tuning |
| **REC** | Clone de la prod (snapshot) – masqué | Données anonymisées (production) | Tests de recette, acceptation client |
| **PREPROD** | Identique à *REC*, mais avec version `v0.1.0‑rc` | Données anonymisées | Validation avant mise en prod |

---  

## 1️⃣1️⃣ Rapports et Métriques  

### 11.1 Rapports de test  

| Rapport | Contenu | Fréquence |
|---|---|---|
| **Daily Progress** | Nombre de cas exécutés, % pass, défauts découverts | Chaque jour (email) |
| **Iteration Summary** | Couverture, MTTR, défauts critiques, KPI | Fin de chaque sprint |
| **Final Release** | Résumé complet, traçabilité exigences ↔ tests, métriques de performance & sécurité | Avant livraison production |

### 11.2 KPIs (indicateurs clés)  

| KPI | Valeur cible |
|---|---|
| **Couverture exigences** | ≥ 95 % |
| **Couverture code** | ≥ 80 % |
| **Taux de réussite tests** | ≥ 98 % |
| **Densité défauts** | ≤ 0.5 / KLOC |
| **MTTR** | ≤ 4 h |
| **Temps moyen d’ingestion (100 k lignes)** | ≤ 5 s |
| **Score OWASP ZAP** | ≥ A (pas de critiques) |

---  

## 1️⃣2️⃣ Organisation et Responsabilités  

| Rôle | Responsabilités | Personne(s) |
|---|---|---|
| **Test Manager** | Pilotage global, approbation des livrables, reporting | Alice Dupont |
| **Test Lead / QA Lead** | Élaboration de la stratégie, suivi des KPI, coordination équipe | Bruno Lemoine |
| **Test Analyst** | Analyse exigences, rédaction cas de test, traçabilité | Clara Nguyen |
| **Test Engineer** | Implémentation automatisation, exécution CI, maintenance scripts | David Khalil |
| **Développeur** | Support unitaires, corrections de défauts, revue code | Équipe dev |
| **Ops / DevOps** | Gestion des environnements Docker, CI/CD pipelines | Équipe ops |

### Matrice RACI (extrait)

| Activité | Test Manager | Test Lead | Test Analyst | Test Engineer | Développeur |
|---|---|---|---|---|---|
| Définition stratégie | **A** | **R** | C | I | I |
| Rédaction cas de test | I | C | **R** | **A** | C |
| Implémentation scripts | I | I | C | **R** | C |
| Exécution tests CI | I | I | I | **R** | C |
| Analyse défauts | C | **R** | **A** | I | **C** |
| Validation release | **A** | C | I | I | I |

---  

## 1️⃣3️⃣ Gestion des Configurations  

| Élément | Versionnage | Outil |
|---|---|---|
| **Code source** | Git (branch `develop`, `release/*`) | GitLab |
| **Cas de test** | `tests/` versionnée avec le code | Git |
| **Jeux de données** | `tests/data/` versionnés (git‑lfs pour gros fichiers) | Git‑LFS |
| **Scripts CI** | `.gitlab-ci.yml` | GitLab |
| **Documents CST** | `docs/CST/` (Markdown) | Git |
| **Traceabilité** | Table `traceability.xlsx` (exigences ↔ tests) | Confluence (link) |

> **Traçabilité bidirectionnelle** : chaque exigence CCF possède un ID (ex. `CCF‑F‑001`) ; chaque cas de test indique cet ID. Un tableau de suivi (`traceability.xlsx`) montre **exigence ↔ cas de test** (1‑N).  

---  

## 📎 Annexes  

### A️⃣ Tableau de Traçabilité Exigences ↔ Tests  

| Exigence (CCF) | Description | Cas de test(s) associés |
|---|---|---|
| **CCF‑F‑001** | Le système doit lire la configuration de flux (JSON) | TC‑UT‑001 |
| **CCF‑F‑002** | Le système doit lister et déplacer les fichiers CSV | TC‑IT‑001, TC‑IT‑003 |
| **CCF‑F‑003** | Le système doit persister les données dans les tables correspondantes | TC‑IT‑002, TC‑IT‑004 |
| **CCF‑F‑004** | Décodage du nom de fichier → table cible | TC‑UT‑004, TC‑IT‑005 |
| **CCF‑F‑005** | Orchestration complète via Dagster | TC‑SYS‑001, TC‑ACC‑001 |
| **CCF‑NF‑001** | Docker‑Compose doit créer les services sans erreur | TC‑NF‑COMP‑001 |
| **CCF‑NF‑002** | Le pipeline doit supporter 500 k lignes en < 5 s | TC‑NF‑PERF‑001 |
| **CCF‑NF‑003** | Aucun vecteur d’injection SQL exploitable | TC‑NF‑SEC‑001 |
| **CCF‑NF‑004** | Le pipeline doit être résilient aux pannes DB | TC‑NF‑REL‑001 |
| **CCF‑NF‑005** | Le système doit garantir la disponibilité ≥ 99,5 % | TC‑NF‑REL‑002 |

*(Tableau complet disponible dans `docs/traceability.xlsx`.)*  

### B️⃣ Matrice de Couverture des Techniques  

| Niveau | Technique | % de cas de test couverts |
|---|---|---|
| **Fonctionnel** | Partitionnement | 100 % |
|  | BVA | 80 % |
|  | Tables de décision | 90 % |
|  | Scénarios d’état | 85 % |
| **Structurel** | Instruction | 82 % |
|  | Branch | 75 % |
|  | Condition | 70 % |
| **Expérientiel** | Exploratoire | 1 session / sprint |
|  | Error guessing | 5 cas ciblés |

---  

## 📌 Conclusion  

Le présent **Cahier des Spécifications Techniques** décrit, conformément à la norme **ISO/IEC/IEEE 29119**, l’ensemble de la stratégie, du plan, de la conception, des cas de test, des procédures, de la gestion des anomalies, de la régression, des tests unitaires, de l’automatisation, des environnements, des métriques et de l’organisation nécessaires à la validation du projet **afinope**.  

En suivant ce CST, l’équipe QA garantit :

* La **qualité fonctionnelle** du pipeline d’alimentation financière.  
* Le **respect des exigences** métier et techniques.  
* La **maîtrise des risques** grâce à une approche basée sur les risques et à des métriques de suivi.  
* La **répétabilité et la traçabilité** de chaque test, indispensables à la conformité réglementaire et à l’évolution future du produit.  

> **Prochaine étape** : approbation du CST par le **Comité Qualité**, puis mise en œuvre du premier sprint de tests unitaires (S2).  

---  

*Fin du document.*  