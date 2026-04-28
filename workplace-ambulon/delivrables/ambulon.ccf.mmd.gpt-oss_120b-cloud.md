# 📄 Cahier des Charges Fonctionnel (CCF) – Projet **ambulon**  

[TOC]

---  

## 1️⃣ Introduction et contexte du projet <a id="intro"></a>

| Élément | Description |
|---|---|
| **Nom du projet** | **ambulon** |
| **Contexte organisationnel** | Le projet s’inscrit dans la stratégie de digitalisation des services d’assistance médicale et de transport d’urgence d’une collectivité territoriale (ou d’un groupe de santé). L’objectif est de remplacer les processus papier / téléphoniques par une plateforme collaborative accessible aux usagers, aux services d’urgence et aux gestionnaires. |
| **Objectifs stratégiques** | 1. Améliorer le temps moyen de prise en charge des patients (objectif : -20 % vs. processus actuel). <br>2. Garantir la traçabilité et la conformité RGPD des données de santé. <br>3. Optimiser l’utilisation du parc d’ambulances (taux d’occupation ≥ 80 %). |
| **Périmètre fonctionnel** | **Inclus** : gestion des usagers, création et suivi des demandes d’intervention, géolocalisation en temps réel, messagerie sécurisée, tableau de bord d’administration, reporting statistique.<br>**Exclus** : prise en charge des dossiers médicaux détaillés (hors périmètre de la plateforme), intégration avec les systèmes de facturation tiers (hors scope initial). |
| **Livrables attendus** | - Application web (responsive) + API REST <br>- Documentation fonctionnelle et technique <br>- Jeux de tests d’acceptation <br>- Plan de formation des utilisateurs |
| **Contraintes majeures** | - Conformité RGPD & HDS (Hébergement de Données de Santé) <br>- Disponibilité ≥ 99,5 % 24 h/24 <br>- Authentification forte (SAML/OIDC) <br>- Hébergement sur cloud souverain (ou équivalent) |

↩︎ [Retour au sommaire](#toc)

---  

## 2️⃣ Expression fonctionnelle du besoin (NF EN 16271) <a id="besoin"></a>

> **Principe** : chaque fonction de service décrit **le quoi** (besoin) sans préciser **le comment** (solution).

| # | Fonction de service (Quoi) | Description | Critères d’appréciation (mesurables) | Pondération (1‑5) | Contraintes associées |
|---|---|---|---|---|---|
| F1 | **Gestion des comptes usagers** | Permettre la création, la mise à jour et la suppression de comptes (patients, volontaires, personnel médical). | - Temps de création ≤ 2 min <br>- Taux d’erreur < 0,5 % <br>- Conformité RGPD (droit à l’oubli) | 5 | Authentification forte, stockage chiffré |
| F2 | **Déclaration d’une demande d’intervention** | Un usager peut déclencher une demande d’ambulance en renseignant localisation, urgence, informations patient. | - Temps de saisie ≤ 3 min <br>- Disponibilité du formulaire ≥ 99 % <br>- Validation des champs critiques (ex : GPS) | 5 | Vérification de la zone de couverture |
| F3 | **Dispatch et affectation d’ambulance** | Le système propose automatiquement (ou manuellement) l’ambulance la plus proche et disponible. | - Temps de dispatch ≤ 30 s <br>- Taux d’affectation correcte ≥ 95 % | 4 | Algorithme de géorouting, disponibilité temps réel |
| F4 | **Suivi en temps réel** | Visualiser la position de l’ambulance et le temps estimé d’arrivée (ETA). | - Actualisation ≤ 5 s <br>- Précision GPS ≤ 5 m | 4 | Intégration avec API de cartographie |
| F5 | **Messagerie sécurisée** | Échanger des messages texte/voice entre usager, équipe médicale et centre de dispatch. | - Chiffrement end‑to‑end <br>- Délai de remise ≤ 2 s | 3 | Conformité HDS |
| F6 | **Tableau de bord administratif** | Visualiser indicateurs (temps moyen d’intervention, taux d’occupation, incidents). | - Temps de génération du rapport ≤ 10 s <br>- Disponibilité ≥ 99 % | 3 | Accès RBAC |
| F7 | **Gestion des incidents & historique** | Enregistrer chaque intervention avec métadonnées (date, durée, statut, acteurs). | - Conservation ≥ 10 ans <br>- Recherche full‑text <br>- Export CSV/JSON | 4 | Archivage sécurisé |
| F8 | **Gestion des droits et rôles** | Définir des profils (patient, volontaire, infirmier, coordinateur, admin) avec permissions granulaire. | - Gestion des rôles via UI <br>- Audit des changements <br>- Temps de mise à jour ≤ 1 min | 5 | Conformité ISO 27001 |
| F9 | **Notifications multicanales** | Envoyer alertes (SMS, email, push) au moment du dispatch, de l’arrivée, et du suivi. | - Taux de délivrabilité ≥ 98 % <br>- Délai de notification ≤ 5 s | 3 | Gestion des préférences usager |
| F10 | **Export & interopérabilité** | Fournir API (REST) et formats d’échange (FHIR, CSV) pour interfacer avec systèmes hospitaliers. | - Temps de réponse API ≤ 200 ms <br>- Conformité FHIR ≥ R4 | 2 | Documentation OpenAPI |

> **Note** : La pondération indique l’impact relatif sur la valeur métier (5 = critique).

↩︎ [Retour au sommaire](#toc)

---  

## 3️⃣ Acteurs et parties prenantes <a id="acteurs"></a>

| Acteur | Type | Rôle | Objectifs | Besoins spécifiques |
|---|---|---|---|---|
| **Patient / Usager** | Humain | Initiateur de la demande | Obtenir une prise en charge rapide & sécurisée | Interface simple, suivi en temps réel, confidentialité |
| **Volontaire / Conducteur** | Humain | Réalise le transport | Optimiser ses déplacements, recevoir les missions | Navigation GPS, messagerie, historique de missions |
| **Médecin / Infirmier** | Humain | Valide l’urgence, suit le patient | Accès aux informations cliniques, coordination | Accès restreint aux données de santé, notifications |
| **Coordinateur de dispatch** | Humain | Gère l’affectation | Maximiser l’efficacité du parc, réduire les temps d’attente | Vue d’ensemble du parc, outils de ré‑affectation |
| **Administrateur système (MOE)** | Humain | Opère la plateforme | Garantir disponibilité, conformité, sécurité | Gestion des droits, logs, monitoring |
| **MOA (Maîtrise d’Ouvrage)** | Organisation | Porteur du besoin métier | Atteindre les objectifs stratégiques | Reporting, tableau de bord, conformité réglementaire |
| **RSSI / DPO** | Organisation | Garant de la sécurité & de la protection des données | Conformité RGPD, HDS | Audit, traçabilité, chiffrement |
| **Système de cartographie** | Système | Fournit la géolocalisation | Calculer ETA, afficher carte | API temps réel, haute précision |
| **Système d’envoi SMS/Email** | Système | Diffuse les notifications | Assurance de la délivrabilité | API fiable, gestion des quotas |

↩︎ [Retour au sommaire](#toc)

---  

## 4️⃣ Cas d’usage (Use Cases) <a id="usecases"></a>

### 4.1 Diagramme de Cas d'Utilisation (UML) – Mermaid  

```mermaid
usecaseDiagram;
    actor Patient as P;
    actor Volontaire as V;
    actor Coordinateur as C;
    actor Médecin as M;
    actor Administrateur as A;
    P --> (Déclarer une demande d'intervention)
    (Déclarer une demande d'intervention) --> C : Notifier;
    C --> (Affecter une ambulance)
    (Affecter une ambulance) --> V : Assignation;
    V --> (Accepter la mission)
    V --> (Suivre le patient)
    M --> (Consulter le dossier d'intervention)
    A --> (Gérer les comptes)
    A --> (Configurer les règles de dispatch)
    A --> (Consulter les rapports)
```

### 4.2 Liste détaillée des cas d’usage  

| # | Nom du cas d’usage | Acteur(s) principal(aux) | Scénario nominal | Scénarios alternatifs / d’erreur | Pré‑conditions | Post‑conditions |
|---|---|---|---|---|---|---|
| UC‑1 | **Déclarer une demande d'intervention** | Patient | 1. Le patient ouvre l’app.<br>2. Il renseigne localisation, type d’urgence, infos patient.<br>3. Il soumet la demande.<br>4. Le système enregistre et notifie le coordinateur. | - *UC‑1‑A* : localisation non disponible → affichage d’un message d’erreur.<br>- *UC‑1‑B* : données incomplètes → mise en évidence des champs obligatoires. | Patient authentifié. | Demande créée, état = « En attente ». |
| UC‑2 | **Affecter une ambulance** | Coordinateur | 1. Le coordinateur visualise la liste des demandes en attente.<br>2. Le système propose l’ambulance la plus proche.<br>3. Le coordinateur confirme ou sélectionne manuellement.<br>4. Le conducteur reçoit la mission. | - *UC‑2‑A* : aucune ambulance disponible → état « En attente de disponibilité ».<br>- *UC‑2‑B* : rejet du conducteur → retour à la sélection. | Demande en état « En attente ». | Demande passe à l’état « Assignée ». |
| UC‑3 | **Accepter la mission** | Volontaire / Conducteur | 1. Le conducteur reçoit la notification.<br>2. Il accepte via l’app.<br>3. Le système change le statut en « En cours ». | - *UC‑3‑A* : conducteur refuse → réaffectation automatique.<br>- *UC‑3‑B* : délai d’acceptation dépassé → alerte au coordinateur. | Mission assignée. | Statut = « En cours ». |
| UC‑4 | **Suivre l'ambulance en temps réel** | Patient, Volontaire, Coordinateur | 1. L’interface affiche la carte avec le marqueur GPS.<br>2. Le ETA est recalculé chaque 5 s. | - *UC‑4‑A* : perte du signal GPS → affichage d’un message « Signal perdu ». | Mission en cours. | Le suivi reste disponible jusqu’à l’arrivée. |
| UC‑5 | **Envoyer une notification d’arrivée** | Système (automatique) | 1. Le système détecte l’arrivée (rayon 30 m).<br>2. Envoie SMS / push au patient et au coordinateur. | - *UC‑5‑A* : échec d’envoi SMS → enregistrement de l’erreur et nouvelle tentative. | Ambulance en route. | Patient notifié de l’arrivée. |
| UC‑6 | **Consulter le tableau de bord** | Administrateur, Coordinateur | 1. L'utilisateur ouvre le tableau de bord.<br>2. Filtre les indicateurs souhaités.<br>3. Exporte le rapport si besoin. | - *UC‑6‑A* : données indisponibles → affichage d’un message d’erreur. | Authentification avec rôle adéquat. | Visualisation ou export des indicateurs. |
| UC‑7 | **Gérer les droits et rôles** | Administrateur | 1. L’admin crée/modifie un rôle.<br>2. Associe les permissions.<br>3. Applique le rôle à un compte. | - *UC‑7‑A* : conflit de permissions → alerte et blocage. | Authentification admin. | Rôles mis à jour, audit enregistré. |
| UC‑8 | **Exporter les données d’intervention** | Médecin, Administrateur | 1. Sélection d’une période.<br>2. Choix du format (CSV, JSON, FHIR).<br>3. Lancement de l’export. | - *UC‑8‑A* : volume trop important → pagination ou génération asynchrone. | Droits d’accès aux données d’intervention. | Fichier exporté disponible. |

↩︎ [Retour au sommaire](#toc)

---  

## 5️⃣ Processus métier (BPMN) <a id="processus"></a>

### 5.1 Diagramme BPMN – Cycle complet d’une demande d’intervention  

```mermaid
bpmnDiagram;
    participant Patient;
    participant Système;
    participant Coordinateur;
    participant Conducteur;
    participant Médecin;
    Patient->>Système: Déclarer demande;
    Système->>Coordinateur: Notifier demande;
    alt Ambulance disponible;
    Coordinateur->>Système: Proposer affectation;
    Système->>Conducteur: Notifier mission;
    Conducteur->>Système: Accepter mission;
    Système->>Patient: Confirmer prise en charge;
    Système->>Patient: Suivi GPS (boucle)
    Conducteur->>Patient: Arrivée patient;
    Système->>Médecin: Transmettre dossier;
    Médecin->>Système: Enregistrer prise en charge;
    else Aucun véhicule;
    Système->>Coordinateur: Alerte indisponibilité;
    Coordinateur->>Patient: Informer délai;
    end
    Système->>Coordinateur: Archiver intervention
```

### 5.2 Description des processus critiques  

| Processus | Description | Points de contrôle | Règles de gestion |
|---|---|---|---|
| **P1 – Création de la demande** | Enregistrement d’une demande d’urgence. | Validation de la localisation, champs obligatoires. | Si localisation hors zone → rejet avec message. |
| **P2 – Dispatch** | Attribution automatique ou manuelle d’une ambulance. | Disponibilité temps réel, distance minimale. | Priorité : urgence > proximité > disponibilité. |
| **P3 – Acceptation du conducteur** | Confirmation de la mission par le conducteur. | Délai d’acceptation ≤ 2 min. | Si refus, réaffectation immédiate. |
| **P4 – Suivi & ETA** | Calcul et mise à jour de l’estimation d’arrivée. | Rafraîchissement ≤ 5 s, précision ≤ 5 m. | Si perte GPS > 30 s → alerte coordinateur. |
| **P5 – Clôture** | Enregistrement de l’intervention terminée. | Vérification de la complétude du dossier. | Archivage sécurisé ≥ 10 ans, conformité RGPD. |

↩︎ [Retour au sommaire](#toc)

---  

## 6️⃣ Règles métier et contraintes fonctionnelles <a id="regles"></a>

| # | Règle métier (IF…THEN) | Source / Justification |
|---|---|---|
| R1 | **IF** la demande est marquée « Urgence » **THEN** le temps maximal de dispatch = 30 s. | Objectif temps de prise en charge. |
| R2 | **IF** le patient n’a pas accepté les conditions RGPD **THEN** la création de compte est bloquée. | Conformité RGPD Art. 7. |
| R3 | **IF** le conducteur décline la mission **THEN** le système réaffecte automatiquement la demande à l’ambulance suivante disponible. | Continuité de service. |
| R4 | **IF** la zone géographique n’est pas couverte **THEN** le système informe le patient et propose un numéro d’appel d’urgence traditionnel. | Limite du périmètre. |
| R5 | **IF** le patient modifie ses coordonnées pendant le suivi **THEN** le trajet est recalculé et le ETA mis à jour. | Qualité du service. |
| R6 | **IF** un utilisateur dépasse 3 tentatives d’authentification échouées **THEN** le compte est bloqué 15 min et une alerte est envoyée à l’administrateur. | Sécurité (ISO 27001). |
| R7 | **IF** le volume d’export dépasse 10 000 lignes **THEN** l’export est généré en mode asynchrone avec notification par email. | Performance. |
| R8 | **IF** le système détecte une perte de connexion GPS > 30 s **THEN** alerter le coordinateur et le patient. | Fiabilité du suivi. |
| R9 | **IF** le patient sélectionne la langue « Français » **THEN** toutes les UI et notifications sont en français. | Accessibilité multilingue. |
| R10 | **IF** le DPO active le mode « Anonymisation » **THEN** les champs personnels (nom, adresse) sont masqués dans les exports statistiques. | Protection des données. |

#### Contraintes réglementaires  

| Domaine | Exigence | Référence |
|---|---|---|
| **RGPD** | Consentement explicite, droit à l’oubli, portabilité des données. | Art. 6‑9, 17, 20 |
| **HDS** | Hébergement certifié pour données de santé. | ANSSI |
| **Accessibilité** | Niveau AA WCAG 2.1. | WCAG 2.1 |
| **Sécurité** | Authentification forte, chiffrement TLS 1.3, audit logs. | ISO 27001, NIST 800‑53 |
| **Interopérabilité** | Support du standard FHIR R4 pour échanges cliniques. | HL7 FHIR |

↩︎ [Retour au sommaire](#toc)

---  

## 7️⃣ Parcours utilisateurs (User Journey) <a id="journey"></a>

### 7.1 Parcours « Demande d’ambulance » (Patient)

| Étape | Interaction | Canal | Critère d’acceptation (GWT) |
|---|---|---|---|
| **1.** Accès à l’app | `Given` le patient a installé l’application <br>`When` il l’ouvre <br>`Then` l’écran d’accueil s’affiche | Mobile/Web | Temps de chargement < 2 s |
| **2.** Authentification | `Given` le patient n’est pas connecté <br>`When` il saisit ses identifiants <br>`Then` il est authentifié avec MFA | Mobile/Web | MFA réussie, session active |
| **3.** Déclaration d’urgence | `Given` l’utilisateur est authentifié <br>`When` il indique sa localisation et le type d’urgence <br>`Then` la demande est enregistrée et le statut = « En attente » | Mobile/Web | Validation des champs, temps ≤ 3 min |
| **4.** Confirmation & suivi | `Given` la demande est créée <br>`When` le système notifie le coordinateur <br>`Then` le patient voit le numéro d’ambulance et la carte en temps réel | Mobile/Web | Carte actualisée ≤ 5 s, ETA affiché |
| **5.** Arrivée de l’ambulance | `Given` l’ambulance approche <br>`When` le rayon de 30 m est franchi <br>`Then` le patient reçoit une notification d’arrivée | Push/SMS | Notification reçue ≤ 5 s |
| **6.** Fin de l’intervention | `Given` le patient est pris en charge <br>`When` le conducteur clôture la mission <br>`Then` le patient peut laisser un avis | Mobile/Web | Avis enregistré, questionnaire affiché |

### 7.2 Parcours « Gestion des droits » (Administrateur)

| Étape | Interaction | Canal | Critère d’acceptation |
|---|---|---|---|
| 1. Authentification admin (MFA) | Web | ≤ 2 s |
| 2. Accès tableau “Gestion des rôles” | Web | UI charge en ≤ 1 s |
| 3. Création d’un nouveau rôle “Coordonnateur” | Web | Rôle créé, audit log enregistré |
| 4. Attribution du rôle à un compte | Web | Confirmation affichée, mail de notification envoyé |
| 5. Vérification des permissions | Web | Test d’accès OK pour le nouveau rôle |

↩︎ [Retour au sommaire](#toc)

---  

## 8️⃣ Modèle Conceptuel de Données (MCD) <a id="mcd"></a>

### 8.1 Diagramme de classes UML (abstrait)  

```mermaid
classDiagram
    class Utilisateur {
    <<entity>>
    +id : UUID;
    +email : String;
    +motDePasse : String;
    +type : Enum{PATIENT, CONDUCTEUR, COORDINATEUR, MEDICAL, ADMIN}
    +dateCréation : DateTime;

    class Demande {
    <<entity>>
    +id : UUID;
    +dateHeure : DateTime;
    +typeUrgence : Enum{A, B, C}
    +localisation : GeoPoint;
    +statut : Enum{EN_ATTENTE, ASSIGNEE, EN_COURS, TERMINEE, ANNULEE}

    class Ambulance {
    <<entity>>
    +id : UUID;
    +immatriculation : String;
    +capacite : Integer;
    +etat : Enum{DISPO, OCCUPEE, EN_MAINTENANCE}

    class Mission {
    <<entity>>
    +id : UUID;
    +dateHeureAssignation : DateTime;
    +eta : Duration;

    class Notification {
    <<entity>>
    +id : UUID;
    +type : Enum{SMS, EMAIL, PUSH}
    +statutEnvoi : Enum{ENVOYE, ECHOUE}
    +dateEnvoi : DateTime;

    class Evenement {
    <<entity>>
    +id : UUID;
    +type : Enum{ARRIVEE, DEPART, CANCELLATION}
    +timestamp : DateTime;

    Utilisateur "1" <-- "0..*" Demande : crée;
    Demande "1" <-- "0..1" Mission : déclenche;
    Mission "1" <-- "1" Ambulance : utilise;
    Mission "1" <-- "1" Utilisateur : conducteur;
    Mission "1" <-- "0..*" Notification : génère;
    Mission "1" <-- "0..*" Evenement : produit
```

### 8.2 Description des entités clés  

| Entité | Attributs majeurs | Rôle métier |
|---|---|---|
| **Utilisateur** | id, email, motDePasse, type, dateCréation | Acteur (patient, conducteur, coordinateur, etc.) |
| **Demande** | id, dateHeure, typeUrgence, localisation, statut | Représente la demande d’intervention |
| **Ambulance** | id, immatriculation, capacite, état | Ressource mobile à affecter |
| **Mission** | id, dateHeureAssignation, eta | Lien entre une demande, une ambulance et un conducteur |
| **Notification** | id, type, statutEnvoi, dateEnvoi | Historique des alertes envoyées |
| **Evenement** | id, type, timestamp | Trace d’étapes clés (arrivée, départ…) |

↩︎ [Retour au sommaire](#toc)

---  

## 9️⃣ Critères d'acceptation et validation <a id="validation"></a>

| Fonction (F) | Critère d’acceptation | Méthode de validation | Responsable | Priorité (MoSCoW) |
|---|---|---|---|---|
| **F1** Gestion des comptes | ✅ Création, modification, suppression sans perte de données, conformité RGPD. | Tests d’acceptation automatisés + revue manuelle de la conformité. | PO / DPO | **M** |
| **F2** Déclaration d’intervention | ✅ Formulaire valide, enregistrement < 2 s, notification immédiate. | Tests fonctionnels (Selenium) + simulation de charge (JMeter). | QA Lead | **C** |
| **F3** Dispatch | ✅ Temps de dispatch ≤ 30 s, affectation correcte dans 95 % des cas. | Tests de performance + scénarios de régression. | MOE | **M** |
| **F4** Suivi GPS | ✅ Rafraîchissement ≤ 5 s, précision ≤ 5 m, perte < 2 % du temps. | Tests terrain avec appareils mobiles, logs de latence. | QA / Testeurs terrain | **C** |
| **F5** Messagerie sécurisée | ✅ Chiffrement end‑to‑end, délai ≤ 2 s, aucune fuite de données. | Analyse de sécurité (OWASP ZAP) + tests d’injection. | Sécurité (RSSI) | **M** |
| **F6** Tableau de bord | ✅ Temps de génération ≤ 10 s, filtres fonctionnels, export PDF/CSV. | Tests UI automatisés + validation des métriques. | PO | **S** |
| **F7** Historique & archivage | ✅ Conservation 10 ans, recherche full‑text, export conforme. | Tests d’intégrité des données + audit log. | DPO / Administrateur | **C** |
| **F8** Gestion des rôles | ✅ Rôles configurables, audit des changements, pas d’escalade d’accès. | Tests de permission (RBAC) + revue de code. | Sécurité | **M** |
| **F9** Notifications | ✅ Taux de délivrabilité ≥ 98 %, délai ≤ 5 s, gestion des erreurs. | Tests d’envoi via simulateur SMS/Email, monitoring. | Ops | **S** |
| **F10** API & interopérabilité | ✅ Réponse ≤ 200 ms, conformité FHIR R4, documentation OpenAPI. | Tests de charge API + validation de schémas. | MOE | **C** |

> **Méthodes de validation communes**  
> - **Tests unitaires** (90 % de couverture)  
> - **Tests d’intégration** (end‑to‑end)  
> - **Tests de charge** (≥ 200 req/s)  
> - **Audit sécurité** (pen‑test, revue code)  
> - **Recette utilisateur** (UAT) avec scénarios décrits en section 4.2  

↩︎ [Retour au sommaire](#toc)

---  

## 🔟 Annexes <a id="annexes"></a>

### A. Glossaire métier  

| Terme | Définition |
|---|---|
| **Demande** | Requête d’intervention d’urgence initiée par un usager. |
| **Dispatch** | Processus d’affectation d’une ambulance à une demande. |
| **ETA** | Estimated Time of Arrival – estimation du temps d’arrivée. |
| **HDS** | Hébergement de Données de Santé, certification française. |
| **RGPD** | Règlement Général sur la Protection des Données (UE). |
| **FHIR** | Fast Healthcare Interoperability Resources – standard d’échange de données de santé. |
| **MoSCoW** | Méthode de priorisation (Must, Should, Could, Won’t). |
| **RBAC** | Role‑Based Access Control – contrôle d’accès basé sur les rôles. |

### B. Référentiels et normes applicables  

| Domaine | Norme / Référentiel | Version |
|---|---|---|
| Management par la valeur | NF EN 16271 | 2023 |
| Ingénierie des exigences | ISO/IEC/IEEE 29148 | 2018 |
| Modélisation UML | ISO/IEC 19505 | 2.x |
| BPMN | ISO/IEC 19510 | 2013 |
| Sécurité de l’information | ISO 27001 | 2017 |
| Protection des données | RGPD | 2016/679 |
| Accessibilité | WCAG 2.1 | AA |
| Interopérabilité santé | HL7 FHIR R4 | 2022 |

### C. Historique des versions du document  

| Version | Date | Auteur | Modifications |
|---|---|---|---|
| 0.1 | 2026‑04‑27 | ChatGPT (assistant) | Version initiale – structure complète selon NF EN 16271 & ISO 29148. |
| 0.2 | – | – | — |
| 1.0 | – | – | — |

---  

*Document généré automatiquement, prêt à être utilisé dans VS Code ou Obsidian.*