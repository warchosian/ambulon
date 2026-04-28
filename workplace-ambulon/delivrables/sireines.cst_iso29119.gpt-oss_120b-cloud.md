# Cahier des Spécifications Techniques – Tests  
**Projet : SIREINES**  
**Version : 2.5.20 (12 / 03 / 2024)** – Dernière mise à jour : 10 / 03 / 2026 02:56 01  

---

## 1. Introduction  

| Élément | Valeur |
|---|---|
| **Nom du produit** | SIREINES |
| **Portée** | Application métier web (Java /J2EE) permettant la gestion des demandes de qualification d’experts et spécialistes scientifiques et techniques. |
| **Environnement cible** | Docker (Tomcat 7 + PostgreSQL 14) – déploiements : Développement, Recette, Pré‑production, Production (IaaS ECO4 – Paris La Défense). |
| **Références** | - ISO/IEC/IEEE 29119‑1 à ‑6 (série complète) <br> - Documentation interne (README, .gitignore, Dockerfile, scripts SQL) <br> - “Home.md” (description fonctionnelle) <br> - “DeploiementApplicatif.md” (processus de mise en production) |
| **Objectif du CST** | Décrire la stratégie, la planification, la conception, l’exécution et le suivi des tests afin de garantir la conformité fonctionnelle, la stabilité, la performance, la sécurité et la maintenabilité de SIREINES conformément aux exigences métier et aux bonnes pratiques ISO 29119. |

---

## 2. Glossaire  

| Acronyme | Signification |
|---|---|
| **CST** | Cahier des Spécifications Techniques (tests) |
| **SUT** | System Under Test (SIREINES) |
| **UI** | User Interface |
| **API** | Application Programming Interface |
| **BDD** | Base de données (PostgreSQL) |
| **CI** | Continuous Integration |
| **CD** | Continuous Delivery |
| **IaaS** | Infrastructure as a Service |
| **BIRT** | Business Intelligence and Reporting Tools |
| **DAO** | Data Access Object |
| **DTO** | Data Transfer Object |
| **JVM** | Java Virtual Machine |
| **JDBC** | Java Database Connectivity |
| **KPI** | Key Performance Indicator |
| **TDD** | Test‑Driven Development |
| **CI / CD pipeline** | GitLab CI (fichiers *.gitlab‑ci.yml) |
| **SonarQube** | Plateforme d’analyse de la qualité du code |
| **JaCoCo** | Outil de mesure de couverture de code Java |
| **Selenium** | Framework d’automatisation de tests UI |
| **REST‑Assured** | Framework de tests d’API REST |
| **JUnit 5** | Framework de tests unitaires Java |
| **Mockito** | Framework de mock pour tests unitaires |
| **Docker‑Compose** | Orchestration des conteneurs (docker‑compose.yml) |
| **Bastion** | Serveur d’accès sécurisé (SSH) |
| **Cerbère** | Gestion des droits d’accès (authentification SSO) |

---

## 3. Stratégie de Test (ISO 29119‑3 – Test Strategy)

### 3.1 Contexte et objectifs  

| Objectif | Description | Métrique cible |
|---|---|---|
| **Couverture fonctionnelle** | Vérifier que chaque fonctionnalité décrite dans les exigences (REQ‑001 … REQ‑020) fonctionne correctement. | **≥ 95 %** de scénarios fonctionnels exécutés avec succès |
| **Stabilité & régression** | S’assurer que les nouvelles livraisons n’introduisent pas de régressions. | **0 défaut critique** en production, **≤ 2 défauts majeurs** en recette |
| **Performance** | Temps de réponse < 2 s pour les pages critiques (Accueil, Recherche dossier, Rapport BIRT). | **90 %** des transactions < 2 s, **≤ 5 %** > 2 s |
| **Sécurité** | Vérifier le respect des exigences de confidentialité (RGPD) et de contrôle d’accès (Cerbère). | **Aucun** défaut de type « Injection », « Broken Auth », « Sensitive Data Exposure » (OWASP Top 10) |
| **Compatibilité** | Fonctionnement sur les navigateurs supportés (Chrome ≥ 90, Edge ≥ 90, Firefox ≥ 88). | **100 %** des scénarios UI valides sur chaque navigateur |
| **Automatisation** | Automatiser les tests de régression UI et API. | **≥ 80 %** des cas de régression automatisés (Selenium + REST‑Assured) |
| **Qualité du code** | Maintenir la dette technique sous contrôle. | **Couverture de code ≥ 80 %** (JaCoCo) + **Qualité Sonar ≥ A** |

### 3.2 Risques & Mitigation  

| Risque | Probabilité | Impact | Stratégie de mitigation |
|---|---|---|---|
| **R‑01 : Défaillance du moteur de recherche (Elasticsearch)** | Moyen | Élevé (perte de la fonctionnalité de recherche dossier) | Tests de charge et de disponibilité du service SearchManager (JUnit + Testcontainers). |
| **R‑02 : Mauvaise gestion des droits Cerbère** | Faible | Critique (exposition de données) | Tests d’authentification et d’autorisation (OWASP ZAP + scénarios SSO). |
| **R‑03 : Migration de la base de données (scripts SQL)** | Moyen | Élevé (perte de données) | Tests d’intégrité post‑migration (scripts DBUnit). |
| **R‑04 : Déploiement Docker non‑reproductible** | Faible | Moyen (downtime) | Validation du `docker‑compose.yml` via `docker‑compose config` et tests d’intégration (Testcontainers). |
| **R‑05 : Rapports BIRT lourds** | Moyen | Moyen (temps de génération > 10 s) | Tests de performance sur les rapports (JMeter). |

### 3.3 Approche générale  

| Niveau de test | Description | Outils | Livrables |
|---|---|---|---|
| **Tests unitaires** | Vérifient chaque classe/ méthode (services, DAO, utils). | JUnit 5, Mockito, JaCoCo | Rapport de couverture, logs JUnit |
| **Tests d’intégration** | Interaction entre modules (DAO ↔ DB, Service ↔ SearchManager). | Testcontainers (PostgreSQL, Elasticsearch), JUnit, DBUnit | Rapport d’intégration, scripts de jeu de données |
| **Tests fonctionnels (UI)** | Parcours utilisateurs (login, création dossier, recherche, export BIRT). | Selenium WebDriver + JUnit, Maven‑Surefire, Allure | Rapport Allure, vidéos d’exécution |
| **Tests API (REST)** | End‑points Struts2 (ex. `/Export.do`). | REST‑Assured, JUnit | Rapport JSON, Swagger (si présent) |
| **Tests de performance** | Charge sur pages critiques, génération de rapports, recherche full‑text. | JMeter, Gatling | Rapport de charge, seuils de performance |
| **Tests de sécurité** | Scan OWASP, tests d’injection, contrôle d’accès. | OWASP ZAP, SonarQube (SAST) | Rapport de vulnérabilité |
| **Tests de non‑régression** | Exécution complète du cycle de régression à chaque livraison. | Selenium Grid, Docker‑Compose (environnement REC) | Rapport de régression, KPI de stabilité |

### 3.4 Techniques de test (ISO 29119‑4)  

| Technique | Niveau d’application | Exemple dans SIREINES |
|---|---|---|
| **Partitionnement en classes d’équivalence** | Fonctionnel | Champs de formulaire `emailContact` (valide / invalide / vide) |
| **Boundary Value Analysis** | Fonctionnel | Dates de création de dossier (`dateRecDebut`, `dateRecFin`) – limites du format `yyyy‑MM‑dd`. |
| **Tests de transition d’états** | Fonctionnel | Workflow d’un dossier : `EN_COURS → VALIDÉ → ARCHIVÉ`. |
| **Tables de décision** | Fonctionnel | Filtre d’extraction (structures, années, mots‑clé) – combinaisons de critères. |
| **Tests basés sur l’expérience (exploratoire)** | Non‑fonctionnel | Exploration des menus dynamiques Struts2, vérification des libellés. |
| **Tests de chemin (MC/DC)** | Unitaire | Méthodes de calcul de l’indice de performance (`calculateScore()`). |
| **Tests de charge (Load/Stress)** | Performance | Simuler 50 utilisateurs simultanés sur la page d’accueil et la recherche. |
| **Tests de sécurité (OWASP Top 10)** | Sécurité | Injection SQL dans le champ `searchTerm`, XSS dans les commentaires de dossier. |
| **Tests de compatibilité** | Non‑fonctionnel | Vérifier le rendu sur Chrome 91, Edge 92, Firefox 89, et sur mobile (responsive). |

---

## 4. Plan de Test (ISO 29119‑3 – Test Plan)

### 4.1 Portée détaillée  

| Fonctionnalité | Modules concernés | Référence CCF (exemple) |
|---|---|---|
| **Authentification & Gestion des droits** | `ApplicationServletContextListener`, `Cerbère` (SSO), `SecurityFilter` | REQ‑001 |
| **Gestion des dossiers** | Controllers `Dossier*Action`, Services `DossiersServices`, DAO `dossiersDao.ksp` | REQ‑002 |
| **Recherche de dossiers** | `SearchManagerInitializer`, Elasticsearch plugin | REQ‑003 |
| **Import de fichiers** | `ImportFichierAction`, `ImportsServices` | REQ‑004 |
| **Export & génération de rapports BIRT** | `BirtManager`, `Report` | REQ‑005 |
| **Export de données (CSV)** | `CsvExport`, `Export` | REQ‑006 |
| **Administration (cerbère, paramétrage)** | `ParamManager`, `cerbère` UI | REQ‑007 |
| **API REST (si applicable)** | `struts.xml` actions exposées | REQ‑008 |
| **Non‑fonctionnel** | Tous | REQ‑009 … REQ‑020 (performance, sécurité, compatibilité, etc.) |

> **Note** : les exigences (REQ‑001 … REQ‑020) sont définies dans le référentiel interne de la DSI et seront reliées aux cas de test dans la matrice de traçabilité (section 7).

### 4.2 Critères d’entrée  

| Condition | Description |
|---|---|
| **Code** | Branch `recette` (ou `preprod` / `prod`) compilée avec succès (`mvn clean verify`). |
| **Environnement** | Docker‑Compose déployé : `sireines-app`, `sireines-db`, `sireines-pgadmin`. |
| **Données de test** | Jeu de données fourni (`sireines-db‑dump‑<date>.sql`) chargé dans le container DB. |
| **Outils** | Maven 3.8+, Docker 20+, Java 11, Selenium 4, JMeter 5, OWASP ZAP. |
| **Accès** | Bastion SSH configuré, variables d’environnement `.env` disponibles. |

### 4.3 Critères de sortie  

| Condition | Description |
|---|---|
| **Couverture code** | **≥ 80 %** (JaCoCo) – excluant les classes générées (`*Generated*`). |
| **Défauts** | Aucun défaut **Critique** ou **Bloquant** en production. <br> Maximum **2** défauts majeurs en recette (doivent être résolus ou justifiés). |
| **Performance** | 90 % des transactions < 2 s, aucun pic > 5 s. |
| **Sécurité** | Aucun défaut OWASP Top 10 ≥ Medium. |
| **Rapport** | Rapport de test complet (Allure) généré, tableau de traçabilité exigences ↔ cas de test validé, KPI de stabilité ≥ 95 %. |
| **Livrable** | Pack `test‑report‑<date>.zip` (rapports, logs, artefacts). |

### 4.4 Ressources  

| Rôle | Responsable | Compétences |
|---|---|---|
| **Test Lead** | *Nom : [À définir]* | ISO 29119, gestion de projet, coordination CI/CD. |
| **Test Engineer (UI)** | *Nom* | Selenium, HTML/JS, Struts2, BIRT. |
| **Test Engineer (API/Intégration)** | *Nom* | REST‑Assured, Testcontainers, PostgreSQL, Elasticsearch. |
| **Test Engineer (Performance)** | *Nom* | JMeter, analyse de logs. |
| **Security Analyst** | *Nom* | OWASP ZAP, SAST (SonarQube). |
| **DevOps** | *Nom* | Docker, GitLab‑CI, Maven, SonarQube. |
| **MOA** | *Nom* | Validation fonctionnelle, exigences métier. |

### 4.5 Calendrier (exemple)  

| Sprint | Activité | Dates |
|---|---|---|
| **S‑0** | Pré‑préparation (environnements, jeux de données) | J‑15 → J‑12 |
| **S‑1** | Tests unitaires & intégration (dev) | J‑11 → J‑7 |
| **S‑2** | Tests fonctionnels UI (recette) | J‑6 → J‑3 |
| **S‑3** | Tests de performance & sécurité | J‑2 → J‑1 |
| **S‑4** | Validation finale, livrable | J 0 (déploiement) |

> **J** = jour de mise en production prévue.  

---

## 5. Conception des Tests (ISO 29119‑4 – Test Design)

### 5.1 Techniques fonctionnelles  

| Technique | Description | Artefact produit |
|---|---|---|
| **Partition d’équivalence** | Définir les classes valides / invalides pour chaque champ de formulaire (ex. `emailContact`). | Table `TC‑FE‑01` (voir section 6). |
| **Boundary Value** | Tester les limites de dates, tailles de texte (`libelle` ≤ 250 car). | Table `TC‑FE‑02`. |
| **Table de décision** | Décision d’export (type = « PDF », « CSV », « XLS ») → actions BIRT. | Table `TC‑FE‑03`. |
| **Scénario d’usage** | Parcours complet : connexion → recherche dossier → export BIRT → déconnexion. | Table `TC‑SC‑01`. |
| **Exploratoire** | Session d’exploration guidée sur les menus Struts2 (dynamic menu). | Rapport d’exploration (PDF). |

### 5.2 Techniques non‑fonctionnelles  

| Technique | Description | Outil |
|---|---|---|
| **Load / Stress** | 50 utilisateurs simultanés pendant 10 min sur la page de recherche. | JMeter (script `search_load.jmx`). |
| **Spike** | Augmentation soudaine à 200 utilisateurs pendant 30 s. | JMeter. |
| **Endurance** | Test de 8 h de requêtes d’import de fichiers. | JMeter + monitoring (cAdvisor). |
| **Security – OWASP‑ZAP** | Scan complet de l’URL `https://sireines.recette…` | ZAP, rapports HTML. |
| **Compatibilité** | Tests UI sur Chrome, Edge, Firefox, Safari (via Selenium Grid). | Selenium‑Grid. |
| **Usabilité** | Session de test avec 5 utilisateurs métier – temps moyen de tâche < 30 s. | Observations + questionnaire SUS. |

### 5.3 Matrice de couverture des techniques  

| Technique | % de cas de test couverts |
|---|---|
| Partition d’équivalence | 30 % |
| Boundary Value | 20 % |
| Table de décision | 15 % |
| Scénario d’usage | 20 %