## 📄 Cahier des Charges Fonctionnel (CCF) – Projet **ambulon**  
*Conforme à la norme NF EN 16271 :2013 – Management par la valeur*  

---

### ⚠️ Ce document est actuellement un **gabarit** ; il ne peut être finalisé tant que les informations suivantes ne sont pas fournies :

| # | Information attendue | Pourquoi c’est indispensable pour le CCF |
|---|----------------------|-------------------------------------------|
| 1 | **Contexte métier et enjeux stratégiques** (ex. : amélioration de la prise en charge des patients, réduction des temps d’intervention, conformité à la réglementation santé, etc.) | Permet de justifier le besoin global et de lier le projet à la stratégie de l’organisation (section 1). |
| 2 | **Objectifs quantifiables** (ex. : < 15 min de temps moyen d’arrivée, ≥ 99 % de disponibilité du service, …) | Sert à définir les critères de performance des fonctions de service (section 2) et à pondérer les besoins (section 3‑4). |
| 3 | **Périmètre fonctionnel** – ce qui est **inclus** et **exclu** du projet (ex. : prise de rendez‑vous, suivi de trajet, communication avec les services d’urgence, etc.) | Nécessaire pour délimiter le champ d’application du CCF (section 1). |
| 4 | **Liste préliminaire des fonctions de service** (FP – fonctions principales, FC – fonctions contraintes) | Base de l’analyse de la valeur (section 2). |
| 5 | **Critères de performance** associés à chaque fonction (ex. : temps de réponse, précision de localisation, taux d’erreur, …) | Permet de rédiger les critères d’appréciation mesurables (section 3‑4). |
| 6 | **Parties prenantes** (ex. : patients, ambulanciers, centre de régulation, direction médicale, services informatiques, autorités de santé, …) | Pour la matrice des parties prenantes (section 7) et la traçabilité des besoins. |
| 7 | **Contraintes réglementaires et techniques** (RGPD, normes HDS, interopérabilité HL7/FHIR, exigences d’infrastructure, budget, planning, …) | Alimente la partie « Contraintes et environnement » (section 8). |
| 8 | **Scénarios d’usage** (nominal, erreur, limites) | Nécessaires pour valider que les besoins couvrent l’ensemble des situations d’utilisation (section 6). |
| 9 | **Critères de sélection et pondérations** attendus pour l’appel d’offres (ex. : prix 30 %, conformité fonctionnelle 40 %, qualité 30 %) | Permet de préparer la grille d’évaluation (section 9). |

> **Remarque** : Le fichier `README.md` présent dans l’arborescence n’a pas été fourni dans le texte ; son contenu serait très utile (description du projet, architecture, technologies utilisées, etc.).  

---

## 📋 Prochaine étape

1. **Copiez‑collez le contenu complet du `README.md`** (ou tout autre document de spécifications existant) dans votre prochain message.  
2. **Répondez aux points 1 à 9** de la table ci‑dessus ; même une description sommaire nous permettra de commencer à remplir les sections du CCF.  
3. Si vous avez déjà identifié certaines fonctions de service ou des exigences critiques, indiquez‑les ; nous les intégrerons immédiatement.  

---

### 📂 Structure du CCF (à remplir dès réception des informations)

| Section | Contenu attendu (exemple) |
|---------|---------------------------|
| **1. Présentation du projet** | Contexte, enjeux, objectifs, périmètre (inclus/exclus). |
| **2. Analyse de la valeur** | Tableau des fonctions de service (FP/FC) + critères de performance. |
| **3. Expression fonctionnelle du besoin** | Hiérarchisation B‑01, B‑01‑01, … avec description « QUOI », critères mesurables, pondération. |
| **4. Caractérisation des besoins** | Tableau détaillé (Fonction, Critère, Importance, Flexibilité, Contraintes). |
| **5. Validation de l’expression du besoin** | Méthodes, ateliers, parties prenantes, traçabilité. |
| **6. Scénarios d’usage** | Nominal, erreur, limites (ex. : appel d’urgence, perte de connexion, conditions météo extrêmes). |
| **7. Parties prenantes** | Tableau (Rôle, Besoins spécifiques, Impact sur la valeur). |
| **8. Contraintes et environnement** | Réglementaires, techniques, organisationnelles, temporelles, budgétaires. |
| **9. Critères de sélection et pondération** | Grille d’évaluation conforme aux exigences des marchés publics. |
| **10. Glossaire et acronymes** | Définitions normalisées. |

---

## 🛠️ Ce que nous pouvons faire dès maintenant (option 1)

Si vous ne disposez pas encore de toutes les informations, nous pouvons :

* **Élaborer un premier jet** basé sur des hypothèses classiques pour un projet de type “**système de gestion d’ambulances**” (prise de rendez‑vous, suivi en temps réel, communication avec les services d’urgence, tableau de bord de performance, conformité RGPD/HDS).  
* Vous le soumettre afin que vous puissiez le valider/modifier rapidement, puis le compléter au fur et à mesure que les données deviennent disponibles.

Vous indiquez simplement : **“Oui, je veux un CCF basé sur un système de gestion d’ambulances”** ou vous précisez les spécificités du projet (ex. : uniquement module de géolocalisation, plateforme mobile, etc.) ; nous rédigerons alors les sections 1‑9 en suivant la norme, en marquant chaque besoin avec un identifiant unique (B‑xx‑xx) et en respectant les règles de vérifiabilité, de flexibilité et de traçabilité.

---

## 📧 Comment procéder ?

1. **Répondez à ce message** avec le contenu du `README.md` ou les éléments listés dans le tableau ci‑dessus.  
2. Ou, si vous préférez un aperçu générique, indiquez : **“Générer un CCF type pour un système de gestion d’ambulances”**.  

Nous attendons vos précisions pour livrer un CCF complet, exploitable dans le cadre d’un appel d’offres public et conforme à la NF EN 16271.