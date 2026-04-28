# 📚 Guide d'atelier : **Définition du MVP** – *admin_ep*  
*Document établi à partir des principes du MVP (Lean Startup) et de la méthode de priorisation MoSCoW*  

[TOC]

---  

## 1️⃣ Introduction et objectifs  {#intro}
> **Définir collectivement le périmètre du Produit Minimum Viable** afin de tester les hypothèses produit d’*admin_ep* avec un effort maîtrisé.  

| 🎯 Objectif | 📌 Description |
|------------|----------------|
| Clarifier la **mission du MVP** | Quel apprentissage vise‑on ? Quelle hypothèse veut‑on valider ? |
| Identifier les **fonctionnalités indispensables** vs. reportables | Classification MoSCoW (Must/Should/Could/Won’t) |
| Aligner **équipes produit, métier et technique** sur un périmètre réaliste | Décision partagée, critères d’acceptation clairs |
| Éviter l’**effet tunnel** | Livrer vite, mesurer, itérer |
| Poser les bases de la **roadmap post‑MVP** | Plan d’évolution vers la V1 |

> ⚠️ **Rappel critique** – Un MVP **n’est pas** une V1 allégée : il peut se limiter à un seul parcours utilisateur, à des contournements (ex. : saisie manuelle) ou à des jeux de données factices tant que l’hypothèse est testable.  

---  

## 2️⃣ Contexte d’usage et positionnement  {#context}
| Élément | Valeur |
|---------|--------|
| **Produit** | *admin_ep* – Administration des établissements publics |
| **Domaine métier** | Moyens généraux (gestion des administrateurs d’établissements sous tutelle du ministère) |
| **Personas / Utilisateurs** | • SPES, DG de tutelle, opérateurs (ex. : Gestionnaires) <br>• Utilisateur référent (représentant métier) |
| **Hypothèses à tester** | 1️⃣ *L’automatisation de l’alimentation depuis le JORF réduit le temps de mise à jour de ≥ 30 %.* <br>2️⃣ *Le module d’alerte mandat (mail) augmente le taux de renouvellement à temps de ≥ 90 %.* |
| **Contraintes techniques** | • Java 8, Tomcat 9.0.8, PostgreSQL 9.6.11 <br>• Montée prévue : Tomcat 10, PostgreSQL 15 <br>• Conteneurisation en cours, IaaS (ECO4) |
| **Contraintes réglementaires** | DICT = Oui (évaluation 07/09/2018) – exigences de traçabilité & sécurisation des données |
| **Story map existant** | *Non fourni* – on part d’une description fonctionnelle (voir section 2). |
| **Environnement cible du MVP** | Pre‑prod (containerisé) → déploiement pilote sur un établissement test. |

---  

## 3️⃣ Pré‑requis indispensables  {#prereq}
- [ ] **Vision produit formalisée** – pitch, objectifs métier, métriques de succès (ex. : % de réduction du temps d’alimentation, taux de renouvellement mandat).  
- [ ] **Hypothèses à tester** – liste claire (voir tableau ci‑dessus).  
- [ ] **Story Mapping / Parcours utilisateur** – au minimum le **parcours « Alimentation JORF → mise à jour mandat »**.  
- [ ] **Personas et retours utilisateurs** – verbatims ou interviews synthétisés.  
- [ ] **Contraintes identifiées** – techniques (versions, conteneurisation), réglementaires (DICT), délais/budget.  

> 💡 *Si un pré‑requis manque, prévoir 20 min en début d’atelier pour le co‑construire (ex. : reformuler la vision en 1 slide).*

---  

## 4️⃣ Parties prenantes et rôles  {#roles}
| Rôle | Profil type | Responsabilité dans l'atelier |
|------|-------------|------------------------------|
| **Animateur** | Chef de produit / PNM | Cadrer, faciliter, garder le cap « apprentissage » |
| **Profil technique** | Tech Lead / Architecte Java | Évaluer faisabilité, effort, dépendances (Tomcat, PostgreSQL, conteneurs) |
| **Porteur métier** | MOA / Responsable DG de tutelle | Valider la pertinence fonctionnelle, la valeur utilisateur |
| **Designer UX/UI** *(optionnel)* | Designer produit | Proposer des maquettes légères du parcours d’alimentation |
| **Utilisateur référent** *(optionnel)* | Opérateur / Gestionnaire | Apporter le regard « usage réel », challenger les priorités |

> ☝️ *Un même participant peut cumuler plusieurs rôles selon les disponibilités.*

---  

## 5️⃣ Logistique de l'atelier  {#logistics}
- **Durée** : 2 h 30 – 4 h (prévoir une pause à 1 h 30 si > 3 h).  
- **Matériel physique** : tableau blanc, post‑its 4 couleurs (M / S / C / W), marqueurs, ruban de masquage.  
- **Matériel digital** : outil collaboratif (Miro, FigJam, Mural…) avec template MoSCoW pré‑préparé.  
- **Livrable de sortie** :  
  1. **Matrice MoSCoW** validée (tableau + justifications)  
  2. **Périmètre MVP** (liste des *Must Have*)  
  3. **Roadmap initiale** (MVP → V1 → itérations)  
  4. **Hypothèses de test** + métriques de succès  

---  

## 6️⃣ Déroulé détaillé de l'atelier  {#run}
### 🎯 Étape 1 – Introduction & alignement (15 min)  {#step1}
1. Présenter les objectifs du MVP (ex. : valider l’hypothèse d’automatisation JORF).  
2. Rappeler le contexte (personas, hypothèses, contraintes).  
3. Expliquer la méthode **MoSCoW** :

| Catégorie | Définition | Critère de décision |
|-----------|------------|---------------------|
| **M**ust Have | Indispensable pour que le MVP soit viable | Sans cela, le produit est inutile / l’hypothèse non testable |
| **S**hould Have | Important mais non critique pour le MVP | Valeur ajoutée significative, mais reportable sans bloquer |
| **C**ould Have | Optionnel, “nice‑to‑have” | Améliore l’expérience mais n’impacte pas l’apprentissage |
| **W**on’t Have | Exclu du MVP (pour l’instant) | Trop coûteux, hors scope, ou non prioritaire pour l’apprentissage |

> ✅ **Conseil** – Reformuler la mission du MVP en 1 phrase :  
> *« Avec ce MVP, nous voulons vérifier que l’alimentation automatique depuis le JORF réduit le temps de mise à jour de ≥ 30 % en observant le taux de traitement des mandats sur 3 mois auprès des gestionnaires. »*

### 🔍 Étape 2 – Rappel du périmètre fonctionnel (30 min)  {#step2}
1. **Afficher le Story Map** (ou la liste des épics) :  
   - **Alimentation JORF** (scraping, parsing)  
   - **Gestion des mandats** (CRUD, notifications)  
   - **Authentification Cerbère** (rôles)  
   - **Interface de lecture / recherche**  
   - **Statistiques & reporting**  
2. Pour chaque fonctionnalité, préciser :  
   - **Besoin utilisateur** (ex. : « Je veux être averti 30 jours avant l’échéance d’un mandat »)  
   - **Hypothèse produit** liée (ex. : « L’alerte mail augmente le taux de renouvellement »)  
   - **Contraintes** (ex. : dépend de Tomcat 10, besoin de tâche cron)  
3. Regrouper les éléments similaires, éliminer les doublons.  

> 📌 *Astuce* : Utiliser des verbes d’action (« alimenter », « notifier », « rechercher ») pour rester centré sur l’expérience.  

### 🎚️ Étape 3 – Classification MoSCoW (60‑90 min)  {#step3}
1. **Présenter chaque fonctionnalité** une à une (ou par groupe).  
2. **Discussion guidée** : poser les questions suivantes :  
   - *Le MVP peut‑il fonctionner sans cette fonctionnalité ?*  
   - *Quel impact sur l’apprentissage si on la retire ?*  
   - *Quel effort technique / délai pour la livrer ?*  
   - *Existe‑t‑il un contournement simple (ex. : saisie manuelle, données factices) ?*  
3. **Vote ou consensus** :  
   - **Option A – Dot Voting** : chaque participant dispose de 3 votes à répartir sur les « Must ».  
   - **Option B – Débat structuré** : un participant propose une catégorie, les autres valident/challengent.  
4. **Placement** : coller le post‑it dans la colonne MoSCoW correspondante.  

> 💡 **Règle d’or** : limiter les *Must Have* à l’essentiel absolu (max ≈ 30 % du total).  

### ✅ Étape 4 – Validation du périmètre MVP (30 min)  {#step4}
Utiliser la **check‑list de validation** :

- [ ] Le périmètre *Must Have* permet‑il de tester **au moins une hypothèse** clairement définie ?  
- [ ] Un utilisateur peut‑il accomplir un **parcours complet** (ex. : JORF → mandat créé → alerte) ?  
- [ ] Les **contournements acceptables** sont‑ils identifiés (ex. : saisie manuelle du JORF) ?  
- [ ] L’**effort estimé** (jours / personnes) est‑il compatible avec le **délai cible** du MVP (ex. : 6 semaines) ?  
- [ ] Les **métriques de succès** (temps d’alimentation, taux de renouvellement) sont‑elles définies ?  

**Ajustements** :  
- Si le périmètre est trop large → re‑discuter les *Must* et reporter certains items en *Should/Could*.  
- Si le périmètre est trop léger → vérifier qu’aucune hypothèse critique n’a été oubliée.  

### 🗺️ Étape 5 – Roadmap & prochaines étapes (15‑30 min)  {#step5}
1. **Documenter les décisions** :  
   - Table *Must Have* (périmètre MVP)  
   - Justifications des arbitrages (traçabilité)  
   - Hypothèses de test associées à chaque *Must*  
2. **Ébaucher la roadmap** :  

| Phase | Contenu | Date cible |
|-------|---------|-----------|
| **MVP** | Alimentation JORF (automatique), gestion mandats + alerte mail, authentification Cerbère (rôles de base) | S+6 semaines |
| **V1** | Interface recherche avancée, tableau de bord statistiques, support multi‑établissements | S+12 semaines |
| **Itérations** | Optimisation performances, migration Tomcat 10 / PostgreSQL 15, conteneurisation complète | S+24 semaines |

3. **Définir le suivi** :  
   - **Qui** pilote les tests utilisateurs du MVP ? (ex. : Responsable métier)  
   - **Comment** collecter & analyser les retours (outil ticket, tableau de bord)  
   - **Quand** prévoir la revue post‑MVP pour décider de la suite (pivot / persévérer / arrêter)  

> 📸 **Action immédiate** : partager la matrice MoSCoW et la roadmap brouillon dans les 24 h pour validation écrite.

---  

## 7️⃣ Conseils de facilitation  {#facilitation}
| Bonnes pratiques | À éviter |
|------------------|----------|
| Ancrer chaque décision dans une **hypothèse à tester** | Prioriser par préférence personnelle ou « on a toujours fait comme ça » |
| Challenger systématiquement les *Must* : *« Et si on enlevait ça ? »* | Accepter un MVP trop large par peur de décevoir |
| Proposer des **contournements légers** (manuel, data factice) pour réduire le scope | Confondre « faisable techniquement » et « nécessaire pour l’apprentissage » |
| Faire participer activement les profils **métiers** et **utilisateurs** | Laisser un seul profil (tech ou métier) dominer les arbitrages |
| Documenter les *Won’t Have* avec leurs raisons (évite les re‑demandes) | Oublier de prévoir la revue post‑MVP et les critères de succès |

---  

## 8️⃣ Alternative : MVP par scénario utilisateur  {#scenario}
Quand la méthode MoSCoW a du mal à réduire le scope (réflexe « tout mettre dans le MVP »), privilégier un **scénario complet** :

| Critère de sélection du scénario MVP | Exemple concret |
|--------------------------------------|-----------------|
| **Parcours complet mais borné** | *Alimenter le mandat d’un établissement depuis le JORF, recevoir l’alerte mail, valider le renouvellement* (tout automatisé sauf la saisie du JORF, qui peut être manuelle). |
| **Forte innovation à tester** | *Nouvelle interface de recherche texte libre* (testée avant d’intégrer les filtres avancés). |
| **Simplicité de mise en œuvre** | *Utiliser des jeux de données JORF fournis en CSV* (pas de scraping) pour le prototype. |
| **Valeur d’apprentissage maximale** | Scénario qui valide l’hypothèse 1 (gain de temps) ou l’hypothèse 2 (effet de l’alerte). |

> 💡 **Astuce** : formuler le scénario MVP comme une user story élargie :  
> *« En tant que **Gestionnaire**, je veux **recevoir automatiquement une alerte mail 30 jours avant l’échéance d’un mandat** afin de **renouveler le mandat à temps**, même si l’alimentation JORF est saisie manuellement. »*

---  

## 9️⃣ Diagramme Mermaid du processus d’atelier MVP (admin_ep)  {#mermaid}
```mermaid
graph TB;
    %% Acteurs;
    actor_pm[👤 Chef de produit]
    actor_tech[👤 Tech Lead]
    actor_biz[👤 Porteur métier]
    actor_user[👤 Utilisateur référent]

    %% Phases (packages)
    package prep["Phase 1 – Pré‑préparation"]
    package workshop["Phase 2 – Atelier MoSCoW"]
    package deliver["Phase 3 – Livrables & suite"]
    package loop["Phase 4 – Boucle d’apprentissage"]

    %% Étapes de la phase 1;
    prep --> stepVision[Vision & objectifs<br/>📌]
    prep --> stepHyp[Hypothèses à tester<br/>🔍]
    prep --> stepMap[Story map (ou liste épics)<br/>🗂️]

    %% Déclenchement de l'atelier;
    stepMap --> workshop;
    %% Étapes de la phase 2;
    workshop --> align[Alignement (intro) 🎯]
    workshop --> recall[Rappel périmètre 📚]
    workshop --> classify[Classification MoSCoW 🎚️]
    workshop --> validate[Validation du périmètre ✅]
    workshop --> roadmap[Roadmap & suite 🗺️]

    %% Livrables de la phase 3;
    roadmap --> deliver;
    deliver --> matrix[Matrice MoSCoW<br/>✅]
    deliver --> scope[Périmètre MVP (Must) ✅]
    deliver --> roadmapDoc[Roadmap initiale 📅]
    deliver --> metrics[Hypothèses & métriques 🎯]

    %% Boucle d’apprentissage;
    metrics --> loop;
    loop --> test[Tests utilisateurs MVP<br/>🧪]
    loop --> analyse[Analyse des retours<br/>📊]
    loop --> decide[Décision (pivot / persévérer / arrêter)🔄]
    decide -.-> prep;
    %% Styles;
    classDef actor fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phase fill:#F0F4C3,stroke:#7B1FA2,stroke-width_2px;
    classDef step fill:#FFF9C4,stroke:#F57F17,stroke-width_1px,stroke-dasharray: 5 5;

    class pm,tech,biz,user actor;
    class prep,workshop,deliver,loop phase;
    class stepVision,stepHyp,stepMap,align,recall,classify,validate,roadmap,matrix,scope,roadmapDoc,metrics,test,analyse,decide step;
```

---  

## 10️⃣ Adaptations contextuelles  {#adaptations}
| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Refonte d’un produit existant** | Partir des points de friction (ex. : mise à jour manuelle des mandats) pour identifier les *Must* qui résolvent les blocages majeurs. |
| **Produit fortement réglementé** | Intégrer les exigences DICT comme *Must* uniquement si elles bloquent l’hypothèse de test ; sinon, prévoir des **contournements** documentés. |
| **Multi‑profil utilisateurs** | Définir un MVP par **persona prioritaire** (ex. : Gestionnaire) ou un **parcours transversal** couvrant les besoins communs. |
| **Contrainte de délai très court** | Cibler **un seul scénario complet** (ex. : alimentation JORF + alerte) ; accepter des contournements manuels en back‑office. |
| **Innovation à fort risque** | Prioriser les fonctionnalités qui valident l’hypothèse la plus incertaine (ex. : parsing JORF) même si le parcours est partiel. |

---  

## 11️⃣ Livrables et intégration continue  {#livrables}
| Livrable immédiat | Description |
|-------------------|-------------|
| **Matrice MoSCoW** | Tableur (ou tableau markdown) listant chaque fonctionnalité + catégorie + justification. |
| **Périmètre MVP** | Liste des *Must Have* + contournements acceptés (ex. : saisie manuelle JORF). |
| **Roadmap initiale** | MVP → V1 → itérations (gantt simplifié). |
| **Hypothèses de test** | Tableau : hypothèse, métrique, seuil de succès, date de mesure. |

| Livrable dérivé | Description |
|-----------------|-------------|
| **Backlog produit** | Epics → user stories taggées MoSCoW. |
| **Plan de test utilisateur** | Recrutement, scénarios, collecte (Google Forms, JIRA). |
| **Template de revue post‑MVP** | Critères de décision : pivot / persévérer / arrêter. |

**Prochaines étapes suggérées**  
1. Rédiger les **user stories MVP** avec critères d’acceptation.  
2. Maquetter les **écrans clés** du parcours (alimenter JORF, alerte mail).  
3. Estimer les stories (t‑shifts) & planifier les sprints de dev.  
4. Préparer le **protocole de test** (KPIs, outils de suivi).  

---  

## 12️⃣ Mini‑glossaire  {#glossary}
| Acronyme | Signification |
|----------|----------------|
| **MVP** | Minimum Viable Product – version minimale d’apprentissage. |
| **MoSCoW** | Méthode de priorisation : Must, Should, Could, Won’t. |
| **JORF** | Journal Officiel de la République Française (source de données). |
| **DICT** | Déclaration d’Impact sur la Protection des Données (exigence RGPD). |
| **Cerbère** | Système d’authentification interne du ministère. |
| **PNM** | Programme National de Modernisation. |
| **ACAI** | Plateforme d’hébergement Java du ministère. |
| **IaaS** | Infrastructure as a Service (cloud). |
| **V1** | Version 1 – produit complet après le MVP. |
| **KPIs** | Key Performance Indicators – métriques de succès. |

---  

## 13️⃣ Retour rapide – Personnalisation en 5 min
Remplacez les parties entre **[crochets]** par vos propres éléments :  

- `[Nom du produit]` → **admin_ep**  
- `[Persona principal]` → **Gestionnaire**  
- `[Hypothèse 1]` → *« L’alimentation automatique depuis le JORF réduit le temps de mise à jour de ≥ 30 % »*  
- `[Hypothèse 2]` → *« Le module d’alerte mandat augmente le taux de renouvellement à ≥ 90 % »*  
- `[Durée cible MVP]` → **6 semaines**  

---  

**Bon atelier !** 🎉  

---  