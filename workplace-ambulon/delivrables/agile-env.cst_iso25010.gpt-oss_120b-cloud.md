# Cahier des Spécifications Techniques (CST) – Projet **agile‑env**  
**Version 1.0 – 2026‑04‑28**  

---  

## 1. Introduction et contexte qualité  

| Élément | Description |
|---|---|
| **Projet** | *agile‑env* – environnement de développement conteneurisé (Docker) destiné à supporter les services : application PHP‑Apache, base de données PostgreSQL et configuration auxiliaire (variables d’environnement, paramètres CAS, etc.). |
| **Objectifs de qualité** | Fournir un **environnement reproductible, sécurisé, performant et maintenable** afin de réduire les temps de mise en place des développeurs, d’assurer la continuité du service en CI/CD et de faciliter la migration vers d’autres plateformes (ex. : Kubernetes, serveurs bare‑metal). |
| **Contexte métier** | Le projet s’inscrit dans la plateforme *ambulon* du Ministère de la Transition Écologique (exemple). Les développeurs doivent pouvoir lancer `docker compose -f docker-compose.dev.yml up` en moins de 2 min et disposer d’un accès aux bases de données et aux services d’authentification CAS. |
| **Contexte technique** | - Docker 17.09+ / Docker‑Compose 1.29+ <br>- Images de base : `php:7.3‑apache‑buster`, `postgres:11‑alpine`, `composer:latest` <br>- Proxy d’entreprise (`http_proxy/https_proxy`) obligatoire pour l’accès aux dépôts externes. |
| **Références aux exigences fonctionnelles (CCF)** | Les CCF sont décrits dans le **Back‑log produit** (ticket #AG‑001 à #AG‑015). Un tableau de traçabilité CCF ↔ CST est fourni en annexe A. |
| **Méthodologie d’évaluation** | - **Analyse statique** : SonarQube, Dockerfile Linter (hadolint), ShellCheck. <br>- **Tests d’intégration** : Docker‑Compose + Postman (API health). <br>- **Mesure en production** : Prometheus + Grafana (latence, utilisation ressources). <br>- **Audits sécurité** : Trivy, OWASP ASVS 4.0, audit interne RGS/ANSSI. |

---  

## 2. Modèle de qualité ISO / IEC 25010  

```
                    ┌─────────────────────────────────────┐
                    │     QUALITÉ DU PRODUIT LOGICIEL     │
                    └─────────────────────────────────────┘
                                        │
    ┌───────────┬───────────┬───────────┼───────────┬───────────┬───────────┬───────────┐
    │           │           │           │           │           │           │           │
    ▼           ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│Aptitude│  │Performance│  │Compatibilité│  │Utilisabilité│  │Fiabilité│  │Sécurité│  │Maintenabilité│  │Portabilité│
│fonction│  │efficacité│  │           │  │           │  │         │  │        │  │           │  │           │
│-nelle │  │           │  │           │  │           │  │         │  │        │  │           │  │           │
└───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘
```

---  

## 3. Spécification détaillée par caractéristique  

> **Notation** : chaque sous‑caractéristique comporte : (i) **Métrique**, (ii) **Objectif chiffré**, (iii) **Méthode de mesure** et (iv) **Pondération** (1 = critique, 5 = faible).  

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Complétude fonctionnelle** | % d’exigences fonctionnelles (CCF) couvertes par l’environnement (Dockerfiles, compose) | **≥ 95 %** | Mapping CCF ↔ Docker artefacts (annexe A) | 2 |
| **Exactitude fonctionnelle** | Taux d’erreurs de configuration (ex. : variables manquantes, ports en conflit) | **≤ 1 %** | Analyse post‑déploiement automatisée (script `check‑env.sh`) | 2 |
| **Adéquation fonctionnelle** | Score d’évaluation par les développeurs (échelle 1‑5) | **≥ 4 / 5** | Survey trimestriel (Google Forms) | 3 |

### 3.2 Performance et efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Comportement temporel** | Temps de réponse 95ᵉ percentile du conteneur PHP (HTTP GET / health) | **≤ 200 ms** | Prometheus `http_response_time_seconds{quantile="0.95"}` | 2 |
| **Utilisation des ressources** | CPU % et RAM % en charge nominal (2 devs simultanés) | CPU ≤ 45 % ; RAM ≤ 55 % | Grafana dashboards (Docker‑stats) | 3 |
| **Capacité** | Nombre d’utilisateurs simultanés supportés (sessions PHP) | **≥ 50** | Test de charge (k6) – scénario “login + API calls” | 4 |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Cohérence** | Conformité aux standards Docker (Docker‑file best‑practices) | **100 %** (aucun warning `hadolint`) | CI lint step `hadolint Dockerfile*` | 3 |
| **Interopérabilité** | Formats/interfaces supportés (ex : PostgreSQL 13, MySQL 8, API REST) | **PostgreSQL 11‑13** ; **REST JSON** | Tests d’intégration via `docker‑compose` – validation des drivers | 4 |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Appréhensibilité** | Temps de formation (lecture du README + `docker compose up`) | **≤ 15 min** | Chronométrage de nouveaux développeurs (cohort ≥ 5) | 4 |
| **Apprenabilité** | Taux de réussite des tâches “démarrer l’environnement” sans aide | **≥ 90 %** | Observation directe (test d’onboarding) | 3 |
| **Opérabilité** | Nombre de commandes Docker nécessaires pour le scénario “full‑stack” | **≤ 4** (ex : `docker compose -f docker-compose.dev.yml up -d`) | Analyse du script d’onboarding | 3 |
| **Esthétique de l’interface** | Score SUS (System Usability Scale) sur le README/CLI | **≥ 68 / 100** | Survey SUS auprès des devs | 5 |
| **Accessibilité** | Conformité WCAG 2.1 niveau AA pour la documentation web interne | **Oui** | Audit avec axe‑core | 5 |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Maturité** | Densité de défauts (bugs) / KLOC (Dockerfile + scripts) | **≤ 0.2 defects/KLOC** | Historique JIRA/Issues (bugs remontés) | 2 |
| **Disponibilité** | % de temps où l’environnement est opérationnel (health‑check OK) | **≥ 99,5 %** | Prometheus `up{job="agile-env"}` | 2 |
| **Tolérance aux fautes** | Temps de récupération (RTO) après arrêt du conteneur DB | **≤ 30 s** | Test de redémarrage (`docker compose restart db`) | 3 |
| **Récupérabilité** | Point de récupération (RPO) – dernière sauvegarde des volumes DB | **≤ 15 min** | Snapshot automatisé (Docker volume backup) | 3 |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Confidentialité** | Score d’audit (Trivy + OWASP ASVS 4.0) | **≥ 90 %** (pas de vulnérabilités critiques) | `trivy image php:7.3‑apache‑buster` + `trivy image postgres:11‑alpine` | 1 |
| **Intégrité** | Presence de mécanismes de vérification d’image (Docker Content Trust) | **Oui** | CI → `DOCKER_CONTENT_TRUST=1` | 2 |
| **Non‑répudiation** | Journalisation des actions administratives (Docker events) | **Oui** | Centralisation via `fluentd` → ELK | 2 |
| **Responsabilité** | Couverture du traçage d’audit (ex : modifications de variables .env) | **≥ 95 %** | Audit des changements Git + Docker‑compose logs | 3 |
| **Authenticité** | Méthodes d’authentification (basic auth + OAuth2 via CAS) | **Oui** | Tests d’accès aux services (curl with token) | 2 |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Modularité** | Ratio de modules indépendants (Docker‑services) | **≥ 80 %** (services distincts) | Analyse `docker‑compose.yml` | 3 |
| **Réutilisabilité** | % de composants Docker réutilisables dans d’autres projets | **≥ 60 %** | Inventaire des images (php‑base, postgres‑base) | 4 |
| **Analysabilité** | Complexité cyclomatique moyenne des scripts Bash (`check‑env.sh`) | **≤ 5** | SonarQube → `cognitive_complexity` | 3 |
| **Modifiabilité** | Temps moyen de modification d’une variable d’environnement (incl. rebuild) | **≤ 10 min** | Chronométrage d’un ticket “change DB port” | 3 |
| **Testabilité** | Couverture de tests (Docker‑compose + k6) | **≥ 80 %** des scénarios critiques | Rapport `k6 run –summary` | 2 |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Pondération |
|---|---|---|---|---|
| **Adaptabilité** | Nombre d’environnements supportés (Linux x86_64, macOS Intel, Windows 10 WSL2) | **3** | Tests de build sur chaque OS (GitLab CI matrix) | 4 |
| **Installabilité** | Temps d’installation (script `setup.sh`) | **≤ 5 min** | Chronométrage sur machine vierge | 3 |
| **Remplaçabilité** | Compatibilité avec formats de configuration standards (env‑file, ini, php array) | **Oui** | Validation du parsing (`dotenv`, `parse_ini_file`) | 4 |

---  

## 4. Architecture technique  

| Élément | Description | Justification qualité |
|---|---|---|
| **Docker‑Compose (v1.29+)** | Orchestration de trois services : `app` (PHP‑Apache), `db` (PostgreSQL) et `proxy` (optionnel) | **Compatibilité**, **Portabilité**, **Déploiement rapide** |
| **Multi‑stage Dockerfile (Dockerfile‑app)** | 1️⃣ Stage `composer` → download dependencies ; 2️⃣ Stage `php:7.3‑apache‑buster` → runtime | **Performance** (réduction de l’image), **Sécurité** (image minimale), **Maintenabilité** (séparation claire) |
| **Variables d’environnement (.env)** | Centralise configuration (proxy, DB credentials, CAS URL) | **Usabilité** (facilité de paramétrage), **Sécurité** (pas de secrets en clair dans Dockerfile) |
| **Configuration Apache (000‑default.conf)** | VirtualHost dédié, expose `/` sur le port 80 | **Compatibilité** (standard Apache), **Performance** (keep‑alive) |
| **Base de données PostgreSQL (docker/db/Dockerfile)** | Image `postgres:11‑alpine` + scripts d’initialisation (`initdb/*.sql`) | **Fiabilité** (image LTS), **Portabilité** (alpine) |
| **Pattern architectural** | **Micro‑service léger** – chaque conteneur possède une responsabilité unique. Utilisation du **Pattern “Adapter”** pour la couche de persistance (PDO). | **Modularité**, **Réutilisabilité**, **Testabilité** |

> **Diagramme de composants** (texte ≈ UML)  

```
[Developer] --> (docker‑compose) --> [app: php‑apache] <---> [db: postgres]
               |                                 |
               |                                 +--> (config: .env, 000‑default.conf)
               |
               +--> (CI/CD) --> (GitLab Runner) --> (hadolint, trivy, sonar)
```  

---  

## 5. Stack technologique qualifié  

| Couche | Technologie | Version | Licence | Pourquoi ? |
|---|---|---|---|---|
| **Conteneurisation** | Docker Engine | ≥ 20.10 | Apache 2.0 | Standard de l’industrie, isolation fiable |
| **Orchestration** | Docker‑Compose | 1.29.2 | Apache 2.0 | Simplicité pour les devs, support multi‑OS |
| **Runtime PHP** | php:7.3‑apache‑buster | 7.3.33‑buster | PHP License | Compatibilité avec l’application existante |
| **Gestionnaire de dépendances** | Composer | 2.6.5 | MIT | Standard PHP, version lockée via `composer.lock` |
| **Base de données** | postgres:11‑alpine | 11.20‑alpine | PostgreSQL License | LTS, image légère |
| **Analyse statique** | Hadolint, ShellCheck, SonarQube | latest | MIT (hadolint) / GPL (Sonar) | Qualité du code Docker & Bash |
| **Sécurité** | Trivy, OWASP ASVS 4.0 | latest | Apache 2.0 | Scan des vulnérabilités |
| **Monitoring** | Prometheus + Grafana | 2.49 / 10.4 | Apache 2.0 | Métriques temps réel |
| **Tests de charge** | k6 | 0.53 | AGPL‑3.0 | Mesure du comportement temporel |
| **CI/CD** | GitLab CI | 16.x | MIT | Intégration native avec repository |

---  

## 6. Stratégie de test et validation  

| Niveau | Objectif | Outils / Métriques | Critères d’acceptation |
|---|---|---|---|
| **Unitaire** | Vérifier la syntaxe des Dockerfiles & scripts | `hadolint`, `ShellCheck` | 0 warnings critiques |
| **Intégration** | Lancer l’ensemble avec `docker‑compose.dev.yml` | GitLab CI job **docker‑compose‑up** | Tous les conteneurs **healthy** (< 30 s) |
| **Performance** | Temps de réponse & utilisation ressources | Prometheus (`http_response_time_seconds`), k6 | < 200 ms 95ᵉ percentile, CPU ≤ 45 % |
| **Sécurité** | Détecter vulnérabilités & mauvaises configurations | Trivy, OWASP ASVS checklist | Aucun CVE ≥ 7, score audit ≥ 90 % |
| **Acceptation** | Validation métier (CCF) | Demo fonctionnelle + questionnaire devs | ≥ 90 % de réponses “satisfait” |
| **Production** | Supervision continue | Grafana dashboards, alerting (thresholds) | Alerte < 5 % du temps, MTTR ≤ 30 min |

---  

## 7. Supervision et métriques  

| Métrique (production) | Seuil d’alerte | Tableau de bord | Action corrective |
|---|---|---|---|
| **Disponibilité (health‑check OK)** | < 99,5 % (sur 1 h) | Grafana `service_up` | Redémarrage du conteneur, analyse log |
| **Latence HTTP 95ᵉ pct** | > 250 ms | Grafana `http_response_time_seconds` | Scaling du conteneur PHP, optimisation du code |
| **CPU % du conteneur PHP** | > 70 % (5 min) | Grafana `container_cpu_usage_seconds_total` | Augmenter replicas, revoir dépendances |
| **Vulnérabilités critiques (Trivy)** | > 0 | GitLab Security Dashboard | Patch de l’image, rebuild |
| **Échec du `docker compose up`** | > 0 | CI job status | Analyse du log, correction du Dockerfile |
| **Taux de réussite des tests k6** | < 95 % | GitLab CI `k6` report | Optimiser requêtes, augmenter ressources DB |

---  

## 8. Documentation technique  

| Artefact | Format | Responsable | Fréquence de mise à jour |
|---|---|---|---|
| **README.md** (racine) | Markdown | Lead DevOps | À chaque version majeure |
| **Dockerfile‑app** | Dockerfile + commentaires | DevOps | Lors de changement d’image |
| **docker‑compose.dev.yml** | YAML | DevOps | Chaque ajout de service |
| **API docs** (si applicatif) | Swagger/OpenAPI | Backend Lead | Aligné avec version du code |
| **Guide d’onboarding** | Markdown + vidéo | QA | Annuel ou après refactor |
| **Runbooks (monitoring, backup)** | Markdown | SRE | Après incident ou mise à jour majeure |
| **Cahier des exigences (CCF)** | Excel / Jira | PO | En continu (backlog) |

---  

## 9. Gestion des dettes techniques  

| Risque / Dette | Impact | Priorité | Plan de remboursement |
|---|---|---|---|
| **PHP 7.3 EOL (2024)** – image obsolète | Sécurité, support | **Haute** | Migrer vers `php:8.2‑apache` (sprint Q3 2026) |
| **Dockerfile‑app non‑optimisé (apt‑cache)** | Taille image, temps de build | **Moyenne** | Nettoyer le cache (`apt-get clean && rm -rf /var/lib/apt/lists/*`) – sprint Q2 2026 |
| **Absence de tests unitaires pour scripts Bash** | Fiabilité | **Moyenne** | Ajouter `bats` tests – sprint Q4 2026 |
| **Gestion des secrets en clair dans `.env`** | Confidentialité | **Haute** | Intégrer HashiCorp Vault ou GitLab CI variables – sprint Q1 2027 |
| **Documentation obsolète** | Utilisabilité | **Moyenne** | Revue trimestrielle – owners assignés |

---  

## Annexes  

### A – Matrice de traçabilité CCF ↔ CST  

| CCF (exemple) | Description | Caractéristique ISO 25010 | Sous‑caractéristique | Métrique CST correspondante |
|---|---|---|---|---|
| **AG‑001** | L’environnement doit démarrer en < 2 min | Performance Efficiency | Comportement temporel | Temps de réponse 95ᵉ pct ≤ 200 ms |
| **AG‑002** | Les variables de connexion DB doivent être configurables | Compatibility | Interopérabilité | Formats supportés – PostgreSQL 11‑13 |
| **AG‑003** | Le conteneur PHP doit exposer le port 80 | Functional Suitability | Complétude fonctionnelle | % CCF couverts ≥ 95 % |
| **AG‑004** | Les logs d’audit doivent être centralisés | Security | Non‑répudiation | Journalisation des actions admin (Oui) |
| **AG‑005** | Le projet doit être déployable sous macOS Catalina | Portability | Adaptabilité | Support 3 OS (Linux, macOS, Windows) |
| **…** | … | … | … | … |

*(La matrice complète, avec les 15 CCF du backlog, est fournie dans le fichier `CCF‑CST‑Mapping.xlsx` joint.)*  

---  

### B – Glossaire  

| Terme | Définition |
|---|---|
| **CCF** | Cas de Conception Fonctionnelle – exigences fonctionnelles du client. |
| **RTO** | Recovery Time Objective – délai maximal acceptable pour rétablir le service. |
| **RPO** | Recovery Point Objective – perte de données maximale tolérée. |
| **SUS** | System Usability Scale – score d’utilisabilité (0‑100). |
| **Trivy** | Scanner de vulnérabilités d’images Docker. |
| **Hadolint** | Linter pour Dockerfile. |
| **k6** | Outil de test de charge et de performance. |
| **Prometheus** | Système de collecte de métriques. |
| **Grafana** | Plateforme de visualisation de métriques. |

---  

## Signature  

| Rôle | Nom | Date | Signature |
|---|---|---|---|
| **Chef de projet** | (à compléter) | 2026‑04‑28 |  |
| **Architecte Qualité** | (à compléter) | 2026‑04‑28 |  |
| **Responsable Sécurité** | (à compléter) | 2026‑04‑28 |  |

---  

*Ce CST est destiné à être versionné dans le dépôt Git du projet (`/docs/CST_agile-env_v1.0.md`) et à servir de référence pour toutes les phases du cycle de vie logiciel (planification, conception, implémentation, test, exploitation et évolution).*