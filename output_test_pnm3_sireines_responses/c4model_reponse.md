D'après le contexte documentaire fourni sur **SIREINES**, le **modèle C4** est utilisé pour décrire son architecture logicielle de manière structurée et hiérarchisée. Voici les **4 niveaux** appliqués à SIREINES et leur signification :

---

### **1. Niveau 1 : Vue Contexte (C4-L1)**
**Objectif** : Montrer le système dans son **écosystème global**, avec ses utilisateurs et ses interactions avec les systèmes externes.
**Contenu pour SIREINES** :
- **Acteurs** :
  - *Utilisateur Métier* (Agent, Gestionnaire RH, etc.) qui interagit via **HTTPS**.
  - *Administrateur Technique* (Exploitant GTI, DevOps) qui gère le déploiement/sauvegardes via **SSH/HTTPS**.
- **Système central** : **SIREINES** (Système de Gestion des Évaluations Scientifiques et Techniques).
- **Systèmes externes** :
  - *Cerbère* (SSO centralisé pour l'authentification).
  - *Système RH* (fournit les données agents).
  - *Services d'Impression* (génération de PDF/courriers).
  - *Cloud ECO4* (infrastructure IaaS OpenStack).

**Représentation** : Diagramme **C4_Context** (Extrait 2).

---

### **2. Niveau 2 : Vue Conteneurs (C4-L2)**
**Objectif** : **Découper le système en conteneurs** (unités déployables indépendamment) et montrer leurs interactions.
**Contenu pour SIREINES** :
- **Conteneurs internes** (dans la frontière *Système SIREINES*) :
  - *Application Web* (Java 7, Struts 2, Vertigo, Tomcat) : Logique métier et interface.
  - *Base de Données* (PostgreSQL 15.2) : Stockage des données métier.
  - *Moteur de Recherche* (Elasticsearch 7.x) : Indexation full-text.
  - *Moteur de Rapports* (BIRT Runtime) : Génération de statistiques.
  - *Cache* (Ehcache) : Optimisation des performances (Hibernate).
- **Infrastructure** :
  - *Reverse Proxy* (Nginx) : Load balancing et terminaison SSL.
  - *Conteneurisation* (Docker) : Packaging et déploiement.
- **Systèmes externes** réutilisés : *Cerbère* et *Système RH*.

**Représentation** : Diagramme **C4_Container** (Extrait 3).

---

### **3. Niveau 3 : Vue Composants (non détaillé dans le contexte)**
**Objectif** : **Zoom sur un conteneur spécifique** pour décrire ses composants internes (modules, services, bibliothèques) et leurs relations.
**Exemple hypothétique pour SIREINES** :
- Pour le conteneur *Application Web*, ce niveau pourrait montrer :
  - Un composant *Gestion des Évaluations* (backend).
  - Un composant *Tableau de Bord* (frontend).
  - Un composant *API REST* pour communiquer avec la base de données.

**Note** : Le contexte documentaire ne fournit pas de diagramme pour ce niveau, mais il est mentionné comme faisant partie de l'analyse complète.

---

### **4. Niveau 4 : Vue Code (non détaillé dans le contexte)**
**Objectif** : **Détail d'un composant** jusqu'au niveau du code (classes, interfaces, packages, etc.).
**Exemple hypothétique pour SIREINES** :
- Pour un composant comme *Gestion des Évaluations*, ce niveau pourrait inclure :
  - Diagrammes de classes (ex: `EvaluationService`, `AgentRepository`).
  - Relations entre packages (ex: `fr.sireines.model`, `fr.sireines.service`).

**Note** : Comme pour le Niveau 3, ce niveau est cité dans les extraits (4 à 7) mais non documenté en détail.

---

### **Synthèse des 4 Niveaux pour SIREINES**
| **Niveau**       | **Portée**                          | **Exemple pour SIREINES**                          | **Diagramme Associé**       |
|------------------|-------------------------------------|----------------------------------------------------|-----------------------------|
| **Contexte (L1)** | Écosystème global                   | Utilisateurs + SIREINES + systèmes externes (Cerbère, RH, Cloud). | C4_Context (Extrait 2)      |
| **Conteneurs (L2)** | Découpage en unités déployables    | Application Web, Base PostgreSQL, Elasticsearch, etc. | C4_Container (Extrait 3)   |
| **Composants (L3)** | Modules internes d'un conteneur    | Non détaillé (ex: API, services backend).          | Non fourni                  |
| **Code (L4)**     | Détails d'implémentation            | Non détaillé (ex: classes Java, packages).        | Non fourni                  |

---
### **Points Clés**
- Le modèle C4 permet une **approche progressive** : du macro (contexte) au micro (code).
- Pour SIREINES, les **niveaux 1 et 2 sont documentés** (diagrammes PlantUML), tandis que les niveaux 3 et 4 sont **mentionnés comme existants** mais non détaillés dans les extraits.
- Les **technologies clés** identifiées :
  - **Backend** : Java 7, Struts 2, Vertigo, Tomcat.
  - **Données** : PostgreSQL, Elasticsearch, Ehcache.
  - **Infrastructure** : Docker, Nginx, Cloud OpenStack.