# 📄 Dossier d’Architecture Technique (DAT) – **SIREINES**  
*Version 1.0 – 2024‑04‑27*  

---  

## 📚 Table des matières  

| # | Section | Lien |
|---|---------|------|
| 1️⃣ | **1️⃣ Introduction & objectifs** | [⤓](#1️⃣-introduction--objectifs) |
| 2️⃣ | **2️⃣ Parties prenantes** | [⤓](#2️⃣-parties‑prenantes) |
| 3️⃣ | **3️⃣ Contraintes** | [⤓](#3️⃣-contraintes) |
| 4️⃣ | **4️⃣ Contexte & périmètre** | [⤓](#4️⃣-contexte--périmètre) |
| 5️⃣ | **5️⃣ Stratégie de solution** | [⤓](#5️⃣-stratégie‑de‑solution) |
| 6️⃣ | **6️⃣ Vue en briques (C4 L2)** | [⤓](#6️⃣-vue‑en‑briques) |
| 7️⃣ | **7️⃣ Vue d’exécution** | [⤓](#7️⃣-vue‑dexécution) |
| 8️⃣ | **8️⃣ Vue déploiement** *(standardisée)* | [⤓](#8️⃣-vue‑déploiement) |
| 9️⃣ | **9️⃣ Sujets transverses** | [⤓](#9️⃣-sujets‑transverses) |
| 🔟 | **🔟 Exigences de qualité** | [⤓](#🔟-exigences‑de‑qualité) |
| 1️⃣1️⃣ | **11️⃣ Risques & dettes** | [⤓](#11️⃣-risques‑et‑dettes) |
| 1️⃣2️⃣ | **12️⃣ Annexes** | [⤓](#12️⃣-annexes) |

---  

## 1️⃣ Introduction & objectifs <a id="1️⃣-introduction--objectifs"></a>

### 1.1 Vue d’ensemble fonctionnelle  
SIREINES (Système d’Information REgistre des Experts et Spécialistes) recense les demandes de qualification des agents par les comités de domaine, assure le suivi de leur évolution, génère les courriers associés et propose des extractions statistiques (pyramides d’âge, fréquence des mots‑clés, évolution des qualifications, …).  

### 1.2 Schéma C4‑L1 (Vue du système)  
```mermaid
graph LR
    subgraph Utilisateurs;
        UA[Agent] 
        UB[Administrateur]
    end
    subgraph Frontend;
        UI[Interface Web (Struts2 + FreeMarker)]
    end
    subgraph Backend;
        APP[Application Java (Tomcat 7, J2EE, Spring, Vertigo)]
        BIRT[BIRT Reporting]
        ES[Elasticsearch Embedded (recherche)]
    end
    DB[(PostgreSQL 14 – schéma SIREINES)]
    subgraph Infra;
        DOCKER[Docker / Docker‑Compose]
        IaaS[Eco4 IaaS – Paris La Défense]
    end
    UA --> UI;
    UB --> UI;
    UI --> APP;
    APP --> BIRT;
    APP --> ES;
    APP --> DB;
    DOCKER --> APP & DB & BIRT;
    IaaS --> DOCKER
```

> *Le diagramme ci‑dessus représente les principaux blocs du système et leurs relations.*  

### 1.3 Objectifs qualité orientés utilisateur  

| # | Objectif | Pourquoi | KPI indicatif |
|---|----------|----------|---------------|
| O1 | **Performance** – temps de réponse < 2 s pour les écrans de recherche | Garantir une navigation fluide aux agents | % de requêtes ≤ 2 s (target ≥ 95 %) |
| O2 | **Sécurité** – confidentialité des DCP (Données à Caractère Personnel) | Conformité RGPD / CNIL | Aucun incident de fuite DCP (0) |
| O3 | **Disponibilité** – 99,5 % de disponibilité mensuelle | Assurer la continuité de service | Uptime (monitoring) |
| O4 | **Maintenabilité** – temps moyen de correction < 4 h | Réduction du coût d’exploitation | MTTR (Mean Time To Repair) |
| O5 | **Traçabilité** – journalisation exhaustive des actions critiques | Auditabilité et conformité | % d’évènements loggués (target 100 %) |

---  

## 2️⃣ Parties prenantes <a id="2️⃣-parties‑prenantes"></a>

| Rôle | Responsable | Contact | Rôle métier |
|------|-------------|---------|-------------|
| **MOA** (Maîtrise d’Ouvrage) | **Pascal Zemour** – CGDD/DRI/AST4 | Pascal.Zemour@developpement-durable.gouv.fr | Pilotage fonctionnel, exigences métier |
| **MOE** (Maîtrise d’Œuvre) – Prestataire (historique) | **Matthieu Georges** – Klee Group | matthieu.georges@kleegroup.com | Architecture, développement, intégration |
| **Chef de projet** | **Vincent Letrouit** – CGDD/DRI/AST4 | Vincent.Letrouit@developpement-durable.gouv.fr | Coordination, planification |
| **Exploitation** | **Infocentre BUN** – CGDD/SDSED | infocentre.bun.sdsed.cgdd@developpement-durable.gouv.fr | Gestion des environnements, incidents |
| **Sécurité / SSI** | **CGDD/SRI/AST2** | – | Gestion des exigences de sécurité, traçabilité |
| **Utilisateurs finaux** | Agents publics, experts, chefs de service | – | Saisie, suivi, consultation des dossiers |
| **Support** | **Portail‑support DIN** | – | Gestion des tickets (Cerbère) |

---  

## 3️⃣ Contraintes <a id="3️⃣-contraintes"></a>

| Type | Description | Impact |
|------|-------------|--------|
| **Techniques** | - Java 1.7, Tomcat 7.0.108‑jdk8 <br> - Struts 2, FreeMarker (FTL) <br> - Spring 2 (bean, AOP, transaction) <br> - Vertigo Dynamo (search, DAO) <br> - PostgreSQL 14 (Docker) <br> - BIRT 4.3 (reporting) <br> - Docker Compose (3 containers) <br> - SonarQube (qualité) | Nécessite des versions compatibles, migration future à prévoir |
| **Organisationnelles** | - Processus de **Merge Request** (GitLab) pour chaque promotion (dev → recette → pre‑prod → prod) <br> - Validation de la **pipeline CI** avant merge <br> - Gestion des **variables d’environnement** via `.env` (DB credentials, ports) | Discipline stricte de la chaîne CI/CD |
| **Réglementaires** | - RGPD – traitement de DCP (coordonnées experts) <br> - CNIL – déclaration n° 1034232 (29/09/2014) <br> - Conservation : 5 ans, destruction après décision <br> - Traçabilité (journalisation) obligatoire | Obligation de journaliser, chiffrer les sauvegardes, contrôler les accès |
| **Sécurité (D‑I‑C‑T)** | **Disponibilité** – réplication de la DB en volume Docker (persistant) <br> **Intégrité** – contraintes FK, triggers, scripts d’upgrade <br> **Confidentialité** – chiffrement des dumps (AES‑256) <br> **Traçabilité** – logs Nginx, Prometheus + AlertManager, sauvegardes versionnées | Implémentation des exigences D‑I‑C‑T (voir § 9️⃣) |
| **Performance** | Temps de réponse < 2 s, indexation Elasticsearch (clé = dossier) | Nécessite des index et du tuning DB |
| **Interopérabilité** | - Import/export via Talend (reports *.rptdesign) <br> - API REST interne (non documentée) | Points d’intégration à surveiller |

---  

## 4️⃣ Contexte & périmètre <a id="4️⃣-contexte--périmètre"></a>

### 4.1 Interactions fonctionnelles  

| Système / acteur | Type d’échange | Protocole / format | Fréquence |
|-------------------|----------------|-------------------|-----------|
| **Agents / Utilisateurs** | Navigation Web (CRUD dossiers, extractions) | HTTP/HTTPS (Struts2) | En temps réel |
| **BIRT** | Génération de rapports (PDF, XLS) | HTTP + BIRT Engine | À la demande |
| **Elasticsearch** | Recherche plein‑texte sur dossiers | Bibliothèque Vertigo (embedded) | En temps réel |
| **Talend** | Imports de fichiers (CSV, XML) → tables | Talend Job (rptdesign) | Batch (quotidien) |
| **Supervision** | Métriques, alertes | Prometheus / Grafana / AlertManager | Continu |
| **Cerbère** | Gestion des tickets / incidents | Web UI | Asynchrone |
| **PostgreSQL** | Persistance des données | JDBC (PostgreSQL driver) | Transactionnelle |
| **Docker‑Compose** | Orchestration des containers | Docker API | Déploiement/scale |

### 4.2 Périmètre fonctionnel  

| Domaine | Fonctionnalité | Description |
|---------|----------------|-------------|
| **Gestion des dossiers** | Création, mise à jour, suivi, recherche | Interface Struts2, DAO Vertigo |
| **Extraction & reporting** | Export CSV, rapports BIRT, tableaux de bord | Talend, BIRT, Elasticsearch |
| **Gestion des courriers** | Génération, suivi, archivage | Templates FreeMarker |
| **Administration** | Gestion des utilisateurs, paramètres, logs | Spring, Struts2, configuration `.env` |
| **Sécurité** | Authentification (session), authorisation (roles) | `sireines-auth-config.xml` (PRM_READ_ALL, PRM_WRITE_ALL) |
| **Sauvegarde & restauration** | Dumps chiffrés, versionning | Scripts `docker exec` → `pg_dump` + AES‑256 |

---  

## 5️⃣ Stratégie de solution <a id="5️⃣-stratégie‑de‑solution"></a>

| Décision | Raison | Alternatives rejetées |
|----------|--------|-----------------------|
| **Architecture monolithique** (un seul WAR/Tomcat) | Simplicité de déploiement, historique existant | Micro‑services (complexité, migration) |
| **Docker‑Compose** pour l’ensemble (app + DB + pgAdmin) | Isolation, reproductibilité, versionning des images | VM bare‑metal (coût, maintenance) |
| **PostgreSQL** en container | Licence Open‑Source, performances, support JSONB | Oracle (coût) |
| **BIRT** intégré pour le reporting | Déjà utilisé, génération PDF/Excel native | JasperReports (migration) |
| **Elasticsearch embedded** (Vertigo) | Recherche rapide sans cluster externe | Cluster dédié (sur‑dimensionné) |
| **Struts 2 + FreeMarker** (FTL) | Stack legacy maintenu, forte communauté interne | Spring MVC (réécriture) |
| **CI / CD** via GitLab CI (pipeline `mvn package`, `docker build`, `docker‑compose up`) | Alignement avec le dépôt GitLab | Jenkins (déjà installé mais redondant) |

### 5.1 Environnement technologique  

| Couche | Technologie | Version |
|--------|-------------|---------|
| **Langage** | Java | 1.7 (compatibilité Tomcat 7) |
| **Serveur d’applications** | Tomcat | 7.0.108‑jdk8 |
| **Framework web** | Struts 2, FreeMarker | 2.5.x, 2.3.x |
| **IoC / DI** | Spring | 2.5.x |
| **ORM / DAO** | Vertigo Dynamo (custom) | – |
| **Reporting** | BIRT | 4.3 |
| **Recherche** | Elasticsearch (embedded) | 7.x (via Vertigo) |
| **Base de données** | PostgreSQL | 14 (Docker) |
| **Conteneurisation** | Docker, Docker‑Compose | 20.10+, 2.22 |
| **Gestion de code** | Git / GitLab | – |
| **Qualité** | SonarQube | – |
| **Supervision** | Prometheus / Grafana / AlertManager | – |
| **CI/CD** | GitLab CI | – |

### 5.2 Outils de la forge logicielle  

| Outil | Usage |
|-------|-------|
| `mvn clean package` | Construction du WAR (`sireines-web-*.war`) |
| `docker build -t sireines-app .` | Création de l’image applicative |
| `docker‑compose up -d` | Lancement des containers (app, db, pgadmin) |
| `gitlab‑ci.yml` | Pipeline CI (build → test → image) |
| `sonar‑project.properties` | Analyse qualité SonarQube |
| `docker‑compose.yml` (dans `sireines_pgadmin`) | Orchestration des trois containers et des volumes persistants |
| `docker‑volume create` | Gestion des volumes `sireines_db_sireines_vol` et `sireines_pgadmin_sireines_vol` |
| `pgAdmin` | Administration de la base (GUI) |
| `BIRT Designer` | Création et modification des rapports (`*.rptdesign`) |
| `Talend` | Jobs d’import (CSV → tables) |

---  

## 6️⃣ Vue en briques (C4 L2) <a id="6️⃣-vue‑en‑briques"></a>

```mermaid
graph TB
    subgraph "Docker‑Compose"
        APP[📦 sireines_app_usine_container<br/>Tomcat 7 + WAR]
        DB[📦 sireines_db_usine_container<br/>PostgreSQL 14]
        PGADMIN[📦 sireines_pgadmin_container<br/>pgAdmin 4]
    end
    subgraph "Volumes persistants"
        VDB[(sireines_db_sireines_vol)]
        VPG[(sireines_pgadmin_sireines_vol)]
    end
    APP -->|JDBC| DB;
    APP -->|HTTP (BIRT)| BIRT[🖨 BIRT Engine (embedded)]
    APP -->|REST/HTML| UI[🖥 Struts2 + FreeMarker UI]
    APP -->|Embedded ES| ES[🔎 Elasticsearch (Vertigo)]
    DB --> VDB;
    PGADMIN --> VPG;
    PGADMIN -->|Web UI| DB;
    VDB -.->|Backup AES‑256| BACKUP[🔐 Dump chiffré]
```

*Le diagramme montre les trois containers, leurs volumes, et les dépendances internes.*  

---  

## 7️⃣ Vue d’exécution <a id="7️⃣-vue‑dexécution"></a>

### Scénario critique : **« Import d’un fichier CSV via l’interface « Import » »**

```mermaid
sequencediagram;
    participant Agent as Agent (Web UI)
    participant UI as Struts2/FreeMarker;
    participant S as Sireines‑Web (Servlet)
    participant IS as ImportsServices (Vertigo)
    participant DB as PostgreSQL;
    participant B as BIRT (rapport d’erreur)

    Agent->>UI: Ouvre page ImportFichier.jsp;
    UI->>S: POST /ImportFichier (multipart)
    S->>IS: ImportsServices.importFile(file)
    IS->>DB: INSERT/UPDATE tables (import, logs)
    alt Erreur de validation;
        IS->>B: Génère rapport d’erreur BIRT;
        B->>S: Retour du PDF d’erreur;
        S->>UI: Affiche lien téléchargement;
    else Succès;
        IS->>UI: Retour OK;
    end
    UI->>Agent: Affiche résultat (succès ou rapport)
```

**Points de contrôle qualité**  

* **Sécurité** – le fichier est stocké uniquement en mémoire (`multipart`), aucune écriture sur le disque.  
* **Traçabilité** – chaque import crée une entrée dans `DT_FILE` et `DT_ERREUR`.  
* **Performance** – le traitement est asynchrone : le serveur accepte le fichier, le job s’exécute en arrière‑plan (thread pool).  

---  

## 8️⃣ Vue Déploiement *(standardisée)* <a id="8️⃣-vue‑déploiement"></a>

### Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|------------|----------|--------|----------------|
| **Développement** | Poste de travail (Docker Desktop) | `sireines_app_usine_container` (Tomcat 7) <br> `sireines_db_usine_container` (PostgreSQL) | `localhost` / `127.0.0.1` | Docker‑Compose + volumes locaux (`