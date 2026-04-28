# 📄 Cahier des Spécifications Techniques (CST) – **admin_ep**  
**Projet** : admin_ep – Administration des établissements publics (MTES‑MCT)  
**Référence** : ISO/IEC/IEEE 29119 (séries 1‑6, 11) – version 2022/2021  

> **Objectif** – Définir la stratégie, la planification, la conception, l’exécution et le suivi des activités de tests du projet *admin_ep* afin de garantir la conformité fonctionnelle, la robustesse, la sécurité et les performances attendues.  

---  

## 1️⃣ Stratégie de test (Test Strategy – ISO 29119‑3)

| Élément | Description |
|---------|-------------|
| **Portée** | <ul><li>Tests unitaires (Java, DAO, services, utils)</li><li>Tests d’intégration (base de données, services REST, batch JORF)</li><li>Tests système (application web, workflow, notifications e‑mail)</li><li>Tests d’acceptation (UAT) – validation métier (MOA)</li><li>Tests de non‑fonctionnels : sécurité, performance, compatibilité, fiabilité, accessibilité</li></ul> |
| **Exclusions** | <ul><li>Tests de charge du serveur d’infrastructure (hardware) – hors du périmètre applicatif</li><li>Tests de migration de version antérieure non livrée (seules les migrations *update/* décrites dans le dépôt sont testées)</li></ul> |
| **Objectifs mesurables** | <ul><li>Couverture de code : ≥ 80 % (branches) – unité, ≥ 70 % (integration)</li><li>Défauts critiques = 0 en production</li><li>Taux de succès des scénarios fonctionnels ≥ 95 %</li><li>Temps moyen de réponse (page + API) ≤ 2 s sous charge 20 utilisateurs simultanés</li><li>Pas de faille OWASP Top 10 détectée en test de sécurité</li></ul> |
| **Contraintes** | <ul><li>Environnement Java 8, Tomcat 9 (ou 10 en phase de migration)</li><li>Base PostgreSQL 9.6.11 → 15 (migration prévue)</li><li>Intégration avec le dispositif Cerbère (authentification SSO)</li><li>Déploiement via Maven 3, Docker (containerisation en cours)</li></ul> |
| **Risques & mitigation** |  |
| **Analyse des risques** |  |
| Risque | Probabilité | Impact | Stratégie de mitigation |
|---|---|---|---|
| Perte d’intégrité des données lors des scripts d’*update* (ex. `1_alter_mandat.sql`) | Moyen | Critique (corruption base) | • Tests de migration automatisés sur base de test clonée ; • Vérification post‑migration via scripts de validation (checksum, row‑count) |
| Fuite d’accès via Cerbère (authentification) | Faible | Critique (exposition données) | • Tests d’intrusion (OWASP ZAP) sur les points d’entrée SSO ; • Revue de code SecurityHelper, RightsHelper |
| Performance dégradée avec le batch JORF (parsing de gros fichiers) | Moyen | Important (temps de traitement) | • Tests de charge sur le job `ArticleAnalyser` avec fichiers > 500 Mo ; • Profilage (Java Flight Recorder) |
| Incompatibilité navigateur (UI Struts2) | Moyen | Moyen (expérience utilisateur) | • Tests de compatibilité sur Chrome, Firefox, Edge, IE 11 (legacy) via Selenium Grid |
| Emails de notification non délivrés | Faible | Important (processus métier) | • Test d’envoi via mock SMTP + vérification du contenu et du header |
| Migration vers Tomcat 10 (Jakarta EE) | Faible | Critique (breakage) | • Tests d’intégration de servlets + validation du descripteur `web.xml` |
| **Approche générale** |  |
| Niveaux de test | - **Unitaire** (JUnit 5 + Mockito) <br> - **Intégration** (Spring Test, Testcontainers PostgreSQL) <br> - **Système** (Selenium WebDriver, RestAssured) <br> - **Acceptation** (Cucumber BDD) |
| Types de test | - **Fonctionnels** (CRUD admin, recherche, mandat, notifications) <br> - **Structurels** (couverture de code, tests de chemins) <br> - **Non‑fonctionnels** (sécurité, performance, compatibilité, fiabilité) <br> - **Régression** (suite automatisée à chaque build) |
| Techniques appliquées | - Partitionnement en classes d’équivalence + BVA sur formulaires (ex. création d’un mandat) <br> - Tables de décision pour les règles de gestion (ex. droits d’accès selon profil) <br> - Tests d’états (workflow mandat → titulaire / suppléant) <br> - Tests exploratoires sur les pages JSP <br> - Data‑driven tests (fichiers CSV d’entrée pour le batch JORF) |

---  

## 2️⃣ Plan de test (Test Plan – ISO 29119‑3)

### 2.1 Portée détaillée

| Module | Fonctionnalités à tester | Exigences associées (CCF) |
|--------|------------------------|--------------------------|
| **adminep‑database** | Création schéma, séquences, tables, scripts *update* | CCF‑DB‑01 … CCF‑DB‑12 |
| **adminep‑web – UI** | Accueil, recherche admin/EP, CRUD admin, mandat, gestionnaires, statistiques, supervision, pages d’erreur | CCF‑UI‑01 … CCF‑UI‑15 |
| **Services REST** | `ArticleServices`, `MandatServices`, `GestionnaireServices`, `ChargeServices` | CCF‑SVC‑01 … CCF‑SVC‑10 |
| **Batch JORF** | `ArticleAnalyser`, `ReindexArticlesByArtiIDTask` | CCF‑BATCH‑01 … CCF‑BATCH‑05 |
| **Sécurité** | Authentification Cerbère, droits RBAC (`RightsHelper`) | CCF‑SEC‑01 … CCF‑SEC‑04 |
| **Notifications** | Envoi e‑mail (mandat proche échéance) | CCF‑NOTIF‑01 |
| **Performance** | Temps de réponse pages, API, traitement JORF | CCF‑PERF‑01 … CCF‑PERF‑03 |
| **Compatibilité** | Navigateurs (Chrome, Firefox, Edge, IE 11) | CCF‑COMP‑01 |
| **Fiabilité** | Reprise après panne (redémarrage Tomcat, reconnexion DB) | CCF‑REL‑01 |

### 2.2 Critères d’entrée

| Élément | Condition |
|--------|-----------|
| **Code** | Build Maven `clean install` sans erreurs, artefacts générés (WAR, SQL zip) |
| **Environnements** | Environnements DEV, INT, PREPROD disponibles, Docker images à jour |
| **Données de test** | Jeux de données `admin_ep_test.sql` (jeu de base minimal) chargés dans PostgreSQL 9.6.11 |
| **Outils** | JUnit 5, Maven Surefire/Failsafe, Testcontainers, Selenium Grid, OWASP ZAP, JMeter |
| **Documentation** | Spécifications fonctionnelles (CCF), diagrammes de séquence, maquettes UI |

### 2.3 Critères de sortie

| Élément | Condition |
|--------|-----------|
| **Couverture** | Code coverage ≥ 80 % (branches) – unité, ≥ 70 % – intégration |
| **Défauts** | Tous les défauts **Critiques** résolus et fermés ; **Majeurs** ≤ 5 en attente de correction (dérogation validée) |
| **KPIs** | Taux de réussite des scénarios fonctionnels ≥ 95 % ; Temps moyen de réponse ≤ 2 s (charge 20 U) |
| **Rapport** | Rapport de test complet (JUnit, Selenium, JMeter, ZAP) archivé dans le référentiel |
| **Livrables** | Jeux de données de test versionnés, scripts de migration validés, documentation de test mise à jour |

### 2.4 Ressources

| Rôle | Nom | Responsabilités |
|------|-----|-----------------|
| **Test Manager** | (ex. C. Arbogast) | Pilotage global, suivi des KPIs, reporting |
| **Test Analyst** | (ex. G. Gilliard) | Élaboration des cas de test, traçabilité CCF ↔ TC |
| **Test Engineer** | (ex. Développeur QA) | Implémentation automatisation, exécution scripts |
| **Développeur** | (équipe Java) | Mise à disposition des builds, correction défauts |
| **Ops / Infra** | (équipe DNUM) | Provisionnement des environnements, monitoring |

#### Outils & licences

| Outil | Usage | Version |
|-------|-------|---------|
| **Maven** | Build & dépendances | 3.8.6 |
| **JUnit 5** | Tests unitaires | 5.9 |
| **Mockito** | Mocking | 4.5 |
| **Testcontainers** | DB conteneurisée | 1.18 |
| **Selenium WebDriver** | Tests UI | 4.9 |
| **Cucumber‑JVM** | BDD/acceptation | 7.11 |
| **OWASP ZAP** | Tests de sécurité | 2.12 |
| **JMeter** | Tests de charge | 5.6 |
| **Allure** | Reporting | 2.19 |
| **GitLab CI** | CI/CD pipeline | — |

### 2.5 Calendrier & jalons

| Phase | Dates (est.) | Livrable |
|-------|--------------|----------|
| **Pré‑planification** | 01/04/2026 – 07/04/2026 | Document CST (déjà réalisé) |
| **Environnement & jeux de données** | 08/04/2026 – 14/04/2026 | Docker compose, `admin_ep_test.sql` |
| **Développement des tests unitaires** | 15/04/2026 – 30/04/2026 | Coverage ≥ 70 % |
| **Tests d’intégration** | 01/05/2026 – 15/05/2026 | Validation des scripts *update* |
| **Tests système (UI + API)** | 16/05/2026 – 31/05/2026 | Scénarios fonctionnels complets |
| **Tests non‑fonctionnels** | 01/06/2026 – 15/06/2026 | Rapport ZAP, JMeter |
| **Recette MOA (UAT)** | 16/06/2026 – 22/06/2026 | Sign‑off MOA |
| **Pré‑production & Revue** | 23/06/2026 – 30/06/2026 | Validation de la migration PostgreSQL 15 |
| **Production** | 01/07/2026 | Go‑live |

---  

## 3️⃣ Conception des tests (Test Design – ISO 29119‑4)

### 3.1 Techniques fonctionnelles

| Technique | Application concrète |
|-----------|----------------------|
| **Partitionnement en classes d’équivalence** | Formulaires d’ajout d’un administrateur : <br> - `nom` (valide / vide) <br> - `email` (valide / format invalide) <br> - `profil` (admin / gestionnaire / lecteur) |
| **Boundary Value Analysis (BVA)** | Champ `durée mandat` (0, 1, 365 jours) ; champ `siren` (9 chiffres) |
| **Tables de décision** | Droits d’accès selon profil : <br> `(profil, action) → autorisé/refusé` (ex. création mandat) |
| **Tests d’états (state‑transition)** | Workflow mandat : `Créé → Titulaire → Suppléant → Expiré → Archivé` |
| **Scénarios de cas d’utilisation** | <ul><li>Création d’un administrateur</li><li>Recherche d’un EP via le moteur JORF</li><li>Envoi de notification d’échéance</li></ul> |
| **Tests de données (data‑driven)** | Jeux CSV pour le batch JORF (ex. différents formats d’articles) |
| **Tests exploratoires** | Session de 2 h sur les pages d’erreur, menus, navigation dynamique |
| **Error guessing** | Injection SQL dans les champs de recherche, dépassement de longueur de chaîne, valeurs nulles dans les appels DAO |

### 3.2 Techniques structurelles

| Technique | Objectif / Métrique |
|-----------|----------------------|
| **Couverture d’instructions** | ≥ 80 % (JaCoCo) – unité |
| **Couverture de branches** | ≥ 80 % – unité |
| **Couverture de conditions** | ≥ 70 % – intégration |
| **MC/DC** (si besoin critique) | Non requis (application non‑safety‑critical) |
| **Tests de chemins** | Analyse cyclomatique des classes critiques (`MandatServices`, `ArticleAnalyser`). Sélection des chemins indépendants (max = Cyclomatic + 1). |
| **Analyse statique** | SonarQube (bugs, vulnérabilités, code smells) – seuil « Blocker » = 0 |

### 3.3 Tests basés sur l’expérience

| Type | Exemple |
|------|---------|
| **Exploratoire** | Session de test libre sur les pages de configuration de l’authentification Cerbère |
| **Error guessing** | Manipulation de l’URL `sessionId` pour tester la réutilisation de session |
| **Check‑list** | Liste de vérification OWASP Top 10 appliquée à chaque endpoint REST |

---  

## 4️⃣ Spécification des cas de test (Test Case Specification – ISO 29119‑3)

### 4.1 Modèle de cas de test (obligatoire)

```markdown
**[TC‑{num}]** <Titre du cas de test>

- **Identifiant** : TC‑{num}
- **Description** : <Phrase courte décrivant le but du test>
- **Préconditions** : <État du système, jeu de données chargé, utilisateur connecté>
- **Entrées** : <Données d’entrée (ex. JSON, paramètres formulaire)>
- **Étapes d'exécution** :
  1. <Action 1>
  2. <Action 2>
  …  
- **Résultat attendu** : <Résultat précis (status HTTP, texte affiché, valeur DB) >
- **Post‑conditions** : <État final du système (ex. ligne insérée)>
- **Priorité** : Critical / High / Medium / Low
- **Exigence couverte** : CCF‑{xxx}
- **Technique utilisée** : Partitionnement / Table de décision / State‑transition / Data‑driven
```

### 4.2 Exemples de cas de test (extraits)

| TC | Titre | Exigence CCF | Priorité | Technique |
|----|-------|--------------|----------|-----------|
| TC‑001 | **Création d’un administrateur valide** | CCF‑UI‑01 | Critical | Partitionnement (valeurs valides) |
| TC‑002 | **Création administrateur – champ email vide** | CCF‑UI‑01 | High | BVA (email) |
| TC‑003 | **Recherche d’un EP via le moteur JORF (mot‑clé « agriculture »)** | CCF‑BATCH‑01 | Critical | Data‑driven (fichier JORF) |
| TC‑004 | **Accès page Administration – utilisateur non autorisé** | CCF‑SEC‑02 | Critical | Table de décision (profil vs action) |
| TC‑005 | **Envoi de notification d’échéance (mandat 5 jours avant)** | CCF‑NOTIF‑01 | High | Scénario d’usage |
| TC‑006 | **Test de charge – 20 utilisateurs simultanés sur recherche admin** | CCF‑PERF‑01 | Medium | JMeter script |
| TC‑007 | **Injection SQL dans le champ `nom` de la recherche** | CCF‑SEC‑03 | Critical | Error guessing |
| TC‑008 | **Migration DB de la version 1.2.0 → 1.2.1 (script `1_function_unaccent.sql`)** | CCF‑DB‑09 | High | Test d’intégration DB |
| TC‑009 | **Redémarrage Tomcat – persistance de session** | CCF‑REL‑01 | Medium | Test de fiabilité |
| TC‑010 | **Compatibilité navigateur – affichage du menu** | CCF‑COMP‑01 | Low | Selenium cross‑browser |

> **Remarque** – La table de traçabilité complète (CCF ↔ TC) est fournie en annexe A.

---  

## 5️⃣ Procédures de test (Test Procedures – ISO 29119‑3)

| Étape | Action | Responsable | Outil |
|-------|--------|--------------|-------|
| **5.1** | Mise en place de l’environnement Docker (PostgreSQL 9.6, Tomcat 9) | Ops | Docker‑Compose |
| **5.2** | Chargement du jeu de données `admin_ep_test.sql` | Test Engineer | psql |
| **5.3** | Exécution des tests unitaires | Dev/QA | `mvn test` (Surefire) |
| **5.4** | Lancement des tests d’intégration (Testcontainers) | QA Engineer | `mvn verify` (Failsafe) |
| **5.5** | Déploiement du WAR sur l’environnement INT | Ops | `gitlab‑ci` |
| **5.6** | Exécution du scénario Selenium (Cucumber) | Test Engineer | `mvn verify -Pcucumber` |
| **5.7** | Exécution du script de charge JMeter | Performance Engineer | JMeter (CLI) |
| **5.8** | Scan de sécurité OWASP ZAP (baseline + attack) | Security Engineer | ZAP Automation |
| **5.9** | Collecte des rapports (JaCoCo, Allure, JMeter, ZAP) | Test Manager | Jenkins / GitLab CI |
| **5.10** | Validation des critères d’entrée/sortie, mise à jour du tableau de suivi des défauts | Test Manager | JIRA/ALM |

---  

## 6️⃣ Gestion des anomalies (Defect Management – ISO 29119‑3)

### 6.1 Classification des défauts

| Sévérité | Définition | Exemple (admin_ep) |
|----------|------------|--------------------|
| **Critique** | Blocage total, aucune solution de contournement possible | Crash du serveur lors du parsing d’un fichier JORF > 500 Mo |
| **Majeur** | Fonction fonctionnelle majeure non‑opérante | Aucun e‑mail de notification d’échéance n’est envoyé |
| **Mineur** | Fonction secondaire impactée, contournable | Pagination du tableau des administrateurs ne fonctionne pas sur Chrome |
| **Cosmétique** | Défaut d’UI/UX uniquement | Orthographe « admininstrateur » dans l’aide contextuelle |

### 6.2 Cycle de vie d’un défaut

1. **Nouveau** – Créé dans JIRA avec les champs obligatoires (CCF, gravité, priorité).  
2. **Assigné** – Assigné à développeur ou équipe concernée.  
3. **En cours de correction** – Code modifié, commit lié (`JIRA‑XX`).  
4. **À retester** – Test Engineer exécute le test de régression correspondant.  
5. **Fermé** – Défaut corrigé (ou rejeté avec justification).  

### 6.3 Métriques de défauts (exemple de tableau de suivi)

| Période | Défauts crit. | Défauts majeurs | Défauts mineurs | Taux de fuite (défauts post‑prod / pré‑prod) |
|---------|---------------|----------------|-----------------|----------------------------------------------|
| Sprint 1 (04/2026) | 0 | 3 | 12 | 0 % |
| Sprint 2 (05/2026) | 0 | 1 | 8 | 5 % |
| Sprint 3 (06/2026) | 0 | 0 | 5 | 2 % |

---  

## 7️⃣ Tests de régression (ISO 29119‑6)

| Aspect | Description |
|--------|-------------|
| **Sélection** | Tous les cas de test automatisés (unitaires, intégration, UI) + les scénarios critiques de production (création mandat, import JORF) |
| **Suite automatisée** | `admin_ep-regression-suite.jar` (Maven‑failsafe) exécuté à chaque pipeline `merge‑request` |
| **Fréquence** | – **CI** : à chaque commit (smoke) <br> – **Nightly** : exécution complète (incl. charge & sécurité) |
| **Critères d’inclusion** | Cas marqués `Regression=true` dans le tag JUnit (`@Tag("Regression")`) |
| **Critères d’exclusion** | Tests nécessitant des données volumineuses (> 1 GB) – exécutés uniquement en *nightly* sur l’environnement PREPROD |
| **Gestion des écarts** | Si régression détectée, le pipeline bloque le merge et crée automatiquement un ticket JIRA (`Regression‑FAIL`) |

---  

## 8️⃣ Tests unitaires (ISO 29119‑11)

| Niveau | Cadre | Couverture cible |
|--------|-------|------------------|
| **Java** | JUnit 5 + Mockito | 80 % branches, 90 % instructions |
| **DAO** | Testcontainers (PostgreSQL) | 75 % (requêtes SQL) |
| **Utils** | JUnit paramétré | 100 % (méthodes statiques) |
| **Méthodologie** | TDD pour les nouvelles fonctionnalités critiques (ex. `MandatServices.calculateExpiration()`) |

*Exemple de test unitaire* :

```java
@Test
@DisplayName("calculateExpiration() – mandat de 365 jours")
void shouldReturnCorrectExpirationDate() {
    // Given
    LocalDate start = LocalDate.of(2026, 3, 1);
    Mandat mandat = new Mandat(start, 365);

    // When
    LocalDate expiration = mandat.calculateExpiration();

    // Then
    assertEquals(LocalDate.of(2027, 2, 28), expiration);
}
```

---  

## 9️⃣ Automatisation des tests

| Niveau | Outil | Raison du choix |
|--------|-------|----------------|
| **Unitaires** | Maven‑Surefire / Failsafe (JaCoCo) | Intégration native, génération de rapports |
| **Intégration** | Testcontainers (PostgreSQL) | Base isolée, reproductible |
| **UI** | Selenium WebDriver + Cucumber‑JVM | Scénarios lisibles par les MOA, exécution parallèle |
| **API** | RestAssured + JUnit5 | Validation fluide des réponses JSON |
| **Performance** | JMeter (non‑GUI) + CI | Simuler 20 U simultanés, collecter temps de réponse |
| **Sécurité** | OWASP ZAP (API) | Scan automatisé, génération de rapports XML |
| **Reporting** | Allure (JUnit, Cucumber, JMeter) | Dashboard unifié, lien depuis GitLab CI |

> **Critères d’automatisabilité** – Tous les scénarios fonctionnels récurrents, les scripts de migration DB et les tests de performance sont automatisés. Les scénarios exploratoires et les tests d’accessibilité sont manuels.

---  

## 🔟 Environnements de test

| Environnement | Configuration | Données | Usage |
|--------------|---------------|--------|-------|
| **DEV** | Docker‑Compose (PostgreSQL 9.6, Tomcat 9) | `admin_ep_dev.sql` (jeu minimal) | Développement, tests unitaires |
| **INT** | VM (Ubuntu 20.04) – Tomcat 9, PostgreSQL 9.6 | `admin_ep_int.sql` (jeu complet) | Tests d’intégration, UI, API |
| **PERF** | VM (4 vCPU, 8 GB RAM) – Tomcat 9, PostgreSQL 15 | Jeu de charge (10 k mandats, 5 k admins) | Tests de charge, profiling |
| **PREPROD** | Docker‑Swarm – Tomcat 10, PostgreSQL 15 | `admin_ep_preprod.sql` (snapshot prod) | Recette, UAT, validation migration |
| **PROD** | Cluster ESXi – Tomcat 9 → 10 (migration), PostgreSQL 15 | Données réelles | Exploitation |

---  

## 1️⃣1️⃣ Rapports et métriques (KPIs)

| Rapport | Contenu | Fréquence | Destinataire |
|--------|---------|-----------|--------------|
| **Test Execution Summary** | Nombre de cas exécutés, réussis/échoués, durée | Chaque build | QA Lead, Dev Leads |
| **Coverage Report** | JaCoCo HTML, % branches, instructions | Nightly | QA, Dev |
| **Defect Dashboard** | Défauts par sévérité, état, trend | Hebdo | PM, QA |
| **Performance Report** | Temps moyen, p95, débit, erreurs | Chaque exécution JMeter | Ops, PO |
| **Security Report** | Vulnérabilités ZAP, CVE | Chaque sprint | SecOps, PO |
| **Regression Trend** | % régression détectée, évolution | Mensuel | Management |

---  

## 1️⃣2️⃣ Organisation et responsabilités (RACI)

| Rôle | Responsable (R) | Accountable (A) | Consulted (C) | Informed (I) |
|------|----------------|----------------|---------------|--------------|
| **Test Manager** | X | X | PO, Dev Leads | All |
| **Test Analyst** | X | | PO, Business Analyst | Dev Leads |
| **Test Engineer** | X | | Dev, Ops | Test Manager |
| **Développeur** | | X | Test Engineer | Test Manager |
| **Ops / Infra** | X | | Test Engineer | Test Manager |
| **Product Owner** | | | Test Analyst, Test Manager | All |
| **MOA (Maîtrise d’Ouvrage)** | | | Test Analyst | Test Manager |

---  

## 1️⃣3️⃣ Gestion des configurations (Configuration Management – ISO 29119‑3)

| Élément | Méthode |
|---------|----------|
| **Cas de test** | Versionnés dans `src/test/resources/tests/` (fichiers `.xlsx` + `.feature`). Chaque modification crée un commit avec message `TC‑<num> update` |
| **Jeux de données** | Scripts SQL versionnés (`db/migrations/`) – taggit par version du projet (`v1.2.3`) |
| **Scripts d’automatisation** | Stockés dans `ci/` (GitLab‑CI YAML) – versionnés avec le code |
| **Traçabilité** | Table `TRACE_TCID_CCF` (Excel) générée automatiquement à partir des annotations `@LinkToRequirement("CCF‑UI‑01")` (Allure) |
| **Gestion de versions** | Gitflow – `develop` → `release/x.x.x` → `master` (production) |
| **Gestion des dépendances** | Maven `pom.xml` – versions figées, mise à jour via Dependabot |

---  

## 📎 Annexes

### **Annexe A – Matrice de traçabilité Exigences ↔ Cas de test**  

| CCF ID | Description | TC(s) associés |
|--------|-------------|----------------|
| CCF‑UI‑01 | Création/édition d’un administrateur | TC‑001, TC‑002 |
| CCF‑UI‑05 | Recherche d’un EP par nom | TC‑003 |
| CCF‑SEC‑02 | Accès page d’administration (RBAC) | TC‑004 |
| CCF‑NOTIF‑01 | Envoi e‑mail d’échéance mandat | TC‑005 |
| CCF‑PERF‑01 | Temps de réponse recherche admin (< 2 s) | TC‑006 |
| CCF‑SEC‑03 | Injection SQL sur champ recherche | TC‑007 |
| CCF‑DB‑09 | Migration 1.2.0 → 1.2.1 (unaccent) | TC‑008 |
| CCF‑REL‑01 | Persistance de session après redémarrage | TC‑009 |
| CCF‑COMP‑01 | Affichage correct du menu sur Chrome/Firefox/IE | TC‑010 |
| … | … | … |

*(Le tableau complet (≈ 150 exigences) est disponible dans le répertoire `docs/traces/` du dépôt.)*  

### **Annexe B – Couverture de code (exemple JaCoCo)**  

```text
-------------------------------------------------------
| Package                         | %Instr | %Branch |
-------------------------------------------------------
| fr.gouv.e2.baseadmin.controller| 87.5   | 78.2   |
| fr.gouv.e2.baseadmin.services  | 84.1   | 71.6   |
| fr.gouv.e2.baseadmin.util     | 92.3   | 85.4   |
| fr.gouv.e2.baseadmin.model     | 88.9   | 80.0   |
-------------------------------------------------------
TOTAL                              86.2      77.6
```  

### **Annexe C – Exemple de script CI GitLab (pipeline)**  

```yaml
stages:
  - build
  - test
  - security
  - performance
  - report

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"

build:
  stage: build
  script:
    - mvn -B -DskipTests clean package
  artifacts:
    paths:
      - target/*.war

unit_test:
  stage: test
  script:
    - mvn -B test
  artifacts:
    reports:
      junit: target/surefire-reports/*.xml
    paths:
      - target/site/jacoco

integration_test:
  stage: test
  script:
    - mvn -B verify
  artifacts:
    reports:
      junit: target/failsafe-reports/*.xml

ui_test:
  stage: test
  script:
    - mvn -B verify -Pcucumber
  artifacts:
    reports:
      cucumber: target/cucumber-reports/*.json

security_scan:
  stage: security
  script:
    - zap-baseline.sh -t http://int.adminep:8080 -r zap-report.xml
  artifacts:
    reports:
      dast: zap-report.xml

performance_test:
  stage: performance
  script:
    - jmeter -n -t jmeter/perf-search-admin.jmx -l results.jtl
  artifacts:
    paths:
      - results.jtl

report:
  stage: report
  script:
    - allure generate target/allure-results -o target/allure-report
  artifacts:
    paths:
      - target/allure-report
    when: always
```  

---  

## ✅ Conclusion

Le présent **Cahier des Spécifications Techniques** décrit de façon exhaustive comment le projet **admin_ep** sera testé conformément à la norme **ISO/IEC/IEEE 29119**. Il couvre :

* la **stratégie** globale (objectifs, risques, niveaux de test)  
* le **plan** détaillé (portée, critères, ressources, planning)  
* la **conception** (techniques fonctionnelles & structurelles)  
* les **cas de test** normalisés, la **traçabilité** CCF ↔ TC, les **procédures** d’exécution, la **gestion des défauts** et les **indicateurs de performance**  

Le respect de ce CST garantit une couverture de test adaptée aux exigences fonctionnelles, de sécurité et de performance de l’application, tout en assurant la **reproductibilité**, la **maintenabilité** et la **transparence** du processus de test.  

---  

*Document rédigé le 27 avril 2026 – Version 1.0*  



---  



**À retenir**  

* **Couverture cible** ≥ 80 % (branches) – les rapports seront générés à chaque build.  
* **Défaut critique** = 0 en production – le processus de revue et de blocage du pipeline assure ce niveau.  
* **Automatisation** = 95 % des scénarios fonctionnels + 100 % des tests de régression.  
* **Sécurité** – aucun défaut OWASP Top 10 détecté avant mise en prod.  

---  



*Fin du CST*  



---  



> **Références** :  
> * ISO/IEC/IEEE 29119‑1 :2022, ‑2 :2021, ‑3 :2021, ‑4 :2021, ‑5 :2016, ‑6 :2021, ‑11 :2020.  
> * Documentation projet `admin_ep` (arborescence, scripts SQL, fichiers `*.md`).  