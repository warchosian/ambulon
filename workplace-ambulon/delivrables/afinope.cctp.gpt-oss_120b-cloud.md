# Cahier des Clauses Techniques Particulières (CCTP)  
## Projet **AFINOPE** – Application financière des opérateurs de l’État  

> **Version** : 1.0 – Date : 28 avril 2026  
> **Références réglementaires** : Code de la commande publique, RGS (niveaux basique & renforcé), RGPD, Référentiel SSI de l’ANSSI, RGI, RGI‑RGAA, ISO / IEC 27001, ISO / IEC 25010, ISO 9001.  

---

## Table des matières  

1. [Objet du marché](#1-objet-du-marché)  
2. [Description technique détaillée](#2-description-technique-détaillée)  
3. [Architecture et conception](#3-architecture-et-conception)  
4. [Exigences de sécurité (RGS, ANSSI)](#4-exigences-de-sécurité-rgs-ansi)  
5. [Interfaces et intégrations](#5-interfaces-et-intégrations)  
6. [Environnements et infrastructure](#6-environnements-et-infrastructure)  
7. [Qualité et conformité](#7-qualité-et-conformité)  
8. [Documentation et formation](#8-documentation-et-formation)  
9. [Tests et recette](#9-tests-et-reçette)  
10. [Maintenance et support](#10-maintenance-et-support)  
11. [Livrables et planning](#11-livrables-et-planning)  
12. [Contraintes légales et réglementaires](#12-contraintes-légales-et-réglementaires)  
13. [Critères de sélection des offres](#13-critères-de-sélection-des-offres)  
14. [Annexes contractuelles](#14-annexes-contractuelles)  

---  

## 1. Objet du marché  

| N° | Description | Référence fonctionnelle (CCF) |
|----|------------|------------------------------|
| 1.1 | Fourniture d’une solution logicielle complète d’ingestion, de transformation, de persistance et de visualisation des données financières des opérateurs de l’État (référentiel : ORGANISME, STRUCTURE, NOMENC, …) | CCF‑FIN‑01 – Gestion des flux financiers |
| 1.2 | Mise à disposition du code source, des conteneurs d’exécution et des scripts d’initialisation de la base de données | CCF‑FIN‑02 – Livraison du livrable technique |
| 1.3 | Services d’exploitation, de maintenance corrective & évolutive, et de support technique pendant une période minimale de 24 mois à compter de la date de réception définitive | CCF‑FIN‑03 – Support & maintenance |
| 1.4 | Garantie de conformité aux exigences de la commande publique (RGS, RGPD, RGI) | CCF‑FIN‑04 – Conformité réglementaire |

**Périmètre** : le prestataire devra livrer une solution fonctionnelle, déployable dans un environnement Docker‑Compose, incluant :  

* un serveur PostgreSQL 5.0 ou supérieur ;  
* une application Python 3.11 (modules Dagster, Pandas, SQLAlchemy, etc.) ;  
* un serveur web Dagster (port 4400) exposant les pipelines d’alimentation ;  
* les scripts d’initialisation des schémas SQL fournis dans le répertoire `sql/` ;  
* les tableaux de bord Superset (optionnels) basés sur les vues `tdb_*` ;  
* les scripts de migration et de nettoyage des données (ex. `known_issue.txt`).  

---  

## 2. Description technique détaillée  

### 2.1 Spécifications fonctionnelles minimales (obligatoires)  

| Référence | Fonctionnalité | Description détaillée |
|----------|----------------|----------------------|
| F‑01 | **Ingestion de fichiers CSV** | Le composant `GestionnaireFichiersCSV` doit scanner le répertoire d’entrée (`flux.entree`) chaque 5 minutes, ne retenir que les fichiers terminés avec l’extension `.csv`, les valider (format, séparateur « ; », présence des colonnes obligatoires) et les déplacer vers le répertoire `flux.sortie` ou `flux.erreur` selon le résultat. |
| F‑02 | **Transformation & normalisation** | Le module `transformateur.py` doit appliquer les fonctions définies dans `helper.py` (ex. `na_to_empty`, `int_to_bool`, `str_to_float`) à chaque colonne, garantir que les champs `bigint` ne contiennent aucun préfixe « '' » (cf. `known_issue.txt`). |
| F‑03 | **Persistance en base PostgreSQL** | `GestionnaireBaseDonnees` doit créer les tables référentielles (scripts `00_*.sql`) et exécutoires (`01_*.sql`) via SQLAlchemy, puis charger chaque DataFrame dans la table cible avec `to_sql(..., if_exists='append')`. En cas d’erreur, le processus doit être journalisé et le fichier déplacé vers `flux.erreur`. |
| F‑04 | **Orchestration des pipelines** | Le pipeline Dagster (`graphe_alimentation.py`) doit inclure les étapes : `ListerFichiers → Valider → Transformer → Charger → GénérerVueTDB`. Chaque étape doit être atomicité‑transactionnelle et déclencher un rollback en cas d’échec. |
| F‑05 | **Exposition d’une API de suivi** | Le serveur Dagster doit fournir, via son UI, le suivi temps réel de chaque exécution (statut, logs, durée). Une API REST minimale (`/health`, `/metrics`) doit être disponible en JSON. |
| F‑06 | **Reporting** | Les vues SQL `tdb_*` (ex. `tdb_view.sql`) doivent être matérialisées chaque nuit (cron 02:00) afin d’alimenter les tableaux de bord Superset. |
| F‑07 | **Gestion des droits** | L’accès à l’UI Dagster et aux bases de données doit être contrôlé par authentification forte (login/password stockés dans le secret manager du conteneur). |
| F‑08 | **Conformité RGPD** | Tout champ contenant des données à caractère personnel (ex. `NOMENC.libelleTiers`) doit être chiffré en repos (AES‑256) et les accès journalisés. |

### 2.2 Spécifications techniques obligatoires  

| Référence | Exigence | Niveau de contrainte |
|-----------|----------|----------------------|
| T‑01 | **Conteneurisation** – Docker ≥ 24.0, images officielles (`python:3.11.10`, `postgres:15-alpine`). | Obligatoire |
| T‑02 | **Gestion des dépendances** – Poetry 1.6 ou supérieur, verrouillage complet (`poetry.lock`). | Obligatoire |
| T‑03 | **Base de données** – PostgreSQL en mode *replication* (1 maître + 1 standby) avec WAL‑archiving. | Obligatoire |
| T‑04 | **Temps de traitement** – Chaque fichier CSV (max 10 Mo) doit être entièrement traité en ≤ 30 s. | Obligatoire |
| T‑05 | **Disponibilité** – Le service doit garantir 99,9 % de disponibilité mensuelle, hors fenêtres de maintenance planifiées (max 4 h/mois). | Obligatoire |
| T‑06 | **Traçabilité** – Tous les traitements doivent être journalisés dans la table `audit_log` (date‑heure, utilisateur, fichier, étape, statut, message). | Obligatoire |
| T‑07 | **Sécurité du réseau** – Tous les flux (client‑app, app‑db) doivent être chiffrés TLS 1.3. | Obligatoire |
| T‑08 | **Sauvegarde** – Backup complet de la base toutes les 24 h, rétention 30 jours, restauration testée mensuellement (RTO ≤ 2 h, RPO ≤ 4 h). | Obligatoire |
| T‑09 | **Conformité RGS** – Niveau **Renforcé** pour les environnements de production. | Obligatoire |
| T‑10 | **Accessibilité** – L’interface web Dagster doit être conforme au RGAA niveau AA. | Obligatoire |

### 2.3 Spécifications techniques souhaitées (optionnelles)  

| Référence | Fonctionnalité | Gains attendus |
|-----------|----------------|----------------|
| S‑01 | **Authentification SSO** (OpenID Connect) | Simplification de la gestion des comptes utilisateurs. |
| S‑02 | **Déploiement sur Cloud souverain** (ex. OVHcloud) | Respect de la souveraineté des données. |
| S‑03 | **Mécanisme de déduplication** des fichiers déjà traités (hash SHA‑256). | Optimisation du débit de traitement. |
| S‑04 | **Alerting** via Prometheus + Alertmanager (mail, Slack). | Réduction du MTTR. |

### 2.4 Spécifications techniques optionnelles (facultatives)  

| Référence | Fonctionnalité | Conditions d’acceptation |
|-----------|----------------|--------------------------|
| O‑01 | **Intégration d’un moteur de règles métier** (Drools) | Livraison d’une preuve de concept fonctionnelle. |
| O‑02 | **Export des résultats au format JSON‑API** | Documentation d’une API REST supplémentaire. |

---  

## 3. Architecture et conception  

### 3.1 Diagramme d’architecture (description textuelle)  

```
+-------------------+       +-------------------+       +-------------------+
|  Client Web (UI) | <---> |  Dagster WebSrv   | <---> |  PostgreSQL DB    |
|  (HTTPS 4400)     |       |  (Port 4400)      |       |  (Port 5432)      |
+-------------------+       +-------------------+       +-------------------+
        ^                         ^                           ^
        |                         |                           |
        | Docker‑Compose          | Docker‑Compose            | Docker‑Compose
        |                         |                           |
+-------------------+       +-------------------+       +-------------------+
|  Conteneur App   |       |  Conteneur DB     |       |  Conteneur Superset|
|  (Python 3.11)   |       |  (Postgres)      |       |  (optionnel)       |
+-------------------+       +-------------------+       +-------------------+
        ^                         ^                           ^
        |                         |                           |
    Volume “/data”            Volume “/var/lib/postgresql”   Volume “/superset”
```

### 3.2 Contraintes architecturales imposées  

| Contraintes | Détails |
|------------|---------|
| **Isolation** | Chaque composant s’exécute dans son propre conteneur, aucune exécution en mode “host”. |
| **Portabilité** | Les images Docker doivent être compatibles avec Docker‑Compose v2.0 et Kubernetes v1.27 (option de migration). |
| **Normes** | Respect des standards ISO / IEC 27001 (Gestion des actifs), ISO / IEC 25010 (Qualité logiciel), W3C HTML 5 (UI). |
| **Interopérabilité (RGI)** | Les schémas SQL doivent respecter le modèle de données RGI – les noms de tables et colonnes sont en majuscules entre guillemets comme dans les scripts fournis. |
| **Patterns** | Architecture “Micro‑services légers” : API Gateway (Dagster), Service de persistance (PostgreSQL), Service de traitement (Python). |
| **Frameworks autorisés** | Dagster 1.8+, SQLAlchemy 2.0+, Pandas 2.1+, Poetry 1.6+. Aucun autre framework ne doit être introduit sans validation préalable. |

---  

## 4. Exigences de sécurité (RGS, ANSSI)

| Référence | Exigence | Niveau RGS | Modalité de vérification |
|-----------|----------|------------|--------------------------|
| **SEC‑01** | Authentification forte (login + mot de passe, stockage haché bcrypt, rotation tous les 90 jours) | Renforcé | Audit du fichier `users.yml` et test d’intrusion interne. |
| **SEC‑02** | Chiffrement TLS 1.3 sur tous les canaux (client‑app, app‑db) | Renforcé | Scan SSL Labs, vérification du certificat auto‑signé ou fourni. |
| **SEC‑03** | Chiffrement des données sensibles en repos (AES‑256) | Renforcé | Inspection du script `encrypt_columns.sql` et tests de déchiffrement. |
| **SEC‑04** | Gestion des comptes à privilèges limités (principle of least privilege) | Renforcé | Revue des rôles PostgreSQL (`read_only`, `etl_user`). |
| **SEC‑05** | Traçabilité & journalisation (audit_log) | Basique | Vérification de la présence et du format des logs dans la table `audit_log`. |
| **SEC‑06** | Gestion des vulnérabilités (ANSSI – CVE) | Basique | Rapport mensuel de `snyk` ou `dependabot`. |
| **SEC‑07** | Conformité RGPD – Droit d’accès, de rectification, d’effacement | Basique | Documentation du registre des traitements et procédure de purge. |
| **SEC‑08** | Sécurité du conteneur (image non root, user non‑privileged, scan Trivy) | Basique | Rapport de scan d’image Docker. |
| **SEC‑09** | PRA/PCA – Plan de reprise d’activité et continuité d’activité | Renforcé | Test de bascule sur le standby PostgreSQL, validation du RTO ≤ 2 h. |

**Obligation de résultat** : le système **doit** garantir une disponibilité de 99,9 % et une intégrité des données conforme aux exigences ci‑dessus.  

**Obligation de moyen** : le prestataire **doit** mettre en œuvre les processus de surveillance 24 / 7, les mises à jour de sécurité mensuelles, et la documentation des incidents.

---  

## 5. Interfaces et intégrations  

| Interface | Type | Protocole / Format | Système cible | Critères de recette |
|----------|------|--------------------|---------------|---------------------|
| I‑01 | **Entrée CSV** | Fichiers `.csv` (UTF‑8, séparateur `;`) | Répertoire `flux.entree` (monté en volume) | Tous les fichiers doivent être lisibles, validation du schéma (nombre de colonnes, types). |
| I‑02 | **Base de données** | PostgreSQL 15, port 5432, SSL | Conteneur `db` | Connexion via `psycopg2` réussie, exécution des scripts `00_*.sql`. |
| I‑03 | **API Dagster** | HTTP / REST, JSON | Clients internes (ex. outil de pilotage) | Réponse `200` pour `/health`, conformité du schéma OpenAPI fourni. |
| I‑04 | **Superset (optionnel)** | HTTP / REST, JSON | Tableau de bord Superset | Les vues `tdb_*` sont visibles, rafraîchissement nocturne sans erreur. |
| I‑05 | **Alerting** | SMTP / Slack webhook | Plateforme de monitoring | Envoi d’alerte en cas d’échec de traitement (ex. `flux.erreur`). |
| I‑06 | **Export RGPD** | CSV, JSON | Autorité de contrôle | Extraction d’un jeu de données à la demande, conformité au droit d’accès. |

---  

## 6. Environnements et infrastructure  

| Environnement | Description | Ressources allouées | Accès réseau |
|--------------|-------------|----------------------|--------------|
| **DEV** | Docker‑Compose local, données de test anonymisées. | 1 CPU, 2 Go RAM, 10 Go disque. | Accès depuis le réseau interne du prestataire uniquement. |
| **RECETTE** | Réplication de la production, jeux de données réelles masquées. | 2 CPU, 4 Go RAM, 20 Go disque. | Accès VPN dédié, authentification 2FA. |
| **PRODUCTION** | Cluster Docker‑Swarm ou Kubernetes, haute disponibilité. | 4 CPU, 8 Go RAM, 100 Go disque (RAID 1). | Accès via firewall d’entreprise, ports 443 (TLS) & 4400 (Dagster). |
| **PRA** | Site de secours (datacenter secondaire) avec réplication PostgreSQL. | Identique à production. | Basculement automatisé via `pg_auto_failover`. |

**Contraintes d’hébergement** : le serveur doit être installé sur une infrastructure **souveraine française** (ex. datacenter certifié ISO 27001, localisation : France métropolitaine).  

**Infrastructure réseau** :  
* Segmentation en VLAN : `VLAN_APP`, `VLAN_DB`, `VLAN_DMZ`.  
* Filtrage de trafic autorisé uniquement entre VLANs selon la matrice ci‑dessus.  

---  

## 7. Qualité et conformité  

| Référence | Exigence | Méthode de contrôle |
|-----------|----------|---------------------|
| Q‑01 | **Conformité ISO 25010** – critères de performance, fiabilité, maintenabilité, sécurité. | Revue de code automatisée (`pylint`, `bandit`) + audit externe. |
| Q‑02 | **Couverture de tests unitaires** ≥ 80 % | Rapport `coverage.xml`. |
| Q‑03 | **Tests d’intégration** – exécution du pipeline complet sur jeu de données de 5 Mo. | Validation du temps de traitement ≤ 30 s (T‑04). |
| Q‑04 | **Tests de charge** – 100 fichiers simultanés (10 Mo chacun). | Temps moyen ≤ 2 min, taux d’erreur = 0 %. |
| Q‑05 | **Tests de sécurité** – scan de vulnérabilités (OWASP Top 10) | Rapport Trivy + test d’intrusion interne. |
| Q‑06 | **Documentation** – livrable `DAT` (Dossier d’Architecture Technique) complet, versionné. | Vérification de la présence de tous les chapitres (architecture, sécurité, exploitation). |
| Q‑07 | **Accessibilité RGAA** – niveau AA sur l’UI Dagster. | Audit par un organisme accrédité. |

---  

## 8. Documentation et formation  

| Livrable | Format | Contenu | Responsable |
|----------|--------|----------|-------------|
| **DOC‑01** *Dossier d’Architecture Technique (DAT)* | PDF + Markdown | Diagrammes, description des flux, matrices de sécurité, plan de reprise. | Prestataire |
| **DOC‑02** *Manuel d’Exploitation* | PDF | Procédures d’installation, de mise à jour, de sauvegarde/restauration, gestion des incidents. | Prestataire |
| **DOC‑03** *Guide Utilisateur* | PDF | Navigation Dagster, suivi des pipelines, export de données. | Prestataire |
| **DOC‑04** *Guide Administrateur* | PDF | Gestion des comptes, configuration TLS, paramétrage des alertes. | Prestataire |
| **FOR‑01** *Formation* | 2 sessions de 4 h (présentiel ou visio) | Formation des équipes DSI (exploitation) et métiers (pilotage). | Formateur désigné par le prestataire |
| **FOR‑02** *Support de formation* | Slides + exercices | Supports remis aux participants. | Prestataire |

---  

## 9. Tests et recette  

### 9.1 Stratégie de recette  

| Phase | Objectif | Livrable | Critère d’acceptation |
|-------|----------|----------|----------------------|
| **R‑01** *Tests unitaires* | Vérifier le bon fonctionnement de chaque fonction/module. | Rapport `coverage.xml` | Couverture ≥ 80 % et aucun test échoué. |
| **R‑02** *Tests d’intégration* | Exécuter le pipeline complet sur jeu de données de référence (10 fichiers). | Journal d’exécution (`audit_log`). | Tous les fichiers traités, temps moyen ≤ 30 s, aucune erreur. |
| **R‑03** *Tests de charge* | Simuler le pic de 100 fichiers simultanés. | Rapport de charge (`k6`, `locust`). | Taux d’erreur = 0 %, latence ≤ 2 min. |
| **R‑04** *Tests de sécurité* | Scanner les vulnérabilités et valider la conformité RGS. | Rapport `Trivy`, `SSL Labs`. | Aucun CVE critique, TLS 1.3 validé, niveau RGS = Renforcé. |
| **R‑05** *Tests d’accessibilité* | Vérifier la conformité RGAA niveau AA. | Rapport d’audit RGAA. | Niveau AA atteint. |
| **R‑06** *Recette fonctionnelle* | Validation par le maître d’ouvrage (MOA). | Procès‑verbal de réception. | Toutes les exigences fonctionnelles (F‑01 à F‑08) validées. |

### 9.2 Gestion des anomalies  

* Chaque anomalie détectée sera enregistrée dans le ticketing interne (Jira/Redmine).  
* Le prestataire devra corriger les anomalies de **niveau critique** sous **48 h** et les **niveau majeur** sous **5 jours ouvrés**.  
* La réception définitive ne pourra intervenir qu’après résolution de toutes les anomalies de niveau **critique** ou **majeur**.

---  

## 10. Maintenance et support  

| Niveau | Description | Délais d’intervention (GTR) | Délais de correction (GTD) | Disponibilité |
|--------|-------------|-----------------------------|----------------------------|---------------|
| **S‑01** *Support fonctionnel* | Assistance sur l’usage des pipelines, extraction de rapports. | 4 h (ouverture de ticket) | 2 j ouvrés | 8 h/24 h |
| **S‑02** *Support technique* | Incident d’infrastructure (Docker, DB, réseau). | 2 h | 1 j ouvré | 24 h/7 j |
| **S‑03** *Maintenance corrective* | Corrections de bugs (code source). | – | 3 j ouvrés | 24 h/7 j |
| **S‑04** *Maintenance évolutive* | Ajout de nouvelles tables, évolution du pipeline. | – | Selon cahier des charges (hors période de garantie). | – |
| **S‑05** *Garantie* | Période de garantie de **24 mois** à compter de la réception définitive. | – | – | – |

**SLA** : le prestataire **doit** garantir un taux de disponibilité du service de **99,9 %** sur l’année civile, hors fenêtres de maintenance planifiées (max 4 h/mois).  

**Pénalités** : en cas de non‑respect du taux de disponibilité, une pénalité de **0,5 % du montant HT du lot** par point de pourcentage manquant sera appliquée, plafonnée à **10 %** du lot.

---  

## 11. Livrables et planning  

### 11.1 Livrables attendus  

| N° | Désignation | Format | Date de remise prévue |
|----|--------------|--------|-----------------------|
| L‑01 | Code source complet (repo Git) | Git (branch `release`) | J‑30 |
| L‑02 | Images Docker (registry interne) | Docker‑hub privé | J‑30 |
| L‑03 | Scripts d’initialisation DB (`initdb.sh`) | Bash | J‑30 |
| L‑04 | Dossier d’Architecture Technique (DAT) | PDF + Markdown | J‑45 |
| L‑05 | Manuel d’Exploitation & Guide Administrateur | PDF | J‑45 |
| L‑06 | Rapport de tests (unitaires, intégration, charge, sécurité) | PDF | J‑45 |
| L‑07 | Procédures de sauvegarde / PRA / PCA | PDF | J‑45 |
| L‑08 | Tableau de bord Superset (option) | Export JSON | J‑60 |
| L‑09 | Procès‑verbal de réception (PR) | PDF | J‑70 |
| L‑10 | Facture finale (conforme au CCTP) | PDF | J‑75 |

### 11.2 Planning (jalons)  

| Jalons | Durée | Date cible | Livrable associé |
|--------|-------|-----------|------------------|
| **M‑01** | Analyse fonctionnelle & validation du CCF | 2026‑05‑15 | CCF signé |
| **M‑02** | Architecture détaillée & choix technologiques | 2026‑06‑01 | DAT v1 |
| **M‑03** | Développement du pipeline d’ingestion | 2026‑07‑15 | Code + tests unitaires |
| **M‑04** | Intégration DB & scripts d’init | 2026‑08‑01 | Scripts DB |
| **M‑05** | Tests d’intégration & recette interne | 2026‑08‑15 | Rapport de tests |
| **M‑06** | Mise en place de l’environnement de pré‑production | 2026‑09‑01 | Docker‑Compose prod |
| **M‑07** | Recette fonctionnelle avec le MOA | 2026‑09‑15 | PR signé |
| **M‑08** | Livraison finale & formation | 2026‑09‑30 | Tous livrables + formation |
| **M‑09** | Garantie & support (début) | 2026‑10‑01 | – |

> **Note** : Tout retard de plus de 5 jours ouvrés sur un jalon entraînera l’application des pénalités de retard prévues à la section 11.3.  

### 11.3 Pénalités de retard  

| Retard | Pénalité |
|--------|----------|
| 1–5 jours | 0,1 % du montant total HT du lot par jour de retard. |
| 6–15 jours | 0,2 % du montant total HT du lot par jour de retard. |
| > 15 jours | 0,5 % du montant total HT du lot par jour de retard (plafond 10 %). |

---  

## 12. Contraintes légales et réglementaires  

| Aspect | Exigence | Référence |
|--------|----------|-----------|
| **Propriété intellectuelle** | Le code source, les scripts et la documentation seront cédés en pleine propriété à l’acheteur, sous licence **GPL‑3.0 ou propre** (licence à définir). | Article L. 213‑1 du Code de la commande publique |
| **Logiciels tiers** | Tous les composants listés dans `pyproject.toml` (Dagster, Pandas, SQLAlchemy, etc.) sont sous licences compatibles (BSD, Apache‑2.0). Le prestataire devra fournir les licences et les mentions légales. | Annexes A – Licences |
| **Protection des données** | Conformité RGPD : registre des traitements, DPIA, droit à l’oubli, chiffrement des données personnelles. | Article RGPD 5‑1, 32 |
| **Archivage** | Les logs (`audit_log`) et les rapports de traitement doivent être archivés 10 ans, en format non propriétaire (CSV, JSON). | Référentiel RGI‑Archivage |
| **Souveraineté des données** | Hébergement sur territoire français, serveur certifié ISO 27001. | Décret 2021‑1234 |
| **Accessibilité** | Interface Dagster conforme au RGAA niveau AA. | Référentiel RGAA v4.1 |
| **Responsabilité** | Le prestataire garantit l’absence de contrefaçon et la conformité aux exigences de sécurité. | Article L. 213‑2 du Code de la commande publique |

---  

## 13. Critères de sélection des offres  

| Critère | Pondération | Barème (sur 10) | Description |
|---------|-------------|-----------------|-------------|
| **C‑01** *Conformité technique* (respect des exigences T‑01 à T‑10) | 40 % | 0 = non‑conforme, 5 = partiellement conforme, 10 = conforme intégralement. |
| **C‑02** *Qualité de la solution* (architecture, maintenabilité, tests) | 25 % | Analyse du DAT, couverture de tests, respect ISO 25010. |
| **C‑03** *Prix* (coût total du lot) | 20 % | Evaluation du prix global (HT). |
| **C‑04** *Organisation du support & SLA* | 10 % | Niveau de service proposé, disponibilité, pénalités. |
| **C‑05** *Valeur ajoutée* (options S‑01 à O‑02) | 5 % | Présence d’options souhaitées ou optionnelles. |

**Notation** : chaque critère sera noté sur 10, puis multiplié par la pondération correspondante. L’offre la mieux notée sera retenue, sous réserve du respect des exigences obligatoires.  

---  

## 14. Annexes contractuelles  

### 14.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **AFINOPE** | Application financière des opérateurs de l’État (objet du marché). |
| **Dagster** | Orchestrateur de pipelines de données, utilisé pour le traitement des flux. |
| **RGS** | Référentiel Général de Sécurité. |
| **RGPD** | Règlement Général sur la Protection des Données. |
| **RGAA** | Référentiel Général d’Amélioration de l’Accessibilité. |
| **RGS‑Basique / Renforcé** | Niveau de sécurité défini par l’ANSSI. |
| **PRA / PCA** | Plan de Reprise d’Activité / Plan de Continuité d’Activité. |
| **SLA** | Service Level Agreement – niveau de service contractuel. |
| **GTR / GTD** | Garantie de Temps de Réponse / Garantie de Temps de Dépannage. |
| **DAT** | Dossier d’Architecture Technique. |
| **CR** | Compte Rendu – tableau de bord d’exécution. |

### 14.2 Références normatives  

| Norme / Référentiel | Version | Domaine d’application |
|---------------------|----------|----------------------|
| ISO / IEC 27001 | 2022 | Sécurité de l’information |
| ISO / IEC 25010 | 2011 | Qualité du logiciel |
| ISO 9001 | 2015 | Management de la qualité |
| RGS (ANSSI) | 2023 | Sécurité des systèmes d’information de l’État |
| RGAA | v4.1 | Accessibilité web |
| RGI | 2022 | Interopérabilité des systèmes d’information de l’État |
| GDPR | 2016/679 | Protection des données personnelles |

### 14.3 Modèles de documents à remplir par le candidat  

| Document | Objectif |
|----------|-----------|
| **Formulaire de Déclaration de Conformité RGS** | Attester le niveau de sécurité appliqué. |
| **Plan de Gestion des Risques** | Identifier les risques et les mesures d’atténuation. |
| **DPIA (Data Protection Impact Assessment)** | Analyse d’impact sur la protection des données. |
| **Calendrier de Livraison** | Détail des jalons et des livrables. |
| **Proposition Financière détaillée** | Décomposition du prix (licences, développements, support). |

---  

### Signature  

*Le présent CCTP constitue le cadre contractuel du marché public AFINOPE. Tout manquement aux exigences ci‑dessus pourra entraîner des sanctions prévues par le Code de la commande publique.*  