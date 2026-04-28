# 📄 Cahier des Spécifications Techniques (CST) – **admin_ep**  
**Projet** : admin_ep – Administration des établissements publics (MTES‑MCT)  
**Version CST** : 1.0 – 2024‑04‑27  

---

## 1. Introduction & Contexte Qualité  

| Élément | Description |
|---------|-------------|
| **Objectifs de qualité** | • Garantir la disponibilité et l’intégrité des données d’administration ; <br>• Assurer la conformité aux exigences de sécurité (RGPD, DICT) ; <br>• Offrir une expérience utilisateur fluide (temps de réponse < 2 s, ergonomie ≥ 4/5). |
| **Contexte métier** | Application de saisie, de consultation et d’analyse des mandats des administrateurs d’établissements publics sous tutelle du ministère. <br>Flux d’alimentation automatique depuis le JORF, notifications d’échéance, recherche plein‑texte. |
| **Contexte technique** | • **Back‑end** : Java 8, Struts 2, Vertigo, Spring‑Boot (modules *boot*). <br>• **Serveur d’applications** : Tomcat 9.0.8 (migration prévue → Tomcat 10, PostgreSQL 15). <br>• **Base de données** : PostgreSQL 9.6.11 (schéma *integration*). <br>• **CI/CD** : Maven, SonarQube, JUnit, Selenium, OWASP‑ZAP. |
| **Références fonctionnelles (CCF)** | Voir tableau **[Matrice CCF ↔ Qualité]** (section 3.9). |
| **Méthodologie d’évaluation** | • **Mesurabilité** : chaque sous‑caractéristique possède une métrique quantitative.<br>• **Pondération** : les priorités métier (Fiabilité = 30 %, Sécurité = 25 %, Performance = 15 %, etc.).<br>• **Outils** : SonarQube, JMeter, New‑Relic, Prometheus‑Grafana, OWASP‑ZAP, Snyk. |

---

## 2. Modèle de qualité ISO / IEC 25010 (2023)

```
┌─────────────────────────────────────┐
│   QUALITÉ DU PRODUIT LOGICIEL       │
└─────────────────────────────────────┘
        │  │  │  │  │  │  │  │
   ┌────┘  │  │  │  │  │  │  └─────┐
   ▼       ▼  ▼  ▼  ▼  ▼  ▼       ▼
Aptitude   Performance   Compatibilité   Utilisabilité   Fiabilité   Sécurité   Maintenabilité   Portabilité
fonctionnelle
```

| Caractéristique | Sous‑caractéristiques (31) |
|-----------------|----------------------------|
| **Aptitude fonctionnelle** | Complétude, Exactitude, Adéquation |
| **Performance efficacité** | Comportement temporel, Utilisation des ressources, Capacité |
| **Compatibilité** | Cohérence, Interopérabilité |
| **Utilisabilité** | Appréhensibilité, Apprenabilité, Opérabilité, Esthétique, Accessibilité |
| **Fiabilité** | Maturité, Disponibilité, Tolérance aux fautes, Récupérabilité |
| **Sécurité** | Confidentialité, Intégrité, Non‑répudiation, Responsabilité, Authenticité |
| **Maintenabilité** | Modularité, Réutilisabilité, Analysabilité, Modifiabilité, Testabilité |
| **Portabilité** | Adaptabilité, Installabilité, Remplaçabilité |

---

## 3. Spécifications détaillées par caractéristique  

> **Notation** : chaque sous‑caractéristique est décrite par : (1) Métrique, (2) Objectif (seuil accepté), (3) Méthode de vérification.

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Complétude fonctionnelle** | % de CCF implémentées (ex : saisie, auto‑aliment, recherche, notification) | **≥ 95 %** | Mapping CCF ↔ modules (tableau 3.9) + revue d’exigences |
| **Exactitude fonctionnelle** | Taux d’erreurs de traitement (défauts / KLOC) sur les fonctions critiques | **≤ 0,5 %** | Tests unitaires + tests d’intégration automatisés |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) sur pertinence des écrans | **≥ 4/5** | Tests d’acceptation (UAT) & questionnaire post‑déploiement |

### 3.2 Performance & efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Comportement temporel** | Temps de réponse 95ᵉ percentile (ms) sur les API principales (search, mandat, admin) | **≤ 2000 ms** | JMeter / New‑Relic sous charge 100 utilisateurs |
| **Utilisation des ressources** | CPU % / RAM % moyen en charge nominale | **CPU ≤ 55 %**, **RAM ≤ 70 %** | Prometheus‑Grafana, tests de montée en charge |
| **Capacité** | Nombre d’utilisateurs concurrents supportés sans dégradation (> 95 % du SLA) | **≥ 150 utilisateurs** | Test de charge progressif jusqu’à 200 users |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Cohérence** | Conformité aux standards UI (Bootstrap 4, WCAG 2.1) – check‑list | **100 %** | Analyse manuelle + outils d’audit (axe‑core) |
| **Interopérabilité** | Nombre de formats d’échange supportés (JSON, XML, CSV) | **≥ 3** (REST JSON, SOAP XML, CSV export) | Tests d’API + validation schémas |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Appréhensibilité** | Temps moyen de prise en main (h) – test utilisateur | **≤ 0,5 h** | Sessions de formation de 30 min + questionnaire |
| **Apprenabilité** | % de tâches réussies sans aide (scenario “Créer mandat”) | **≥ 90 %** | Tests d’usabilité avec panel de 10 personnes |
| **Opérabilité** | Nombre moyen de clics pour créer un administrateur | **≤ 5 clics** | Analyse de flux UI (Google Analytics) |
| **Esthétique** | Score SUS (System Usability Scale) | **≥ 68/100** | Questionnaire SUS post‑déploiement |
| **Accessibilité** | Conformité WCAG 2.1 niveau AA | **Oui** | Outils axe‑core, WAVE |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Maturité** | Densité de défauts (défauts/KLOC) en production | **≤ 0,2** | Système de suivi JIRA, rapports mensuels |
| **Disponibilité** | % de disponibilité (Uptime) – calcul sur 30 jours | **≥ 99,7 %** (≈ 7 h 15 min d’arrêt max) | Monitoring New‑Relic, alertes SLA |
| **Tolérance aux fautes** | Temps de récupération (RTO) après incident | **≤ 5 min** | Tests de bascule (failover DB) |
| **Récupérabilité** | Point de récupération (RPO) – perte de données maximale | **≤ 5 min** | Sauvegardes incrémentielles + tests de restauration |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Confidentialité** | Score d’audit OWASP‑ASVS (niveau L2) | **≥ 90 %** | Scan OWASP‑ZAP + revues de code |
| **Intégrité** | Présence de contrôles d’intégrité (hash, signatures) – **Oui/Non** | **Oui** | Inspection du code (SecurityHelper, RightsHelper) |
| **Non‑répudiation** | Journalisation des actions critiques (audit log) – couverture % | **≥ 100 %** | Log4j2 + audit‑trail analysé |
| **Responsabilité** | Traçabilité des actions (ID session, IP) – % d’événements tracés | **≥ 100 %** | Tests fonctionnels sur SecurityFilter |
| **Authenticité** | Méthodes d’authentification (Cerbère SSO, LDAP) – nombre de mécanismes | **≥ 2** (SSO + mot‑de‑passe) | Tests d’authentification, revue de configuration |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Modularité** | Couplage (CBO) & Cohésion (LCOM) – moyenne sur le code | **CBO ≤ 5**, **LCOM ≥ 0,6** | SonarQube (rules “Cyclic dependencies”, “Package cohesion”) |
| **Réutilisabilité** | % de composants réutilisables (services, DAO) | **≥ 30 %** | Analyse de l’architecture (services‑baseadmin, integration) |
| **Analysabilité** | Complexité cyclomatique moyenne | **≤ 10** | SonarQube |
| **Modifiabilité** | Temps moyen de modification (jour‑homme) d’une fonctionnalité | **≤ 0,5 j‑h** (4 h) | Historique JIRA (lead‑time) |
| **Testabilité** | Couverture de tests unitaires (branches) | **≥ 80 %** | JaCoCo + SonarQube |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Vérification |
|----------------------|----------|----------|--------------|
| **Adaptabilité** | Nombre d’environnements supportés (dev, pre‑prod, prod, recette) | **4** | Scripts d’orchestration (Docker‑Compose, Kubernetes) |
| **Installabilité** | Temps d’installation d’une instance (minutes) | **≤ 30 min** | Documentation d’installation automatisée (Ansible) |
| **Remplaçabilité** | Compatibilité avec standards de déploiement (WAR, Docker) | **Oui** | Tests de packaging (Maven assembly) |

---

### 3.9 Matrice de correspondance CCF ↔ Critères de qualité  

| **CCF (exigences fonctionnelles)** | **Aptitude F.** | **Performance** | **Compatibilité** | **Utilisabilité** | **Fiabilité** | **Sécurité** | **Maintenabilité** | **Portabilité** |
|-------------------------------------|------------------|-------------------|-------------------|-------------------|---------------|--------------|----------------------|-----------------|
| **Saisie manuelle d’un administrateur** | ✔︎ Complétude, Exactitude | – | – | ✔︎ Appréhensibilité, Opérabilité | – | – | ✔︎ Modularité, Testabilité | – |
| **Alimentation auto‑J​ORF** | ✔︎ Exactitude, Adéquation | ✔︎ Temps de réponse (parsing) | ✔︎ Interopérabilité (XML/JSON) | – | ✔︎ Disponibilité, Récupérabilité | – | ✔︎ Réutilisabilité (services Article) | – |
| **Authentification Cerbère / SSO** | – | – | – | – | – | ✔︎ Confidentialité, Authenticité, Non‑répudiation | – | – |
| **Archivage des mandats** | ✔︎ Complétude, Exactitude | – | – | – | ✔︎ Disponibilité, Tolérance aux fautes | ✔︎ Intégrité | ✔︎ Analysabilité (schémas) | – |
| **Recherche plein‑texte** | ✔︎ Adéquation (résultats pertinents) | ✔︎ Temps de réponse < 2 s | ✔︎ Formats d’export CSV/JSON | ✔︎ Apprenabilité (recherche) | – | – | – | – |
| **Statistiques & tableaux de bord** | ✔︎ Complétude (indicateurs) | ✔︎ Performance (agrégation) | – | ✔︎ Esthétique, Accessibilité | – | – | – | – |
| **Notification d’échéance (mail)** | ✔︎ Exactitude (date) | – | – | – | ✔︎ Disponibilité du service mail | ✔︎ Confidentialité (TLS) | – | – |
| **Gestion des droits (profil Cerbère)** | – | – | – | – | – | ✔︎ Responsabilité, Authent. | – | – |
| **Déploiement (Docker / WAR)** | – | – | – | – | – | – | – | ✔︎ Installabilité, Adaptabilité |

*✔︎ = le sous‑critère participe à la satisfaction de l’exigence fonctionnelle.*

---

## 4. Architecture technique  

### 4.1 Diagramme de composants (simplifié)

```
┌─────────────────────────────────────────────────────┐
│                 admin_ep (WAR)                       │
│                                                     │
│  ┌─────────────┐   ┌─────────────────────┐           │
│  │  Web UI     │   │  Services (Spring) │           │
│  │ (Struts2)   │──▶│  - Article          │           │
│  └─────┬───────┘   │  - BaseAdmin        │           │
│        │           │  - Integration      │           │
│        │           └───────┬─────────────┘           │
│  ┌─────▼───────┐           │                     │
│  │  Security   │◀──────────┘ (SecurityFilter)   │
│  │ (Cerbère)  │                               │
│  └─────┬───────┘                               │
│        │                                       │
│  ┌─────▼───────┐   ┌─────────────────────┐    │
│  │  DB Layer   │──▶│ PostgreSQL 9.6/15   │    │
│  │ (JPA/Hibernate)│ (schéma integration)│    │
│  └─────────────┘   └─────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

* **Modules clés (Java packages)**  
  * `fr.gouv.e2.baseadmin.boot.*` – initialisation (I18n, Scheduler, SecurityManager).  
  * `fr.gouv.e2.baseadmin.controller.*` – actions Struts 2 (admins, établissements, mandats, etc.).  
  * `fr.gouv.e2.baseadmin.services.*` – logique métier (Article, BaseAdmin, Integration).  
  * `fr.gouv.e2.baseadmin.security.*` – gestion des droits, filtres.  
  * `fr.gouv.e2.baseadmin.util.*` – helpers (SQLConstantes, OdsUtil, JORFExtractor).  

* **Patrons architecturaux**  
  * **MVC** (Struts 2) – sépare la présentation, le contrôle et le modèle.  
  * **DAO / Service** – couche d’accès aux données (JPA) et logique métier (services).  
  * **Facade** (SecurityFilter) – point d’entrée unique pour la sécurisation.  
  * **Factory** (ServicesBaseAdminProvider) – injection des implémentations.  

* **Impacts qualité**  
  * **Modularité** → découpage en packages facilite la **maintenabilité** et les **tests unitaires**.  
  * **Facade Security** → centralise les contrôles, améliore la **sécurité** et la **traçabilité**.  
  * **JPA / Hibernate** → assure la **portabilité** du code d’accès aux données (DB‑agnostic).  

---

## 5. Stack technologique qualifié  

| Couche | Technologie | Version | Licence | Justification qualité |
|--------|------------|---------|----------|----------------------|
| **Langage** | Java | 8 (prévu → 11) | GPL / Oracle Binary Code License | Stabilité, large écosystème de tests (JUnit, JaCoCo). |
| **Framework Web** | Struts 2 (core) + Vertigo | 2.5.x | Apache 2.0 | MVC éprouvé, support de la **maintenabilité** et de la **compatibilité**. |
| **DI / Boot** | Vertigo‑Boot (custom) | 1.3 | Apache 2.0 | Simplifie la configuration, favorise la **modularité**. |
| **Serveur d’applications** | Apache Tomcat | 9.0.8 (upgrade → 10) | Apache 2.0 | Gestion du **déploiement** WAR, monitoring intégré. |
| **Base de données** | PostgreSQL | 9.6.11 (upgrade → 15) | PostgreSQL Licence | ACID, haute **disponibilité**, réplication. |
| **Gestion de dépendances** | Maven | 3.6.x | Apache 2.0 | Reproductibilité des builds, **installabilité**. |
| **CI / Qualimétrie** | SonarQube, JaCoCo, Snyk | – | – | Analyse de **code**, **vulnérabilités**. |
| **Tests fonctionnels** | JUnit 5, Selenium, Cucumber | – | – | Couverture **unitaire** & **acceptation**. |
| **Tests de charge** | JMeter, Gatling | – | – | Validation **performance**. |
| **Sécurité** | OWASP‑ZAP, Dependency‑Check | – | – | Scans **vulnérabilités**. |
| **Surveillance** | Prometheus + Grafana, New‑Relic | – | – | Métriques **runtime**, alertes SLA. |
| **Conteneurisation** | Docker, Docker‑Compose | – | – | **Portabilité**, déploiement reproductible. |

---

## 6. Stratégie de test & validation  

| Niveau | Objectif | Outils | Critères d’acceptation |
|--------|----------|--------|------------------------|
| **Unitaire** | Vérifier chaque classe/service | JUnit 5 + Mockito + JaCoCo | Coverage ≥ 80 % |
| **Intégration** | Interaction DB‑service, sécurité | Spring Test, TestContainers (Postgres) | Tous les scénarios CCF passent, aucune régression |
| **Fonctionnel** | Parcours UI (saisie, recherche, notification) | Selenium WebDriver + Cucumber | Scénarios UAT 100 % réussis |
| **Performance** | Temps de réponse, charge | JMeter (95 % ≤ 2 s) | Pas de dégradation > 5 % sous 150 users |
| **Sécurité** | Détection de vulnérabilités, tests d’intrusion | OWASP‑ZAP, Dependency‑Check | Score ASVS ≥ 90 % |
| **Acceptation** | Validation métier | Sessions UAT avec PO & utilisateurs | Satisfaction ≥ 4/5 sur questionnaire |
| **Non‑régression** | Garantir aucune régression après chaque commit | SonarQube Quality Gate (bugs ≤ 0, vuln ≤ 0) | Pipeline bloque si gate non respecté |

---

## 7. Supervision & métriques en production  

| Métrique | Source | Seuil d’alerte | Tableau de bord |
|----------|--------|----------------|-----------------|
| **Uptime** | New‑Relic / Prometheus | < 99,7 % (alertes > 30 min) | Grafana “SLA” |
| **Temps de réponse moyen** | JMeter‑report (synthetic) | > 1,8 s (warning) / > 2 s (critical) | Grafana “Performance” |
| **CPU / RAM** | Prometheus node exporter | CPU > 80 % (5 min) / RAM > 85 % | Grafana “Ressources” |
| **Taux d’erreurs HTTP (5xx)** | Log4j2 + Elastic‑Stack | > 0,5 % (warning) | Kibana “Errors” |
| **Débits de sauvegarde** | pgBackRest logs | Durée > 30 min (critical) | Grafana “Backup” |
| **Alertes de sécurité** | OWASP‑ZAP nightly scan | Toute vulnérabilité CVSS ≥ 7 (critical) | SonarQube “Security” |
| **Taux de succès des jobs Scheduler** | Quartz logs | < 95 % (warning) | Grafana “Scheduler” |
| **Nombre d’incidents d’échéance non notifiés** | Table `mandat` + audit | > 2 jours de retard (critical) | Dashboard “Mandats” |

---

## 8. Documentation technique  

| Type | Format | Standard | Responsable |
|------|--------|----------|-------------|
| **Code** | Javadoc (Java 8) | JSR‑269 | Équipe dev |
| **API** | Swagger/OpenAPI 3.0 | – | Équipe API |
| **Architecture** | Diagrammes UML (PlantUML) | ISO/IEC 42010 | Architecte |
| **Déploiement** | Playbooks Ansible + Docker‑Compose | Ansible Best‑Practices | Ops |
| **Opération** | Runbooks (incident, backup, restore) | ITIL v4 | Ops |
| **Qualimétrie** | Rapport SonarQube, JaCoCo, OWASP‑ZAP | – | QA |

---

## 9. Gestion des dettes techniques  

| Risque / Dette | Impact | Plan de remboursement | Horizon |
|----------------|--------|------------------------|---------|
| **Version Java 8** | Obsolescence, manque de support LTS | Migration vers Java 11 (modules, tests de compatibilité) | Q4 2024 |
| **PostgreSQL 9.6** → 15 | Sécurité & performances | Upgrade via pg_dump/restore, validation de scripts SQL | Q2 2025 |
| **Tomcat 9 → 10** (Servlet 5) | Breakage de API Struts 2 | Refactorisation du `web.xml` + tests d’intégration | Q1 2025 |
| **Couplage entre `security` et `controller`** | Difficulté de tests unitaires | Introduire un service d’autorisation (Strategy pattern) | Q3 2024 |
| **Scripts SQL d’initialisation** (hard‑coded) | Risque de divergence entre dev / prod | Externaliser dans Liquibase migrations | Q2 2024 |
| **Documentation manuelle** | Perte de traçabilité | Générer automatiquement la documentation (Javadoc + Swagger) | Q4 2024 |

> **Suivi** : chaque dette est enregistrée dans le backlog JIRA (composant *Technical Debt*) avec estimation en story points et priorité ≥ M‑2 (M = version majeure).

---

## 10. Conclusion  

Le présent CST formalise les exigences de **qualité** du produit *admin_ep* conformément au modèle ISO / IEC 25010 2023. Les métriques, objectifs chiffrés et méthodes de vérification permettent :

* **De mesurer** de façon objective chaque aspect (performance, sécurité, fiabilité, …).  
* **De piloter** les évolutions (p.ex. migration vers Java 11, PostgreSQL 15) tout en maîtrisant les risques.  
* **De fournir** aux parties prenantes (MOA, MOE, exploitation) une visibilité sur le respect des SLA et des exigences réglementaires (RGPD, DICT).

Le suivi continu (CI/CD, dashboards) assure la **conformité** du produit tout au long de son cycle de vie.  

---  

*Document rédigé par l’Architecte Qualité Logicielle – ISO / IEC 25010 – 2024‑04‑27*