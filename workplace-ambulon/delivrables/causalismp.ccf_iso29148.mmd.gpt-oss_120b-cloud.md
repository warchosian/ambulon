# 📄 **Cahier des Charges Fonctionnel (CCF) – projet *causalismp***  
**Conforme à la norme ISO/IEC/IEEE 29148 : 2018**  

> **Version** : 1.0 – 2024‑04‑28  
> **Auteur** : Équipe d’ingénierie des exigences (extraits du code, des documents et du wiki du projet)  

---  

## 1️⃣ Identification et contexte du document  

| Élément | Valeur |
|---|---|
| **Identifiant du CCF** | CCF‑CAUSALISMP‑V1.0 |
| **Titre** | Gestion des accidents du travail et des maladies professionnelles |
| **Projet** | causalismp |
| **Références** | - `causalismp.code.filtered.md` (extraction du code source) <br> - `causalismp.code.summarized.md` (résumé du code) <br> - `causalismp.wiki.md` (description métier) |
| **Portée** | Système web (WAR) de saisie, consultation, édition, export et synchronisation des dossiers d’accident et de maladie professionnelle, ainsi que la gestion des tables de référence (grades, services, statuts, etc.). |
| **Objectifs** | • Centraliser les données d’accidents et de maladies professionnelles.<br>• Garantir la traçabilité et la conformité réglementaire.<br>• Permettre la mise à jour automatisée des référentiels via des web‑services externes.<br>• Fournir des écrans de saisie ergonomiques (Struts 1 + JSP). |
| **Historique des versions** | <ul><li>V1.0 – 2024‑04‑28 – Création du CCF à partir des artefacts fournis.</li></ul> |
| **Statut** | Draft (en cours de validation avec les parties prenantes). |
| **Propriétaire** | Comité de pilotage du projet *causalismp* (Managers du document). |
| **Parties prenantes** | • **Managers** : Adrien DESSARTRE, Anthony BOULOY, Anthony MEAUZOONE, Antoine DUBOIS, Christian ARBOGAST, Jeanne VODUNGBO, Julien GARDIN, Nicolas DEMEY <br>• **Développeurs** : Grégoire GUITTET, Hervé MARCHAL, Jenkins Causalismp, Maxime Careil, Pascal FORHAN, Vincent JUSTIN <br>• **Rapporteurs / Qualité** : Chantal CURBET, Christophe LOUVARD, Erwan SALMON, … (voir wiki) <br>• **Utilisateurs finaux** : Agents de prévention, Médecins du travail, Gestionnaires RH, Auditeurs internes/externes. |

---  

## 2️⃣ Description de l’écosystème (System/Software Context)

```mermaid
graph LR
    U[Utilisateurs (agents, médecins, RH)] -->|Utilisent| W[causalismp‑WEB (Struts/JSP)]
    W -->|Accède à| DB[(Base de données Oracle)]
    W -->|Appelle| WS[Web‑services externes (StubWS.jar, WSClient*)]
    DB -->|Contient| REF[Tables de référence (Grade, Service, Statut, …)]
    DB -->|Contient| DACC[Table ACCIDENT]
    DB -->|Contient| DMAL[Table MALADIE]
    WS -->|Synchronise| REF;
    subgraph Environnement;
        J[Serveur d’application (Tomcat / JBoss)]
        O[Serveur Oracle]
        S[Serveur de web‑services externes]
    end
    J --> W;
    O --> DB;
    S --> WS
```

| Élément | Description |
|---|---|
| **Frontière du système** | Le système s’arrête à l’interface web (Struts) et aux services REST/SOAP appelés via `StubWS.jar`. |
| **Interfaces externes** | - **JNDI datasource** `java:comp/env/jdbc/userDScausalis` (Oracle). <br> - **Web‑services** (ex. `WSClientService`, `WSClientGrade`, `WSClientEffectif`). |
| **Acteurs** | - **Agent de saisie** (création/modification de dossiers). <br> - **Médecin du travail** (consultation, validation). <br> - **Gestionnaire RH** (export, statistiques). <br> - **Auditeur** (consultation en lecture seule). |
| **Environnement opérationnel** | Application déployée dans un conteneur Java EE (Tomcat/JBoss). Base Oracle 11g+. Accès via navigateur web (IE 11, Firefox, Chrome). |

---  

## 3️⃣ Exigences fonctionnelles (Functional Requirements)

> **Notation** : chaque exigence suit le format ISO 29148 (ID, titre, description, rationale, source, priority, verification, dependencies).  

| ID | Titre | Description | Rationale | Source | Priority | Verification | Dependencies |
|----|-------|-------------|-----------|--------|----------|--------------|--------------|
| **EXG‑FCT‑001** | Authentification unique | L’application doit authentifier chaque utilisateur via le composant `Cerbere` (cf. `reauth.jsp`). | Sécurité réglementaire (RGPD, Code du travail). | Code (reauth.jsp) | Mandatory | Test d’intégration (login/logout) + revue de code | – |
| **EXG‑FCT‑002** | Gestion des rôles | Le système doit associer chaque utilisateur à un rôle (ex. `Service`, `Statut`) et limiter l’accès aux écrans en fonction du rôle. | Séparation des responsabilités. | Code (Constantes, Service beans) | Mandatory | Test fonctionnel (accès selon rôle) | EXG‑FCT‑001 |
| **EXG‑FCT‑003** | Saisie d’un dossier d’accident | L’écran `EditionDossierAction` doit permettre de créer/modifier un **dossier d’accident** (classe `Accident`). Tous les champs obligatoires doivent être validés côté serveur (`CommonException`). | Conformité aux exigences légales de déclaration d’accident. | Code (Action, Form, Exception) | Mandatory | Tests unitaires `EditionDossierAction*Test` (non fournis mais attendus) | EXG‑FCT‑001 |
| **EXG‑FCT‑004** | Saisie d’un dossier de maladie professionnelle | L’écran `EditionDossierMaladieAction*` doit permettre de créer/modifier un **dossier de maladie** (classe `DossierMaladie`). | Obligations de suivi des maladies professionnelles. | Code (Action, Form) | Mandatory | Tests fonctionnels d’édition | EXG‑FCT‑001 |
| **EXG‑FCT‑005** | Consultation des dossiers | L’écran `DossiersAction` (et `DossiersMaladieAction`) doit lister les dossiers selon les filtres de recherche (`RechercheDossiersForm`). | Besoin métier de suivi et reporting. | Code (Action, Form) | Mandatory | Tests d’acceptation (listing + filtres) | EXG‑FCT‑001 |
| **EXG‑FCT‑006** | Export des dossiers | Le composant `CausalisExportManager` doit exporter les dossiers au format OpenOffice (via `FichierOpenOffice`). | Besoin de partage avec les organismes de contrôle. | Code (Export) | Desirable | Test d’intégration (export → fichier .odt) | EXG‑FCT‑003, EXG‑FCT‑004 |
| **EXG‑FCT‑007** | Gestion des tables de référence | Les services `GradeService`, `DomaineAffectationService`, `StatutService`, `TachePrescriteService` doivent fournir les listes de référence (lecture seule) via DAO Castor. | Centralisation des référentiels, cohérence des données. | Code (Service) | Mandatory | Tests unitaires `*ServiceTest` | – |
| **EXG‑FCT‑008** | Synchronisation des référentiels | L’interface `SynchronizeService` doit synchroniser les grades avec le service externe `TranscodageGradeService` (via `WSClientGrade`). | Maintien à jour des référentiels externes. | Code (SynchronizeService, WS filter) | Optional (déploiement différé) | Test d’intégration (mock WS) | EXG‑FCT‑007 |
| **EXG‑FCT‑009** | Calcul de la tranche d’âge | Le helper `TrancheAgeHelper` doit déterminer la tranche d’âge (1‑5) à partir de l’année de naissance et de l’année de synchronisation. | Utilisé dans les exportations/statistiques. | Code (TrancheAgeHelper) | Desirable | Test unitaire `TrancheAgeHelperTest` | – |
| **EXG‑FCT‑010** | Gestion des erreurs techniques | Toutes les erreurs techniques doivent être encapsulées dans `TechnicalException` et journalisées (`Log4jInitializer`). | Faciliter le support et la traçabilité. | Code (TechnicalException, Log4j) | Mandatory | Test de levée d’exception + logs | – |
| **EXG‑FCT‑011** | Validation côté serveur des formulaires | Chaque `Form` (ex. `GenericForm`, `DateValidator`) doit valider les champs obligatoires et lever `CommonException` en cas d’erreur. | Garantir l’intégrité des données. | Code (Form, Exception) | Mandatory | Tests unitaires de validation | EXG‑FCT‑003, EXG‑FCT‑004 |
| **EXG‑FCT‑012** | Pagination des listes | La pagination (max = 30) doit être appliquée aux listes d’objets (ex. `EffectifsAction`) via le paramètre `pagination.max`. | Performance UI et expérience utilisateur. | Property file (`project.properties`) | Mandatory | Test fonctionnel (pages > 30) | – |
| **EXG‑FCT‑013** | Interface d’aide contextuelle | Tous les écrans doivent afficher le bouton d’aide (`<a href="javascript:popup_dep()">`) comme dans `haut.jspf`. | Support aux utilisateurs. | JSP (haut.jspf) | Optional | Inspection UI | – |
| **EXG‑FCT‑014** | Gestion des avertissements UI | Le composant `ActionWarning` doit permettre d’afficher des messages d’avertissement non bloquants (ex. données incomplètes). | Améliorer la convivialité. | Code (ActionWarning) | Optional | Test UI (message affiché) | – |
| **EXG‑FCT‑015** | Gestion des statuts de dossiers | Le champ `saisieTerminee` (dans `Service`) doit indiquer la clôture d’un dossier d’accident et `saisieMaladiesProTerminee` celle d’un dossier maladie. | Suivi du cycle de vie des dossiers. | Code (Service) | Mandatory | Test de mise à jour du statut | EXG‑FCT‑003, EXG‑FCT‑004 |
| **EXG‑FCT‑016** | Recherche avancée | Le formulaire `RechercheDossiersForm` doit permettre de filtrer les dossiers par période, service, grade, etc. | Besoin d’analyse et de reporting. | Code (Form) | Mandatory | Test fonctionnel (combinaisons de filtres) | EXG‑FCT‑005 |
| **EXG‑FCT‑017** | Gestion des logs d’audit | Tous les événements critiques (login, création/édition/suppression de dossiers) doivent être loggués via Log4j (`log4j.xml`). | Traçabilité légale. | Config (`log4j.xml`) | Mandatory | Inspection des fichiers de log | – |
| **EXG‑FCT‑018** | Gestion de la version du produit | Le fichier `version.properties` doit être généré à chaque build avec les variables `${project.causalis.version}` et `${project.causalis.date}`. | Assurer la traçabilité des livrables. | Build (Maven) | Mandatory | Vérification du contenu du WAR | – |

> **Remarque** : Les exigences ci‑dessus sont dérivées du code source, des scripts SQL et du wiki. D’autres exigences (ex. sauvegarde, haute disponibilité) seront détaillées dans les exigences non‑fonctionnelles.

---  

## 4️⃣ Exigences non‑fonctionnelles (Non‑Functional Requirements)

### 4.1 Exigences de performance  

| ID | Titre | Description | Rationale | Priority | Verification |
|----|-------|-------------|-----------|----------|--------------|
| **EXG‑PER‑001** | Temps de réponse UI | Chaque page doit être rendue en < 2 s (connexion 3G) et < 1 s (LAN). | Acceptabilité utilisateur. | Mandatory | Tests de charge (JMeter). |
| **EXG‑PER‑002** | Temps de traitement des exports | L’export d’un lot de ≤ 500 dossiers doit finir < 30 s. | Respect des délais de reporting. | Desirable | Test d’intégration export. |
| **EXG‑PER‑003** | Consommation mémoire | Le serveur d’application ne doit pas dépasser 512 Mo de heap pour 100 concurrents. | Optimisation de l’infrastructure. | Mandatory | Monitoring JVM (JVisualVM). |

### 4.2 Exigences d’interface externe  

| ID | Titre | Description | Rationale | Priority | Verification |
|----|-------|-------------|-----------|----------|--------------|
| **EXG‑INT‑001** | API de synchronisation | Le service `SynchronizeService` expose une méthode `int synchronize()` accessible via JMX. | Permettre l’orchestration externe. | Optional | Test JMX call. |
| **EXG‑INT‑002** | Accès JNDI datasource | Le JNDI `java:comp/env/jdbc/userDScausalis` doit être déclaré dans `context.xml`. | Découplage de la configuration. | Mandatory | Vérification du fichier `context.xml`. |
| **EXG‑INT‑003** | Web‑services externes | Les WS client (`WSClientGrade`, `WSClientEffectif`) doivent être configurés avec les URL définies dans `cerbere-bouchon.xml`. | Interopérabilité. | Optional | Test de connexion mockée. |

### 4.3 Exigences de qualité  

| ID | Titre | Description | Rationale | Priority | Verification |
|----|-------|-------------|-----------|----------|--------------|
| **EXG‑QUAL‑001** | Couverture de tests unitaires | Minimum 80 % de couverture du code Java (excluant les JSP). | Qualité du code. | Mandatory | SonarQube (`sonar.projectKey`). |
| **EXG‑QUAL‑002** | Respect du standard de codage | Conformité aux conventions Java (Indentation 4 sp, Javadoc). | Lisibilité, maintenance. | Mandatory | Analyse Sonar / Checkstyle. |
| **EXG‑QUAL‑003** | Documentation | Chaque classe publique doit disposer d’un Javadoc complet. | Faciliter la maintenance. | Mandatory | Inspection code. |
| **EXG‑QUAL‑004** | Gestion des dépendances | Utilisation de Maven 3 avec versionnage fixe des librairies (ex. Struts 1.3.10, Castor 1.3). | Reproductibilité des builds. | Mandatory | `pom.xml` audit. |

### 4.4 Exigences de conception et contraintes  

| ID | Titre | Description | Rationale | Priority |
|----|-------|-------------|-----------|----------|
| **EXG‑DES‑001** | Architecture en couches | Séparation stricte : **Web (Struts)** → **Service** → **DAO (Castor)** → **Base**. | Faciliter les évolutions. | Mandatory |
| **EXG‑DES‑002** | Utilisation de Struts 1 | Le framework Struts 1 est imposé (legacy). | Conformité historique. | Mandatory |
| **EXG‑DES‑003** | Utilisation de Castor JDO | Gestion de la persistance via Castor JDO (`database.xml`). | Compatibilité avec l’existant. | Mandatory |
| **EXG‑DES‑004** | Packaging Maven multi‑module | Modules `causalismp‑database`, `‑deployment`, `‑doc`, `‑web`. | Modularité, réutilisabilité. | Mandatory |
| **EXG‑DES‑005** | Utilisation de JDK 1.8 | Compatibilité avec les serveurs d’entreprise. | Support long terme. | Mandatory |

### 4.5 Exigences de sécurité  

| ID | Titre | Description | Rationale | Priority | Verification |
|----|-------|-------------|-----------|----------|--------------|
| **EXG‑SEC‑001** | Authentification forte | Utiliser le composant `Cerbere` avec chiffrement des mots de passe (hash + sel). | Protection des données personnelles. | Mandatory | Tests d’intrusion (OWASP ZAP). |
| **EXG‑SEC‑002** | Contrôle d’accès basé sur les rôles (RBAC) | Les actions Struts (`*Action`) doivent vérifier le rôle via `session.getAttribute("utilisateur")`. | Séparer les droits. | Mandatory | Tests fonctionnels (accès refusé). |
| **EXG‑SEC‑003** | Transmission sécurisée | Toutes les communications serveur ↔ client doivent être via HTTPS (TLS 1.2+). | Confidentialité. | Mandatory | Scan SSL (Qualys). |
| **EXG‑SEC‑004** | Protection contre les injections SQL | Les DAO utilisent des paramètres nommés (`dao.getAll("Grade", map, operators, "tri")`). | Éviter les attaques. | Mandatory | Analyse statique (FindSecBugs). |
| **EXG‑SEC‑005** | Gestion des sessions | Timeout de session = 30 min d’inactivité, invalidation à la déconnexion. | Limiter le risque de détournement. | Mandatory | Test de session expiration. |

---  

## 5️⃣ Modèle de données conceptuel  

> **Notation UML simplifiée (Mermaid)**  

```mermaid
classDiagram
    class Accident {
        +int id;
        +Date dateAccident;
        +String description;
        +Grade grade;
        +Service service;
        +int saisieTerminee;

    class DossierMaladie {
        +int id;
        +Date dateDiagnostic;
        +String description;
        +Grade grade;
        +Service service;
        +int saisieMaladiesProTerminee;

    class Grade {
        +int code;
        +String libelle;
        +int codeGroupementGrade;

    class Service {
        +int code;
        +String libelle;
        +int saisieTerminee;
        +int saisieMaladiesProTerminee;

    class Statut {
        +int code;
        +String libelle;

    class Utilisateur {
        +String login;
        +String nom;
        +String prenom;
        +Service service;
        +String role;

    Accident "1" --> "1" Service : appartient à;
    Accident "1" --> "1" Grade   : possède;
    DossierMaladie "1" --> "1" Service : appartient à;
    DossierMaladie "1" --> "1" Grade   : possède;
    Utilisateur "1" --> "1" Service : travaille pour;
    Utilisateur "1" --> "1" Statut  : a
```

*Toutes les tables de référence (Grade, Service, Statut, DomaineAffectation, etc.) héritent de `TablesReferences` (classe abstraite non détaillée).*

---  

## 6️⃣ Modélisation des comportements  

### 6.1 Diagrammes de cas d’utilisation  

```mermaid
usecaseDiagram;
    actor Agent;
    actor Médecin;
    actor GestionnaireRH;
    actor Auditeur;
    Agent --> (Saisir un dossier d’accident)
    Agent --> (Saisir un dossier de maladie)
    Agent --> (Consulter ses dossiers)
    Médecin --> (Valider un dossier)
    GestionnaireRH --> (Exporter les dossiers)
    GestionnaireRH --> (Consulter les statistiques)
    Auditeur --> (Consulter les dossiers en lecture seule)
    GestionnaireRH --> (Synchroniser les référentiels)
```

### 6.2 Diagrammes d’activités (exemple : création d’un dossier d’accident)

```mermaid
statediagram-v2;
    [*] --> Authentifier;
    Authentifier --> SaisirFormulaire;
    SaisirFormulaire --> ValiderFormulaire;
    ValiderFormulaire -->|OK| PersisterDossier;
    ValiderFormulaire -->|Erreur| AfficherErreur;
    PersisterDossier --> EnregistrerLog;
    EnregistrerLog --> [*]
```

### 6.3 Diagrammes d’états (exemple : cycle de vie d’un dossier)

```mermaid
statediagram;
    [*] --> Brouillon;
    Brouillon --> EnCours : Soumission;
    EnCours --> Terminé : Validation;
    EnCours --> Rejeté : Refus;
    Terminé --> Archivé : 30 jours;
    Rejeté --> Archivé : 30 jours
```

### 6.4 Diagrammes de séquence (exemple : synchronisation des grades)

```mermaid
sequencediagram;
    participant UI as "Interface admin"
    participant Service as "GradeService"
    participant WS as "WSClientGrade"
    participant DB as "Base Oracle"
    UI->>Service: demanderSynchronisation()
    Service->>WS: getGradesExternes()
    WS-->>Service: listeGrades;
    Service->>DB: comparer & insérer nouveaux grades;
    DB-->>Service: résultat (nb lignes insérées)
    Service-->>UI: nbLignesInsérées
```

---  

## 7️⃣ Attributs d’exigences (Requirements Attributes)

| Attribut | Description | Exemple |
|----------|-------------|----------|
| **Identifiant** | Code unique suivant la convention `EXG‑<catégorie>‑<numéro>` | `EXG‑FCT‑001` |
| **Description** | Énoncé clair, non ambigu | « L’application doit authentifier chaque utilisateur via Cerbere » |
| **Rationale** | Pourquoi l’exigence existe | Conformité RGPD & Code du travail |
| **Source** | Origine (code, document, atelier) | `reauth.jsp`, `README.md`, `wiki` |
| **Priority** | Mandatory / Desirable / Optional | Mandatory |
| **Status** | Draft / Approved / Baseline | Draft |
| **Verification** | Méthode de vérification (test, inspection) | Test d’intégration login/logout |
| **Risk** | Impact potentiel si non‑respectée | High (perte de données) |
| **Stability** | Probabilité de changement | Stable (référentiel métier) |
| **Dependencies** | Autres exigences ou composants liés | `EXG‑FCT‑001` dépend de `EXG‑SEC‑001` |

---  

## 8️⃣ Traçabilité des exigences  

> **Matrice de traçabilité (RTM)** – Les colonnes représentent les exigences fonctionnelles (EXG‑FCT‑xxx) ; les lignes les artefacts (use‑case, classe, test, fichier).  

| Artefact / Exigence | **EXG‑FCT‑001** | **EXG‑FCT‑003** | **EXG‑FCT‑006** | **EXG‑FCT‑008** | **EXG‑PER‑001** | **EXG‑SEC‑001** |
|---------------------|----------------|----------------|----------------|----------------|----------------|----------------|
| **Use‑case** `Saisir un dossier d’accident` | ✔ | ✔ | – | – | ✔ | – |
| **Classe** `Cerbere` (login) | ✔ | – | – | – | – | ✔ |
| **JSP** `reauth.jsp` | ✔ | – | – | – | – | – |
| **Action** `EditionDossierAction` | – | ✔ | – | – | ✔ | – |
| **Service** `GradeService` | – | – | – | ✔ | – | – |
| **WS Client** `WSClientGrade` | – | – | – | ✔ | – | – |
| **Test** `EditionDossierActionTest` | – | ✔ | – | – | – | – |
| **Test** `TrancheAgeHelperTest` | – | – | – | – | – | – |
| **Performance test** (JMeter) | – | – | – | – | ✔ | – |
| **Audit log** `log4j.xml` | – | – | – | – | – | ✔ |

> **Notes**  
> * Une case « ✔ » indique que l’artefact réalise ou vérifie l’exigence.  
> * Les exigences non‑fonctionnelles (PER, SEC, QUAL, etc.) sont liées à des artefacts de configuration ou de test.  

---  

## 9️⃣ Gestion des exigences  

| Processus | Description | Outils / Artifacts |
|-----------|-------------|--------------------|
| **Gestion du changement** | Toute modification d’une exigence doit passer par une **RFC** (Request for Change) qui décrit la raison, l’impact et le plan de mise à jour. | JIRA / GitLab Issues, tableau de suivi des RFC. |
| **Résolution des conflits** | Conflits entre exigences (ex. performance vs sécurité) sont résolus lors d’ateliers de priorisation avec les **Managers** et **Développeurs**. | Matrice de priorisation, réunion de gouvernance (bi‑hebdo). |
| **Priorisation** | Utilisation d’une pondération (MoSCoW) : *Must* (mandatory), *Should* (desirable), *Could* (optional), *Won’t*. | Tableur de priorisation, tableau Kanban. |
| **Outils recommandés** | - **JIRA** (gestion des exigences & des tickets) <br> - **Confluence** (documentation) <br> - **GitLab CI** (pipeline de build & tests) <br> - **SonarQube** (qualité & couverture) | Tous les artefacts (exigences, tests, revues) sont liés via les IDs. |

---  

## 🔟 Validation et vérification  

| Niveau | Activité | Méthode | Artefact(s) concerné(s) |
|--------|----------|----------|--------------------------|
| **Revue d’exigences** | Validation du CCF par les **Managers** et **Rapporteurs** | Walk‑through, checklist de conformité ISO 29148 | CCF complet |
| **Tests unitaires** | Vérification du bon fonctionnement de chaque classe/ méthode | JUnit + Mockito | `*ServiceTest`, `*PredicateTest`, `TrancheAgeHelperTest` |
| **Tests d’intégration** | Vérification des flux complets (UI → Service → DAO → DB) | Selenium + DBUnit | `EditionDossierAction*`, `DossiersAction`, `Export` |
| **Tests de performance** | Mesure du temps de réponse et de la charge | JMeter scripts (login, recherche, export) | EXG‑PER‑001, EXG‑PER‑002 |
| **Tests de sécurité** | Scans d’injection, tests d’authentification | OWASP ZAP, Sonar‑Security, tests d’accès RBAC | EXG‑SEC‑001 à EXG‑SEC‑005 |
| **Inspection de code** | Vérification du respect des standards Java et des Javadoc | Checkstyle, SonarQube | EXG‑QUAL‑001 à EXG‑QUAL‑004 |
| **Revue de configuration** | Validation des fichiers `log4j.xml`, `project.properties`, `context.xml` | Checklist de configuration | EXG‑SEC‑003, EXG‑INT‑001 |
| **Audit de logs** | Vérification que tous les événements critiques sont journalisés | Analyse des fichiers de log (Log4j) | EXG‑SEC‑005, EXG‑QUAL‑001 |
| **Acceptation utilisateur (UAT)** | Validation fonctionnelle par les **Utilisateurs finaux** (agents, médecins) | Sessions de test avec scénarios métier | EXG‑FCT‑003, EXG‑FCT‑004, EXG‑FCT‑005 |

> **Critères d’acceptation**  
> - **100 %** des exigences *Mandatory* sont couvertes par au moins un test.  
> - **Couverture de code** ≥ 80 % (exigence EXG‑QUAL‑001).  
> - Aucun défaut de sévérité *Critical* ou *High* détecté en phase de test.  

---  

## 📚 Annexes  

### A. Glossaire  

| Terme | Définition |
|---|---|
| **Accident** | Événement de travail entraînant un dommage corporel, enregistré dans la table `ACCIDENT`. |
| **Maladie professionnelle** | Pathologie reconnue comme liée à l’activité professionnelle, enregistrée dans `DMAL`. |
| **Grade** | Niveau hiérarchique ou classification du personnel, référencé dans la table `GRADE`. |
| **Service** | Unité fonctionnelle (ex. : Service RH, Service Sécurité). |
| **Cerbere** | Module d’authentification interne (défini dans le projet). |
| **StubWS.jar** | Bibliothèque contenant les stubs des web‑services externes. |
| **TranscodageGrade** | Mapping entre le grade interne Causalis et le code du système externe Rehucit. |
| **RBAC** | Role‑Based Access Control – contrôle d’accès basé sur les rôles. |

### B. Références  

| Référence | Description |
|-----------|-------------|
| **ISO/IEC/IEEE 29148 : 2018** | Norme de génie des exigences. |
| **README.md** (racine) | Contexte de reprise du projet, décision de suppression de l’ACAI parent. |
| **causalismp‑database/scripts** | Scripts de migration de la base (renommage colonnes, mise à jour accident). |
| **Wiki `home.md`** | Présentation métier et liste des membres. |
| **pom.xml** (racine) | Configuration Maven multi‑module. |
| **sonar‑project.properties** | Paramétrage SonarQube (quality‑gate). |

---  

## 📌 Conclusion  

Ce **Cahier des Charges Fonctionnel** décrit de façon exhaustive les exigences du projet **causalismp**, en les classant selon les catégories fonctionnelles et non‑fonctionnelles de la norme ISO 29148. Il fournit :

* Un **modèle de données** et des **modèles comportementaux** (UML, diagrammes Mermaid).  
* Une **matrice de traçabilité** reliant exigences, cas d’utilisation, classes, tests et artefacts de configuration.  
* Un **plan de validation** couvrant tests unitaires, intégration, performance, sécurité et acceptation utilisateur.  

Le document constitue une base solide pour la **planification**, le **développement** et le **contrôle qualité** du système, et pourra être enrichi lors des ateliers de clarification avec les parties prenantes.  

---  

*Fin du CCF – Version 1.0 – 2024‑04‑28*  