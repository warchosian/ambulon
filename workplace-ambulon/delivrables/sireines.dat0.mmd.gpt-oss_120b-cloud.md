# Dossier d’Architecture Technique (DAT) – SIREINES  
**Projet :** SIREINES – Répertoire d’experts et spécialistes scientifiques et techniques  
**Version du DAT :** 1.0 – 2024‑03‑15  

---

## 1. Introduction et objectifs  

### 1.1 Vue d’ensemble fonctionnelle (C4 ‑ Level 1)  

```mermaid
graph TD
    A[Utilisateurs (agents, experts, administrateurs)] -->|Utilise| B[SIREINES Web App]
    B -->|Accède aux données| C[(PostgreSQL DB)]
    B -->|Génère des rapports| D[BIRT Reporting Engine]
    B -->|Communique avec| E[GitLab CI / Maven Repository]
    B -->|Expose| F[API Struts2 / Vertigo (recherche, import/export)]
```

> **SIREINES** est une application web métier qui centralise les demandes de qualification d’agents, les soumet aux comités de domaine, conserve les avis et génère des rapports de suivi.  

### 1.2 Objectifs de qualité orientés utilisateur  

| # | Objectif | Motivation utilisateur |
|---|----------|------------------------|
| Q1 | **Performance** – temps de réponse < 2 s pour les écrans de recherche | L’utilisateur doit pouvoir consulter rapidement les dossiers |
| Q2 | **Sécurité** – conformité D‑I‑C‑T (Disponibilité, Intégrité, Confidentialité, Traçabilité) | Protection des données personnelles des experts (DACP) |
| Q3 | **Maintenabilité** – couverture de tests unitaires ≥ 80 % & documentation à jour | Réduction du coût de l’évolution fonctionnelle |
| Q4 | **Accessibilité** – conformité WCAG 2.1 AA | Garantir l’accès aux agents en situation de handicap |
| Q5 | **Opérabilité** – monitoring continu + alertes SLA ≤ 5 min d’indisponibilité | Assurer la continuité du service public |

---

## 2. Parties prenantes  

| Rôle | Personne / Service | Contact | Attentes principales |
|------|----------------------|---------|---------------------|
| **MOA** | CGDD / DRI / AST4 (Zémour Pascal) | Pascal.Zemour@developpement-durable.gouv.fr | Fonctionnalités métier, conformité CNIL, livrables documentés |
| **MOE** | Klee Group (ex‑prestataire) – maintenant équipes internes DNUM/PNM3 | Vincent.Letrouit@developpement-durable.gouv.fr | Qualité du code, respect des standards Java / Spring, alignement CI/CD |
| **Exploitation** | DSN / INFRA (ECO4 IaaS) | infra‑ops@eco4.gouv.fr | Disponibilité, sauvegardes, supervision (Prometheus/Grafana) |
| **Utilisateurs finaux** | Agents, experts, membres de comités | support‑sireines@dgfip.fr | Accès simple, recherche efficace, export de rapports |
| **Sécurité / DPO** | CGDD / DPO | dpo@cgdd.gouv.fr | Confidentialité, traçabilité, auditabilité |
| **Support** | Portail‑support DIN | support‑din@din.gouv.fr | Gestion des incidents, tickets (Cerbère) |

---

## 3. Contraintes  

| Type | Contraintes |
|------|--------------|
| **Techniques** | - Java 8, Tomcat 7 (Docker‑image `tomcat:7.0.108-jdk8`) <br> - PostgreSQL 14 (image `postgres:14.1‑alpine`) <br> - BIRT 4.3 pour les rapports <br> - Maven 3.6+ pour le build <br> - GitLab CI pour l’intégration continue |
| **Organisationnelles** | - Processus de mise en production via `merge request` (recette → pre‑prod → prod) <br> - Validation CNIL (déclaration 29/09/2014) <br> - Gestion des secrets via `.env` et variables CI |
| **Réglementaires** | - RGPD : traçabilité, droit d’accès, archivage 5 ans (DUA) <br> - CNIL : conformité à la déclaration n°1034232 <br> - Sécurité D‑I‑C‑T (voir § 4) |
| **Opérationnelles** | - Temps de mise à jour cible ≤ 30 min (rolling‑update Docker) <br> - Sauvegarde quotidienne des bases + dumps chiffrés AES‑256 (GTI) |

---

## 4. Contexte et périmètre  

### 4.1 Contexte métier  

SIREINES sert le **CGDD / DRI / AST4** à :  

* Recueillir les demandes de qualification d’agents.  
* Piloter les comités de domaine (validation, avis).  
* Produire des statistiques et des rapports (BIRT).  
* Garantir la traçabilité des décisions (audit).  

### 4.2 Contexte technique  

| Élément | Technologie / Interface |
|---------|------------------------|
| **Application** | Java /J2EE, Spring Core, Struts2, Vertigo (search), BIRT, FreeMarker (FTL) |
| **Base de données** | PostgreSQL 14, scripts SQL (install / alter / drop) |
| **Conteneurisation** | Docker (Tomcat + PostgreSQL + pgAdmin) – déploiement via `docker‑compose.yml` |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`) → Maven → Docker image |
| **Monitoring** | Prometheus + Grafana + Alertmanager (stack GTI) |
| **Supervision** | Portainer (containers), PSIN (supervision applicative) |
| **Sauvegardes** | Dumps chiffrés (AES‑256) → stockage objet B3, SecNumCloud, Google Cloud |
| **Authentification** | Config XML `sireines‑auth‑config.xml` (roles R_ADMIN) – Intégration possible SSO (future) |
| **Journalisation** | Log4j 2, fichiers rotation, agrégation via GTI |
| **Gestion des secrets** | `.env` (Docker) + GitLab CI variables (non versionnées) |

---

## 5. Stratégie de solution  

| Décision | Raison | Alternatives évaluées |
|----------|--------|-----------------------|
| **Architecture 3‑tiers** (Web / App / DB) | Séparation claire des responsabilités, facilité de scaling | Monolithique sans conteneur (rejeté – déploiement lourd) |
| **Docker + Docker‑Compose** | Reproductibilité, isolation, versionnage du stack | VM‑based (coût + complexité) |
| **Maven + Assembly** | Build fiable, génération d’artefacts (`sireines‑web.war`) | Gradle (non‑maîtrisé) |
| **Spring + Struts2** | Héritage du code existant, compatibilité Java 8 | Migration vers Spring Boot (à moyen terme) |
| **BIRT** pour les rapports | Outil déjà intégré, support du format BIRT | JasperReports (coût de migration) |
| **Vertigo Search (Elasticsearch Embedded)** | Recherche full‑text déjà implémentée | Elastic Cloud (future évolutif) |
| **Monitoring GTI (Prometheus/Grafana)** | Stack déjà déployée dans l’infrastructure GTI | New Relic (coût) |
| **CI avec GitLab** | Conformité aux pratiques internes | Jenkins (déjà en place mais moins intégré) |

---

## 6. Vue en Briques (C4 ‑ Level 2)

```mermaid
graph TD
    subgraph "Docker‑Compose"
    A[Tomcat Container (sireines‑app)] --> B[PostgreSQL Container (sireines‑db)]
    A --> C[pgAdmin Container (sireines‑pgadmin)]
    end
    A --> D[War: sireines‑web.war]
    D -->|Struts2 / Spring| E[Business Logic (Java packages i2.application.sireines.*)]
    E -->|Vertigo Search| F[Embedded Elasticsearch]
    E -->|BIRT| G[Report Engine (BIRT 4.3)]
    B -->|SQL scripts| H[Schema (sireines)] 
    B -->|Dump / Restore| I[Backup Store (B3 / SecNumCloud / GCP)]
    C -->|UI| J[pgAdmin UI]
    subgraph "External"
    K[GitLab CI] -->|Artifacts| A;
    L[Prometheus / Grafana] -->|Metrics| A;
    M[Portainer] -->|Container Mgmt| A;
    end
```

* **Conteneur Tomcat** : exécute le WAR `sireines‑web.war`.  
* **Conteneur PostgreSQL** : héberge la base `sireines`.  
* **Conteneur pgAdmin** : interface d’administration DB.  
* **BIRT** : rend les rapports au format PDF/HTML.  
* **Vertigo Search** : moteur de recherche intégré (Elasticsearch embedded).  

---

## 7. Vue d’exécution (scénarios critiques)  

### 7.1 Scénario 1 – Soumission d’une demande de qualification  

| Étape | Action | Composant | Technologie |
|------|--------|-----------|-------------|
| 1 | L’utilisateur remplit le formulaire Struts2 | `sireines-web` (controller `DossierRechercheAction`) | Struts2, FreeMarker |
| 2 | Validation côté serveur | `CommonServices` (méthodes de validation) | Java |
| 3 | Persistance du dossier | DAO `dossiersDao.ksp` | Vertigo + PostgreSQL |
| 4 | Indexation pour recherche | `SearchManagerInitializer` (re‑index) | Vertigo + Embedded ES |
| 5 | Envoi de notification mail | `CommonServices.sendMail` | JavaMail (SMTP) |
| 6 | Retour UI avec message de succès | JSP/FTL | Struts2 UI |

### 7.2 Scénario 2 – Génération d’un rapport BIRT  

| Étape | Action | Composant | Technologie |
|------|--------|-----------|-------------|
| 1 | L’utilisateur clique “Export PDF” | `BirtManager` (interface) | BIRT API |
| 2 | Le manager charge le design `.rptdesign` depuis `/sireines‑web/src/main/resources/...` | BIRT Engine | BIRT 4.3 |
| 3 | Le moteur interroge la DB via DAO | Vertigo + PostgreSQL | SQL |
| 4 | Le rapport est rendu en PDF et transmis au navigateur | HTTP / Servlet | Tomcat |
| 5 | Le fichier PDF est archivé (optionnel) | `/opt/app/backups` | Filesystem + AES‑256 |

### 7.3 Scénario 3 – Mise à jour de version (pipeline CI)  

| Étape | Action | Composant | Technologie |
|------|--------|-----------|-------------|
| 1 | Merge request `recette → preprod` (ou `preprod → prod`) | GitLab | Git |
| 2 | GitLab CI compile le projet (`mvn clean package`) | Maven | Maven |
| 3 | Docker image `sireines‑app` est construite (`docker build`) | Dockerfile | Docker |
| 4 | Déploiement via `docker-compose up -d` | Docker‑Compose | Docker |
| 5 | Tests fonctionnels automatisés (Selenium) | GitLab CI | Selenium |
| 6 | Monitoring déclenche alertes si temps de réponse > 2 s | Prometheus + Alertmanager | Prometheus |

---

## 8. Vue Déploiement *(section standardisée – NE PAS MODIFIER)*  

```markdown
### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | À compléter | À compléter | À compléter | À compléter |
| Recette       | À compléter | À compléter | À compléter | À compléter |
| Production    | À compléter | À compléter | À compléter | À compléter |

### Infrastructure
Le produit est hébergé sur le cloud interne ECO4 basé sur Openstack, dans le tenant 'pnm3' du département.  
Le reverse-proxy Nginx du schéma ci-dessous est en fait une paire de Nginx load-balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx] -- B[Application]
    B -- C[Base de données]
    B -- D[Autres services]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :
- via Portainer pour la partie purement conteneurisée,
- via la stack Prometheus/Grafana/Loki/AlertManager,
- Le produit dispose également d'une supervision PSIN.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
- le stockage objet B3 du IaaS ministériel,
- le stockage objet Outscale SecNumCloud (via la prestation qu'a le GTI sur le marché "Nuage Public"),
- le stockage objet standard de Google Cloud (via la prestation qu'a le GTI sur le marché "Nuage Public").
```

---

## 9. Sujets transverses  

| Sujet | Description | Implémentation actuelle | Évolution souhaitée |
|-------|-------------|------------------------|---------------------|
| **Authentification** | Gestion des rôles (R_ADMIN) via `sireines‑auth‑config.xml` | Auth locale (login/password) | SSO (CAS / OpenID Connect) |
| **Journalisation** | Log4j2 configuré (fichier, rotation) | `log4j.xml` | Centralisation Syslog / ELK |
| **Monitoring** | Métriques JVM, HTTP, DB exposées à Prometheus | `portainer`, `Prometheus` | Dashboard dédié SIREINES (latence, taux d’erreur) |
| **Gestion des erreurs** | `ErrorHandler` Struts2 → page `application-error.jsp` | Page générique | Enrichir avec trace ID (correlation) |
| **API** | Struts2 actions exposés (REST‑like) | `sireines‑web/src/main/java/.../controller/*` | Documenter OpenAPI, sécuriser OAuth2 |
| **Sécurité des données** | Chiffrement des dumps, RGPD | Scripts backup GTI (AES‑256) | chiffrement au repos (Transparent Data Encryption) |
| **CI/CD** | `.gitlab-ci.yml` compile, package, push Docker | Build Maven → Docker | Déploiement blue‑green, canary |
| **BIRT Reporting** | Templates `.rptdesign` | `sireines‑talend/reports/*.rptdesign` | Migration vers JasperReports (future) |

---

## 10. Exigences de qualité (tableau scénarios de validation)  

| ID | Exigence | Scénario de test | Critère d’acceptation |
|----|----------|-------------------|------------------------|
| **Q‑PERF‑01** | Temps de réponse < 2 s pour la recherche de dossiers | Simuler 100 concurrent users via JMeter | 95 % des requêtes ≤ 2 s |
| **Q‑SEC‑01** | Confidentialité des données personnelles | Vérifier chiffrement des dumps, accès DB | Aucun dump en clair, accès DB limité aux rôles |
| **Q‑MAINT‑01** | Couverture tests unitaires ≥ 80 % | Exécuter `mvn test` | Rapport JaCoCo ≥ 80 % |
| **Q‑ACC‑01** | Conformité WCAG 2.1 AA | Audit axe‑core sur les pages principales | Score axe ≥ 90 % |
| **Q‑OP‑01** | Disponibilité ≥ 99,5 % (SLA) | Simuler panne du container DB, vérifier redémarrage auto | Temps d’indisponibilité < 5 min |
| **Q‑TRACE‑01** | Traçabilité des actions critiques | Vérifier logs d’audit (login, modifications) | Log contenant `userId`, `timestamp`, `actionId` |
| **Q‑SCAL‑01** | Scalabilité horizontale du web‑app | Ajouter 2 instances Tomcat via compose | Le load‑balancer répartit le trafic, aucune régression fonctionnelle |

---

## 11. Risques et dettes techniques  

| Risque / Dette | Impact | Probabilité | Mesure corrective |
|----------------|--------|-------------|--------------------|
| **R‑1 :