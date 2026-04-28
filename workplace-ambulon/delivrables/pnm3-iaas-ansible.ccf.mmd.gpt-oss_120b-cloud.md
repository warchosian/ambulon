# 📄 Cahier des Charges Fonctionnel (CCF) – **pnm3‑iaas‑ansible**  

[TOC]

---  

## 1. Introduction et contexte du projet  <a id="intro"></a>

| Élément | Description |
|---|---|
| **Nom du projet** | *pnm3‑iaas‑ansible* – Automatisation de la mise en place et de la gestion d’une infrastructure IaaS (Docker, Nginx, métriques, Portainer Edge) via Ansible. |
| **Contexte organisationnel** | Le projet est hébergé dans le GitLab interne du ministère : `gitlab‑forge.din.developpement‑durable.gouv.fr/snum/pnm3/gti/pnm3‑iaas‑ansible`. Il s’inscrit dans la démarche « Infrastructure as Code » du service GTI (Gestion des Technologies d’Information). |
| **Objectifs stratégiques** | 1. Garantir la **reproductibilité** et la **traçabilité** du déploiement d’environnements serveur. <br>2. Centraliser la **configuration** (proxy, variables, credentials) afin d’assurer la **conformité** aux exigences de sécurité (RGPD, RGS). <br>3. Faciliter la **collecte de métriques** et la **surveillance** (Prometheus/Loki). <br>4. Permettre le **déploiement d’un agent Portainer Edge** pour la gestion des conteneurs à distance. |
| **Périmètre fonctionnel** | **Inclus** : <br>• Provisionnement des utilitaires communs (Docker, Nginx, Python, packages). <br>• Gestion des faits d’inventaire (scripts `id.fact`). <br>• Déploiement du stack **metrics** (cibles Prometheus, Loki). <br>• Déploiement de l’**agent Portainer Edge**. <br>• Gestion des clés SSH et des credentials. <br>• Gestion du proxy HTTP/HTTPS. <br>**Exclus** : <br>• Gestion du matériel (hyperviseur, réseau physique). <br>• Déploiement d’applications métiers hors métriques. |
| **Livrables attendus** | • Playbooks Ansible opérationnels (déjà fournis). <br>• Documentation fonctionnelle (présentée ici). <br>• Jeux de tests d’acceptation (critères, scripts). <br>• Diagrammes d’architecture fonctionnelle (UML, BPMN, Mermaid). |

↩︎ [Retour au sommaire](#toc)

---  

## 2. Expression fonctionnelle du besoin (NF EN 16271)  <a id="besoin"></a>

Le besoin est découpé en **fonctions de service** (FS). Chaque fonction décrit **le quoi** (exigence) sans préciser le comment.  

| # | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Niveau d’importance / Pondération* | Contraintes associées |
|---|---|---|---|---|---|
| **FS‑01** | **Gestion des hôtes cibles** | Identifier, authentifier et préparer les serveurs destinés au déploiement. | • Tous les hôtes listés dans `inventory.ini` sont accessibles (ping ≤ 100 ms). <br>• Le compte `admingti` possède les droits sudo sans mot‑de‑passe. | **Haut** (30 %) | Proxy HTTP obligatoire pour les accès sortants. |
| **FS‑02** | **Provisionnement des utilitaires communs** | Installer Docker, Nginx, Python 3, Pip, paquets système, et configurer le proxy Docker. | • Docker ≥ 20.10 installé et le service `docker` démarre. <br>• Nginx ≥ 1.18 installé et écoute sur le port 80. <br>• Python 3 ≥ 3.9 et pip ≥ 21.0 présents. <br>• Fichier `/etc/docker/daemon.json` inclut les variables proxy. | **Haut** (25 %) | Doit être **idempotent** – exécution multiple sans changement. |
| **FS‑03** | **Gestion des faits d’inventaire** | Déployer le script `id.fact` qui expose les métadonnées de chaque hôte. | • Le script est présent dans `/etc/ansible/facts.d/id.fact` et exécutable (chmod 755). <br>• Retourne un JSON valide contenant le champ `hostname`. | **Moyen** (10 %) | Nécessite l’accès internet via le proxy. |
| **FS‑04** | **Gestion des credentials SSH** | Centraliser les clés publiques de l’équipe dans le fichier `authorized_keys` de l’utilisateur `admingti`. | • Toutes les clés listées dans le répertoire `keys/` sont présentes dans `/home/admingti/.ssh/authorized_keys`. <br>• Aucun doublon, aucune clé expirée. | **Moyen** (8 %) | Les clés sont stockées chiffrées dans le dépôt Git (Vault). |
| **FS‑05** | **Déploiement du stack Metrics** | Installer les exporters (node, docker, nginx, etc.) et configurer les cibles Prometheus/Loki. | • Les dossiers listés dans `variables.directories_to_create` existent avec les droits 0755. <br>• Les fichiers de cibles (`*.yml`) sont générés conformément aux templates Jinja. <br>• Le service Prometheus expose les métriques ≥ 99 % du temps. | **Haut** (15 %) | Les variables `METRICS_USER` / `METRICS_PASSWD` sont injectées via un secret Vault. |
| **FS‑06** | **Déploiement de l’agent Portainer Edge** | Provisionner le container `portainer/agent` avec les paramètres d’identification Edge. | • Container `portainer_edge_agent` en état `running`. <br>• Les variables `EDGE_ID`, `EDGE_KEY` sont correctement injectées. <br>• Le port 8000 est ouvert et accessible depuis le serveur de gestion. | **Moyen** (7 %) | Nécessite le montage du socket Docker et du répertoire `/` (privileged). |
| **FS‑07** | **Gestion du proxy HTTP/HTTPS** | Appliquer le proxy à tous les services (Docker, apt, ansible, export‑ers). | • Variable d’environnement `http_proxy` et `https_proxy` définies dans `/etc/environment` et dans les services systemd. <br>• `no_proxy` inclut `localhost` et les domaines internes. | **Moyen** (5 %) | Valeur du proxy : `http://proxybl-m.edcs.fr:3128`. |
| **FS‑08** | **Gestion des templates AWS‑CLI** | Générer les fichiers de configuration AWS (`config`, `credentials`) à partir des variables d’inventaire. | • Les deux fichiers existent dans `~/.aws/` avec les permissions 0600. <br>• Les valeurs `aws_region`, `aws_output`, `aws_access_key_id`, `aws_secret_access_key` sont correctement substituées. | **Faible** (3 %) | Aucun accès internet direct – doit passer par le proxy. |
| **FS‑09** | **Gestion des configurations Nginx** | Déployer les fichiers de configuration Nginx (ex. `nginx.conf`, `.htpasswd`). | • Le fichier `/etc/nginx/nginx.conf` correspond au template fourni. <br>• Le service Nginx démarre sans erreurs. | **Faible** (2 %) | Nginx ne doit être installé que sur les hôtes `nginx` du groupe d’inventaire. |
| **FS‑10** | **Gestion des packages de personnalisation** | Déployer les dot‑files (`.vimrc`, `.zshrc`, `.zshaliases`) pour les utilisateurs. | • Les fichiers sont présents dans le répertoire `$HOME` de chaque utilisateur cible. <br>• Les alias fonctionnent (`dcu`, `dps`, …). | **Très faible** (1 %) | Aucun impact sur la sécurité. |

\* **Pondération** : répartition de 100 % pour établir la priorité de l’évaluation des offres.  

↩︎ [Retour au sommaire](#toc)

---  

## 3. Acteurs et parties prenantes  <a id="acteurs"></a>

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **MOA** (Maîtrise d’Ouvrage) – Direction GTI | Décideur, financeur | • Garantir la conformité aux exigences de sécurité.<br>• Obtenir un livrable opérationnel. | • Documentation fonctionnelle complète.<br>• Traçabilité des changements. |
| **MOE** (Maîtrise d’Œuvre) – Équipe DevOps | Réalise le déploiement, maintient les playbooks | • Automatiser le provisioning.<br>• Assurer la disponibilité du service. | • Accès aux scripts Ansible, variables d’environnement, Vault. |
| **Administrateur Système** | Exploite les serveurs cibles | • Vérifier l’état des services, appliquer des correctifs. | • Logs détaillés (`/var/log/pnm3-iaas-ansible/*.log`).<br>• Procédures de rollback. |
| **Opérateur de Monitoring** | Consomme les métriques | • Visualiser la santé des serveurs via Grafana. | • Cibles Prometheus correctement générées.<br>• Accès aux secrets `METRICS_USER/PASSWD`. |
| **Développeur Application** | Déploie ses services sur la même infra | • Utiliser Docker/Portainer sans reconfigurer le proxy. | • Accès au socket Docker et aux variables d’environnement. |
| **RSSI** (Responsable Sécurité des Systèmes d’Information) | Veille sécurité | • S’assurer du respect du RGPD et RGS. | • Aucun mot de passe en clair dans les dépôts.<br>• Gestion du contrôle d’accès (Vault). |
| **Équipe Support** | Traite les incidents | • Disposer d’un Playbook de restauration. | • Documentation d’utilisation et de dépannage. |

↩︎ [Retour au sommaire](#toc)

---  

## 4. Cas d’usage (Use Cases)  <a id="usecases"></a>

### 4.1 Diagramme de cas d’utilisation (Mermaid)  

```mermaid
usecaseDiagram;
    actor MOA as MOA;
    actor MOE / DevOps as MOE;
    actor Admin Sys as ADMIN;
    actor Opérateur Métriques as METRICS;
    actor Développeur App as DEV;
    actor RSSI as RSSI;
    MOA --> (Valider le CCF)
    MOE --> (Déployer l’infrastructure)
    ADMIN --> (Vérifier l’état des services)
    METRICS --> (Consulter les métriques)
    DEV --> (Déployer ses conteneurs)
    RSSI --> (Auditer la conformité)

    (Déployer l’infrastructure) ..> (Provisionner utilitaires) : <<include>>
    (Déployer l’infrastructure) ..> (Déployer le stack Metrics) : <<include>>
    (Déployer l’infrastructure) ..> (Déployer l’agent Portainer) : <<include>>
    (Déployer l’infrastructure) ..> (Gérer les credentials SSH) : <<include>>
    (Déployer l’infrastructure) ..> (Appliquer le proxy) : <<include>>
```

### 4.2 Description détaillée des cas d’usage  

| N° | Nom du cas d’usage | Acteur(s) principal(s) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **UC‑01** | **Déployer l’infrastructure** | MOE | 1. Le pipeline CI démarre (`ci‑deploy‑common.yml`). <br>2. Le playbook clone le dépôt. <br>3. Le playbook `common.yml` est exécuté sur tous les hôtes. <br>4. Les rôles `common`, `metrics`, `portainer‑edge‑agent` sont appliqués successivement. | *E1* : Échec de connexion SSH → le pipeline s’arrête, notification Slack. <br>*E2* : Retour code non‑zéro d’un rôle → le playbook marque le host comme **failed** et continue sur les autres. | Inventaire à jour, variables d’environnement définies, accès Vault. | Tous les services requis sont opérationnels et les logs sont archivés. |
| **UC‑02** | **Mettre à jour le stack Metrics** | MOE / METRICS | 1. Le pipeline `ci‑deploy‑metrics.yml` s’exécute. <br>2. Le rôle `metrics` crée / met à jour les dossiers cibles. <br>3. Les templates Jinja génèrent les fichiers `target.yml`, `urls_*.yml`. <br>4. Le service Prometheus reload les configurations. | *E1* : Variable `METRICS_USER` manquante → le playbook échoue, le ticket d’incident est créé. | Role `metrics` présent dans l’inventaire `supervision`. | Les nouvelles cibles sont prises en compte par Prometheus sans interruption. |
| **UC‑03** | **Déployer l’agent Portainer Edge** | MOE / DEV | 1. Le pipeline `ci‑deploy‑portainer‑edge‑agent.yml` s’exécute. <br>2. Le rôle `portainer‑edge‑agent` crée le fichier `docker‑compose.yml` et lance `docker compose up -d`. | *E1* : Le socket Docker n’est pas accessible → le container ne démarre pas, le playbook signale l’erreur. | Docker installé et fonctionnel, variables `EDGE_ID`/`EDGE_KEY` présentes. | L’agent s’enregistre auprès du serveur Portainer et signale son statut « connected ». |
| **UC‑04** | **Gérer les clés SSH** | MOE / ADMIN | 1. Le playbook `keys.yml` lit le répertoire `keys/`. <br>2. Il assemble les clés dans `/tmp/keys`. <br>3. `authorized_key` les injecte dans le compte `admingti`. | *E1* : Clé corrompue → le playbook signale l’erreur, aucune modification n’est appliquée. | Fichiers de clés présents, accès en écriture au home de `admingti`. | Le fichier `authorized_keys` contient exactement les clés attendues. |
| **UC‑05** | **Collecter les faits d’inventaire** | MOE / ADMIN | 1. Le rôle `common` exécute `facts.yml`. <br>2. Le script `id.fact` est copié et exécuté. <br>3. Ansible récupère les métadonnées (`hostname`, `tags`). | *E1* : Le script ne renvoie pas de JSON → la collecte échoue, le host est marqué `unreachable`. | Le répertoire `/etc/ansible/facts.d` existe. | Les faits sont disponibles dans `ansible_local.id`. |
| **UC‑06** | **Auditer la conformité** | RSSI | 1. Le RSSI consulte les dépôts Git et le Vault. <br>2. Vérifie l’absence de mots de passe en clair. <br>3. Lance un playbook de **audit** (non fourni) qui contrôle les permissions. | *E1* : Un secret est trouvé en clair → le ticket de non‑conformité est créé. | Accès en lecture au dépôt et au Vault. | Le rapport d’audit confirme la conformité ou liste les écarts. |

↩︎ [Retour au sommaire](#toc)

---  

## 5. Processus métier (BPMN)  <a id="processus"></a>

```mermaid
bpmnDiagram;
    participant CI as "CI GitLab"
    participant ANS as "Ansible Runner"
    participant REPO as "GitLab Repo"
    participant INF as "Infrastructure (hosts)"

    CI->>REPO: 1. Trigger pipeline (push / schedule)
    REPO->>CI: 2. Checkout sources;
    CI->>ANS: 3. Execute playbook ci‑deploy‑common.yml;
    ANS->>INF: 4. Apply role common (Docker, Nginx, Python, etc.)
    ANS->>INF: 5. Apply role metrics (if host ∈ supervision)
    ANS->>INF: 6. Apply role portainer‑edge‑agent (if host ∈ all)
    ANS->>CI: 7. Return status (success / failure)
    CI->>CI: 8. Notify (Slack / Email) + Archive logs
```

**Points de contrôle**  

| Étape | Contrôle | Responsable |
|---|---|---|
| 3 – Exécution du playbook | Retour code = 0, logs `common_utilities.log` | MOE |
| 4 – Provisionnement commun | Vérification des services (`docker`, `nginx`, `python3`) | ADMIN |
| 5 – Stack Metrics | Fichiers cibles générés, Prometheus reload OK | METRICS |
| 6 – Agent Portainer | Container `running`, port 8000 ouvert | DEV |
| 7 – Retour status | Notification automatisée | CI / MOA |

↩︎ [Retour au sommaire](#toc)

---  

## 6. Règles métier et contraintes fonctionnelles  <a id="regles"></a>

| N° | Règle métier (condition → action) | Source / Référence |
|---|---|---|
| **R‑01** | Si le serveur appartient au groupe `docker` → le fichier `override.conf` doit être présent et le service Docker doit être redémarré. | `playbooks/roles/common/files/docker/override.conf` |
| **R‑02** | Si `http_proxy` est défini → toutes les tâches `apt`, `pip`, `awscli` doivent utiliser le proxy (`environment`). | `playbooks/common.yml` |
| **R‑03** | Si un hôte possède le tag `metrics` → les dossiers listés dans `metrics.vars.directories_to_create` doivent être créés avant le rendu des templates. | `playbooks/roles/metrics/vars/main.yml` |
| **R‑04** | Si le rôle `team_creds` est exécuté → aucune clé privée ne doit être copiée sur le serveur cible. | `playbooks/roles/team_creds/tasks/main.yml` |
| **R‑05** | Si le fichier `id.fact` ne renvoie pas de JSON valide → le playbook doit s’arrêter (fail fast). | `playbooks/roles/common/tasks/facts.yml` |
| **R‑06** | Les variables `aws_access_key_id` et `aws_secret_access_key` **NE DOIVENT PAS** être stockées en clair dans le dépôt Git. | `awscli/templates/*.j2` + Vault |
| **R‑07** | Tous les logs de playbooks (`*.log`) doivent être conservés ≥ 30 jours et accessible en lecture par l’équipe support. | CI pipeline (`ansible.builtin.shell` redirection) |
| **R‑08** | Le rôle `metrics-rpnginx` doit supprimer le répertoire `/etc/nginx/sites-enabled` avant de copier sa propre configuration. | `metrics-rpnginx/vars/main.yml` |
| **R‑09** | Les secrets (`METRICS_USER`, `METRICS_PASSWD`) sont fournis via **GitLab CI variables** chiffrées et ne sont jamais exposés dans les templates. | `.gitlab-ci.yml` (non affiché) |
| **R‑10** | Conformité RGPD : aucune donnée à caractère personnel n’est collectée par les scripts `id.fact`. | Analyse fonctionnelle du script |

↩︎ [Retour au sommaire](#toc)

---  

## 7. Parcours utilisateurs (User Journey)  <a id="journey"></a>

### 7.1 Parcours « Déploiement complet » (admin)

| Étape | Action (Given/When/Then) | Responsable | Outils |
|---|---|---|---|
| **1** | **Given** le dépôt est à jour et les variables CI sont définies, **When** le développeur valide le merge request, **Then** le pipeline GitLab démarre automatiquement. | Développeur | GitLab CI |
| **2** | **Given** le pipeline a lancé `ci‑deploy‑common.yml`, **When** le playbook s’exécute, **Then** chaque hôte reçoit les utilitaires communs et les logs sont écrits dans `/var/log/pnm3‑iaas‑ansible/common_utilities.log`. | MOE / Ansible Runner | Ansible |
| **3** | **Given** le rôle `metrics` est inclus, **When** les dossiers sont créés, **Then** les fichiers `target.yml` et `urls_*.yml` sont générés et Prometheus reload. | Opérateur Métriques | Prometheus |
| **4** | **Given** le rôle `portainer‑edge‑agent` est exécuté, **When** le container démarre, **Then** l’agent apparaît dans l’interface Portainer. | Développeur | Portainer |
| **5** | **Given** le pipeline s’est terminé, **When** un statut `SUCCESS` est publié, **Then** le tableau de bord GitLab indique le résultat et les logs sont archivés. | MOA | GitLab UI |

### 7.2 Parcours « Gestion des clés SSH »

| Étape | Action | Responsable | Outils |
|---|---|---|---|
| **1** | L’administrateur ajoute une nouvelle clé publique dans le répertoire `keys/`. | ADMIN | Éditeur de texte |
| **2** | Le playbook `keys.yml` est déclenché (manuellement ou via CI). | ADMIN | Ansible |
| **3** | Le rôle `team_creds` assemble toutes les clés et les copie dans `~admingti/.ssh/authorized_keys`. | ADMIN | Ansible |
| **4** | L’administrateur vérifie la présence de la clé via `ssh -i ~/.ssh/id_rsa admingti@host`. | ADMIN | SSH client |
| **5** | En cas d’erreur, le playbook renvoie un code != 0 et le ticket d’incident est créé. | ADMIN | GitLab Issues |

↩︎ [Retour au sommaire](#toc)

---  

## 8. Modèle Conceptuel de Données (MCD)  <a id="mcd"></a>

```mermaid
classDiagram
    class Host {
        +string hostname;
        +string ip;
        +list<string> groups;
        +dict facts;

    class Role {
        +string name;
        +list<string> tasks;
        +dict vars;

    class VariableSet {
        +string name;
        +dict values;

    class MetricTarget {
        +string url;
        +string pole;
        +string instance;

    class Credential {
        +string type   "ssh|aws|gcloud"
        +string value  "public key / access key"

    class LogEntry {
        +datetime ts;
        +string host;
        +string playbook;
        +string level;
        +string message;

    Host "1" --> "*" Role : uses;
    Host "1" --> "1" VariableSet : has;
    Host "1" --> "*" MetricTarget : provides;
    Host "1" --> "*" Credential : stores;
    Host "1" --> "*" LogEntry : generates
```

*Le MCD se veut **abstrait** : aucune notion de tables physiques, clé primaire ou type de base de données n’est exprimée.*  

↩︎ [Retour au sommaire](#toc)

---  

## 9. Critères d’acceptation et validation  <a id="acceptation"></a>

| Fonction de service | Critère d’acceptation | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| **FS‑01** | Tous les hôtes pingables, compte `admingti` sudo sans mot‑de‑passe. | Playbook `ci‑clone‑project.yml` + script ping. | ADMIN | **M** |
| **FS‑02** | Docker, Nginx, Python 3, Pip installés, services démarrés. | `ansible.builtin.service_facts` + `docker info`. | MOE | **S** |
| **FS‑03** | Script `id.fact` présent, exécutable, retourne JSON valide. | `ansible.builtin.command` + validation JSON. | ADMIN | **M** |
| **FS‑04** | `authorized_keys` contient exactement les clés du répertoire `keys/`. | `diff` entre `/tmp/keys` et le fichier distant. | ADMIN | **C** |
| **FS‑05** | Tous les dossiers listés créés, fichiers de cibles générés, Prometheus reload OK. | `ansible.builtin.stat` + `curl -s http://localhost:9090/-/reload`. | METRICS | **S** |
| **FS‑06** | Container `portainer_edge_agent` en état `running`, port 8000 ouvert. | `docker ps` + `nc -zv localhost 8000`. | DEV | **C** |
| **FS‑07** | Variables `http_proxy`/`https_proxy` appliquées aux services Docker et apt. | `systemctl show docker | grep Proxy`. | ADMIN | **M** |
| **FS‑08** | Fichiers `~/.aws/config` & `credentials` créés, permissions 0600. | `stat -c %a ~/.aws/*`. | DEV | **L** |
| **FS‑09** | Nginx démarre sans erreurs, `nginx -t` OK. | `ansible.builtin.service_facts` + `nginx -t`. | ADMIN | **L** |
| **FS‑10** | Dot‑files présents, alias fonctionnels. | `grep dcu ~/.zshrc`. | DEV | **L** |

**Méthode de validation globale**  

1. Exécution du pipeline complet (`ci‑deploy‑common.yml` → `ci‑deploy‑metrics.yml` → `ci‑deploy‑portainer‑edge‑agent.yml`).  
2. Analyse automatisée du fichier de log (`/var/log/pnm3‑iaas‑ansible/*.log`) avec un script de **validation** qui compare les critères ci‑dessus.  
3. Validation manuelle ponctuelle (audit) par le RSSI.  

↩︎ [Retour au sommaire](#toc)

---  

## 10. Annexes  <a id="annexes"></a>

### 10.1 Glossaire métier

| Terme | Définition |
|---|---|
| **IaaS** | Infrastructure as a Service – fourniture de ressources de calcul, stockage et réseau sous forme de services. |
| **Playbook** | Fichier YAML décrivant une suite de tâches Ansible. |
| **Role** | Ensemble réutilisable de fichiers (tasks, vars, templates, files) pour une fonction métier. |
| **Proxy** | Serveur intermédiaire qui relaie les requêtes HTTP/HTTPS vers Internet. |
| **Metrics stack** | Ensemble de services (Prometheus, Loki, exporters) collectant et stockant les métriques. |
| **Portainer Edge Agent** | Agent léger déployé sur chaque nœud pour la gestion distante des containers via Portainer. |
| **Vault** | Outil de chiffrement de secrets (ex. GitLab CI variables chiffrées). |
| **RGPD** | Règlement Général sur la Protection des Données – cadre légal européen. |
| **RGS** | Référentiel Général de Sécurité – exigences de sécurité de l’État français. |

### 10.2 Référentiels et normes applicables

| Référence | Description |
|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences – processus, documents, bonnes pratiques. |
| **ISO/IEC 19505** | UML 2.x – notation des diagrammes (use‑case, class). |
| **ISO/IEC 19510** | BPMN – modélisation des processus métiers. |
| **RGPD** (UE 2016/679) | Protection des données à caractère personnel. |
| **RGS** (ANSSI) | Sécurité des systèmes d’information de l’État. |

### 10.3 Historique des versions du document

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 2026‑04‑28 | ChatGPT (OpenAI) | Création du CCF complet, génération de diagrammes, tables de critères. |
| 1.1 | – | – | À venir – intégration de retours MOA / MOE. |

---  

*Fin du Cahier des Charges Fonctionnel.*  

↩︎ **[↑ Retour au sommaire](#toc)**