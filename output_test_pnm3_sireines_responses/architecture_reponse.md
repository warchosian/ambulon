Voici une description de l'architecture technique du système **SIREINES**, basée uniquement sur les extraits documentaires fournis :

---

### **1. Vue d'ensemble architecturale**
**Type d'architecture** :
- **Monolithe web Java** (justifié par la simplicité de déploiement, la cohérence avec le *legacy*, et une équipe réduite).

---

### **2. Couches architecturales et composants**

#### **2.1. Couche Application (Application Layer)**
**Services exposés** :
- **SvcDossiers** : Gestion des dossiers (intègre **Elasticsearch (ES)** pour l'indexation).
- **SvcAgents** : Gestion des agents.
- **SvcSeances** : Gestion des séances.
- **SvcExtr** : Délègue les extractions de rapports au moteur **BIRT**.
- **SvcRef** : Services de référence (rôle non détaillé).

**Intégrations clés** :
- **Authentification** : Le composant **Actions** utilise **Cerbere** pour l'authentification.
- **Recherche** : **SvcDossiers** indexe les données dans **Elasticsearch (ES)**.
- **Reporting** : **SvcExtr** délègue la génération de rapports à **BIRT**.

---

#### **2.2. Composants critiques (C4-L3)**
| **Composant**                     | **Rôle**                                                                 | **Vulnérabilités/Dettes**                          | **Dépendances**                          |
|------------------------------------|--------------------------------------------------------------------------|----------------------------------------------------|------------------------------------------|
| **DossierRechercheMotsClefsAction** (COMP-001) | Recherche de dossiers par mots-clés.                                   | Vulnérabilités critiques non détaillées.         | Non spécifiées.                          |
| **ExtractionsServicesImpl** (COMP-002)       | Implémentation des services d'extraction (lié à **BIRT**).             | Vulnérabilités critiques + dette technique **critique**. | **BIRT**.                               |
| **ImportsServicesImpl** (COMP-003)           | Gestion des imports de données.                                         | Vulnérabilités critiques.                         | Non spécifiées.                          |
| **CerbereUtil + SireinesSessionFilter** (COMP-004) | Authentification et gestion des sessions (via **Cerbere**).       | Vulnérabilités identifiées (niveau 🟡).           | Dépendances externes critiques.         |
| **ESEmbeddedSearchServicesPlugin** (COMP-005) | Plugin pour l'indexation **Elasticsearch** embarqué.                   | Vulnérabilités critiques.                         | **Elasticsearch 7.x**.                   |

---

### **3. Patterns architecturaux**
- **MVC (Model-View-Controller)** :
  - **Framework** : **Struts 2** (couche présentation) + **Vertigo Framework** (services, DAO, ORM léger).
  - **Justification** : Standard historique du projet, génération de code via **MDA (Model-Driven Architecture)**, et productivité pour une équipe réduite.
- **Persistance** :
  - **SQL natif** + **MDA (KSP)** pour un contrôle fin des requêtes métier complexes.
- **Recherche** :
  - **Elasticsearch embarqué** (version 7.x) pour la recherche full-text performante sur les dossiers.
- **Reporting** :
  - **BIRT intégré** (version 4.x) pour générer des rapports complexes et paramétrables.
- **Conteneurisation** :
  - **Docker + Docker Compose** pour la portabilité et la reproductibilité des environnements.

---

### **4. Couche Technologie (Technology Layer)**
#### **4.1. Langages et Frameworks**
| **Catégorie**       | **Technologie**       | **Version** | **Rôle**                                  |
|---------------------|------------------------|-------------|-------------------------------------------|
| Langage             | Java                   | 1.7         | Logique métier.                           |
| Framework Web       | Struts 2               | 2.x         | Couche présentation (MVC).               |
| Framework Métier    | Vertigo                | -           | Services, DAO, ORM léger.                |
| Base de données     | PostgreSQL             | 15.2        | Persistance relationnelle.               |
| Moteur de recherche | Elasticsearch          | 7.x         | Indexation full-text (embarqué).          |
| Reporting           | BIRT                   | 4.x         | Génération de rapports.                  |
| Frontend            | Bootstrap              | 2/3         | UI responsive.                            |
| Template Engine     | FreeMarker              | -           | Génération des vues.                     |
| Build               | Maven                  | 3.6         | Compilation et packaging.                |
| Conteneur           | Tomcat                 | 9.x         | Serveur d'applications (embarqué).       |

#### **4.2. Artifacts et déploiement**
- **Fichiers principaux** :
  - `sireines-web.war` : Déployé dans `/usr/local/tomcat/webapps/ROOT/`.
  - Fichiers de rapports (`*.rptdesign`) : Stockés dans `/usr/local/tomcat/webapps/ROOT/report/`.
  - Script SQL (`crebas.sql`) : Modèle de base de données dans `sireines-database/modele/`.
  - Configuration Elasticsearch (`elasticsearch.yml`) : Dans `src/main/resources/search/config/`.

---

### **5. Synthèse des choix architecturaux**
| **Décision**               | **Technologie/Pattern**       | **Justification**                                                                 |
|----------------------------|-------------------------------|----------------------------------------------------------------------------------|
| Architecture monolithique  | Java (Struts 2 + Vertigo)     | Simplicité, cohérence avec le *legacy*, équipe réduite.                          |
| Persistance                | SQL natif + MDA (KSP)         | Performance et contrôle fin des requêtes complexes.                              |
| Recherche                  | Elasticsearch embarqué        | Recherche full-text performante.                                                 |
| Reporting                  | BIRT intégré                  | Rapports complexes et paramétrables (exigence métier).                          |
| Conteneurisation           | Docker + Docker Compose       | Portabilité et reproductibilité des environnements.                             |
| Authentification           | Cerbere                       | Solution centralisée pour la sécurité.                                           |

---
### **6. Points d'attention**
- **Dettes techniques** :
  - **Critique** pour **ExtractionsServicesImpl** (COMP-002).
  - Vulnérabilités identifiées dans plusieurs composants (ex : **CerbereUtil**, **ESEmbeddedSearchServicesPlugin**).
- **Sécurité** :
  - Analyse **STRIDE** et **OWASP Top 10 2021** référencées (détails non fournis dans les extraits).
  - Recommandations prioritaires classées en **court/moyen/long terme** (ex : actions urgentes à 0-3 mois).

---
Cette architecture reflète un équilibre entre **héritage technique** (Java 1.7, Struts 2) et **modernisation partielle** (Elasticsearch, Docker), avec des défis liés à la **sécurité** et à la **dette technique**.