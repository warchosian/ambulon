# 📄 Dossier d’Architecture Technique – **Formation Écologie**
> **Projet** : formation‑ecologie  
> **Version** : 0.2.7  
> **Date** : 2026‑04‑27  

[TOC]

---

## 1️⃣ Introduction et objectifs  

### 1.1 Vue d’ensemble (C4‑L1)  
```mermaid
C4Context;
    title System Context – Formation Écologie;
    Enterprise_Boundary(gouv, "Ministère de la Transition écologique") {
        Person(user, "Utilisateur ministériel", "Recherche de formations")
        System(formation, "Portail Formation Écologie", "Application Django de consultation du catalogue RenoiRH")
        System_Ext(renoirh, "RenoiRH", "Système source des données de formation")
        System_Ext(meilisearch, "MeiliSearch", "Moteur de recherche plein‑texte")

    Enterprise_Boundary(gti, "Groupe Technique Informatique (GTI)") {
        System_Ext(db, "PostgreSQL", "Base de données métier")
        System_Ext(infra, "OpenStack/ECO4", "Infrastructure cloud interne")

    user --> formation : Utilise l’interface web;
    formation --> renoirh : Lecture du catalogue (CSV via S3/SFTP)
    formation --> meilisearch : Indexation / requêtes de recherche;
    formation --> db : Persistance des modèles métier;
    formation --> infra : Déploiement (Docker, Nginx)
```

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif | Critère d’acceptation |
|---|----------|------------------------|
| 1 | **Performance de recherche** | Temps de réponse < 200 ms pour les requêtes MeiliSearch, même en période de forte charge. |
| 2 | **Accessibilité** | Conformité RGAA 3.0 + Design System de l’État (DSFR), tests d’accessibilité automatisés. |
| 3 | **Disponibilité** | Service disponible ≥ 99,5 % (SLA) grâce à la redondance Nginx + Docker. |
| 4 | **Sécurité des données** | Aucun accès non‑autorisé aux données publiques, journalisation de toutes les actions critiques. |
| 5 | **Maintenabilité** | Couverture de tests unitaires ≥ 80 %, documentation à jour, CI/CD automatisée. |

---

## 2️⃣ Parties prenantes  

| Rôle | Attente principale |
|------|--------------------|
| **Utilisateurs ministériels** | Recherche rapide et fiable des formations RenoiRH, avec visualisation cartographique. |
| **Groupe Technique Informatique (GTI)** | Exploitation stable, supervision centralisée, mise à jour continue des dépendances. |
| **Maîtrise d’Ouvrage (MOA)** | Conformité fonctionnelle aux besoins métier, respect des exigences légales (RGAA, RGPD). |
| **Développeurs** | Code lisible, tests automatisés, pipeline CI/CD fiable. |
| **Responsable Sécurité (RSSI)** | Garantie de la confidentialité, intégrité et traçabilité des logs. |

---

## 3️⃣ Contraintes  

### 3.1 Contraintes techniques  

* **Framework** : Python 3.11 + Django 4.x (MVT).  
* **Gestion des dépendances** : Poetry (déclaré dans `pyproject.toml`).  
* **Base de données** : PostgreSQL 15.2 (docker‑compose).  
* **Recherche** : MeiliSearch 0.30 (docker).  
* **Frontend** : Templates Django, DSFR (Design System de l’État), Leaflet + Leaflet.markercluster.  
* **Conteneurisation** : Docker + Docker‑Compose (dev et prod).  
* **Reverse‑proxy** : Nginx (pair load‑balanced).  

### 3.2 Contraintes organisationnelles  

* Respect du **processus de livraison continue** du GTI (scripts de sauvegarde, supervision via Portainer & Prometheus/Grafana).  
* Utilisation du **cloud interne ECO4** (OpenStack) – tenant `pnm3`.  

### 3.3 Contraintes de sécurité – modèle D‑I‑C‑T  

| Dimension | Exigence | Implémentation |
|-----------|----------|----------------|
| **Disponibilité** | Le catalogue doit être accessible 24/7. | Redondance Nginx, health‑checks Docker, alerts Prometheus. |
| **Intégrité** | Les données importées depuis RenoiRH doivent rester cohérentes. | Transactions Django, contraintes d’intégrité référentielle, validations modèles (`int_list_validator`). |
| **Confidentialité** | Les seules données exposées sont publiques. | Pas de stockage d’informations sensibles, accès réseau limité aux services internes. |
| **Traçabilité** | Historiser les actions critiques (import, re‑index, admin). | Logs Django → fichier `log/` (module `app/services/log.py`), agrégés dans Loki. |

---

## 4️⃣ Contexte et périmètre  

### 4.1 Contexte métier  

Le portail permet aux agents du ministère de :

* Consulter le **catalogue RenoiRH** (formations, sessions, lieux).  
* Effectuer des **recherches avancées** (texte plein‑texte, filtres par domaine, département).  
* Visualiser les **formations sur une carte** interactive (Leaflet).  

### 4.2 Contexte technique  

| Élément | Description |
|---------|-------------|
| **Application Django** (`app/`) | Modèles métier (`Stage`, `Session`, `Periode`, `Domaine`, `SousDomaine`, `Theme`, `Departement`, `Partenaire`, `BandeauAccueil`, `Article`, `Subscriber`, `Subscription`). |
| **Gestion des imports** | Cron `import_cisirh.py` récupère les CSV depuis S3, les parse (`parse_*`), les persiste, puis déclenche le re‑index. |
| **Recherche** | MeiliSearch indexe les entités `Stage` et `Session` via `app/services/reindex.py`. |
| **Frontend** | Templates Django, DSFR, Leaflet + Leaflet.markercluster (static assets). |
| **Supervision** | Portainer, Prometheus/Grafana/Loki/AlertManager, supervision PSIN. |
| **Sauvegarde** | Dumps PostgreSQL chiffrés AES‑256, stockés sur B3, Outscale SecNumCloud et Google Cloud. |

---

## 5️⃣ Stratégie de solution  

### 5.1 Décisions architecturales majeures  

| Décision | Raison |
|----------|--------|
| **Monolithe Django (MVT)** | Simplicité de déploiement, cohérence avec l’héritage du projet, pas besoin d’orchestration micro‑services. |
| **MeiliSearch** comme moteur de recherche dédié | Temps de réponse très faible, configuration minimale, compatible Docker. |
| **Indexation asynchrone (cron)** | Découplage du traitement lourd d’import des requêtes utilisateurs. |
| **Utilisation de Leaflet.markercluster** | Gestion efficace du clustering de centaines de points sur la carte. |
| **Docker + Docker‑Compose** | Environnements reproducibles (dev, prod). |
| **Poetry** pour la gestion des paquets | Verrouillage des versions, reproducibilité. |

### 5.2 Environnement technologique  

| Catégorie | Technologie / Version |
|-----------|-----------------------|
| **Langage** | Python 3.11.7 |
| **Framework** | Django 4.2.x |
| **Base de données** | PostgreSQL 15.2‑alpine |
| **Recherche** | MeiliSearch 0.30 |
| **Conteneurs** | Docker 23.x, Docker‑Compose 2.27 |
| **Reverse‑proxy** | Nginx 1.24 (pair load‑balanced) |
| **Frontend** | HTML + Jinja (Django), DSFR v2, Leaflet 1.9, Leaflet.markercluster 1.4.1 |
| **CI/CD** | GitLab CI, Makefile (raccourcis), Poetry |
| **Supervision** | Prometheus 2.x, Grafana 10.x, Loki 2.x, AlertManager, Portainer |
| **Sécurité** | TLS terminée au niveau Nginx, logs chiffrés, sauvegardes AES‑256 |

### 5.3 Forge logicielle – CI/CD  

* **Pipeline GitLab** (déclenché à chaque push) : lint (`flake8`), tests (`pytest`), build Docker images, déploiement sur l’environnement de staging.  
* **Makefile** fournit les cibles suivantes : `run`, `migrations`, `migrate`, `superuser`, `emptydb`, `runcrons`, `loaddb`, `reindexall`.  
* **Poetry** gère les dépendances et crée l’environnement virtuel *in‑project*.  

---

## 6️⃣ Vue en Briques (C4‑L2)  

```mermaid
C4Container;
    title Container Diagram – Formation Écologie;
    Enterprise_Boundary(gouv, "Ministère") {
        Person(user, "Utilisateur")
        Container(web, "Django Web App", "Python/Django", "Gestion du MVT, API, Authentification")
        ContainerDb(db, "PostgreSQL", "Base de données relationnelle", "Persist les modèles métier")
        Container(search, "MeiliSearch", "Moteur de recherche plein‑texte", "Indexe Stage & Session")
        Container(static, "Nginx", "Reverse‑proxy + serveur static", "Expose /static, /media, TLS termination")

    Rel(user, web, "Interaction UI (HTTPS)")
    Rel(web, db, "ORM (SQL)")
    Rel(web, search, "API HTTP – Indexation / Recherche")
    Rel(web, static, "Serve static assets")
    Rel(static, web, "Proxy HTTP (127.0.0.1_8000)")
```

### 6.1 Principaux conteneurs  

| Conteneur | Responsabilité | Principaux modules |
|-----------|----------------|--------------------|
| **Django Web App** | Logique métier, API, rendu HTML | `app/models/*`, `app/views/*`, `app/services/*`, `app/templatetags/*`, `formation/settings.py` |
| **PostgreSQL** | Persistance des entités métier | Tables générées par les migrations (`Stage`, `Session`, `Periode`, etc.) |
| **MeiliSearch** | Indexation plein‑texte, recherche ultra‑rapide | `app/services/reindex.py` (indexation), `app/views/search_with_map.py` (requêtes) |
| **Nginx** | Reverse‑proxy, SSL, gestion des fichiers statiques | `deploy/vhost.conf` |
| **Cron / Management Commands** | Import quotidien de RenoiRH, nettoyage, re‑index | `app/management/commands/import_cisirh.py`, `app/services/cleanup.py` |

---

## 7️⃣ Vue Exécution  

### 7.1 Scénario 1 – Import & indexation quotidienne des données RenoiRH  

```mermaid
sequencediagram;
    participant Cron as "Cron (Import RenoiRH)"
    participant Django as "Django (app/management)"
    participant DB as "PostgreSQL"
    participant Search as "MeiliSearch"
    participant Log as "Fichier log"

    Cron->>+Django: lance `import_cisirh` (S3 → tmp CSV)
    Django->>+DB: persiste les modèles (Stage, Session, Periode, …)
    DB-->>-Django: ACK;
    Django->>+Search: re‑index (stages & sessions)
    Search-->>-Django: confirmation;
    Django->>+Log: écrit log d’import + indexation;
    Log-->>-Django: OK
```

### 7.2 Scénario 2 – Recherche utilisateur (interface web)  

```mermaid
sequencediagram;
    participant User as "Navigateur"
    participant Front as "Frontend (HTML/JS)"
    participant Meili as "MeiliSearch"
    participant Django as "Django (detail API)"
    participant DB as "PostgreSQL"

    User->>+Front: saisit texte + filtres;
    Front->>+Meili: requête `/indexes/stage/search?...`
    Meili-->>-Front: résultats (JSON)
    Front->>+Django: demande détails d’une formation (id)
    Django->>+DB: SELECT * FROM stage WHERE id=…
    DB-->>-Django: enregistrement;
    Django-->>-Front: HTML détaillé;
    Front-->>User: affichage résultat
```

---

## 8️⃣ Vue Déploiement *(section standardisée)*  

### 8.1 Environnements  

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|-----------------|
| **Développement** | Docker‑Compose local | 1 conteneur Django, 1 PostgreSQL, 1 MeiliSearch | `127.0.0.1` (ports 8000, 5432, 7700) | Hot‑reload (`DEBUG=True`), données de test. |
| **Recette** | Cloud interne ECO4 (tenant `pnm3`) | 2 conteneurs (Django + DB) + MeiliSearch dédié | VLAN interne, accès restreint aux équipes QA | Jeux de données anonymisées, sauvegarde quotidienne. |
| **Production** | Cloud interne ECO4 (tenant `pnm3`) | 2 conteneurs (Django + DB) + MeiliSearch haute disponibilité | Load‑balanced Nginx (pair), TLS cert‑managed, monitoring complet | Sauvegarde chiffrée AES‑256, sauvegarde multi‑site (B3, Outscale, GCP). |

### 8.2 Infrastructure  

Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant **`pnm3`** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx (load‑balanced)] --> B[Django App (Docker)]
    B --> C[PostgreSQL]
    B --> D[MeiliSearch]
```

### 8.3 Supervision  

Le produit est supervisé via le système standard du GTI :

* **Portainer** – gestion et suivi des conteneurs.  
* **Stack Prometheus / Grafana / Loki / AlertManager** – métriques, tableaux de bord, logs agrégés, alertes.  
* **Supervision PSIN** – monitoring de la disponibilité réseau et des services critiques.  

### 8.4 Sauvegardes  

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

* le **stockage objet B3** du IaaS ministériel,  
* le **stockage objet Outscale SecNumCloud** (via la prestation « Nuage Public » du GTI),  
* le **stockage objet Google Cloud** (via la même prestation « Nuage Public »).  

---

## 9️⃣ Sujets transverses  

* **Authentification** – Utilisation du backend `django-cas-ng` (non affiché dans le code mais présent dans `pyproject.toml`).  
* **Journalisation** – `app/services/log.py` crée des fichiers journaux journalier, agrégés dans Loki.  
* **Gestion des erreurs** – Vues `error403`, `error404`, `error500` avec affichage du nom d’utilisateur.  
* **API REST** – Endpoint `sousdomaine_api.py` (CSRF‑exempt) renvoie les sous‑domaines d’un domaine.  
* **Gestion des imports** – Cron `import_cisirh` + scripts `cleanup.py` pour la suppression des fichiers temporaires.  
* **Internationalisation** – Aucun texte hard‑coded n’est traduit ; futur axe d’évolution.  

---

## 🔟 Exigences de qualité  

| Exigence | Méthode de validation | Critère d’acceptation |
|----------|-----------------------|-----------------------|
| **Performance de recherche** | Tests de charge (`locust` ou `k6`) sur l’API MeiliSearch | 95 % des requêtes < 200 ms en charge normale. |
| **Conformité RGAA** | Audit Lighthouse + outils RGAA (e.g. *wave*, *axe*) | Score ≥ 95 % sur toutes les pages publiques. |
| **Sécurité des communications** | Scan SSL (testssl.sh) et tests d’injection | TLS 1.2+ avec cipher suites fortes, aucune vulnérabilité OWASP Top 10. |
| **Intégrité des données** | Tests d’intégrité post‑import (checksum, row‑count) | Aucun écart entre CSV source et tables PostgreSQL. |
| **Couverture de tests** | `pytest --cov=app` | ≥ 80 % de couverture sur le code métier (`models`, `services`, `views`). |
| **Disponibilité** | Monitoring Prometheus + alertes | Aucune alerte de downtime > 5 min sur 30 jours. |

---

## 1️⃣1️⃣ Risques et dettes techniques  

| Risque / Dette | Impact | Probabilité | Mesure d’atténuation |
|----------------|--------|-------------|----------------------|
| **Documentation de l’indexation MeiliSearch** (dette) | Difficulté à reproduire le processus d’import en cas d’incident. | Moyen | Rédiger un ADR détaillé, automatiser la génération de rapports d’indexation. |
| **Dépendance à un seul moteur de recherche** (risque) | Si MeiliSearch devient indisponible, la recherche est bloquée. | Faible | Mettre en place un fallback vers PostgreSQL full‑text search (future évolution). |
| **Gestion des versions de dépendances** (dette) | Incompatibilités lors de la mise à jour de Django ou MeiliSearch. | Moyen | Utiliser Poetry lock, tests CI à chaque bump de version. |
| **Sécurité du endpoint CSRF‑exempt** (risque) | Possibilité d’abus de l’API `sousdomaine_api`. | Faible | Restreindre l’accès par token ou par whitelist d’IP interne. |
| **Scalabilité du conteneur Django** (risque) | Augmentation du nombre d’utilisateurs peut saturer le worker WSGI. | Moyen | Configurer le nombre de workers Gunicorn en fonction du CPU, prévoir horizontal scaling via Docker Swarm/K8s. |
| **Gestion du singleton `BandeauAccueil`** (dette) | Migration ou fixture mal gérée peut créer plusieurs instances. | Faible | Ajouter une contrainte d’unicité au niveau DB (`UniqueConstraint(fields=['pk'])`). |

---

## 1️⃣2️⃣ Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **RenoiRH** | Référentiel national des offres de formation RH, source des données de catalogue. |
| **DSFR** | Design System de l’État Français, ensemble de composants UI et de règles d’accessibilité. |
| **GTI** | Groupe Technique Informatique – responsable de l’infrastructure et de la supervision. |
| **ECO4** | Cloud interne du ministère, basé sur OpenStack. |
| **MeiliSearch** | Moteur de recherche full‑text open‑source, optimisé pour la rapidité. |
| **S3** | Service de stockage objet (utilisé ici comme dépôt de fichiers CSV). |
| **Cron** | Planificateur de tâches Unix, utilisé pour les imports et le re‑index. |
| **ADR** | Architectural Decision Record – documentation des décisions d’architecture. |
| **RGAA** | Référentiel Général d’Amélioration de l’Accessibilité – exigences d’accessibilité web. |
| **PSIN** | Plateforme de Supervision d’Infrastructure Nationale. |

### 12.2 Décisions d’architecture – ADR  

| ADR | Sujet | Décision | Raison |
|-----|-------|----------|---------|
| **ADR‑001** | **Moteur de recherche** | Adoption de **MeiliSearch** plutôt qu’Elasticsearch. | Simplicité d’intégration, faible empreinte Docker, performances suffisantes pour le volume de données. |
| **ADR‑002** | **Structure du projet** | Monolithe Django (MVT) au lieu de micro‑services. | Cohérence avec l’héritage existant, moindre complexité d’orchestration. |
| **ADR‑003** | **Gestion des imports** | Cron + commande `import_cisirh` + scripts `cleanup`. | Découplage du traitement lourd, fiabilité via logs et re‑index. |
| **ADR‑004** | **Supervision** | Stack Prometheus/Grafana/Loki + Portainer. | Outils standards du GTI, visibilité centralisée. |
| **ADR‑005** | **Gestion des dépendances** | Utilisation de **Poetry**. | Verrouillage précis des versions, isolation du virtual‑env. |
| **ADR‑006** | **Sécurité du endpoint API** | CSRF‑exempt uniquement pour `sousdomaine_api`. | Nécessité fonctionnelle (appel AJAX interne), mitigé par restriction réseau interne. |
| **ADR‑007** | **Singleton `BandeauAccueil`** | Enforce `pk=1` et désactive `delete()`. | Garantir l’existence d’un seul bandeau d’accueil configurable via l’admin. |

---

*Document généré automatiquement le 27 avril 2026 à partir de l’analyse du code source, des fichiers de configuration et du wiki existant.*  