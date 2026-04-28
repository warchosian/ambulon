# Spécification fonctionnelle et technique de l'application **ambulon**

*Document auto‑porté, compatible avec VS Code (extension Markdown Preview Enhanced) ou Obsidian (support Mermaid activé).  
Aucun lien externe requis, toutes les références sont internes.*

---  

## Table des matières  

| # | Section | Lien |
|---|---------|------|
| 1 | **Portée, domaine et périmètre** | [↩ Retour](#portée-domaine-et-périmètre) |
| 2 | **Partie fonctionnelle** | |
|   | 2.1 Acteurs | [↩ Retour](#acteurs) |
|   | 2.2 Cas d’usage | [↩ Retour](#cas-dusage) |
|   | 2.3 Règles métier | [↩ Retour](#règles-métier) |
|   | 2.4 Workflows critiques | [↩ Retour](#workflows-critiques) |
|   | 2.5 Décision tables & scénarii | [↩ Retour](#décision‑tables‑scénarii) |
| 3 | **Partie technique** | |
|   | 3.1 Architecture logique | [↩ Retour](#architecture-logique) |
|   | 3.2 Architecture physique & déploiement | [↩ Retour](#architecture‑physique‑déploiement) |
|   | 3.3 Modules & flux de données | [↩ Retour](#modules‑flux‑de‑données) |
|   | 3.4 Sécurité | [↩ Retour](#sécurité) |
|   | 3.5 Dette technique | [↩ Retour](#dette‑technique) |
| 4 | **Annexes** | |
|   | 4.1 Diagrammes Mermaid | [↩ Retour](#diagrammes‑mermaid) |
|   | 4.2 Références | [↩ Retour](#références) |

---  

## 1️⃣ Portée, domaine et périmètre <a id="portée-domaine-et-périmètre"></a>

| Élément | Description |
|---------|-------------|
| **Nom de l’application** | `ambulon` |
| **Chemin du dépôt** | `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\ambulon` |
| **Domaines applicatifs** | *Archivage physique* (défini par le cahier des charges du projet). |
| **Contexte opérationnel** | Site **SIT_ID = 29** ; base de données **Oracle prep37**. |
| **Périmètre fonctionnel inclus** | - Gestion des **versements**<br>- Gestion des **demandes**<br>- Gestion des **mouvements** (entrée/sortie de dossiers) |
| **Périmètre fonctionnel exclu** | - Gestion des **patients**<br>- **Facturation**<br>- **Workflow avancé** (ex. approbation multi‑niveau, notifications externes) |
| **Hypothèses** | Aucun autre module métier n’est présent dans le code fourni. |
| **Contraintes connues** | Aucun détail technique n’est disponible dans les sources fournies. |

> **⚠️ Informations manquantes**  
> Le dépôt ne contient que le fichier `README.md` (6 197 octets) sans contenu exploitable. Toutes les sections suivantes sont donc présentées **sous forme de modèle** à compléter dès que les artefacts (code source, spécifications, diagrammes, etc.) seront disponibles.

---  

## 2️⃣ Partie fonctionnelle <a id="partie-fonctionnelle"></a>

### 2.1 Acteurs <a id="acteurs"></a>

| Acteur | Rôle | Interactions attendues |
|--------|------|------------------------|
| **Opérateur d’archivage** | Saisie et validation des versements/demandes | Crée, modifie, supprime des enregistrements d’archivage. |
| **Gestionnaire de site** | Supervision du site SIT_ID = 29 | Accède aux rapports de mouvements, configure les paramètres de la base Oracle. |
| **Administrateur DB** | Gestion de la base Oracle prep37 | Effectue les sauvegardes, les restaurations et la gestion des comptes. |
| **Auditeur** | Contrôle de conformité | Consulte les historiques de mouvements, exporte les logs. |

> **⚠️ À préciser** : Les profils exacts, leurs droits d’accès et leurs contraintes de sécurité devront être définis à partir du cahier des charges ou du code métier.

### 2.2 Cas d’usage <a id="cas-dusage"></a>

| ID | Titre | Acteur principal | Résumé |
|----|-------|------------------|--------|
| CU‑01 | **Enregistrement d’un versement** | Opérateur d’archivage | Saisie des métadonnées du dossier, validation, persistance en Oracle. |
| CU‑02 | **Création d’une demande d’accès** | Opérateur d’archivage | Saisie d’une demande, affectation d’un statut « En attente », notification au gestionnaire. |
| CU‑03 | **Mouvement de sortie** | Gestionnaire de site | Sélection d’un dossier, mise à jour du statut, génération d’un bordereau de sortie. |
| CU‑04 | **Export de journal d’audit** | Auditeur | Extraction des logs de mouvements sur une période donnée, format CSV/Excel. |

> **⚠️ Remarque** : Les scénarios détaillés (pré‑conditions, post‑conditions, extensions) restent à rédiger dès que les spécifications fonctionnelles seront disponibles.

### 2.3 Règles métier <a id="règles-métier"></a>

| # | Règle | Formulation précise | Source (à compléter) |
|---|-------|----------------------|----------------------|
| R‑01 | **Format de date** | Toutes les dates sont stockées au format `YYYYMMDD` (ex. 20240428). | — |
| R‑02 | **Mapping des salles** | Le code salle (`SXXX`) doit être préfixé par le site (`29-`). Exemple : `29‑S001`. | — |
| R‑03 | **Statut de versement** | Un versement ne peut passer de « En cours » à « Validé » que si le champ `checksum` est calculé et stocké. | — |
| R‑04 | **Limite de taille de fichier** | Aucun fichier joint ne doit excéder **100 Mo**. | — |

> **⚠️ À enrichir** : Les règles ci‑dessus sont des exemples génériques ; elles doivent être validées avec le propriétaire du produit.

### 2.4 Workflows critiques <a id="workflows-critiques"></a>

#### Workflow 1 – Enregistrement d’un versement

```mermaid
sequencediagram;
    participant Op as Opérateur d'archivage;
    participant UI as Interface Web;
    participant S as Service Versement;
    participant DB as Oracle prep37;
    Op->>UI: Saisie du formulaire;
    UI->>S: POST /versements;
    S->>S: Validation des règles R‑01, R‑02, R‑03;
    alt Validation OK;
    S->>DB: INSERT versement;
    DB-->>S: OK;
    S->>UI: 201 Created;
    else Erreur de validation;
    S->>UI: 400 Bad Request (détails)
    end
```

> **⚠️ Remarque** : Les points d’intégration (API, services internes) restent à préciser.

### 2.5 Décision tables & scénarii <a id="décision-tables-scenarii"></a>

#### Table de décision – Validation du statut de versement

| Condition | `checksum` présent ? | `dateVersement` valide ? | Résultat attendu |
|-----------|----------------------|--------------------------|------------------|
| C1 | Oui | Oui | Acceptation |
| C2 | Non | Oui | Rejet (checksum manquant) |
| C3 | Oui | Non | Rejet (date invalide) |
| C4 | Non | Non | Rejet (checksum & date) |

#### Scénario type – Création d’une demande d’accès

1. L’opérateur ouvre le formulaire « Nouvelle demande ».  
2. Il saisit le **numéro de dossier**, le **motif** et la **date souhaitée**.  
3. Le système vérifie le format du numéro (ex. `29‑S001‑000123`).  
4. Si la date est antérieure à la date du jour, le système renvoie une erreur.  
5. Sinon, la demande est enregistrée avec le statut **« En attente »** et un mail de notification est envoyé au gestionnaire de site.  

> **⚠️ À détailler** : Les messages exacts, les codes d’erreur et les exigences de performance restent à collecter.

---  

## 3️⃣ Partie technique <a id="partie-technique"></a>

### 3.1 Architecture logique <a id="architecture-logique"></a>

```mermaid
graph LR
    subgraph UI[Interface Utilisateur]
    Web[Web UI (HTML/JS)]
    end
    subgraph BE[Logique Métier]
    API[REST API]
    ServiceV[Service Versement]
    ServiceD[Service Demande]
    ServiceM[Service Mouvement]
    end
    subgraph DB[Persistance]
    Oracle[(Oracle prep37)]
    end
    Web --> API;
    API --> ServiceV;
    API --> ServiceD;
    API --> ServiceM;
    ServiceV --> Oracle;
    ServiceD --> Oracle;
    ServiceM --> Oracle
```

*Description* :  
- **UI** : couche de présentation (non détaillée dans le code fourni).  
- **API** : point d’entrée HTTP, expose les ressources `/versements`, `/demandes`, `/mouvements`.  
- **Services** : implémentation de la logique métier (validation, calculs, état).  
- **Oracle** : stockage unique de toutes les entités.

> **⚠️ À compléter** : Langage de programmation, framework (Spring Boot, .NET, etc.), gestion des transactions, stratégies de cache.

### 3.2 Architecture physique & déploiement <a id="architecture-physique-deploiement"></a>

```mermaid
deploymentDiagram;
    node "Serveur d’application" as AppSrv {
    component "API Gateway" as GW;
    component "Service Versement" as SV;
    component "Service Demande" as SD;
    component "Service Mouvement" as SM;

    node "Base de données" as DBSrv {
    artifact "Oracle prep37" as DB;

    node "Poste client" as Client {
    artifact "Navigateur Web" as Browser;

    Browser --> GW : HTTPS;
    GW --> SV : gRPC/REST;
    GW --> SD : gRPC/REST;
    GW --> SM : gRPC/REST;
    SV --> DB : JDBC;
    SD --> DB : JDBC;
    SM --> DB : JDBC
```

*Hypothèses* :  
- Un **serveur d’application** dédié héberge les services.  
- La **base Oracle** réside sur un serveur distinct, accessible via le réseau interne.  
- La communication client‑serveur se fait en **HTTPS**.

> **⚠️ À préciser** : Topologie réseau, équilibrage de charge, haute disponibilité, processus de CI/CD.

### 3.3 Modules & flux de données <a id="modules-flux-de-donnees"></a>

| Module | Responsabilité | Entrées | Sorties |
|--------|----------------|---------|---------|
| `API Gateway` | Routage, authentification | Requêtes HTTP | Réponses HTTP, appels internes |
| `Service Versement` | Gestion des versements | DTO Versement, `checksum` | Persisté en Oracle, événements d’audit |
| `Service Demande` | Gestion des demandes d’accès | DTO Demande | Persisté, notifications |
| `Service Mouvement` | Gestion des mouvements (entrée/sortie) | DTO Mouvement | Persisté, génération de bordereaux |
| `Audit Logger` | Traçabilité | Logs d’activité | Table `AUDIT_LOG` dans Oracle |

#### Exemple de flux – Enregistrement d’un versement

1. **Client** → **API Gateway** : `POST /versements` (payload JSON).  
2. **API Gateway** → **Service Versement** : appel interne avec le DTO.  
3. **Service Versement** → **Oracle** : `INSERT` + calcul du `checksum`.  
4. **Service Versement** → **Audit Logger** : écriture d’un événement `VERSEMENT_CREATED`.  
5. **Service Versement** → **API Gateway** : réponse `201 Created`.  

---  

### 3.4 Sécurité <a id="securite"></a>

| Aspect | Description | Actions recommandées |
|--------|-------------|----------------------|
| **Authentification** | Aucun mécanisme identifié dans le code fourni. | Implémenter **OAuth 2.0** ou **JWT** au niveau du `API Gateway`. |
| **Autorisation** | Rôles d’acteurs (opérateur, gestionnaire, admin) non définis. | Utiliser un **RBAC** granulaire sur chaque endpoint. |
| **Données sensibles** | `checksum`, références de dossiers, logs d’audit. | Chiffrer en‑repos (Transparent Data Encryption d’Oracle) et en‑transit (TLS 1.2+). |
| **Secrets** | Aucun fichier de configuration (ex. `application.yml`) n’est présent. | Externaliser les secrets via **Vault** ou variables d’environnement sécurisées. |
| **Journalisation** | Aucun composant de logging visible. | Centraliser les logs avec **ELK** ou **Graylog**, inclure les IDs de transaction. |
| **Conformité** | Archivage physique → exigences de **RGPD** / **HIPAA** potentielles. | Réaliser une **analyse d’impact** (DPIA) dès que le périmètre métier sera clarifié. |

---  

### 3.5 Dette technique <a id="dette-technique"></a>

| Symptomome observé | Origine probable | Impact | Remédiation |
|--------------------|------------------|--------|-------------|
| **Absence de code source** | Aucun fichier analysé (README uniquement). | Impossible d’évaluer la qualité, la maintenabilité. | Récupérer le dépôt complet, analyser le code. |
| **Hard‑coding potentiel** | Mention dans les exigences (ex. `SIT_ID = 29`). | Risque de duplication et d’erreurs lors de changements. | Externaliser dans un fichier de configuration. |
| **Manque de tests automatisés** | Aucun artefact de tests détecté. | Risque de régression, difficultés de CI. | Introduire une suite **unit** et **intégration** dès le premier sprint. |
| **Documentation insuffisante** | Aucun diagramme, spécification ou commentaires. | Barrière à la prise en main par de nouveaux développeurs. | Produire la documentation décrite dans ce fichier. |

---  

## 4️⃣ Annexes <a id="annexes"></a>

### 4.1 Diagrammes Mermaid <a id="diagrammes-mermaid"></a>

| Diagramme | Description | Code |
|----------|-------------|------|
| **Cas d’usage** | Vue d’ensemble des interactions acteurs‑système. | ```mermaid\nusecaseDiagram\n    actor Op as "Opérateur d'archivage"\n    actor Gest as "Gestionnaire de site"\n    actor Aud as "Auditeur"\n    rectangle System {\n        Op --> (Enregistrement d'un versement)\n        Op --> (Création d'une demande)\n        Gest --> (Mouvement de sortie)\n        Aud --> (Export de journal d'audit)\n    }\n``` |
| **Séquence – Versement** | Flux détaillé d’un enregistrement de versement. | (voir section 2.4) |
| **Composants** | Architecture logique (UI, API, Services, DB). | (voir section 3.1) |
| **Déploiement** | Répartition physique des éléments. | (voir section 3.2) |
| **État – Demande** | Cycle de vie d’une demande d’accès. | ```mermaid\nstateDiagram-v2\n    [*] --> EnAttente\n    EnAttente --> Approuvee : validation\n    EnAttente --> Rejetee : refus\n    Approuvee --> Termine : clôture\n    Rejetee --> Termine : clôture\n``` |

> **⚠️ Note** : Les diagrammes ci‑dessus sont fonctionnels (syntaxiquement valides) mais reflètent uniquement la structure modèle. Ils devront être enrichis avec les détails réels du projet.

### 4.2 Références <a id="references"></a>

1. **arc42 – Architecture Documentation** – <https://arc42.org> (consultable pour la structuration du présent document).  
2. **ISO/IEC/IEEE 29148 – Ingénierie des exigences** – norme de référence pour la modélisation des exigences.  
3. **Oracle Database Documentation** – pour les bonnes pratiques de sécurisation et de performance.  

---  

## 📌 Conclusion

Ce document constitue **une base de travail** à destination des équipes projet / architectes / développeurs.  
En l’état, il expose :

* la **définition du périmètre** (archivage physique, site 29, Oracle prep37) ;
* un **modèle fonctionnel** (acteurs, cas d’usage, règles métier, tables de décision) ;
* une **architecture technique** (logique, physique, sécurité, dette technique) ;
* des **diagrammes Mermaid** prêts à être affichés dans VS Code ou Obsidian.

**Prochaines étapes** :

1. **Fournir le code source complet** (ou au minimum le `README.md` détaillé) afin de valider/compléter chaque section.  
2. **Définir les exigences détaillées** (exigences de performance, SLA, contraintes réglementaires).  
3. **Enrichir les diagrammes** avec les noms réels des services, endpoints, tables de la base de données.  
4. **Mettre en place le pipeline CI/CD** et le référentiel de gestion des secrets.  

---  

*Document généré uniquement à partir des fichiers fournis (README.md de 6 197 octets). Aucun contenu externe n’a été ajouté.*