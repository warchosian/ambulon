## 📄 Cahier des Charges Fonctionnel (CCF) – Projet **ambulon**  
**Version 0.1 – Ébauche**  
*(conforme à la norme NF EN 16271 :2013 – Management par la valeur)*  

---

> **NOTE IMPORTANTE**  
> Le présent document a été généré à titre d’**ébauche** ; il ne comporte pour l’instant aucune description fonctionnelle du besoin, car les informations détaillées du projet (contenu du README, architecture, objectifs, parties‑prenantes, contraintes, etc.) n’ont pas été communiquées.  
> Pour finaliser le CCF, merci de fournir :
> 1. **Une description synthétique** du projet : finalité, contexte métier, enjeux stratégiques.  
> 2. **Le texte complet du README.md** (ou tout autre document d’expression du besoin déjà rédigé).  
> 3. **Les parties prenantes** identifiées (maîtrise d’ouvrage, maîtrise d’œuvre, utilisateurs finaux, services support, etc.).  
> 4. **Les contraintes connues** (réglementaires, techniques, budgétaires, planning).  
> 5. **Les critères de performance attendus** (ex. temps de réponse, disponibilité, sécurité, ergonomie).  

Une fois ces éléments fournis, je pourrai :

* Compléter la **section 1 – Présentation du projet**.  
* Identifier les **fonctions de service (FP/FC)** et les **critères de performance** (section 2).  
* Décomposer le besoin en **niveaux hiérarchiques** (global, partiels, élémentaires) avec identifiants uniques (section 3).  
* Remplir le **tableau de caractérisation des besoins** (section 4).  
* Décrire les **scénarios d’usage** (section 6).  
* Finaliser la **grille de sélection** (section 9) et la **tracabilité** (section 5).  

---

### 📑 Plan du CCF (à compléter)

| N° | Section | Contenu attendu |
|----|---------|-----------------|
| 1 | **Présentation du projet** | Contexte, objectifs, périmètre (inclus / exclus). |
| 2 | **Analyse de la valeur** | Fonctions de service (FP / FC), critères de performance associés. |
| 3 | **Expression fonctionnelle du besoin** | Décomposition hiérarchique : B‑01, B‑01‑01, B‑01‑01‑01 … (description *quoi*, pas *comment*). |
| 4 | **Caractérisation des besoins** | Tableau : Fonction, Critère d’appréciation, Niveau d’importance, Flexibilité, Contraintes. |
| 5 | **Validation de l’expression du besoin** | Méthodes, ateliers, parties prenantes validées, traçabilité. |
| 6 | **Scénarios d’usage** | Scénarios nominaux, d’erreur, limites. |
| 7 | **Parties prenantes (Stakeholders)** | Tableau : Partie prenante, Rôle, Besoins spécifiques, Impact sur la valeur. |
| 8 | **Contraintes et environnement** | Organisationnelles, réglementaires (RGPD, RGS, etc.), techniques, temporelles, budgétaires. |
| 9 | **Critères de sélection et pondération** | Grille d’évaluation conforme aux marchés publics (pondération, modalité de notation). |
|10 | **Glossaire et acronymes** | Définitions normalisées, acronymes. |

---

## 🔧 Prochaine étape : collecte d’informations

### 1️⃣ Fournir le texte du **README.md** (ou tout autre document de spécification)

> Exemple de points à extraire :
> * Quel problème le produit **ambulon** résout‑il ?
> * Qui sont les utilisateurs finaux (médecins, ambulanciers, patients, etc.) ?
> * Quelles sont les fonctions majeures attendues (ex. : suivi en temps réel, géolocalisation, transmission de données vitales, interface mobile) ?
> * Quelles sont les exigences non fonctionnelles (sécurité, confidentialité, disponibilité, performance) ?

### 2️⃣ Décrire le **cadre stratégique**  

* Alignement avec la stratégie de l’organisme (ex. : amélioration de la prise en charge d’urgence, conformité aux exigences du service public de santé).  
* Objectifs quantifiables (ex. : réduire le temps moyen d’arrivée sur site de 15 % d’ici 12 mois).

### 3️⃣ Lister les **parties prenantes**  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|-----------------|------|---------------------|----------------------|
| Exemple : Direction médicale | Commanditaire | Fiabilité, conformité légale | Priorité élevée |
| … | … | … | … |

### 4️⃣ Indiquer les **contraintes** connues  

* Réglementaires : RGPD, normes de santé (HDS, ISO 13485), exigences de l’ARS, etc.  
* Techniques : compatibilité avec les systèmes d’information hospitaliers (SIH), exigences d’interopérabilité (HL7/FHIR).  
* Budgétaires : budget total, plafond de dépenses par lot.  
* Planning : date de mise en service cible, jalons majeurs.

### 5️⃣ Définir les **critères de performance** (mesurables)  

| Critère | Unité | Valeur cible | Méthode de mesure |
|---------|-------|--------------|--------------------|
| Temps de latence de transmission des données vitales | ms | ≤ 200 ms | Tests de charge, simulation réseau |
| Disponibilité du service | % | ≥ 99,5 % | Monitoring continu, SLA |
| … | … | … | … |

---

## 📌 Rappel des exigences NF EN 16271

| Exigence | Description | À vérifier dans le CCF final |
|----------|-------------|------------------------------|
| **Distinction besoin/solution** | Aucun élément de prescription technique (ex. : « utiliser le framework X »). | Toutes les sections (2‑4) doivent rester *déclaratives* du **quoi**. |
| **Vérifiabilité** | Chaque critère doit être mesurable ou observable. | Tous les critères d’appréciation (tables 4 & 9) sont quantifiés. |
| **Hiérarchisation** | Niveau d’importance clairement pondéré (Obligatoire / Souhaitable / Optionnel). | Tableau 4 indique le niveau d’importance et la flexibilité. |
| **Flexibilité** | Indiquer si le critère est négociable. | Colonne **Flexibilité** du tableau 4. |
| **Traçabilité** | Chaque besoin possède un identifiant unique. | Identifiant (ex. B‑01‑02) présent dans tout le document. |

---

## 📎 Modèle de tableau de caractérisation (section 4)

| Fonction | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|----------|------------------------|---------------------|-------------|-------------|
| **F1 – Suivi en temps réel** | Temps de latence ≤ 200 ms | Obligatoire | Fixe | Réseau 4G/5G, bande passante minimale 2 Mbps |
| **F2 – Transmission sécurisée** | Chiffrement AES‑256, conformité RGPD | Obligatoire | Fixe | Certification HDS |
| **F3 – Interface mobile** | Ergonomie selon norme ISO 9241, temps de réponse ≤ 1 s | Souhaitable | Négociable | Compatibilité iOS ≥ 13, Android ≥ 9 |
| **F4 – Historisation des données** | Conservation 5 ans, accès auditabilité | Optionnel | Négociable | Stockage conforme ISO 27001 |
| … | … | … | … | … |

---

## 🗓️ Prochaine itération

1. **Réception des informations complémentaires** (README, contexte, parties prenantes, contraintes).  
2. **Enrichissement du CCF** : remplissage des sections 1 à 9, génération des identifiants, validation de la traçabilité.  
3. **Relecture conjointe** avec le maître d’ouvrage (MOA) et le maître d’œuvre (MOE) pour validation de l’expression du besoin.  
4. **Publication** du CCF final (format Markdown, compatible avec les outils de gestion d’exigences – ex. Jira / Azure DevOps / IBM Rational DOORS).  

---

### 📞 À votre disposition

Je reste disponible pour :

* **Accompagner** la rédaction du texte de chaque section.  
* **Formuler** les fonctions de service (FP/FC) à partir de votre description fonctionnelle.  
* **Construire** la grille de sélection adaptée à votre procédure de marché public.  

> **Merci de transmettre les éléments demandés** afin que nous puissions avancer rapidement vers un CCF complet, conforme à la norme NF EN 16271 et parfaitement exploitable dans le cadre de votre appel d’offres.  

--- 

*Document généré par ChatGPT (modèle GPT‑4o) – 27 avril 2026*