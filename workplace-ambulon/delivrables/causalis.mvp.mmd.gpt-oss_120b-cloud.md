# 📘 Guide d’atelier : **Définition du MVP** (Méthode MoSCoW)  
*Projet : **causalis** – Application de gestion et de statistiques des accidents du travail*  

> **Document établi à partir des principes du MVP (Lean Startup) et de la méthode de priorisation MoSCoW**  

---  

## 📖 Table des matières  
[TOC]

---  

## 1️⃣ Introduction & objectifs  

| 🎯 Objectif | Description |
|------------|-------------|
| **Clarifier la mission du MVP** | *« Avec ce MVP, nous voulons vérifier que le nouveau tableau de bord d’accidents améliore la prise de décision des gestionnaires tout en limitant le temps de développement. »* |
| **Prioriser les fonctionnalités** | Classer les besoins en **Must / Should / Could / Won’t** pour limiter le périmètre. |
| **Aligner les équipes produit, métier & technique** | Créer un consensus sur ce qui sera réellement livré dans la première itération. |
| **Éviter l’effet tunnel** | Livrer rapidement, mesurer, apprendre, itérer. |
| **Poser les bases de la roadmap post‑MVP** | Décider des prochains incréments (V1, V2, …). |

> ⚠️ **Rappel critique** – Un **MVP** n’est **pas** une version allégée de V1. C’est le plus petit incrément **capable de valider une ou plusieurs hypothèses** (ex. : adoption du tableau de bord, qualité des données).  

---  

## 2️⃣ Contexte d’usage & positionnement  

| Élément | Détails |
|---------|---------|
| **Produit** | **causalis** – Application Java (Struts 1.x, Castor JDO, Oracle) qui regroupe les accidents du travail et les maladies professionnelles des agents du ministère. |
| **Domaines métier** | Ressources humaines → Santé, action et dialogue social. |
| **Acteurs clés** | - **Gestionnaires** (managers, chefs de service) – utilisent les indicateurs pour piloter la prévention. <br> - **Administrateurs** (MOA/MOE) – configurent les référentiels, assurent la conformité RGPD. <br> - **Développeurs** – maintiennent la stack Java/Struts. |
| **Hypothèses à tester** | 1️⃣ Les gestionnaires consulteront quotidiennement le **tableau de bord** pour prendre des décisions. <br> 2️⃣ Un **export CSV** des statistiques suffit à déclencher l’adoption initiale. <br> 3️⃣ La **qualité des données** (absence de doublons, cohérence des grades) est suffisante avec les contrôles actuels. |
| **Contraintes** | - Stack technologique verrouillée : Java 6, Struts 1.x, Castor JDO, Oracle 11g. <br> - Déploiement sur le centre‑serveur ministériel (Paris La Défense) – aucune modification d’infrastructure possible pendant l’atelier. <br> - Besoin de conformité RGPD (archivage, traçabilité). |
| **Livrables attendus (post‑atelier)** | - Périmètre **MVP** (liste “Must Have”). <br> - Matrice MoSCoW complète. <br> - Roadmap initiale (MVP → V1). <br> - Hypothèses de test + métriques de succès (ex. : taux d’usage ≥ 30 % en 4 semaines). |

---  

## 3️⃣ Pré‑requis indispensables  

| ✅ | Pré‑requis |
|----|------------|
| [ ] | **Vision produit** : pitch, objectifs métier, KPI (ex. : réduction du taux d’accidents de 5 % en 1 an). |
| [ ] | **Story‑mapping** complet (ou au minimum les parcours utilisateurs majeurs : création d’un dossier d’accident, consultation du tableau de bord, export CSV). |
| [ ] | **Personas** détaillés (Gestionnaire, Administrateur, Développeur). |
| [ ] | **Liste des hypothèses** à valider (voir section 2). |
| [ ] | **Contraintes techniques** (Java 6, Struts 1.x, JNDI datasource). |
| [ ] | **Ressources de test** : jeux de données anonymisés (≈ 1 000 dossiers). |
| [ ] | **Décideur** disponible (Chef de produit / PO). |

> 💡 *Si un pré‑requis manque, prévoir 15 min en début d’atelier pour le co‑construire rapidement (ex. : reformuler la vision en 1 phrase).*

---  

## 4️⃣ Parties prenantes & rôles  

| Rôle | Profil type | Responsabilité pendant l’atelier |
|------|-------------|-----------------------------------|
| **Animateur** | Chef de produit / PO | Cadrer, faciliter, garder le focus “apprentissage”. |
| **Développeur senior** | Lead technique Java/Struts | Évaluer faisabilité & effort technique, identifier les dépendances (Castor, Oracle). |
| **MOA / Responsable métier** | Manager Santé/Prévention | Valider la pertinence fonctionnelle, prioriser les indicateurs. |
| **UX / Designer (optionnel)** | Designer UI | Proposer des maquettes légères du tableau de bord (wireframe). |
| **Utilisateur référent (Gestionnaire)** | Responsable de service | Apporter le regard “terrain”, challenger les priorités. |
| **Responsable conformité RGPD** | MOA / SSI | Vérifier que les exigences légales sont prises en compte (archivage, anonymisation). |

> ☝️ *Un même participant peut cumuler plusieurs rôles selon les disponibilités.*

---  

## 5️⃣ Logistique de l’atelier  

| Élément | Détails |
|---------|---------|
| **Durée** | 2 h 30 – 4 h (prévoir une pause à 1 h 30 si > 3 h). |
| **Support physique** | Tableau blanc, post‑its 4 couleurs (Must = rouge, Should = vert, Could = bleu, Won’t = gris), marqueurs, ruban. |
| **Support digital** | Mural / FigJam / Klaxoon – template MoSCoW pré‑chargé, partage du tableau en temps réel. |
| **Livrables immédiats** | - Matrice MoSCoW (tableau partagé). <br> - Périmètre MVP (liste “Must”). <br> - Roadmap MVP → V1 (gantt simplifié). |
| **Enregistrement** | Photos du tableau (ou capture d’écran) + notes partagées dans le repo (`/docs/mvp-workshop`). |

---  

## 6️⃣ Déroulé détaillé de l’atelier  

### 🎯 Étape 1 – Introduction & alignement (15 min)  

1. **Présenter les objectifs** (slide 1).  
2. **Rappel du contexte** : produit, acteurs, hypothèses (slide 2).  
3. **Expliquer MoSCoW** (slide 3) – tableau comparatif des catégories (voir ci‑dessous).  
4. **Formuler la mission du MVP** en 1 phrase :  
   > *« Avec ce MVP, nous voulons vérifier que le tableau de bord d’accidents, disponible en export CSV, permet aux gestionnaires de réduire le taux d’accidents de 5 % en un an. »*  

### 🔍 Étape 2 – Rappel du périmètre fonctionnel (30 min)  

- **Afficher le story‑map** (ou la liste des user‑stories) :  
  1. **Création d’un dossier d’accident** (formulaire, validation).  
  2. **Consultation du tableau de bord** (filtrage, agrégations).  
  3. **Export CSV** des statistiques.  
  4. **Gestion des référentiels** (grades, services, causes).  
- **Pour chaque story**, préciser :  
  - **Besoin utilisateur** (ex. : “voir le nombre d’accidents par service”).  
  - **Hypothèse à tester** (ex. : “l’export CSV suffit à la première adoption”).  
  - **Contraintes** (ex. : “doit fonctionner sous Struts 1.x”, “pas de nouveau composant JS”).  

### 🎚️ Étape 3 – Classification MoSCoW (60‑90 min)  

| Catégorie | Définition | Critère de décision (exemple causalis) |
|-----------|------------|----------------------------------------|
| **M**ust Have | Indispensable pour que le MVP soit viable | - Tableau de bord **consultable** (filtrage par service). <br> - Export **CSV** des indicateurs clés. <br> - Validation de la **qualité des données** (pas de doublons). |
| **S**hould Have | Important mais non critique pour la première validation | - Export **XLS** (en plus du CSV). <br> - Tableau de bord **responsive** (adapté mobile). |
| **C**ould Have | Optionnel, « nice‑to‑have » | - Vue **graphique** (chart JS). <br> - Fonction **d’alerte email** (threshold). |
| **W**on’t Have | Exclu du MVP (pour l’instant) | - Refonte complète du **frontend Struts** (migration Angular). <br> - Intégration **BigData** (Hadoop). |

**Méthode** :  
1. **Présenter chaque story** une à une.  
2. **Questionner** :  
   - *« Le MVP peut‑il fonctionner sans cette fonctionnalité ? »*  
   - *« Quel impact sur l’apprentissage si on l’enlève ? »*  
   - *« Quel effort (jours personne) ? »*  
   - *« Existe‑t‑il un contournement manuel ? »*  
3. **Vote** : chaque participant dispose de **3 votes** (post‑its rouges) à placer sur les items qu’il estime *Must*.  
4. **Placement** : les items avec le plus de votes deviennent **Must**, les suivants **Should**, etc.  
5. **Limiter les Must** : si > 5 items, demander de re‑définir le périmètre (ex. : regrouper plusieurs indicateurs dans un même tableau).  

> 💡 **Règle d’or** : le nombre de *Must* doit être **gérable** (≤ 5 items) pour garantir un **déploiement < 2 semaines**.  

### ✅ Étape 4 – Validation du périmètre MVP (30 min)  

Utiliser la **check‑list** suivante :  

- [ ] Le périmètre *Must* permet de tester **au moins une hypothèse** (ex. : adoption du tableau de bord).  
- [ ] Un **parcours utilisateur complet** existe (ex. : connexion → tableau de bord → export CSV).  
- [ ] Les **contournements** acceptés sont listés (ex. : génération CSV via script batch).  
- [ ] L’**effort estimé** (jours personne) ≤ 10 J/P (déploiement rapide).  
- [ ] Les **métriques de succès** sont définies (ex. : taux d’usage ≥ 30 % en 4 semaines, taux d’erreur < 2 %).  

**Si un point échoue** : revenir à l’étape 3 pour re‑classer ou scinder l’item.  

### 🗺️ Étape 5 – Roadmap & prochaines étapes (15‑30 min)  

1. **Documenter** :  
   - Liste finale des **Must** (MVP).  
   - Justifications (pour traçabilité).  
   - Hypothèses & métriques associées.  
2. **Ébaucher la roadmap** :  

| Phase | Contenu | Date cible |
|------|----------|------------|
| **MVP** | Tableau de bord + export CSV + validation données | **Semaine 1‑2** (déploiement pilote). |
| **V1** | Export XLS, responsive UI, alertes email | **Mois 2‑3**. |
| **V2** | Graphiques dynamiques, API REST, migration vers Spring Boot | **Mois 4‑6**. |

3. **Définir le suivi** : qui pilote les tests utilisateurs, comment collecter les métriques, date de la **revue post‑MVP**.  

> 📸 *Action immédiate* : partager la matrice MoSCoW et la roadmap dans le dépôt (`/docs/mvp`) **dans les 24 h** pour validation écrite.  

---  

## 7️⃣ Conseils de facilitation  

| Bonnes pratiques | À éviter |
|------------------|----------|
| Ancrer chaque décision dans une **hypothèse à tester**. | Décider par préférence personnelle ou « on a toujours fait comme ça ». |
| Challenger systématiquement les **Must** : *« Et si on l’enlevait ? »* | Accepter un MVP trop large par peur de décevoir. |
| Proposer des **contournements légers** (script batch, export manuel). | Confondre « faisable techniquement » avec « nécessaire pour l’apprentissage ». |
| Faire participer activement les **gestionnaires** (utilisateurs finaux). | Laisser un seul profil (technique ou métier) dominer les arbitrages. |
| Documenter les **Won’t** avec leurs raisons (évite les retours ultérieurs). | Oublier de prévoir la revue post‑MVP et les critères de succès. |

---  

## 8️⃣ Alternative : MVP par **scénario utilisateur complet**  

| Critère de sélection du scénario MVP | Exemple concret (causalis) |
|---------------------------------------|----------------------------|
| **Parcours complet mais borné** | *« En tant que Gestionnaire, je veux consulter le tableau de bord d’accidents par service et exporter les résultats en CSV, même si l’export XLS n’est pas disponible. »* |
| **Forte innovation à tester** | *« Tester l’intégration d’un nouveau référentiel de grades (TranscodageGrade) via le service WS. »* |
| **Simplicité de mise en œuvre** | Utiliser le **script SQL** déjà présent (`20200116-causalis-1.6.sql`) pour préparer les données de test. |
| **Valeur d’apprentissage maximale** | Valider que le tableau de bord influence les décisions de prévention (mesure via questionnaire). |

> 💡 *Formuler le scénario MVP comme une user‑story élargie :*  
> **« En tant que [Gestionnaire], je veux [voir le tableau de bord d’accidents et exporter les données en CSV] afin de [prendre des décisions de prévention rapidement] ».**  

---  

## 9️⃣ Diagramme Mermaid du processus de définition du MVP (MoSCoW)

```mermaid
graph TB;
    %% Acteurs;
    pm[👤 Chef de produit]
    dev[👤 Lead technique]
    biz[👤 Responsable métier]
    ux[👤 Designer (opt.)]
    user[👤 Gestionnaire référent]

    %% Phase 1 - Pré‑préparation;
    subgraph prep["Phase 1 – Pré‑préparation"]
        ctx[Contexte (product, personas, hypothèses)]
        story[Story‑mapping / parcours]
    end;
    %% Phase 2 - Atelier;
    subgraph workshop["Phase 2 – Atelier MoSCoW"]
        intro[Intro & objectifs]
        remind[ rappel périmètre fonctionnel]
        classify[Classification MoSCoW]
        validate[Validation périmètre MVP]
        roadmap[Roadmap & prochaines étapes]
    end;
    %% Phase 3 - Livrables;
    subgraph deliver["Phase 3 – Livrables & suite"]
        matrix[Matrice MoSCoW<br/>validée]
        scope[Périmètre MVP<br/>(Must Have)]
        plan[Roadmap MVP → V1]
        metrics[Hypothèses + métriques]
    end;
    %% Phase 4 - Boucle d’apprentissage;
    subgraph loop["Phase 4 – Boucle d’apprentissage"]
        test[Tests utilisateurs<br/>MVP]
        analyse[Analyse des retours]
        decide[Décision : persévérer / pivoter / arrêter]
    end;
    %% Flux;
    pm -->|Cadrage| ctx;
    dev -->|Apports techniques| ctx;
    biz -->|Besoins métier| ctx;
    ux -->|Wireframes (opt.)| ctx;
    ctx --> story;
    story --> intro;
    intro --> remind;
    remind --> classify;
    classify --> validate;
    validate --> scope;
    scope --> matrix;
    matrix --> roadmap;
    roadmap --> plan;
    plan --> test;
    test --> analyse;
    analyse --> decide;
    decide -->|MVP OK| deliver;
    decide -->|MVP insuffisant| prep;
    %% Styles;
    classDef role fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phase fill:#90EE90,stroke:#2E7D32,stroke-width_2px;
    classDef deliver fill:#FFFFE0,stroke:#F57C00,stroke-width_2px;
    classDef loop fill:#E6E6FA,stroke:#7B1FA2,stroke-width_2px;
    class pm,dev,biz,ux,user role;
    class prep,workshop,deliver,loop phase;
```

---  

## 10️⃣ Adaptations contextuelles  

| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Refonte d’un produit existant** | Partir des points de friction actuels (ex. : lenteur du tableau de bord, export limité) pour identifier les *Must* qui résolvent les blocages majeurs. |
| **Produit fortement réglementé** | Intégrer les exigences RGPD comme *Must* (ex. : anonymisation, archivage). Les contraintes légales peuvent être **Won’t** si elles ne sont pas nécessaires pour la première validation. |
| **Multi‑personas utilisateurs** | Prioriser le **Gestionnaire** (principal acteur) pour le MVP ; les autres personas (développeur, admin) seront **Should** ou **Could**. |
| **Contraintes de délai très court** | Cibler un **scénario MVP** unique (tableau de bord + export CSV) et accepter des contournements manuels (ex. : génération de CSV via script). |
| **Innovation à fort risque** | Prioriser la validation de l’**export CSV** (low risk) avant la mise en place du **nouveau référentiel de grades** (high risk). |

---  

## 11️⃣ Livrables & intégration continue  

| Livrable immédiat | Description |
|-------------------|-------------|
| **Matrice MoSCoW** | Tableau Excel / Google Sheet avec les colonnes Must / Should / Could / Won’t + estimations d’effort. |
| **Périmètre MVP** | Document (Markdown) listant les *Must* avec description fonctionnelle et critères d’acceptation. |
| **Roadmap** | Gantt simplifié (ex. : GitLab Milestones) du MVP → V1 → V2. |
| **Hypothèses & métriques** | Table de suivi (ex. : KPI : taux d’usage, taux d’erreur, temps de génération CSV). |
| **Backlog produit** | Issues GitLab taggées `MVP`, `Should`, `Could`. |
| **Plan de test MVP** | Scénario de test utilisateur (script, questionnaire). |
| **Template de revue post‑MVP** | Checklist décisionnelle (persévérer / pivoter / arrêter). |

### Prochaines étapes suggérées  

1. **Créer la branche `mvp/initial`** et y placer le backlog filtré (only Must).  
2. **Développer le tableau de bord** (Struts Action + JSP) et l’export CSV (service `ExportService`).  
3. **Déployer en environnement de test** (centre‑serveur ministériel – même JNDI).  
4. **Lancer les tests utilisateurs** (2 semaines) et collecter les métriques.  
5. **Organiser la revue MVP** (date fixée : + 4 semaines).  

---  

## 📚 Mini‑glossaire  

| Acronyme | Signification |
|----------|----------------|
| **MVP** | Minimum Viable Product – version minimale destinée à **valider une hypothèse**. |
| **MoSCoW** | Priorisation : **M**ust, **S**hould, **C**ould, **W**on’t. |
| **PO** | Product Owner – responsable du backlog produit. |
| **MOA** | Maîtrise d’Ouvrage – partie métier. |
| **MOE** | Maîtrise d’Œuvre – partie technique. |
| **RGPD** | Règlement Général sur la Protection des Données. |
| **JNDI** | Java Naming and Directory Interface – source de données. |
| **DAO** | Data Access Object – couche d’accès aux données. |
| **SSI** | Sécurité des Systèmes d’Information. |

---  

## ✅ Checklist finale avant de clôturer l’atelier  

- [ ] Vision produit reformulée en 1 phrase.  
- [ ] Story‑mapping affiché et compris par tous.  
- [ ] Tous les items ont été classés MoSCoW.  
- [ ] Le nombre de **Must** ≤ 5 et l’effort total ≤ 10 J/P.  
- [ ] La **check‑list MVP** (section 4) est remplie.  
- [ ] La **roadmap** MVP → V1 est dessinée.  
- [ ] Les **hypothèses & métriques** sont listées.  
- [ ] Les livrables (matrice, périmètre, roadmap) sont partagés dans le repo.  

🚀 **Le MVP est maintenant défini !** Vous disposez d’un périmètre clair, d’une roadmap et de critères d’apprentissage pour lancer rapidement le premier incrément. Bonne livraison !  