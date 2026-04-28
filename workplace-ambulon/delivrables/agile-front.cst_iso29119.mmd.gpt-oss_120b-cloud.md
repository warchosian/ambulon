# 📄 Cahier des Spécifications Techniques (CST) – **agile‑front**  
**Projet** : agile‑front – Application Vue.js (Vuetify) de gestion d’études  

**Norme** : ISO/IEC/IEEE 29119 (toutes les parties) – version 2022/2021  

**Date** : 27 avril 2026  

---  

> **NOTE** – Ce CST a été élaboré à partir de l’arborescence et du code source fourni (voir *Document 1 – agile‑front.code.filtered.md*).  
> Les exigences fonctionnelles (CCF) sont dérivées du code et du README ; les exigences non‑fonctionnelles sont définies à partir des bonnes pratiques du stack (Vue 3, Vuetify, Axios) et des contraintes métier (sécurité, performance, compatibilité).  

---  

## 1️⃣ Stratégie de Test (Test Strategy) – ISO 29119‑3  

| Élément | Description |
|---------|-------------|
| **1.1 Contexte et objectifs** | L’application *agile‑front* fournit les écrans de connexion, de consultation, de création et d’édition d’études, ainsi que des fonctions d’export et de visualisation de tutoriels. Les tests visent à garantir la **qualité fonctionnelle**, la **sécurité** (authentification, accès aux API), la **performance** (temps de réponse < 2 s en charge normale) et la **compatibilité** (navigateurs modernes). |
| **Portée** | **Inclus** : tous les modules Vue (`components/`, `views/`, `store/`, `services/`, `mixins/`). <br>**Exclu** : scripts de build (`node_modules/`, `dist/`), fichiers de configuration de CI non‑exécutables. |
| **Objectifs mesurables** | • Couverture de code **≥ 80 %** (instruction) au niveau unité.<br>• Couverture des exigences **≥ 95 %** (traçabilité bidirectionnelle).<br>• Taux de défauts critiques **= 0** en production.<br>• Temps moyen de régression **≤ 30 min** par build. |
| **Contraintes & dépendances** | • API back‑end accessible via `VUE_APP_API_BASE_URL` (mock disponible).<br>• Environnement Node ≥ 14, Yarn 1.22.<br>• Tests UI nécessitent Chrome ≥ 110 (headless) et Firefox ≥ 115. |
| **1.2 Risques & mitigation** |  |

| Risque | Probabilité | Impact | Stratégie de mitigation |
|--------|-------------|--------|------------------------|
| API back‑end instable (latence > 5 s) | Moyenne | Élevé | Utiliser un serveur mock (WireMock) pour tests d’intégration; timeout < 10 s. |
| Mauvaise gestion des états de session (token expiré) | Faible | Critique | Tests de sécurité automatisés OWASP ZAP ; scénario d’expiration du JWT. |
| Régression fonctionnelle lors de l’ajout de nouveaux champs d’étude | Élevée | Moyen | Suite de régression automatisée (Cypress) incluant tous les écrans d’étude. |
| Compatibilité navigateurs (IE 11) | Faible | Faible | Tests de compatibilité ciblant les 2 dernières versions de Chrome, Firefox, Edge – IE non‑supporté (documenté). |
| Défaillance du store Vuex (mutations non‑pures) | Moyenne | Moyen | Tests unitaires sur chaque mutation/action avec couverture 100 %. |
| Fuite de données sensibles dans les logs (debugger) | Faible | Critique | Linter (`eslint`) déjà désactive `no-console` en prod ; audit de logs via tests de sécurité. |

| **1.3 Approche générale** |
|--------------------------|
| **Niveaux de test** : <br>• **Unitaire** – Vue components, mixins, store modules, services (Jest).<br>• **Intégration** – Interaction component‑store‑service (Vue Test Utils + Jest).<br>• **Système** – End‑to‑end (Cypress) couvrant scénarios de bout en bout.<br>• **Acceptation** – Tests d’acceptation utilisateur (Cucumber‑Gherkin) exécutés en environnement *REC*. |
| **Types de test** : <br>• Fonctionnel (validation des flux UI, API).<br>• Non‑fonctionnel : performance, sécurité, compatibilité, utilisabilité.<br>• Structurel (coverage, chemins).<br>• Régression (suite automatisée à chaque build). |
| **Techniques appliquées** (voir § 3) : <br>• Partitionnement en classes d’équivalence, BVA, tables de décision (services).<br>• Tests de transition d’état (store, router).<br>• Tests de chemin (complexité cyclomatique).<br>• Tests exploratoires & error‑guessing sur UI. |

---  

## 2️⃣ Plan de Test (Test Plan) – ISO 29119‑3  

### 2.1 Portée détaillée  

| Fonctionnalité | Fichiers associés | Exigence (CCF) |
|----------------|-------------------|----------------|
| **Login** | `src/views/Login.vue`, `src/services/SecurityService.js`, `src/store/modules/security.js` | CCF‑001 – Authentification sécurisée |
| **Gestion des études** | `src/services/LegacyProxyService.js`, `src/store/modules/studies.js`, `src/views/Etude*.vue` | CCF‑002 – CRUD études |
| **Export des études** | `src/components/EtudesExportPanel.vue`, `src/services/ExportService.js` | CCF‑003 – Export CSV/JSON |
| **Filtrage** | `src/mixins/filterUtilMixin.js` | CCF‑004 – Filtrage dynamique |
| **Tutoriels** | `src/views/Tutoriels.vue` | CCF‑005 – Accès aux ressources externes |
| **Thème & UI** | `src/plugins/vuetify.js`, `src/App.vue` | CCF‑006 – Conformité UI Vuetify |
| **Routing** | `src/router.js` | CCF‑007 – Navigation sécurisée |
| **Configuration** | `.env.sample`, `vue.config.js` | CCF‑008 – Paramétrage environnemental |

> **Exclusions** : Scripts de build (`babel.config.js`, `postcss.config.js`), fichiers de documentation (`README.md`). Justification – hors périmètre de validation fonctionnelle.

### 2.2 Critères d’entrée  

| Condition | Vérification |
|-----------|--------------|
| Code compilable (`yarn build` sans erreurs) | ✅ Build réussi |
| Environnements (DEV, INT, REC, PERF) provisionnés | ✅ VM/containers prêts |
| Jeux de données de test disponibles (mock JSON) | ✅ `fixtures/` importés |
| Linter et formatage passent (`yarn lint`) | ✅ 0 violations critiques |
| Tests unitaires précédents passent (> 80 % couverture) | ✅ Rapport Jest OK |

### 2.3 Critères de sortie  

| Condition | Valeur cible |
|-----------|--------------|
| **Couverture de code** – instruction ≥ 80 % (Jest) | ✅ |
| **Défauts critiques** – 0 en production | ✅ |
| **Défauts majeurs** – ≤ 2 % du total détecté | ✅ |
| **Exigences testées** – ≥ 95 % (traçabilité) | ✅ |
| **Tests de régression** – suite exécutée, 0 échecs | ✅ |
| **Documentation** – rapports et matrices à jour | ✅ |

### 2.4 Ressources  

| Rôle | Nom / Profil | Responsabilités |
|------|--------------|-----------------|
| **Test Manager** | Alice Dupont (QA Lead) | Pilotage global, approbation livrables |
| **Test Analyst** | Bruno Martin | Élaboration cas de test, traçabilité |
| **Automation Engineer** | Clara Zhou | Scripts Cypress/Jest, CI integration |
| **Performance Engineer** | David Leclerc | Scénarios Load/Stress (k6) |
| **Security Analyst** | Eva Gómez | Scans OWASP ZAP, revues code |
| **Développeurs** | Équipe Front‑end (3) | Support test data, correction défauts |

**Environnements**  

| Env | OS / Browser | Configuration | Usage |
|-----|--------------|---------------|-------|
| DEV | Ubuntu 22.04, Chrome 118 (headless) | Node 14, Yarn 1.22 | Développement, tests unitaires |
| INT | Windows 10, Chrome 118 / Firefox 115 | Docker compose (api‑mock) | Tests d’intégration |
| REC | Ubuntu 22.04, Chrome 118 (non‑headless) | Base de données pré‑remplie (anonymisée) | Tests de recette |
| PERF | Ubuntu 22.04, k6 0.45 | API réel (sandbox) | Tests de charge |
| PREPROD | Identique à prod | Mirror de prod | Validation finale, UAT |

**Outils**  

| Catégorie | Outil | Raison |
|-----------|-------|--------|
| Unit testing | **Jest** + **Vue Test Utils** | Couverture JavaScript/Vue |
| UI automation | **Cypress** (v12) | E2E, CI/CD friendly |
| Performance | **k6** | Scriptable load testing |
| Security | **OWASP ZAP** | Scan dynamique |
| CI/CD | **GitLab CI** | Pipelines automatisés |
| Gestion des tests | **TestRail** (ou **Xray**) | Traceabilité, reporting |
| Gestion des défauts | **Jira** | Workflow defect |

### 2.5 Calendrier & jalons  

| Phase | Dates (est.) | Livrable |
|-------|--------------|----------|
| **Pré‑test** (setup, data) | 2026‑05‑01 → 2026‑05‑03 | Environnement prêt |
| **Tests unitaires** | 2026‑05‑04 → 2026‑05‑07 | Rapport Jest + couverture |
| **Tests d’intégration** | 2026‑05‑08 → 2026‑05‑11 | Rapport Vue Test Utils |
| **Tests système (Cypress)** | 2026‑05‑12 → 2026‑05‑16 | Rapport Cypress |
| **Tests de performance** | 2026‑05‑17 → 2026‑05‑18 | Rapport k6 |
| **Tests de sécurité** | 2026‑05‑19 → 2026‑05‑20 | Rapport ZAP |
| **Recette** | 2026‑05‑21 → 2026‑05‑23 | Rapport Recette + approbation |
| **Release** | 2026‑05‑24 | Déploiement prod |
| **Post‑release monitoring** | 2026‑05‑25 → 2026‑05‑31 | Dashboard defect escape |

---  

## 3️⃣ Conception des Tests (Test Design) – ISO 29119‑4  

### 3.1 Techniques de test fonctionnel  

| Technique | Application concrète | Exemple de cas |
|----------|--------------------|----------------|
| **Partitionnement en classes d’équivalence** | Entrées du formulaire d’étude (titre, date, catégorie) | Classe valide – titre non vide, date future; classe invalide – titre vide, date passée |
| **Boundary Value Analysis (BVA)** | Champ “année” du filtre (`filterUtilMixin`) | Valeurs limites : 2011 (min), année courante + 7 (max) |
| **Tables de décision** | API `LegacyProxyService` – actions *GET/POST* selon présence d’`id` | Condition 1 : `id` présent → `GET /etudes/:id` ; Condition 2 : `id` absent → `GET /etudes/new` |
| **Tests de transition d’états** | Store Vuex `security` – états *non‑connecté ↔ connecté* | Transition : `fetchSubject` → mutation `SET_SUBJECT` → getters `isConnected`/`isAdmin` |
| **Scénarios (use‑case)** | Parcours utilisateur « Créer une étude » | 1. Login → 2. Accéder à *EtudeNew* → 3. Remplir formulaire → 4. Soumettre → 5. Vérifier message succès |
| **Tests exploratoires** | Navigation libre dans l’UI (menus, filtres) | Session de 45 min, capture des anomalies UI non‑couverts par les cas automatiques |
| **Error guessing** | Manipulation de l’URL (`/etudes/abc`) | Attente d’erreur 400/404, vérification du message d’erreur |

### 3.2 Techniques de test structurel  

| Technique | Objectif | Métrique cible |
|-----------|----------|----------------|
| **Instruction coverage** | Exerciser chaque ligne JS | ≥ 80 % (Jest) |
| **Branch coverage** | Vérifier chaque branche conditionnelle (ex. `if (id)`) | ≥ 75 % |
| **Condition coverage** | Tester chaque condition booléenne séparément | ≥ 70 % |
| **MC/DC** (si exigence critique) | Couvrir toutes les combinaisons de décision | Non requis (application non‑safety‑critical) |
| **Chemins indépendants** | Analyse cyclomatique des fonctions complexes (`filterUtilMixin.getDateRange`) | Cyclomatique ≤ 10, tous les chemins couverts |

### 3.3 Tests basés sur l’expérience  

| Type | Description |
|------|-------------|
| **Exploratoire** | Sessions de 30 min ciblant les nouvelles versions du composant `EtudesExportPanel.vue`. |
| **Error guessing** | Injection de caractères spéciaux dans les champs texte (XSS test). |
| **Check‑list** | Liste dérivée des défauts précédents (ex. “login button disabled after click”) appliquée à chaque build. |

---  

## 4️⃣ Spécification des Cas de Test (Test Case Specification) – ISO 29119‑3  

> **Template** (obligatoire) – à réutiliser dans TestRail / Xray.  

```text
[TC-XXX] <Titre du cas de test>
├── Identifiant          : TC-XXX
├── Description         : <Description concise du scénario>
├── Préconditions       : <État requis avant exécution>
├── Entrées             : <Données d’entrée (ex. JSON, valeurs UI)>
├── Étapes d'exécution  :
│   1. <Action 1>
│   2. <Action 2>
│   …
├── Résultat attendu    : <Sortie attendue / état du système>
├── Post‑conditions     : <État après exécution>
├── Priorité            : Critical / High / Medium / Low
├── Exigence couverte   : CCF‑<nnn>
└── Technique utilisée  : <Partitionnement / Table de décision / Transition d’état …>
```

### 4.1 Exemples de cas de test fonctionnels  

| ID | Titre | Exigence | Technique | Priorité |
|----|-------|----------|------------|----------|
| **TC‑F‑001** | Login valide | CCF‑001 | Partitionnement (valid/invalid) | Critical |
| **TC‑F‑002** | Login invalide (mot de passe erroné) | CCF‑001 | Partitionnement | High |
| **TC‑F‑003** | Création d’une étude – données complètes | CCF‑002 | Scénario d’usage | Critical |
| **TC‑F‑004** | Création d’une étude – champ “titre” vide | CCF‑002 | BVA (titre = “”) | High |
| **TC‑F‑005** | Export CSV d’une étude sélectionnée | CCF‑003 | Table de décision (type export) | Medium |
| **TC‑F‑006** | Filtrage par année (année min) | CCF‑004 | BVA (2011) | Medium |
| **TC‑F‑007** | Accès au tutoriel externe (lien valide) | CCF‑005 | Transition d’état (click → navigation) | Low |
| **TC‑F‑008** | Changement de thème via Vuetify (dark/light) | CCF‑006 | Exploratoire | Low |

### 4.2 Exemples de cas de test non‑fonctionnels  

| ID | Titre | Type | Objectif | Méthode |
|----|-------|------|----------|---------|
| **TC‑NF‑001** | Temps de réponse de la page d’accueil | Performance | ≤ 2 s (chargement complet) | k6 script “load_homepage” |
| **TC‑NF‑002** | Charge simultanée 100 utilisateurs (login) | Performance (stress) | Pas de dégradation > 30 % | k6 “ramp‑up” |
| **TC‑NF‑003** | Scan OWASP Top 10 – Injection SQL | Sécurité | Aucun vecteur d’injection détecté | ZAP auto‑scan |
| **TC‑NF‑004** | Test d’accessibilité (WCAG 2.1 AA) | Utilisabilité | Contraste, navigation clavier | axe‑core (Cypress) |
| **TC‑NF‑005** | Compatibilité Chrome 118 & Firefox 115 | Compatibilité | UI identique, aucun défaut visuel | Cypress cross‑browser |
| **TC‑NF‑006** | Résilience – perte de connexion API pendant édition | Fiabilité | Application récupère et affiche message d’erreur | Cypress + network‑stubbing |

---  

## 5️⃣ Procédures de Test (Test Procedures) – ISO 29119‑3  

| Étape | Action | Responsable | Artefact |
|-------|--------|-------------|----------|
| **P‑01** | **Pré‑mise en place** – provisionner l’environnement (Docker compose) | Automation Engineer | `docker-compose.yml` |
| **P‑02** | **Chargement des jeux de données** – importer fixtures (`fixtures/*.json`) | Test Analyst | `fixtures/` |
| **P‑03** | **Exécution des tests unitaires** – `yarn test:unit` | Automation Engineer | Rapport Jest (`jest-report.xml`) |
| **P‑04** | **Exécution des tests d’intégration** – `yarn test:integration` | Automation Engineer | Rapport Vue Test Utils |
| **P‑05** | **Exécution des tests Cypress** – `yarn cypress:run` (headless) | Automation Engineer | Rapport Cypress (`cypress-report.xml`) |
| **P‑06** | **Analyse de couverture** – `yarn coverage` | Automation Engineer | `coverage/` (HTML) |
| **P‑07** | **Tests de performance** – `k6 run load_homepage.js` | Performance Engineer | Rapport k6 (`k6-report.html`) |
| **P‑08** | **Tests de sécurité** – lancement ZAP | Security Analyst | Rapport ZAP (`zap-report.xml`) |
| **P‑09** | **Validation des critères de sortie** – revue des métriques | Test Manager | Dashboard de critères (`cst‑metrics.xlsx`) |
| **P‑10** | **Clôture** – mise à jour du tableau de traçabilité, archivage des artefacts | Test Manager | Traceability Matrix, Test Summary Report |

---  

## 6️⃣ Gestion des Anomalies (Defect Management) – ISO 29119‑3  

### 6.1 Classification des défauts  

| Sévérité | Définition | Exemple dans *agile‑front* |
|----------|------------|---------------------------|
| **Critique** | Blocage total, aucune solution de contournement | Crash du router → page blanche après login |
| **Majeur** | Fonction principale inopérante | Impossible de créer une étude (POST 500) |
| **Mineur** | Fonction secondaire impactée | Icône du bouton “Register” mal alignée |
| **Cosmétique** | Problème UI/UX uniquement | Faute d’orthographe dans le tooltip “Export” |

### 6.2 Cycle de vie d’un défaut  

1. **Nouveau** – créé dans Jira (`BUG-####`).  
2. **Assigné** – à un développeur Front‑end.  
3. **En cours de correction** – code modifié, commit lié (`git commit -m "FIX: …"`).  
4. **À retester** – testeur exécute le cas de régression correspondant.  
5. **Fermé** – `Résolu` (corrigé) ou `Rejeté` (non‑reproductible).  

### 6.3 Métriques de défauts  

| Métrique | Formule | Objectif |
|----------|---------|----------|
| **Densité de défauts** | nb défauts / KLOC | ≤ 0,5 |
| **Defect Escape Rate** | nb défauts détectés en prod / nb défauts totaux | ≤ 5 % |
| **MTTR** (Mean Time To Repair) | Σ (temps résolution) / nb défauts résolus | ≤ 2 j |
| **Taux de réouverture** | nb réouvertes / nb résolues | ≤ 2 % |
| **Coverage des exigences** | nb exigences testées / nb exigences totales | ≥ 95 % |

---  

## 7️⃣ Tests de Régression (ISO 29119‑6)  

| Critère | Description |
|---------|-------------|
| **Sélection** | Tous les cas de test automatisés couvrant les API `LegacyProxyService`, `SecurityService`, store `studies` et `security`, ainsi que les scénarios UI critiques (login, création/édition d’étude). |
| **Suite automatisée** | Répertoire `cypress/integration/regression/` – exécute les 50 + cas de régression à chaque pipeline. |
| **Fréquence** | À chaque merge (pipeline CI) et avant chaque release (nightly run). |
| **Inclusion** | Tests unitaires, d’intégration, E2E, performance baseline. |
| **Exclusion** | Tests UI non‑déterministes (ex. animations) – marqués `skip`. |
| **Critères d’acceptation** | Aucun test de régression ne doit échouer ; si échec, le build est bloqué. |

---  

## 8️⃣ Tests Unitaires (ISO 29119‑11)  

| Module | Framework | Couverture cible | Exemple de test |
|--------|------------|-------------------|-----------------|
| `filterUtilMixin.js` | Jest + Vue Test Utils | 90 % instruction | Vérifier que `getDateRange()` renvoie la bonne séquence d’années. |
| `SecurityService.js` | Jest (mock Axios) | 100 % | Simuler réponse 200 et vérifier que `getSubject()` renvoie `response.data`. |
| `store/modules/security.js` | Jest | 95 % | Mutation `SET_SUBJECT` met à jour l’état; getters `isConnected`/`isAdmin`. |
| `LegacyProxyService.js` | Jest (axios‑mock‑adapter) | 100 % | `postStudy({id, formData})` construit l’URL correcte et envoie POST. |
| `components/EtudesList.vue` | Vue Test Utils | 80 % | Rendu d’une liste d’études mockées, vérification du nombre d’items affichés. |

> **Stratégie TDD** – Non obligatoire, mais recommandée pour les nouveaux modules (ex. `ExportService`).  

---  

## 9️⃣ Automatisation des Tests  

| Aspect | Détails |
|-------|---------|
| **Outils** | Cypress (E2E), Jest (unit), k6 (performance), OWASP ZAP (security). |
| **Framework** | - **Cypress** : Page‑object pattern (`cypress/support/pages/`). <br> - **Jest** : `setupFilesAfterEnv` avec `@vue/test-utils`. |
| **CI/CD** | `.gitlab-ci.yml` déclenche les jobs : `unit`, `integration`, `e2e`, `perf`, `security`. <br> Artefacts (`.xml` JUnit) publiés pour les dashboards. |
| **Critères d’automatisabilité** | - Pas de dépendance à des données dynamiques non‑mockables.<br> - UI stable (pas de sélecteurs dynamiques).<br> - Temps d’exécution ≤ 5 min par job. |
| **Gestion des données** | Fixtures JSON versionnées (`cypress/fixtures/`). <br> Environnements distincts via variables CI (`API_BASE_URL`). |
| **Maintenance** | Revue mensuelle des scripts, mise à jour des sélecteurs après refactor UI. |

---  

## 🔟 Environnements de Test  

| Environnement | Configuration détaillée | Usage |
|---------------|------------------------|-------|
| **DEV** | Node 14, Yarn 1.22, Chrome 118 (headless), API mock (WireMock) | Développement, tests unitaires |
| **INT** | Docker compose (api‑mock + DB SQLite), Chrome 118, Firefox 115 | Tests d’intégration, validation API |
| **REC** | VM Ubuntu 22.04, Chrome 118 (non‑headless), base de données anonymisée, réseau réel | Recette fonctionnelle & non‑fonctionnelle |
| **PERF** | k6 runner, API sandbox (prod‑like), charge 0‑200 rps | Tests de charge, endurance |
| **PREPROD** | Mirror prod (same config, données réelles) | Validation finale, UAT client |

---  

## 1️⃣1️⃣ Rapports & Métriques  

### 11.1 Rapports de test  

| Rapport | Fréquence | Destinataire | Contenu |
|--------|-----------|--------------|---------|
| **Daily Test Execution** | Quotidien (fin de journée) | Test Manager, Dev Leads | Nombre de cas exécutés, échecs, défauts nouveaux |
| **Sprint Test Summary** | Fin de sprint (2 semaines) | PO, QA, Management | Couverture, critères d’entrée/sortie, défauts critiques |
| **Release Test Report** | Avant chaque release | Stakeholders | Résultats globaux, KPI, recommandations |
| **Post‑Release Defect Escape** | 1 mois après release | QA, Ops | Défauts en prod, analyse des causes |

### 11.2 KPIs (Key Performance Indicators)  

| KPI | Formule | Valeur cible |
|-----|---------|--------------|
| **Couverture des exigences** | (Exigences testées / Total exigences) × 100 | ≥ 95 % |
| **Couverture de code** | (Lignes couvertes / Lignes totales) × 100 | ≥ 80 % |
| **Taux de réussite des tests** | (Tests passés / Tests exécutés) × 100 | ≥ 98 % |
| **Densité de défauts** | Nb défauts / KLOC | ≤ 0,5 |
| **Effort de test** | Jours/homme dépensés / Points fonctionnels | ≤ 1 j/pt |
| **Productivité** | Cas de test créés / jour | ≥ 10 |
| **Défaut escape rate** | Nb défauts détectés en prod / Nb défauts totaux | ≤ 5 % |
| **MTTR** | Σ (temps de correction) / Nb défauts résolus | ≤ 2 j |

---  

## 1️⃣2️⃣ Organisation & Responsabilités  

| Rôle | Responsable | Responsabilités clés |
|------|-------------|----------------------|
| **Test Manager** | Alice Dupont (QA Lead) | Définit stratégie, approuve livrables, suit KPIs |
| **Test Analyst** | Bruno Martin | Rédaction cas de test, traçabilité CCF↔TC |
| **Automation Engineer** | Clara Zhou | Scripts Cypress/Jest, intégration CI |
| **Performance Engineer** | David Leclerc | Scénarios k6, analyse résultats |
| **Security Analyst** | Eva Gómez | Scans ZAP, revues code sécurité |
| **Developpeur Front‑end** | Équipe (3) | Assistance data, correction défauts |
| **Product Owner** | – | Validation critères d’acceptation |
| **Ops / Release Engineer** | – | Déploiement, monitoring post‑release |

### Matrice RACI (extrait)

| Activité | Test Manager | Test Analyst | Automation Engineer | Dev | PO |
|----------|--------------|--------------|--------------------|-----|----|
| Définir exigences de test | A | R | – | C | C |
| Rédiger cas de test | – | R | – | C | I |
| Implémenter automatisation | – | – | R | C | I |
| Exécuter tests unitaires | – | – | R | – | I |
| Exécuter tests E2E | – | – | R | – | I |
| Analyser résultats & KPI | R | – | – | C | A |
| Signoff Release | A | – | – | C | R |

---  

## 1️⃣3️⃣ Gestion des Configurations  

| Élément | Gestion | Outil |
|---------|---------|-------|
| **Cas de test** | Versionning (Git) – chaque modification crée un commit avec tag `TC-<num>` | TestRail (synchronisation Git) |
| **Jeux de données** | Dossiers `cypress/fixtures/` versionnés | Git |
| **Scripts de test** | Branch `test/automation` → merge `main` après review | GitLab CI |
| **Configurations d’environnement** | Fichiers `.env.*`, `vue.config.js` | Git (exclure secrets) |
| **Traçabilité** | Table `Requirement ↔ Test Case` dans TestRail | TestRail ↔ Jira (link) |

---  

## 📎 Annexes  

1. **Table de traçabilité Exigence ↔ Cas de test** (extrait)  

| Exigence (CCF) | Cas de test associés |
|----------------|----------------------|
| CCF‑001 (Login) | TC‑F‑001, TC‑F‑002, TC‑NF‑003 |
| CCF‑002 (CRUD études) | TC‑F‑003, TC‑F‑004, TC‑F‑005, TC‑NF‑001 |
| CCF‑003 (Export) | TC‑F‑005, TC‑NF‑002 |
| CCF‑004 (Filtrage) | TC‑F‑006, TC‑NF‑004 |
| CCF‑005 (Tutoriels) | TC‑F‑007 |
| CCF‑006 (Thème Vuetify) | TC‑F‑008 |
| CCF‑007 (Routing) | TC‑F‑001, TC‑F‑003 |
| CCF‑008 (Paramétrage) | TC‑NF‑005 |

2. **Matrice de couverture des techniques de test**  

| Technique | % de cas appliqués |
|-----------|--------------------|
| Partitionnement | 45 % |
| BVA | 20 % |
| Table de décision | 15 % |
| Transition d’état | 10 % |
| Exploratoire | 5 % |
| Error guessing | 5 % |

3. **Exemple de script Cypress (Login)**  

```javascript
// cypress/integration/login_spec.js
describe('Login – scénario fonctionnel', () => {
  beforeEach(() => {
    cy.intercept('GET', '/security/subject', { fixture: 'subject.json' }).as('getSubject');
  });

  it('TC-F-001 – Login valide', () => {
    cy.visit('/login');
    cy.get('input[label="Username"]').type('test.user');
    cy.get('input[label="Password"]').type('P@ssw0rd');
    cy.get('button').contains('Login').click();

    cy.wait('@getSubject').its('response.statusCode').should('eq', 200);
    cy.url().should('include', '/home');
    cy.contains('Welcome').should('be.visible');
  });
});
```

4. **Exemple de script k6 (load_homepage.js)**  

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  stages: [
    { duration: '30s', target: 20 }, // ramp‑up
    { duration: '2m', target: 20 },  // steady
    { duration: '30s', target: 0 }  // ramp‑down
  ],
};

export default function () {
  const res = http.get('https://agile-front.example.com/');
  check(res, {
    'status 200': r => r.status === 200,
    'response time < 2000ms': r => r.timings.duration < 2000,
  });
  sleep(1);
}
```

---  

## 📚 Conclusion  

Ce **Cahier des Spécifications Techniques** décrit l’ensemble du cadre de test nécessaire pour garantir la qualité du projet *agile‑front* conformément à la norme **ISO/IEC/IEEE 29119**.  

- La **stratégie** repose sur une approche **risque‑driven**, combinant tests unitaires, d’intégration, système et acceptation.  
- Le **plan** fixe les critères d’entrée/sortie, les ressources, le calendrier et les jalons.  
- La **conception** utilise les meilleures techniques de test fonctionnel et structurel, tout en capitalisant sur l’expérience (exploratoire, error‑guessing).  
- Les **cas de test** sont formalisés, traçables à chaque exigence fonctionnelle et non‑fonctionnelle.  
- La **gestion des défauts**, les **tests de régression**, l’**automatisation**, les **environnements**, les **rapports** et les **KPIs** assurent une maîtrise continue du processus qualité.  

Le respect de ce CST permettra d’obtenir une **couverture élevée**, de **minimiser les défauts en production** et de livrer un produit fiable, sécurisé et performant.  

---  

*Document généré le 27 avril 2026 – Version 1.0 – Auteur : ChatGPT (OpenAI) – Références ISO 29119‑1…‑11.*  