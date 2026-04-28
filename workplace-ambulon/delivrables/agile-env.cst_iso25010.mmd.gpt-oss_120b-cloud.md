# Cahier des Spécifications Techniques (CST) – **agile‑env**  
**Projet** : *agile‑env* – Environnement de développement Docker pour l’application *ambulon*  
**Version CST** : 1.0 – 2026‑04‑28  

---  

## 1. Introduction et contexte qualité  

| Élément | Description |
|--------|-------------|
| **Objectifs qualité du projet** | • Fournir un environnement de développement reproductible, stable et sécurisé. <br>• Garantir la disponibilité ≥ 99,9 % en CI/CD. <br>• Limiter le temps de mise à jour ≤ 30 min. |
| **Contexte métier** | L’équipe *ambulon* développe une application PHP 7.3 sous Apache, persistant ses données dans PostgreSQL 11. Le besoin est d’avoir un **docker‑compose** local qui reproduise la stack de production pour les développeurs, les tests d’intégration et les revues de code. |
| **Contexte technique** | • Docker ≥ 20.10, Docker‑Compose ≥ 2.0 <br>• Base d’image : `php:7.3‑apache‑buster` et `postgres:11‑alpine` <br>• Utilisation d’un proxy interne (variables `http_proxy`/`https_proxy`). |
| **Références aux exigences fonctionnelles (CCF)** | Voir matrice **CCF ↔ Qualité** (section 3.9). |
| **Méthodologie d’évaluation** | • **Mesure continue** via SonarQube, Prometheus + Grafana et des scripts d’audit (OWASP ASVS). <br>• **Revues de code** (pull‑request) pour la conformité aux règles de style et de sécurité. <br>• **Tests automatisés** (unités, intégration, charge). |

---  

## 2. Modèle de qualité ISO / IEC 25010  

```
                    ┌─────────────────────────────────────┐
                    │     QUALITÉ DU PRODUIT LOGICIEL     │
                    └─────────────────────────────────────┘
                                        │
    ┌───────────┬───────────┬───────────┼───────────┬───────────┬───────────┬───────────┐
    ▼           ▼           ▼           ▼           ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│Aptitude│ │Performance│ │Compatibilité│ │Utilisabilité│ │Fiabilité│ │Sécurité│ │Maintenabilité│ │Portabilité│
│fonction│ │efficacité│ │            │ │            │ │          │ │       │ │            │ │           │
│-nelle │ │           │ │            │ │            │ │          │ │       │ │            │ │           │
└───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘  └───────┘
```  

---  

## 3. Spécification détaillée par caractéristique  

> **Notation** : chaque sous‑caractéristique possède : (i) Métrique, (ii) Objectif chiffré, (iii) Méthode de vérification, (iv) Pondération (0‑5) selon la priorité métier.  

| Caractéristique | Sous‑caractéristique | Métrique | Objectif | Vérif. | Pondération |
|-----------------|----------------------|----------|---------|--------|-------------|
| **3.1 Aptitude fonctionnelle** | Complétude fonctionnelle | % d’exigences fonctionnelles couvertes (CCF) | **≥ 95 %** | Rapport de couverture CCF (script `ccf‑coverage.sh`) | 5 |
| | Exactitude fonctionnelle | Taux d’erreurs de provisionnement (docker‑compose up) | **≤ 0.5 %** | Tests d’intégration (CI) – `docker‑compose‑test.yml` | 4 |
| | Adéquation fonctionnelle | Score d’évaluation utilisateur (échelle 1‑5) | **≥ 4/5** | Survey post‑déploiement (Google‑Form) | 3 |
| **3.2 Performance et efficacité** | Comportement temporel | Temps de réponse 95ᵉ percentile du conteneur *app* (HTTP GET `/health`) | **≤ 200 ms** | Test Load (`hey` ou `k6`) dans pipeline CI | 4 |
| | Utilisation des ressources | CPU ≤ 30 % / RAM ≤ 250 MiB en charge nominale (2 devs + CI) | **≤ 30 % CPU**, **≤ 250 MiB RAM** | Prometheus + Grafana dashboards `agile‑env‑metrics` | 4 |
| | Capacité | Nombre d’utilisateurs simultanés supportés (sessions HTTP) | **≥ 50** | Test de charge `k6` (scenario 50 VUs) | 3 |
| **3.3 Compatibilité** | Cohérence | Conformité aux standards Docker‑Compose 3.8 (YAML lint) | **100 %** | `docker‑compose‑lint` (yamllint + docker‑compose‑config) | 3 |
| | Interopérabilité | Nombre de formats de variables d’environnement supportés (`.env`, `docker secret`, `ConfigMap`) | **≥ 2** | Inspection du script d’entrée `entrypoint.sh` | 2 |
| **3.4 Utilisabilité** | Appréhensibilité | Temps moyen de mise en route (clone + `docker‑compose up`) | **≤ 5 min** | Chronométrage automatisé (`setup‑timer.sh`) | 3 |
| | Apprenabilité | % de développeurs réussissant le *first‑run* sans aide | **≥ 90 %** | Questionnaire d’onboarding | 3 |
| | Opérabilité | Nombre moyen de commandes Docker nécessaires pour un *reset* complet | **≤ 3** | Script `reset‑env.sh` (3 cmd) | 2 |
| | Esthétique de l’interface | Score SUS (System Usability Scale) du README + docs | **≥ 68/100** | Survey SUS | 2 |
| | Accessibilité | Conformité WCAG 2.1 AA du portail de documentation (GitLab Wiki) | **Oui** | Audit Axe‑core | 1 |
| **3.5 Fiabilité** | Maturité | Densité de défauts (bugs) détectés en QA / KLOC | **≤ 0.2 bugs/KLOC** | SonarQube “bugs” metric | 4 |
| | Disponibilité | % de temps où `docker‑compose up` est opérationnel (sur 30 jours) | **≥ 99,9 %** | Monitoring uptime (Uptime‑Robot) | 5 |
| | Tolérance aux fautes | RTO (Recovery Time Objective) après arrêt du conteneur DB | **≤ 1 min** | Test de résilience (`docker‑restart‑test.sh`) | 4 |
| | Récupérabilité | RPO (Recovery Point Objective) des bases PostgreSQL | **≤ 5 min** | Backup schedule (`pg_dump` cron) | 4 |
| **3.6 Sécurité** | Confidentialité | Score d’audit OWASP ASVS Level 2 (v4.0) | **≥ 90 %** | Scan `owasp‑zap` + `trivy` | 5 |
| | Intégrité | Présence de signatures d’image (Docker Content Trust) | **Oui** | `docker trust inspect` | 4 |
| | Non‑répudiation | Journalisation centralisée des actions `docker‑events` → ELK | **Oui** | Vérif. log ELK | 4 |
| | Responsabilité | Couverture du traçage d’audit (ID utilisateur → action) | **≥ 95 %** | Analyse log ELK | 3 |
| | Authentification | Méthodes d’authentification (Basic + OAuth) exposées via Apache | **Oui** | Test d’accès `curl -u` & token | 3 |
| **3.7 Maintenabilité** | Modularité | Couplage moyen (LCOM) ≤ 0.3, Cohésion ≥ 0.7 (analysé par SonarQube) | **LCOM ≤ 0.3** / **Cohésion ≥ 0.7** | SonarQube | 4 |
| | Réutilisabilité | % de scripts Docker réutilisables dans d’autres projets | **≥ 30 %** | Inventaire `docker‑reusables/` | 2 |
| | Analysabilité | Complexité cyclomatique moyenne ≤ 10 (PHP) | **≤ 10** | SonarQube “cognitive complexity” | 3 |
| | Modifiabilité | Temps moyen de modification d’une variable d’environnement (incl. tests) | **≤ 0.5 h** | Historique Git (lead‑time) | 3 |
| | Testabilité | Couverture de tests unitaires (PHPUnit) ≥ 80 % | **≥ 80 %** | SonarQube “coverage” | 4 |
| **3.8 Portabilité** | Adaptabilité | Nombre d’environnements supportés (Linux x86_64, macOS ARM, Windows WSL) | **≥ 3** | CI matrix (`docker‑build‑matrix.yml`) | 2 |
| | Installabilité | Temps d’installation (script `install‑env.sh`) | **≤ 10 min** | Chronométrage automatisé | 2 |
| | Remplaçabilité | Compatibilité avec images alternatives (`php:8.0‑apache`, `postgres:13`) | **Oui (tests)** | Matrix de tests de compatibilité | 1 |

---

### 3.9 Matrice de traçabilité CCF ↔ Qualité  

| CCF (Exigence fonctionnelle) | Description | Caractéristique ISO 25010 liée | Sous‑caractéristique | Métrique de conformité |
|-------------------------------|-------------|--------------------------------|----------------------|------------------------|
| **CCF‑001** | Provisionner une base PostgreSQL 11 avec scripts d’initialisation. | Fiabilité – Disponibilité | Disponibilité | % uptime du conteneur DB (Uptime‑Robot) |
| **CCF‑002** | Fournir une stack Apache + PHP 7.3 configurée (vhost, php.ini). | Compatibilité – Cohérence | Cohérence | Validation `docker‑compose‑config` contre schema |
| **CCF‑003** | Permettre le lancement en une commande (`docker‑compose up -d`). | Utilisabilité – Appréhensibilité | Temps de mise en route | Chronométrage `setup‑timer.sh` |
| **CCF‑004** | Exposer les variables d’environnement via fichier `.env`. | Sécurité – Confidentialité | Confidentialité | Scan de fuite de secrets (`trivy`) |
| **CCF‑005** | Supporter le re‑build d’image avec le cache Docker. | Performance – Capacité | Capacité | Temps de `docker build` (benchmark) |
| **CCF‑006** | Autoriser le remplacement du conteneur DB par une version `postgres:13` en CI. | Portabilité – Remplaçabilité | Remplaçabilité | Succès du job CI `db‑upgrade‑test` |
| **CCF‑007** | Générer un fichier de santé (`/health`) répondant 200 ms. | Performance – Comportement temporel | Temps de réponse | Test load `k6 healthcheck.js` |
| **CCF‑008** | Journaliser toutes les actions Docker (start/stop) dans ELK. | Sécurité – Non‑répudiation | Journalisation | Vérif. log ELK (query) |
| **CCF‑009** | Fournir un Docker‑Compose multi‑environnement (dev, test). | Portabilité – Adaptabilité | Environnements supportés | CI matrix `docker‑compose‑matrix.yml` |
| **CCF‑010** | Documenter le processus d’on‑boarding (README). | Utilisabilité – Esthétique | SUS | Score SUS via questionnaire |

---

## 4. Architecture technique  

### 4.1 Diagramme de composants (UML)  

```mermaid
graph TD
    A[Developer Machine] -->|docker‑compose| B[Docker Network "agile‑env"]
    B --> C[php_7.3‑apache (app)]
    B --> D[postgres_11‑alpine (db)]

    C -->|HTTP| E[Apache vhost 000‑default.conf]
    C -->|PHP| F[PHP extensions (pdo, pdo_pgsql, intl)]

    D -->|SQL scripts| G[initdb/*.sql]
    D -->|restore script| H[restore.sh]

    subgraph "Configuration"
    I[.env] --> C
    J[param.ini] --> D
    K[config_CAS.php] --> C
    end

    subgraph "CI/CD"
    L[GitLab Runner] -->|build| C
    L -->|test| D
    L -->|scan| M[Trivy/OWASP‑ZAP]
    end

    subgraph "Monitoring"
    N[Prometheus] --> C
    N --> D
    O[Grafana] --> N
    P[ELK] --> L
    end
```

### 4.2 Justification des choix techniques  

| Décision | Impact qualité |
|----------|----------------|
| **Docker‑Compose v3.8** – orchestration déclarative | **Compatibilité** (cohérence) + **Portabilité** (multi‑OS) |
| **Image `php:7.3‑apache‑buster`** – version LTS sécurisée | **Sécurité** (patches) + **Maintenabilité** (déploiement standard) |
| **PostgreSQL 11‑alpine** – image minimaliste | **Performance** (faible empreinte) + **Portabilité** (alpine) |
| **Proxy interne** via `ENV http_proxy/https_proxy` | **Sécurité** (contrôle du trafic) + **Compatibilité** (environnements d’entreprise) |
| **Trivy & OWASP‑ZAP** dans pipeline CI | **Sécurité** (vulnérabilités) + **Fiabilité** (prévention de régressions) |
| **Prometheus/Grafana** pour métriques | **Performance** (monitoring temps réel) + **Fiabilité** (détection d’incidents) |
| **ELK** pour audit | **Sécurité** (non‑répudiation) + **Maintenabilité** (traceabilité) |

---

## 5. Stack technologique qualifié  

| Catégorie | Technologie | Version | Licence | Raison qualité |
|-----------|-------------|----------|---------|----------------|
| **Conteneurisation** | Docker Engine | 24.0.5 | Apache 2.0 | Standard de déploiement, isolement |
| **Orchestration** | Docker‑Compose | 2.20.2 | Apache 2.0 | Simplicité, prise en charge multi‑OS |
| **Base PHP** | php:7.3‑apache‑buster | 7.3.33‑buster | PHP License | LTS, extensions pdo, intl |
| **Base DB** | postgres:11‑alpine | 11.20‑alpine | PostgreSQL Licence | Légèreté, performances |
| **Gestion de dépendances** | Composer | latest | MIT | Gestion PHP moderne |
| **Gestion de code** | GitLab CE | 16.5 | MIT | CI/CD intégré |
| **Analyse statique** | SonarQube | 10.5 | GNU GPL v3 | Qualité code, métriques |
| **Scanning sécurité** | Trivy | 0.49.1 | Apache 2.0 | Vulnérabilités images |
| **Tests de charge** | k6 | 0.53.0 | AGPL‑3.0 | Performance, RTO |
| **Monitoring** | Prometheus | 2.53.0 | Apache 2.0 | Collecte métriques |
| **Dashboard** | Grafana | 10.4.0 | AGPL‑3.0 | Visualisation |
| **Logging/Audit** | ELK (Elasticsearch 8.x, Logstash, Kibana) | 8.12 | Elastic License | Traçabilité, non‑répudiation |
| **Lint YAML** | yamllint | 1.35.1 | GPL‑3.0 | Cohérence config |
| **Tests unitaires** | PHPUnit | 10.5 | BSD‑3 | Testabilité |

---

## 6. Stratégie de test et validation  

| Niveau | Objectif | Outils | Métriques cibles |
|--------|----------|--------|-------------------|
| **Unitaires** | Vérifier logique PHP (fonctions, classes) | PHPUnit, Xdebug | Couverture ≥ 80 % |
| **Intégration** | Interaction app ↔ DB, variables d’environnement | Docker‑Compose, Testcontainers, PHPUnit‑DB | Succès ≥ 99 % des scénarios |
| **Fonctionnels** | Scénarios métier (ex. login CAS) | Cypress (front) + Postman (API) | Taux de réussite ≥ 95 % |
| **Performance** | Temps de réponse, charge | k6, Locust, Grafana alerts | 95ᵉ percentile ≤ 200 ms |
| **Sécurité** | Détection vulnérabilités, conformité | Trivy, OWASP‑ZAP, Snyk | Score ASVS ≥ 90 % |
| **Résilience** | RTO/RPO, redémarrage DB | Chaos‑Monkey (Docker‑kill), scripts `restart‑test.sh` | RTO ≤ 1 min, RPO ≤ 5 min |
| **Acceptation** | Validation par PO/DevOps | GitLab Merge Request, checklist | Tous les critères de la matrice CCF satisfaits |

*Critères d’acceptation technique* : chaque métrique doit atteindre son objectif (see §3). Un **pipeline CI** automatisé exécute l’ensemble des tests et bloque le merge si une violation est détectée.

---

## 7. Supervision et métriques  

| KPI | Source de données | Seuil d’alerte | Dashboard |
|-----|-------------------|----------------|------------|
| **Uptime app** | Uptime‑Robot / Prometheus `up` | < 99,9 % (rouge) | Grafana “Availability” |
| **CPU/Memory** | Prometheus `container_cpu_usage_seconds_total`, `container_memory_usage_bytes` | CPU > 70 % (warning) / > 90 % (critical) | Grafana “Resources” |
| **Temps de réponse 95ᵉ pct** | Prometheus `http_request_duration_seconds` | > 250 ms (warning) | Grafana “Latency” |
| **Bugs/defects** | SonarQube “bugs” | > 0.2 bugs/KLOC (warning) | SonarQube “Quality Gate” |
| **Score de sécurité Trivy** | Trivy scan report | > 5 high CVEs (critical) | GitLab CI “Security” |
| **Couverture tests** | SonarQube “coverage” | < 80 % (warning) | SonarQube |
| **Logs d’audit** | ELK Kibana | Absence d’événement critique (e.g., auth failures) > 5 min | Kibana “Audit” |

### Alerting (exemple)  

```yaml
# prometheus-alerts.yml
groups:
  - name: agile-env-availability
    rules:
      - alert: AppDown
        expr: up{job="agile-env-app"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "L'application agile‑env est indisponible"
          description: "Aucun conteneur app ne répond depuis plus de 2 minutes."
```

---

## 8. Documentation technique  

| Artefact | Format | Responsable | Norme |
|----------|--------|--------------|-------|
| **README** | Markdown | DevOps Lead | GitLab‑Wiki style |
| **Dockerfiles** | Dockerfile | Infra Engineer | Dockerfile best‑practices (Docker‑file‑lint) |
| **docker‑compose.yml** | YAML | Infra Engineer | Docker‑Compose schema v3.8 |
| **API docs** | OpenAPI 3.0 (yaml) | Backend Lead | Swagger‑UI |
| **Code** | PHP (PSR‑12) | Developers | PHP‑CS‑Fixer, PHPStan |
| **Scripts d’installation** | Bash | DevOps Lead | ShellCheck |
| **Tests** | PHPUnit, k6 scripts | QA Engineer | JUnit XML reports |
| **Monitoring** | Grafana dashboards (JSON) | SRE | Grafana best‑practices |
| **Sécurité** | Trivy & OWASP‑ZAP reports | Security Engineer | OWASP ASVS v4.0 |

Tous les artefacts sont versionnés dans le dépôt GitLab, taggés avec le numéro de version du *environment* (`agile-env-vX.Y.Z`).  

---

## 9. Gestion des dettes techniques  

| Risque / Dette | Impact | Action corrective | Priorité | Échéance |
|----------------|--------|-------------------|----------|----------|
| **Dockerfile « composer :latest »** | Image non figée → ruptures | Pin version (`composer:2.7.6`) | Haute | Sprint 1 |
| **PHP 7.3** (EOL 2024) | Fin de support sécurité | Migration vers `php:8.2‑apache` | Moyenne | Sprint 3 |
| **Absence de tests d’intégration DB** | Risque de régression de schéma | Ajouter `testcontainers‑php` + CI job | Haute | Sprint 2 |
| **Logging des variables d’environnement** | Fuite possible d’informations sensibles | Masquer les valeurs dans ELK via pipeline | Haute | Immédiat |
| **Documentation README minimal** | Onboarding long | Rédiger guide détaillé + vidéos | Moyenne | Sprint 2 |
| **Pas de scan de licences** | Risque de non‑conformité | Intégrer `FOSSA` ou `Licensee` dans CI | Faible | Sprint 4 |

*Suivi* – Le tableau de dettes est maintenu dans le projet GitLab sous **Issues → Epic “Technical Debt”**. Chaque dette possède un **Definition of Done (DoD)** incluant mise à jour de la documentation et des métriques associées.

---  

## Annexes  

### A. Tableau récapitulatif des objectifs chiffrés  

| Sous‑caractéristique | Objectif | Métrique | Source |
|----------------------|----------|----------|--------|
| Complétude fonctionnelle | ≥ 95 % | % CCF couverts | `ccf‑coverage.sh` |
| Temps de réponse 95ᵉ pct | ≤ 200 ms | `http_request_duration_seconds` | Prometheus |
| CPU utilisation (app) | ≤ 30 % | `container_cpu_usage_seconds_total` | Prometheus |
| Disponibilité (app) | ≥ 99,9 % | Uptime‑Robot | Grafana |
| Score OWASP ASVS | ≥ 90 % | Trivy + ZAP | GitLab CI |
| Couverture tests unitaires | ≥ 80 % | SonarQube “coverage” | SonarQube |
| RTO (DB) | ≤ 1 min | `restart‑test.sh` | CI |
| RPO (DB) | ≤ 5 min | Backup interval | Cron |
| SUS (README) | ≥ 68/100 | Survey SUS | Google‑Form |
| Adaptabilité | ≥ 3 environnements | CI matrix success | GitLab CI |

### B. Glossaire  

| Acronyme | Signification |
|----------|---------------|
| CCF | **C**apabilité **C**ontrôle **F**onctionnelle (exigence fonctionnelle) |
| RTO | **Recovery Time Objective** |
| RPO | **Recovery Point Objective** |
| SUS | **System Usability Scale** |
| OWASP ASVS | **Application Security Verification Standard** |
| CI/CD | **Continuous Integration / Continuous Delivery** |
| LCOM | **Lack of Cohesion of Methods** |
| KLOC | **Kilo Lines of Code** |

---  

*Ce CST est vivant : il sera révisé à chaque version majeure de l’environnement (ex. migration PHP 8.x, changement de base de données). Les métriques et seuils seront ajustés en fonction des retours d’expérience et des exigences métier évolutives.*  