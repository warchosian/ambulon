# Honore Front – Documentation Technique  

[TOC]

---

## 1. Présentation générale  

Le projet **honore‑front** est une application **SPA** développée avec **Vue 2** (class‑component + TypeScript) et empaquetée via **Vue‑CLI**.  
Le bundle produit (`dist/`) est servi par un conteneur **Docker** basé sur **nginx:latest**.  
Le tout est orchestré par un pipeline **GitLab CI/CD** qui compile le code, exécute les tests JUnit (actuellement un test dummy) et publie l’image Docker.

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 2. Structure du dépôt  

```text
honore-front/
├─ .browserslistrc
├─ .dockerignore
├─ .editorconfig
├─ .eslintignore
├─ .gitignore
├─ .gitlab-ci.yml
├─ .npmrc
├─ Dockerfile
├─ docker/
│   └─ nginx.conf
├─ public/
│   └─ index.html
├─ src/
│   ├─ assets/
│   │   └─ .gitkeep
│   ├─ components/
│   │   ├─ .gitkeep
│   │   ├─ Alert.vue
│   │   ├─ Draft.vue
│   │   ├─ Footer.vue
│   │   ├─ Header.vue
│   │   ├─ SearchApplicantDialog.vue
│   │   ├─ Selector.vue
│   │   └─ TextField.vue
│   ├─ modules/
│   │   ├─ archives/
│   │   │   └─ screens/ArchiveScreen.vue
│   │   ├─ folders/
│   │   │   ├─ components/… (AddTags.vue, …)
│   │   │   ├─ layout/FilesFollowUpLayout.vue
│   │   │   └─ screens/ApplicantsList.vue, FolderDetail.vue
│   │   ├─ home/
│   │   │   └─ screens/{Accessibility, Cookies, DraftList, Home, LegalMentions, Privacy}.vue
│   │   ├─ onBoarding/
│   │   │   ├─ components/… (DateBox.vue, Stepper.vue, …)
│   │   │   ├─ layout/OnBoardingLayout.vue
│   │   │   └─ screens/… (ActivityScreen.vue, Annuity.vue, …)
│   │   ├─ recommandants/
│   │   │   ├─ components/… (RecommandantForm.vue, …)
│   │   │   └─ screens/RecommandantDetail.vue, RecommandantsListScreen.vue
│   │   ├─ sessions/
│   │   │   ├─ components/… (LHONMPromotion.vue, MMPromotion.vue, …)
│   │   │   └─ screens/SessionList.vue, SessionScreen.vue
│   │   └─ .gitkeep
│   └─ styles/
│       ├─ base.scss
│       ├─ functions.scss
│       ├─ variables.module.scss
│       └─ variables.scss
├─ junit.xml
└─ README.md
```

*Les dossiers `components`, `screens` et `layout` sont organisés par domaine fonctionnel (`home`, `folders`, `onBoarding`, …).  
Les fichiers `.gitkeep` permettent de garder les répertoires vides dans le VCS.*

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 3. Architecture technique  

```mermaid
graph TD
    A[Développeur] -->|npm run build| B[Vue‑CLI]
    B --> C[dist/ (bundle static)]
    C --> D[Docker build]
    D --> E[nginx_latest]
    E --> F[Conteneur Docker (production)]
    F --> G[Clients (navigateurs)]
    subgraph CI/CD;
    CI[GitLab CI] -->|build| D;
    CI -->|tests| T[JUnit (dummy)]
    CI -->|push| R[Registry Docker]
    end
```

*Le pipeline CI compile le code, génère le bundle, exécute les tests JUnit, crée l’image Docker et la pousse vers le registre.*  

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 4. Build & Déploiement  

| Élément | Description | Points clés |
|---------|-------------|-------------|
| **Vue‑CLI** | Transpile TypeScript, SCSS et génère le répertoire `dist/`. | `productionSourceMap` doit être désactivé pour réduire la taille. |
| **Dockerfile** | <pre>FROM nginx:latest<br/>RUN mkdir /app<br/>COPY dist /app<br/>COPY docker/nginx.conf /etc/nginx/nginx.conf</pre> | Copie uniquement le bundle, le serveur Nginx sert les fichiers statiques. |
| **nginx.conf** | Fichier de configuration Nginx. <br>`try_files $uri $uri/ /index.html;` assure le fallback SPA. | Log format personnalisé, worker = 1, `root /app`. |
| **.dockerignore** | Empêche l’inclusion de `node_modules` et autres artefacts inutiles. | Ajouter `coverage`, `.cache`, `*.map` si besoin. |
| **CI (`.gitlab-ci.yml`)** | Inclut le job `front.yml` du projet partagé. Variable `USE_NEW_REGISTRY: "true"` active le registre privé. | Aucun job de tests unitaires réel (seul dummy). |

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 5. Gestion des dépendances  

| Fichier | Rôle | Détails |
|--------|------|---------|
| **.npmrc** | Redirige les scopes `@pnm3` et `@pasta` vers le **Google Artifact Registry**. | `@pnm3:registry=https://europe-west9-npm.pkg.dev/...` |
| **package.json** *(non affiché)* | Liste les dépendances publiques et privées. | Les paquets privés sont résolus via les scopes ci‑dessus. |
| **.gitignore** | Exclut les fichiers `.env*` contenant les secrets. | Garantit que les credentials ne sont jamais versionnés. |

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 6. Styling & SCSS  

| Fichier | Fonction |
|---------|----------|
| `src/styles/functions.scss` | Fonction utilitaire `torem($size)` → conversion px → rem. |
| `src/styles/variables.scss` & `variables.module.scss` | Variables globales (couleurs, espacements, typographie). |
| `*.vue` | Chaque composant possède un bloc `<style scoped lang="scss">` pour éviter les fuites de styles. |
| `src/modules/folders/layout/FilesFollowUpLayout.vue` | Exemple d’import SCSS global : `@import "../../../styles/variables";` |

> **Recommandation** : centraliser la taille de base (`$base-font: 16px`) et faire référencer `torem()` pour éviter les divergences si la base change.

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 7. Qualité du code  

| Outil | Configuration | Objectif |
|-------|----------------|----------|
| **ESLint** | `.eslintignore` exclut `**/*.d.ts`, `.eslintrc.js`, `dist`, `migrations`. | Linting du code source TypeScript/Vue. |
| **EditorConfig** | Indentation 2 espaces, LF, UTF‑8, suppression des espaces en fin de ligne. | Uniformité entre éditeurs. |
| **browserslist** | `> 1%` + `last 2 versions`. | Cible large de navigateurs, mais peut alourdir le bundle. |
| **JUnit** | `junit.xml` (dummy test). | Intégré à GitLab pour le reporting, mais aucune couverture réelle. |

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 8. Points d’attention & Recommandations  

| Domaine | Risque / Observation | Action recommandée |
|---------|----------------------|-------------------|
| **Taille de l’image** | `nginx:latest` + `dist` contenant potentiellement des source‑maps. | Désactiver `productionSourceMap` dans `vue.config.js` ou nettoyer le dossier avant le `COPY`. |
| **.dockerignore** | Ne couvre que `node_modules`. | Ajouter `coverage`, `.cache`, `*.map`, `Dockerfile.dev` si présent. |
| **Registre npm privé** | Expiration des credentials → build échoue. | Utiliser le token CI (`CI_JOB_TOKEN`) et renouveler les accès via les variables GitLab. |
| **Pipeline CI** | Un seul test dummy ; aucune suite unitaires/e2e réelle. | Implémenter des tests Jest (unit) et Cypress (e2e) et les publier dans le pipeline. |
| **Browserslist** | Cible large → bundle plus volumineux. | Réévaluer la cible (ex. `defaults` ou `> 0.5%`) en fonction du public réel. |
| **ESLint ignore** | Risque de masquer des erreurs dans des dossiers non listés. | Vérifier les patterns d’exclusion et s’assurer que tout le code source est linté. |
| **Variables d’environnement** | `.env*` ignorés, mais Nginx ne lit pas ces fichiers. | Injecter les variables via un script d’entrée (`envsubst`) ou générer `index.html` dynamiquement. |
| **SCSS fonction `torem`** | Base fixe à 16 px ; changement de base nécessiterait une mise à jour globale. | Centraliser la base dans une variable SCSS (`$base-font: 16px`) et référencer la fonction. |
| **Routing SPA** | `try_files … /index.html` assure le fallback, mais les URLs profondes doivent être testées. | Vérifier les routes via `curl` en production et documenter le besoin de ce fallback. |

↩ [Retour au sommaire](#honore-front-documentation-technique)

---

## 9. Synthèse  

- **Stack** : Vue 2 + TypeScript, SCSS, Vue‑CLI, Docker + Nginx, GitLab CI, registre npm privé (Google Artifact Registry).  
- **Architecture** : Application modulaire (modules / screens / components), build statique, conteneur Nginx ultra‑léger.  
- **Bonnes pratiques** : Linting, editorconfig, browserslist, CI, gestion des secrets.  
- **Axes d’amélioration** : Tests automatisés réels, optimisation de la taille d’image, gestion plus fine des dépendances et des variables d’environnement.

↩ [Retour au sommaire](#honore-front-documentation-technique)