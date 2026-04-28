# admin_ep – Documentation Technique

[TOC]

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 1. Introduction ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

**Projet** : `admin_ep`  
**Chemin racine** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\admin_ep`  
**Nombre de fichiers non‑binaires** : 275  

### 1.1. Contexte fonctionnel
L’application **Admin EP** (Administration des établissements publics) centralise les listes des membres des conseils d’administration des établissements publics placés sous la tutelle du ministère de la Transition écologique et solidaire.  
Elle assure :

| Fonctionnalité | Description |
|----------------|-------------|
| **Interface d’écriture** | Saisie manuelle des administrateurs, gestionnaires, mandats, etc. |
| **Alimentation automatique** | Extraction de données depuis le JORF (Journal officiel de la République Française). |
| **Authentification** | Gestion des droits via le SSO Cerbère. |
| **Archivage** | Conservation des mandats expirés et des pièces jointes. |
| **Lecture & recherche** | Consultation et recherche multi‑critères (établissement, personne, mandat). |
| **Statistiques** | Tableaux de bord et indicateurs de suivi. |
| **Alertes d’échéance** | Notification par e‑mail des mandats proches de la fin. |

### 1.2. Parties prenantes
| Rôle | Responsable |
|------|--------------|
| Maîtrise d’ouvrage | SG / SPES |
| Maîtrise d’œuvre | SG / SNUM / PNM / DPNM3 / BPN |
| Prestataire | CGI |
| Chef de produit | Christian Arbogast (SG / DNUM / PNM / DPNM3 / BPN) |
| Directrice de produit | Céline Gilliard (SG / DNUM / PNM / DPNM3 / BPN) |

### 1.3. Accès & environnements
| Environnement | Version | URL |
|---------------|---------|-----|
| Production | 1.3.3 (12/2021) | <https://adminep.e2.rie.gouv.fr/> |
| Pré‑production | 1.3.3 (12/2021) | <https://adminep.preprod.e2.rie.gouv.fr/> |
| Recette (déprécié) | — | <http://adminep.recette.e2.rie.gouv.fr/> |
| Supervision PSIN | — | <http://psin.supervision.e2.rie.gouv.fr/portails/MonApplication.php?application=ADMINEP> |

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 2. Structure du projet ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

Le dépôt est organisé en modules Maven :

```
admin_ep
├─ adminep-database
│   ├─ scripts
│   │   ├─ init          (création schéma, séquences, tables, données de base)
│   │   └─ update       (scripts de migration versionnée)
│   └─ pom.xml
├─ adminep-deployment
│   ├─ conf
│   └─ pom.xml
├─ adminep-doc
│   └─ pom.xml
├─ adminep-web
│   ├─ src/main/java
│   │   ├─ com/github/jferard/fastods/style/...
│   │   └─ fr/gouv/e2/baseadmin/...
│   │       ├─ boot        (initialisation Spring/Vertigo)
│   │       ├─ controller  (Struts 2 actions)
│   │       ├─ model       (entités métier)
│   │       ├─ security    (gestion des sessions et droits)
│   │       └─ services    (logique métier)
│   ├─ src/main/resources
│   │   ├─ boot/config      (configuration Spring/Vertigo)
│   │   ├─ definitions/*   (KSP – Vertigo DSL)
│   │   └─ webapp          (JSP, static assets)
│   └─ pom.xml
├─ search (outils de recherche)
└─ pom.xml (agrégateur)
```

### 2.1. Diagramme de modules Maven

```mermaid
graph TD;
    A[admin_ep (aggregator)] --> B[adminep-database]
    A --> C[adminep-deployment]
    A --> D[adminep-doc]
    A --> E[adminep-web]
    A --> F[search]
    B --> B1[scripts/init]
    B --> B2[scripts/update]
    E --> E1[controller]
    E --> E2[services]
    E --> E3[model]
    E --> E4[resources]
```

### 2.2. Arborescence détaillée (extrait)

```
adminep-web
 ├─ src/main/java/fr/gouv/e2/baseadmin
 │   ├─ boot
 │   │   ├─ I18nResourcesInitializer.java
 │   │   ├─ MasterDataInitializer.java
 │   │   ├─ SchedulerInitializer.java
 │   │   └─ SecurityManagerInitializer.java
 │   ├─ controller
 │   │   ├─ accueil/AccueilAction.java
 │   │   ├─ admins/DetailAdminAction.java
 │   │   ├─ admins/RechercheAdminsAction.java
 │   │   ├─ admins/UpsertAdminAction.java
 │   │   ├─ etablissements/DetailEPAction.java
 │   │   ├─ etablissements/RechercheEPAction.java
 │   │   ├─ etablissements/UpsertEPAction.java
 │   │   ├─ mandats/DetailMandatAction.java
 │   │   ├─ mandats/UpsertMandatAction.java
 │   │   └─ ... (autres contrôleurs)
 │   ├─ model
 │   │   ├─ referentiel/CodeEnum.java
 │   │   ├─ utilisateur/TypeProfilBaseAdmin.java
 │   │   └─ wiki/WikiArticleUrl.java
 │   ├─ security
 │   │   ├─ BaseAdminUserSession.java
 │   │   ├─ RightsHelper.java
 │   │   └─ SecurityHelper.java
 │   └─ services
 │       ├─ article/ArticleServices.java
 │       ├─ baseadmin/administrateur/AdministrateurServices.java
 │       ├─ integration/college/CollegeServices.java
 │       └─ ... (autres services)
 └─ src/main/resources
     ├─ boot/components/core.xml
     ├─ boot/config/application-config.xml
     ├─ definitions/services/article/recherche/rechercheArticleDao.ksp
     └─ webapp/WEB-INF/jsp/... (JSP de présentation)
```

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 3. Base de données ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

### 3.1. Schéma « integration »

Le schéma `integration` contient l’ensemble des tables métier.  
Les scripts d’initialisation sont :

* `0_createUserAndDB.sql` – création du rôle `baseadmin` et de la base `baseadmin`.
* `1_createSequenceAndTablesIntegration.sql` – séquences, tables et contraintes.
* `2_populateTablesIntegration.sql` – données de référence (type de mandat, type d’instance, charges, ministères, etc.).

#### 3.1.1. Exemple de création de table (simplifié)

```sql
CREATE TABLE integration.TYPE_MANDAT
(
    TMA_ID   BIGINT NOT NULL,
    TMA_TYPE VARCHAR(64) NOT NULL,
    PRIMARY KEY (TMA_ID)
);
COMMENT ON TABLE TYPE_MANDAT IS 'Liste des types de mandats';
```

#### 3.1.2. Principales tables (extrait)

| Table | Description |
|-------|-------------|
| `TYPE_MANDAT` | Types de mandat (Titulaire / Suppléant). |
| `TYPE_INSTANCE` | Types d’instance (Conseil d’administration, Conseil de surveillance). |
| `MODE_NOMINATION` | Modes de nomination (Arrêté, Décret, etc.) avec mots‑clés. |
| `CHARGE` | Charges ministérielles (ex. « Affaires étrangères »). |
| `MINISTERE` | Ministères (sigle, nom, statut). |
| `COLLEGE` | Collèges (identifiant). |
| `ETABLISSEMENT` | Établissements publics (SIREN, libellé, type d’instance). |
| `SYNONYME_COLLEGE` | Synonymes associés aux collèges. |
| `MINISTERE_CHARGE` | Association charge ↔ ministère. |
| `ETABLISSEMENT_COLLEGE` | Liaison établissement ↔ collège (nombre de membres, durée mandat). |
| `TUTELLE_ETABLISSEMENT_CHARGE` | Tutelle d’un établissement par une charge. |
| `DIRECTION` | Directions (sigle, intitulé). |
| `DIRECTION_MINISTERE` | Liaison direction ↔ ministère. |

#### 3.1.3. Diagramme ER simplifié

```mermaid
erDiagram;
    TYPE_MANDAT ||--o{ MANDAT : "type"
    TYPE_INSTANCE ||--o{ ETABLISSEMENT : "instance"
    CHARGE ||--o{ MINISTERE_CHARGE : "charge"
    MINISTERE ||--o{ MINISTERE_CHARGE : "ministère"
    ETABLISSEMENT ||--o{ ETABLISSEMENT_COLLEGE : "college"
    COLLEGE ||--o{ ETABLISSEMENT_COLLEGE : "établissement"
    ETABLISSEMENT ||--o{ TUTELLE_ETABLISSEMENT_CHARGE : "tutelle"
    CHARGE ||--o{ TUTELLE_ETABLISSEMENT_CHARGE : "charge"
    DIRECTION ||--o{ DIRECTION_MINISTERE : "direction"
    MINISTERE ||--o{ DIRECTION_MINISTERE : "ministère"
```

### 3.2. Scripts de migration (dossier `update`)

Les mises à jour sont versionnées (`0.1.0_to_0.2.0`, `0.2.0_to_0.3.0`, …) et contiennent :

* Ajout / suppression de colonnes.
* Création de nouvelles tables (ex. `gestionnaires`).
* Population de données de référence (tutelle, gestionnaires, etc.).
* Corrections ponctuelles (`1_correction_17181.sql`).

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 4. Build & dépendances ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

### 4.1. Maven – Aggrégateur

Le `pom.xml` à la racine agrège les modules :

```xml
<modules>
    <module>adminep-database</module>
    <module>adminep-deployment</module>
    <module>adminep-doc</module>
    <module>adminep-web</module>
    <module>search</module>
</modules>
```

### 4.2. `adminep-database/pom.xml`

* Packaging : `pom` (module purement SQL).  
* Plugin : `maven-assembly-plugin` → création d’une archive `sql.zip` contenant le répertoire `scripts/update`.

### 4.3. `adminep-web/pom.xml`

Principales dépendances (extrait) :

| Groupe | Artefact | Version | Rôle |
|--------|----------|---------|------|
| `org.springframework` | `spring-context` | 5.x | Inversion de contrôle (Vertigo). |
| `org.apache.struts` | `struts2-core` | 2.5.x | Framework MVC. |
| `org.displaytag` | `displaytag` | 1.2.x | Table HTML dynamique. |
| `org.postgresql` | `postgresql` | 42.x | Driver JDBC. |
| `org.apache.logging.log4j` | `log4j-core` | 2.x | Logging. |
| `com.github.jferard` | `fastods` | 1.4.x | Génération de fichiers ODS. |

Le packaging final produit un fichier WAR déployable sur Tomcat 9 (ou Tomcat 10 après migration).

### 4.4. Gestion des versions

| Module | Version actuelle (mars 2026) |
|--------|------------------------------|
| `adminep-web` | 1.2.3 |
| `adminep-database` | 1.2.3 |
| `adminep-deployment` | 1.2.3 |
| `adminep-doc` | 1.2.3 |

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 5. Déploiement ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

### 5.1. Conteneur d’exécution
* **Serveur d’application** : Tomcat 9.0.8 (en cours de migration vers Tomcat 10).  
* **Base de données** : PostgreSQL 9.6.11 (prévu PostgreSQL 15).  

### 5.2. Configuration Tomcat (`WEB-INF/web.xml`)

* Déclaration du **Servlet** Struts 2 (`org.apache.struts2.dispatcher.filter.StrutsPrepareAndExecuteFilter`).  
* Paramètres de **session timeout** et de **sécurité** (filtre Cerbère).  

### 5.3. Fichiers de configuration Vertigo (`boot/config/*.xml`)

| Fichier | Rôle |
|---------|------|
| `application-config.xml` | Paramètres généraux (datasource, scheduler). |
| `baseadmin-auth-config.xml` | Mapping des rôles Cerbère → autorisations applicatives. |
| `elasticsearch.yml` | Configuration du moteur de recherche (utilisé par le module `article`). |

### 5.4. Déploiement automatique (Maven)

Le module `adminep-deployment` produit deux archives :

* **`assembly-sources.xml`** → source distribution.  
* **`assembly-zip.xml`** → WAR + scripts SQL (`sql.zip`) pour automatiser la création de la base.

Le processus CI (GitLab CI) exécute :

```bash
mvn clean install
mvn -pl adminep-web war:war
```

Puis copie le WAR dans le répertoire de déploiement Tomcat et redémarre le serveur.

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 6. Architecture applicative ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

### 6.1. Vue d’ensemble

```mermaid
flowchart LR;
    subgraph WEB[Web Tier]
        A[Struts2 Controllers] --> B[Vertigo Services]
        B --> C[DAO (JDBC)]
    end;
    subgraph BATCH[Batch / Scheduler]
        D[ArticleAnalyser] --> B;
        D --> E[JORF Extractor]
    end;
    subgraph DB[PostgreSQL]
        C --> F[(integration schema)]
    end;
    A --> G[HTML/JSP Views]
    G --> H[Static assets (CSS, JS, images)]
```

* **Contrôleurs** (`fr.gouv.e2.baseadmin.controller.*`) : actions Struts 2, réception des requêtes HTTP, validation des formulaires.  
* **Services** (`fr.gouv.e2.baseadmin.services.*`) : logique métier, appels DAO, orchestrations (ex. `ArticleAnalyser`).  
* **DAO** (via Vertigo `Service` abstractions) : accès JDBC standard, utilisation de `PreparedStatement`.  
* **Batch** : `ArticleAnalyser` parcourt le JORF, crée / met à jour les entités `Mandat`, `Gestionnaire`, `Etablissement`.  

### 6.2. Sécurité

* **Cerbère** : SSO interne (LDAP).  
* **`SecurityFilter`** : filtre servlet qui récupère le token Cerbère, crée une instance `BaseAdminUserSession`.  
* **`RightsHelper`** : méthode utilitaire `hasRight(user, right)` utilisée dans les actions pour protéger les opérations CRUD.  

### 6.3. Gestion des sessions

```java
public class BaseAdminUserSession {
    private String login;
    private Set<String> roles;
    // getters / setters
}
```

Le filtre injecte cet objet dans la **RequestContext** afin que les actions puissent récupérer les informations d’identité.

### 6.4. Composants UI

* **JSP** : fichiers sous `WEB-INF/jsp/**` (ex. `admins/detailAdmin.jsp`).  
* **Tags DisplayTag** : tableau dynamique avec pagination, tri, export CSV/Excel.  
* **Bootstrap 3** : feuilles de style (`bootstrap.css`, `bootstrap.min.css`).  
* **Chosen** : listes déroulantes améliorées (ex. sélection de collèges).  

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 7. Exploitation & support ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

### 7.1. Contacts techniques

| Fonction | Nom | Email |
|----------|-----|-------|
| Chef de produit | Christian Arbogast | <Christian.Arbogast@developpement-durable.gouv.fr> |
| Directrice de produit | Céline Gilliard | <celine.gilliard@developpement-durable.gouv.fr> |
| Support technique | assistance‑adminep@developpement-durable.gouv.fr | – |

### 7.2. Gestion des incidents

* **Ticketing** – Portail SIT : <https://portail-support.din.developpement-durable.gouv.fr/projects/admin-ep/issues>  
* **Escalade** – Niveau 1 : équipe de développement CGI.  
* **Escalade 2** – MOE : SG / DNUM / PNM / DPNM3 / BPN.

### 7.3. Audits & conformité

| Aspect | Statut |
|--------|--------|
| Évaluation DICT | **Oui** (07/09/2018) |
| RGPD – Registre des traitements | Maintenu (voir `admin_ep.wikisi.md`) |
| Sécurité des communications | HTTPS obligatoire (TLS 1.2+) |

### 7.4. Points de vigilance

* Migration prévue vers **Tomcat 10** et **PostgreSQL 15** : vérifier la compatibilité du driver JDBC et la migration des `web.xml` (namespace `jakarta.servlet`).  
* Conteneurisation en cours : Dockerfile disponible dans le répertoire `docker/` (non inclus dans ce résumé).  

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

---

## 8. Annexes ↩ [Retour au sommaire](#admin_ep‑documentation‑technique)

### 8.1. Liste exhaustive des fichiers (extrait)

| Chemin relatif | Taille | Type |
|----------------|--------|------|
| `.gitignore` | 24 octets | texte |
| `adminep-database/assembly.xml` | 627 octets | XML |
| `adminep-database/pom.xml` | 1 538 octets | XML |
| `adminep-database/scripts/init/0_createUserAndDB.sql` | 261 octets | SQL |
| `adminep-database/scripts/init/1_createSequenceAndTablesIntegration.sql` | 7 651 octets | SQL |
| `adminep-database/scripts/init/2_populateTablesIntegration.sql` | 138 797 octets | SQL |
| `adminep-web/src/main/java/fr/gouv/e2/baseadmin/controller/admins/DetailAdminAction.java` | 7 450 octets | Java |
| `adminep-web/src/main/resources/boot/config/application-config.xml` | 482 octets | XML |
| `adminep-web/src/main/webapp/WEB-INF/jsp/admins/detailAdmin.jsp` | 16 620 octets | JSP |
| `adminep-web/src/main/webapp/static/css/bootstrap.css` | 127 343 octets | CSS |
| … (les 275 fichiers sont listés dans le fichier source) | | |

### 8.2. Références externes

* **JORF – OpenData** : <https://echanges.dila.gouv.fr/OPENDATA/JORF/>  
* **Bulletin officiel – RSS** : <https://www.bulletin-officiel.developpement-durable.gouv.fr/rss>  

### 8.3. Glossaire

| Terme | Définition |
|-------|------------|
| **Mandat** | Période durant laquelle un administrateur exerce ses fonctions. |
| **Gestionnaire** | Personne responsable de la gestion administrative d’un établissement. |
| **College** | Instance de décision (ex. Conseil d’administration). |
| **Charge** | Ministère ou service chargé d’un domaine (ex. « Affaires étrangères »). |
| **Cerbère** | Système d’authentification unique (SSO) interne au ministère. |

↩ [Retour au sommaire](#admin_ep‑documentation‑technique)