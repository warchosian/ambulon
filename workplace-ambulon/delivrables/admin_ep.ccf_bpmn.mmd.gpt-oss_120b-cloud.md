# Cahier des Charges Fonctionnel (CCF) – **admin_ep**  
*Modélisation BPMN – ISO/IEC 19510 :2013*  

> **Version** : 1.0 – 2024‑04‑27  
> **Auteur** : ChatGPT (expert BPMN)  

---  

## 1. Introduction & Contexte

| Élément | Description |
|---|---|
| **Organisation** | Ministère de la Transition Écologique & Solidaire (MTES‑MCT). L’application *admin_ep* (Administration des Établissements Publics) regroupe les données des membres des conseils d’administration (CA) et de surveillance (CS) des 96 établissements publics placés sous la tutelle du ministère. |
| **Environnement technique** | - Java 8 – Tomcat 9 (en cours de migration vers Tomcat 10) <br> - PostgreSQL 9.6 → 15 <br> - Conteneurisation (Docker) – IaaS (ECO4) <br> - Authentification Cerbère (SSO) |
| **Objectifs de la modélisation BPMN** | 1. Formaliser les processus métier (CRUD, import JORF, notifications, recherche, reporting). <br>2. Garantir la traçabilité des exigences à la réalisation (exécutabilité éventuelle). <br>3. Servir de base à l’évolution (version 2.0, migration Tomcat 10/PostgreSQL 15). |
| **Périmètre fonctionnel** | • Interface d’écriture (CRUD sur administrateurs, gestionnaires, établissements, mandats) <br>• Alimentation automatique via le JORF <br>• Authentification / habilitations Cerbère <br>• Archivage & historisation des mandats <br>• Recherche plein texte <br>• Statistiques globales <br>• Notification d’échéance de mandat (mail) <br>• Supervision & audit (logs, métriques) |
| **Glossaire métier (extraits)** | **CA** – Conseil d’administration <br>**CS** – Conseil de surveillance <br>**Mandat** – Période d’exercice d’un administrateur (titulaire ou suppléant) <br>**Gestionnaire** – Utilisateur habilité à créer/modifier les données <br>**Charge** – Ministère chargé d’un établissement (ex : “Affaires étrangères”) <br>**TUTELLE** – Relation entre établissement et charge(s) ministère |

---  

## 2. Cartographie des processus (Process Map)

### 2.1 Nomenclature hiérarchique

| Niveau | Type | Exemple de processus |
|---|---|---|
| **1** | **Stratégique** | Gestion du catalogue de références (type mandat, type instance, mode nomination, charge, ministère) |
| **2** | **Opérationnel** | • Gestion des administrateurs <br>• Gestion des établissements <br>• Gestion des mandats <br>• Import JORF <br>• Notification d’échéance |
| **2** | **Support** | Authentification Cerbère, Gestion des droits, Sauvegarde/archivage |
| **2** | **Management** | Reporting statistique, Supervision, Gestion des incidents |

### 2.2 Matrice de processus

| ID Proc. | Nom | Type | Propriétaire | Priorité |
|---|---|---|---|---|
| **P‑001** | Création / mise à jour d’un administrateur | Opérationnel | **MOE** – SG/DNUM/PNM/DPNM3/BPN | Critique |
| **P‑002** | Import automatique JORF → création/actualisation de mandats | Opérationnel | **MOA** – SG/SPES | Haute |
| **P‑003** | Notification d’échéance de mandat | Opérationnel | **MOA** – SG/SPES | Haute |
| **P‑004** | Recherche d’un établissement / administrateur | Opérationnel | **MOE** – SG/DNUM | Moyenne |
| **P‑005** | Gestion des droits Cerbère | Support | **Sécurité** – SG/DNUM | Critique |
| **P‑006** | Production de statistiques / tableau de bord | Management | **MOA** – SG/SPES | Moyenne |
| **P‑007** | Supervision & audit (logs, métriques) | Management | **Ops** – MSP | Haute |

---  

## 3. Modélisation BPMN détaillée  

> **Notation** : diagrammes Mermaid (BPMN‑2.0 subset). Chaque diagramme représente un **Pool** « admin_ep » et les **Lanes** des acteurs.  

### 3.1 Process : Gestion des administrateurs (CRUD)

```mermaid
%%{init: {'theme':'base', 'flowchart':{'curve':'linear'}}%% }%%
graph TD;
    subgraph "Pool : admin_ep"
        direction LR;
        lane1[Gestionnaire] --> start((Start))
        start --> task1[Afficher liste des administrateurs]
        task1 --> gateway{Action ?}
        gateway -->|Créer| task2[Formulaire création]
        gateway -->|Modifier| task3[Formulaire modification]
        gateway -->|Supprimer| task4[Confirmer suppression]
        task2 --> task5[Valider saisie]
        task3 --> task5;
        task4 --> task5;
        task5 --> service1[(Service : AdminService.saveOrUpdate())]
        service1 --> end((End))
    end
```

**Éléments BPMN**  

| Élément | Type BPMN | Description |
|---|---|---|
| **Start** | Event (Start) | Déclenché par l’utilisateur (clic “Créer/Modifier/Supprimer”). |
| **Task** | Activity (User Task) | Interaction UI (formulaire). |
| **Gateway** | Exclusive (XOR) | Décision fonctionnelle sur l’action. |
| **Service** | Service Task | Appel au service `AdminService`. |
| **End** | Event (End) | Retour UI avec message de succès/erreur. |

### 3.2 Process : Import JORF (automatique)

```mermaid
%%{init: {'theme':'base', 'flowchart':{'curve':'linear'}}%% }%%
graph TD;
    subgraph "Pool : admin_ep"
        direction TB;
        lane1[Scheduler] --> start((Start – Cron 02_00))
        start --> task1[Downloader JORF (RSS/ZIP)]
        task1 --> task2[Extractor JORF (XML) ]
        task2 --> task3[Parser ArticleAnalyser]
        task3 --> gateway{Article valide ?}
        gateway -->|Oui| task4[Recherche établissements déjà présents]
        gateway -->|Non| task5[Log rejet]
        task4 --> task6[Création / mise à jour mandat (Call Activity)]
        task6 --> end((End))
    end
```

- **Call Activity** : `GestionMandat` (voir § 3.3).  
- **Boundary Timer Event** (non‑déclenché ici) pourra être ajouté pour timeout du téléchargement.  

### 3.3 Process : Gestion des mandats (CRUD + archivage)

```mermaid
%%{init: {'theme':'base', 'flowchart':{'curve':'linear'}}%% }%%
graph LR;
    subgraph "Pool : admin_ep"
        lane1[Gestionnaire] --> start((Start))
        start --> task1[Rechercher mandat existant]
        task1 --> gateway{Mandat trouvé ?}
        gateway -->|Oui| task2[Mettre à jour mandat]
        gateway -->|Non| task3[Créer nouveau mandat]
        task2 --> task4[Calculer dates d’échéance]
        task3 --> task4;
        task4 --> service1[(MandatService.save())]
        service1 --> boundary{Date d’échéance < 30j ?}
        boundary -->|Oui| notify[SendMail Notification]
        boundary -->|Non| end((End))
    end
```

- **Boundary Event** : *Timer* (30 jours avant fin) déclenche la **Notification**.  
- **Data Object** : `Mandat` (persisté en base).  

### 3.4 Process : Recherche (full‑text)

```mermaid
graph TD;
    subgraph "Pool : admin_ep"
        lane1[Utilisateur] --> start((Start – saisie recherche))
        start --> task1[Construire requête Lucene/Elasticsearch]
        task1 --> service1[(SearchService.search())]
        service1 --> task2[Afficher résultats paginés]
        task2 --> end((End))
    end
```

### 3.5 Process : Supervision & reporting

```mermaid
graph TD;
    subgraph "Pool : admin_ep"
        lane1[Ops] --> start((Start – Scheduler 00_00))
        start --> task1[Collecter métriques (JVM, DB, temps de traitement JORF)]
        task1 --> task2[Enregistrer dans Prometheus / Grafana]
        task2 --> task3[Générer rapports PDF (stats, alertes)]
        task3 --> end((End))
    end
```

---  

## 4. Règles de gestion métier

| Point de décision | Condition | Règle métier | Source |
|---|---|---|---|
| **RB‑001** | `Mandat.dateFin` ≤ aujourd’hui + 30 jours | **Notifier** le référent (mail) ; le mandat passe en statut *« À renouveler »*. | Spécifications fonctionnelles (wiki) |
| **RB‑002** | `Utilisateur.role` = *Cerbère 619* | Accès **lecture/écriture** uniquement aux écrans de *Gestionnaires* et *Établissements*. | Politique de sécurité |
| **RB‑003** | `Charge` appartient à la **liste référentielle** (table `CHARGE`) | Validation du champ « Charge » lors de la création d’un établissement. | Table `CHARGE` (scripts init) |
| **RB‑004** | `Mandat.type` ∈ {`Titulaire`, `Suppléant`} | Un même administrateur ne peut pas avoir **deux mandats du même type** sur le même établissement simultanément. | Business rule (doc wiki) |
| **RB‑005** | `Etablissement` créé | Le **téléchargement JORF** doit être lancé 24 h après création pour récupérer les premiers mandats. | Process « Import JORF » |
| **RB‑006** | `User.password` – non‑stocké (SSO Cerbère) | Aucun mot de passe n’est conservé dans la base. | Politique d’authentification |
| **RB‑007** | `Statut` d’un mandat = *« Échu »* | Le mandat est archivé (table `MANDAT_ARCHIVE`) et retiré des vues actives. | Règle d’archivage (doc wiki) |
| **RB‑008** | `FileUpload` (pièce jointe) > 5 Mo | Rejet du fichier, message d’erreur « Taille maximale dépassée ». | Contraintes techniques |

---  

## 5. Données & Documents

| Catégorie | Élément BPMN | Description |
|---|---|---|
| **Data Object** | `Administrateur` | Identité, rôle, dates de mandat, pièces jointes. |
| **Data Object** | `Etablissement` | SIREN, libellé, type d’instance, charge(s), tutelle(s). |
| **Data Object** | `Mandat` | `type`, `dateDébut`, `dateFin`, `statut`, `référent`. |
| **Data Store** | `BASEADMIN` (PostgreSQL) | Schéma *integration* (tables `TYPE_MANDAT`, `CHARGE`, `ETABLISSEMENT`, …). |
| **Data Store** | `ARCHIVE` | Table `MANDAT_ARCHIVE` + pièces jointes. |
| **Artifact** | `ReportStatistiques.pdf` | Document généré (process « Reporting »). |
| **Artifact** | `MailNotification` | Message envoyé par le processus de notification. |
| **Artifact** | `LogFile` | Logs d’import JORF, erreurs, audit. |

---  

## 6. Acteurs & Rôles

| Lane (BPMN) | Rôle métier | Responsabilités | Compétences |
|---|---|---|---|
| **Gestionnaire** | Opérateur MOE (SG/DNUM/PNM/DPNM3/BPN) | Saisie / mise à jour des données, validation des référentiels. | Connaissance du domaine administratif, maîtrise de l’interface. |
| **Scheduler** | Service d’orchestration (Camunda/Quartz) | Lancement périodique du job JORF, génération des rapports. | Programmation Java, gestion des tâches planifiées. |
| **Utilisateur** | Opérateur fonctionnel (SPES, DG de tutelle) | Consultation, recherche, lecture des rapports. | Accès en lecture, utilisation du moteur de recherche. |
| **Ops / Supervision** | Équipe d’exploitation (MSP) | Surveillance des performances, gestion des incidents. | Administration Tomcat/PostgreSQL, monitoring. |
| **Cerbère** | Système d’authentification | Gestion des droits, SSO, logs d’accès. | IAM, conformité sécurité. |

---  

## 7. Performances & Indicateurs (KPIs)

| Indicateur | Formule | Objectif | Seuil d’alerte |
|---|---|---|---|
| **Temps moyen d’import JORF** | Σ (temps téléchargement + extraction + parsing) / nb articles | < 5 min | > 10 min |
| **Taux de mandat expirés non notifiés** | nb mandats > 30 j non notifiés / nb mandats à notifier | 0 % | > 5 % |
| **Disponibilité applicative** | (temps up / temps total) × 100 | 99,5 % | < 99 % |
| **Temps de réponse UI (CRUD)** | ms entre clic et affichage | < 800 ms | > 1 s |
| **Volume d’archives** | taille (GB) de `MANDAT_ARCHIVE` | ≤ 10 GB (2024) | > 15 GB |
| **Nombre de recherches / jour** | compteur `searchService.search()` | ≥ 1 000 | < 200 (dégradation) |

*Points de mesure BPMN* : **Timer Event** (pour le temps d’import), **Message Event** (notification mail), **Boundary Event** (timeout de téléchargement).  

---  

## 8. Gestion des Exceptions

| Scénario | Déclencheur | Gestion (BPMN) | Conséquence |
|---|---|---|---|
| **Timeout téléchargement JORF** | > 2 min sans réponse HTTP | **Boundary Timer Event** → *Task* “Notifier admin” → *End* (process abort) | Mail d’alerte, création d’incident |
| **Erreur parsing XML** | Exception `SAXException` | **Boundary Error Event** → *Task* “Log & alerter” → *End* | Log détaillé, ticket d’incident |
| **Mandat invalide (dateFin < dateDébut)** | Validation métier | **Boundary Error Event** sur *Task* “Valider mandat” → *Task* “Afficher message d’erreur” → *End* | Retour UI, aucune persistance |
| **Échec d’envoi mail** | SMTP refusé | **Boundary Escalation Event** → *Task* “Ré‑essayer 3× puis alerter Ops” → *End* | Notification différée, suivi Ops |
| **Violation de droits Cerbère** | Accès non autorisé | **Boundary Conditional Event** → *Task* “Afficher page 403” → *End* | Refus d’accès, audit de sécurité |

---  

## 9. Sous‑processus & Réutilisation

| Sous‑processus (Call Activity) | Description | Réutilisation |
|---|---|---|
| **GestionMandat** | Création / mise à jour d’un mandat, calcul d’échéance, archivage. | Utilisé par *Import JORF* et *Gestion manuelle* (CRUD). |
| **EnvoiNotificationMail** | Construction et envoi d’un mail (template, destinataire). | Utilisé par *Notification d’échéance* et *Alertes d’erreur*. |
| **RechercheFullText** | Interrogation Elasticsearch, pagination. | Utilisé par les écrans *Recherche Administrateurs*, *Recherche EP*, *Statistiques*. |
| **SupervisionCollecte** | Récupération métriques (JVM, DB, job). | Utilisé par *Reporting* et *Monitoring* (Ops). |
| **AuthentificationCerbère** | Validation du token SSO, récupération des rôles. | Invoqué dès chaque entrée UI (gateway). |

---  

## 10. Matrice de traçabilité (Exigences ↔ Processus)

| Exigence CCF | Processus BPMN | Tâche(s) concernée(s) | Scénario de test |
|---|---|---|---|
| **EXG‑001** – Créer/éditer administrateur | P‑001 (Gestion admin) | `UserTask: Formulaire création/modif` | **Nominal** : saisie valide → persistance + affichage succès |
| **EXG‑002** – Import JORF (automatique) | P‑002 (Import JORF) | `Task: Downloader`, `Task: Parser` | **Nominal** : fichier JORF disponible → création mandats |
| **EXG‑003** – Notification échéance | P‑003 (Gestion mandats) | `Boundary Timer Event` | **Nominal** : mandat à 30 j → mail envoyé |
| **EXG‑004** – Recherche plein texte | P‑004 (Recherche) | `ServiceTask: SearchService.search()` | **Nominal** : requête “Ministère*” → résultats > 0 |
| **EXG‑005** – Accès restreint Cerbère | P‑005 (Gestion droits) | `Conditional Event` | **Erreur** : user non Cerbère → page 403 |
| **EXG‑006** – Reporting statistique | P‑006 (Statistiques) | `Task: Générer rapport PDF` | **Nominal** : exécution nightly → PDF présent dans `/reports` |
| **EXG‑007** – Supervision & logs | P‑007 (Supervision) | `Task: Collecter métriques` | **Nominal** : métriques dans Grafana, alertes configurées |

---  

## 11. Validation & Conformité BPMN

### 11.1 Checklist BPMN

- [x] Tous les flux ont une source et une cible.  
- [x] Une et une seule activité de **Start** par processus.  
- [x] Au moins une activité de **End**.  
- [x] Pas de **gateway** orphelin (toutes les sorties sont reliées).  
- [x] Labels des passerelles explicites (XOR, AND, OR).  
- [x] Nomenclature cohérente (Pools = *admin_ep*, Lanes = rôles).  

### 11.2 Niveaux de conformité

| Niveau | Sous‑ensemble BPMN | Usage prévu |
|---|---|---|
| **Descriptive** | Diagrammes de processus (CRUD, import) – uniquement lecture. | Documentation fonctionnelle. |
| **Analytic** | Inclusion de **Boundary Events**, **Data Objects**, **Message Flows**. | Analyse d’impact, calcul KPI. |
| **Common Executable** | Diagrammes **GestionMandat**, **EnvoiNotificationMail** (exécutables via Camunda). | Implémentation moteur de workflow. |

---  

## 12. Implémentation & Exécution  

### 12.1 Maturité processus (CMMI‑like)

| Niveau | Caractéristique | BPMN applicable |
|---|---|---|
| 1 – Initial | Processus ad‑hoc, non documentés. | — |
| 2 – Managed | Documentation de base, suivi des incidents. | **Descriptive** (processus CRUD). |
| 3 – Defined | Standardisation, modèles réutilisables. | **Analytic** (sous‑processus, KPI). |
| 4 – Quantified | Mesure, amélioration continue. | **Common Executable** (jobs JORF, notifications). |
| 5 – Optimized | Optimisation proactive, IA. | Future – intégration de décision‑engine. |

### 12.2 Intégration système

| Composant | Version / Technologie | Rôle BPMN |
|---|---|---|
| **Camunda BPM** (ou **Activiti**) | 7.x – Java 8 | Exécution des processus *GestionMandat*, *Import JORF*, *Notification*. |
| **PostgreSQL** | 15 | Persistance des Data Objects (`ADMINISTRATEUR`, `MANDAT`, …). |
| **Elasticsearch** | 7.x | Indexation / recherche plein texte (process « Recherche »). |
| **Spring‑Boot** | 2.x | Injection de services, orchestration des tâches. |
| **Quartz Scheduler** | 2.x | Lancement des jobs (import JORF, reporting). |
| **Prometheus / Grafana** | – | Collecte des métriques (process « Supervision »). |
| **Cerbère SSO** | – | Authentification (Message Flow *Login* → *Auth Service*). |
| **Mail Server (SMTP)** | – | Envoi des notifications d’échéance. |

---  

## 13. Annexes  

### 13.1 Glossaire complet (extraits)

| Terme | Définition |
|---|---|
| **CA** | Conseil d’administration d’un établissement public. |
| **CS** | Conseil de surveillance d’un établissement public. |
| **Mandat** | Période d’exercice d’un administrateur (titulaire ou suppléant). |
| **Charge** | Ministère chargé d’un établissement (ex : « Affaires étrangères »). |
| **TUTELLE** | Relation hiérarchique entre établissement et charge(s) ministère. |
| **Cerbère** | Système d’authentification unique (SSO) du ministère. |
| **JORF** | Journal Officiel de la République Française – source officielle des nominations. |
| **ACAI** | Plateforme d’hébergement (clusters ESXi) du ministère. |

### 13.2 Références documentaires  

| Ref. | Document | Lien / Emplacement |
|---|---|---|
| **DOC‑001** | `admin_ep.wiki.md` (Fiche produit) | `G:\…\admin_ep\admin_ep.wiki.md` |
| **DOC‑002** | `admin_ep.code.filtered.md` (scripts SQL, pom, config) | `G:\…\admin_ep\adminep‑database\…` |
| **DOC‑003** | `admin_ep.code.summarized.md` (arborescence) | idem |
| **DOC‑004** | `admin_ep.wikisi.md` (méta‑données) | idem |
| **STD‑001** | ISO/IEC 19510 :2013 (BPMN) | Norme internationale – OMG |

---  

## 14. Conclusion  

Le présent **Cahier des Charges Fonctionnel** fournit une vue exhaustive et normalisée (BPMN / ISO 19510) des processus de l’application *admin_ep*.  

*Les diagrammes ci‑dessus* permettent :  

* de communiquer clairement aux équipes MOA/MOE les flux fonctionnels,  
* d’assurer la traçabilité des exigences vers les activités implémentées,  
* de préparer l’évolution vers des processus **exécutables** (Camunda) et vers la migration technologique (Tomcat 10 / PostgreSQL 15).  

Toute modification future (ajout de nouveaux types de mandats, évolution du moteur de recherche, intégration IA) pourra s’appuyer sur les **sous‑processus réutilisables** et sur la **matrice de traçabilité** déjà définie.  

---  

*Fin du CCF.*  



---  

**NOTE** – Les diagrammes Mermaid présentés sont compatibles avec la plupart des éditeurs Markdown (GitLab, VS Code, Docsify). Pour générer des modèles **exécutables**, il suffit d’exporter chaque diagramme au format BPMN 2.0 (XML) via un outil de conversion (ex : *bpmn.io*).  



---  

**Contact** :  
*Chef de produit* – Christian Arbogast – `Christian.Arbogast@developpement-durable.gouv.fr`  
*Assistance technique* – `assistance-adminep@developpement-durable.gouv.fr`  