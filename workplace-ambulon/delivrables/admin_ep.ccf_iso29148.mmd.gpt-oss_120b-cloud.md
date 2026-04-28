# 📄 Cahier des Charges Fonctionnel (CCF) – **admin_ep**  
*Conforme à la norme ISO/IEC/IEEE 29148 : 2018*  

> **Version** : 1.0 – 27 avril 2026  
> **Auteur** : Équipe Ingénierie des Exigences – SG/DNUM/PNM/DPNM3/BPN  
> **Références** :  
> - Wiki “home › Fiche‑Produit” (Document 3)  
> - Code source du projet (Documents 1 & 2) – arborescence et scripts SQL  
> - Document 4 “admin_ep.wikisi.md” (méta‑données)  

---

## 1️⃣ Identification et contexte du document
| Élément | Valeur |
|---|---|
| **ID du CCF** | CCF‑ADMINEP‑001 |
| **Projet** | admin_ep (Administration des établissements publics) |
| **Version du CCF** | 1.0 |
| **Date** | 27 avril 2026 |
| **Statut** | Draft → (à valider par la Maîtrise d’Ouvrage) |
| **Auteur(s)** | PO : SG/SPES, MOE : SG/DNUM/PNM/DPNM3/BPN |
| **Objet** | Définir les exigences fonctionnelles et non‑fonctionnelles du système admin_ep, son périmètre, ses acteurs, ses flux de données et les critères de validation. |
| **Portée** | Couverture complète du **backend Java/Struts2**, de la **base de données PostgreSQL**, des **interfaces web** (JSP/HTML) et du **module d’analyse/notification**. |
| **Exclusions** | Gestion du parc serveur, CI/CD, conteneurisation (Docker/K8s) – hors du périmètre fonctionnel. |

---

## 2️⃣ Description de l’écosystème (System/Software Context)

```mermaid
graph LR;
    subgraph Ext[Environnement externe]
        JORF[Source JORF (OpenData)] -->|Flux d’alimentation| ETL[Module d’analyse (ArticleAnalyser)]
        LDAP[Annuaire Cerbère] -->|AuthN/AuthZ| WEB[Web UI (Struts2/JSP)]
        SMTP[Mail serveur] -->|Envoi notifications| NOTIF[Service de notification]
    end;
    subgraph SYS[admin_ep System]
        WEB -->|Appels REST/Action| BLL[Business Logic Layer]
        BLL -->|CRUD| DB[(PostgreSQL)]
        BLL -->|Recherche| ES[Elasticsearch (facultatif)]
        BLL -->|Planification| SCHED[Scheduler (Quartz)]
        SCHED -->|Tâches périodiques| ETL;
        NOTIF -->|Envoi mail| USER[Utilisateurs (SPES, DG, Opérateurs)]
    end;
    Ext -->|HTTPS| WEB
```

**Frontières du système**  
- **Entrées** : requêtes HTTP (pages JSP, actions Struts), fichiers JORF (XML/.tar.gz), messages LDAP (authentification).  
- **Sorties** : réponses HTML/JSON, courriels de rappel, fichiers d’archive, exports CSV/ODS.  

**Principaux acteurs**  

| Rôle | Description | Source |
|---|---|---|
| **SPES** (Service de la Politique de l’Environnement) | Maîtrise d’ouvrage, définit les besoins fonctionnels. | Wiki “Fiche‑Produit” |
| **DG de tutelle** | Décide des validations de mandats, reçoit les alertes. | Wiki |
| **Opérateurs** | Saisissent / mettent à jour les données administratives. | Wiki |
| **Utilisateur Cerbère** | Authentifie les utilisateurs via le filtre Cerbère. | Code `SecurityFilter.java` |
| **Scheduler** | Processus interne qui déclenche le calcul d’échéances. | Code `SchedulerInitializer.java` |
| **Elasticsearch** (optionnel) | Indexe les articles JORF pour la recherche plein texte. | `adminep-web` resources |

---

## 3️⃣ Exigences fonctionnelles  

> **Notation** : `[ID] Titre` – chaque exigence possède les attributs décrits à la section 7.  

| ID | Titre | Description | Rationale | Source | Priority | Verification |
|---|---|---|---|---|---|---|
| **EXG-FCT-001** | Authentification unique | L’application doit authentifier chaque utilisateur via le filtre **Cerbère** (ID 619) et créer une session sécurisée. | Sécurité, traçabilité des actions | Wiki (Fiche‑Produit) / Code `SecurityFilter.java` | Mandatory | Test d’intégration (login / logout) |
| **EXG-FCT-002** | Gestion des profils | Chaque utilisateur possède un **profil** (BaseAdmin, Cerbère) qui détermine les droits d’accès (CRUD) sur les entités. | Gestion des habilitations | Code `Roles.java`, `RightsHelper.java` | Mandatory | Tests unitaires + revue de code |
| **EXG-FCT-003** | Saisie manuelle des administrateurs | L’opérateur peut créer, modifier et supprimer un **Administrateur** via le formulaire `upsertAdmin.jsp`. | Maintien de la donnée de référence | Wiki / UI `UpsertAdminAction.java` | Mandatory | Scénario BDD « Given…When…Then » |
| **EXG-FCT-004** | Saisie manuelle des établissements | Permet la création / mise à jour d’un **Établissement** (SIREN, libellé, type d’instance). | Couverture du périmètre fonctionnel | UI `UpsertEPAction.java` | Mandatory | Test fonctionnel UI |
| **EXG-FCT-005** | Gestion des mandats | Créer / éditer les **Mandats** (type : Titulaire / Suppléant) associés à un administrateur et à un établissement. | Traçabilité légale | UI `UpsertMandatAction.java` | Mandatory | Tests d’intégrité référentielle |
| **EXG-FCT-006** | Recherche multi‑critères | Un moteur de recherche doit permettre de filtrer les administrateurs, établissements, mandats (nom, SIREN, collège, type mandat, date). | Usabilité | UI `RechercheAdminsAction.java` & `RechercheEPAction.java` | Mandatory | Tests de recherche + performance (< 2 s) |
| **EXG-FCT-007** | Import JORF automatisé | Un **ArticleAnalyser** doit récupérer les fichiers JORF (RSS ou archive .tar.gz), extraire les nominations et les insérer dans la base. | Alimenter la base à jour | Code `ArticleAnalyser.java` | Mandatory | Test d’import (fichier mock) |
| **EXG-FCT-008** | Notification d’échéance | Le **Scheduler** doit détecter les mandats arrivant à expiration (≤ 30 jours) et envoyer un mail au référent. | Prévention des oublis | Code `SchedulerInitializer.java` | Mandatory | Test d’envoi (mail mock) |
| **EXG-FCT-009** | Historisation des mandats | Conserver les mandats expirés dans une table d’archive afin de pouvoir interroger les historiques. | Conformité légale | Base de données `mandat` + `mandat_archive` (non listé) | Optional | Vérification des triggers |
| **EXG-FCT-010** | Tableau de bord statistique | Générer des indicateurs (nombre d’établissements, mandats actifs, évolution temporelle) affichables dans `statistiques.jsp`. | Pilotage | UI `StatistiquesAction.java` | Optional | Validation visuelle + tests de calcul |
| **EXG-FCT-011** | Export ODS/CSV | Permettre l’export des listes d’administrateurs ou de mandats au format ODS ou CSV. | Interopérabilité | Utilitaire `OdsUtil.java` | Optional | Test d’export (format valide) |
| **EXG-FCT-012** | Gestion des synonymes de collèges | Ajouter / modifier les synonymes d’un collège (table `SYNONYME_COLLEGE`). | Recherche plus souple | Script SQL `5_create_tables_gestionnaires.sql` (création) | Optional | Test d’insertion + recherche |
| **EXG-FCT-013** | Gestion des tutelles | Lier un établissement à une ou plusieurs **Charges** (table `TUTELLE_ETABLISSEMENT_CHARGE`). | Modélisation juridique | Script SQL `1_alter_tutelle.sql` | Optional | Test d’intégrité FK |
| **EXG-FCT-014** | Page d’accueil personnalisée | Afficher un tableau de bord contextuel selon le profil de l’utilisateur (menu, fil d’Ariane). | UX | JSP `accueil.jsp` + `Menu.java` | Mandatory | Test UI par profil |
| **EXG-FCT-015** | Gestion des erreurs | Un **ErrorHandler** doit capturer les exceptions et afficher la page `application-error.jsp`. | Fiabilité | Code `ErrorHandler.java` | Mandatory | Tests de résilience (exception volontaire) |

> **Remarque** : Les exigences de capacité (ex. « le système doit supporter 500 utilisateurs simultanés ») sont exprimées en tant que **Exigences de performance** (section 4.1) et ne figurent pas dans le tableau ci‑dessus.

---

## 4️⃣ Exigences non‑fonctionnelles  

### 4.1 Performance
| ID | Description | Rationale | Vérification |
|---|---|---|---|
| **EXG-NFR-001** | Temps de réponse ≤ 2 s pour toute requête de recherche (≈ 10 000 lignes). | UX, productivité | Tests de charge (JMeter) |
| **EXG-NFR-002** | Le Scheduler doit exécuter le job d’échéance en ≤ 5 s, toutes les 24 h. | Disponibilité | Profilage Java |
| **EXG-NFR-003** | Le processus d’import JORF doit traiter un fichier de 200 Mo en ≤ 30 s. | Volume de données | Test d’import avec jeu de données réel |

### 4.2 Interfaces externes
| ID | Interface | Description |
|---|---|---|
| **EXG-INT-001** | **HTTPS** (port 443) – UI Web | Toutes les communications client‑serveur chiffrées TLS 1.2+. |
| **EXG-INT-002** | **LDAP Cerbère** (port 389/636) – Authentification | Filtre `SecurityFilter.java` utilise le service Cerbère. |
| **EXG-INT-003** | **SMTP** – Envoi de notifications | Configurable via `application-config.xml`. |
| **EXG-INT-004** | **JORF OpenData** – RSS/HTTP | URL : <https://echanges.dila.gouv.fr/OPENDATA/JORF/> |
| **EXG-INT-005** | **Elasticsearch** (optionnel) – Indexation plein texte | Déclaré dans `boot-config.xml`. |

### 4.3 Qualité
| ID | Exigence |
|---|---|
| **EXG-QLT-001** | **Maintenabilité** – Code Java doit respecter le style Checkstyle fourni (rules.xml). |
| **EXG-QLT-002** | **Testabilité** – 80 % de couverture de tests unitaires (JaCoCo). |
| **EXG-QLT-003** | **Fiabilité** – Taux d’erreur ≤ 0,1 % en production (monitoring Sentry). |
| **EXG-QLT-004** | **Portabilité** – Application doit pouvoir être déployée sur Tomcat 9‑10 et PostgreSQL 9.6–15. |

### 4.4 Conception & contraintes
| ID | Contrainte |
|---|---|
| **EXG-CON-001** | **Java 8** minimum, compatible JDK 11 (code source). |
| **EXG-CON-002** | **Framework** : Struts 2, Vertigo, Vertigo‑Dynamo, DisplayTag. |
| **EXG-CON-003** | **Maven** : version 3.6+, packaging `war`. |
| **EXG-CON-004** | **Base de données** : PostgreSQL 9.6+ (scripts fournis). |
| **EXG-CON-005** | **Gestion des dépendances** : Toutes les librairies déclarées dans les `pom.xml`. |

### 4.5 Sécurité
| ID | Exigence |
|---|---|
| **EXG-SEC-001** | **Confidentialité** – Tous les flux HTTP → HTTPS. |
| **EXG-SEC-002** | **Intégrité** – Signature des fichiers JORF importés (SHA‑256). |
| **EXG-SEC-003** | **Disponibilité** – Redondance Tomcat Cluster (session sticky). |
| **EXG-SEC-004** | **Authentification** – AuthN via Cerbère, token JWT stocké en session. |
| **EXG-SEC-005** | **Autorisation** – Contrôle RBAC défini dans `Roles.java`. |
| **EXG-SEC-006** | **Audit** – Historisation des actions critiques (INSERT/UPDATE/DELETE) dans tables `audit_*`. |

---

## 5️⃣ Modèle de données conceptuel (UML class)

```mermaid
classdiagram;
    %% Entités principales;
    class Administrateur {
        +Long id;
        +String nom;
        +String prenom;
        +String email;
        +String civilite;
        +String typeProfil (BASEADMIN|CERBERE)
    }
    class Etablissement {
        +Long id;
        +String siren;
        +String sigle;
        +String libelle;
        +String libelleDe;
        +TypeInstance typeInstance;
    }
    class Mandat {
        +Long id;
        +Date dateDebut;
        +Date dateFin;
        +TypeMandat type (TITULAIRE|SUPPLEANT)
        +ModeNomination mode;
    }
    class Charge {
        +Long id;
        +String libelle;
    }
    class Ministere {
        +Long id;
        +String sigle;
        +String nom;
        +String statut;
    }
    class College {
        +Long id;
        +String identifiant;
    }
    class TypeInstance {
        +Long id;
        +String type;
        +String a_linstance_de;
        +String de_linstance_de;
    }
    class TypeMandat {
        +Long id;
        +String type;
    }
    class ModeNomination {
        +Long id;
        +String code;
        +String mode;
        +String motCleTitre;
        +String motCleCorpsTexte;
    }
    class TutelleEtablissementCharge {
        +Boolean principale;
    }
    class SynonymeCollege {
        +String synonyme;
        +Boolean defaut;
    }

    %% Relations;
    Administrateur "1" -- "0..*" Mandat : détient >
    Etablissement "1" -- "0..*" Mandat : concerné >
    Etablissement "1" -- "0..*" EtablissementCollege : possède >
    EtablissementCollege "0..*" -- "1" College : lie >
    Etablissement "1" -- "0..*" TutelleEtablissementCharge : sousTutelle >
    TutelleEtablissementCharge "0..*" -- "1" Charge : charge >
    Charge "0..*" -- "1" Ministere : appartient >
    College "0..*" -- "0..*" SynonymeCollege : aSynonymes >
    Mandat "0..*" -- "1" TypeMandat : type >
    Mandat "0..*" -- "1" ModeNomination : mode >
    Etablissement "1" -- "1" TypeInstance : instanceDe >
```

---

## 6️⃣ Modélisation des comportements  

### 6.1 Cas d’utilisation (UML use‑case)

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#0066CC','edgeLabelBackground':'#FFFFFF'}}%%}%%
useCaseDiagram;
    actor Opérateur as Op;
    actor DG de tutelle as DG;
    actor SPES (MOA) as SPES;
    actor Utilisateur (Cerbère) as User;
    rectangle "admin_ep" {
        Op --> (Saisir Administrateur)
        Op --> (Saisir Etablissement)
        Op --> (Gérer Mandat)
        Op --> (Recherche)
        Op --> (Exporter données)

        DG --> (Recevoir notifications d’échéance)
        DG --> (Valider / Refuser mandat)

        SPES --> (Définir paramètres de notification)
        SPES --> (Consulter tableau de bord)

        User --> (Se connecter)
        User --> (Accéder selon son profil)
    }
```

### 6.2 Diagramme d’activité – **Processus d’import JORF**

```mermaid
statediagram-v2;
    [*] --> TéléchargerFlux;
    TéléchargerFlux --> DécompresserArchive;
    DécompresserArchive --> ParseXML;
    ParseXML --> FiltrerNominations;
    FiltrerNominations --> EnrichirBase;
    EnrichirBase --> MettreAJourStatistiques;
    MettreAJourStatistiques --> [*]
```

### 6.3 Diagramme de séquence – **Notification d’échéance**

```mermaid
sequencediagram;
    participant Scheduler;
    participant ServiceMandat;
    participant Mailer;
    participant User (DG)

    Scheduler->>ServiceMandat: getMandatsEcheance(≤30j)
    ServiceMandat-->>Scheduler: List<Mandat>
    Scheduler->>Mailer: sendMail(to=DG.email, body=…)
    Mailer-->>User: Email reçu
```

---

## 7️⃣ Attributs d’exigences (exemple pour quelques exigences)

| ID | Identifiant | Description | Rationale | Source | Priority | Status | Verification Method | Risk | Stability |
|----|--------------|-------------|-----------|--------|----------|--------|---------------------|------|-----------|
| EXG-FCT-001 | Authentification unique | Authentifier chaque utilisateur via Cerbère (ID 619). | Sécurité, traçabilité. | Wiki / Code `SecurityFilter.java` | Mandatory | Test d’intégration (login/logout) | Medium | Stable |
| EXG-FCT-006 | Recherche multi‑critères | Filtrer par nom, SIREN, collège, type mandat, dates. | Usabilité. | UI `RechercheAdminsAction.java` | Mandatory | BDD scenario, temps de réponse <2 s | Low | Stable |
| EXG-NFR-001 | Temps de réponse ≤ 2 s | Garantir une UX fluide. | Satisfaction utilisateur. | Performance test plan | Mandatory | Load test (JMeter) | High | Volatile (dépend du volume) |
| EXG-SEC-004 | Authentification via Cerbère | Utiliser le service d’authentification central. | Conformité aux politiques. | Code `SecurityFilter.java` | Mandatory | Test d’accès refusé sans token | High | Stable |
| EXG-CON-001 | Java 8 minimum | Compatibilité avec les librairies actuelles. | Contraintes techniques. | `pom.xml` | Mandatory | Compilation JDK 8+ | Low | Stable |

> **Notation** : chaque exigence suit le modèle ISO 29148 (ID, Description, Rationale, Source, Priority, Status, Verification, Risk, Stability).

---

## 8️⃣ Traçabilité des exigences  

| Exigence (ID) | Source(s) | Artefact de conception | Artefact de test |
|---|---|---|---|
| EXG‑FCT‑001 | Wiki “Fiche‑Produit”, `SecurityFilter.java` | Diagramme de séquence (Auth), classe `BaseAdminUserSession` | TestLoginLogout.java |
| EXG‑FCT‑003 | UI `upsertAdmin.jsp`, `DetailAdminAction.java` | Diagramme de séquence (Create/Update Admin) | AdminCreateTest.java |
| EXG‑FCT‑006 | UI `RechercheAdminsAction.java`, `RechercheEPAction.java` | Diagramme d’activité (Recherche) | SearchPerformanceTest.java |
| EXG‑FCT‑007 | ArticleAnalyser.java, JORF RSS | Diagramme d’activité (Import JORF) | JORFImportTest.java |
| EXG‑FCT‑008 | SchedulerInitializer, `MandatsResolver.java` | Diagramme de séquence (Notification) | NotificationJobTest.java |
| EXG‑NFR‑001 | Performance spec (Wiki) | Diagramme d’activité (Search) | LoadTestSearch.jmx |
| EXG‑SEC‑004 | Cerbère spec, `SecurityFilter.java` | Diagramme de séquence (Auth) | SecurityFilterTest.java |
| EXG‑CON‑001 | `pom.xml`, `adminep-web/pom.xml` | Architecture (Maven modules) | BuildPipeline (Jenkins) |
| EXG‑QLT‑002 | JaCoCo report (CI) | N/A | CoverageReport.html |

> La matrice complète (exigences × artefacts) est maintenue dans le référentiel **ALM** (Jira + Confluence) sous le ticket **ADMINEP‑REQ‑001**.

---

## 9️⃣ Gestion des exigences  

| Processus | Description | Responsable | Outils |
|---|---|---|---|
| **Gestion du changement** | Toute modification d’exigence doit passer par le workflow **Change Request** (CR) avec validation MOA & MOE. | PO / Chef de projet | Jira (Workflow CR) |
| **Résolution des conflits** | Analyse d’impact (matrice de dépendances) → décision collégiale. | Comité de pilotage | Confluence (page d’impact) |
| **Priorisation** | Méthode MoSCoW (Must, Should, Could, Won’t) – appliquée dans le backlog Jira. | PO | Jira (Backlog) |
| **Suivi** | Revues mensuelles des exigences (review meeting) – mise à jour du statut (Draft/Approved/Baseline). | PMO | Confluence, Jira (Reports) |
| **Traçabilité** | Chaque exigence possède un **ID** unique, liée aux artefacts (code, tests, doc). | QA Lead | ALM (Jira ↔ Bitbucket) |

---

## 🔟 Validation et vérification  

| Niveau | Objectif | Méthode | Critères d’acceptation |
|---|---|---|---|
| **Unitaires** | Vérifier le bon fonctionnement de chaque composant Java. | JUnit + Mockito | ≥ 80 % de couverture, tests verts. |
| **Intégration** | S’assurer de la cohérence entre couche UI, BLL et DB. | Tests d’intégration Spring/Struts2 (MockMVC) | Tous les scénarios BDD (Given/When/Then) passent. |
| **Système** | Valider le comportement complet (import JORF, notifications, recherche). | Test end‑to‑end avec jeux de données (Docker compose). | Temps de réponse < 2 s, aucune erreur 5xx. |
| **Performance** | Garantir les exigences de temps de réponse et de charge. | JMeter scripts (100 utilisateurs simultanés). | < 2 s pour 95 % des requêtes, pas de fuite de mémoire. |
| **Sécurité** | Vérifier l’authentification, l’autorisation et la confidentialité. | OWASP ZAP + tests d’injection SQL. | Aucun résultat de vulnérabilité critique. |
| **Recette** | Validation métier par la MOA. | Sessions de test avec les acteurs (SPES, DG, Opérateurs). | Signature du rapport de recette. |

---

## 📌 Annexes  

1. **Glossaire** (extraits)  
   - **Mandat** : période de fonction d’un administrateur au sein d’un établissement.  
   - **Charge** : ministère ou direction responsable d’un établissement.  
   - **College** : groupe d’établissements partageant une même mission.  

2. **Références**  
   - ISO/IEC/IEEE 29148 : 2018 – *Systems and software engineering – Life cycle processes – Requirements engineering*  
   - `adminep-web/src/main/resources/struts.xml` (déclaration des actions).  
   - `adminep-database/scripts/init/2_populateTablesIntegration.sql` (données de référence).  

3. **Liens utiles** (ALM)  
   - Jira : <https://jira.gouv.fr/projects/ADMINEP>  
   - Confluence : <https://confluence.gouv.fr/display/ADMINEP/Requirements>  

---  

> **Fin du CCF** – Toute modification doit être consignée dans le registre de changement (section 9).  

---  