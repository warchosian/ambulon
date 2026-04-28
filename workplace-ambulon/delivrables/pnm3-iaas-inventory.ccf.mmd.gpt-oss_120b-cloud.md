# 📘 Cahier des Charges Fonctionnel (CCF) – **pnm3‑iaas‑inventory**  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet {#intro}

| Élément | Description |
|---|---|
| **Nom du projet** | `pnm3‑iaas‑inventory` |
| **Référentiel** | `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\pnm3-iaas-inventory` |
| **Nature** | Ensemble d’**playbooks Ansible** et de **fichiers de configuration** permettant de maintenir un inventaire centralisé des machines IaaS (Infrastructure as a Service) utilisées par la plateforme *pnm3* (RIE, DIN, etc.). |
| **Objectifs stratégiques** | 1. Garantir la **cohérence** et la **traçabilité** des environnements (DEV, PREPROD, PROD, DEMO, INT, RECETTE). <br>2. Automatiser la **mise à jour** de l’inventaire Ansible et la **configuration DNS**. <br>3. Faciliter le **déploiement** d’applications via les données d’inventaire (IP, DNS, métriques, portainer). <br>4. Centraliser la **gestion des accès SSH** (clé privée publique). |
| **Périmètre fonctionnel** | **Inclus** : <br>• Gestion du catalogue de machines (YAML). <br>• Génération et mise à jour du fichier d’inventaire Ansible. <br>• Provisionnement DNS (playbooks `dns/playbooks`). <br>• Publication des métriques et des identifiants Portainer. <br>• Gestion des environnements et tags. <br>• CI/CD (pipeline GitLab). <br>**Exclus** : <br>• Gestion du cycle de vie des VM (création/suppression hors Ansible). <br>• Monitoring des services applicatifs (hors métriques d’inventaire). |
| **Livrables attendus** | 1. Documentation fonctionnelle (CCF). <br>2. Playbooks Ansible opérationnels. <br>3. Fichiers d’inventaire validés. <br>4. Scripts de génération de configuration SSH/DNS. |
| **Contraintes majeures** | - Conformité aux normes **NF EN 16271** (expression fonctionnelle du besoin) et **ISO/IEC/IEEE 29148** (ingénierie des exigences). <br>- Respect du **RGPD** pour les adresses IP et les données de connexion. <br>- Compatibilité avec les outils CI/CD GitLab et les agents **Portainer Edge**. |
| **Références** | NF EN 16271, ISO/IEC/IEEE 29148:2018, ISO/IEC 19505 (UML 2.x), ISO/IEC 19510 (BPMN). |

↩︎ [Retour au sommaire](#toc)

---  

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) {#fonctions}

### 2.1 Décomposition en fonctions de service

| # | Fonction de service (FS) | Description (quoi) | Critères d’appréciation | Niveau d’importance / Pondération* | Contraintes |
|---|---|---|---|---|---|
| FS‑01 | **Gestion du catalogue de machines** | Centraliser, versionner et publier la description de chaque machine (IP, DNS, produit, environnement, métriques, portainer). | - 100 % des machines décrites dans le répertoire `inventory/`. <br>- Validation YAML (schema) sans erreur. | **Très haute** (30 %) | - Respect du schéma YAML (clé `machine`, `ip`, `dns`, `products`, `environment`, `tags`). <br>- Aucun champ sensible (ex. clé privée) n’est stocké. |
| FS‑02 | **Génération de l’inventaire Ansible** | Transformer les fichiers YAML du catalogue en un inventaire utilisable par Ansible (`inventory.ini`). | - Inventaire généré sans doublons. <br>- Temps de génération ≤ 5 s pour 200 machines. | **Haute** (20 %) | - Doit être idempotent. |
| FS‑03 | **Provisionnement DNS** | Appliquer la configuration DNS (unbound) sur les hôtes DNS via le playbook `dns/playbooks/*.yml`. | - 100 % des hôtes DNS configurés avec le fichier `unbound.conf`. <br>- Redémarrage du service `unbound` réussi. | **Moyenne** (15 %) | - Accès `sudo` requis. |
| FS‑04 | **Gestion des accès SSH** | Déployer la clé publique `inventory.key.pub` sur les comptes systèmes (`dns` ou `docker`). | - Clé présente dans `~/.ssh/authorized_keys` de chaque hôte ciblé. <br>- Aucun accès non‑autorisé détecté. | **Moyenne** (10 %) | - La clé privée ne doit jamais être versionnée (`.gitignore`). |
| FS‑05 | **Publication des métriques** | Fournir les URLs de métriques (Prometheus, Grafana) via le champ `metrics` du catalogue. | - URL accessible (code 200) depuis le réseau interne. | **Moyenne** (10 %) | - Conformité aux conventions de nommage `xxx.metrics.pnm3...`. |
| FS‑06 | **Intégration Portainer Edge** | Propager `edgeId` / `edgeKey` aux hôtes qui utilisent Portainer. | - Agent Portainer enregistré et fonctionnel. | **Faible** (5 %) | - Tags `docker` obligatoires pour les hôtes concernés. |
| FS‑07 | **Gestion des environnements** | Classifier chaque machine selon `environment` (DEV, PREPROD, PROD, DEMO, INT, RECETTE). | - 100 % des machines correctement taguées. | **Moyenne** (5 %) | - Les scripts de CI/CD utilisent ce champ pour le ciblage. |
| FS‑08 | **CI/CD pipeline GitLab** | Déclencher les playbooks à chaque modification du répertoire `inventory/`. | - Pipeline passe (`green`) pour chaque commit. | **Moyenne** (5 %) | - Fichier `.gitlab-ci.yml` doit rester valide. |

\* La somme des pondérations = 100 %.

### 2.2 Priorisation (MoSCoW)  

| Priorité | Fonctions | Justification |
|---|---|---|
| **Must** | FS‑01, FS‑02, FS‑04 | Le catalogue et l’inventaire sont le cœur du projet. |
| **Should** | FS‑03, FS‑05, FS‑07 | Nécessaires pour le bon fonctionnement des environnements. |
| **Could** | FS‑06, FS‑08 | Améliorent l’expérience mais ne bloquent pas le service. |
| **Won’t** | (hors périmètre) | Gestion du provisioning VM, monitoring applicatif détaillé. |

↩︎ [Retour au sommaire](#toc)

---  

## 3️⃣ Acteurs et parties prenantes {#acteurs}

| Acteur | Rôle | Objectifs / Besoins spécifiques |
|---|---|---|
| **MOA (Maître d’Ouvrage)** | Responsable fonctionnel du SI RIE | • Disposer d’un inventaire fiable.<br>• Garantir la traçabilité des environnements. |
| **MOE (Maître d’Œuvre)** | Équipe DevOps / Infrastructure | • Implémenter et maintenir les playbooks.<br>• Assurer la conformité sécurité. |
| **Opérateurs de plateforme** | Administrateurs système | • Ajouter / supprimer des machines.<br>• Vérifier la bonne configuration DNS/SSH. |
| **Développeurs d’applications** | Consommateurs de l’inventaire | • Utiliser les variables d’inventaire dans les pipelines CI/CD. |
| **RSSI (Responsable Sécurité des Systèmes d’Information)** | Garant de la sécurité | • S’assurer du respect du RGPD et de la non‑exposition des clés privées. |
| **Utilisateurs finaux (services métiers)** | Consommateurs indirects | • Bénéficier d’applications disponibles via les URLs d’accès (`appUrls`). |

↩︎ [Retour au sommaire](#toc)

---  

## 4️⃣ Cas d’usage (Use Cases) {#use-cases}

### 4.1 Diagramme de cas d’utilisation (UML)  

```mermaid
usecaseDiagram;
    actor MOA as MOA;
    actor MOE as MOE;
    actor Opérateur as OP;
    actor Développeur as DEV;
    actor RSSI as RSSI;
    MOA --> (Définir besoin fonctionnel)
    MOE --> (Mettre en place playbooks)
    OP --> (Ajouter / Modifier machine)
    OP --> (Déployer clé SSH)
    OP --> (Appliquer configuration DNS)
    DEV --> (Consulter inventaire Ansible)
    DEV --> (Déployer application)
    RSSI --> (Auditer conformité sécurité)

    (Déployer clé SSH) ..> (Gérer catalogue) : <<include>>
    (Appliquer configuration DNS) ..> (Gérer catalogue) : <<include>>
    (Consulter inventaire) ..> (Gérer catalogue) : <<extend>>
```

### 4.2 Catalogue détaillé des cas d’usage  

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| UC‑01 | **Ajouter une machine au catalogue** | Opérateur | 1. L’opérateur crée un fichier `inventory/<nom>.yml` conforme au schéma.<br>2. Commit & push.<br>3. Le pipeline GitLab lance le playbook `generate_inventory.py`.<br>4. L’inventaire Ansible est mis à jour. | - **UC‑01‑A** : Fichier YAML invalide → rejet du commit (linter).<br>- **UC‑01‑B** : IP déjà existante → erreur d’unicité, le pipeline échoue. | - Accès au dépôt GitLab.<br>- Linter Ansible installé. | - La machine apparaît dans l’inventaire.<br>- Un ticket de suivi (optionnel) est créé. |
| UC‑02 | **Modifier les attributs d’une machine** | Opérateur | 1. Modification du fichier YAML (ex. changement d’`environment`).<br>2. Commit & push.<br>3. Le pipeline regénère l’inventaire. | - **UC‑02‑A** : Modification du champ `machine` (nom) → création d’une nouvelle entrée + suppression de l’ancienne. | - Machine déjà présente dans le catalogue. | - Les nouvelles valeurs sont prises en compte immédiatement. |
| UC‑03 | **Supprimer une machine** | Opérateur | 1. Suppression du fichier YAML.<br>2. Commit & push.<br>3. Le pipeline retire la machine de l’inventaire. | - **UC‑03‑A** : Tentative de suppression d’une machine encore utilisée par un service → alerte manuelle (tag `exclude`). | - Aucun processus critique ne dépend de la machine. | - La machine n’apparaît plus dans l’inventaire. |
| UC‑04 | **Déployer la clé SSH sur les hôtes** | Opérateur | 1. Le playbook `dns/playbooks/setup.yml` lit la variable `inventory.key.pub`.<br>2. La tâche `authorized_key` copie la clé sur l’utilisateur cible. | - **UC‑04‑A** : Clé publique manquante → échec du playbook, notification Slack. | - Fichier `inventory.key.pub` présent (décrit dans `.gitignore`). | - Accès SSH password‑less fonctionnel. |
| UC‑05 | **Appliquer la configuration DNS** | Opérateur | 1. Exécution du playbook `dns/playbooks/main.yml`.<br>2. Le template `unbound.conf` est copié.<br>3. Service `unbound` redémarré. | - **UC‑05‑A** : Service `unbound` ne démarre pas → rollback, alerte. | - Hôte DNS reachable via Ansible. | - Résolution DNS interne mise à jour. |
| UC‑06 | **Consulter l’inventaire depuis un pipeline CI** | Développeur | 1. Le job CI récupère le fichier `inventory.ini`.<br>2. Utilise les variables (`{{ hostvars[...] }}`) pour déployer l’application. | - **UC‑06‑A** : Inventaire non synchronisé → job échoue, re‑run après pipeline. | - Pipeline déclenché après un commit. | - Déploiement applicatif réussi. |
| UC‑07 | **Auditer la conformité sécurité** | RSSI | 1. Exécution du script de lint (`.ansible-lint`).<br>2. Vérification de l’absence de clés privées dans le repo.<br>3. Rapport envoyé. | - **UC‑07‑A** : Violation détectée → blocage du merge. | - Accès en lecture au dépôt. | - Conformité attestée ou corrective appliquée. |

↩︎ [Retour au sommaire](#toc)

---  

## 5️⃣ Processus métier (BPMN) {#processus} *(optionnel)*  

```mermaid
bpmnDiagram
  participant MOE as "Équipe DevOps"
  participant Git as "GitLab"
  participant CI as "Pipeline CI"
  participant ANS as "Ansible"
  
  startEvent(start) 
  --> task1[Création / mise à jour d’un fichier YAML]
  --> task2[Commit & Push]
  --> task3[GitLab déclenche pipeline]
  --> task4[Run lint & validation]
  --> exclusiveGateway(gw1)
  -->|OK| task5[Run generate_inventory.py]
  -->|KO| taskError[Notifier l’opérateur]
  --> task6[Ansible apply (DNS / SSH)]
  --> endEvent(end);
  
  gw1 -->|Erreur| taskError;
  taskError --> endEvent;
```

↩︎ [Retour au sommaire](#toc)

---  

## 6️⃣ Règles métier et contraintes fonctionnelles {#regles}

| # | Règle (formulation conditionnelle) | Source / Référence |
|---|---|---|
| R‑01 | **Si** un fichier `inventory/*.yml` est ajouté **alors** il doit contenir les clés obligatoires `machine`, `ip`, `dns`, `products`, `environment`. | NF EN 16271 – §5.1 |
| R‑02 | **Si** le champ `environment` = `PROD` **alors** le tag `docker` **et** le champ `portainer.edgeId` sont obligatoires. | ISO/IEC 29148 – exigence de qualité |
| R‑03 | **Si** `appUrls` contient une URL `proxy` **alors** le domaine doit appartenir au sous‑domaine `din.developpement-durable.gouv.fr`. | Contrainte organisationnelle |
| R‑04 | **Si** le fichier `.gitignore` ne mentionne `inventory.key` **alors** le commit est rejeté. | Politique Git |
| R‑05 | **Si** la version de Debian du serveur est < 12 **alors** le playbook `setup.yml` doit installer le paquet `sudo`. | Contrainte technique |
| R‑06 | **Si** le champ `metrics.url` utilise le protocole `http` **alors** il doit être accessible uniquement depuis le réseau interne (IP 10/172/192.168). | Sécurité réseau |
| R‑07 | **Si** un tag `exclude` est présent **alors** l’hôte n’est pas considéré dans les pipelines de déploiement automatisé. | Gestion de la chaîne CI/CD |
| R‑08 | **Si** le playbook `dns/playbooks/main.yml` échoue **alors** le job CI doit être marqué `failed` et un ticket JIRA doit être créé automatiquement. | Processus d’incident |

↩︎ [Retour au sommaire](#toc)

---  

## 7️⃣ Parcours utilisateurs (User Journey) {#parcours}

| Étape | Interaction | Action attendue | Critères d’acceptation (Gherkin) |
|---|---|---|---|
| **1. Connexion** | Opérateur ouvre le dépôt GitLab. | Authentification via SSO. | `Given` l’opérateur est authentifié `When` il ouvre le projet `Then` il voit la branche `main`. |
| **2. Création d’une machine** | L’opérateur crée `inventory/nouvelle‑machine.yml`. | Fichier conforme au schéma. | `Given` le fichier respecte le schéma `When` il commit `Then` le pipeline passe le lint. |
| **3. Validation CI** | GitLab déclenche le pipeline. | Lint, génération d’inventaire, playbooks DNS/SSH. | `Given` le pipeline démarre `When` toutes les étapes réussissent `Then` l’inventaire est mis à jour. |
| **4. Consultation** | Développeur récupère `inventory.ini`. | Variables d’hôte disponibles pour le déploiement. | `Given` le job CI récupère le fichier `When` il exécute le playbook d’app `Then` le service est déployé sur la nouvelle machine. |
| **5. Audit** | RSSI lance le script d’audit. | Aucun secret présent, conformité RGPD. | `Given` le script d’audit s’exécute `When` aucun secret trouvé `Then` le rapport indique “OK”. |

↩︎ [Retour au sommaire](#toc)

---  

## 8️⃣ Modèle Conceptuel de Données (MCD) {#mcd}

```mermaid
classDiagram
    class Machine {
        +string machine;
        +string ip;
        +list~string~ dns;
        +list~string~ products;
        +list~string~ appUrls;
        +string environment;
        +list~string~ tags;
        +Portainer portainer;
        +Metrics metrics;
        +System system;

    class Portainer {
        +string edgeId;
        +string edgeKey;

    class Metrics {
        +string name;
        +string url;
        +string pole;

    class System {
        +string name;
        +int version;

    Machine "1" --> "0..1" Portainer;
    Machine "1" --> "1" Metrics;
    Machine "1" --> "1" System
```

*Remarque* : Le modèle reste **indépendant de toute technologie** (pas de tables SQL, pas de contraintes d’implémentation).

↩︎ [Retour au sommaire](#toc)

---  

## 9️⃣ Critères d’acceptation et validation {#acceptation}

| Fonction | Critère d’acceptation | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| FS‑01 (Catalogue) | Tous les fichiers YAML valides, aucun doublon d’IP. | `ansible-lint` + script Python de vérification d’unicité. | MOE | **MUST** |
| FS‑02 (Inventaire) | Inventaire Ansible généré, synchronisé avec le catalogue. | Comparaison du checksum du fichier `inventory.ini` avant/après commit. | MOE | **MUST** |
| FS‑03 (DNS) | Unbound configuré, service actif. | `ansible-playbook -check dns/playbooks/main.yml` + `systemctl status unbound`. | Opérateur | **SHOULD** |
| FS‑04 (SSH) | Clé publique présente dans `authorized_keys`. | `ssh` vers chaque hôte, `grep` de la clé. | Opérateur | **MUST** |
| FS‑05 (Métriques) | URL répond en `200` depuis le réseau interne. | `curl -I $url`. | RSSI | **SHOULD** |
| FS‑06 (Portainer) | Edge agent enregistré, `edgeId` reconnu. | API Portainer `/api/endpoints`. | MOE | **COULD** |
| FS‑07 (Environnements) | Chaque machine possède le tag `environment` correct. | Script de contrôle `grep environment` sur le répertoire. | MOE | **SHOULD** |
| FS‑08 (CI/CD) | Pipeline passe à chaque modification du catalogue. | Historique GitLab CI (`green`). | MOE | **COULD** |

↩︎ [Retour au sommaire](#toc)

---  

## 🔟 Annexes {#annexes}

### A. Glossaire métier  

| Terme | Définition |
|---|---|
| **IaaS** | Infrastructure as a Service – ressources de calcul, réseau et stockage fournies sous forme de VM. |
| **Portainer Edge** | Agent léger permettant la gestion de conteneurs Docker depuis une instance centrale. |
| **Unbound** | Résolveur DNS récursif utilisé pour la résolution interne. |
| **Metrics** | Points d’exposition des indicateurs de santé (Prometheus). |
| **Environment** | Niveau d’isolation (DEV, PREPROD, PROD, DEMO, INT, RECETTE). |
| **Tag `exclude`** | Indique que la machine ne doit pas être prise en compte dans les déploiements automatisés. |

### B. Référentiels et normes applicables  

| Référence | Intitulé |
|---|---|
| NF EN 16271 | Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel. |
| ISO/IEC/IEEE 29148:2018 | Ingénierie des exigences – Processus et documentation. |
| ISO/IEC 19505 | UML 2.x – Notation et diagrammes. |
| ISO/IEC 19510 | BPMN – Modélisation des processus métier. |
| RGPD | Règlement Général sur la Protection des Données – gestion des IP et clés. |

### C. Historique des versions du CCF  

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 2024‑04‑28 | ChatGPT (Assistant) | Création initiale du CCF – structuration complète selon NF EN 16271 & ISO 29148. |
| 1.1 | – | – | (à venir) Ajout de scénarios de reprise après sinistre. |
| 1.2 | – | – | (à venir) Intégration du modèle de données détaillé (ER). |

↩︎ [Retour au sommaire](#toc)

---  

*Fin du Cahier des Charges Fonctionnel*  

---  