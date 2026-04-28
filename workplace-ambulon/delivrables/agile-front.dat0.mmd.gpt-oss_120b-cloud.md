# Dossier d’Architecture Technique (DAT) – **agile‑front**  
*Projet : Interface web de gestion d’études Agile*  

---

## 1. Introduction et objectifs  

### 1.1 Vue d’ensemble fonctionnelle  
Le produit **agile‑front** est une application mono‑page (SPA) développée avec **Vue 3** et **Vuetify**. Elle permet aux utilisateurs :  

* de s’authentifier (login) ;  
* de consulter, créer, modifier et exporter des *études* et leurs *financements* ;  
* d’accéder à des tableaux de bord statistiques, des tutoriels vidéo et des liens utiles ;  
* d’interagir avec le back‑office (API REST) via le service **LegacyProxyService**.  

### 1.2 Diagramme C4 – Niveau 1 (Contexte)  

```mermaid
graph LR
    A[Utilisateurs] -->|Navigateur HTTP| B[agile‑front (SPA)]
    B -->|API REST (HTTPS)| C[API Back‑office (Legacy)]
    C -->|Base de données| D[(DB Études)]
    B -->|Assets CDN| E[Google Fonts / Material Design Icons]
    style A fill:#bbf,stroke:#333,stroke-width_2px;
    style B fill:#f9f,stroke:#333,stroke-width_2px;
    style C fill:#bfb,stroke:#333,stroke-width_2px;
    style D fill:#ffb,stroke:#333,stroke-width_2px;
    style E fill:#ffd,stroke:#333,stroke-width_2px
```

### 1.3 Objectifs de qualité (orientés utilisateur)  

| # | Objectif | Raison métier / utilisateur |
|---|----------|----------------------------|
| 1 | **Performance** – temps de réponse < 2 s pour les écrans principaux | Fluidité de la navigation, satisfaction utilisateur |
| 2 | **Sécurité** – authentification forte, protection des données d’étude | Conformité RGPD, prévention des fuites |
| 3 | **Maintenabilité** – architecture modulaire, tests unitaires > 80 % | Réduction du coût de l’évolution et du support |
| 4 | **Accessibilité** – conformité WCAG 2.1 AA | Inclusion de tous les utilisateurs, exigences légales |
| 5 | **Opérabilité** – déploiement continu, rollback automatisé | Disponibilité continue, réactivité aux incidents |

---

## 2. Parties prenantes  

| Rôle | Contact (exemple) | Attentes principales |
|------|-------------------|----------------------|
| **MOA** (Maîtrise d’Ouvrage) | `moa@agile.example.com` | Fonctionnalités métier, respect des délais |
| **Développeur Front** | `dev.front@agile.example.com` | Documentation technique, environnement de dev stable |
| **Architecte SI** | `archi@agile.example.com` | Cohérence avec l’architecture globale, conformité aux standards |
| **RSSI** (Responsable Sécurité) | `rssi@agile.example.com` | Gestion des risques, traçabilité, chiffrement |
| **Exploitation** | `ops@agile.example.com` | Supervision, sauvegarde, procédure de mise en production |
| **Utilisateurs finaux** | – | Expérience fluide, disponibilité, protection de leurs données |

---

## 3. Contraintes  

### 3.1 Contraintes d’architecture  

| Type | Description |
|------|-------------|
| **Technique** | Utilisation de Vue 3, Vuetify, Babel, PostCSS. API uniquement en HTTPS. |
| **Organisationnelle** | CI/CD via GitLab CI, revue de code obligatoire. |
| **Réglementaire** | Conformité RGPD, exigences d’accessibilité WCAG 2.1 AA. |
| **Performance** | Taille du bundle < 500 KB (gzip). |
| **Interopérabilité** | Compatibilité avec navigateurs listés dans `.browserslistrc` (> 1 % usage, dernières 2 versions). |

### 3.2 Contraintes de sécurité – modèle D‑I‑C‑T  

| Dimension | Exigence | Mesure prévue |
|-----------|----------|---------------|
| **Disponibilité** | 99,5 % mensuel | Load‑balancing Nginx, health‑checks, redondance des conteneurs. |
| **Intégrité** | Protection contre altération des données | Hachage SHA‑256 des payloads, validation côté serveur. |
| **Confidentialité** | Chiffrement des échanges et du stockage | HTTPS TLS 1.3, dumps AES‑256 (voir § 8). |
| **Traçabilité** | Audit complet des actions utilisateurs | Journalisation via middleware Axios + serveur de logs (ELK). |

---

## 4. Contexte et périmètre  

### 4.1 Contexte métier  
L’application est destinée aux **agents de pilotage** et **chercheurs** du ministère de l’Environnement. Elle s’intègre aux processus de suivi des études d’impact, de financement et de diffusion de résultats.  

### 4.2 Contexte technique  

| Interface externe | Protocole | Fréquence / Volume | Type |
|------------------|-----------|-------------------|------|
| **API Legacy** (études, sécurité) | HTTPS/REST (JSON) | ~50 req/s en pic | Synchronous |
| **CDN fonts / icons** | HTTPS | ponctuel | Stateless |
| **Service de sauvegarde** (B3, Outscale, GCP) | HTTPS/REST | quotidien (dump) | Asynchrone |
| **Système de monitoring GTI** | Prometheus pushgateway | continue | Metrics |

---

## 5. Stratégie de solution  

### 5.1 Décisions architecturales majeures  

| Décision | Raison | Impact |
|----------|--------|--------|
| **SPA Vue 3 + Vuetify** | Réactivité, UI Material, communauté active | Facilite le développement UI, maintenabilité |
| **Axios + token JWT (via `SecurityService`)** | Centralisation de la sécurité HTTP | Simplifie la gestion des en‑têtes, rafraîchissement de token |
| **Vuex (store) en mode modules** | Séparation claire des domaines (`studies`, `security`) | Evolutif, testable |
| **Dockerisation (containeur unique)** | Portabilité, isolement | Simplifie le déploiement sur le cloud interne |
| **CI/CD GitLab** | Pipelines automatisés (lint, test, build, push) | Qualité continue, rapidité de mise en prod |

### 5.2 Environnement technologique  

| Couche | Technologie | Version |
|-------|--------------|---------|
| **Frontend** | Vue 3, Vuetify 2, Vue‑Router, Vuex | ^3.2, ^2.5 |
| **Langage** | JavaScript (ES2020) + Babel | - |
| **Build** | Webpack (via Vue‑CLI) | - |
| **Styling** | PostCSS, Autoprefixer | - |
| **Tests** | Jest + Vue Test Utils | - |
| **Conteneurisation** | Docker (node:14‑alpine) | - |
| **CI/CD** | GitLab CI, Docker Registry | - |
| **Infra** | OpenStack (tenant *pnm3*), Nginx load‑balancer, PostgreSQL (DB Études) | - |

### 5.3 Forge logicielle  

| Élément | Outil |
|---------|-------|
| **Gestion de code** | GitLab (repo `agile-front`) |
| **Intégration continue** | GitLab CI (lint → test → build → push) |
| **Tests unitaires** | Jest (coverage > 80 %) |
| **Analyse statique** | ESLint (config `.eslintrc.js`) |
| **Déploiement** | Docker Compose (dev) / Helm chart (prod) |
| **Documentation** | Markdown dans le repo, diagrammes Mermaid |

---

## 6. Vue en briques  

### 6.1 Vue conteneur (C4 – Niveau 2)  

```mermaid
graph TD
    subgraph "Frontend Container"
        FE[Vue SPA (agile‑front)]
        FE -->|axios| API[Legacy Proxy Service]
        FE -->|store| Vuex[Vuex Store]
        FE -->|router| Router[Vue‑Router]
    end
    subgraph "Backend Container"
        API -->|REST| BE[API Legacy (Java/Node)]
        BE -->|SQL| DB[(PostgreSQL)]
    end
    subgraph "Infrastructure"
        NGINX[Nginx LB] --> FE;
        NGINX --> BE;
    end
    style FE fill:#f9f,stroke:#333,stroke-width_2px;
    style API fill:#bbf,stroke:#333,stroke-width_2px;
    style BE fill:#bfb,stroke:#333,stroke-width_2px;
    style DB fill:#ffb,stroke:#333,stroke-width_2px;
    style NGINX fill:#ffd,stroke:#333,stroke-width_2px
```

### 6.2 Description des conteneurs  

| Conteneur | Rôle | Principaux artefacts |
|-----------|------|---------------------|
| **Vue SPA** | Interface utilisateur, routage, rendu réactif | `src/main.js`, `src/App.vue`, `src/router.js`, `src/views/*` |
| **Vuex Store** | Gestion d’état partagé (`studies`, `security`) | `src/store/modules/*` |
| **Legacy Proxy Service** | Wrapper HTTP vers l’API existante | `src/services/LegacyProxyService.js` |
| **Security Service** | Récupération du sujet, gestion du token | `src/services/SecurityService.js` |
| **Nginx** | Entrée unique, TLS termination, load‑balancing | `nginx.conf` (non versionné, fourni par infra) |
| **PostgreSQL** | Persistance des études, financements, logs | Schéma DB (hors périmètre front) |

---

## 7. Vue exécution  

### 7.1 Scénario critique 1 – Authentification (login)  

1. L’utilisateur ouvre l’URL → le **SPA** charge `Login.vue`.  
2. Le formulaire envoie les credentials à `SecurityService.getSubject()` (axios → `/security/subject`).  
3. Le backend valide, renvoie un **JWT** et les attributs du sujet.  
4. Le token est stocké dans **Vuex** (`security` module) et dans **sessionStorage**.  
5. Le routeur redirige vers la page d’accueil protégée.  

*Points de contrôle* :  
* Validation du JWT (signature, expiration).  
* Journalisation de l’événement dans le service de logs.  

### 7.2 Scénario critique 2 – Création d’une étude  

1. L’utilisateur clique sur **« Nouvelle étude »** → `EtudeNew.vue`.  
2. Le composant récupère les listes de référence via `StudiesService.getReferenceData()`.  
3. L’utilisateur remplit le formulaire et déclenche `StudiesService.createStudy(formData)`.  
4. `LegacyProxyService.createStudy` POST `/etudes/new?api=true`.  
5. Le backend crée l’enregistrement, renvoie l’ID et le statut 201.  
6. Le front met à jour le store (`studies` module) et navigue vers la vue `Etude.vue`.  

*Points de contrôle* :  
* Vérification de la conformité du payload (JSON schema).  
* Gestion des erreurs réseau (retry, fallback).  

### 7.3 Scénario critique 3 – Export des études (fonctionnalité « Export »)  

1. L’utilisateur sélectionne une ou plusieurs études dans `EtudesList.vue`.  
2. Le composant appelle `ExportService.exportStudies(ids)`.  
3. Le service POST `/export` (via `LegacyProxyService`).  
4. Le serveur génère un fichier CSV, renvoie une URL de téléchargement signé (validité 5 min).  
5. Le front ouvre la URL dans un nouvel onglet, le navigateur télécharge le fichier.  

*Points de contrôle* :  
* Le lien signé est **HTTPS** et limité dans le temps (confidentialité).  
* Le fichier est enregistré dans le bucket de sauvegarde (voir § 8).  

---

## 8. Vue Déploiement *(section standardisée)*  

```markdown
### Environnements
| Environnement | Hébergement | Serveurs | Réseau | Particularités |
|---------------|-------------|----------|--------|----------------|
| Développement | À compléter | À compléter | À compléter | À compléter |
| Recette       | À compléter | À compléter | À compléter | À compléter |
| Production    | À compléter | À compléter | À compléter | À compléter |

### Infrastructure
Le produit est hébergé sur le cloud interne ECO4 basé sur Openstack, dans le tenant 'pnm3' du département.  
Le reverse-proxy Nginx du schéma ci-dessous est en fait une paire de Nginx load-balancés en frontal des produits hébergés sur le tenant.

```mermaid
graph TD
    A[Nginx] -- B[Application]
    B -- C[Base de données]
    B -- D[Autres services]
```

### Supervision
Le produit est supervisé via le système standard du GTI pour ce faire :
- via Portainer pour la partie purement conteneurisée,
- via la stack Prometheus/Grafana/Loki/AlertManager,
- Le produit dispose également d'une supervision PSIN.

### Sauvegardes
Les sauvegardes de la base de données sont assurées par des scripts standards du GTI permettant la création de dumps cryptés en AES-256 et déposés sur :
- le stockage objet B3 du IaaS ministériel,
- le stockage objet Outscale SecNumCloud (via la prestation qu'a le GTI sur le marché "Nuage Public"),
- le stockage objet standard de Google Cloud (via la prestation qu'a le GTI sur le marché "Nuage Public").
```

---

## 9. Sujets transverses  

| Sujet | Implémentation / Référence |
|-------|----------------------------|
| **Authentification** | JWT, rafraîchissement via `SecurityService`, stockage en `sessionStorage`. |
| **Autorisation** | Guard Vue‑Router (`meta.requiresAuth`), checks `isAdmin` dans store. |
| **Journalisation** | Intercepteur Axios → envoi vers `/logs` (ELK), logs côté client (console + sentry éventuel). |
| **Monitoring** | Métriques UI (performance API) exposées via `/metrics` → Prometheus. |
| **Gestion des erreurs** | Wrapper `apiClient` avec `try/catch`, UI toast via Vuetify `v-snackbar`. |
| **API** | Tous les appels passent par les services (`LegacyProxyService`, `ExportService`, `StudiesService`). |
| **Internationalisation (i18n)** | Prévu via `vue-i18n` (non encore activé). |
| **Accessibilité** | Utilisation de composants Vuetify accessibles, tests aXe. |
| **CI/CD** | Lint → Tests → Build → Docker image → Push → Deploy (GitLab CI). |
| **Sécurité des données** | CSP, HSTS, cookies `SameSite=Strict`, chiffrement des dumps (voir § 8). |

---

## 10. Exigences de qualité  

| ID | Exigence | Critère d’acceptation (scénario de validation) |
|----|----------|-----------------------------------------------|
| Q‑01 | **Temps de chargement** de la page d’accueil < 2 s (3G) | Mesure via Lighthouse, score ≥ 90 % en performance. |
| Q‑02 | **Authentification sécurisée** – JWT signé SHA‑256, expiration ≤ 30 min | Test d’injection de token expiré → refus d’accès, logs d’événement. |
| Q‑03 | **Couverture de tests unitaires** ≥ 80 % | Rapport Jest `coverage` affichant ≥ 80 % sur toutes les sources. |
| Q‑04 | **Conformité WCAG 2.1 AA** | Audit aXe automatisé + revue manuelle, aucune erreur critique. |
| Q‑05 | **Disponibilité** ≥ 99,5 % mensuel | Monitoring Prometheus → alerte si downtime > 5 min. |

---

## 11. Risques et dettes techniques  

| Risque | Impact | Mesure corrective / mitigation |
|--------|--------|--------------------------------|
| **Dépendance à l’API Legacy** (non‑documentée) | Blocage fonctionnel si l’API change | Wrapper `LegacyProxyService` isolé, tests contract‑first, plan de migration vers API versionnée. |
| **Bundle JavaScript trop lourd** (vu la présence de Vuetify) | Dégradation performance sur 3G | Analyse Webpack Bundle Analyzer, lazy‑loading des routes, tree‑shaking. |
| **Gestion du token côté client** (stockage en `sessionStorage`) | Risque XSS → vol de token | CSP strict, désactiver `eval`, audit de dépendances, envisager HttpOnly cookie. |
| **Documentation technique insuffisante** | Difficulté de maintenance | ADR (Architecture Decision Records) obligatoires, mise à jour du README. |
| **Dettes liées aux tests d’intégration** | Couverture fonctionnelle faible | Ajouter tests Cypress pour les flux critiques (login, export). |

---

## 12. Annexes  

### 12.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **SPA** | Single Page Application – application web qui charge une seule page HTML et gère la navigation en JavaScript. |
| **Vuex** | Bibliothèque de gestion d’état centralisée pour Vue.js. |
| **JWT** | JSON Web Token – token signé transportant les claims d’un utilisateur. |
| **C4** | Modèle de visualisation d’architecture (Context, Container, Component, Code). |
| **RGPD** | Règlement Général sur la Protection des Données (UE). |
| **WCAG** | Web Content Accessibility Guidelines. |
| **CI/CD** | Intégration Continue / Déploiement Continu. |
| **NGINX LB** | Nginx configuré en tant que Load‑Balancer. |
| **OpenStack** | Plate‑forme cloud open source utilisée par le ministère. |

### 12.2 Décisions d’architecture (ADR) – exemples  

| # | Décision | Contexte | Conséquence |
|---|----------|----------|-------------|
| ADR‑01 | **Choisir Vue 3 + Vuetify** comme framework UI | Besoin d’une UI réactive, cohérente avec le design system du ministère | Gains de productivité, mais bundle plus important → optimisation nécessaire. |
| ADR‑02 | **Utiliser Docker** pour le front | Uniformité des environnements dev / prod | Simplifie le déploiement, nécessite gestion des images et du registre. |
| ADR‑03 | **JWT via `SecurityService`** | Authentification centralisée côté front | Découplage du front du back, nécessite sécurisation du stockage du token. |
| ADR‑04 | **CI avec GitLab** | Pipeline déjà en place dans l’organisation | Automatisation des tests et du déploiement, dépendance à la disponibilité du runner. |
| ADR‑05 | **Sauvegarde AES‑256** des dumps DB | Obligation de protection des données sensibles | Conformité RGPD, nécessite gestion des clés de chiffrement. |

---

*Fin du Dossier d’Architecture Technique*  