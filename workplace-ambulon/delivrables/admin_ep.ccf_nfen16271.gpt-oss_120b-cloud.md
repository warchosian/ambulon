# 📄 Cahier des Charges Fonctionnel (CCF) – **admin_ep**  
*Conforme à la norme NF EN 16271 :2013 – Management par la valeur*  

> **Version** : 1.0 – 2024‑04‑27  
> **Document unique** – Markdown (compatible avec les outils de gestion d’exigences)  

---  

## 1️⃣ Présentation du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | **admin_ep** – Administration des établissements publics (MTES‑MCT) |
| **Références** | - Wiki : `admin_ep.wiki.md`  <br> - Fiche produit : `home__Fiche-Produit.md`  <br> - Documentation JORF : `doc-JORF-BO.md` |
| **Contexte et enjeux stratégiques** | - Mutualiser la gestion des listes des membres des conseils d’administration des 96 établissements publics placés sous la tutelle du ministère. <br> - Garantir la traçabilité et la pérennité des mandats (archivage, alertes). <br> - Automatiser l’alimentation à partir du Journal Officiel de la République Française (JORF). |
| **Objectifs du projet** | 1. **Fiabilité** : disposer d’une source unique, à jour, vérifiable. <br> 2. **Valeur métier** : faciliter la consultation et la mise à jour des mandats pour les services de tutelle (SPES, DG de tutelle, opérateurs). <br> 3. **Sécurité & conformité** : respect du RGPD, de la DICT et des exigences d’authentification (Cerbère). |
| **Périmètre fonctionnel** | **Inclus**  <br> • Interface d’écriture (CRUD) des établissements, mandats, gestionnaires. <br> • Interface de lecture (consultation, recherche). <br> • Module d’import JORF (extraction, enrichissement). <br> • Gestion des alertes de fin de mandat (mail). <br> • Statistiques globales. <br> • Archivage des mandats et pièces jointes. <br> • Authentification Cerbère (rôles). <br> **Exclus**  <br> • Gestion du budget ou de la comptabilité des établissements. <br> • Gestion des contenus du site public (CMS). |

---  

## 2️⃣ Analyse de la valeur  

### 2.1 Fonctions de service (FS)  

| N° | Fonction de service | Type | Description (QUOI) | Critères de performance associés |
|---|---|---|---|---|
| **FS‑01** | **Gestion du référentiel des établissements et mandats** | **FP** (Fonction Principale) | Permettre la création, la mise à jour, la suppression et la consultation des établissements, des mandats et des gestionnaires. | - **Disponibilité** : ≥ 99 % (heure ouvrée). <br> - **Temps de réponse** : ≤ 2 s pour les opérations CRUD. <br> - **Intégrité des données** : contrôle de cohérence (FK, contraintes métier). |
| **FS‑02** | **Alimentation automatique à partir du JORF** | **FC** (Fonction Contraint) | Importer quotidiennement les articles du JORF, extraire les nominations et les associer aux établissements. | - **Fréquence** : une fois par jour (cron). <br> - **Taux de réussite** : ≥ 95 % des articles correctement traités. <br> - **Traçabilité** : log d’import avec horodatage. |
| **FS‑03** | **Recherche d’information** | **FP** | Offrir un moteur de recherche multi‑critères (nom établissement, personne, mandat, etc.). | - **Temps de réponse** : ≤ 1 s pour 95 % des requêtes. <br> - **Pertinence** : ≥ 80 % de résultats pertinents (test utilisateur). |
| **FS‑04** | **Alertes de fin de mandat** | **FP** | Générer et envoyer automatiquement des notifications par mail aux référents avant l’expiration d’un mandat. | - **Délai d’envoi** : ≤ 24 h avant expiration. <br> - **Taux d’envoi** : 100 % des alertes prévues. |
| **FS‑05** | **Statistiques & reporting** | **FP** | Produire des indicateurs agrégés (nombre de mandats, répartition par type, évolution temporelle). | - **Mise à jour** : quotidienne. <br> - **Exactitude** : ± 2 % (validation avec jeu de données de référence). |
| **FS‑06** | **Authentification & habilitation** | **FC** | Garantir l’accès aux fonctions selon les rôles (Cerbère, profils BaseAdmin). | - **Conformité RGPD** : gestion du consentement, droit d’accès. <br> - **Temps d’authentification** : ≤ 1 s. |
| **FS‑07** | **Archivage des mandats et pièces** | **FC** | Conserver l’historique complet des mandats (échéances, pièces jointes). | - **Durée de conservation** : minimum 10 ans. <br> - **Intégrité** : hash SHA‑256 stocké. |
| **FS‑08** | **Interface utilisateur (Web)** | **FP** | Fournir des écrans ergonomiques (CRUD, recherche, tableau de bord). | - **Usabilité** : score ≥ 4/5 (questionnaire SUS). <br> - **Compatibilité navigateurs** : Chrome, Firefox, Edge (versions ≥ 90). |

> **Note** : *FP* = Fonction Principale (justifie l’existence du système).  
> *FC* = Fonction Contraint (imposée par le contexte réglementaire ou technique).

### 2.2 Pondération des critères (exemple)  

| Critère | Pondération | Type |
|---|---|---|
| Disponibilité | 20 % | Obligatoire |
| Temps de réponse | 15 % | Obligatoire |
| Sécurité (RGPD, Cerbère) | 20 % | Obligatoire |
| Intégrité & traçabilité des données | 15 % | Obligatoire |
| Pertinence de la recherche | 10 % | Souhaitable |
| Usabilité UI | 10 % | Souhaitable |
| Compatibilité / Portabilité | 5 % | Optionnel |

---  

## 3️⃣ Expression fonctionnelle du besoin  

### 3.1 Niveau **Système** (B‑01)  

| ID | Description fonctionnelle (QUOI) | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|---|
| **B‑01** | **Gestion centralisée du référentiel établissements‑mandats** | - Disponibilité ≥ 99 % (heure ouvrée) <br> - Temps de réponse ≤ 2 s (CRUD) <br> - Historisation ≥ 10 ans | Obligatoire | Fixe | Conformité RGPD, DICT |
| **B‑02** | **Alimentation JORF automatisée** | - Exécution quotidienne <br> - Taux de succès ≥ 95 % <br> - Log détaillé | Obligatoire | Négociable (fréquence) | Accès ouvert aux flux JORF |
| **B‑03** | **Moteur de recherche multi‑critères** | - Temps de réponse ≤ 1 s (95 % des requêtes) <br> - Pertinence ≥ 80 % | Obligatoire | Négociable (nombre de filtres) | Aucun |
| **B‑04** | **Alertes mandat expirant** | - Envoi mail ≤ 24 h avant fin <br> - Taux d’envoi 100 % | Obligatoire | Négociable (canal de diffusion) | Respect des règles de messagerie interne |
| **B‑05** | **Statistiques et reporting** | - Mise à jour quotidienne <br> - Exactitude ± 2 % | Souhaitable | Négociable (granularité) | Aucun |
| **B‑06** | **Gestion des habilitations (Cerbère)** | - Authentification ≤ 1 s <br> - Gestion des rôles (admin, référent) | Obligatoire | Fixe | Conformité RGPD, Charte de sécurité |
| **B‑07** | **Archivage des mandats & pièces** | - Conservation ≥ 10 ans <br> - Vérification d’intégrité (hash) | Obligatoire | Fixe | RGPD, DICT |
| **B‑08** | **Interface Web ergonomique** | - Score SUS ≥ 4/5 <br> - Compatibilité navigateurs ≥ 90 | Souhaitable | Négociable (thème) | Accessibilité WCAG 2.1 AA |

### 3.2 Niveau **Sous‑système** (exemple)  

| ID | Description fonctionnelle | Critère d’appréciation | Niveau d’importance |
|---|---|---|---|
| **B‑01‑01** | Gestion des établissements (CRUD) | Temps de réponse ≤ 2 s, cohérence FK | Obligatoire |
| **B‑01‑02** | Gestion des mandats (CRUD + historique) | Historisation ≥ 10 ans, auditabilité | Obligatoire |
| **B‑01‑03** | Gestion des gestionnaires (rôles Cerbère) | Mapping 1‑N, mise à jour en temps réel | Obligatoire |
| **B‑02‑01** | Extraction des articles JORF | Parsing XML/HTML, taux de succès ≥ 95 % | Obligatoire |
| **B‑02‑02** | Enrichissement des entités (nom, fonction) | Matching > 90 % avec référentiel interne | Souhaitable |
| **B‑03‑01** | Indexation plein‑texte (ElasticSearch) | Temps de réponse ≤ 1 s, disponibilité ≥ 99 % | Obligatoire |
| **B‑04‑01** | Scheduler des alertes (Quartz) | Exécution fiable, logs d’envoi | Obligatoire |
| **B‑05‑01** | Tableaux de bord (KPI) | Actualisation quotidienne, export CSV | Souhaitable |
| **B‑06‑01** | Authentification SSO Cerbère | Temps d’auth ≤ 1 s, logs d’accès | Obligatoire |
| **B‑07‑01** | Stockage des pièces jointes (Blob) | Intégrité SHA‑256, durée ≥ 10 ans | Obligatoire |
| **B‑08‑01** | UI responsive (Bootstrap) | Score SUS ≥ 4/5, test cross‑browser | Souhaitable |

### 3.3 Niveau **Élémentaire** (exemple)  

| ID | Description fonctionnelle | Critère d’appréciation |
|---|---|---|
| **B‑01‑01‑01** | Formulaire “Création établissement” | Validation front‑end, temps de traitement ≤ 2 s |
| **B‑01‑02‑01** | Enregistrement mandat avec date de début/fin | Contrôle de cohérence (date fin > date début) |
| **B‑02‑01‑01** | Script “JORF Extractor” (Java) | Taux de parsing ≥ 95 % |
| **B‑03‑01‑01** | Index ElasticSearch “mandat” | Latence ≤ 200 ms |
| **B‑04‑01‑01** | Job Quartz “MandatAlert” | Exécution dans les 5 min précédant la date cible |
| **B‑06‑01‑01** | Filtre “SecurityFilter” (Vertigo) | Authentification ≤ 1 s, refus 403 si non autorisé |
| **B‑07‑01‑01** | Table “mandat_archive” (PostgreSQL) | Index sur date d’expiration, vérif. hash |
| **B‑08‑01‑01** | Page “Liste établissements” (JSP) | Temps de rendu ≤ 1 s, pagination 25 lignes |

---  

## 4️⃣ Caractérisation des besoins  

| Fonction de service | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|
| **FS‑01** (Gestion référentiel) | Disponibilité ≥ 99 % <br> Temps de réponse ≤ 2 s | Obligatoire | Fixe | RGPD, DICT |
| **FS‑02** (Alimentation JORF) | Fréquence = quotidienne <br> Taux de succès ≥ 95 % | Obligatoire | Négociable (heure) | Accès aux flux JORF |
| **FS‑03** (Recherche) | Temps de réponse ≤ 1 s <br> Pertinence ≥ 80 % | Obligatoire | Négociable (nombre filtres) | Aucun |
| **FS‑04** (Alertes) | Envoi ≤ 24 h avant fin <br> 100 % d’envoi | Obligatoire | Négociable (canal) | Politique mail interne |
| **FS‑05** (Statistiques) | Actualisation quotidienne <br> Exactitude ± 2 % | Souhaitable | Négociable (granularité) | Aucun |
| **FS‑06** (Authentification) | Temps ≤ 1 s <br> Gestion Cerbère | Obligatoire | Fixe | RGPD, Charte sécurité |
| **FS‑07** (Archivage) | Conservation ≥ 10 ans <br> Vérif. hash | Obligatoire | Fixe | RGPD, DICT |
| **FS‑08** (UI) | Score SUS ≥ 4/5 <br> Compatibilité navigateurs | Souhaitable | Négociable (thème) | WCAG 2.1 AA |

---  

## 5️⃣ Validation de l’expression du besoin  

| Étape | Méthode | Participants | Livrable | Traçabilité |
|---|---|---|---|---|
| 5.1 | Ateliers de cadrage (2 j) | Maîtrise d’ouvrage (SG/SPES), Maîtrise d’œuvre, Responsable Sécurité, Chef de produit | Cahier des charges fonctionnel (ce document) | Référence : B‑xx (ID) |
| 5.2 | Interviews utilisateurs (opérateurs, DG de tutelle) | Utilisateurs finaux | Synthèse besoins fonctionnels | Matrice besoins ↔ fonctions (B‑01…B‑08) |
| 5.3 | Validation formelle | Comité de pilotage (MOA, MOE, Prestataire) | Procès‑verbal de validation | Signatures numériques, lien vers le CCF |
| 5.4 | Revue de conformité RGPD/DICT | DPO, RSSI | Rapport de conformité | Annexes RGPD, DICT |

---  

## 6️⃣ Scénarios d’usage  

| Type de scénario | Description | Flux principal | Variantes / erreurs |
|---|---|---|---|
| **S‑NOM‑01** (Nominal) | **Création d’un mandat** : L’opérateur se connecte, crée un établissement, saisit un mandat, le sauvegarde. | Auth → Formulaire → Validation → Persistance → Confirmation | - Erreur de validation (date fin < date début) → message d’erreur <br> - Contrainte DB (FK manquant) → rollback |
| **S‑NOM‑02** (Nominal) | **Import JORF** : Le job quotidien récupère le flux, extrait les nominations, crée/actualise les mandats. | Scheduler → JORFExtractor → Matching → Upsert → Log | - Flux indisponible → alerte mail <br> - Parsing partiel → mise en file d’attente pour re‑traitement |
| **S‑ERR‑01** (Erreur) | **Échec d’authentification** : Un utilisateur non autorisé tente d’accéder à la page de gestion. | Auth → Refus → Redirection vers page d’erreur | - Compte désactivé → message “compte inactif” |
| **S‑LIM‑01** (Limite) | **Mandat expiré** : Le job d’alerte détecte un mandat expiré depuis > 30 jours. | Scheduler → Scan → Envoi mail de rappel → Archivage | - Mail non délivré → relance automatique après 2 h |
| **S‑LIM‑02** (Limite) | **Recherche massive** : L’utilisateur lance une recherche sur 10 000 lignes. | UI → Requête → ElasticSearch → Pagination | - Temps de réponse > 2 s → affichage d’un indicateur “chargement long” |

---  

## 7️⃣ Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|---|---|---|---|
| **SG / SPES** (Maîtrise d’ouvrage) | Commanditaire | Fiabilité, traçabilité, conformité RGPD/DICT | Garantie de la pertinence métier |
| **DG de tutelle** | Utilisateur principal | Consultation, alertes, reporting | Améliore la prise de décision |
| **Opérateurs (gestionnaires)** | Utilisateurs opérationnels | Interface d’écriture, recherche, archivage | Accélère la mise à jour des mandats |
| **SG / SNUM / PNM / DPNM3 / BPN** (Maîtrise d’œuvre) | Responsable technique & fonctionnel | Respect des contraintes techniques, planning | Assure la livrabilité du projet |
| **CGI** (Prestataire) | Fournisseur de développement | Implémentation conforme, support | Réduction des coûts de maintenance |
| **DPO / RSSI** | Sécurité & conformité | RGPD, DICT, auditabilité | Réduction des risques légaux |
| **Direction du Système d’Information (DSI)** | Hébergement & exploitation | Disponibilité, monitoring, sauvegarde | Garantit la continuité de service |
| **Utilisateurs finaux (public)** | Consultation en lecture seule | Accès aux informations publiques | Transparence de l’administration |

---  

## 8️⃣ Contraintes et environnement  

| Domaine | Contraintes |
|---|---|
| **Organisationnelles** | - Respect du planning de montée de version (Tomcat 10, PostgreSQL 15). <br> - Coordination entre MOA, MOE et Prestataire. |
| **Réglementaires** | - RGPD (droit d’accès, conservation). <br> - DICT (évaluation sécurité). <br> - Charte Cerbère (authentification unique). |
| **Techniques** | - Serveur d’application : Tomcat 9 → 10 (migration). <br> - Base : PostgreSQL 9.6 → 15 (migration). <br> - Recherche : ElasticSearch (version 7.x). <br> - Conteneurisation (Docker) en cours. |
| **Temps & Budget** | - Livraison prévue Q4 2024. <br> - Budget max : € 350 k (développement, tests, migration). |
| **Qualité** | - Tests unitaires ≥ 80 % de couverture. <br> - Tests d’intégration & charge (≥ 500 req/s). <br> - Documentation technique & fonctionnelle à jour. |

---  

## 9️⃣ Critères de sélection et pondération (pour appel d’offres)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---|---|---|---|
| **C‑01** | **Compétences fonctionnelles** (gestion référentiel, JORF) | 25 % | 0‑5 (expertise démontrée) |
| **C‑02** | **Compétences techniques** (Java 8, Tomcat 10, PostgreSQL 15, ElasticSearch) | 20 % | 0‑5 (certifications, références) |
| **C‑03** | **Conformité RGPD / DICT** | 15 % | 0‑5 (audit antérieur) |
| **C‑04** | **Méthodologie Agile / DevOps** | 10 % | 0‑5 (processus, CI/CD) |
| **C‑05** | **Coût total (TCO)** | 15 % | Prix forfaitaire / TCO estimé |
| **C‑06** | **Délais de mise en production** | 10 % | Planning proposé |
| **C‑07** | **Qualité documentaire** | 5 % | Livrables fournis (Cahier des charges, guides) |

---  

## 🔟 Glossaire & acronymes  

| Acronyme | Signification |
|---|---|
| **CCF** | Cahier des Charges Fonctionnel |
| **FP** | Fonction Principale |
| **FC** | Fonction Contraint |
| **RGPD** | Règlement Général sur la Protection des Données |
| **DICT** | Déclaration d’Intérêt à la Sécurité des Systèmes d’Information |
| **CERBERE** | Système d’authentification unique de l’État |
| **JORF** | Journal Officiel de la République Française |
| **SUS** | System Usability Scale |
| **WCAG** | Web Content Accessibility Guidelines |
| **DAO** | Data Access Object |
| **POJO** | Plain Old Java Object |
| **SQS** | Simple Queue Service (utilisé pour le découpage de flux JORF) |
| **KPI** | Key Performance Indicator |
| **SLA** | Service Level Agreement |
| **DSI** | Direction des Systèmes d’Information |
| **MOA** | Maîtrise d’Ouvrage |
| **MOE** | Maîtrise d’Œuvre |
| **SNUM** | Service Numérique |
| **PNM** | Programme National de Modernisation |
| **DPNM3** | Direction du Programme Numérique 3 |
| **BPN** | Bureau de Pilotage Numérique |
| **ACAI** | Architecture Cloud d’Application Intergouvernementale |
| **IaaS** | Infrastructure as a Service |

---  

## 📌 Conclusion  

Le présent **Cahier des Charges Fonctionnel** décrit, de façon exhaustive et **sans aucune prescription technique**, les besoins fonctionnels, les fonctions de service, les critères de performance, les parties prenantes et les contraintes du projet **admin_ep**.  

Il constitue le socle de référence pour :

* La rédaction des **Cahiers des Charges Techniques** (CCT) et des **Spécifications d’Architecture**.  
* La conduite de la **procédure de passation** (appel d’offres) en conformité avec les exigences de la norme NF EN 16271.  
* Le pilotage, la **validation** et le **suivi** de la réalisation jusqu’à la mise en production.  

---  

*Document préparé par :* **[Votre Nom] – Expert Management par la Valeur**  
*Date* : 2024‑04‑27   (Version 1.0)  



---  



*Ce CCF doit être maintenu à jour tout au long du cycle de vie du projet, chaque évolution étant tracée dans le registre de modifications.*  



---  



**Fin du document**