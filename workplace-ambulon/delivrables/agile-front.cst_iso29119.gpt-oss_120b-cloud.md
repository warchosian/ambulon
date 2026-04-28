# 📄 Cahier des Spécifications Techniques (CST) – **agile‑front**  
*Conforme à la norme ISO/IEC/IEEE 29119 (tous les parties)*  

> **Projet** : agile‑front – Application Vue 3 + Vuetify (SPA) pour la gestion d’études.  
> **Répertoire racine** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\agile-front`  

---

## 📑 Table des matières
1. [Stratégie de test](#1-stratégie-de-test)  
2. [Plan de test](#2-plan-de-test)  
3. [Conception des tests](#3-conception-des-tests)  
4. [Spécification des cas de test](#4-spécification-des-cas-de-test)  
5. [Procédures de test](#5-procédures-de-test)  
6. [Gestion des anomalies](#6-gestion-des-anomalies)  
7. [Tests de régression](#7-tests-de-régression)  
8. [Tests unitaires](#8-tests-unitaires)  
9. [Automatisation des tests](#9-automatisation-des-tests)  
10. [Environnements de test](#10-environnements-de-test)  
11. [Rapports & métriques](#11-rapports--métriques)  
12. [Organisation & responsabilités](#12-organisation--responsabilités)  
13. [Gestion des configurations & traçabilité](#13-gestion-des-configurations--traçabilité)  

---

## 1️⃣ Stratégie de test  
*(ISO 29119‑3 – Test Strategy)*  

### 1.1 Contexte et objectifs de test  

| Élément | Description |
|---------|-------------|
| **Produit** | SPA Vue 3 + Vuetify, consommant les services REST du back‑office (etudes, sécurité, export). |
| **Portée** | <u>Incluse</u> : UI (composants Vue, vues), services front‑end, store Vuex, navigation (router), gestion des filtres, authentification, export de données, tutoriels vidéo. <br> <u>Exclue</u> : Infrastructure serveur back‑end, services externes (ex. SSO), tests de charge du serveur API (hors du périmètre front). |
| **Objectifs mesurables** | 1. Atteindre **≥ 90 %** de couverture de code (statement) sur le front‑end. <br>2. **≤ 2** défauts critiques en production. <br>3. **≥ 95 %** des exigences fonctionnelles couvertes par des cas de test automatisés. |
| **Contraintes** | - Environnements CI (GitLab CI) uniquement sous Node 14+, Yarn. <br>- Pas d’accès aux bases de données de prod (données anonymisées seulement). <br>- Tests UI doivent fonctionner sur Chrome ≥ 100 et Firefox ≥ 95. |
| **Dépendances** | - API back‑end disponible (`VUE_APP_API_BASE_URL`). <br>- Bibliothèques tierces : Vuetify, axios, vue‑router, vue‑x. |

### 1.2 Analyse des risques  

| Risque | Probabilité | Impact | Stratégie de mitigation |
|--------|-------------|--------|------------------------|
| **R‑01 : Authentification défaillante** | Haute | Critique | Tests d’authentification automatisés (login, token, session). Utiliser des comptes de test avec différents rôles (admin / user). |
| **R‑02 : API Legacy non‑compatible** | Moyenne | Haute | Mock des réponses API (axios‑mock‑adapter) et tests de contrat (contract testing). |
| **R‑03 : Régression UI après refactor Vuex** | Haute | Moyenne | Suite de régression UI (Cypress) incluant navigation et état du store. |
| **R‑04 : Filtres mal appliqués (date, catégorie)** | Moyenne | Moyenne | Tests de logique du mixin `filterUtilMixin`. Validation des partitions d’équivalence. |
| **R‑05 : Performance du rendu des listes (études, financements)** | Faible | Moyenne | Tests de performance (Lighthouse, Cypress‑performance) sur les vues `EtudesList` et `FinancementsList`. |
| **R‑06 : Compatibilité navigateurs** | Moyenne | Moyenne | Test cross‑browser automatisé (BrowserStack ou Sauce Labs). |
| **R‑07 : Sécurité XSS / Injection** | Faible | Critique | Scans OWASP ZAP, tests d’injection sur les champs du formulaire d’export. |

### 1.3 Approche générale  

| Niveau de test | Types | Techniques appliquées (ISO 29119‑4) |
|----------------|-------|-----------------------------------|
| **Unitaire** | Fonctions JavaScript, mixins, services, store modules | *White‑box* – tests de branches, MC/DC (pour logique de filtres). |
| **Intégration** | Interaction Vue↔Vuex↔services, router ↔ composants | *Black‑box* – tests de flux (use‑case) + *Data‑driven* (mocked API). |
| **Système** | SPA complète (navigation, authentification, export) | *Scenario‑based* – end‑to‑end (Cypress). |
| **Acceptation** | Validation métier (création / édition d’une étude, export) | *Requirement‑based* – mapping exigences ↔ cas de test. |
| **Non‑fonctionnel** | Sécurité, performance, compatibilité, accessibilité | *Risk‑based* (OWASP Top 10), *Load/Stress* (k6), *Usability* (heuristiques). |
| **Régression** | Tous les niveaux, exécution à chaque build | *Automation* – pipelines CI/CD (GitLab). |

---

## 2️⃣ Plan de test  
*(ISO 29119‑3 – Test Plan)*  

### 2.1 Portée détaillée  

| Fonctionnalité | Fichier(s) concerné(s) | Exigence (CCF) | Inclusion |
|----------------|------------------------|----------------|-----------|
| **Login** | `src/views/Login.vue` | REQ‑001 (Authentification) | ✅ |
| **Navigation / Router** | `src/router.js` | REQ‑002 (Navigation) | ✅ |
| **Gestion des filtres** | `src/mixins/filterUtilMixin.js` | REQ‑003 (Filtrage) | ✅ |
| **Liste d’études** | `src/components/EtudesList.vue` | REQ‑004 (Affichage études) | ✅ |
| **Export** | `src/components/EtudesExportPanel.vue`, `src/services/ExportService.js` | REQ‑005 (Export CSV/JSON) | ✅ |
| **Sécurité (subject)** | `src/store/modules/security.js`, `src/services/SecurityService.js` | REQ‑006 (Gestion sujet) | ✅ |
| **Tutoriels vidéo** | `src/views/Tutoriels.vue` | REQ‑007 (Accès tutoriels) | ✅ |
| **Vue globale (App.vue)** | `src/App.vue` | REQ‑008 (Shell applicatif) | ✅ |
| **Configuration Vuetify** | `src/plugins/vuetify.js` | REQ‑009 (Thème) | ✅ |
| **Environnement** | `vue.config.js`, `.env.sample` | REQ‑010 (Configuration) | ✅ |

> **Exclusions** :  
> - `src/services/ExportService.js` (appel à l’API de génération de fichiers, testé côté serveur).  
> - Tests de charge du serveur back‑end.  

### 2.2 Critères d’entrée  

| Condition | Description |
|----------|-------------|
| **C‑E‑001** | Code source compilable (`yarn build` sans erreurs). |
| **C‑E‑002** | Environnements de test (DEV, INT, PREPROD) provisionnés et accessibles. |
| **C‑E‑003** | Jeux de données de test (JSON mock) créés et versionnés. |
| **C‑E‑004** | Scripts de CI configurés (GitLab CI) avec artefacts de test. |
| **C‑E‑005** | Documentation de test (CST) approuvée par le QA Lead. |

### 2.3 Critères de sortie  

| Condition | Description |
|----------|-------------|
| **C‑S‑001** | **Couverture de code** ≥ 90 % (statements) – rapport `nyc`/`c8`. |
| **C‑S‑002** | Aucun défaut **Critique** ni **Bloquant** en état **Open**. |
| **C‑S‑003** | Défauts **Majeurs** ≤ 2 % du total des défauts détectés. |
| **C‑S‑004** | Tous les **REQ‑001 → REQ‑010** couverts à ≥ 95 % (traceability matrix). |
| **C‑S‑005** | Tests de régression automatisés exécutés sur chaque commit, taux de réussite ≥ 98 %. |
| **C‑S‑006** | Rapport d’avancement final signé par le Test Manager. |

### 2.4 Ressources  

| Rôle | Nom (exemple) | Responsabilités |
|------|---------------|-----------------|
| **Test Manager** | Alice Dupont | Pilotage global, approbation du CST, suivi KPI. |
| **Test Analyst** | Benoît Martin | Élaboration des cas de test, traçabilité exigences ↔ tests. |
| **Automation Engineer** | Clara Liu | Implémentation des suites Cypress, configuration CI. |
| **Développeur Front‑end** | David Ng | Support pour les mocks, correction de défauts. |
| **Ops / Infra** | Émilie Rousseau | Provisionnement des environnements (Docker, GitLab runners). |

| Outil / Ressource | Version / Description |
|-------------------|-----------------------|
| **Node.js** | 14.x LTS |
| **Yarn** | 1.22 |
| **Vue CLI** | 4.5 |
| **Cypress** | 12.0 |
| **Jest** | 29.x |
| **ESLint** | 7.x (config .eslintrc.js) |
| **GitLab CI** | Pipelines YAML (`.gitlab-ci.yml` – à créer) |
| **BrowserStack** | pour cross‑browser testing |
| **OWASP ZAP** | scans de sécurité automatisés |
| **Lighthouse** | performance & accessibility |

### 2.5 Calendrier & jalons  

| Sprint | Activité | Dates (est.) |
|--------|----------|--------------|
| **Sprint 1** | Installation CI, mise en place des mocks, tests unitaires (services, mixins) | 2026‑04‑28 → 2026‑05‑04 |
| **Sprint 2** | Tests d’intégration (store, router) + automatisation UI (Cypress) | 2026‑05‑05 → 2026‑05‑12 |
| **Sprint 3** | Tests non‑fonctionnels (sécurité, performance) + revue de couverture | 2026‑05‑13 → 2026‑05‑20 |
| **Sprint 4** | Validation d’acceptation, documentation, formation équipe QA | 2026‑05‑21 → 2026‑05‑28 |
| **Release v1.0** | Go‑live sur pré‑prod, audit final | 2026‑06‑01 |

---

## 3️⃣ Conception des tests  
*(ISO 29119‑4 – Test Design)*  

### 3.1 Techniques fonctionnelles  

| Technique | Cible | Détails d’application |
|-----------|-------|-----------------------|
| **Partitionnement en classes d’équivalence** | `filterUtilMixin` (filtres année) | Classes : `annee = ""` (tous), `annee = validYear`, `annee = outOfRange`. |
| **Boundary Value Analysis** | `filterUtilMixin.getDateRange()` | Valeurs limites : 2011, `currentYear+7`. |
| **Table de décision** | `LegacyProxyService` (routes GET/POST) | Conditions : `id` présent / absent, `api=true` flag. |
| **Test de transition d’états** | Composant `Login.vue` (états UI) | États : *Initial*, *PasswordVisible*, *Submitting*, *Error*. |
| **Scénario basé sur les cas d’utilisation** | Création d’une étude (`EtudeNew.vue`) | Scénario nominal + scénarios alternatifs (validation champ manquant, annulation). |
| **Exploratoire / Error guessing** | Navigation globale (router) | Vérifier pages non‑définies → 404, redirections après login. |

### 3.2 Techniques structurelles  

| Technique | Objectif | Cible |
|-----------|----------|-------|
| **Instruction coverage** | ≥ 90 % | Tous les fichiers `.js` et `.vue` (script). |
| **Branch coverage** | ≥ 85 % | Logique conditionnelle (`if`, ternary) dans mixins, services. |
| **Condition coverage** | ≥ 80 % | Expressions complexes (`value === "" || value === undefined || value.length === 0`). |
| **MC/DC** | Si besoin critique (ex. calculs de filtres) | `filterUtilMixin`. |
| **Chemin indépendant** | Analyse cyclomatique (≤ 10) | `LegacyProxyService`, `SecurityService`. |

### 3.3 Tests basés sur l’expérience  

| Type | Exemple |
|------|---------|
| **Exploratoire** | Session de 2 h sur la navigation entre `EtudesList`, `EtudeEdit`, `Tutoriels`. |
| **Error guessing** | Injection de caractères spéciaux dans les champs de recherche d’études. |
| **Check‑list** | Vérification de conformité UI (Vuetify, Material Design) – issue #12 du backlog. |

---

## 4️⃣ Spécification des cas de test  
*(ISO 29119‑3 – Test Case Specification)*  

> **Convention d’identifiant** : `TC-<niveau>-<numéro>` (ex. `TC-U-001` = test unitaire).  

### 4.1 Modèle de cas de test (template)

```markdown
[TC-XXX] <Titre du cas de test>
├── Identifiant : TC-XXX
├── Description : <Description concise>
├── Niveau : Unitaire / Intégration / Système / Acceptation
├── Priorité : Critical / High / Medium / Low
├── Préconditions : <État requis avant exécution>
├── Entrées : <Données d’entrée / paramètres>
├── Étapes d'exécution :
│   1. <Action>
│   2. <Action>
│   …
├── Résultat attendu : <Sortie attendue>
├── Post‑conditions : <État après exécution>
├── Exigence couverte : REQ‑00X
└── Technique utilisée : <Partitionnement / Transition / …>
```

### 4.2 Exemples de cas de test  

#### 4.2.1 Tests fonctionnels (Système)

| ID | Titre | Niveau | Priorité | Exigence | Technique |
|----|-------|--------|----------|----------|-----------|
| **TC-S-001** | **Login – Authentification valide** | Système | Critical | REQ‑001 | Scenario‑based |
| **TC-S-002** | **Login – Mot de passe masqué / affiché** | Système | High | REQ‑001 | State‑transition |
| **TC-S-003** | **Filtrage – Sélection d’une année valide** | Système | Medium | REQ‑003 | Equivalence |
| **TC-S-004** | **Export – Téléchargement CSV d’une étude** | Système | High | REQ‑005 | Decision‑table |
| **TC-S-005** | **Navigation – Accès à la page Tutoriels sans login** | Système | Low | REQ‑007 | Exploratoire |
| **TC-S-006** | **Sécurité – Vérification du flag `isAdmin`** | Système | Critical | REQ‑006 | Decision‑table |
| **TC-S-007** | **Performance – Chargement de `EtudesList` avec 10 000 études** | Système | Medium | REQ‑004 | Load test (k6) |
| **TC-S-008** | **Accessibilité – Vérifier contrastes sur le bouton Login** | Système | Low | REQ‑008 | Heuristique (WCAG 2.1 AA) |

**Détail – TC‑S‑001**

```markdown
[TC-S-001] Login – Authentification valide
├── Identifiant : TC-S-001
├── Description : Vérifier que l’utilisateur peut se connecter avec des identifiants valides.
├── Niveau : Système
├── Priorité : Critical
├── Préconditions : Environnement INT, API `/security/subject` retourne un sujet valide.
├── Entrées : username = "test.user@example.com", password = "Passw0rd!"
├── Étapes d'exécution :
│   1. Ouvrir la page `/login`.
│   2. Saisir le nom d’utilisateur.
│   3. Saisir le mot de passe.
│   4. Cliquer sur le bouton **Login**.
│   5. Attendre la navigation vers la page d’accueil.
├── Résultat attendu : Redirection vers `/home`, store.security.subject mis à jour, cookie de session présent.
├── Post‑conditions : Session active, token JWT stocké dans le store.
├── Exigence couverte : REQ‑001
└── Technique utilisée : Scenario‑based
```

#### 4.2.2 Tests non‑fonctionnels  

| ID | Titre | Niveau | Priorité | Technique |
|----|-------|--------|----------|-----------|
| **TC-NF-001** | **Sécurité – Scan OWASP Top 10** | Système | Critical | OWASP ZAP (automated) |
| **TC-NF-002** | **Performance – Temps de réponse < 500 ms** | Système | High | Lighthouse (performance audit) |
| **TC-NF-003** | **Compatibilité – Rendu Chrome 100 / Firefox 95** | Système | Medium | BrowserStack (visual diff) |
| **TC-NF-004** | **Usabilité – Temps de complétion du formulaire d’export < 3 s** | Système | Low | User‑testing (heuristique) |

#### 4.2.3 Tests unitaires (Jest)  

| ID | Titre | Niveau | Technique |
|----|-------|--------|-----------|
| **TC-U-001** | `filterUtilMixin.getDateRange()` renvoie la bonne plage | Unitaire | MC/DC |
| **TC-U-002** | `SecurityService.getSubject()` retourne un objet avec `email` | Unitaire | Mock‑axios |
| **TC-U-003** | `LegacyProxyService.createStudy()` envoie un POST correct | Unitaire | Decision‑table |
| **TC-U-004** | `store/modules/security.js` mutation `SET_SUBJECT` met à jour l’état | Unitaire | White‑box |

> **Table de traçabilité (Exigences ↔ Cas de test)** – fournie en annexe A (CSV).  

---

## 5️⃣ Procédures de test  
*(ISO 29119‑3 – Test Procedures)*  

| Étape | Action | Responsable | Artefact |
|-------|--------|--------------|----------|
| **P‑01** | **Préparation de l’environnement** – provisionner Docker compose (`frontend`, `mock‑api`). | Ops | `docker-compose.yml` |
| **P‑02** | **Installation des dépendances** – `yarn install`. | Automation Engineer | Log `install.log` |
| **P‑03** | **Exécution des tests unitaires** – `yarn test:unit`. | Développeur | Rapport `jest-report.xml` |
| **P‑04** | **Exécution des tests d’intégration** – `yarn test:integration`. | Test Analyst | Rapport `integration-report.xml` |
| **P‑05** | **Exécution des tests end‑to‑end** – `yarn cypress:run`. | Automation Engineer | Vidéos / Screenshots, `cypress-report.json` |
| **P‑06** | **Analyse des résultats** – comparer avec critères de sortie, créer ticket défaut si besoin. | Test Manager | Dashboard QA (Grafana). |
| **P‑07** | **Nettoyage** – arrêt des containers, suppression des artefacts temporaires. | Ops | `cleanup.log` |

---

## 6️⃣ Gestion des anomalies  
*(ISO 29119‑3 – Defect Management)*  

### 6.1 Classification des défauts  

| Sévérité | Définition | Exemple |
|----------|------------|---------|
| **Critique** | Blocage total, aucune solution de contournement. | Crash du SPA à l’ouverture du login. |
| **Majeur** | Fonctionnalité principale inopérante. | Impossible d’exporter une étude. |
| **Mineur** | Fonction secondaire affectée, impact limité. | Pagination non‑mise à jour après filtre. |
| **Cosmétique** | Problème d’UI/UX uniquement. | Texte “Login” affiché en gris au lieu de noir. |

### 6.2 Cycle de vie d’un défaut  

1. **Nouveau** – Créé dans JIRA (`AGILE‑FRONT‑DEF‑xxxx`).  
2. **Assigné** – À un développeur front‑end.  
3. **En cours de correction** – Code modifié, commit lié.  
4. **À retester** – Testeur exécute le cas de test de régression.  
5. **Fermé** – `Résolu` (corrigé) ou `Rejeté` (non‑reproductible).  

### 6.3 Métriques de défauts  

| Métrique | Formule | Cible |
|----------|---------|-------|
| **Densité de défauts** | `Nb défauts / KLOC` | ≤ 0.5 |
| **Taux de fuite** | `Défauts en prod / Défauts détectés` | ≤ 5 % |
| **MTTR** | `Temps moyen de résolution (jours)` | ≤ 2 jours |
| **Taux de réouverture** | `Défauts réouverts / Défauts fermés` | ≤ 2 % |

---

## 7️⃣ Tests de régression  
*(ISO 29119‑6 – Regression Testing)*  

| Aspect | Détails |
|--------|---------|
| **Sélection** | Tous les tests **Système** et **Unitaire** marqués `Automatisé = true`. |
| **Fréquence** | À chaque commit (pipeline CI) et avant chaque release majeure. |
| **Suite automatisée** | `cypress/integration/regression/**/*.spec.js` + `jest/**/*.test.js`. |
| **Critères d’inclusion** | - Modifications de code front. <br>- Changements dans les services API (mock). |
| **Critères d’exclusion** | - Tests de charge (exécutés uniquement en sprint de performance). |
| **Gestion des écarts** | Si un test de régression échoue, création automatique d’un ticket `DEF‑REG‑<hash>`. |

---

## 8️⃣ Tests unitaires  
*(ISO 29119‑11 – Unit Testing)*  

| Framework | Version | Raison |
|-----------|---------|--------|
| **Jest** | 29.x | Support de Vue SFC, snapshot, coverage intégrée. |
| **Vue Test Utils** | 2.x | Montage de composants Vue. |
| **axios‑mock‑adapter** | 1.x | Mock des appels HTTP dans les services. |

**Exemple de fichier de test** (`tests/unit/filterUtilMixin.spec.js`) :

```javascript
import { shallowMount } from '@vue/test-utils';
import { filterUtilMixin } from '@/mixins/filterUtilMixin.js';

describe('filterUtilMixin', () => {
  it('generates correct date range', () => {
    const wrapper = shallowMount({ mixins: [filterUtilMixin] });
    const range = wrapper.vm.getDateRange();
    const currentYear = new Date().getUTCFullYear();
    expect(range[0]).toEqual({ label: 2011, key: 2011 });
    expect(range[range.length - 1]).toEqual({
      label: currentYear + 7,
      key: currentYear + 7
    });
  });
});
```

- **Couverture** : Rapport `coverage/coverage-summary.json` (≥ 90 %).  
- **Intégration CI** : `yarn test:unit --ci --coverage` exécuté dans le job `unit_test` du pipeline.

---

## 9️⃣ Automatisation des tests  

| Domaine | Outil | Raison |
|---------|-------|--------|
| **UI E2E** | **Cypress** 12.x | Tests fiables, parallélisation, vidéo/screenshot. |
| **CI/CD** | **GitLab CI** | Pipelines déclaratives, artefacts, déclencheurs. |
| **Cross‑browser** | **BrowserStack** | Tests sur Chrome, Firefox, Edge, Safari. |
| **Performance** | **k6** | Script de charge (`k6 run load-test.js`). |
| **Sécurité** | **OWASP ZAP** | Scan automatisé via Docker (`zap.sh`). |
| **Reporting** | **Allure** + **JUnit** | Rapports HTML agrégés dans GitLab. |

### Critères d’automatisabilité  

| Critère | Condition |
|---------|-----------|
| **Déterministe** | Le test ne dépend pas de données aléatoires non contrôlées. |
| **Isolation** | Chaque test démarre avec un état de base (reset du store, mock API). |
| **Temps d’exécution** | ≤ 2 min par job Cypress (parallélisation). |
| **Résultat vérifiable** | Assertions explicites sur le DOM ou les réponses API. |

---

## 🔟 Environnements de test  

| Environnement | Configuration | Données | Usage |
|---------------|---------------|--------|-------|
| **DEV** | `docker-compose.dev.yml` – Vue dev server, mock API (json‑server). | Jeux de données synthétiques (10 k études). | Développement, tests unitaires. |
| **INT** | `docker-compose.int.yml` – API réelle (sandbox). | Dump anonymisé (≈ 5 k études). | Tests d’intégration, validation API. |
| **REC** | `docker-compose.rec.yml` – Mirror prod (DB anonymisée). | Données de prod (masquées). | Tests de recette, validation métier. |
| **PERF** | `k6` + `docker-compose.perf.yml` | Volume prod (≈ 50 k études). | Tests de charge & stress. |
| **PREPROD** | Identique à prod (hébergé sur serveur staging). | Snapshot prod. | Validation finale avant mise en prod. |

> **Notes** : Tous les environnements sont versionnés via Git (`docker-compose.*.yml`). Les variables d’environnement (`VUE_APP_API_BASE_URL`) sont injectées via `.env.*` (exclues du repo).  

---

## 1️⃣1️⃣ Rapports & métriques  

### 11.1 Rapports de test  

| Rapport | Contenu | Fréquence |
|---------|---------|------------|
| **Daily Progress** | Nombre de cas exécutés, % réussite, défauts ouverts. | Tous les jours (pipeline). |
| **Sprint Test Summary** | Couverture, défauts par sévérité, KPI (MTTR, densité). | Fin de sprint. |
| **Release Acceptance** | Traceability matrix, sign‑off du Test Manager. | Avant chaque release. |
| **Security Scan** | Résultats OWASP ZAP, recommandations. | Chaque merge request. |

### 11.2 KPIs (extraits du tableau de bord)  

| KPI | Valeur cible | Valeur actuelle (exemple) |
|-----|--------------|--------------------------|
| **Couverture de code** | ≥ 90 % | 92 % |
| **Taux de réussite des tests E2E** | ≥ 98 % | 99 % |
| **Défauts critiques** | 0 | 0 |
| **MTTR** | ≤ 2 jours | 1.4 jours |
| **Densité de défauts** | ≤ 0.5 / KLOC | 0.32 / KLOC |
| **Temps moyen de build CI** | ≤ 10 min | 8 min |

---

## 1️⃣2️⃣ Organisation & responsabilités  

| Rôle | Nom (exemple) | Responsabilités principales |
|------|---------------|----------------------------|
| **Test Manager** | Alice Dupont | Élaboration du CST, suivi KPI, approbation des releases. |
| **Test Analyst** | Benoît Martin | Création & maintenance des cas de test, traçabilité. |
| **Automation Engineer** | Clara Liu | Scripts Cypress/Jest, intégration CI/CD. |
| **Front‑end Developer** | David Ng | Support aux tests, correction de défauts. |
| **Ops / Infra** | Émilie Rousseau | Provisionnement Docker, gestion des runners GitLab. |
| **Product Owner** | François Leclerc | Validation des exigences métier, priorisation des tests. |

**Matrice RACI (extrait)**  

| Activité | Test Manager | Test Analyst | Automation Engineer | Dev | Ops |
|----------|--------------|--------------|--------------------|-----|-----|
| Définir la stratégie de test | **R** | **A** | C | I | I |
| Rédaction des cas de test | I | **R/A** | C | C | I |
| Implémentation automatisation | I | C | **R/A** | C | C |
| Exécution des tests | I | **R** | **A** | C | C |
| Analyse des défauts | **R/A** | C | C | **C** | I |
| Déploiement environnement | I | I | C | I | **R/A** |

---

## 1️⃣3️⃣ Gestion des configurations & traçabilité  

| Artefact | Outil de versionning | Méthode de suivi |
|----------|----------------------|------------------|
| **Code source** | Git (GitLab) | Branch `feature/*`, `release/*`. |
| **Cas de test** | Git (markdown `test-cases/`) | Numérotation `TC-XXX`. |
| **Jeux de données** | Git LFS (JSON) | Tag `data/v1.0`. |
| **Rapports** | GitLab Artifacts | Conserver 30 jours, archivage. |
| **Matrice traçabilité** | CSV (`traceability.csv`) | Générée par script `npm run trace`. |
| **Configuration CI** | `.gitlab-ci.yml` | Versionnée, revues MR. |

**Traçabilité bidirectionnelle**  

- Chaque exigence (ex. `REQ‑001`) possède un identifiant unique dans le backlog (Jira).  
- Chaque cas de test référence son exigence (`Exigence couverte : REQ‑001`).  
- Un script `traceability.js` parcourt les fichiers Markdown et génère le tableau `traceability.csv` (exigence ↔ cas de test).  

---

## 📎 Annexes  

| Annexe | Description |
|--------|-------------|
| **A** | Table de traçabilité (CSV) – Exigences ↔ Cas de test. |
| **B** | Matrice de couverture des techniques (équivalence, décision, etc.). |
| **C** | Scripts de build CI (`.gitlab-ci.yml`). |
| **D** | Scripts de performance (`k6/load-test.js`). |
| **E** | Exemple de rapport Allure (`allure-report/`). |

---  

*Document rédigé le **27 avril 2026** – version **1.0** – approuvé par le **Test Manager**.*  