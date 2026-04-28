# Cahier des Charges Fonctionnel (CCF) – Projet **afinope**  
*Conforme à la norme NF EN 16271 :2013 – Management par la valeur*  

> **Version** : 1.0 – 2026‑04‑28  
> **Références** : NF EN 16271 :2013, NF X50‑151 (remplacée), CG‑U‑2024‑01 (marchés publics)  

---  

## 1. Présentation du projet  

| Élément | Description |
|---|---|
| **Intitulé** | afinope – Application financière des opérateurs de l’État |
| **Contexte** | L’État doit centraliser, valider et piloter les flux financiers (référentiels, exécutoires, exécutions) issus de multiples organismes (ORGANISME, STRUCTURE, …). Le projet vise à automatiser l’import, la transformation, le stockage et la restitution des données dans un environnement Docker‑Compose (PostgreSQL + Dagster). |
| **Enjeux stratégiques** | - Fiabilisation du reporting budgétaire et comptable <br> - Réduction des traitements manuels (gain de temps, diminution du risque d’erreur) <br> - Conformité aux exigences légales (RGPD, RGS, référentiels financiers) <br> - Mise à disposition d’indicateurs de performance via Superset |
| **Objectifs** | 1. **Ingestion** automatisée de fichiers CSV (flux financiers) <br> 2. **Validation** structurée de la conformité des données (schémas, types, contraintes) <br> 3. **Transformation** des données brutes en modèles métier (tables : ORGANISME, BAL, ABE, …) <br> 4. **Persistance** fiable dans PostgreSQL <br> 5. **Orchestration** des pipelines via Dagster <br> 6. **Exposition** de vues analytiques (TDB) pour les outils de BI |
| **Périmètre fonctionnel** | **Inclus** : <br> - Gestion des répertoires d’entrée, sortie et d’erreurs <br> - Lecture, validation et stockage de tous les fichiers listés dans `analyse/flux.txt` (REF, EXECUTOIRE, EXECUTION) <br> - Provision d’un circuit d’alimentation (Dagster) et d’un point d’accès API (Dagster‑WebServer) <br> - Export de vues SQL (tdb_*) pour Superset <br> **Exclus** : <br> - Gestion des droits d’accès aux bases de données (hors périmètre de l’application) <br> - Déploiement de l’infrastructure hardware (serveur PostgreSQL, réseau) <br> - Développement de visualisations spécifiques dans Superset (hors vues fournies) |

---  

## 2. Analyse de la valeur  

### 2.1 Fonctions de service (FS)  

| N° | Fonction de service | Type | Description (QUOI) | Critères de performance (exemples) |
|---|---|---|---|---|
| **FS‑01** | **Ingestion de fichiers CSV** | FP (Fonction Principale) | Recevoir les fichiers déposés dans le répertoire *entrée* et les placer dans *sortie* ou *erreur* après traitement. | - Temps moyen d’ingestion ≤ 5 s par fichier <br> - Taux de fichiers correctement déplacés ≥ 99,5 % |
| **FS‑02** | **Validation de la conformité des données** | FC (Fonction Contraint) | Vérifier que chaque ligne respecte les contraintes SQL (type, longueur, clés étrangères, valeurs numériques) et générer un rapport d’erreurs. | - Couverture de validation ≥ 95 % des colonnes <br> - Détection d’anomalies ≤ 0,1 % de faux‑negatifs |
| **FS‑03** | **Transformation et enrichissement** | FP | Convertir les champs bruts (ex : `str_to_float`, `int_to_bool`) et appliquer les règles métiers (ex : détermination du type de séquence). | - Taux de transformation correcte ≥ 99,8 % <br> - Pas de perte de colonnes essentielles |
| **FS‑04** | **Persistance dans PostgreSQL** | FP | Insérer les DataFrames dans les tables de référence (`ORGANISME`, `BAL`, `ABE`, …) en mode *append* avec gestion des conflits. | - Durée d’insertion ≤ 3 s/10 000 lignes <br> - Aucun doublon de clé primaire |
| **FS‑05** | **Orchestration des pipelines** | FP | Exécuter les étapes ci‑dessus de façon séquentielle/conditionnelle via Dagster (circuit d’alimentation). | - Disponibilité du pipeline ≥ 99,9 % <br> - Temps de cycle complet ≤ 10 min pour un jeu complet |
| **FS‑06** | **Publication de vues analytiques** | FP | Mettre à disposition les vues SQL (tdb_*) exploitées par Superset pour le pilotage et la soutenabilité. | - Latence de rafraîchissement ≤ 5 min après chargement <br> - Intégrité référentielle des vues ≥ 100 % |
| **FS‑07** | **Gestion de la configuration** | FC | Lire le fichier `config.json` (ou variables d’environnement) pour les chemins d’entrée/sortie/erreur. | - Reprise automatique en cas de modification du config ≤ 2 s |
| **FS‑08** | **Traçabilité & journalisation** | FC | Produire des logs (niveau INFO/ERROR) pour chaque étape, accessibles via le conteneur `app`. | - Conservation des logs ≥ 30 jours <br> - Format JSON structuré |

### 2.2 Critères de valeur (pondération)  

| Fonction | Niveau d’importance | Pondération | Justification |
|---|---|---|---|
| FS‑01 | Obligatoire | 15 % | Point d’entrée du processus |
| FS‑02 | Obligatoire | 20 % | Garant de la fiabilité des données |
| FS‑03 | Obligatoire | 15 % | Nécessaire pour la cohérence métier |
| FS‑04 | Obligatoire | 20 % | Persistance définitive et exploitable |
| FS‑05 | Obligatoire | 15 % | Orchestration = valeur ajoutée |
| FS‑06 | Souhaitable | 5 % | Améliore la prise de décision |
| FS‑07 | Obligatoire | 5 % | Flexibilité d’exploitation |
| FS‑08 | Obligatoire | 5 % | Conformité aux exigences d’audit |

---  

## 3. Expression fonctionnelle du besoin  

### 3.1 Niveau **Système** (Besoin global)  

| ID | Besoin (QUOI) | Critère d’appréciation (mesurable) | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|---|
| **B‑01** | Le système doit **ingérer** automatiquement les fichiers CSV déposés dans le répertoire configuré. | - Détection du fichier ≤ 2 s après dépôt <br> - Déplacement du fichier vers *sortie* ou *erreur* sans perte de données | Obligatoire | Fixe | Chemin d’entrée configurable (`config.json`) |
| **B‑02** | Le système doit **valider** chaque ligne conformément aux schémas SQL définis dans le répertoire `sql/`. | - Taux de détection d’erreurs ≥ 99 % <br> - Rapport d’erreurs généré au format JSON | Obligatoire | Négociable (seuil de tolérance) | Respect des contraintes de type, de longueur, de clé primaire/étrangère |
| **B‑03** | Le système doit **transformer** les valeurs brutes en types métiers (float, bool, date). | - Conversion correcte ≥ 99,8 % <br> - Aucun champ obligatoire laissé à `NULL` sans justification | Obligatoire | Négociable (liste de transformations) | Utilisation des fonctions `na_to_empty`, `int_to_bool`, `str_to_float` |
| **B‑04** | Le système doit **stocker** les DataFrames dans PostgreSQL, tables créées via les scripts `sql/*`. | - Temps d’insertion ≤ 3 s/10 k lignes <br> - Aucun doublon de PK, aucune violation d’intégrité | Obligatoire | Fixe | Base PostgreSQL version 13+ (conteneur `db`) |
| **B‑05** | Le système doit **orchestrer** le flux complet (ingestion → validation → transformation → persistance) via Dagster. | - Disponibilité du pipeline ≥ 99,9 % <br> - Temps de cycle complet ≤ 10 min (jeu complet) | Obligatoire | Négociable (temps de cycle) | Déploiement Docker‑Compose, ressources CPU ≥ 2 vCPU |
| **B‑06** | Le système doit **publier** les vues analytiques `tdb_*` actualisées à chaque exécution. | - Latence de mise à jour ≤ 5 min <br> - Intégrité des vues (COUNT = Σ COUNT tables sources) | Souhaitable | Négociable | Vue matérialisée ou non, selon performance |
| **B‑07** | Le système doit **gérer** la configuration (chemins, logs) via un fichier JSON ou variables d’environnement. | - Rechargement de la config ≤ 2 s sans redémarrage <br> - Validation de la syntaxe JSON avant prise en compte | Obligatoire | Fixe | Fichier `config.json` à la racine du projet |
| **B‑08** | Le système doit **produire** des traces d’exécution (logs) structurées, conservées 30 jours. | - Format JSON, champs : `timestamp`, `level`, `module`, `message` <br> - Rotation automatique journalière | Obligatoire | Fixe | Volume Docker `./logs` monté en lecture/écriture |

### 3.2 Niveau **Sous‑système** (exemple : GestionnaireFichiersCSV)  

| ID | Besoin | Critère d’appréciation | Importance | Flexibilité | Contraintes |
|---|---|---|---|---|---|
| **B‑01‑01** | Lister les fichiers *.csv* dans le répertoire *entrée*. | - Retour de la liste < 0,5 s | Obligatoire | Fixe | Aucun fichier non‑CSV doit être retourné |
| **B‑01‑02** | Déplacer chaque fichier traité vers *sortie* ou *erreur*. | - Opération `shutil.move` réussie 100 % du temps | Obligatoire | Négociable (mode copie) | Permissions d’écriture sur les deux répertoires |
| **B‑02‑01** | Vérifier la conformité de chaque colonne selon le DDL SQL. | - Utilisation de `pandas` + contraintes SQL < 1 s/10 k lignes | Obligatoire | Négociable (niveau de granularité) | Table de métadonnées disponible dans `sql/` |
| **B‑04‑01** | Créer les tables si elles n’existent pas (script `AfinopeBase.metadata.create_all`). | - Succès sans erreur 100 % | Obligatoire | Fixe | Connexion via `SourceDonnees.get_connection()` |
| **B‑04‑02** | Insérer le DataFrame en mode `append` avec `index=False`. | - Retour du nombre de lignes insérées > 0 | Obligatoire | Fixe | Gestion des conflits de PK à l’aide de `ON CONFLICT DO NOTHING` (implémentation future) |

---  

## 4. Caractérisation des besoins  

| Fonction | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|
| **FS‑01 – Ingestion** | Temps de détection ≤ 2 s | Obligatoire | Fixe | Chemin *entrée* configurable |
| **FS‑02 – Validation** | Taux de détection d’erreurs ≥ 99 % | Obligatoire | Négociable (seuil) | Respect des DDL SQL |
| **FS‑03 – Transformation** | Conversion correcte ≥ 99,8 % | Obligatoire | Négociable (liste) | Utilisation des helpers `na_to_empty`, `int_to_bool`, `str_to_float` |
| **FS‑04 – Persistance** | Durée d’insertion ≤ 3 s/10 k lignes | Obligatoire | Fixe | PostgreSQL 13+, schéma `public` |
| **FS‑05 – Orchestration** | Disponibilité ≥ 99,9 % | Obligatoire | Négociable (temps de cycle) | Dagster 1.8+, Docker‑Compose |
| **FS‑06 – Vues analytiques** | Latence ≤ 5 min | Souhaitable | Négociable | Vues définies dans `sql/06_superset/01_tdb/` |
| **FS‑07 – Configuration** | Rechargement ≤ 2 s | Obligatoire | Fixe | Fichier `config.json` au format valide |
| **FS‑08 – Traçabilité** | Logs JSON, rotation 30 jours | Obligatoire | Fixe | Volume `./logs` monté |

---  

## 5. Validation de l’expression du besoin  

| Action | Méthode | Responsable(s) | Livrable | Traçabilité |
|---|---|---|---|---|
| **Atelier de cadrage** | Workshop (2 j) – analyse des flux `analyse/flux.txt` | Chef de projet, PO, Architecte, DSI, Responsable Financier | Compte‑rendu + matrice RACI | Référence : V‑01 |
| **Revue fonctionnelle** | Walk‑through du CCF avec les parties prenantes | PO, Experts métier (finances), Auditeur RGPD | Validation signée (PDF) | Référence : V‑02 |
| **Prototype** | Déploiement d’une version “sandbox” (Docker‑Compose) | Équipe dev, Testeurs fonctionnels | Rapport de test d’ingestion & validation | Référence : V‑03 |
| **Acceptation** | Test d’intégration (scenario nominal, limites, erreurs) | Maîtrise d’ouvrage, DSI | Procès‑verbal d’acceptation (PVA) | Référence : V‑04 |

---  

## 6. Scénarios d’usage  

| Type | Description | Étapes clés | Résultat attendu |
|---|---|---|---|
| **Nominal** | Chargement quotidien d’un lot de fichiers CSV (REF, EXECUTOIRE, EXECUTION). | 1. Déposer les fichiers dans *entrée*.<br>2. Dagster déclenche le pipeline.<br>3. Chaque fichier est listé, validé, transformé, stocké.<br>4. Vues `tdb_*` rafraîchies. | Tous les fichiers apparaissent dans *sortie*, logs `INFO`, aucune erreur. |
| **Erreur** | Un fichier contient une colonne `bigint` invalide (`''152`). | 1. Dépôt du fichier.<br>2. Validation détecte l’erreur.<br>3. Le fichier est déplacé vers *erreur*.<br>4. Rapport JSON indique la ligne et la colonne fautives. | Fichier dans *erreur*, log `ERROR`, rapport exploitable pour correction. |
| **Limite** | Traitement d’un fichier de 2 Go (≈ 5 M lignes). | 1. Dépôt du fichier.<br>2. Pipeline démarre, utilise `chunksize` de Pandas.<br>3. Insertion progressive dans PostgreSQL. | Temps total ≤ 15 min, consommation mémoire ≤ 1 Go, aucun dépassement de quota disque. |
| **Exception** | Le conteneur PostgreSQL n’est pas disponible. | 1. Pipeline démarre, tentative de connexion échoue.<br>2. Le système génère un log `CRITICAL` et stoppe le pipeline. | Alerte immédiate, aucune perte de données, reprise possible après restauration du DB. |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|---|---|---|---|
| **Direction Financière** | Maîtrise d’ouvrage | Fiabilité du reporting, conformité légale | Priorité maximale (obligatoire) |
| **Équipe IT / DSI** | Exploitant technique | Facilité de déploiement (Docker), monitoring, logs | Garantie d’opérabilité, réduction des coûts |
| **Auditeurs internes / RGPD** | Contrôle conformité | Traçabilité complète, conservation des logs, gestion des données personnelles | Risque juridique, valeur légale |
| **Développeurs / Mainteneurs** | Réalisateur | Documentation claire, code testable, modularité | Maintenabilité, évolutivité |
| **Utilisateurs finaux (analystes)** | Consommateur de données | Accès aux vues TDB via Superset, délais de mise à jour courts | Valeur décisionnelle |
| **Fournisseur d’infrastructure (hébergeur)** | Fournisseur | Disponibilité du conteneur PostgreSQL, réseau | SLA, continuité de service |

---  

## 8. Contraintes et environnement  

| Domaine | Contraintes |
|---|---|
| **Organisationnel** | Le projet doit être livré **dans 6 mois** (début 2026‑05 → fin 2026‑10). |
| **Réglementaire** | - Conformité RGPD (données à caractère personnel) <br> - Référentiel RGS (sécurité des services) <br> - Respect des normes comptables publiques (PCG) |
| **Technique** | - Docker ≥ 20.10, Docker‑Compose ≥ 2.20 <br> - PostgreSQL 13+ (conteneur `db`) <br> - Python 3.11.10, dépendances listées dans `pyproject.toml` <br> - Dagster 1.8+, Dagster‑WebServer <br> - Volume persistant `./db/data` pour la BD |
| **Performance** | - Temps de cycle complet ≤ 10 min (lot complet) <br> - Mémoire max du conteneur `app` ≤ 2 GiB |
| **Sécurité** | - Accès réseau limité aux ports 4400 (Dagster) et 5432 (PostgreSQL) <br> - Secrets gérés via `.env` (non versionnés) |
| **Budgétaire** | - Coût maximal d’infrastructure (cloud ou on‑prem) ≤ 15 k €/an <br> - Licence logicielle uniquement open‑source (pas de coût additionnel) |

---  

## 9. Critères de sélection et pondération (marchés publics)

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---|---|---|---|
| **Valeur fonctionnelle** | Couverture des fonctions de service (FS‑01 à FS‑08) | 40 % | 0‑5 pts par fonction (max 40) |
| **Qualité technique** | Architecture (Docker, Dagster), conformité aux standards (PEP8, SQL) | 20 % | 0‑5 pts |
| **Coût total** | Prix global (licences, hébergement, support) | 15 % | Inverse du coût (plus bas = meilleur score) |
| **Délais** | Planning de mise en production | 10 % | 0‑5 pts (respect du planning) |
| **Sécurité & conformité** | RGPD, RGS, auditabilité | 10 % | 0‑5 pts (preuves documentées) |
| **Innovation / valeur ajoutée** | Fonctionnalités optionnelles (vues Superset, monitoring avancé) | 5 % | 0‑5 pts |

*Score maximal = 100 pts.*  

---  

## 10. Glossaire & acronymes  

| Acronyme / Terme | Définition |
|---|---|
| **AFINOPE** | Application Financière des Opérateurs de l’État |
| **CSV** | Comma‑Separated Values – format de fichier texte |
| **Dagster** | Plateforme d’orchestration de pipelines de données |
| **RGPD** | Règlement Général sur la Protection des Données (UE) |
| **RGS** | Référentiel Général de Sécurité (France) |
| **PCG** | Plan Comptable Général |
| **FP** | Fonction Principale (indispensable à l’existence du produit) |
| **FC** | Fonction Contraint (imposée par le contexte) |
| **B‑xx** | Identifiant du besoin (ex : B‑01) |
| **FS‑xx** | Identifiant de la fonction de service (ex : FS‑01) |
| **FP‑xx‑xx** | Besoin partiel (niveau sous‑système) |
| **SQL** | Structured Query Language |
| **Superset** | Outil de visualisation et tableau de bord open‑source |
| **Docker‑Compose** | Outil de définition et exécution d’applications multi‑conteneurs |
| **CI/CD** | Intégration Continue / Déploiement Continu |
| **PVA** | Procès‑Verbal d’Acceptation |
| **RDS** | Référentiel de données (ensemble des tables du projet) |

---  

## Annexes  

| Annexe | Contenu |
|---|---|
| **A** | Diagramme de flux fonctionnel (extrait du fichier `analyse/flux.txt`) |
| **B** | Modèle de données (schémas `sql/00_referentiel/*.sql`) |
| **C** | Exemple de fichier `config.json` (chemins, logs) |
| **D** | Matrice de traçabilité exigences ↔ fonctions de service |
| **E** | Plan de tests fonctionnels (ingestion, validation, persistance) |
| **F** | Liste des risques et mesures d’atténuation (ex : indisponibilité DB) |

---  

*Fin du Cahier des Charges Fonctionnel – Projet **afinope**.*  