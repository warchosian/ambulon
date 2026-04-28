# Cahier des Spécifications Techniques (CST) – **agile‑infra**  
**Projet** : agile‑infra  
**Chemin du dépôt** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\agile‑infra`  

> **Norme** : ISO/IEC/IEEE 29119 (séries 1‑6, 11) – version 2022/2021.  
> **Date** : 27 avril 2026  
> **Auteur** : Test Lead – Qualité & Test  

---  

## 1️⃣ Stratégie de test  *(ISO 29119‑3 – Test Strategy)*  

### 1.1 Contexte et objectifs de test  

| Élément | Description |
|---------|-------------|
| **Portée fonctionnelle** | Validation du **pipeline CI/CD** qui exécute le playbook Ansible `recette/main.yml` et déploie les conteneurs Docker via le template `docker‑compose.yml.j2`. |
| **Portée non‑fonctionnelle** | Sécurité du traitement des secrets, performance du déploiement (temps d’exécution), conformité aux bonnes pratiques d’Ansible (idempotence, atomicité). |
| **Exclusions** | Tests de charge du service applicatif tournant dans les conteneurs – hors du périmètre *infra*. |
| **Objectifs mesurables** | 1. Atteindre **≥ 95 %** de couverture de code Ansible (via `ansible‑lint` + `ansible‑test`). <br>2. Aucun défaut de **sévérité Critique** ni **Majeur** en production. <br>3. Temps moyen du job CI ≤ **6 min** (déploiement dry‑run) et ≤ **4 min** (déploiement réel). |
| **Contraintes** | Utilisation de l’image Docker `pasta‑cooker‑client:v1.0.6` dans le job CI, variables d’environnement `CD_URL`, `PROJECT`, `SECRET_KEY`, `DECRYPT_PASSWORD`. |
| **Dépendances** | - Serveur GitLab Runner disponible. <br>- Accès réseau au serveur de configuration (`ws://cooker.pnm3.r2.eco4.cloud…`). <br>- Secrets stockés dans `recette/vars/secrets.yml` (cryptés). |

### 1.2 Analyse des risques et mitigation  

| Risque | Probabilité | Impact | Stratégie de mitigation |
|--------|-------------|--------|--------------------------|
| **R1 – Fuite de secrets** (exposition du fichier `secrets.yml` dans les logs) | Moyenne | Critique | Masquage des variables `SECRET_KEY`/`DECRYPT_PASSWORD` dans le job CI, audit des logs, utilisation de `--no-log` dans Ansible. |
| **R2 – Échec du `docker compose up` (conteneurs non‑lancés)** | Haute | Majeur | Vérifier la présence du binaire Docker, ajouter un handler de vérification post‑déploiement (`docker ps`). |
| **R3 – Non‑idempotence du playbook** (exécution répétée crée des doublons) | Moyenne | Majeur | Utiliser `state: present`/`absent`, tests unitaires Ansible (`ansible-test sanity`). |
| **R4 – Déploiement hors‑temps (pipeline trop long)** | Faible | Moyen | Benchmark du job, optimisation du template Jinja, parallélisation des tâches avec `async`/`poll`. |
| **R5 – Incompatibilité de version Docker‑Compose** | Faible | Moyen | Verrouiller la version du binaire Docker‑Compose dans l’image Docker utilisée. |
| **R6 – Mauvaise configuration du chemin d’application (`app_path`)** | Moyenne | Mineur | Test de validation du chemin (`stat`) avant utilisation, test de dry‑run. |

### 1.3 Approche générale  

| Niveau de test | Types de test | Techniques appliquées |
|----------------|---------------|-----------------------|
| **Unitaire** | Tests unitaires sur les rôles/handlers Ansible (`ansible-test units`) | *White‑box* – couverture de lignes, de branches. |
| **Intégration** | Exécution du playbook sur un environnement `INT` (Docker VM) | *Black‑box* – scénario `dry‑run` + `real‑run`; *Data‑driven* – jeux de variables secrets/versions. |
| **Système** | Job CI (`.gitlab-ci.yml`) déclenché par changement dans `recette/**` | *Model‑Based* – diagramme d’état du pipeline, *Decision‑Table* pour les règles de déclenchement. |
| **Acceptation** | Validation de la stack déployée par l’équipe Ops (recette) | *Exploratoire* – check‑list de conformité (sécurité, performance). |
| **Régression** | Suite automatisée exécutée à chaque merge sur `main` | *Risk‑Based* – priorisation des tests critiques (handlers, secrets). |
| **Non‑fonctionnel** | Sécurité (OWASP), performance (temps d’exécution), fiabilité (re‑exécution) | *Boundary‑Value* (temps), *Threat‑Modeling* (secrets), *Load‑Testing* (déploiement simultané). |

---  

## 2️⃣ Plan de test  *(ISO 29119‑3 – Test Plan)*  

### 2.1 Portée détaillée  

| Fonctionnalité | Description | Inclus | Exclu | Référence CCF |
|----------------|-------------|--------|------|---------------|
| **CI pipeline** | Job `run_recette` déclenche le playbook | ✅ | – | CCF‑INF‑001 |
| **Playbook Ansible** | `recette/main.yml` – gestion du chemin, secrets, versions, template Docker‑Compose | ✅ | – | CCF‑INF‑002 |
| **Handler** | `recette/handlers/main.yml` – `docker compose up -d` | ✅ | – | CCF‑INF‑003 |
| **Template Jinja** | `docker‑compose.yml.j2` – génération du fichier `docker-compose.yml` | ✅ | – | CCF‑INF‑004 |
| **Gestion des secrets** | Chargement du fichier `vars/secrets.yml` (crypté) | ✅ | – | CCF‑SEC‑001 |
| **Dry‑run / Real‑run** | Variable `dry_run` contrôle le chemin d’installation | ✅ | – | CCF‑INF‑005 |
| **Versionning** | Variables `backVersion`, `frontVersion`, `dbVersion` | ✅ | – | CCF‑INF‑006 |
| **Environnement de test** | `DEV`, `INT`, `REC`, `PERF`, `PREPROD` (voir §10) | ✅ | – | CCF‑ENV‑001 |

### 2.2 Critères d’entrée  

| Condition | Vérification |
|-----------|--------------|
| Code source disponible dans la branche `dev` | GitLab pipeline **passed** sur `lint` |
| Playbook `recette/main.yml` **syntactiquement valide** (`ansible‑lint` OK) | Rapport `ansible‑lint` ≤ 5 warnings |
| Environnements Docker/Ansible provisionnés (`DEV`) | `docker ps` fonctionnel, `ansible --version` ≥ 2.13 |
| Secrets (`SECRET_KEY`, `DECRYPT_PASSWORD`) injectés via GitLab CI variables | Variable `masked` et `protected` |
| Jeux de données de test créés (secrets, versions) | Fichiers `secrets.yml`/`versions.yml` présents dans `recette/vars/` |

### 2.3 Critères de sortie  

| Condition | Valeur cible |
|-----------|--------------|
| **Couverture de code** (Ansible + Jinja) | ≥ 95 % (statements) |
| **Taux de défauts critiques** | 0 |
| **Taux de défauts majeurs** | ≤ 1 % du nombre total de cas exécutés |
| **Couverture des exigences** | ≥ 98 % (traçabilité CCF ↔ TC) |
| **Temps moyen du job CI** | ≤ 6 min (dry‑run) ; ≤ 4 min (real‑run) |
| **Résultat de la validation de la stack** | Tous les conteneurs `up` (`docker ps`) et services accessibles (HTTP 200) |
| **Rapport de test** | Signé par le Test Lead, stocké dans le référentiel `test‑reports/` |

### 2.4 Ressources  

| Ressource | Détails |
|-----------|---------|
| **Équipe** | Test Manager (TM), Test Analyst (TA), Test Engineer (TE), DevOps Engineer (DE), Security Analyst (SA) |
| **Environnements** | `DEV` – VM Ubuntu 22.04, Docker 23, Ansible 2.14 ; `INT` – même configuration, données de production masquées ; `REC` – réplica de prod (pré‑prod) |
| **Outils** | GitLab CI, `pasta‑cooker‑client` Docker image, Ansible‑Lint, Ansible‑Test, `pytest‑ansible`, `docker‑compose`, SonarQube (qualité code), OWASP ZAP (security), JMeter (performance), JIRA (défauts) |
| **Données de test** | Jeux de secrets (`secrets.yml`) – 3 jeux (valides, expirés, corrompus) ; versions (`versions.yml`) – 2 jeux (latest, older) |
| **Formation** | Atelier “Testing Ansible Playbooks” – 2 jours, participants : TE, DE |

### 2.5 Calendrier & jalons  

| Phase | Dates prévues | Livrables |
|-------|----------------|-----------|
| **Planification** | 01/05 – 05/05 2026 | Test Strategy, Test Plan |
| **Pré‑préparation** (environnements, jeux de données) | 06/05 – 12/05 | Environnements configurés, jeux de données |
| **Développement cas de test** | 13/05 – 19/05 | TC‑001 … TC‑050 (voir §4) |
| **Exécution tests unitaires** | 20/05 – 22/05 | Rapport unitaires |
| **Exécution tests d’intégration** | 23/05 – 27/05 | Rapport d’intégration |
| **Exécution tests système & régression** | 28/05 – 03/06 | Rapport système, suite régression |
| **Tests non‑fonctionnels (sécurité & perf.)** | 04/06 – 07/06 | Rapport sécurité, rapport perf. |
| **Clôture & livrable final** | 08/06 – 10/06 | CST complet, recommandations |

---  

## 3️⃣ Conception des tests  *(ISO 29119‑4 – Test Design)*  

### 3.1 Techniques de test fonctionnel  

| Technique | Application au projet |
|-----------|----------------------|
| **Partitionnement en classes d’équivalence** | <ul><li>**Chemin d’installation** : `real_path` (valide) vs `dry_run_path` (valide)</li><li>**Secrets** : <code>valid</code>, <code>expired</code>, <code>corrupted</code></li><li>**Versions** : `latest`, `specific` (ex: `:4.7.0`)</li></ul> |
| **Boundary Value Analysis** | Valeurs limites du chemin (`/opt/app/` vs `/opt/app-dry-run/`), taille du fichier `docker-compose.yml` (≤ 1 KB, > 1 KB). |
| **Tables de décision** | Décision `notify: up the containers` uniquement si `dry_run == false`. Table : <br>**Condition** – `dry_run` (True/False) → **Action** – `Notify Handler` (Yes/No). |
| **Tests de transition d’états** | Diagramme d’état du pipeline CI : *Idle → Triggered → Running → Success / Failure*. Tests couvrent chaque transition (ex. changement de fichier déclencheur, échec du playbook). |
| **Tests de scénarios (use‑case)** | <ul><li>**SC‑01** – Déploiement **dry‑run** (vérifier génération du fichier, pas de `docker compose up`).</li><li>**SC‑02** – Déploiement **réel** (vérifier démarrage conteneurs).</li><li>**SC‑03** – Déploiement avec **secret expiré** (échec attendu, message d’erreur). </li></ul> |

### 3.2 Techniques de test structurel  

| Technique | Objectif |
|-----------|----------|
| **Couverture d’instructions** | ≥ 95 % des tâches Ansible exécutées (via `ansible‑test coverage`). |
| **Couverture de branches** | Toutes les branches `if` (`dry_run` condition) couvertes. |
| **Couverture de conditions** | Evaluation booléenne de `dry_run` et de la présence de `secrets`. |
| **MC/DC** (si besoin) | Non requis (système non‑safety‑critical). |
| **Tests de chemins** | Calcul de la complexité cyclomatique du playbook (≈ 4) → identification de **4 chemins indépendants** (dry‑run, real‑run, secret‑valid, secret‑invalid). |

### 3.3 Tests basés sur l’expérience  

| Technique | Utilisation |
|-----------|--------------|
| **Exploratoire** | Session de 2 h par le Test Engineer sur le job CI pour identifier des cas “hors‑cahier”. |
| **Error Guessing** | Anticipation de fautes courantes : <ul><li>Variable non définie (`app_path`)</li><li>Mauvais format Jinja (`{{ variable }}` manquant)</li></ul> |
| **Check‑list défauts historiques** | Analyse des tickets JIRA des releases précédentes (ex. “docker compose up fails on missing network”). |

---  

## 4️⃣ Spécification des cas de test  *(ISO 29119‑3 – Test Case Specification)*  

> **Template standard** (obligatoire) – à réutiliser pour chaque cas.  

````markdown
**[TC‑XXX]** Titre du cas de test  
├── Identifiant : TC‑XXX  
├── Description : [Description concise]  
├── Pré‑conditions : [État requis avant exécution]  
├── Entrées : [Données d’entrée]  
├── Étapes d’exécution :  
│   1. [Action]  
│   2. [Action]  
│   …  
├── Résultat attendu : [Sortie attendue]  
├── Post‑conditions : [État après exécution]  
├── Priorité : Critical / High / Medium / Low  
├── Exigence couverte : CCF‑YYY  
└── Technique utilisée : [Partitionnement / Table de décision / …]  
````  

### 4.1 Cas de test fonctionnels (exemples)

| TC ID | Titre | Exigence | Priorité | Technique |
|-------|-------|----------|----------|-----------|
| **TC‑001** | Déploiement **dry‑run** – génération du fichier `docker-compose.yml` | CCF‑INF‑002 | High | Partitionnement (dry‑run / real‑run) |
| **TC‑002** | Déploiement **réel** – conteneurs démarrés | CCF‑INF‑003 | Critical | Table de décision |
| **TC‑003** | Chargement des **secrets** valides | CCF‑SEC‑001 | Critical | Equivalence (valid / invalid) |
| **TC‑004** | Chargement des **secrets** expirés (détection) | CCF‑SEC‑001 | High | Error guessing |
| **TC‑005** | Vérification de la **version** du backend (`backVersion`) appliquée dans le template | CCF‑INF‑006 | Medium | Boundary Value |
| **TC‑006** | Gestion d’une **erreur de syntaxe Jinja** (template invalide) | CCF‑INF‑004 | High | Exploratoire |
| **TC‑007** | Exécution du **pipeline CI** suite à un changement dans `recette/**` | CCF‑INF‑001 | Critical | State transition |
| **TC‑008** | **Rollback** – exécution du playbook avec `dry_run: true` après un déploiement réel | CCF‑INF‑005 | Medium | Scenario |
| **TC‑009** | **Idempotence** – exécution du même playbook deux fois consécutives (dry‑run) | CCF‑INF‑003 | High | Coverage (branches) |
| **TC‑010** | **Sécurité** – les variables `SECRET_KEY` et `DECRYPT_PASSWORD` ne sont pas affichées dans les logs CI | CCF‑SEC‑001 | Critical | Security checklist |

#### Exemple détaillé – TC‑001  

````markdown
**[TC‑001]** Déploiement dry‑run – génération du fichier docker‑compose.yml  
├── Identifiant : TC‑001  
├── Description : Vérifier que le playbook génère le fichier `docker-compose.yml` dans le répertoire `dry_run_path` sans lancer les conteneurs.  
├── Pré‑conditions : <ul><li>Environnement `DEV` provisionné</li><li>Variables CI définies (`CD_URL`, `PROJECT`, `SECRET_KEY`, `DECRYPT_PASSWORD`)</li><li>Fichier `recette/vars/secrets.yml` contenant des secrets valides</li></ul>  
├── Entrées : <ul><li>`dry_run: true` (défini dans le playbook)</li><li>`real_path = /opt/app/`</li><li>`dry_run_path = /opt/app-dry-run/`</li></ul>  
├── Étapes d’exécution :  
│   1. Lancer le job GitLab CI (`run_recette`).  
│   2. Le job exécute `pasta‑cooker $PLAYBOOK …`.  
│   3. Ansible crée la variable `app_path` → `/opt/app-dry-run/`.  
│   4. Tâche *upload docker compose file* rend le template `docker‑compose.yml.j2` dans `/opt/app-dry-run/docker-compose.yml`.  
│   5. Aucun handler n’est notifié (condition `dry_run` true).  
│   6. Vérifier la présence du fichier via `ls -l /opt/app-dry-run/docker-compose.yml`.  
├── Résultat attendu : <ul><li>Fichier présent, contenu conforme aux versions définies (`backVersion`, `frontVersion`, `dbVersion`).</li><li>Aucun conteneur Docker n’est créé (`docker ps` ne montre pas les services).</li></ul>  
├── Post‑conditions : <ul><li>Répertoire `/opt/app-dry-run/` contenant le fichier.</li><li>Environnement `DEV` reste inchangé.</li></ul>  
├── Priorité : High  
├── Exigence couverte : CCF‑INF‑002  
└── Technique utilisée : Partitionnement (dry‑run / real‑run)
````  

*(Les cas de test 2‑10 sont rédigés de façon analogue ; les IDs, priorités et techniques sont indiqués dans le tableau ci‑dessus.)*  

### 4.2 Cas de test non‑fonctionnels  

| TC ID | Type | Objectif | KPI | Priorité |
|-------|------|----------|-----|----------|
| **TC‑NF‑001** | **Performance** – Temps de génération du fichier (dry‑run) | ≤ 30 s | Temps moyen (s) | Medium |
| **TC‑NF‑002** | **Performance** – Temps total du job CI (real‑run) | ≤ 4 min | Durée totale (min) | Critical |
| **TC‑NF‑003** | **Sécurité** – Pas de fuite de `SECRET_KEY` dans les logs | Aucun mot‑clé visible | Nombre d’occurrences | Critical |
| **TC‑NF‑004** | **Fiabilité** – Re‑exécution du job après échec (retry) | Succès après 2 tentatives | Ratio succès/retry | High |
| **TC‑NF‑005** | **Compatibilité** – Exécution du playbook sous Ansible 2.13 et 2.14 | Pas d’erreur de compatibilité | Nombre d’erreurs | Low |
| **TC‑NF‑006** | **Usabilité** – Clarté du message d’erreur lorsqu’un secret est manquant | Message explicite “Secret not found” | Satisfaction (échelle 1‑5) | Medium |

---  

## 5️⃣ Procédures de test  *(ISO 29119‑3 – Test Procedures)*  

1. **Pré‑exécution**  
   - Clone du dépôt dans l’environnement `DEV`.  
   - Vérifier la présence des variables CI (`SECRET_KEY`, `DECRYPT_PASSWORD`).  
   - Lancer le script `scripts/setup‑dev.sh` (installe Docker, Ansible, crée les répertoires).  

2. **Configuration de l’environnement**  
   - `export ANSIBLE_CONFIG=./ansible.cfg`  
   - `ansible‑galaxy install -r requirements.yml` (si besoin).  

3. **Exécution des cas de test**  
   - Utiliser le framework `pytest‑ansible` : `pytest -v tests/functional/`.  
   - Chaque test génère un artefact JUnit XML importé dans GitLab CI.  

4. **Gestion des données de test**  
   - Jeux de secrets stockés sous `testdata/secrets/` (chiffrés).  
   - Scripts `scripts/decrypt‑secrets.sh` décryptent temporairement en RAM.  

5. **Post‑exécution**  
   - Collecter les logs du job CI (`job.log`), les artefacts Docker (`docker‑compose.yml`).  
   - Exécuter le script `scripts/cleanup.sh` (suppression des dossiers temporaires).  

6. **Reporting**  
   - Générer le rapport consolidé via `sonar-scanner` (qualité code) + `junit2html`.  
   - Archiver les rapports dans `test-reports/<date>/`.  

---  

## 6️⃣ Gestion des anomalies *(Defect Management)*  

### 6.1 Classification des défauts  

| Sévérité | Définition | Exemple |
|----------|------------|---------|
| **Critique** | Blocage total du pipeline ou fuite de secret | Job CI échoue avant toute exécution, secret affiché en clair |
| **Majeur** | Fonctionnalité majeure non‑opérante | `docker compose up` ne démarre aucun conteneur |
| **Mineur** | Fonctionnalité secondaire impactée | Chemin `dry_run_path` créé avec mauvais propriétaire |
| **Cosmétique** | Problème d’UI/UX uniquement | Message d’erreur peu lisible (typo) |

### 6.2 Cycle de vie d’un défaut  

1. **Nouveau** – Créé dans JIRA (ou Azure DevOps).  
2. **Assigné** – Attribution au développeur ou ingénieur DevOps.  
3. **En cours de correction** – Code modifié, commit lié au ticket.  
4. **À retester** – Le testeur exécute le cas de test correspondant.  
5. **Fermé** – Statut *Résolu* (ou *Rejeté* si non‑reproductible).  

### 6.3 Métriques de défauts  

| Métrique | Formule | Cible |
|----------|---------|-------|
| **Densité de défauts** | Nº défauts / KLOC (ou par 100 TC) | ≤ 0,5 |
| **Defect Escape Rate** | Défauts détectés en prod / total défauts | ≤ 5 % |
| **MTTR** (Mean Time To Repair) | Σ temps de résolution / Nº défauts | ≤ 2 jours |
| **Taux de réouverture** | Défauts réouverts / Défauts résolus | ≤ 2 % |

---  

## 7️⃣ Tests de régression *(ISO 29119‑6 – Regression Testing)*  

| Aspect | Détails |
|--------|---------|
| **Sélection** | Tous les cas **TC‑001‑TC‑010** + **TC‑NF‑001‑TC‑NF‑006** (suite de régression automatisée). |
| **Fréquence** | À chaque **merge** sur `main` (pipeline CI) et avant chaque **release** majeure. |
| **Automatisation** | Suite `tests/regression/` exécutée via `pytest‑ansible` ; déclenchée par le job `regression_test` dans `.gitlab-ci.yml`. |
| **Critères d’inclusion** | Cas critiques (déploiement réel, secrets, handler) et tout bug corrigé récemment. |
| **Critères d’exclusion** | Tests de charge (exécutés séparément) et tests d’usabilité (hors CI). |
| **Gestion des écarts** | Si un test de régression échoue, création automatique d’un ticket `DEF‑REG‑<n>` avec lien vers le commit. |

---  

## 8️⃣ Tests unitaires *(ISO 29119‑11 – Unit Testing)*  

| Unité | Outil | Objectif | Couverture cible |
|-------|-------|----------|-----------------|
| **Handler `up the containers`** | `ansible-test units` | Vérifier la commande Docker générée | 100 % |
| **Template Jinja (`docker-compose.yml.j2`)** | `jinja2‑tests` (pytest) | Rendu correct des variables `backVersion`, `frontVersion`, `dbVersion` | 100 % |
| **Fonctions custom (si présentes)** | `pytest` | Logique de calcul de `app_path` | 95 % |
| **Scripts de support (`scripts/decrypt‑secrets.sh`)** | `shunit2` | Décryptage sans fuite | 100 % |

> **Note** : Les tests unitaires sont exécutés dans le job `unit_test` avant le job `run_recette`.  

---  

## 9️⃣ Automatisation des tests  

| Aspect | Détails |
|-------|---------|
| **Outils** | GitLab CI, `pasta‑cooker‑client` (exécution playbook), `pytest‑ansible`, `ansible‑lint`, `sonar‑scanner`, `OWASP ZAP`. |
| **Framework** | **Hybrid** – scripts Bash pour le setup, **PyTest** pour l’orchestration des cas, **JUnit** pour les rapports. |
| **Intégration CI/CD** | `.gitlab-ci.yml` contient les jobs : `unit_test`, `run_recette`, `regression_test`, `security_scan`, `performance_test`. |
| **Critères d’automatisabilité** | <ul><li>Pas d’interaction humaine requise (secrets injectés via variables CI).</li><li>Résultat déterministe (idempotent).</li><li>Temps d’exécution ≤ 5 min (dry‑run).</li></ul> |
| **Gestion des artefacts** | Artefacts `docker-compose.yml`, `junit.xml`, `sonar-report` sont publiés et conservés 30 jours. |
| **Maintenance** | Mise à jour du pipeline chaque version majeure d’Ansible (notification dans le backlog). |

---  

## 🔟 Environnements de test  

| Environnement | Configuration | Données | Usage |
|----------------|---------------|---------|-------|
| **DEV** | Ubuntu 22.04, Docker 23, Ansible 2.14, 2 CPU, 4 GB RAM | Secrets fictifs (non‑sensibles) | Tests unitaires, dry‑run, développement |
| **INT** | Identique à DEV, réseau interne | Secrets réels (chiffrés) | Tests d’intégration, real‑run, validation pipeline |
| **REC** | Mirror de prod (OS, Docker version) | Données anonymisées (production‑like) | Tests d’acceptation (Ops) |
| **PERF** | VM haute performance (8 CPU, 16 GB RAM) | Volume de secrets ×10 | Tests de charge du pipeline (temps de génération) |
| **PREPROD** | Identique à REC, accès aux services externes | Données réelles (masquées) | Validation finale avant mise en prod |

---  

## 1️⃣1️⃣ Rapports et métriques  

### 11.1 Types de rapports  

| Rapport | Fréquence | Destinataires | Contenu clé |
|---------|-----------|---------------|-------------|
| **Rapport d’avancement quotidien** | Chaque jour ouvré | Test Lead, DevOps, PO | % cas exécutés, défauts critiques, blocages |
| **Rapport d’itération** | Fin de chaque sprint (2 semaines) | Équipe projet, Management | Couverture exigences, KPI, plan d’action |
| **Rapport de clôture** | Fin de projet / release | Toutes parties prenantes | Résumé global, métriques finales, leçons apprises |
| **Rapport de sécurité** | Après chaque scan ZAP | SecOps, PO | Vulnérabilités détectées, statut remediation |

### 11.2 KPIs de suivi  

| KPI | Formule | Objectif |
|-----|---------|----------|
| **Couverture exigences** | Nº exigences testées / Nº exigences totales | ≥ 98 % |
| **Couverture code** | Lines covered / Total lines (Ansible) | ≥ 95 % |
| **Taux de réussite des tests** | Nº cas passés / Nº cas exécutés | ≥ 99 % |
| **Densité de défauts** | Nº défauts / 100 TC | ≤ 0,5 |
| **Effort de test** | Jours/homme dépensés | ≤ 15 j/h pour le sprint |
| **Productivité** | Nº cas de test automatisés / jour | ≥ 8 |
| **Temps moyen de build CI** | Durée totale du job `run_recette` | ≤ 4 min (real‑run) |

---  

## 1️⃣2️⃣ Organisation et responsabilités  

| Rôle | Responsabilités | RACI (R‑A‑C‑I) |
|------|----------------|----------------|
| **Test Manager (TM)** | Définit stratégie, approuve plan, supervise métriques | **R** |
| **Test Analyst (TA)** | Rédaction cas de test, traçabilité CCF ↔ TC | **A** |
| **Test Engineer (TE)** | Exécution automatisée, reporting quotidien | **C** |
| **DevOps Engineer (DE)** | Provisionnement environnements, CI/CD | **C** |
| **Security Analyst (SA)** | Revues sécurité, scans OWASP ZAP | **I** |
| **Product Owner (PO)** | Validation des exigences, acceptation | **I** |
| **Developpeur (DEV)** | Correction défauts, support aux TE | **I** |

> **Matrice RACI détaillée** disponible en annexe `RACI.xlsx`.  

---  

## 1️⃣3️⃣ Gestion des configurations  

| Élément | Méthode |
|---------|---------|
| **Cas de test** | Versionnés via Git (`tests/`), tag `TC‑v1.0`, suivi dans JIRA (lié à CCF). |
| **Jeux de données** | Stockés sous `testdata/` avec hash SHA‑256, versionnés (Git LFS si > 100 MB). |
| **Playbooks / Templates** | Dépôt Git, version `vX.Y.Z`, changelog. |
| **Environnements** | Définis dans `infrastructure/terraform/`, versionnés, `terraform plan` enregistré. |
| **Traçabilité** | Table `TRACEABILITY.md` : CCF ↔ TC ↔ Defect ↔ Commit. |

---  

## 1️⃣4️⃣ Annexes  

| Annexe | Description |
|--------|-------------|
| **A – Table de traçabilité CCF ↔ TC** (`TRACEABILITY.md`) |
| **B – Matrice de couverture des techniques** (`TECH_COVERAGE.md`) |
| **C – Diagramme d’état du pipeline CI** (`pipeline_state.png`) |
| **D – Scripts d’automatisation** (`scripts/`) |
| **E – Modèle de rapport JUnit** (`junit_template.xml`) |
| **F – RACI.xlsx** (feuille de calcul) |

---  

### 📌 Conclusion  

Ce **Cahier des Spécifications Techniques** formalise l’ensemble du processus de test du projet **agile‑infra** conformément à la norme **ISO/IEC/IEEE 29119**. Il décrit :

* la **stratégie** alignée sur les risques,  
* le **plan** avec critères d’entrée/sortie,  
* la **conception** (techniques fonctionnelles & structurelles),  
* les **cas de test** (fonctionnels & non‑fonctionnels) avec traçabilité,  
* les **procédures**, **gestion des anomalies**, **régression**, **unitaires**,  
* l’**automatisation** intégrée au pipeline CI/CD,  
* les **environnements**, **rapports**, **KPIs**, **organisation**, et la **gestion de configuration**.  

Le respect de ce CST garantit une **qualité mesurable**, une **maîtrise des risques** et une **livraison fiable** du pipeline d’infrastructure « agile‑infra ».  

---  

*Document généré le 27 avril 2026 – Version 1.0*  