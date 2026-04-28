# Dossier d’Architecture Technique – **agile‑back**

[TOC]

---

## 1. Introduction et objectifs {#introduction}
**Vue fonctionnelle**  
*agile‑back* est le back‑office de l’application **Agile**. Il permet aux agents de :

* créer / modifier / supprimer des **études**,
* gérer les **financements**, **dotations**, **BOP**, **groupes**, **profils** et **utilisateurs**,
* exporter les données au format CSV / ODS,
* être notifié par e‑mail des changements.

L’accès se fait via le **CAS** (Central Authentication Service) et l’interface web est exposée via **Symfony** (Twig) ainsi que des **API REST** (API‑Platform).

### 1.1 Schéma C4 – Niveau 1 (System Context) {#c4-l1}
```mermaid
graph TD
    Front[Agile‑front<br/>Interface utilisateur] -->|REST/HTML| App[agile‑back<br/>Symfony (MVC + API‑Platform)]
    App -->|JDBC/SQL| DB[(PostgreSQL<br/>DB)]
    App -->|CAS 2.0| CAS[CAS Server<br/>(authentification SSO)]
    App -->|SMTP/TLS| Mail[Mail Server]
    App -->|HTTP| ExtAPI[Services externes<br/>(ex. API statistiques)]
    style Front fill:#E3F2FD,stroke:#1565C0,stroke-width_2px;
    style App  fill:#FFF3E0,stroke:#EF6C00,stroke-width_2px;
    style DB   fill:#E8F5E9,stroke:#2E7D32,stroke-width_2px;
    style CAS  fill:#FCE4EC,stroke:#C2185B,stroke-width_2px;
    style Mail fill:#E1F5FE,stroke:#0288D1,stroke-width_2px
```

### 1.2 Objectifs de qualité orientés utilisateur
| # | Objectif | Raison métier |
|---|----------|---------------|
| 1 | **Performance** – temps de réponse < 2 s pour la création d’une étude | Fluidité de la saisie, productivité des agents |
| 2 | **Sécurité** – authentification CAS, chiffrement TLS, traçabilité des actions | Conformité RGPD & exigences de la DSI |
| 3 | **Maintenabilité** – architecture modulaire, tests unitaires ≥ 80 % | Réduction du coût de l’évolution fonctionnelle |
| 4 | **Disponibilité** – SLA ≥ 99,5 % (HA Nginx + sauvegardes) | Garantir l’accès aux données critiques |
| 5 | **Extensibilité** – API versionnée, capacité à ajouter de nouveaux types d’entités | Accompagner les évolutions du domaine métier |

↩ [Retour au sommaire](#toc)

---

## 2. Parties prenantes {#parties-prenantes}
| Rôle | Principale attente |
|------|--------------------|
| **MOA / Product Owner** | Fonctionnalités conformes au cahier des charges, livrables dans les itérations |
| **Développeurs back‑end** | Cadre stable (Symfony 5+, PHP 7.4+), CI/CD fiable, documentation d’API |
| **Développeurs front‑end (Agile‑front)** | API stable, contrats de données (JSON/CSV) clairement définis |
| **RSSI / Sécurité** | Authentification CAS, chiffrement TLS, logs d’audit, conformité RGPD |
| **Administrateur système** | Déploiement automatisé, monitoring, procédures de backup & restauration |
| **Utilisateurs finaux (agents, analystes)** | Interface réactive, gestion simple des études, notifications par mail |
| **Équipe d’exploitation** | Supervision via Prometheus/Grafana, alerting, capacité de mise à jour sans interruption |

↩ [Retour au sommaire](#toc)

---

## 3. Contraintes {#contraintes}
### 3.1 Techniques
| Contraine | Détail |
|-----------|--------|
| **Langage / Framework** | PHP ≥ 7.4, Symfony 5.x, API‑Platform |
| **Base de données** | PostgreSQL 9.6+ (driver `pdo_pgsql`) |
| **Authentification** | CAS 2.0 (client PHPCAS) – SSO interne |
| **Messagerie** | SMTP (paramétré via `mailer.yaml`) |
| **Cache** | Symfony cache + Doctrine result/system cache |
| **CI/CD** | GitLab CI, tests PHPunit, linting, déploiement via scripts |
| **Infrastructure** | Nginx reverse‑proxy, conteneurs Docker (facultatif) |
| **Internationalisation** | UTF‑8, prise en charge de plusieurs langues (ex. via `locale` dans Symfony) |

### 3.2 Organisationnelles
* Méthodologie **Agile Scrum** – itérations de 2 semaines.
* Livraison continue sur les environnements **dev**, **recette**, **prod**.
* Documentation obligatoire dans le dépôt (README, ADR).

### 3.3 Réglementaires / Sécuritaires (modèle D‑I‑C‑T)
| Axe | Exigence |
|-----|----------|
| **Disponibilité** | HA Nginx (2 instances), sauvegardes quotidiennes, temps de reprise ≤ 1 h |
| **Intégrité** | Transactions Doctrine, contraintes d’unicité (ex. `email`), validation côté serveur |
| **Confidentialité** | TLS 1.2+ sur toutes les communications, chiffrement AES‑256 des dumps |
| **Traçabilité** | Monolog → fichier + stack Prometheus/Grafana, logs d’accès CAS, audit des actions CRUD (via `EventSubscriber`) |

↩ [Retour au sommaire](#toc)

---

## 4. Contexte et périmètre {#contexte}
### 4.1 Partenaires fonctionnels
| Partenaire | Rôle |
|------------|------|
| **Agile‑front** | Application UI qui consomme les API de *agile‑back* |
| **CAS Server** | Authentifie les utilisateurs (SSO) |
| **Mail Server** | Envoi de notifications (ex. changement d’étude) |
| **Statistiques externes** | Consommation ponctuelle d’API tierces (ex. reporting) |
| **Équipe DSI** | Fournit l’infrastructure (OpenStack/ECO4) et la politique de sauvegarde |

### 4.2 Interfaces techniques
| Interface | Protocole | Fréquence | Type de données |
|-----------|-----------|-----------|-----------------|
| **Web UI** | HTTPS (HTML/JS/CSS) | Interaction utilisateur | Formulaires, JSON |
| **API‑Platform** | HTTPS (REST) | On‑demand | JSON, CSV |
| **CAS** | HTTPS (CAS 2.0) | À chaque login | Ticket, service URL |
| **SMTP** | TLS | Événementiel (mail) | MIME (texte/html) |
| **PostgreSQL** | TCP (5432) | Transactionnelle | SQL |
| **Prometheus** | HTTP (scrape) | 15 s | Métriques au format texte |

↩ [Retour au sommaire](#toc)

---

## 5. Stratégie de solution {#strategie}
### 5.1 Décisions architecturales majeures
| Décision | Raison |
|----------|--------|
| **Monolithe Symfony** (MVC + API‑Platform) | Simplicité de mise en œuvre, réutilisation du même code côté web & API |
| **Utilisation de Doctrine ORM** | Gestion transparente des entités métier, migrations automatiques |
| **Intégration CAS** via `phpCAS` | SSO centralisé, conformité aux exigences de la DSI |
| **API‑Platform** pour l’exposition REST | Génération automatique de documentation OpenAPI, pagination, filtres |
| **Nginx en reverse‑proxy** (load‑balanced) | Haute disponibilité & termination TLS |
| **Stack de supervision (Prometheus/Grafana/Loki)** | Visibilité opérationnelle, alerting pré‑emptif |
| **Sauvegardes chiffrées AES‑256** | Protection des données sensibles, conformité RGPD |

### 5.2 Stack technologique
| Couche | Technologie |
|--------|--------------|
| **Langage** | PHP 7.4 / 8.0 |
| **Framework** | Symfony 5.x, API‑Platform |
| **ORM** | Doctrine 2 |
| **Templates** | Twig |
| **Front‑end** | JavaScript (jQuery 1.12), CSS (Agile‑composants) |
| **Auth** | phpCAS |
| **Mail** | Symfony Mailer (SMTP) |
| **Base de données** | PostgreSQL |
| **Web server** | Nginx (2 instances) |
| **Supervision** | Prometheus, Grafana, Loki, Alertmanager |
| **CI/CD** | GitLab CI (tests, lint, déploiement) |
| **Gestion de version** | Git (GitLab) |

### 5.3 Outils de la forge logicielle
* **GitLab** – dépôt, merge‑request, protection des branches.
* **GitLab CI** – pipelines `test → build → deploy`.
* **PHPUnit** – tests unitaires.
* **PHPStan / Psalm** – analyse statique.
* **Doctrine Migrations** – versionnage du schéma DB.
* **Docker (optionnel)** – conteneurisation locale pour les développeurs.

↩ [Retour au sommaire](#toc)

---

## 6. Vue en Briques (C4 – Niveau 2) {#vue-briques}
```mermaid
C4Container;
    title agi­le‑back – Vue en Briques;
    Enterprise_Boundary(b, "agile‑back") {
        Container(nginx, "Nginx", "Reverse‑proxy + Load Balancer", "Termine TLS, répartit le trafic HTTP")
        Container(app, "Symfony Application", "PHP", "MVC + API‑Platform, gestion des entités, logique métier")
        ContainerDb(db, "PostgreSQL", "SGBD", "Stockage persistant des études, financements, etc.")
        Container(cas, "CAS Client", "phpCAS", "Authentification SSO via serveur CAS")
        Container(mail, "Mailer", "Symfony Mailer", "Envoi de notifications e‑mail")
        Container(prom, "Supervision", "Prometheus/Grafana/Loki", "Métriques, logs, alertes")
    }

    Rel(nginx, app, "HTTP/HTTPS", "REST, HTML")
    Rel(app, db, "JDBC/SQL", "Doctrine ORM")
    Rel(app, cas, "CAS 2.0", "Ticket validation")
    Rel(app, mail, "SMTP/TLS", "Notification")
    Rel(app, prom, "HTTP", "Scrape metrics")
    Rel(nginx, prom, "HTTP", "Expose /metrics")
```

**Descriptions brèves**

| Brique | Rôle |
|--------|------|
| **Nginx** | Point d’entrée unique, gère le TLS, répartit le trafic entre deux instances de l’application pour la haute disponibilité. |
| **Symfony Application** | Coeur fonctionnel : contrôleurs, services, formulaires, API‑Platform, sécurité, logs. |
| **PostgreSQL** | Persistance des entités métier (etudes, financements, utilisateurs, etc.). |
| **CAS Client** | Bibliothèque `phpCAS` qui redirige l’utilisateur vers le serveur CAS, valide le ticket et injecte l’identité dans la session Symfony. |
| **Mailer** | Envoi d’e‑mails transactionnels (création/modification d’étude, alertes). |
| **Supervision** | Collecte de métriques (temps de réponse, nombre de requêtes), logs centralisés, alertes sur seuils critiques. |

↩ [Retour au sommaire](#toc)

---

## 7. Vue Exécution (Scénarios critiques) {#vue-execution}
### 7.1 Scénario 1 – Création d’une étude (utilisateur authentifié)

```mermaid
sequencediagram;
    participant User as Agent (Navigateur)
    participant Nginx;
    participant App as Symfony;
    participant CAS as CAS Server;
    participant DB as PostgreSQL;
    participant Mail as Mailer;
    User->>Nginx: GET /etudes/new (HTTPS)
    Nginx->>App: Forward request;
    App->>CAS: Redirect to CAS login (if not authenticated)
    CAS-->>User: Formulaire login;
    User->>CAS: POST credentials;
    CAS-->>User: Ticket + URL de retour;
    User->>Nginx: GET /etudes/new?ticket=XYZ;
    Nginx->>App: Forward request + ticket;
    App->>CAS: Validate ticket;
    CAS-->>App: Validation OK + attributs (email, groupe)
    App->>User: Render formulaire (Twig)
    User->>App: POST formulaire (étude)
    App->>DB: INSERT étude + relations;
    DB-->>App: OK (id)
    App->>Mail: Send notification mail;
    Mail-->>User: (mail envoyé)
    App-->>User: 302 → /etudes/{id} (success)
```

**Points de validation**  
* Authentification CAS réussie → `User` possède un `session_id`.  
* Transaction DB commitée – aucune perte de données.  
* Mail envoyé et loggé (`monolog`).

---

### 7.2 Scénario 2 – Export CSV d’une étude (admin)

```mermaid
sequencediagram;
    participant Admin as Admin UI;
    participant Nginx;
    participant App as Symfony (API‑Platform)
    participant DB as PostgreSQL;
    Admin->>Nginx: GET /api/etudes/{id}/export.csv (Bearer token)
    Nginx->>App: Forward request;
    App->>App: Vérification du rôle (ROLE_ADMIN)
    App->>DB: SELECT * FROM etude WHERE id=…
    DB-->>App: Résultat;
    App->>App: Sérialisation CSV (DataTransformer)
    App-->>Admin: CSV (Content‑Disposition: attachment)
```

**Points de validation**  
* Le rôle `ROLE_ADMIN` est requis (sécurité).  
* Le CSV respecte le format attendu (colonne = propriété).  
* La réponse est correctement encodée en UTF‑8.

---

### 7.3 Scénario 3 – Notification d’erreur critique (ex. perte de connexion DB)

```mermaid
sequencediagram;
    participant Nginx;
    participant App as Symfony;
    participant DB as PostgreSQL;
    participant Alert as Alertmanager;
    App->>DB: SELECT …
    DB-->>App: ERROR (connection timeout)
    App->>App: Capture exception (EventSubscriber)
    App->>Alert: POST alert (severity=critical)
    Alert-->>App: ACK;
    App->>Nginx: 503 Service Unavailable
```

**Points de validation**  
* L’exception est loguée (`monolog`).  
* L’alerte est visible dans Grafana/Alertmanager.  
* L’utilisateur voit la page d’erreur 503.

↩ [Retour au sommaire](#toc)

---

## 8. Vue Déploiement (section standardisée) {#vue-deploiement}
### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| **Développement** | VM locale / Docker | 1 × Nginx + 1 × PHP‑FPM | LAN interne | Base de données en mode `sqlite` ou `postgres` dev, logs en `debug` |
| **Recette** | OpenStack/ECO4 (tenant `pnm3`) | 2 × Nginx (load‑balanced) + 2 × PHP‑FPM | VLAN isolé, accès limité aux testeurs | DB de pré‑production, sauvegardes journalières, monitoring complet |
| **Production** | OpenStack/ECO4 (tenant `pnm3`) | 2 × Nginx (HA) + 4 × PHP‑FPM | VLAN DMZ, firewall strict | DB principale + réplica, sauvegardes chiffrées, alerting, TLS 1.2+ |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **OpenStack**, dans le tenant **'pnm3'** du département.  
Le reverse‑proxy **Nginx** du schéma ci‑dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx (HA)] --> B[Symfony Application]
    B --> C[PostgreSQL]
    B --> D[CAS Client]
    B --> E[Mail Server]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :

* via **Portainer** pour la partie purement conteneurisée,
* via la stack **Prometheus/Grafana/Loki/AlertManager**,
* Le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :

* le stockage objet **B3** du IaaS ministériel,
* le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché *« Nuage Public »*),
* le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché *« Nuage Public »*).

↩ [Retour au sommaire](#toc)

---

## 9. Sujets transverses {#transverses}
| Domaine | Traitement dans *agile‑back* |
|---------|------------------------------|
| **Authentification** | `phpCAS` + `security.yaml` (firewall `main`, `anonymous: true`). Authentification SSO, mapping du `email` en `User` Symfony. |
| **Autorisation** | Voter `EtudesVoter` pour vérifier les droits sur les entités (ROLE_ADMIN, propriétaire, groupe). |
| **Journalisation** | `monolog.yaml` – handler `main` (fichier), `console`, `fingers_crossed` en prod, logs JSON pour ingestion Loki. |
| **Monitoring** | Exporter les métriques via `prometheus_bundle`, endpoints `/metrics`. Dashboard Grafana pré‑configurés (latence, taux d’erreur, utilisation DB). |
| **Gestion des erreurs** | `EventSubscriber\AddPaginationHeaders` ajoute les en‑têtes de pagination, `ExceptionListener` centralise les réponses JSON d’erreur. |
| **API** | API‑Platform expose les entités (`Etudes`, `Financements`, …) avec pagination, filtres, formats JSON/CSV/HTML. |
| **Sécurité des données** | TLS sur toutes les communications, chiffrement des dumps, `Doctrine` utilise les transactions, validation côté formulaire (`FormType`). |
| **Internationalisation** | `locale` configurable, fichiers de traduction (`translations/`), prise en charge UTF‑8. |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml` – tests, lint, build, déploiement). |
| **Gestion de configuration** | `config/packages/*.yaml` séparés par env (`dev`, `prod`, `test`). Variables d’environnement (`.env`) pour DSN, mailer, CAS URL. |

↩ [Retour au sommaire](#toc)

---

## 10. Exigences de qualité {#qualite}
| Exigence | Critère d’acceptation | Scénario de validation |
|----------|----------------------|--------------------------|
| **Performance** | Temps moyen de création d’une étude ≤ 2 s (95 % des requêtes) | Test de charge JMeter sur `/etudes/new` (100 concurrents) |
| **Sécurité – Confidentialité** | Toutes les communications TLS 1.2+, aucune donnée sensible en clair | Scan SSL Labs, test d’interception (OWASP ZAP) |
| **Sécurité – Traçabilité** | Chaque action CRUD → log avec `user_id`, `timestamp`, `entity_id` | Requête dans les logs (`grep "CREATE" /var/log/app.log`) |
| **Disponibilité** | SLA ≥ 99,5 % (max 4 h d’indisponibilité par mois) | Monitoring uptime via Prometheus `up{job="nginx"}` |
| **Maintenabilité** | Couverture unitaires ≥ 80 % | Rapport PHPUnit (`phpunit --coverage-html`) |
| **Extensibilité** | Ajout d’une nouvelle entité (ex. `Projet`) sans modifier le code existant | Création d’un `Projet` entity, génération API‑Platform, tests de non‑régression |
| **Scalabilité** | Le service reste réactif avec 2 × instances PHP‑FPM | Test de montée en charge, métriques CPU < 70 % sous 200 RPS |

↩ [Retour au sommaire](#toc)

---

## 11. Risques et dettes techniques {#risques}
| Risque / Dette | Impact | Mesure d’atténuation |
|----------------|--------|----------------------|
| **Monolithe Symfony** | Difficulté à évoluer vers micro‑services si le volume d’utilisateurs explose | Isoler les modules critiques (ex. API‑Platform) derrière des services séparés dès que le besoin apparaît |
| **Dépendance au CAS** | Indisponibilité du serveur CAS bloque tout le système | Mise en place d’un **fallback** (mode `anonymous` limité) et monitoring du service CAS |
| **Version PHP / Symfony** | Fin de support peut entraîner des vulnérabilités | Politique de mise à jour annuelle, tests de compatibilité automatisés |
| **Gestion des migrations DB** | Risque de perte de données en production | Revue manuelle des scripts de migration, sauvegarde pré‑déploiement obligatoire |
| **Manque de tests d’intégration** | Bugs non détectés lors de changements de contrats API | Introduire des tests d’intégration (Behat) sur les endpoints critiques |
| **Configuration environnementale** (variables `.env`) | Erreurs de configuration entre env → incidents | Utiliser `dotenv` avec validation (`symfony/config`), CI vérifie la présence de toutes les variables |
| **Supervision limitée en dev** | Détection tardive des régressions de performance | Repliquer la stack de monitoring sur les environnements `dev`/`recette` |

↩ [Retour au sommaire](#toc)

---

## 12. Annexes {#annexes}
### 12.1 Glossaire
| Terme | Définition |
|-------|------------|
| **C4** | Modèle d’architecture (Context, Containers, Components, Code) |
| **CAS** | Central Authentication Service – protocole SSO |
| **API‑Platform** | Framework Symfony qui génère automatiquement des API REST/GraphQL |
| **Doctrine ORM** | Bibliothèque d’abstraction de la base de données pour PHP |
| **Nginx** | Serveur web & reverse‑proxy, utilisé ici en mode HA |
| **Prometheus** | Système de collecte de métriques |
| **Loki** | Agrégateur de logs compatible Grafana |
| **ADR** | Architecture Decision Record – décision documentée |
| **D‑I‑C‑T** | Modèle de sécurité (Disponibilité, Intégrité, Confidentialité, Traçabilité) |
| **HA** | High Availability – haute disponibilité |
| **CI/CD** | Intégration continue / Déploiement continu |

### 12.2 Décisions d’Architecture (ADRs) – Extraits
| ADR | Sujet | Décision |
|-----|-------|----------|
| **ADR‑001** | **Framework** | Adoption de Symfony 5.x (MVP, communauté, bundles) |
| **ADR‑002** | **Authentification** | Utilisation de `phpCAS` pour le SSO interne |
| **ADR‑003** | **Exposition API** | API‑Platform pour génération automatique d’OpenAPI, pagination, filtres |
| **ADR‑004** | **Persistances** | PostgreSQL comme SGBD unique (transactions ACID, support JSON) |
| **ADR‑005** | **Supervision** | Stack Prometheus/Grafana/Loki, alerting via Alertmanager |
| **ADR‑006** | **Déploiement** | Nginx load‑balanced (2 instances) sur OpenStack, sauvegardes AES‑256, réplication DB |
| **ADR‑007** | **Gestion des erreurs** | Centralisation via `EventSubscriber` et `ExceptionListener` pour réponses JSON uniformes |
| **ADR‑008** | **CI/CD** | GitLab CI avec jobs `test`, `lint`, `docker‑build`, `deploy‑prod` |

---

*Document généré selon le modèle **arc42** et adapté à l’application **agile‑back**.*  

↩ [Retour au sommaire](#toc)  