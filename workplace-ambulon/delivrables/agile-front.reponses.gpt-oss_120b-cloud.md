# Projet : agile‑front

[TOC]

↩ [Retour au sommaire](#projet-agile-front)

---  

## 📖 Vue d’ensemble  

Le projet **agile‑front** est une application web Vue 2 + Vuetify qui sert d’interface utilisateur pour la plateforme *Agile* (gestion d’études, financements, statistiques, etc.).  
Elle consomme une API REST définie via les variables d’environnement `VUE_APP_API_BASE_URL`.  

Principaux objectifs :  

| Objectif | Description |
|----------|-------------|
| **Interface riche** | Utilise Vuetify (Material Design) et des composants Vue personnalisés. |
| **Modularité** | Séparation claire entre *components*, *views*, *services* et *store* (Vuex). |
| **Extensibilité** | Mixins et services facilitent l’ajout de nouvelles fonctionnalités. |
| **Déploiement simple** | Configuration via `vue.config.js` et scripts npm/yarn. |

↩ [Retour au sommaire](#projet-agile-front)

---  

## 📂 Arborescence du dépôt  

```text
agile-front/
├─ .browserslistrc
├─ .env.sample
├─ .eslintrc.js
├─ .gitignore
├─ README.md
├─ babel.config.js
├─ postcss.config.js
├─ vue.config.js
├─ public/
│   └─ index.html
└─ src/
    ├─ App.vue
    ├─ main.js
    ├─ router.js
    ├─ components/
    │   ├─ ConfirmationDialog.vue
    │   ├─ EtudesExportPanel.vue
    │   ├─ EtudesList.vue
    │   └─ FinancementsList.vue
    ├─ mixins/
    │   └─ filterUtilMixin.js
    ├─ plugins/
    │   └─ vuetify.js
    ├─ services/
    │   ├─ ExportService.js
    │   ├─ LegacyProxyService.js
    │   ├─ SecurityService.js
    │   └─ StudiesService.js
    ├─ store/
    │   ├─ store.js
    │   └─ modules/
    │       ├─ security.js
    │       └─ studies.js
    └─ views/
        ├─ Assistance.vue
        ├─ Etude.vue
        ├─ EtudeEdit.vue
        ├─ EtudeNew.vue
        ├─ Home.vue
        ├─ Liens.vue
        ├─ Login.vue
        ├─ Statistiques.vue
        ├─ Tutoriels.vue
        └─ Videos.vue
```

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🛠️ Build & exécution  

| Action | Commande | Description |
|--------|----------|-------------|
| **Installation des dépendances** | `yarn install` | Installe les paquets définis dans `package.json`. |
| **Démarrage en mode dev** | `yarn serve` | Lance le serveur de développement (Hot‑Reload). |
| **Compilation pour production** | `yarn build` | Produit les assets optimisés dans `dist/`. |
| **Lancement du serveur de prod** | `serve -s dist` *(ou équivalent)* | Sert les fichiers statiques construits. |

Le serveur de développement écoute sur `0.0.0.0` (configurable dans `vue.config.js`).  

↩ [Retour au sommaire](#projet-agile-front)

---  

## ⚙️ Fichiers de configuration  

| Fichier | Rôle | Extrait clé |
|--------|------|-------------|
| **`.browserslistrc`** | Déclaration des navigateurs cibles. | `> 1%`<br>`last 2 versions` |
| **`.env.sample`** | Modèle de variables d’environnement. | `VUE_APP_API_BASE_URL=` |
| **`.eslintrc.js`** | Règles ESLint (Vue Essentiel + Prettier). | `no-console`/`no-debugger` désactivés en dev. |
| **`babel.config.js`** | Preset Babel pour Vue. | `["@vue/app"]` |
| **`postcss.config.js`** | Plugins PostCSS (autoprefixer). | `autoprefixer: {}` |
| **`vue.config.js`** | Configuration Vue‑CLI (publicPath, devServer). | `publicPath: "/"`<br>`host: "0.0.0.0"` |
| **`public/index.html`** | Point d’entrée HTML. | `<div id="app"></div>` |

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🚀 Point d’entrée de l’application  

### `src/main.js`

```javascript
import Vue from "vue";
import "./plugins/vuetify";
import App from "./App.vue";
import store from "./store/store";
import vuetify from "./plugins/vuetify";
import router from "./router";

Vue.config.productionTip = false;

new Vue({
  vuetify,
  router,
  store,
  render: h => h(App)
}).$mount("#app");
```

### `src/App.vue` (simplifié)

```html
<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script>
export default {
  name: "App"
};
</script>
```

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🧩 Composants UI majeurs  

| Composant | Fonction | Emplacement |
|-----------|----------|--------------|
| **ConfirmationDialog.vue** | Boîte de dialogue générique de confirmation. | `src/components/` |
| **EtudesExportPanel.vue** | Interface d’export des études (CSV, PDF). | `src/components/` |
| **EtudesList.vue** | Liste paginée des études. | `src/components/` |
| **FinancementsList.vue** | Affichage des financements associés. | `src/components/` |

Ces composants sont réutilisés dans les *views* `Etude.vue`, `EtudeEdit.vue`, etc.  

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🔧 Mixins  

### `src/mixins/filterUtilMixin.js`

Fournit des filtres de date et un compteur de filtres actifs :

```javascript
export const filterUtilMixin = {
  data() {
    return {
      annees: [{ label: "Toutes", key: "" }, ...this.getDateRange()],
      filtres: { annee: new Date().getUTCFullYear() }
    };
  },
  methods: {
    getDateRange() {
      const dateRange = [];
      const year = new Date().getUTCFullYear();
      for (let i = 2011; i < year + 8; i++) {
        dateRange.push({ label: i, key: i });
      }
      return dateRange;
    }
  },
  computed: {
    nombreFiltres() {
      let count = 0;
      for (const [key, value] of Object.entries({
        ...this.globalFilters,
        ...this.filtres
      })) {
        if (value && value.length) count++;
      }
      return count;
    }
  }
};
```

Utilisé par plusieurs vues pour uniformiser la logique de filtrage.  

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🎨 Plugin Vuetify  

**`src/plugins/vuetify.js`** initialise Vuetify 2 avec un thème personnalisé :

```javascript
import "@mdi/font/css/materialdesignicons.css";
import Vue from "vue";
import Vuetify from "vuetify/lib";

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: "#202328",
        secondary: "#4874b8",
        accent: "#7fc6a4"
      }
    }
  },
  icons: { iconfont: "mdi" }
});
```

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🗂️ Services (accès API)  

| Service | Endpoint(s) | Usage principal |
|---------|-------------|-----------------|
| **LegacyProxyService** | `/etudes/*`, `/etudes/new`, `/etudes/:id/edit` | Récupération/modification d’études (ancienne API). |
| **SecurityService** | `/security/subject` | Récupération du sujet de sécurité (infos utilisateur). |
| **ExportService** *(non affiché mais présent)* | … | Gestion des exportations (CSV, PDF). |
| **StudiesService** *(non affiché mais présent)* | … | Opérations CRUD spécifiques aux études. |

Tous les services utilisent un client Axios configuré :

```javascript
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL,
  withCredentials: true,
  headers: { Accept: "application/json", "Content-Type": "application/json" },
  timeout: 100000
});
```

### Diagramme de séquence – Authentification & Chargement d’une étude  

```mermaid
sequencediagram;
    participant UI as Vue Component;
    participant Store as Vuex Store;
    participant SecSvc as SecurityService;
    participant Proxy as LegacyProxyService;
    UI->>Store: dispatch('security/fetchSubject')
    Store->>SecSvc: GET /security/subject;
    SecSvc-->>Store: subject data;
    Store-->>UI: isConnected / isAdmin flags;
    UI->>Store: dispatch('studies/fetchStudy', id)
    Store->>Proxy: GET /etudes/{id}
    Proxy-->>Store: étude payload;
    Store-->>UI: étude data
```

↩ [Retour au sommaire](#projet-agile-front)

---  

## 📦 Store Vuex  

### `src/store/store.js`

```javascript
import Vue from "vue";
import Vuex from "vuex";
import * as studies from "@/store/modules/studies.js";
import * as security from "@/store/modules/security.js";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: { studies, security },
  financements: ["z"],
  state: {
    categories: [
      "sustainability","nature","animal welfare","housing",
      "education","food","community"
    ]
  }
});
```

### Module `security.js`

| Élément | Description |
|--------|-------------|
| **state.subject** | Tableau contenant les informations du sujet (email, rôles). |
| **mutation SET_SUBJECT** | Met à jour `state.subject`. |
| **action fetchSubject** | Appelle `SecurityService.getSubject()` puis commit. |
| **getters** | `isConnected` → présence d’`email`<br>`isAdmin` → présence d’`admin`. |

### Module `studies.js` *(non détaillé dans l’extrait mais présent)*  

Gère la liste des études, les filtres, la pagination, etc.  

↩ [Retour au sommaire](#projet-agile-front)

---  

## 📺 Vues principales  

| Vue | Rôle | Points clés |
|-----|------|--------------|
| **Login.vue** | Page d’authentification (formulaire). | Utilise `v-text-field`, toggle du mot de passe. |
| **Tutoriels.vue** | Liste de liens vidéo tutoriaux. | `v-list-item` avec icône `mdi-filmstrip`. |
| **Home.vue** | Accueil du tableau de bord. | (contenu non fourni, mais importé). |
| **Etude.vue / EtudeEdit.vue / EtudeNew.vue** | CRUD complet d’une étude. | S’appuient sur les services et le store. |
| **Statistiques.vue** | Visualisation de métriques. | (non détaillé). |
| **Liens.vue** | Catalogue de liens externes. | (non détaillé). |
| **Videos.vue** | Lecteur vidéo intégré. | (non détaillé). |

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🏗️ Diagramme d’architecture frontale  

```mermaid
graph TD
    subgraph UI;
        A[Vue Components] --> B[Views (router-view)]
        B --> C[App.vue]
    end
    subgraph State;
        D[Vuex Store] --> E[Modules: security, studies]
    end
    subgraph Services;
        F[LegacyProxyService] 
        G[SecurityService] 
        H[ExportService] 
        I[StudiesService]
    end
    subgraph Config;
        J[vuetify.js] 
        K[router.js] 
        L[env variables]
    end
    C --> D;
    C --> F;
    C --> G;
    C --> H;
    C --> I;
    D --> F;
    D --> G;
    D --> H;
    D --> I;
    J --> A;
    K --> B;
    L --> F;
    L --> G;
    L --> H;
    L --> I
```

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🔐 Considérations de sécurité  

1. **Cookies & CORS** – `withCredentials: true` indique que l’API utilise des cookies d’authentification ; le serveur doit autoriser le domaine via CORS.  
2. **Environnement** – `VUE_APP_API_BASE_URL` doit être défini en production (ex. `https://api.example.com`).  
3. **ESLint** – `no-console` et `no-debugger` sont activés en production, évitant la fuite d’informations de debug.  
4. **Gestion des erreurs** – Les services renvoient les promesses Axios ; il convient d’ajouter des interceptors globales pour centraliser le traitement des erreurs HTTP (401, 403, 500).  

↩ [Retour au sommaire](#projet-agile-front)

---  

## 🚀 Déploiement & CI/CD (suggestions)  

| Étape | Action recommandée |
|-------|---------------------|
| **Build** | `yarn build` → artefacts dans `dist/`. |
| **Docker** | Image `node:16-alpine` → copie de `dist/` dans `nginx:alpine`. |
| **CI** | Pipeline GitLab CI : `npm ci`, `npm run lint`, `npm run test`, `npm run build`. |
| **Variables** | Stocker `VUE_APP_API_BASE_URL` dans les variables d’environnement du runner. |
| **Cache** | Activer le cache npm (`cache: npm`) pour accélérer les builds. |

↩ [Retour au sommaire](#projet-agile-front)

---  

## 📈 Perspectives d’évolution  

| Axe | Prochaine étape |
|-----|-----------------|
| **Internationalisation (i18n)** | Intégrer `vue-i18n` et externaliser les chaînes de texte. |
| **Tests unitaires** | Ajouter Jest + Vue Test Utils pour les composants critiques. |
| **Gestion avancée des erreurs** | Implémenter un store `notifications` et un interceptor Axios global. |
| **PWA** | Activer le plugin Vue CLI PWA pour un mode offline. |
| **Refactorisation du store** | Passer à Pinia (Vue 3) lors d’une migration future. |

↩ [Retour au sommaire](#projet-agile-front)