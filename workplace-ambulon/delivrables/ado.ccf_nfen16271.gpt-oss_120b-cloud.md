# 📄 Cahier des Charges Fonctionnel (CCF) – **Projet ADO**  
*Conformément à la norme NF EN 16271 :2013 (Management par la valeur)*  

---  

## 1️⃣ Présentation du projet  

| Élément | Description |
|--------|-------------|
| **Nom du projet** | ADO – Consultation des dossiers RH archivés de ReHucit |
| **Contexte** | Avant la bascule du SIRH ReHucit → RenoiRH (30/05/2019), les dossiers RH des agents n’ont pas tous été migrés. ADO permet aux services de la DRH de consulter ces données historiques. |
| **Enjeux stratégiques** | - Garantir la continuité d’accès aux dossiers administratifs et financiers (ex : audit, retraite). <br> - Conformité juridique (obligation d’accès aux archives). <br> - Soutien à la prise de décision (historisation, traçabilité). |
| **Objectifs** | 1. Offrir une interface web sécurisée de recherche et de consultation d’un agent. <br> 2. Produire les différents **rapports** (Mini‑CV, état de service, actes, conjoint, enfants, etc.) au format PDF/HTML/CSV/XLSX. <br> 3. Historiser chaque consultation (journal) et permettre son suivi/purge. |
| **Périmètre fonctionnel (inclus)** | • Recherche d’agents (critères libres, date de naissance, matricule, nom, ville, pays). <br> • Consultation détaillée d’un agent (identité, situation familiale, carrière, affectations, rémunération, etc.). <br> • Génération des rapports : Mini‑CV, Rapport 19, 20, 21, 22, Acte, Conjoint, Enfant, Historique, Suivi d’utilisation, Purge. <br> • Gestion du journal d’accès (enregistrement, affichage, export, purge). |
| **Périmètre fonctionnel (exclus)** | • Saisie ou modification des données RH (aucune fonctionnalité de mise à jour). <br> • Gestion des droits d’administration (hors scope : uniquement filtrage d’accès). <br> • Intégration de nouvelles sources de données post‑2019. |
| **Environnement d’exploitation** | Application web (HTTPS) hébergée sur le centre‑serveur ministériel Paris La Défense – plateforme IaaS (ECO4). |

---  

## 2️⃣ Analyse de la valeur  

### 2.1 Fonctions de service (FS)  

| Code | Fonction de service | Type | Description |
|------|---------------------|------|-------------|
| **FS‑01** | **Recherche d’agents** | FP (Fonction Principale) | Permet à un utilisateur de retrouver un ou plusieurs agents à partir de critères libres (nom, matricule, lieu de naissance, dates). |
| **FS‑02** | **Visualisation du dossier agent** | FP | Affiche toutes les informations historiques d’un agent (identité, état civil, carrière, affectations, rémunération, enfants, conjoint, etc.). |
| **FS‑03** | **Génération de rapports** | FP | Produit, à la demande de l’utilisateur, les différents rapports (Mini‑CV, Rapport 19‑22, Actes, Conjoint, Enfants, etc.) dans les formats requis (PDF, XLSX, CSV, HTML, TXT). |
| **FS‑04** | **Historisation des consultations** | FP | Enregistre chaque consultation (date, heure, agent, utilisateur, paramètres) dans le journal d’accès. |
| **FS‑05** | **Suivi d’utilisation** | FP | Permet de filtrer et d’afficher le journal selon des intervalles de dates, afin de contrôler l’usage de l’application. |
| **FS‑06** | **Purge du journal** | FP | Supprime les enregistrements du journal antérieurs à une date donnée, conformément aux exigences de conservation. |
| **FS‑07** | **Sécurisation de l’accès** | FC (Fonction Contraint) | L’accès à l’application doit être filtré par le composant *FiltreCerbere* (authentification unique, contrôle de profil unique). |
| **FS‑08** | **Disponibilité du service** | FC | L’application doit être disponible ≥ 99,5 % sur une base annuelle (exigence de la DICT). |
| **FS‑09** | **Traçabilité & audit** | FC | Tous les accès et actions doivent être traçables (horodatage, identifiant utilisateur, IP). |
| **FS‑10** | **Conformité RGPD/DACP** | FC | Les données à caractère personnel doivent être traitées conformément au RGPD (consentement, droit d’accès, chiffrement au repos). |

### 2.2 Critères de performance associés  

| Fonction | Critère | Valeur attendue | Unité | Type de critère |
|----------|---------|------------------|-------|----------------|
| FS‑01 | Temps de réponse de la recherche | ≤ 3 s | secondes | Mesurable |
| FS‑02 | Temps de chargement du dossier complet | ≤ 4 s | secondes | Mesurable |
| FS‑03 | Durée de génération d’un rapport PDF | ≤ 5 s | secondes | Mesurable |
| FS‑04 | Volume journal quotidien maximal | ≤ 10 000 enregistrements | lignes | Mesurable |
| FS‑05 | Temps de filtrage du journal | ≤ 2 s | secondes | Mesurable |
| FS‑06 | Temps d’exécution d’une purge (1 million de lignes) | ≤ 30 s | secondes | Mesurable |
| FS‑07 | Temps d’authentification | ≤ 1 s | seconde | Mesurable |
| FS‑08 | Disponibilité | ≥ 99,5 % | % annuel | Mesurable |
| FS‑09 | Conservation des logs (audit) | ≥ 2 ans | années | Mesurable |
| FS‑10 | Chiffrement des données au repos | AES‑256 | – | Vérifiable |

---  

## 3️⃣ Expression fonctionnelle du besoin  

| Identifiant | Niveau | Description fonctionnelle (QUOI) | Critères d’appréciation | Niveau d’importance |
|------------|--------|--------------------------------|--------------------------|----------------------|
| **B‑01** | Système | L’utilisateur doit pouvoir **rechercher** un ou plusieurs agents en renseignant un ou plusieurs critères libres (nom, prénom, matricule RGP/RRH, ville/pays de naissance, dates de naissance, dates de naissance, etc.). | - Retour d’au moins 1 résultat en ≤ 3 s.<br>- Recherche sensible à la casse et aux accents (unaccent). | Obligatoire |
| **B‑02** | Système | L’utilisateur doit pouvoir **visualiser le dossier complet** d’un agent sélectionné, incluant : identité, état civil, historique des noms, enfants, conjoint, carrières, affectations (interne, externe, hors‑administration), quotités, traitements indiciaires, banques, etc. | - Affichage complet en ≤ 4 s.<br>- Tous les champs listés dans la documentation technique doivent être présents. | Obligatoire |
| **B‑03** | Système | L’utilisateur doit pouvoir **générer** chaque type de **rapport** (Mini‑CV, Rapport 19, 20, 21, 22, Acte, Conjoint, Enfant, Éléments de rémunération, Temps partiel, Mode de paiement) au format demandé (PDF, XLSX, CSV, HTML, TXT). | - Génération en ≤ 5 s.<br>- Respect du schéma de colonnes indiqué dans les *adapters* (ex : 13 colonnes pour le rapport état service). | Obligatoire |
| **B‑04** | Système | Chaque consultation (recherche, visualisation, génération de rapport) doit être **enregistrée** dans le journal d’accès (date, heure, matricule agent, identifiant utilisateur, paramètres, nom du rapport). | - Enregistrement en < 1 s.<br>- Conservation pendant au moins 2 ans. | Obligatoire |
| **B‑05** | Système | L’utilisateur doit pouvoir **interroger le journal** en filtrant sur une date de début / date de fin et visualiser les lignes correspondantes (triées décroissantes). | - Filtrage en ≤ 2 s. | Obligatoire |
| **B‑06** | Système | L’utilisateur (profil “admin journal”) doit pouvoir **purger** le journal en spécifiant une date seuil (suppression de toutes les lignes antérieures). | - Opération terminée en ≤ 30 s pour 1 M lignes.<br>- Confirmation avant suppression. | Obligatoire |
| **B‑07** | Système | L’accès à l’application doit être **filtré** par le composant *FiltreCerbere* (authentification unique, profil unique). | - Authentification réussie en ≤ 1 s.<br>- Refus d’accès si plusieurs profils. | Contraint |
| **B‑08** | Système | L’application doit garantir une **disponibilité** de 99,5 % sur l’année (hors fenêtres de maintenance planifiées). | - Disponibilité mesurée via monitoring. | Contraint |
| **B‑09** | Système | Le système doit assurer la **traçabilité** de toutes les actions (journal, horodatage, IP, utilisateur). | - Logs d’audit conservés 2 ans. | Contraint |
| **B‑10** | Système | Le traitement des données à caractère personnel doit être **conforme RGPD/DACP** (chiffrement au repos, droit d’accès, droit à l’effacement). | - Données chiffrées AES‑256.<br>- Procédure d’effacement sur demande. | Contraint |

---  

## 4️⃣ Caractérisation des besoins  

| Fonction | Critère d’appréciation | Niveau d'importance | Flexibilité | Contraintes |
|----------|------------------------|----------------------|-------------|-------------|
| B‑01 | Temps de réponse ≤ 3 s | Obligatoire | Négociable (≤ 5 s acceptable) | Aucun |
| B‑02 | Temps de chargement ≤ 4 s | Obligatoire | Négociable (≤ 6 s) | Aucun |
| B‑03 | Durée génération ≤ 5 s | Obligatoire | Négociable (≤ 8 s) | Format de sortie fixe (PDF/HTML/CSV/XLSX) |
| B‑04 | Enregistrement < 1 s | Obligatoire | Fixe | Conservation 2 ans |
| B‑05 | Filtrage ≤ 2 s | Obligatoire | Négociable (≤ 4 s) | Aucun |
| B‑06 | Purge ≤ 30 s (1 M lignes) | Obligatoire | Négociable (≤ 60 s) | Confirmation obligatoire |
| B‑07 | Authentification ≤ 1 s | Contraint | Fixe | Un seul profil autorisé |
| B‑08 | Disponibilité ≥ 99,5 % | Contraint | Fixe | Fenêtre de maintenance ≤ 4 h/mois |
| B‑09 | Traçabilité 2 ans | Contraint | Fixe | Aucun |
| B‑10 | Chiffrement AES‑256 | Contraint | Fixe | Conformité RGPD |

---  

## 5️⃣ Validation de l’expression du besoin  

| Méthode | Participants | Livrable | Traçabilité |
|---------|--------------|----------|-------------|
| **Ateliers fonctionnels** (3 sessions) | • PO : Eric Boyon (DRH) <br> • Responsable sécurité : rssi.drh@… <br> • MOE : Céline Gilliard (PNM3) <br> • Utilisateurs pilotes (services d’administration centrale) | Procès‑verbal d’atelier + matrice de traçabilité des exigences | Chaque besoin (B‑xx) relié à un **exigence ID** (ex : REQ‑A‑001) |
| **Interviews individuelles** | Utilisateurs finaux (≈ 15) | Synthèse des besoins métiers | Référencé dans le tableau d’exigences |
| **Revue documentaire** (documentation technique, requêtes SQL) | MOE, MOA | Validation des champs attendus dans les rapports | Mapping « champ base → critère » consigné |
| **Tests d’acceptation** (UAT) | Utilisateurs pilotes | Script de tests + rapport de validation | Chaque test porte le numéro du besoin (B‑xx) |

---  

## 6️⃣ Scénarios d’usage  

| Scénario | Description | Étapes clés |
|----------|-------------|-------------|
| **S‑01 – Recherche d’un agent** | L’utilisateur saisit « Dupont » dans le champ recherche. | 1. Saisie du critère.<br>2. Clique sur **Rechercher**.<br>3. Le système renvoie la liste des agents correspondants (≤ 3 s). |
| **S‑02 – Consultation du dossier** | Après S‑01, l’utilisateur clique sur le matricule RGP = 123456. | 1. Requête **get_agent_by_mat_rgp**.<br>2. Affichage du dossier complet (identité, carrière, affectations, etc.). |
| **S‑03 – Génération d’un Mini‑CV** | L’utilisateur consulte le Mini‑CV et demande le téléchargement PDF. | 1. Sélection du bouton **Export PDF**.<br>2. Le service **IJasperService** crée le fichier.<br>3. Le téléchargement démarre (< 5 s). |
| **S‑04 – Historisation** | Chaque action (S‑01 à S‑03) crée une entrée dans le journal. | 1. Enregistrement de la date, heure, utilisateur, paramètres.<br>2. Confirmation immédiate (≤ 1 s). |
| **S‑05 – Suivi d’utilisation** | Un responsable veut connaître les accès du 01/01/2025 au 31/01/2025. | 1. Accès à la page **Suivi**.<br>2. Saisie des dates.<br>3. Affichage du tableau (tri décroissant) (< 2 s). |
| **S‑06 – Purge du journal** | Après 2 ans, le responsable purge les logs antérieurs au 01/01/2023. | 1. Accès à la page **Purge**.<br>2. Saisie de la date seuil.<br>3. Confirmation, puis suppression (≤ 30 s). |
| **S‑07 – Contrôle d’accès** | Un utilisateur non‑autorisé tente d’accéder à l’application. | 1. FiltreCerbere intercepte la requête.<br>2. Redirection vers la page d’erreur (authentification refusée). |

---  

## 7️⃣ Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|-----------------|------|----------------------|----------------------|
| **DRH – Services d’administration centrale** | Utilisateur métier | Accès fiable aux dossiers historiques, génération de rapports légaux, traçabilité des consultations. | Valeur élevée (continuité de service public, conformité juridique). |
| **SG/DRH / Pôle SSI** | Responsable sécurité | Filtrage unique, chiffrement, audit, disponibilité. | Valeur critique (maîtrise du risque, conformité RGPD). |
| **Équipe MOE (PNM3, DNUM)** | Développeur / mainteneur | Spécifications claires, contraintes techniques (PostgreSQL, JasperReports), windows de maintenance. | Valeur moyenne (maintenabilité, évolutivité). |
| **Direction Générale (DG) – Pilotage** | Décideur | Reporting d’usage, indicateurs de disponibilité, conformité. | Valeur élevée (pilotage stratégique). |
| **Auditeurs internes / CNIL** | Contrôle conformité | Accès aux logs d’audit, respect du RGPD/DACP. | Valeur critique (risques légaux). |
| **Utilisateurs finaux (agents)** | Bénéficiaires indirects | Possibilité de récupérer leurs propres données (droit d’accès). | Valeur sociétale. |

---  

## 8️⃣ Contraintes et environnement  

| Type | Description |
|------|-------------|
| **Organisationnelles** | Un seul profil d’utilisateur autorisé par session (voir `MultipleProfilsException`). |
| **Réglementaires** | RGPD (article 30 – registre des traitements), DICT (disponibilité ≥ 99,5 %). |
| **Techniques** | - Base de données PostgreSQL ≥ 9.6 (scripts SQL fournis). <br> - JasperReports ≥ 6.0. <br> - Application déployée sur IaaS (ECO4) avec HTTPS obligatoire. |
| **Sécurité** | - FiltreCerbere (authentification unique). <br> - Chiffrement AES‑256 au repos. <br> - Journaux d’audit conservés 2 ans. |
| **Temporelles** | - Fenêtre de maintenance planifiée ≤ 4 h/mois. <br> - Temps de réponse maximale défini dans les critères (voir tableau 2.2). |
| **Budgétaires** | - Coût d’hébergement IaaS déjà alloué (pas de dépassement prévu). <br> - Aucun coût de licence supplémentaire (logiciels open‑source). |

---  

## 9️⃣ Critères de sélection et pondération (pour appel d’offres)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---------|--------------|-------------|----------------------|
| **Qualité fonctionnelle** | Couverture des besoins (B‑01 à B‑10) | 30 % | 0‑5 points (conformité totale = 5). |
| **Performance** | Temps de réponse, génération de rapports, purge | 20 % | Mesure en secondes (score inverse). |
| **Sécurité** | Authentification, chiffrement, traçabilité | 15 % | Vérification des certificats, audits. |
| **Disponibilité / Fiabilité** | SLA ≥ 99,5 % | 10 % | Historique d’incidents. |
| **Conformité RGPD** | Gestion des données personnelles | 10 % | Analyse d’impact DPO. |
| **Coût total de possession** | Licence, hébergement, support | 10 % | Coût annuel € / point. |
| **Méthodologie agile** | Capacité à livrer en itérations | 5 % | Présentation du backlog. |

---  

## 🔟 Glossaire et acronymes  

| Acronyme | Signification | Commentaire |
|----------|---------------|-------------|
| **ADO** | *Application de Consultation des dossiers d’archives* | Projet métier. |
| **RGP** | *Référentiel Général des Personnels* (matricule ReHucit). |
| **RRH** | *Référentiel Ressources Humaines* (matricule RenoiRH). |
| **PDF** | *Portable Document Format*. |
| **XLSX** | Format Microsoft Excel (OpenXML). |
| **CSV** | *Comma‑Separated Values*. |
| **HTML** | *HyperText Markup Language*. |
| **TXT** | *Plain Text*. |
| **DI** | *Disponibilité*. |
| **CI** | *Confidentialité*. |
| **TI** | *Intégrité*. |
| **TA** | *Traçabilité*. |
| **RGPD** | *Règlement Général sur la Protection des Données*. |
| **DACP** | *Données à Caractère Personnel*. |
| **JasperReports** | Bibliothèque Java de génération de rapports. |
| **FiltreCerbere** | Filtre d’authentification unique (SSO) déployé par la DRH. |
| **FP** | Fonction Principale (selon NF EN 16271). |
| **FC** | Fonction Contraint (selon NF EN 16271). |
| **PO** | *Product Owner* (Eric Boyon). |
| **MOE** | *Maîtrise d’Œuvre* (Équipe PNM3). |
| **MOA** | *Maîtrise d’Ouvrage* (DRH). |
| **UAT** | *User Acceptance Test* (tests d’acceptation). |
| **IAAS** | *Infrastructure as a Service*. |
| **ECO4** | Plateforme d’hébergement ministérielle. |
| **AES‑256** | Algorithme de chiffrement symétrique (256 bits). |
| **SQL** | *Structured Query Language*. |
| **JPA** | *Java Persistence API*. |
| **DTO** | *Data Transfer Object*. |
| **SLA** | *Service Level Agreement*. |
| **UML** | *Unified Modeling Language* (non utilisé dans le CCF). |
| **PMO** | *Project Management Office* (non mentionné mais référent). |

---  

## 📌 Conclusion  

Le présent **Cahier des Charges Fonctionnel** décrit de façon exhaustive les besoins fonctionnels du projet **ADO**, en les structurant selon la norme **NF EN 16271**.  

- Les **fonctions de service** (FS‑01 à FS‑10) traduisent les exigences métier et les contraintes réglementaires.  
- Les **critères de performance** et **niveaux d’importance** permettent de mesurer la valeur attendue et de piloter les offres fournisseurs.  
- La **traçabilité** entre exigences, scénarios d’usage et parties prenantes garantit la conformité aux exigences de la DICT et du RGPD.  

Ce document constitue la base contractuelle pour la phase de conception, de sélection des prestataires et de validation des livrables.  

*Version 1.0 – 27 / 03 / 2026*  

---  