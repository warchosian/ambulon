Je vais analyser le code source fourni pour générer un DAT (Dossier d'Architecture Technique) complet selon le modèle C4.

---

<a id="dossier-darchitecture-technique-dat"></a>
# Dossier d'Architecture Technique (DAT)

## Table des matières

<ul>
<li><a id="toc-application-formation-écologie"></a><a href="#application-formation-écologie">Application Formation-Écologie</a>
</li>
<li><a id="toc-1-introduction-et-objectifs"></a><a href="#1-introduction-et-objectifs">1. Introduction et objectifs</a>
<ul>
<li><a id="toc-vue-densemble"></a><a href="#vue-densemble">Vue d'ensemble</a>
</li>
<li><a id="toc-objectifs-de-qualité-orientés-utilisateur"></a><a href="#objectifs-de-qualité-orientés-utilisateur">Objectifs de qualité orientés utilisateur</a>
</ul>
</li>
<li><a id="toc-2-niveau-1-vue-contexte-system-context"></a><a href="#2-niveau-1-vue-contexte-system-context">2. Niveau 1 — Vue Contexte (System Context)</a>
<ul>
<li><a id="toc-diagramme-c4-l1"></a><a href="#diagramme-c4-l1">Diagramme C4-L1</a>
</li>
<li><a id="toc-acteurs-principaux"></a><a href="#acteurs-principaux">Acteurs principaux</a>
</li>
<li><a id="toc-systèmes-externes"></a><a href="#systèmes-externes">Systèmes externes</a>
</ul>
</li>
<li><a id="toc-3-parties-prenantes"></a><a href="#3-parties-prenantes">3. Parties prenantes</a>
</li>
<li><a id="toc-4-contraintes"></a><a href="#4-contraintes">4. Contraintes</a>
<ul>
<li><a id="toc-contraintes-techniques"></a><a href="#contraintes-techniques">Contraintes techniques</a>
</li>
<li><a id="toc-contraintes-organisationnelles"></a><a href="#contraintes-organisationnelles">Contraintes organisationnelles</a>
</li>
<li><a id="toc-exigences-de-sécurité-modèle-d-i-c-t"></a><a href="#exigences-de-sécurité-modèle-d-i-c-t">Exigences de sécurité (modèle D-I-C-T)</a>
</ul>
</li>
<li><a id="toc-5-niveau-2-vue-conteneurs-containers"></a><a href="#5-niveau-2-vue-conteneurs-containers">5. Niveau 2 — Vue Conteneurs (Containers)</a>
<ul>
<li><a id="toc-diagramme-c4-l2"></a><a href="#diagramme-c4-l2">Diagramme C4-L2</a>
</li>
<li><a id="toc-description-des-conteneurs"></a><a href="#description-des-conteneurs">Description des conteneurs</a>
</li>
<li><a id="toc-décisions-architecturales-majeures"></a><a href="#décisions-architecturales-majeures">Décisions architecturales majeures</a>
</li>
<li><a id="toc-environnement-technologique"></a><a href="#environnement-technologique">Environnement technologique</a>
</li>
<li><a id="toc-forge-logicielle"></a><a href="#forge-logicielle">Forge logicielle</a>
</ul>
</li>
<li><a id="toc-6-niveau-3-vue-composants-components"></a><a href="#6-niveau-3-vue-composants-components">6. Niveau 3 — Vue Composants (Components)</a>
<ul>
<li><a id="toc-diagramme-c4-l3-application-web-django"></a><a href="#diagramme-c4-l3-application-web-django">Diagramme C4-L3 (Application Web Django)</a>
</li>
<li><a id="toc-composants-principaux"></a><a href="#composants-principaux">Composants principaux</a>
</li>
<li><a id="toc-modèle-de-données-simplifié"></a><a href="#modèle-de-données-simplifié">Modèle de données simplifié</a>
</ul>
</li>
<li><a id="toc-7-niveau-4-vue-code-code"></a><a href="#7-niveau-4-vue-code-code">7. Niveau 4 — Vue Code (Code)</a>
</li>
<li><a id="toc-8-vue-exécution-scénarios"></a><a href="#8-vue-exécution-scénarios">8. Vue Exécution (Scénarios)</a>
<ul>
<li><a id="toc-scénario-1-recherche-de-formation-avec-critères"></a><a href="#scénario-1-recherche-de-formation-avec-critères">Scénario 1 : Recherche de formation avec critères</a>
</li>
<li><a id="toc-scénario-2-import-quotidien-des-données-cisirh"></a><a href="#scénario-2-import-quotidien-des-données-cisirh">Scénario 2 : Import quotidien des données CISIRH</a>
</li>
<li><a id="toc-scénario-3-inscription-hors-self-agent"></a><a href="#scénario-3-inscription-hors-self-agent">Scénario 3 : Inscription hors Self-Agent</a>
</ul>
</li>
<li><a id="toc-9-vue-déploiement"></a><a href="#9-vue-déploiement">9. Vue Déploiement</a>
<ul>
<li><a id="toc-diagramme-c4-déploiement"></a><a href="#diagramme-c4-déploiement">Diagramme C4-Déploiement</a>
</li>
<li><a id="toc-environnements"></a><a href="#environnements">Environnements</a>
</li>
<li><a id="toc-infrastructure"></a><a href="#infrastructure">Infrastructure</a>
</li>
<li><a id="toc-supervision"></a><a href="#supervision">Supervision</a>
</li>
<li><a id="toc-sauvegardes"></a><a href="#sauvegardes">Sauvegardes</a>
</ul>
</li>
<li><a id="toc-10-sujets-transverses"></a><a href="#10-sujets-transverses">10. Sujets transverses</a>
<ul>
<li><a id="toc-authentification"></a><a href="#authentification">Authentification</a>
</li>
<li><a id="toc-journalisation"></a><a href="#journalisation">Journalisation</a>
</li>
<li><a id="toc-monitoring"></a><a href="#monitoring">Monitoring</a>
</li>
<li><a id="toc-gestion-des-erreurs"></a><a href="#gestion-des-erreurs">Gestion des erreurs</a>
</li>
<li><a id="toc-api-et-intégrations"></a><a href="#api-et-intégrations">API et intégrations</a>
</ul>
</li>
<li><a id="toc-11-exigences-de-qualité"></a><a href="#11-exigences-de-qualité">11. Exigences de qualité</a>
</li>
<li><a id="toc-12-risques-et-dettes-techniques"></a><a href="#12-risques-et-dettes-techniques">12. Risques et dettes techniques</a>
</li>
<li><a id="toc-13-annexes"></a><a href="#13-annexes">13. Annexes</a>
<ul>
<li><a id="toc-glossaire"></a><a href="#glossaire">Glossaire</a>
</li>
<li><a id="toc-décisions-darchitecture-adr"></a><a href="#décisions-darchitecture-adr">Décisions d'Architecture (ADR)</a>
</li>
</ul>
</li>
</ul>

---

<a id="application-formation-écologie"></a>
## Application Formation-Écologie [↑](#toc-application-formation-écologie)

**[TOC]**

---

<a id="1-introduction-et-objectifs"></a>
## 1. Introduction et objectifs [↑](#toc-1-introduction-et-objectifs)

<a id="vue-densemble"></a>
### Vue d'ensemble [↑](#toc-vue-densemble)
Formation-Écologie est une application web Django permettant la gestion et la consultation de l'offre de formation professionnelle du pôle ministériel MTE (Ministère de la Transition Écologique). L'application offre un portail de recherche de formations, un système d'abonnement par email, et des outils d'administration pour la gestion des contenus.

<a id="objectifs-de-qualité-orientés-utilisateur"></a>
### Objectifs de qualité orientés utilisateur [↑](#toc-objectifs-de-qualité-orientés-utilisateur)
1. **Accessibilité** : Conformité RGAA 4.1.2 (82,35% des critères respectés) pour garantir l'accès à tous les agents
2. **Performance** : Temps de réponse < 2s pour les recherches via indexation MeiliSearch
3. **Maintenabilité** : Architecture modulaire Django avec séparation claire des responsabilités
4. **Sécurité** : Authentification CAS, chiffrement AES-256 des sauvegardes, conformité RGS
5. **Disponibilité** : Hébergement cloud redondant avec supervision 24/7

---

<a id="2-niveau-1-vue-contexte-system-context"></a>
## 2. Niveau 1 — Vue Contexte (System Context) [↑](#toc-2-niveau-1-vue-contexte-system-context)

<a id="diagramme-c4-l1"></a>
### Diagramme C4-L1 [↑](#toc-diagramme-c4-l1)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

LAYOUT_WITH_LEGEND()

Person(agent, "Agent MTE", "Agent du ministère ou extérieur recherchant une formation")
Person(admin, "Administrateur", "Gestionnaire de contenus et formations")
Person(superieur, "Supérieur hiérarchique", "Valide les demandes d'inscription")

System_Boundary(formation_eco, "Formation-Écologie") {
    System(app, "Application Formation-Écologie", "Portail de recherche et gestion des formations")
}

System_Ext(cisirh, "CISIRH", "Système source des données formations (exports CSV)")
System_Ext(self_agent, "Self Agent", "Portail RH pour inscription des agents internes")
System_Ext(api_inscription, "API Inscription", "Service externe pour inscription hors-self")
System_Ext(hedwige, "Hedwige", "Service d'envoi d'emails transactionnels")
System_Ext(cas, "CAS", "Central Authentication Service pour authentification")
System_Ext(meilisearch, "MeiliSearch", "Moteur de recherche full-text")
System_Ext(s3, "Stockage S3", "Stockage objet pour imports et médias")

Rel(agent, app, "Recherche formations, s'abonne", "HTTPS")
Rel(admin, app, "Gère contenus, articles", "HTTPS")
Rel(superieur, app, "Valide inscriptions", "Email")
Rel(app, cisirh, "Importe données formations", "CSV/S3")
Rel(app, self_agent, "Redirection inscription", "HTTPS")
Rel(app, api_inscription, "Soumet inscriptions", "REST/JSON")
Rel(app, hedwige, "Envoie emails", "REST/JSON")
Rel(app, cas, "Authentification", "CAS Protocol")
Rel(app, meilisearch, "Indexe et recherche", "HTTP/7700")
Rel(app, s3, "Stocke fichiers", "S3 API")

@enduml
```

<a id="acteurs-principaux"></a>
### Acteurs principaux [↑](#toc-acteurs-principaux)

| Acteur | Objectif principal |
|--------|-------------------|
| **Agent MTE** | Trouver et s'inscrire à une formation professionnelle adaptée |
| **Agent hors ministère** | S'inscrire via formulaire spécifique (sans accès Self Agent) |
| **Administrateur** | Gérer les articles, bandeaux d'accueil et abonnements |
| **Supérieur hiérarchique** | Valider les demandes de formation de ses collaborateurs |

<a id="systèmes-externes"></a>
### Systèmes externes [↑](#toc-systèmes-externes)

| Système | Type d'interaction | Fréquence | Données échangées |
|---------|-------------------|-----------|-------------------|
| **CISIRH** | Import de données | Quotidien (cron) | CSV Stages, Sessions, Périodes |
| **Self Agent** | Redirection | À la demande | URL avec code stage |
| **API Inscription** | Soumission formulaire | À la demande | JSON inscription hors-self |
| **Hedwige** | Envoi d'emails | Quotidien (cron) + événements | HTML emails, destinataires |
| **CAS** | Authentification | À la connexion | Tickets CAS, attributs utilisateur |
| **MeiliSearch** | Recherche temps réel | Continu | Index sessions, requêtes |
| **S3 (MinIO)** | Stockage fichiers | Import quotidien + uploads | CSV, images, documents |

---

<a id="3-parties-prenantes"></a>
## 3. Parties prenantes [↑](#toc-3-parties-prenantes)

| Rôle | Attente principale |
|------|-------------------|
| **Direction des Ressources Humaines (DRH)** | Offre de formation à jour et accessible à tous les agents |
| **SG/DNUM/DPNM/PNM3** | Hébergement sécurisé, supervision et maintenance |
| **CISIRH** | Fourniture fiable des données formations |
| **Agents du ministère** | Recherche intuitive et inscription simplifiée |
| **Correspondants locaux formation** | Gestion des inscriptions des agents sans Self Agent |
| **RSSI** | Conformité sécurité, chiffrement des données sensibles |

---

<a id="4-contraintes"></a>
## 4. Contraintes [↑](#toc-4-contraintes)

<a id="contraintes-techniques"></a>
### Contraintes techniques [↑](#toc-contraintes-techniques)
- **Stack imposée** : Python 3.11+, Django 4.2 LTS, PostgreSQL 15+
- **Hébergement** : Cloud interne ECO4 (OpenStack), tenant PNM3
- **Conformité DSFR** : Design System de l'État Français obligatoire
- **RGAA 4.1.2** : Accessibilité partielle conforme (82,35%)

<a id="contraintes-organisationnelles"></a>
### Contraintes organisationnelles [↑](#toc-contraintes-organisationnelles)
- **Authentification** : CAS ministériel obligatoire pour agents internes
- **Données personnelles** : Traitement conforme RGPD, conservation limitée
- **Classification** : Données de niveau "diffusion restreinte"

<a id="exigences-de-sécurité-modèle-d-i-c-t"></a>
### Exigences de sécurité (modèle D-I-C-T) [↑](#toc-exigences-de-sécurité-modèle-d-i-c-t)

| Dimension | Exigence | Mesure technique |
|-----------|----------|------------------|
| **Disponibilité** | 99.5% de disponibilité | Supervision Prometheus/Grafana, alerting |
| **Intégrité** | Protection contre altération données | Hash des fichiers importés, logs d'audit |
| **Confidentialité** | Protection données personnelles | Chiffrement AES-256, accès restreints |
| **Traçabilité** | Traçabilité des actions | Logs applicatifs, historique des imports |

---

<a id="5-niveau-2-vue-conteneurs-containers"></a>
## 5. Niveau 2 — Vue Conteneurs (Containers) [↑](#toc-5-niveau-2-vue-conteneurs-containers)

<a id="diagramme-c4-l2"></a>
### Diagramme C4-L2 [↑](#toc-diagramme-c4-l2)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

LAYOUT_WITH_LEGEND()

Person(agent, "Agent", "Utilisateur du portail")
Person(admin, "Admin", "Administrateur Django")

System_Boundary(formation_eco, "Formation-Écologie") {
    Container(web, "Application Web Django", "Python 3.11, Django 4.2", "Portail utilisateurs et API")
    Container(admin_django, "Admin Django", "Python 3.11, Django 4.2", "Interface d'administration")
    Container(celery, "Celery Workers", "Python", "Tâches asynchrones et cron")
    ContainerDb(postgres, "PostgreSQL", "PostgreSQL 15", "Données métier et sessions")
    ContainerDb(meilisearch, "MeiliSearch", "MeiliSearch 1.x", "Index de recherche full-text")
    ContainerDb(redis, "Redis", "Redis 7", "Cache et broker Celery")
    Container(file_storage, "Stockage Fichiers", "S3/MinIO", "Uploads et imports CSV")
}

System_Ext(cas, "CAS", "Authentification centralisée")
System_Ext(hedwige, "Hedwige", "Service emails")
System_Ext(cisirh_s3, "S3 CISIRH", "Source données")

Rel(agent, web, "Utilise", "HTTPS/443")
Rel(admin, admin_django, "Administre", "HTTPS/443")
Rel(web, postgres, "Lit/Écrit", "JDBC/5432")
Rel(web, meilisearch, "Recherche", "HTTP/7700")
Rel(web, redis, "Cache", "Redis/6379")
Rel(web, file_storage, "Stocke fichiers", "S3 API")
Rel(celery, postgres, "Met à jour", "JDBC/5432")
Rel(celery, meilisearch, "Réindexe", "HTTP/7700")
Rel(celery, hedwige, "Envoie emails", "REST")
Rel(celery, cisirh_s3, "Importe données", "S3 API")
Rel(web, cas, "S'authentifie", "CAS")

@enduml
```

<a id="description-des-conteneurs"></a>
### Description des conteneurs [↑](#toc-description-des-conteneurs)

| Conteneur | Technologie | Responsabilité | Port exposé |
|-----------|-------------|----------------|-------------|
| **Application Web Django** | Python 3.11, Django 4.2, Gunicorn | Portail utilisateurs, API REST, rendu templates | 8000 (interne) |
| **Admin Django** | Python 3.11, Django 4.2 | Gestion des articles, abonnements, imports | 8000 (interne) |
| **Celery Workers** | Python, Celery 5.x | Tâches planifiées : import CISIRH, envoi emails, réindexation | - |
| **PostgreSQL** | PostgreSQL 15 | Persistance des données métier (stages, sessions, abonnements) | 5432 |
| **MeiliSearch** | MeiliSearch 1.x | Indexation et recherche full-text des formations | 7700 |
| **Redis** | Redis 7 | Cache Django, broker de messages Celery | 6379 |
| **Stockage S3** | MinIO (compatible S3) | Stockage des fichiers CSV d'import, uploads d'images | 9000 |

<a id="décisions-architecturales-majeures"></a>
### Décisions architecturales majeures [↑](#toc-décisions-architecturales-majeures)

1. **Architecture monolithique Django** : Choix pragmatique pour une équipe réduite, avec séparation logique par modules (models, views, services)
2. **Indexation découplée (MeiliSearch)** : Recherche performante sans surcharge de la base principale, réindexation asynchrone
3. **Import asynchrone des données** : Traitement des fichiers CISIRH via Celery pour éviter blocage du serveur web
4. **Double mode authentification** : CAS pour agents internes, formulaire libre pour agents externes

<a id="environnement-technologique"></a>
### Environnement technologique [↑](#toc-environnement-technologique)

| Couche | Technologie | Version |
|--------|-------------|---------|
| **Langage** | Python | 3.11+ |
| **Framework Web** | Django | 4.2 LTS |
| **ORM** | Django ORM | 4.2 |
| **Moteur de templates** | Django Templates | 4.2 |
| **Frontend** | DSFR (Système de Design de l'État) | 1.14.2 |
| **Cartographie** | Leaflet + MarkerCluster | 1.9.4 / 1.4.1 |
| **Recherche** | MeiliSearch | 1.x |
| **Base de données** | PostgreSQL | 15 |
| **Cache/Message broker** | Redis | 7 |
| **Tâches asynchrones** | Celery | 5.x |
| **Conteneurisation** | Docker | 24.x |
| **Orchestration** | Docker Compose | 2.x |

<a id="forge-logicielle"></a>
### Forge logicielle [↑](#toc-forge-logicielle)

| Outil | Usage |
|-------|-------|
| **GitLab** | Gestion de source, CI/CD |
| **GitLab CI** | Pipeline de build et déploiement |
| **BuildKit** | Construction d'images Docker optimisées |
| **Registry interne** | Stockage des images (registry.gitlab-forge.din...) |
| **Poetry** | Gestion des dépendances Python |
| **Flake8** | Linting code Python |

---

<a id="6-niveau-3-vue-composants-components"></a>
## 6. Niveau 3 — Vue Composants (Components) [↑](#toc-6-niveau-3-vue-composants-components)

<a id="diagramme-c4-l3-application-web-django"></a>
### Diagramme C4-L3 (Application Web Django) [↑](#toc-diagramme-c4-l3-application-web-django)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

LAYOUT_WITH_LEGEND()

Container_Boundary(django_app, "Application Django") {
    Component(urls, "URLs Router", "Django URLs", "Routage des requêtes HTTP")
    Component(views, "Views Layer", "Django Views", "Logique de présentation et contrôleurs")
    Component(forms, "Forms Layer", "Django Forms", "Validation et traitement des formulaires")
    Component(models, "Models Layer", "Django ORM", "Entités métier et persistance")
    Component(services, "Services Layer", "Python Modules", "Logique métier et intégrations")
    Component(search, "Search Module", "MeiliSearch Client", "Indexation et recherche")
    Component(admin, "Admin Interface", "Django Admin", "Interface d'administration")
    Component(templates, "Templates", "HTML/Django Templates", "Rendu des pages web")
    Component(static, "Static Files", "CSS/JS/Images", "Assets statiques (DSFR, Leaflet)")
}

ContainerDb(postgres, "PostgreSQL", "", "Base de données")
ContainerDb(meilisearch, "MeiliSearch", "", "Moteur de recherche")

Rel(views, forms, "Utilise")
Rel(views, models, "Interroge")
Rel(views, services, "Appelle")
Rel(views, search, "Recherche")
Rel(views, templates, "Rend")
Rel(forms, models, "Valide contre")
Rel(services, models, "Manipule")
Rel(services, postgres, "Écrit/Lit")
Rel(search, meilisearch, "Indexe/Recherche")
Rel(models, postgres, "Persiste")

@enduml
```

<a id="composants-principaux"></a>
### Composants principaux [↑](#toc-composants-principaux)

| Composant | Package/Module | Responsabilité |
|-----------|---------------|----------------|
| **Views** | `app.views.*` | 20+ vues : recherche, détail formation, articles, abonnement |
| **Forms** | `app.forms.*` | Formulaires de recherche, inscription, abonnement avec validation métier |
| **Models** | `app.models.*` | 15 entités : Stage, Session, Periode, Article, Subscription, etc. |
| **Services** | `app.services.*` | Import CSV, parsing, réindexation, nettoyage, logs |
| **Search** | `app.search` | Wrapper MeiliSearch avec configuration des index |
| **Admin** | `app.admin` | Configuration de l'interface d'administration Django |

<a id="modèle-de-données-simplifié"></a>
### Modèle de données simplifié [↑](#toc-modèle-de-données-simplifié)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Organisateur│────<│    Stage    │>────│  StageType  │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   Session   │>────┐
                    │  (formation)│     │
                    └──────┬──────┘     │
                           │            │
                    ┌──────┴──────┐     │
                    │   Periode   │     │
                    └─────────────┘     │
                                        │
                           ┌────────────┴────────────┐
                           │      Subscription       │
                           │  (abonnement email)     │
                           └─────────────────────────┘
```

---

<a id="7-niveau-4-vue-code-code"></a>
## 7. Niveau 4 — Vue Code (Code) [↑](#toc-7-niveau-4-vue-code-code)

Ce niveau n'est pas détaillé dans ce document. Les diagrammes de classes UML et ERD complets sont disponibles sur demande auprès de l'équipe de développement.

Les principaux patterns de code utilisés :
- **MVT (Model-View-Template)** : Pattern Django standard
- **Service Layer** : Logique métier isolée dans `app/services/`
- **Repository Pattern** : Accès données via Managers Django
- **Command Pattern** : Commandes de management Django pour imports

---

<a id="8-vue-exécution-scénarios"></a>
## 8. Vue Exécution (Scénarios) [↑](#toc-8-vue-exécution-scénarios)

<a id="scénario-1-recherche-de-formation-avec-critères"></a>
### Scénario 1 : Recherche de formation avec critères [↑](#toc-scénario-1-recherche-de-formation-avec-critères)

```plantuml
@startuml
!theme plain
title Scénario: Recherche de formation

actor Agent
participant "Navigateur" as Browser
participant "Django\n(View)" as View
participant "SearchForm\n(Validation)" as Form
participant "MeiliSearch\nClient" as Search
database "MeiliSearch\nIndex" as Index

Agent -> Browser : Saisit critères\n(domaine, date, lieu)
Browser -> View : POST /recherche/
View -> Form : Validation données
Form --> View : Données validées

View -> Search : search_sessions(filters, sort)
Search -> Index : Requête HTTP /indexes/sessions/search
Index --> Search : Résultats JSON (hits, nbHits)

Search --> View : Résultats paginés
View -> View : Enrichissement données\n(calcul durée, formatage)
View --> Browser : HTML + résultats
Browser --> Agent : Affiche tableau formations\n(avec liens vers détail)

@enduml
```

<a id="scénario-2-import-quotidien-des-données-cisirh"></a>
### Scénario 2 : Import quotidien des données CISIRH [↑](#toc-scénario-2-import-quotidien-des-données-cisirh)

```plantuml
@startuml
!theme plain
title Scénario: Import CISIRH (Cron quotidien)

participant "Celery\nScheduler" as Cron
participant "ImportCisirh\nCommand" as Cmd
participant "S3 Client" as S3
participant "CSV Parser\nServices" as Parser
database "PostgreSQL" as PG
database "MeiliSearch" as Search

Cron -> Cmd : Exécution quotidienne\n(00:00)
Cmd -> S3 : download_all_from_S3()
S3 --> Cmd : Fichiers CSV\n(STAGES.csv, SESSIONS.csv, PERIODES.csv)

par Traitement parallèle
    Cmd -> Parser : update_stages()
    Parser -> PG : INSERT/UPDATE stages
    Parser -> PG : Nettoyage données orphelines
    
    Cmd -> Parser : update_sessions()
    Parser -> PG : INSERT/UPDATE sessions\n(marquage new=True)
    
    Cmd -> Parser : update_periodes()
    Parser -> PG : INSERT périodes
end

Cmd -> Search : reindex()
Search -> PG : Récupération toutes sessions
Search -> Search : Mise à jour index "sessions"

Cmd -> S3 : delete_file_cisirh()
S3 --> Cmd : Fichiers temporaires supprimés

Cmd -> PG : Log import (CronJobLog)

@enduml
```

<a id="scénario-3-inscription-hors-self-agent"></a>
### Scénario 3 : Inscription hors Self-Agent [↑](#toc-scénario-3-inscription-hors-self-agent)

```plantuml
@startuml
!theme plain
title Scénario: Inscription agent sans Self-Agent

actor Agent
participant "Formulaire\nWeb" as Form
participant "Django\n(View)" as View
participant "Registration\nForm (Validation)" as Val
participant "API\nInscription" as API
participant "Hedwige\n(Email)" as Mail
actor "Supérieur\nHiérarchique" as Sup

Agent -> Form : Remplit formulaire\n(données personnelles)
Form -> View : POST /inscription-hors-self/
View -> Val : Validation métier\n(champs obligatoires, formats)
Val --> View : Formulaire valide

View -> API : POST /api/inscription\n(JSON données agent)
API --> View : 201 Created / Erreur

alt Succès
    View -> Mail : Envoi email confirmation\n(à l'agent)
    View -> Mail : Envoi email validation\n(au supérieur)
    View --> Form : Redirection avec message\n"Demande enregistrée"
    Form --> Agent : Affiche confirmation
    
    Sup -> Mail : Réception email\nlien validation
    Sup -> Sup : Validation demande\n(via lien)
else Échec API
    View --> Form : Erreur technique
    Form --> Agent : Message d'erreur\n"Service indisponible"
end

@enduml
```

---

<a id="9-vue-déploiement"></a>
## 9. Vue Déploiement [↑](#toc-9-vue-déploiement)

<a id="diagramme-c4-déploiement"></a>
### Diagramme C4-Déploiement [↑](#toc-diagramme-c4-déploiement)

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

LAYOUT_WITH_LEGEND()

title Déploiement Production - Cloud ECO4

Deployment_Node(eco4, "Cloud ECO4", "OpenStack Tenant PNM3") {
    Deployment_Node(nginx_cluster, "Nginx Cluster", "Load Balancer HA") {
        Container(nginx1, "Nginx 1", "Reverse Proxy, SSL termination")
        Container(nginx2, "Nginx 2", "Reverse Proxy, SSL termination")
    }
    
    Deployment_Node(app_servers, "Application Servers", "Docker Swarm/K8s") {
        Container(django1, "Django App 1", "Gunicorn, 4 workers")
        Container(django2, "Django App 2", "Gunicorn, 4 workers")
        Container(celery_worker, "Celery Workers", "3 replicas")
        Container(celery_beat, "Celery Beat", "Scheduler")
    }
    
    Deployment_Node(data_layer, "Data Layer", "Réseau interne") {
        ContainerDb(postgres, "PostgreSQL", "Primary + Replica")
        ContainerDb(meilisearch, "MeiliSearch", "Single node")
        ContainerDb(redis, "Redis", "Cache + Broker")
    }
    
    Deployment_Node(storage, "Stockage", "Ceph/S3") {
        Container(minio, "MinIO", "Stockage objets")
        Container(files, "Volumes", "Fichiers statiques, uploads")
    }
}

Deployment_Node(monitoring, "Supervision", "Stack GTI") {
    Container(prometheus, "Prometheus", "Métriques")
    Container(grafana, "Grafana", "Visualisation")
    Container(loki, "Loki", "Logs")
    Container(alertmanager, "AlertManager", "Alerting")
    Container(portainer, "Portainer", "Gestion conteneurs")
}

Rel(nginx_cluster, app_servers, "HTTP/8000", "Load balancing")
Rel(app_servers, data_layer, "JDBC/Redis", "Connexions persistantes")
Rel(app_servers, storage, "S3 API", "Fichiers")
Rel(monitoring, eco4, "Scrape", "Métriques et logs")

@enduml
```

<a id="environnements"></a>
### Environnements [↑](#toc-environnements)

| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | Local/Docker | 1 (localhost) | Interne | SQLite possible, DEBUG=True |
| Intégration | Cloud ECO4 (tenant dev) | 2 (small) | VLAN isolé | Données de test, accès restreint |
| Recette | Cloud ECO4 (tenant rec) | 2 (medium) | VLAN restreint | Données anonymisées, tests RSSI |
| Production | Cloud ECO4 (tenant pnm3) | 4+ (medium+) | DMZ + interne | HA activé, backup automatique |

<a id="infrastructure"></a>
### Infrastructure [↑](#toc-infrastructure)

Le produit est hébergé sur le cloud interne ECO4 basé sur Openstack, dans le tenant 'pnm3' du département.  
Le reverse-proxy Nginx du schéma ci-dessous est en fait une paire de Nginx load-balancés en frontal des produits hébergés sur le tenant.

<a id="supervision"></a>
### Supervision [↑](#toc-supervision)

Le produit est supervisé via le système standard du GTI pour ce faire :
- via Portainer pour la partie purement conteneurisée,
- via la stack Prometheus/Grafana/Loki/AlertManager,
- Le produit dispose également d'une supervision PSIN.

<a id="sauvegardes"></a>
### Sauvegardes [↑](#toc-sauvegardes)

Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
- le stockage objet B3 du IaaS ministériel,
- le stockage objet Outscale SecNumCloud (via la prestation qu'a le GTI sur le marché "Nuage Public"),
- le stockage objet standard de Google Cloud (via la prestation qu'a le GTI sur le marché "Nuage Public").

---

<a id="10-sujets-transverses"></a>
## 10. Sujets transverses [↑](#toc-10-sujets-transverses)

<a id="authentification"></a>
### Authentification [↑](#toc-authentification)
- **Mode CAS** : Pour agents du ministère (authentification centralisée)
- **Mode Local** : Pour développement et tests (Django auth)
- **Hors Self-Agent** : Formulaire libre avec validation email pour agents externes

<a id="journalisation"></a>
### Journalisation [↑](#toc-journalisation)
- Logs applicatifs structurés (JSON) dans Loki
- Historique des imports CISIRH (table `CronJobLog`)
- Logs de sécurité : tentatives d'accès, erreurs 403/404/500

<a id="monitoring"></a>
### Monitoring [↑](#toc-monitoring)
- Métriques métier : nombre de recherches, taux de conversion inscription
- Métriques techniques : temps de réponse, erreurs 5xx, saturation DB
- Alertes : indisponibilité, erreurs d'import, file Celery bloquée

<a id="gestion-des-erreurs"></a>
### Gestion des erreurs [↑](#toc-gestion-des-erreurs)
- Pages d'erreur personnalisées (403, 404, 500) avec template DSFR
- Fallback gracieux : si MeiliSearch indisponible, message utilisateur clair
- Retry Celery : 3 tentatives avec backoff exponentiel

<a id="api-et-intégrations"></a>
### API et intégrations [↑](#toc-api-et-intégrations)
- API REST interne pour sous-domaines et départements (JSON)
- Intégration externe : API Inscription (hors-self), Hedwige (emails)
- RSS Feeds : flux de formations filtrables

---

<a id="11-exigences-de-qualité"></a>
## 11. Exigences de qualité [↑](#toc-11-exigences-de-qualité)

| Exigence | Scénario de validation |
|----------|------------------------|
| Temps de réponse recherche < 2s | Test de charge JMeter : 100 requêtes/min, 95e percentile < 2s |
| Disponibilité 99.5% | Mesure sur 30 jours : (temps total - indisponibilité) / temps total |
| RGAA 82%+ conforme | Audit TEMESIS annuel avec rapport de conformité |
| Import quotidien réussi | Taux de succès des tâches Celery > 99% sur 30 jours |
| Récupération backup < 4h | Test semestriel de restauration complète |

---

<a id="12-risques-et-dettes-techniques"></a>
## 12. Risques et dettes techniques [↑](#toc-12-risques-et-dettes-techniques)

| Risque/Dette | Impact | Probabilité | Mesure d'atténuation |
|--------------|--------|-------------|----------------------|
| **Montée de version Django 4.2 → 5.x** | Moyen | Élevée | Planifier migration LTS 2025, tests de non-régression |
| **Dépendance CISIRH (source unique données)** | Élevé | Moyenne | Mise en place de cache étendu, alerte en cas d'absence d'import |
| **MeiliSearch mono-instance** | Moyen | Faible | Backup quotidien de l'index, procédure de reconstruction documentée |
| **Code legacy (fonctions longues)** | Moyen | Élevée | Refactoring progressif, couverture de tests à augmenter |
| **Secrets dans variables d'environnement** | Faible | Moyenne | Migration vers Vault ou équivalent GTI |

---

<a id="13-annexes"></a>
## 13. Annexes [↑](#toc-13-annexes)

<a id="glossaire"></a>
### Glossaire [↑](#toc-glossaire)

| Terme | Définition |
|-------|------------|
| **CISIRH** | Centre Interministériel de Services Informatiques relatifs aux Ressources Humaines |
| **Self Agent** | Portail RH ministériel pour la gestion des agents |
| **DSFR** | Design System de l'État Français (composants UI accessibles) |
| **MeiliSearch** | Moteur de recherche open source, alternative à Elasticsearch |
| **Celery** | Framework de traitement de tâches asynchrones pour Python |
| **CAS** | Central Authentication Service (protocole SSO) |
| **Hedwige** | Service d'envoi d'emails transactionnels du ministère |

<a id="décisions-darchitecture-adr"></a>
### Décisions d'Architecture (ADR) [↑](#toc-décisions-darchitecture-adr)

| ID | Date | Sujet | Décision | Statut |
|----|------|-------|----------|--------|
| ADR-001 | 2024-01 | Moteur de recherche | Adoption de MeiliSearch vs Elasticsearch | Accepté |
| ADR-002 | 2024-02 | Authentification | Double mode CAS/Local pour flexibilité | Accepté |
| ADR-003 | 2024-03 | Import données | Traitement asynchrone via Celery vs synchrone | Accepté |
| ADR-004 | 2024-06 | Frontend | DSFR obligatoire vs framework JS moderne | Accepté |

---

**[↩ Retour au sommaire](#toc)**

---
*Document généré le 28 février 2026 - Version 1.0*