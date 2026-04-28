# Cahier des Charges Fonctionnel (CCF) – **SIREINES**  
*Conforme à la norme NF EN 16271 :2013 (Management par la valeur)*  

---  

## 1. Présentation du projet  

| Élément | Description |
|---|---|
| **Nom du projet** | SIREINES – Système d’Information de Recensement des Experts et Spécialistes |
| **Contexte** | Application métier du Ministère de la Transition Écologique (DRI/AST4) qui recense, suit et valorise les demandes de qualification des agents par les comités de domaine. |
| **Objectifs** | 1️⃣ Assurer la traçabilité et la mise à jour du répertoire d’experts. <br>2️⃣ Faciliter la saisie, le suivi et la clôture des dossiers de qualification. <br>3️⃣ Produire des extractions et rapports (BIRT) à destination des services internes et de la CNIL. <br>4️⃣ Garantir la conformité RGPD et la disponibilité en production (IaaS ECO4). |
| **Périmètre fonctionnel** | • Gestion du cycle de vie des **dossiers** (création, modification, suivi, clôture). <br>• Gestion des **agents**, **référentiels** (structures, comités, corps, grades, mots‑clé, qualifications). <br>• **Import** de fichiers (CSV, Excel) et génération d’une **synthèse d’import**. <br>• **Export / extraction** de jeux de données (extractions totales, par année, pyramides d’âge, fréquence mots‑clé, etc.). <br>• **Recherche** plein‑texte (Elasticsearch) sur les dossiers. <br>• **Production de rapports** BIRT (statistiques, états d’avancement). <br>• Gestion des **utilisateurs / authentification** (SSO, rôle R_ADMIN). <br>• **Administration** (paramétrage, logs, monitoring). |
| **Exclusions** | • Outils de développement (Eclipse, Docker‑Compose interne). <br>• Gestion de la facturation ou du budget (hors suivi interne). <br>• Interfaces mobiles natives (seulement interface web). |
| **Environnement cible** | • Serveurs Linux (Docker + Tomcat 7, PostgreSQL 14). <br>• Déploiement en IaaS (ECO4) – production, pré‑prod, recette. <br>• Accès via navigateur (HTTPS). |
| **Livrables attendus** | • Application web (WAR) déployable. <br>• Scripts d’initialisation / migration de la base (SQL). <br>• Docker‑Compose & Dockerfile. <br>• Documentation d’installation, d’exploitation et de recette. <br>• Jeux de tests fonctionnels et de performance. |

---  

## 2. Analyse de la valeur  

| # | Fonction de service | Type | Description | Critères de performance |
|---|---|---|---|---|
| **FP‑01** | **Gestion du cycle de vie des dossiers de qualification** | **Principale** | Saisie, suivi, mise à jour et clôture des dossiers d’expertise. | Temps de saisie ≤ 5 min / dossier, taux d’erreur ≤ 1 % (validation métier). |
| **FC‑01** | **Conformité réglementaire (RGPD, CNIL)** | **Contraint** | Respect des obligations de protection des données personnelles. | Audit RGPD = OK, traçabilité des accès, chiffrement des données sensibles. |
| **FC‑02** | **Disponibilité & performance** | **Contraint** | Service disponible ≥ 99,5 % 24/7, temps de réponse < 2 s (pages) / < 5 s (extractions). | SLA = 99,5 % mensuel, temps de réponse mesuré. |
| **FC‑03** | **Sécurité (HTTPS, authentification, rôles)** | **Contraint** | Authentification via SSO, gestion des rôles (R_ADMIN, utilisateurs). | Aucun accès non‑autorisé détecté sur les logs d’audit. |
| **FP‑02** | **Gestion des référentiels (structures, comités, corps, grades, mots‑clé, qualifications)** | **Service** | Administration des listes de référence utilisées dans les dossiers. | Temps de mise à jour ≤ 10 min, cohérence référentielle garantie (FK). |
| **FP‑03** | **Import de fichiers et synthèse d’import** | **Service** | Chargement de fichiers (CSV, Excel), validation, génération d’un rapport de synthèse. | Taux de succès d’import ≥ 95 %, durée d’import < 3 min / 10 Mo. |
| **FP‑04** | **Export / extraction de jeux de données** | **Service** | Génération d’extractions (totales, par année, pyramides d’âge, fréquence mots‑clé, etc.). | Temps d’extraction < 30 s, formats CSV/XLSX/BIRT. |
| **FP‑05** | **Recherche plein‑texte (Elasticsearch)** | **Service** | Recherche rapide sur dossiers, mots‑clé, qualifications. | Temps de recherche < 1 s, pertinence ≥ 90 % (tests utilisateurs). |
| **FP‑06** | **Production de rapports BIRT** | **Service** | Rapports statistiques, états de suivi, export PDF/HTML. | Génération < 5 s, conformité du rendu (BIRT 4.3). |
| **FP‑07** | **Gestion des utilisateurs / rôles** | **Service** | Création, modification, désactivation des comptes, attribution des rôles. | Temps de provisioning ≤ 5 min, audit complet des changements. |
| **FP‑08** | **Administration & monitoring** | **Service** | Gestion des logs, métriques (Docker, Tomcat, PostgreSQL), sauvegarde des volumes. | Rétention logs ≥ 30 j, sauvegarde BDD quotidienne. |

---  

## 3. Expression fonctionnelle du besoin  

### 3.1 Niveau système (B‑01) – Besoin global  

| ID | Description fonctionnelle (QUOI) | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|---|
| **B‑01** | Fournir une application web sécurisée, disponible et conforme RGPD pour la gestion du répertoire d’experts. | Satisfaction du cahier des charges fonctionnel + SLA ≥ 99,5 % + audit RGPD OK | **Obligatoire** | **Fixe** | RGPD, ISO 27001, hébergement IaaS (ECO4). |

### 3.2 Niveau sous‑système (B‑01‑01 … B‑01‑08)  

| ID | Fonction (QUOI) | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|---|
| **B‑01‑01** | Gestion du cycle de vie des dossiers (création, suivi, clôture). | 100 % des dossiers créés avec statut initial, mise à jour possible, clôture archivable. | Obligatoire | Négociable (UI) | Respect des règles métier (qualifications). |
| **B‑01‑02** | Gestion des référentiels (structures, comités, corps, grades, mots‑clé, qualifications). | Cohérence référentielle (FK), temps de mise à jour ≤ 10 min. | Obligatoire | Négociable (interface) | Aucun doublon, historisation des changements. |
| **B‑01‑03** | Import de fichiers et génération de synthèse. | Taux de succès ≥ 95 %, durée d’import < 3 min / 10 Mo. | Souhaitable | Négociable | Formats CSV, Excel, validation syntaxique. |
| **B‑01‑04** | Export / extraction de jeux de données. | Export complet, format CSV/XLSX, temps < 30 s. | Souhaitable | Négociable | Limites de taille (max = 5 Go). |
| **B‑01‑05** | Recherche plein‑texte sur dossiers et référentiels. | Temps de réponse < 1 s, pertinence ≥ 90 %. | Souhaitable | Négociable | Indexation Elasticsearch, mise à jour quotidienne. |
| **B‑01‑06** | Production de rapports BIRT (statistiques, états). | Génération < 5 s, rendu conforme BIRT 4.3. | Souhaitable | Négociable | Templates fournis, export PDF/HTML. |
| **B‑01‑07** | Gestion des utilisateurs, authentification et rôles. | Provisioning ≤ 5 min, journalisation complète. | Obligatoire | Négociable | SSO (CAS/OIDC), chiffrement mots‑de‑passe. |
| **B‑01‑08** | Administration, monitoring et sauvegarde. | Sauvegarde BDD quotidienne, logs 30 j, disponibilité ≥ 99,5 %. | Obligatoire | Négociable | Docker‑Compose, volumes persistants, alerting (Prometheus/Alertmanager). |

### 3.3 Niveau élémentaire (exemple B‑01‑01‑01 … B‑01‑01‑04)  

| ID | Élément fonctionnel | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|---|---|---|---|---|---|
| **B‑01‑01‑01** | Formulaire de création de dossier (page Accueil.do → “Nouveau dossier”). | Champ obligatoire = 5, validation côté serveur, temps de saisie ≤ 5 min. | Obligatoire | Négociable (layout) | Validation métier (ex : agent existant). |
| **B‑01‑01‑02** | Workflow de suivi (états : En cours, En attente, Validé, Clôturé). | Transition d’état conforme au diagramme, historique complet. | Obligatoire | Négociable | Historisation immutable. |
| **B‑01‑01‑03** | Gestion des pièces jointes (PDF, DOCX). | Taille max = 10 Mo, téléchargement < 5 s. | Souhaitable | Négociable | Stockage dans volume Docker. |
| **B‑01‑01‑04** | Fonction de clôture archivistique (déplacement vers volume d’archive). | Archive créée, accès en lecture‑seule, suppression après 5 ans. | Souhaitable | Négociable | Conformité DUA = 5 ans. |

*(Les tables élémentaires sont générées de façon similaire pour chaque sous‑système.)*

---  

## 4. Caractérisation des besoins  

| Fonction | Critère d’appréciation | Niveau d'importance | Flexibilité | Contraintes |
|---|---|---|---|---|
| Gestion du cycle de vie des dossiers | 100 % des dossiers créés avec statut initial, mise à jour possible, clôture archivable | Obligatoire | Fixe | Règles métier, auditabilité |
| Gestion des référentiels | Cohérence référentielle, mise à jour ≤ 10 min | Obligatoire | Négociable (UI) | Aucun doublon, historique |
| Import de fichiers | Taux de succès ≥ 95 %, durée < 3 min / 10 Mo | Souhaitable | Négociable | Formats CSV/Excel, validation |
| Export / extraction | Export complet, format CSV/XLSX, temps < 30 s | Souhaitable | Négociable | Limite taille 5 Go |
| Recherche plein‑texte | Temps < 1 s, pertinence ≥ 90 % | Souhaitable | Négociable | Indexation Elasticsearch |
| Rapports BIRT | Génération < 5 s, rendu conforme | Souhaitable | Négociable | Templates BIRT 4.3 |
| Gestion des utilisateurs | Provisioning ≤ 5 min, journalisation | Obligatoire | Négociable | SSO, chiffrement |
| Administration & monitoring | Sauvegarde quotidienne, logs 30 j, disponibilité ≥ 99,5 % | Obligatoire | Négociable | Docker‑Compose, alerting |

---  

## 5. Validation de l'expression du besoin  

| Méthode | Description | Parties prenantes impliquées | Traçabilité |
|---|---|---|---|
| **Ateliers fonctionnels** | Sessions de 2 h avec MOA (CGDD/AST4), MOE (Klee Group/Acteurs internes) pour recenser les besoins métiers. | MOA, MOE, équipes sécurité, DSI. | Comptes‑rendus → tickets JIRA (ID = REQ‑SIREINES‑xx). |
| **Interviews utilisateurs** | Entretiens ciblés (agents, référents, chefs de service) pour valider les scénarios d’usage. | Utilisateurs finaux, chefs de bureau. | Synthèse → matrice de traçabilité B‑xx ↔︎ REQ‑xx. |
| **Revue documentaire** | Analyse des exigences légales (RGPD, CNIL) et des documents de déploiement (Docker, Maven). | DPO, Responsable conformité. | Checklist conformité → annexes. |
| **Prototype UI** | Maquette interactive (Figma) validée avant le développement. | UI/UX, MOA. | Versionning maquette → lien dans le CCF. |
| **Tests d’acceptation** | Jeux de tests fonctionnels (T‑01 à T‑12) exécutés en pré‑prod. | QA, MOA. | Rapport de campagne → référence dans le tableau de validation. |

---  

## 6. Scénarios d’usage  

### 6.1 Scénarios nominaux  

| N° | Acteur | Description | Résultat attendu |
|---|---|---|---|
| **S‑N‑01** | Agent | Crée un nouveau dossier, saisit les mots‑clé, associe un référentiel, soumet. | Dossier enregistré, état *En cours*, notification mail. |
| **S‑N‑02** | Gestionnaire | Recherche dossiers par mot‑clé, filtre par année, exporte CSV. | Fichier CSV contenant les dossiers filtrés, temps < 30 s. |
| **S‑N‑03** | Administrateur | Déploie une nouvelle version via Docker‑Compose (mise à jour du WAR). | Application redémarrée sans perte de données, SLA maintenu. |
| **S‑N‑04** | Responsable qualité | Génère le rapport BIRT “Pyramide des âges”. | PDF disponible, rendu conforme au modèle. |

### 6.2 Scénarios d’erreur  

| N° | Acteur | Situation | Gestion de l’erreur |
|---|---|---|---|
| **S‑E‑01** | Agent | Saisie d’un champ obligatoire manquant. | Message d’erreur inline, sauvegarde bloquée. |
| **S‑E‑02** | Importateur | Fichier CSV mal formaté. | Rapport de synthèse indique lignes erronées, import annulé. |
| **S‑E‑03** | Service | Défaillance du service Elasticsearch. | Recherche désactivée, affichage d’un bandeau d’information, journalisation. |
| **S‑E‑04** | Admin | Tentative de déploiement sans volume persistant. | Docker‑Compose échoue, rollback automatisé, alerte. |

### 6.3 Scénarios limites  

| N° | Condition | Impact | Traitement |
|---|---|---|---|
| **S‑L‑01** | Import de 5 Go de données (max volume). | Temps d’import > 30 min. | Découpage automatique du fichier, affichage d’une barre de progression. |
| **S‑L‑02** | 10 000 requêtes simultanées (pic de charge). | Risque dépassement SLA. | Mise en place de pool de connexions, scaling horizontal du conteneur app. |
| **S‑L‑03** | Suppression accidentelle d’un volume Docker. | Perte de données. | Restauration depuis la sauvegarde du jour précédent, notification d’incident. |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|---|---|---|---|
| **MOA – CGDD/AST4** | Commanditaire, validation fonctionnelle | Traçabilité, conformité RGPD, reporting CNIL | Valeur métier élevée (obligation légale). |
| **MOE – Klee Group / Acteurs internes** | Développement, maintenance | Architecture modulaire, CI/CD, Docker, tests automatisés | Réduction des coûts d’exploitation. |
| **Utilisateurs finaux (agents, référents)** | Saisie & suivi dossiers | Ergonomie, temps de saisie réduit, accès aux rapports | Satisfaction utilisateur, adoption. |
| **Responsable Sécurité (DPO)** | Conformité, audit | Chiffrement, journalisation, gestion des droits | Assurance de conformité, réduction risque. |
| **Equipe Ops (DSI)** | Déploiement, monitoring | Scripts Docker, sauvegarde, alerting | Disponibilité, temps de récupération. |
| **Support / Help‑Desk** | Assistance aux usagers | Documentation, logs détaillés | Résolution rapide d’incidents. |
| **Auditeur CNIL** | Vérification conformité | Accès aux journaux, preuves de consentement | Validation légale, continuité du service. |

---  

## 8. Contraintes et environnement  

| Catégorie | Description |
|---|---|
| **Réglementaires** | RGPD (art. 30, 32), CNIL (déclaration n° 1034232), archivage légal (DUA = 5 ans). |
| **Techniques** | Hébergement IaaS (ECO4) – VM Linux, Docker ≥ 20.10, Tomcat 7.0.108‑JDK8, PostgreSQL 14, Elasticsearch 7.x, BIRT 4.3. |
| **Sécurité** | TLS 1.2+, SSO (CAS/OIDC), mots‑de‑passe hashés (bcrypt), firewall réseau, sauvegarde chiffrée. |
| **Performance** | SLA ≥ 99,5 % (temps de réponse < 2 s pages, < 5 s extractions). |
| **Organisationnelles** | Processus de merge → pipeline CI → validation QA, dates de release synchronisées avec les fenêtres de maintenance (02 h–04 h). |
| **Opérationnelles** | Volumes Docker persistants (`sireines_db_sireines_vol`, `sireines_pgadmin_sireines_vol`), sauvegarde quotidienne BDD, rotation des logs 30 j, monitoring via Prometheus + Grafana. |
| **Environnement de développement** | Maven 3.6+, Java 1.7, IDE IntelliJ/Eclipse, tests unitaires JUnit, tests d’intégration Spring, Docker‑Compose local. |

---  

## 9. Critères de sélection et pondération (marchés publics)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---|---|---|---|
| **Fonctionnalités** | Couverture du périmètre fonctionnel (B‑01‑01 à B‑01‑08) | 35 % | 0‑5 points (exigence remplie = 5). |
| **Conformité RGPD / CNIL** | Respect des exigences légales (FC‑01) | 15 % | Oui = 5, Partiel = 2, Non = 0. |
| **Performance & disponibilité** | SLA ≥ 99,5 % (FC‑02) | 10 % | Mesurée en production. |
| **Sécurité** | Authentification SSO, chiffrement, journalisation (FC‑03) | 10 % | Conforme = 5, Partiel = 2, Non = 0. |
| **Technologies** | Docker, PostgreSQL, Elasticsearch, BIRT (compatibilité) | 10 % | Versions conformes = 5, Dérogation = 2, Non = 0. |
| **Coût total de possession (TCO)** | Licence, hébergement, maintenance (3 ans) | 10 % | Estimation < 150 k € = 5, 150‑250 k € = 3, > 250 k € = 0. |
| **Plan de transition / déploiement** | Procédure CI/CD, documentation (FC‑08) | 5 % | Documenté = 5, Partiel = 2, Absence = 0. |
| **Qualité documentaire** | Manuels d’installation, guides de recette (Docs) | 5 % | Complet = 5, Partiel = 2, Insuffisant = 0. |

---  

## 10. Glossaire et acronymes  

| Acronyme | Signification |
|---|---|
| **B‑FP** | Fonction Principale |
| **B‑FC** | Fonction Contraint |
| **RGPD** | Règlement Général sur la Protection des Données |
| **CNIL** | Commission Nationale de l’Informatique et des Libertés |
| **IaaS** | Infrastructure as a Service |
| **ECO4** | Plateforme d’hébergement ministérielle (IaaS) |
| **SSO** | Single Sign‑On |
| **BIRT** | Business Intelligence and Reporting Tools |
| **DAO** | Data Access Object |
| **DTO** | Data Transfer Object |
| **CI/CD** | Continuous Integration / Continuous Deployment |
| **SLA** | Service Level Agreement |
| **DUA** | Durée d’Utilisation Autorisée (archivage) |
| **SIREINES** | Système d’Information de Recensement des Experts et Spécialistes |
| **Maven** | Outil de gestion de projet Java |
| **Docker‑Compose** | Orchestrateur de conteneurs multi‑services |
| **Elasticsearch** | Moteur de recherche plein‑texte |
| **JPA** | Java Persistence API |
| **DTO** | Data Transfer Object |
| **B‑01‑xx** | Identifiant hiérarchique du besoin (cf. section 3) |
| **JIRA** | Outil de suivi des tickets (exemple) |
| **PO** | Product Owner |
| **DPO** | Data Protection Officer |

---  

*Fin du Cahier des Charges Fonctionnel – SIREINES*   (Conforme NF EN 16271)  