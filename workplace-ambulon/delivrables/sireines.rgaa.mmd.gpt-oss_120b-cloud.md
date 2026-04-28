# 📋 Guide d’atelier d’homologation RGAA – **SIREINES**  

*Document auto‑portant, au format **Markdown**, prêt à être ouvert dans VS Code, Obsidian ou tout autre éditeur.*  

> **« Préparer et piloter l’homologation RGAA d’un produit numérique »**  

---  

## 🗂️ Table des matières  
1. [Introduction et objectifs](#1-introduction-et-objectifs)  
2. [Contexte d’usage](#2-contexte-dusage)  
3. [Pré‑requis](#3-pre-requis)  
4. [Parties prenantes et rôles](#4-parties-prenantes-et-rôles)  
5. [Logistique](#5-logistique)  
6. [Déroulé détaillé de l’atelier](#6-déroulé-détaillé-de-latelier)  
   - 6.1 🎯 Cadrage réglementaire  
   - 6.2 🔍 Identification des critères RGAA applicables  
   - 6.3 📊 Évaluation & scoring  
   - 6.4 🎚️ Priorisation & plan d’action  
   - 6.5 🏁 Documentation & homologation  
7. [Conseils de facilitation](#7-conseils-de-facilitation)  
8. [Matrice de conformité (exemple)](#8-matrice-de-conformité-exemple)  
9. [Diagramme Mermaid du processus d’homologation](#9-diagramme-mermaid-du-processus-dhomologation)  
10. [Glossaire RGAA / WCAG](#10-glossaire-rgaa--wcag)  
11. [Livrables & suite du projet](#11-livrables--suite-du-projet)  

---  

## 1️⃣ Introduction et objectifs  

| Élément | Valeur |
|---|---|
| **Produit** | **SIREINES** – Système d’information de recensement des experts et spécialistes scientifiques et techniques |
| **Type** | Application Web (Tomcat + BIRT) – déployée en conteneurs Docker |
| **Public cible** | Agents du ministère, experts, spécialistes, usagers internes (fonctionnaires) |
| **Objectif de l’atelier** | Préparer, réaliser et formaliser l’homologation RGAA 4.1+ (déclinaison française des WCAG 2.1/2.2) afin de : <br>• Valider la conformité légale (loi 2005‑11‑11, décret 2019‑768, arrêté 2021) <br>• Obtenir un taux de conformité ≥ 75 % (seuil légal) <br>• Définir un plan d’amélioration continue (objectif 100 % pour le SIG) |
| **Méthodologie** | Atelier de 3 h 30 – basé sur le **RGAA 4.1+** (critères, thèmes, niveaux de conformité) |  

---  

## 2️⃣ Contexte d’usage  

| Domaine | Information |
|---|---|
| **Cadre réglementaire** | • Loi n° 2005‑102 du 11 février 2005 <br>• Décret n° 2019‑768 du 24 juillet 2019 <br>• Arrêté du 29 avril 2021 (RGAA 4.1) <br>• Directive UE 2016/2102 (accessibilité des sites publics) |
| **Environnements** | • Production : `https://sireines.e2.rie.gouv.fr/Accueil.do` <br>• Pré‑prod : `https://sireines.preprod.e2.rie.gouv.fr/Accueil.do` <br>• Recette : `http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/Accueil.do` |
| **Technologies** | Java /J2EE (1.7), Struts 2, FreeMarker (.ftl), BIRT 4.3, Docker + Compose, PostgreSQL 14 (alpine) |
| **Seuils de conformité** | **Minimum légal** : ≥ 75 % des critères <br>**Cible SIG** : 100 % (conformité totale) |
| **Date de dernière version en prod** | 12 mars 2024 – v 2.5.20 (voir `Sireines.Version.md`) |
| **Périmètre fonctionnel à auditer** | Tous les écrans accessibles depuis le menu principal (≈ 30 pages) : <br>Accueil, Dossiers, Extraction, Référentiels, Import/Export, Gestion des agents, etc. |
| **Contraintes d’exploitation** | Hébergement IaaS (ECO4) – centre serveur ministériel Paris La Défense <br>Authentification via SSO interne (voir `sireines-auth-config.xml`) |

---  

## 3️⃣ Pré‑requis  

| ✔️ | Action |
|---|---|
| **Périmètre produit** | URLs, versions des war (`sireines-web‑*.war`), liste des pages (exemple : `webapp/jsp/**/*.jsp`) |
| **Public‑cible** | Personas : agent administratif, expert, responsable de comité, usager interne |
| **Stack technique** | Docker Compose (`docker-compose.yml`), fichier `.env`, accès aux logs Tomcat (`/opt/app/logs`) |
| **État des lieux accessibilité** | Si aucun audit préalable, lancer un **scan rapide** avec **axe‑core**, **Lighthouse** ou **PA11Y** pour identifier les bloquants majeurs |
| **Référentiel DSFR** (facultatif) | Version du Design System Français utilisée (si appliquée) |
| **Outils** | • Navigateurs : Chrome + NVDA ou VoiceOver <br>• Extensions : Axe DevTools, WAVE <br>• Éditeur : VS Code (ou tout IDE) pour visualiser les fichiers `.ftl` et les templates |  

---  

## 4️⃣ Parties prenantes et rôles  

| Rôle | Profil type | Responsabilité pendant l’atelier |
|---|---|---|
| **Animateur / Référent accessibilité** | Chef de projet / UX / Expert RGAA | Facilite, explique les critères, arbitre les priorités |
| **Développeur front / Tech Lead** | Dev Java/Struts 2, FreeMarker | Évalue la faisabilité des corrections, estime l’effort technique |
| **Designer UX/UI** | Designer produit, connaissance du DSFR | Propose des alternatives accessibles (couleurs, focus, tailles) |
| **Juriste / Conformité** | RSSI, DPO, MOA juridique | Valide la conformité légale, rédige la déclaration d’accessibilité |
| **Représentant utilisateurs** *(optionnel)* | Agent, expert, association d’usagers handicap | Teste les scénarios réels, signale les difficultés d’usage |
| **Ops / Infra** | Administrateur Docker/VM | Vérifie l’accès aux logs, aux conteneurs, prépare l’environnement de test |  

---  

## 5️⃣ Logistique  

| Item | Détails |
|---|---|
| **Durée** | 3 h 30 min (prévoir 15 min de pause) |
| **Matériel** | - Tableau blanc ou paperboard <br>- Post‑its 4 couleurs (Conforme / Non‑conforme / À‑vérifier / Hors‑périmètre) <br>- Laptop + projecteur <br>- Accès à l’instance Docker (`sireinesrec`) via Bastion (voir `Archives/Déploiement‑de‑l'applicatif‑recette‑preprod‑prod.md`) |
| **Outils digitaux** | - **Axe DevTools** (Chrome) <br>- **PA11Y** (CLI) <br>- **GitLab** (pour récupérer le war) <br>- **VS Code** (édition des templates `.ftl`) |
| **Livrable de sortie** | - **Matrice de conformité RGAA** (exemple section 8) <br>- **Plan d’action** (priorités, responsables, échéances) <br>- **Brouillon de déclaration d’accessibilité** (texte à compléter) |
| **Environnement de test** | Conteneur Docker : `docker-compose -f docker-compose.yml up -d` (voir `Recette/LivraisonSurPosteDocker.md`) – accès via `http://localhost:8080/Accueil.do` |  

---  

## 6️⃣ Déroulé détaillé de l’atelier  

### 🎯 6.1 Cadrage réglementaire (30 min)

1. **Rappel du cadre légal** (loi 2005, décret 2019, arrêté 2021, directive UE 2016/2102).  
2. **Présentation du RGAA 4.1** – les 4 principes WCAG : *Perceptible – Utilisable – Compréhensible – Robuste*.  
3. **Définir le périmètre d’audit** :  
   - Toutes les pages accessibles via le menu principal (≈ 30 pages).  
   - Navigation clavier, lecteurs d’écran, contrastes, alternatives textuelles, formulaires, tables, scripts.  
4. **Exemple de non‑conformité** : image du logo sans `alt` (voir `sireines-web/src/main/resources/template/simple_read/checkbox.ftl` où le `alt` est absent).  

> **Astuce** : ouvrir un navigateur, activer le mode “Inspecteur”, sélectionner un élément `<img>` et vérifier la présence de `alt=""`.  

---

### 🔍 6.2 Identification des critères applicables (45 min)

| Thème RGAA | Exemple de critère critique | Pages concernées (exemples) |
|---|---|---|
| **Images** | 1.1 « Chaque image porte‑une alternative textuelle » | `accueil.jsp`, `dossiers/dossierDetail.jsp` |
| **Couleurs** | 1.2 « Le contraste doit être ≥ 4.5 :1 » | Tous les formulaires (`.ftl`), menus |
| **Multimédia** | 3.1 « Les vidéos doivent proposer des sous‑titres » | Rapports BIRT (PDF/HTML) |
| **Tables** | 4.1 « Les tables de données doivent être correctement structurées » | `dossiers/dossierRecherche.jsp` |
| **Liens** | 5.1 « Le texte du lien doit être explicite » | Tous les `<s:a href>` dans les JSP |
| **Scripts** | 7.1 « Les composants dynamiques doivent être accessibles au clavier » | Navigation dynamique (`menu.jsp`) |
| **Navigation** | 9.1 « La navigation principale doit être accessible au clavier » | `header.jsp`, `menu.jsp` |
| **Information & consultation** | 10.1 « Les messages d’erreur doivent être lisibles par un AT » | Formulaires d’import (`importFichier.jsp`) |

**Méthode** : travailler en binômes (développeur + designer) ; cocher chaque critère : ✅ Conforme / ❌ Non‑conforme / ⚠️ À‑vérifier / 🚫 Hors‑périmètre.  

---

### 📊 6.3 Évaluation et scoring (45 min)

1. **Tests rapides** :  
   - **Manuel** : navigation clavier (`Tab`, `Enter`), lecture d’écran (NVDA).  
   - **Automatique** : `npx pa11y http://localhost:8080/Accueil.do --reporter json > audit.json`.  
2. **Calcul du taux** :  

```text
Taux = (Nb critères conformes) / (Nb critères applicables) × 100
```

3. **Identifier les écarts critiques** :  
   - Bloquants (ex. : images sans `alt`, focus invisible).  
   - Bloquants partiels (ex. : contraste insuffisant).  
   - Améliorations (ex. : libellés de champs plus clairs).  

> **Objectif** : dépasser 75 % avant la fin de l’atelier.  

---

### 🎚️ 6.4 Priorisation et plan d’action (45 min)

| Impact | Effort | Priorité | Action (exemple) | Responsable | Échéance |
|---|---|---|---|---|---|
| **Fort** | **Faible** | 🔴 P1 (Quick win) | Ajouter `alt` aux logos (`<img src="..." alt="logo SIREINES">`) | Dev Front | + 2 jours |
| **Fort** | **Fort** | 🟡 P2 (Investissement) | Re‑définir le contraste des menus (CSS) | UI/UX | + 1 semaine |
| **Faible** | **Faible** | 🟢 P3 | Mettre à jour les libellés des champs de recherche | Dev Back | + 3 jours |
| **Faible** | **Fort** | ⚪ P4 | Refactoriser le composant de pagination dynamique | Architecte | + 2 semaines |

**Livrable** : tableau « Plan d’action » à insérer dans le **backlog** (Jira, GitLab Issues).  

---

### 🏁 6.5 Documentation et homologation (30 min)

1. **Rédiger la déclaration d’accessibilité** (modèle obligatoire) :  

```markdown
# Déclaration d’accessibilité de SIREINES  

- **Version du produit** : {{VERSION}} (déploiement {{DATE}})  
- **URL de la version en production** : https://sireines.e2.rie.gouv.fr/Accueil.do  
- **Taux de conformité RGAA** : {{TAUX}} % ({{NB_CONFORME}} / {{NB_TOTAL}})  
- **Critères non‑conformes** : 1.1, 5.1, 7.1 (voir matrice)  
- **Moyens de contact** :  
  - Email : {{CONTACT_EMAIL}}  
  - Téléphone : {{CONTACT_TEL}}  
- **Voie de recours** : Défenseur des droits – https://www.defenseurdesdroits.fr/  
- **Date de publication** : {{DATE_PUBLICATION}}  

*Cette déclaration est mise à jour à chaque nouvelle version de l’application.*  
```  

2. **Assembler le dossier d’homologation** :  
   - Matrice de conformité (section 8).  
   - Plan d’action (section 6.4).  
   - Rapport d’audit automatisé (`audit.json`).  
   - Capture d’écran des tests d’AT (NVDA).  

3. **Soumettre** : déposer le dossier dans le **GitLab CI** (`/docs/accessibilite/`) et notifier le **RSSI** et le **DPO**.  

---  

## 7️⃣ Conseils de facilitation  

| Bonnes pratiques | À éviter |
|---|---|
| Utiliser un scénario réel (ex. : création d’un dossier) pour illustrer chaque critère | Se perdre dans le jargon technique du RGAA (ex. : “niveau de conformité AA/AAA”) |
| Faire valider chaque correction en temps réel (lecture d’écran) | Reporter systématiquement les corrections “complexes” sans analyse d’impact |
| Documenter les décisions d’exemption (si besoin) | Omettre les critères « hors‑périmètre » sans justification |
| Mettre à jour la matrice au fur et à mesure | Utiliser uniquement des scores d’outils automatiques (risk of false‑positives) |
| Impliquer le représentant utilisateurs dès le début | Négliger les tests d’accessibilité mobile (si appliqué) |

---  

## 8️⃣ Matrice de conformité (exemple)  

| Thème | Critère RGAA | Statut | Observation | Action corrective | Priorité |
|---|---|---|---|---|---|
| **Images** | 1.1 « Chaque image porte une alternative textuelle » | ❌ Non‑conforme | Logo SIREINES sans `alt` (templates `header.jsp`) | Ajouter `alt="logo SIREINES"` | 🔴 P1 |
| **Couleurs** | 1.2 « Contraste ≥ 4.5 :1 » | ⚠️ À‑vérifier | Boutons du menu avec couleur `#777` sur fond `#fff` | Ajuster CSS (`color:#222`) | 🟡 P2 |
| **Formulaires** | 5.3 « Les champs obligatoires doivent être indiqués » | ✅ Conforme | Tous les champs ont `*` et `required="true"` | — | — |
| **Navigation** | 9.1 « Navigation principale accessible au clavier » | ❌ Non‑conforme | Le menu déroulant ne reçoit pas le focus (`tabindex` manquant) | Ajouter `tabindex="0