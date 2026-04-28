# 📄 Cahier des Charges Fonctionnel (CCF) – **SIAM 2**  
**Version 0.1** – 2026‑04‑28  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet <a id="intro"></a>

| Élément | Description |
|--------|-------------|
| **Nom du projet** | SIAM 2 (Système d’Information d’Archivage et de Management – version 2) |
| **ID** | 578 |
| **Statut** | En construction |
| **Portée géographique** | Nationale (France) |
| **Environnement d’accès** | Application Web (LAMP) – SaaS (ECO4) hébergée au centre‑serveur ministériel Paris La Défense |
| **Date de démarrage** | 01/01/2024 |
| **Objectif stratégique** | Moderniser la gestion des archives papier intermédiaires du ministère, garantir la traçabilité, la disponibilité et la conformité légale (Code du patrimoine, RGPD) tout en facilitant la diffusion et la valorisation des documents. |
| **Périmètre fonctionnel** | <ul><li>Collecte, concentration, valorisation, diffusion et support d’archives papier.</li><li>Gestion de métadonnées, recherche, consultation, traçabilité et reporting.</li></ul> |
| **Périmètre exclu** | <ul><li>Gestion des archives numériques déjà stockées dans d’autres SI (ex. DMP, SIA).</li><li>Gestion du stockage physique (logistique d’entrepôt).</li></ul> |

↩ [Retour au sommaire](#toc)

---  

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) <a id="besoin"></a>

| **Fonction de service** | **Description (quoi)** | **Critères d’appréciation (mesurables)** | **Pondération** | **Contraintes** |
|------------------------|------------------------|------------------------------------------|----------------|-----------------|
| **F1 – Collecte d’archives** | Permettre à un agent de saisir, numériser (le cas échéant) et référencer une archive papier entrante. | <ul><li>Temps moyen de saisie ≤ 5 min par archive.</li><li>≥ 99 % des champs obligatoires remplis.</li><li>Validation de la conformité du format de référence (norme ISO 15489).</li></ul> | 20 % | Respect du niveau de confidentialité (DICT 2). |
| **F2 – Concentration** | Regrouper plusieurs archives liées (ex. dossiers, séries) dans un même dossier logique. | <ul><li>Capacité à créer un lot de ≥ 100 archives en une opération.</li><li>Traçabilité du lien « parent‑enfant » enregistrée dans le journal d’audit.</li></ul> | 15 % | Aucun dépassement du volume maximal de 10 GB par lot (limite technique). |
| **F3 – Valorisation** | Enrichir les archives de métadonnées (descriptives, techniques, juridiques). | <ul><li>≥ 95 % des métadonnées obligatoires renseignées.</li><li>Utilisation d’un vocabulaire contrôlé (thésaurus métier).</li></ul> | 15 % | Conformité aux exigences du RGPD (article 89). |
| **F4 – Diffusion** | Rendre les archives consultables et téléchargeables selon les droits d’accès. | <ul><li>Temps de réponse ≤ 2 s pour une recherche simple.</li><li>Gestion des droits d’accès selon le modèle DICT (Disponibilité 2, Intégrité 2, Confidentialité 2, Traçabilité 1).</li></ul> | 20 % | Accès uniquement via HTTPS/TLS 1.3, filtrage IP autorisé. |
| **F5 – Support & Assistance** | Fournir une aide en ligne (FAQ, tickets) et un suivi de la résolution. | <ul><li>Temps moyen de prise en charge ≤ 30 min.</li><li>Taux de résolution au premier contact ≥ 80 %.</li></ul> | 10 % | Respect du SLA « Production » du centre‑serveur. |
| **F6 – Gestion des droits et traçabilité (DICT)** | Appliquer les exigences de disponibilité, intégrité, confidentialité, traçabilité. | <ul><li>Disponibilité ≥ 99,5 % (code 2).</li><li>Intégrité contrôlée par checksum quotidien.</li><li>Confidentialité assurée par classification et chiffrement au repos.</li><li>Traçabilité : journal d’audit conservé 5 ans.</li></ul> | 15 % | Conformité aux référentiels ISO 27001, RGPD. |
| **F7 – Reporting & Pilotage** | Générer des indicateurs de performance (ex. nombre d’archives collectées, temps de diffusion). | <ul><li>Tableaux de bord actualisés quotidiennement.</li><li>Export PDF/CSV disponible sous 5 sec.</li></ul> | 5 % | Aucun impact sur la disponibilité du service. |

↩ [Retour au sommaire](#toc)

---  

## 3️⃣ Acteurs et parties prenantes <a id="acteurs"></a>

| **Acteur** | **Rôle** | **Objectifs** | **Besoins spécifiques** |
|------------|----------|--------------|------------------------|
| **Agent** | Utilisateur final – collecte d’archives | Saisir rapidement les archives, garantir la conformité des métadonnées. | Interface simple, assistance contextuelle, validation de champ. |
| **Service d’administration centrale** | Gestion globale des droits, suivi de la conformité | Piloter la politique d’archivage, assurer le respect du DICT. | Gestion des profils, reporting consolidé, auditabilité. |
| **Service départemental / régional** | Utilisateurs intermédiaires – diffusion locale | Accéder aux archives pertinentes, répondre aux demandes de consultation. | Recherche avancée, filtres géographiques, suivi de demandes. |
| **MOA SSI (Sécurité des Systèmes d’Information)** | Garant de la sécurité et de la conformité | Veiller à la mise en œuvre du DICT, RGPD. | Tableaux de bord sécurité, alertes d’incident. |
| **MOE (Équipe produit)** | Conception, développement, exploitation | Livrer une solution fiable, évolutive et maintenable. | Spécifications fonctionnelles détaillées, environnement de test. |
| **Direction du projet (DG, DNUM, PNM, DPNM3)** | Pilotage stratégique | Assurer la cohérence avec les obligations légales et la politique ministérielle. | Visibilité sur le planning, coûts, risques. |
| **Utilisateurs externes (public)** | Consultation d’archives publiques | Accéder aux documents rendus publics. | Interface publique, respect du droit d’accès. |

↩ [Retour au sommaire](#toc)

---  

## 4️⃣ Cas d’usage (Use Cases) <a id="usecases"></a>

### 4.1 Diagramme de cas d’utilisation (Mermaid)

```mermaid
usecaseDiagram;
    actor Agent as A;
    actor Service Central as SC;
    actor Service Départemental as SD;
    actor Service Régional as SR;
    actor MOA SSI as MOA;
    actor MOE as MOE;
    A --> (Collecter une archive)
    A --> (Enrichir les métadonnées)
    A --> (Créer un lot de concentration)

    SC --> (Gérer les droits)
    SC --> (Produire les rapports de conformité)

    SD --> (Rechercher une archive)
    SD --> (Consulter une archive)
    SR --> (Rechercher une archive)

    MOA --> (Auditer la traçabilité)
    MOA --> (Vérifier la disponibilité)

    MOE --> (Déployer une version)
    MOE --> (Maintenir l’infrastructure)
```

### 4.2 Tableau récapitulatif des cas d’usage

| **Code** | **Nom du cas d’usage** | **Acteur(s) principal(aux)** | **Scénario nominal** | **Scénarios alternatifs / d’erreur** | **Pré‑conditions** | **Post‑conditions** |
|----------|-----------------------|------------------------------|----------------------|--------------------------------------|--------------------|---------------------|
| UC‑01 | Collecter une archive | Agent | 1. L’agent ouvre le formulaire de collecte.<br>2. Saisit les champs obligatoires (titre, date, provenance).<br>3. Téléverse le document numérisé (facultatif).<br>4. Valide → l’archive est enregistrée avec statut *Collectée*. | - UC‑01‑A : Le formulaire est incomplet → message d’erreur.<br>- UC‑01‑B : Le fichier dépasse la taille maximale → rejet. | L’agent est authentifié, le module de collecte est disponible. | L’archive apparaît dans le catalogue avec métadonnées partielles. |
| UC‑02 | Concentrer des archives | Agent | 1. Sélection d’un ou plusieurs enregistrements.<br>2. Choix d’un dossier parent.<br>3. Confirmation → les liens « parent‑enfant » sont créés. | - UC‑02‑A : Aucun élément sélectionné → message d’avertissement.<br>- UC‑02‑B : Le dossier cible est verrouillé → refus. | Au moins deux archives existantes, droits de concentration. | Les archives sont rattachées au même dossier logique, journal d’audit mis à jour. |
| UC‑03 | Enrichir les métadonnées | Agent | 1. Ouvre la fiche d’une archive.<br>2. Modifie/complète les champs métadonnées.<br>3. Sauvegarde → les métadonnées sont versionnées. | - UC‑03‑A : Valeur non conforme au vocabulaire → rejet.<br>- UC‑03‑B : Conflit de version (mise à jour concurrente) → résolution. | L’utilisateur possède le droit *édition*. | Métadonnées validées, indice de recherche mis à jour. |
| UC‑04 | Rechercher une archive | Service Central / Départemental / Régional | 1. Saisit des critères (date, mot‑clé, service).<br>2. Lance la recherche.<br>3. Résultats affichés, possibilité de filtrer. | - UC‑04‑A : Aucun résultat → message d’information.<br>- UC‑04‑B : Recherche trop large → temps de réponse > 5 s → suggestion de raffinement. | Le moteur de recherche est opérationnel, l’acteur est authentifié. | Liste d’archives correspondante présentée, possibilité d’accès ou de demande. |
| UC‑05 | Diffuser une archive | Service Central / Départemental / Régional | 1. Sélectionne une archive autorisée.<br>2. Clique sur *Consulter / Télécharger*.<br>3. Le système vérifie les droits, délivre le document. | - UC‑05‑A : Droits insuffisants → accès refusé, journal d’incident.<br>- UC‑05‑B : Archive en cours de restauration → message d’attente. | Droits d’accès valides, archive disponible. | L’utilisateur visualise ou télécharge le document, audit de l’accès enregistré. |
| UC‑06 | Gérer les droits (DICT) | MOA SSI | 1. Accède à la console d’administration.<br>2. Définit les profils (Disponibilité 2, etc.).<br>3. Applique les règles aux services. | - UC‑06‑A : Conflit de règle → alerte.<br>- UC‑06‑B : Modification non autorisée → rejet. | Authentification forte, rôle *admin‑security*. | Droits actualisés, journal d’audit mis à jour. |
| UC‑07 | Produire un rapport de conformité | Service Central | 1. Sélectionne le type de rapport (ex. DICT, volume d’archives).<br>2. Lance le calcul.<br>3. Export PDF/CSV. | - UC‑07‑A : Temps de génération > 10 s → optimisation requise.<br>- UC‑07‑B : Aucun résultat (période vide) → message d’information. | Données de suivi disponibles. | Rapport généré, disponible au téléchargement. |

↩ [Retour au sommaire](#toc)

---  

## 5️⃣ Processus métier (BPMN) <a id="processus"></a>

### 5.1 Diagramme BPMN (Mermaid)

```mermaid
bpmnDiagram;
    participant Agent;
    participant "Service Central" as SC;
    participant "MOA SSI" as MOA;
    startEvent(idStart, "Début du processus")
    task(idCollect, "Collecte d’une archive")
    exclusiveGateway(idCheck, "Archive valide ?")
    task(idEnrich, "Enrichir les métadonnées")
    task(idConcent, "Concentration (lot)")
    task(idDiff, "Diffusion / Consultation")
    task(idAudit, "Audit DICT")
    endEvent(idEnd, "Fin du processus")

    startEvent --> idCollect --> idCheck;
    idCheck -->|Oui| idEnrich --> idConcent --> idDiff --> idAudit --> idEnd;
    idCheck -->|Non| endEvent(idReject, "Rejet") --> idEnd
```

### 5.2 Description textuelle

| **Étape** | **Responsable** | **Activité** | **Points de contrôle / règle métier** |
|----------|----------------|--------------|--------------------------------------|
| 1. Collecte | Agent | Saisie des informations d’une archive papier. | Tous les champs obligatoires doivent être renseignés (R‑M01). |
| 2. Validation | Système | Vérifie la conformité du formulaire. | Si non conforme → rejet (R‑M02). |
| 3. Enrichissement | Agent | Ajout de métadonnées complémentaires. | Utilisation d’un vocabulaire contrôlé (R‑M03). |
| 4. Concentration | Agent | Regroupement d’archives liées. | Volume du lot ≤ 10 GB (R‑M04). |
| 5. Diffusion | Service (central/départemental) | Consultation ou téléchargement selon droits. | Vérification des droits DICT (R‑S01). |
| 6. Audit DICT | MOA SSI | Contrôle de disponibilité, intégrité, confidentialité, traçabilité. | Journal d’audit conservé 5 ans (R‑S02). |
| 7. Reporting | Service Central | Génération des indicateurs de performance. | Reporting quotidien (R‑R01). |

↩ [Retour au sommaire](#toc)

---  

## 6️⃣ Règles métier et contraintes fonctionnelles <a id="regles"></a>

| **Code** | **Formulation (IF … THEN …)** | **Type** | **Référence** |
|----------|------------------------------|----------|---------------|
| R‑M01 | IF l’utilisateur soumet le formulaire de collecte, THEN tous les champs *Titre, Date, Provenance* doivent être remplis. | Métadonnées obligatoires | NF EN 16271 |
| R‑M02 | IF le formulaire comporte des valeurs hors du vocabulaire contrôlé, THEN bloquer la validation et afficher le message d’erreur. | Validation | ISO 25964 |
| R‑M03 | IF l’archive est associée à un lot, THEN le volume total du lot ne doit pas dépasser 10 GB. | Contraintes de taille | Infrastructure interne |
| R‑M04 | IF l’utilisateur demande la diffusion, THEN le système vérifie le profil DICT (Disponibilité 2, Intégrité 2, Confidentialité 2, Traçabilité 1). | Sécurité | DICT 2221 |
| R‑S01 | IF un accès est consenti, THEN le journal d’audit doit être mis à jour avec *userId, timestamp, action*. | Traçabilité | ISO 27001 |
| R‑S02 | IF la donnée est stockée, THEN le chiffrement AES‑256 doit être appliqué au repos. | Confidentialité | RGPD Art 89 |
| R‑R01 | IF le reporting quotidien est généré, THEN le fichier doit être disponible en moins de 5 s. | Performance | SLA Production |
| C‑L01 | IF le système est en production, THEN la disponibilité doit être ≥ 99,5 % (code 2). | Disponibilité | DICT 2221 |

↩ [Retour au sommaire](#toc)

---  

## 7️⃣ Parcours utilisateurs (User Journey) <a id="journey"></a>

### 7.1 Parcours « Collecte d’une archive » (Agent)

| **Étape** | **Action de l’utilisateur** | **Interaction système** | **Critères d’acceptation (Given/When/Then)** |
|-----------|----------------------------|------------------------|--------------------------------------------|
| 1 | Ouvre le tableau de bord | Affiche le bouton *Nouvelle collecte* | **Given** l’agent est connecté, **When** il clique sur *Nouvelle collecte*, **Then** le formulaire de collecte s’affiche. |
| 2 | Remplit les champs obligatoires | Validation en temps réel | **Given** le formulaire vide, **When** il saisit un titre valide, **Then** le champ passe en vert. |
| 3 | Joins un fichier numérisé (optionnel) | Vérifie la taille ≤ 20 MB | **Given** le fichier ≤ 20 MB, **When** il le téléverse, **Then** le système accepte le fichier. |
| 4 | Clique *Enregistrer* | Enregistre l’archive, crée le statut *Collectée*, journal d’audit. | **Given** le formulaire complet, **When** il clique *Enregistrer*, **Then** l’archive apparaît dans le catalogue. |
| 5 | Recevoir confirmation | Message « Archive enregistrée » | **Given** l’enregistrement réussi, **When** le système renvoie la réponse, **Then** l’agent voit le message de succès. |

### 7.2 Parcours « Consultation d’une archive » (Service Départemental)

| Étape | Action | Interaction | Critères d’acceptation |
|-------|--------|-------------|------------------------|
| 1 | Saisit un mot‑clé dans la barre de recherche | Le moteur interroge l’index Elasticsearch | **Given** le service est authentifié, **When** il saisit *« Plan de ville »*, **Then** les résultats pertinents s’affichent sous 2 s. |
| 2 | Sélectionne une archive | Vérification des droits DICT | **Given** l’archive possède le droit *Confidentialité 2*, **When** le service a ce droit, **Then** le bouton *Consulter* est activé. |
| 3 | Clique *Consulter* | Le document est affiché en mode lecture‑seule | **Given** le droit est validé, **When** il clique *Consulter*, **Then** le document s’ouvre dans le visualiseur. |
| 4 | Télécharge le fichier | Le fichier est téléchargé via HTTPS | **Given** le téléchargement est autorisé, **When** il lance le téléchargement, **Then** le fichier est reçu sans altération (checksum OK). |

↩ [Retour au sommaire](#toc)

---  

## 8️⃣ Modèle Conceptuel de Données (MCD) <a id="mcd"></a>

### 8.1 Diagramme de classes (UML simplifié – Mermaid)

```mermaid
classDiagram
    class Archive {
        +id : UUID;
        +titre : String;
        +dateCréation : Date;
        +provenance : String;
        +statut : Enum{Collectée, Enrichie, Concentrée, Diffusée}
        +checksum : String;
    }
    class Metadonnée {
        +cle : String;
        +valeur : String;
        +type : Enum{Descriptive, Technique, Juridique}
    }
    class Utilisateur {
        +id : UUID;
        +nom : String;
        +email : String;
        +role : Enum{Agent, ServiceCentral, ServiceDept, ServiceReg, MOA, MOE}
    }
    class Droit {
        +disponibilité : Int;
        +intégrité : Int;
        +confidentialité : Int;
        +traçabilité : Int;
    }
    class Lot {
        +id : UUID;
        +nom : String;
        +volume : Decimal;
    }
    class JournalAudit {
        +id : UUID;
        +timestamp : DateTime;
        +action : String;
        +utilisateurId : UUID;
    }

    Archive "1" <-- "0..*" Metadonnée : possède;
    Archive "1" <-- "0..*" Lot : appartient à;
    Utilisateur "1" <-- "0..*" JournalAudit : génère;
    Utilisateur "1" <-- "0..*" Droit : possède;
    Utilisateur "1" <-- "0..*" Archive : crée
```

### 8.2 Description des entités

| **Entité** | **Attributs clés** | **Relations** |
|-----------|-------------------|---------------|
| **Archive** | `id`, `titre`, `dateCréation`, `provenance`, `statut`, `checksum` | 0..* Metadonnée, 0..* Lot, 1 Créateur (Utilisateur) |
| **Metadonnée** | `cle`, `valeur`, `type` | Belongs‑to Archive |
| **Lot** | `id`, `nom`, `volume` | Contient 0..* Archive |
| **Utilisateur** | `id`, `nom`, `email`, `role` | Possède 0..* Droit, génère 0..* JournalAudit |
| **Droit** | `disponibilité`, `intégrité`, `confidentialité`, `traçabilité` | Assigné à Utilisateur |
| **JournalAudit** | `id`, `timestamp`, `action`, `utilisateurId` | Enregistre chaque interaction critique |

↩ [Retour au sommaire](#toc)

---  

## 9️⃣ Critères d’acceptation et validation <a id="acceptation"></a>

| **Fonction** | **Critère d’acceptation** | **Méthode de validation** | **Responsable** | **Priorité (MoSCoW)** |
|--------------|---------------------------|----------------------------|------------------|-----------------------|
| F1 – Collecte | Le formulaire accepte les champs obligatoires et refuse les valeurs hors format. | Tests fonctionnels automatisés + revue manuelle. | PO / MOE | **M** (Must) |
| F2 – Concentration | Un lot de ≥ 100 archives peut être créé en ≤ 30 s. | Tests de charge (JMeter) + monitoring. | MOE | **M** |
| F3 – Valorisation | 95 % des métadonnées obligatoires sont renseignées pour chaque archive. | Audit de la base (SQL) + rapports de conformité. | MOA SSI | **S** (Should) |
| F4 – Diffusion | Temps de réponse ≤ 2 s pour une recherche simple, accès sécurisé via HTTPS. | Tests de performance + analyse des logs d’accès. | MOA SSI | **M** |
| F5 – Support | Temps moyen de prise en charge ≤ 30 min, taux de résolution au premier contact ≥ 80 %. | KPI du système de ticketing (Jira). | Support / MOA | **C** (Could) |
| F6 – DICT | Disponibilité ≥ 99,5 % sur 30 jours, journal d’audit conservé 5 ans. | Monitoring (Grafana) + audit externe. | MOA SSI | **M** |
| F7 – Reporting | Tableaux de bord actualisés quotidiennement, export < 5 s. | Tests d’intégration + revue utilisateur. | PO | **W** (Won’t – hors périmètre initial) |

↩ [Retour au sommaire](#toc)

---  

## 🔟 Annexes <a id="annexes"></a>

### 10.1 Glossaire métier

| **Terme** | **Définition** |
|-----------|----------------|
| **Archive** | Document papier ou numérisé conservé pour répondre aux exigences légales de préservation. |
| **Lot / Concentration** | Regroupement logique d’archives liées (ex. même dossier administratif). |
| **Métadonnée** | Donnée descriptive ou technique permettant de caractériser une archive. |
| **DICT** | Acronyme *Disponibilité, Intégrité, Confidentialité, Traçabilité* – exigences de sécurité. |
| **MOA** | Maîtrise d’Ouvrage – partie commanditaire du projet. |
| **MOE** | Maîtrise d’Œuvre – équipe de conception, développement et exploitation. |
| **SaaS (ECO4)** | Plateforme d’hébergement en mode Software‑as‑a‑Service, fournie par le ministère. |
| **RGPD – article 89** | Exception archivistique permettant le traitement de données à caractère personnel à des fins d’archivage. |
| **Code DI​CT 2221** | Référentiel de classification interne (Disponibilité 2, …). |

### 10.2 Référentiels et normes applicables

| **Référence** | **Intitulé** | **Objet** |
|---------------|--------------|-----------|
| NF EN 16271 | Management par la valeur – Expression fonctionnelle du besoin | Structure du CCF. |
| ISO / IEC 29148:2018 | Ingénierie des exigences | Définition des exigences fonctionnelles et non‑fonctionnelles. |
| ISO / IEC 19505 | UML 2.x | Notation des diagrammes. |
| ISO / IEC 19510 | BPMN 2.0 | Modélisation des processus métier. |
| ISO 27001 | Sécurité de l’information | Gestion des risques et exigences de sécurité. |
| RGPD (Art. 89) | Exception archivistique | Traitement des données à caractère personnel dans les archives. |
| Code du patrimoine (L.211‑1, L.211‑4, L.212‑2… ) | Obligations légales de conservation et diffusion des archives publiques. |

### 10.3 Historique des versions

| **Version** | **Date** | **Auteur** | **Modifications** |
|------------|----------|------------|-------------------|
| 0.1 | 2026‑04‑28 | ChatGPT (OpenAI) | Première rédaction du CCF – intégration des sources fournies. |
| 0.0 | – | – | Document initial (extraits de la documentation projet). |

↩ [Retour au sommaire](#toc)

---  

*Fin du Cahier des Charges Fonctionnel – SIAM 2*  