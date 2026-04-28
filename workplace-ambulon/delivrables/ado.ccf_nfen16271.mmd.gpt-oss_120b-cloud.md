# Cahier des Charges Fonctionnel (CCF) – Projet **ADO**  
*Gestion de la consultation des dossiers RH archivés (ReHucit) – version 2.0.26*  

> **Conformité** : NF EN 16271 :2013 (Management par la valeur) – édition française.  
> **Version du CCF** : 1.0 – 27 / 04 / 2026  
> **Références** :  
> • Documentation technique ADO (v2.2) – 19/06/2024  
> • Documentation métier – 23/03/2026  
> • Base de données PostgreSQL – scripts `ado_create_table_1.0.0.sql` … `script_v2_0_25.sql`  
> • Normes : RGPD, RGS, DICT 1332, DACP, NF EN 16271  

---

## 1. Présentation du projet  

| Élément | Description |
|---------|-------------|
| **Intitulé** | **ADO – Consultation des données RH archivées (ReHucit)** |
| **Contexte** | L’application ADO permet aux services de la DRH de consulter les dossiers RH des agents tels qu’ils figuraient dans le SIRH **ReHucit** à la date du **30/05/2019**, avant la migration vers **RenoiRH**. Elle garantit l’accès aux dossiers non repris dans RenoiRH. |
| **Objectifs** | 1️⃣ Assurer la **consultation fiable** des historiques RH (identité, carrière, rémunération, absences, etc.). <br>2️⃣ Faciliter la **production de rapports** (Mini‑CV, état de service, actes, etc.) au format PDF/Excel/CSV via JasperReports. <br>3️⃣ Garantir la **traçabilité** des accès (journalisation) et le **respect des exigences réglementaires** (RGPD, DICT, DACP). |
| **Périmètre fonctionnel** | **Inclus** : recherche d’agents, affichage du détail d’un agent, génération de tous les rapports listés (Mini‑CV, état de service, actes, etc.), journal d’accès, fonction de purge des journaux, export JasperReports. <br>**Exclus** : mise à jour ou création de données RH (application strictement en lecture), import de nouvelles sources, gestion du SIRH RenoiRH. |
| **Environnement technique** | Java 17 / Spring Boot 2.x, PostgreSQL 13+, JasperReports, Maven (assembly), serveur IaaS (ECO4 – Paris La Défense), HTTPS. |
| **Contraintes temporelles** | Livraison en **production** prévue : **30/09/2026** – phases : recette (30/07/2026), pré‑production (31/08/2026). |
| **Contraintes budgétaires** | Budget global alloué : **250 k €** (développement, tests, exploitation). |

---

## 2. Analyse de la valeur  

### 2.1 Fonctions de service  

| Code | Fonction de service | Type | Justification (valeur) |
|------|--------------------|------|------------------------|
| **FP‑01** | **Consultation d’un dossier RH** | **Fonction Principale** | Valeur centrale pour les utilisateurs (agents, services RH) – répond à la finalité légale de mise à disposition des archives. |
| **FP‑02** | **Production de rapports (Mini‑CV, état de service, actes, etc.)** | **Fonction Principale** | Permet l’exploitation des données (audit, contrôle interne, support décisionnel). |
| **FC‑01** | **Sécurisation des accès (authentification, filtrage Cerbere)** | **Fonction Contraint** | Obligatoire par le **socle de sécurité** (RGPD, DICT, SSI). |
| **FC‑02** | **Traçabilité des consultations (journalisation)** | **Fonction Contraint** | Exigence de **traçabilité** (DICT 1332 – niveau 2). |
| **FC‑03** | **Respect des exigences de disponibilité (DI‑1)** | **Fonction Contraint** | Disponibilité = 1 (haute) – service critique pour les agents. |
| **FC‑04** | **Conformité RGPD/DACP** | **Fonction Contraint** | Traitement de données à caractère personnel (NIR, etc.). |
| **FC‑05** | **Gestion de la purge des journaux** | **Fonction Contraint** | Conformité à la politique de rétention (30 jours). |
| **FC‑06** | **Export des rapports (PDF, XLSX, CSV, TXT)** | **Fonction Contraint** | Nécessaire pour la diffusion aux interlocuteurs hors‑application. |

### 2.2 Critères de performance associés  

| Fonction | Critère | Unité | Valeur cible | Méthode de mesure |
|----------|---------|-------|--------------|-------------------|
| FP‑01 | Temps de réponse recherche (≤ 2 s) | seconde | ≤ 2 | Tests de charge (JMeter). |
| FP‑01 | Temps de réponse détail agent (≤ 1,5 s) | seconde | ≤ 1,5 | Tests unitaires + intégration. |
| FP‑02 | Temps de génération rapport (≤ 5 s) | seconde | ≤ 5 | Benchmarks JasperReports. |
| FC‑01 | Taux de refus d’accès non‑autorisé (≥ 99,9 %) | % | ≥ 99,9 | Tests d’intrusion, logs Cerbere. |
| FC‑02 | Conservation des logs pendant 30 jours | jour | 30 | Requête sur table `journal`. |
| FC‑03 | Disponibilité mensuelle (≥ 99,5 %) | % | ≥ 99,5 | Monitoring (Prometheus). |
| FC‑04 | Conformité RGPD (audit) | – | OK | Rapport d’audit. |
| FC‑05 | Durée maximale de purge (≤ 10 min) | minute | ≤ 10 | Test de charge purge. |
| FC‑06 | Intégrité du fichier exporté (checksum) | – | OK | SHA‑256 post‑génération. |

---

## 3. Expression fonctionnelle du besoin  

### 3.1 Décomposition hiérarchique des besoins  

| Identifiant | Niveau | Description fonctionnelle (QUOI) | Critère d’appréciation (mesurable) | Importance |
|-------------|--------|-----------------------------------|------------------------------------|------------|
| **B‑01** | Système | **Consultation des dossiers RH archivés** | – | **Obligatoire** |
| B‑01‑01 | Sous‑système | Recherche d’agents (nom, matricule, lieu naissance, etc.) | Temps de réponse ≤ 2 s, pertinence ≥ 95 % | Obligatoire |
| B‑01‑02 | Sous‑système | Affichage du détail complet d’un agent | Temps de réponse ≤ 1,5 s, affichage 100 % des champs définis | Obligatoire |
| B‑01‑03 | Sous‑système | Export du détail (PDF, XLSX, CSV, TXT) | Temps de génération ≤ 5 s, checksum OK | Obligatoire |
| **B‑02** | Système | **Production de rapports métiers** | – | **Obligatoire** |
| B‑02‑01 | Sous‑système | Mini‑CV (identité, carrière, rémunération) | Temps ≤ 5 s, conformité aux modèles JRXML | Obligatoire |
| B‑02‑02 | Sous‑système | Rapport état de service (poste, grade, quotité) | Temps ≤ 5 s, 13 colonnes exactes | Obligatoire |
| B‑02‑03 | Sous‑système | Rapport actes (actes administratifs) | Temps ≤ 5 s, 11 colonnes, format HTML/PDF | Obligatoire |
| B‑02‑04 | Sous‑système | Rapport conjoint, enfants, affectations, etc. (10‑12 rapports) | Temps ≤ 5 s, conformité aux modèles | Obligatoire |
| **B‑03** | Système | **Sécurité & traçabilité** | – | **Obligatoire** |
| B‑03‑01 | Sous‑système | Authentification & filtrage (FiltreCerbere) | Taux d’accès refusé non‑autorisé ≥ 99,9 % | Obligatoire |
| B‑03‑02 | Sous‑système | Journalisation de chaque accès | Enregistrement complet, rétention 30 jours | Obligatoire |
| B‑03‑03 | Sous‑système | Purge automatisée des journaux | Durée ≤ 10 min, suppression conforme | Obligatoire |
| **B‑04** | Système | **Conformité réglementaire** | – | **Obligatoire** |
| B‑04‑01 | Sous‑système | RGPD / DACP – anonymisation & droit d’accès | Audit RGPD OK, logs de consentement | Obligatoire |
| B‑04‑02 | Sous‑système | DICT – disponibilité, intégrité, traçabilité | Disponibilité ≥ 99,5 %, intégrité 100 % | Obligatoire |
| **B‑05** | Système | **Exploitation & maintenance** | – | **Souhaitable** |
| B‑05‑01 | Sous‑système | Monitoring (Prometheus + Grafana) | Alertes < 5 min, tableau de bord | Souhaitable |
| B‑05‑02 | Sous‑système | Documentation (API, rapports, procédures) | Docs à jour, versionnée Git | Souhaitable |

> **Notation** : *Obligatoire* = niveau de priorité 1, *Souhaitable* = niveau 2, *Optionnel* = niveau 3.  

---

### 3.2 Caractérisation des besoins (tableau obligatoire)

| Fonction | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|----------|------------------------|---------------------|-------------|-------------|
| **Recherche d’agents** | Temps de réponse ≤ 2 s, pertinence ≥ 95 % | Obligatoire | Négociable (≤ 3 s acceptable) | Respect du filtre Cerbere, RGPD (données personnelles) |
| **Affichage détail agent** | Temps de réponse ≤ 1,5 s, affichage 100 % des champs | Obligatoire | Négociable (≤ 2 s) | Aucun champ sensible en clair (masquage NIR) |
| **Export rapport** | Génération ≤ 5 s, checksum OK | Obligatoire | Négociable (≤ 7 s) | Formats PDF/Excel/CSV conformes aux modèles JRXML |
| **Mini‑CV** | Conformité modèle Mini‑CV (13 colonnes) | Obligatoire | Fixe | Aucun |
| **Rapport état de service** | 13 colonnes exactes, ordre défini | Obligatoire | Fixe | Aucun |
| **Sécurité (FiltreCerbere)** | Taux refus ≥ 99,9 % | Obligatoire | Fixe | Implémentation OIDC/LDAP |
| **Journalisation** | Conservation 30 jours, intégrité 100 % | Obligatoire | Fixe | RGPD – droit à l’effacement |
| **Purge journaux** | Durée ≤ 10 min, aucune perte d’autres données | Obligatoire | Fixe | Conformité politique de rétention |
| **Conformité RGPD/DACP** | Audit OK, registre des traitements à jour | Obligatoire | Fixe | 6° NIR – chiffrement au repos |
| **Disponibilité (DICT‑1)** | Uptime ≥ 99,5 % mensuel | Obligatoire | Fixe | Redondance serveur, backup quotidien |
| **Monitoring** | Alertes < 5 min, tableau temps réel | Souhaitable | Négociable | Outil open‑source recommandé |

---

## 4. Validation de l’expression du besoin  

| Étape | Méthode | Participants | Livrable | Traçabilité |
|-------|---------|--------------|----------|-------------|
| 4.1 | Ateliers métier (DRH, SG/DRH) | PO, chefs de service RH, experts RGPD | Cahier des charges fonctionnel (actuel) | Matrice RACI |
| 4.2 | Revues techniques (architectes, équipe dev) | Lead dev, architecte sécurité, admin DB | Validation technique des contraintes | Références aux sections 2‑4 |
| 4.3 | Validation juridique (RSSI, DPO) | DPO, Responsable SSI | Attestation conformité RGPD/DICP | Signature du DPO |
| 4.4 | Recette d’acceptation (UAT) | Utilisateurs finaux (agents, services RH) | Rapport de recette & validation des critères | Lié aux identifiants B‑xx‑xx |

---

## 5. Scénarios d’usage  

| Scénario | Type | Description | Conditions d’entrée | Conditions de sortie |
|----------|------|-------------|---------------------|----------------------|
| **S‑01** | Nominal | **Recherche d’un agent** – l’utilisateur saisit un nom ou matricule → l’application renvoie la liste des agents correspondants (≤ 20 résultats). | FiltreCerbere authentifié, connexion DB OK. | Temps de réponse ≤ 2 s, pertinence ≥ 95 %. |
| **S‑02** | Nominal | **Affichage détail** – le user clique sur un résultat → le détail complet (identité, carrières, absences, etc.) s’affiche. | Résultat de recherche sélectionné, droits lecture sur le matricule. | Temps ≤ 1,5 s, 100 % champs affichés, NIR masqué. |
| **S‑03** | Nominal | **Export Mini‑CV** – l’utilisateur sélectionne “Export PDF” → le fichier est généré et téléchargé. | Détail chargé, format choisi (PDF/Excel/CSV). | Génération ≤ 5 s, checksum OK, conformité modèle. |
| **S‑04** | Erreur | **Base de données indisponible** – le serveur DB ne répond pas pendant une recherche. | Authentifié, DB down. | Message d’erreur *« Service temporairement indisponible »*, log d’incident dans `journal`. |
| **S‑05** | Erreur | **Accès non autorisé** – un compte sans droit tente d’accéder à un rapport. | FiltreCerbere rejette la requête. | Retour HTTP 403, journal d’accès refusé (≥ 99,9 %). |
| **S‑06** | Limite | **Export d’un grand volume** – l’utilisateur demande un rapport contenant > 10 000 lignes. | FiltreCerbere autorisé, paramètres de pagination désactivés. | Génération ≤ 30 s (dérogation), pagination automatique, alerte de charge. |
| **S‑07** | Limite | **Purge des journaux** – exécution de la tâche de purge à 02 h00. | Planning de purge déclenché, journal > 30 jours. | Suppression < 10 min, logs de purge conservés 7 jours. |

---

## 6. Parties prenantes (Stakeholders)

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|-----------------|------|---------------------|----------------------|
| **SG/DRH** (maîtrise d’ouvrage) | Commanditaire, utilisateur métier | Accès fiable aux archives, conformité juridique, reporting. | Valeur stratégique (mission de service public). |
| **Agents (utilisateurs finaux)** | Consommateur de l’information | Consultation simple, export de leurs dossiers. | Satisfaction utilisateur, réduction des appels au support. |
| **Équipe MOE (développeurs, architectes)** | Réalisation technique | Cadre technique stable, outils de test, documentation. | Qualité du produit, délai de livraison. |
| **RSSI / DPO** | Sécurité & conformité | Sécurisation, journalisation, RGPD, DICT. | Risque juridique, réputation. |
| **Direction des Systèmes d’Information (DSI)** | Exploitation | Disponibilité, monitoring, sauvegarde. | Continuité de service. |
| **Prestataire d’hébergement (ECO4)** | Hébergement | Infrastructure IaaS, scalabilité, réseau sécurisé. | Disponibilité, SLA. |
| **Audit interne** | Contrôle | Accès aux traces, conformité aux exigences. | Conformité réglementaire. |

---

## 7. Contraintes et environnement  

| Catégorie | Description |
|-----------|-------------|
| **Organisationnelles** | Processus de validation (atelier, revue juridique), budget 250 k €, planning fixé, gouvernance par la DRH. |
| **Réglementaires** | RGPD (articles 5, 32, 33 / 34), DICT 1332 (disponibilité 1, intégrité 3, traçabilité 2), DACP (traitement de NIR), RGS (sécurité de l’information). |
| **Techniques** | PostgreSQL ≥ 13, Java 17, Spring Boot 2.x, JasperReports ≥ 6.20, HTTPS/TLS 1.2+, authentification OIDC via `FiltreCerbere`. |
| **Sécurité** | Chiffrement des colonnes sensibles (NIR), journalisation détaillée, filtrage IP, politique de mots de passe, mise à jour mensuelle des dépendances. |
| **Temps & coûts** | Livraison finale 30/09/2026, budget 250 k €, marge de 10 % pour imprévus. |
| **Qualité** | Couverture de tests unitaires ≥ 80 %, tests d’intégration, tests de charge (JMeter) – 100 utilisateurs simultanés. |
| **Interopérabilité** | Export au format standard (CSV, XLSX, PDF) compatible avec outils internes (Excel, SharePoint). |
| **Maintenance** | Documentation versionnée, scripts de migration DB (scripts `v2_0_xx`), procédure de purge automatisée (cron). |

---

## 8. Critères de sélection et pondération (marché public)

| Critère | Sous‑critère | Pondération (%) | Modalité de notation |
|---------|--------------|----------------|----------------------|
| **Conformité fonctionnelle** | Respect des besoins B‑xx (obligatoire) | **40** | Oui/Non (exigence obligatoire). |
| **Qualité technique** | Architecture (micro‑services vs monolithe) | 10 | 0‑5 pts (5 = architecture évolutive). |
| | Couverture tests (unitaires ≥ 80 %) | 5 | 0‑5 pts. |
| | Performance (temps réponse ≤ 2 s) | 5 | 0‑5 pts (mesuré). |
| **Sécurité & conformité** | RGPD/DICP/DICT | **25** | 0‑10 pts (audit). |
| | Authentification (Cerbere) | 10 | 0‑10 pts (intégration OIDC). |
| | Journalisation & purge | 5 | 0‑5 pts. |
| **Coût** | Prix total (TTC) | **15** | Valeur absolue – score inverse. |
| **Plan de mise en œuvre** | Planning (délais) | 5 | 0‑5 pts (respect des jalons). |
| **Support & maintenance** | SLA (disponibilité ≥ 99,5 %) | **5** | 0‑5 pts (contrat). |

> **Total = 100 %**. Le cahier des charges impose que toute offre ne doit pas obtenir moins de **70 %** au global et **100 %** sur les critères obligatoires (Conformité fonctionnelle, Sécurité, RGPD).

---

## 9. Glossaire et acronymes  

| Acronyme / Terme | Définition |
|------------------|------------|
| **ADO** | Application de consultation des dossiers RH archivés (ReHucit). |
| **RGPD** | Règlement Général sur la Protection des Données (UE). |
| **DICT** | Dispositif d’Information et de Communication de la Trésorerie – référentiel DICT 1332 (Disponibilité, Intégrité, Confidentialité, Traçabilité). |
| **DACP** | Données à caractère personnel – catégorie de données sensibles (ex. NIR). |
| **Cerbere** | Filtre de sécurité (authentification, autorisation) développé par la DSI. |
| **JasperReports** | Bibliothèque Java de génération de rapports (PDF, XLSX, CSV, …). |
| **PDF** | Portable Document Format – format de rendu fixe. |
| **XLSX** | Format Microsoft Excel (OpenXML). |
| **CSV** | Valeurs séparées par des virgules – format texte. |
| **HT** | HyperText Transfer – protocole HTTP sur TLS (HTTPS). |
| **IaaS** | Infrastructure as a Service – service cloud (ECO4). |
| **UAT** | User Acceptance Testing – recette utilisateur. |
| **OIDC** | OpenID Connect – protocole d’authentification. |
| **NIR** | Numéro d’Inscription au Répertoire – identifiant unique français. |
| **SN‑001** | Référence interne de la spécification (ex. « SN‑001 – Recherche agents »). |
| **JPA** | Java Persistence API – couche d’abstraction ORM. |
| **Maven** | Outil de gestion de projets Java (build, dépendances). |
| **Spring Boot** | Framework d’auto‑configuration Spring. |
| **PR** | Pull Request – processus de revue de code. |
| **SIRH** | Système d’Information des Ressources Humaines. |
| **RenoiRH** | Nouveau SIRH de la DRH (successeur de ReHucit). |
| **ECO4** | Plateforme IaaS du ministère de la Transition écologique. |
| **JRE** | Java Runtime Environment. |
| **JVM** | Java Virtual Machine. |
| **CI/CD** | Intégration Continue / Livraison Continue. |
| **SQL** | Structured Query Language – langage de requête de bases de données. |
| **PL/pgSQL** | Langage procédural de PostgreSQL. |
| **HTTPS** | HTTP Secure – protocole chiffré TLS. |
| **SLA** | Service Level Agreement – engagement de niveau de service. |
| **UML** | Unified Modeling Language – notation de modélisation. |
| **UML‑seq** | Diagramme de séquence UML. |
| **UML‑class** | Diagramme de classe UML. |
| **UML‑activity** | Diagramme d’activité UML. |

---  

*Fin du Cahier des Charges Fonctionnel – Projet ADO*  

> **Remarque** : Ce document ne comporte aucune prescription technique (ex. « utiliser PostgreSQL », « déployer sur Tomcat »). Il se limite à l’expression du **besoin** (quoi) afin de garantir la **neutralité** exigée par la norme NF EN 16271. Toutes les solutions techniques devront être proposées dans les **offres** des fournisseurs, en respectant les critères de sélection ci‑dessus.  