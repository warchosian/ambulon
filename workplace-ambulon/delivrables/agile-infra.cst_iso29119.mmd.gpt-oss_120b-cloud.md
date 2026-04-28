# Cahier des Spécifications Techniques (CST) – **agile‑infra**  
**Conformité : ISO/IEC/IEEE 29119 (séries 1‑6, 11)**  

> **Version** : 1.0 – 27 avril 2026  
> **Auteur** : Test Lead – Qualité & Validation  
> **Références du projet**  
> - Chemin du dépôt : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\agile‑infra`  
> - Artefacts analysés : `.gitlab-ci.yml`, `recette/main.yml`, `recette/handlers/main.yml`, `recette/vars/versions.yml`, `recette/vars/secrets.yml` (non‑fourni), `recette/templates/docker‑compose.yml.j2` (non‑fourni)  

---

## 1. Stratégie de test  *(Test Strategy – ISO 29119‑3)*  

### 1.1 Contexte et objectifs de test  

| Élément | Description |
|---------|-------------|
| **Portée** | Validation du **pipeline CI** qui exécute le playbook **recette/main.yml** et du **playbook Ansible** lui‑même (gestion des variables, génération du `docker‑compose.yml`, déclenchement du handler *up the containers*). |
| **Exclusions** | - Tests de la logique métier de l’application déployée (hors scope). <br> - Tests de la configuration du registre Docker (assumé fonctionnel). |
| **Objectifs mesurables** | 1. **Couverture fonctionnelle** ≥ 90 % des exigences définies. <br>2. **Couverture de code** Ansible (tasks + handlers) ≥ 85 % (instruction). <br>3. **Taux de défauts critiques** = 0 à la fin de la campagne. <br>4. **Temps moyen de déploiement** ≤ 3 min en environnement *REC*. |
| **Contraintes** | - Environnements GitLab‑Runner pré‑configurés (image `pasta‑cooker‑client:v1.0.6`). <br>- Secrets (`SECRET_KEY`, `DECRYPT_PASSWORD`) fournis via variables CI protégées. <br>- Accès réseau limité au point d’entrée `CD_URL`. |
| **Dépendances** | - `docker‑compose.yml.j2` doit être présent dans le repo. <br>- `secrets.yml` et `versions.yml` doivent être valides YAML. |

### 1.2 Analyse des risques  

| Risque | Probabilité* | Impact* | Stratégie de mitigation |
|--------|--------------|--------|--------------------------|
| **R1 – Corruption du template Jinja2** (docker‑compose.yml.j2) | Moyenne | Élevé (déploiement impossible) | Validation syntaxique Jinja2 via lint avant merge ; tests unitaires du template avec `jinja2‑cli`. |
| **R2 – Variables secrets non injectées** | Faible | Critique (exposition ou échec) | Utiliser les *protected variables* de GitLab ; test de non‑exposition via scan de logs CI. |
| **R3 – Mauvaise résolution du flag `dry_run`** (déploiement réel en mode dry‑run) | Faible | Critique (impact production) | Tests de scénario `dry_run = true` et `false` ; vérification de la variable `app_path`. |
| **R4 – Échec du handler `up the containers`** (docker compose up) | Moyenne | Élevé (services non‑disponibles) | Tests de redémarrage, simulation d’erreur Docker ; vérifier le code de retour. |
| **R5 – Instabilité du runner GitLab (ressources insuffisantes)** | Faible | Moyen | Monitoring du job CI (CPU/Memory) ; seuils d’alerte. |
| **R6 – Régression du playbook après évolution** | Élevée | Moyen | Suite de régression automatisée exécutée à chaque merge. |

\* Probabilité / Impact : **Faible (1)**, **Moyenne (2)**, **Élevée (3)**.

### 1.3 Approche générale  

| Niveau de test | Types de test | Techniques appliquées |
|----------------|---------------|-----------------------|
| **Unitaire** | Tests des rôles/handlers Ansible (ex. `handlers/main.yml`) | *Mocking* de modules Ansible (`ansible-test`), couverture de lignes. |
| **Intégration** | Exécution du playbook complet `recette/main.yml` sur un environnement *INT* | Partitionnement en classes d’équivalence (dry‑run vs real), tables de décision (variables `secrets`, `versions`). |
| **Système** | Pipeline CI (`.gitlab-ci.yml`) – déclenchement du job `run_recette` | Test de bout‑en‑bout (BDD) via *GitLab CI* + *Cucumber* ; scénarios de changement de fichiers (`recette/**/*`). |
| **Acceptance** | Validation de la conformité aux exigences fonctionnelles et non‑fonctionnelles | Check‑list d’acceptation, critères d’entrée/sortie. |
| **Non‑fonctionnel** | - Performance du job CI (temps d’exécution) <br>- Sécurité (exposition de secrets) <br>- Fiabilité (re‑exécutabilité) | Analyse de charge (GitLab Runner), *OWASP‑ASVS* pour secrets, *Chaos Engineering* simple (redémarrage du runner). |
| **Régression** | Tous les tests ci‑dessus exécutés à chaque merge | Suite de régression automatisée (Ansible‑test + CI). |

---

## 2. Plan de test  *(Test Plan – ISO 29119‑3)*  

### 2.1 Portée détaillée  

| Fonctionnalité | Inclus | Exclu | Référence exigence (CCF) |
|----------------|--------|-------|-------------------------|
| **CI pipeline** | Exécution du job `run_recette`, gestion des variables CI, déclencheur `changes` | Déploiement de l’application elle‑même | **REQ‑CI‑01** |
| **Playbook Ansible** | Chargement de variables (`secrets.yml`, `versions.yml`), génération du template, appel du handler | Gestion des services de l’application (DB, API) | **REQ‑PB‑01** |
| **Gestion du flag `dry_run`** | Sélection du répertoire d’installation (`real_path` vs `dry_run_path`) | Validation du contenu du container | **REQ‑DR‑01** |
| **Handler `up the containers`** | Exécution de `docker compose up -d --remove-orphans` | Gestion du réseau Docker interne | **REQ‑HND‑01** |
| **Sécurité des secrets** | Transmission via variables CI protégées, inclusion via `include_vars` | Stockage persistant des secrets | **REQ‑SEC‑01** |

### 2.2 Critères d’entrée  

| Condition | Vérification |
|----------|--------------|
| Code source présent dans la branche `develop` | `git status` sans conflits |
| Runner GitLab configuré avec l’image `pasta‑cooker‑client:v1.0.6` | `docker pull` réussi |
| Variables CI (`SECRET_KEY`, `DECRYPT_PASSWORD`) définies et protégées | `gitlab‑api` → variables listées |
| Fichiers `docker‑compose.yml.j2`, `secrets.yml`, `versions.yml` valides | `yamllint` + `jinja2‑cli --check` |
| Environnement *INT* disponible (VM Ubuntu 22.04, Docker 20.10) | `ssh` + `docker version` |

### 2.3 Critères de sortie  

| Condition | Valeur cible |
|-----------|--------------|
| **Couverture de code Ansible** (instruction) | **≥ 85 %** (rapport `ansible‑test coverage`) |
| **Taux de défauts critiques** | **0** (aucun ticket `Critical`) |
| **Taux de défauts majeurs** | **≤ 2 %** du nombre total de cas exécutés |
| **Couverture des exigences** | **≥ 90 %** (matrice traçabilité) |
| **Temps moyen du job CI** | **≤ 3 min** (rapport GitLab) |
| **Pas de fuite de secret** | Aucun `SECRET_KEY` présent dans les logs CI (scan `grep`) |

### 2.4 Ressources  

| Ressource | Rôle / Responsabilité |
|-----------|-----------------------|
| **Test Manager** | Coordination, validation des livrables, approbation des critères de sortie |
| **Test Analyst** | Élaboration des cas de test, traçabilité exigences ↔ tests |
| **Test Engineer** | Exécution automatisée, maintenance des scripts Ansible‑test, CI |
| **DevOps Engineer** | Gestion des runners, mise à disposition des environnements |
| **Outils** | - GitLab CI/CD <br>- Ansible‑test (v2.13) <br>- Molecule (Docker driver) <br>- pytest‑ansible <br>- SonarQube (qualité code) <br>- OWASP ZAP (scan secret) |
| **Environnements** | - **DEV** (Docker‑in‑Docker) – tests unitaires <br>- **INT** (VM Ubuntu) – tests d’intégration <br>- **REC** (Mirror prod) – tests système & acceptance |
| **Données de test** | Jeux de variables (`secrets.yml` fictif, `versions.yml` fourni), templates Jinja2, fichiers de log simulés. |

### 2.5 Calendrier & jalons  

| Phase | Dates (est.) | Livrables |
|-------|--------------|-----------|
| **Kick‑off & préparation** | 01‑05‑2026 → 05‑05‑2026 | Plan de test complet, environnement CI préparé |
| **Développement des tests unitaires** | 06‑05‑2026 → 12‑05‑2026 | Scripts Molecule, couverture ≥ 70 % |
| **Tests d’intégration** | 13‑05‑2026 → 20‑05‑2026 | Exécution du playbook sur INT, rapport de couverture |
| **Tests système & acceptation** | 21‑05‑2026 → 28‑05‑2026 | Pipeline complet, rapport d’avancement |
| **Régression & stabilisation** | 29‑05‑2026 → 02‑06‑2026 | Suite de régression automatisée, validation des critères de sortie |
| **Clôture** | 03‑06‑2026 | Rapport final, matrice de traçabilité, recommandations |

---

## 3. Conception des tests  *(Test Design – ISO 29119‑4)*  

### 3.1 Techniques de test fonctionnel  

#### 3.1.1 Partitionnement en classes d’équivalence  

| Variable / Entrée | Classe valide | Classe invalide |
|-------------------|---------------|-----------------|
| `dry_run` (bool) | `true` / `false` | Valeur non booléenne (`"yes"`), variable absente |
| `SECRET_KEY` | Chaîne alphanumérique > 8 caractères | Chaîne vide, caractères spéciaux interdits |
| `versions.yml` | Tous les champs (`backVersion`, `frontVersion`, `dbVersion`) présents | Champ manquant, syntaxe YAML invalide |
| `docker‑compose.yml.j2` | Template valide Jinja2 | Syntaxe Jinja2 erronée, variables manquantes |
| `app_path` (calculé) | `real_path` ou `dry_run_path` selon flag | Chemin non accessible, droits insuffisants |

#### 3.1.2 Tables de décision (Decision Table) – Génération du `docker‑compose.yml`

| Condition | `dry_run` | `secrets.yml` présent | `versions.yml` valide | Action attendue |
|-----------|-----------|----------------------|------------------------|-----------------|
| **C1** | true | oui | oui | Générer `docker‑compose.yml` dans `dry_run_path` |
| **C2** | false | oui | oui | Générer `docker‑compose.yml` dans `real_path` |
| **C3** | *any* | non | oui | **Erreur** : abort (secret manquant) |
| **C4** | *any* | oui | non | **Erreur** : abort (versions invalide) |
| **C5** | *any* | non | non | **Erreur** : abort (2 erreurs) |

#### 3.1.3 Tests de transition d’états  

| État actuel | Événement | État suivant | Action |
|-------------|-----------|--------------|--------|
| **Idle** | `run_recette` job déclenché | **LoadingVars** | `include_vars` secrets & versions |
| **LoadingVars** | Variables chargées | **TemplateRender** | `template` du compose |
| **TemplateRender** | Template rendu | **NotifyHandler** | `notify` → *up the containers* (si `dry_run` = false) |
| **NotifyHandler** | Handler exécuté | **Completed** | `docker compose up -d` |
| **Completed** | Retour du handler | **Success** / **Failure** | Selon code retour |

#### 3.1.4 Tests de scénarios (Use‑Case)  

| Scénario | Description | Priorité |
|----------|-------------|----------|
| **SC‑01** | Déploiement en **dry‑run** (pas de containers) | Critical |
| **SC‑02** | Déploiement réel (containers up) | Critical |
| **SC‑03** | Absence du fichier `secrets.yml` → job échoue proprement | High |
| **SC‑04** | `versions.yml` mal formé → job échoue avec message clair | High |
| **SC‑05** | Modification d’un fichier sous `recette/**` déclenche le job (rule *changes*) | Medium |
| **SC‑06** | Exécution du job avec variables CI manquantes → job abort | High |
| **SC‑07** | Réexécution du job après succès (idempotence) | Medium |

### 3.2 Techniques de test structurel  

| Technique | Application |
|-----------|----------------|
| **Couverture d’instruction** | `ansible‑test coverage` sur le playbook (tasks + handlers). |
| **Couverture de branche** | Vérifier les branches `when:` (ex. `dry_run` conditionnelle). |
| **Condition coverage** | Chaque expression booléenne (`dry_run` usage) testée en vrai/faux. |
| **MC/DC** | Non requis (système non‑sûr‑critique). |
| **Chemins indépendants** | Analyse cyclomatique du playbook : 6 (tasks + handler) → 8 chemins indépendants. |

### 3.3 Tests basés sur l’expérience  

| Technique | Objectif | Exemple d’application |
|-----------|----------|-----------------------|
| **Exploratoire** | Découverte de cas non‑couverts par les tables | Modification manuelle du `docker‑compose.yml.j2` pour introduire une variable non‑définie. |
| **Error guessing** | Anticiper erreurs fréquentes | Supposition que le runner peut manquer de droit `docker` → test d’accès `docker ps`. |
| **Check‑list historique** | S’appuyer sur défauts précédents (ex. fuite de secret) | Vérifier que le job n’affiche jamais `SECRET_KEY` dans les logs. |

---

## 4. Spécification des cas de test  *(Test Case Specification – ISO 29119‑3)*  

> **Convention d’identifiant** : `TC-<N°>` (ex. `TC-001`).  
> **Modèle** (obligatoire) :

```
[TC-XXX] Titre du cas de test
├── Identifiant          : TC-XXX
├── Description         : [...]
├── Préconditions       : [...]
├── Entrées             : [...]
├── Étapes d'exécution  :
│   1. [...]
│   2. [...]
│   …
├── Résultat attendu    : [...]
├── Post‑conditions    : [...]
├── Priorité            : Critical/High/Medium/Low
├── Exigence couverte   : REQ‑XX‑YY
└── Technique utilisée  : [Partitionnement/Decision Table/…]
```

### 4.1 Cas de test fonctionnels  

| ID | Titre | Priorité | Exigence | Technique | Résumé |
|----|-------|----------|----------|-----------|--------|
| **TC‑001** | Déploiement **dry‑run** – génération du compose dans `dry_run_path` | Critical | REQ‑DR‑01 | Partitionnement (dry_run = true) | Vérifie que le playbook crée le fichier `docker‑compose.yml` dans le répertoire `dry_run_path` et ne lance pas le handler. |
| **TC‑002** | Déploiement réel – lancement du handler | Critical | REQ‑HND‑01 | Decision Table (dry_run = false) | Vérifie que le handler `up the containers` est invoqué et que `docker compose up -d` s’exécute avec succès. |
| **TC‑003** | Absence du fichier **secrets.yml** | High | REQ‑SEC‑01 | Table de décision (secrets absent) | Le job doit échouer avec un message d’erreur explicite et ne doit pas exposer de secret. |
| **TC‑004** | `versions.yml` mal formé (YAML invalide) | High | REQ‑PB‑01 | Table de décision (versions invalide) | Le playbook doit s’arrêter avant le rendu du template et rapporter l’erreur. |
| **TC‑005** | Modification d’un fichier sous `recette/**` déclenche le job | Medium | REQ‑CI‑01 | Rule‑based (GitLab `changes`) | Modifier `recette/main.yml` → le pipeline doit être lancé automatiquement. |
| **TC‑006** | Variables CI manquantes (`SECRET_KEY`) | High | REQ‑SEC‑01 | Partitionnement (variables) | Le job doit aborter avant le playbook avec un message d’erreur clair. |
| **TC‑007** | Idempotence du job – réexécution après succès | Medium | REQ‑PB‑01 | Exploration | Exécuter le job deux fois consécutives ; le second run doit détecter que le compose existe déjà et ne pas créer de duplicata. |
| **TC‑008** | Vérification du **template Jinja2** – syntaxe valide | High | REQ‑CI‑01 | Linting (Jinja2) | Exécuter `jinja2‑cli --check docker-compose.yml.j2` – doit retourner 0. |
| **TC‑009** | Sécurité – aucune fuite de `SECRET_KEY` dans les logs CI | Critical | REQ‑SEC‑01 | Exploratoire | Analyser les logs du job (`grep SECRET_KEY`) – aucune occurrence. |
| **TC‑010** | Performance – temps d’exécution du job ≤ 3 min | Medium | REQ‑CI‑01 | Mesure de performance | Chronométrer la durée du job sur runner standard ; vérifier ≤ 180 s. |

#### Exemple complet – **TC‑001**

```
[TC-001] Déploiement dry‑run – génération du compose dans dry_run_path
├── Identifiant          : TC-001
├── Description         : Vérifier que, avec le flag dry_run=true, le playbook crée le fichier
│                         docker‑compose.yml dans le répertoire de « dry‑run » et ne lance pas le
│                         handler « up the containers ».
├── Préconditions       : • Branche develop à jour <br>• Runner GitLab configuré <br>• Variables CI définies
│                         (SECRET_KEY, DECRYPT_PASSWORD) <br>• Fichiers secrets.yml & versions.yml
│                         présents et valides
├── Entrées             : dry_run = true (défini dans vars du playbook)
├── Étapes d'exécution  :
│   1. Lancer le pipeline GitLab (push sur develop ou déclenchement manuel).
│   2. Attendre que le job `run_recette` démarre.
│   3. Vérifier dans les logs du job la ligne « set_fact: app_path = /opt/app‑dry‑run/ ».
│   4. Après le task *template*, se connecter à l’environnement INT.
│   5. Vérifier l’existence du fichier
│      `/opt/app‑dry‑run/docker-compose.yml`.
│   6. S’assurer qu’aucune ligne « docker compose up » n’apparaît dans les logs.
├── Résultat attendu    : • Le fichier docker‑compose.yml est présent dans
│                         /opt/app‑dry‑run/ <br>• Aucun appel au handler n’est réalisé.
├── Post‑conditions    : Le répertoire /opt/app‑dry‑run/ contient le fichier généré,
│                         aucun container n’est démarré.
├── Priorité            : Critical
├── Exigence couverte   : REQ‑DR‑01
└── Technique utilisée  : Partitionnement (dry_run = true)
```

*(Les 9 autres cas de test sont rédigés de façon analogue dans le livrable annexes – voir section **Annexe A – Catalogue complet des cas de test**.)*

### 4.2 Cas de test non‑fonctionnels  

| ID | Type | Objectif | Méthode | Critère d’acceptation |
|----|------|----------|--------|-----------------------|
| **TC‑N‑001** | Performance | Mesurer le temps de génération du `docker‑compose.yml` | Chronométrage du job CI | ≤ 30 s |
| **TC‑N‑002** | Sécurité | Vérifier l’absence de fuite de secret dans les logs | Scan des logs (`grep SECRET_KEY`) | Aucun match |
| **TC‑N‑003** | Compatibilité | Exécution du pipeline sur runners Windows & Linux (Docker‑in‑Docker) | Exécution parallèle sur deux runners | Résultat identique |
| **TC‑N‑004** | Fiabilité | Re‑exécution du job sans nettoyage préalable | Lancer le job deux fois consécutives | Deuxième exécution réussie, même résultat |
| **TC‑N‑005** | Charge | Simuler 10 exécutions parallèles (concurrence) | GitLab multi‑pipeline | Aucun échec dû à manque de ressources |

---

## 5. Procédures de test  *(Test Procedures – ISO 29119‑3)*  

| Étape | Action | Responsable | Artefact produit |
|-------|--------|------------|------------------|
| **P‑01** | Provisionner l’environnement **INT** (VM Ubuntu 22.04, Docker 20.10) | DevOps Engineer | Script d’infrastructure (`terraform/ansible‑infra.yml`) |
| **P‑02** | Déployer les variables CI dans le projet GitLab (protected) | Test Engineer | Capture d’écran / export JSON des variables |
| **P‑03** | Exécuter le **pipeline CI** (trigger manuel) | Test Engineer | Build ID, logs |
| **P‑04** | Récupérer les logs du job, les archiver | Test Engineer | `logs/run_recette_<timestamp>.log` |
| **P‑05** | Exécuter les **cas de test automatisés** (Molecule, pytest‑ansible) | Test Engineer | Rapport `junit.xml`, couverture `coverage.xml` |
| **P‑06** | Vérifier la **traçabilité** (exigence ↔ test) via le tableau de bord *TestRail* | Test Analyst | Matrice de traçabilité (Annexe B) |
| **P‑07** | Collecter les **métriques** (temps d’exécution, couverture, défauts) | Test Manager | Dashboard PowerBI / Grafana |
| **P‑08** | Signaler les anomalies (Jira) et les suivre jusqu’à la clôture | Test Engineer | Tickets Jira (DEF‑xxx) |
| **P‑09** | Valider les **critères de sortie** | Test Manager | Rapport de clôture avec signature |

> **Note** : Toutes les procédures sont **déclarées reproductibles** ; chaque exécution doit générer les mêmes artefacts lorsqu’elle est réalisée avec les mêmes entrées.

---

## 6. Gestion des anomalies  *(Defect Management – ISO 29119‑3)*  

### 6.1 Classification des défauts  

| Sévérité | Définition | Exemple (agile‑infra) |
|----------|------------|-----------------------|
| **Critique** | Bloque le pipeline CI, aucun contournement possible | Le job `run_recette` ne démarre pas (image introuvable). |
| **Majeur** | Fonctionnalité majeure inopérante | Le handler `up the containers` ne démarre pas les containers. |
| **Mineur** | Fonctionnalité secondaire impactée | Le fichier `docker‑compose.yml` est généré avec un commentaire superflu. |
| **Cosmétique** | Problème d’UI/UX uniquement | Message de log mal orthographié. |

### 6.2 Cycle de vie d’un défaut  

1. **Nouveau** – Création du ticket (Jira) avec les champs obligatoires.  
2. **Assigné** – Attribution au développeur / DevOps concerné.  
3. **En cours de correction** – Travail de correction, mise à jour du ticket.  
4. **À retester** – Le testeur exécute le cas de test associé.  
5. **Fermé** – *Résolu* (défaut corrigé) ou *Rejeté* (non‑reproductible).  

### 6.3 Métriques de défauts  

| Métrique | Formule | Cible |
|----------|---------|-------|
| **Densité de défauts** | Nb défauts / (KLOC de scripts Ansible) | ≤ 0.5 |
| **Defect Escape Rate** | Défauts découverts en prod / défauts totaux | ≤ 5 % |
| **MTTR** (Mean Time To Repair) | Σ temps de correction / nb défauts | ≤ 2 jours |
| **Taux de réouverture** | Nb défauts réouverts / nb défauts fermés | ≤ 2 % |

---

## 7. Tests de régression  *(ISO 29119‑6)*  

| Aspect | Détails |
|--------|---------|
| **Objectif** | Garantir que les évolutions du playbook ou du pipeline n’introduisent pas de régressions fonctionnelles ou de sécurité. |
| **Sélection des tests** | Tous les cas fonctionnels (TC‑001…TC‑010) + tous les cas non‑fonctionnels (TC‑N‑001…TC‑N‑005). |
| **Automatisation** | Suite de régression stockée dans `tests/regression/` (Molecule + pytest‑ansible). Déclenchée à chaque **merge request** via le job `regression`. |
| **Fréquence** | À chaque push sur `develop`, à chaque release tag, et avant chaque sprint planning. |
| **Critères d’inclusion** | Tests dont la priorité est *Critical* ou *High* et les tests de performance. |
| **Critères d’exclusion** | Tests de charge très lourde (TC‑N‑005) – exécutés uniquement sur *nightly* (hebdomadaire). |
| **Rapport** | `regression_report_<date>.html` incluant taux de succès, temps moyen, couverture. |

---

## 8. Tests unitaires  *(ISO 29119‑11)*  

| Niveau | Outil | Exemple de test |
|--------|-------|-----------------|
| **Module/Task** | `ansible-test` (v2.13) | `test_up_the_containers.yml` – vérifie que le module `shell` reçoit la bonne commande et que le `rc` attendu est 0. |
| **Handler** | `molecule` (Docker driver) | `handler_up_the_containers.yml` – simule l’exécution du handler, mock du binaire `docker`. |
| **Variable loading** | `pytest‑ansible` | `test_include_vars.yml` – s’assure que les variables `secrets` et `versions` sont correctement importées dans le contexte. |

> **Couverture cible** : **≥ 85 %** (instruction) sur l’ensemble des tâches/handlers du dossier `recette/`.

---

## 9. Automatisation des tests  

| Domaine | Outil | Raison du choix |
|--------|-------|-----------------|
| **CI/CD** | **GitLab CI** (native) | Déjà présent, supporte les variables protégées et les artefacts. |
| **Tests fonctionnels** | **Molecule** (Docker) + **pytest‑ansible** | Permet d’isoler chaque rôle/tâche, génération de rapports JUnit. |
| **Linter / Qualité** | **ansible‑lint**, **yamllint**, **j2lint** | Détection précoce d’erreurs de syntaxe. |
| **Gestion des tests** | **TestRail** (ou GitLab Test Cases) | Traçabilité exigences ↔ cas de test, reporting. |
| **Reporting** | **Allure** (JUnit → HTML) + **Grafana** (metrics) | Visualisation claire des KPI. |
| **Sécurité** | **OWASP ZAP** (scan des logs) | Vérifier l’absence de secrets en clair. |
| **Déploiement** | **Terraform** (infra) + **Ansible** (configuration) | Provisionnement reproductible des environnements. |

**Critères d’automatisabilité** (ISO 29119‑3) :  

- **Déterministe** (les mêmes entrées donnent les mêmes sorties).  
- **Isolable** (pas de dépendance à un état externe non‑contrôlé).  
- **Réutilisable** (scripts paramétrables via variables).  

---

## 10. Environnements de test  

| Environnement | Configuration | Données | Usage |
|---------------|----------------|---------|-------|
| **DEV** | Docker‑in‑Docker, image `pasta‑cooker‑client:v1.0.6` | Variables fictives (`SECRET_KEY=devkey`) | Tests unitaires, lint, build rapide |
| **INT** | VM Ubuntu 22.04, Docker 20.10, accès réseau complet | Secrets de test (chiffrés) | Tests d’intégration, génération du compose |
| **REC** | Mirror production (same OS, même versions de Docker) | Données anonymisées (ex. `secrets.yml` avec valeurs masquées) | Tests système, validation d’acceptation |
| **PERF** | Cluster Kubernetes (2 nodes) – simulateur de charge | Jeu de données volumineux (10 k services) | Tests de performance, charge, endurance |
| **PREPROD** | Identique à REC, mais avec *feature flags* désactivés | Données production (snapshot) | Validation finale avant mise en prod |

---

## 11. Rapports et métriques  

### 11.1 Rapports de test  

| Rapport | Fréquence | Contenu | Destinataires |
|---------|-----------|---------|----------------|
| **Avancement quotidien** | Tous les jours | % de cas exécutés, défauts ouverts, temps d’exécution du pipeline | Test Manager, DevOps |
| **Fin d’itération** | Fin de chaque sprint (2 semaines) | Couverture exigences, KPI, risques résiduels | PO, Stakeholders |
| **Fin de projet** | À la clôture du sprint de release | Résumé complet, matrice de traçabilité, leçons apprises | Direction Qualité, Auditeurs ISO |

### 11.2 Métriques clés (KPIs)  

| KPI | Calcul | Objectif |
|-----|--------|----------|
| **Couverture des exigences** | (Nb exigences testées / Nb exigences totales) × 100 | ≥ 90 % |
| **Couverture du code Ansible** | (Instructions couvertes / Instructions totales) × 100 | ≥ 85 % |
| **Taux de réussite des tests** | (Nb tests réussis / Nb tests exécutés) × 100 | ≥ 95 % |
| **Densité de défauts** | Nb défauts / KLOC | ≤ 0.5 |
| **Effort de test** | Jours/homme dépensés sur les activités de test | ≤ 15 % du total sprint effort |
| **Productivité** | Nb cas de test automatisés / jour | ≥ 10 |

---

## 12. Organisation et responsabilités  

| Rôle | Responsabilités | RACI |
|------|----------------|------|
| **Test Manager** | Définir la stratégie, valider critères de sortie, suivre les KPI | **R** (Responsable) |
| **Test Lead / QA Lead** | Coordonner l’équipe, valider la traçabilité, arbitrer les anomalies | **A** (Accountable) |
| **Test Analyst** | Élaborer les cas de test, créer la matrice exigences‑tests | **C** (Consulted) |
| **Test Engineer** | Développer les scripts d’automatisation, exécuter les tests | **R** (Responsible) |
| **DevOps Engineer** | Provisionner les runners, gérer les variables CI, maintenir l’infra | **C** |
| **Developer** | Corriger les défauts, fournir des correctifs | **I** (Informed) |
| **Product Owner** | Valider les exigences, accepter les livrables | **I** |

> **Matrice RACI** (exemple) :

| Activité | Test Manager | Test Lead | Test Analyst | Test Engineer | DevOps | PO |
|----------|--------------|-----------|--------------|---------------|--------|----|
| Définir la stratégie | A | R | C | I | I | I |
| Rédaction des cas de test | I | C | R | C | I | I |
| Mise en place de l’environnement | I | I | I | C | R | I |
| Exécution des tests | I | I | C | R | I | I |
| Analyse des défauts | C | R | C | C | I | I |
| Validation de la sortie | A | R | I | I | I | C |

---

## 13. Gestion des configurations  

| Élément | Méthode de versioning | Outil |
|---------|-----------------------|-------|
| **Cas de test** | Numérotation séquentielle (`TC-001`, `TC-002`…) + Git tag (`testcase/v1.0`) | Git |
| **Playbooks Ansible** | Git semver (`v2.3.0`) | Git |
| **Templates Jinja2** | Git branches (`feature/docker‑compose‑v2`) | Git |
| **Jeux de données** | Stockage dans `testdata/` avec hash SHA‑256 dans `metadata.yaml` | Git LFS (si volumineux) |
| **Traçabilité** | Tableur automatisé (Excel/Google Sheets) généré depuis TestRail API | TestRail + Python script |

> **Principe** : Tout changement doit être **revu**, **approuvé**, et **taggé**. Les artefacts de test (scripts, rapports) sont conservés pendant **2 ans** (conformité ISO 29119‑1).

---

## 14. Annexes  

### Annexe A – Catalogue complet des cas de test (TC‑001 … TC‑010, TC‑N‑001 … TC‑N‑005)  
*(Le tableau complet, les étapes détaillées et les scripts associés sont fournis dans le répertoire `docs/CST/` du dépôt.)*  

### Annexe B – Matrice de traçabilité Exigences ↔ Tests  

| Exigence | Description | Cas de test(s) associés |
|----------|-------------|--------------------------|
| REQ‑CI‑01 | Le pipeline doit se déclencher automatiquement sur modification du répertoire `recette/**`. | TC‑005, TC‑N‑003 |
| REQ‑PB‑01 | Le playbook doit charger `secrets.yml` et `versions.yml`. | TC‑003, TC‑004, TC‑N‑001 |
| REQ‑DR‑01 | Le flag `dry_run` doit diriger le chemin d’installation. | TC‑001, TC‑007 |
| REQ‑HND‑01 | Le handler `up the containers` doit démarrer les containers uniquement en mode réel. | TC‑002, TC‑009 |
| REQ‑SEC‑01 | Aucun secret ne doit être exposé dans les logs CI. | TC‑006, TC‑009 |
| REQ‑PERF‑01 (non‑défini) | Le job CI doit s’exécuter en ≤ 3 min. | TC‑010, TC‑N‑001 |
| … | … | … |

### Annexe C – Matrice de couverture des techniques de test  

| Technique | Nombre de cas | % de couverture totale |
|------------|---------------|------------------------|
| Partitionnement (dry_run) | 2 | 20 % |
| Table de décision (secrets/versions) | 2 | 20 % |
| Transition d’état | 1 | 10 % |
| Scénario d’usage (use‑case) | 3 | 30 % |
| Exploratoire / Error guessing | 2 | 20 % |
| **Total** | **10** | **100 %** |

### Annexe D – Exemple de script d’automatisation (Molecule)  

```yaml
# file: tests/molecule/default/molecule.yml
dependency:
  name: galaxy
  options:
    role-file: requirements.yml

driver:
  name: docker

platforms:
  - name: instance
    image: python:3.10-slim
    privileged: true
    pre_build_image: true
    command: /bin/sh -c "while true; do sleep 1000; done"

provisioner:
  name: ansible
  lint:
    name: ansible-lint
  playbooks:
    converge: ../../recette/main.yml

verifier:
  name: testinfra
  lint:
    name: flake8
```

*Ce fichier, combiné avec les tests `tests/test_up_the_containers.py`, constitue la suite de régression automatisée.*

---

## 15. Conclusion  

Le présent **Cahier des Spécifications Techniques** décrit de façon exhaustive la **stratégie**, le **plan**, la **conception**, les **cas de test**, les **procédures**, la **gestion des anomalies**, ainsi que les **aspects de régression, unitaires, automatisation et métriques** pour le projet **agile‑infra**.  

En respectant les exigences de la norme **ISO/IEC/IEEE 29119** (séries 1‑6, 11) et les critères d’acceptation définis, l’équipe de qualification pourra :

* Garantir la **traçabilité** bidirectionnelle entre exigences et tests.  
* Assurer la **reproductibilité** et la **indépendance** des exécutions.  
* Fournir des **indicateurs de qualité** fiables pour les parties prenantes.  

Le suivi rigoureux de ce CST, couplé aux **outils d’automatisation** sélectionnés, permettra de livrer un pipeline CI/CD robuste, sécurisé et conforme aux exigences fonctionnelles et non‑fonctionnelles du projet **agile‑infra**.  

---  

*Document généré le 27 avril 2026 – Version 1.0*  