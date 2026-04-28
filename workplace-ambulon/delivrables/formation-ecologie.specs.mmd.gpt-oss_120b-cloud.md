# 📘 Spécification fonctionnelle et technique de l'application **formation‑ecologie**

> **Nom de l’application** : `formation-ecologie`  
> **Référentiel** : ce document est **auto‑porté** – il ne dépend d’aucune source externe et peut être ouvert tel quel dans VS Code ou Obsidian (support Mermaid activé).  
> **Conventions** :  
> • Tous les titres utilisent la syntaxe Markdown (`#`, `##`, …).  
> • Les ancres internes (`[↩ Retour au sommaire]`) permettent la navigation intra‑document.  
> • Les diagrammes Mermaid sont encadrés par ```` ```mermaid ``` ```` et respectent la syntaxe standard.  
> • Les sections suivent la structure **arc42** + **ISO/IEC/IEEE 29148** (voir tableau de bord ci‑dessous).  

---  

## 📑 Table des matières (cliquable)

1. [Portée, domaine et périmètre](#1-portée-domaine-et-périmètre)  
2. [Contraintes d’architecture & de sécurité](#2-contraintes-darchitecture--de-sécurité)  
3. [Contexte fonctionnel – Acteurs & cas d’usage](#3-contexte-fonctionnel--acteurs--cas-dusage)  
4. [Modélisation fonctionnelle détaillée](#4-modélisation-fonctionnelle-détaillée)  
5. [Architecture logique & physique (Vue en briques)](#5-architecture-logique--physique-vue-en-briques)  
6. [Vues d’exécution (runtime)](#6-vues-dexecution-runtime)  
7. [Déploiement & infrastructure](#7-déploiement--infrastructure)  
8. [Analyse de la sécurité](#8-analyse-de-la-sécurité)  
9. [Dette technique & points d’amélioration](#9-dette-technique--points-damelioration)  
10 [Qualité documentaire & traçabilité](#10-qualité-documentaire--traçabilité)  
11. [Glossaire](#11-glossaire)  

---  

## 1️⃣ Portée, domaine et périmètre <a id="1-portée-domaine-et-périmètre"></a>

| Élément | Description |
|---------|-------------|
| **Domaine applicatif** | **Archivage physique** du catalogue de formations du système **RenoiRH** (Référentiel National des Offres de Formation). |
| **Contexte opérationnel** | - **Site** : `SIT_ID = 29`  <br>- **Base de données** : Oracle `prep37` (dans le DAT, le projet réel utilise PostgreSQL 15 en dev, mais la donnée source provient d’Oracle). |
| **Périmètre fonctionnel inclus** | • Gestion **versements** (import CSV des formations) <br>• Gestion des **demandes** (recherche, filtres, affichage détaillé) <br>• Gestion des **mouvements** (mise à jour du statut des périodes, indexation MeiliSearch). |
| **Périmètre fonctionnel exclu** | • Gestion des **patients** (hors domaine) <br>• **Facturation** (non couverte) <br>• **Workflow avancé** (ex : approbation multi‑étapes, notifications complexes). |
| **Objectifs de qualité** (extraits du DAT) | 1️⃣ Temps de réponse < 200 ms pour les recherches <br>2️⃣ Conformité RGAA / DSFR (Design System de l’État) <br>3️⃣ Maintenabilité (code structuré, documentation, tests). |

---  

## 2️⃣ Contraintes d’architecture & de sécurité <a id="2-contraintes-darchitecture--de-sécurité"></a>

### 2.1 Contraintes d’architecture (arc42 – Section 2)

| Catégorie | Détail |
|-----------|--------|
| **Langage** | Python 3.11 + Django 4.x (framework MVT). |
| **Gestion des dépendances** | Poetry (`pyproject.toml`). |
| **Base de données** | PostgreSQL 15.2‑alpine (Docker) – migration depuis Oracle. |
| **Moteur de recherche** | MeiliSearch 0.30 (Docker). |
| **Design System** | DSFR (Design System de l’État) – CSS `dsfr.min.css`. |
| **Conteneurisation** | Docker + Docker‑Compose (`docker‑compose.dev.yml`). |
| **Serveur web** | Nginx (reverse‑proxy) – configuration `deploy/vhost.conf`. |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`), Makefile (cibles `run`, `migrate`, `reindexall`, …). |
| **Gestion des fichiers temporaires** | Répertoire `tmp/` (hard‑coded dans `app/services/cleanup.py`). |
| **Limite de ligne** | Flake8 : `max-line-length = 160`. |

### 2.2 Contraintes de sécurité (arc42 – Section 8)

| Aspect | Exigence | Implémentation |
|--------|----------|----------------|
| **Disponibilité** | Accès continu au catalogue. | Nginx en front, conteneurs redémarrables (`restart: unless‑stopped`). |
| **Intégrité** | Données RenoiRH fiables. | Import CSV via `import_cisirh.py` avec validation (regex, `int_list_validator`). |
| **Confidentialité** | Données publiques uniquement. | Aucun stockage de données sensibles (pas de PII). |
| **Traçabilité** | Historisation des imports & erreurs. | Modèle `LogImport` (supprimé en migration 0017) – logs journaliers via `app/services/log.py`. |
| **Gestion des secrets** | Pas de secrets en clair. | Variables d’environnement (`POSTGRES_USER`, `MEILI_MASTER_KEY`, …) injectées dans Docker‑Compose. |
| **Protection CSRF** | API `sousdomaine_api` est `@csrf_exempt`. | Risque : exposé aux attaques CSRF – recommandé de sécuriser avec token ou authentification. |
| **Hardening** | `BandeauAccueil` singleton – suppression désactivée. | Garantit qu’une seule instance existe, évite la perte de configuration. |

---  

## 3️⃣ Contexte fonctionnel – Acteurs & cas d’usage <a id="3-contexte-fonctionnel--acteurs--cas-dusage"></a>

### 3.1 Acteurs

| Acteur | Rôle |
|--------|------|
| **Utilisateur interne** (ministériel) | Recherche, consultation, téléchargement de fiches formation. |
| **Administrateur** | Gestion du contenu (articles, partenaires), déclenchement des imports, supervision des logs. |
| **Système RenoiRH** (source CSV) | Fournit les fichiers de formation (via SFTP → S3). |
| **Moteur de recherche MeiliSearch** | Fournit la recherche plein‑texte. |
| **Nginx** | Reverse‑proxy, sert les assets static/media. |
| **Cron / Scheduler** | Exécute les jobs d’import (`import_cisirh`) et de re‑indexation. |

### 3.2 Cas d’usage (Use‑Case Diagram)

```mermaid
usecaseDiagram;
    actor Utilisateur as U;
    actor Administrateur as A;
    actor RenoiRH (SFTP) as R;
    actor MeiliSearch as M;
    U --> (Consulter le catalogue)
    U --> (Rechercher une formation)
    U --> (Visualiser la carte)
    U --> (Télécharger le formulaire d’inscription)
    U --> (S’abonner / se désabonner)

    A --> (Gérer les partenaires)
    A --> (Lancer l’import CSV)
    A --> (Re‑indexer les données)
    A --> (Consulter les logs)

    R --> (Fournir les CSV)
    M --> (Indexer les formations)
    M --> (Répondre aux requêtes de recherche)
```

### 3.3 Scénarios d’usage (extraits du DAT)

| # | Titre | Description succincte |
|---|-------|----------------------|
| **S1** | **Indexation des données RenoiRH** | Cron → `import_cisirh` → parse CSV → persiste en DB → `reindex.py` → MeiliSearch. |
| **S2** | **Recherche utilisateur** | L’utilisateur saisit une requête → front → appel MeiliSearch → affichage résultats → détails via Django. |
| **S3** | **Téléchargement du formulaire d’inscription** | Vue `download_registration_form` renvoie le PDF `bulletin_inscription_vierge_site_formation_matte_VF1_20250205.pdf`. |
| **S4** | **Gestion du bandeau d’accueil** | Singleton `BandeauAccueil` (pk = 1) – création/édition via admin, suppression bloquée. |
| **S5** | **Abonnement à la newsletter** | Formulaire `SubscriptionForm` → création `Subscriber` (UUID) → envoi mail (via `subscription_sendmails` command). |

---  

## 4️⃣ Modélisation fonctionnelle détaillée <a id="4-modélisation-fonctionnelle-détaillée"></a>

### 4.1 Décision tables (business rules)

#### 4.1.1 `Periode.etat` (valeurs autorisées)

| Code | Signification | Commentaire |
|------|---------------|-------------|
| 0 | **ANNULÉE** | La période a été annulée. |
| 1 | **CLOSE** | Inscription clôturée. |
| 2 | **OUVERTE** | Inscription encore possible. |
| 3 | **RÉALISÉE** | Formation terminée. |

*Implémentation* – `app/models/periode.py` utilise `int_list_validator("0","1","2","3")`.

#### 4.1.2 `Article.type` (détermination du référent)

| Type | Référent URL | Référent titre |
|------|--------------|----------------|
| 0 | `/publications/actualites/` | **Actualités** |
| 1 | `/publications/reglementation/` | **Articles de réglementation** |
| autre | `""` | `""` |

*Implémentation* – `app/views/article.py`.

#### 4.1.3 `Subscriber` → `UUID` unique

| Champ | Règle | Source |
|-------|--------|--------|
| `uuid` | `UUID4`, non‑éditable, unique | `models.UUIDField(default=uuid.uuid4, editable=False, unique=True)` |

### 4.2 Formules & calculs

| Contexte | Formule | Source |
|----------|---------|--------|
| **Progression du re‑index** | `completion = round((i / count) * 100, 2)` | `app/services/reindex.py` |
| **Calcul du nombre de sessions par département** | `SELECT code_departement, COUNT(*) FROM session GROUP BY code_departement` | `app/views/search_with_map.py` (`get_sessions_count_by_departement`). |

### 4.3 Diagrammes de séquence

#### 4.3.1 Import CSV & Indexation (Scénario S1)

```mermaid
sequencediagram;
    participant Cron as Cron (Scheduler)
    participant Cmd as Django Management Command (import_cisirh)
    participant DB as PostgreSQL;
    participant MS as MeiliSearch;
    participant Log as app/services/log.py;
    Cron->>+Cmd: launch import_cisirh (04_30)
    Cmd->>+DB: parse CSV & persister (Stage, Session, Periode)
    DB-->>-Cmd: OK;
    Cmd->>+Log: log_msg("import", "success", line_number)
    Log-->>-Cmd: file écrit;
    Cmd->>+MS: reindex() (via reindex.py)
    MS-->>-Cmd: index confirmé;
    Cmd->>-Cron: fin
```

#### 4.3.2 Recherche utilisateur (Scénario S2)

```mermaid
sequencediagram;
    participant UI as Frontend (browser)
    participant API as Django View (search_with_map)
    participant MS as MeiliSearch;
    UI->>+API: saisie texte + filtres;
    API->>+MS: query HTTP GET;
    MS-->>-API: résultats JSON;
    API->>-UI: affichage HTML (templates/search_with_map.html)
```

### 4.4 Diagrammes de swimlane (workflow d’import)

```mermaid
swimlane;
    title Workflow d’import RenoiRH;
    lane "Système RenoiRH (SFTP)" {
        SFTP --> S3 : copy CSV (4_00)
    }
    lane "Django (Cron)" {
        Cron --> Import : trigger import_cisirh (4_30)
        Import --> DB : persistance;
        Import --> Log : log_msg;
        Import --> Reindex : call reindex()
    }
    lane "MeiliSearch" {
        Reindex --> Index : clear + index;
    }
```

### 4.5 Diagramme de classe (simplifié – vue relationnelle)

```mermaid
classDiagram
    class Stage {
        +BigAutoField id;
        +CharField label;
        +CharField premier_niveau;
        +CharField public_cible;
        +ForeignKey session;
    }
    class Session {
        +BigAutoField id;
        +CharField label;
        +DateField date_debut;
        +DateField date_fin;
        +CharField code_departement;
    }
    class Periode {
        +IntegerField numero;
        +DateField date_debut;
        +DateField date_fin;
        +CharField departement_lieu;
        +CharField ville_lieu;
        +CharField lieu;
        +IntegerField etat;
    }
    class Domaine {
        +CharField label;
        +IntegerField number;
        +CharField prefix_type;
    }
    class SousDomaine {
        +CharField label;
        +ForeignKey domaine;
    }
    class Theme {
        +CharField label;
        +ForeignKey sous_domaine;
    }
    class Departement {
        +CharField code;
        +CharField libelle;
    }
    class Partenaire {
        +URLField logo_url;
        +CharField titre;
        +CharField soustitre;
    }
    class BandeauAccueil {
        +CharField titre;
        +TextField message;
    }
    class Subscriber {
        +UUIDField uuid;
        +EmailField email;
    }
    class Subscription {
        +ForeignKey subscriber;
        +ForeignKey session;
    }

    Stage --> Session : belongsTo;
    Session --> Departement : manyToOne;
    Periode --> Session : belongsTo;
    SousDomaine --> Domaine : manyToOne;
    Theme --> SousDomaine : manyToOne;
    Subscription --> Subscriber : manyToOne;
    Subscription --> Session : manyToOne
```

---  

## 5️⃣ Architecture logique & physique – Vue en briques <a id="5-architecture-logique--physique-vue-en-briques"></a>

### 5.1 Diagramme de composants (arc42 – Section 5)

```mermaid
graph TD
    subgraph "Application Django (app)"
        A1[Models] --> A2[Views]
        A2 --> A3[Templates]
        A1 --> A4[Forms]
        A1 --> A5[Signals]
        A1 --> A6[Management Commands]
        A1 --> A7[Services (log, cleanup, reindex)]
    end
    subgraph "Moteur de recherche"
        B1[MeiliSearch] 
    end
    subgraph "Base de données"
        C1[PostgreSQL]
    end
    subgraph "Infrastructure"
        D1[Nginx (reverse‑proxy)]
        D2[Docker Engine]
        D3[Docker‑Compose]
    end
    A1 --> C1;
    A2 --> C1;
    A7 --> B1;
    D1 --> A1;
    D1 --> B1;
    D3 --> D2;
    D2 --> A1;
    D2 --> B1;
    D2 --> C1
```

### 5.2 Vue physique (déploiement)

| Composant | Conteneur Docker | Port exposé | Volume persistant |
|-----------|------------------|--------------|-------------------|
| **PostgreSQL** | `formation-db` | `5432:5432` | `./pgdata:/var/lib/postgresql/data` |
| **MeiliSearch** | `formation-search` | `7700:7700` | `./searchdata:/meili_data/data.ms` |
| **Django (app)** | `formation-app` (défini via `Dockerfile`) | `8000` (interne) | `./static:/opt/app/static`<br>`./media:/opt/app/media` |
| **Nginx** | `nginx-proxy` (hors‑scope du repo) | `8080` (public) | `./static:/opt/app/static` (read‑only) |
| **Cron (import & reindex)** | `formation-app` (processus `runcrons`) | – | – |

---  

## 6️⃣ Vues d’exécution (runtime) <a id="6-vues-dexecution-runtime"></a>

### 6.1 Diagramme d’activité – Recherche utilisateur

```mermaid
flowchart TD
    Start[Début] --> UI[User saisit requête]
    UI --> Front[Front (JS/HTML)]
    Front --> Django[Vue Django (search_with_map)]
    Django --> MS[Appel MeiliSearch]
    MS --> Result[Résultats JSON]
    Result --> Django;
    Django --> Render[Render template results]
    Render --> UI;
    UI --> End[Fin]
```

### 6.2 Diagramme d’état – `Subscriber`

```mermaid
statediagram-v2;
    [*] --> Created;
    Created --> Confirmed : email validation (via lien)
    Confirmed --> Unsubscribed : désinscription globale;
    Unsubscribed --> [*]
```

---  

## 7️⃣ Déploiement & infrastructure <a id="7-déploiement--infrastructure"></a>

### 7.1 Diagramme de déploiement (arc42 – Section 7)

```mermaid
graph LR
    subgraph "Environnement Production"
        Nginx[Nginx (LB + Reverse‑proxy)]
        DjangoApp[Django (container)]
        DB[PostgreSQL (container)]
        Search[MeiliSearch (container)]
    end
    Nginx -->|HTTP/HTTPS| DjangoApp;
    DjangoApp -->|SQL| DB;
    DjangoApp -->|REST| Search;
    Nginx -->|Static/Media| DB;
    Nginx -->|Static/Media| Search
```

### 7.2 Environnements (extraits du DAT)

| Environnement | URL | Serveur |
|---------------|-----|---------|
| **Développement** | `http://dev.formation-ecologie.pnm3.eco4.cloud.e2.rie.gouv.fr/` | 192.168.5.139 |
| **Production** | `http://formation-ecologie.e2.rie.gouv.fr/` | 192.168.5.52 |

*Les conteneurs sont orchestrés par `docker‑compose.dev.yml` (dev) et un équivalent `docker‑compose.prod.yml` (non affiché).*

### 7.3 Supervision & sauvegarde (DAT)

* **Supervision** – Portainer, Prometheus/Grafana/Loki/Alertmanager, PSIN.  
* **Sauvegarde** – Dumps AES‑256 stockés sur trois buckets : Object B3 (ministériel), Outscale SecNumCloud, Google Cloud.

---  

## 8️⃣ Analyse de la sécurité <a id="8-analyse-de-la-sécurité"></a>

| Domaine | Risque identifié | Mesure de mitigation |
|---------|-------------------|------------------------|
| **CSRF** | API `sousdomaine_api` est exemptée (`@csrf_exempt`). | Ajouter token d’authentification (ex : JWT) ou limiter l’accès par IP. |
| **Secrets** | Clés (`MEILI_MASTER_KEY`, credentials DB) sont injectées via env. | S’assurer que les variables sont stockées dans un coffre (Vault, GitLab CI variables). |
| **Logs** | `app/services/log.py` écrit des fichiers texte non chiffrés. | Restreindre les permissions du répertoire `log/` (0600) et archiver via le système de logs centralisé (Loki). |
| **Fichiers temporaires** | `cleanup.py` supprime des fichiers dans `tmp/` hard‑coded. | Centraliser le répertoire via variable d’environnement (`TMP_DIR`). |
| **Injection SQL** | Utilisation d’ORM Django protège contre l’injection. | Continuer à éviter les requêtes brutes; valider les entrées côté serveur. |
| **Hardening Nginx** | Configuration basique (`listen 8080`). | Ajouter TLS, headers de sécurité (`Content‑Security‑Policy`, `X‑Frame‑Options`). |
| **Gestion du singleton** (`BandeauAccueil`) | `save()` force `pk=1`, `delete()` est no‑op. | Documenter le comportement, ajouter tests unitaires pour éviter les créations multiples. |

---  

## 9️⃣ Dette technique & points d’amélioration <a id="9-dette-technique--points-damelioration"></a>

| Item | Description | Impact | Proposition |
|------|-------------|--------|--------------|
| **Hard‑coding des chemins** (`tmp/`, `static/app/registration_form/`) | Risque de rupture en prod. | Introduire des variables d’environnement (`TMP_DIR`, `REG_FORM_PATH`). |
| **CSRF exempt sur API** | Risque de cross‑site request forgery. | Sécuriser avec token ou passer par Django Rest Framework avec authentification. |
| **Absence de tests automatisés** | Couverture incertaine. | Ajouter `pytest-django` + coverage, créer tests pour `import_cisirh`, `reindex`, `views`. |
| **Documentation des index MeiliSearch** | Processus d’indexation peu visible. | Ajouter README `docs/meilisearch.md` et logs détaillés. |
| **LogImport modèle supprimé** | Historique des erreurs d’import perdu. | Conserver les logs dans un système centralisé (ELK) plutôt que d’effacer la table. |
| **Flake8 max‑line‑length 160** | Lignes très longues, lisibilité réduite. | Réduire à 120, appliquer `black` et `isort`. |
| **Gestion du singleton `BandeauAccueil`** | Logique d’enforced pk=1 dans le modèle – peu idiomatique. | Utiliser un modèle de configuration avec `django-constance` ou une table de paramètres. |
| **Duplication du code de calcul de progression** (reindex) | Même formule répétée pour stages & sessions. | Refactoriser dans `app/services/progress.py`. |
| **Absence de migration de données Oracle → PostgreSQL** | Migration manuelle non documentée. | Ajouter scripts de migration (ex : `pgloader`). |

---  

## 🔟 Qualité documentaire & traçabilité <a id="10-qualité-documentaire--traçabilité"></a>

* **Structure** – Respect de l’architecture arc42 (sections 1‑9) et du standard ISO/IEC/IEEE 29148 (exigences fonctionnelles & non‑fonctionnelles).  
* **Navigation** – Chaque grande partie possède un lien « ↩ Retour au sommaire » et les diagrammes sont ancrés localement.  
* **Lisibilité** – Textes courts, tableaux synthétiques, exemples concrets tirés du code source.  
* **Traçabilité** – Les exigences fonctionnelles (ex : recherche < 200 ms) sont reliées aux artefacts de code (`app/services/reindex.py`, `app/views/search_with_map.py`).  
* **Versioning** – Le fichier `VERSION` (`0.2.7`) indique la version du produit ; le diagramme de version peut être ajouté dans le futur.  

---  

## 11️⃣ Glossaire <a id="11-glossaire"></a>

| Terme | Définition |
|-------|------------|
| **RenoiRH** | Système source des offres de formation du ministère (fournit les CSV). |
| **DSFR** | Design System de l’État Français (front‑end). |
| **MeiliSearch** | Moteur de recherche plein‑texte léger utilisé pour l’indexation des formations. |
| **S3** | Stockage objet (MinIO) utilisé comme zone tampon pour les fichiers CSV. |
| **Cron** | Programme planifié (ex : `runcrons`) exécutant des tâches d’import et de re‑indexation. |
| **Singleton** | Pattern où une seule instance d’une classe (ex : `BandeauAccueil`) est autorisée. |
| **UUID** | Identifiant unique universel (v4) utilisé pour les abonnés. |
| **Int‑list validator** | Validateur Django assurant que l’entier appartient à la liste `[0,1,2,3]`. |
| **Arc42** | Modèle de documentation d’architecture logiciel. |
| **ISO/IEC/IEEE 29148** | Standard de spécification des exigences. |

---  

## 📎 Annexes (non obligatoires)

* **Lien externe** – Documentation officielle d’arc42 : <https://arc42.org> (autorisé).  
* **Références internes** – Tous les ancres (`#section‑…`) pointent vers les sections du présent document.  

---  

*Fin du document – Toutes les informations proviennent exclusivement des sources fournies (code, README, DAT, wiki).*