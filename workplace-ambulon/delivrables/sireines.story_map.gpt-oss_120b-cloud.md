# 📘 Guide d’atelier : **Story Mapping** – *Représenter le périmètre fonctionnel de **SIREINES***

> **Document** : généré à partir des artefacts du projet **SIREINES** (voir les fichiers fournis).  
> **Méthodologie** : *User Story Mapping* – Jeff Patton, *User Story Mapping : Discover the Whole Story, Build the Right Product* (2014).  

---

## 📑 Sommaire  <a name="toc"></a>

| # | Section |
|---|---------|
| 1️⃣ | [Objectifs & livrable](/#introduction-et-objectifs) |
| 2️⃣ | [Contexte d’usage](/#contexte-dusage) |
| 3️⃣ | [Pré‑requis](/#pré‑requis) |
| 4️⃣ | [Parties prenantes & rôles](/#parties-prenantes-et‑rôles) |
| 5️⃣ | [Logistique](/#logistique) |
| 6️⃣ | [Déroulé détaillé de l’atelier](/#déroulé‑détaillé‑de‑latelier) |
| 7️⃣ | [Conseils de facilitation](/#conseils‑de‑facilitation) |
| 8️⃣ | [Exemple de Story Map (texte)](/#exemple‑de‑story‑map‑texte) |
| 9️⃣ | [Diagramme PlantUML](/#diagramme‑plantuml) |
| 🔟 | [Adaptations contextuelles](/#adaptations‑contextuelles) |
| 🔢 | [Livrables & étapes suivantes](/#livrables‑et‑étapes‑suivantes) |

---

## 1️⃣ Introduction & objectifs <a name="introduction-et-objectifs"></a>

**Livrable attendu**  
> *« Représenter visuellement le périmètre fonctionnel de SIREINES aligné sur le parcours utilisateur »*  

**Méthodologie** : Story Mapping (Jeff Patton)  

| Objectif opérationnel | Pourquoi ? |
|----------------------|------------|
| 🎯 **Comprendre collectivement le parcours cible de l’usager** | Aligner les équipes sur la **vision métier** (ex. : suivi de la qualification d’un agent). |
| 🎯 **Identifier les fonctionnalités nécessaires à chaque étape** | Découper le backlog en **épics → user stories**. |
| 🎯 **Prioriser pour définir un MVP fonctionnel** | Décider ce qui doit être livré en **Recette**, **Pré‑prod** ou **Prod**. |
| 🎯 **Créer un support visuel partagé** | Faciliter la **communication** entre MOA, MOE, DevOps, sécurité, RGPD, etc. |

---

## 2️⃣ Contexte d’usage <a name="contexte-dusage"></a>

| Élément | Valeur (extrait des artefacts) |
|---------|---------------------------------|
| **Produit** | **SIREINES** – répertoire national des experts / spécialistes scientifiques et techniques. |
| **Domaine métier** | Gestion des demandes de qualification par les comités de domaine (RGPD, Cerbère, BIRT). |
| **Environnement** | Application Java /J2EE, conteneur Tomcat 7, base PostgreSQL, Docker Compose, IaaS (ECO4). |
| **Contraintes** | - Déclaration CNIL (29/09/2014, n° 1034232) <br> - Sécurité (Cerbère ID 546/564) <br> - RGPD (données personnelles d’experts) <br> - Disponibilité : Prod → https://sireines.e2.rie.gouv.fr |
| **Livrables existants** | - `README.md`, `budget.md`, `declaration-rgpd.md` <br> - Scripts Docker, `docker-compose.yml` <br> - Documentation de déploiement (Recette/Pre‑prod/Prod). |
| **Objectifs produit** | - Permettre aux agents de **déposer**, **suivre**, **recevoir** la décision d’un comité de qualification. <br> - Offrir aux référentiels (structures, comités, mots‑clés) une **interface d’administration**. |
| **Persona(s) (à affiner)** | 1️⃣ **Chargé de mission (MOA)** – ex. : Pascal Zemour, responsable fonctionnel. <br> 2️⃣ **Développeur / DevOps (MOE)** – ex. : Matthieu Georges, Klee Group. <br> 3️⃣ **Agent (utilisateur final)** – salarié qui crée une demande de qualification. |
| **Quand l’utiliser** | - **Cadrage d’une nouvelle version** (ex. : 2.5.20) <br> - **Refonte d’un écran** (ex. : formulaire de création de dossier) <br> - **Priorisation d’un backlog** pour la prochaine itération (Recette → Prod). |

> **Astuce** : si vous avez un fichier `storymap_context_sireines.md`, remplacez les valeurs entre `[…]` par les vôtres.

---

## 3️⃣ Pré‑requis <a name="pré‑requis"></a>

| ✅ | Élément |
|---|----------|
| [ ] | **Vision produit** – pitch, objectifs, métriques (ex. : taux de dossiers validés, temps moyen de traitement). |
| [ ] | **Personas & recherches utilisateurs** – fiches (MOA, MOE, Agent) avec jobs‑to‑be‑done et pain‑points. |
| [ ] | **Problèmes utilisateurs hiérarchisés** – ex. : “Impossible de retrouver un mot‑clé”, “Pas de notification de décision”. |
| [ ] | **Contraintes réglementaires / techniques** – RGPD, Cerbère, BIRT 4.3, version Java 1.7, Docker Compose, PostgreSQL 14.1‑alpine. |
| [ ] | **Accès aux environnements** – Bastion + alias (`sireinesrec`, `sireinesppr`, `sireinesprod`). |
| [ ] | **Artefacts de référence** – derniers `war`, `docker‑compose.yml`, scripts `alter_*.sql`, `README.md`. |
| [ ] | **Éventuel “quick‑fix”** – si un pré‑requis manque, prévoir **15 min** en début d’atelier pour le co‑construire. |

> **Tip** : cochez chaque case en temps réel sur le tableau blanc (ou Miro) ; cela montre la **transparence** et la **préparation** de l’équipe.

---

## 4️⃣ Parties prenantes & rôles <a name="parties-prenantes-et‑rôles"></a>

| Rôle | Profil type | Responsabilité pendant l’atelier |
|------|-------------|-----------------------------------|
| **Animateur** | PO / Chef de produit (ex. : Pascal Zemour) | Piloter le déroulé, veiller aux règles d’écoute, synthétiser les décisions. |
| **Facilitateur UX** | Designer UX / Analyste fonctionnel | Proposer des verbes d’action, animer la génération d’idées, garder le focus utilisateur. |
| **Tech Lead / Architecte** | Développeur senior (ex. : Matthieu Georges) | Vérifier la faisabilité technique, identifier les dépendances (Docker, BIRT, Cerbère). |
| **MOA / Responsable métier** | Chef de bureau (ex. : Vincent Letrouit) | Valider la pertinence fonctionnelle, prioriser les exigences métier. |
| **Ops / Sécurité** | Responsable infra / SSI (ex. : équipe SG/DNUM) | Apporter les contraintes de sécurité (Cerbère ID, RGPD) et les exigences d’exploitation. |
| **Utilisateur final** *(optionnel)* | Agent, expert | Apporter la vision terrain, tester les verbes d’action (ex. : “déposer une demande”). |
| **Product Owner (PO) : **| *Facultatif* – peut cumuler avec l’animateur. |   |

> **Rappel** : un même profil peut cumuler plusieurs rôles selon la taille de l’équipe.

---

## 5️⃣ Logistique <a name="logistique"></a>

| Élément | Détails |
|--------|---------|
| **Durée totale** | **2 h 30 – 3 h** (incl. pause de 15 min à mi‑parcours). |
| **Matériel physique** | - Tableau blanc ou paperboard <br> - Post‑its : 3 couleurs (vert = backbone, bleu = stories, jaune = MVP). <br> - Marqueurs, ruban de masquage. |
| **Outils digitaux** | - **Miro / FigJam / Mural** (template Story Map pré‑chargé) <br> - **GitLab** (pour consulter le `README`, les scripts) <br> - **Docker Desktop** (démo rapide du conteneur `sireines-app`). |
| **Livrable de sortie** | - Photo/export du tableau (PNG, PDF). <br> - Diagramme PlantUML (section 9). <br> - Décision : liste des stories MVP + points de vigilance. |
| **Lieu** | Salle de réunion équipée d’un projecteur ou salle virtuelle (Miro partagé). |
| **Pré‑session** | 10 min d’**alignement** sur le contexte (slides de rappel – see section 2). |

---

## 6️⃣ Déroulé détaillé de l’atelier <a name="déroulé‑détaillé‑de‑latelier"></a>

> **Notation** : <u>Horizontal = parcours utilisateur (backbone)</u> – <u>Vertical = granularité fonctionnelle (stories)</u> – <u>ligne de flottaison = MVP/V1</u>.

| Étape | Temps | Action | Méthode / Questions clés |
|-------|-------|--------|--------------------------|
| **0️⃣ Warm‑up** | 5 min | Accueil, tour de table, rappel des **règles de co‑création** (écoute active, pas de jugement). | “Quel est votre rôle aujourd’hui ?” |
| **1️⃣ Introduction** | 5 min | Présenter les **objectifs** et le **contexte SIREINES** (vision, contraintes RGPD, Cerbère, BIRT). | “Quel est le problème principal que nous voulons résoudre ?” |
| **2️⃣ Backbone – Parcours utilisateur** | 30 min | **Définir les grandes étapes** du parcours d’un agent (ex. : *Se connecter → Déposer une demande → Suivre la décision → Consulter le statut*). | “Quelles sont les **actions observables** que l’usager réalise ?” |
| **3️⃣ Détails verticaux** | 45 min | Pour chaque étape, **brainstormer** toutes les tâches, informations, points de friction. Utiliser 3 couleurs de post‑its. | “Quelles infos sont nécessaires ? Quels écrans apparaissent ? Quels points de friction ?” |
| **4️⃣ Priorisation / Ligne de flottaison (MVP)** | 30 min | **Tracer la ligne de flottaison** : au‑dessus = MVP (déploiement Recette), en‑dessous = features V2+. | “Quelles stories sont **indispensables** pour que l’usager aille au bout ?” |
| **5️⃣ Validation & Consolidation** | 20 min | Relire le Story Map **collectivement** ; noter les **décisions**, **risques** (ex. : “Le mot‑clé doit être unique → contrainte DB”). | “Tout le monde est‑il d’accord ? Quels points restent à approfondir ?” |
| **6️⃣ Prochaine étape** | 10 min | Décider du **format du backlog** (épics → stories → critères d’acceptation) et du **plan de livraison** (Recette → Pre‑prod → Prod). | “Qui rédige les user stories ? Qui les priorise ?” |
| **7️⃣ Clôture** | 5 min | Remercier, rappeler les livrables attendus (photo, diagramme PlantUML, liste MVP). | – |

> **Facilitation tip** : utilisez un **timer** visible pour chaque étape afin de garder le rythme.

---

## 7️⃣ Conseils de facilitation <a name="conseils‑de‑facilitation"></a>

| Bonnes pratiques | À éviter |
|------------------|----------|
| 🔄 **Reformuler** les idées à haute voix pour vérifier la compréhension. | ❌ S’enfermer dans les détails techniques (laissons le Tech Lead intervenir plus tard). |
| 👥 **Faire parler tout le monde** (tour de table à chaque colonne). | ❌ Laisser un participant monopoliser la parole. |
| ✂️ **Time‑boxing strict** (timer, signal visuel). | ❌ Déborder sur la pause ou la prochaine étape. |
| 📌 **Ancrer chaque story** dans un **job‑to‑be‑done** (“En tant qu’agent, je veux…”). | ❌ Confondre “nice‑to‑have” et “must‑have”. |
| 📚 **Documenter les arbitrages** (ex. : “Mots‑clés uniques – contrainte DB”). | ❌ Oublier de noter les décisions de priorité. |
| 🎨 **Utiliser les couleurs** pour différencier MVP / V2 / V3. | ❌ Mélanger les post‑its sans légende. |

---

## 8️⃣ Exemple de Story Map (texte) <a name="exemple‑de‑story‑map‑texte"></a>

```
Backbone (horizontal) – Parcours de l’agent
--------------------------------------------------------------
[1] Se connecter → [2] Déposer une demande → [3] Suivre la décision → [4] Consulter le statut → [5] Archiver / Exporter

Stories (verticales) – Détails par étape
--------------------------------------------------------------
1. Se connecter
   • Saisir identifiant / mot de passe (authentification Cerbère)
   • Récupérer le profil (RGPD : consentement)
   • Gestion du mot de passe expiré (BIRT notification)

2. Déposer une demande
   • Sélectionner le type de qualification
   • Remplir le formulaire (données personnelles, pièces jointes)
   • Valider le formulaire (contrôles métier)
   • Recevoir accusé de réception (email)

3. Suivre la décision
   • Accéder à la liste des dossiers en cours
   • Visualiser les commentaires du comité
   • Recevoir notification de mise à jour (BIRT rapport)

4. Consulter le statut
   • Historique des décisions
   • Télécharger le rapport BIRT (PDF)
   • Demander une ré‑ouverture (si refus)

5. Archiver / Exporter
   • Export CSV des dossiers (RGPD export)
   • Suppression sécurisée après 5 ans (conformité DUA)
   • Archivage légal (CNIL)

MVP (au‑dessus de la ligne de flottaison) :
- Authentification Cerbère
- Dépôt de la demande (formulaire + pièces jointes)
- Accusé de réception
- Suivi du statut (liste + notifications)
- Export PDF du rapport BIRT

V2+ (en‑dessous) :
- Gestion des mots‑clés avancée
- Historique complet + export CSV
- Fonctionnalité “Ré‑ouverture”
- Tableau de bord statistique (nombre de dossiers, délais, etc.)
```

---

## 9️⃣ Diagramme PlantUML <a name="diagramme‑plantuml"></a>

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam roundcorner 20
skinparam legend right
  Méthode : Story Mapping (Jeff Patton)
  Axe horizontal : Parcours utilisateur
  Axe vertical   : Détails fonctionnels (stories)
  Ligne rouge    : Périmètre MVP / V1
endlegend

'--- Backbone (parcours) -------------------------------------------------
package "Backbone – Parcours Agent" as backbone {
  rectangle "Se connecter\n(Authent. Cerbère)" as step1 #LightBlue
  rectangle "Déposer une demande\n(Formulaire + pièces)" as step2 #LightBlue
  rectangle "Suivre la décision\n(Notifs & commentaires)" as step3 #LightBlue
 