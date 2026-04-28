# 📄 Cahier des Spécifications Techniques (CST) – **admin_ep**  
**Projet** : admin_ep – Administration des établissements publics (MTES‑MCT)  
**Version du CST** : 1.0 – 27/04/2026  

---  

## 1️⃣ Introduction & Contexte Qualité  

| Élément | Description |
|--------|-------------|
| **Objectifs de qualité du projet** | - Garantir la disponibilité ≥ 99,9 % (SLAs ministériels) <br> - Assurer la **fiabilité** des mandats (détection d’échéances, archivage) <br> - Offrir une **expérience utilisateur** fluide (SUS ≥ 68) <br> - Respecter les exigences de **sécurité** (confidentialité, intégrité, traçabilité) <br> - Permettre l’évolution (modularité, maintenabilité) afin de faciliter les montées de version Tomcat 10 / PostgreSQL 15 |
| **Contexte métier** | Base de données partagée recensant les membres des conseils d’administration des établissements publics du MTES‑MCT (≈ 96 établissements).  <br>Fonctionnalités : saisie manuelle, alimentation automatique via JORF, recherche, tableau de bord statistique, notifications d’échéance, gestion des droits (Cerbère). |
| **Contexte technique** | - **Langage** : Java 8 (déprécié, à migrer) <br> - **Framework Web** : Struts 2 (MVC) + Vertigo (DI) <br> - **Serveur d’applications** : Tomcat 9.0.8 (prévu → Tomcat 10) <br> - **SGBD** : PostgreSQL 9.6.11 (prévu → PostgreSQL 15) <br> - **Build** : Maven 3.6, modules : `adminep-database`, `adminep-web`, `adminep-deployment`, `adminep-doc` <br> - **Infrastructure** : IaaS (ECO4) – datacenter Paris La Défense, conteneurisation en cours (Docker/K8s) |
| **Méthodologie d’évaluation qualité** | - **Mesure automatisée** : SonarQube, JMeter, JUnit, OWASP ZAP, Prometheus/Grafana. <br> - **Revues** : peer‑code, audit sécurité (ANSSI RGS). <br> - **Tests d’acceptation** : scénarios fonctionnels (CCF) exécutés dans les environnements **Pre‑prod** et **Production**. |

---

## 2️⃣ Modèle de Qualité ISO/IEC 25010  

```
                     ┌─────────────────────┐
                     │ QUALITÉ PRODUIT     │
                     └─────────────────────┘
        ┌───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐
        │ Apt.  │ Perf. │ Compat│ Utili.│ Fiab. │ Sécur.│ Maint.│ Portab.│
        │ Funct.│ Eff.  │ ibili │ té   │ ité   │ ity   │ ité   │ ity    │
        └───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
```

| Caractéristique | Sous‑caractéristiques (31) |
|-----------------|---------------------------|
| **Aptitude fonctionnelle** | Complétude, Exactitude, Adéquation |
| **Performance & efficacité** | Comportement temporel, Utilisation des ressources, Capacité |
| **Compatibilité** | Cohérence, Interopérabilité |
| **Utilisabilité** | Appréhensibilité, Apprenabilité, Opérabilité, Esthétique, Accessibilité |
| **Fiabilité** | Maturité, Disponibilité, Tolérance aux fautes, Récupérabilité |
| **Sécurité** | Confidentialité, Intégrité, Non‑répudiation, Responsabilité, Authenticité |
| **Maintenabilité** | Modularité, Réutilisabilité, Analysabilité, Modifiabilité, Testabilité |
| **Portabilité** | Adaptabilité, Installabilité, Remplaçabilité |

---  

## 3️⃣ Spécification détaillée par caractéristique  

> **Toutes les métriques sont mesurables, chiffrées et traçables (CCF → CST).**  

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Source (CCF) |
|----------------------|----------|----------|--------------|
| **Complétude fonctionnelle** | % d’exigences fonctionnelles couvertes (ex. CRUD admins, recherche, notification) | **≥ 95 %** | Table “Fonctionnalités” du wiki (home → Fiche‑Produit) |
| **Exactitude fonctionnelle** | Taux d’erreurs de saisie détectées en fin de transaction (détection d’incohérences mandat) | **≤ 0,5 %** | Validation métier (service `MandatServicesImpl`) |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | **≥ 4,2/5** | Enquête SUS (phase bêta) |

**Justification technique**  
- Architecture **MVC** (Struts2) + **DAO** assure la séparation des préoccupations → plus facile de garantir la complétude.  
- Règles de validation SQL (contraintes FK, triggers) assurent l’exactitude.  
- UI (Bootstrap + Chosen) répond aux exigences d’opérabilité.

---

### 3.2 Performance & efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Outil de mesure |
|----------------------|----------|----------|-----------------|
| **Comportement temporel** | Temps moyen de réponse (95ᵉ percentile) sur les pages de recherche | **≤ 2 s** | JMeter (scenario « Recherche EP ») |
| **Utilisation des ressources** | CPU / RAM moyen sous charge (200 utilisateurs simultanés) | **CPU ≤ 70 %**, **RAM ≤ 65 %** | Prometheus + Grafana |
| **Capacité** | Nombre d’utilisateurs simultanés supportés sans dégradation > 2 s | **≥ 300** | Test de charge JMeter (ramp‑up 0‑300) |

**Justification**  
- Le **pool de connexions** (HikariCP) limite le nombre de connexions DB.  
- Le **cache** (Ehcache) sur les listes de référentiels (charges, ministères).  
- Le serveur Tomcat est configuré avec **thread pool** adapté (maxThreads = 250).

---

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Commentaire |
|----------------------|----------|----------|--------------|
| **Cohérence** | % de conformité aux standards UI (Bootstrap 4) | **100 %** | Vérification via axe‑core |
| **Interopérabilité** | Nombre de formats d’échange supportés (CSV, JSON, XML) | **≥ 3** | API REST (JSON) + export CSV + import XML (scripts d’initialisation) |

---

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Source |
|----------------------|----------|----------|--------|
| **Appréhensibilité** | Temps de formation d’un nouvel opérateur (en heures) | **≤ 2 h** | Sessions internes |
| **Apprenabilité** | % de tâches réussies à la première tentative (ex. création d’un admin) | **≥ 90 %** | Tests utilisateurs |
| **Opérabilité** | Nombre moyen de clics pour créer un mandat | **≤ 5** | Analyse UI (wireframes) |
| **Esthétique** | Score SUS global | **≥ 68/100** | Étude SUS (beta) |
| **Accessibilité** | Conformité WCAG 2.1 Niveau AA | **Oui** | Audit axe‑core + manuel |

---

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Outil |
|----------------------|----------|----------|-------|
| **Maturité** | Densité de défauts (défauts/KLOC) | **≤ 0,5** | SonarQube / Bugzilla |
| **Disponibilité** | % de temps de service (Uptime) | **≥ 99,9 %** | Pingdom / Prometheus |
| **Tolérance aux fautes** | RTO (temps de récupération) après incident DB | **≤ 5 min** | Tests de basculement (replication) |
| **Récupérabilité** | RPO (point de récupération) | **≤ 15 min** | Sauvegarde PostgreSQL (WAL) |

---

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Référentiel |
|----------------------|----------|----------|--------------|
| **Confidentialité** | Score d’audit (ANSSI RGS) | **≥ 80 %** | Rapport audit (2024) |
| **Intégrité** | Présence de contrôles de hash (SHA‑256) sur les pièces jointes | **Oui** | Implémentation `SecurityHelper` |
| **Non‑répudiation** | Journalisation des actions critiques (audit log) | **Oui** | `LogAccessInterceptor` + ELK |
| **Responsabilité** | % de logs d’audit couverts (ex. création mandat) | **≥ 95 %** | ELK Dashboard |
| **Authenticité** | Méthodes d’authentification utilisées (Cerbère SSO + LDAP) | **Oui** | `SecurityManagerInitializer` |

---

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Outil |
|----------------------|----------|----------|-------|
| **Modularité** | Couplage moyen (efferent) | **≤ 0,3** | SonarQube (Dependency Structure Matrix) |
| **Réutilisabilité** | % de composants réutilisables (services) | **≥ 60 %** | Analyse du package `services.*` |
| **Analysabilité** | Complexité cyclomatique moyenne | **≤ 10** | SonarQube |
| **Modifiabilité** | Temps moyen (person‑day) pour ajouter une nouvelle charge | **≤ 0,5 j** | Historique tickets |
| **Testabilité** | Couverture de tests unitaires | **≥ 80 %** | JaCoCo (Maven) |

---

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Commentaire |
|----------------------|----------|----------|-------------|
| **Adaptabilité** | Nombre d’environnements supportés (dev, pre‑prod, prod, Docker) | **4** | Dockerfile + Helm chart |
| **Installabilité** | Temps d’installation d’une instance Docker (first‑time) | **≤ 10 min** | Script `docker-compose up` |
| **Remplaçabilité** | Compatibilité avec les standards de déploiement (K8s, Helm) | **Oui** | Manifestes Helm fournis |

---  

## 4️⃣ Architecture technique  

### 4.1 Diagramme de composants (UML) – description synthétique  

```
+-------------------+      +-------------------+      +-------------------+
|  admin_ep‑web     |      |  admin_ep‑db     |      |  admin_ep‑deploy |
| (Struts2 MVC)    |<---->| (PostgreSQL)      |<---->| (Maven, Docker) |
+-------------------+      +-------------------+      +-------------------+
        |                         ^                     |
        |                         |                     |
        |   +---------------------+---------------------+|
        |   |   Services (DAO, Business)             |
        |   +------------------------------------------+
        |
        +---> UI (JSP + Bootstrap)  <---+---  REST API (JSON)
```

* **Web** – `adminep-web` : contrôleurs Struts2, décorateurs, filtres de sécurité, JSP + Bootstrap UI.  
* **Business** – `services.*` : logique métier (Mandat, Charge, Etablissement, etc.).  
* **Persistance** – `adminep-database` : scripts DDL/DML, schéma *integration*, séquences, contraintes FK.  
* **Déploiement** – `adminep-deployment` : assembly zip, configuration Tomcat, fichiers `web.xml`, `log4j2.xml`.  
* **Documentation** – `adminep-doc` : génération de Javadoc, Swagger (si API) et livrables.  

### 4.2 Justification des choix techniques  

| Décision | Impact sur la qualité (ISO 25010) |
|----------|----------------------------------|
| **Struts 2 + MVC** | *Utilisabilité* (séparation UI/logic) ; *Maintenabilité* (contrôleurs légers) |
| **DAO + Service Layer** | *Fiabilité* (transactions gérées) ; *Modularité* (réutilisabilité) |
| **PostgreSQL** | *Sécurité* (chiffrement, rôle) ; *Disponibilité* (replication) |
| **Tomcat 9 + SSL** | *Sécurité* (TLS) ; *Performance* (thread pool) |
| **Maven 3 + SonarQube** | *Analysabilité* (qualité du code) ; *Testabilité* (plugins) |
| **Docker/K8s** (en cours) | *Portabilité* (déploiement multi‑environnements) ; *Installabilité* (automatisation) |
| **Cache Ehcache** | *Performance* (temps de réponse) ; *Utilisabilité* (UX réactive) |
| **OWASP ZAP + Pen‑Test** | *Sécurité* (détection vulnérabilités) |
| **Prometheus + Grafana** | *Supervision* (alertes SLA) ; *Fiabilité* (détection précoce) |

---  

## 5️⃣ Stack technologique qualifié  

| Couche | Technologie | Version | Licence | Pourquoi ce choix (qualité) |
|--------|--------------|---------|---------|-----------------------------|
| **Langage** | Java | 8 (prévu → 11) | GPL + Oracle Binary Code License | Maturité, vaste écosystème, robustesse |
| **Framework Web** | Struts 2 | 2.5.26 | Apache 2.0 | MVC éprouvé, intégration Vertigo |
| **DI / IoC** | Vertigo | 3.0 | Apache 2.0 | Découplage, testabilité |
| **UI** | Bootstrap | 4.5 | MIT | Responsive, bonne ergonomie |
| **Base de données** | PostgreSQL | 9.6.11 (prévu → 15) | PostgreSQL License | ACID, réplication, sécurité |
| **Serveur d’applications** | Tomcat | 9.0.8 (prévu → 10) | Apache 2.0 | Gestion de sessions, compatibilité Java EE |
| **Build** | Maven | 3.6.3 | Apache 2.0 | Gestion de dépendances, reproducibilité |
| **Gestion de logs** | Log4j2 | 2.17 | Apache 2.0 | Flexibilité, rotation, intégration ELK |
| **Cache** | Ehcache | 3.9 | Apache 2.0 | Améliore le temps de réponse |
| **Tests unitaires** | JUnit | 5.9 | Eclipse Public License | Couverture de code |
| **Tests d’intégration** | Spring Test (pour DAO) | 5.9 | Apache 2.0 | Transactions rollback |
| **Tests de charge** | JMeter | 5.6 | Apache 2.0 | Mesure performance |
| **Analyse statique** | SonarQube | 9.9 LTS | LGPLv3 | Qualité du code |
| **Sécurité** | OWASP ZAP | 2.12 | Apache 2.0 | Scan vulnérabilités |
| **Supervision** | Prometheus + Grafana | 2.45 / 10.2 | Apache 2.0 | Métriques temps réel |
| **Conteneurisation** | Docker | 24.0 | Apache 2.0 | Portabilité, reproductibilité |

---  

## 6️⃣ Stratégie de test & validation  

| Niveau | Activité | Outils | Critères d’acceptation |
|--------|----------|--------|------------------------|
| **Unitaire** | Tests JUnit sur chaque classe (`*Service`, `*Dao`, `*Helper`) | JUnit 5, JaCoCo | Couverture **≥ 80 %** |
| **Intégration** | Tests de persistance avec base H2 ou PostgreSQL (transactions) | Spring Test, DBUnit | Tous les scénarios CRUD passent **sans erreur** |
| **Fonctionnel** | Scénarios CCF (ex. CRUD admin, recherche, notification) | Selenium + JUnit, Cucumber | **≥ 95 %** de scénarios réussis en pre‑prod |
| **Performance** | Tests de charge (200‑300 utilisateurs) | JMeter, Grafana | Temps de réponse **≤ 2 s**, CPU ≤ 70 % |
| **Sécurité** | Scan dynamique, revue de code | OWASP ZAP, SonarQube (security hotspot) | Aucun **High** ou **Critical** non résolu |
| **Acceptation** | Validation métier (MOA) | Checklist CCF, tableau de bord KPI | Tous les KPI (SUS, disponibilité, etc.) atteints |
| **Regression** | Exécution nightly du pipeline CI | GitLab CI, Docker | Build **green** et métriques stables |

**Plan de tests automatisés (CI)**  

```yaml
stages:
  - compile
  - unit-test
  - integration-test
  - performance
  - security
  - package
  - deploy

unit_test:
  stage: unit-test
  script:
    - mvn clean test jacoco:report
  artifacts:
    paths: [target/site/jacoco]

integration_test:
  stage: integration-test
  script:
    - mvn verify -Pintegration-tests

performance_test:
  stage: performance
  script:
    - jmeter -n -t jmeter/performance.jmx -l results.jtl
  artifacts:
    paths: [results.jtl]

security_scan:
  stage: security
  script:
    - zap-baseline.py -t https://adminep-preprod.e2.rie.gouv.fr -r zap-report.html
```

---  

## 7️⃣ Supervision & métriques en production  

| Métrique | Seuil d’alerte | Source | Action |
|----------|----------------|--------|--------|
| **Uptime** | < 99,9 % (sur 24 h) | Pingdom / Prometheus | Escalade N2, vérification Tomcat |
| **Temps de réponse (95ᵉ pct)** | > 2 s | JMeter‑synthetic + Prometheus | Analyse thread pool, scaling |
| **CPU** | > 80 % (5 min) | Node Exporter | Auto‑scale (K8s) |
| **RAM** | > 75 % (5 min) | Node Exporter | Vérifier fuite mémoire (GC logs) |
| **Taux d’erreurs HTTP 5xx** | > 1 % | ELK (log4j2) | Redémarrage conteneur, analyse stacktrace |
| **Nombre de logs d’audit non‑archivés** | > 0 | ELK | Purge / augmentation stockage |
| **Débit de notifications mail** | < 95 % délivrées | MailHog / Postfix | Vérifier SMTP, quota |
| **Détection d’anomalies de sécurité** | Toute alerte OWASP ZAP | ZAP nightly scan | Patch, CVE update |

**Dashboard** (Grafana) – panneaux : “Availability”, “Response‑time”, “CPU/RAM”, “Error‑rate”, “Security‑alerts”, “Notification‑delivery”.

---  

## 8️⃣ Documentation technique  

| Type | Outil | Livrable | Fréquence |
|------|-------|----------|-----------|
| **Code** | Javadoc (Maven plugin) | `target/site/apidocs` | À chaque release |
| **API** | Swagger/OpenAPI (Springfox) | `swagger-ui.html` | À chaque release |
| **Architecture** | PlantUML (UML) | `docs/architecture/*.png` | Version 1.0 |
| **Processus CI/CD** | GitLab CI YAML | `.gitlab-ci.yml` | Continu |
| **Guide d’installation** | Markdown | `README_INSTALL.md` | Version 1.0 + mise à jour Docker |
| **Guide d’exploitation** | Confluence page (export PDF) | `OPS_guide.pdf` | Tous les changements majeurs |
| **Gestion des incidents** | Jira Service Management | Ticket template | En continu |
| **Tests** | JaCoCo, JMeter reports | `target/site/jacoco`, `jmeter/report.html` | Chaque pipeline |

---  

## 9️⃣ Gestion des dettes techniques  

| Dette | Risque | Priorité | Plan de remboursement |
|------|--------|----------|-----------------------|
| **Java 8** (EOL 2026) | Obsolescence, perte de support sécurité | **Élevée** | Migration vers Java 11 (phase 1) puis Java 17 (phase 2) – estimation 4 sprints |
| **Tomcat 9** → Tomcat 10 (Jakarta EE 9) | Incompatibilité de bibliothèques Struts2 | **Élevée** | Piloter migration dans le sprint 12, tests d’intégration complet |
| **PostgreSQL 9.6** → 15 | Fin de support, performances limitées | **Moyenne** | Mise en place d’une réplication en lecture, bascule progressive (feature‑flag) |
| **Couplage Struts2‑Vertigo** | Difficulté de tests unitaires | **Moyenne** | Introduire un wrapper service, augmenter couverture unitaires |
| **Absence de tests d’acceptation automatisés** | Risque de régression fonctionnelle | **Élevée** | Développer scénarios Cucumber + Selenium (sprint 8‑10) |
| **Documentation incomplète (Swagger)** | Difficulté d’intégration tierce | **Faible** | Générer automatiquement à chaque build, publier sur Nexus |
| **Scripts SQL monolithiques** | Risque de migration difficile | **Moyenne** | Refactoriser en migrations Flyway (sprint 6) |
| **Gestion des secrets en clair** (`log4j2.xml`, `application-config.xml`) | Vulnérabilité | **Élevée** | Passer à HashiCorp Vault / Kubernetes Secrets (sprint 9) |

**Suivi** – tableau de bord “Technical Debt” dans Jira, poids (story points) et date cible de résolution.

---  

## 🔗 Matrice de correspondance CCF ↔ Critères de qualité  

| CCF (exigence fonctionnelle) | Caractéristique ISO 25010 | Sous‑caractéristique | Métrique associée |
|------------------------------|----------------------------|----------------------|-------------------|
| **Création / mise à jour d’un admin** | Aptitude fonctionnelle | Complétude, Exactitude | % de champs obligatoires remplis, taux d’erreurs de validation |
| **Recherche d’un établissement** | Performance & efficacité | Comportement temporel | Temps de réponse 95ᵉ percentile |
| **Export CSV / JSON** | Compatibilité | Interopérabilité | Formats supportés |
| **Gestion des droits (Cerbère)** | Sécurité | Confidentialité, Authenticité | Audits log, SSO success rate |
| **Notification d’échéance** | Fiabilité | Disponibilité, Tolérance aux fautes | % de mails délivrés, RTO |
| **Tableau de bord statistique** | Utilisabilité | Esthétique, Appréhensibilité | Score SUS, nombre de clics |
| **Import JORF** | Maintenabilité | Modifiabilité | Temps d’ajout d’un nouveau parser |
| **Déploiement sur Docker** | Portabilité | Installabilité | Temps d’installation |
| **Sauvegarde / restauration** | Fiabilité | Récupérabilité | RPO / RTO mesurés |

---  

## 📌 Conclusion  

Le présent CST formalise les exigences de qualité du projet **admin_ep** en s’appuyant sur le modèle ISO/IEC 25010. Les métriques définies sont **mesurables**, **traçables** aux exigences fonctionnelles (CCF) et **vérifiables** via les outils de la chaîne CI/CD.  

Le plan d’action suivant doit être validé :  

1. **Migration technologique** (Java 11/17, Tomcat 10, PostgreSQL 15).  
2. **Industrialisation des tests** (unitaires, fonctionnels, performance, sécurité).  
3. **Mise en place de la supervision** (Prometheus + Grafana, alerting SLA).  
4. **Réduction des dettes techniques** selon le tableau de bord.  

Le respect de ces engagements permettra d’atteindre les objectifs de disponibilité, de sécurité et d’évolutivité attendus par les parties prenantes du ministère.  

---  

*Document généré le 27/04/2026 – Auteur : ChatGPT (OpenAI) – Révision par l’équipe Qualité SQA.*