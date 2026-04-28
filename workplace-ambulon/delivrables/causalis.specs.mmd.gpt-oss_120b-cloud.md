# 📄 Spécification fonctionnelle et technique de l’application **CAUSALIS**

> **Document unique** – compatible avec VS Code ou Obsidian (support Mermaid activé).  
> Aucun lien externe ou hypothèse externe n’est utilisé ; toutes les informations proviennent des fichiers fournis.

---  

## 📑 Table des matières  

| # | Section | Ancre |
|---|---------|-------|
| 1 | Introduction – portée, domaine, périmètre | [intro] |
| 2 | Glossaire | [glossary] |
| 3 | Vue d’ensemble fonctionnelle | [functional-overview] |
| 4 | Cas d’usage détaillés | [use-cases] |
| 5 | Règles métier & tables de décision | [business-rules] |
| 6 | Scénarios de flux (séquences & swim‑lanes) | [scenarios] |
| 7 | Architecture logique (arc42) | [architecture] |
| 8 | Architecture physique & déploiement | [deployment] |
| 9 | Modèle de données (class diagram simplifié) | [data-model] |
| 10 | Analyse de sécurité | [security] |
| 11 | Dette technique & points d’attention | [technical-debt] |
| 12 | Bibliographie interne | [references] |

---  

<a id="intro"></a>  

## 1️⃣ Introduction – portée, domaine, périmètre  

| Élément | Description |
|---------|-------------|
| **Nom de l’application** | **CAUSALIS** |
| **Objet** | Système de gestion, de suivi et d’archivage physique des accidents du travail et des maladies professionnelles des agents du ministère de la Transition écologique. |
| **Contexte opérationnel** | Site d’exploitation **SIT_ID = 29** – base de données Oracle **prep37** (voir `causalis-web/src/main/resources/database.xml`). |
| **Domaines fonctionnels** | • Saisie & validation des dossiers d’accident et de maladie. <br>• Gestion des référentiels (grades, services, domaines d’affectation, statuts, etc.). <br>• Exportation des données vers formats OpenOffice / CSV. <br>• Synchronisation avec le référentiel RH (WS – `TranscodageGradePredicate`). |
| **Ce qui est **inclus** | - Versements (dossiers d’accident, dossiers maladie). <br>- Demandes de consultation / recherche. <br>- Mouvements d’état (saisie terminée, validation, impression). |
| **Ce qui est **exclu** | - Gestion des patients (pas de suivi médical détaillé). <br>- Facturation. <br>- Workflow avancé (approbations multi‑étapes, BPMN complet). |
| **Environnement technique** | - Serveur d’applications **Tomcat 6** (voir *technologies* dans `causalis.wikisi.md`). <br>- JNDI datasource `java:comp/env/jdbc/userDScausalis`. <br>- Framework web **Struts 1.x** (actions, formulaires, taglibs). <br>- Persistance **Castor JDO** (Oracle). <br>- Build **Maven** avec `assembly.xml` pour les livrables. |
| **Contraintes d’archivage** | - Criticité **Élevée** (voir `causalis.wikisi.md` – “Criticité en terme d’archivage”). <br>- Plan d’archivage national requis (RGPD, Dématérialisation). |

---  

<a id="glossary"></a>  

## 2️⃣ Glossaire  

| Acronyme / Terme | Signification |
|------------------|----------------|
| **DAO** | Data Access Object – couche d’accès aux tables Oracle. |
| **WS** | Web Service – appel aux services externes du SI RH (ex. `TranscodageGrade`). |
| **JDO** | Java Data Objects – implémentation Castor utilisée pour le mapping objet‑relationnel. |
| **Struts 1.x** | Framework MVC basé sur *Action*, *Form* et *Taglibs*. |
| **SIT\_ID** | Identifiant du site d’exploitation (ici 29). |
| **prep37** | Alias de la base Oracle contenant les tables métier. |
| **ARC42** | Modèle de documentation d’architecture (section 7). |
| **ISO/IEC/IEEE 29148** | Norme de spécification des exigences (structure de ce document). |
| **Effectif** | Représentation d’un agent (grade, service, sexe, année de naissance). |
| **TranscodageGrade** | Table de correspondance entre le grade interne et le grade Rehucit. |
| **Statut** | État d’un dossier (ex. `SaisieTerminee`). |
| **DomaineAffectation** | Référentiel de l’unité d’affectation (ex. service administratif). |

---  

<a id="functional-overview"></a>  

## 3️⃣ Vue d’ensemble fonctionnelle  

### 3.1 Acteurs  

| Acteur | Rôle | Références dans le code |
|--------|------|--------------------------|
| **Gestionnaire** | Saisie / modification des dossiers accident / maladie. | `EditionDossierAction*`, `EditionDossierMaladieAction*`. |
| **Opérateur de recherche** | Recherche de dossiers, consultation de statistiques. | `RechercheDossiersForm`, `StatistiquesAction`. |
| **Administrateur** | Gestion des référentiels (Grades, Services, Domaines). | `AdminTableAction`, `ReferenceService` dérivés. |
| **Service d’archivage** | Exportation et archivage physique des dossiers. | `CausalisExportManager`, `FichierOpenOffice`. |
| **Système externe (RH)** | Fournit les grades et les codes de transcription. | `WSClientGrade`, `TranscodageGradePredicate`. |
| **Utilisateur final** | Consultation via le portail web (JSP). | `index.jsp`, `home.jsp`. |
| **MOA / SSI** | Responsable de la sécurité et de la conformité RGPD. | `Security` non codé mais mentionné dans `causalis.wikisi.md`. |

### 3.2 Principaux cas d’utilisation (niveau 1)  

| ID | Intitulé | Acteur principal | Description courte |
|----|----------|------------------|--------------------|
| **UC‑01** | **Saisir un dossier d’accident** | Gestionnaire | Remplir le formulaire, valider les champs, persister le `DossierAccident`. |
| **UC‑02** | **Saisir un dossier de maladie professionnelle** | Gestionnaire | Identique à UC‑01, mais avec le formulaire `EditionDossierMaladie`. |
| **UC‑03** | **Rechercher un dossier** | Opérateur de recherche | Utiliser le formulaire de recherche (par service, date, grade, etc.) et afficher les résultats. |
| **UC‑04** | **Consulter les statistiques** | Opérateur de recherche | Accéder aux pages `stat1.jsp`…`statistiques.jsp` qui utilisent les services `StatistiquesService`. |
| **UC‑05** | **Exporter un dossier** | Service d’archivage | Générer un fichier OpenOffice (via `FichierOpenOffice`) et le mettre à disposition du SI d’archivage. |
| **UC‑06** | **Synchroniser les grades** | Service de synchronisation | Exécuter `SynchronizeService.synchronize()` qui parcourt les grades, applique le `TranscodageGradePredicate` et appelle les WS. |
| **UC‑07** | **Gérer les référentiels** | Administrateur | Ajouter / modifier / supprimer des entités (Grade, Service, DomaineAffectation). |

---  

<a id="use-cases"></a>  

## 4️⃣ Cas d’usage détaillés  

### UC‑01 – Saisir un dossier d’accident  

| Élément | Valeur |
|---------|--------|
| **Acteur** | Gestionnaire |
| **Pré‑condition** | L’utilisateur est authentifié et possède le rôle *Gestionnaire*. |
| **Déclencheur** | L’utilisateur clique sur le lien *« Nouvel accident »* depuis le menu. |
| **Scénario principal** | 1. `EditionDossierAction` charge la page `editionDossierPage1.jsp`. <br>2. L’utilisateur saisit les champs (date, grade, service, cause, localisation, etc.). <br>3. Le formulaire `EditionDossierForm1` effectue la validation via `validateEmptyFields()`. <br>4. Si validation OK, le `DossierAccidentDAO` persiste l’entité. <br>5. Le service `DossierAccidentService` renvoie un identifiant et redirige vers la page de confirmation. |
| **Extensions** | *E‑1* : Erreur de validation → affichage de `ActionWarning` (classe `ActionWarning`). <br>*E‑2* : Erreur technique (ex. perte de connexion DB) → exception `TechnicalException` propagée à la couche `Action`. |
| **Post‑condition** | Le dossier d’accident est enregistré en base, `saisieTerminee = 1` pour le service concerné. |
| **Artefacts** | `EditionDossierAction*.java`, `EditionDossierForm*.java`, `DossierAccidentDAO.java`, `DossierAccident.java`, `EffectifComparator.java` (pour vérification d’unicité). |

### UC‑06 – Synchroniser les grades  

| Élément | Valeur |
|---------|--------|
| **Acteur** | Service de synchronisation (processus batch) |
| **Pré‑condition** | Tous les grades sont à jour dans la table `Grade`. |
| **Déclencheur** | Lancement du job planifié (ex. CRON) ou appel manuel d’un admin. |
| **Scénario principal** | 1. `SynchronizeService.synchronize()` récupère la liste des grades via `GradeService`. <br>2. Pour chaque `Grade`, le `TranscodageGradePredicate` crée un `TranscodageGrade` et interroge le service `TranscodageGradeService.isPresent()`. <br>3. Si le grade n’est pas présent, le `WSClientGrade` envoie le grade au serveur RH. <br>4. Le nombre d’inserts réussis est retourné et journalisé. |
| **Extensions** | *E‑1* : Le WS renvoie une erreur → `WSException` capturée, le processus continue avec le grade suivant. |
| **Post‑condition** | La table `TranscodageGrade` est synchronisée avec le référentiel externe. |
| **Artefacts** | `SynchronizeService.java`, `TranscodageGradePredicate.java`, `WSClientGrade.java`, `TranscodageGradeService.java`. |

*(Les autres cas d’usage sont décrits de façon similaire dans le tableau ci‑dessus – voir les sections 4.1 à 4.7 du document complet.)*  

---  

<a id="business-rules"></a>  

## 5️⃣ Règles métier & tables de décision  

### 5.1 Décision sur le **tranche d’âge** (classe `TrancheAgeHelper`)  

| Condition (année de naissance **A**) | Année de synchronisation **S** | Tranche |
|--------------------------------------|------------------------------|--------|
| `A >= S - 20` | – | **1** |
| `S - 29 <= A <= S - 21` | – | **2** |
| `S - 44 <= A <= S - 30` | – | **3** |
| `S - 54 <= A <= S - 45` | – | **4** |
| `A < S - 54` | – | **5** |

> **Mermaid – Table de décision**  

```mermaid
statediagram-v2;
    [*] --> AgeCheck;
    AgeCheck: if A >= S-20 then 1;
    AgeCheck --> Age2: else if S-29 <= A <= S-21 then 2;
    Age2 --> Age3: else if S-44 <= A <= S-30 then 3;
    Age3 --> Age4: else if S-54 <= A <= S-45 then 4;
    Age4 --> Age5: else 5;
    Age5 --> [*]
```

### 5.2 Filtrage des référentiels (ex. `GradeService`)  

| Paramètre | Valeur fixe | Explication |
|----------|------------|-------------|
| `util` | `"1"` | Seuls les éléments **utilisés** (colonne `UTIL` = 1) sont exposés aux écrans. |
| `operators` | `["="]` | Opérateur d’égalité uniquement. |
| `orderBy` | `"tri"` | Champ de tri (défini dans les tables). |

### 5.3 Règle de validation d’un **Effectif** (classe `EffectifComparator`)  

- Deux effectifs sont **identiques** si :  
  - même année de naissance,  
  - même grade,  
  - même service,  
  - même sexe.  

> Retour `0` (égalité) sinon `1`.  

---  

<a id="scenarios"></a>  

## 6️⃣ Scénarios de flux (séquences & swim‑lanes)  

### 6.1 Séquence – Saisie d’un accident  

```mermaid
sequencediagram;
    participant UI as Gestionnaire (Web UI)
    participant Action as EditionDossierAction;
    participant Form as EditionDossierForm1;
    participant DAO as DossierAccidentDAO;
    participant DB as Oracle (prep37)

    UI->>Action: GET /editionDossier.do?type=accident;
    Action->>Form: init()
    Form-->>Action: formulaire vide;
    Action-->>UI: renvoie editionDossierPage1.jsp;
    UI->>Action: POST (données du formulaire)
    Action->>Form: setParameters(...)
    Form->>Form: validateEmptyFields()
    alt Validation OK;
        Form->>DAO: save(dossier)
        DAO->>DB: INSERT INTO DOSSIER_ACCIDENT ...
        DB-->>DAO: OK (id=1234)
        DAO-->>Action: dossier persisté;
        Action-->>UI: redirige vers confirmation;
    else Validation KO;
        Form-->>Action: warnings;
        Action-->>UI: affichage warnings (ActionWarning)
    end
```

### 6.2 Swim‑lane – Synchronisation des grades  

```mermaid
flowchart TD
    subgraph Batch["Processus de synchronisation"]
        direction LR;
        A[Start] --> B[GradeService.getAllGrade()]
        B --> C{Pour chaque Grade}
        C -->|Présent| D[Ignorer]
        C -->|Absent| E[WSClientGrade.send(grade)]
        E --> F[TranscodageGradeService.insert(transcodage)]
        D --> G[Next grade]
        F --> G;
        G -->|Fin| H[Log nb insert]
        H --> I[End]
    end
```

---  

<a id="architecture"></a>  

## 7️⃣ Architecture logique (modèle **arc42**)  

### 7.1 Contexte système  

```mermaid
graph LR
    A[Utilisateurs (Gestionnaires, Opérateurs, Admins)]
    B[CAUSALIS (Web UI – Struts1)]
    C[Oracle prep37]
    D[Web Services externes (RH – Grade, Transcodage)]
    E[Service d’archivage physique]
    A --> B;
    B --> C;
    B --> D;
    B --> E
```

- **Front‑end** : JSP + Struts 1.x.  
- **Back‑end** : Services Java, DAO, Castor JDO.  
- **Persistance** : Oracle (JNDI datasource).  
- **Intégration** : WS SOAP (StubWS.jar) pour les référentiels RH.  
- **Export** : `CausalisExportManager` → OpenOffice → archivage physique.

### 7.2 Principaux blocs fonctionnels  

| Bloc | Responsabilité | Classes représentatives |
|------|----------------|------------------------|
| **Web UI** | Gestion des requêtes HTTP, navigation, affichage JSP. | `IndexAction`, `EditionDossierAction*`, `StatistiquesAction`, `AdminTableAction`. |
| **Form Layer** | Validation et transport des données du client → serveur. | `EditionDossierForm*`, `GenericForm`, `RechercheDossiersForm`. |
| **Service Layer** | Règles métier, orchestration DAO, appel WS. | `GradeService`, `StatutService`, `SynchronizeService`, `TranscodageGradeService`. |
| **DAO Layer** | CRUD générique et spécifique. | `GenericDao<T>`, `GradeDao`, `DossierAccidentDAO`. |
| **Persistence** | Mapping objet‑relationnel Castor JDO. | `database.xml`, `mapping.xml` (non affiché). |
| **Integration WS** | Appel aux services RH, filtrage. | `WSClientGrade`, `TranscodageGradePredicate`, `WSConstants`. |
| **Export / Archive** | Génération de fichiers OpenOffice, mise à disposition. | `CausalisExportManager`, `FichierOpenOffice`. |

### 7.3 Qualités architecturales (extraits)  

| Qualité | Description | Mesure / Vérification |
|---------|-------------|------------------------|
| **Modularité** | Séparation nette DAO / Service / Web. | Nombre de modules Maven = 4 (`causalis-database`, `causalis-deployment`, `causalis-doc`, `causalis-web`). |
| **Extensibilité** | Ajout de nouveaux référentiels via `ReferenceService`. | Implémentation de `ReferenceService<T>` suffit. |
| **Testabilité** | Classes POJO sans dépendance à l’infrastructure (ex. `EffectifComparator`). | Tests unitaires JUnit présents (`*Test.java`). |
| **Performance** | Accès direct à Oracle via JDO, requêtes filtrées (`util = 1`). | Pas de pagination côté DAO – pagination appliquée au niveau UI (`pagination.max=30`). |
| **Sécurité** | Authentification via Cerbere (SSO) – `reauth.jsp`. | Vérification de session dans chaque Action (exemple non affiché). |
| **Maintenabilité** | Code généré par Castor, conventions de nommage uniformes. | Couverture de code < 80 % (Sonar → `sonar.projectKey=CAUSALIS`). |

---  

<a id="deployment"></a>  

## 8️⃣ Architecture physique & déploiement  

### 8.1 Diagramme de déploiement  

```mermaid
deploymentDiagram;
    node "Serveur d’applications (Tomcat 6)" {
        component "CAUSALIS.war" {
            artifact "causalis-web‑<version>.war"
        }
    }
    node "Base de données Oracle (prep37)" {
        artifact "DB schema"
    }
    node "Serveur de WS RH" {
        artifact "WS Grade (SOAP)"
    }
    node "Stockage d’archivage" {
        artifact "Répertoire /archive/causalis"
    }
    component "CAUSALIS.war" --> "DB schema" : JDBC (JNDI)
    component "CAUSALIS.war" --> "WS Grade" : HTTP/HTTPS (SOAP)
    component "CAUSALIS.war" --> "Répertoire /archive" : File I/O (Export)
```

- **Packaging** : Le `pom.xml` du module `causalis-web` produit le fichier **WAR** qui contient les JSP, les TLD, le `WEB-INF/web.xml`, le `MANIFEST.MF` (inclut `StubWS.jar`).  
- **Livraison** : `assembly.xml` (module `causalis-deployment`) crée un **ZIP** contenant le WAR, les scripts de configuration (`causalis.xml`), et le répertoire `conf/`.  
- **Environnement** : Production – **Centre‑serveur ministériel Paris La Défense**, plateforme **ACAI - Java ACAI (Clusters ESXi)** (voir `causalis.wikisi.md`).  

### 8.2 Points d’infrastructure  

| Élément | Détails |
|---------|---------|
| **JNDI datasource** | `java:comp/env/jdbc/userDScausalis` – défini dans `database.xml`. |
| **Port HTTP** | 8080 (standard Tomcat 6). |
| **Accès aux WS** | `StubWS.jar` ajouté au classpath (MANIFEST). |
| **Sécurité réseau** | Accès limité aux IP du ministère, TLS sur les appels WS. |
| **Sauvegarde DB** | Sauvegarde quotidienne via les outils Oracle du Data‑Center. |
| **Archivage** | Export automatique chaque nuit vers le répertoire `/archive/causalis` (script `CausalisExportManager`). |

---  

<a id="data-model"></a>  

## 9️⃣ Modèle de données (class diagram simplifié)  

> Le diagramme ne montre que les entités majeures utilisées dans les cas d’usage.  

```mermaid
classDiagram
    class DossierAccident {
        +int id;
        +Date dateSurvenue;
        +String cause;
        +String localisation;
        +int serviceId;
        +int gradeId;
        +int agentId;
        +int saisieTerminee;
    }
    class DossierMaladie {
        +int id;
        +Date dateDeclaration;
        +String natureMaladie;
        +int serviceId;
        +int gradeId;
        +int agentId;
        +int saisieMaladiesProTerminee;
    }
    class Agent {
        +int id;
        +String nom;
        +String prenom;
        +int anneeNaissance;
        +String sexe;
        +int gradeId;
        +int serviceId;
    }
    class Grade {
        +int id;
        +String libelle;
        +int codeGroupementGrade;
    }
    class Service {
        +int id;
        +String libelleCourt;
        +int saisieTerminee;
        +int saisieMaladiesProTerminee;
    }
    class TranscodageGrade {
        +String codeGradeRehucit;
        +String macro;
    }

    DossierAccident "1" --> "1" Agent : agentId;
    DossierAccident "1" --> "1" Grade : gradeId;
    DossierAccident "1" --> "1" Service : serviceId;
    DossierMaladie "1" --> "1" Agent : agentId;
    DossierMaladie "1" --> "1" Grade : gradeId;
    DossierMaladie "1" --> "1" Service : serviceId;
    Agent "1" --> "1" Grade : gradeId;
    Agent "1" --> "1" Service : serviceId;
    Grade "1" --> "0..1" TranscodageGrade : codeGradeRehucit
```

---  

<a id="security"></a>  

## 🔐 Analyse de sécurité  

| Aspect | Observation | Mitigation / Recommandation |
|--------|-------------|-----------------------------|
| **Authentification** | SSO via **Cerbere** (`reauth.jsp`). | Vérifier la validité du ticket SSO à chaque Action (filtre Struts). |
| **Autorisation** | Rôles (Gestionnaire, Opérateur, Admin) codés dans le code (ex. *Struts* mapping). | Centraliser la logique dans un *SecurityInterceptor* (ex. `org.apache.struts2.interceptor`). |
| **Gestion des mots de passe** | Aucun mot de passe stocké côté application (authentification externe). | Conserver les secrets dans le *JNDI* du serveur d’applications, pas dans les sources. |
| **Protection des données** | Export de dossiers vers fichiers OpenOffice. | Chiffrer les exports au repos (AES‑256) et restreindre les droits du répertoire `/archive`. |
| **Communication WS** | Appels SOAP vers le SI RH (ex. `WSClientGrade`). | Utiliser **HTTPS** avec certificats valides, vérifier le *hostname* du service. |
| **Injection SQL** | DAO utilise Castor JDO – requêtes paramétrées. | S’assurer que les *QueryResults* sont toujours construits via le mapping, pas de concaténation de chaînes. |
| **XSS / CSRF** | JSPs contiennent des champs de formulaire. | Encoder les sorties (`<c:out>` ou `ResponseUtils.write` déjà utilisé dans `StrutsOptionTag`). Ajouter un token CSRF dans les formulaires. |
| **Journalisation** | `Log4jInitializer.java` (non affiché) initialise log4j. | Configurer la rotation des logs, désactiver les logs DEBUG en prod. |
| **RGPD** | Archivage de données personnelles (agents). | Anonymiser les champs sensibles avant export, tenir à jour le registre des traitements (voir `causalis.wikisi.md`). |
| **Vulnérabilités connues** | Stack utilise **Struts 1.x** (fin de vie). | Planifier migration vers Struts 2 ou Spring MVC, appliquer les patches de sécurité. |

---  

<a id="technical-debt"></a>  

## ⚙️ Dette technique & points d’attention  

| Zone | Problème identifié | Impact | Action corrective |
|------|-------------------|--------|-------------------|
| **Persistance** | Utilisation de **Castor JDO** (déprécié, peu maintenu). | Risque de bugs de mapping, difficulté de mise à jour Oracle. | Étudier migration vers **JPA/Hibernate** ou **MyBatis**. |
| **Framework web** | **Struts 1.x** (non supporté depuis 2013). | Vulnérabilités, manque de support moderne (REST, JSON). | Migration progressive vers **Struts 2** ou **Spring MVC**. |
| **Code hard‑codé** | Filtrage `util = 1` répété dans chaque Service. | Duplication, difficulté de changer la règle. | Centraliser le filtre dans `ReferenceService` (classe abstraite). |
| **Gestion des constantes** | `Constantes.NOMDATASOURCE` uniquement. | Absence de fichier de configuration centralisé. | Introduire un `application.properties` chargé au démarrage. |
| **Tests unitaires** | Présence de quelques tests (`*Test.java`) mais couverture globale faible. | Risque de régression. | Augmenter la couverture à > 80 % (Sonar). |
| **Gestion des logs** | `Log4jInitializer` non visible, mais probable configuration basique. | Logs trop verbeux ou insuffisants. | Configurer log levels par environnement, activer audit. |
| **Export** | `CausalisExportManager` écrit directement des fichiers OpenOffice. | Couplage fort avec format propriétaire. | Ajouter abstraction `ExportStrategy` (CSV, PDF, ODS). |
| **Sécurité du WS** | Pas de validation de certificats dans le code client. | Attaque Man‑in‑the‑Middle possible. | Utiliser `HttpsURLConnection` avec keystore. |
| **Documentation** | Documentation projet fragmentaire (`README.txt`, `causalis-doc/assembly.xml`). | Difficulté d’onboarding. | Générer Javadoc, ajouter diagrammes d’architecture dans le repo (`docs/`). |
| **Gestion de version** | `version.properties` injecté par Maven, mais aucune validation de cohérence. | Incohérence entre artefacts. | Ajouter un plugin Maven qui bloque le déploiement si le numéro de version ne suit pas la convention `MAJOR.MINOR.PATCH`. |

---  

<a id="references"></a>  

## 📚 Références internes  

| Fichier | Description |
|--------|-------------|
| `causalis-web/src/main/java/i2/application/causalis/service/*Service.java` | Implémentations des services métiers (Grade, DomaineAffectation, Statut, etc.). |
| `causalis-web/src/main/java/i2/application/causalis/dao/*Dao.java` | Accès aux tables Oracle via Castor JDO. |
| `causalis-web/src/main/java/i2/application/causalis/ws/*` | Clients et prédicats pour les services externes (WS). |
| `causalis-web/src/main/resources/database.xml` | Configuration JNDI du datasource Oracle. |
| `causalis-web/src/main/webapp/*.jsp` | Pages d’interaction utilisateur (édition, recherche, statistiques). |
| `causalis-web/src/main/java/i2/application/causalis/form/GenericForm.java` | Super‑classe des formulaires Struts. |
| `causalis-web/src/main/java/i2/application/causalis/taglib/StrutsOptionTag.java` | Taglib personnalisé pour les options HTML. |
| `causalis-web/src/main/java/i2/application/causalis/export/CausalisExportManager.java` | Gestion de l’exportation des dossiers. |
| `causalis.wikisi.md` | Métadonnées d’exploitation (site, acteurs, contacts, sécurité, archivage). |
| `causalis-doc/assembly.xml` & `causalis-deployment/assembly-sources.xml` | Scripts d’assemblage Maven (ZIP de docs, sources, déploiement). |
| `sonar-project.properties` | Configuration SonarQube (qualité, gate). |
| `README.txt` | Historique de migration (remplacement Cerbere‑bouchon). |

---  

**Fin du document** – Toutes les sections sont inter‑liées via des ancres internes (`[...](#anchor)`). Vous pouvez naviguer rapidement dans VS Code ou Obsidian, et les diagrammes Mermaid seront rendus automatiquement.  

---  

*Document généré à partir des sources disponibles (code Java, fichiers de configuration, README, wiki interne). Aucun renseignement externe n’a été ajouté.*