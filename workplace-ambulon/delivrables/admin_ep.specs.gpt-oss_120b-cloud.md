# Spécification fonctionnelle et technique de l’application **admin_ep**  

*Document auto‑porté – compatible avec VS Code / Obsidian (PlantUML activé). Aucun lien externe requis, à l’exception du lien vers la documentation officielle d’arc42.*  

---  

## 📖 Table des matières  

| # | Section | Lien |
|---|---------|------|
| 1 | Introduction – portée, domaine et contexte | [↩](#introduction---portée-domaine-et-contexte) |
| 2 | Glossaire | [↩](#glossaire) |
| 3 | Spécification fonctionnelle | [↩](#spécification-fonctionnelle) |
| 3.1 | Acteurs | [↩](#acteurs) |
| 3.2 | Cas d’usage (use‑case) | [↩](#cas-dusage) |
| 3.3 | Règles métier (tableaux de décision) | [↩](#règles-métier) |
| 3.4 | Workflows critiques (diagrammes swimlane) | [↩](#workflows-critiques) |
| 3.5 | Scénarii détaillés | [↩](#scénarii-détaillés) |
| 4 | Spécification technique | [↩](#spécification-technique) |
| 4.1 | Architecture logique (diagramme composants) | [↩](#architecture-logique) |
| 4.2 | Architecture physique (diagramme déploiement) | [↩](#architecture-physique) |
| 4.3 | Modules / packages Java | [↩](#modules--packages) |
| 4.4 | Modèle de données (schéma relationnel simplifié) | [↩](#modèle-de-données) |
| 4.5 | Flux de données (diagramme séquence) | [↩](#flux-de-données) |
| 4.6 | Analyse de sécurité | [↩](#analyse-de-sécurité) |
| 4.7 | Dette technique identifiée | [↩](#dette-technique) |
| 5 | Qualité documentaire (conformité arc42 & ISO/IEC/IEEE 29148) | [↩](#qualité-documentaire) |
| 6 | Références | [↩](#références) |

---  

## 1️⃣ Introduction – portée, domaine et contexte <a id="introduction---portée-domaine-et-contexte"></a>  

| Élément | Description |
|---------|-------------|
| **Nom de l’application** | `admin_ep` (Administration des établissements publics) |
| **Domaine applicatif** | **Archivage physique** des mandats, pièces justificatives et métadonnées associées aux établissements publics du Ministère de la Transition Écologique (MTES‑MCT). |
| **Contexte opérationnel** | Site : **SIT_ID = 29** – serveur de production du ministère.<br>Base de données : **Oracle prep37** (déploiement Oracle 9.6 / PostgreSQL 9.6 en phase de migration). |
| **Périmètre fonctionnel** (extrait du wiki `admin_ep.wikisi.md`) | • Gestion des **versements** (saisie manuelle d’un mandat).<br>• Gestion des **demandes** (création/modification de dossiers).<br>• Gestion des **mouvements** (suivi des changements de mandat, archivage des pièces). |
| **Exclusions** | • Gestion des patients, facturation, workflow avancé (ex. BPMN complet).<br>• Traitement de données hors‑mandats (ex. statistiques RH non‑mandataires). |

> **Source** : informations issues de `admin_ep.wikisi.md` (section *Description* et *Domaines métier*) et du fichier `home › Fiche‑Produit.md` (section *Périmètre fonctionnel*).  

---  

## 2️⃣ Glossaire <a id="glossaire"></a>  

| Terme | Définition |
|-------|------------|
| **Mandat** | Période pendant laquelle un administrateur (titulaire ou suppléant) exerce ses fonctions au sein d’un conseil d’administration. |
| **TUTELLE** | Relation entre un établissement public et une ou plusieurs **charges** (ministères) qui assurent le suivi administratif. |
| **Charge** | Unité ministérielle (ex. « Affaires étrangères ») qui porte la responsabilité de la tutelle. |
| **CERBERE** | Système d’authentification unique du ministère (profil = 619). |
| **ACA I** | Plateforme d’hébergement (clusters ESXi) utilisée en production. |
| **ARC42** | Méthodologie de documentation d’architecture logicielle. |
| **ISO/IEC/IEEE 29148** | Norme de spécifications fonctionnelles et techniques. |
| **Swimlane** | Diagramme d’activité où chaque « couloir » représente un acteur ou une couche technique. |
| **Decision Table** | Tableau de règles conditionnelles (ex. formatage de dates). |

---  

## 3️⃣ Spécification fonctionnelle <a id="spécification-fonctionnelle"></a>  

### 3.1️⃣ Acteurs <a id="acteurs"></a>  

| Acteur | Rôle | Référence (code) |
|--------|------|-------------------|
| **Administrateur métier (MA)** | Saisie et mise à jour des mandats via l’interface web. | `DetailAdminAction.java`<br>`UpsertAdminAction.java` |
| **Gestionnaire de tutelle** | Associe les établissements aux charges, valide les pièces. | `UpsertGestionnairesAction.java` |
| **Opérateur de supervision** | Consulte les historiques, déclenche les alertes d’échéance. | `SupervisionAction.java` |
| **Utilisateur Cerbère** | Authentifie l’accès (profil = 619). | `SecurityManagerInitializer.java` |
| **Service JORF** (automatisé) | Récupère les textes officiels et alimente la base. | `ArticleAnalyser.java` (module *articleanalyser*) |
| **Scheduler** | Planifie l’envoi des mails d’avertissement. | `SchedulerInitializer.java` |

> Les classes Java correspondantes sont accessibles via les ancres suivantes :  
> *Administrateur* → [`DetailAdminAction`](#tree-adminep-web-src-main-java-fr-gouv-e2-baseadmin-controller-admins-DetailAdminAction-java) – [`UpsertAdminAction`](#tree-adminep-web-src-main-java-fr-gouv-e2-baseadmin-controller-admins-UpsertAdminAction-java)  
> *Gestionnaire* → [`UpsertGestionnairesAction`](#tree-adminep-web-src-main-java-fr-gouv-e2-baseadmin-controller-gestionnaires-UpsertGestionnairesAction-java)  
> *Supervision* → [`SupervisionAction`](#tree-adminep-web-src-main-java-fr-gouv-e2-baseadmin-controller-supervision-SupervisionAction-java)  

---

### 3.2️⃣ Cas d’usage (Use‑Case) <a id="cas-dusage"></a>  

```plantuml
@startuml
left to right direction
actor "Administrateur métier" as AM
actor "Gestionnaire tutelle" as GT
actor "Opérateur supervision" as OS
actor "Service JORF (batch)" as JORF

rectangle admin_ep {
  usecase "UC‑01 Créer/Mettre à jour un mandat" as UC01
  usecase "UC‑02 Rechercher un établissement" as UC02
  usecase "UC‑03 Signaler échéance mandat" as UC03
  usecase "UC‑04 Import JORF automatisé" as UC04
  usecase "UC‑05 Export PDF / Archive" as UC05
}

AM --> UC01
AM --> UC02
GT --> UC02
GT --> UC05
OS --> UC03
JORF --> UC04
@enduml
```

*Explication* : chaque cas d’usage est implémenté par un **Action** Struts 2 (ex. `UpsertAdminAction` ↔ UC‑01, `RechercheEPAction` ↔ UC‑02).  

---  

### 3.3️⃣ Règles métier (tableaux de décision) <a id="règles-métier"></a>  

#### 3.3.1 Formatage des dates de mandat  

| Condition (type de mandat) | Format attendu | Exemple |
|----------------------------|----------------|---------|
| **Titulaire** | `dd/MM/yyyy` | `15/04/2023` |
| **Suppléant** | `dd/MM/yyyy` | `01/01/2024` |
| **Date d’échéance** | `dd/MM/yyyy` (calcul = date début + durée) | `15/04/2025` |

> Implémentation dans `FormatterDateRange.java` : `@startuml` → [FormatterDateRange.java](#tree-adminep-web-src-main-java-io-vertigo-dynamox-domain-formatter-FormatterDateRange-java)  

#### 3.3.2 Détermination du chargeur de tutelle  

| Charge | Ministère associé (exemple) | Validation (bool) |
|--------|----------------------------|-------------------|
| `Affaires étrangères` | `Ministère chargé des affaires étrangères` | true |
| `Agriculture` | `Ministère chargé de l’agriculture` | true |
| `…` | … | … |

> La règle est appliquée lors de l’insertion dans la table **TUTELLE_ETABLISSEMENT_CHARGE** (voir `tutelle_etablissement_chargeDao.ksp`).  

---  

### 3.4️⃣ Workflows critiques (diagrammes *swimlane*) <a id="workflows-critiques"></a>  

#### 3.4.1 Création / mise à jour d’un mandat  

```plantuml
@startuml
|Administrateur|
start
:Ouvre l’écran “UpsertAdmin”;
:Remplit les champs (nom, prénom, type, dates);
|Security|
:Vérifie le profil Cerbère (ID = 619);
|Business|
:Appelle `MandatServices.upsertMandat`;
|DAO|
:Persist en base (TABLE MANDAT);
|Scheduler|
:Planifie alerte 30 jours avant échéance;
stop
@enduml
```

> Les classes appelées sont : `MandatServicesImpl.java` → `MandatServices.java` (cf. `adminep-web/src/main/java/.../services/baseadmin/mandat/`).  

#### 3.4.2 Import automatisé JORF  

```plantuml
@startuml
|Batch|
start
:Scheduler déclenche `ArticleAnalyser`;
:Charge les articles JORF (via `JORFExtractor`);
:Parse le texte (`ArticleAnalyser` → `StepAnalyse…`);
:Identifie mandats, établissements, dates;
|DAO|
:Enrichit les tables `CHARGE`, `ETABLISSEMENT`, `MANDAT`;
|Notifier|
:Envoie mail de résumé au gestionnaire;
stop
@enduml
```

> Implémentation principale : `ArticleAnalyser.java` + étapes dans le package `util.articleanalyser.step`.  

---  

### 3.5️⃣ Scénarii détaillés (exemples) <a id="scénarii-détaillés"></a>  

| Scénario | Description | Étapes clés | Résultat attendu |
|----------|-------------|-------------|------------------|
| **S‑01** – Création d’un mandat **Titulaire** | Un administrateur saisit un nouveau mandat titulaire pour l’établissement « Etablissement X ». | 1. Authentification Cerbère (profil 619).<br>2. Navigation → *Accueil* → *Gestion → Mandats*.<br>3. Ouverture du formulaire `UpsertMandat.jsp`.<br>4. Saisie du type « Titulaire », date début, durée 5 ans.<br>5. Validation → appel `MandatServices.upsertMandat`.<br>6. Confirmation UI (`actionmessage.ftl`). | Le mandat est persistant (`MANDAT`), la date d’échéance calculée, l’alerte d’échéance planifiée. |
| **S‑02** – Recherche d’un établissement | Un gestionnaire veut retrouver tous les mandats d’un établissement donné. | 1. Authentification.<br>2. Accès à *Recherche EP* (`RechercheEPAction`).<br>3. Saisie du SIREN ou d’un synonyme.<br>4. Le service `EtablissementServices.search` interroge les tables `ETABLISSEMENT` + `SYNONYME_COLLEGE`.<br>5. Affichage du tableau de résultats (`listeGestionnaires.jsp`). | Liste des établissements et leurs mandats, avec liens vers les pages de détail (`DetailEPAction`). |
| **S‑03** – Alerte d’échéance | Le scheduler détecte un mandat qui expire dans < 30 jours. | 1. `SchedulerInitializer` invoque `MandatServices.checkEcheances` chaque nuit.<br>2. Recherche des mandats où `date_fin - sysdate <= 30`.<br>3. Envoi d’un mail via `MailService` (non‑décrit dans le code mais référencé dans les propriétés).<br>4. Historisation dans `STATISTIQUES`. | L’opérateur de supervision reçoit un courriel, le tableau de bord affiche la notification. |
| **S‑04** – Import JORF (batch) | Le job quotidien de récupération JORF alimente la base. | 1. `Scheduler` lance `ArticleAnalyser` à 02 h00.<br>2. `JORFExtractor` télécharge le fichier `.tar.gz` depuis le flux RSS (voir `doc‑JORF‑BO.md`).<br>3. Les étapes `StepAnalyse…` extraient les mentions de mandats.<br>4. Les services `MandatServicesImpl` persiste les nouveaux enregistrements.<br>5. Log d’exécution (`log4j2.xml`). | Les nouveaux mandats sont disponibles dans l’interface, aucune duplication grâce aux contrôles d’unicité (`mandatDao.ksp`). |

---  

## 4️⃣ Spécification technique <a id="spécification-technique"></a>  

### 4.1️⃣ Architecture logique (diagramme de composants) <a id="architecture-logique"></a>  

```plantuml
@startuml
package "Web Layer" {
  [Struts2 Action] as Action
  [JSP Views] as View
}
package "Business Layer" {
  [MandatServices] as MS
  [EtablissementServices] as ES
  [ChargeServices] as CS
  [ArticleAnalyser] as AA
}
package "Data Access Layer" {
  [MandatDao] as MD
  [EtablissementDao] as ED
  [ChargeDao] as CD
  [JORFChargesDao] as JD
}
package "Infrastructure" {
  [Oracle / PostgreSQL] as DB
  [Mail Server] as Mail
  [Scheduler (Quartz)] as Scheduler
}
Action --> MS : upsertMandat()
Action --> ES : rechercheEtablissement()
Action --> CS : rechercheCharge()
MS --> MD
ES --> ED
CS --> CD
AA --> JD
MD --> DB
ED --> DB
CD --> DB
JD --> DB
Scheduler --> AA : execute()
Scheduler --> MS : checkEcheances()
@enduml
```

*Notes* :  
* Les **actions** Struts2 (`*Action.java`) constituent le point d’entrée HTTP.  
* Les **services** implémentent la logique métier (ex. `MandatServicesImpl`).  
* Les **DAOs** sont générés par Vertigo/KSP (fichiers *.ksp* dans `resources/boot/definitions`).  
* La **base** Oracle prep37 (ou PostgreSQL 9.6) stocke les tables décrites dans les scripts d’init.  

---  

### 4.2️⃣ Architecture physique (diagramme de déploiement) <a id="architecture-physique"></a>  

```plantuml
@startuml
node "Serveur d’application (Tomcat 9.0.8 – ACAI)" as Tomcat {
  artifact "admin_ep.war" {
    component "Web UI (JSP/Struts2)" as UI
    component "Business Services (Spring)" as BS
  }
}
node "Base de données (Oracle prep37)" as Oracle {
  database "Schema integration" as Schema
}
node "Scheduler (Quartz)" as Quartz {
  component "Job ArticleAnalyser"
}
node "Mail Gateway" as Mail {
  [SMTP]
}
Tomcat --> UI : HTTP/HTTPS
Tomcat --> BS : Spring DI
BS --> Schema : JDBC
Quartz --> BS : API (MandatServices)
Quartz --> Mail : SMTP
@enduml
```

*Le serveur d’application est hébergé sur le **centre‑serveur ministériel Paris La Défense** (Production – ACAI). Le déploiement se fait via le fichier `adminep.xml` (déploiement Maven).*

---  

### 4.3️⃣ Modules / packages Java <a id="modules--packages"></a>  

| Package | Contenu principal | Exemple de classe |
|---------|-------------------|--------------------|
| `fr.gouv.e2.baseadmin.boot` | Initialisation du framework (I18n, Scheduler, Security) | `SecurityManagerInitializer.java` |
| `fr.gouv.e2.baseadmin.controller` | Struts2 actions (MVC) | `DetailAdminAction.java`, `RechercheEPAction.java` |
| `fr.gouv.e2.baseadmin.decorator.actif` | Décorateurs UI (actif/inactif) | `ActifDecorator.java` |
| `fr.gouv.e2.baseadmin.dynamo.search` | Tâches asynchrones (re‑index) | `ReindexArticlesByArtiIDTask.java` |
| `fr.gouv.e2.baseadmin.errorhandler` | Gestion centralisée des erreurs | `ErrorHandler.java` |
| `fr.gouv.e2.baseadmin.model` | Enum et POJO métier | `CodeEnum.java`, `RoleApplicatifEnum.java` |
| `fr.gouv.e2.baseadmin.orchestra` | Traitement JORF (extraction, parsing) | `TraitementRecuperationJORF.java` |
| `fr.gouv.e2.baseadmin.security` | Gestion des sessions et droits | `BaseAdminUserSession.java`, `RightsHelper.java` |
| `fr.gouv.e2.baseadmin.services` | Interfaces métier (service) | `MandatServices.java`, `ArticleServices.java` |
| `fr.gouv.e2.baseadmin.util` | Helpers génériques (String, ODS, JORF) | `StringUtil.java`, `OdsUtil.java` |
| `io.vertigo.struts2.core` | Classes utilitaires Vertigo | `AbstractUiListUnmodifiable.java` |
| `org.displaytag.render` | Writers HTML pour les tables | `HtmlTableWriter.java` |

---  

### 4.4️⃣ Modèle de données (schéma relationnel simplifié) <a id="modèle-de-données"></a>  

```plantuml
@startuml
entity TYPE_MANDAT {
  * TMA_ID : PK
  * TMA_TYPE
}
entity TYPE_INSTANCE {
  * TIN_ID : PK
  * TIN_TYPE
  * TIN_A_LINSTANCE_DE
  * TIN_DE_LINSTANCE_DE
}
entity CHARGE {
  * CHA_ID : PK
  * CHA_CHARGE
  * CHA_MINISTERE_CHARGE_DE
}
entity MINISTERE {
  * MIN_ID : PK
  * MIN_SIGLE
  * MIN_NOM
}
entity COLLEGE {
  * COL_ID : PK
  * COL_IDENTIFIANT
}
entity ETABLISSEMENT {
  * ETA_ID : PK
  * ETA_SIREN
  * ETA_LIBELLE
  * TIN_ID_FK : FK → TYPE_INSTANCE
}
entity MANDAT {
  * MAN_ID : PK
  * MAN_TYPE_FK : FK → TYPE_MANDAT
  * MAN_TITULAIRE_ID : FK → ADMIN (non montré)
  * MAN_DEBUT : DATE
  * MAN_FIN : DATE
  * ETA_ID_FK : FK → ETABLISSEMENT
}
entity TUTELLE_ETABLISSEMENT_CHARGE {
  * ETA_ID_FK : FK → ETABLISSEMENT
  * CHA_ID_FK : FK → CHARGE
  * TUT_TUTELLE_PRINCIPALE : BOOLEAN
}
TYPE_MANDAT ||--o{ MANDAT : "type"
TYPE_INSTANCE ||--o{ ETABLISSEMENT : "instance"
CHARGE ||--o{ TUTELLE_ETABLISSEMENT_CHARGE : "charge"
ETABLISSEMENT ||--o{ MANDAT : "mandats"
ETABLISSEMENT ||--o{ TUTELLE_ETABLISSEMENT_CHARGE : "tutelle"
@enduml
```

*Le script d’initialisation `1_createSequenceAndTablesIntegration.sql` crée ces tables ; les *DAOs* sont générés à partir des fichiers `*.ksp` (ex. `mandatDao.ksp`).*  

---  

### 4.5️⃣ Flux de données (diagramme séquence) <a id="flux-de-données"></a>  

#### 4.5.1 Création d’un mandat (use‑case UC‑01)  

```plantuml
@startuml
actor "Administrateur" as Admin
participant "Struts2 Front‑Controller" as FC
participant "UpsertMandatAction" as Action
participant "MandatServices" as Service
participant "MandatDao (JDBC)" as DAO
database "Oracle prep37" as DB

Admin -> FC : POST /upsertMandat
FC -> Action : invoke()
Action -> Service : upsertMandat(dto)
Service -> DAO : insertOrUpdate(mandat)
DAO -> DB : INSERT / UPDATE
DB --> DAO : OK
DAO --> Service : OK
Service --> Action : résultat
Action --> FC : forward to JSP (actionmessage)
FC --> Admin : page de confirmation
@enduml
```

#### 4.5.2 Import JORF (use‑case UC‑04)  

```plantuml
@startuml
actor "Scheduler (Quartz)" as Scheduler
participant "ArticleAnalyser (batch)" as Analyzer
participant "JORFExtractor" as Extractor
participant "StepAnalyse…" as Steps
participant "MandatServices" as Service
participant "MandatDao" as DAO
database "Oracle prep37" as DB

Scheduler -> Analyzer : execute()
Analyzer -> Extractor : download()
Extractor --> Analyzer : XML/JAR
Analyzer -> Steps : parse()
Steps -> Service : upsertMandat()
Service -> DAO : INSERT/UPDATE
DAO -> DB : SQL
DB --> DAO : OK
DAO --> Service : OK
Service --> Analyzer : done
Analyzer --> Scheduler : finish
@enduml
```

---  

### 4.6️⃣ Analyse de sécurité <a id="analyse-de-sécurité"></a>  

| Aspect | Risque identifié | Contre‑mesure (implémentée ou à implémenter) |
|--------|-----------------|----------------------------------------------|
| **Authentification** | Accès non autorisé si le token Cerbère est falsifié. | Utilisation du `SecurityManagerInitializer` et du filtre `SecurityFilter.java` (Spring Security) – validation du token JWT Cerbère. |
| **Autorisation** | Un utilisateur peut manipuler des mandats hors de son périmètre. | `RightsHelper.java` vérifie les rôles (`RoleApplicatifEnum`, `RoleVertigoEnum`). |
| **Injection SQL** | Construction dynamique de requêtes (ex. recherche libre). | Tous les services utilisent les DAOs générés par Vertigo (requêtes paramétrées). |
| **Exposition de données sensibles** | Export PDF contenant des informations personnelles. | Les vues JSP filtrent les champs selon le rôle (`actionmessage.ftl`). |
| **Disponibilité** | Défaillance du scheduler → perte d’alertes d’échéance. | Redondance du job Quartz (retry) et monitoring via `SupervisionAction`. |
| **Confidentialité des pièces jointes** | Stockage des pièces sur le serveur web. | Les pièces sont stockées hors‑doc‑root, accès contrôlé par `BaseAdminUserSession`. |
| **Log & audit** | Traçabilité insuffisante des modifications. | `log4j2.xml` configure les logs d’audit (niveau INFO) et le `ErrorHandler` centralise les exceptions. |

---  

### 4.7️⃣ Dette technique identifiée <a id="dette-technique"></a>  

| Zone | Observation | Impact | Action corrective |
|------|--------------|--------|-------------------|
| **Hard‑coding de messages** | Certaines chaînes sont codées en dur dans les JSP (`actionmessage-default.ftl`). | Difficulté de localisation / évolution. | Externaliser les messages dans `messages.properties`. |
| **Gestion des dates** | `FormatterDateRange` utilise `java.util.Date` (déprécié). | Risque de bugs de fuseau horaire. | Migrer vers `java.time` (`LocalDate`, `Period`). |
| **Couplage Struts2 ↔ Vertigo** | Les actions héritent de `AbstractBaseAdminActionSupport` qui mixe deux frameworks. | Complexité de test unitaire. | Refactoriser en services purement Spring, actions légères. |
| **Scripts SQL d’initialisation** | Séquences et contraintes créées séparément du modèle KSP → risque de désynchronisation. | Incohérence schéma / migration difficile. | Générer les scripts à partir des définitions KSP (outil Vertigo). |
| **Absence de tests d’intégration** | Aucun module de test automatisé pour les DAOs. | Régression possible lors des évolutions. | Ajouter un module `adminep-integration-tests` avec `Testcontainers`. |
| **Gestion des pièces jointes** | Stockage sur disque sans stratégie de rotation. | Consommation d’espace serveur. | Implémenter un store S3 ou un nettoyage programmé. |

---  

## 5️⃣ Qualité documentaire (conformité arc42 & ISO/IEC/IEEE 29148) <a id="qualité-documentaire"></a>  

| Critère | Conformité | Commentaire |
|---------|------------|-------------|
| **Structure arc42** | Sections « Introduction », « Solution Strategy », « Building Block View », « Runtime View », « Deployment View », « Cross‑cutting Concepts » (sécurité, performance) sont présentes sous forme de sections 1–4. | Les titres sont alignés avec le modèle arc42. |
| **Norme ISO 29148** | Description des exigences fonctionnelles (use‑cases, règles métier, scénarios) et techniques (architecture, données, sécurité). | Le document fournit la traçabilité entre exigences et artefacts (ex. code, diagrammes). |
| **Navigation** | Table des matières cliquable, liens internes (`[↩ Retour à…]`). | Tous les diagrammes PlantUML sont intégrés (`@startuml … @enduml`). |
| **Lisibilité** | Utilisation de tableaux, listes à puces, exemples concrets. | Les diagrammes sont légers et lisibles dans VS Code/Obsidian. |
| **Maintenabilité** | Chaque artefact (classe, script SQL) est référencé via les ancres générées par le listing de fichiers. | Facilite la mise à jour incrémentale. |

---  

## 6️⃣ Références <a id="références"></a>  

* **Documentation arc42** – <https://arc42.org> (lien externe uniquement à titre d’information).  
* **Fichiers sources** – Arborescence du projet `admin_ep` (voir le listing fourni).  
* **Scripts d’initialisation** – `adminep-database/scripts/init/*.sql`.  
* **Fichiers de configuration** – `adminep-deployment/conf/adminep.xml`, `adminep-web/src/main/resources/boot/config/*.xml`.  
* **Wiki** – `admin_ep.wikisi.md`, `home › Fiche‑Produit.md`.  

---  

*Fin du document.*  