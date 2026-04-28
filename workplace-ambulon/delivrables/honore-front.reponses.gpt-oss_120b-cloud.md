# Documentation Technique du Projet honore‑front  

[TOC]

---  

## 📖 1️⃣ Vue d’ensemble du projet  
Le projet **honore‑front** est une application **Single‑Page Application (SPA)** développée avec **Vue 2** (class‑component) et **TypeScript**. Le code source est organisé en modules fonctionnels (`home`, `folders`, `onBoarding`, …) chacun contenant :

* `layout/` : wrappers de mise en page qui ne font que `<router‑view/>`.  
* `screens/` : pages affichées par le routeur.  
* `components/` : UI réutilisables (ex. `DateBox.vue`, `Alert.vue`).  

Le build est réalisé avec **Vue‑CLI** qui produit un répertoire `dist/` contenant les assets statiques. Ce répertoire est ensuite empaqueté dans une image Docker basée sur **nginx:latest** et déployé via le pipeline **GitLab CI/CD**.

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## 🏗️ 2️⃣ Architecture technique  

```mermaid
graph TD
    %% CI/CD pipeline;
    subgraph CI;
    A[GitLab CI] --> B[Install dependencies]
    B --> C[Run lint & tests]
    C --> D[Build (Vue‑CLI) → dist/]
    D --> E[Docker build (nginx + dist/)]
    E --> F[Push image to registry]
    end
    %% Runtime;
    subgraph Runtime;
    G[Docker container (nginx)] --> H[nginx.conf]
    H --> I[Serve static files from /app]
    I --> J[SPA fallback: /index.html]
    J --> K[Vue router → <router‑view/>]
    K --> L[Modules (home, folders, onBoarding …)]
    end
    %% Artefacts;
    style CI fill:#f9f9f9,stroke:#333,stroke-width_1px;
    style Runtime fill:#e8f5e9,stroke:#333,stroke-width_1px
```

**Description**  

| Élément | Rôle | Technologie |
|---|---|---|
| **GitLab CI** | Orchestration du build, test, packaging | `.gitlab-ci.yml` |
| **Vue‑CLI** | Transpilation TypeScript, bundling, minification | `npm run build` |
| **Docker** | Isolation et déploiement | `Dockerfile` |
| **nginx** | Serveur HTTP statique, fallback SPA | `docker/nginx.conf` |
| **Vue router** | Navigation client‑side | `<router‑view/>` dans les layouts |
| **Modules** | Séparation fonctionnelle du code | `src/modules/*` |

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## 🛠️ 3️⃣ Stack technologique  

| Catégorie | Technologie | Version (si connue) | Usage |
|---|---|---|---|
| **Framework UI** | Vue 2 (class‑component) | – | Rendering, réactivité, routing |
| **Langage** | TypeScript | – | Typage statique des *.vue* et *.ts* |
| **Bundler / CLI** | Vue‑CLI | – | Build du SPA (`dist/`) |
| **Styling** | SCSS + fonctions utilitaires (`to‑rem`) | – | Design system, responsive units |
| **Web server** | NGINX (image `nginx:latest`) | – | Servir les assets, fallback SPA |
| **Containerisation** | Docker | – | Construction de l’image de production |
| **CI/CD** | GitLab CI | – | Pipeline de build, test, déploiement |
| **Package registry** | Google Artifact Registry (npm) | – | Dépendances privées (`@pnm3`, `@pasta`) |
| **Qualité du code** | ESLint, EditorConfig, Browserslist | – | Linting, formatage, cibles navigateurs |
| **Tests** | JUnit (rapport XML) | – | Intégration avec GitLab Test‑Report |
| **Gestion des secrets** | .gitignore (exclusion `.env*`) | – | Protection des variables d’environnement |

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## 📦 4️⃣ Build, Docker & Déploiement  

### 4.1 Processus de build  

1. `npm ci` – installation des dépendances (registries privés).  
2. `npm run lint` – linting via ESLint.  
3. `npm run test` – exécution du test JUnit (dummy).  
4. `npm run build` – génération du répertoire `dist/` (Vue‑CLI).  

### 4.2 Dockerfile  

```dockerfile
FROM nginx:latest

RUN mkdir /app
COPY dist /app
COPY docker/nginx.conf /etc/nginx/nginx.conf
```

*Le Dockerfile copie uniquement le répertoire `dist/` et le fichier de configuration NGINX.*  

### 4.3 nginx.conf  

```conf
user  nginx;
worker_processes  1;
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
  worker_connections  1024;
}

http {
  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;

  log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
  access_log  /var/log/nginx/access.log  main;

  sendfile        on;
  keepalive_timeout  65;

  server {
    listen       80;
    server_name  localhost;

    location / {
      root   /app;
      index  index.html;
      try_files $uri $uri/ /index.html;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
      root   /usr/share/nginx/html;
    }
  }
}
```

*Le `try_files` assure le fallback vers `index.html` pour toutes les routes SPA.*  

### 4.4 CI/CD (`.gitlab-ci.yml`)  

```yaml
include:
  - project: "snum/pnm3/public/pasta/pasta-ci"
    file: "applications/front.yml"
variables:
  USE_NEW_REGISTRY: "true"
```

Le pipeline inclut un fichier partagé `applications/front.yml` qui réalise : install, lint, test, build, Docker image build & push.  

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## 📂 5️⃣ Principaux fichiers de configuration  

| Fichier | Type | Rôle | Points clés |
|---|---|---|---|
| `.browserslistrc` | Browserslist | Cibles navigateurs → `> 1%` + `last 2 versions`. |
| `.dockerignore` | Docker | Exclut `node_modules` (et potentiellement d’autres dossiers temporaires). |
| `.editorconfig` | Editeur | Indentation 2 espaces, LF, UTF‑8, trim‑trailing‑whitespace. |
| `.eslintignore` | ESLint | Ignorer `**/*.d.ts`, `.eslintrc.js`, `dist`, `migrations`. |
| `.gitignore` | Git | Exclut `node_modules`, `dist`, fichiers `.env*`, logs, IDE. |
| `.gitlab-ci.yml` | CI/CD | Déclenche le pipeline partagé, variable `USE_NEW_REGISTRY`. |
| `.npmrc` | npm | Registre privé Google Artifact (`@pnm3`, `@pasta`). |
| `docker/nginx.conf` | NGINX | Configuration serveur statique + SPA fallback. |
| `Dockerfile` | Docker | Construction de l’image production (nginx + `dist`). |
| `junit.xml` | Tests | Rapport JUnit (dummy) pour GitLab. |
| `public/index.html` | HTML | Point d’entrée du SPA, injecté par Vue‑CLI. |
| `src/styles/functions.scss` | SCSS | Fonction utilitaire `torem($size)` → px → rem. |
| `src/modules/**/layout/*.vue` | Vue | Layouts contenant uniquement `<router-view/>`. |
| `src/modules/**/components/*.vue` | Vue | Composants UI réutilisables (ex. `DateBox.vue`). |
| `src/modules/**/screens/*.vue` | Vue | Pages affichées par le routeur. |

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## 🧩 6️⃣ Composants clés et UI  

| Composant | Emplacement | Fonction | Props / API |
|---|---|---|---|
| `DateBox.vue` | `src/modules/onBoarding/components/DateBox.vue` | Affiche une donnée chiffrée avec un titre (ex. « Jours restants »). | `title: string` (required), `count: string` (required). |
| `FilesFollowUpLayout.vue` | `src/modules/folders/layout/FilesFollowUpLayout.vue` | Wrapper de layout pour le module `folders`. | Aucun – ne fait que `<router-view/>`. |
| `Cookies.vue` | `src/modules/home/screens/Cookies.vue` | Page d’information sur la gestion des cookies. | Aucun – iframe vers le service public. |
| `LegalMentions.vue` | `src/modules/home/screens/LegalMentions.vue` | Page des mentions légales (texte statique). | Aucun. |
| `Alert.vue`, `Footer.vue`, `Header.vue` | `src/components/` | UI réutilisable (alertes, pied de page, en‑tête). | Props spécifiques selon le composant (non détaillés ici). |

Tous les composants utilisent `<style lang="scss">` avec **scoped** afin d’éviter les fuites de styles.  

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## ⚠️ 7️⃣ Points d’attention et recommandations  

| Domaine | Risque / Observation | Recommandation |
|---|---|---|
| **Taille de l’image Docker** | `nginx:latest` + `dist/` peut contenir des source‑maps non nécessaires. | Désactiver les source‑maps (`productionSourceMap: false` dans `vue.config.js`) ou les nettoyer avant le `COPY`. |
| **.dockerignore** | Seul `node_modules` est ignoré. D’autres dossiers (`.cache`, `coverage`) pourraient être ajoutés. | Enrichir le fichier pour exclure tout artefact de build inutile. |
| **Registre npm privé** | Le token d’accès peut expirer, entraînant des échecs de CI. | Utiliser les variables CI (`CI_JOB_TOKEN`) et automatiser le renouvellement. |
| **Pipeline de tests** | Le `junit.xml` ne contient qu’un test dummy. | Ajouter des suites de tests réelles (Jest, Cypress) et publier leurs rapports. |
| **Cibles browserslist** | `> 1%` + `last 2 versions` inclut des navigateurs legacy, augmentant le bundle. | Ajuster la cible selon le public réel (ex. `defaults` ou `>= 0.5%`). |
| **ESLint ignore** | Certains dossiers (`dist`, `migrations`) sont ignorés ; assurez‑vous que tout le code source est linté. | Vérifier les patterns d’ignore pour ne pas masquer des erreurs. |
| **Variables d’environnement** | `.env*` sont ignorés, mais NGINX ne lit pas ces fichiers. | Injecter les variables via un script d’entrée (`envsubst`) ou via le serveur d’application qui génère le `index.html`. |
| **Fonction SCSS `torem`** | Base fixe à `16px`. Si la taille de base change, il faut mettre à jour manuellement. | Centraliser la base dans une variable `$base-font: 16px` et référencer la fonction. |
| **Fallback SPA** | `try_files $uri $uri/ /index.html` fonctionne tant que le serveur ne gère pas d’API côté back‑end. | Documenter ce besoin et tester les routes profondes avec `curl`. |

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

## 📚 8️⃣ Glossaire  

| Terme | Définition |
|---|---|
| **SPA** | Single‑Page Application ; l’ensemble de l’interface est chargé une seule fois puis géré côté client. |
| **Vue‑CLI** | Outil de scaffolding et de build pour les projets Vue.js. |
| **SCSS** | Syntactically Awesome Style Sheets, pré‑processeur CSS. |
| **Browserslist** | Liste de navigateurs cibles utilisée par Babel, Autoprefixer, etc. |
| **CI/CD** | Intégration continue / Déploiement continu. |
| **Artifact Registry** | Service Google Cloud pour héberger des paquets npm privés. |
| **Fallback** | Redirection de toutes les requêtes non trouvées vers `index.html` afin que le routeur client prenne le relais. |

↩ [Retour au sommaire](#documentation-technique-du-projet-honore-front)  

---  

*Ce document a été généré de façon autonome à partir du code source du projet honore‑front. Toutes les informations présentées sont tirées des fichiers analysés et sont destinées à être exploitées directement dans un environnement de documentation compatible Obsidian ou VS Code.*  