# 📘 Guide d’atelier : Définition du MVP (Minimum Viable Product) avec la méthode MoSCoW  
*Produit : **SIREINES** – Répertoire national des experts et spécialistes*  

---  

## 📑 Table des matières  
[TOC]

---  

## 1️⃣ Introduction & objectifs  

**Objectif principal** : *« Définir collectivement le périmètre du Produit Minimum Viable (MVP) afin de tester les hypothèses clés du produit SIREINES avec un effort maîtrisé. »*  

**Méthodologie** : Atelier + MVP (Lean Startup) + Priorisation MoSCoW (Must / Should / Could / Won’t).  

### 🎯 Objectifs opérationnels  

| 🎯 | Description |
|---|-------------|
| **Clarifier la mission du MVP** | Quel apprentissage visons‑nous ? (ex. validation du processus d’import / de qualification / des rapports BIRT). |
| **Identifier les fonctionnalités indispensables** | Séparer les *Must‑have* (indispensables) des *Should/Could/Won’t* (report‑offs). |
| **Aligner les équipes** | Produit, Métier, Technique – même vision du périmètre et des contraintes. |
| **Éviter le “tunnel”** | Livrer vite, mesurer, itérer. |
| **Poser les bases de la roadmap post‑MVP** | Quelle suite logique après le MVP ? |

> ⚠️ **Rappel critique** : Un MVP n’est **pas** une V1 allégée. C’est le **plus petit produit capable d’apporter un apprentissage** (ex. un parcours utilisateur complet, même avec des contournements manuels ou des données factices).  

---  

## 2️⃣ Contexte d’usage & positionnement  

| **Type de livrable** | **Nature** | **Quand l’utiliser** |
|----------------------|------------|----------------------|
| **Déploiement SIREINES** | Application Web + BIRT + PostgreSQL | Après la phase de recherche utilisateur et la création du story‑map. |
| **MVP** | Sub‑set fonctionnel du produit (ex. import + qualification + rapport BIRT) | Avant le lancement de la version **2.5.20** (prod 12/03/2024) pour tester les nouvelles règles de qualification. |
| **Pre‑prod / Recette / Prod** | Environnements distincts (recette, pre‑prod, prod) | Le MVP sera d’abord déployé en **recette** (URL `http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/`). |

### Principaux **hypothèses à tester** (exemples tirés du backlog)  

| # | Hypothèse | Métrique de succès |
|---|-----------|---------------------|
| H1 | *L’import d’un fichier *.csv via le module “Import Fichier”* est fiable à ≥ 95 % (taux d’erreurs < 5 %). | % de dossiers importés sans erreur. |
| H2 | *Le workflow de qualification (début → fin) peut être réalisé en < 5 min* par un agent. | Temps moyen de traitement d’un dossier. |
| H3 | *Les rapports BIRT (extraction 05, 08, 10) se génèrent en < 30 s*. | Durée de génération du PDF. |
| H4 | *Le système d’envoi de mail (notification) fonctionne avec le compte générique `sireines@...`*. | Taux de mails délivrés (bounce = 0 %). |
| H5 | *Un utilisateur (agent) peut consulter son tableau de bord en < 2 clics*. | Nombre de clics moyen. |

> **À vous** : remplacez, ajoutez ou retirez les hypothèses en fonction de votre story‑map actuelle (voir le fichier `sireines‑database/script/…` ou votre backlog JIRA).  

---  

## 3️⃣ Parties prenantes & rôles  

| Rôle | Profil type | Responsabilité dans l’atelier |
|------|-------------|------------------------------|
| **Animateur** | Chef de produit / PO | Faciliter, garder le focus “apprentissage”. |
| **Profil technique** | Lead dev, architecte, DBA | Évaluer faisabilité, effort, dépendances (Docker, PostgreSQL, BIRT). |
| **Porteur métier** | MOA / Chef de bureau (ex. Vincent Letrouit) | Valider pertinence fonctionnelle & conformité RGPD. |
| **Designer UX/UI** (optionnel) | Designer produit | Proposer des maquettes légères (pages “Import”, “Dashboard”). |
| **Utilisateur référent** (optionnel) | Agent SIREINES (ex. expert) | Apporter le regard “usage réel”, challenger les priorités. |

> 📌 *NB : plusieurs rôles peuvent être cumulés selon les disponibilités.*  

---  

## 4️⃣ Logistique de l’atelier  

| Élément | Détails |
|--------|---------|
| **Durée** | 2 h 30 – 4 h (prévoir pause à 1 h 30 si > 3 h). |
| **Matériel** | Tableau blanc / Post‑its 4 couleurs (M / S / C / W), marqueurs, projecteur. <br>Support numérique : Mural / FigJam / Miro **pré‑préparé** avec le template MoSCoW. |
| **Livrables** | Matrice MoSCoW + périmètre *Must‑have* (MVP), justification, roadmap MVP → V1, hypothèses + métriques. |
| **Suivi** | Responsable désigné (ex. Chef de produit) qui crée le ticket JIRA “MVP SIREINES – [date]”. |  

---  

## 5️⃣ Déroulé détaillé de l’atelier  

### 5.1 Étape 1 — Introduction & alignement (15 min)  

1. **Présenter** l’objectif du MVP (apprentissage).  
2. **Rappeler** le contexte SIREINES (mission, sites, version 2.5.20, architecture Docker).  
3. **Formuler** la mission du MVP en 1 phrase :  
   > *« Avec ce MVP, nous voulons vérifier que l’import d’un fichier CSV et la génération du rapport BIRT fonctionnent correctement, afin de réduire le temps de qualification de 30 % ».*
4. **Expliquer** la méthode MoSCoW (tableau ci‑dessous).  

| Catégorie | Définition | Critère de décision |
|-----------|------------|---------------------|
| **Must**   | Indispensable pour que le MVP soit viable | Sans cela le produit ne peut pas répondre à l’hypothèse. |
| **Should** | Important mais non critique | Reportable sans bloquer l’apprentissage. |
| **Could**  | Optionnel, “nice‑to‑have” | Améliore l’expérience mais pas l’apprentissage. |
| **Won’t**  | Exclu du MVP (pour le moment) | Trop coûteux, hors périmètre ou non prioritaire. |

---  

### 5.2 Étape 2 — Rappel du périmètre fonctionnel (30 min)  

*Afficher le **story‑map** (ou la liste d’épics) :*

| Épic | User Story (exemple) | Hypothèse associée |
|------|----------------------|--------------------|
| **Import Fichier** | En tant qu’**agent**, je veux importer un CSV de dossiers pour les créer automatiquement. | H1 |
| **Qualification** | En tant qu’**expert**, je veux valider un dossier en 5 min. | H2 |
| **Rapports BIRT** | En tant qu’**agent**, je veux télécharger le rapport “Population qualifiée”. | H3 |
| **Notifications** | En tant qu’**agent**, je reçois un mail lorsqu’un dossier change d’état. | H4 |
| **Dashboard** | En tant qu’**agent**, je vois mon tableau de bord en 2 clics. | H5 |

*Si vous avez déjà un story‑map dans votre repo (ex. `/sireines‑web/src/main/resources/...`), ouvrez‑le et parcourez les épics.*  

---  

### 5.3 Étape 3 — Classification MoSCoW (60‑90 min)  

**Processus**  

1. **Présenter chaque fonctionnalité** (épic / user‑story).  
2. **Questionner** :  
   - *Le MVP peut‑il fonctionner sans ?*  
   - *Quel impact sur l’apprentissage ?*  
   - *Quel effort ?* (Docker, BIRT, DB scripts)  
   - *Existe‑t‑il un contournement simple ?* (ex. import manuel, données factices).  
3. **Vote / consensus** :  
   - *Option A : Dot‑Voting* – chaque participant dispose de 3 votes à distribuer sur les “Must”.  
   - *Option B : Débat structuré* – un·e champion·ne propose la catégorie, le groupe valide ou challenge.  
4. **Placer** chaque fonctionnalité dans la colonne correspondante (tableau ci‑dessous).  

| Fonctionnalité | MoSCoW | Justification |
|-----------------|--------|---------------|
| Import Fichier (CSV) | **Must** | Hypothèse H1 ; besoin de tester la fiabilité du processus d’import. |
| Qualification (workflow) | **Must** | Hypothèse H2 ; cœur du produit, mesure du temps de traitement. |
| Rapport BIRT 05 | **Should** | Valeur ajoutée, mais on peut valider le workflow sans le rapport complet. |
| Rapport BIRT 08 (pyramide d’âge) | **Could** | Nice‑to‑have, pas indispensable pour le premier apprentissage. |
| Notification mail | **Should** | Vérifier la chaîne d’alerte, mais on peut la simuler. |
| Dashboard (2‑clic) | **Could** | Améliore l’expérience, non critique pour l’apprentissage. |
| Export CSV des résultats | **Won’t** | Pas besoin pour le MVP, à planifier ultérieurement. |
| Gestion des droits (Cerbère) | **Won’t** | Déjà en place, hors scope du MVP. |

*(Adaptez ce tableau en fonction de vos épics et de votre backlog.)*  

---  

### 5.4 Étape 4 — Validation du périmètre MVP (30 min)  

Utilisez la **check‑list** suivante :  

- [ ] Le périmètre *Must* permet de tester **au moins une hypothèse** clairement définie.  
- [ ] Un parcours utilisateur complet (ex. Import → Qualification → Rapport) est réalisable.  
- [ ] Les contournements (ex. données factices, import manuel) sont identifiés.  
- [ ] L’effort estimé (temps de dev, tests, Docker) est compatible avec le délai cible (ex. 2 semaines).  
- [ ] Les métriques de succès (taux d’erreurs, temps de traitement) sont définies.  

**Si le périmètre est trop large** : réduire les *Must* en re‑évaluant les hypothèses.  
**Si le périmètre est trop mince** : vérifier qu’aucune hypothèse clé n’est exclue.  

---  

### 5.5 Étape 5 — Roadmap & prochaines étapes (15‑30 min)  

| Livrable | Contenu | Responsable | Date cible |
|----------|---------|------------|-----------|
| **Matrice MoSCoW** | Tableaux *Must/Should/Could/Won’t* + justifications | Animateur | Fin d’atelier |
| **Périmètre MVP** | Liste *Must* + critères d’acceptation | PO | +1 jour |
| **Plan de test** | Scénario “Import → Qualification → Rapport”, métriques, jeux de données | QA | +3 jours |
| **Roadmap** | *Must* → MVP (Semaine 1‑2) → *Should* → V1 (Semaine 3‑4) | PO + Tech Lead | +1 semaine |
| **Revue post‑MVP** | Analyse des métriques, décision (pivot / persévérer / arrêter) | Comité produit | Fin Sprint 2 |

---  

## 6️⃣ Conseils de facilitation  

| Bonnes pratiques | À éviter |
|------------------|----------|
| Ancrer chaque décision dans **une hypothèse** à tester. | Décider par “c’est comme avant” ou “c’est trop long”. |
| Challenger systématiquement les *Must* : *“Et si on l’enlevait ?”* | Accepter un MVP trop large par peur de décevoir. |
| Proposer des **contournements légers** (ex. données CSV factices, import manuel). | Confondre “facile à développer” avec “indispensable”. |
| Faire participer **les profils métier** (agents, experts). | Laisser la décision à un seul profil (ex. technique). |
| Documenter **les “Won’t”** avec leurs raisons (pour éviter les retours). | Oublier la revue post‑MVP et les critères de succès. |

---  

## 7️⃣ Alternative : MVP par **scénario utilisateur**  

Lorsque la méthode MoSCoW conduit à trop de *Must*, privilégiez un **scénario complet** :  

| Critère de sélection du scénario | Exemple SIREINES |
|--------------------------------|-------------------|
| **Parcours complet mais borné** | *Import CSV → Qualification → Génération du rapport BIRT 05*. |
| **Innovation à forte risque** | *Nouvelle interface d’import “drag‑and‑drop”*. |
| **Facilité de mise en œuvre** | *Utiliser le conteneur `sireines‑pgadmin_container` déjà présent*. |
| **Valeur d’apprentissage maximale** | *Mesurer le temps moyen de qualification*. |

*Formulez le scénario* :  

> *« En tant qu’agent, je veux importer un fichier CSV, le valider et télécharger le rapport BIRT 05, afin de mesurer le gain de temps sur le processus de qualification. »*  

---  

## 8️⃣ Diagramme Mermaid du processus d’atelier  

```mermaid
flowchart TB;
    %% Acteurs;
    pm[👤 Chef de produit / PO]
    tech[👤 Lead technique]
    biz[👤 MOA / Chef de bureau]
    des[👤 Designer UX (opt)]
    usr[👤 Agent référent (opt)]

    %% Phases;
    subgraph prep["Phase 1 – Pré‑atelier"]
        p1[Vision produit & hypothèses] 
        p2[Story‑map ou épics] 
        p3[Contraintes (RGPD, Docker, BIRT)] 
    end;
    subgraph workshop["Phase 2 – Atelier MoSCoW"]
        w1[Intro & alignement] 
        w2[Rappel périmètre fonctionnel] 
        w3[Classification MoSCoW] 
        w4[Validation du périmètre MVP] 
        w5[Roadmap & actions] 
    end;
    subgraph post["Phase 3 – Post‑MVP"]
        t1[Tests fonctionnels (Import, Qualification, BIRT)] 
        t2[Collecte métriques] 
        t3[Revue post‑MVP → Pivot / Persévérer / Arrêter] 
    end;
    %% Flux;
    pm -->|Guide| p1;
    tech -->|Vérif. technique| p3;
    biz -->|Contraintes métier| p2;
    des -->|UX simplifiée| p2;
    usr -->|Usage réel| p2;
    p1 --> w1;
    p2 --> w2;
    p3 --> w2;
    w1 --> w2;
    w2 --> w3;
    w3 --> w4;
    w4 --> w5;
    w5 --> t1;
    t1 --> t2;
    t2 --> t3;
    t3 -->|Décision| pm;
    %% Styles;
    classDef acteur fill:#E3F2FD,stroke:#1976D2,stroke-width_2px;
    classDef phase fill:#E6E6FA,stroke:#7B1FA2,stroke-width_2px;
    class pm,tech,biz,des,usr acteur;
    class prep,workshop,post phase;
```

---  

## 9️⃣ Adaptations contextuelles (SIREINES)  

| Contexte | Adaptation recommandée |
|----------|------------------------|
| **Refonte d’un produit existant** | Partir des **points de friction** (ex. import CSV = erreurs fréquentes) pour identifier les *Must*. |
| **Produit fortement réglementé (RGPD)** | Les contraintes RGPD (déclaration 29/09/2014) deviennent **Must** si elles impactent le MVP (ex. gestion du consentement). |
| **Multi‑profil utilisateurs** | Sélectionner un **persona principal** (ex. Agent) pour