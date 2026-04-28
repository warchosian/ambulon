# 📄 Cahier des Spécifications Techniques (CST) – **SIREINES**  
**Version : 2.5.20 (12 mars 2024)**  
**Date : 27 avril 2026**  

---  

## 1️⃣ Introduction & Contexte Qualité  

| Élément | Description |
|---|---|
| **Projet** | SIREINES – Système d’information de recensement et de suivi des qualifications d’experts et spécialistes scientifiques et techniques. |
| **Périmètre** | Application web Java/J2EE + services REST + BIRT + PostgreSQL, déployée sur Docker (IaaS ECO4) – environnements **Recette**, **Pré‑prod**, **Prod**. |
| **Objectifs de qualité** | Garantir la disponibilité, la conformité aux exigences légales (RGPD, CNIL), la maintenabilité et la performance d’une application à forte charge de consultation (84 % SELECT, 10 % INSERT, 4 % UPDATE) tout en supportant les exigences d’audit et de traçabilité. |
| **Références fonctionnelles (CCF)** | – Spécifications fonctionnelles du module « Gestion des dossiers » (création, recherche, mise à jour, export). <br>– Spécifications d’import / export (CSV, BIRT). <br>– Gestion des utilisateurs, authentification, droits (role R_ADMIN). <br>– Reporting BIRT (statistiques, pyramide d’âge, fréquence mots‑clés). |
| **Méthodologie d’évaluation** | - **Mesure automatisée** (SonarQube, JMeter, Gatling, JUnit/Mockito, JaCoCo). <br>- **Audits manuels** (revues de code, tests d’acceptation, revues de sécurité OWASP). <br>- **Tableaux de bord** (Grafana + Prometheus) pour le suivi en production. |

---  

## 2️⃣ Modèle de Qualité ISO / IEC 25010  

```
QUALITÉ DU PRODUIT LOGICIEL
│
├─ 1. Aptitude fonctionnelle
├─ 2. Performance & efficacité
├─ 3. Compatibilité
├─ 4. Utilisabilité
├─ 5. Fiabilité
├─ 6. Sécurité
├─ 7. Maintenabilité
└─ 8. Portabilité
```

---  

## 3️⃣ Spécifications détaillées par caractéristique  

> **Notation** : chaque sous‑caractéristique possède : *Métrique* – *Objectif* – *Méthode de mesure* – *Justification technique*.

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Complétude fonctionnelle** | % de fonctions implémentées vs exigences CCF | ≥ 98 % | Mapping CCF → classes/Endpoints (outil *ArchUnit*). | Le modèle MVC + Struts 2 assure un découpage clair des actions. |
| **Exactitude fonctionnelle** | Taux d’erreurs de calcul/traitement (ex : statistiques BIRT) | ≤ 0,5 % | Tests unitaires + tests d’intégration (JUnit + DBUnit) sur chaque service. | Utilisation de *Vertigo* (Dynamo) pour la couche métier, garantissant la cohérence des DTO/DT. |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | ≥ 4,2/5 | Questionnaire post‑déploiement (Google Forms) + analyse moyenne. | UI Struts 2 avec thèmes *xhtml* / *simple* et components BIRT, déjà éprouvés. |

### 3.2 Performance & efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Comportement temporel** | 95ᵉ percentile du temps de réponse (GET / dossier) | ≤ 1,5 s | Gatling/JMeter scripts (10 k transactions simultanées). | Tomcat 7 + JDBC optimisé, pool de connexions HikariCP (via Spring). |
| **Utilisation des ressources** | CPU % et RAM % sous charge nominale (100 utilisateurs) | CPU ≤ 70 %, RAM ≤ 75 % du conteneur | Prometheus + Grafana (exporters JMX). | Docker + cgroup limit (2 vCPU, 2 GiB) – paramétrage *JAVA_OPTS* – GC G1. |
| **Capacité** | Nombre d’utilisateurs concurrents supportés (sans dégradation > 10 %) | ≥ 250 utilisateurs | Test de charge progressif + monitoring latence. | Architecture « stateless » (session externalisée via Redis / Docker‑network). |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Cohérence** | % de conformité aux standards (HTML5, CSS3, WCAG 2.1) | ≥ 90 % | *axe‑core* (accessibilité) + *W3C validator*. | Thèmes *xhtml* respectent les spécifications W3C, ajout d’attributs ARIA. |
| **Interopérabilité** | Nombre de formats d’échange supportés (CSV, JSON, BIRT XML) | ≥ 3 (CSV, JSON‑REST, BIRT) | Tests d’import/export automatisés (CI). | Services REST (Jackson) + export CSV via *DisplayTag* & *BirtManager*. |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Appréhensibilité** | Temps de formation (h) pour tâches de base | ≤ 2 h | Séances de test avec utilisateurs finaux (Minitab). | Interface Struts 2 + templates *xhtml* simplifiés, libellés clairs. |
| **Apprenabilité** | Taux de réussite première tentative (sans aide) | ≥ 85 % | Test de scénario « Créer dossier » (10 participants). | Guides contextuels (tooltips) intégrés via *tooltip.ftl*. |
| **Opérabilité** | Nombre d’actions (clics) pour créer un dossier | ≤ 7 clics | Analyse des logs UI (Google Analytics). | Navigation à deux niveaux (menu → formulaire). |
| **Esthétique** | Score SUS (System Usability Scale) | ≥ 68/100 | Questionnaire SUS. | CSS Bootstrap + custom *sireines.css* assure un rendu moderne. |
| **Accessibilité** | Niveau de conformité RGAA / WCAG | Niveau AA minimum | *axe‑core* + audit manuel. | Utilisation de balises ARIA, contraste > 4.5 : 1. |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Maturité** | Densité de défauts (défauts/KLOC) | ≤ 0,5 / KLOC | SonarQube + historique bugs JIRA. | Code Java ≥ 2 kLOC, couverture ≥ 80 % (JaCoCo). |
| **Disponibilité** | % de temps de service (Uptime) | ≥ 99,90 % (SLA) | Monitoring *uptime* via Grafana + Alertmanager. | Redondance du conteneur d’application (Docker‑compose replicas = 2). |
| **Tolérance aux fautes** | Temps de récupération (RTO) après arrêt du conteneur | ≤ 30 s | Tests de bascule (docker‑restart). | Docker restart‑policy = always, health‑checks. |
| **Récupérabilité** | Point de récupération (RPO) des données BDD | ≤ 5 min | Tests de restauration à partir du volume Docker. | Volume persistant *sireines_db_sireines_vol* + sauvegarde quotidienne via *pg_dump* (cron). |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Confidentialité** | Score d’audit OWASP ASVS Level 2 | ≥ 80 % | Scan automatisé (OWASP ZAP) + revue manuelle. | Spring Security + JWT pour l’authentification, contraintes de rôle (R_ADMIN). |
| **Intégrité** | % de contrôles d’intégrité (hash SHA‑256) sur fichiers de configuration | 100 % | Script d’intégrité au démarrage. | Docker‑image signée (Docker Content Trust). |
| **Non‑répudiation** | Journalisation des actions critiques (audit log) | 100 % des actions (CRUD) | ELK stack (Filebeat → Logstash → Kibana). | *log4j.xml* configuré en mode *ASYNC* avec MDC. |
| **Responsabilité** | Couverture de traçage d’audit (ID session, IP) | 100 % | Analyse des logs via Kibana. | Filtre d’audit Spring Security. |
| **Authenticité** | Méthodes d’authentification utilisées | 2FA (mot de passe + OTP) | Tests d’intrusion (hydra). | Integration avec *Keycloak* (ou LDAP) via Spring Security. |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Modularité** | Couplage (CBO) & Cohésion (LCOM) | CBO ≤ 5, LCOM ≤ 0.2 | SonarQube (metrics “Coupling Between Objects”). | Architecture en modules Vertigo (Dynamo + Search) + Struts 2 + Spring. |
| **Réutilisabilité** | % de composants réutilisables (services) | ≥ 60 % | Analyse des dépendances (Maven Dependency‑Tree). | Services *Agents*, *Dossiers*, *Extractions* exposés via interfaces. |
| **Analysabilité** | Complexité cyclomatique moyenne | ≤ 10 | SonarQube (Cyclomatic Complexity). | Méthodes découpées en petites fonctions, tests unitaires. |
| **Modifiabilité** | Temps moyen de modification (h) d’une règle métier | ≤ 2 h | Historique JIRA (temps passé). | Utilisation de *Vertigo* DSL (kpr/ksp) pour la description des modèles. |
| **Testabilité** | Couverture de tests unitaires | ≥ 80 % | JaCoCo report. | Projet Maven multi‑module, tests automatisés intégrés au pipeline CI. |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Objectif | Méthode de mesure | Justification technique |
|---|---|---|---|---|
| **Adaptabilité** | Nombre d’environnements supportés (Docker‑Linux, Docker‑Windows) | ≥ 2 | Déploiement sur VM de test Windows + Linux. | Dockerfile multi‑stage, images basées sur `tomcat:7.0.108-jdk8`. |
| **Installabilité** | Temps d’installation (minutes) sur poste de travail | ≤ 10 min | Script d’installation (`docker‑compose up -d`). | Docker‑compose automatisé, .env pré‑configuré. |
| **Remplaçabilité** | % de dépendances compatibles avec des alternatives (ex : PostgreSQL vs MySQL) | ≥ 70 % | Analyse des abstractions DAO (Vertigo). | DAO basés sur JPA / JDBC, pas de code SQL propriétaire. |

---  

## 4️⃣ Architecture Technique  

### 4.1 Diagramme de composants (simplifié)

```
+-------------------+          +--------------------+          +-------------------+
|  Utilisateur Web  | <--HTTP--> |  Tomcat (sireines) | <--JDBC--> | PostgreSQL (sireines-db) |
+-------------------+          +--------------------+          +-------------------+
        ^                               ^                              ^
        |                               |                              |
        |                               |                              |
        |    +-------------------+      |    +-------------------+     |
        +----| Spring Security  |<-----+----| Vertigo/Dynamo    |-----+
             +-------------------+           +-------------------+
                     ^                                 ^
                     |                                 |
        +------------+------------+        +------------+------------+
        |  Struts2 (Actions)      |        |  BIRT (Reporting)      |
        +------------------------+        +------------------------+
```

* **Tomcat 7** : conteneur d’application, version compatible Java 8 (JDK 8).  
* **Spring Security** : gestion des rôles (R_ADMIN) et du filtre d’authentification.  
* **Struts 2** : framework MVC, génération des pages via *Freemarker* (`*.ftl`).  
* **Vertigo /Dynamo** : couche métier (services, DAO, recherche ElasticSearch).  
* **BIRT 4.3** : génération de rapports PDF/HTML (statistiques, pyramide d’âge).  
* **PostgreSQL 14‑alpine** : base de données relationnelle, volumes Docker persistants.  
* **Docker‑Compose** : orchestration (3 containers + 2 volumes).  
* **Prometheus + Grafana** : supervision (CPU, RAM, latence HTTP, health‑checks).  
* **ELK Stack** : agrégation et recherche de logs (audit, sécurité).  

### 4.2 Justification des choix  

| Critère | Décision | Impact Qualité |
|---|---|---|
| **Performance** | Tomcat + JDK 8 + HikariCP pool | Temps de réponse < 1,5 s. |
| **Fiabilité** | Docker‑restart = always, health‑checks | RTO ≤ 30 s, haute disponibilité. |
| **Sécurité** | Spring Security + JWT + OWASP‑ZAP | Conformité ASVS L2, auditabilité. |
| **Maintenabilité** | Architecture modulaire Vertigo + Struts 2 | Couplage faible, tests unitaires ≥ 80 %. |
| **Portabilité** | Docker multi‑stage, image `tomcat:7.0.108-jdk8` | Déploiement sur tout OS supportant Docker. |
| **Utilisabilité** | Bootstrap + Freemarker themes *xhtml* | Score SUS ≥ 68, conformité AA WCAG. |

---  

## 5️⃣ Stack Technologique Qualité  

| Niveau | Technologie | Version | Raison Qualité |
|---|---|---|---|
| **Langage** | Java | 8 (LTS) | Stabilité, large écosystème, support par SonarQube. |
| **Web Container** | Tomcat | 7.0.108 | Légèreté, compatibilité J2EE, mature. |
| **Framework MVC** | Struts 2 | 2.5.x | Gestion centralisée des actions, support des thèmes Freemarker. |
| **DI / Sécurité** | Spring Core + Spring Security | 5.x | Injection de dépendances, gestion fine des rôles. |
| **Moteur Métier** | Vertigo /Dynamo | 3.x | Génération de code (kpr/ksp), recherche ElasticSearch intégrée. |
| **Recherche** | ElasticSearch (embedded) | 7.x | Recherche full‑text rapide sur les mots‑clés. |
| **Base de données** | PostgreSQL | 14‑alpine | Fiabilité, performances SELECT‑intensives, support JSON. |
| **Reporting** | BIRT | 4.3 | Génération de rapports PDF/HTML, intégration via *BirtManager*. |
| **Conteneurisation** | Docker + Docker‑Compose | 20.10+ | Portabilité, isolation, gestion des volumes. |
| **CI/CD** | GitLab CI | – | Pipelines automatisés (build, test, scan, déploiement). |
| **Qualimétrie** | SonarQube, JaCoCo, JMeter, Gatling, OWASP ZAP | – | Mesure continue des indicateurs ISO 25010. |
| **