# admin_ep – Documentation technique

[TOC]

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 📖 1. Présentation du projet <a id="presentation-du-projet"></a>

**Nom** : *admin_ep* (Administration des établissements publics)  
**Objectif** : Gestion centralisée des membres des conseils d’administration des établissements publics placés sous la tutelle du ministère de la Transition écologique et solidaire (MTES‑MCT).  
**Fonctionnalités principales**  

| Fonction | Description |
|---|---|
| **Interface d'écriture** | Saisie manuelle des administrateurs et de leurs mandats. |
| **Alimentation automatique** | Extraction des données depuis le JORF (Journal officiel) à l’aide d’un analyseur dédié. |
| **Authentification** | Gestion des droits via le SSO Cerbère. |
| **Archivage** | Historisation des mandats et des pièces jointes. |
| **Lecture** | Consultation des données via une interface web. |
| **Statistiques** | Tableau de bord et indicateurs globaux. |
| **Alertes** | Notification par e‑mail des mandats proches de l’échéance. |
| **Recherche** | Moteur de recherche complet (établissements, personnes, mandats). |

**Environnement**  

| Élément | Version / Type |
|---|---|
| **Java** | 8 (OpenJDK) |
| **Serveur d’applications** | Tomcat 9.0.8 (en cours de migration vers Tomcat 10) |
| **Base de données** | PostgreSQL 9.6.11 (prévu PostgreSQL 15) |
| **Infrastructure** | Hébergement ministériel LDF – plateforme ACAI / IaaS (ECO4) |
| **Build** | Maven 3.x (multi‑module) |

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 🏗️ 2. Architecture générale <a id="architecture-generale"></a>

```mermaid
graph TD;
    subgraph Frontend;
        UI[Interface Web (JSP/Struts2)] -->|HTTPS| SecFilter[SecurityFilter]
    end;
    subgraph Backend;
        Controllers[Contrôleurs (Struts2 actions)] --> Services[Services métier]
        Services --> DAO[DAO (JPA/Hibernate)]
        DAO --> DB[(PostgreSQL)]
        Controllers --> Util[Utilitaires (StringUtil, OdsUtil, …)]
        Controllers --> Sec[Security (Roles, RightsHelper)]
    end;
    subgraph Integration;
        JORF[Extractor JORF] --> Analyzer[ArticleAnalyser]
        Analyzer --> DAO;
    end;
    subgraph Infrastructure;
        Tomcat[Tomcat] --> Frontend;
        Tomcat --> Backend;
        Tomcat --> Integration;
        DB --> Tomcat;
    end
```

*Légende*  

- **UI** : JSP + Struts tags.  
- **SecFilter** : filtre servlet qui applique la sécurité Cerbère.  
- **Controllers** : actions Struts2 (ex. `AccueilAction`, `DetailAdminAction`).  
- **Services** : couche métier (ex. `AdministrateurServices`, `ChargeServices`).  
- **DAO** : accès persistant via JPA (`EntityManager`).  
- **Integration** : processus d’ingestion JORF (ex. `JORFExtractor`, `ArticleAnalyser`).  

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 📂 3. Arborescence du dépôt <a id="arborescence-du-depot"></a>

```
admin_ep/
├─ .gitignore
├─ pom.xml                                 ← pom parent
├─ adminep-database/
│   ├─ assembly.xml
│   ├─ pom.xml
│   └─ scripts/
│       ├─ init/
│       │   ├─ 0_createUserAndDB.sql
│       │   ├─ 1_createSequenceAndTablesIntegration.sql
│       │   ├─ 2_populateTablesIntegration.sql
│       │   ├─ 3_createTablesExtraction.sql
│       │   └─ 4_createTablesBaseAdmin.sql
│       └─ update/
│           └─ … (scripts de migration)
├─ adminep-deployment/
│   ├─ conf/
│   │   └─ adminep.xml
│   ├─ assembly-sources.xml
│   ├─ assembly-zip.xml
│   └─ pom.xml
├─ adminep-doc/
│   ├─ assembly.xml
│   └─ pom.xml
├─ adminep-web/
│   ├─ src/
│   │   └─ main/
│   │       ├─ java/
│   │       │   └─ fr/gouv/e2/baseadmin/
│   │       │       ├─ boot/… (initialisation)
│   │       │       ├─ controller/
│   │       │       │   ├─ accueil/AccueilAction.java
│   │       │       │   ├─ admins/… (Detail, Recherche, Upsert)
│   │       │       │   ├─ etablissements/… (Detail, Recherche, Upsert)
│   │       │       │   ├─ mandats/… (Detail, Upsert)
│   │       │       │   └─ … (footer, gestionnaires, …)
│   │       │       ├─ model/… (enums, référentiels)
│   │       │       ├─ security/… (Roles, RightsHelper)
│   │       │       ├─ services/… (article, baseadmin, integration, …)
│   │       │       └─ util/… (ArticleAnalyser, JORFExtractor, StringUtil)
│   │       ├─ resources/
│   │       │   ├─ boot/… (components, config)
│   │       │   ├─ definitions/… (ksp files)
│   │       │   ├─ mda/… (configuration MDA)
│   │       │   ├─ template/baseadmin/… (FTL templates)
│   │       │   ├─ displaytag.properties
│   │       │   ├─ log4j2.xml
│   │       │   ├─ struts.xml
│   │       │   └─ version.properties
│   │       └─ webapp/
│   │           ├─ META-INF/context.xml
│   │           ├─ WEB-INF/
│   │           │   ├─ jsp/… (pages JSP)
│   │           │   ├─ applicationContext.xml
│   │           │   ├─ cerbere-filtre.xml
│   │           │   └─ web.xml
│   │           └─ static/… (CSS, JS, wiki)
│   ├─ pom.xml
│   └─ .gitignore
└─ search/
    ├─ .gitignore
    └─ README.md
```

> **Note** : chaque sous‑module possède son propre `pom.xml` et peut être construit indépendamment.

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 🗄️ 4. Modèle de données <a id="modele-de-donnees"></a>

### 4.1. Tables principales (extraits)

| Table | Description | Clé primaire | Principales colonnes |
|---|---|---|---|
| **TYPE_MANDAT** | Types de mandat (Titulaire / Suppléant) | `TMA_ID` | `TMA_TYPE` |
| **TYPE_INSTANCE** | Types d’instance (Conseil d’administration, Conseil de surveillance) | `TIN_ID` | `TIN_TYPE`, `TIN_A_LINSTANCE_DE`, `TIN_DE_LINSTANCE_DE` |
| **MODE_NOMINATION** | Modes de nomination (Arrêté, Décret, Décret du Président) | `MNO_ID` | `MNO_CODE`, `MNO_MODE`, `MNO_MOT_CLE_TITRE`, `MNO_MOT_CLE_CORPS_TEXTE` |
| **CHARGE** | Charges ministérielles (ex. « Affaires étrangères ») | `CHA_ID` | `CHA_CHARGE`, `CHA_MINISTERE_CHARGE_DE`, … |
| **CIVILITE** | Civilités (M., Mme, Dr…) | `CIV_ID` | `CIV_CODE`, `CIV_INTITULE`, `CIV_TITRE` |
| **MINISTERE** | Ministères (sigle, nom, statut) | `MIN_ID` | `MIN_SIGLE`, `MIN_NOM`, `MIN_STATUT` |
| **COLLEGE** | Collèges (identifiant) | `COL_ID` | `COL_IDENTIFIANT` |
| **ETABLISSEMENT** | Établissements publics (SIREN, libellé…) | `ETA_ID` | `ETA_SIREN`, `ETA_SIGLE`, `ETA_LIBELLE`, `TIN_ID_FK` |
| **SYNONYME_COLLEGE** | Synonymes de collèges | `COL_ID_FK` + `SYN_SYNONYME` | `SYN_DEFAUT` |
| **MINISTERE_CHARGE** | Relation charge ↔ ministère | (`CHA_ID_FK`, `MIN_ID_FK`) | – |
| **ETABLISSEMENT_COLLEGE** | Liaison établissement ↔ collège (nombre membres, durée) | (`ETA_ID_FK`, `COL_ID_FK`) | `ETC_NOMBRE_MEMBRES`, `ETC_DUREE_MANDAT` |
| **TUTELLE_ETABLISSEMENT_CHARGE** | Tutelle d’un établissement par une charge | (`ETA_ID_FK`, `CHA_ID_FK`) | `TUT_TUTELLE_PRINCIPALE` |
| **DIRECTION** | Directions (sigle, intitulé) | `DIR_ID` | `DIR_SIGLE`, `DIR_INTITULE` |
| **DIRECTION_MINISTERE** | Relation direction ↔ ministère | (`DIR_ID_FK`, `MIN_ID_FK`) | – |

### 4.2. Diagramme ER simplifié

```mermaid
erDiagram;
    TYPE_MANDAT ||--|| TYPE_INSTANCE : « type »
    TYPE_INSTANCE ||--o{ ETABLISSEMENT : « instance »
    ETABLISSEMENT ||--o{ ETABLISSEMENT_COLLEGE : « lieu »
    COLLEGE ||--o{ ETABLISSEMENT_COLLEGE : « collège »
    COLLEGE ||--o{ SYNONYME_COLLEGE : « synonyme »
    CHARGE ||--o{ MINISTERE_CHARGE : « charge‑ministere »
    MINISTERE ||--o{ MINISTERE_CHARGE : « charge »
    CHARGE ||--o{ TUTELLE_ETABLISSEMENT_CHARGE : « tutelle »
    ETABLISSEMENT ||--o{ TUTELLE_ETABLISSEMENT_CHARGE : « tutelle »
    DIRECTION ||--o{ DIRECTION_MINISTERE : « direction‑ministere »
    MINISTERE ||--o{ DIRECTION_MINISTERE : « direction »
```

> Le schéma complet (avec contraintes FK, index et séquences) se trouve dans les scripts `1_createSequenceAndTablesIntegration.sql` et `2_populateTablesIntegration.sql`.

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 🧩 5. Modules applicatifs <a id="modules-applicatifs"></a>

| Module | Package racine | Principaux packages | Fonction |
|---|---|---|---|
| **Boot** | `fr.gouv.e2.baseadmin.boot` | `I18nResourcesInitializer`, `MasterDataInitializer`, `SchedulerInitializer`, `SecurityManagerInitializer` | Initialisation du contexte Spring/Vertigo, planification des tâches. |
| **Controller** | `fr.gouv.e2.baseadmin.controller` | `accueil`, `admins`, `etablissements`, `mandats`, `gestionnaires`, `footer`, `navigation`, `session`, `statistiques`, `supervision`, `utilisateurs` | Actions Struts2 (ex. `DetailAdminAction`, `RechercheEPAction`). |
| **Model** | `fr.gouv.e2.baseadmin.model` | `referentiel`, `utilisateur`, `wiki` | Enums et objets métiers (ex. `CodeEnum`, `RoleApplicatifEnum`). |
| **Security** | `fr.gouv.e2.baseadmin.security` | `BaseAdminUserSession`, `OperationSecurite`, `RightsHelper`, `Roles`, `SecurityHelper` | Gestion des droits Cerbère. |
| **Services** | `fr.gouv.e2.baseadmin.services` | `article`, `baseadmin`, `integration`, `jorfCharges` | Logique métier et DAO (ex. `AdministrateurServices`, `ChargeServices`). |
| **Util** | `fr.gouv.e2.baseadmin.util` | `articleanalyser`, `jorf`, `CerbereUtil`, `MandatsResolver`, `NomPrenomUtil`, `OdsUtil`, `SQLConstantes`, `StringUtil` | Outils de traitement (ex. extraction JORF, génération ODS). |
| **Decorator** | `fr.gouv.e2.baseadmin.decorator.actif` | `ActifDecorator` | Décorateur de présentation. |
| **Dynamo‑search** | `fr.gouv.e2.baseadmin.dynamo.search` | `ReindexArticlesByArtiIDTask` | Re‑indexation des articles dans Elasticsearch. |
| **Errorhandler** | `fr.gouv.e2.baseadmin.errorhandler` | `ErrorHandler` | Gestion centralisée des erreurs. |
| **Webapp** | `src/main/webapp` | `WEB-INF/jsp/**`, `static/**` | Pages JSP, ressources CSS/JS, wiki statique. |
| **Resources** | `src/main/resources` | `boot/**`, `definitions/**`, `mda/**`, `template/baseadmin/**` | Configurations Spring, définitions Vertigo, templates Freemarker. |

### 5.1. Exemple de classe : `DetailAdminAction`

```java
public class DetailAdminAction extends AbstractBaseAdminActionSupport {
    private Long adminId;
    private AdminDto admin;

    public String execute() {
        admin = adminService.findById(adminId);
        return SUCCESS;
    }

    // getters / setters
}
```

*Cette action récupère les données d’un administrateur via le service `AdministrateurServices` et les expose à la JSP `detailAdmin.jsp`.*

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 🚀 6. Build, packaging & déploiement <a id="build-deploiement"></a>

### 6.1. Structure Maven

```mermaid
graph TD;
    parent[pom.xml (parent)] --> db[adminep-database]
    parent --> dep[adminep-deployment]
    parent --> doc[adminep-doc]
    parent --> web[adminep-web]
    db --> db_assembly[assembly.xml (SQL zip)]
    web --> web_resources[resources/*]
    web --> web_war[war packaging]
```

- **`adminep-database`** : module *pom* (type `pom`) qui ne produit pas d’artifact mais regroupe les scripts SQL.  
- **`adminep-deployment`** : module de packaging *assembly* (ZIP) contenant les scripts de déploiement et les fichiers de configuration.  
- **`adminep-doc`** : module de documentation (assembly).  
- **`adminep-web`** : module principal, packaging `war`.  

### 6.2. Commandes courantes

| Action | Commande Maven |
|---|---|
| **Compile** | `mvn clean compile` |
| **Package (war + zip)** | `mvn clean package` |
| **Construire uniquement les scripts SQL** | `mvn -pl adminep-database package` |
| **Lancer les tests unitaires** | `mvn test` |
| **Déployer le WAR sur Tomcat** | Copier `adminep-web/target/adminep-web.war` dans `$CATALINA_HOME/webapps/` et redémarrer Tomcat. |

### 6.3. Fichiers de configuration clés

| Fichier | Rôle |
|---|---|
| `adminep-deployment/conf/adminep.xml` | Paramètres d’environnement (JNDI, datasource). |
| `adminep-web/src/main/resources/boot/config/application-config.xml` | Configuration Spring Vertigo (services, DAO). |
| `adminep-web/src/main/resources/boot/config/baseadmin-auth-config.xml` | Mapping des rôles Cerbère. |
| `adminep-web/src/main/webapp/WEB-INF/web.xml` | Déclaration du `SecurityFilter`, des servlets Struts2. |
| `adminep-web/src/main/resources/log4j2.xml` | Logging (appenders, niveaux). |
| `adminep-web/src/main/resources/struts.xml` | Mapping des actions Struts2. |

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 🔐 7. Sécurité & authentification <a id="securite-authentification"></a>

- **SSO Cerbère** : l’application s’appuie sur le filtre `SecurityFilter` (package `io.vertigo.vega.impl.servlet.filter`) qui interroge le serveur d’authentification Cerbère.  
- **Roles** : définis dans `fr.gouv.e2.baseadmin.security.Roles` (ex. `ADMIN`, `GESTIONNAIRE`, `CONSULTANT`).  
- **RightsHelper** : vérifie les droits sur chaque action (ex. `RightsHelper.checkAccess("ADMIN")`).  
- **Session** : encapsulée par `BaseAdminUserSession`, stockée dans la session HTTP.  

> **Bonnes pratiques**  
  - Ne jamais stocker de mots de passe en clair dans les fichiers de configuration.  
  - Activer le logging de sécurité (`log4j2.xml` → logger `security`).  
  - Mettre à jour le certificat TLS du serveur Cerbère lors de chaque renouvellement.

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 📈 8. Exploitation & supervision <a id="exploitation-supervision"></a>

| Aspect | Méthode |
|---|---|
| **Logs applicatifs** | `log4j2.xml` → fichiers sous `$CATALINA_HOME/logs/` (`admin_ep.log`). |
| **Statistiques** | Action `StatistiquesAction` → tableau de bord accessible depuis `/statistiques`. |
| **Alertes mandats** | Job planifié (`SchedulerInitializer`) qui exécute `MandatsResolver` et envoie des e‑mails via le service `MailService`. |
| **Supervision Tomcat** | JMX (`JMX` → monitoring via `JConsole` ou `Prometheus JMX exporter`). |
| **Healthcheck** | URL `http://<host>/admin_ep/health` (définie dans `web.xml` via servlet `HealthCheckServlet`). |
| **Sauvegarde DB** | Dump PostgreSQL quotidien (`pg_dump`) et archivage des scripts SQL (`adminep-database/assembly.xml`). |

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 📚 9. Références & documentation associée <a id="references-documentation"></a>

| Source | Type | Lien |
|---|---|---|
| **Wiki interne** | Documentation fonctionnelle | `static/wiki/` (ex. `detail_admin.html`, `cre_mod_ep.html`). |
| **JIRA / Support** | Suivi des tickets | <https://portail-support.din.developpement-durable.gouv.fr/projects/admin-ep> |
| **JORF** | Source de données officielle | <https://echanges.dila.gouv.fr/OPENDATA/JORF/> |
| **Guide d’installation** | README du projet | `adminep-doc/assembly.xml` (contenu PDF). |
| **Manuel d’administration** | PDF interne | `adminep-web/src/main/resources/boot/config/baseadmin-auth-config.xml`. |

↩ [Retour au sommaire](#admin_ep-technical-documentation)

---

## 📌 10. Historique des versions <a id="historique-versions"></a>

| Version | Date | Modifications majeures |
|---|---|---|
| **1.3.3** | 12/2021 | Migration vers PostgreSQL 15 (en cours), conteneurisation Docker, mise à jour Tomcat 10. |
| **1.2.5** | 05/2020 | Refactorisation du module JORF, ajout du moteur de recherche Elastic. |
| **1.2.2** | 14/02/2019 | Introduction du framework Vertigo, amélioration des droits Cerbère. |

*Les versions précédentes (pré‑prod, recette) sont archivées dans le dépôt sous les tags Git.*

↩ [Retour au sommaire](#admin_ep-technical-documentation)

--- 

*Document généré le 27 avril 2026 – © Direction Générale du Ministère de la Transition écologique et solidaire*