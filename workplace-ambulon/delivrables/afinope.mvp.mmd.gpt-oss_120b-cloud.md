# 📚 Guide d’atelier : Définir le MVP du produit **afinope** avec la méthode MoSCoW  

> **Document établi à partir des principes du MVP (Lean Startup) et de la méthode de priorisation MoSCoW**  

---  

## 📖 Table des matières  
[TOC]

---  

## 1️⃣ Introduction et objectifs  

**Objectif global** : « Définir collectivement le périmètre du Produit Minimum Viable pour tester les hypothèses produit d’**afinope** avec un effort maîtrisé. »  

**Méthodologie** : Atelier combinant le cadre **MVP (Lean Startup)** et la priorisation **MoSCoW** (Must / Should / Could / Won’t).  

### Objectifs opérationnels  

| 🎯 | Description |
|---|---|
| **Clarifier la mission du MVP** | Quelle hypothèse testons‑nous ? Quelle donnée ou quel processus voulons‑nous valider ? |
| **Identifier les fonctionnalités indispensables** | Séparer les *Must* des *Should / Could* afin de limiter le scope. |
| **Aligner les équipes** | Produit, métier, technique et design s’accordent sur un périmètre réaliste. |
| **Livrer vite, apprendre, itérer** | Créer un incrément exploitable rapidement, puis mesurer les retours. |
| **Préparer la roadmap post‑MVP** | Définir les suites logiques (V1, itérations…) dès le départ. |

> ⚠️ **Rappel critique** : Un MVP n’est **pas** une V1 allégée. C’est le plus petit ensemble d’interactions capable de **valider** une hypothèse, même avec des contournements manuels ou des jeux de données factices.  

---  

## 2️⃣ Contexte d’usage et positionnement  

| Élément | Détails |
|---|---|
| **Produit** | **afinope** – Application financière des opérateurs de l’État (gestion de flux CSV, stockage dans PostgreSQL, visualisation Superset). |
| **Domaines métier** | Finances publiques, contrôle budgétaire, reporting exécutif. |
| **Quand l’utiliser** | <ul><li>Après la phase de recherche utilisateur (interviews, études de besoins).</li><li>Une fois le **Story Map** ou le backlog épique établi (ex. : ingestion CSV → validation → stockage → tableau de bord).</li><li>Avant le lancement du développement du premier incrément. </li></ul> |
| **Cas d’usage typiques** | <ul><li>Lancement d’un nouveau service de dépôt de données financières.</li><li>Refonte d’un processus de contrôle budgétaire existant.</li><li>Test d’une hypothèse à fort risque (ex. : “l’automatisation de la validation CSV réduit le temps de traitement de 50 %”).</li><li>Réduction de périmètre pour respecter un délai de mise en production. </li></ul> |

---  

## 3️⃣ Pré‑requis indispensables  

> ✅ **Note** : Si un pré‑requis manque, allouer 10‑20 min en début d’atelier pour le co‑construire.  

- [ ] **Vision produit formalisée** – Pitch, objectifs métier, indicateurs de succès (ex. : temps moyen de traitement, taux d’erreur de validation).  
- [ ] **Hypothèses à tester** – Liste claire (ex. : “L’import CSV automatisé diminue les erreurs de saisie de 30 %”).  
- [ ] **Story Mapping** – Parcours utilisateur complet (ex. : *Déposer un fichier → Valider → Visualiser le tableau de bord*).  
- [ ] **Personas** – Au minimum : <ul><li>**Analyste Financier** (utilise les tableaux de bord). </li><li>**Data Engineer** (déploie les pipelines). </li><li>**Responsable de contrôle** (valide la conformité). </li></ul>  
- [ ] **Contraintes identifiées** – Techniques (PostgreSQL, DAGster), réglementaires (RGPD, normes comptables), budgetaires, délais.  

---  

## 4️⃣ Parties prenantes et rôles  

| Rôle | Profil type | Responsabilité dans l’atelier |
|------|-------------|--------------------------------|
| **Animateur** | Chef de produit / PNM | Cadre, facilitation, garde du focus « apprentissage » |
| **Profil technique** | Tech Lead / Architecte | Évaluer faisabilité, effort, dépendances (ex. : connexion DB, Docker). |
| **Porteur métier** | MOA / Responsable financier | Valider la pertinence fonctionnelle, valeur utilisateur. |
| **Designer UX/UI** *(optionnel)* | Designer produit | Proposer des alternatives légères, vérifier expérience minimale. |
| **Utilisateur référent** *(optionnel)* | Analyste financier | Apporter le regard « usage réel », challenger les priorités. |

> ☝️ **Astuce** : Un même collaborateur peut cumuler plusieurs rôles si les compétences le permettent.  

---  

## 5️⃣ Logistique de l’atelier  

- **Durée** : 2 h 30 – 4 h (pause à 1 h 30 si > 3 h).  
- **Matériel**  
  - *Physique* : tableau blanc, post‑its 4 couleurs (M / S / C / W), marqueurs, ruban masking.  
  - *Digital* : Miro / FigJam / Mural avec template MoSCoW pré‑préparé.  
- **Livrables attendus**  
  - Périmètre MVP validé.  
  - Matrice MoSCoW (liste fonctionnelle + justification).  
  - Roadmap initiale (MVP → V1 → itérations).  
  - Hypothèses de test + métriques de succès.  

---  

## 6️⃣ Déroulé détaillé de l’atelier  

### 🎯 Étape 1 — Introduction & alignement (15 min)  

1. **Présenter les objectifs du MVP**  
   - « Avec ce MVP, nous voulons vérifier que **[hypothèse]** en observant **[métrique]** auprès de **[persona]**. »  
2. **Rappel du contexte** – personas, hypothèses, contraintes.  
3. **Expliquer MoSCoW** (voir tableau ci‑dessous).  

| Catégorie | Définition | Critère de décision |
|-----------|------------|---------------------|
| **Must** | Indispensable pour que le MVP soit viable | Sans cela, le produit est inutile ou l’hypothèse non testable |
| **Should** | Important mais non critique | Valeur ajoutée significative, mais reportable sans bloquer |
| **Could** | Optionnel, “nice‑to‑have” | Améliore l’expérience mais n’impacte pas l’apprentissage |
| **Won’t** | Exclu du MVP (pour l’instant) | Trop coûteux, hors scope, ou non prioritaire pour l’apprentissage |

> ✅ **Action** : Formuler la mission du MVP en 1 phrase et l’afficher.  

### 🔍 Étape 2 — Rappel du périmètre fonctionnel (30 min)  

- Afficher le **Story Map** (ex. : *Déposer CSV → Valider → Stocker → Visualiser tableau de bord*).  
- Pour chaque étape, préciser :  
  1. **Besoin utilisateur** (ex. : “Je veux déposer mon fichier de flux comptable”).  
  2. **Hypothèse testée** (ex. : “L’automatisation de la validation réduit le temps de traitement”).  
  3. **Contraintes** (ex. : format CSV strict, conformité aux normes comptables).  
- Regrouper, éliminer les doublons.  

### 🎚️ Étape 3 — Classification MoSCoW (60‑90 min)  

1. **Présenter chaque fonctionnalité/épique** (ex. : *Gestionnaire de fichiers CSV*, *Gestionnaire base de données*, *Pipeline DAGster*, *Dashboard Superset*).  
2. **Discussion guidée** – poser les questions :  
   - *« Le MVP peut‑il fonctionner sans cette fonctionnalité ? »*  
   - *« Quel impact sur l’apprentissage si on la retire ? »*  
   - *« Quel effort technique / délai ? »*  
   - *« Existe‑t‑il un contournement simple (ex. : fichier CSV manuel) ? »*  
3. **Vote ou consensus**  
   - **Dot‑Voting** : chaque participant reçoit 3 votes à placer sur les « Must » potentiels.  
   - **Débat structuré** : un participant propose une catégorie, les autres valident ou challengent.  
4. **Placement** : coller chaque fonctionnalité dans la colonne MoSCoW correspondante (post‑its ou cartes digitales).  

> 💡 **Règle d’or** : Limiter les *Must* à l’essentiel absolu ; si tout est *Must*, rien n’est priorisé.  

### ✅ Étape 4 — Validation du périmètre MVP (30 min)  

Utiliser la **check‑list** suivante :  

- [ ] Le périmètre MVP permet‑il de tester **au moins une hypothèse** clairement définie ?  
- [ ] Un utilisateur peut‑il accomplir **un parcours complet** (ex. : déposer, valider, voir tableau) ?  
- [ ] Les **contournements acceptés** (ex. : validation manuelle) sont identifiés.  
- [ ] L’**effort estimé** est compatible avec le délai cible du MVP.  
- [ ] Les **métriques de succès** (ex. : temps moyen de traitement < 5 min) sont définies.  

**Si le périmètre est trop large** → revisiter les *Must* et re‑déplacer en *Should* ou *Could*.  
**Si trop léger** → vérifier qu’aucune hypothèse critique n’a été oubliée.  

### 🗺️ Étape 5 — Roadmap & prochaines étapes (15‑30 min)  

1. **Documenter les décisions**  
   - Liste finale des *Must* (périmètre MVP).  
   - Justifications (pour traçabilité).  
   - Hypothèses de test associées.  
2. **Ébaucher la roadmap**  

| Phase | Contenu |
|------|---------|
| **MVP** | Must + contournements, date cible, métriques. |
| **V1** | Priorité *Should* (ex. : tableau de bord complet, alertes automatisées). |
| **Backlog** | *Could* + idées futures. |
| **Review post‑MVP** | Décider pivot / persévérer / arrêter. |
| **Itération suivante** | Re‑planifier selon les retours. |
3. **Définir le suivi**  
   - Responsable du test utilisateur (ex. : analyste financier).  
   - Processus de collecte & analyse des retours (tableau de bord KPI).  
   - Date de la revue post‑MVP.  

> 📸 **Action immédiate** : Partager la matrice MoSCoW et la roadmap brouillon dans les 24 h (ex. : via Confluence ou Notion).  

---  

## 7️⃣ Conseils de facilitation  

| Bonnes pratiques | À éviter |
|------------------|----------|
| Ancrer chaque décision dans une **hypothèse à tester**. | Prioriser par préférence personnelle ou “on a toujours fait comme ça”. |
| Challenger systématiquement les *Must* : *« Et si on l’enlevait ? »* | Accepter un MVP trop large par peur de décevoir. |
| Proposer des **contournements légers** (ex. : validation manuelle, jeux de données factices). | Confondre “faisable techniquement” avec “nécessaire pour l’apprentissage”. |
| Faire participer activement **métiers & utilisateurs**. | Laisser un seul profil (tech ou métier) dominer les arbitrages. |
| Documenter les **“Won’t Have”** avec leurs raisons (pour éviter les re‑demandes). | Oublier de prévoir la revue post‑MVP et les critères de succès. |

---  

## 8️⃣ Alternative : MVP par scénario utilisateur  

Lorsque la méthode MoSCoW ne suffit pas à réduire le scope, privilégier un **scénario utilisateur complet** :  

| Critère de sélection du scénario MVP | Exemple concret (afinope) |
|--------------------------------------|--------------------------|
| **Parcours complet mais borné** | *Déposer un fichier CSV de flux comptable → Validation manuelle → Visualisation d’un tableau synthétique* (le traitement back‑office reste manuel). |
| **Forte innovation à tester** | Nouvelle interface de **détection d’anomalies** : on teste l’UX avant d’intégrer le moteur d’analyse. |
| **Simplicité de mise en œuvre** | Parcours ne nécessitant pas de jointure avec les tables de référence ; on utilise des jeux de données de test. |
| **Valeur d’apprentissage maximale** | Scénario qui valide l’hypothèse la plus risquée (ex. : “l’automatisation de la validation CSV diminue le temps de traitement de 50 %”). |

> 💡 **Formulation** : *« En tant que **[persona]**, je veux **[action complète]** afin de **[bénéfice]**, même si **[contournement accepté]** ».  

---  

## 9️⃣ Diagramme Mermaid du processus de définition du MVP  

```mermaid
graph TB;
    %% Acteurs;
    pm[👤 Chef de produit]
    tech[👤 Profil technique]
    business[👤 Porteur métier]
    user[👤 Utilisateur référent]

    %% Phase 1 – Pré‑préparation;
    subgraph prep[" Phase 1 – Pré‑préparation "]
        vision[Vision produit & hypothèses]
        story[Story Mapping / backlog]
        constraints[Contraintes (tech, légales, budget)]
    end;
    %% Phase 2 – Atelier;
    subgraph workshop[" Phase 2 – Atelier MoSCoW "]
        align[Alignement : objectifs MVP]
        map[Recall du périmètre fonctionnel]
        classify[Classification MoSCoW]
        validate[Validation du périmètre MVP]
    end;
    %% Phase 3 – Livrables;
    subgraph deliver[" Phase 3 – Livrables & suite "]
        matrix[Matrice MoSCoW validée]
        roadmap[Roadmap MVP → V1 → itérations]
        metrics[Hypothèses de test & métriques]
    end;
    %% Phase 4 – Boucle d’apprentissage;
    subgraph loop[" Phase 4 – Boucle d’apprentissage "]
        test[Tests utilisateurs du MVP]
        learn[Analyse des retours & apprentissages]
        decide[Décision : pivoter / persévérer / arrêter]
    end;
    %% Flux principaux;
    pm -->|Cadrage| vision;
    tech -->|Spécifications| story;
    business -->|Contraintes| constraints;
    constraints -->|Démarrage atelier| align;
    align --> map;
    map --> classify;
    classify --> validate;
    validate --> matrix;
    matrix --> roadmap;
    roadmap --> test;
    test --> learn;
    learn --> decide;
    decide -.->|Itération suivante| vision;
    %% Liens vers notes;
    classify -.-> note1;
    validate -.-> note2;
    loop -.-> note3;
    %% Styles;
    classDef phasePrep fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phaseWorkshop fill:#C8E6C9,stroke:#2E7D32,stroke-width_2px;
    classDef phaseDeliver fill:#FFF9C4,stroke:#F57C00,stroke-width_2px;
    classDef phaseLoop fill:#F3E5F5,stroke:#7B1FA2,stroke-width_2px;
    classDef actor fill:#E1F5FE,stroke:#0288D1,stroke-width_2px;
    classDef noteStyle fill:#FAFAFA,stroke:#BDBDBD,stroke-dasharray_5 5;

    class vision,story,constraints phasePrep;
    class align,map,classify,validate phaseWorkshop;
    class matrix,roadmap,metrics phaseDeliver;
    class test,learn,decide phaseLoop;
    class pm,tech,business,user actor;
    class note1,note2,note3 noteStyle;

    note1["📋 MoSCoW : Must = indispensable, Should = important, Could = optionnel, Won’t = exclu."]
    note2["✅ Checklist MVP : hypothèse testable, parcours complet, contournement, effort, métriques."]
    note3["🔄 Lean : Build → Measure → Learn – le MVP est un outil d’apprentissage, pas une version finale."]
```

---  

## 🔟 Adaptations contextuelles  

| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Refonte d’un produit existant** | Partir des points de friction (ex. : erreurs de validation CSV) pour identifier les *Must* qui résolvent les blocages majeurs. |
| **Produit fortement réglementé** | Intégrer les exigences légales comme *Must* uniquement si elles bloquent l’hypothèse ; sinon prévoir des **contournements documentés** (ex. : jeu de données de test conforme). |
| **Multi‑personas** | Choisir un **persona prioritaire** (ex. : analyste financier) pour le MVP ; couvrir les besoins des autres dans les *Should*/*Could*. |
| **Contrainte de délai très court** | Cibler **un seul scénario complet** (déposer CSV → tableau synthétique) avec des contournements manuels en back‑office. |
| **Innovation à fort risque** | Prioriser les fonctionnalités qui valident l’hypothèse la plus incertaine, même si le parcours est partiel. |

---  

## 1️⃣1️⃣ Livrables et intégration continue  

| Livrable immédiat | Description |
|-------------------|-------------|
| **Matrice MoSCoW** | Tableau listant chaque fonctionnalité avec sa catégorie et justification. |
| **Périmètre MVP** | Liste des *Must* + contournements acceptés. |
| **Roadmap initiale** | MVP → V1 → itérations, avec jalons temporels. |
| **Hypothèses de test & métriques** | Ex. : “Temps moyen de traitement < 5 min”, “Taux d’erreur < 2 %”. |
| **Backlog produit structuré** | Épics → user stories taggées MoSCoW. |
| **Plan de test utilisateur** | Recrutement, scénarios, collecte de données. |
| **Template de revue post‑MVP** | Critères de décision (pivot / persévérer / arrêter). |

### Prochaines étapes suggérées  

1. **Rédaction des user stories MVP** (inclure critères d’acceptation).  
2. **Maquettage des écrans clés** (déposer CSV, tableau de bord simplifié).  
3. **Estimation technique** (effort, dépendances, story points).  
4. **Planification des sprints** (début du développement MVP).  
5. **Préparation du protocole de test** (recrutement analystes, métriques).  

---  

## 📚 Mini‑glossaire  

| Acronyme / Terme | Définition |
|------------------|------------|
| **MVP** | Minimum Viable Product – version la plus petite permettant de valider une hypothèse. |
| **MoSCoW** | Méthode de priorisation : Must, Should, Could, Won’t. |
| **Story Map** | Visualisation du parcours utilisateur découpé en activités & sous‑tâches. |
| **Persona** | Représentation synthétique d’un groupe d’utilisateurs cibles. |
| **Hypothèse produit** | Pari à tester (ex. : “l’automatisation réduit le temps de traitement”). |
| **Pivot** | Changement de direction suite à l’échec d’une hypothèse. |
| **Backlog** | Liste priorisée des besoins fonctionnels et non fonctionnels. |
| **DAGster** | Orchestrateur de pipelines de données (utilisé dans afinope). |
| **Superset** | Outil de visualisation de données (tableaux de bord). |

---  

## 🔚 Conclusion  

Cet atelier vous fournit un cadre complet pour **définir, prioriser et livrer** le MVP d’**afinope** en s’appuyant sur la méthode MoSCoW. En suivant le déroulé proposé, vous obtiendrez :  

1. Un périmètre clairement **aligné** sur les hypothèses critiques.  
2. Une **roadmap** qui évite le piège du “MVP trop large”.  
3. Un plan d’**apprentissage** (tests, métriques) permettant de décider rapidement de la suite.  

Bonne facilitation ! 🚀  