# 📘 Dossier d’Architecture Technique (DAT) – **agile‑back**

[TOC]

---

## 1️⃣ Introduction et objectifs {#introduction}

### 1.1 Vue d’ensemble fonctionnelle
**agile‑back** est le back‑office de l’application **Agile**.  
Il permet la création, la modification et la consultation d’études / financements / dotations / groupes, ainsi que la gestion des utilisateurs et des autorisations.  
L’interface web est rendue avec Twig ; les API REST/JSON sont exposées via **API Platform**.

### 1.2 Schéma C4 – Niveau 1 (Système)
```mermaid
graph TD
    U[Utilisateur (Administrateur, Gestionnaire)] -->|Utilise| AB[agile‑back]
    AB -->|Consomme| API[API Platform (REST/JSON)]
    AB -->|Accède à| DB[(PostgreSQL DB)]
    AB -->|S’authentifie via| CAS[CAS Server]
    AB -->|Communique avec| AF[agile‑front (UI)]
    AF -->|Appel API| API;
    style U fill:#E3F2FD,stroke:#0D47A1,stroke-width_2px;
    style AB fill:#FFF3E0,stroke:#E65100,stroke-width_2px;
    style DB fill:#E8F5E9,stroke:#1B5E20,stroke-width_2px;
    style CAS fill:#F3E5F5,stroke:#6A1B9A,stroke-width_2px;
    style AF fill:#E1F5FE,stroke:#0277BD,stroke-width_2px
```

### 1.3 Objectifs de qualité orientés utilisateur
| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Performance** – temps de réponse < 2 s pour les écrans de création d’étude | Garantir une expérience fluide aux agents |
| 2 | **Sécurité** – authentification forte via CAS, chiffrement des données sensibles | Conformité RGPD & exigences du ministère |
| 3 | **Maintenabilité** – code structuré (Symfony 5.x), tests unitaires ≥ 70 % | Réduire le coût de l’évolution fonctionnelle |
| 4 | **Disponibilité** – SLA ≥ 99,5 % en production | Assurer la continuité du service aux usagers |
| 5 | **Extensibilité** – API ouverte & versionnée | Faciliter l’intégration de nouveaux front‑ends (ex. agile‑mobile) |

↩ **[Retour au sommaire](#toc)**  

---

## 2️⃣ Parties prenantes {#parties-prenantes}

| Rôle | Attente principale |
|------|--------------------|
| **MOA – Direction Agile** | Visibilité sur les indicateurs de suivi et conformité réglementaire |
| **Développeurs Symfony** | Architecture claire, documentation à jour, CI/CD fiable |
| **Opérateurs / Exploitants** | Déploiement automatisé, monitoring complet, procédures de restauration |
| **RSSI** | Gestion des vulnérabilités, traçabilité des accès, chiffrement des sauvegardes |
| **Utilisateurs finaux (Gestionnaires d’études)** | Interface ergonomique, temps de réponse rapide, fiabilité des données |
| **Équipe Front‑office (agile‑front)** | API stable, documentation Swagger/OpenAPI à jour |

↩ **[Retour au sommaire](#toc)**  

---

## 3️⃣ Contraintes {#contraintes}

### 3.1 Contraintes techniques
* **Framework** : Symfony 5.x (PHP 8.1 recommandé)  
* **Base de données** : PostgreSQL 13 / 14, accès via Doctrine ORM  
* **Authentification** : CAS (phpCAS) – SSO interne au ministère  
* **API** : API Platform, JSON / CSV, versionnée (`/api/v1`)  
* **Infrastructure** : Hébergement sur le cloud interne ECO4 (OpenStack) – VM Debian/Ubuntu, Nginx + PHP‑FPM  
* **CI/CD** : GitLab CI, pipelines Docker (build, test, deploy)  

### 3.2 Contraintes organisationnelles
* Livraison continue avec validation de la sécurité (SAST, DAST) avant mise en prod.  
* Gestion des changements via la plateforme GitLab ‑ Merge Requests.  

### 3.3 Contraintes réglementaires
* **RGPD** – anonymisation des logs, droit à l’oubli.  
* **D‑I‑C‑T** (Disponibilité, Intégrité, Confidentialité, Traçabilité) :  
  * **Disponibilité** : réplication PostgreSQL, sauvegardes 3×/jour.  
  * **Intégrité** : contraintes DB, validation côté serveur.  
  * **Confidentialité** : chiffrement AES‑256 des dumps, transport TLS 1.2+.  
  * **Traçabilité** : journalisation via Monolog (JSON) et stack Prometheus/Grafana.  

↩ **[Retour au sommaire](#toc)**  

---

## 4️⃣ Contexte et périmètre {#contexte}

### 4.1 Systèmes partenaires
| Système | Type d’interaction | Protocole / Fréquence |
|---------|-------------------|-----------------------|
| **agile‑front** | Consommation d’API (CRUD études, export) | HTTP / REST, appels asynchrones |
| **CAS serveur** | Authentification SSO | HTTPS, requêtes ponctuelles lors du login |
| **Base PostgreSQL** | Persistance des entités métiers | Connexion DB persistante via Doctrine |
| **E-mail SMTP** | Envoi de notifications | SMTP (STARTTLS) via Symfony Mailer |
| **Monitoring GTI** | Supervision métriques & alertes | Prometheus scrape (15 s) |
| **Portainer** | Gestion des containers Docker (dev) | API HTTP |

### 4.2 Interfaces techniques
| Interface | Format | Sécurité |
|------------|--------|----------|
| `/api/*` | JSON, CSV | JWT / HTTPS |
| `CAS` | CAS 3.0 protocol | TLS, validation du certificat |
| DB | PostgreSQL wire protocol | TLS, authentication `md5`/`scram-sha-256` |
| SMTP | RFC 5321 | TLS, authentification SASL |

↩ **[Retour au sommaire](#toc)**  

---

## 5️⃣ Stratégie de solution {#strategie}

| Décision architecturale | Justification |
|------------------------|----------------|
| **Monolithe Symfony** (pas de micro‑services) | Simplicité de déploiement, cohérence du modèle de données, faible complexité fonctionnelle. |
| **API Platform** pour l’exposition d’API | Génération automatique de la documentation OpenAPI, pagination, filtres, support CSV. |
| **Doctrine ORM** | Mapping objet‑relationnel mature, migrations gérées (`doctrine_migrations`). |
| **CAS (phpCAS)** comme fournisseur d’identité | Conformité aux exigences ministérielles d’authentification unique. |
| **Docker** (dev) & **GitLab CI** | Isolation des environnements, reproductibilité des builds. |
| **Nginx + PHP‑FPM** | Séparation du reverse‑proxy et du moteur PHP, scalabilité horizontale. |
| **Prometheus / Grafana** | Monitoring natif, alerting sur latence, erreurs HTTP, utilisation CPU/mémoire. |

#### 5.1 Stack technique

| Couche | Technologie | Version |
|--------|--------------|---------|
| **Langage** | PHP | 8.1 |
| **Framework** | Symfony | 5.4 (LTS) |
| **API** | API Platform | 2.6 |
| **ORM** | Doctrine | 2.9 |
| **Base de données** | PostgreSQL | 13 |
| **Web Server** | Nginx | 1.22 |
| **Auth** | phpCAS | 1.6 |
| **CI/CD** | GitLab CI | – |
| **Containerisation (dev)** | Docker | 20.10 |
| **Monitoring** | Prometheus, Grafana, Loki, Alertmanager | – |
| **Logs** | Monolog (JSON) | – |

#### 5.2 Forge logicielle

| Outil | Usage |
|-------|-------|
| **GitLab** | Gestion du code, MR, CI pipelines |
| **PHPUnit** | Tests unitaires |
| **PHPStan / Psalm** | Analyse statique |
| **PHP CS Fixer** | Formatage du code |
| **Docker Compose** (dev) | Lancement d’un stack Nginx + PHP + Postgres |
| **Portainer** | Supervision des containers en dev |

↩ **[Retour au sommaire](#toc)**  

---

## 6️⃣ Vue en Briques (C4 – Niveau 2) {#vue-en-briques}

```mermaid
graph TD
    subgraph "Infrastructure"
    N[nginx (reverse‑proxy)]
    P[php‑fpm]
    DB[(PostgreSQL)]
    CAS[CAS Server]
    MON[Prometheus/Grafana/Loki]
    end
    subgraph "Application"
    APP[agile‑back (Symfony)]
    end
    N --> P --> APP;
    APP --> DB;
    APP --> CAS;
    APP --> MON;
    N -->|HTTPS| CAS;
    N -->|HTTPS| DB
```

### 6.1 Description des conteneurs principaux  

| Conteneur | Rôle | Principales technologies |
|----------|------|--------------------------|
| **nginx** | Reverse‑proxy, TLS termination, load‑balancing (2 instances en prod) | Nginx 1.22, LetsEncrypt (ou certificat interne) |
| **php‑fpm** | Exécution du code PHP, gestion du pool de processus | PHP‑FPM 8.1 |
| **agile‑back (Symfony)** | Core métier : contrôleurs, services, formulaires, API | Symfony 5.4, API Platform, Doctrine |
| **PostgreSQL** | Persistance des entités (Études, Financements, Utilisateurs…) | PostgreSQL 13, réplication streaming |
| **CAS** | Authentification unique (SSO) | phpCAS 1.6, protocole CAS 3.0 |
| **Prometheus/Grafana/Loki** | Collecte métriques, visualisation, logs, alerting | Prometheus 2.x, Grafana 9.x, Loki 2.x |

↩ **[Retour au sommaire](#toc)**  

---

## 7️⃣ Vue Exécution (Scénarios critiques) {#vue-execution}

### 7.1 Scénario 1 – Authentification d’un gestionnaire d’étude

```mermaid
sequencediagram;
    participant User as Gestionnaire;
    participant Front as agile‑front;
    participant BE as agile‑back;
    participant CAS as CAS Server;
    User->>Front: Accède à la page « Créer étude »
    Front->>BE: Requête GET /etudes/new (HTTP 302)
    BE->>CAS: Redirection vers /cas/login?service=...
    CAS->>User: Formulaire de login CAS;
    User->>CAS: Saisie credentials;
    CAS-->>BE: Ticket CAS (service ticket)
    BE->>CAS: Validation du ticket;
    CAS-->>BE: Confirmation + attributs utilisateur;
    BE-->>Front: Session établie, redirection vers /etudes/new;
    Front-->>User: Formulaire de création affiché
```

*Points de contrôle* : journalisation du ticket, vérification du certificat, traçabilité (Monolog).

### 7.2 Scénario 2 – Création d’une étude avec notification email

```mermaid
sequencediagram;
    participant User as Gestionnaire;
    participant BE as agile‑back;
    participant DB as PostgreSQL;
    participant Mail as SMTP;
    User->>BE: POST /etudes (payload JSON)
    BE->>DB: INSERT étude + relations;
    DB-->>BE: Confirmation (ID)
    BE->>Mail: Envoi email de notification (template)
    Mail-->>BE: ACK;
    BE-->>User: 201 Created + URL de l’étude
```

*Points de contrôle* : validation des données (Form/DTO), transaction DB, envoi email via Symfony Mailer, logs d’envoi.

### 7.3 Scénario 3 – Export CSV d’une étude

```mermaid
sequencediagram;
    participant User as Gestionnaire;
    participant BE as agile‑back;
    participant DB as PostgreSQL;
    User->>BE: GET /api/etudes/123/export.csv;
    BE->>DB: SELECT * FROM etudes WHERE id=123;
    DB-->>BE: Résultat;
    BE->>BE: Transformation → CSV (ExportUtil)
    BE-->>User: fichier CSV (Content‑Disposition)
```

*Points de contrôle* : contrôle des droits (Voter), formatage CSV, logs d’export, limites de taille.

↩ **[Retour au sommaire](#toc)**  

---

## 8️⃣ Vue Déploiement *(section standardisée)* {#vue-deploiement}

### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | Machine locale / Docker Compose | 1 × Nginx, 1 × PHP‑FPM, 1 × Postgres | LAN interne | Variables `.env.dev`, Debug Toolbar activé |
| **Recette** | Cloud interne ECO4 (VM) | 2 × Nginx (load‑balancer), 2 × PHP‑FPM, 1 × Postgres réplication | VLAN 10 | Données anonymisées, tests d’intégration automatisés |
| **Production** | Cloud interne ECO4 (tenant `pnm3`) | 2 × Nginx (HAProxy LB), 4 × PHP‑FPM, 2 × Postgres (primary + standby) | VLAN 20, DMZ | TLS certs internes, sauvegardes chiffrées, monitoring GTI complet |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant **`pnm3`** du département.  
Le reverse‑proxy Nginx du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx Load‑Balancer] --> B[PHP‑FPM (x4)]
    B --> C[Symfony (agile‑back)]
    C --> D[PostgreSQL Primary]
    C --> E[PostgreSQL Standby]
    C --> F[CAS Server]
    C --> G[Prometheus/Grafana/Loki]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :

- via **Portainer** pour la partie purement conteneurisée,  
- via la stack **Prometheus/Grafana/Loki/AlertManager**,  
- le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

- le stockage objet **B3** du IaaS ministériel,  
- le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché *« Nuage Public »),  
- le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché *« Nuage Public »*).

↩ **[Retour au sommaire](#toc)**  

---

## 9️⃣ Sujets transverses {#transverses}

| Sujet | Description | Implémentation |
|-------|-------------|----------------|
| **Authentification** | SSO via CAS, token de session Symfony | `phpCAS` + `Security.yaml` (firewall `main`) |
| **Autorisation** | Voter `EtudesVoter` pour contrôle d’accès fine‑grained | Implémenté dans `src/Security/Voter/EtudesVoter.php` |
| **Journalisation** | Monolog en JSON, canaux `main`, `security`, `deprecation` | Config `config/packages/*/monolog.yaml` |
| **Gestion des erreurs** | Exception listeners, page d’erreur personnalisée, fallback JSON | `ExceptionListener` dans `services.yaml` |
| **API** | API Platform, pagination, filtres, versionnage (`/api/v1`) | Annotations `@ApiResource` sur les entités |
| **Export** | CSV & ODS via `ExportUtil`, `Valorisation` services | `src/util/ExportUtil.php` |
| **Sécurité des données** | Chiffrement des backups, TLS partout, CSP headers | Nginx `add_header Content‑Security‑Policy` |
| **Tests** | PHPUnit + Symfony Test Client, couverture ≥ 70 % | `phpunit.xml.dist` & `tests/` |
| **CI/CD** | GitLab pipelines : build → test → security scan → deploy | `.gitlab-ci.yml` (non présent dans l’arborescence mais prévu) |

↩ **[Retour au sommaire](#toc)**  

---

## 🔟 Exigences de qualité {#qualite}

| Exigence | Critère d’acceptation | Scénario de validation |
|----------|----------------------|------------------------|
| **Performance** | Temps moyen de réponse < 2 s (95 % des requêtes) | Tests de charge JMeter sur `/etudes` en prod, analyse des métriques Prometheus (`http_request_duration_seconds`) |
| **Sécurité** | Aucun CVE critique non corrigé, conformité OWASP Top 10 | SAST (PHPStan), DAST (OWASP ZAP) dans pipeline CI |
| **Disponibilité** | SLA ≥ 99,5 % (downtime < 3 h/mois) | Monitoring alertes `up`/`down` sur Nginx et PostgreSQL, rapports Grafana |
| **Maintenabilité** | Couverture de tests unitaires ≥ 70 % | Exécution `phpunit --coverage-text` dans pipeline |
| **Extensibilité** | API versionnée, backward compatible | Tests d’intégration sur `/api/v1` et `/api/v2` (simulés) |
| **Traçabilité** | Tous les accès utilisateurs journalisés avec `user_id` | Vérification des logs `security` via Kibana/Loki |

↩ **[Retour au sommaire](#toc)**  

---

## 1️⃣1️⃣ Risques et dettes techniques {#risques}

| Risque / Dette | Impact | Mesure corrective / d’atténuation |
|----------------|--------|-----------------------------------|
| **Dépendance au serveur CAS** | Indisponibilité totale de l’application si le SSO échoue | Mise en place d’un fallback local (login/password) en mode maintenance, monitoring du service CAS |
| **Absence de tests d’intégration** | Régression fonctionnelle non détectée | Ajouter des scénarios d’intégration (Symfony Panther) dans le pipeline CI |
| **Version PHP proche de la fin de support** | Vulnérabilités non corrigées | Planifier la migration vers PHP 8.2 avant fin 2025 |
| **Gestion manuelle des migrations** | Risque d’incohérence schema DB | Utiliser `doctrine:migrations:migrate` automatisé en CI, revue code des migrations |
| **Basse couverture des contrôles d’accès** | Fuite de données sensibles | Auditer les Voter, ajouter des tests unitaires pour chaque règle d’accès |
| **Sauvegardes non chiffrées (historique)** | Non‑conformité RGPD | Vérifier les scripts de backup, forcer le chiffrement AES‑256 sur tous les dumps |

↩ **[Retour au sommaire](#toc)**  

---

## 1️⃣2️⃣ Annexes {#annexes}

### 12.1 Glossaire
| Terme | Définition |
|-------|------------|
| **CAS** | Central Authentication Service – protocole SSO utilisé par le ministère. |
| **API Platform** | Framework Symfony pour exposer des API REST/GraphQL avec documentation OpenAPI. |
| **DTO** | Data Transfer Object – structure de données pour les échanges API. |
| **Voter** | Composant Symfony de décision d’accès (RBAC). |
| **GTI** | Groupe Technique Informatique – responsable de la supervision et des sauvegardes. |
| **ECO4** | Cloud interne ministériel basé sur OpenStack. |
| **D‑I‑C‑T** | Modèle de sécurité : Disponibilité, Intégrité, Confidentialité, Traçabilité. |

### 12.2 Décisions d’architecture (ADR)

| # | Décision | Contexte | Conséquence |
|---|----------|----------|--------------|
| **ADR‑001** | Utiliser **Symfony 5.4 LTS** | Besoin d’un framework mature, support long terme | Stabilisation du code, migration future vers Symfony 6 prévue |
| **ADR‑002** | Exposer les API via **API Platform** | Nécessité d’une documentation OpenAPI et de filtres automatisés | Gain de productivité, génération de code client possible |
| **ADR‑003** | Authentification par **CAS (phpCAS)** | Conformité aux exigences ministérielles d’authentification unique | Centralisation de la gestion des identités, dépendance au service CAS |
| **ADR‑004** | Déployer en **monolithe** (pas de micro‑services) | Taille du domaine fonctionnel limité, besoin rapide de mise en production | Simplicité du déploiement, évolution future possible vers micro‑services si le périmètre s’élargit |
| **ADR‑005** | Sauvegardes **AES‑256** sur trois stores différents | Obligation RGPD & exigences de redondance | Résilience des données, conformité légale |

↩ **[Retour au sommaire](#toc)**  

---  

*Document généré le **28 avril 2026** – prêt à être utilisé dans VS Code ou Obsidian (Mermaid activé).*