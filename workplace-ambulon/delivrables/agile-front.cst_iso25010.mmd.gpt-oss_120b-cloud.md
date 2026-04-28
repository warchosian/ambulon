# 📄 Cahier des Spécifications Techniques (CST) – **agile‑front**  
**Projet** : agile‑front – Application Vue.js (Vue 2 + Vuetify)  
**Références** : ISO/IEC 25010:2023 – Modèle de qualité produit, 8 caractéristiques, 31 sous‑caractéristiques  

---  

## 1️⃣ Introduction et contexte qualité  

| Élément | Description |
|---------|-------------|
| **Objectifs qualité** | • Fournir une interface web responsive, ergonomique et fiable pour la saisie, la consultation et l’export de données d’études.<br>• Garantir la continuité de service (≥ 99,5 % de disponibilité) et la protection des données utilisateurs (conformité RGPD). |
| **Contexte métier** | Portail interne du ministère de la Transition écologique (ex : « Agile »). Utilisateurs : agents, experts, administrateurs. Fonctionnalités clés : connexion, consultation d’études, création/modification, export, visualisation de tutoriels/vidéos. |
| **Contexte technique** | • Front : Vue 2 (CLI) + Vuetify 2, JavaScript ES6, Babel, PostCSS.<br>• Build : Webpack via `vue-cli-service`.<br>• Déploiement : serveur HTTP (NGINX) en mode SPA, base‑URL configurable (`VUE_APP_API_BASE_URL`).<br>• Gestion d’état : Vuex (modules `studies` et `security`). |
| **Références aux exigences fonctionnelles (CCF)** | Les exigences fonctionnelles sont décrites dans les composants Vue (ex : `Login.vue`, `EtudesList.vue`, `EtudesExportPanel.vue`, `SecurityService.js`). Chaque CCF sera tracé dans la **Matrice CCF ↔ CST** (section 9). |
| **Méthodologie d’évaluation** | • **Revues de code** (ESLint, Prettier, SonarQube).<br>• **Tests automatisés** (Jest + Vue Test Utils) – couverture ≥ 80 %.<br>• **Tests de performance** (Lighthouse, k6) – temps de réponse ≤ 1 s (95ᵉ percentile).<br>• **Analyse de sécurité** (OWASP ZAP, Snyk).<br>• **Mesure en production** (Grafana + Prometheus). |

---  

## 2️⃣ Modèle de qualité ISO 25010  

```
                    ┌─────────────────────────────────────┐
                    │   QUALITÉ DU PRODUIT LOGICIEL        │
                    └─────────────────────────────────────┘
                                    │
   ┌───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┐
   │       │       │       │       │       │       │       │       │
   ▼       ▼       ▼       ▼       ▼       ▼       ▼       ▼
Aptitude   Performance   Compatibilité   Utilisabilité   Fiabilité   Sécurité   Maintenabilité   Portabilité
fonctionnelle  et efficacité                        

```

---  

## 3️⃣ Spécification détaillée par caractéristique  

> **Notation** : chaque sous‑caractéristique possède :  
> - **Métrique** (mesurable, outil)  
> - **Valeur cible** (objectif à atteindre)  
> - **Méthode de vérification** (comment la mesurer)  

### 3.1 Aptitude fonctionnelle (Functional Suitability)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Complétude fonctionnelle** | % d’exigences fonctionnelles couvertes (CCF) | **≥ 95 %** | Mapping CCF ↔ Composants (section 9) + revue fonctionnelle |
| **Exactitude fonctionnelle** | Taux d’erreurs de calcul/traitement (ex : nombre de réponses API erronées / total) | **≤ 0,5 %** | Tests unitaires + tests d’intégration (Jest, Cypress) |
| **Adéquation fonctionnelle** | Score d’évaluation utilisateur (échelle 1‑5) | **≥ 4,2 /5** | Enquête SUS + interview post‑déploiement |

### 3.2 Performance et efficacité (Performance Efficiency)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Comportement temporel** | Temps de réponse 95ᵉ percentile (page load, appel API) | **≤ 1 s** (SPA) | Lighthouse, k6, Chrome DevTools |
| **Utilisation des ressources** | CPU % / RAM % sous charge nominale (100 utilisateurs) | CPU ≤ 55 % ; RAM ≤ 70 % | Chrome DevTools, Grafana (Prometheus) |
| **Capacité** | Nombre d’utilisateurs simultanés supportés sans dégradation > 5 % | **≥ 200 utilisateurs** | Test de charge k6 (ramp‑up) |
| **Efficacité énergétique** *(optionnelle)* | Consommation moyenne du navigateur (W) | **≤ 5 W** (desktop) | Chrome Power API |

### 3.3 Compatibilité (Compatibility)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Cohérence** | Conformité aux standards W3C (HTML5, CSS3, ES6) | **100 %** | W3C validator, ESLint |
| **Interopérabilité** | Formats/interfaces supportés (ex : JSON, CSV, PDF) | **JSON + CSV** (export) | Tests d’API (Postman) + revue du code `ExportService.js` |

### 3.4 Utilisabilité (Usability)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Appréhensibilité** | Temps moyen de formation (débutant) | **≤ 2 h** | Sessions d’onboarding + questionnaire |
| **Apprenabilité** | % de tâches réussies sans formation (ex : login, recherche) | **≥ 90 %** | Tests utilisateurs (remote) |
| **Opérabilité** | Nombre moyen de clics pour tâche « Créer une étude » | **≤ 5 clics** | Analyse de parcours UI (Hotjar) |
| **Esthétique de l’interface** | Score SUS (System Usability Scale) | **≥ 68/100** | Enquête SUS |
| **Accessibilité** | Conformité WCAG 2.1 niveau AA | **Oui** | axe‑core, Lighthouse accessibility audit |

### 3.5 Fiabilité (Reliability)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Maturité** | Densité de défauts (défauts/KLOC) | **≤ 0,5 défauts/KLOC** | SonarQube, bug‑tracker |
| **Disponibilité** | % de temps opérationnel (SLA) | **≥ 99,5 %** | Monitoring (UptimeRobot, Grafana) |
| **Tolérance aux fautes** | Temps de récupération (RTO) après incident | **≤ 5 min** | Tests de résilience (Chaos Monkey) |
| **Récupérabilité** | Point de récupération (RPO) des données côté front (state) | **≤ 1 min** (re‑hydratation Vuex) | Tests de re‑connexion et de restauration d’état |

### 3.6 Sécurité (Security)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Confidentialité** | Score d’audit (OWASP ASVS Level 2) | **≥ 80 %** | Snyk, OWASP ZAP |
| **Intégrité** | Présence de contrôles d’intégrité (CSP, Subresource Integrity) | **Oui** | Analyse du CSP dans `index.html` |
| **Non‑répudiation** | Journalisation des actions sensibles (login, export) | **100 %** | Logique dans `SecurityService.js` + serveur backend |
| **Responsabilité (traceability)** | Couverture des logs (ex : API calls) | **≥ 95 %** | Centralisation via ELK |
| **Authenticité** | Méthodes d’authentification (session cookie, JWT) | **Oui** | `LegacyProxyService.js` + backend OIDC |

### 3.7 Maintenabilité (Maintainability)

| Sous‑caractéristique | Métrique | Valeur cible | Otool / Méthode |
|----------------------|----------|--------------|-----------------|
| **Modularité** | Couplage / Cohésion (SonarQube) – **Couplage ≤ 0,3**, **Cohésion ≥ 0,7** | SonarQube, `eslint-plugin-import` |
| **Réutilisabilité** | % de composants réutilisables (ex : `filterUtilMixin`) | **≥ 30 %** | Analyse de code |
| **Analysabilité** | Complexité cyclomatique moyenne | **≤ 10** | SonarQube |
| **Modifiabilité** | Temps moyen de modification (ticket) | **≤ 2 jours** | Historique JIRA |
| **Testabilité** | Couverture de tests unitaires + e2e | **≥ 80 %** | Jest, Cypress, Vue Test Utils |
| **Documentation** | % de fichiers avec JSDoc/Swagger commentés | **≥ 90 %** | ESLint `jsdoc` plugin |

### 3.8 Portabilité (Portability)

| Sous‑caractéristique | Métrique | Valeur cible | Outil / Méthode |
|----------------------|----------|--------------|-----------------|
| **Adaptabilité** | Nombre d’environnements supportés (OS + navigateurs) | **Windows + Linux + macOS** ; **Chrome ≥ 90**, **Firefox ≥ 88**, **Edge ≥ 90** | BrowserStack, Cypress |
| **Installabilité** | Temps d’installation (npm + yarn + build) | **≤ 5 min** | Script CI (`npm ci && yarn build`) |
| **Remplaçabilité** | Compatibilité avec formats standards (JSON, CSV) | **Oui** | Tests d’import/export |

---  

## 4️⃣ Architecture technique  

### 4.1 Diagramme de composants (UML)  

```
+--------------------+          +--------------------+
|  Vue (SPA) Front   | <--API--> |   Backend API      |
+--------------------+          +--------------------+
        |                                 |
        |  Vuex Store (state)             |
        |    +-------------------+          |
        +----| modules           |----------+
             |  - studies.js    |
             |  - security.js   |
             +-------------------+

Components (Vue)                     Services (axios wrappers)
+--------------------+               +---------------------------+
| App.vue            |               | LegacyProxyService.js     |
| Router.js          |               | SecurityService.js        |
| Views (Login,…)    |               | ExportService.js          |
| Components (… )    |               | StudiesService.js         |
+--------------------+               +---------------------------+

Plugins
+--------------------+
| vuetify.js (UI)    |
| filterUtilMixin.js |
+--------------------+
```

### 4.2 Justification des choix techniques  

| Qualité | Décision technique | Impact |
|--------|-------------------|--------|
| **Performance** | Vuetify (tree‑shaking) + lazy‑loading des routes (`router.js`) | Réduction du bundle initial, améliore le temps de réponse |
| **Sécurité** | `axios` avec `withCredentials:true`, en‑tête `Accept`/`Content-Type`, timeout 100 s | Limite les attaques CSRF, renforce la robustesse réseau |
| **Maintenabilité** | Vuex modules (`studies`, `security`) – séparation des domaines | Facilite la localisation des changements |
| **Portabilité** | Utilisation de standards ES6, Babel presets `@vue/app` | Compatibilité navigateurs modernes |
| **Utilisabilité** | Vuetify UI components (cards, forms) + `mdi` icons | Cohérence visuelle, accessibilité intégrée |
| **Fiabilité** | Gestion centralisée des erreurs via interceptors (à implémenter) | Centralise la tolérance aux fautes |

---  

## 5️⃣ Stack technologique qualifié  

| Couche | Technologie | Version | Licence | Raison qualité |
|--------|-------------|---------|---------|----------------|
| **Framework UI** | Vue 2.6.x | `^2.6.14` | MIT | Mature, large écosystème, support Vuex |
| **Component library** | Vuetify 2.5.x | `^2.5.10` | MIT | Thème personnalisable, bonnes pratiques d’accessibilité |
| **Bundler** | webpack (via Vue‑CLI) | `^4.44` | MIT | Configurable, plugins de performance |
| **Transpiler** | Babel | `^7.12` | MIT | ES6 → navigateur cible |
| **CSS** | PostCSS + autoprefixer | `^8.0` | MIT | Compatibilité navigateurs |
| **State mgmt** | Vuex | `^3.6` | MIT | Modulaire, traceabilité |
| **HTTP client** | axios | `^0.21` | MIT | Intercepteurs, timeout, gestion cookies |
| **Lint/format** | ESLint + Prettier | `^7.32 / ^2.5` | MIT | Qualité du code, règles `plugin:vue/essential` |
| **Tests** | Jest, Vue Test Utils, Cypress | `^26 / ^1.0` | MIT | Couverture, tests end‑to‑end |
| **CI/CD** | GitLab CI | – | – | Pipelines automatisés (lint, test, build) |
| **Monitoring** | Prometheus + Grafana | – | – | Métriques temps réel (CPU, RAM, latence) |
| **Sécurité** | Snyk, OWASP ZAP | – | – | Analyse des vulnérabilités des dépendances |

---  

## 6️⃣ Stratégie de test et validation  

| Niveau de test | Objectif | Outils | Couverture / Critères d’acceptation |
|----------------|----------|--------|-------------------------------------|
| **Unitaires** | Vérifier chaque fonction/service | Jest + Vue Test Utils | ≥ 80 % de lignes, 0 % de tests échoués |
| **Intégration** | Interaction Vuex ↔ services, routing | Jest + mock Axios | Tous les flux API (login, CRUD) testés |
| **End‑to‑End** | Parcours utilisateur complet (login → export) | Cypress (headless) | Temps de réponse ≤ 2 s, aucune régression UI |
| **Performance** | Temps de chargement, utilisation ressources | Lighthouse CI, k6 | 95ᵉ percentile ≤ 1 s, CPU ≤ 55 % sous 200 U |
| **Sécurité** | Détection vulnérabilités, conformité OWASP | Snyk (deps), ZAP (runtime) | Score OWASP ≥ 80 % |
| **Accessibilité** | Conformité WCAG AA | axe‑core, Lighthouse | Aucun critère d’erreur « critical » |
| **Qualité du code** | Densité de défauts, complexité | SonarQube, ESLint | Complexité cyclomatique ≤ 10, défauts/KLOC ≤ 0,5 |

---  

## 7️⃣ Supervision et métriques en production  

| KPI | Seuil d’alerte | Source de donnée | Fréquence |
|-----|----------------|------------------|-----------|
| **Disponibilité** | < 99,5 % (alert) | Grafana (Uptime) | 5 min |
| **Temps de réponse (API)** | > 1 s (alert) | Prometheus `http_request_duration_seconds` | 1 min |
| **Utilisation CPU** | > 70 % (alert) | Node exporter | 1 min |
| **Erreur front (JS)** | > 5 % des sessions (alert) | Sentry (error rate) | 5 min |
| **Couverture de tests** | < 80 % (dégradé) | SonarQube | chaque pipeline |
| **Score de sécurité** | OWASP < 80 % (alert) | Snyk/ZAP | chaque pipeline |
| **Score d’accessibilité** | < 85 % (alert) | Lighthouse CI | chaque build |

**Tableaux de bord** : Grafana dashboards regroupant les métriques ci‑dessus, alertes via Slack/Email.

---  

## 8️⃣ Documentation technique  

| Type | Format | Outils |
|------|--------|--------|
| **Code** | JSDoc (functions), Vue component docs (`/** */`) | eslint‑plugin‑jsdoc |
| **API** | OpenAPI 3 (JSON) – généré côté backend, référencé dans README | Swagger UI |
| **Architecture** | Diagrammes UML (draw.io) | Markdown + images |
| **Guide d’installation** | README.md (sections *Installation*, *Configuration*) | Markdown |
| **Guide d’utilisation** | Wiki GitLab – tutoriels, captures d’écran | Markdown |
| **Exploitation** | SOP (Standard Operating Procedures) – monitoring, rollback | Confluence |

---  

## 9️⃣ Matrice de traçabilité CCF ↔ CST  

> **CCF** = Exigences fonctionnelles (extraits du code).  
> La colonne **CST** indique la caractéristique ISO 25010 et la métrique associée.

| CCF (exemple) | Description | Caract. ISO 25010 | Sous‑caract. | Métrique / Objectif CST |
|---------------|-------------|-------------------|--------------|------------------------|
| **CCF‑001** | Authentifier l’utilisateur (login) | Sécurité | Confidentialité, Authenticité | Score OWASP ≥ 80 % ; Auth via cookie/session |
| **CCF‑002** | Lister les études (EtudesList.vue) | Fonctionnalité | Complétude, Exactitude | ≥ 95 % des études affichées, erreur < 0,5 % |
| **CCF‑003** | Créer/éditer une étude (EtudeEdit.vue) | Maintenabilité | Modifiabilité, Testabilité | Temps de modification ≤ 2 j, couverture tests ≥ 80 % |
| **CCF‑004** | Exporter les études en CSV (ExportService.js) | Compatibilité | Interopérabilité | Export CSV conforme RFC 4180, testé sur Chrome/Firefox |
| **CCF‑005** | Afficher les tutoriels vidéo (Tutoriels.vue) | Utilisabilité | Opérabilité, Esthétique | ≤ 3 clics pour lancer vidéo, SUS ≥ 68 |
| **CCF‑006** | Filtrer les listes par année (filterUtilMixin.js) | Performance | Utilisation des ressources | CPU ≤ 55 % lors du filtrage de 10 000 lignes |
| **CCF‑007** | Gestion des erreurs API (interceptor à implémenter) | Fiabilité | Tolérance aux fautes | RTO ≤ 5 min, logs 100 % |
| **CCF‑008** | Support multi‑navigateurs | Portabilité | Adaptabilité | Tests BrowserStack sur Chrome/Firefox/Edge |
| **CCF‑009** | Thème personnalisable via Vuetify | Compatibilité | Cohérence | Conformité aux guidelines UI du ministère |
| **CCF‑010** | Gestion du state global (Vuex) | Maintenabilité | Modularité, Analysabilité | Couplage ≤ 0,3, Cohésion ≥ 0,7 (SonarQube) |

*(La matrice complète inclura les 30 + exigences fonctionnelles du projet – à enrichir par le PO.)*

---  

## 10️⃣ Gestion des dettes techniques  

| Risque / dette | Impact | Priorité | Plan de remboursement |
|----------------|--------|----------|-----------------------|
| **Absence d’intercepteur global Axios** | Faible tolérance aux erreurs, logs incomplets | Haute | Implémenter `src/services/httpInterceptor.js` (Sprint 2) |
| **Couverture de tests < 80 % sur les composants UI** | Régression UI possible | Moyenne | Augmenter les tests Cypress (Sprint 3) |
| **Documentation JSDoc manquante sur `ExportService.js`** | Difficile de réutiliser le service | Basse | Ajouter JSDoc (Sprint 4) |
| **Déploiement sans HTTPS en dev** | Risque de fuite de cookies | Haute | Configurer NGINX TLS (CI pipeline) |
| **Complexité cyclomatique de `filterUtilMixin.js` > 10** | Maintenance difficile | Moyenne | Refactoriser en fonctions pures (Sprint 5) |

---  

## 11️⃣ Annexes  

* **Annexe A** – Diagrammes UML (composants, séquence login, export).  
* **Annexe B** – Scripts CI/CD (`.gitlab-ci.yml`).  
* **Annexe C** – Exemple de fichier de configuration Prometheus (`node_exporter`).  
* **Annexe D** – Modèle de rapport d’audit de sécurité (OWASP).  

---  

*Ce CST a été rédigé le **27 avril 2026** conformément à la norme ISO/IEC 25010 2023. Il constitue la base contractuelle entre les équipes produit, développement et assurance qualité pour le projet **agile‑front**.*