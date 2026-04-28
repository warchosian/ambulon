# 📄 Cahier des Charges Fonctionnel (CCF) – **siss‑infra**  

[TOC]

---

## 1️⃣ Introduction et contexte du projet {#intro}

### 1.1 Présentation du projet
Le projet **siss‑infra** regroupe l’ensemble des scripts d’infrastructure **Ansible** permettant de :

* Provisionner les environnements **pre‑prod**, **recette** et **prod**.  
* Gérer les secrets (via *Ansible Vault*).  
* Déployer les conteneurs Docker à l’aide de **docker‑compose**.  
* Piloter les versions applicatives et bases de données via des variables d’environnement.

### 1.2 Objectifs stratégiques
| Objectif | Description | KPI de succès |
|----------|--------------|----------------|
| **Fiabilité du déploiement** | Automatiser le lancement / arrêt des conteneurs sans intervention manuelle. | < 5 % d’échecs de déploiement en production. |
| **Traçabilité des versions** | Centraliser les versions d’application et de DB dans des fichiers YAML versionnés. | Historique complet disponible dans Git. |
| **Sécurité des secrets** | Stocker les secrets chiffrés et les injecter uniquement au moment du déploiement. | Aucun secret en clair dans le dépôt. |
| **Intégration CI/CD** | Déclencher les playbooks via le pipeline GitLab CI. | 100 % des merges déclenchent un job de déploiement. |

### 1.3 Périmètre fonctionnel
| Inclus | Exclu |
|-------|-------|
| • Playbooks Ansible (`handlers`, `vars`, `templates`).<br>• Gestion des versions (`versions.yml`).<br>• Gestion des secrets (`secrets.yml`).<br>• Scripts Docker‑Compose. | • Développement de l’application métier.<br>• Gestion du réseau sous‑jacent (firewall, load‑balancer).<br>• Monitoring/observabilité (hors scope du CCF). |

---

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) {#besoin}

| **Fonction de service (FS)** | **Description (quoi)** | **Critères d’appréciation** | **Pondération** | **Contraintes** |
|------------------------------|------------------------|------------------------------|-----------------|-----------------|
| **FS‑01** : Provisionner l’environnement | Créer le répertoire de travail (`app_path`) et préparer les variables d’environnement pour un environnement donné (preprod, recette, prod). | • Temps de provisioning ≤ 30 s.<br>• Aucun fichier temporaire en clair. | 15 % | Utiliser les chemins définis dans `vars/versions.yml`. |
| **FS‑02** : Gérer les secrets | Charger les secrets chiffrés (`secrets.yml`) via Ansible Vault et les rendre disponibles aux conteneurs. | • Secrets jamais stockés en clair sur le disque.<br>• Décryptage réussi à 100 % des runs. | 20 % | Le mot de passe du vault doit être fourni par le pipeline CI. |
| **FS‑03** : Déployer les conteneurs | Exécuter `docker compose up -d --remove-orphans` dans le répertoire de l’application. | • Tous les services sont *healthy* dans ≤ 2 min.<br>• Aucun conteneur orphelin. | 25 % | Docker‑Compose version ≥ 2.0 ; images taggées avec `appVersion`. |
| **FS‑04** : Arrêter les conteneurs (recette uniquement) | Exécuter `docker compose down` pour nettoyer l’environnement de test. | • Tous les conteneurs arrêtés et supprimés.<br>• Aucun volume persistant non‑nettoyé. | 10 % | Autorisé uniquement sur l’environnement **recette**. |
| **FS‑05** : Mettre à jour les versions | Modifier les valeurs `appVersion` et `dbVersion` dans `vars/versions.yml` et appliquer le déploiement. | • Version appliquée correctement (docker‑compose utilise le bon tag).<br>• Roll‑back possible en cas d’échec. | 15 % | La syntaxe du tag doit être `:<MAJOR>.<MINOR>.<PATCH>`. |
| **FS‑06** : Intégration CI/CD | Le pipeline GitLab déclenche les playbooks correspondants selon la branche (dev → preprod, release → prod, MR → recette). | • 100 % des pipelines terminent (succès ou échec clairement indiqué).<br>• Rapport de déploiement généré. | 15 % | Utilisation du fichier `.gitlab-ci.yml` fourni. |

> **Note** : La pondération totale = 100 %.

---

## 3️⃣ Acteurs et parties prenantes {#acteurs}

| **Acteur** | **Rôle** | **Objectifs** | **Besoins spécifiques** |
|------------|----------|---------------|--------------------------|
| **Administrateur DevOps** | MOE (Maîtrise d’Œuvre) | Garantir la disponibilité de l’infrastructure. | Accès complet aux playbooks, aux secrets, aux logs CI. |
| **Responsable MOA** | MOA (Maîtrise d’Ouvrage) | Valider que les livrables répondent aux exigences métier. | Rapports de version, traçabilité, conformité RGPD. |
| **Pipeline GitLab CI** | Système automatisé | Orchestrer le déclenchement des déploiements. | Variables d’environnement sécurisées, secrets Vault. |
| **Utilisateurs Finaux** | Consommateurs du service | Accéder à l’application déployée. | Disponibilité du service, temps de réponse. |
| **RSSI** | Sécurité de l’information | Vérifier le chiffrement des secrets et la conformité. | Aucun secret en clair, auditabilité. |

---

## 4️⃣ Cas d’usage (Use Cases) {#usecases}

### 4.1 Diagramme de cas d’utilisation (Mermaid)

```mermaid
usecaseDiagram;
    actor Administrateur DevOps as DevOps
    actor Pipeline GitLab CI as CI
    actor Responsable MOA as MOA
    actor Utilisateur Final as User

    DevOps --> (Provisionner environnement)
    DevOps --> (Gérer secrets)
    DevOps --> (Déployer conteneurs)
    DevOps --> (Arrêter conteneurs)
    DevOps --> (Mettre à jour versions)

    CI --> (Déclencher pipeline)
    CI --> (Récupérer secrets)
    CI --> (Appliquer playbook)

    MOA --> (Valider version)
    MOA --> (Consulter rapports)

    User --> (Consulter service)
```

### 4.2 Tableau des cas d’usage

| **CU** | **Nom** | **Acteur(s) principal(aux)** | **Scénario nominal** | **Scénarios alternatifs / d’erreur** | **Pré‑conditions** | **Post‑conditions** |
|--------|----------|----------------------------|----------------------|---------------------------------------|--------------------|---------------------|
| CU‑01 | Provisionner environnement | Administrateur DevOps | 1. Lancer le playbook `preprod/handlers/main.yml`.<br>2. Ansible crée le répertoire `app_path` et charge les variables.<br>3. Retour OK. | A1 – Le répertoire existe déjà → Ansible signale *already present* et continue.<br>E1 – Échec de connexion SSH → arrêt du playbook, notification CI. | L’accès SSH au serveur cible est fonctionnel. | Répertoire prêt, variables en mémoire. |
| CU‑02 | Gérer les secrets | Administrateur DevOps / CI | 1. Le playbook lit `vars/secrets.yml` (Ansible Vault).<br>2. Déchiffre les secrets avec le mot‑de‑passe fourni par le pipeline.<br>3. Injecte les variables d’environnement dans le conteneur. | A1 – Mot‑de‑passe manquant → le job CI échoue, alerte. | Le mot‑de‑passe du vault est disponible dans les variables CI. | Secrets disponibles uniquement en mémoire pendant le déploiement. |
| CU‑03 | Déployer les conteneurs | Administrateur DevOps / CI | 1. Exécution de `docker compose up -d --remove-orphans` via le handler.<br>2. Docker télécharge les images taggées `appVersion`/`dbVersion`.<br>3. Tous les services passent à l’état *healthy*. | A1 – Image introuvable → rollback à la version précédente.<br>E1 – Conteneur ne démarre pas → arrêt du job, log d’erreur. | Docker‑Compose installé, images accessibles. | Conteneurs en cours d’exécution, version conforme. |
| CU‑04 | Arrêter les conteneurs (recette) | Administrateur DevOps | 1. Exécution de `docker compose down` dans l’environnement **recette**.<br>2. Tous les services sont arrêtés et les volumes nettoyés. | A1 – Conteneur déjà arrêté → message *already stopped*.<br>E1 – Erreur de suppression de volume → log et continuation. | Environnement **recette** actif. | Aucun conteneur actif, environnement propre. |
| CU‑05 | Mettre à jour les versions | Administrateur DevOps / CI | 1. Modifier `vars/versions.yml` (ex: `appVersion: ":6.4.1"`).<br>2. Relancer le playbook de déploiement.<br>3. Docker télécharge la nouvelle image, redéploiement. | A1 – Tag non disponible → rollback et alerte.<br>E1 – Incompatibilité DB ↔ App → arrêt du pipeline. | Nouvelle version validée en pré‑prod. | Application et DB tournent sur les nouvelles versions. |
| CU‑06 | Intégration CI/CD | Pipeline GitLab CI | 1. Push sur branche `dev` → pipeline déclenche `preprod`.<br>2. Push sur `release` → pipeline déclenche `prod`.<br>3. MR → pipeline déclenche `recette`. | A1 – Variable d’environnement manquante → job échoue.<br>E1 – Timeout du job → relance manuelle. | `.gitlab-ci.yml` présent, variables CI configurées. | Rapport de déploiement généré, statut du job affiché. |

---

## 5️⃣ Processus métier (BPMN) {#processus}

### 5.1 Diagramme BPMN (Mermaid)

```mermaid
bpmnDiagram;
    participant DevOps
    participant CI as "GitLab CI"
    participant Docker as "Docker Engine"
    participant Vault as "Ansible Vault"

    startEvent(start) --> task1[Déclencher pipeline CI]
    task1 --> exclusiveGateway{Branche ?}
    exclusiveGateway -->|dev| task2[Déployer pre‑prod]
    exclusiveGateway -->|release| task3[Déployer prod]
    exclusiveGateway -->|MR| task4[Déployer recette]

    task2 --> task2a[Charger secrets (Vault)]
    task2a --> task2b[Provisionner répertoire]
    task2b --> task2c[Docker compose up]
    task2c --> endEvent(endPreprod)

    task3 --> task3a[Charger secrets (Vault)]
    task3a --> task3b[Provisionner répertoire]
    task3b --> task3c[Docker compose up]
    task3c --> endEvent(endProd)

    task4 --> task4a[Charger secrets (Vault)]
    task4a --> task4b[Provisionner répertoire]
    task4b --> task4c[Docker compose down]
    task4c --> task4d[Docker compose up]
    task4d --> endEvent(endRecette)
```

### 5.2 Points de contrôle et règles de gestion
| Point de contrôle | Règle de gestion |
|-------------------|------------------|
| **Chargement des secrets** | Le mot‑de‑passe du vault doit être fourni via la variable CI `VAULT_PASSWORD`. |
| **Versionnage** | Le tag `appVersion` doit correspondre à une image Docker existante dans le registre. |
| **Environnements** | Seul l’environnement **recette** autorise l’étape *down* avant *up*. |
| **Rollback** | En cas d’échec du déploiement, le playbook doit restaurer la version précédente et notifier le canal Slack `#infra-alerts`. |

---

## 6️⃣ Règles métier et contraintes fonctionnelles {#regles}

| **Règle** | **Formulation** |
|-----------|-----------------|
| **R‑01** | *Si* le pipeline CI est déclenché sur la branche `release`, *alors* le playbook `prod/handlers/main.yml` doit être exécuté. |
| **R‑02** | *Si* le secret `DB_PASSWORD` est absent du vault, *alors* le job CI doit échouer immédiatement. |
| **R‑03** | *Si* `appVersion` ne commence pas par `:` suivi de trois nombres séparés par des points, *alors* le commit doit être rejeté par le hook Git. |
| **R‑04** | *Si* le temps de démarrage d’un service dépasse 120 s, *alors* le job doit être marqué comme **failed** et un ticket JIRA doit être créé. |
| **R‑05** | *Si* l’environnement est `prod`, *alors* aucun conteneur ne doit être arrêté manuellement hors du playbook. |

### Contraintes
* **Réglementaires** : conformité RGPD – les données sensibles restent chiffrées en repos.  
* **Techniques** : Docker‑Compose ≥ 2.0, Ansible ≥ 2.9, GitLab Runner Docker‑executor.  
* **Performance** : le déploiement complet (provision + up) ≤ 5 min en prod.  

---

## 7️⃣ Parcours utilisateurs (User Journey) {#journey}

| **Étape** | **Action utilisateur / système** | **Point de contact** | **Critère d’acceptation (GWT)** |
|-----------|----------------------------------|----------------------|--------------------------------|
| 1. Commit code | Développeur pousse sur `dev` | GitLab | **Given** le développeur a les droits de push **When** il pousse sur `dev` **Then** le pipeline *pre‑prod* démarre. |
| 2. Pipeline CI | GitLab CI déclenche le playbook `preprod` | GitLab CI | **Given** le pipeline démarre **When** le job *load‑secrets* s’exécute **Then** les secrets sont décryptés sans erreur. |
| 3. Provision | Ansible crée le répertoire `app_path` | Serveur cible | **Given** le serveur est accessible **When** le playbook s’exécute **Then** le répertoire existe. |
| 4. Déploiement | Docker compose lance les services | Docker Engine | **Given** les images existent **When** `docker compose up` est lancé **Then** tous les containers sont *healthy* dans ≤ 120 s. |
| 5. Validation | MOA consulte le rapport de version | Dashboard interne | **Given** le déploiement est terminé **When** le MOA ouvre le rapport **Then** il voit la version `6.4.x` et le statut *OK*. |
| 6. Production | Merge sur `release` déclenche prod | GitLab CI → Prod | **Given** le MR est approuvé **When** il est mergé **Then** le pipeline *prod* déploie la même version en prod. |
| 7. Incident | Un service échoue en prod | Alerting (PagerDuty) | **Given** le service est *unhealthy* **When** le seuil de 2 min est dépassé **Then** une alerte est générée et le rollback automatique se lance. |

---

## 8️⃣ Modèle Conceptuel de Données (MCD) {#mcd}

```mermaid
classDiagram
    class Environment {
    <<enumeration>>
    name

    class ApplicationVersion {
    appVersion : string

    class DBVersion {
    dbVersion : string

    class Secret {
    key : string
    encryptedValue : string

    class DeploymentTask {
    id : UUID
    timestamp : datetime
    status : enum{SUCCESS,FAILURE}
    log : text

    Environment "1" <-- "0..*" DeploymentTask : "déploie"
    DeploymentTask "1" --> "1" ApplicationVersion : "utilise"
    DeploymentTask "1" --> "1" DBVersion : "utilise"
    DeploymentTask "1" --> "0..*" Secret : "injecte"
```

> **Note** : Aucun attribut technique (chemin serveur, IP) n’est modélisé ici ; le MCD reste purement métier.

---

## 9️⃣ Critères d'acceptation et validation {#acceptation}

| **Fonction** | **Critère d'acceptation** | **Méthode de validation** | **Responsable** | **Priorité** |
|--------------|---------------------------|---------------------------|-----------------|--------------|
| FS‑01 | Provisioning ≤ 30 s, répertoire créé | Tests automatisés (Ansible `assert`) | DevOps | **M** |
| FS‑02 | Aucun secret en clair, décryptage réussi | Scan du répertoire post‑run, `ansible-vault view` | RSSI | **M** |
| FS‑03 | Tous les services *healthy* en ≤ 2 min | `docker compose ps` + healthcheck | QA | **C** |
| FS‑04 | `docker compose down` supprime tous les conteneurs | Vérification `docker ps -a` vide | QA | **C** |
| FS‑05 | Version appliquée correspond à `versions.yml` | Comparaison du tag d’image (docker inspect) | DevOps | **M** |
| FS‑06 | Pipeline CI génère un rapport + statut | Analyse du job GitLab (`artifacts`) | MOA | **M** |

> **M** = Must, **C** = Could, **W** = Would (MoSCoW).

---

## 🔟 Annexes {#annexes}

### 10.1 Glossaire

| **Terme** | **Définition** |
|-----------|----------------|
| **Ansible Vault** | Outil d’Ansible permettant de chiffrer des fichiers de variables. |
| **Docker‑Compose** | Outil de définition et d’orchestration de services Docker à partir d’un fichier YAML. |
| **Playbook** | Ensemble de tâches Ansible décrivant une séquence d’opérations. |
| **Pipeline CI** | Chaîne d’étapes automatisées déclenchées par GitLab à chaque commit. |
| **Version tag** | Identifiant d’image Docker au format `:<MAJOR>.<MINOR>.<PATCH>`. |
| **Rollback** | Retour à la version précédente en cas d’échec du déploiement. |
| **Healthcheck** | Script ou commande permettant de vérifier la disponibilité d’un conteneur. |

### 10.2 Référentiels et normes applicables

| **Référence** | **Objet** |
|---------------|-----------|
| NF EN 16271 | Management par la valeur – Expression fonctionnelle du besoin. |
| ISO/IEC/IEEE 29148:2018 | Ingénierie des exigences. |
| ISO/IEC 19505 | UML 2.x – Modélisation. |
| ISO/IEC 19510 | BPMN – Modélisation des processus métier. |
| RGPD | Protection des données à caractère personnel. |
| RGS | Référentiel Général de Sécurité (France). |

### 10.3 Historique des versions du CCF

| **Version** | **Date** | **Auteur** | **Modifications** |
|-------------|----------|------------|------------------|
| 1.0 | 2026‑04‑28 | ChatGPT (OpenAI) | Document initial – structure complète. |
| 1.1 | – | – | À venir – intégration des retours MOA. |

---

*Fin du Cahier des Charges Fonctionnel – **siss‑infra***  

↩ Retour au **sommaire**.