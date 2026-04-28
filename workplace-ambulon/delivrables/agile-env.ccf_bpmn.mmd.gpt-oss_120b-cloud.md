# Cahier des Charges Fonctionnel (CCF) – **agile‑env**
> **Projet** : agile‑env  
> **Chemin** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\agile-env`  
> **Norme** : ISO/IEC 19510 :2013 (BPMN 2.0) – Maintenue par l’OMG  

---

## 1. Introduction & Contexte

| Élément | Description |
|--------|-------------|
| **Organisation** | Équipe DevOps / Développement d’ambulon (application PHP/Apache) hébergée dans des conteneurs Docker. |
| **Environnement** | Linux (Debian buster) – images Docker officielles : `postgres:11‑alpine`, `php:7.3‑apache‑buster`, `composer:latest`. |
| **Objectifs BPMN** | • Formaliser les flux de *provisionnement* et *déploiement* de l’environnement de développement. <br>• Garantir la traçabilité des exigences fonctionnelles et non‑fonctionnelles. <br>• Produire des modèles exécutables (niveau *Common Executable*) afin de pouvoir les exporter vers Camunda / Activiti. |
| **Périmètre** | - Construction de l’image **DB** (Dockerfile `docker/db/Dockerfile`). <br>- Construction de l’image **App** (Dockerfile‑app). <br>- Orchestration via `docker‑compose.dev.yml`. <br>- Gestion des paramètres (`.env`, `config_CAS.php`, `param.ini`). <br>- Cycle de vie du conteneur (build → start → stop → clean). |
| **Glossaire** | <ul><li>**DevOps Engineer** – Responsable du provisioning des conteneurs.</li><li>**DB Admin** – Responsable du script d’initialisation PostgreSQL.</li><li>**App Developer** – Responsable du code PHP et des dépendances Composer.</li><li>**Artifact** – Fichier de configuration, script d’initialisation ou image Docker.</li></ul> |

---

## 2. Cartographie des processus (Process Map)

### 2.1 Nomenclature hiérarchique

| Niveau | Type | Exemple |
|-------|------|---------|
| **1** | Processus métier stratégique | **P‑001** : *Gestion du cycle de vie de l’environnement de développement* |
| **2** | Processus métier opérationnel | **P‑001‑A** : *Construire l’image de la base de données* <br> **P‑001‑B** : *Construire l’image applicative* |
| **2** | Processus de support | **P‑001‑C** : *Gestion des secrets et variables d’environnement* |
| **2** | Processus de management | **P‑001‑D** : *Contrôle de conformité & reporting* |

### 2.2 Matrice de processus

| ID Processus | Nom | Type | Propriétaire | Priorité |
|--------------|-----|------|--------------|----------|
| **P‑001‑A** | Construire l’image DB | Opérationnel | DB Admin | Critique |
| **P‑001‑B** | Construire l’image App | Opérationnel | DevOps Engineer | Critique |
| **P‑001‑C** | Gestion des variables d’environnement | Support | DevOps Engineer | Important |
| **P‑001‑D** | Contrôle de conformité (BPMN, Sécurité) | Management | QA Lead | Important |
| **P‑001‑E** | Orchestration via Docker‑Compose | Opérationnel | DevOps Engineer | Critique |
| **P‑001‑F** | Mise à jour de l’application | Opérationnel | App Developer | Important |

---

## 3. Modélisation BPMN détaillée

> **Notation** : Diagrammes Mermaid compatibles BPMN 2.0 (exécutables).  
> **Convention** : Un diagramme = un niveau d’abstraction (règle 1).  

### 3.1 Diagramme de **Collaboration** – Provisionnement complet

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#2F80ED', 'edgeLabelBackground':'#fff' }}%%%%%%%%%%%%%%%%%%}%%
bpmnDiagram
  participant DevOps as "DevOps Engineer"
  participant DB as "PostgreSQL DB"
  participant App as "PHP / Apache App"

  DevOps->>DB: Build DB image (Dockerfile‑db)
  DB-->>DevOps: Image disponible (agile‑env-db_latest)

  DevOps->>App: Build App image (Dockerfile‑app)
  App-->>DevOps: Image disponible (agile‑env-app_latest)

  DevOps->>DB: docker‑compose up (service db)
  DB->>DB: Initialise schema (initdb/*.sql)
  DB-->>DevOps: DB ready (port 5432)

  DevOps->>App: docker‑compose up (service app)
  App->>App: Copie config (000‑default.conf, .env, param.ini)
  App->>App: Composer install (vendor)
  App-->>DevOps: App ready (http://localhost)

  DevOps->>DevOps: Vérification health‑check (GET /status)
  DevOps-->>DevOps: OK → Cycle de vie démarré
```

### 3.2 Diagramme de **Processus** – *Construire l’image DB* (P‑001‑A)

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%
bpmnDiagram
  startEvent(start1, "Déclenchement manuel / CI")
  task(buildDocker, "docker build –f docker/db/Dockerfile .")
  task(tagImage, "docker tag → agile‑env‑db_latest")
  task(pushRegistry, "docker push (registry interne)")
  endEvent(end1, "Image DB disponible")
  startEvent --> buildDocker --> tagImage --> pushRegistry --> end1
```

### 3.3 Diagramme de **Processus** – *Construire l’image App* (P‑001‑B)

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%
bpmnDiagram
  startEvent(start2, "Déclenchement manuel / CI")
  task(prepareComposer, "Stage 1 : FROM composer_latest → copy /usr/bin/composer")
  task(buildApp, "Stage 2 : FROM php_7.3‑apache‑buster")
  task(installDeps, "RUN apt‑get … && docker‑php‑ext‑install pdo pdo_pgsql intl")
  task(copyConf, "COPY docker/conf/000‑default.conf → /etc/apache2/sites‑available")
  task(setupPhp, "COPY php.ini‑production → php.ini")
  task(finalize, "COPY --from=composer /usr/bin/composer /usr/bin/composer")
  endEvent(end2, "Image App prête")
  start2 --> prepareComposer --> buildApp --> installDeps --> copyConf --> setupPhp --> finalize --> end2
```

### 3.4 Diagramme de **Choreography** – *Orchestration Docker‑Compose* (optionnel)

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%
bpmnDiagram
  choreographyTask(startCompose, "docker‑compose -f docker‑compose.dev.yml up", "DevOps Engineer")
  choreographyTask(startDB, "Démarrage du service db", "PostgreSQL DB")
  choreographyTask(initDB, "Exécution initdb/*.sql", "PostgreSQL DB")
  choreographyTask(startApp, "Démarrage du service app", "PHP / Apache App")
  choreographyTask(healthCheck, "Health‑check HTTP", "DevOps Engineer")
  startCompose --> startDB --> initDB --> startApp --> healthCheck
```

### 3.5 Diagramme de **Conversation** – *Gestion des variables d’environnement* (optionnel)

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%
bpmnDiagram
  conversation(convEnv, "Gestion .env")
  participant DevOps
  participant CI
  convEnv --> DevOps: Lecture .env
  convEnv --> CI: Export variables
```

---

## 4. Règles de gestion métier

| Point de décision (Gateway) | Condition | Règle métier (RB‑xxx) | Source |
|-----------------------------|-----------|----------------------|--------|
| **GW‑DB‑TAG** (exclusive) | `branch = "main"` | **RB‑001** : Taguer l’image DB en `latest` uniquement sur la branche *main*. | Git‑flow |
| **GW‑APP‑PROXY** (exclusive) | `http_proxy` non vide | **RB‑002** : Appliquer le proxy HTTP uniquement en environnement interne. | Politique réseau |
| **GW‑COMPOSE‑ENV** (exclusive) | `ENV = "dev"` | **RB‑003** : Utiliser le fichier `docker‑compose.dev.yml` pour les environnements de développement. | Documentation CI |
| **GW‑HEALTH‑OK** (exclusive) | `GET /status` = 200 | **RB‑004** : Continuer le pipeline uniquement si le health‑check renvoie 200. | SLA interne |

---

## 5. Données et documents

### 5.1 Objets de données

| Data Object | Description | Persistance |
|-------------|-------------|--------------|
| **initdb/*.sql** | Scripts d’initialisation du schéma PostgreSQL. | **Data Store** (`/docker-entrypoint-initdb.d/`) |
| **.env** | Variables d’environnement (DB_PASSWORD, APP_ENV). | **Data Store** (fichier versionné). |
| **config_CAS.php** | Configuration du CAS (authentification unique). | **Data Object** (lu par l’app). |
| **param.ini** | Paramètres applicatifs (locale, timezone). | **Data Object**. |
| **Dockerfile‑app / Dockerfile‑db** | Définition des images. | **Data Store** (repo Git). |

### 5.2 Artifacts

| Artifact | Usage |
|----------|-------|
| **Group “Build‑Artifacts”** | Regroupe les images Docker générées. |
| **Annotation** | “Le proxy doit être désactivé en prod” (attachée à `ENV‑PROXY`). |
| **Association** | Lien entre `Dockerfile‑app` et `composer.json` (non présent mais implicite). |

---

## 6. Acteurs & Rôles

| Lane BPMN | Rôle métier | Responsabilités | Compétences |
|-----------|-------------|-----------------|--------------|
| **DevOps Engineer** | Provisionnement CI/CD | Build images, orchestrer Docker‑Compose, gérer secrets | Docker, Bash, CI (GitLab CI) |
| **DB Admin** | Gestion de la base | Rédiger scripts init, valider schéma, définir paramètres PostgreSQL | PostgreSQL, SQL, sécurité |
| **App Developer** | Développement applicatif | Ajouter dépendances Composer, mettre à jour config PHP | PHP, Composer, Apache |
| **QA Lead** | Contrôle qualité | Vérifier conformité BPMN, exécuter tests de santé | BPMN, testing, monitoring |

### 6.2 Répartition des tâches

| Tâche | Type | Responsable |
|-------|------|--------------|
| `docker build -f docker/db/Dockerfile .` | Service Task (automatisé) | DevOps |
| `docker-compose up -d` | Service Task | DevOps |
| `psql -f initdb/*.sql` | Script Task | DB Admin |
| `composer install` | Service Task | App Developer |
| `curl http://localhost/status` | Script Task (health‑check) | QA Lead |

---

## 7. Performances & Indicateurs (KPIs)

### 7.1 Métriques de processus

| Indicateur | Formule | Objectif | Seuil d’alerte |
|------------|---------|----------|----------------|
| **Temps moyen de build DB** | `Σ(build_time_DB) / nb_builds` | `< 3 min` | `> 5 min` |
| **Temps moyen de build App** | `Σ(build_time_App) / nb_builds` | `< 5 min` | `> 8 min` |
| **Taux de succès du health‑check** | `OK / (OK + KO)` | `≥ 99 %` | `< 95 %` |
| **Coût de stockage des images** | `size(image) * €/GB/mois` | `< 10 €/mois` | `> 15 €/mois` |
| **Durée de déploiement Docker‑Compose** | `end_time - start_time` | `< 30 s` | `> 45 s` |

### 7.2 Points de mesure BPMN

* **Timer Event** – `Timer (30 s)` sur le health‑check pour déclencher la **Gateway GW‑HEALTH‑OK**.  
* **Monitoring** – `Service Task “CollectMetrics”` (exemple d’extension Camunda) pour pousser les KPI vers Prometheus.

---

## 8. Gestion des exceptions

| Type d’événement | Déclencheur | Gestion (Boundary Event) | Conséquence |
|-------------------|-------------|------------------------|------------|
| **Timer** | Build > 10 min | `Boundary Timer` → `NotifyOps` (Email) | Annulation du job CI |
| **Error** | `docker‑compose up` renvoie code != 0 | `Boundary Error` → `RollbackCompose` | Nettoyage des conteneurs |
| **Escalation** | Health‑check KO 3× consécutives | `Boundary Escalation` → `Ticket JIRA` | Intervention humaine |
| **Compensation** | Déploiement partiel (DB ok, App KO) | `Boundary Compensation` → `docker‑compose down` | Retour à état précédent |

### 8.2 Scénarios d’erreur documentés

| Scénario | Déclencheur | Gestion | Conséquence |
|----------|-------------|---------|-------------|
| **Timeout DB init** | `initdb/*.sql` > 2 min | Timer → Notification → Escalade | Pipeline arrêté, DBA notifié |
| **Erreur de script Composer** | `composer install` exit 1 | Error → Clean‑up `docker rmi` | Build annulé, logs archivés |
| **Port conflict** | `docker‑compose up` port 5432 déjà utilisé | Error → Retry avec `docker‑compose -p dev2` | Nouvelle instance lancée, alerte admin |

---

## 9. Sous‑processus & Réutilisation

| Sous‑processus | ID | Description | Réutilisation |
|----------------|----|-------------|---------------|
| **SP‑DB‑Init** | `SP‑001` | Initialise le schéma PostgreSQL à partir des scripts `.sql`. | Appelé par **P‑001‑A** et **P‑001‑E** (re‑déploiement). |
| **SP‑App‑Config** | `SP‑002` | Copie les fichiers de config (`000‑default.conf`, `.env`, `param.ini`) et lance Composer. | Partagé entre **P‑001‑B** et **P‑001‑F** (mise à jour). |
| **SP‑HealthCheck** | `SP‑003` | Effectue un GET `/status` et renvoie OK/KO. | Utilisé par **P‑001‑E** et **P‑001‑D**. |
| **SP‑Rollback** | `SP‑004` | `docker-compose down -v` + suppression images temporaires. | Gestion des erreurs (P‑001‑A/B/E). |

### 9.2 Call Activities

* **Call Activity “SP‑DB‑Init”** dans **P‑001‑A**.  
* **Call Activity “SP‑App‑Config”** dans **P‑001‑B**.  
* **Call Activity “SP‑HealthCheck”** dans **P‑001‑E** (post‑déploiement).  

Paramètres d’entrée / sortie :

| Call Activity | Input | Output |
|---------------|-------|--------|
| SP‑DB‑Init | `initdb/*.sql` (list) | `DB_READY = true` |
| SP‑App‑Config | `.env`, `config_CAS.php`, `param.ini` | `APP_READY = true` |
| SP‑HealthCheck | URL (`http://localhost/status`) | `HEALTH = OK/KO` |

---

## 10. Matrice de traçabilité (Exigences ↔ BPMN)

| Exigence CCF | Processus BPMN | Tâche(s) | Scénario de test |
|--------------|----------------|----------|------------------|
| **EXG‑001** – *Provisionner un environnement dev complet* | **P‑001‑E** (Orchestration) | `docker‑compose up` (service db, service app) | **Nominal** – Build + Up + Health‑check OK |
| **EXG‑002** – *Gestion du proxy HTTP* | **P‑001‑B** (Build App) | `ENV http_proxy` (Task `installDeps`) | **Conditionnel** – Proxy présent → variable injectée |
| **EXG‑003** – *Rollback en cas d’erreur* | **P‑001‑A/B/E** | `Boundary Error` → `RollbackCompose` | **Erreur** – Simuler exit 1 sur `docker‑compose` → Vérifier nettoyage |
| **EXG‑004** – *Sécurité des secrets* | **P‑001‑C** | Lecture `.env` (Script Task) | **Sécurité** – Vérifier que le fichier n’est pas exposé dans les logs |
| **EXG‑005** – *Conformité BPMN* | **Tous** | Validation via checklist (section 11) | **Audit** – Tous les éléments BPMN présents et correctement nommés |

---

## 11. Validation & Conformité

### 11.1 Checklist BPMN (exécutée avant livraison)

- [ ] Tous les flux ont une source et une cible.  
- [ ] Une **et une seule** activité de **Start Event** par processus.  
- [ ] Au moins **une** activité de **End Event**.  
- [ ] Aucun **gateway** orphelin (tout gateway a au moins deux séquences entrantes/sortantes).  
- [ ] Labels des passerelles explicites (`GW‑DB‑TAG`, `GW‑HEALTH‑OK`).  
- [ ] Nomenclature cohérente (`P‑001‑A`, `SP‑001`).  
- [ ] Tous les **Data Objects** sont associés à leurs activités (annotation).  
- [ ] Modélisation **exécutable** (pas de symboles non‑standard).  

### 11.2 Niveaux de conformité BPMN

| Niveau | Description | Couverture |
|--------|-------------|------------|
| **Descriptive** | Diagrammes lisibles, pas d’éléments exécutables. | **P‑001‑D** (Contrôle) |
| **Analytic** | Ajout de **Data Objects**, **Annotations**, **Gateways** détaillées. | **P‑001‑A/B/E** |
| **Common Executable** | Tous les **Service Tasks**, **Script Tasks**, **Message Flows** définis → export Camunda. | **P‑001‑A/B/E** (déploiement complet) |

---

## 12. Implémentation & Exécution

### 12.1 Maturité des processus

| Niveau | Caractéristiques | BPMN applicable |
|--------|------------------|-----------------|
| 1 – **Initial** | Processus ad‑hoc, pas de documentation. | – |
| 2 – **Managé** | Documentation basique, diagrammes descriptifs. | **Descriptive** |
| 3 – **Défini** | Standardisation, réutilisation de sous‑processus. | **Analytic** |
| 4 – **Quantifié** | Mesure KPI, monitoring automatisé. | **Analytic** + **Common Executable** |
| 5 – **Optimisé** | Amélioration continue, boucle de feedback. | **Common Executable** (exécution automatisée) |

> **Agile‑env** est actuellement au **Niveau 4** (processus définis, KPI mesurés, ready for executable BPMN).

### 12.2 Intégration système

| Composant | Rôle | Interface |
|-----------|------|-----------|
| **Camunda BPM** | Moteur d’exécution BPMN | REST API pour déclencher `P‑001‑E` |
| **GitLab CI** | Orchestration du pipeline | `.gitlab-ci.yml` → `docker build`, `docker-compose up` |
| **Prometheus / Grafana** | Monitoring KPI | Exporter métriques via `camunda:metrics` |
| **Vault (HashiCorp)** | Gestion des secrets (`.env`) | API `GET /secret/agile-env` |
| **PostgreSQL** | Persistance DB | Data Store `/docker-entrypoint-initdb.d/` |
| **Apache/ PHP** | Application métier | Service `app` exposé sur `http://localhost` |

---

## 13. Annexes

### 13.1 Glossaire métier (aligné BPMN)

| Terme | Définition |
|-------|------------|
| **Build** | Construction d’une image Docker à partir d’un Dockerfile. |
| **Compose** | Orchestration multi‑conteneurs via `docker‑compose.yml`. |
| **Health‑check** | Vérification de disponibilité d’un service via requête HTTP. |
| **Rollback** | Annulation d’un déploiement et restauration de l’état précédent. |
| **Secret** | Valeur confidentielle (mot de passe DB, token) stockée hors du repo. |

### 13.2 Références normatives

1. **ISO/IEC 19510 :2013** – Business Process Model and Notation (BPMN 2.0).  
2. **OMG BPMN 2.0 Specification** – https://www.omg.org/spec/BPMN/2.0/.  
3. **Camunda BPMN Execution Model** – https://docs.camunda.org/manual/latest/reference/bpmn20/.  

---

*Ce CCF a été rédigé conformément aux exigences de la norme ISO/IEC 19510 et aux bonnes pratiques de modélisation BPMN. Les diagrammes fournis sont prêts à être importés dans un moteur BPMN (Camunda, Activiti, etc.) pour exécution ou simulation.*