# 📄 Cahier des Spécifications Techniques (CST) – **causalismp**  
**Version** : 1.0.0 – 2024‑04‑28  
**Projet** : *causalismp* – Gestion des accidents du travail et des maladies professionnelles  
**Références normatives** : ISO/IEC 25010:2023 (SQuaRE – Product quality model)  

---  

## 1. Introduction & Contexte Qualité  

| Élément | Description |
|---------|-------------|
| **Objectifs de qualité du projet** | • Garantir la **fiabilité** et la **disponibilité** du service d’enregistrement et de consultation des accidents/maladies. <br>• Assurer la **pertinence fonctionnelle** (exhaustivité, exactitude, adéquation) des données métier. <br>• Offrir une **expérience utilisateur** simple (temps d’apprentissage < 2 h, 5 clics max pour les actions courantes). <br>• Maintenir un **coût de maintenance** faible grâce à une architecture modulaire et une couverture de tests élevée (> 80 %). |
| **Contexte métier** | Le logiciel est destiné aux services RH/Prévention des entreprises du groupe *Ambulon*. Il centralise : <br>– la saisie d’accidents du travail, <br>– la saisie de maladies professionnelles, <br>– la consultation de statistiques, <br>– l’export des dossiers (OpenOffice), <br>– la synchronisation des référentiels (grades, services) avec le SI externe *Rehucit* via des WS. |
| **Contexte technique** | • **Plateforme** : Java 8, Maven multi‑module, serveur d’applications compatible J2EE (Tomcat 9 / JBoss EAP). <br>• **Framework Web** : Struts 1.x (Action, ActionForm, TagLib). <br>• **Persistance** : Castor JDO + Oracle 12c (datasource JNDI `jdbc/userDScausalis`). <br>• **Intégration WS** : Stubs dans `StubWS.jar`. <br>• **CI/CD** : GitLab‑CI, SonarQube (quality‑gate). <br>• **Monitoring** : Prometheus + Grafana (via JMX exporter). |
| **Méthodologie d’évaluation qualité** | 1. **Mesure continue** via SonarQube (bugs, vulnérabilités, couverture, duplication, complexité). <br>2. **Tests automatisés** (unitaires, d’intégration, end‑to‑end) exécutés à chaque *pipeline* CI. <br>3. **Tests de performance** (JMeter) sur les scénarios critiques (création dossier, export). <br>4. **Audit de conformité** (RGAA/WCAG 2.1 AA) sur l’interface JSP. <br>5. **Tableaux de bord** en production (SLA ≥ 99,9 % uptime, RT ≤ 2 s 95ᵉ percentile). |

---

## 2. Modèle de Qualité ISO 25010 (Produit)

```
┌─────────────────────────────────────┐
│      QUALITÉ DU PRODUIT LOGICIEL      │
└─────────────────────────────────────┘
          │
   ┌──────┼───────┬───────┬───────┬───────┬───────┬───────┐
   │      │       │       │       │       │       │       │
   ▼      ▼       ▼       ▼       ▼       ▼       ▼       ▼
Aptitude   Performance   Compatibilité   Utilisabilité   Fiabilité   Sécurité   Maintenabilité   Portabilité
fonctionnelle   efficacité   (interopérabilité)   (appréhensibilité…)   (disponibilité…)   (confidentialité…)   (modularité…)   (adaptabilité…)
```

| Caractéristique | Sous‑caractéristiques (31) |
|----------------|----------------------------|
| **1. Aptitude fonctionnelle** | Complétude, Exactitude, Adéquation |
| **2. Performance & efficacité** | Comportement temporel, Utilisation des ressources, Capacité |
| **3. Compatibilité** | Cohérence, Interopérabilité |
| **4. Utilisabilité** | Appréhensibilité, Apprenabilité, Opérabilité, Esthétique, Accessibilité |
| **5. Fiabilité** | Maturité, Disponibilité, Tolérance aux fautes, Récupérabilité |
| **6. Sécurité** | Confidentialité, Intégrité, Non‑répudiation, Responsabilité, Authenticité |
| **7. Maintenabilité** | Modularité, Réutilisabilité, Analysabilité, Modifiabilité, Testabilité |
| **8. Portabilité** | Adaptabilité, Installabilité, Remplaçabilité |

---

## 3. Spécifications détaillées par caractéristique  

> Les tableaux ci‑dessous indiquent la **métrique**, la **méthode de mesure**, le **seuil cible** (exigence) et la **valeur actuelle** (placeholder à renseigner après le premier run de production).  

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Complétude fonctionnelle** | % d’exigences fonctionnelles implémentées (CCF) | Mapping CCF → classes *Action/Service* (traceability matrix) | **≥ 95 %** | – |
| **Exactitude fonctionnelle** | Taux d’erreurs de saisie détectées (validation + logs) | Analyse logs (Log4j) + tests unitaires (assertions) | **≤ 1 %** des enregistrements | – |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | Questionnaire post‑déploiement (5 utilisateurs pilotes) | **≥ 4/5** | – |

### 3.2 Performance & efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Comportement temporel** | Temps de réponse 95ᵉ percentile (ms) | JMeter script *CreateDossier*, *Export* | **≤ 2000 ms** | – |
| **Utilisation des ressources** | CPU % / RAM % sous charge nominale (50 utilisateurs) | Prometheus JMX exporter (cpu, heap) | **CPU ≤ 70 %**, **RAM ≤ 80 %** | – |
| **Capacité** | Nombre d’utilisateurs simultanés supportés (sans dégradation) | Test de charge progressive JMeter | **≥ 150 users** | – |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Cohérence** | Conformité aux standards Struts 1 (XHTML, taglibs) | Analyse statique (HTML validator) | **100 %** conformité | – |
| **Interopérabilité** | Formats d’échange supportés (XML, JSON) | Inventaire des WSDL/REST exposés | **≥ 3** formats (XML + JSON + CSV) | – |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Appréhensibilité** | Temps de formation (h) pour un nouveau user | Sessions de formation + questionnaire | **≤ 2 h** | – |
| **Apprenabilité** | % de tâches réussies sans formation | Test “first‑time‑use” (5 tâches) | **≥ 90 %** | – |
| **Opérabilité** | Nombre de clics pour créer un dossier accident | Observation + script Selenium | **≤ 5 clics** | – |
| **Esthétique** | Score SUS (System Usability Scale) | Questionnaire SUS auprès 20 utilisateurs | **≥ 68/100** | – |
| **Accessibilité** | Niveau de conformité RGAA/WCAG | Audit Axe / WAVE | **AA** minimum | – |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Maturité** | Densité de défauts (bugs / KLOC) | SonarQube *bugs* / *lines of code* | **≤ 0,5 bugs/KLOC** | – |
| **Disponibilité** | % de temps de disponibilité (Uptime) | Monitoring Prometheus + SLA calculator | **≥ 99,9 %** | – |
| **Tolérance aux fautes** | Temps moyen de récupération (MTTR) après incident | Incident logs (time to restore) | **≤ 5 min** | – |
| **Récupérabilité** | Point de récupération acceptable (RPO) | Backup policy (DB dump) | **≤ 15 min** | – |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Confidentialité** | Score d’audit (OWASP ASVS Level 2) | Scan OWASP ZAP + manuel | **≥ 90 %** de conformité | – |
| **Intégrité** | Présence de contrôles d’intégrité (hash, signatures) | Revue de code + tests d’injection | **Oui** (implémenté) | – |
| **Non‑répudiation** | Journalisation des actions sensibles | Log4j audit logs (user, action, timestamp) | **Oui** | – |
| **Responsabilité** | Couverture du traçage d’audit (actions / modules) | Analyse des logs | **≥ 95 %** des actions | – |
| **Authenticité** | Méthodes d’authentification utilisées | Integration Cerbere (SSO) + LDAP | **LDAP + SSO** | – |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Modularité** | Couplage / Cohésion (SonarQube) | *Cognitive Complexity*, *Package Tangle Index* | **Couplage ≤ 0,2**, **Cohésion ≥ 0,8** | – |
| **Réutilisabilité** | % de composants réutilisables (services, DAO) | Inventaire des classes **public** | **≥ 70 %** | – |
| **Analysabilité** | Complexité cyclomatique moyenne | SonarQube *complexity* | **≤ 10** | – |
| **Modifiabilité** | Temps moyen de modification (person‑day) | Historique JIRA + temps réel | **≤ 1 j/h** | – |
| **Testabilité** | Couverture de tests unitaires (%) | JaCoCo (Maven) | **≥ 80 %** | – |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Méthode de mesure | Objectif | Valeur actuelle |
|----------------------|----------|-------------------|----------|-----------------|
| **Adaptabilité** | Nombre d’environnements supportés (OS/Serveur) | Documentation d’installation | **≥ 3** (Linux Ubuntu 20.04, RHEL 8, Windows Server 2019) | – |
| **Installabilité** | Temps d’installation standard (min) | Script d’automatisation (Ansible) | **≤ 15 min** | – |
| **Remplaçabilité** | Compatibilité avec formats standards d’échange (CSV, XML, JSON) | Inventaire des exporteurs | **Oui** (3 formats) | – |

---

## 4. Architecture technique  

### 4.1 Diagramme de composants (description)

```
+-------------------+          +-------------------+          +-------------------+
|   Web Browser     |  HTTP    |   Web Container   |  JNDI    |   Oracle DB       |
| (JSP / Struts UI) | <------> | (Tomcat / JBoss) | <------> | (causalis schema) |
+-------------------+          +-------------------+          +-------------------+
        ^                               ^                               ^
        |                               |                               |
        |                               |                               |
        |                               |                               |
+-------------------+   RMI/JMS   +-------------------+   Castor JDO   +-------------------+
| Struts 1 Actions  | <--------> | Service Layer     | <-----------> | DAO (Castor)      |
| (Action, Form)   |            | (Reference, Sync) |              | (GenericDao<T>) |
+-------------------+            +-------------------+              +-------------------+
        ^                               ^                               ^
        |                               |                               |
        |                               |                               |
+-------------------+       +-------------------+               +-------------------+
| WS Clients (Stub) | ----> | WS Converters    |               | Utility classes   |
| (StubWS.jar)      |       | (TrancheAge, …) |               | (DBTools, …)      |
+-------------------+       +-------------------+               +-------------------+
```

### 4.2 Justification des choix  

| Couches | Choix technologiques | Impact sur la qualité |
|--------|----------------------|-----------------------|
| **Web** | Struts 1 + JSP | **Utilisabilité** (templates JSP simples) ; **Compatibilité** via taglibs personnalisés. |
| **Service** | POJO services (`*Service`) + interface `SynchronizeService` | **Modularité** (séparation logique) ; **Maintenabilité** (testabilité unitaire élevée). |
| **DAO** | Castor JDO + XML mapping (`database.xml`) | **Portabilité** (XML mapping) ; **Fiabilité** (transactions JDO). |
| **WS** | Stubs `StubWS.jar` + convertisseurs (`TrancheAgeHelper`) | **Interopérabilité** (exposition de services externes) ; **Sécurité** (délimitation du périmètre). |
| **Build** | Maven multi‑module + Assembly descriptors | **Installabilité** (archives ZIP automatisées) ; **Portabilité** (indépendance du IDE). |
| **CI/CD** | GitLab‑CI + SonarQube | **Qualité** (quality‑gate) ; **Fiabilité** (déploiement automatisé). |
| **Monitoring** | Prometheus + Grafana (JMX exporter) | **Disponibilité** (alertes temps réel) ; **Performance** (visualisation RT). |

---

## 5. Stack technologique qualifié  

| Couche | Technologie | Version | Licence | Commentaires |
|--------|-------------|---------|----------|--------------|
| **JDK** | OpenJDK | 1.8.0_382 | GPL‑2 with Classpath Exception | Compatibilité Struts 1. |
| **Build** | Maven | 3.8.6 | Apache 2.0 | Multi‑module, assembly, sonar‑plugin. |
| **Web Framework** | Apache Struts 1.3.10 | 1.3.10 | Apache 2.0 | Action‑based, stable pour les applications internes. |
| **Persistance** | Castor JDO | 1.4.1 | Apache 2.0 | Mapping XML, JNDI datasource. |
| **DB** | Oracle | 12c (ou supérieur) | Oracle Commercial | Datasource JNDI `jdbc/userDScausalis`. |
| **WS Client** | StubWS.jar (custom) | – | Proprietary | Fournit les clients `WSClientEffectif`, `WSClientGrade`, `WSClientService`. |
| **Logging** | Log4j 1.2.17 | 1.2.17 | Apache 2.0 | Configurable via `log4j.xml`. |
| **CI** | GitLab‑CI | – | – | Pipelines avec Maven, SonarQube, Docker (optional). |
| **Qualimétrie** | SonarQube | 9.9 LTS | GNU LGPL v3 | Quality‑gate, coverage, duplication, bugs. |
| **Tests** | JUnit 4, Mockito 2, JaCoCo, Selenium, JMeter, OWASP ZAP | – | EPL/Apache | Unit, intégration, UI, performance, sécurité. |
| **Monitoring** | Prometheus 2.x + Grafana 9.x + JMX exporter | – | Apache 2.0 | Métriques JVM, DB, HTTP. |
| **Documentation** | Javadoc, Markdown, Confluence (optional) | – | – | Génération Javadoc via Maven plugin. |
| **Packaging** | Maven Assembly | – | Apache 2.0 | `assembly.xml`, `assembly-sources.xml`, `assembly-doc.xml`. |

---

## 6. Stratégie de test et validation  

| Niveau | Type de test | Outils | Cible (coverage / seuil) | Commentaires |
|--------|--------------|--------|--------------------------|--------------|
| **Unitaire** | Classes POJO, Services, DAO | JUnit 4 + Mockito | **≥ 80 %** (JaCoCo) | Mocks du `DataSource`, `Castor` pour DAO. |
| **Intégration** | DAO + DB réelle (Oracle) | JUnit + Testcontainers (Oracle XE) | **≥ 70 %** | Vérifie les mappings Castor, requêtes `getAll`. |
| **Fonctionnel (Struts)** | Actions, Form validation | Selenium WebDriver + Struts‑Test‑Case | **≥ 70 %** scénarios critiques (création dossier, export) | Tests de navigation, messages d’erreur. |
| **Performance** | Temps de réponse, charge | JMeter (scripts `CreateDossier`, `Export`) | **RT ≤ 2 s** 95ᵉ percentile, **150 users** max | Tests en environnement *staging* identique à prod. |
| **Sécurité** | Scan vulnérabilités, tests d’injection | OWASP ZAP, SonarQube SAST | **Aucun** *Critical* / *High* non résolu | Tests d’authentification, CSRF, XSS, SQLi. |
| **Accessibilité** | Conformité RGAA/WCAG | axe‑core, WAVE | **AA** | Vérification des contrastes, ARIA, navigation clavier. |
| **Recette** | Validation métier (CCF) | JIRA + Test‑Run | **100 %** des cas d’usage validés | Mapping CCF → sous‑caractéristiques (voir tableau 7). |

### 6.1 Plan de tests automatisés (exemple)

```text
src/test/java/
 ├─ i2/application/causalis/dao/
 │    └─ GenericDaoTest.java                (unit)
 ├─ i2/application/causalis/service/
 │    ├─ AnneeServiceTest.java              (unit)
 │    ├─ GradeServiceTest.java              (unit)
 │    └─ ServiceServiceTest.java            (unit)
 ├─ i2/application/causalis/tool/
 │    ├─ BeanToolTest.java                  (unit)
 │    └─ GenericFetcherTest.java            (unit)
 ├─ i2/application/causalis/ws/
 │    ├─ client/
 │    │    ├─ WSClientEffectifTest.java      (unit + mock WS)
 │    │    └─ WSClientGradeTest.java
 │    ├─ converter/
 │    │    ├─ TrancheAgeHelperTest.java     (unit)
 │    │    └─ TranscodageGradeConverterTest.java
 │    └─ filter/
 │         └─ EffectifGradePredicateTest.java
 └─ integration/
      └─ DaoIntegrationTest.java             (real DB)
```

---

## 7. Supervision & métriques en production  

| KPI | Source | Seuil d’alerte | Tableau de bord |
|-----|--------|----------------|-----------------|
| **Disponibilité (Uptime)** | Prometheus (`up` metric) | < 99,9 % (warning) | Grafana “Service Availability”. |
| **Temps de réponse moyen** | JMX exporter (`http.server.requests.latency`) | > 2 s (critical) | Grafana “Response Time”. |
| **Taux d’erreur HTTP 5xx** | Prometheus `http_server_requests_total{status=~"5.."}` | > 0,5 % (warning) | Grafana “Error Rate”. |
| **CPU usage (JVM)** | `process_cpu_seconds_total` | > 80 % (warning) | Grafana “CPU”. |
| **Heap usage** | `jvm_memory_bytes_used{area="heap"}` | > 85 % (critical) | Grafana “Heap”. |
| **Nombre de threads actifs** | `jvm_threads_live` | > 200 (warning) | Grafana “Threads”. |
| **Transactions DB (TPS)** | `oracle_sessions_active` | < 10 TPS (warning) | Grafana “DB Throughput”. |
| **Couverture de tests** | SonarQube `coverage` | < 80 % (warning) | SonarQube dashboard. |
| **Vulnérabilités critiques** | SonarQube `security_hotspots` | > 0 (critical) | SonarQube “Security”. |

> **Alerting** : AlertManager envoie des notifications Slack & email aux équipes *DevOps* et *Support* dès que l’un des seuils est dépassé.

---

## 8. Documentation technique  

| Artefact | Format | Responsable | Publication |
|----------|--------|-------------|--------------|
| **Code source** | Javadoc (Maven `javadoc:jar`) | Développeurs | Artefact `causalismp-web‑javadoc.jar` sur Nexus. |
| **API WS** | Swagger (via `swagger‑core` – généré à partir des interfaces) | Architecte | Page Confluence *API WS*. |
| **Guide d’installation** | Markdown + PDF | DevOps | Repo `docs/installation/`. |
| **Guide d’exploitation** | Markdown | Support | Confluence *Run‑book*. |
| **Manuel utilisateur** | HTML (static) | UX | Accessible via `/aide.html`. |
| **Matrice de traçabilité CCF → Qualité** | Excel (ou MD table) | Chef de projet | Annexé au CST (section 9). |
| **Rapports SonarQube** | HTML (dashboard) | Qualité | Accessible via SonarQube URL. |
| **Diagrammes d’architecture** | PlantUML (source + PNG) | Architecte | `docs/architecture/`. |
| **Changelog** | Markdown (`CHANGELOG.md`) | Release manager | Tag Git. |

---

## 9. Gestion des dettes techniques  

| Dette | Description | Risque | Priorité | Plan de remboursement |
|-------|-------------|--------|----------|----------------------|
| **DAO générique incomplet** | `RechercheDossiersMaladiesDAO` vide. | Fonctionnalité manquante (recherche maladies). | **Moyen** | Implémenter dans le sprint 3, ajouter tests unitaires. |
| **Exception `TechnicalException` hérite de `Throwable`** | Empêche le catch `Exception` générique. | Risque de propagation non gérée. | **Élevé** | Refactoriser pour hériter de `Exception` (Sprint 1). |
| **Custom `ArrayList` extensions** (`ListeTableauEffectifs`, `ListeEnteteTableauEffectifs`) | Créent des objets “fantômes” qui peuvent masquer des bugs. | Complexité accrue, testabilité réduite. | **Moyen** | Remplacer par `List<Item>` avec `computeIfAbsent` (Sprint 2). |
| **Scripts SQL sans rollback** | Aucun script de retour en arrière. | Risque de migration irréversible. | **Élevé** | Ajouter des scripts `*_rollback.sql` pour chaque migration (Sprint 1). |
| **Hard‑coded JNDI name** (`Constantes.NOMDATASOURCE`) | Couplage fort au serveur d’applications. | Difficulté de portage. | **Faible** | Externaliser dans `application.properties` (Sprint 2). |
| **TagLib `StrutsOptionTag` substitue les guillemets** | Peut générer du HTML non‑valide si le texte contient déjà des apostrophes. | Problèmes d’accessibilité / XSS. | **Moyen** | Utiliser `StringEscapeUtils.escapeHtml4` (Sprint 3). |
| **Manque de tests d’interopérabilité WS** | Aucun test d’appel réel aux services externes. | Défaillance en production lors de la synchronisation. | **Élevé** | Créer des tests d’intégration avec *WireMock* (Sprint 2). |
| **Absence de gestion de version du schéma DB** | Scripts SQL versionnés mais pas de contrôle de version automatisé. | Incohérence entre environnements. | **Moyen** | Intégrer Flyway ou Liquibase (Sprint 4). |
| **Documentation d’installabilité fragmentaire** | Le README ne décrit pas les pré‑requis (JDK, Oracle, JNDI). | Risque d’échec d’installation. | **Faible** | Rédiger un guide d’installation complet (Sprint 1). |

> **Suivi** : chaque dette possède une *user story* dans le backlog JIRA, avec *definition of done* incluant code, tests, documentation et revue.

---

## 10. Matrice de traçabilité CCF → Critères de Qualité  

| # | Fonctionnalité CCF (extraits du backlog) | Sous‑caractéristique ISO 25010 | Métrique associée | Objectif | Commentaire |
|---|-------------------------------------------|-------------------------------|-------------------|----------|--------------|
| F1 | Saisie d’un **dossier accident** (création, validation). | **Aptitude fonctionnelle – Complétude** | % d’exigences implémentées (CCF) | ≥ 95 % | Mappé aux actions `DossierAccidentService`. |
| F2 | Saisie d’un **dossier maladie professionnelle**. | **Aptitude fonctionnelle – Exactitude** | Taux d’erreurs de saisie détectées | ≤ 1 % | Validation côté Form (`DateValidator`). |
| F3 | Export d’un **dossier** au format OpenOffice. | **Performance – Capacité** | Nombre d’utilisateurs simultanés exportant | ≥ 150 | Test JMeter `Export`. |
| F4 | Consultation des **statistiques par grade**. | **Utilisabilité – Opérabilité** | Nombre de clics pour accéder à la statistique | ≤ 5 | Action `StatistiquesAction`. |
| F5 | Synchronisation des **grades** avec le SI *Rehucit*. | **Sécurité – Confidentialité** | Score d’audit OWASP (exposition des WS) | ≥ 90 % | `SynchronizeService` + `TranscodageGradePredicate`. |
| F6 | Gestion des **référentiels** (Grade, Service, Statut). | **Maintenabilité – Modularité** | Couplage / Cohésion (Sonar) | Couplage ≤ 0,2, Cohésion ≥ 0,8 | `ReferenceService<T>`. |
| F7 | Accès multi‑plateforme (Windows, Linux) via le **WAR**. | **Portabilité – Adaptabilité** | Environnements supportés | ≥ 3 | Dockerfile + Ansible playbook. |
| F8 | **Disponibilité** du service 24/7. | **Fiabilité – Disponibilité** | Uptime % (Prometheus) | ≥ 99,9 % | SLA défini. |
| F9 | **Authentification** via Cerbere/LDAP. | **Sécurité – Authenticité** | Méthodes d’authentification utilisées | LDAP + SSO | `Cerbere` integration. |
| F10| **Accessibilité** du formulaire de création (WCAG AA). | **Utilisabilité – Accessibilité** | Niveau de conformité RGAA/WCAG | AA | Audit Axe. |

> La matrice complète (incluant toutes les 31 sous‑caractéristiques) est disponible en annexe *X* (Excel).  

---

## 11. Annexes  

| Annexe | Contenu |
|--------|---------|
| **A** | Diagrammes PlantUML (architecture, séquence de synchronisation). |
| **B** | Tableaux de bord Grafana (captures d’écran). |
| **C** | Rapport SonarQube (extrait). |
| **D** | Script JMeter (création dossier, export). |
| **E** | Check‑list d’audit de sécurité (OWASP). |
| **F** | Exemple de fichier `application.properties` (production). |
| **G** | Historique des versions (CHANGELOG). |
| **H** | Matrice de traçabilité détaillée (XLSX). |

---

## 12. Conclusion  

Le présent **Cahier des Spécifications Techniques** formalise les exigences de qualité du produit *causalismp* conformément à ISO/IEC 25010:2023. Les objectifs chiffrés, les métriques de mesure, la stratégie de tests, le monitoring en production et le plan de gestion des dettes techniques offrent un cadre robuste pour :

* **Assurer la conformité** aux exigences fonctionnelles et non‑fonctionnelles.  
* **Garantir la visibilité** continue de la qualité via SonarQube et les KPI de production.  
* **Faciliter l’évolution** du produit grâce à une architecture modulaire et une documentation à jour.  

Le suivi des indicateurs et la réévaluation périodique (toutes les 2 semaines) permettront d’ajuster les seuils et de réduire la dette technique, assurant ainsi la pérennité du système sur le long terme.  

---  

*Document généré le 28 avril 2024, révisé par l’équipe d’architecture logicielle.*  