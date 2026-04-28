# 📄 Cahier des Charges Fonctionnel (CCF) – **CausalisMP**  
*Gestion des accidents du travail et des maladies professionnelles*  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | **CausalisMP** |
| **Périmètre** | Application web (Struts 1) permettant la création, la consultation, la modification et l’export des dossiers d’accidents du travail et de maladies professionnelles, ainsi que la gestion des référentiels associés (grades, services, statuts, tâches prescrites, etc.). |
| **Environnement technique** | - Java 8, Maven multi‑module  <br> - Struts 1 (Action / ActionForm) <br> - Castor JDO (XML‑mapping) <br> - Oracle (JNDI datasource `jdbc/userDScausalis`) <br> - Web‑services externes (StubWS) pour la synchronisation des référentiels <br> - JSP + TagLib personnalisés |
| **Objectifs stratégiques** | 1. Centraliser les informations d’accident et de maladie professionnelle. <br> 2. Garantir la traçabilité et la conformité réglementaire (RGPD, RGS). <br> 3. Fournir des indicateurs statistiques fiables pour le pilotage RH. <br> 4. Automatiser la synchronisation des référentiels (grades, services, etc.) avec les systèmes externes (Rehucit, Cerbere). |
| **Livrables** | - WAR `causalismp-web` (déploiement sur serveur d’applications). <br> - Scripts de migration DB (`causalismp-database/script`). <br> - Documentation d’installation & d’utilisation (module `causalismp-doc`). <br> - Packages sources (`causalismp-deployment/assembly‑sources.zip`). |
| **Périmètre fonctionnel** | **Inclus** : gestion des dossiers accidents & maladies, gestion des effectifs, consultation & export de statistiques, gestion des référentiels, synchronisation, authentification, audit des actions. <br> **Exclu** : modules de paie, gestion des contrats, reporting avancé hors statistiques de base. |

---  

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271)

> **Fonction de Service (FS)** = **« quoi »** (décrit le besoin métier, pas la solution technique).  

| # | Fonction de Service | Description (quoi) | Critères d’appréciation | Importance (pondération %) | Contraintes |
|---|---|---|---|---|---|
| **FS‑01** | **Saisie d’un dossier d’accident** | Permettre à un gestionnaire d’enregistrer toutes les informations d’un accident du travail (date, lieu, nature, gravité, lésions, causes, effectifs impliqués). | - Enregistrement complet en < 5 min.<br>- Validation de la cohérence des champs (ex. : année naissance ≤ année accident).<br>- Génération d’un identifiant unique. | Respect du schéma DB (`ACCIDENT`), conformité RGPD (consentement). |
| **FS‑02** | **Saisie d’un dossier de maladie professionnelle** | Enregistrer les informations d’une maladie liée au travail (date de déclaration, type, service, grade, effectif). | - Enregistrement complet en < 5 min.<br>- Vérification de l’appartenance du salarié à l’entreprise. | Même contraintes que FS‑01. |
| **FS‑03** | **Gestion des effectifs** | Créer, modifier et rechercher les effectifs (personnes, grade, service, sexe, année de naissance) associés aux dossiers. | - Recherche par critères (service, grade, tranche d’âge) < 2 s.<br>- Pas de doublons (un même effectif ne doit pas être saisi deux fois). | Utilisation du `EffectifComparator` (égalité stricte). |
| **FS‑04** | **Consultation des statistiques** | Produire des indicateurs agrégés (nombre d’accidents / grade, taux d’incidence, évolution temporelle). | - Temps de génération < 3 s.<br>- Export au format CSV / OpenOffice. | Les calculs doivent être reproductibles (pas de valeurs aléatoires). |
| **FS‑05** | **Export des dossiers** | Exporter les dossiers (accident ou maladie) au format OpenOffice (ODS) ou PDF. | - Export complet sans perte de champs.<br>- Taille du fichier < 5 Mo. | Utilisation de `CausalisExportManager` & `FichierOpenOffice`. |
| **FS‑06** | **Gestion des référentiels (grades, services, statuts, tâches… )** | Créer, mettre à jour et consulter les tables de référence utilisées dans les dossiers. | - Mise à jour en < 1 min.<br>- Historisation des changements. | Les tables sont gérées par les *ReferenceService* (lecture uniquement dans la version actuelle). |
| **FS‑07** | **Synchronisation avec les systèmes externes** | Mettre à jour les référentiels (ex. : `TranscodageGrade`) depuis les web‑services externes (StubWS). | - Taux de réussite ≥ 99 % des lignes insérées.<br>- Log détaillé des erreurs. | Implémentation du contrat `SynchronizeService`. |
| **FS‑08** | **Authentification & gestion de session** | Authentifier les utilisateurs, gérer la ré‑authentification (`reauth.jsp`). | - Authentification en < 2 s.<br>- Session expirée automatiquement après 30 min d’inactivité. | Conformité aux exigences de sécurité (RSSI, RGPD). |
| **FS‑09** | **Gestion des alertes & warnings** | Afficher les messages d’avertissement (ex. : contraintes de saisie, erreurs métier). | - Message visible immédiatement.<br>- Couleur et icône standardisées. | Utilisation de `ActionWarning` & `WarningsTag`. |
| **FS‑10** | **Audit & traçabilité** | Enregistrer chaque création/modification/suppression de dossier avec l’identifiant de l’utilisateur. | - Log d’audit complet (date, heure, utilisateur, action). | Conformité aux exigences légales de traçabilité. |

---  

## 3️⃣ Acteurs et parties prenantes  

| Rôle | Description | Besoins spécifiques |
|---|---|---|
| **MOA (Maîtrise d’Ouvrage)** | Direction RH, service prévention, DSI. | Définir les processus, valider les exigences fonctionnelles, assurer la conformité légale. |
| **MOE (Maîtrise d’Œuvre)** | Équipe de développement (développeurs, architecte, testeurs). | Disposer d’un cahier des charges clair, d’un environnement de test, d’indicateurs de qualité (SonarQube). |
| **Gestionnaire RH (utilisateur métier)** | Crée et suit les dossiers accidents/maladies, consulte les statistiques. | Interface ergonomique, recherche rapide, export de données, assistance contextuelle. |
| **Agent de prévention** | Saisit les causes, effectifs, vérifie la conformité. | Accès aux listes de références (grades, services), validation des règles métier. |
| **Manager / Responsable de service** | Consulte les indicateurs de son service, valide les dossiers. | Vue filtrée par service, tableau de bord synthétique. |
| **Auditeur interne** | Vérifie la traçabilité et la conformité RGPD. | Accès en lecture aux logs d’audit, export des historiques. |
| **RSSI (Responsable Sécurité des Systèmes d’Information)** | Garantit la sécurité des flux et des données. | Authentification forte, chiffrement des communications, respect du RGS. |
| **Intégrateur externe (Rehucit, Cerbere)** | Fournit les référentiels via web‑services. | API stable, contrat de synchronisation (`SynchronizeService`). |

---  

## 4️⃣ Cas d’usage (Use Cases)

### 4.1 Diagramme de cas d’utilisation (UML)  

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#0366d6','edgeLabelBackground':'#f6f8fa','nodeBorder':'#0366d6','clusterBkg':'#e1e4e8'}}%%%%%%%%%%%%%%%%%%%%%%%%}%%
usecaseDiagram;
    title Cas d’utilisation – CausalisMP;
    actor Gestionnaire as G;
    actor Agent as A;
    actor Manager as M;
    actor Auditeur as AU;
    actor RSSI as R;
    G --> (Créer dossier accident)
    G --> (Créer dossier maladie)
    G --> (Rechercher effectif)
    G --> (Consulter statistiques)
    G --> (Exporter dossier)

    A --> (Mettre à jour référentiels)
    A --> (Synchroniser référentiels)

    M --> (Visualiser tableau de bord)
    M --> (Valider dossier)

    AU --> (Consulter audit)
    R --> (Gérer authentification)
    R --> (Détecter anomalies de sécurité)

    (Créer dossier accident) --> \(Valider saisie)
    (Créer dossier maladie) --> \(Valider saisie)
    (Exporter dossier) --> \(Générer fichier ODS)
    (Synchroniser référentiels) --> \(Appeler web‑service)
```

### 4.2 Description détaillée des cas d’usage  

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **CU‑01** | Créer dossier d’accident | Gestionnaire | 1. L’utilisateur ouvre le formulaire *Dossier Accident*.<br>2. Saisit les champs obligatoires (date, lieu, nature, grade, effectif).<br>3. Clique **Enregistrer**.<br>4. Le système génère un identifiant et persiste le dossier. | - **CA‑01** : Champ manquant → affichage d’un warning (ActionWarning).<br>- **CA‑02** : Date future → rejet avec message d’erreur.<br>- **CA‑03** : Conflit d’identifiant → génération d’un nouvel ID. | L’utilisateur est authentifié, le formulaire est chargé. | Le dossier est stocké en base, visible dans la liste des dossiers. |
| **CU‑02** | Créer dossier de maladie professionnelle | Gestionnaire | Identique à CU‑01 mais avec le formulaire *Dossier Maladie*. | - **CA‑04** : Type de maladie non reconnu → message d’erreur.<br>- **CA‑05** : Aucun effectif associé → proposition de création d’un effectif. | Authentification, accès au formulaire. | Dossier persistant, indexé par type de maladie. |
| **CU‑03** | Rechercher un effectif | Gestionnaire / Agent | 1. L’utilisateur ouvre la page *Effectifs*.<br>2. Saisit les critères (service, grade, tranche d’âge).<br>3. Lance la recherche.<br>4. Le système renvoie la liste correspondante. | - **CA‑06** : Aucun résultat → affichage d’un message « Aucun effectif trouvé ». | L’utilisateur dispose des droits de lecture sur les effectifs. | Liste d’effectifs affichée (ou message vide). |
| **CU‑04** | Consulter les statistiques | Gestionnaire / Manager | 1. L’utilisateur sélectionne le module *Statistiques*.<br>2. Choisit la période et le type de tableau (accidents / maladies).<br>3. Le système calcule et affiche les indicateurs. | - **CA‑07** : Période vide → utilisation de la période par défaut (année courante). | Accès aux tables de référence, données d’historique disponibles. | Tableau de bord affiché, export possible. |
| **CU‑05** | Exporter un dossier | Gestionnaire | 1. Depuis la vue détaillée du dossier, l’utilisateur clique **Exporter**.<br>2. Choisit le format (ODS, PDF).<br>3. Le système génère le fichier et propose le téléchargement. | - **CA‑08** : Erreur de génération (ex. : problème de fichier) → affichage d’un warning et journalisation. | Dossier complet, droits d’export. | Fichier exporté, journal d’export mis à jour. |
| **CU‑06** | Synchroniser les référentiels | Agent | 1. L’agent lance la tâche *Synchroniser* depuis le menu.<br>2. Le système appelle les web‑services externes (StubWS).<br>3. Les nouvelles lignes sont insérées en base. | - **CA‑09** : Web‑service indisponible → abort, log d’erreur, message à l’utilisateur.<br>- **CA‑10** : Ligne déjà présente → filtrage via `TranscodageGradePredicate`. | Connexion réseau, droits d’accès aux WS. | Référentiels à jour, log de synchronisation. |
| **CU‑07** | Authentifier / Re‑authentifier | Tous les utilisateurs | 1. L’utilisateur saisit login / mot de passe.<br>2. Le système valide les credentials via Cerbere.<br>3. En cas d’inactivité, la page *reauth.jsp* est affichée, l’utilisateur se reconnecte. | - **CA‑11** : Identifiants invalides → message d’erreur.<br>- **CA‑12** : Session expirée → redirection vers *reauth.jsp*. | Aucun (accès public à la page de login). | Session valide, token d’authentification créé. |
| **CU‑08** | Auditer les actions | Auditeur | 1. L’auditeur accède à la page *Audit*.<br>2. Filtre par période, utilisateur, type d’action.<br>3. Visualise/exports les logs. | - **CA‑13** : Aucun log trouvé → message informatif. | Accès en lecture aux tables d’audit. | Logs affichés/exportés. |

---  

## 5️⃣ Processus métier (BPMN)  

> Processus « Création et validation d’un dossier d’accident »  

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#0366d6','edgeLabelBackground':'#f6f8fa','nodeBorder':'#0366d6','clusterBkg':'#e1e4e8'}}%%%%%%%%%%%%%%%%%%%%%%%%}%%
bpmnDiagram;
    participant Gestionnaire;
    participant Système;
    participant Responsable;
    startEvent(id="start", name="Début")
    task(id="saisir", name="Saisir le dossier accident")
    exclusiveGateway(id="gw1", name="Données valides ?")
    task(id="enregistrer", name="Enregistrer le dossier")
    task(id="notif", name="Notifier le responsable")
    task(id="valider", name="Valider le dossier")
    endEvent(id="end", name="Fin")

    startEvent --> saisir --> gw1;
    gw1 -->|Oui| enregistrer --> notif --> valider --> endEvent;
    gw1 -->|Non| task(id="corriger", name="Corriger les erreurs") --> saisir
```

*Points de contrôle* :  
- **GW1** : Validation des règles métier (ex. : année naissance ≤ année accident).  
- **Task « Notifier le responsable »** : Envoi d’un e‑mail via le service de messagerie interne.  

---  

## 6️⃣ Règles métier et contraintes fonctionnelles  

| # | Règle métier (format conditionnel) | Description détaillée | Source code / référence |
|---|---|---|---|
| **R‑01** | `if (effectif.annee_naissance >= anneeSynchro - 20) then tranche = '1'` | Détermination de la tranche d’âge (1 = 0‑20 ans). Implémenté dans `TrancheAgeHelper.makeTrancheAge`. | `TrancheAgeHelper.java` |
| **R‑02** | `if (grade.codeGradeRehucit not in TranscodageGrade table) then insert` | Insertion d’un grade uniquement s’il n’existe pas déjà (predicate `TranscodageGradePredicate`). | `TranscodageGradePredicate.java` |
| **R‑03** | `ACCIDENT.ACC_REPETITIF = 1` pour les accidents répétés (script `20190403‑…sql`). | Marque l’accident comme récurrent pour le même grade. | `20190403-causalis-1.5.1.sql` |
| **R‑04** | `if (date > today) then reject` | Interdiction de saisir une date future. | Validation côté formulaire (`DateValidator`). |
| **R‑05** | `if (effectif1 != null && effectif2 != null && all fields equal) then compare() == 0` | Comparaison d’effectifs via `EffectifComparator`. | `EffectifComparator.java` |
| **R‑06** | `if (user.session.inactive > 30 min) then redirect to reauth.jsp` | Gestion de l’expiration de session. | `reauth.jsp`. |
| **R‑07** | `if (grade.codeGroupementGrade is null) then warning` | Le champ `codeGroupementGrade` est obligatoire pour les grades. | `Grade.java` (attribut). |
| **R‑08** | `if (DossierAccidentIncomplet) then saisieTerminee = 0` | Un dossier incomplet empêche la clôture. | `DossierAccidentIncomplet.java`. |
| **R‑09** | `if (user.role not in [Gestionnaire, Agent, Manager]) then deny access` | Contrôle d’accès basé sur les rôles. | TagLib / Struts `Action` (non montré). |
| **R‑10** | `if (TechnicalException) then log & display warning` | Gestion centralisée des erreurs techniques. | `TechnicalException.java`. |

---  

## 7️⃣ Parcours utilisateurs (User Journey)

### 7.1 Parcours « Gestionnaire crée un dossier d’accident »

| Étape | Action de l’utilisateur | Système | Points de contrôle / feedback |
|---|---|---|---|
| 1️⃣ | Se connecte (login / mot de passe) | Authentifie via `Cerbere`, crée la session. | Message d’erreur en cas d’identifiants invalides. |
| 2️⃣ | Clique sur le menu **« Créer Accident »** | Charge la page `editionDossierPage1.jsp`. | Affichage du formulaire, pré‑remplissage du service (si connu). |
| 3️⃣ | Saisit les champs obligatoires (date, lieu, nature, grade, effectif). | Validation côté client (JavaScript) puis côté serveur (`DateValidator`). | Highlight des champs manquants, warning via `ActionWarning`. |
| 4️⃣ | Clique **Enregistrer**. | `EditionDossierAction` persiste le dossier via `DossierAccidentService`. | Retour `success` → affichage du récapitulatif. |
| 5️⃣ | Consulte le récapitulatif, décide de **Clôturer**. | Met à jour `saisieTerminee = 1`. | Message de confirmation. |
| 6️⃣ | Option **Exporter** le dossier. | `CausalisExportManager` génère le fichier ODS. | Téléchargement du fichier. |
| 7️⃣ | Se déconnecte ou reste inactif → `reauth.jsp`. | Session invalidée après 30 min. | Redirection vers la page de ré‑authentification. |

### 7.2 Parcours « Agent synchronise les grades »

| Étape | Action | Système | Feedback |
|---|---|---|---|
| 1 | Lance **« Synchroniser les référentiels »** | `SynchronizeService` appelle les WS via `WSClientGrade`. | Barre de progression, log d’exécution. |
| 2 | Le système récupère la liste des grades externes. | `WSClientGrade` → parse la réponse. | Affichage du nombre de grades à insérer. |
| 3 | `TranscodageGradePredicate` filtre les déjà présents. | Insertion conditionnelle via `TranscodageGradeService`. | Message « X nouvelles lignes insérées ». |
| 4 | En cas d’erreur (WS indisponible) | Capture `WSException`, logue l’erreur. | Affichage d’un warning, proposition de ré‑essai. |

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)

> Diagramme de classes (UML) représentant les entités métier et leurs relations principales.  

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#0366d6','edgeLabelBackground':'#f6f8fa','nodeBorder':'#0366d6','clusterBkg':'#e1e4e8'}}%%%%%%%%%%%%%%%%%%%%%%%%}%%
classDiagram
    class Utilisateur {
        +int id;
        +String login;
        +String nom;
        +String role;

    class DossierAccident {
        +int id;
        +Date dateAccident;
        +String lieu;
        +String nature;
        +String gravite;
        +int saisieTerminee;

    class DossierMaladie {
        +int id;
        +Date dateDeclaration;
        +String typeMaladie;
        +int saisieTerminee;

    class Effectif {
        +int id;
        +int anneeNaissance;
        +String sexe;
        +Grade grade;
        +Service service;

    class Grade {
        +int id;
        +String libelle;
        +int codeGroupementGrade;

    class Service {
        +int id;
        +String libelleCourt;
        +String libelleLong;

    class Statistiques {
        +int id;
        +String type (ACC/MA)
        +int annee;
        +int valeur;

    class TranscodageGrade {
        +String codeGradeRehucit;
        +String macro;

    Utilisateur "1" --> "*" DossierAccident : crée >
    Utilisateur "1" --> "*" DossierMaladie : crée >
    DossierAccident "1" --> "*" Effectif : concerne >
    DossierMaladie "1" --> "*" Effectif : concerne >
    Effectif "1" --> "1" Grade : possède >
    Effectif "1" --> "1" Service : appartient à >
    Grade "1" --> "1" TranscodageGrade : ↔ (synchronisation) >
    Service "1" --> "*" Statistiques : génère >
```

*Remarques* :  
- `Effectif` est partagé entre accidents et maladies.  
- `TranscodageGrade` assure le mapping entre le grade Causalis et le grade Rehucit (synchronisation).  
- Les tables de référence (`Grade`, `Service`, `Statut`, `TachePrescrite`, …) sont toutes des **TablesReferences** (classe abstraite non affichée).  

---  

## 9️⃣ Critères d’acceptation et validation  

| Fonction de Service | Critère d’acceptation (exemple) | Méthode de validation | Priorité (MoSCoW) | Responsable |
|---|---|---|---|---|
| **FS‑01** Saisie dossier accident | Enregistrement complet en < 5 min, identifiant unique, champs obligatoires remplis. | Tests fonctionnels automatisés (Selenium) + revue de code. | **M** (Must) | Équipe de tests fonctionnels |
| **FS‑02** Saisie dossier maladie | Même critère que FS‑01 + vérification du lien avec un effectif existant. | Tests unitaires (`DossierMaladieServiceTest`). | **M** | Équipe de tests unitaires |
| **FS‑03** Gestion des effectifs | Recherche < 2 s, pas de doublons, comparaison via `EffectifComparator`. | Jeu de données de 10 000 effectifs, mesure de performance. | **S** (Should) | QA Performance |
| **FS‑04** Statistiques | Temps de génération < 3 s, export CSV/ODS conforme au modèle. | Tests d’intégration (`StatistiquesActionTest`). | **M** | PO / QA |
| **FS‑05** Export dossiers | Fichier généré < 5 Mo, toutes les colonnes présentes, nommage `dossier_<id>.ods`. | Comparaison des hashes avant/après export. | **M** | Développeur Export |
| **FS‑06** Référentiels | Mise à jour < 1 min, historique des modifications. | Audit DB, comparaison avant/après. | **C** (Could) | DBA |
| **FS‑07** Synchronisation | Taux de réussite ≥ 99 %, log d’erreurs < 0,5 % des lignes. | Tests d’intégration (`SynchronizeServiceTest`). | **M** | Intégrateur |
| **FS‑08** Authentification | Authentification < 2 s, session expirée après 30 min, logs d’accès. | Tests de charge (`JMeter`) + revue de sécurité. | **M** | RSSI |
| **FS‑09** Warnings | Message d’avertissement affiché immédiatement, style uniforme. | Tests UI (`ActionWarning` affichage). | **S** | UI/UX Designer |
| **FS‑10** Audit | Chaque action (CRUD) journalisée avec timestamp, utilisateur, type d’action. | Requête sur table `AUDIT_LOG`. | **M** | Responsable conformité |

---  

## 🔟 Annexes  

### A. Glossaire métier  

| Terme | Définition |
|---|---|
| **Accident du travail** | Événement imprévu sur le lieu de travail entraînant une blessure ou un dommage corporel. |
| **Maladie professionnelle** | Pathologie reconnue comme liée à l’activité professionnelle. |
| **Effectif** | Personne physique employée, identifiée par son grade, service, année de naissance et sexe. |
| **Grade** | Niveau hiérarchique ou classification du personnel (ex. : Agent, Technicien, Cadre). |
| **Service** | Unité organisationnelle (ex. : Administration, Production). |
| **Statut** | État du dossier (ex. : En cours, Validé, Clôturé). |
| **Tâche prescrite** | Action obligatoire à réaliser suite à un accident (ex. : visite médicale). |
| **TranscodageGrade** | Mapping entre le code de grade interne et le code du référentiel externe Rehucit. |
| **SynchronizeService** | Service métier qui synchronise les référentiels internes avec les services externes. |
| **Cerbere** | Composant d’authentification interne (déconnexion, logoff). |
| **StubWS** | Bibliothèque contenant les stubs des web‑services externes (ex. : grade, service). |
| **Bouchon** | Implémentation factice (stub) utilisée en phase de test. |

### B. Référentiels et normes applicables  

| Référence | Description |
|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences – Processus de spécification et de gestion des exigences. |
| **RGPD** | Règlement général sur la protection des données – exigences de confidentialité et de traçabilité. |
| **RGS** | Référentiel Général de Sécurité – exigences d’authentification et de chiffrement. |
| **ISO 9001** | Management de la qualité – exigences de traçabilité et d’audit. |

### C. Historique des versions du document  

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 2024‑04‑28 | ChatGPT (OpenAI) | Première rédaction du CCF complet selon NF EN 16271 & ISO 29148. |
| 1.1 | – | – | À venir (ajout de retours MOA/MOE). |

---  

*Document généré en conformité avec la norme NF EN 16271 et le standard ISO/IEC/IEEE 29148, prêt à être utilisé dans VS Code ou Obsidian.*  