# Cahier des Charges Fonctionnel (CCF) – **SIREINES**  
*Version 1.0 – 15 / 03 / 2024*  

---  

## 📚 Table des matières  
[TOC]

---  

## 1️⃣ Introduction et contexte du projet  

### 1.1 Présentation du projet  
SIREINES (Système d’Information de REgistre des INtérvenants Experts et Spécialistes) est une application Java/J2EE web qui recense, suit et gère les demandes de qualification des agents par les comités de domaine du **CGDD/DRI/AST4**.  

- **Objectif stratégique** : fournir un référentiel unique, à jour et sécurisé des experts scientifiques et techniques, faciliter la prise de décision des comités et assurer le suivi administratif des dossiers.  
- **Environnement** : déploiement en conteneurs Docker (Tomcat 7, PostgreSQL 14) sur la plateforme IaaS (ECO4) du ministère, avec BIRT 4.3 pour les rapports.  

### 1.2 Périmètre fonctionnel  

| Inclus | Exclu |
|--------|-------|
| Gestion des **dossiers** (création, édition, consultation, archivage) | Gestion des **données hors‑SIREINES** (ex : ressources humaines du ministère) |
| Gestion des **référentiels** (agents, structures, comités, qualifications, mots‑clés) | Développement de nouveaux modules de type **CRM** |
| Import / Export de fichiers (CSV, XML) | Migration de bases existantes (hors‑SIREINES) |
| Génération de rapports BIRT (extractions, statistiques) | Hébergement sur d’autres clouds (AWS, Azure) |
| Authentification et gestion des droits (RGPD, RGS) |  |

---  

## 2️⃣ Expression fonctionnelle du besoin  

### 2.1 Décomposition en **fonctions de service** (FS)  

| # | Fonction de service (FS) | Description (quoi) | Critères d’appréciation (mesurables) | Importance (MoSCoW) | Contraintes |
|---|--------------------------|--------------------|--------------------------------------|--------------------|--------------|
| **FS‑01** | **Gestion des dossiers** | Création, mise à jour, consultation, clôture et archivage d’un dossier de qualification. | – Temps moyen de création ≤ 5 s.<br>– 99,5 % de disponibilité du formulaire.<br>– Historisation de chaque modification (audit). | **M** | RGPD : traçabilité, conservation ≤ 5 ans. |
| **FS‑02** | **Recherche dossiers** | Recherche multi‑critères (agent, structure, date, statut, mots‑clés). | – Temps de réponse ≤ 2 s pour < 10 000 dossiers.<br>– Précision ≥ 95 % (rappel). | **M** | Index Elasticsearch (v7) – mise à jour quotidienne. |
| **FS‑03** | **Gestion des référentiels** | CRUD sur agents, structures, comités, qualifications, niveaux de mots‑clés. | – Temps moyen de modification ≤ 3 s.<br>– Validation métier (ex : code unique). | **M** | Règles de gestion métier (ex : un mot‑clé ne peut appartenir qu’à un niveau). |
| **FS‑04** | **Import de fichiers** | Import de fichiers CSV/Excel contenant des agents, dossiers ou mots‑clés. | – Taux d’erreur ≤ 1 % des lignes importées.<br>– Retour détaillé (ligne, cause). | **S** | Fichier ≤ 50 Mo, encodage UTF‑8. |
| **FS‑05** | **Export / Extraction** | Génération de rapports (PDF, CSV, XLS) via BIRT 4.3 (ex : pyramide d’âges, fréquence mots‑clés). | – Temps de génération ≤ 10 s pour un rapport complet.<br>– Qualité du PDF ≥ 300 dpi. | **S** | BIRT 4.3, licences compatibles. |
| **FS‑06** | **Authentification & Autorisation** | Authentification unique (SSO) + gestion des profils (admin, comité, agent). | – Temps de login ≤ 2 s.<br>– 0 % de fuite d’informations (tests de pénétration). | **M** | Conformité RGS / RGPD, authentification via **Cerbère** (OAuth2). |
| **FS‑07** | **Notification par email** | Envoi d’emails automatiques (validation, décision, rappel). | – Délai d’envoi ≤ 30 s après l’événement.<br>– Taux de délivrabilité ≥ 98 %. | **S** | SMTP interne, gestion des bounce. |
| **FS‑08** | **Statistiques d’usage** | Tableau de bord (nombre de dossiers, temps moyen de traitement, etc.). | – Refresh ≤ 5 min.<br>– Disponibilité ≥ 99 %. | **C** | Utilisation de BIRT + Grafana (optionnel). |
| **FS‑09** | **Gestion des droits (RBAC)** | Attribution fine des permissions (lecture/écriture) selon les rôles. | – 0 % d’accès non autorisé détecté en audit trimestriel. | **M** | Règles d’accès : *admin* > *comité* > *agent*. |
| **FS‑10** | **Audit & Traçabilité** | Journalisation de toutes les actions critiques (CRUD, imports, exports). | – Conservation ≥ 2 ans.<br>– Requête d’audit ≤ 3 s. | **M** | Syslog + ELK stack (optionnel). |

> **Note** : Les fonctions sont exprimées uniquement au niveau **« quoi »** – le **« comment »** (implémentation technique) sera détaillé dans la partie « Solution » du présent CCF.

---  

## 3️⃣ Acteurs et parties prenantes  

| Acteur | Rôle | Besoins spécifiques |
|--------|------|---------------------|
| **MOA – CGDD/DRI/AST4** | Maîtrise d’Ouvrage, décision fonctionnelle | Suivi des demandes, conformité réglementaire, reporting. |
| **MOE – SG/DNUM/PNM3** | Maîtrise d’Œuvre, exploitation | Disponibilité, scalabilité, sécurité, maintenance. |
| **Agent (utilisateur final)** | Soumission d’une demande de qualification, consultation de son dossier | Interface simple, suivi en temps réel, notifications. |
| **Membre du Comité de domaine** | Évaluation et décision sur les dossiers | Recherche avancée, filtres, historique des évaluations. |
| **Administrateur système** | Gestion de l’infrastructure (Docker, PostgreSQL) | Accès aux logs, sauvegardes, mise à jour des images. |
| **Service de messagerie** | Envoi de notifications | Fiabilité, respect des standards de messagerie sécurisée. |
| **Service BIRT** | Génération de rapports | Qualité d’impression, export multi‑format. |
| **Auditeur RGPD** | Vérification de la conformité | Accès aux logs d’audit, traçabilité des données personnelles. |

---  

## 4️⃣ Cas d’usage (Use Cases)  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#2F81AD', 'edgeLabelBackground':'#fff'}}%%}%%
usecaseDiagram;
    actor Agent as A;
    actor Membre du Comité as C;
    actor Administrateur as Adm;
    actor Service Messagerie as M;
    actor Service BIRT as B;
    A --> (Soumettre une demande)
    A --> (Consulter l’état de son dossier)
    A --> (Télécharger un rapport)

    C --> (Rechercher des dossiers)
    C --> (Évaluer un dossier)
    C --> (Valider / Refuser une qualification)

    Adm --> (Gérer les référentiels)
    Adm --> (Importer des fichiers)
    Adm --> (Effectuer des extractions)

    (Soumettre une demande) --> \(Enregistrer le dossier) : <<include>>
    (Enregistrer le dossier) --> \(Notifier l’agent) : <<extend>>
    (Évaluer un dossier) --> \(Notifier le décision) : <<extend>>
    (Notifier le décision) --> \(Envoyer email) : <<include>>
    (Exporter un rapport) --> \(Générer le rapport BIRT) : <<include>>
```

### 4.1 Description détaillée (scénario nominal)  

| Cas d’usage | Acteur(s) principal(s) | Description | Pré‑conditions | Post‑conditions |
|------------|-----------------------|-------------|----------------|-----------------|
| **Soumettre une demande** | Agent | L’agent remplit le formulaire de création de dossier, indique ses mots‑clés, sa structure, et lance l’enregistrement. | Agent authentifié. | Dossier créé, état = *« En cours »*, email de confirmation envoyé. |
| **Rechercher des dossiers** | Membre du Comité | Saisie de critères (structure, date, mots‑clés), lancement de la recherche, affichage de la liste paginée. | Authentifié, droits de lecture sur les dossiers. | Résultats affichés, possibilité d’ouvrir le détail. |
| **Évaluer un dossier** | Membre du Comité | Consultation du dossier, saisie d’une décision (qualification, refus) avec commentaires, sauvegarde. | Dossier en statut *« En cours »*. | Dossier passe en *« Décision »*, notification à l’agent. |
| **Importer un fichier** | Administrateur | Sélection d’un fichier CSV, mapping des colonnes, lancement de l’import, retour du rapport d’erreurs. | Accès admin, fichier valide ≤ 50 Mo. | Données ajoutées/modifiées, logs d’import générés. |
| **Exporter un rapport** | Agent / Comité | Choix du type de rapport (pyramide d’âges, fréquence mots‑clés), génération via BIRT, téléchargement. | Accès aux données, droits de lecture. | Fichier PDF/CSV disponible, log d’export créé. |

### 4.2 Scénarios alternatifs / d’erreur  

- **Import – fichier mal formé** → affichage d’une erreur détaillée, aucune donnée n’est importée.  
- **Recherche – aucun résultat** → affichage d’un message *« Aucun dossier trouvé »*.  
- **Évaluation – perte de connexion** → le système enregistre le travail en cours, l’utilisateur reprend après reconnexion.  

---  

## 5️⃣ Processus métier (BPMN)  

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#2F81AD', 'edgeLabelBackground':'#fff'}}%%}%%
bpmnDiagram;
    participant Agent;
    participant SIREINES as App;
    participant Comité;
    participant Email as Mail;
    participant BIRT;
    startEvent(start) --> taskCreate[Créer le dossier]
    taskCreate --> exclusiveGateway{Dossier complet ?}
    exclusiveGateway -->|Oui| taskSave[Enregistrer le dossier]
    exclusiveGateway -->|Non| taskEdit[Retour à la saisie]
    taskSave --> taskNotify[Notifier l’agent]
    taskNotify --> endEvent(end)

    taskSave --> taskAssign[Assignation au comité]
    taskAssign --> taskReview[Révision du comité]
    taskReview --> exclusiveGateway2{Décision}
    exclusiveGateway2 -->|Qualification| taskQualify[Enregistrer qualification]
    exclusiveGateway2 -->|Refus| taskReject[Enregistrer refus]
    taskQualify --> taskReport[Générer rapport BIRT]
    taskReject --> taskReport;
    taskReport --> taskNotifyDecision[Notifier l’agent]
    taskNotifyDecision --> endEvent
```

**Explication du processus**  

1. **Création du dossier** par l’agent.  
2. **Vérification** de la complétude du formulaire.  
3. **Enregistrement** et **notification** à l’agent.  
4. **Assignation** du dossier au comité compétent.  
5. **Évaluation** du comité → décision (qualification / refus).  
6. **Mise à jour** du statut, génération du **rapport BIRT**, puis **notification** à l’agent.  

---  

## 6️⃣ Règles métier et contraintes fonctionnelles  

| # | Règle métier (IF THEN) | Source / Référence |
|---|------------------------|--------------------|
| **RM‑01** | *Si* le dossier contient un **mot‑clé** dont le **niveau** = 3, *alors* il doit être **examined par le comité de domaine**. | Spécifications fonctionnelles V2.5.20 |
| **RM‑02** | *Si* la date de création du dossier dépasse **5 ans**, *alors* le dossier passe en **archivage** automatique. | RGPD, politique de rétention |
| **RM‑03** | *Si* l’agent n’est plus rattaché à aucune **structure active**, *alors* son accès est **bloqué**. | Règle métier « Gestion des droits » |
| **RM‑04** | *Si* le **rapport BIRT** dépasse **10 Mo**, *alors* le serveur doit le **compresser** avant le téléchargement. | Contraintes de bande passante |
| **RM‑05** | *Si* le champ **email** ne respecte pas le format RFC 5322, *alors* le formulaire doit afficher **une erreur**. | Validation front‑end |
| **RM‑06** | *Si* l’utilisateur possède le rôle **admin**, *alors* il peut **supprimer** un référentiel (ex : mot‑clé). | Gestion RBAC |
| **RM‑07** | *Si* le **mot‑clé** est déjà présent à un autre niveau, *alors* la création d’un nouveau niveau est **interdite**. | Contrôle d’unicité |
| **RM‑08** | *Si* le serveur détecte **plus de 3 échecs** d’authentification consécutifs, *alors* le compte est **bloqué** 15 min. | Politique de sécurité (RGS) |
| **RM‑09** | *Si* le **dump** de la base est réalisé, *alors* il doit être stocké **au minimum 30 jours** sur un volume distinct. | Plan de continuité d’activité |

---  

## 7️⃣ Parcours utilisateurs (User Journey)  

### 7.1 Parcours « Soumission d’une demande »

| Étape | Interaction | Système |
|-------|--------------|---------|
| 1. **Connexion** | L’agent saisit ses identifiants (SSO Cerbère). | Authentification via OAuth2, création de session. |
| 2. **Accès au tableau de bord** | Affichage du menu « Nouvelle demande ». | Chargement du composant UI (Struts2 + FreeMarker). |
| 3. **Création du dossier** | Remplissage du formulaire (structure, mots‑clés, pièces jointes). | Validation client (JS) → appel au service `DossiersServices.create()`. |
| 4. **Validation** | Le bouton **« Enregistrer »** déclenche la sauvegarde. | Transaction Spring (propagation = REQUIRED). |
| 5. **Notification** | Envoi d’un email de confirmation. | `CommonServices.sendMail()`. |
| 6. **Suivi** | L’agent visualise le statut « En cours » dans la liste de ses dossiers. | Requête `DossiersServices.searchByAgent()`. |
| 7. **Fin** | L’agent peut télécharger le **rapport d’état** (BIRT). | `Report.generate("etat_dossier")`. |

### 7.2 Parcours « Évaluation par le comité »

| Étape | Interaction | Système |
|-------|--------------|---------|
| 1. **Connexion comité** | Authentification SSO. | Same as above. |
| 2. **Accès à la file d’attente** | Liste filtrée par **structure** et **date**. | Recherche Elasticsearch (`DossiersMotsClefsSearchLoader`). |
| 3. **Ouverture du dossier** | Lecture détaillée (documents, historique). | `DossiersServices.getDetail(id)`. |
| 4. **Prise de décision** | Sélection « Qualifié » / « Refus », saisie de commentaire. | `DossiersServices.updateDecision()`. |
| 5. **Génération du rapport** (optionnel) | Cliquer sur **« Rapport »** → BIRT. | `Report.generate("qualification")`. |
| 6. **Notification** | Email envoyé à l’agent. | `CommonServices.sendMail()`. |
| 7. **Archivage** (automatique) | Si le statut passe à **« Clôturé »** > 5 ans → archivage. | Job planifié (`Quartz`) → `ArchivageService`. |

---  

## 8️⃣ Modèle Conceptuel de Données (MCD)  

```mermaid
classdiagram;
    class Dossier {
        +Long dosId;
        +Date dateReception;
        +String statut;
        +String commentaire;
    }
    class Agent {
        +Long agentId;
        +String nom;
        +String prenom;
        +String email;
        +String structureId;
    }
    class Structure {
        +String strId;
        +String libelleCourt;
    }
    class Comité {
        +Long comId;
        +String libelle;
    }
    class Qualification {
        +Long quaId;
        +String libelle;
    }
    class MotCle {
        +Long mclId;
        +String libelle;
        +Integer niveau;
    }
    class Rapport {
        +Long rapId;
        +String type;
        +Date dateGeneration;
    }

    Dossier --> Agent : "déposé par"
    Dossier --> Structure : "rattaché à"
    Dossier --> Comité : "examiné par"
    Dossier --> Qualification : "résultat"
    Dossier --> MotCle : "contient"
    Dossier --> Rapport : "génère"
    Agent --> Structure : "appartient à"
    MotCle --> "Niveau" : "1..3"
```

### 8.1 Principaux attributs  

| Entité | Attributs clés | Description |
|--------|----------------|-------------|
| **Dossier** | `dosId`, `dateReception`, `statut`, `commentaire` | Enregistrement principal. |
| **Agent** | `agentId`, `nom`, `prenom`, `email`, `structureId` | Utilisateur final. |
| **Structure** | `strId`, `libelleCourt` | Service ou direction de rattachement. |
| **Comité** | `comId`, `libelle` | Organe décisionnel. |
| **Qualification** | `quaId`, `libelle` | Résultat du comité. |
| **MotCle** | `mclId`, `libelle`, `niveau` | Classification du dossier. |
| **Rapport** | `rapId`, `type`, `dateGeneration` | Document BIRT généré. |

---  

## 9️⃣ Critères d’acceptation et validation  

| Fonction (FS) | Critère d’acceptation | Méthode de validation | Priorité |
|----------------|------------------------|------------------------|----------|
| **FS‑01** | Création d’un dossier en ≤ 5 s, données correctement persistées, email envoyé. | Tests fonctionnels automatisés (JUnit + Selenium), test de charge JMeter (100 concurrents). | **M** |
| **FS‑02** | Recherche renvoie les résultats attendus en ≤ 2 s, précision ≥ 95 %. | Suite de jeux de données (10 k dossiers) + tests d’intégration Elasticsearch. | **M** |
| **FS‑03** | CRUD référentiels respecte les règles d’unicité, audit des modifications. | Tests unitaires, revue de code, audit logs. | **M** |
| **FS‑04** | Import d’un fichier CSV ≤ 50 Mo avec < 1 % d’erreurs, rapport détaillé. | Test d’import avec fichiers de référence, vérification du log d’erreurs. | **S** |
| **FS‑05** | Rapport BIRT généré < 10 s, PDF ≥ 300 dpi, nommage correct. | Tests d’intégration BIRT, validation visuelle. | **S** |
| **FS‑06** | Authentification SSO réussie en ≤ 2 s, aucun accès non autorisé. | Tests de pénétration OWASP ZAP, audit de logs. | **M** |
| **FS‑07** | Email de notification reçu ≤ 30 s, taux de délivrabilité ≥ 98 %. | Envoi vers serveur de test, suivi via MailHog. | **S** |
| **FS‑08** | Tableau de bord actualisé toutes les 5 min, disponibilité ≥ 99 %. | Monitoring Grafana/Prometheus. | **C** |
| **FS‑09** | RBAC empêche toute action non autorisée (tests d’accès). | Tests d’autorisation automatisés. | **M** |
| **FS‑10** | Logs d’audit conservés ≥ 2 ans, requêtes d’audit < 3 s. | Vérification via Kibana. | **M** |

---  

## 🔟 Annexes  

### 10.1 Glossaire métier  

| Terme | Définition |
|-------|------------|
| **Dossier** | Enregistrement d’une demande de qualification d’un agent. |
| **Qualification** | Décision du comité (ex : *Qualifié*, *Non‑qualifié*). |
| **Mot‑clé** | Étiquette de classification (niveau 1 = thésaurus, 2 = sous‑thésaurus, 3 = spécifique). |
| **Comité de domaine** | Jury de spécialistes qui valide les qualifications. |
| **BIRT** | Business Intelligence and Reporting Tools, moteur de génération de rapports. |
| **Cerbère** | Service d’authentification SSO du ministère (OAuth2). |
| **RGPD** | Règlement Général sur la Protection des Données. |
| **RGS** | Référentiel Général de Sécurité. |
| **Elasticsearch** | Moteur de recherche full‑text utilisé pour la recherche dossiers. |

### 10.2 Références normatives  

| Norme | Intitulé | Application |
|-------|----------|-------------|
| **NF EN 16271** | Management par la valeur – Expression fonctionnelle du besoin – Cahier des charges fonctionnel | Méthodologie de rédaction du présent CCF. |
| **ISO/IEC/IEEE 29148:2018** | Ingénierie des exigences – Processus d’élaboration, de gestion et de traçabilité | Structure du CCF, gestion des exigences, traçabilité. |
| **ISO 9001** | Système de management de la qualité | Garantir la qualité du processus de développement. |
| **RGPD Art. 30** | Registre des activités de traitement | Traçabilité des traitements de données personnelles. |
| **RGS v2** | Référentiel Général de Sécurité | Sécurité des échanges, authentification, chiffrement. |

### 10.3 Historique des versions du document  

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0 | 15/03/2024 | ChatGPT (IA) | Version initiale – synthèse des sources fournies. |
| 1.1 | 02/04/2024 | — | Ajout du diagramme BPMN et des critères d’acceptation détaillés. |

---  

## 📌 Conclusion  

Le présent **Cahier des Charges Fonctionnel** décrit de façon exhaustive les besoins fonctionnels de **SIREINES**, les acteurs, les cas d’usage, les processus métier, les règles de gestion, le modèle de données et les critères d’acceptation.  
Il constitue la base contractuelle entre la **MOA** (CGDD/DRI/AST4) et la **MOE** (SG/DNUM/PNM3) pour la conception, le développement, les tests, le déploiement et la mise en production de la solution, en conformité avec les exigences **NF EN 16271** et **ISO/IEC/IEEE 29148**.  

---  

*Document généré automatiquement à partir des sources du projet SIREINES (code, README, wiki, procédures). Aucun lien externe n’est nécessaire pour la lecture complète.*