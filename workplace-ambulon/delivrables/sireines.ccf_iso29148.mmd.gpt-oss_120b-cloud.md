# 📄 Cahier des Charges Fonctionnel (CCF) – SIREINES  
**Version : 1.0 – 2024‑06‑27**  
**Conforme à : ISO/IEC/IEEE 29148 : 2018**  

---  

## 1️⃣ Identification & Contexte du Document  

| Élément | Valeur |
|---|---|
| **Identifiant du CCF** | **CCF‑SIREINES‑2024‑01** |
| **Projet** | SIREINES – Système d’information de recensement des experts et spécialistes scientifiques et techniques |
| **Version du projet** | 2.5.20 (déploiement : 12 mars 2026) |
| **Maître d’Ouvrage (MOA)** | CGDD / DRI / AST4 – Pascal Zemour (chef de projet) – Vincent Letrouit (sponsor) |
| **Maître d’Œuvre (MOE)** | Klee Group (historique) – SG / DNUM / PNM / DPNM3 (actuel) |
| **Périmètre fonctionnel** | Gestion du répertoire d’experts, suivi des dossiers de qualification, génération de rapports, import/export, recherche, notifications, administration de la sécurité (Cerbère). |
| **Environnement d’exécution** | Serveur ministériel (Paris La Défense) – IaaS (ECO4) – Docker + Tomcat 7 + PostgreSQL 14 + BIRT 4.3 – Web (HTTPS) |
| **Objectifs du CCF** | 1️⃣ Formaliser les exigences du système ; 2️⃣ Garantir la traçabilité de chaque exigence ; 3️⃣ Définir les critères d’acceptation et les moyens de vérification. |
| **Références** | • `README.md`, `budget.md`, `declaration-rgpd.md` (documentation projet)  <br>• `settings.xml`, `pom.xml` (Maven) <br>• `Dockerfile`, `docker‑compose.yml` (déploiement) <br>• `application‑config.xml`, `struts.xml` (configuration) <br>• `BirtManager.java`, `SearchManagerInitializer.java` (code) <br>• `*.ftl` (templates UI) <br>• `*.sql` (scripts DB) |
| **Date de création** | 15 / 03 / 2022 (fiche) – mise à jour : 27 / 06 / 2024 |
| **Statut** | En production – maintenu et évolutif |

---  

## 2️⃣ Vision du Système & Modèle de Contexte (UML)

```mermaid
graph LR;
    subgraph Utilisateurs;
        U1[Chef de projet] 
        U2[Agent (expert)] 
        U3[Comité de domaine] 
        U4[Administrateur] 
    end;
    subgraph Système;
        S1[SIREINES Web] 
        S2[Base PostgreSQL] 
        S3[ElasticSearch] 
        S4[BIRT Reporting] 
        S5[Cerbère – AuthZ] 
    end;
    U1 -->|déploiement, suivi| S1;
    U2 -->|consultation, saisie| S1;
    U3 -->|qualification, vote| S1;
    U4 -->|configuration, import| S1;
    S1 -->|lecture/écriture| S2;
    S1 -->|indexation/recherche| S3;
    S1 -->|génération PDF/HTML| S4;
    S1 -->|authentification| S5
```

*Le diagramme montre les acteurs externes et les sous‑systèmes internes avec leurs flux principaux.*

---  

## 3️⃣ Exigences Fonctionnelles  

> **Convention d’identifiant** : `EXG‑FCT‑XXX` (ex. `EXG‑FCT‑001`).  
> **Structure** : Description, Rationale, Source, Priority, Verification, Dependencies.  

| ID | Description | Rationale | Source | Priority | Verification | Dependencies |
|----|-------------|-----------|--------|----------|--------------|--------------|
| **EXG‑FCT‑001** | **Gestion du référentiel d’experts** – création, mise à jour, consultation et désactivation d’un expert. | Constituer le répertoire d’experts nécessaire aux qualifications. | Analyse métier – MOA | Mandatory | Test fonctionnel UI + Vérif. BDD (table `EXPERT`) | Aucun |
| **EXG‑FCT‑002** | **Gestion des dossiers** – création, édition, suivi d’état, attachement de documents. | Chaque demande de qualification doit être tracée. | Spécifications fonctionnelles – MOA | Mandatory | Test d’intégration (CRUD) + Audit logs | EXG‑FCT‑001 |
| **EXG‑FCT‑003** | **Processus de qualification** – affectation d’un comité, saisie du résultat, mise à jour du statut du dossier (`QUALIFIE`, `NON_QUALIFIE`, `EN_ATTENTE`). | Formaliser le flux décisionnel des comités. | Procédure métier – MOA | Mandatory | Scénario BDD : `Given` dossier `When` comité vote `Then` statut mis à jour | EXG‑FCT‑002 |
| **EXG‑FCT‑004** | **Moteur de recherche plein‑texte** sur dossiers, experts, mots‑clés via ElasticSearch. | Faciliter la recherche d’informations par les agents. | Architecture – MOE | Mandatory | Tests performance (< 2 s) + Vérif. indexation (script `DossierMotsClefsSearchLoader`) | EXG‑FCT‑002 |
| **EXG‑FCT‑005** | **Génération de rapports BIRT** (extraction totale, pyramide d’âge, fréquence mots‑clés, etc.). | Produire les livrables attendus par la direction. | Documentation BIRT – MOE | Mandatory | Vérif. PDF/HTML conforme aux maquettes (rapports *.rptdesign) | EXG‑FCT‑002, EXG‑FCT‑004 |
| **EXG‑FCT‑006** | **Export CSV** de toute extraction (module `CsvExport`). | Besoin d’alimenter d’autres outils d’analyse. | Spécifications d’export – MOA | Desirable | Test de conformité du fichier (encodage UTF‑8, séparateur “;”) | EXG‑FCT‑005 |
| **EXG‑FCT‑007** | **Import de fichiers** (CSV, Excel) via le module `ImportsServices`. | Alimenter la base en masse (ex. import SPS). | Procédure d’import – MOE | Desirable | Test d’import (succès / échec, log) | EXG‑FCT‑001, EXG‑FCT‑002 |
| **EXG‑FCT‑008** | **Gestion des comptes utilisateurs** via Cerbère (authentification, rôle : `R_ADMIN`, `R_USER`). | Sécuriser l’accès aux données sensibles. | Politique de sécurité – RGPD | Mandatory | Test d’authentification, contrôle d’accès (RBAC) | Aucun |
| **EXG‑FCT‑009** | **Envoi de notifications e‑mail** (validation, rejet, rappel). | Informer les agents du statut de leurs dossiers. | Besoin métier – MOA | Mandatory | Test d’envoi SMTP (classe `CommonServices.sendMail`) | EXG‑FCT‑003 |
| **EXG‑FCT‑010** | **Gestion de la configuration applicative** (fichier `application‑config.xml`, variables d’environnement). | Permettre le paramétrage sans recompilation. | Documentation d’installation – MOE | Mandatory | Vérif. prise en compte des variables (`version`, `nbRowPage`) | Aucun |
| **EXG‑FCT‑011** | **Mise à jour de la base de données** via scripts SQL versionnés (`script/alter …`, `script/install`). | Garantir la cohérence du schéma entre les environnements. | DevOps – CI/CD | Mandatory | Exécution réussie du pipeline Maven/Docker (`docker‑compose up -d`) | Aucun |
| **EXG‑FCT‑012** | **Dashboard d’administration** (pages `admin/*` – statistiques, logs, gestion des utilisateurs). | Offrir un point de contrôle aux administrateurs. | UX – MOA | Optional | Test d’accès (seul R_ADMIN) | EXG‑FCT‑008 |
| **EXG‑FCT‑013** | **Gestion des mentions légales & RGPD** (pages `mentionsLegales.jsp`, `declaration-rgpd.md`). | Conformité légale. | Déclaration RGPD – MOA | Mandatory | Vérif. présence du lien dans le footer | Aucun |

*(La liste ci‑dessus n’est pas exhaustive ; d’autres exigences sont détaillées dans le tableau de traçabilité.)*  

---  

## 4️⃣ Exigences Non‑Fonctionnelles  

| ID | Catégorie | Description | Rationale | Priority | Verification |
|----|-----------|-------------|-----------|----------|--------------|
| **EXG‑NFR‑001** | **Performance** | Temps de réponse < 2 s pour toute requête de recherche affichant ≤ 100 résultats. | Garantir l’expérience utilisateur. | Mandatory | Tests de charge (JMeter) |
| **EXG‑NFR‑002** | **Scalabilité** | Le système doit supporter 200 utilisateurs simultanés sans dégradation (> 95 % de réponses < 2 s). | Anticiper la montée en charge. | Mandatory | Tests de stress |
| **EXG‑NFR‑003** | **Disponibilité** | SLA = 99,5 % de disponibilité mensuelle (excluant maintenance planifiée). | Continuité de service. | Mandatory | Monitoring (Grafana + Prometheus) |
| **EXG‑NFR‑004** | **Sécurité – Confidentialité** | Chiffrement TLS 1.2+ sur toutes les communications HTTP. | Protection des données personnelles (RGPD). | Mandatory | Scan SSL (Qualys) |
| **EXG‑NFR‑005** | **Sécurité – Intégrité** | Toutes les requêtes SQL passent par des paramètres préparés (prévention injection). | Sécuriser la BDD. | Mandatory | Analyse statique (SonarQube) |
| **EXG‑NFR‑006** | **Sécurité – Authentification** | Authentification unique via Cerbère + tokens JWT avec expiration ≤ 30 min. | Centraliser la gestion des accès. | Mandatory | Tests d’expiration de token |
| **EXG‑NFR‑007** | **Sécurité – Autorisation** | RBAC avec au minimum les rôles `R_ADMIN`, `R_USER`. | Limiter l’accès aux fonctions critiques. | Mandatory | Tests d’accès négatif |
| **EXG‑NFR‑008** | **Maintenabilité** | Couverture de tests unitaires ≥ 80 % (JUnit, Mockito). | Faciliter l’évolution. | Mandatory | Rapport SonarQube |
| **EXG‑NFR‑009** | **Portabilité** | L’application doit être exécutable sur tout serveur Docker ≥ 20.10 (Linux, Windows). | Simplifier le déploiement. | Mandatory | Tests d’image sur deux OS |
| **EXG‑NFR‑010** | **Compatibilité navigateur** | Support Chrome ≥ 90, Firefox ≥ 88, Edge ≥ 90. | Accessibilité utilisateurs. | Mandatory | Tests Selenium |
| **EXG‑NFR‑011** | **Traçabilité** | Chaque modification d’un dossier doit être historisée (table `DOSSIER_HISTO`). | Audits & conformité. | Mandatory | Requête SQL de vérification |
| **EXG‑NFR‑012** | **Auditabilité** | Logs applicatifs au format JSON, centralisés via ELK. | Analyse post‑incident. | Optional | Visualisation Kibana |
| **EXG‑NFR‑013** | **Conformité RGPD** | Droit à l’oubli : suppression définitive d’un expert après 5 ans d’inactivité. | Obligations légales. | Mandatory | Test de suppression et purge du volume DB |
| **EXG‑NFR‑014** | **Internationalisation** | Interface uniquement en français (i18n prévu pour futur). | Cohérence avec la cible. | Optional | Vérif. absence de chaînes codées en dur |

---  

## 5️⃣ Modèle de Données Conceptuel (UML)  

```mermaid
classdiagram;
    class Expert {
        +Long id;
        +String nom;
        +String prenom;
        +String email;
        +String fonction;
        +String statut   // ACTIVE / INACTIVE;
        +Date dateCreation;
    }
    class Dossier {
        +Long id;
        +String reference;
        +String etat   // EN_ATTENTE, QUALIFIE, REJETTE;
        +Date dateReception;
        +Date dateQualification;
        +String commentaire;
    }
    class Qualification {
        +Long id;
        +String libelle;
        +String description;
    }
    class Comité {
        +Long id;
        +String libelle;
        +String type   // DOMAINE / THESAURUS;
    }
    class MotCle {
        +Long id;
        +String libelle;
        +Integer niveau;
    }
    class Rapport {
        +Long id;
        +String type   // BIRT, CSV;
        +Date dateGeneration;
    }

    Expert "1" --> "0..*" Dossier : possède;
    Dossier "1" --> "0..1" Qualification : qualification;
    Dossier "1" --> "0..1" Comité : évaluéPar;
    Dossier "1" --> "0..*" MotCle : motsClés;
    Rapport "0..*" --> "1" Dossier : porteSur
```

*Le diagramme montre les entités principales et leurs relations (clé étrangère, cardinalité).*

---  

## 6️⃣ Modélisation des Comportements  

### 6.1 Diagramme de Cas d’Utilisation  

```mermaid
usecaseDiagram;
    actor Agent as Agent;
    actor Comité as Comité;
    actor Administrateur as Admin;
    rectangle SIREINES {
        Agent --> (Saisir un dossier)
        Agent --> (Consulter son profil)
        Agent --> (Exporter ses dossiers)
        Comité --> (Qualifier un dossier)
        Comité --> (Consulter les rapports)
        Admin --> (Gérer les utilisateurs)
        Admin --> (Configurer les import/export)
        Admin --> (Consulter les logs)
    }
```

### 6.2 Diagramme d’Activité – Processus de Qualification  

```mermaid
statediagram-v2;
    [*] --> SaisirDossier;
    SaisirDossier --> AffecterComité;
    AffecterComité --> AttenteVote;
    AttenteVote --> VotePositif : vote = QUALIFIE;
    AttenteVote --> VoteNegatif : vote = REJETTE;
    VotePositif --> MiseAJourStatut;
    VoteNegatif --> MiseAJourStatut;
    MiseAJourStatut --> Notification;
    Notification --> [*]
```

### 6.3 Diagramme de Séquence – Import de Fichier CSV  

```mermaid
sequencediagram;
    participant UI as "Interface Web"
    participant Ctrl as "ImportFichierAction"
    participant Svc as "ImportsServices"
    participant DB as "PostgreSQL"
    UI->>Ctrl: submit(file)
    Ctrl->>Svc: import(file)
    Svc->>DB: INSERT ... (batch)
    DB-->>Svc: OK / Errors;
    Svc->>Ctrl: Résultat (succès / échecs)
    Ctrl->>UI: Affichage du rapport
```

---  

## 7️⃣ Attributs des Exigences (Tableau)  

| Identifiant | Description | Source | Priority | Status | Verification Method | Risk | Stability |
|------------|-------------|--------|----------|--------|---------------------|------|-----------|
| EXG‑FCT‑001 | Gestion du référentiel d’experts | Analyse métier | Mandatory | Draft | Test fonctionnel UI + BDD | Medium | Stable |
| EXG‑FCT‑002 | Gestion des dossiers | Spécifications | Mandatory | Draft | Test d’intégration CRUD | High | Stable |
| EXG‑FCT‑003 | Processus de qualification | Procédure métier | Mandatory | Draft | BDD scénario | High | Stable |
| EXG‑FCT‑004 | Recherche plein‑texte | Architecture | Mandatory | Draft | Test performance <2 s | Medium | Stable |
| EXG‑FCT‑005 | Génération de rapports BIRT | Documentation BIRT | Mandatory | Draft | Vérif PDF/HTML | Medium | Stable |
| EXG‑NFR‑001 | Temps de réponse <2 s | SLA | Mandatory | Draft | Test charge JMeter | High | Stable |
| … | … | … | … | … | … | … | … |

---  

## 8️⃣ Matrice de Traçabilité (Exigences ↔ Artefacts)  

| Exigence | Artefacts de Code | Fichiers de Configuration | Scripts / SQL | Tests |
|----------|-------------------|---------------------------|--------------|-------|
| EXG‑FCT‑001 | `AgentsServices.java`, `AgentDetailAction.java` | `application-config.xml` (paramètre `nbRowPage`) | `crebas.sql` (table `AGENT`) | `AgentsServicesTest.java` |
| EXG‑FCT‑002 | `DossiersServices.java`, `DossierDetailAction.java` | `struts.xml` (action `/DossierDetail`) | `crebas.sql` (table `DOSSIER`) | `DossiersServicesIT.java` |
| EXG‑FCT‑003 | `QualificationDetailAction.java`, `SearchManagerInitializer.java` | `sireines-auth-config.xml` (rôles) | `alter_0.7.sql` (colonne `QUA_ID_RENOUVELLEMENT`) | `QualificationWorkflowTest.java` |
| EXG‑FCT‑004 | `SearchManager.java`, `DossierMotsClefsSearchLoader.java` | `elasticsearch.yml` | – | `SearchIntegrationTest.java` |
| EXG‑FCT‑005 | `BirtManagerImpl.java`, `Report.java` | `birt.tld` | – | `BirtReportGenerationTest.java` |
| EXG‑FCT‑006 | `CsvExport.java` | – | – | `CsvExportTest.java` |
| EXG‑FCT‑007 | `ImportFichierAction.java`, `ImportsServicesImpl.java` | – | `crebas.sql` (table `IMPORT`) | `ImportServiceTest.java` |
| EXG‑FCT‑008 | `ApplicationServletContextListener.java`, `CerbereUtil.java` | `sireines-auth-config.xml` | – | `AuthIntegrationTest.java` |
| EXG‑FCT‑009 | `CommonServicesImpl.java` (sendMail) | `mail.properties` | – | `MailServiceTest.java` |
| EXG‑FCT‑010 | `application-config.xml`, `.env` | – | – | – |
| EXG‑FCT‑011 | `script/*.sql` (alter, install) | `docker-compose.yml` (volumes) | `alter_0.7.sql` etc. | `DbMigrationTest.sh` |
| EXG‑FCT‑012 | `admin/*` (non présent dans l’extrait, à créer) | – | – | – |
| EXG‑FCT‑013 | `mentionsLegales.jsp`, `declaration-rgpd.md` | – | – | – |

*(Les références sont tirées des chemins du dépôt : `sireines-web/src/main/java/...`, `sireines-database/script/...`, `sireines-web/src/main/resources/...`.)*  

---  

## 9️⃣ Gestion des Exigences  

| Processus | Description | Responsable | Outil |
|----------|-------------|------------|------|
| **Capture** | Recueil des besoins auprès du MOA, rédaction dans le CCF. | Analyste fonctionnel | Confluence / GitLab‑Wiki |
| **Analyse & Priorisation** | Classification (Mandatory/Desirable/Optional) & affectation de priorité. | PO / PM | JIRA (backlog) |
| **Spécification** | Rédaction détaillée, attribution d’identifiants, définition des critères d’acceptation. | Analyste + Développeur | Markdown (CCF) |
| **Vérification** | Revue de conformité (peer‑review) – chaque exigence doit être **Correct**, **Unambiguous**, **Complete**, **Consistent**, **Verifiable**, **Modifiable**, **Traceable** (7 qualités ISO). | QA Lead | SonarQube, Review‑Board |
| **Validation** | Validation formelle par le MOA (signature) après réussite des tests d’acceptation. | MOA | GitLab‑MR approbation |
| **Gestion du changement** | Toute modification → création d’une *Change Request* (CR) → mise à jour du CCF, re‑triage, re‑validation. | Change Manager | ServiceNow / JIRA |
| **Suivi d’avancement** | Burndown chart, indicateur de % d’exigences implémentées. | Scrum Master | Azure DevOps |

---  

## 10️⃣ Validation & Vérification  

| Niveau | Méthode | Exigence(s) concernée(s) | Critère d’acceptation | Outil |
|--------|----------|---------------------------|-----------------------|-------|
| **Unité** | Tests unitaires (JUnit, Mockito) | Toutes les fonctions métier (EXG‑FCT‑001…013) | Couverture ≥ 80 % | JaCoCo, SonarQube |
| **Intégration** | Tests d’intégration (Spring Test, DBUnit) | CRUD dossiers / experts, import CSV | Opérations réussies sans erreur DB | Maven‑failsafe |
| **Système** | Tests fonctionnels (Selenium, Cucumber) | Scénarios BDD (`Given/When/Then`) | Parcours complet sans régression | Cucumber‑JVM |
| **Performance** | JMeter scripts, seuil 2 s | EXG‑NFR‑001, ‑002 | 95 % des requêtes < 2 s sous charge 200 U | JMeter |
| **Sécurité** | OWASP ZAP, SonarQube, tests d’injection | EXG‑NFR‑004/005/007/008 | Aucun vulnérabilité critique | ZAP, Sonar |
| **Acceptation** | Recette utilisateur (UAT) | Toutes les exigences fonctionnelles | Validation signée du MOA | Test‑UAT checklist |
| **Audit** | Revue de logs & traçabilité | EXG‑NFR‑011 | Historisation complète (audit‑log) | ELK Stack |

---  

## 11️⃣ Annexes  

### 11.1 Glossaire  

| Terme | Définition |
|-------|------------|
| **Dossier** | Demande de qualification d’un expert, contenant les informations administratives et le statut de la procédure. |
| **Qualification** | Décision du comité de domaine (qualifié / non‑qualifié). |
| **BIRT** | Business Intelligence and Reporting Tools – moteur de génération de rapports. |
| **Cerbère** | Service d’authentification et d’autorisation (SSO) utilisé par SIREINES. |
| **ElasticSearch** | Moteur de recherche plein‑texte intégré pour les requêtes sur dossiers et experts. |
| **Docker‑Compose** | Outil de orchestration des conteneurs (app, DB, pgAdmin). |
| **RGPD** | Règlement Général sur la Protection des Données. |

### 11.2 Références  

| N° | Document | Lien |
|---|----------|------|
| 1 | `README.md` (déploiement) | `gitlab/.../sireines/README.md` |
| 2 | `budget.md` (budget) | idem |
| 3 | `declaration-rgpd.md` | idem |
| 4 | `settings.xml` (Maven) | idem |
| 5 | `Dockerfile` & `docker‑compose.yml` | idem |
| 6 | `application‑config.xml` | idem |
| 7 | `sireines‑auth‑config.xml` | idem |
| 8 | `BirtManager.java` | `sireines‑web/src/main/java/.../BirtManager.java` |
| 9 | `SearchManagerInitializer.java` | idem |
|10 | `*.ftl` (templates Struts2) | `sireines‑web/src/main/resources/template/...` |
|11 | `script/*.sql` (mise à jour DB) | `sireines‑database/script/...` |
|12 | `pom.xml` (Maven) | idem |
|13 | `sonar‑project.properties` | idem |
|14 | `Recette/LivraisonSurIAAS.md` (tests techniques) | idem |

---  

## ✅ Conclusion  

Le présent Cahier des Charges Fonctionnel décrit de manière exhaustive les exigences fonctionnelles et non‑fonctionnelles du système **SIREINES**, leur traçabilité vers les artefacts existants (code source, scripts SQL, templates, configurations) ainsi que les critères de vérification et les processus de gestion des exigences.  

Il constitue le référentiel de référence pour :

* **Développement** – Implémentation conforme aux exigences, couverture de tests, respect des normes de qualité.  
* **Intégration / Déploiement** – Mise à jour contrôlée via les scripts versionnés et Docker.  
* **Exploitation** – Surveillance de la performance, de la sécurité et du respect du RGPD.  

Toute évolution future devra suivre le processus de gestion du changement décrit en section 9, afin de garantir la **cohérence**, la **qualité** et la **traçabilité** du système sur l’ensemble de son cycle de vie.  