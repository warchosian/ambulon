# 📌 Cahier des Charges Fonctionnel (CCF) – **agile‑back**
> **Version 1.0 – 27 avril 2026**  
> **[TOC]**  

---  

## 1️⃣ Introduction et contexte du projet
| Élément | Description |
|---|---|
| **Intitulé du projet** | **agile‑back** – back‑office de l’application *Agile* permettant la création, la modification et le suivi d’études stockées dans PostgreSQL. |
| **Organisation porteuse** | Équipe *WarchoLife* (développement Symfony 5+, PostgreSQL, CAS pour l’authentification). |
| **Objectifs stratégiques** | 1. Centraliser la saisie et la gestion des études, dotations, financements, groupes, services et thèmes.<br>2. Garantir la traçabilité des actions (création / modification) et la valorisation des résultats.<br>3. Fournir des exports (CSV, ODS) pour les besoins de pilotage et de reporting.<br>4. Assurer la sécurité via le protocole CAS et la conformité RGPD. |
| **Livrables attendus** | - Application web back‑office (Symfony) fonctionnelle.<br>- Documentation technique et fonctionnelle.<br>- Jeux de tests d’acceptation.<br>- Procédures d’installation / déploiement. |
| **Périmètre fonctionnel** | **Inclus** : Gestion des études, dotations, financements, groupes, services, thèmes, profils, utilisateurs, authentification CAS, export CSV/ODS, notifications e‑mail.<br>**Exclu** : Front‑office *Agile‑front*, modules de calcul avancé, intégration de sources externes non‑CAS. |
| **Contraintes majeures** | - Architecture MVC Symfony (Modèle/Vue/Contrôleur).<br>- Base de données PostgreSQL.<br>- Utilisation du composant **API‑Platform** pour les API REST.<br>- Respect du RGPD (données personnelles, consentement).<br>- Hébergement sur serveur Linux avec PHP 8.2+. |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 2️⃣ Expression fonctionnelle du besoin *(NF EN 16271)*
> **Fonctions de service (FS)** = *Ce que le système doit faire* (pas comment).  

| # | Fonction de service | Description (quoi) | Critères d’appréciation (mesurables) | Niveau d’importance (pondération) | Contraintes associées |
|---|---|---|---|---|---|
| **FS‑01** | **Gestion des études** | Créer, lire, mettre à jour, supprimer (CRUD) une *étude* avec ses métadonnées (titre, zone géographique, groupe, thème, description, etc.). | - Temps de création ≤ 3 s.<br>- 99 % de disponibilité du formulaire.<br>- Historique complet des modifications (date, utilisateur). | **30 %** (critique) | - Validation serveur + client.<br>- Conformité aux règles de nommage (ex. `titre_etude` → `titreetude`). |
| **FS‑02** | **Gestion des dotations** | Saisir, associer et visualiser les dotations budgétaires par année, groupe, BOP et sous‑action. | - Détection d’erreurs de montant ≤ 0,5 %.<br>- Export CSV des dotations ≤ 5 s. | **12 %** | - Montant ≥ 0.<br>- Respect des formats monétaires. |
| **FS‑03** | **Gestion des financements** | Enregistrer les demandes de financement, dates de décision, AE, CP, etc. | - Validation croisée avec dotations ≥ 95 % de réussite.<br>- Notification e‑mail de validation (temps d’envoi ≤ 2 s). | **12 %** | - Règle de cohérence : financement ≤ dotation. |
| **FS‑04** | **Gestion des groupes, services, thèmes** | CRUD des référentiels « Groupes », « Services », « Thèmes ». | - 0 % d’erreur de duplication (token unique).<br>- Temps moyen de modification ≤ 2 s. | **8 %** | - Token alphanumérique unique. |
| **FS‑05** | **Gestion des utilisateurs & profils** | CRUD des comptes, affectation à un groupe, rôle (admin / utilisateur). | - Authentification CAS réussie ≥ 99,5 % des tentatives.<br>- Gestion des mots de passe (hash bcrypt). | **10 %** | - Conformité RGPD (droit à l’oubli). |
| **FS‑06** | **Authentification via CAS** | Authentifier les utilisateurs avec le serveur CAS externe. | - Temps d’authentification ≤ 2 s.<br>- 99 % de taux de succès. | **10 %** | - Utilisation du composant `phpCAS` fourni dans `public/cas`. |
| **FS‑07** | **Export de données** | Générer des exports **CSV** et **ODS** à la demande (études, dotations, financements, valorisations). | - Taille max 5 Mo exportée ≤ 10 s.<br>- Intégrité du fichier (checksum SHA‑256). | **8 %** | - Respect du format RFC 4180 (CSV) et ODS OpenDocument. |
| **FS‑08** | **Notification e‑mail** | Envoyer des e‑mails de notification (création/modification d’étude, alerte). | - Taux de livraison ≥ 98 %.<br>- Délai d’envoi ≤ 3 s. | **5 %** | - Utilisation du service `mailer` configuré (`MAILER_DSN`). |
| **FS‑09** | **Suivi de la valorisation** | Saisir les actions de valorisation réalisées et les liens associés. | - 100 % des champs obligatoires remplis.<br>- Historique de valorisation conservé 5 ans. | **5 %** | - Validation de l’URL (format `https://…`). |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 3️⃣ Acteurs et parties prenantes
| Rôle | Description | Objectifs | Besoins spécifiques |
|---|---|---|---|
| **MOA (Maître d’Ouvrage)** | Responsable métier du suivi des études. | Piloter les projets, disposer de rapports fiables. | Export CSV/ODS, tableau de bord, traçabilité. |
| **MOE (Maître d’Œuvre)** | Équipe de développement (WarchoLife). | Implémenter les exigences fonctionnelles et techniques. | Accès au code, environnements de test, documentation. |
| **Administrateur (admin)** | Utilisateur avec droits complets (gestion des référentiels, utilisateurs). | Créer/modifier/supprimer toutes les entités. | Interface CRUD, gestion des rôles, logs d’audit. |
| **Utilisateur métier** | Agent en charge d’une ou plusieurs études. | Saisir/modifier les études, suivre les dotations. | Formulaires ergonomiques, validation en temps réel. |
| **Service d’authentification CAS** | Système externe (JASIG) d’authentification unique. | Authentifier les utilisateurs. | Intégration via `phpCAS`, prise en charge du SSO. |
| **RSSI (Responsable Sécurité des Systèmes d’Information)** | Garant de la conformité sécurité. | Veiller au respect du RGPD, journalisation, chiffrement. | Gestion des sessions, stockage sécurisé des mots‑de‑passe. |
| **Développeur Front‑Office (Agile‑front)** | Consomme les API exposées. | Récupérer les données d’études. | API REST conforme à OpenAPI (via API‑Platform). |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 4️⃣ Cas d’usage (Use Cases)  
> Diagramme UML de cas d’utilisation (Mermaid)  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#fff', 'nodeBorder':'#0366d6' }}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
usecaseDiagram;
    actor Admin as A;
    actor Utilisateur métier as U;
    actor CAS as C;
    rectangle "agile‑back" {
    A --> (Gérer les études)
    A --> (Gérer les dotations)
    A --> (Gérer les financements)
    A --> (Gérer les référentiels)
    A --> (Gérer les utilisateurs)
    A --> (Exporter les données)
    A --> (Notifier par e‑mail)
    U --> (Consulter les études)
    U --> (Créer/Modifier une étude)
    U --> (Suivre la valorisation)
    C --> (Authentifier)

```

### 4.1 Tableau récapitulatif des cas d’usage  

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Description du scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| **CU‑01** | Créer une étude | Utilisateur métier | 1. L’utilisateur se connecte via CAS.<br>2. Il accède au formulaire « Nouvelle étude ».<br>3. Il remplit les champs obligatoires et soumet.<br>4. Le système enregistre l’étude et notifie l’administrateur. | - **AE‑01** : Authentification CAS échouée → affichage d’un message d’erreur.<br>- **AE‑02** : Validation serveur échoue → affichage des messages de champ. | Session CAS valide. | Étude créée, entrée dans la table `Etudes`, notification e‑mail envoyée. |
| **CU‑02** | Modifier une étude | Utilisateur métier / Admin | 1. Sélection de l’étude dans la liste.<br>2. Accès au formulaire d’édition.<br>3. Modification des champs.<br>4. Enregistrement. | - **AE‑03** : Conflit de version (optimistic lock) → proposer de recharger.<br>- **AE‑04** : Droits insuffisants (utilisateur vs admin) → refus. | Étude existante, droits d’accès. | Étude mise à jour, historique de modification enregistré. |
| **CU‑03** | Supprimer une étude | Admin | 1. Sélection de l’étude.<br>2. Confirmation de suppression.<br>3. Le système supprime l’enregistrement. | - **AE‑05** : Étude liée à des dotations → annulation avec message. | Droits admin, étude sans dépendances critiques. | Enregistrement retiré, logs d’audit. |
| **CU‑04** | Exporter les études (CSV) | Admin | 1. L’administrateur choisit « Export CSV ».<br>2. Le système génère le fichier et le propose en téléchargement. | - **AE‑06** : Volume > 5 Mo → pagination ou message d’erreur. | Session admin active. | Fichier CSV disponible, checksum calculé. |
| **CU‑05** | Authentifier (CAS) | Tous les acteurs | 1. L’utilisateur accède à l’application.<br>2. Redirection vers le serveur CAS.<br>3. Retour avec ticket valide.<br>4. Création de la session locale. | - **AE‑07** : Ticket invalide → redirection vers la page de login CAS. | Aucun (premier accès). | Session PHP créée, identifiant stocké en session. |
| **CU‑06** | Gérer les référentiels (groupes, services, thèmes) | Admin | 1. Accès à la page de gestion du référentiel.<br>2. CRUD via les formulaires. | - **AE‑08** : Token déjà utilisé → rejet. | Session admin valide. | Table référentielle mise à jour, logs. |
| **CU‑07** | Envoyer une notification e‑mail | Système (trigger) | 1. Après création/modif d’une étude, le service `SiteUpdateMailer` déclenche l’envoi.<br>2. L’e‑mail est remis au destinataire. | - **AE‑09** : serveur SMTP indisponible → mise en file d’attente. | Étude enregistrée, configuration `MAILER_DSN`. | E‑mail envoyé, statut enregistré. |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 5️⃣ Processus métier (optionnel)  
> Diagramme BPMN (Mermaid) décrivant le processus de **création d’une étude**.  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#fff', 'nodeBorder':'#0366d6' }}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
bpmnDiagram;
    participant Utilisateur;
    participant CAS;
    participant Application;
    participant Mailer;
    Utilisateur->>CAS: Demande d’accès (redirection)
    CAS-->>Utilisateur: Ticket SSO;
    Utilisateur->>Application: Envoi ticket;
    Application->>Application: Validation ticket (phpCAS)
    Application->>Utilisateur: Accès à l’interface;
    Utilisateur->>Application: Saisie du formulaire « Nouvelle étude »
    Application->>Application: Validation métier (règles de nommage, cohérence)
    Application->>Application: Persistance (INSERT Etudes)
    Application->>Mailer: Trigger notification;
    Mailer->>Utilisateur: Envoi e‑mail;
    Application-->>Utilisateur: Confirmation création
```

**Points de contrôle**  
- **Ticket CAS valide** (sécurité).  
- **Validations métier** (ex. `titre_etude` unique).  
- **Enregistrement** (transaction DB).  
- **Envoi e‑mail** (statut de délivrance).  

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 6️⃣ Règles métier et contraintes fonctionnelles
| # | Règle métier (condition → action) | Type de contrainte |
|---|---|---|
| **R‑01** | `if (titre_etude` déjà présent) `then` refuser la création avec message *« Titre déjà utilisé »*. | Unicité (DB unique index). |
| **R‑02** | `if (montant_dotation < 0)` `then` bloquer la saisie. | Validation numérique. |
| **R‑03** | `if (financement > dotation_associée)` `then` alerter et empêcher la validation. | Cohérence budgétaire. |
| **R‑04** | `if (user_role != ADMIN)` `then` interdire l’accès aux pages d’administration. | Contrôle d’accès (security.yaml). |
| **R‑05** | `if (export_format == CSV)` `then` encoder en UTF‑8, séparer par `;` (RFC 4180). | Conformité format. |
| **R‑06** | `if (email not matching regex ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$)` `then` bloquer l’envoi. | Validation e‑mail. |
| **R‑07** | `if (user logs out)` `then` invalider la session immédiatement. | Gestion de session. |
| **R‑08** | `if (données personnelles stockées)` `then` chiffrer le champ `email` au repos. | RGPD – chiffrement. |
| **R‑09** | `if (export ODS)` `then` appliquer le schéma ODS standard (OpenDocument). | Conformité ODS. |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 7️⃣ Parcours utilisateurs (User Journey)
| Parcours | Étapes clés (Given / When / Then) | Points de contact | Critères d’acceptation |
|---|---|---|---|
| **Création d’une étude** | **Given** l’utilisateur est authentifié via CAS.<br>**When** il clique sur *Nouvelle étude* → formulaire affiché.<br>**Then** il remplit les champs obligatoires, valide et reçoit une confirmation. | Page *Nouvelle étude* (Twig), bouton *Créer*, message de succès. | - Formulaire affiché en ≤ 1 s.<br>- Tous les champs obligatoires sont marqués.<br>- Aucun message d’erreur côté serveur.<br>- Notification e‑mail reçue ≤ 3 s. |
| **Modification d’une dotation** | **Given** l’admin visualise la liste des dotations.<br>**When** il sélectionne *Modifier* d’une ligne.<br>**Then** le formulaire pré‑rempli s’affiche, il change le montant et sauvegarde. | Tableau des dotations, bouton *Modifier*, champ *Montant*. | - Temps de chargement du formulaire ≤ 2 s.<br>- Montant accepté uniquement si ≥ 0.<br>- Historique de modification enregistré. |
| **Export CSV des études** | **Given** l’admin est connecté.<br>**When** il choisit *Export CSV* dans le menu *Export*.<br>**Then** le fichier est téléchargé et contient toutes les colonnes attendues. | Menu *Export*, bouton *CSV*, téléchargement. | - Fichier < 5 Mo.<br>- Colonnes : id, titre, groupe, thème, statut, date création.<br>- Checksum SHA‑256 affiché. |
| **Authentification via CAS** | **Given** l’utilisateur accède à l’URL du back‑office.<br>**When** il clique sur *Se connecter* → redirection CAS.<br>**Then** il revient authentifié dans l’application. | Page d’accueil, lien *Se connecter*, serveur CAS. | - Redirection en ≤ 1 s.<br>- Ticket CAS valide.<br>- Session créée, `$_SESSION['email']` renseigné. |
| **Gestion des utilisateurs** | **Given** l’admin possède le rôle *ADMIN*.<br>**When** il crée un nouvel utilisateur via le formulaire.<br>**Then** le compte apparaît dans la liste, l’e‑mail de bienvenue est envoyé. | Formulaire *Nouvel utilisateur*, bouton *Créer*, e‑mail. | - Validation du mot de passe (complexité).<br>- Email envoyé ≤ 3 s.<br>- Utilisateur visible dans la liste. |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)  
> Diagramme de classes UML abstrait (Mermaid) représentant les entités métier et leurs relations.  

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0366d6', 'edgeLabelBackground':'#fff', 'nodeBorder':'#0366d6' }}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%}%%
classDiagram
    class Utilisateurs {
    +int id;
    +string nom;
    +string prenom;
    +string email;
    +string token;
    +datetime createdAt;

    class Profils {
    +int id;
    +string libelle;
    +bool admin;

    class Groupes {
    +int id;
    +string token;
    +string libelle;

    class Services {
    +int id;
    +string service;
    +string direction;
    +bool visible;
    +string region;

    class Themes {
    +int id;
    +string theme;

    class Bop {
    +int id;
    +string libelle_bop;
    +string commentaires_bop;
    +string sigle;
    +bool visible;

    class Etudes {
    +int id;
    +string titre_etude;
    +string zone_geographique;
    +datetime date_creation;
    +string description;
    +string resultat_attendu;
    +string methode;
    +string objectif;

    class Dotations {
    +int id;
    +int annee;
    +float montantdotation;

    class Financements {
    +int id;
    +float montant;
    +date date_comite;

    class Valorisation {
    +int id;
    +string commentaire;
    +string url;

    Utilisateurs "1" --> "0..*" Profils : possède >
    Utilisateurs "1" --> "0..*" Groupes : appartient à >
    Etudes "0..*" --> "1" Utilisateurs : créé par >
    Etudes "0..*" --> "1" Bop : lié à >
    Etudes "0..*" --> "1" Groupes : concerne >
    Etudes "0..*" --> "1" Themes : classifie >
    Etudes "0..*" --> "1" Services : concerne >
    Dotations "0..*" --> "1" Etudes : finance >
    Financements "0..*" --> "1" Etudes : finance >
    Valorisation "0..*" --> "1" Etudes : valorise >
    Bop "0..*" --> "1" Services : appartient à >
```

**Notes**  
- Les relations sont majoritairement *un‑à‑plusieurs* (ex. un groupe possède plusieurs études).  
- Les tables `Abonnements`, `Evenements` et `Types` existent mais ne sont pas détaillées ici (hors périmètre fonctionnel principal).  

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 9️⃣ Critères d'acceptation et validation
| Fonctionnalité | Critère d'acceptation (exemple) | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| **Gestion des études** | Création d’une étude en ≤ 3 s, champs obligatoires validés, email de notification reçu. | Tests fonctionnels automatisés (PHPUnit + Symfony Panther) + test manuel. | PO + QA | **Must** |
| **Gestion des dotations** | Montant ≥ 0, export CSV généré en ≤ 5 s, checksum valide. | Tests unitaires (Doctrine) + script d'export. | Développeur Back‑end | **Must** |
| **Gestion des financements** | Cohérence financement ≤ dotation, notification e‑mail en ≤ 3 s. | Tests d’intégration + monitoring Mailer. | QA | **Should** |
| **Authentification CAS** | 99,5 % de succès, délai ≤ 2 s. | Tests de charge (JMeter) + logs serveur. | RSSI | **Must** |
| **Export ODS** | Fichier ODS conforme au schéma, taille ≤ 5 Mo, génération ≤ 10 s. | Validation via `odfpy` + test manuel. | PO | **Could** |
| **Gestion des utilisateurs** | Création, modification, suppression fonctionnelles, conformité RGPD (droit à l’oubli). | Tests d’acceptation, audit RGPD. | PO + RSSI | **Must** |
| **Notification e‑mail** | Taux de délivrance ≥ 98 %, délai ≤ 3 s. | Vérification via logs `mailer` + outil de suivi (MailHog). | Développeur Back‑end | **Should** |
| **Valeur de la performance** | Temps moyen de réponse global ≤ 2 s (pages CRUD). | Tests de charge, New Relic. | QA | **Must** |

↩︎ Retour au **[Sommaire](#toc)**  

---  

## 🔟 Annexes
### A. Glossaire métier
| Terme | Définition |
|---|---|
| **Étude** | Dossier de projet contenant les informations de planification, objectifs, méthode et résultats attendus. |
| **Dotation** | Allocation budgétaire annuelle affectée à un groupe ou à une BOP. |
| **Financement** | Demande d’argent supplémentaire liée à une étude, validée par un comité. |
| **BOP** | *Business Operating Plan* – regroupement de projets au sein d’une même entité budgétaire. |
| **CAS** | Central Authentication Service – protocole SSO utilisé pour l’authentification unique. |
| **Valorisation** | Action de diffusion ou de mise en valeur d’une étude (ex. publication, lien internet). |
| **Profil** | Ensemble de droits (admin / utilisateur) attribués à un compte. |
| **Export CSV/ODS** | Extraction des données au format texte (CSV) ou tableur (ODS) pour les besoins d’analyse. |

### B. Référentiels et normes applicables
| Référence | Intitulé |
|---|---|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin & CCF. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences tout au long du cycle de vie. |
| **ISO/IEC 19505** | UML 2.x – notation des diagrammes. |
| **ISO/IEC 19510** | BPMN – modélisation des processus métier. |
| **RGPD** (UE) | Règlement Général sur la Protection des Données. |
| **RFC 4180** | Format de fichier CSV. |
| **OpenDocument ODS** | Standard ouvert de feuilles de calcul. |

### C. Historique des versions du document
| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 1.0 | 27 avril 2026 | ChatGPT (OpenAI) | Création initiale du CCF selon les exigences. |
| 1.1 | – | – | — |

---  

### 📌 Fin du Cahier des Charges Fonctionnel
> **Ce document est autonome, complet et exploitable tel quel dans VS Code ou Obsidian.**  
> Toutes les références internes sont hyperliées pour une navigation fluide.  

---  