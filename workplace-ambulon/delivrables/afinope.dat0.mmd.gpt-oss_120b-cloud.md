# Dossier d’Architecture Technique (DAT) – **Afinope**  

> **Version** : 1.0 – 27 avril 2026  
> **Auteur** : Équipe Architecture – GTI  

---

## 1. Introduction et objectifs  

### 1.1 Vue d’ensemble fonctionnelle (C4 – Niveau 1)  

```mermaid
graph LR;
    subgraph Utilisateurs;
        UA[Analystes financiers] 
        UB[Administrateurs système] 
        UC[Responsable sécurité] 
    end;
    subgraph Système Afinope;
        A1[Dagster orchestrateur] 
        A2[Web UI (Dagster Webserver)] 
        A3[Modules d’ingestion CSV] 
        A4[Base de données PostgreSQL] 
        A5[Superset dashboards] 
    end;
    subgraph Externes;
        E1[Sources CSV (ex‑fileshare)] 
        E2[Service de sauvegarde (B3/Outscale/GC)] 
    end;
    UA -->|consultation| A5;
    UA -->|déclenchement manuel| A2;
    UB -->|déploiement & monitoring| A1;
    UC -->|audit & conformité| A4;
    A3 -->|lecture/écriture| A4;
    A2 -->|expose API GraphQL| A1;
    A1 -->|planifie| A3;
    A1 -->|expose métriques| Prometheus;
    A4 -->|dump| E2;
    E1 -->|dépose CSV| A3
```

*Le système Afinope orchestre la collecte, la transformation et le stockage de flux financiers (CSV) afin d’alimenter des tableaux de bord décisionnels.*  

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif | Pourquoi | Indicateur cible |
|---|-----------|-----------|-----------------|
| Q‑1 | **Performance** – traitement d’un lot CSV ≤ 30 s (≈ 10 Mo) | Respect des délais de clôture budgétaire | Temps moyen de traitement < 30 s |
| Q‑2 | **Sécurité** – confidentialité des données financières | Conformité RGPD & exigences DSI | Aucun incident de fuite ; chiffrement AES‑256 des backups |
| Q‑3 | **Maintenabilité** – code modulaire & testable | Réduction du coût de l’évolution fonctionnelle | Couverture de tests unitaires ≥ 80 % |
| Q‑4 | **Accessibilité** – UI disponible 24 h/24, 7 j/7 | Garantir l’accès aux décideurs | Disponibilité du service ≥ 99,5 % |
| Q‑5 | **Opérabilité** – supervision complète | Détection précoce des incidents | MTTR < 15 min ; alertes via AlertManager |

---

## 2. Parties prenantes  

| Rôle | Contact (exemple) | Attentes principales |
|------|-------------------|----------------------|
| **Maître d’Ouvrage (MOA)** | M. Dupont – Direction Financière | Fiabilité des données, reporting à jour |
| **Product Owner** | S. Leroy – Responsable Data | Flexibilité du pipeline, livrables rapides |
| **Développeurs** | Équipe Afinope (Python) | Environnement de dev stable, CI/CD automatisé |
| **Ops / SRE** | J. Martin – Plateforme Cloud | Déploiement automatisé, haute disponibilité |
| **RSSI** | C. Bertin – Sécurité | Conformité aux normes DSI, traçabilité |
| **Utilisateurs finaux** | Analystes comptables | Accès aux tableaux de bord, temps de réponse rapide |
| **Gestionnaire de sauvegarde** | Equipe GTI – Infra | Sauvegarde fiable, restauration testée |

---

## 3. Contraintes  

### 3.1 Contraintes d’architecture  

| Type | Description |
|------|-------------|
| **Techniques** | Python 3.11, PostgreSQL 13+, Docker ≥ 20.10, Dagster 1.8, Superset ≥ 2.0 |
| **Organisationnelles** | Déploiement sur le cloud interne **ECO4** (OpenStack), CI/CD via GitLab Runner, gestion des secrets via `.env` (Vault) |
| **Réglementaires** | RGPD, ISO 27001, exigences DINS (décret 2022‑123) |
| **Performance** | Traitement de 10 000 lignes CSV ≤ 30 s, requêtes DB ≤ 200 ms pour les vues de tableau de bord |
| **Interopérabilité** | Interfaces CSV (UTF‑8, séparateur “;”), API GraphQL Dagster, connexion ODBC/JDBC pour Superset |

### 3.2 Contraintes de sécurité – modèle **D‑I‑C‑T**  

| Dimension | Exigence | Mesure appliquée |
|-----------|----------|------------------|
| **Disponibilité** | 99,5 % uptime | Redémarrage automatique (Docker `restart: unless‑stopped`), Nginx load‑balancés, sauvegarde périodique |
| **Intégrité** | Garantie d’absence de corruption | Transactions ACID PostgreSQL, validation du schéma CSV (pandas + contraintes SQL) |
| **Confidentialité** | Protection des données sensibles | Chiffrement AES‑256 des dumps, variables d’environnement protégées, accès réseau limité (VPC) |
| **Traçabilité** | Audit complet des actions | Logs structurés (JSON) via `dagster` + `Portainer`, métriques Prometheus, historisation des migrations DB |

---

## 4. Contexte et périmètre  

### 4.1 Contexte métier  

Afinope est le moteur de **transformation et de consolidation** des flux financiers provenant de multiples entités publiques (organismes, structures, tiers).  
Il produit les tableaux de bord **Superset** utilisés par les analystes pour :  

* suivre les engagements budgétaires,  
* piloter l’exécution des budgets (ex : ABE, BAL, BIL),  
* préparer les états d’exécution (DESE, DESP, EFP).  

### 4.2 Contexte technique  

| Interface externe | Protocole / Format | Fréquence | Type |
|-------------------|--------------------|-----------|------|
| **Sources CSV** | fichiers sur partage réseau (SMB) | quotidien (batch) | Entrée |
| **Base de données** | PostgreSQL (SQL) | en temps réel (transaction) | Persistance |
| **Superset** | HTTP/HTTPS (REST) | lecture | Visualisation |
| **Sauvegarde** | Scripts internes (dump + AES‑256) | quotidien (nightly) | Sortie |
| **CI/CD** | GitLab CI (Docker) | à chaque push | Déploiement |

---

## 5. Stratégie de solution  

### 5.1 Décisions architecturales majeures  

| Décision | Raison | Impact |
|----------|--------|--------|
| **Micro‑services légers (Docker)** | Isolation des dépendances, scalabilité | Déploiement simple, mise à jour indépendante |
| **Orchestration Dagster** | Gestion de pipelines ETL avec traçabilité | Reprise sur échec, visibilité des runs |
| **SQLAlchemy + Alembic** | ORM + migrations versionnées | Maintenabilité du schéma DB |
| **Superset** comme BI front‑end | Outil standard interne, intégration PostgreSQL | Réduction du coût de développement UI |
| **Nginx load‑balancer** | Point d’entrée unique, TLS termination | Sécurité & haute disponibilité |
| **CI/CD GitLab + Poetry** | Gestion des dépendances reproducible | Déploiement automatisé, reproducibilité |

### 5.2 Environnement technologique  

| Couche | Technologie |
|--------|-------------|
| **Langage** | Python 3.11 (type hints, async possible) |
| **Framework** | Dagster (pipeline), FastAPI (future API) |
| **Base de données** | PostgreSQL 13 (tables ≈ 30, vues matérialisées) |
| **Front‑end** | Superset (dashboards), Dagster Web UI |
| **Conteneurisation** | Docker ≥ 20.10, docker‑compose |
| **Infrastructure** | OpenStack (tenant `pnm3`) – cloud interne ECO4 |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`), Poetry (`pyproject.toml`) |
| **Supervision** | Prometheus / Grafana / Loki / AlertManager, Portainer |
| **Sauvegarde** | Scripts de dump + chiffrement AES‑256, stockage B3, Outscale SecNumCloud, Google Cloud |

### 5.3 Forge logicielle (pipeline de construction)  

1. **Pull** du dépôt GitLab → déclenchement du runner.  
2. **Poetry install** (environnement virtuel *in‑project*).  
3. **Tests unitaires** (`pytest` + coverage).  
4. **Lint** (`ruff`, `black`).  
5. **Build** de l’image Docker (`Dockerfile.app`).  
6. **Push** vers le registre interne.  
7. **Déploiement** via `docker‑compose up -d` (environnements dev/recette/prod).  

---

## 6. Vue en Briques (C4 – Niveau 2)  

```mermaid
graph TD;
    subgraph "Conteneurs"
        C1[nginx (load‑balancer)] 
        C2[dagster‑webserver] 
        C3[dagster‑daemon (scheduler)] 
        C4[afinope‑app (Python ETL)] 
        C5[postgres (db)] 
        C6[superset (BI)] 
    end;
    C1 --> C2;
    C1 --> C6;
    C2 --> C3;
    C3 --> C4;
    C4 --> C5;
    C6 --> C5;
    style C1 fill:#f9f,stroke:#333,stroke-width_2px;
    style C2 fill:#bbf,stroke:#333,stroke-width_2px;
    style C3 fill:#bbf,stroke:#333,stroke-width_2px;
    style C4 fill:#bfb,stroke:#333,stroke-width_2px;
    style C5 fill:#ffb,stroke:#333,stroke-width_2px;
    style C6 fill:#fbb,stroke:#333,stroke-width_2px
```

| Conteneur | Responsabilité principale | Image / Build |
|-----------|--------------------------|---------------|
| **nginx** | Reverse‑proxy, TLS termination, load‑balancing | `nginx:stable-alpine` |
| **dagster‑webserver** | UI & API GraphQL (déclenchement manuel) | `dagster-webserver:1.8` |
| **dagster‑daemon** | Scheduler (exécution planifiée) | `dagster:1.8` |
| **afinope‑app** | Ingestion CSV → transformation → persistance (modules `GestionnaireFichiersCSV`, `GestionnaireBaseDonnees`) | `Dockerfile.app` (Python 3.11) |
| **postgres** | Stockage persistant des référentiels & exécutoire | `postgres:13-alpine` |
| **superset** | Tableaux de bord décisionnels | `apache/superset:latest` |

---

## 7. Vue Exécution  

### 7.1 Scénario critique : **Traitement d’un lot CSV**  

| Étape | Acteur | Action | Artefact / Résultat |
|------|--------|--------|----------------------|
| 1 | **Scheduler Dagster** | Lance le job `ingest_csv` à 02 h00 (cron) | |
| 2 | **afinope‑app** (`GestionnaireFichiersCSV`) | Liste les fichiers CSV dans le répertoire d’entrée | `["REF_NOMENC_20240522.csv", …]` |
| 3 | **afinope‑app** (`GestionnaireFichiersCSV`) | Déplace chaque fichier vers `/processing` (atomic) | |
| 4 | **afinope‑app** (`GestionnaireBaseDonnees`) | Ouvre une connexion `SQLAlchemy` → `BEGIN` | Transaction ouverte |
| 5 | **afinope‑app** (`transformateur`) | Lit CSV via `pandas`, applique `helper` (nettoyage, conversion) | `DataFrame` normalisé |
| 6 | **afinope‑app** (`GestionnaireBaseDonnees`) | `to_sql(..., if_exists="append")` → insertion en batch | Rows insérées |
| 7 | **afinope‑app** | Commit transaction, log `INFO` avec `run_id` | `run_id=2026-04-27-001` |
| 8 | **Dagster** | Met à jour le statut du run (`SUCCESS`/`FAILED`) | Métriques exposées à Prometheus |
| 9 | **Superset** | Rafraîchit les vues matérialisées (triggered via `REFRESH MATERIALIZED VIEW`) | Dashboard actualisé |
| 10 | **Supervision** | AlertManager envoie un mail si le run dépasse 30 s ou échoue | Notification au SRE |

### 7.2 Scénario de récupération : **Échec d’insertion**  

1. Exception levée dans `stockage_dataframe` (ex. violation de contrainte).  
2. `GestionnaireBaseDonnees` effectue **rollback**.  
3. Dagster marque le step comme `FAILED`, crée un ticket JIRA via webhook.  
4. L’opérateur peut relancer le job après correction du fichier.  

---

## 8. Vue Déploiement *(section standardisée)*  

```markdown
### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | À compléter | À compléter | À compléter | À compléter |
| Recette       | À compléter | À compléter | À compléter | À compléter |
| Production    | À compléter | À compléter | À compléter | À compléter |
```

### Infrastructure  
Le produit est hébergé sur le cloud interne **ECO4** basé sur **Openstack**, dans le tenant **'pnm3'** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD;
    A[Nginx] -- B[Application]
    B -- C[Base de données]
    B -- D[Autres services]
```

### Supervision  
Le produit est supervisé via le système standard du GTI pour ce faire :  
- via **Portainer** pour la partie purement conteneurisée,  
- via la stack **Prometheus/Grafana/Loki/AlertManager**,  
- Le produit dispose également d’une supervision **PSIN**.

### Sauvegardes  
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :  
- le stockage objet **B3** du IaaS ministériel,  
- le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché "Nuage Public"),  
- le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché "Nuage Public").

---

## 9. Sujets transverses  

| Sujet | Implémentation concrète | Points d’attention |
|-------|------------------------|--------------------|
| **Authentification** | Intégration LDAP via `dagster-webserver` + SSO (OpenID Connect) | Gestion des groupes (analystes, admins) |
| **Journalisation** | Logs JSON via `structlog` dans chaque conteneur ; agrégation dans Loki | Rotation des logs, conformité GDPR |
| **Monitoring** | Prometheus scrape `dagster`, `postgres_exporter`, `nginx`; alertes sur durée de run, latence DB | Dashboard Grafana dédié aux ETL |
| **Gestion des erreurs** | Exceptions capturées, `Retry` (backoff) sur I/O, `dead‑letter` folder pour CSV non traitables | Alertes automatisées |
| **API** | Dagster expose GraphQL & REST (`/dagster/graphql`) ; futur micro‑service FastAPI pour requêtes ad‑hoc | Versionning, throttling |
| **CI/CD** | GitLab CI pipeline (lint → test → build → push) ; déploiement `docker‑compose` | Sécurité des variables d’environnement |
| **Sécurité des données** | Chiffrement des backups, TLS end‑to‑end, secrets dans Vault, contrôle d’accès au réseau (Security Groups) | Audits réguliers |
| **Documentation & DevOps** | `README.md` + diagrammes Mermaid, ADRs dans `docs/adr/` | Maintien à jour automatisé via CI |

---

## 10. Exigences de qualité  

| ID | Exigence | Scénario de validation | Critère d’acceptation |
|----|----------|------------------------|-----------------------|
| **Q‑01** | Temps de traitement d’un fichier CSV de 10 Mo ≤ 30 s | Exécution du job `ingest_csv` sur un jeu de test | Durée mesurée < 30 s (Prometheus metric `dagster_job_duration_seconds`) |
| **Q‑02** | Confidentialité des sauvegardes | Vérifier le dump chiffré avec `openssl aes-256-cbc -d` (clé manquante) | Impossible de déchiffrer sans clé |
| **Q‑03** | Disponibilité du service web | Simuler une panne du conteneur `afinope‑app` | Nginx redirige le trafic vers le conteneur de secours (pas d’interruption) |
| **Q‑04** | Couverture de tests unitaires | `pytest --cov=app` | Coverage ≥ 80 % |
| **Q‑05** | Traçabilité des traitements | Consulter les logs dans Loki ou la table `dagster_runs` | Chaque run possède un `run_id`, timestamp, status et lien vers le fichier source |
| **Q‑06** | Intégrité des données | Insertion d’un CSV contenant une valeur `NULL` dans un champ NOT NULL | Transaction échoue, aucun enregistrement partiel n’est persistant |
| **Q‑07** | Opérabilité – MTTR | Induire une panne (kill du conteneur DB) | AlertManager notifie en < 5 min, restauration automatisée en < 15 min |

---

## 11. Risques et Dettes techniques  

| Risque | Impact | Mesure corrective / mitigation |
|--------|--------|------------------------------|
| **R‑01** | **Explosion de la mémoire** lors du chargement de gros CSV (≥ 100 Mo) | Implémenter le streaming `pandas.read_csv(..., chunksize=…)` ; tests de charge |
| **R‑02** | **Évolution du schéma CSV** (nouveaux champs) | Versionner les schémas dans `docs/schemas/`, ajouter des adaptateurs de migration |
| **R‑03** | **Faille de sécurité** sur les secrets (.env) | Utiliser HashiCorp Vault + rotation automatique des credentials |
| **R‑04** | **Défaillance du job Dagster** non détectée | AlertManager sur `dagster_job_status` = `FAILED` + escalation JIRA |
| **R‑05** | **Dette technique** – code très couplé entre `gestionnaire_fichier_csv` et `gestionnaire_base_donnees` | Refactoriser en services indépendants, appliquer le principe SOLID |
| **R‑06** | **Obsolescence du framework** (Dagster 1.x) | Suivi de version, tests d’intégration avant upgrade majeur |
| **R‑07** | **Conformité RGPD** – logs contenant des données personnelles | Anonymiser les champs sensibles, définir une politique de rétention 30 jours |

---

## 12. Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **ETL** | Extract‑Transform‑Load – processus de collecte, transformation et chargement de données. |
| **Dagster** | Plateforme d’orchestration de pipelines de données, fournit un UI et un scheduler. |
| **Superset** | Outil de visualisation BI open‑source, se connecte à PostgreSQL. |
| **ECO4** | Cloud interne du Ministère (OpenStack). |
| **D‑I‑C‑T** | Modèle de sécurité : Disponibilité, Intégrité, Confidentialité, Traçabilité. |
| **ADR** | Architectural Decision Record – documentation des décisions majeures. |
| **PSIN** | Plateforme de Supervision Inter‑Nationale (interne GTI). |
| **Portainer** | UI de gestion des conteneurs Docker. |
| **Vault** | Gestion centralisée des secrets. |

### 12.2 Décisions d’architecture (ADR) – Exemple  

| ADR | Titre | Décision | Raison | Statut |
|-----|-------|----------|--------|--------|
| **ADR‑001** | Choix de Docker pour la conteneurisation | Docker + docker‑compose | Standardisation interne, portabilité | ✅ Adoptée |
| **ADR‑002** | Utilisation de Dagster pour l’orchestration | Dagster 1.8 (GraphQL API) | Visibilité des runs, reprise sur erreur | ✅ Adoptée |
| **ADR‑003** | Stockage des données dans PostgreSQL | PostgreSQL 13, contraintes ACID | Fiabilité, requêtes complexes | ✅ Adoptée |
| **ADR‑004** | Gestion des secrets via Vault | HashiCorp Vault + `.env` injection | Sécurité, conformité | ✅ Adoptée |
| **ADR‑005** | Utilisation de Superset pour le reporting | Superset latest (SQL‑Alchemy) | Outil déjà présent dans la DSI | ✅ Adoptée |

---

*Fin du Dossier d’Architecture Technique*  

---  

**Note** : Ce DAT est volontairement générique ; chaque équipe projet pourra spécialiser les tableaux « Environnements », « Parties prenantes », ou ajouter des diagrammes détaillés (C4‑L3/L4) en fonction des spécificités fonctionnelles qui seront définies lors de la phase d’expression des besoins.  