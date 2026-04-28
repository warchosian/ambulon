# 📄 Cahier des Charges Fonctionnel (CCF) – **admin_ep**  
*Conforme à la norme NF EN 16271 : 2013*  

---

## 1️⃣ Présentation du projet  

| Élément | Description |
|---------|-------------|
| **Intitulé** | Administration des établissements publics (admin_ep) |
| **Contexte** | Plateforme métier du ministère de la Transition écologique et solidaire (MTES‑MCT) permettant de recenser, gérer et consulter les membres des conseils d’administration des établissements publics placés sous la tutelle du ministère (≈ 96 établissements). |
| **Enjeux stratégiques** | - Garantir la traçabilité et la conformité juridique (RGPD, DICT). <br>- Centraliser les données administratives pour faciliter la gouvernance et les audits. <br>- Automatiser l’alimentation à partir du JORF afin de réduire les saisies manuelles. |
| **Objectifs** | 1. Offrir une **interface d’écriture** (saisie manuelle). <br>2. Mettre en place une **ingestion automatique** des mentions du JORF. <br>3. Gérer **l’authentification** via Cerbère et les habilitations. <br>4. Assurer **l’archivage** des mandats échus et pièces jointes. <br>5. Proposer une **interface de lecture** (consultation, recherche). <br>6. Fournir un **module d’analyse/statistiques**. <br>7. Implémenter une **alerte de fin de mandat** (mail). |
| **Périmètre fonctionnel** | <ul><li>**Inclus** : Base de données PostgreSQL, application web Java/Struts2, modules d’ingestion JORF, moteur de recherche, alerting mail, tableau de bord statistique, authentification Cerbère, archivage, supervision.</li><li>**Exclus** : Gestion des contenus du site public, fonctionnalités de facturation, interfaces tierces non‑décrites (ex. ERP).</li></ul> |
| **Environnements** | Production, Pré‑production, Recette (hébergement MSP – centre Paris La Défense). |
| **Version cible** | 1.3.3 (déploiement en cours) – migration prévue vers Tomcat 10 / PostgreSQL 15. |
| **Références** | - Fiche‑Produit (doc *home › Fiche‑Produit*) <br>- Documentation technique (arborescence du dépôt *admin_ep*) <br>- Méta‑données (doc *admin_ep.wikisi*) |

---

## 2️⃣ Analyse de la valeur  

| Fonction de service | Type | **FP** (Fonction Principale) | **FC** (Fonction Contraint) | Critères de performance |
|---------------------|------|------------------------------|-----------------------------|--------------------------|
| **F‑01 Saisie manuelle** | Service | ✔️ | - Accès authentifié <br>- Historisation des changements | Temps de saisie ≤ 2 min / enregistrement ≤ 5 s |
| **F‑02 Ingestion JORF** | Service | ✔️ | - Source JORF officielle (URL https://echanges.dila.gouv.fr/OPENDATA/JORF/) <br>- Fréquence de mise à jour (quotidienne) | Latence ≤ 30 min après publication JORF <br>Exactitude ≥ 99 % |
| **F‑03 Authentification / Habilitation** | Service | ✔️ | - Authentification via Cerbère (ID 619) <br>- Gestion des profils (admin, opérateur, DG tutelle) | Disponibilité ≥ 99,9 % <br>Temps de connexion ≤ 2 s |
| **F‑04 Archivage** | Service | ✔️ | - Conservation légale (mandats échus, pièces) ≥ 10 ans <br>- Accès en lecture seule | Recherche archivage ≤ 3 s |
| **F‑05 Consultation / Recherche** | Service | ✔️ | - Indexation des champs (nom, établissement, mandat) <br>- Recherche plein texte | Temps de réponse ≤ 1 s (résultat < 100 enregistrements) |
| **F‑06 Statistiques & Reporting** | Service | ✔️ | - Calculs agrégés (nombre de mandats, expirations) <br>- Export CSV/Excel | Génération ≤ 5 s |
| **F‑07 Alerte expiration** | Service | ✔️ | - Notification mail au référent désigné <br>- Paramétrage du seuil (30 jours) | Envoi ≤ 15 min avant expiration |
| **F‑08 Supervision & Monitoring** | Service |  | - Intégration à la plateforme de supervision (PSIN) | Disponibilité ≥ 99,5 % |
| **F‑09 Sauvegarde & Restaurations** | Service |  | - Backup quotidien, restauration test mensuelle | RTO ≤ 4 h, RPO ≤ 1 h |
| **F‑10 Sécurité des données** | Service |  | - Conformité RGPD & DICT <br>- Chiffrement au repos (AES‑256) | Aucun incident de sécurité <br>Audit annuel positif |

---

## 3️⃣ Expression fonctionnelle du besoin  

### 3.1 Niveau système (besoin global)  

| ID | Description fonctionnelle (QUOI) | Critère d’appréciation (mesurable) | Niveau d’importance |
|----|--------------------------------|-----------------------------------|----------------------|
| **B‑01** | **Gestion centralisée du référentiel des administrateurs** | • Disponibilité ≥ 99,9 % <br>• Temps moyen de mise à jour ≤ 5 s | Obligatoire |
| **B‑02** | **Alimentation automatique à partir du JORF** | • Latence ≤ 30 min après diffusion <br>• Taux d’erreur d’import ≤ 0,5 % | Obligatoire |
| **B‑03** | **Contrôle d’accès basé sur Cerbère** | • Authentification réussie ≥ 99,9 % <br>• Temps de connexion ≤ 2 s | Obligatoire |
| **B‑04** | **Archivage complet des mandats** | • Conservation ≥ 10 ans <br>• Recherche archivage ≤ 3 s | Obligatoire |
| **B‑05** | **Recherche multi‑critères (nom, EP, mandat, etc.)** | • Temps de réponse ≤ 1 s <br>• Résultats pertinents ≥ 95 % | Obligatoire |
| **B‑06** | **Tableaux de bord statistiques** | • Génération ≤ 5 s <br>• Export CSV/Excel sans perte | Souhaitable |
| **B‑07** | **Alerte de fin de mandat par mail** | • Envoi ≤ 15 min avant expiration <br>• Taux de délivrabilité ≥ 98 % | Obligatoire |
| **B‑08** | **Supervision de l’application** | • Couverture monitoring ≥ 95 % des services <br>• Alertes en temps réel | Souhaitable |
| **B‑09** | **Sauvegarde et restauration** | • Backup quotidien <br>• RTO ≤ 4 h, RPO ≤ 1 h | Obligatoire |
| **B‑10** | **Conformité sécurité (RGPD, DICT)** | • Audit annuel sans non‑conformité <br>• Chiffrement au repos | Obligatoire |

### 3.2 Sous‑systèmes (besoins partiels)  

| ID | Description fonctionnelle | Critère d’appréciation | Niveau |
|----|---------------------------|------------------------|--------|
| **B‑01‑01** | Interface web de création/modification d’un administrateur | • Temps de saisie ≤ 2 min <br>• Validation côté serveur en ≤ 3 s | Obligatoire |
| **B‑01‑02** | Gestion des profils/rights (cerbère) | • Attribution en ≤ 5 min <br>• Rôle correctement appliqué | Obligatoire |
| **B‑02‑01** | Parser les fichiers JORF (XML/ZIP) | • Traitement complet ≤ 30 min <br>• Log d’erreurs détaillé | Obligatoire |
| **B‑02‑02** | Déduplication / rapprochement avec référentiel existant | • Taux de doublons détectés ≥ 99 % | Obligatoire |
| **B‑04‑01** | Historisation des modifications (audit) | • Enregistrement immuable <br>• Consultation ≤ 3 s | Obligatoire |
| **B‑05‑01** | Moteur de recherche plein texte (Lucene/Elasticsearch) | • Temps de réponse ≤ 800 ms <br>• Pertinence ≥ 95 % | Obligatoire |
| **B‑06‑01** | Dashboard « Statistiques mandats » | • Temps de génération ≤ 5 s <br>• Export CSV sans perte | Souhaitable |
| **B‑07‑01** | Scheduler d’envoi de mails (cron) | • Envoi fiable ≥ 98 % <br>• Gestion des rebonds | Obligatoire |
| **B‑08‑01** | Export de métriques vers PSIN | • Intervalle de collecte ≤ 5 min | Souhaitable |
| **B‑09‑01** | Script de backup PostgreSQL | • Succès ≥ 99,5 % <br>• Vérification d’intégrité | Obligatoire |
| **B‑10‑01** | Masquage / chiffrement des données sensibles (email, pièces) | • Algorithme AES‑256 <br>• Aucun accès non‑autorisé détecté | Obligatoire |

### 3.3 Composants élémentaires (besoins élémentaires)  

| ID | Description fonctionnelle | Critère d’appréciation | Niveau |
|----|---------------------------|------------------------|--------|
| **B‑01‑01‑01** | Formulaire « Ajouter un administrateur » (champs : nom, prénom, fonction, EP, mandat) | • Validation côté client (HTML5) <br>• Enregistrement ≤ 2 s | Obligatoire |
| **B‑01‑01‑02** | Page « Liste des administrateurs » avec pagination | • Chargement ≤ 1 s (page 10) | Obligatoire |
| **B‑02‑01‑01** | Job batch « Téléchargement JORF » (HTTP GET, fichier ZIP) | • Succès de téléchargement ≥ 99 % | Obligatoire |
| **B‑02‑01‑02** | Parser XML JORF → DTO | • Aucun champ obligatoire manquant <br>• Log d’erreurs < 0,1 % | Obligatoire |
| **B‑05‑01‑01** | Indexation Elasticsearch des champs : nom, EP, mandat, date | • Indexation ≤ 30 s pour 10 000 enregistrements | Obligatoire |
| **B‑07‑01‑01** | Template mail d’alerte (objet, corps, destinataire) | • Conformité RGPD <br>• Taux de délivrabilité ≥ 98 % | Obligatoire |
| **B‑09‑01‑01** | Script pg_dump compressé (gzip) | • Taille du dump ≤ 5 Go <br>• Durée ≤ 30 min | Obligatoire |
| **B‑10‑01‑01** | Module de chiffrement des pièces jointes (AES‑256) | • Aucun texte en clair dans la base <br>• Déchiffrement fonctionnel | Obligatoire |

> **Notation** : *Obligatoire* = critère indispensable, *Souhaitable* = valeur ajoutée, *Optionnel* = facultatif.

---

## 4️⃣ Caractérisation des besoins  

| Fonction | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|----------|------------------------|---------------------|-------------|-------------|
| **F‑01 Saisie manuelle** | Temps de saisie ≤ 2 min ; enregistrement ≤ 5 s | Obligatoire | Négociable (≤ 3 min) | Authentification Cerbère |
| **F‑02 Ingestion JORF** | Latence ≤ 30 min ; taux d’erreur ≤ 0,5 % | Obligatoire | Négociable (≤ 45 min) | Source officielle JORF |
| **F‑03 Authentification** | Disponibilité ≥ 99,9 % ; connexion ≤ 2 s | Obligatoire | Fixe | Cerbère ID 619 |
| **F‑04 Archivage** | Conservation ≥ 10 ans ; recherche ≤ 3 s | Obligatoire | Négociable (≥ 5 ans) | RGPD, DICT |
| **F‑05 Recherche** | Temps réponse ≤ 1 s ; pertinence ≥ 95 % | Obligatoire | Négociable (≤ 1,5 s) | Indexation Elasticsearch |
| **F‑06 Statistiques** | Génération ≤ 5 s ; export CSV | Souhaitable | Négociable (≤ 10 s) | Aucun |
| **F‑07 Alerte** | Envoi ≤ 15 min avant expiration ; délivrabilité ≥ 98 % | Obligatoire | Négociable (≤ 30 min) | SMTP institutionnel |
| **F‑08 Supervision** | Couverture ≥ 95 % ; alertes temps réel | Souhaitable | Négociable (≥ 90 %) | PSIN |
| **F‑09 Sauvegarde** | RTO ≤ 4 h ; RPO ≤ 1 h | Obligatoire | Négociable (RTO ≤ 6 h) | Hébergement MSP |
| **F‑10 Sécurité** | Audit annuel sans non‑conformité ; chiffrement AES‑256 | Obligatoire | Fixe | RGPD, DICT |

---

## 5️⃣ Validation de l’expression du besoin  

| Méthode | Description | Parties prenantes impliquées |
|---------|-------------|------------------------------|
| **Atelier MOA / MOE** | Sessions de clarification des besoins fonctionnels et techniques. | Maîtrise d’ouvrage (SG/SPES), Maîtrise d’œuvre (SG/DNUM/PNM/DPNM3/BPN), Opérateurs, DG tutelle. |
| **Interviews utilisateurs** | Recueil des attentes des utilisateurs finaux (agents SPES, DG tutelle). | Utilisateurs finaux, Responsable de produit (Christian ARBOGAST). |
| **Revue documentaire** | Analyse des spécifications existantes (Fiche‑Produit, wiki, code). | Équipe projet, Responsable sécurité (RGPD). |
| **Prototype UI** | Démonstration d’une maquette d’écran (saisie, recherche). | UI/UX designer, utilisateurs test. |
| **Validation formelle** | Signature du CCF par les représentants légaux. | **Validé par** : <br>• Maîtrise d’ouvrage – SG/SPES <br>• Maîtrise d’œuvre – SG/DNUM/PNM/DPNM3/BPN <br>• Responsable sécurité – DSI <br>• Responsable conformité RGPD – DPO |

---

## 6️⃣ Scénarios d’usage  

| # | Scénario | Type | Description (déroulement) | Critères de succès |
|---|----------|------|---------------------------|---------------------|
| **S‑01** | **Création d’un administrateur** | Nominal | L’utilisateur se connecte (Cerbère) → Accède au formulaire → Saisit les informations → Clique “Enregistrer” → Le système crée l’enregistrement et l’archive. | Enregistrement visible dans la liste < 5 s, audit créé. |
| **S‑02** | **Échec d’authentification** | Erreur | L’utilisateur saisit de mauvais identifiants → Le système renvoie un message d’erreur sans révéler le login valide. | Message d’erreur affiché < 2 s, aucune donnée exposée. |
| **S‑03** | **Import JORF quotidien** | Nominal | Le batch démarre à 02 h00 → Télécharge le fichier ZIP JORF → Décompresse, parse, déduplique, crée/actualise les administrateurs → Archive le fichier. | Tous les nouveaux mandats importés, latence ≤ 30 min, log d’exécution sans erreur. |
| **S‑04** | **Recherche d’un établissement** | Nominal | L’utilisateur saisit le nom d’un EP → Le moteur Elasticsearch renvoie les administrateurs associés. | Temps de réponse ≤ 1 s, pertinence ≥ 95 %. |
| **S‑05** | **Alerte de mandat expirant** | Nominal | Le scheduler identifie un mandat expirant dans 30 jours → Envoie un mail au référent. | Mail reçu < 15 min, contenu conforme. |
| **S‑06** | **Consultation d’un mandat archivé** | Limite | L’utilisateur recherche un mandat échus datant de 8 ans → Le système interroge les archives. | Résultat retourné ≤ 3 s, conformité RGPD. |
| **S‑07** | **Défaillance du serveur DB** | Erreur | PostgreSQL devient indisponible → Le système bascule sur le backup, alerte la supervision. | Restauration en < 4 h, aucun ticket perte de données. |
| **S‑08** | **Export de statistiques** | Nominal | L’utilisateur clique “Export CSV” → Le tableau de bord génère le fichier. | Fichier créé ≤ 5 s, intégrité des données. |

---

## 7️⃣ Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|-----------------|------|----------------------|----------------------|
| **SG/SPES** (Maîtrise d’ouvrage) | Donneur d’ordre | Fiabilité, traçabilité, conformité juridique | Garantie de l’usage métier, validation légale |
| **DG de tutelle** | Utilisateur métier | Accès aux données, alertes, reporting | Décisions de gouvernance, contrôle |
| **Opérateurs (administrateurs de la plateforme)** | Exploitant | Interface de gestion, supervision, sauvegarde | Maintenabilité, continuité de service |
| **Équipe MOE (SG/DNUM/PNM/DPNM3/BPN)** | Réalisateur | Développement, tests, déploiement, documentation | Qualité technique, respect des délais |
| **Responsable Sécurité / DPO** | Conformité | RGPD, DICT, chiffrement, audit | Conformité réglementaire, réputation |
| **Équipe Infrastructure (MSP – centre Paris La Défense)** | Hébergement | Disponibilité, backup, monitoring | Disponibilité, SLA |
| **Prestataire CGI** (développeur) | Fournisseur technique | Livraison des modules, support | Respect du périmètre fonctionnel |
| **Utilisateurs finaux (SPES, agents de tutelle)** | Consommateur | Recherche simple, accès aux archives | Satisfaction utilisateur |

---

## 8️⃣ Contraintes et environnement  

| Domaine | Contraintes |
|---------|-------------|
| **Réglementaires** | - RGPD (article 30) – droit à l’oubli, registre des traitements. <br>- DICT (déclaration d’impact) – validation 07/09/2018. |
| **Organisationnelles** | - Respect du planning de migration vers Tomcat 10 / PostgreSQL 15 (Q3‑2026). <br>- Alignement avec la politique de conteneurisation (Docker/K8s) en cours. |
| **Techniques** | - Base PostgreSQL 9.6.11 en prod → upgrade prévu vers 15. <br>- Serveur d’applications Tomcat 9.0.8 → migration Tomcat 10. <br>- Utilisation d’Elasticsearch 7.x pour la recherche. |
| **Sécurité** | - Authentification unique via Cerbère (ID 619). <br>- Chiffrement AES‑256 des pièces jointes. <br>- Accès réseau limité aux plages internes du ministère. |
| **Performance** | - Disponibilité globale ≥ 99,9 % (SLA). <br>- Temps de réponse < 2 s pour les écrans critiques. |
| **Budgétaires** | - Budget total du projet 2025 : 350 k € (incl. licences, hébergement, migration). |
| **Temporalité** | - Livraison version 1.4 (migration complète) prévue avant fin 2026. |
| **Environnement de développement** | - Maven multi‑modules (adminep‑database, adminep‑web, adminep‑deployment). <br>- Gestion des dépendances via pom.xml. |
| **Interopérabilité** | - Exposition d’API REST pour l’alimentation JORF (future). <br>- Intégration à la plateforme de supervision PSIN. |

---

## 9️⃣ Critères de sélection et pondération (pour appel d’offres)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---------|--------------|--------------|----------------------|
| **Coût** | Prix global (licences, services, maintenance) | 25 % | € / point (plus bas = meilleur) |
| **Conformité RGPD / DICT** | Procédures d’anonymisation, registre, audit | 20 % | Oui/Non + score d’audit |
| **Qualité technique** | Architecture (micro‑services), compatibilité Tomcat 10, PostgreSQL 15 | 15 % | Evaluation technique (0‑5) |
| **Performance** | Temps de réponse, disponibilité, latence ingestion JORF | 10 % | Tests de charge (benchmark) |
| **Sécurité** | Chiffrement, gestion des droits, journalisation | 10 % | Vérification des mécanismes |
| **Maintenabilité** | Documentation, tests unitaires, CI/CD | 10 % | Analyse du dépôt Git |
| **Expérience du prestataire** | Références similaires (administration publique) | 5 % | Nombre de projets réussis |
| **Plan de migration** | Méthodologie upgrade Tomcat/PostgreSQL | 5 % | Qualité du planning proposé |

> **Score final** = Σ (pondération × note) / 100. Le prestataire doit atteindre **≥ 70 %** pour être retenu.

---

## 🔟 Glossaire et acronymes  

| Acronyme / Terme | Définition |
|------------------|------------|
| **ADMINEP** | Administration des établissements publics (application métier). |
| **JORF** | Journal officiel de la République française (source officielle des nominations). |
| **Cerbère** | Service d’authentification unique du ministère (SSO). |
| **RGPD** | Règlement général sur la protection des données (UE). |
| **DICT** | Déclaration d’incident de sécurité de données à caractère personnel. |
| **SPES** | Service de la politique de l’État (maîtrise d’ouvrage). |
| **DG** | Direction Générale (utilisateur métier). |
| **PG** | PostgreSQL (SGBD). |
| **Tomcat** | Serveur d’applications Java (Servlet container). |
| **Elasticsearch** | Moteur de recherche plein texte. |
| **PSIN** | Plateforme de supervision du ministère (monitoring). |
| **SLA** | Service Level Agreement – niveau d’engagement de service. |
| **RTO** | Recovery Time Objective – délai maximal de remise en service. |
| **RPO** | Recovery Point Objective – perte maximale de données acceptable. |
| **DAO** | Data Access Object – couche d’accès aux données. |
| **ACAI** | Architecture Cloud d’Application Intergouvernementale (plateforme de déploiement). |
| **IaaS** | Infrastructure as a Service (hébergement cloud). |
| **CSV** | Comma‑Separated Values – format d’export tabulaire. |
| **REST** | Representational State Transfer – style d’architecture d’API. |
| **MCT** | Ministère de la Transition écologique et solidaire. |
| **MP** | Marché public (procédure d’appel d’offres). |

---  

*Document élaboré le **27 avril 2026** – Version 1.0 – Conformité NF EN 16271 : 2013*  

---  

**Fin du CCF**.  