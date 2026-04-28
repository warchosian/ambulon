# Cahier des Clauses Techniques Particulières (CCTP) – **Projet : admin_ep**

> **Référence du marché** : [​À préciser]  
> **Date de rédaction** : 27 avril 2026  
> **Version** : 1.0  

---  

## Table des matières
1. [Objet du marché](#1-objet-du-marché)  
2. [Description technique détaillée](#2-description-technique-détaillée)  
3. [Architecture et conception](#3-architecture-et-conception)  
4. [Exigences de sécurité (RGS, ANSSI)](#4-exigences-de-sécurité-rgs-anssi)  
5. [Interfaces et intégrations](#5-interfaces-et-intégrations)  
6. [Environnements et infrastructure](#6-environnements-et-infrastructure)  
7. [Qualité et conformité](#7-qualité-et-conformité)  
8. [Documentation et formation](#8-documentation-et-formation)  
9. [Tests et recette](#9-tests-et-recette)  
10. [Maintenance et support](#10-maintenance-et-support)  
11. [Livrables et planning](#11-livrables-et-planning)  
12. [Contraintes légales et réglementaires](#12-contraintes-légales-et-réglementaires)  
13. [Critères de sélection des offres](#13-critères-de-sélection-des-offres)  
14. [Annexes contractuelles](#14-annexes-contractuelles)  

---  

## 1. Objet du marché
| Élément | Description |
|---|---|
| **Intitulé** | Fourniture, déploiement et maintenance de la solution **admin_ep** (Administration des établissements publics) |
| **Périmètre fonctionnel** | • Gestion du répertoire des membres des conseils d’administration des établissements publics du MTES‑MCT  <br>• Interface d’écriture (saisie manuelle) <br>• Alimentation automatique à partir du JO (outil d’extraction JORF) <br>• Authentification via Cerbère (SSO) <br>• Archivage des mandats échus et pièces associées <br>• Interface de lecture (consultation) <br>• Module d’analyse statistique <br>• Notification d’échéance par courriel |
| **Périmètre technique** | • Application Java (Spring/Struts‑2) déployée sur Tomcat 9 (migration prévue vers Tomcat 10) <br>• Base de données PostgreSQL 9.6 (évolutive vers PostgreSQL 15) <br>• Packaging Maven multi‑module (adminep‑database, adminep‑deployment, adminep‑web, adminep‑doc) <br>• Conteneurisation en cours (Docker) <br>• Hébergement sur le centre‑serveur ministériel Paris La Défense (environnement Production, Pré‑production et Recette) |
| **Livrable attendu** | • Code source complet (GitLab) <br>• Scripts d’initialisation et de migration de la base (SQL) <br>• Artefacts déployables (WAR, ZIP d’assemblage) <br>• Documentation technique et fonctionnelle (DAT, guides d’installation, guides d’exploitation) <br>• Procédures de formation utilisateurs et administrateurs |
| **Référence au CCF** | Le **Cahier des Clauses Générales (CCG)** du présent marché s’applique. Le présent CCTP détaille les exigences techniques spécifiques. |

---  

## 2. Description technique détaillée  

| Niveau | Spécifications |
|---|---|
| **Fonctionnelles minimales** (obligatoires) | 1. Gestion du référentiel **TYPE_MANDAT**, **TYPE_INSTANCE**, **MODE_NOMINATION**, **CHARGE**, **CIVILITE**, **MINISTERE**, **COLLEGE**, **ETABLISSEMENT** (voir scripts `1_createSequenceAndTablesIntegration.sql` et `2_populateTablesIntegration.sql`). <br>2. Saisie, mise à jour et suppression des administrateurs, gestionnaires, mandats via les actions Struts 2 (`DetailAdminAction`, `UpsertAdminAction`, etc.). <br>3. Authentification unique via Cerbère (module `SecurityManagerInitializer`). <br>4. Extraction JORF automatisée (package `util.jorf`, classes `JORFExtractor`, `FileUtil`). <br>5. Notification d’échéance par e‑mail (SMTP configuré dans `application-config.xml`). |
| **Techniques obligatoires** | • **Java 8** (minimum) – compilation avec Maven 3.x <br>• **Servlet API 3.1** – Tomcat 9 (compatibilité Tomcat 10 prévue) <br>• **PostgreSQL 9.6** – schéma `integration` (scripts d’init) <br>• **Maven Assembly** – production d’un archive ZIP contenant les scripts de migration (`adminep-database/assembly.xml`). <br>• **HTTPS** obligatoire (certificat TLS signé) <br>• **Journalisation** via Log4j2 (`log4j2.xml`) avec rotation quotidienne. |
| **Techniques souhaitées** | • Migration vers **PostgreSQL 15** (compatible avec les scripts existants). <br>• Utilisation de **Spring Boot** pour simplifier le bootstrap (facultatif). <br>• Mise en place d’une **API REST** (OpenAPI 3) pour les opérations de lecture. |
| **Techniques optionnelles** | • Déploiement **Kubernetes** (Helm chart fourni). <br>• Utilisation du **RGAA 4.1** pour l’accessibilité front‑end. <br>• Intégration d’un moteur de recherche **Elasticsearch** (déjà présent dans `boot/config/elasticsearch.yml`). |

---  

## 3. Architecture et conception  

| Aspect | Exigence |
|---|---|
| **Modèle architectural** | Architecture **n‑tier** (Web → Business → Data) respectant le **RGI** (Référentiel Général d’Interopérabilité) : <br>• Couche présentation : JSP/Struts‑2, CSS/Bootstrap, assets `static/` <br>• Couche métier : services Java sous `fr.gouv.e2.baseadmin.services.*` <br>• Couche persistance : JPA (Hibernate) configurée dans `persistence.xml` |
| **Standards** | • **ISO 27001** – gestion de la sécurité de l’information <br>• **ISO 25010** – qualité du logiciel (fiabilité, performance, maintenabilité) <br>• **IEEE 1471** – description d’architecture <br>• **W3C** – HTML 5, CSS 3, HTTP/1.1, HTTPS |
| **Interopérabilité** | Conformité **RGI** : utilisation de **KSP** (Ksp‑definition) pour les modèles de données, version `application.kpr` fourni. <br>Export/import CSV conforme aux spécifications du ministère. |
| **Frameworks / Bibliothèques autorisés** | • **Struts‑2** (core) <br>• **Vertigo** (dynamox, vega) <br>• **Displaytag** (table rendering) <br>• **Log4j2** (logging) <br>• **Apache Commons**, **Google Guava** (versions compatibles avec Java 8) |
| **Patterns** | • **DAO** (Data Access Object) <br>• **Service‑Facade** <br>• **Singleton** (SecurityHelper) <br>• **Factory** (TrustManagerAllCertificates) |

---  

## 4. Exigences de sécurité (RGS, ANSSI)

| Exigence | Niveau | Obligation / Moyen | Méthode de vérification |
|---|---|---|---|
| **Niveau de sécurité RGS** | **Basique** (RGS 1) – compatible avec la politique d’accès interne du ministère. | Obligation de résultat : la solution **doit** respecter les exigences du Référentiel Général de Sécurité (confidentialité, intégrité, disponibilité). | Audit de conformité RGS 1 par le RSSI du ministère. |
| **Authentification** | SSO Cerbère (Kerberos + SAML) | Le prestataire **doit** intégrer le module `SecurityManagerInitializer` et valider les jetons SAML. | Test d’authentification avec comptes de test (admin, gestionnaire, lecteur). |
| **Contrôle d’accès** | RBAC (rôles `ADMIN`, `GESTIONNAIRE`, `LECTEUR`) implémenté dans `Roles.java`. | Obligation de résultat : chaque action Struts‑2 doit vérifier le droit via `RightsHelper`. | Revue de code + tests unitaires (couverture ≥ 90 %). |
| **Chiffrement des données en transit** | TLS 1.2 minimum, cipher suites **AES‑256‑GCM** et **ECDHE‑RSA**. | Obligation de moyen : le serveur Tomcat 9 doit être configuré (`conf/server.xml`). | Scan SSL (Qualys SSL Labs) – grade A+. |
| **Chiffrement des données au repos** | **AES‑256** sur les colonnes sensibles (ex : mots‑de‑passe, données personnelles) via `pgcrypto`. | Obligation de moyen : les scripts d’initialisation doivent créer les fonctions de chiffrement. | Vérification du schéma (`SELECT * FROM pg_roles WHERE rolname='baseadmin';`). |
| **Journalisation** | Journaux d’accès, d’erreurs et d’audit doivent être centralisés via **Log4j2** et **ELK** (déjà configuré). | Obligation de résultat : rétention ≥ 365 jours, horodatage UTC. | Inspection des fichiers `logs/` et requêtes Kibana. |
| **Traçabilité** | Tous les traitements de données personnelles doivent être consignés (RGPD). | Obligation de moyen : chaque modification d’un mandat doit créer une entrée dans la table `audit_log`. | Requête SQL de vérification. |
| **RGPD** | Respect du principe de minimisation, droit d’accès, droit à l’effacement. | Obligation de résultat : mise à disposition d’un **Data Protection Impact Assessment (DPIA)**. | Validation par le DPD du ministère. |
| **Gestion des vulnérabilités** | Scans mensuels (OWASP ZAP, Snyk). | Obligation de moyen : le prestataire doit fournir un rapport de suivi. | Rapport d’audit. |

---  

## 5. Interfaces et intégrations  

| Interface | Description | Protocole / Format | Points de contrôle |
|---|---|---|---|
| **Web UI** | Application Struts‑2 exposée via `https://adminep.e2.rie.gouv.fr/`. | HTTP / HTTPS, HTML 5, CSS 3, JavaScript. | Tests fonctionnels Selenium, conformité RGAA. |
| **API interne** | Accès aux services métier via les **Action** Struts‑2 (ex : `/admin_ep/admins/RechercheAdminsAction`). | HTTP POST/GET, paramètres URL‑encoded. | Tests d’intégration (MockMVC). |
| **Service d’alimentation JORF** | Extraction quotidienne du flux JORF (RSS) → parsing (`JORFExtractor`). | HTTP GET (RSS), XML. | Validation du schéma XSD JORF, test de parsing sur jeu de données. |
| **Authentification Cerbère** | SSO via SAML 2.0. | SAML 2.0, HTTPS. | Vérification du certificat IdP, test de logout Single Logout. |
| **Base de données** | PostgreSQL 9.6 (ou 15). | JDBC 4.2, SQL. | Scripts de migration versionnés (`adminep-database/scripts/update/...`). |
| **Elasticsearch** (optionnel) | Indexation des articles JORF. | REST JSON, HTTP. | Tests de recherche plein‑texte, mapping `articleDao.ksp`. |
| **Mail** | Envoi de notifications d’échéance. | SMTP TLS, texte/HTML. | Test d’envoi vers boîte de test, suivi des bounces. |
| **Supervision PSIN** | Point de santé (`/supervision`). | HTTP GET, JSON. | Monitoring via Nagios/Prometheus (alertes < 5 min). |

---  

## 6. Environnements et infrastructure  

| Environnement | Description | Contraintes |
|---|---|---|
| **Production** | Hébergement MSP – Centre‑serveur ministériel Paris La Défense – Tomcat 9.0.8, PostgreSQL 9.6.11 (migration prévue vers 15). | Disponibilité ≥ 99,9 % (SLA), sauvegarde quotidienne, PRA ≤ 4 h. |
| **Pré‑production** | Identique à la prod (clonage) pour validation des releases. | Doit être synchronisé quotidiennement avec la prod (replication). |
| **Recette** | Environnement de tests fonctionnels. | Accès restreint, données anonymisées. |
| **Conteneurisation (en cours)** | Docker images (`adminep-web`, `adminep-db`). | Conformité aux standards Docker 1.13, images signées (Docker Content Trust). |
| **Réseau** | Zone DMZ – accès uniquement via HTTPS (port 443). | Pare‑feu avec règles « allow inbound 443 from *.gouv.fr ». |
| **PRA / PCA** | Plan de reprise d’activité – réplication asynchrone vers datacenter secondaire. | RTO ≤ 4 h, RPO ≤ 30 min. |
| **Sécurité périmétrique** | IDS/IPS (Snort), WAF (ModSecurity) en front‑end. | Log d’événements transmis au SIEM. |

---  

## 7. Qualité et conformité  

| Critère | Référence | Exigence |
|---|---|---|
| **Qualité logicielle** | ISO 25010 – **Fiabilité** | Taux d’erreur ≤ 0,1 % en production (défini via incidents). |
| **Performance** | Temps de réponse HTTP ≤ 2 s (95 % des requêtes). | Tests de charge (JMeter) – 200 concurrent users, 30 min. |
| **Disponibilité** | SLA ≥ 99,9 % (hors fenêtres de maintenance). | Monitoring en temps réel. |
| **Maintenabilité** | Documentation du code (Javadoc) ≥ 80 % des classes publiques. | Couverture de tests unitaires ≥ 90 % (JaCoCo). |
| **Accessibilité** | RGAA 4.1 – **Conformité** | Niveau AA au minimum (audit automatisé Axe). |
| **Interopérabilité** | RGI – utilisation des KSP (`model.ksp`, `domains.ksp`). | Validation via le validateur RGI du ministère. |

---  

## 8. Documentation et formation  

| Livrable | Format | Contenu |
|---|---|---|
| **Documentation d’architecture technique (DAT)** | PDF + diagrammes UML | Architecture n‑tier, flux JORF, processus de sauvegarde, schéma de base. |
| **Guide d’installation** | Markdown / PDF | Prérequis, procédure d’installation (Maven, Docker, scripts SQL), configuration TLS, paramètres `application-config.xml`. |
| **Guide d’exploitation** | PDF | Gestion des logs, supervision, procédures de redémarrage, mise à jour. |
| **Guide utilisateur** | HTML (dans le WAR) | Navigation dans l’interface, recherches, gestion des mandats. |
| **Guide d’administration** | PDF | Gestion des comptes Cerbère, création de nouveaux types, import/export CSV. |
| **Programme de formation** | Présentations PowerPoint + ateliers | 2 jours – (1) prise en main fonctionnelle, (2) administration et maintenance. |
| **Support de formation** | Vidéos courtes (≤ 5 min) | Démonstrations de la création d’un administrateur, de la génération d’une alerte. |

---  

## 9. Tests et recette  

| Type de test | Objectif | Critères d’acceptation |
|---|---|---|
| **Tests unitaires** | Vérifier le comportement des classes Java (services, DAO, utilitaires). | Couverture ≥ 90 % (JaCoCo). |
| **Tests d’intégration** | Interaction entre les couches (Web ↔ Service ↔ DB). | Tous les scénarios fonctionnels exécutés avec succès (rapport JUnit). |
| **Tests fonctionnels** | Validation du parcours utilisateur (saisie, recherche, notification). | Scénarios décrits dans le **Plan de Test Fonctionnel** (Selenium) passent à 100 %. |
| **Tests de performance** | Charge (200 users) et stress (500 users). | Temps de réponse moyen ≤ 2 s, aucune perte de données. |
| **Tests de sécurité** | Scan OWASP ZAP, Snyk, audit RGS. | Aucun défaut critique, tous les défauts majeurs corrigés. |
| **Recette fonctionnelle** | Vérification par le maître d’ouvrage. | Sign-off du **Cahier des Tests de Recette** (document annexé). |
| **Gestion des anomalies** | Système de suivi JIRA (ou équivalent). | Toutes les anomalies de priorité ≤ P2 résolues avant mise en production. |
| **Recette avec réserves** | Si des réserves subsistent, elles doivent être listées et planifiées. | Aucun blocage critique – mise en production autorisée sous réserve. |

---  

## 10. Maintenance et support  

| Niveau | Service | Délai d’intervention | Niveau de service (SLA) |
|---|---|---|---|
| **Niveau 1 – Support fonctionnel** | Assistance aux utilisateurs (ticket, mail). | Accusé de réception ≤ 15 min, résolution ≤ 4 h (P1). | Disponibilité ≥ 8 h/jour, 5 j/sem. |
| **Niveau 2 – Support technique** | Corrections de bugs, mise à jour de dépendances. | Intervention ≤ 2 h, correction ≤ 24 h (P2). | 24/7 (astreinte). |
| **Niveau 3 – Maintenance évolutive** | Ajout de nouvelles fonctionnalités (ex : nouveaux types de mandats). | Planning trimestriel, délai de livraison ≤ 30 j ouvrés après validation. | - |
| **Garantie** | 12 mois à compter de la mise en production. | - | - |
| **Disponibilité** | Garantie de disponibilité ≥ 99,9 % (hors fenêtres de maintenance). | Fenêtres de maintenance ≤ 4 h/mois, planifiées. | - |

---  

## 11. Livrables et planning  

| Jalons | Date cible | Livrable |
|---|---|---|
| **Kick‑off** | 15 mai 2026 | Cahier des charges fonctionnel signé |
| **Livraison du code source complet** | 30 juin 2026 | Repository GitLab (`admin_ep`), tags version 1.0 |
| **Livraison des scripts d’initialisation & migration** | 30 juin 2026 | `adminep-database/scripts/` (init + update) |
| **Déploiement en pré‑production** | 15 juillet 2026 | WAR déployé sur serveur Tomcat 9, base PostgreSQL 9.6 |
| **Tests d’acceptation (UAT)** | 31 juillet 2026 | Rapport de recette signé par le MOA |
| **Mise en production** | 15 août 2026 | Application accessible via `https://adminep.e2.rie.gouv.fr/` |
| **Formation utilisateurs** | 20‑25 août 2026 | Sessions de formation + supports |
| **Clôture du projet** | 31 août 2026 | Procès‑verbal de réception définitive, livrables archi‑vés |

> **Pénalités de retard** : - 0,5 % du montant du lot par jour ouvré de retard au-delà du 15 août 2026, plafonné à 10 % du lot.

---  

## 12. Contraintes légales et réglementaires  

| Domaine | Référence | Exigence |
|---|---|---|
| **Propriété intellectuelle** | Code source sous licence **MIT** (ou licence interne du ministère). Le prestataire cède les droits d’exploitation, de modification et de distribution au ministère. |
| **Licences tierces** | Toutes les bibliothèques tierces (Struts‑2, Log4j2, etc.) doivent être compatibles avec la politique de licences du ministère (GPL v2 ou plus, Apache 2.0, MIT). |
| **RGPD** | Article 32, 33, 34 du RGPD. | DPIA réalisé, registre des traitements à jour, droit d’accès et d’effacement implémentés. |
| **Archivage** | Référentiel **RGAA** et **RGI**. | Les archives (mandats, pièces jointes) doivent être conservées ≥ 10 ans, chiffrées, accessibles uniquement aux profils habilités. |
| **Sécurité** | RGS 1 (basique) – **ANSSI**. | Mise en œuvre de mesures de protection physique (datacenter), logique (TLS, chiffrement, journaux). |
| **Accessibilité** | RGAA 4.1 – **Décret n° 2021‑1234**. | Niveau AA au minimum, audit d’accessibilité avant mise en production. |
| **Période de conservation des logs** | 365 jours (article 30‑1 de la loi Informatique et Libertés). | Logs centralisés, archivés, indexés. |

---  

## 13. Critères de sélection des offres  

| Critère | Pondération | Échelle d’évaluation |
|---|---|---|
| **Conformité fonctionnelle** (CCF) | 30 % | Excellent = 100 pts, Satisfaisant = 70 pts, Insuffisant = 0 pts |
| **Respect des exigences RGS / Sécurité** | 25 % | Conforme = 100 pts, Partiellement = 50 pts, Non conforme = 0 pts |
| **Qualité du code / Tests** | 15 % | Couverture ≥ 90 % = 100 pts, 70‑90 % = 50 pts, < 70 % = 0 pts |
| **Plan de mise en œuvre & planning** | 10 % | Respect des jalons = 100 pts, retard < 15 j = 50 pts, > 15 j = 0 pts |
| **Coût total** (TTC) | 10 % | Le prix le plus bas obtient 100 pts, les autres sont proportionnels. |
| **Valeur ajoutée (ex : conteneurisation, API REST, automatisation CI/CD)** | 10 % | Présentation détaillée et démonstration = 100 pts, partielle = 50 pts, absente = 0 pts |

> **Notation** : chaque critère est noté sur 100 pts, la somme pondérée donne la note finale sur 100 pts. Le soumissionnaire ayant la note la plus élevée sera retenu, sous réserve du respect des exigences contractuelles.

---  

## 14. Annexes contractuelles  

| Annexe | Contenu |
|---|---|
| **A – Glossaire** | Définitions des termes (Mandat, Charge, Charge de ministère, etc.). |
| **B – Références normatives** | ISO 27001, ISO 25010, RGS 1, RGAA 4.1, RGI, ANSSI, RGPD. |
| **C – Modèle de documents à remplir** | *Fiche de suivi d’incident*, *Rapport de tests de recette*, *DPIA*, *Registre des traitements*. |
| **D – Tableau de suivi des livrables** | Matrice RACI (Responsable, Autorité, Consulté, Informé). |
| **E – Modèle de contrat de maintenance** | SLA détaillés, pénalités, conditions de renouvellement. |
| **F – Exemple de plan de reprise d’activité (PRA)** | Architecture de réplication, procédure de bascule. |
| **G – Check‑list de conformité RGS** | Points de contrôle à valider avant la mise en production. |

---  

*Fait à Paris, le 27 avril 2026.*  

---  

*Fin du CCTP*  