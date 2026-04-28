# 📄 Cahier des Spécifications Techniques (CST) – **SIREINES**  
**Projet :** SIREINES – Répertoire national des experts et spécialistes scientifiques et techniques  
**Version :** 2.5.20 (12 mars 2024) – 2024‑03‑27  
**Auteur :** [Nom du Test‑Lead] – Direction Qualité / DSI CGDD‑SRIE‑AST2  

> **Objectif** – Ce document décrit la stratégie, le plan, les techniques, les cas de test, les procédures et les indicateurs de suivi des tests du système SIREINES, conformément à la norme **ISO/IEC/IEEE 29119** (séries 1‑6 + 11).  

---  

## 1️⃣  Stratégie de test (ISO 29119‑3 §5)

### 1.1 Contexte et objectifs de test  

| Élément | Description |
|---|---|
| **Périmètre fonctionnel** | Gestion des dossiers de qualification, import/export de fichiers, génération de rapports BIRT, recherche Elasticsearch, administration (Cerbère), interface Struts2 (HTML / FTL). |
| **Périmètre non fonctionnel** | Performance (temps de réponse < 2 s), sécurité (OWASP Top 10, protection des données à caractère personnel – RGPD), disponibilité (99,5 % / mois), compatibilité navigateurs (Chrome ≥ 90, Edge, Firefox), reproductibilité des builds Docker, conformité aux exigences légales (déclaration CNIL n°1034232). |
| **Objectifs mesurables** | • 95 % de couverture fonctionnelle (exigences CCF) <br>• 80 % de couverture du code (branches) <br>• 0 défaut critique en production <br>• Taux de fuite ≤ 5 % (défauts détectés en prod) <br>• Temps moyen de résolution (MTTR) ≤ 2 jours |
| **Contraintes** | • Environnement Docker (Tomcat 7, PostgreSQL 14, Elasticsearch 7) <br>• Déploiement via CI GitLab (pipeline Maven / Docker) <br>• Données sensibles (DACP) – anonymisation obligatoire <br>• Accès limité aux environnements Recette/Pre‑prod via Bastion (SSH) |
| **Dépendances** | • Artefacts Maven (`sireines-web.war`) <br>• Scripts d’initialisation DB (`crebas.sql`, `init.sql`) <br>• Configuration Cerbère (ID 546/564) <br>• Outils de reporting BIRT 4.3, PrinceXML (PDF) |

### 1.2 Risques et mitigation  

| Risque | Probabilité | Impact | Stratégie de mitigation |
|---|---|---|---|
| **R1 – Perte d’intégrité des données (DACP)** | Moyenne | Critique | Tests d’anonymisation (`CommonServices.sendMail`, `StringUtils.isValidCriteria`) ; validation des contraintes DB (FK, uniques) ; audit de conformité RGPD en pre‑prod. |
| **R2 – Défaillance du moteur de recherche** | Faible | Élevé | Tests de régression des index Elasticsearch (`SearchManagerInitializer`) ; jeu de données de test (`extractions`), test de charge sur requêtes de recherche. |
| **R3 – Incompatibilité du WAR avec Tomcat 7** | Moyenne | Élevé | Tests d’intégration du conteneur Docker (`docker-compose up -d`) ; validation du `Dockerfile` (COPY, unzip). |
| **R4 – Temps de réponse > 2 s sous charge** | Moyenne | Élevé | Tests de performance (JMeter) sur scénarios d’extraction (extraction 08, 09). |
| **R5 – Vulnérabilités OWASP Top 10** | Faible | Critique | Analyse statique (SonarQube, SpotBugs) ; tests de sécurité (OWASP ZAP) sur les points d’entrée Struts2. |
| **R6 – Déploiement erroné (pipeline CI)** | Faible | Moyen | Validation du pipeline GitLab (jobs `maven‑install`, `docker‑build`, `docker‑compose`) ; tests d’intégration continue (CI‑TC). |

### 1.3 Approche générale  

| Niveau de test | Types de test | Technique(s) principale(s) | Outils |
|---|---|---|---|
| **Unitaire** | Tests de classes Java (services, utils, contrôleurs) | *White‑box* – couverture de code, tests de chemin, MC/DC (si critique) | JUnit 5, Mockito, JaCoCo, Maven Surefire |
| **Intégration** | Interaction entre modules (service ↔ DAO, DAO ↔ PostgreSQL, SearchManager ↔ Elasticsearch) | *White‑box* – tests de contrats, tests de base de données | Spring Test, Testcontainers (PostgreSQL, Elasticsearch), Flyway |
| **Système** | Scénarios bout‑en‑bout (UI Struts2, BIRT, import / export) | *Black‑box* – partitionnement en classes d’équivalence, BVA, tables de décision | Selenium WebDriver (Chrome), Cucumber BDD, RestAssured (API éventuelles) |
| **Acceptation** | Validation métier (extraction rapports, qualification, gestion dossiers) | *Exploratoire* + *Decision Table* (ex : `ChoixReferentielAction`) | TestRail (traceability), scripts Cucumber |
| **Non‑fonctionnel** | Performance, sécurité, compatibilité, fiabilité | *Load/Stress* (JMeter), *Vulnerability Scan* (OWASP ZAP), *Cross‑browser* (BrowserStack) | JMeter, ZAP, BrowserStack, SonarQube |
| **Régression** | Suite automatisée de tous les tests ci‑dessus | *Sélection par risque* (priorité = Critical/High) | Jenkins + Maven + Docker‑Compose (pipeline `regression`) |

> **Note** – La stratégie s’appuie sur le **risk‑based testing** (ISO 29119‑5) : les tests critiques (ex : import de fichiers, génération de rapports BIRT, recherche) sont exécutés à chaque build ; les tests à faible risque (ex : pages statiques) sont exécutés en nightly.

---  

## 2️⃣  Plan de test (ISO 29119‑3 §6)

| Élément | Détails |
|---|---|
| **Portée détaillée** | **Fonctionnalités à tester** : <br>• Accueil, Mentions Légales, Contact <br>• Gestion des agents, dossiers, références (balises, corps, comités) <br>• Import de fichiers (pages `importFichier.jsp`) <br>• Extraction de rapports (extractions 01‑10) <br>• Recherche Elasticsearch (DossierMotsClefsSearchLoader) <br>• Génération BIRT (PDF/HTML) <br>• Authentification (Cerbère) <br>• Gestion des sessions (SireinesSessionFilter) <br>**Exclusions** : scripts d’infrastructure (Dockerfile, docker‑compose), fichiers de configuration (`settings.xml`). |
| **Exigences de test** | Les exigences sont décrites dans le **CCF** (cahier de charges fonctionnel) – elles sont référencées dans le tableau de traçabilité (section 14). |
| **Critères d’entrée** | • Code compilé (`mvn clean package`) <br>• Artefact `sireines-web.war` disponible <br>• Environnements Docker (Recette, Pre‑prod, Prod) accessibles <br>• Jeu de données de test chargé (`sireines-db‑init.sql`) <br>• Outils d’automatisation (Selenium, JMeter) installés |
| **Critères de sortie** | • Couverture de code ≥ 80 % (branches) <br>• Tous les scénarios critiques exécutés sans défauts critiques <br>• Taux de défauts majeurs ≤ 1 % en pré‑prod <br>• Rapport d’exécution (TestNG/JUnit) signé et archivé <br>• Validation du pipeline CI (`pipeline‑success`) |
| **Ressources** | **Équipe** : <br>• Test‑Lead (coordination) <br>• 2 Test‑Engineers (automatisation) <br>• 1 Performance‑Engineer <br>• 1 Security‑Analyst <br>**Environnements** : <br>• Docker‑Compose (Recette, Pre‑prod) <br>• VM Linux pour les tests de charge (2 vCPU, 4 GB) <br>**Outils** : <br>• Maven 3.6+, JDK 8, GitLab CI, SonarQube, Selenium, JMeter, OWASP‑ZAP, Docker, Testcontainers |
| **Calendrier et jalons** | | |
| Sprint 1 (S‑01) – 2024‑04‑01 → 2024‑04‑07 | Mise en place du framework de test (JUnit / Selenium) – Validation du build Docker |
| Sprint 2 (S‑02) – 2024‑04‑08 → 2024‑04‑14 | Tests unitaires (services, utils) – Couverture ≥ 70 % |
| Sprint 3 (S‑03) – 2024‑04‑15 → 2024‑04‑21 | Tests d’intégration (DB, Elasticsearch) – Validation du jeu de données |
| Sprint 4 (S‑04) – 2024‑04‑22 → 2024‑04‑28 | Tests système (UI) – Scénarios d’import, extraction, BIRT |
| Sprint 5 (S‑05) – 2024‑04‑29 → 2024‑05‑05 | Tests non‑fonctionnels (perf, sec) – Rapport de charge |
| Sprint 6 (S‑06) – 2024‑05‑06 → 2024‑05‑12 | Régression complète + validation de la release 2.5.20 |
| **Livrables** | • Test‑Strategy (ce document) <br>• Test‑Plan (Annexe A) <br>• Test‑Design (Annexe B) <br>• Cas de test détaillés (Annexe C) <br>• Rapports d’exécution (HTML/JUnit) <br>• Matrice de traçabilité (Annexe D) <br>• Dashboard SonarQube & Jenkins |

---  

## 3️⃣  Conception des tests (ISO 29119‑4)

### 3.1 Techniques de test fonctionnel  

| Technique | Application dans SIREINES |
|---|---|
| **Partitionnement en classes d’équivalence** | • Champs de formulaire : `emailContact` (valide/invalid) <br>• Paramètres d’extraction (`anneeQual`, `dateRecDebut`) – valeurs limites (ex : 1900‑2100) |
| **Analyse des valeurs limites (BVA)** | • Numéros de dossier (`dos_id` : 1‑MAX) <br>• Pagination (`nbRowPage` : 1‑100) |
| **Tables de décision** | • Décision de génération de rapports (`typeAffichage` = PDF/HTML) <br>• Gestion des droits (`Menu` → `MENTIONS`, `CONTACT`) |
| **Tests de transition d’états** | • Cycle de vie d’un dossier : `EN_COURS` → `VALIDÉ` → `ARCHIVÉ` (contrôlé par `DossierDetailAction`) |
| **Tests de scénarios** | • Scénario « Import d’un fichier » (pages `importFichier.jsp` → service `ImportsServices.importer`) <br>• Scénario « Extraction d’un rapport » (choix type, bouton « Extraire », génération BIRT) |

### 3.2 Techniques de test structurel  

| Technique | Couverture cible |
|---|---|
| **Instruction coverage** | ≥ 80 % |
| **Branch coverage** | ≥ 75 % |
| **Condition coverage** | ≥ 70 % |
| **MC/DC** | Utilisé sur les méthodes critiques de sécurité (`ErrorHandler`, `SireinesSessionFilter`) |
| **Complexité cyclomatique** | ≤ 10 par méthode (détectée par SonarQube) |
| **Tests de chemins indépendants** | Générés automatiquement par JaCoCo + Pitest (mutation testing) |

### 3.3 Tests basés sur l’expérience  

| Domaine | Types de test |
|---|---|
| **Exploratoire** | Sessions de navigation manuelle sur les écrans « Dossiers », « Import », « Extraction » pour détecter des incohérences d’UI ou de flux. |
| **Error‑guessing** | Injecter des fichiers CSV mal formés, tester les limites de taille de fichier (> 5 Mo). |
| **Check‑lists** | Checklist issue du **Mantis** (ex : 0061626 – anomalie de livraison 2.5.6) appliquée à chaque build. |

---  

## 4️⃣  Spécification des cas de test (ISO 29119‑3 §7)  

> **Convention** – Chaque cas de test suit le template obligatoire.  

### 4.1 Exemple de cas de test fonctionnel (Import de fichier)

```
[TC-IMP-001] Import d’un fichier CSV valide
├── Identifiant : TC-IMP-001
├── Description : Vérifier que l’import d’un fichier CSV correctement formaté crée les enregistrements attendus dans la table DOSSER.
├── Pré‑conditions : 
│   • Application déployée (docker‑compose up -d)  
│   • Base de données initialisée (scripts/init.sql)  
│   • Session utilisateur authentifiée (Cerbère)  
├── Entrées : 
│   • Fichier « test_import.csv » (5 enregistrements valides)  
│   • Paramètre `upload` = fichier CSV  
├── Étapes d'exécution :  
│   1. Accéder à `http://sireines.recette/.../ImportFichier.do`  
│   2. Cliquer sur le bouton « Choisir un fichier », sélectionner `test_import.csv`  
│   3. Cliquer sur « Importer »  
│   4. Attendre la page de synthèse (`ImportSynthese.jsp`)  
│   5. Vérifier le tableau de synthèse affichant `SI_SUCCES = true` et `MESSAGE = "Import terminé"`  
│   6. Exécuter la requête SQL `SELECT COUNT(*) FROM dossier WHERE source='IMPORT_CSV';`  
├── Résultat attendu :  
│   • La page de synthèse indique succès.  
│   • La table `dossier` contient exactement 5 nouvelles lignes.  
│   • Aucun enregistrement n’est en erreur (colonne `SI_SUCCES` = true).  
├── Post‑conditions :  
│   • Données importées restent disponibles pour les tests suivants.  
├── Priorité : High  
├── Exigence couverte : CCF‑IMPORT‑001 (Import de fichiers)  
└── Technique utilisée : Partitionnement en classes d’équivalence (fichier valide / invalide)
```

### 4.2 Exemple de cas de test non‑fonctionnel (Performance – extraction 08)

```
[TC-PERF-008] Temps de réponse de l’extraction « Pyramide des âges »  
├── Identifiant : TC-PERF-008  
├── Description : Mesurer le temps de génération du rapport « pyramide des âges » (extraction08) sous charge 20 utilisateurs simultanés.  
├── Pré‑conditions :   
│   • Environnement Recette (docker‑compose) avec jeu de données complet (≈ 200 000 dossiers).  
│   • JMeter installé, script `extraction