# 📄 Dossier d’Architecture Technique (DAT) – **Afinope**  
[TOC]

---

## 1️⃣ Introduction et objectifs

**Afinope** est une application Python destinée à la production de tableaux de bord financiers pour les opérateurs de l’État. Elle orchestre la lecture de fichiers CSV, le chargement dans une base PostgreSQL et l’exposition de vues exploitées par Superset.

### Objectifs de qualité (orientés utilisateur)

| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Performance** – traitement de milliers de lignes CSV en < 30 s | Réactivité des tableaux de bord |
| 2 | **Sécurité** – chiffrement des backups, contrôle d’accès RBAC | Conformité aux exigences de la DGFIP |
| 3 | **Fiabilité** – reprise après incident, logs détaillés | Garantir la continuité des rapports financiers |
| 4 | **Maintenabilité** – découpage en composants testables | Faciliter l’évolution du modèle de données |
| 5 | **Observabilité** – métriques Prometheus, alertes | Détection rapide des ruptures de chaîne de traitement |

---

## 2️⃣ Niveau 1 – Vue **Contexte** (System Context)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(analyst, "Analyste Financier", "Consulte les tableaux de bord dans Superset")
Person(admin, "Administrateur Ops", "Déploie, configure et assure la supervision")
System_Ext(csv_source, "Source CSV DGFIP", "Fichiers fournis par la DGFIP (ex. REF_NOMENC_20240522.csv)")
System_Ext(superset, "Superset (BI)", "Consomme les vues SQL exposées par Afinope")
System(afinope, "Afinope", "Application de traitement et d’alimentation de la base financière")

Rel(analyst, superset, "Navigue les dashboards")
Rel(admin, afinope, "Déploie / administre")
Rel(afinope, csv_source, "Lit les CSV")
Rel(afinope, superset, "Expose des vues SQL")
Rel(afinope, PostgreSQL, "Persiste les données")
@enduml
```

### Acteurs principaux

| Acteur | Objectif |
|--------|----------|
| **Analyste Financier** | Visualiser les indicateurs de performance financière |
| **Administrateur Ops** | Déployer, monitorer et mettre à jour l’application |
| **Système DGFIP (CSV)** | Fournir les flux de données brutes chaque jour ouvré |

### Systèmes externes

| Système | Rôle |
|---------|------|
| **PostgreSQL** | Base de données relationnelle hébergeant les référentiels et les tables d’exécution |
| **Superset** | Plateforme de visualisation (BI) consommant les vues SQL générées |
| **DGFIP (CSV)** | Source de données métier (référentiels, exécutions, etc.) |

---

## 3️⃣ Parties prenantes

| Rôle | Attente principale |
|------|--------------------|
| **MOA (Maitrise d’Ouvrage)** | Fiabilité des données financières, conformité aux référentiels DGFIP |
| **Développeurs** | Architecture claire, tests unitaires, CI/CD fiable |
| **RSSI** | Confidentialité des données, traçabilité des accès, sauvegardes chiffrées |
| **Exploitation** | Monitoring automatisé, capacité de reprise rapide |
| **Utilisateurs finaux (Analystes)** | Accès aux dashboards à jour, latence minimale |

---

## 4️⃣ Contraintes

### Techniques
| Type | Description |
|------|-------------|
| **Langage / Framework** | Python 3.11, Dagster 1.8, SQLAlchemy 2.0 |
| **Base de données** | PostgreSQL 13 (ou sup.), schéma public |
| **Conteneurisation** | Docker, Docker‑Compose |
| **CI/CD** | GitLab CI (pipeline défini dans `.gitlab-ci.yml`) |
| **Gestion des dépendances** | Poetry (verrouillé dans `poetry.lock`) |

### Organisationnelles
| Type | Description |
|------|-------------|
| **Livraison continue** | Déploiement automatisé sur les environnements dev / rec / prod |
| **Documentation** | Diagrammes C4, README, ADRs dans `docs/` (non fourni mais recommandé) |
| **Gestion de configuration** | Fichier `config.json` monté en volume, variables d’environnement `.env` |

### Réglementaires
| Type | Description |
|------|-------------|
| **D‑I‑C‑T** | <ul><li>**Disponibilité** : SLA ≥ 99,9 % (HA Nginx + réplication PostgreSQL)</li><li>**Intégrité** : contraintes de clé primaire, types stricts</li><li>**Confidentialité** : sauvegardes chiffrées AES‑256, accès limité aux rôles</li><li>**Traçabilité** : logs Dagster, audit PostgreSQL</li></ul> |

---

## 5️⃣ Niveau 2 – Vue **Conteneurs** (Containers)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

System_Boundary(afinope_boundary, "Afinope") {
    Container(app, "Afinope WebApp", "Python/Dagster", "Orchestre les pipelines ETL, expose les API REST et le Web UI")
    Container(db, "PostgreSQL", "PostgreSQL 13", "Stocke les référentiels et les tables d’exécution")
    Container(superset, "Superset (BI)", "Python/Flask", "Consomme les vues SQL pour les dashboards")
    Container(nginx, "Nginx Load‑Balancer", "Nginx", "Terminaison TLS, routage vers l’app")
}

Rel(nginx, app, "HTTP/HTTPS")
Rel(app, db, "JDBC/SQLAlchemy")
Rel(app, superset, "SQL Views (read‑only)")
@enduml
```

### Description des conteneurs

| Conteneur | Responsabilité | Technologie | Interactions clés |
|----------|----------------|--------------|-------------------|
| **Afinope WebApp** | Pipeline Dagster : ingestion CSV → transformation → persistance | Python 3.11, Dagster, SQLAlchemy, Pandas | Lit les CSV (`GestionnaireFichiersCSV`), charge les DataFrames (`GestionnaireBaseDonnees`), expose des vues via SQLAlchemy |
| **PostgreSQL** | Base de données centrale | PostgreSQL 13, Docker‑volume `db/data` | Persistance des tables référentielles et d’exécution |
| **Superset** | Visualisation BI | Python 3, Flask, SQLAlchemy | Lecture en read‑only des vues (`tdb_view`, …) |
| **Nginx** | Point d’entrée réseau, TLS, load‑balancing | Nginx (2 instances) | Répartition du trafic HTTP/HTTPS vers le conteneur `app` |

### Décisions architecturales majeures

| Décision | Justification |
|----------|---------------|
| **Conteneurisation Docker** | Isolation des dépendances, portabilité entre environnements |
| **Dagster comme orchestrateur** | Gestion native des pipelines, UI de monitoring, retry & back‑off |
| **PostgreSQL comme source unique** | Cohérence transactionnelle, support des vues matérialisées |
| **Superset en lecture‑seule** | Séparation claire des responsabilités (ETL vs BI) |
| **Nginx en front** | Gestion du TLS, scalabilité horizontale simple |

### Environnement technologique

| Couche | Outils / Versions |
|--------|-------------------|
| **Langage** | Python 3.11.10 |
| **Gestion de dépendances** | Poetry 1.8 |
| **Orchestration** | Dagster 1.8 (WebServer) |
| **Base de données** | PostgreSQL (Docker) |
| **BI** | Superset (déployé séparément) |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`) |
| **Conteneurisation** | Docker 23, Docker‑Compose 2.23 |
| **Monitoring** | Prometheus / Grafana (via GTI) |
| **Logs** | Portainer, GTI, PSIN |

---

## 6️⃣ Niveau 3 – Vue **Composants** (Components) – *Conteneur principal : Afinope WebApp*

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

Container(app, "Afinope WebApp", "Python/Dagster")

Component(flux, "Flux", "Gestion du chemin d’entrée / sortie / erreur")
Component(gestionnaireCSV, "GestionnaireFichiersCSV", "Déplacement, listage des CSV")
Component(gestionnaireDB, "GestionnaireBaseDonnees", "Création des tables, stockage DataFrames")
Component(circuit, "CircuitAlimentation", "Coordonne les flux de données")
Component(afinopeCore, "Afinope Core", "Logique métier, API Dagster")
Component(helper, "Helper", "Fonctions utilitaires (conversion, nettoyage)")

Rel(flux, gestionnaireCSV, "Passe les chemins")
Rel(gestionnaireCSV, gestionnaireDB, "Envoie les DataFrames")
Rel(gestionnaireDB, afinopeCore, "Persistance")
Rel(circuit, afinopeCore, "Orchestration Dagster")
Rel(helper, afinopeCore, "Utilisé par")
@enduml
```

### Responsabilités des composants

| Composant | Rôle |
|-----------|------|
| **Flux** | Encapsule les répertoires `entree`, `sortie`, `erreur` (configurable) |
| **GestionnaireFichiersCSV** | Recherche les fichiers CSV, les déplace après traitement |
| **GestionnaireBaseDonnees** | Crée les tables via `AfinopeBase.metadata`, stocke les DataFrames dans PostgreSQL |
| **CircuitAlimentation** | Définit le pipeline Dagster (jobs, schedules) |
| **Afinope Core** | Point d’entrée Dagster, journalisation, injection de dépendances |
| **Helper** | Conversions `na → ''`, `int → bool`, `str → float` pour nettoyer les données |

---

## 7️⃣ Niveau 4 – Vue **Code** (niveau détaillé)

> **Remarque** : les diagrammes de classes et ERD sont disponibles dans le répertoire `docs/` (non fourni ici).  
> Pour les scénarios critiques, des diagrammes de séquence sont présentés dans la section suivante.

---

## 8️⃣ Vue **Exécution** – Scénarios critiques

### 8.1 Ingestion d’un fichier CSV

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Sequence.puml

actor Analyste as user
participant "Nginx LB" as nginx
participant "Afinope WebApp" as app
participant "GestionnaireFichiersCSV" as csvMgr
participant "GestionnaireBaseDonnees" as dbMgr
database PostgreSQL as db

user -> nginx : Upload CSV via volume mount (ou copie dans /entree)
activate nginx
nginx -> app : Notification de nouveau fichier (polling)
activate app
app -> csvMgr : lister_les_fichiers()
csvMgr --> app : ["REF_NOMENC_20240522.csv"]
app -> csvMgr : deplacer_fichier(..., "erreur") [if error]
app -> dbMgr : stocker_dataframe(df, "NOMENC")
dbMgr -> db : INSERT INTO "NOMENC"
deactivate dbMgr
deactivate app
deactivate nginx
@enduml
```

**Points de validation**  
- Le fichier apparaît dans le répertoire `sortie` ou `erreur`.  
- Une ligne d’audit est écrite dans les logs Dagster.  
- La table cible possède le nombre de lignes attendu.

### 8.2 Génération et publication d’une vue Superset

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Sequence.puml

participant "Afinope WebApp" as app
database PostgreSQL as db
participant Superset as sup

app -> db : CREATE OR REPLACE VIEW tdb_view AS …
activate db
db --> app : OK
deactivate db
app -> sup : Notification (via webhook ou refresh)
activate sup
sup -> db : SELECT * FROM tdb_view
sup --> app : Dashboard actualisé
deactivate sup
@enduml
```

**Points de validation**  
- La vue `tdb_view` est à jour (timestamp de dernière mise à jour).  
- Superset affiche les nouveaux indicateurs sans erreur.

---

## 9️⃣ Vue **Déploiement** *(section standardisée)*

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
    Deployment_Node(nginx, "Nginx Cluster", "Load Balancer") {
        Container(app, "Afinope WebApp", "Docker", "Dagster WebServer")
    }
    Deployment_Node(db, "Base de données", "PostgreSQL") {
        ContainerDb(database, "PostgreSQL", "PostgreSQL", "Données métier")
    }
    Deployment_Node(sup, "Superset BI", "Docker") {
        Container(superset, "Superset", "Python/Flask", "Dashboards")
    }
}

Rel(nginx, app, "HTTP/HTTPS")
Rel(app, database, "JDBC/SQLAlchemy")
Rel(app, superset, "SQL View (read‑only)")
@enduml
```

### Environnements

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | Cloud interne (tenant pnm3) | 1 × Nginx, 1 × App, 1 × DB | VLAN dev | Docker‑Compose local, logs verbeux |
| Recette | Cloud interne (tenant pnm3) | 2 × Nginx (HA), 2 × App, 1 × DB (replication) | VLAN rec | Tests d’intégration automatisés, données masquées |
| Production | Cloud interne (tenant pnm3) | 2 × Nginx (load‑balancing), 3 × App (Dagster workers), 2 × DB (master‑slave) | VLAN prod | TLS, sauvegardes chiffrées, monitoring GTI |

### Infrastructure

Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant `pnm3` du département. Le reverse‑proxy Nginx du schéma ci‑dessus est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

Deployment_Node(cloud, "Cloud ECO4", "OpenStack Tenant pnm3") {
    Deployment_Node(nginx, "Nginx Cluster", "Load Balancer") {
        Container(app, "Application", "Docker", "Application principale")
    }
    Deployment_Node(db, "Base de données", "PostgreSQL") {
        ContainerDb(database, "Database", "PostgreSQL", "Données métier")
    }
}

Rel(nginx, app, "HTTP/HTTPS")
Rel(app, database, "JDBC/SQL")
@enduml
```

### Supervision

Le produit est supervisé via le système standard du GTI :

- **Portainer** : gestion et monitoring des conteneurs Docker.  
- **Stack Prometheus / Grafana / Loki / AlertManager** : métriques d’usage, logs centralisés, alertes.  
- **Supervision PSIN** : suivi des indicateurs de disponibilité et de performance.

### Sauvegardes

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps chiffrés en **AES‑256** et déposés sur :

| Cible | Description |
|-------|-------------|
| **Objet B3 (IaaS ministériel)** | Stockage durable et résilient |
| **Outscale SecNumCloud** | Offre publique “Nuage Public” du GTI |
| **Google Cloud Storage** | Offre publique “Nuage Public” du GTI |

---

## 🔟 Sujets transverses

| Thème | Décisions / Implémentation |
|-------|---------------------------|
| **Authentification** | Authentification via LDAP (déployée côté Nginx) pour l’accès à l’UI Dagster et Superset |
| **Journalisation** | Logs structurés JSON via `logging` Python, agrégés par Loki |
| **Monitoring** | Métriques exposées par le serveur Dagster (`/metrics`) et par le exporter PostgreSQL |
| **Gestion des erreurs** | Retry automatique dans Dagster, alertes via AlertManager |
| **API** | Endpoints REST minimalistes exposés par Dagster (facultatif) |
| **Sécurité des données** | Chiffrement des backups, connexion DB via SSL, secrets dans `.env` (non versionnés) |
| **CI/CD** | Pipelines GitLab : lint, tests unitaires (pytest), build Docker, déploiement via `docker‑compose` |

---

## 1️⃣1️⃣ Exigences de qualité

| Exigence | Scénario de validation |
|----------|--------------------------|
| **Performance** – traitement < 30 s | Exécuter le pipeline complet sur un jeu de 10 000 lignes, mesurer le temps via les métriques Dagster |
| **Sécurité** – chiffrement des backups | Vérifier que le fichier de dump possède l’en‑tête `AES‑256` et qu’il n’est pas lisible en clair |
| **Fiabilité** – reprise après crash | Simuler l’arrêt du conteneur `app`, redémarrer, vérifier que le pipeline reprend à l’étape suivante sans perte de données |
| **Observabilité** – alertes en cas d’échec | Provoquer une erreur de parsing CSV, s’assurer que l’alerte `pipeline_failure` est générée dans AlertManager |
| **Maintenabilité** – couverture de tests ≥ 80 % | Exécuter `pytest --cov=app` et vérifier le pourcentage de couverture |

---

## 1️⃣2️⃣ Risques et dettes techniques

| Risque / Dette | Impact | Atténuation |
|----------------|--------|--------------|
| **Dépendance à Dagster** | Verrouillage sur une version spécifique | Documenter les procédures de mise à jour, prévoir des tests d’intégration lors de chaque upgrade |
| **Gestion manuelle des CSV** | Risque d’erreurs de format non détectées | Ajouter un schéma de validation (pydantic/cerberus) avant l’ingestion |
| **Absence de tests d’intégration DB** | Bugs de migration non détectés | Introduire des tests de migration avec `pytest-postgresql` |
| **Sauvegardes non testées** | Perte de données en cas de sinistre | Planifier des restaurations périodiques sur un environnement de test |
| **Scalabilité limitée** (single‑node DB) | Saturation en production | Étudier la mise en place de PostgreSQL en mode **Patroni** ou **Citus** pour le scaling horizontal |

---

## 1️⃣3️⃣ Annexes

### Glossaire

| Terme | Définition |
|-------|------------|
| **Dagster** | Plateforme d’orchestration de pipelines de données, similaire à Airflow mais avec un focus sur le typage et le monitoring. |
| **Superset** | Outil open‑source de visualisation de données (BI) développé par Apache. |
| **GTI** | Groupe Technique d’Infrastructure, responsable de la supervision et des sauvegardes. |
| **DGFIP** | Direction Générale des Finances Publiques – source des référentiels CSV. |
| **C4** | Modèle de visualisation d’architecture (Context, Containers, Components, Code). |

### Décisions d’Architecture (ADRs) – exemples

| ADR # | Sujet | Décision | Statut |
|------|-------|----------|--------|
| 1 | Utiliser **Docker** pour l’ensemble des services | Docker simplifie le déploiement multi‑environnements | ✅ Adoptée |
| 2 | Orchestration avec **Dagster** plutôt qu’Airflow | Dagster offre une meilleure intégration Python et un UI plus riche | ✅ Adoptée |
| 3 | Stockage des données dans **PostgreSQL** | Relationnel, support des vues, conformité aux exigences D‑I‑C‑T | ✅ Adoptée |
| 4 | Exposer les dashboards via **Superset** | Outil BI déjà standardisé dans l’organisation | ✅ Adoptée |
| 5 | Utiliser **Nginx** comme point d’entrée unique | Centralise TLS, facilite le scaling horizontal | ✅ Adoptée |

---

*Ce document est auto‑contenu, généré en Markdown compatible avec VS Code ou Obsidian (PlantUML activé). Toutes les sections sont navigables via les ancres internes.*