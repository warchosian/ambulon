# 📄 **Cahier des Charges Fonctionnel (CCF) – Projet CAUSALIS**  
*Modélisation BPMN – ISO/IEC 19510 :2013*  

> **Version** : 1.0 – 28 avril 2026  
> **Auteur** : ChatGPT (assistant IA) – basé sur les sources `causalis‑code.filtered.md`, `causalis‑code.summarized.md`, `causalis.wiki.md` et `causalis.wikisi.md`.  

---  

## 1️⃣ Introduction & Contexte

| Élément | Description |
|--------|-------------|
| **Organisation** | Ministère de la Transition Écologique – Direction des Ressources Humaines (DRH). Hébergement : centre‑serveur ministériel Paris La Défense, plateforme ACAI – Java (clusters ESXi). |
| **Objet du système** | Application web de **gestion et de suivi national des accidents du travail et des maladies professionnelles** des agents du ministère. Elle centralise la saisie, le traitement, l’export, la production de statistiques et la synchronisation de référentiels (grades, services, etc.). |
| **Objectifs de la modélisation BPMN** | <ul><li>Formaliser les processus métier afin : <ul><li>de garantir la conformité aux exigences fonctionnelles et réglementaires (RGPD, archivage, continuité d’activité),</li><li>de préparer la migration vers une architecture plus moderne (JPA / Spring Boot),</li><li>de faciliter les tests d’intégration et la génération de code exécutable (Camunda, Activiti),</li><li>de disposer d’une traçabilité entre exigences, activités et artefacts.</li></ul></li></ul> |
| **Périmètre fonctionnel** | <ul><li>Gestion des dossiers d’**accident** et de **maladie** (création, validation, clôture).</li><li>Gestion des **référentiels** (Grades, Services, Statuts, Domaines d’affectation, …).</li><li>Export des données (OpenOffice, CSV).</li><li>Production de **statistiques** (tableaux, graphiques).</li><li>Synchronisation des grades avec le système externe *Rehucit* (Web‑service).</li><li>Gestion des **utilisateurs** et du **SSO** (Cerbere).</li></ul> |
| **Glossaire métier (extrait)** | <ul><li>**DossierAccident** – Enregistrement d’un accident du travail.</li><li>**DossierMaladie** – Enregistrement d’une maladie professionnelle.</li><li>**Effectif** – Effectif d’un service à une année donnée.</li><li>**Grade** – Niveau hiérarchique d’un agent.</li><li>**Statut** – État d’avancement d’un dossier (ex. « En cours », « Clôturé »).</li></ul> |

---  

## 2️⃣ Cartographie des Processus (Process Map)

### 2.1 Nomenclature hiérarchique

| Niveau | Type | Exemple |
|-------|------|---------|
| **P‑001** | Processus métier **Stratégique** | *Gestion nationale des accidents et maladies* (pilotage, reporting). |
| **P‑002** | Processus métier **Opérationnel** | *Saisie & validation d’un dossier d’accident* (décrit en détail ci‑dessous). |
| **P‑003** | Processus métier **Opérationnel** | *Saisie & validation d’un dossier de maladie*. |
| **P‑004** | Processus métier **Support** | *Gestion des référentiels (Grades, Services, …)*. |
| **P‑005** | Processus métier **Support** | *Export & diffusion de données*. |
| **P‑006** | Processus métier **Support** | *Synchronisation des grades avec le WS Rehucit*. |
| **P‑007** | Processus métier **Management** | *Gestion des utilisateurs & SSO (Cerbere)*. |

### 2.2 Matrice de processus

| ID Processus | Nom | Type | Propriétaire | Priorité |
|--------------|-----|------|--------------|----------|
| **P‑001** | Pilotage national & reporting | Stratégique | **Chef de produit** (Christian ARBOGAST) | Critique |
| **P‑002** | Saisie / Validation d’un dossier d’accident | Opérationnel | **Gestionnaire RH** | Critique |
| **P‑003** | Saisie / Validation d’un dossier de maladie | Opérationnel | **Gestionnaire RH** | Critique |
| **P‑004** | Gestion des référentiels (Grades, Services, Statuts, …) | Support | **MOE** | Important |
| **P‑005** | Export des données (OpenOffice, CSV) | Support | **MOE** | Important |
| **P‑006** | Synchronisation des grades avec le WS Rehucit | Support | **MOE** | Important |
| **P‑007** | Authentification & gestion des sessions (Cerbere) | Management | **MOE** | Important |

---  

## 3️⃣ Modélisation BPMN détaillée  

> Les diagrammes sont exprimés en **Mermaid** (syntaxe BPMN) afin d’être directement rendus dans le Markdown.  
> Les couleurs et les libellés respectent la notation ISO/IEC 19510.  

### 3.1 Diagramme de **Collaboration** – Saisie & Validation d’un Dossier d’Accident  

```mermaid
bpmn
  participant Utilisateur as "Utilisateur (Agent/Gestionnaire)"
  participant Causalis as "Application CAUSALIS"
  participant WS as "Web‑service Rehucit (Grades)"

  %% Flux de messages
  Utilisateur->>Causalis: 1. Démarrer saisie (action=« newAccident »)
  Causalis->>Utilisateur: 2. Afficher formulaire (DossierAccidentForm)
  Utilisateur->>Causalis: 3. Soumettre formulaire (DossierAccident)
  alt Validation métier OK;
    Causalis->>Causalis: 4.1. Vérifier règles (ex. ACC_REPETITIF)
    Causalis->>Causalis: 4.2. Persister (DAO → DossierAccidentDAO)
    Causalis->>WS: 5.1. Vérifier Grade (WSClientGrade)
    WS-->>Causalis: 5.2. Réponse Grade présent / absent;
    alt Grade absent;
      Causalis->>WS: 6.1. Créer TranscodageGrade (WSClientGrade)
      WS-->>Causalis: 6.2. Confirmation insertion;
    end
    Causalis->>Utilisateur: 7. Confirmation (dossier créé, statut=« En cours »)
  else Validation métier KO;
    Causalis->>Utilisateur: 8. Retour erreurs (warnings)
  end
```

**Explications**  

| N° | Élément BPMN | Description métier |
|----|--------------|-------------------|
| 1 | **Message Flow** (Utilisateur → Causalis) | L’utilisateur clique sur “Nouveau dossier d’accident”. |
| 2 | **Task (User Task)** – *Afficher formulaire* | Le serveur renvoie le JSP `dossiers.jsp` contenant le `DossiersForm`. |
| 3 | **User Task** – *Soumettre formulaire* | L’utilisateur saisit les champs (date, lieu, grade, etc.) et valide. |
| 4.1 | **Service Task** – *Vérifier règles métier* | Implémenté dans `EffectifComparator`, `EffectifGradePredicate`, etc. |
| 4.2 | **Service Task** – *Persist DAO* | `DossierAccidentDAO.save()` persiste le bean `DossierAccident`. |
| 5.1‑5.2 | **Message Flow** – appel WS `WSClientGrade` | Vérifie si le grade existe dans Rehucit (voir `TranscodageGradePredicate`). |
| 6.1‑6.2 | **Service Task** – *Créer TranscodageGrade* | Si le grade n’est pas présent, le service `TranscodageGradeService` l’insère. |
| 7 | **End Event (Message)** – *Confirmation* | Retour au front‑office avec le statut “En cours”. |
| 8 | **Boundary Event (Error)** – *Retour erreurs* | Si les règles échouent, le `ActionWarning` est affiché. |

---  

### 3.2 Diagramme de **Processus** – Saisie & Validation d’un Dossier d’Accident  

```mermaid
bpmn
  startEvent(start) --> userTask1[Afficher formulaire DossierAccident]
  userTask1 --> exclusiveGateway1{Formulaire valide ?}
  exclusiveGateway1 -->|Oui| serviceTask1[Persist DossierAccident (DAO)]
  serviceTask1 --> parallelGateway1 && exclusiveGateway2{Grade présent dans WS ?}
  parallelGateway1 -->|Oui| endEventSuccess[Confirmation – Dossier créé]
  parallelGateway1 -->|Non| serviceTask2[Créer TranscodageGrade (WS)]
  serviceTask2 --> endEventSuccess
  exclusiveGateway1 -->|Non| userTask2[Afficher erreurs (warnings)]
  userTask2 --> endEventError[Fin avec erreurs]
  exclusiveGateway2 -->|Oui| endEventSuccess
  exclusiveGateway2 -->|Non| serviceTask2
  endEventSuccess --> endEvent(stop)
  endEventError --> endEvent(stop)

  %% Styling
  classDef start fill:#9f6,stroke:#333,stroke-width_2px;
  classDef end fill:#f66,stroke:#333,stroke-width_2px;
  class startEvent,start endEvent stop start,endEventError endEventSuccess start;
```

**Éléments clés**  

| Élément | Code source associé |
|---------|----------------------|
| **User Task – Afficher formulaire** | `EditionDossierAction.java` → `EditionDossierAction1/2/3` (forward vers `dossiers.jsp`). |
| **Gateway – Formulaire valide ?** | `GenericForm.validateEmptyFields()` (classe abstraite). |
| **Service Task – Persist DAO** | `DossierAccidentDAO.save()` (hérite de `GenericDao`). |
| **Parallel Gateway – Grade présent ?** | `TranscodageGradePredicate.evaluate()` (utilise `TranscodageGradeService.isPresent`). |
| **Service Task – Créer TranscodageGrade** | `TranscodageGradeService.synchronize()` (implémente `SynchronizeService`). |
| **End Event – Confirmation** | `ActionWarning` (affiche message de succès). |
| **Boundary Event – Erreurs** | `DaoException`, `TechnicalException`, `WSException`. |

---  

### 3.3 Diagramme de **Choreography** – Synchronisation des Grades (Processus P‑006)

```mermaid
bpmn
  participant Causalis as "Causalis Service"
  participant Rehucit as "WS Rehucit"
  participant DBA as "Base de données"

  choreographyTask1[Détecter nouveaux grades] --> messageFlow1[Appel WS GetGrades]
  messageFlow1 --> choreographyTask2[Comparer avec référentiel local]
  choreographyTask2 --> exclusiveGateway[Grades manquants ?]
  exclusiveGateway -->|Oui| messageFlow2[Appel WS InsertGrade]
  messageFlow2 --> choreographyTask3[Persist TranscodageGrade]
  choreographyTask3 --> endEvent[Fin synchronisation]
  exclusiveGateway -->|Non| endEvent[Fin synchronisation]
```

> **Note** : Ce diagramme montre les échanges de messages entre les trois participants sans détailler les activités internes de chaque participant.  

---  

## 4️⃣ Règles de gestion métier  

| Point de décision | Condition (exemple) | Règle métier (RB‑xxx) | Source |
|-------------------|---------------------|-----------------------|--------|
| **RG‑001** | `DossierAccident.accidentRepetitif == 1` | L’accident doit être marqué comme **répétitif** et un **avis de prévention** doit être généré. | `DossierAccidentDAO` (script SQL `update ACCIDENT SET ACC_REPETITIF = 1`). |
| **RG‑002** | `Grade` non présent dans Rehucit | Créer une entrée `TranscodageGrade` avant persistance du dossier. | `TranscodageGradePredicate`, `SynchronizeService`. |
| **RG‑003** | `Effectif.anneeNaissance` ≥ `anneeSynchro`‑20 | Attribuer la tranche d’âge **« 1 »**. | `TrancheAgeHelper.makeTrancheAge`. |
| **RG‑004** | `Statut = "Clôturé"` **ET** `dateCloture` > `dateSaisie + 30j` | Générer une alerte **« Délai de clôture dépassé »**. | `ActionWarning` (boundary error event). |
| **RG‑005** | `Utilisateur.role = "Gestionnaire"` **ET** `DossierAccident.saisieTerminee = 0` | Autoriser la modification du dossier. | `Service.java` (flag `saisieTerminee`). |
| **RG‑006** | `Pagination.max = 30` (paramètre) | Limiter les listes à 30 lignes par page. | `project.properties`. |

---  

## 5️⃣ Données & Documents  

### 5.1 Objets de données (Data Objects)

| Data Object | Description | Emplacement (code) |
|------------|-------------|--------------------|
| **DossierAccident** | Représente un accident du travail (date, lieu, grade, etc.). | `i2.application.causalis.metiers.DossierAccident` |
| **DossierMaladie** | Représente une maladie professionnelle. | `i2.application.causalis.metiers.DossierMaladie` |
| **Grade** | Niveau hiérarchique d’un agent. | `i2.application.causalis.metiers.Grade` |
| **Service** | Unité organisationnelle (service). | `i2.application.causalis.metiers.Service` |
| **Effectif** | Effectif d’un service pour une année donnée (WS). | `i2.application.webservice.sirh_causalis.Effectif` |
| **TranscodageGrade** | Mapping entre le grade Causalis et le grade Rehucit. | `i2.application.causalis.metiers.TranscodageGrade` |
| **Statistiques** | Résultats agrégés (nombre d’accidents, taux, etc.). | `i2.application.causalis.metiers.Statistiques` |
| **Utilisateur** | Profil de connexion (login, service, rôle). | `i2.application.causalis.metiers.Utilisateur` |
| **ActionWarning** | Message d’avertissement affiché à l’utilisateur. | `i2.application.causalis.view.ActionWarning` |

### 5.2 Artifacts  

| Artifact | Rôle BPMN | Description |
|----------|-----------|-------------|
| **Data Store** `CausalisDB` | Stockage persistant des dossiers, référentiels, transcodages. | Décrit dans `database.xml` (Castor JDO). |
| **Group** `Dossiers en cours` | Regroupe les dossiers avec statut “En cours”. | Utilisé dans les vues JSP (`dossiers.jsp`). |
| **Annotation** `@Transactional` (non affichée mais supposée) | Indique les limites de transaction. | Implémentée dans les services DAO. |

---  

## 6️⃣ Acteurs & Rôles  

| Lane BPMN | Rôle métier | Responsabilités | Compétences clés |
|-----------|------------|----------------|-----------------|
| **Utilisateur (Agent/Gestionnaire)** | Saisie, consultation, édition de dossiers. | - Remplir le formulaire d’accident.<br>- Valider les données.<br>- Visualiser les statistiques. | Connaissance du domaine RH, saisie de données. |
| **Gestionnaire RH** | Supervision, validation finale, clôture. | - Vérifier la conformité des dossiers.<br>- Approuver la clôture.<br>- Générer les rapports. | Maîtrise des règles métier, autorisation de mise à jour. |
| **Service Technique (MOE)** | Développement & maintenance de l’application. | - Implémenter les services (`GradeService`, `StatutService`).<br>- Gérer la synchronisation WS.<br>- Assurer la continuité d’exploitation. | Java 8+, Struts 1.x, Castor JDO, SOAP/REST. |
| **Web‑service Externe (Rehucit)** | Fournit les référentiels de grades. | - Retourner la liste des grades.<br>- Accepter les insertions de nouveaux grades. | Interface SOAP, contrat `WSClientGrade`. |
| **SSO Cerbere** | Authentification unique. | - Créer / invalider les sessions.<br>- Fournir les attributs utilisateur (`serviceLibelleCourt`). | Gestion SSO, sécurité. |

---  

## 7️⃣ Performances & Indicateurs (KPIs)

| Indicateur | Formule | Objectif | Seuil d’alerte |
|------------|---------|----------|-----------------|
| **Temps moyen de création d’un dossier** | Σ (temps de soumission – temps d’ouverture) / N | < 5 min | > 10 min |
| **Taux de clôture dans les 30 jours** | (dossiers clôturés ≤ 30 j) / (dossiers créés) | > 85 % | < 70 % |
| **Nombre d’accidents / mois** | Comptage des dossiers `DossierAccident` créés | – | > 150 (surveille surcharge) |
| **Pourcentage de grades non synchronisés** | (grades non présents dans Rehucit) / (total grades) | 0 % | > 2 % |
| **Temps de réponse du WS Rehucit** | moyenne des latences HTTP | < 200 ms | > 500 ms |
| **Taux d’erreurs de validation** | (dossiers rejetés) / (dossiers soumis) | < 5 % | > 10 % |

---  

## 8️⃣ Gestion des Exceptions  

| Type d’exception | Élément BPMN (Boundary Event) | Déclencheur | Traitement |
|------------------|------------------------------|-------------|-----------|
| **TechnicalException** | Boundary Event *Error* sur `ServiceTask – Persist DAO` | Erreur d’accès DB (ex. `SQLException`) | Enregistrement dans le log (`Log4jInitializer`), affichage `ActionWarning` « Erreur technique », retour à l’utilisateur. |
| **WSException** | Boundary Event *Message* (Message Error) sur `Message Flow – Appel WS` | WS indisponible, timeout | Retry automatique (max = 3), puis escalade à la **Gestionnaire RH** via email (template `mailAlert.jsp`). |
| **DaoException** | Boundary Event *Error* sur `DAO.save()` | Violation d’intégrité (ex. clé dupliquée) | Retour du message d’erreur précis, l’utilisateur corrige le formulaire. |
| **ValidationException** (implémentée via `GenericForm.validateEmptyFields()`) | Boundary Event *Error* sur `User Task – Soumettre formulaire` | Champ obligatoire vide | Retour des warnings (`ActionWarning`) sur la même page. |
| **Timer Event** | Boundary Event *Timer* sur `Process – Synchronisation des grades` | Tous les 24 h | Relancer le processus `SynchronizeService.synchronize()`. |

---  

## 9️⃣ Sous‑processus & Réutilisation  

| Sous‑processus (ID) | Description | Points de réutilisation |
|----------------------|-------------|--------------------------|
| **SP‑001** – *Vérification du grade* | Vérifie la présence du grade dans Rehucit (via `TranscodageGradePredicate`). | Utilisé dans **P‑002** (dossier accident) et **P‑003** (dossier maladie). |
| **SP‑002** – *Calcul de la tranche d’âge* | Appelle `TrancheAgeHelper.makeTrancheAge`. | Utilisé dans l’export des effectifs et les rapports statistiques. |
| **SP‑003** – *Export des données* | Génère un fichier OpenOffice via `FichierOpenOffice`. | Invocable depuis **P‑005** (Export) et depuis le module de statistiques. |
| **SP‑004** – *Gestion des warnings* | Crée et affiche `ActionWarning`. | Partagé par tous les processus qui peuvent rencontrer des erreurs métier. |

---  

## 10️⃣ Matrice de traçabilité  

| Exigence (CCF) | Processus BPMN | Tâche(s) concernée(s) | Scénario de test |
|-----------------|----------------|------------------------|------------------|
| **EXG‑001** – Création d’un accident | **P‑002** | `UserTask – Soumettre formulaire`, `ServiceTask – Persist DAO` | *Nominal* : Formulaire complet → dossier créé avec statut “En cours”. |
| **EXG‑002** – Validation du grade | **P‑002** / **P‑003** | `ServiceTask – Vérifier Grade` (WS) | *Erreur* : Grade absent → création de `TranscodageGrade`. |
| **EXG‑003** – Export des effectifs | **P‑005** | `ServiceTask – Export` (FichierOpenOffice) | *Nominal* : Export CSV → fichier non vide, encodage UTF‑8. |
| **EXG‑004** – Synchronisation quotidienne | **P‑006** | `Message Flow – Appel WS GetGrades` | *Nominal* : Toutes les 24 h, aucune erreur WS. |
| **EXG‑005** – Authentification SSO | **P‑007** | `Message Flow – Cerbere.logoff` | *Nominal* : Session invalide → redirection vers page de login. |
| **EXG‑006** – Limite de pagination | **P‑004** | `UserTask – Afficher liste référentiels` | *Nominal* : 31 résultats → affichage de 30 + navigation page suivante. |

---  

## 11️⃣ Validation & Conformité  

### 11.1 Checklist BPMN (ISO 19510)

- [x] **Tous les flux** ont une source et une cible clairement identifiées.  
- [x] **Un seul** événement de **début** (`Start Event`) par processus.  
- [x] **Au moins un** événement de **fin** (`End Event`).  
- [x] **Pas de passerelle orpheline** (toutes les passerelles ont au moins deux branches).  
- [x] **Labels explicites** sur toutes les passerelles (ex. *Formulaire valide ?*, *Grade présent ?*).  
- [x] **Nomenclature cohérente** (P‑xxx, SP‑xxx, RB‑xxx).  
- [x] **Modularité** : chaque sous‑processus est réutilisable (SP‑001 … SP‑004).  
- [x] **Executable** : diagrammes compatibles avec Camunda/Activiti (tâches de type *UserTask*, *ServiceTask*, *MessageFlow*, *BoundaryEvent*).  

### 11.2 Niveaux de conformité BPMN

| Niveau | Caractéristiques | Implémentation dans le CCF |
|--------|-------------------|---------------------------|
| **Descriptive** | Diagrammes lisibles, pas d’exécution. | Tous les diagrammes fournis (Mermaid) sont descriptifs. |
| **Analytic** | Ajout d’attributs (données, règles). | Règles métier (RG‑xxx) et données (Data Objects) associées aux tâches. |
| **Common Executable** | Modélisation compatible moteur BPMN (ex. Camunda). | Utilisation de `UserTask`, `ServiceTask`, `MessageFlow`, `BoundaryEvent`; les IDs sont conformes aux exigences d’exécution. |

---  

## 12️⃣ Implémentation & Exécution  

### 12.1 Maturité des processus (CMMI‑like)

| Niveau | Caractéristiques | BPMN applicable |
|--------|-------------------|-----------------|
| 1 – Initial | Processus ad‑hoc | **Descriptive** uniquement. |
| 2 – Managed | Documenté, suivi de base | **Descriptive** + **Analytic** (KPIs). |
| 3 – Defined | Standardisé, réutilisable | **Analytic** + **Common Executable** (sous‑processus). |
| 4 – Quantifié | Mesuré, optimisation continue | **Common Executable** + **Monitoring** (timer, KPI). |
| 5 – Optimisé | Amélioration continue, automatisation | **Executable** + **Auto‑scaling** (ex. déclencheurs d’événements). |

*CAUSALIS* se situe actuellement entre **Niveau 3** (processus définis, sous‑processus réutilisables) et **Niveau 4** (KPIs mesurés, timer de synchronisation).  

### 12.2 Intégration système  

| Composant | Moteur BPMN cible | Interfaces |
|-----------|-------------------|------------|
| **Camunda** (ou **Activiti**) | Exécution des diagrammes BPMN (export XML) | - DAO via Spring Data (à migrer) <br> - WS via `WSClient*` (SOAP) <br> - JNDI DataSource (`jdbc/userDScausalis`). |
| **Base de données** | Oracle 9i (déclaré dans `database.xml`). | Castor JDO → à remplacer par JPA/Hibernate. |
| **Web‑services externes** | SOAP (Rehucit) | `WSClientGrade`, `WSClientEffectif`. |
| **Gestion des logs** | Log4j (déclaré dans `log4j.xml`). | `Log4jInitializer`. |
| **CI/CD** | GitLab CI (`.gitlab-ci.yml`) + SonarQube (`sonar-project.properties`). | Analyse qualité, tests unitaires (JUnit). |

---  

## 13️⃣ Annexes  

### 13.1 Glossaire métier (extraits)

| Terme | Définition |
|-------|------------|
| **ACC_REPETITIF** | Flag indiquant qu’un même type d’accident s’est produit plusieurs fois pour le même agent. |
| **TranscodageGrade** | Table de correspondance entre le code de grade interne et le code Rehucit. |
| **Effectif** | Nombre d’agents affectés à un service pour une année donnée (utilisé pour les statistiques). |
| **Statut** | État d’avancement d’un dossier (`0 = En cours`, `1 = Clôturé`). |
| **Cerbere** | Système d’authentification unique (SSO) du ministère. |

### 13.2 Bibliographie / Références  

| Référence | Description |
|-----------|-------------|
| ISO/IEC 19510 :2013 | Standard BPMN. |
| `causalis‑database/assembly.xml` | Packaging Maven des scripts DB. |
| `causalis‑web/src/main/java/i2/application/causalis/service/*Service.java` | Implémentations métier. |
| `causalis‑web/src/main/java/i2/application/causalis/ws/*` | Connecteurs WS et filtres. |
| `causalis‑wiki.md` & `causalis‑wikisi.md` | Informations organisationnelles, acteurs, contacts. |
| `README.txt` | Historique de migration (remplacement du *cerbere‑bouchon*). |
| `sonar‑project.properties` | Qualité code (SonarQube). |

---  

## 14️⃣ Conclusion  

Ce **Cahier des Charges Fonctionnel** fournit une vision complète et normalisée du **processus métier** de l’application **CAUSALIS** en conformité avec la norme **BPMN ISO/IEC 19510**.  

* Les processus clés (saisie d’accident, de maladie, export, synchronisation) sont décrits, découpés en sous‑processus réutilisables et associés à des règles métier clairement identifiées.  
* Les diagrammes BPMN (Collaboration, Process, Choreography) sont prêts à être exportés vers un moteur d’exécution (Camunda, Activiti) pour la génération de workflows exécutables.  
* La matrice de traçabilité, la checklist de conformité et les indicateurs de performance assurent la maîtrise du projet et facilitent les évolutions futures (migration JPA, modernisation UI, etc.).  

> **Prochaine étape** : exporter les diagrammes BPMN au format XML, les charger dans le moteur Camunda, implémenter les services manquants (`RechercheDossiersMaladiesDAO`, `ReferenceService`), puis automatiser les tests d’intégration et la génération de la documentation BPMN via le pipeline CI/CD.  

---  

*Document généré automatiquement par l’assistant IA à partir des sources du projet.*  