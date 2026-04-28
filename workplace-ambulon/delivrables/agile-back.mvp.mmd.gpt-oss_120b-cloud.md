# 📘 Guide d’atelier : **Définir le MVP** avec la méthode **MoSCoW**  
*Document établi à partir des principes du MVP (Lean Startup) et de la méthode de priorisation MoSCoW*  

---  

## 📑 Table des matières  <!-- TOC -->
1. [Introduction & objectifs](#1-introduction--objectifs)  
2. [Contexte d’usage & positionnement](#2-contexte-dusage--positionnement)  
3. [Pré‑requis indispensables](#3-pre-requis-indispensables)  
4. [Parties prenantes & rôles](#4-parties-prenantes--rôles)  
5. [Logistique de l’atelier](#5-logistique-de-latelier)  
6. [Déroulé détaillé de l’atelier](#6-déroulé-détaillé-de-latelier)  
   - 6.1 Étape 1 – Introduction & alignement  
   - 6.2 Étape 2 – Rappel du périmètre fonctionnel  
   - 6.3 Étape 3 – Classification MoSCoW  
   - 6.4 Étape 4 – Validation du périmètre MVP  
   - 6.5 Étape 5 – Roadmap & prochaines étapes  
7. [Conseils de facilitation](#7-conseils-de-facilitation)  
8. [Alternative : MVP par scénario utilisateur](#8-alternative--mvp-par-scénario-utilisateur)  
9. [Diagramme Mermaid du processus MVP](#9-diagramme-mermaid-du-processus-mvp)  
10. [Adaptations contextuelles](#10-adaptations-contextuelles)  
11. [Livrables & suite d’intégration continue](#11-livrables--suite-dintégration-continue)  
12. [Mini‑glossaire](#12-mini-glossaire)  

---  

## 1️⃣ Introduction & objectifs
> **Vue d’ensemble** : *« Définir collectivement le périmètre du Produit Minimum Viable pour tester des hypothèses produit avec un effort maîtrisé »*  

**Méthodologie** : Atelier basé sur le **MVP (Lean Startup)** + priorisation **MoSCoW**.  

### 🎯 Objectifs opérationnels
| # | Objectif |
|---|----------|
| 🎯 | Clarifier la mission du MVP : **qu’est‑ce qu’on apprend ? quelle hypothèse teste‑t‑on ?** |
| 🔍 | Identifier les fonctionnalités **indispensables** vs. **reportables** |
| 🤝 | Aligner équipes produit, métier & technique sur un périmètre réaliste |
| 📏 | Éviter l’effet tunnel : livrer vite, mesurer, itérer |
| 🗺️ | Poser les bases de la roadmap post‑MVP (MVP → V1 → itérations) |

> ⚠️ **Rappel critique** – Un MVP n’est **pas** une V1 allégée. C’est un **outil d’apprentissage** qui peut se limiter à **un seul parcours utilisateur** avec des contournements (données factices, saisie manuelle…) acceptables.  

---  

## 2️⃣ Contexte d’usage & positionnement
| Élément | Détails |
|--------|--------|
| **Type de livrable** | Standard ✅ |
| **Nature** | Atelier 🤝 |
| **Activité** | « Imaginer une solution » |
| **Quand l’utiliser** | <ul><li>Après recherche utilisateur & formalisation de la vision produit</li><li>Après un premier travail de périmètre fonctionnel (ex. : Story Mapping)</li><li>Avant le lancement des développements, pour cadrer le premier incrément</li></ul> |
| **Cas d’usage typiques** | <ul><li>Lancement d’un nouveau produit digital</li><li>Refonte d’un service existant avec changement de paradigme</li><li>Test d’une innovation ou d’une hypothèse à fort risque</li><li>Réduction de scope pour respecter des contraintes de délai/budget</li></ul> |

*Exemple d’application* : **agile‑back** – back‑office Symfony permettant la création / modification d’études.  
Hypothèse type : *« Les utilisateurs (agents métier) peuvent créer une étude complète en moins de 5 minutes ».*
  
---  

## 3️⃣ Pré‑requis indispensables
> ✅ **À préparer **avant l’atelier (ou co‑construire 20 min en début d’atelier).  

| ✔️ | Pré‑requis |
|---|------------|
| 1️⃣ | **Vision produit** : pitch, objectifs métier, métriques de succès |
| 2️⃣ | **Hypothèses à tester** : liste claire des paris produit à valider / invalider |
| 3️⃣ | **Story Mapping** (ou backlog fonctionnel) : parcours utilisateur + fonctionnalités associées |
| 4️⃣ | **Personas & retours utilisateurs** : verbatims, enquêtes, entretiens synthétisés |
| 5️⃣ | **Contraintes identifiées** : techniques, réglementaires, budgétaires, délais |

> 💡 *Si un pré‑requis manque, réserver 20 min en début d’atelier pour le reformuler rapidement (ex. : rédiger la vision en 1 slide).*

---  

## 4️⃣ Parties prenantes & rôles
| Rôle | Profil type | Responsabilité dans l’atelier |
|------|-------------|------------------------------|
| **Animateur** | Chef de produit / PO | Cadrer, faciliter, garder le cap « apprentissage » |
| **Profil technique** | Tech Lead / Architecte | Évaluer faisabilité, effort, dépendances techniques |
| **Porteur métier** | MOA / Responsable métier | Valider la pertinence fonctionnelle & la valeur utilisateur |
| **Designer UX/UI** *(optionnel)* | Designer produit | Proposer des alternatives légères, valider l’expérience minimale |
| **Utilisateur référent** *(optionnel)* | Personne cible du produit | Apporter le regard « usage réel », challenger les priorités |

> ☝️ *Un même participant peut cumuler plusieurs rôles selon la disponibilité.*  

---  

## 5️⃣ Logistique de l’atelier
| Élément | Détails |
|--------|---------|
| **Durée** | 2 h 30 – 4 h (prévoir une pause à 1 h 30 si > 3 h) |
| **Matériel – physique** | Tableau blanc, post‑its 4 couleurs (Must/Should/Could/Won’t), marqueurs, ruban de masquage |
| **Matériel – digital** | Outil collaboratif (Mural, FigJam, Miro, Klaxoon…) avec template MoSCoW pré‑préparé |
| **Livrable de sortie** | Périmètre MVP validé + matrice MoSCoW + roadmap initiale + hypothèses de test |
| **Salle** | Configuration en U ou en cercle pour favoriser les échanges |

---  

## 6️⃣ Déroulé détaillé de l’atelier  

### 🎯 Étape 1 — Introduction & alignement (15 min)  
**Objectif** : Aligner toutes les parties sur les objectifs et le cadre de l’atelier.  

1. Présenter la **mission du MVP** :  
   *« Avec ce MVP, nous voulons vérifier que **[hypothèse]** en observant **[métrique]** auprès de **[persona]**. »*  
2. Rappeler le **contexte** (personas, hypothèses, contraintes).  
3. Expliquer la méthode **MoSCoW** :  

| Catégorie | Définition | Critère de décision |
|-----------|------------|---------------------|
| **M**ust Have | Indispensable pour que le MVP soit viable | Sans cela, le produit est inutile / l’hypothèse non testable |
| **S**hould Have | Important mais non critique pour le MVP | Valeur ajoutée significative, mais reportable sans bloquer |
| **C**ould Have | Optionnel, « nice‑to‑have » | Améliore l’expérience mais n’impacte pas l’apprentissage |
| **W**on’t Have | Exclu du MVP (pour l’instant) | Trop coûteux, hors scope, ou non prioritaire pour l’apprentissage |

> ✅ **Conseil** : Formuler la mission du MVP en **une phrase** avant de passer à l’étape suivante.  

---

### 🔍 Étape 2 — Rappel du périmètre fonctionnel (30 min)  
**Objectif** : Re‑contextualiser les fonctionnalités potentielles avant la priorisation.  

1. Afficher le **Story Map** (ou la liste des épics / user stories).  
2. Pour chaque étape du parcours :  
   - Besoin utilisateur associé  
   - Hypothèse produit testée  
   - Contraintes techniques / réglementaires connues  
3. Regrouper les éléments similaires, supprimer les doublons.  

> 📌 *Utiliser des verbes d’action utilisateur (« Créer », « Modifier », « Exporter ») pour rester centré sur l’expérience.*  

---

### 🎚️ Étape 3 — Classification MoSCoW (60‑90 min)  
**Objectif** : Prioriser collectivement les fonctionnalités selon MoSCoW.  

1. **Présentation** – chaque fonctionnalité/épic est affichée une à une.  
2. **Discussion guidée** – poser les questions suivantes :  
   - *« Le MVP peut‑il fonctionner sans cette fonctionnalité ? »*  
   - *« Quel impact sur l’apprentissage si on la retire ? »*  
   - *« Quel effort technique / délai pour la livrer ? »*  
   - *« Existe‑t‑il un contournement simple (manuel, data factice) ? »*  
3. **Vote ou consensus** :  
   - **Dot‑Voting** : chaque participant dispose de 3‑5 votes à répartir sur les “Must Have” potentiels.  
   - **Débat structuré** : une personne propose une catégorie, les autres valident / challengent.  
4. **Placement** : déposer la fonctionnalité dans la colonne **Must / Should / Could / Won’t**.  

> 💡 **Règle d’or** : Limiter les **Must Have** à **l’essentiel absolu**. Si tout est “Must”, rien n’est prioritaire.  

---

### ✅ Étape 4 — Validation du périmètre MVP (30 min)  
**Objectif** : Vérifier que le périmètre “Must Have” forme un MVP cohérent et testable.  

#### 📋 Checklist de validation  
- [ ] Le périmètre MVP **permet de tester au moins une hypothèse claire**.  
- [ ] Un utilisateur peut **accomplir un parcours complet** (même minimal).  
- [ ] Les **contournements acceptés** sont identifiés (ex. : saisie manuelle, jeux de données factices).  
- [ ] L’**effort estimé** est compatible avec le **délai cible** du MVP.  
- [ ] Les **métriques de succès** sont définies pour évaluer les retours.  

#### 🔧 Ajustements  
- Si le périmètre est **trop large** → re‑discuter les “Must Have”, identifier des reports.  
- Si le périmètre est **trop léger** → vérifier qu’une hypothèse critique n’a pas été oubliée.  

---

### 🗺️ Étape 5 — Roadmap & prochaines étapes (15‑30 min)  
**Objectif** : Poser les bases de la suite : MVP → V1 → itérations.  

| Livrable | Contenu |
|----------|---------|
| **Matrice MoSCoW** | Décisions finales (Must/Should/Could/Won’t) + justifications |
| **Périmètre MVP** | Liste des “Must Have” + contournements acceptés |
| **Roadmap initiale** | <ul><li>MVP : périmètre, métriques, date cible</li><li>V1 : intégration des “Should Have” prioritaires</li><li>Backlog : “Could Have” + idées futures</li></ul> |
| **Plan de suivi** | • Responsable du test MVP (ex. : PO) <br>• Méthode de collecte & d’analyse des retours <br>• Date de revue post‑MVP (pivot / persévérer / arrêter) |

> 📸 **Action immédiate** : Partager la matrice MoSCoW et la roadmap brouillon **dans les 24 h** pour validation écrite.  

---  

## 7️⃣ Conseils de facilitation
| Bonnes pratiques | À éviter |
|------------------|----------|
| Ancrer chaque décision dans une **hypothèse** à tester | Prioriser par préférence personnelle ou « on a toujours fait comme ça » |
| Challenger systématiquement les **Must Have** : *« Et si on l’enlevait ? »* | Accepter un MVP trop large par peur de décevoir |
| Proposer des **contournements légers** (manuel, data factice) pour réduire le scope | Confondre “faisable techniquement” et “nécessaire pour l’apprentissage” |
| Faire participer activement les profils **métier** et **utilisateurs** | Laisser un seul profil (tech ou métier) dominer les arbitrages |
| Documenter les **Won’t Have** avec leurs raisons (pour éviter les re‑demandes) | Oublier de prévoir la revue post‑MVP et les critères de succès |

---  

## 8️⃣ Alternative : MVP par scénario utilisateur  
Lorsque la méthode MoSCoW peine à réduire le scope (réflexe “tout mettre dans le MVP”), privilégier une approche **par scénario complet** :  

| Critère de sélection du scénario MVP | Exemple concret |
|--------------------------------------|-----------------|
| **Parcours complet mais borné** | Dépôt d’un dossier sans l’instruction : l’utilisateur va au bout, le traitement est manuel en back‑office |
| **Forte innovation à tester** | Nouvelle interface de saisie : tester l’ergonomie avant d’intégrer les SI existants |
| **Simplicité de mise en œuvre** | Parcours ne nécessitant pas de reprise de données complexes, ou contournable via un jeu de données bac à sable |
| **Valeur d’apprentissage maximale** | Scénario qui valide l’hypothèse la plus risquée ou incertaine du produit |

> 💡 **Astuce** : Formuler le scénario MVP comme une **user story élargie** :  
*« En tant que **[persona]**, je veux **[action complète]** afin de **[bénéfice]**, même si **[contournement accepté]** ».  

---  

## 9️⃣ Diagramme Mermaid du processus de définition du MVP
```mermaid
graph TB;
    %% Acteurs;
    pm[👤 Chef de produit]:::acteur;
    tech[👤 Tech Lead]:::acteur;
    biz[👤 Porteur métier]:::acteur;
    user[👤 Utilisateur référent]:::acteur;
    %% Phase 1 – Pré‑préparation;
    subgraph prep["Phase 1 – Pré‑préparation"]
        vision[Vision & hypothèses]:::phasePrep;
        storymap[Story Mapping / Backlog]:::phasePrep;
        constraints[Contraintes (tech, reg.)]:::phasePrep;
    end;
    %% Phase 2 – Atelier MoSCoW;
    subgraph workshop["Phase 2 – Atelier MoSCoW"]
        align[Alignement : objectifs MVP]:::phaseWorkshop;
        classify[Classification MoSCoW]:::phaseWorkshop;
        validate[Validation périmètre MVP]:::phaseWorkshop;
    end;
    %% Phase 3 – Livrables & suite;
    subgraph deliver["Phase 3 – Livrables & suite"]
        matrix[Matrice MoSCoW]:::phaseDeliver;
        roadmap[Roadmap MVP → V1]:::phaseDeliver;
        metrics[Hypothèses de test & métriques]:::phaseDeliver;
    end;
    %% Phase 4 – Boucle d’apprentissage;
    subgraph loop["Phase 4 – Boucle d’apprentissage"]
        test[Tests utilisateurs MVP]:::phaseLoop;
        learn[Analyse des retours]:::phaseLoop;
        decide[Décision : pivot / persévérer / arrêter]:::phaseLoop;
    end;
    %% Flux principaux;
    vision --> align;
    storymap --> align;
    constraints --> align;
    align --> classify;
    classify --> validate;
    validate --> matrix;
    matrix --> roadmap;
    roadmap --> test;
    test --> learn;
    learn --> decide;
    decide -.-> vision;
    %% Styles;
    classDef acteur fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phasePrep fill:#ADD8E6,stroke:#1976D2,stroke-width_2px;
    classDef phaseWorkshop fill:#90EE90,stroke:#2E7D32,stroke-width_2px;
    classDef phaseDeliver fill:#FFFFE0,stroke:#F57C00,stroke-width_2px;
    classDef phaseLoop fill:#E6E6FA,stroke:#7B1FA2,stroke-width_2px;
```

---  

## 🔟 Adaptations contextuelles
| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Refonte d’un produit existant** | Partir des points de friction actuels pour identifier les “Must Have” qui résolvent les blocages majeurs. |
| **Produit fortement réglementé** | Intégrer les contraintes légales comme “Must Have” **uniquement** si elles bloquent l’hypothèse de test ; sinon prévoir des contournements documentés. |
| **Multi‑profils utilisateurs** | Définir un MVP par **persona prioritaire**, ou un parcours transversal minimal couvrant les besoins communs. |
| **Contraintes de délai très court** | Cibler **un seul scénario utilisateur complet** plutôt que des fonctionnalités éparses ; accepter des contournements manuels en back‑office. |
| **Innovation à fort risque** | Prioriser les fonctionnalités qui valident l’**hypothèse la plus incertaine**, même si le parcours est partiel. |

---  

## 1️⃣1️⃣ Livrables et intégration continue
| Livrable immédiat | Description |
|-------------------|-------------|
| **Matrice MoSCoW** (tableau) | Décisions finales + justifications (archivées dans Confluence / Notion). |
| **Périmètre MVP** | Liste des “Must Have” + contournements acceptés (doc partagé). |
| **Roadmap initiale** | MVP → V1 → itérations (backlog tagué MoSCoW). |
| **Hypothèses de test & métriques** | KPIs à suivre (ex. : temps de création d’étude, taux d’erreur). |
| **Plan de test utilisateur** | Scénarios, recrutement, collecte (Google Forms, Hotjar, etc.). |
| **Template de revue post‑MVP** | Critères décisionnels : pivot / persévérer / arrêter. |

| Livrable dérivé | Description |
|-----------------|-------------|
| **Backlog produit structuré** | Epics → user stories avec tags MoSCoW. |
| **Maquettes légères** | Wireframes du parcours MVP (Sketch / Figma). |
| **Estimation technique** | Story points / effort (planning poker). |
| **Sprint plan** | Stories du MVP découpées en tâches. |
| **Protocoles de suivi** | Dashboard (Grafana, Metabase) pour les métriques. |
| **Documentation de décision** | Historique des arbitrages (pour audit). |

### Prochaines étapes suggérées
1. Rédiger les **user stories MVP** avec critères d’acceptation.  
2. Maquetter les écrans clés du parcours MVP.  
3. Estimer techniquement & planifier les sprints de développement.  
4. Préparer le **protocole de test utilisateur** & les métriques de suivi.  
5. Lancer le **développement du MVP** et préparer la **revue post‑MVP** (2‑3 semaines après le lancement).  

---  

## 1️⃣2️⃣ Mini‑glossaire
| Acronyme / Terme | Définition |
|-------------------|------------|
| **MVP** | Minimum Viable Product : version la plus petite du produit qui permet de tester une hypothèse métier. |
| **MoSCoW** | Méthode de priorisation : Must, Should, Could, Won’t. |
| **Story Mapping** | Technique de Jeff Patton : visualiser le parcours utilisateur → épics → stories. |
| **Hypothèse produit** | Pari mesurable : *« Si on ajoute X, alors Y »*. |
| **Pivot** | Changement de direction basé sur les apprentissages du MVP. |
| **V1** | Première version fonctionnelle complète (au‑delà du MVP). |
| **Contournement** | Solution temporaire (ex. : données factices, saisie manuelle) acceptée pour le MVP. |
| **KPIs** | Key Performance Indicators – métriques de succès du MVP. |
| **PO** | Product Owner – responsable de la vision produit et du backlog. |
| **Tech Lead** | Responsable technique, valide la faisabilité et l’effort. |
| **DO‑R** | Definition of Ready – critères pour qu’une story entre en sprint. |
| **DO‑D** | Definition of Done – critères de complétion d’une story. |

---  

*Ce guide est prêt à être copié‑collé dans VS Code, Obsidian ou tout autre éditeur Markdown. Il ne dépend d’aucune source externe et peut être personnalisé en **5 minutes** en remplaçant les parties entre `[…]` par les informations propres à votre projet.*  