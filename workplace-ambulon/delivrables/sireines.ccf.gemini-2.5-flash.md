[TOC]

# Cahier des Charges Fonctionnel (CCF) - Système SIREINES

---

## 1. Introduction et contexte du projet ↩ [Retour au sommaire](#table-des-matières)

### 1.1. Présentation du projet et de son contexte organisationnel

Le projet SIREINES (Système d'Information pour le Recensement des Experts et Spécialistes Scientifiques et Techniques) vise à informatiser la gestion des demandes de qualification des agents du Ministère de la Transition Écologique et Solidaire (MTES), spécifiquement sous la responsabilité de la mission des compétences scientifiques et techniques (CGDD/DRI/AST4). Ce système centralise les informations relatives aux dossiers de qualification, aux avis d'évaluation émis par les comités de domaine, et assure le suivi de l'évolution des qualifications. Il permet également d'informer les agents sur l'état de leurs demandes.

Le système SIREINES est un SI à enjeux, hébergé sur une plateforme IaaS (ECO4) au Centre-serveur ministériel de Paris La Défense, et fait l'objet d'une déclaration CNIL (n°1034232 du 29/09/2014) concernant le traitement de données à caractère personnel (coordonnées des experts et spécialistes).

### 1.2. Objectifs stratégiques et attendus du projet

Les objectifs principaux du projet SIREINES sont les suivants :

*   **Centralisation de l'information :** Constituer une base de données unique et fiable des experts et spécialistes scientifiques et techniques, incluant leurs dossiers de qualification et les avis d'évaluation.
*   **Optimisation des processus :** Rationaliser et fluidifier les processus de gestion des demandes de qualification, du dépôt initial à l'information de l'agent.
*   **Aide à la décision :** Fournir des outils d'analyse et de reporting pour le suivi de l'évolution des qualifications, la fréquence des mots-clés, la pyramide des âges, et d'autres indicateurs pertinents pour la gestion des compétences.
*   **Conformité réglementaire :** Assurer la conformité avec les réglementations en vigueur, notamment le RGPD et les exigences d'accessibilité.
*   **Amélioration de l'expérience utilisateur :** Offrir une interface intuitive et efficace pour les administrateurs, les gestionnaires de comités et les agents.

### 1.3. Périmètre fonctionnel (inclus / exclus)

#### 1.3.1. Fonctions incluses

Le système SIREINES doit couvrir les fonctionnalités suivantes :

*   **Gestion des dossiers :** Création, consultation, modification, recherche et archivage des dossiers de qualification des agents.
*   **Gestion des agents :** Consultation des informations des agents liées à leurs qualifications.
*   **Gestion des référentiels :** Administration des listes de valeurs (corps, grades, structures, comités de domaine, mots-clés, qualifications, rapporteurs, balises, gestionnaires).
*   **Gestion des séances :** Planification, organisation et suivi des séances des comités d'évaluation, incluant l'affectation des dossiers.
*   **Génération de courriers :** Création et personnalisation de courriers types liés aux étapes du processus de qualification.
*   **Import de données :** Intégration de données massives (ex: agents, dossiers) via des fichiers structurés.
*   **Extraction et reporting :** Génération de rapports statistiques et d'extractions de données personnalisables.
*   **Gestion des accès :** Authentification et gestion des autorisations des utilisateurs basées sur des rôles.
*   **Consultation d'informations :** Accès aux pages d'information générales (accueil, contact, mentions légales).

#### 1.3.2. Fonctions exclues

Les fonctionnalités suivantes sont explicitement exclues du périmètre de ce projet :

*   La gestion des ressources humaines non directement liées au processus de qualification (ex: gestion des carrières, paie).
*   L'intégration native avec des systèmes d'information externes autres que le système d'authentification centralisé (Cerbère) et les outils de reporting (BIRT/Talend). Toute nouvelle intégration devra faire l'objet d'une étude spécifique.
*   La gestion des infrastructures techniques (serveurs, bases de données) qui relève de l'environnement d'hébergement (IaaS ECO4).

---

## 2. Expression fonctionnelle du besoin ↩ [Retour au sommaire](#table-des-matières)

Cette section détaille les fonctions de service attendues du système, en se concentrant sur le "quoi" et non le "comment". Chaque fonction est décrite avec des critères d'appréciation mesurables et un niveau d'importance pour l'évaluation des offres.

### 2.1. Fonctions de service

| ID Fonction | Fonction de service (quoi) | Description | Critères d'appréciation | Niveau d'importance (MoSCoW) | Contraintes associées |
| :---------- | :------------------------- | :---------- | :---------------------- | :-------------------------- | :-------------------- |
| F.01        | **Gérer les dossiers de qualification** | Permettre aux utilisateurs autorisés de créer, consulter, modifier, rechercher et archiver les dossiers de qualification des agents. Cela inclut la gestion des informations générales, les fiches de conclusion, les courriers associés et les documents justificatifs. | - Temps de réponse pour la recherche de dossier < 3 secondes.<br>- Taux de succès des opérations CRUD > 99%.<br>- Intégrité des données des dossiers garantie (pas de perte d'information).<br>- Traçabilité complète des modifications apportées aux dossiers. | Must-have | - Conformité CNIL/RGPD pour les données personnelles.<br>- Accès basé sur les rôles utilisateur. |
| F.02        | **Rechercher et consulter les agents** | Offrir la possibilité de rechercher des agents et de consulter leurs informations pertinentes pour le processus de qualification. | - Temps de réponse pour la recherche d'agent < 2 secondes.<br>- Exhaustivité des informations affichées pour l'agent (nom, prénom, corps, grade, structure, etc.). | Must-have | - Les informations proviennent de sources fiables (synchronisation ou saisie contrôlée). |
| F.03        | **Administrer les référentiels** | Permettre la gestion (création, modification, suppression, recherche) des données de référence utilisées par le système, telles que les corps, grades, structures, comités de domaine, mots-clés, qualifications, rapporteurs, balises et gestionnaires. | - Cohérence des données référentielles assurée.<br>- Facilité de mise à jour des entrées référentielles.<br>- Disponibilité des référentiels pour toutes les fonctions nécessitant une liste de valeurs. | Must-have | - Unicité des libellés pour chaque référentiel.<br>- Historisation des modifications des référentiels si pertinent. |
| F.04        | **Gérer les séances d'évaluation** | Permettre la planification, la création, la modification et le suivi des séances d'évaluation des comités de domaine, ainsi que l'affectation des dossiers aux séances. | - Possibilité d'affecter plusieurs dossiers à une même séance.<br>- Visualisation claire des dossiers affectés à une séance.<br>- Validation des dates de séance (passée