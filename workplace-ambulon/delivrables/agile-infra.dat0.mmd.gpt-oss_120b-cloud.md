# Dossier d’Architecture Technique (DAT) – **agile‑infra**
*Projet : agile‑infra*  
*Version : 1.0 – 2026‑04‑27*  

---  

## 1. Introduction et objectifs  

### 1.1 Vue d’ensemble fonctionnelle (C4‑L1)  

```mermaid
graph TD
    A[Développeur] -->|push code| B[GitLab Repository]
    B -->|pipeline déclenché| C[GitLab CI Runner]
    C -->|exécute| D[Ansible Playbook (recette/main.yml)]
    D -->|déploie| E[Docker‑Compose (frontend, backend, DB)]
    E -->|expose| F[Nginx Reverse‑Proxy]
    F -->|service| G[Utilisateurs / Applications clientes]

    style A fill:#E3F2FD,stroke:#2196F3,stroke-width_2px;
    style B fill:#FFF3E0,stroke:#FB8C00,stroke-width_2px;
    style C fill:#E8F5E9,stroke:#66BB6A,stroke-width_2px;
    style D fill:#F3E5F5,stroke:#AB47BC,stroke-width_2px;
    style E fill:#E0F7FA,stroke:#00ACC1,stroke-width_2px;
    style F fill:#FFEBEE,stroke:#E53935,stroke-width_2px;
    style G fill:#F5F5F5,stroke:#9E9E9E,stroke-width_2px
```

*Le projet **agile‑infra** automatise le déploiement d’une stack applicative (frontend, backend, base de données) via un pipeline GitLab CI qui invoque un playbook Ansible. Le playbook génère un `docker‑compose.yml` à partir d’un template Jinja2, charge les secrets et les versions, puis lance les conteneurs avec Docker Compose. Un reverse‑proxy Nginx assure l’accès externe.*

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif | Raison métier / utilisateur |
|---|-----------|----------------------------|
| 1 | **Performance** – temps de mise à jour < 5 min après commit | Garantir une disponibilité continue de la plateforme |
| 2 | **Sécurité** – chiffrement AES‑256 des sauvegardes, gestion des secrets hors code | Protéger les données sensibles et répondre aux exigences réglementaires |
| 3 | **Maintenabilité** – code IaC versionné, tests automatisés | Réduire le coût de la dette technique et faciliter les évolutions |
| 4 | **Opérabilité** – monitoring centralisé (Prometheus/Grafana) et alertes | Permettre aux équipes d’exploitation de réagir rapidement |
| 5 | **Accessibilité** – interface web conforme WCAG 2.1 AA | Assurer l’accès à tous les usagers internes/externes |

---  

## 2. Parties prenantes  

| Rôle | Contact | Attentes principales |
|------|---------|----------------------|
| **Maître d’Ouvrage (MOA)** | M. Dupont – PO | Livraison fiable, respect des SLAs |
| **Développeur / Mainteneur** | S. Leroy – DevOps | CI/CD fluide, documentation à jour |
| **Responsable Sécurité (RSSI)** | C. Moreau – RSSI | Conformité D‑I‑C‑T, auditabilité |
| **Exploitation / Ops** | J. Martin – Ops | Supervision, sauvegardes, restauration |
| **Utilisateurs finaux** | Équipes métier | Accès stable aux services métiers |
| **Fournisseur d’infrastructure** | GTI – Support Cloud | Disponibilité du tenant ECO4, support technique |

---  

## 3. Contraintes  

### 3.1 Contraintes d’architecture  

| Domaine | Contrainte |
|---------|------------|
| **Technologique** | Utilisation exclusive d’Ansible ≥ 2.9, Docker Compose ≥ 2.0, images Docker signées |
| **Infrastructure** | Hébergement sur le cloud interne **ECO4** (OpenStack) – tenant `pnm3` |
| **Organisationnelle** | Tous les livrables (playbooks, templates, secrets) versionnés dans le dépôt GitLab du projet |
| **Réglementaire** | Respect du RGPD pour les données à caractère personnel, archivage 6 ans des logs |
| **Interopérabilité** | Interface avec le service `pasta‑cooker-client` via WebSocket (`ws://cooker.pnm3.r2.eco4.cloud.e2.rie.gouv.fr`) |

### 3.2 Contraintes de sécurité (modèle D‑I‑C‑T)  

| Aspect | Exigence |
|--------|----------|
| **Disponibilité** | Redondance Nginx (2 instances) + health‑checks automatisés |
| **Intégrité** | Signature des images Docker, contrôle d’intégrité des templates Jinja2 |
| **Confidentialité** | Secrets stockés dans `recette/vars/secrets.yml` chiffrés, déchiffrement via `SECRET_KEY` et `DECRYPT_PASSWORD` fournis par CI |
| **Traçabilité** | Logs GitLab CI, journaux Ansible (`ansible.log`), audit des changements de configuration (Git commit hash) |

---  

## 4. Contexte et périmètre  

### 4.1 Contexte métier  

*Le projet **agile‑infra** fournit l’infrastructure nécessaire à la plateforme « Agile » (gestion de projets, tableaux Kanban, reporting). Il s’agit d’un composant partagé entre plusieurs équipes internes qui nécessite un déploiement rapide, fiable et sécurisé.*

### 4.2 Contexte technique  

| Interface externe | Protocole / Format | Fréquence / Volume | Description |
|-------------------|--------------------|--------------------|-------------|
| **GitLab CI** | HTTPS / YAML | À chaque push sur branche `main` ou `feature/*` | Déclenche le job `run_recette` |
| **pasta‑cooker‑client** | WebSocket (`ws://…`) | Une connexion par pipeline | Exécute le playbook Ansible |
| **Docker Registry** | HTTPS (OCI) | Pull d’images lors du `docker compose up` | Images `front`, `back`, `db` référencées via `versions.yml` |
| **Nginx Reverse‑Proxy** | HTTP/HTTPS | Permanent (traffic utilisateur) | Point d’entrée unique, load‑balancing |
| **Prometheus / Grafana** | HTTP / Pull | Scraping chaque 15 s | Métriques d’applications et d’infrastructure |
| **Stockage objet** | S3‑compatible (AES‑256) | Sauvegarde quotidienne | B3, Outscale SecNumCloud, Google Cloud |

---  

## 5. Stratégie de solution  

### 5.1 Modèles de conception & décisions majeures  

| Décision | Justification |
|----------|----------------|
| **Infrastructure as Code (IaC) avec Ansible** | Centralise la configuration, facilite la reproductibilité |
| **Déploiement conteneurisé via Docker‑Compose** | Simplicité de mise en place, versionnage des services |
| **Pipeline GitLab CI + pasta‑cooker‑client** | Orchestration automatisée, séparation des responsabilités CI/infra |
| **Reverse‑proxy Nginx en front** | Gestion du TLS, point d’entrée unique, scalabilité |
| **Monitoring stack Prometheus/Grafana/Loki** | Observabilité complète (metrics, logs, alertes) |
| **Sauvegarde chiffrée AES‑256** | Conformité aux exigences de confidentialité |

### 5.2 Environnement technologique  

| Couche | Technologie / Version |
|-------|-----------------------|
| **CI/CD** | GitLab 13.x, Runner Docker, pasta‑cooker‑client v1.0.6 |
| **Provisionning** | Ansible 2.10+, Jinja2 templates |
| **Conteneurs** | Docker 23.x, Docker‑Compose 2.20 |
| **Langages** | YAML (playbooks, CI), Jinja2, Bash (handlers) |
| **Base de données** | PostgreSQL 11.16‑alpine3.16 (déclaré dans `versions.yml`) |
| **Frontend** | Image Docker `front:latest` (ex. React) |
| **Backend** | Image Docker `back:4.7.0` (ex. Spring Boot) |
| **Reverse‑proxy** | Nginx 1.24 (load‑balanced pair) |
| **Monitoring** | Prometheus 2.48, Grafana 10, Loki 2.9, AlertManager 0.27 |
| **Sauvegarde** | Scripts GTI, chiffrement AES‑256, stockage S3‑compatible |

### 5.3 Forge logicielle  

| Élément | Outil / Configuration |
|---------|----------------------|
| **Gestion du code** | GitLab repository (branch `main` = production) |
| **Intégration continue** | `.gitlab-ci.yml` – job `run_recette` |
| **Tests** | Ansible lint, Docker‑Compose validation (`docker compose config`), tests unitaires applicatifs (ex. Maven/Gradle) |
| **Déploiement** | `pasta-cooker $PLAYBOOK --project $PROJECT --url $CD_URL …` |
| **Artefacts** | Images Docker poussées vers registre interne (ECO4) |
| **Audit** | GitLab audit logs, Ansible verbose (`-vvv`) |

---  

## 6. Vue en Briques (C4‑L2)  

```mermaid
graph TB
    subgraph CI;
        CI[GitLab CI Runner]
        CI -->|trigger| ANS[Ansible Executor (pasta‑cooker)]
    end
    subgraph Infra;
        ANS -->|playbook| TPL[Template Engine (Jinja2)]
        ANS -->|creates| DC[Docker‑Compose File]
        DC -->|orchestrates| APP[Application Stack]
        APP -->|frontend| FE[Container: front]
        APP -->|backend| BE[Container: back]
        APP -->|db| DB[Container: postgres]
        APP -->|proxy| NG[Nginx (load‑balanced pair)]
    end
    subgraph Monitoring;
        MON[Prometheus/Grafana/Loki]
        APP -.-> MON;
        NG -.-> MON;
    end
    subgraph Backup;
        BCK[Backup Scripts (AES‑256)]
        DB --> BCK;
    end
    style CI fill:#E3F2FD,stroke:#2196F3;
    style ANS fill:#F3E5F5,stroke:#AB47BC;
    style TPL fill:#FFF3E0,stroke:#FB8C00;
    style DC fill:#E8F5E9,stroke:#66BB6A;
    style APP fill:#E0F7FA,stroke:#00ACC1;
    style NG fill:#FFEBEE,stroke:#E53935;
    style MON fill:#F5F5F5,stroke:#9E9E9E;
    style BCK fill:#FCE4EC,stroke:#D81B60
```

*Descriptions des conteneurs principaux*  

| Conteneur | Rôle | Principaux services exposés |
|----------|------|-----------------------------|
| `front` | UI web (React/Angular) | HTTP 80 → Nginx → `front` |
| `back` | API métier (Spring Boot, Java) | HTTP 8080 (via Nginx) |
| `postgres` | BD relationnelle | Port 5432 (interne) |
| `nginx` | Reverse‑proxy, TLS termination, load‑balancing | HTTPS 443 → `front`/`back` |
| `prometheus` | Scraping metrics (`/metrics` endpoint) | Port 9090 |
| `grafana` | Dashboard visualisation | Port 3000 |
| `loki` | Centralisation des logs | Port 3100 |

---  

## 7. Vue Exécution  

### 7.1 Scénario 1 – Déploiement continu (pipeline CI)  

1. **Commit** sur branche `main` → GitLab détecte le changement.  
2. Job `run_recette` démarre sur le runner Docker avec l’image `pasta‑cooker-client`.  
3. Variables d’environnement (`CD_URL`, `PROJECT`, `SECRET_KEY`, `DECRYPT_PASSWORD`) sont injectées.  
4. `pasta‑cooker` exécute le playbook `recette/main.yml`.  
5. Ansible crée le répertoire d’application (real vs dry‑run), charge les secrets (`secrets.yml`) et les versions (`versions.yml`).  
6. Le template `docker-compose.yml.j2` est rendu dans le répertoire cible.  
7. Handler `up the containers` lance `docker compose up -d --remove-orphans`.  
8. Nginx (déjà déployé) détecte les nouveaux conteneurs via Docker‑Compose networking.  

*Résultat* : l’application est disponible à l’URL `http://agile.rec.pnm3.eco4.cloud.e2.rie.gouv.fr` en moins de 5 min.

### 7.2 Scénario 2 – Mise à jour d’une version d’image  

1. L’équipe **dev** pousse une nouvelle image `front:1.2.0` dans le registre Docker interne.  
2. Le fichier `recette/vars/versions.yml` est mis à jour (`frontVersion: ":1.2.0"`).  
3. Un nouveau commit déclenche le même pipeline.  
4. Ansible reconstruit le `docker‑compose.yml` avec la nouvelle version.  
5. Handler `up the containers` effectue un `docker compose up -d --remove-orphans` → Docker effectue un **rolling update** (stop old container, start new).  
6. Monitoring détecte le temps de réponse ; si une anomalie survient, AlertManager envoie une alerte.

### 7.3 Scénario 3 – Restauration suite à sinistre  

1. Incident déclaré → l’opérateur lance le script de restauration du backup (stocké sur B3 ou Outscale).  
2. Le dump chiffré est déchiffré (AES‑256) puis importé dans le conteneur PostgreSQL.  
3. Ansible exécute un playbook de **re‑provisioning** qui recrée les répertoires et relance les conteneurs.  
4. Les métriques et logs reviennent à la normale, l’alerte se clôture automatiquement.

---  

## 8. Vue Déploiement *(section standardisée)*  

### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | À compléter | À compléter | À compléter | À compléter |
| Recette       | À compléter | À compléter | À compléter | À compléter |
| Production    | À compléter | À compléter | À compléter | À compléter |

### Infrastructure
Le produit est hébergé sur le cloud interne **ECO4** basé sur **Openstack**, dans le tenant **'pnm3'** du département.  
Le reverse-proxy **Nginx** du schéma ci-dessous est en fait une paire de Nginx load‑balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx] -- B[Application]
    B -- C[Base de données]
    B -- D[Autres services]
```

### Supervision
Le produit est supervisé via le système standard du **GTI** pour ce faire :  
- via **Portainer** pour la partie purement conteneurisée,  
- via la stack **Prometheus/Grafana/Loki/AlertManager**,  
- Le produit dispose également d’une supervision **PSIN**.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en **AES‑256** et déposés sur :  
- le stockage objet **B3** du IaaS ministériel,  
- le stockage objet **Outscale SecNumCloud** (via la prestation qu'a le GTI sur le marché "Nuage Public"),  
- le stockage objet standard de **Google Cloud** (via la prestation qu'a le GTI sur le marché "Nuage Public").

---  

## 9. Sujets transverses  

| Sujet | Implémentation dans **agile‑infra** | Points d’attention |
|-------|-----------------------------------|-------------------|
| **Authentification** | Aucun login interne – accès via reverse‑proxy TLS avec certificats client (optionnel) | Gestion du cycle de vie des certificats |
| **Journalisation** | Logs conteneurs centralisés via **Loki** ; logs Ansible via `ansible.log` | Rotation des logs, conformité GDPR |
| **Monitoring** | Prometheus scrute les métriques `/metrics` des services ; Grafana dashboards pré‑configurés | Alertes seuils de latence, utilisation CPU/Memory |
| **Gestion des erreurs** | Handlers Ansible (`up the containers`) avec `failed_when` et `ignore_errors` | Notification d’échec via AlertManager |
| **API** | Backend expose API REST / JSON ; documentée via OpenAPI 3.0 (stockée dans repo) | Versioning de l’API, tests contractuels |
| **Sécurité des secrets** | `secrets.yml` chiffré, déchiffrement via variables CI (`SECRET_KEY`, `DECRYPT_PASSWORD`) | Rotation périodique des clés, audit d’accès CI |
| **CI/CD** | Pipeline GitLab unique (`run_recette`) | Ajout futur de tests de sécurité (SAST/DAST) |
| **Observabilité** | Traces distribuées via **Jaeger** (optionnel) | Corrélation logs/metrics/traces |

---  

## 10. Exigences de qualité  

| ID | Exigence | Scénario de validation |
|----|----------|--------------------------|
| Q‑01 | **Performance** – le temps de mise à jour doit être ≤ 5 min | Mesure du temps entre le commit et la disponibilité du service (script de test HTTP) |
| Q‑02 | **Sécurité** – les dumps de BD sont chiffrés AES‑256 | Vérifier le header du fichier dump (`openssl enc -d -aes-256-cbc`) |
| Q‑03 | **Maintenabilité** – le playbook doit passer l’`ansible-lint` sans warnings | Exécution du job CI `ansible-lint` |
| Q‑04 | **Opérabilité** – alertes de surcharge CPU (> 80 %) doivent être générées | Simuler charge via `stress-ng` et vérifier l’alerte dans AlertManager |
| Q‑05 | **Accessibilité** – conformité WCAG 2.1 AA pour l’interface front | Audit automatisé avec `axe-core` sur le front déployé |

---  

## 11. Risques et dettes techniques  

| Risque | Impact | Mesure corrective / mitigation |
|--------|--------|--------------------------------|
| **R1 – Secrets en clair dans le dépôt** | Violation de la confidentialité | Utiliser `git‑crypt` ou `ansible-vault`; interdiction de commit de fichiers non chiffrés |
| **R2 – Dépendance à une version unique de Docker‑Compose** | Blocage lors de mises à jour majeures | Définir une politique de mise à jour semver, tests de compatibilité en pré‑production |
| **R3 – Single point of failure du reverse‑proxy** | Indisponibilité du service | Déployer Nginx en HA (2 instances) avec keepalived ou équivalent |
| **R4 – Accès réseau limité au tenant ECO4** | Impossibilité de déployer en dehors du périmètre | Documenter les pré‑requis réseau, prévoir un environnement de test isolé |
| **R5 – Dette de tests unitaires côté application** | Régression fonctionnelle | Intégrer des tests automatisés dans le pipeline (JUnit, Jest) et faire du coverage > 80 % |

---  

## 12. Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **CI** | Continuous Integration – automatisation du build et des tests. |
| **CD** | Continuous Delivery/Deployment – automatisation du déploiement. |
| **IaC** | Infrastructure as Code – gestion de l’infrastructure via du code déclaratif. |
| **Playbook** | Fichier Ansible décrivant une série de tâches. |
| **Template Jinja2** | Fichier texte contenant des placeholders remplacés à l’exécution. |
| **Tenant** | Espace isolé dans un cloud OpenStack. |
| **D‑I‑C‑T** | Modèle de sécurité : Disponibilité, Intégrité, Confidentialité, Traçabilité. |
| **GTI** | Groupe Technique d’Infrastructure – équipe responsable du cloud interne. |

### 12.2 Décisions d’architecture (ADR)  

| ADR # | Décision | Date | Statut | Raison |
|-------|----------|------|--------|--------|
| ADR‑001 | Utiliser **Ansible** comme moteur d’orchestration IaC | 2025‑09‑12 | Adoptée | Offre un langage déclaratif simple, large communauté, intégration CI facile |
| ADR‑002 | Stocker les secrets dans **GitLab CI variables** et les déchiffrer en temps réel | 2025‑09‑15 | Adoptée | Evite le stockage persistant de secrets, conformité D‑I‑C‑T |
| ADR‑003 | Reverse‑proxy **Nginx** en paire load‑balanced | 2025‑10‑01 | Adoptée | Haute disponibilité, support TLS natif |
| ADR‑004 | Utiliser **Docker‑Compose** plutôt que Kubernetes pour ce périmètre | 2025‑10‑10 | Adoptée | Simplicité, faible volume de services, contraintes d’équipe |
| ADR‑005 | Sauvegardes chiffrées AES‑256 sur trois fournisseurs de stockage | 2025‑11‑05 | Adoptée | Redondance, conformité RGPD, résilience aux pannes fournisseurs |

---  

*Fin du Dossier d’Architecture Technique.*  