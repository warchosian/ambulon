# Dossier d’Architecture Technique (DAT) – **admin_ep**  
*(Modèle Arc42 – version générique, prête à être adaptée à tout projet similaire)*  

---  

## 1. Introduction et objectifs  

### 1.1 Vue d’ensemble fonctionnelle (C4 ‑ Level 1)  

```mermaid
graph TD
    A[Utilisateurs] -->|HTTPS| B[Web‑App (Tomcat 9 + Java 8)]
    B -->|JDBC| C[Base de données PostgreSQL]
    B -->|REST / HTTP| D[Service JORF (cron)]
    B -->|SMTP| E[Service de notification (mail)]
    B -->|HTTPS| F[Reverse‑proxy Nginx (load‑balanced)]
    F --> G[Infrastructure OpenStack – tenant *pnm3* (ECO4)]
```  

*Le système admin_ep permet aux acteurs de la tutelle (SPES, DG, opérateurs) de saisir, consulter et analyser les mandats des administrateurs d’établissements publics. Un moteur d’import automatisé récupère les données du JORF et alimente la base. Un service de monitoring signale les échéances de mandat.*

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif (qualité) | Raison métier / utilisateur |
|---|--------------------|------------------------------|
| 1 | **Performance** – temps de réponse < 2 s pour les recherches d’administrateurs | L’utilisateur doit obtenir rapidement les informations recherchées. |
| 2 | **Sécurité** – authentification Cerbère, chiffrement TLS, traçabilité des accès | Les données sont sensibles (mandats, pièces jointes). |
| 3 | **Maintenabilité** – architecture en couches, tests unitaires ≥ 80 % | Facilite l’évolution (nouveaux établissements, nouvelles règles). |
| 4 | **Accessibilité** – conformité WCAG 2.1 niveau AA pour les pages publiques | L’application doit être utilisable par tous les agents. |
| 5 | **Opérabilité** – supervision temps réel (Prometheus/Grafana) et alertes mail | Garantir la disponibilité du service (SLA = 99,5 %). |

---  

## 2. Parties prenantes  

| Rôle | Contact (exemple) | Attentes / Besoins |
|------|-------------------|--------------------|
| **Maîtrise d’ouvrage (MOA)** | SG / SPES – contact@spes.gouv.fr | Fonctionnalités métier, respect des délais, conformité réglementaire. |
| **Maîtrise d’œuvre (MOE)** | SG / DNUM / PNM3 – c.gilliard@developpement-durable.gouv.fr | Architecture claire, livrables de qualité, documentation. |
| **Prestataire (CGI)** | Chef de projet – c.arbogast@developpement-durable.gouv.fr | Implémentation, support technique, évolutions. |
| **Utilisateurs finaux** | Agents de tutelle, opérateurs | Accès rapide aux informations, notifications d’échéances, interface intuitive. |
| **RSSI** | sec.rssi@developpement-durable.gouv.fr | Sécurité des flux, conformité DICT / RGPD. |
| **Équipe de supervision (PSIN)** | supervision@psin.gouv.fr | Monitoring, alertes, rapports d’incident. |
| **Équipe de support** | assistance-adminep@developpement-durable.gouv.fr | Gestion des incidents, assistance aux usagers. |

---  

## 3. Contraintes  

### 3.1 Contraintes d’architecture  

| Type | Description |
|------|-------------|
| **Techniques** | Java 8, Spring / Struts 2, Vertigo, PostgreSQL 9.6 → 15, Tomcat 9, Nginx, Docker, GitLab CI, Maven 3, SonarQube, JUnit, Log4j2. |
| **Organisationnelles** | Respect du processus de validation des changements (ticketing JIRA), livrables versionnés, séparation Dev/Recette/Prod. |
| **Réglementaires** | DICT (déclaration d’incident), RGPD (données personnelles des administrateurs), exigences d’accessibilité (WCAG 2.1). |
| **Opérationnelles** | Haute disponibilité ≥ 99,5 % (load‑balancing Nginx, réplication PostgreSQL), sauvegardes quotidiennes chiffrées. |
| **Environnementales** | Hébergement sur le cloud interne **ECO4** (OpenStack), conformité aux exigences du ministère (PCI 2). |

### 3.2 Contraintes de sécurité – modèle D‑I‑C‑T  

| Dimension | Exigence |
|----------|----------|
| **Disponibilité** | Redondance Nginx × 2, réplication PostgreSQL, monitoring temps réel, plan de reprise d’activité (RTO ≤ 30 min). |
| **Intégrité** | Contrôle d’intégrité des scripts d’import JORF (SHA‑256), transactions ACID, contraintes d’unicité (PK/FK). |
| **Confidentialité** | TLS 1.2+ sur tous les flux, chiffrement AES‑256 des dumps, masquage des champs sensibles (PII). |
| **Traçabilité** | Log4j2 + centralisation (ELK), journalisation des accès (authentification Cerbère), auditabilité (DI​CT). |

---  

## 4. Contexte et périmètre  

### 4.1 Contexte métier  

- **Partenaires fonctionnels** : SPES, Direction Générale de la Tutelle, opérateurs de saisie, services juridiques.  
- **Objectif métier** : Centraliser les listes des membres des conseils d’administration des établissements publics du MTES‑MCT, assurer la traçabilité des mandats et générer des alertes d’échéance.  

### 4.2 Contexte technique  

| Interface | Protocole / Fréquence | Type |
|-----------|----------------------|------|
| **Front‑office** | HTTPS (REST/HTML) | Utilisateur final (navigateur) |
| **Import JORF** | HTTPS (GET) – exécution cron (quotidienne) | Service d’alimentation automatisée |
| **Base de données** | JDBC (PostgreSQL) | Persistance |
| **Notification mail** | SMTP (TLS) | Service d’envoi d’alertes |
| **Supervision** | HTTP (Prometheus scrape) – 30 s | Monitoring |
| **Sauvegarde** | S3‑compatible (B3, Outscale, GCS) – quotidien | Stockage des dumps chiffrés |

---  

## 5. Stratégie de solution  

### 5.1 Modèles de conception / décisions architecturales majeures  

| Décision | Motif | Alternatives rejetées |
|----------|-------|------------------------|
| **Architecture en couches (MVC + Service + DAO)** | Séparation claire des responsabilités, testabilité. | Monolithe sans découpage, micro‑services (trop de complexité pour ce périmètre). |
| **Utilisation du pattern Factory & Decorator** (ex : `ActifDecorator`) | Extensibilité des objets métier (ajout de comportements sans modifier les classes existantes). | Héritage direct (rigide). |
| **Containerisation Docker + orchestration via Docker‑Compose (dev) / OpenStack (prod)** | Portabilité, réplication d’environnements, alignement avec la politique « containérisation ». | Installation manuelle sur VM (non‑reproductible). |
| **CI/CD avec GitLab CI, Maven, SonarQube** | Automatisation du build, qualité code, déploiement continu en pré‑prod. | Scripts Bash ad‑hoc (maintenance lourde). |
| **Reverse‑proxy Nginx en paire (load‑balancing)** | Haute disponibilité front‑end, terminaison TLS. | Apache HTTP (moins performant pour le load‑balancing). |
| **Sauvegarde chiffrée AES‑256 + multi‑cible (B3, Outscale, GCS)** | Redondance géographique, conformité sécurité. | Sauvegarde locale uniquement (risque perte). |

### 5.2 Environnement technologique  

| Côté serveur | Technologie / Version |
|--------------|----------------------|
| **Langage** | Java 8 (OpenJDK) |
| **Framework web** | Struts 2 + Vertigo (MVC) |
| **Persistance** | JPA /Hibernate, PostgreSQL 9.6 → 15 |
| **Serveur d’applications** | Tomcat 9.0.8 |
| **Reverse‑proxy** | Nginx 1.20 (load‑balancing) |
| **Conteneur** | Docker 20.x, Docker‑Compose (dev) |
| **Orchestration prod** | OpenStack (ECO4) – tenant *pnm3* |
| **CI/CD** | GitLab CI, Maven, SonarQube, JUnit, Jacoco |
| **Supervision** | Prometheus + Grafana + AlertManager |
| **Logging** | Log4j2 + ELK (Filebeat → Logstash → Kibana) |
| **Sécurité** | TLS 1.2+, Cerbère SSO, OAuth 2.0 (future), HashiCorp Vault (secrets) |
| **Sauvegarde** | Scripts pg_dump + OpenSSL AES‑256, stockage B3, Outscale SecNumCloud, Google Cloud Storage |

### 5.3 Forge logicielle  

- **Gestion de code** : GitLab (repo mono‑module).  
- **Gestion des dépendances** : Maven (pom.xml multi‑module).  
- **Qualité** : SonarQube (analyse statique), JaCoCo (coverage).  
- **Tests** : JUnit 5, Mockito, integration tests (Docker‑Compose).  
- **Déploiement** : GitLab‑Runner → Docker image → registre Docker interne → déploiement via scripts Ansible sur OpenStack.  

---  

## 6. Vue en Briques (C4 ‑ Level 2)  

```mermaid
graph TD
    subgraph "Infrastructure"
        N1[Nginx LB] 
        N2[Nginx LB]
        DB[(PostgreSQL Cluster)]
        S1[Prometheus] 
        S2[Grafana] 
    end
    subgraph "Application"
        A1[admin_ep‑web (Tomcat)] 
        A2[admin_ep‑batch (import JORF)] 
        A3[admin_ep‑mail (notification)] 
    end
    N1 --> A1;
    N2 --> A1;
    A1 --> DB;
    A2 --> DB;
    A3 --> DB;
    A1 --> S1;
    A2 --> S1;
    A3 --> S1;
    S1 --> S2
```

**Description des conteneurs principaux**  

| Conteneur | Rôle | Principaux artefacts |
|-----------|------|----------------------|
| `admin_ep‑web` | Application web (Struts 2) – interface utilisateur, actions, services. | `admin_ep‑web‑*.war` |
| `admin_ep‑batch` | Processus batch (cron) : récupération JORF, parsing, mise à jour DB. | `admin_ep‑batch‑*.jar` |
| `admin_ep‑mail` | Service d’envoi de mails (mandats proches d’échéance). | `admin_ep‑mail‑*.jar` |
| `PostgreSQL` | Persistance des référentiels, mandats, logs d’import. | Schéma `integration`, `baseadmin`. |
| `Nginx` | Reverse‑proxy, TLS termination, load‑balancing (2 instances). | Config `adminep.xml`. |
| `Prometheus / Grafana` | Collecte métriques (JVM, Tomcat, PostgreSQL) et visualisation. | Exporters `jmx_exporter`, `postgres_exporter`. |

---  

## 7. Vue Exécution (Scénarios critiques)  

### 7.1 Scénario 1 – Recherche d’un administrateur (session utilisateur)  

```mermaid
sequencediagram;
    participant U as Utilisateur;
    participant B as Browser;
    participant N as Nginx LB;
    participant W as admin_ep‑web (Tomcat)
    participant DB as PostgreSQL;
    participant L as Log4j2;
    U->>B: Ouvre URL https://adminep.e2.rie.gouv.fr/
    B->>N: GET /admin_ep/
    N->>W: Forward request (TLS terminated)
    W->>W: Authentification Cerbère (filter)
    W->>DB: SELECT * FROM administrateur WHERE nom LIKE ?
    DB-->>W: Résultat (liste)
    W->>L: Log access (user, action)
    W->>B: HTML + JSP (liste résultats)
    B->>U: Affichage
```

*Validations* : temps de réponse < 2 s, logs d’accès traçables, contrôle d’accès Cerbère.  

### 7.2 Scénario 2 – Import automatisé JORF (batch)  

```mermaid
sequencediagram;
    participant S as Scheduler (cron)
    participant B as admin_ep‑batch;
    participant J as JORF HTTP endpoint;
    participant DB as PostgreSQL;
    participant L as Log4j2;
    participant M as Prometheus;
    S->>B: Lancement (00_00 UTC)
    B->>J: GET /jorf/diff.tar.gz;
    J-->>B: Flux XML;
    B->>B: Parsing (ArticleAnalyser, Steps…)
    B->>DB: INSERT / UPDATE (transaction ACID)
    DB-->>B: Confirmation;
    B->>L: Log import (niveau INFO)
    B->>M: Push métriques (nb articles importés)
```

*Points de contrôle* : intégrité du fichier (SHA‑256), transaction DB, métriques d’import.  

### 7.3 Scénario 3 – Notification d’échéance de mandat  

```mermaid
sequencediagram;
    participant C as Cron (daily 06_00)
    participant S as admin_ep‑mail;
    participant DB as PostgreSQL;
    participant M as Mail server (SMTP TLS)

    C->>S: Lancement job;
    S->>DB: SELECT mandats WHERE date_fin BETWEEN now() + 30d AND now()
    DB-->>S: Liste de mandats;
    loop for each mandat;
        S->>M: SEND mail (to référent)
        M-->>S: ACK;
    end
    S->>S: Log notification (Log4j2)
```

*Vérifications* : mails délivrés, logs d’envoi, métriques de taux de succès.  

---  

## 8. Vue Déploiement *(section standardisée)*  

```markdown
### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | Docker‑Compose local | 1 × Tomcat, 1 × PostgreSQL, 2 × Nginx | 127.0.0.1 | Accès dev uniquement, données factices. |
| Recette       | OpenStack ECO4 (tenant *pnm3*) | 2 × Tomcat, 1 × PostgreSQL HA, 2 × Nginx LB | VLAN 10 | Jeux de données réalistes, tests d’intégration. |
| Production    | OpenStack ECO4 (tenant *pnm3*) | 4 × Tomcat, 2 × PostgreSQL HA, 2 × Nginx LB | VLAN 20 | HA, sauvegardes quotidiennes, monitoring complet. |
```

```mermaid
graph TD
    A[Nginx] -- B[Application]
    B -- C[Base de données]
    B -- D[Autres services]
```

### Supervision  
Le produit est supervisé via le système standard du GTI pour ce faire :  

- via **Portainer** pour la partie purement conteneurisée,  
- via la stack **Prometheus/Grafana/Loki/AlertManager**,  
- Le produit dispose également d'une supervision **PSIN**.  

### Sauvegardes  
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES‑256 et déposés sur :  

- le stockage objet **B3** du IaaS ministériel,  
- le stockage objet **Outscale SecNumCloud** (via la prestation qu’a le GTI sur le marché "Nuage Public"),  
- le stockage objet standard de **Google Cloud** (via la prestation qu’a le GTI sur le marché "Nuage Public").  

---  

## 9. Sujets transverses  

| Sujet | Implémentation dans admin_ep |
|-------|------------------------------|
| **Authentification** | Filtre `SecurityFilter` (Cerbère SSO) – jeton JWT en cours de migration. |
| **Journalisation** | Log4j2 → ELK ; pattern MDC (user, session, request‑id). |
| **Monitoring** | Exporters JMX (Tomcat), PostgreSQL exporter, alertes (mandat proche, downtime). |
| **Gestion des erreurs** | `ErrorHandler` central, pages d’erreur personnalisées (error_*.jsp). |
| **API** | Struts actions exposent des endpoints REST / JSON (ex : `/api/admins/search`). |
| **Sécurité des données** | Chiffrement des dumps, stockage des secrets dans Vault, contrôle d’accès RBAC (`Roles.java`). |
| **CI/CD** | Pipelines GitLab : build → test → Sonar → Docker image → déploiement (staging → prod). |
| **Documentation** | Wiki intégrée (templates `*.ftl`), génération Javadoc, ADRs versionnées dans `/adr`. |
| **Internationalisation** | `I18nResourcesInitializer` charge les bundles (`messages_*.properties`). |

---  

## 10. Exigences de qualité  

| Exigence (qualité) | Scénario de validation | Critère d’acceptation |
|---------------------|------------------------|-----------------------|
| **Performance** | Test de charge (JMeter) – 200 utilisateurs simultanés sur la recherche. | Temps moyen < 2 s, p99 < 4 s. |
| **Sécurité** | Scan OWASP ZAP + test d’intrusion. | Aucun CVE ≥ 7, aucune fuite d’information. |
| **Maintenabilité** | Couverture de code unitaires > 80 % (JaCoCo). | Rapport JaCoCo ≥ 80 %. |
| **Accessibilité** | Audit axe‑core (WCAG 2.1). | Niveau AA atteint sur les pages critiques. |
| **Opérabilité** | Simulation de panne du nœud DB, bascule automatique. | RTO ≤ 30 min, aucune perte de transaction. |
| **Traçabilité** | Vérification des logs d’accès (Log4j2). | Chaque requête possède un `request-id` unique. |
| **Sauvegarde / Restauration** | Test de restauration d’un dump chiffré sur un serveur de test. | Restauration complète en < 15 min, données cohérentes. |

---  

## 11. Risques et Dettes techniques  

| Risque / Dette | Impact | Mesure corrective / Mitigation |
|----------------|--------|--------------------------------|
| **Obsolescence du JDK 8** | Support limité, vulnérabilités non corrigées. | Plan de migration vers JDK 11/17 (road‑map 2025). |
| **Dépendance à Struts 2 (fin de vie)** | Risque de sécurité, manque de nouvelles fonctionnalités. | Étude de migration vers Spring Boot + Spring MVC (proof‑of‑concept 2024). |
| **Scripts de migration DB manuels** | Possibles incohérences entre environnements. | Automatiser les migrations avec Flyway/Liquibase, versionner les scripts. |
| **Charge du parsing JORF** (gros volumes) | Saturation CPU, latence du batch. | Optimiser le parser (streaming XML, parallélisation), mettre en place du scaling horizontal. |
| **Gestion des secrets dans les fichiers** | Risque de fuite. | Centraliser dans HashiCorp Vault, rotation automatisée. |
| **Déploiement manuel en prod** | Erreurs humaines, temps d’arrêt. | Introduire Helm/Ansible pour le déploiement automatisé sur OpenStack. |
| **Sauvegarde unique sur un seul site** | Perte de données en cas de sinistre. | Ajouter réplication multi‑site (B3 + GCS). |

---  

## 12. Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **EP** | Établissement Public (sous tutelle du MTES‑MCT). |
| **JORF** | Journal Officiel de la République Française – source officielle des actes législatifs. |
| **Cerbère** | Système d’authentification unique (SSO) du ministère. |
| **DICT** | Déclaration d’Incidents de Sécurité de l’Information. |
| **RGPD** | Règlement Général sur la Protection des Données. |
| **ECO4** | Cloud interne du ministère (OpenStack). |
| **PSIN** | Plateforme de Supervision Inter‑Nationale. |
| **ADR** | Architecture Decision Record – document de décision d’architecture. |
| **DAO** | Data Access Object – couche d’accès aux données. |
| **DTO** | Data Transfer Object – objet de transfert de données. |
| **WCAG** | Web Content Accessibility Guidelines. |
| **CI/CD** | Intégration Continue / Déploiement Continu. |
| **HA** | High Availability (haute disponibilité). |
| **RTO** | Recovery Time Objective – temps maximal de reprise. |
| **RPO** | Recovery Point Objective – perte maximale de données admissible. |

### 12.2 Décisions d’architecture (ADRs)  

| # | Décision | Contexte | Résultat |
|---|----------|----------|----------|
| **ADR‑001** | **Utilisation de Maven multi‑module** | Besoin d’une build unifiée pour les modules `adminep‑database`, `adminep‑web`, `adminep‑deployment`. | Gestion simplifiée des dépendances, versionnage cohérent. |
| **ADR‑002** | **Conteneurisation Docker** | Nécessité d’un environnement reproductible (dev/recette/prod). | Dockerfiles créés, images stockées dans registre interne. |
| **ADR‑003** | **Reverse‑proxy Nginx en paire** | Exigence de haute disponibilité front‑end. | Load‑balancing round‑robin, TLS termination, health‑checks. |
| **ADR‑004** | **Pattern MVC + Service + DAO** | Complexité fonctionnelle (gestion mandats, import JORF). | Séparation claire, testabilité accrue. |
| **ADR‑005** | **Sauvegarde chiffrée AES‑256 + stockage multi‑cible** | Conformité sécurité et continuité d’activité. | Scripts automatisés, tests de restauration mensuels. |
| **ADR‑006** | **Monitoring Prometheus/Grafana** | Besoin de visibilité temps réel et alertes. | Exporters configurés, dashboards opérationnels. |
| **ADR‑007** | **Authentification via Cerbère** | Politique ministérielle d’authentification unique. | Filtre `SecurityFilter` intégré, mapping des rôles. |
| **ADR‑008** | **Gestion de la dette Struts 2** | Struts 2 en fin de vie, risque sécurité. | Plan de migration à Spring Boot d’ici 2025. |

---  

*Ce DAT a été rédigé en suivant strictement le modèle Arc42, avec un niveau de détail suffisant pour être exploité par les développeurs, les exploitants, la MOA et le RSSI. Il reste évolutif : chaque nouvelle version de l’application pourra être enrichie d’ADRs supplémentaires, de scénarios de test et d’indicateurs de performance.*  