# 📦 MVP Definition Workshop – SIREINES  
**Product :** **SIREINES** – Gestion des qualifications d’experts et spécialistes (CGDD/DRI/AST2)  
**Domain :** Administration publique – Gestion des dossiers d’évaluation scientifique & technique  
**Version :** 2.5.x (déploiements : Recette, Pre‑prod, Prod)  

> **Objectif** – Définir collectivement le périmètre *Minimum Viable Product* (MVP) qui permettra de **tester les hypothèses / valider les besoins prioritaires** du produit SIREINES tout en maîtrisant les contraintes techniques, réglementaires (CNIL, RGPD) et d’infrastructure (Docker / PostgreSQL / BIRT).  

---  

## 1️⃣ Introduction & objectifs (15 min)

| ✅ Objectif | 📌 Description |
|------------|-----------------|
| **Clarifier la mission du MVP** | *« Quel apprentissage voulons‑nous obtenir ? Quelle hypothèse métier ou technique voulons‑nous valider ? »* |
| **Prioriser les fonctionnalités** | Classer les éléments entre **Must / Should / Could / Won’t** (méthode MoSCoW). |
| **Aligner les équipes** | Mettre en évidence les dépendances (Docker / BIRT / base de données) et les exigences de conformité (CNIL, RGPD). |
| **Préparer la suite** | Élaborer un premier backlog et un plan de release (MVP → V1 → Itérations). |

> ⚠️ **Rappel** – Un MVP n’est **pas** une version “allégée” du produit final ; c’est **un outil d’apprentissage** qui peut contenir un seul parcours utilisateur complet (ex. : “déposer une demande de qualification” ) avec des contournements acceptés (données factices, traitements manuels).  

---  

## 2️⃣ Contexte d’usage & positionnement (10 min)

| 📦 Élément | ℹ️ Détails SIREINES |
|-----------|-------------------|
| **Type de livrable** | Atelier + document de sortie (MVP scope, matrice MoSCoW, roadmap). |
| **Quand l’utiliser** | Avant tout nouveau développement (ex. : nouveau module d’export BIRT, interface « mise à jour auto‑profil », API d’alimentation externe). |
| **Cas d’usage typiques** | • Lancement d’une nouvelle fonctionnalité (ex. : tableau de bord statistiques).<br>• Refactorisation majeure (migration Docker → IaaS).<br>• Besoin de valider une hypothèse de flux (ex. : “les agents utilisent le bouton ‘Affecter’ sans formation”). |
| **Environnements** | Recette → `http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/`<br>Pre‑prod → `https://sireines.preprod.e2.rie.gouv.fr/Accueil.do`<br>Prod → `https://sireines.e2.rie.gouv.fr/Accueil.do` |
| **Contraintes majeures** | • **Sécurité / RGPD** : données personnelles (experts).<br>• **CNIL** : déclaration n°1034232 (validité 4 ans).<br>• **Infrastructure** : Docker compose (app, db, pgAdmin), IaaS (ECO4).<br>• **Technos** : Java 7, Struts 2, BIRT 4.3, PostgreSQL 14, Talend, Maven. |
| **Hypothèses à tester** (exemples) | 1️⃣ *“Un export BIRT automatisé augmente de 30 % le taux de lecture des rapports par les comités.”*<br>2️⃣ *“Les agents remplissent le formulaire de qualification en moins de 5 min si le champ ‘Mot‑clé’ est auto‑complété.”*<br>3️⃣ *“Le déploiement via Docker compose sur un poste de travail reproduit fidèlement l’environnement de recette.”* |

> 👉 **À préparer avant l’atelier** :  
> • Vision produit (slide 1).  
> • Liste des *personas* (ex. : Agent, Responsable de comité, Administrateur IAAS).  
> • Story‑map ou backlog fonctionnel existant (ex. : les écrans Accueil → Recherche → Affectation).  
> • Tableau des **contraintes** (techniques, réglementaires, budget).  

---  

## 3️⃣ Pré‑requis indispensables

| ✅ Pré‑requis | 📄 Livrable à fournir |
|--------------|----------------------|
| **Vision produit** (objectif, métriques de succès) | Slide ou doc `VISION.md`. |
| **Hypothèses à tester** (liste claire) | Table `HYPOTHESES.md`. |
| **Story‑map / backlog fonctionnel** | Fichier `STORYMAP.md` (épopées, fonctionnalités, user‑stories). |
| **Personas & retours utilisateurs** | Synthèse `PERSONAS.md`. |
| **Contraintes identifiées** (tech, RGPD, CNIL, budget, délai) | `CONTRAINTES.md`. |
| **Ressources logistiques** (salle, tableau blanc, post‑its 4 couleurs) | Vérifié le jour J. |
| **Accès aux environnements** (Docker, BIRT, PostgreSQL) | Credentials partagés (ex. : `docker-compose.yml`, `.env`). |

> **Tip :** Si un pré‑requis manque, réserver **15 min** au début de l’atelier pour le co‑créer rapidement (ex. : reformuler une hypothèse).  

---  

## 4️⃣ Parties prenantes & rôles

| 🎭 Rôle | 👤 Responsable | 🎯 Responsabilité pendant l’atelier |
|---------|----------------|-----------------------------------|
| **Animateur / Product Owner** | Chef de produit SIREINES (ex. : Pascal Zémour) | Facilite, garde le focus sur l’apprentissage, valide le périmètre final. |
| **Tech‑lead** | Architecte Java / Docker (ex. : Matthieu Georges) | Évalue la faisabilité technique, effort, dépendances Docker / BIRT. |
| **MOA / Responsable métier** | Responsable de la qualification (ex. : Vincent Letrouit) | Valide la valeur métier, les exigences réglementaires. |
| **Designer UX/UI** *(optionnel)* | Designer produit | Propose des maquettes légères, vérifie la simplicité du parcours. |
| **Utilisateur référent** *(optionnel)* | Agent expert (ex. : représentant du COM) | Apporte le point de vue “terrain”, challenge les priorités. |
| **Ops / Infra** | Responsable IaaS (ex. : équipe DPNM3) | Vérifie les contraintes d’infrastructure (Docker, volumes, IAAS). |
| **Scrum‑master / Coach** *(facilitateur)* | Facilitateur externe ou interne | Gère le timing, les votes, la documentation des décisions. |

> 👉 **Astuce** : Si vous avez moins de participants, combinez les rôles (ex. : PO + MOA).  

---  

## 5️⃣ Logistique de l’atelier

| 📦 Élément | 📋 Détails |
|------------|-----------|
| **Durée totale** | **2 h 30 min** (max 3 h) – prévoir une pause de **10 min** à mi‑parcours. |
| **Supports physiques** | Tableau blanc, 4 paquets de post‑its (Must = vert, Should = jaune, Could = bleu, Won’t = gris), marqueurs, stickers. |
| **Supports numériques** | Miro / Mural / FigJam (template MoSCoW pré‑chargé). <br>Google Docs ou Confluence pour la prise de notes collaborative. |
| **Livrables attendus** | • **Matrice MoSCoW** (tableau partagé).<br>• **Périmètre MVP** (liste Must).<br>• **Roadmap initiale** (MVP → V1 → Itérations).<br>• **Plan de test** (hypothèses, métriques). |
| **Enregistrement** | Photo du tableau blanc (ou capture d’écran) + notes dans le repo `sireines/docs/mvp-workshop/`. |

---  

## 6️⃣ Agenda détaillé (step‑by‑step)

| ⏱ Temps | 📍 Étape | 🎯 Objectif | 🛠️ Livrable / Artefact |
|----------|----------|------------|------------------------|
| **0‑15 min** | **1️⃣ Introduction & alignement** | Présenter objectifs, rappeler contraintes (RGPD, Docker, délai). | *Slide “MVP = apprentissage”* |
| **15‑45 min** | **2️⃣ Rappel du périmètre fonctionnel** | Revoir la story‑map / backlog existant, éliminer doublons. | *Tableau “Feature → Épopée → User‑Story”* |
| **45‑65 min** | **3️⃣ Identification des scénarios utilisateurs** | Sélectionner **1‑2 parcours** critiques (ex. : “Déposer une demande”, “Exporter le rapport”). | *Canvas “User Journey”* |
| **65‑80 min** | **4️⃣ Formulation des hypothèses** | Pour chaque scénario, écrire **HYPOTHÈSE + MÉTRIQUE** (ex. : temps de traitement < 5 min). | *Table “Hypothèse / KPI”* |
| **80‑120 min** | **5️⃣ Brainstorming des fonctionnalités** | Lister **toutes** les fonctions qui pourraient répondre aux scénarios (sans jugement). | *Post‑its → Mur de fonctions* |
| **120‑165 min** | **6️⃣ Classification MoSCoW** | Chaque fonction est placée dans **Must / Should / Could / Won’t** (dot‑voting ou discussion). | *Matrice MoSCoW* |
| **165‑195 min** | **7️⃣ Validation du périmètre MVP** | Vérifier que les **Must** forment un **parcours complet** et que les **hypothèses** sont testables. | *Checklist MVP* |
| **195‑215 min** | **8️⃣ Roadmap & prochaines étapes** | Positionner les Must (MVP), Should (V1), Could (backlog). Définir **qui** (owner) et **quand** (date) les actions. | *Roadmap Gantt simplifiée* |
| **215‑225 min** | **9️⃣ Wrap‑up & feedback** | Recapitulatif, points d’action, satisfaction des participants. | *Liste d’actions* + *Feedback rapide* |
| **225‑240 min** | **(Option) Pause / Q&A** | Temps libre pour questions ou points non couverts. | — |

> **Tip** – Utilisez le chronomètre partagé (Zoom, Teams) pour respecter les créneaux.  

---  

## 7️⃣ Modèles & templates (à copier‑coller)

### 7.1 Vision & métriques (exemple)

```markdown
# Vision SIREINES – MVP
**Objectif business** : Accélérer la collecte des qualifications d’experts de 30 % d’ici 6 mois.  
**Métrique principale** : % de dossiers soumis via le nouveau formulaire “Auto‑complétion Mot‑clé”.  
**KPI secondaires** :  
- Temps moyen de dépôt (< 5 min).  
- Taux d’erreur de saisie (< 2 %).  
- Nombre d’utilisateurs actifs (≥ 80 % des agents ciblés).  
```

### 7.2 Canvas d’hypothèse

| # | Hypothèse | KPI / Métrique | Critère de succès |
|---|-----------|----------------|-------------------|
| 1 | L’auto‑complétion des mots‑clés réduit le temps de saisie | Temps moyen de saisie (sec) | < 300 sec |
| 2 | L’export BIRT automatisé augmente le taux de lecture | % de rapports ouverts | + 30 % |
| … | … | … | … |

### 7.3 Table de brainstorming (post‑its → tableau)

| Fonctionnalité | Description courte | Scénario lié | Priorité (MoSCoW) |
|----------------|--------------------|--------------|-------------------|
| Auto‑complétion mots‑clés | Suggestion dynamique lors de la saisie | Déposer une demande |  |
| Export PDF BIRT | Générer un rapport PDF à la volée | Visualiser le résultat |  |
| Bouton “Affecter” simplifié | Un clic pour assigner un expert | Affecter un dossier |  |
| … | … | … | … |

### 7.4 Matrice MoSCoW (exemple)

| Must (Indispensable) | Should (Important) | Could (Nice‑to‑have) | Won’t (Exclu) |
|----------------------|-------------------|----------------------|--------------|
| Auto‑complétion mots‑clés | Export PDF BIRT | Historique des actions | Intégration LDAP |
| Validation formulaire côté client | Tableau de bord stats | Mode sombre UI | Export CSV de tous les logs |
| … | … | … | … |

### 7.5 Checklist de validation du MVP

- [ ] Le périmètre **Must** couvre **un parcours complet** (dépot → validation).  
- [ ] Chaque Must répond à **au moins une hypothèse testable**.  
- [ ] Les contournements (ex. : données factices, traitement manuel) sont **documentés**.  
- [ ] L’effort estimé (story points / jour) **≤ 30 %** du sprint prévu.  
- [ ] Les contraintes RGPD/CNIL sont **respectées** (ex. : anonymisation, logs).  

### 7.6 Roadmap simplifiée

| Release | Contenu | Owner | Date cible |
|--------|---------|-------|-----------|
| **MVP** (Must) | Auto‑complétion, validation formulaire, export BIRT (baseline) | PO / Tech‑lead | S‑print 5 |
| **V1** (Should) | Tableau de bord statistique, notifications email | PO / Designer | S‑print 8 |
| **Backlog** (Could) | Mode sombre, intégration LDAP, API publique | – | – |

---  

## 8️⃣ Conseils de facilitation

| ✅ Bonnes pratiques |