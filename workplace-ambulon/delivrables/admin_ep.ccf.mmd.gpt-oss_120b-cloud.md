# 📄 Cahier des Charges Fonctionnel (CCF) – **admin_ep**  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | **admin_ep** – Administration des établissements publics (EP) |
| **Objectif principal** | Mettre à disposition une application web permettant **l’enregistrement, la consultation, la mise à jour et le suivi** des membres des conseils d’administration (mandats) des établissements publics placés sous la tutelle du ministère de la Transition écologique et solidaire (MTES‑MCT). |
| **Enjeux métier** | - Garantir la **fiabilité** et la **traçabilité** des données de gouvernance (mandats, pièces associées). <br> - Faciliter la **recherche** d’un administrateur ou d’un établissement. <br> - Automatiser la **mise à jour** des données à partir du JORF. <br> - Alerter les responsables en cas d’**échéance de mandat**. |
| **Enjeux techniques** | - Compatibilité avec **Tomcat 10** et **PostgreSQL 15** (montée de version). <br> - Déploiement **containerisé** (Docker) et **IaaS**. <br> - Authentification via le **SSO Cerbère**. |
| **Périmètre fonctionnel** | **Inclus** : <br> • Gestion des administrateurs (CRUD). <br> • Gestion des établissements, collèges, charges, ministères, directions. <br> • Gestion des mandats (type, période, pièces). <br> • Recherche multi‑critères. <br> • Tableau de bord statistique. <br> • Notification d’échéance mandat (mail). <br> • Import automatique depuis le JORF. <br> • Archivage des mandats expirés. <br> **Exclus** : <br> • Gestion des budgets ou de la facturation des EP. <br> • Fonctionnalités de workflow avancé (validation multi‑étapes). |
| **Livrables attendus** | - Application Web (WAR) + scripts SQL d’initialisation. <br> - Dockerfile & compose. <br> - Documentation utilisateur & technique. <br> - Jeux de tests d’acceptation. |
| **Contraintes** | - Respect des référentiels **RGPD**, **DICT**, **RGS**. <br> - Hébergement sur le **datacenter ministériel** (Paris La Défense). <br> - Niveau de service (disponibilité ≥ 99 %). |
| **Références** | - NF EN 16271 (expression fonctionnelle du besoin). <br> - ISO/IEC/IEEE 29148 :2018 (ingénierie des exigences). <br> - Documentation fournie (wiki, *.md, scripts SQL). |

---  

## 2️⃣ Expression fonctionnelle du besoin *(NF EN 16271)*  

> **Fonction de service** = « Ce que le système doit faire » (le **quoi**).  

| N° | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Pondération | Contraintes |
|---|---|---|---|---|---|
| **FS‑1** | **Gestion des administrateurs** | Créer, lire, mettre à jour, supprimer (CRUD) les fiches d’administrateurs et leurs profils (Cerbère). | - Temps moyen de création ≤ 2 min.<br>- Taux d’erreur ≤ 0,5 % sur les opérations CRUD.<br>- Historisation de chaque modification (audit). | 15 % | - Rôle obligatoire (admin, gestionnaire, etc.). |
| **FS‑2** | **Gestion des établissements publics** | Saisir et maintenir les informations (SIREN, libellé, type d’instance, collèges associés). | - Complétude des champs ≥ 95 %.<br>- Recherche par SIREN ou libellé en ≤ 3 s. | 10 % | - Un établissement ↔ un type d’instance (FK). |
| **FS‑3** | **Gestion des mandats** | Enregistrer les mandats (type : titulaire/suppléant), période, pièces jointes, mode de nomination. | - Validation de la cohérence dates (début < fin).<br>- Pièces obligatoires ≥ 1 pour chaque mandat. | 15 % | - Un administrateur ne peut occuper deux mandats du même type sur le même EP simultanément. |
| **FS‑4** | **Recherche et consultation** | Moteur de recherche multi‑critères (nom, EP, collège, charge, mandat, période). | - Temps de réponse ≤ 2 s pour 95 % des requêtes.<br>- Précision ≥ 90 % (rappel + précision). | 12 % | - Utilisation de l’indexation full‑text (PostgreSQL). |
| **FS‑5** | **Import automatique JORF** | Lire les flux JORF (XML/.tar.gz), extraire les nominations, les intégrer dans la base. | - Couverture ≥ 95 % des nouvelles nominations détectées.<br>- Latence d’import ≤ 24 h après publication JORF. | 13 % | - Scheduler (Quartz) configuré, logs détaillés. |
| **FS‑6** | **Statistiques & reporting** | Générer des indicateurs (nombre d’administrateurs, mandats actifs, expirations, répartition par collège, etc.). | - Tableau de bord actualisé en ≤ 5 min.<br>- Export CSV/Excel disponible. | 8 % | - Respect du format RGPD (anonymisation possible). |
| **FS‑7** | **Notification d’échéance** | Envoyer un email au référent dès qu’un mandat arrive à **+30 jours** de son expiration. | - Taux de délivrabilité ≥ 98 %.<br>- Délai d’envoi ≤ 1 h après le déclencheur. | 7 % | - Template mail validé par la DG de tutelle. |
| **FS‑8** | **Authentification & habilitation** | Authentifier les utilisateurs via Cerbère, appliquer les droits (lecture, écriture, admin). | - Temps d’authentification ≤ 1 s.<br>- Aucun accès non autorisé détecté (audit). | 10 % | - SSO Cerbère, conformité RGS. |
| **FS‑9** | **Archivage des mandats expirés** | Déplacer les mandats expirés (et leurs pièces) vers une zone d’archive consultable. | - Conservation ≥ 10 ans.<br>- Accès en lecture uniquement. | 5 % | - Stockage séparé (ex. S3‑compatible). |
| **FS‑10** | **Gestion des référentiels** | CRUD des référentiels (type mandat, type instance, mode nomination, charge, ministère, direction, collège, synonymes). | - Cohérence référentiels (FK) ≥ 100 %. | 5 % | - Versionning des référentiels (historique). |

---

## 3️⃣ Acteurs et parties prenantes  

| Acteur | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **MOA – SG/SPES** | Maîtrise d’Ouvrage | Piloter le projet, valider les livrables, garantir la conformité fonctionnelle. | Cahier des charges détaillé, suivi de projet, reporting. |
| **MOE – SG/SNUM/PNM/DPNM3/BPN** | Maîtrise d’Œuvre | Concevoir, développer, tester, déployer l’application. | Spécifications techniques, accès aux environnements, documentation API. |
| **Prestataire – CGI** | Développeur / intégrateur | Réaliser le développement et la mise en production. | Accès aux référentiels métiers, supports fonctionnels. |
| **DG de tutelle (DMES‑MCT)** | Responsable fonctionnel | Suivre la gouvernance des EP, valider les données. | Tableau de bord, export réglementaire, alertes d’échéance. |
| **Opérateurs (services du ministère)** | Utilisateurs opérationnels | Saisir / mettre à jour les administrateurs, gérer les mandats. | Interface ergonomique, droits d’édition, recherche rapide. |
| **Gestionnaires de données (SI)** | Administrateur technique | Installer, configurer, monitorer l’application. | Accès serveur, scripts de déploiement, logs. |
| **Utilisateurs externes (ex. équipe audit)** | Consultation | Accéder aux statistiques et aux archives. | Accès en lecture, export CSV, respect RGPD. |
| **Système Cerbère** | SSO / Authentification | Authentifier les utilisateurs et fournir les attributs de profil. | Intégration SAML/OIDC, mapping des profils. |
| **Moteur JORF** | Source de données | Fournir les arrêtés de nomination. | Accès aux flux (RSS, .tar.gz), parsing fiable. |

---

## 4️⃣ Cas d’usage (Use Cases)  

### 4.1 Diagramme de cas d’utilisation (UML)  

```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#003366','edgeLabelBackground':'#ffffff','nodeBorder':'#003366'}}%%%%%%%%%%%%%%%%%%%%%%%%}%%
usecaseDiagram;
    actor Opérateur as Op;
    actor DG de tutelle as DG;
    actor Système Cerbère as Cerb;
    actor Moteur JORF as JORF;
    rectangle admin_ep {
        Op --> (Créer/Mettre à jour Administrateur)
        Op --> (Créer/Mettre à jour Établissement)
        Op --> (Gérer Mandat)
        Op --> (Rechercher)
        Op --> (Consulter Statistiques)

        (Gérer Mandat) --> \(Envoyer Notification d’échéance) : <<include>>
        (Gérer Mandat) --> \(Archiver Mandat expiré) : <<include>>

        DG --> (Consulter Statistiques)
        DG --> (Consulter Archives)

        Cerb --> (Authentifier utilisateur) : <<extend>>
        JORF --> (Importer nominations JORF) : <<include>>

```

### 4.2 Liste détaillée des cas d’usage  

| N° | Nom du cas d’usage | Acteur(s) principal(s) | Description (scénario nominal) | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **CU‑1** | Créer/Mettre à jour Administrateur | Opérateur | 1. L’opérateur s’authentifie.<br>2. Il accède à la page “Administrateur”.<br>3. Il remplit le formulaire (nom, prénom, email, profil Cerbère, établissements associés).<br>4. Il valide. | - **AE‑1** : Le champ obligatoire manquant → affichage d’un message d’erreur.<br>- **AE‑2** : L’utilisateur n’a pas le droit d’écrire → redirection vers page d’erreur 403. | L’utilisateur est authentifié et possède le rôle « Gestionnaire ». | La fiche administrateur est créée ou mise à jour, un audit est enregistré. |
| **CU‑2** | Créer/Mettre à jour Établissement | Opérateur | 1. Accès à la section “Établissements”.<br>2. Saisie du SIREN, libellé, type d’instance, collèges, etc.<br>3. Validation. | - **AE‑3** : SIREN déjà existant → message “Établissement déjà présent”. | L’utilisateur est authentifié. | L’établissement est persistant, les référentiels liés sont mis à jour. |
| **CU‑3** | Gérer Mandat (CRUD) | Opérateur | 1. Sélection d’un administrateur.<br>2. Ouverture de l’onglet “Mandats”.<br>3. Ajout d’un mandat (type, dates, mode, pièces).<br>4. Enregistrement. | - **AE‑4** : Dates incohérentes (début > fin) → rejet.<br>- **AE‑5** : Pièce manquante → avertissement. | L’administrateur et l’établissement existent. | Le mandat est enregistré, le planning d’échéance est (re)calculé. |
| **CU‑4** | Recherche d’informations | Opérateur / DG | 1. Saisie d’un ou plusieurs critères (nom, EP, collège, charge, période).<br>2. Lancement de la recherche.<br>3. Résultats affichés avec filtres. | - **AE‑6** : Aucun résultat → affichage “Aucun résultat”. | Aucun (accessible à tout utilisateur authentifié). | Les résultats sont présentés, export possible. |
| **CU‑5** | Importation JORF (automatique) | Moteur JORF (scheduler) | 1. Le scheduler déclenche le job chaque jour.<br>2. Le job télécharge le flux JORF.<br>3. Le parseur extrait les nominations.<br>4. Les nouvelles entrées sont insérées (ou mises à jour). | - **AE‑7** : Flux indisponible → log d’erreur, nouvelle tentative 6 h plus tard.<br>- **AE‑8** : Format invalide → alerte admin. | Le serveur a accès à internet, le job est configuré. | Les nominations JORF sont synchronisées, logs mis à jour. |
| **CU‑6** | Notification d’échéance | Scheduler | 1. Chaque nuit, le job identifie les mandats expirant dans +30 jours.<br>2. Un email est généré et envoyé au référent. | - **AE‑9** : Mail non délivré → mise en file d’attente, alerte admin. | Le référent possède une adresse mail valide. | Le mail est envoyé, l’événement est journalisé. |
| **CU‑7** | Consultation Statistiques | DG / Opérateur | 1. Accès au tableau de bord.<br>2. Sélection d’un indicateur (ex. nombre d’administrateurs par collège).<br>3. Visualisation graphique + export. | - **AE‑10** : Données manquantes → message “Données insuffisantes”. | L’utilisateur est authentifié. | Le tableau de bord affiche les indicateurs demandés. |
| **CU‑8** | Authentification via Cerbère | Tous les utilisateurs | 1. L’utilisateur saisit ses identifiants Cerbère.<br>2. Le SSO renvoie un token.<br>3. Le token est vérifié, les rôles sont récupérés. | - **AE‑11** : Authentification échouée → redirection login + message. | Aucun (page publique). | L’utilisateur possède une session valide, les droits sont appliqués. |
| **CU‑9** | Archivage Mandat expiré | Scheduler / Opérateur | 1. Le job nocturne détecte les mandats expirés.<br>2. Les pièces sont déplacées vers l’archive.<br>3. Le mandat devient “archivé” (lecture seule). | - **AE‑12** : Erreur de copie → journal d’erreur, relance manuelle. | Le mandat est expiré depuis ≥ 1 jour. | Le mandat est archivé, visibilité limité à la lecture. |
| **CU‑10** | Gestion des référentiels | MOE / Opérateur | 1. Accès à la section “Référentiels”.<br>2. Ajout / modification / suppression d’un type (ex. type mandat).<br>3. Validation. | - **AE‑13** : Référentiel utilisé par des données actives → refus avec explication. | L’utilisateur possède le rôle “Admin référentiel”. | Le référentiel est mis à jour, les contraintes FK sont respectées. |

---  

## 5️⃣ Processus métier (optionnel)  

### 5.1 Diagramme BPMN – Import JORF & Mise à jour des mandats  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%
bpmnDiagram;
    participant "Scheduler" as S;
    participant "Job Import JORF" as J;
    participant "Parser" as P;
    participant "Base de données" as DB;
    participant "Notifier" as N;
    S->>J: Démarrer (cron quotidien)
    J->>P: Télécharger flux JORF;
    P->>P: Parse XML / TAR.GZ;
    P->>DB: Upsert nominations;
    alt Nouvelles nominations;
        DB->>N: Générer notification (mail)
    else Aucune nouveauté;
        note right of DB: Pas d’action;
    end
    J->>S: Fin du job (log)
```

### 5.2 Diagramme BPMN – Gestion du mandat et alerte d’échéance  

```mermaid
%%{init: {'theme':'base'}}%%%%%%%%%%%%%%%%%%%%%%%%%%
bpmnDiagram;
    participant "Opérateur" as O;
    participant "Application" as A;
    participant "Scheduler" as S;
    participant "Mail" as M;
    O->>A: Saisie/Modification mandat;
    A->>A: Vérifier cohérence dates;
    A->>A: Persist (audit)
    A->>S: (Ré)planifier alerte (date d’échéance - 30j)
    S->>M: Envoi mail alerte;
    M->>O: (Copie) mail reçu
```

---  

## 6️⃣ Règles métier et contraintes fonctionnelles  

| N° | Règle (formulation conditionnelle) | Source / Référence |
|---|---|---|
| **R‑1** | **Un administrateur ne peut occuper deux mandats du même type sur le même EP simultanément**. <br> _Si_ (admin, EP, type mandat) → **pas** de chevauchement de dates. | FS‑3, NF EN 16271 |
| **R‑2** | **Le mandat doit toujours avoir une date de début antérieure à la date de fin**. | FS‑3 |
| **R‑3** | **Chaque mandat doit être associé à au moins une pièce justificative**. | FS‑3 |
| **R‑4** | **Les données de référence (type mandat, type instance, charge, ministère) sont en lecture‑seule pour les utilisateurs non‑admin**. | FS‑10 |
| **R‑5** | **Le JORF ne doit être importé qu’une fois par jour** (scheduler). | FS‑5 |
| **R‑6** | **Les notifications d’échéance sont envoyées 30 jours avant la date de fin du mandat**. | FS‑7 |
| **R‑7** | **Les pièces archivées sont conservées minimum 10 ans** (RGPD, DICT). | Contrainte légale |
| **R‑8** | **Tous les accès doivent être journalisés (authentification, CRUD, import)**. | Sécurité, audit |
| **R‑9** | **Le SSO Cerbère fournit les attributs suivants : identifiant, rôle, email**. | Authentification |
| **R‑10** | **La recherche doit être insensible à la casse et aux accents**. | FS‑4 |

---  

## 7️⃣ Parcours utilisateurs (User Journey)  

### 7.1 Parcours « Création d’un administrateur »  

| Étape | Action de l’utilisateur | Système | Points de contrôle |
|---|---|---|---|
| 1 | Se connecter via Cerbère | Authentification SSO | Temps ≤ 1 s, logs d’accès |
| 2 | Accéder à “Gestion Administrateurs” | UI | Vérification du rôle (Gestionnaire) |
| 3 | Cliquer “Nouveau Administrateur” | UI | Affichage du formulaire |
| 4 | Remplir les champs obligatoires (nom, prénom, email, profil) | Validation front‑end | Champ manquant → message d’erreur |
| 5 | Sélectionner les établissements associés | UI (liste déroulante) | Vérification de l’existence du SIREN |
| 6 | Valider | Backend (CRUD) | Transaction DB, audit INSERT |
| 7 | Confirmation + redirection vers la fiche | UI | Message “Création réussie” |
| 8 | Historiser l’opération | DB + logs | Conformité audit |

### 7.2 Parcours « Réception d’une alerte d’échéance »  

| Étape | Action du système | Description |
|---|---|---|
| 1 | Scheduler nocturne (00:00) | Recherche mandats expirant dans +30 j |
| 2 | Génération du mail (template HTML) | Contient admin, EP, date d’échéance, lien vers le mandat |
| 3 | Envoi via serveur SMTP interne | Confirmation d’envoi (status 250) |
| 4 | Enregistrement dans le journal d’envoi | Date/heure, destinataire, statut |
| 5 | L’utilisateur référent reçoit le mail (Inbox) | Peut cliquer pour accéder au mandat dans l’app |

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)  

> Diagramme UML simplifié (classes, attributs clés, relations).  

```mermaid
classDiagram
    class Administrateur {
        +Long id;
        +String nom;
        +String prenom;
        +String email;
        +String profilCerb;
        +Date createdAt;

    class Etablissement {
        +Long id;
        +String siren;
        +String libelle;
        +String sigle;
        +TypeInstance typeInstance;

    class Mandat {
        +Long id;
        +Date debut;
        +Date fin;
        +TypeMandat typeMandat;
        +ModeNomination modeNomination;
        +String pieceJointePath;

    class TypeMandat {
        +Long id;
        +String libelle;

    class TypeInstance {
        +Long id;
        +String libelle;

    class ModeNomination {
        +Long id;
        +String code;
        +String libelle;

    class Charge {
        +Long id;
        +String libelle;

    class Ministere {
        +Long id;
        +String sigle;
        +String nom;

    class College {
        +Long id;
        +String identifiant;

    Administrateur "1" --> "*" Mandat : possède >
    Etablissement "1" --> "*" Mandat : concerne >
    Etablissement "1" --> "1" TypeInstance : type >
    Mandat "1" --> "1" TypeMandat : type >
    Mandat "1" --> "1" ModeNomination : mode >
    Charge "1" --> "*" Ministere : chargeDe >
    Etablissement "*" --> "*" College : appartient >
    College "*" --> "*" SynonymeCollege : possède >
```

---  

## 9️⃣ Critères d'acceptation et validation  

| Fonction | Critère d’acceptation (exemple) | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| **Gestion des administrateurs** | Création d’un administrateur en ≤ 2 min, audit présent. | Tests fonctionnels automatisés + revue de logs. | QA / MOE | **M** |
| **Gestion des mandats** | Aucun doublon de mandat (R‑1) détecté. | Jeu de données de test (overlap) + contraintes DB. | QA | **M** |
| **Recherche** | Temps de réponse ≤ 2 s pour 95 % des requêtes. | Tests de charge (JMeter) sur jeu de 10 k enregistrements. | Performance Engineer | **M** |
| **Import JORF** | Couverture ≥ 95 % des nouvelles nominations. | Comparaison avec le flux officiel sur 30 jours. | MOE | **M** |
| **Notification** | Mail reçu dans ≤ 1 h, taux délivrabilité ≥ 98 %. | Monitoring SMTP + rapport de délivrabilité. | Ops | **M** |
| **Statistiques** | Tableau de bord actualisé en ≤ 5 min. | Test de rafraîchissement (cron) + mesure temps. | PO | **S** |
| **Authentification** | Aucun accès non autorisé (audit). | Pen‑test + revue des logs d’accès. | Security Officer | **M** |
| **Archivage** | Mandats archivés conservés ≥ 10 ans, accès lecture‑seule. | Vérification du stockage et des droits. | Ops | **S** |
| **Gestion des référentiels** | Modification bloquée si référentiel utilisé (R‑13). | Tests d’intégrité référentielle. | DBA | **C** |
| **Conformité RGPD** | Export anonymisé possible, registre des traitements à jour. | Audit conformité. | DPO | **M** |

---  

## 🔟 Annexes  

### 10.1 Glossaire métier  

| Terme | Définition |
|---|---|
| **Administrateur** | Personne nommée membre du conseil d’administration ou de surveillance d’un EP. |
| **EP** | Établissement public placé sous la tutelle du MTES‑MCT. |
| **Mandat** | Période pendant laquelle un administrateur exerce ses fonctions (titulaire ou suppléant). |
| **Charge** | Fonction ministérielle (ex. « Affaires étrangères ») à laquelle un mandat peut être rattaché. |
| **Mode de nomination** | Type d’arrêté (Arrêté, Décret, Décret du Président). |
| **College** | Regroupement d’établissements (ex. « Collège du ministère de la Transition »). |
| **SynonymeCollege** | Nom alternatif d’un collège (ex. « Ministère de l’Écologie »). |
| **Cerbère** | Système d’authentification unique (SSO) de l’État. |
| **JORF** | Journal officiel de la République française (source des nominations). |
| **Statistiques** | Indicateurs agrégés (nombre d’administrateurs, mandats actifs, expirations, …). |
| **Archivage** | Conservation à long terme des mandats expirés et pièces justificatives. |

### 10.2 Référentiels et normes applicables  

| Référentiel / Norme | Domaine d’application |
|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences tout au long du cycle de vie. |
| **RGPD** | Protection des données à caractère personnel. |
| **DICT** | Déclaration d’Intention de Conformité au RGPD (France). |
| **RGS** | Référentiel Général de Sécurité (authentification, chiffrement). |
| **ISO 27001** | Sécurité de l’information (audit). |
| **ISO 20022** | Format d’échange de données (possibilité d’extension). |

### 10.3 Historique des versions du CCF  

| Version | Date | Modifications |
|---|---|---|
| **1.0** | 2024‑04‑27 | Version initiale (déduite des sources). |
| **1.1** | 2024‑05‑10 | Ajout du BPMN « Import JORF », mise à jour des pondérations. |
| **1.2** | 2024‑06‑01 | Intégration des exigences RGPD, ajout du tableau d’acceptation détaillé. |

---  

*Fin du Cahier des Charges Fonctionnel*  

↩ Retour au **sommaire**.  