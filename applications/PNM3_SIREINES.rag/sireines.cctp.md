Je vais générer le CCTP complet pour SIREINES. Ce document sera structuré selon les 14 sections obligatoires du cadre réglementaire, appliquées à l'architecture technique réelle du projet (Java 1.7, Struts, PostgreSQL, BIRT, Cerbère, Docker).

---

# CAHIER DES CLAUSES TECHNIQUES PARTICULIÈRES (CCTP)

## Application SIREINES — Gestion des qualifications scientifiques et techniques

**Référence marché :** [À compléter par le pouvoir adjudicateur]  
**Version :** 1.0  
**Date :** 19 mars 2026  
**Pouvoir adjudicateur :** Ministère de la Transition écologique et de la Cohésion des territoires — CGDD/DRI/AST4  

---

## SOMMAIRE

1. [Objet du marché](#1-objet-du-marché)
2. [Description technique détaillée](#2-description-technique-détaillée)
3. [Architecture et conception](#3-architecture-et-conception)
4. [Exigences de sécurité](#4-exigences-de-sécurité)
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

## 1. OBJET DU MARCHÉ

### 1.1 Définition de l'objet

Le présent marché a pour objet la **maintenance évolutive et corrective** de l'application **SIREINES** (Système d'Information pour la Recherche et l'Évaluation des compétences INtEgrées Scientifiques), ainsi que l'**exploitation** des environnements de recette, pré-production et production.

L'application SIREINES est un système d'information métier permettant :
- La gestion des demandes de qualification par les comités de domaine des agents
- Le suivi de l'évolution des compétences scientifiques et techniques
- La coordination de l'évaluation par les comités de domaine
- L'information des agents sur les suites de leurs demandes

### 1.2 Références au CCF (Cahier des Clauses Fonctionnelles)

Le présent CCTP doit être lu conjointement avec le CCF qui définit :
- Les processus métier de qualification des agents
- Les rôles et habilitations (administrateur, gestionnaire, rapporteur, agent)
- Les workflows de validation des dossiers de qualification
- Les règles de gestion des séances de comité

### 1.3 Périmètre des prestations

| Domaine | Description | Obligation |
|---------|-------------|------------|
| Maintenance corrective | Correction des anomalies de tous niveaux (bloquantes, majeures, mineures) | Résultat |
| Maintenance évolutive | Développement des évolutions fonctionnelles et techniques | Résultat |
| Maintenance adaptative | Adaptation aux évolutions de l'environnement technique | Résultat |
| Exploitation | Gestion des environnements, sauvegardes, supervision | Moyen |
| Support utilisateur | Hotline, assistance technique niveau 1 et 2 | Moyen |
| Documentation | Mise à jour de l'ensemble de la documentation technique et fonctionnelle | Résultat |

### 1.4 Exclusions du marché

Le présent marché exclut expressément :
- La réalisation d'une refonte totale de l'application sans validation préalable
- La migration vers une technologie différente sans clause spécifique
- La gestion des infrastructures réseau et postes de travail des utilisateurs finaux

---

## 2. DESCRIPTION TECHNIQUE DÉTAILLÉE

### 2.1 Spécifications fonctionnelles minimales (références CCF)

L'application devra permettre la gestion des entités métier suivantes :

| Module | Fonctionnalités minimales |
|--------|---------------------------|
| **Agents** | CRUD agents, recherche multicritère, consultation fiche détaillée |
| **Dossiers de qualification** | Création, modification, suivi du workflow de qualification, gestion des 5 mots-clés, gestion des fiches de conclusion (avis, projet de qualification, conclusions) |
| **Séances de comité** | Planification, affectation des dossiers, gestion des dates de passage |
| **Rapporteurs** | Affectation principale/secondaire, gestion des disponibilités |
| **Référentiels** | Gestion des corps, grades, structures, macro-structures, comités de domaine, qualifications, thésaurus de mots-clés |
| **Courriers** | Génération des courriers types (convocation, notification, etc.) |
| **Extractions/Reporting** | 10 rapports BIRT standards + rapports CPII/ACAI spécifiques, export CSV |
| **Imports** | Import de masse via fichier (format à spécifier) |

### 2.2 Spécifications techniques obligatoires (impératif)

| Exigence | Spécification | Modalité de vérification |
|----------|---------------|--------------------------|
| Langage de développement | Java 1.7 (compatibilité ascendante à valider) | Audit de code |
| Framework web | Apache Struts 2 (dernière version stable compatible) | Audit de code |
| Framework métier | Vertigo (version stable) | Audit de code |
| Base de données | PostgreSQL 15.x | Test de connexion et requêtes |
| Moteur de recherche | Elasticsearch (embedded ou standalone) | Tests de recherche full-text |
| Génération de rapports | BIRT (Business Intelligence and Reporting Tools) | Génération des 10 rapports standards |
| Authentification | Intégration Cerbère (client 4.7.4 ou supérieur) | Test de connexion SSO |
| Conteneurisation | Docker et Docker Compose | Déploiement sur environnement de recette |
| Serveur d'application | Apache Tomcat 9.x | Vérification version |

### 2.3 Spécifications techniques souhaitées (souhaitable, noté)

| Exigence | Spécification | Pondération notation |
|----------|---------------|---------------------|
| Migration Java | Proposition de migration vers Java 11 ou 17 LTS | 15% |
| Modernisation frontend | Remplacement progressif des JSP par un framework moderne (React, Vue.js, Angular) | 10% |
| API REST | Exposition des fonctionnalités via API REST documentée (OpenAPI/Swagger) | 10% |
| Tests automatisés | Couverture de code > 60% (tests unitaires + intégration) | 10% |
| CI/CD améliorée | Pipeline GitLab complète avec tests de sécurité (SAST/DAST) | 5% |

### 2.4 Spécifications techniques optionnelles (facultatif)

| Exigence | Description | Impact sur prix |
|----------|-------------|---------------|
| Migration base de données | Évolution vers PostgreSQL 16 | À chiffrer séparément |
| Conteneurisation complète | Kubernetes pour l'orchestration | À chiffrer séparément |
| Monitoring avancé | Intégration Prometheus/Grafana | À chiffrer séparément |

---

## 3. ARCHITECTURE ET CONCEPTION

### 3.1 Contraintes architecturales imposées

L'architecture devra respecter les contraintes suivantes :

```
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                       │
│  JSP + Tags Struts + Templates Freemarker + Bootstrap CSS   │
├─────────────────────────────────────────────────────────────┤
│                    COUCHE CONTRÔLEUR                         │
│  Actions Struts (pattern MVC) + Validators                  │
├─────────────────────────────────────────────────────────────┤
│                    COUCHE MÉTIER                             │
│  Services Java + Vertigo (DAO, KSP) + MDA                   │
├─────────────────────────────────────────────────────────────┤
│                    COUCHE DONNÉES                            │
│  PostgreSQL + Elasticsearch (indexation full-text)          │
├─────────────────────────────────────────────────────────────┤
│                    COUCHE INTÉGRATION                        │
│  Cerbère (SSO) + BIRT (reporting) + Talend (ETL)           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Standards et normes obligatoires

| Domaine | Standard | Application |
|---------|----------|-------------|
| Modélisation données | Merise / PowerDesigner | Modèle physique de données (MPD) |
| Génération de code | MDA (Model Driven Architecture) | Génération DAO et entités via Vertigo |
| Sécurité web | OWASP Top 10 | Protection contre injections XSS, SQL, CSRF |
| Protocoles réseau | HTTPS/TLS 1.2 minimum | Toutes les communications |
| Encodage | UTF-8 | Stockage et échanges de données |

### 3.3 Exigences d'interopérabilité et de portabilité

| Exigence | Description | Niveau |
|----------|-------------|--------|
| RGI — Interopérabilité | Respect du Référentiel Général d'Interopérabilité | Obligatoire |
| API d'intégration | Fourniture de points d'intégration documentés pour les systèmes tiers | Obligatoire |
| Portabilité données | Export des données au format standard (CSV, XML, JSON) | Obligatoire |
| Conteneurisation | Livraison sous forme d'images Docker pour garantir la portabilité | Obligatoire |

### 3.4 Patterns et frameworks autorisés ou imposés

| Élément | Statut | Version/Spécification |
|---------|--------|----------------------|
| Apache Struts 2 | Imposé | Dernière version stable compatible Java 1.7 |
| Vertigo | Imposé | Version utilisée en production ou compatible |
| Spring (si utilisé) | Autorisé | Version compatible Java 1.7 |
| Hibernate/JPA | Non imposé | Utilisation via Vertigo uniquement |
| jQuery/Bootstrap | Imposé | Versions embarquées existantes |

---

## 4. EXIGENCES DE SÉCURITÉ

### 4.1 Niveau de sécurité requis

| Environnement | Niveau RGS | Justification |
|---------------|------------|---------------|
| Production | RGS basique | Données personnelles des agents, données métier sensibles |
| Pré-production | RGS basique | Données de production anonymisées |
| Recette | Hors RGS | Données de test fictives |

### 4.2 Authentification et contrôle d'accès

| Exigence | Spécification | Modalité de vérification |
|----------|---------------|--------------------------|
| Authentification unique | Intégration Cerbère (SSO) | Test de connexion via portail agent |
| Gestion des habilitations | Rôles : ADMIN, GESTIONNAIRE, RAPPORTEUR, AGENT | Matrice des droits documentée |
| Durée de session | Timeout de 30 minutes d'inactivité | Test de déconnexion automatique |
| Mot de passe applicatif (admin technique) | Complexité : 12 caractères minimum, majuscules, minuscules, chiffres, caractères spéciaux | Audit de configuration |

### 4.3 Chiffrement des données

| Type de données | Chiffrement en transit | Chiffrement au repos |
|-----------------|------------------------|----------------------|
| Données personnelles des agents | TLS 1.2 minimum | Non requis (RGS basique) |
| Identifiants de connexion | TLS 1.2 minimum | Hachage fort (bcrypt, PBKDF2) |
| Documents joints | TLS 1.2 minimum | Non requis |
| Sauvegardes de base de données | — | Chiffrement du volume de stockage |

### 4.4 Traçabilité et journalisation

| Exigence | Spécification | Conservation |
|----------|---------------|--------------|
| Logs d'authentification | Date/heure, identifiant, résultat (succès/échec), IP source | 1 an |
| Logs d'accès aux données sensibles | Date/heure, utilisateur, action (CRUD), identifiant ressource | 1 an |
| Logs d'administration | Date/heure, administrateur, action réalisée | 3 ans |
| Logs techniques | Niveau ERROR, WARN, INFO configurable | 6 mois |

**Format des logs :** JSON structuré avec horodatage ISO 8601, identifiant de corrélation.

### 4.5 Conformité RGPD

| Exigence | Mise en œuvre | Preuve attendue |
|----------|---------------|---------------|
| Registre des traitements | À maintenir à jour | Document fourni |
| Droit d'accès | Fonctionnalité d'extraction des données personnelles | Procédure documentée |
| Droit à l'effacement | Procédure de suppression des données (anonymisation conservée pour l'historique) | Procédure documentée |
| Droit à la portabilité | Export des données au format JSON ou XML | Test de fonctionnement |
| Notification des violations | Procédure de signalement sous 72 heures | Procédure documentée |
| DPO | Coordonnées du DPO affichées dans l'application | Capture d'écran |

---

## 5. INTERFACES ET INTÉGRATIONS

### 5.1 Systèmes existants à interfacer

| Système | Type d'interface | Protocole/Format | Fréquence |
|---------|------------------|------------------|-----------|
| Cerbère (SSO) | Authentification | SAML 2.0 ou protocole propriétaire Cerbère | Temps réel |
| Annuaire LDAP/AD | Authentification (optionnel) | LDAPS | Temps réel |
| Système de fichiers | Stockage des documents joints | Système de fichiers local ou montage NFS | À la volée |
| Talend (ETL) | Import/Export de données | Base de données PostgreSQL | Batch quotidien |

### 5.2 Spécifications techniques des interfaces

#### 5.2.1 Intégration Cerbère

| Paramètre | Valeur |
|-----------|--------|
| URL service recette | https://cerbere.recette.e2.rie.gouv.fr/ |
| URL service production | [À compléter] |
| ID application recette | 564 |
| ID application production | 546 |
| Mode de connexion | Redirection HTTP POST vers Cerbère |
| Retour d'information | Identifiant agent, nom, prénom, email, structure |

#### 5.2.2 Interface base de données (Talend/ETL)

| Paramètre | Valeur |
|-----------|--------|
| Type | PostgreSQL |
| Mode d'accès | JDBC |
| Schéma dédié ETL | `sireines_etl` ou vue dédiée |
| Droits | SELECT uniquement sur tables métier, INSERT/UPDATE sur tables de staging |

### 5.3 Modalités de recette des interfaces

| Interface | Test de recette | Critère d'acceptation |
|-----------|-----------------|----------------------|
| Cerbère | Connexion avec 5 profils différents | Authentification réussie, rôles correctement attribués |
| Import ETL | Import d'un fichier test de 1000 lignes | Taux de rejet < 1%, temps de traitement < 5 minutes |
| Export données | Export CSV de 10 000 dossiers | Fichier généré, données cohérentes |

---

## 6. ENVIRONNEMENTS ET INFRASTRUCTURE

### 6.1 Contraintes d'hébergement

| Environnement | Type d'hébergement | Contraintes |
|---------------|-------------------|-------------|
| Développement | Poste de travail Docker Desktop | Autonome, sans dépendance réseau |
| Recette | Cloud ECO4 (souverain) | Accès via bastion, réseau RIE |
| Pré-production | Cloud ECO4 (souverain) | Isolation réseau, données anonymisées |
| Production | Cloud ECO4 (souverain) | Haute disponibilité, PRA/PCA |

### 6.2 Exigences de haute disponibilité et PRA/PCA

| Indicateur | Valeur | Mesure |
|------------|--------|--------|
| Disponibilité production | 99,5% mensuel | (Temps total - temps d'indisponibilité) / Temps total |
| RTO (Recovery Time Objective) | 4 heures | Temps maximum de rétablissement après sinistre |
| RPO (Recovery Point Objective) | 1 heure | Perte de données maximale acceptable |
| PRA | Site secondaire Cloud ECO4 | Basculement manuel ou automatique selon criticité |

### 6.3 Contraintes réseau et sécurité périmètrique

| Élément | Spécification |
|---------|---------------|
| Pare-feu | Ouverture ports 443 (HTTPS) uniquement en entrée |
| Reverse proxy | Apache HTTPD ou équivalent, configuration TLS 1.2+ |
| WAF | Recommandé (mod_security ou équivalent cloud) |
| Segmentation réseau | DMZ applicative, accès base de données uniquement depuis applicatif |

### 6.4 Spécifications des environnements

#### 6.4.1 Environnement de développement

| Composant | Spécification |
|-----------|---------------|
| Docker Desktop | Version stable récente |
| PostgreSQL | Image `postgres:15.2-alpine` ou supérieure |
| Tomcat | Image `tomcat:9-jdk8` ou équivalent |
| Volumes persistants | `sireines_db_sireines_vol` pour les données |

#### 6.4.2 Environnement de recette

| Composant | Spécification |
|-----------|---------------|
| URL d'accès | http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/ |
| Bastion | `sireinesrec` |
| Déploiement | Docker Compose sur VM dédiée |
| Base de données | Conteneur PostgreSQL avec volume persistant |

#### 6.4.3 Environnement de production

| Composant | Spécification |
|-----------|---------------|
| URL d'accès | https://sireines.e2.rie.gouv.fr/Accueil.do |
| Bastion | `sireinesprod` |
| Déploiement | Docker Compose ou orchestration Kubernetes |
| Base de données | Service managé PostgreSQL ou conteneur avec réplication |

---

## 7. QUALITÉ ET CONFORMITÉ

### 7.1 Référentiels de qualité applicables

| Référentiel | Domaine | Application |
|-------------|---------|-------------|
| ISO 9001 | Management qualité | Processus de maintenance et support |
| ISO 25010 (SQuaRE) | Qualité logicielle | Maintenabilité, fiabilité, sécurité |
| ISO 27001 (si certifié) | Sécurité de l'information | Gestion des risques sécurité |

### 7.2 Exigences de maintenabilité

| Exigence | Spécification | Mesure |
|----------|---------------|--------|
| Documentation du code | Javadoc obligatoire pour les classes et méthodes publiques | Taux de couverture > 80% |
| Complexité cyclomatique | Maximum 15 par méthode | Outil SonarQube |
| Duplication de code | Maximum 3% | Outil SonarQube |
| Dette technique | Correction des blockeurs et critiques dans les 30 jours | Tableau de bord SonarQube |

### 7.3 Exigences de performance

| Indicateur | Seuil acceptable | Seuil optimal | Mesure |
|------------|------------------|---------------|--------|
| Temps de réponse page simple | < 3 secondes | < 1 seconde | Tests de charge JMeter |
| Temps de réponse recherche complexe | < 5 secondes | < 2 secondes | Tests de charge JMeter |
| Temps de génération rapport BIRT | < 30 secondes | < 10 secondes | Tests manuels |
| Nombre d'utilisateurs simultanés | 50 | 100 | Tests de charge |
| Disponibilité | 99,5% | 99,9% | Monitoring |

### 7.4 Compatibilité et accessibilité

| Exigence | Niveau | Spécification |
|----------|--------|---------------|
| RGAA | Partiel | Niveau A obligatoire, niveau AA souhaitable |
| Compatibilité navigateurs | Obligatoire | Chrome, Firefox, Edge (2 dernières versions) |
| Responsive design | Souhaitable | Adaptation tablette (Bootstrap existant) |

---

## 8. DOCUMENTATION ET FORMATION

### 8.1 Liste des documents à fournir

| Document | Destinataire | Format | Fréquence de mise à jour |
|----------|--------------|--------|-------------------------|
| Document d'Architecture Technique (DAT) | MOA, MOE, RSSI | Markdown/PDF | À chaque évolution majeure |
| Dossier d'Installation et d'Exploitation (DIE) | Exploitation | Markdown/PDF | À chaque livraison |
| Guide utilisateur | Utilisateurs finaux | PDF/HTML | À chaque évolution fonctionnelle |
| Guide administrateur | Administrateurs techniques | Markdown/PDF | À chaque évolution technique |
| Documentation de l'API (si créée) | Intégrateurs | OpenAPI/Swagger | À chaque évolution |
| Procédures de secours | Exploitation, RSSI | Markdown/PDF | Annuelle |
| Registre des traitements RGPD | DPO | Excel/PDF | À chaque évolution |

### 8.2 Formats et standards de documentation

| Élément | Standard |
|---------|----------|
| Architecture | C4 Model ou équivalent |
| Modèles de données | PowerDesigner (fichiers .pdm, .oom) |
| Code source | Javadoc, commentaires pertinents |
| Procédures | Markdown, versionné dans GitLab |

### 8.3 Programme de formation

| Formation | Public | Durée | Contenu |
|-----------|--------|-------|---------|
| Prise en main fonctionnelle | Nouveaux utilisateurs | 1/2 journée | Navigation, saisie des dossiers, recherche |
| Administration technique | Administrateurs | 1 journée | Déploiement, configuration, supervision |
| Exploitation | Équipe d'exploitation | 1/2 journée | Sauvegardes, restaurations, procédures d'urgence |

---

## 9. TESTS ET RECETTE

### 9.1 Stratégie de recette et critères d'acceptation

| Phase | Type de recette | Responsable | Critère d'entrée | Critère de sortie |
|-------|-----------------|-------------|------------------|-------------------|
| Recette interne MOE | Tests unitaires et d'intégration | Prestataire | Livraison du code | Taux de bugs bloquants = 0 |
| Recette technique | Tests de sécurité, performance | MOA + RSSI | Validation MOE | Validation des critères de sécurité |
| Recette fonctionnelle | Tests métier, parcours utilisateurs | MOA métier | Validation technique | Validation des 10 scénarios critiques |
| Recette de conformité | Tests RGPD, accessibilité | DPO + MOA | Validation fonctionnelle | Conformité attestée |

### 9.2 Types de tests obligatoires

| Type de test | Outil suggéré | Couverture exigée |
|--------------|---------------|-------------------|
| Tests unitaires | JUnit | > 40% du code métier |
| Tests d'intégration | JUnit + DBUnit | Tous les DAO et services |
| Tests de sécurité (SAST) | SonarQube, OWASP Dependency-Check | 0 vulnérabilité critique |
| Tests de sécurité (DAST) | OWASP ZAP (si applicable) | Rapport de vulnérabilités |
| Tests de charge | JMeter | 50 utilisateurs simultanés |

### 9.3 Modalités de la recette fonctionnelle et technique

| Élément | Description |
|---------|-------------|
| Durée | 10 jours ouvrés maximum par livraison |
| Environnement | Recette identique à la production (hors données) |
| Jeu de données | Jeu de test représentatif (minimum 1000 dossiers) |
| Gestion des anomalies | Outil de suivi (GitLab Issues ou Mantis hérité) |
| Recette avec réserves | Acceptable si réserves mineures sans impact métier |

### 9.4 Gestion des anomalies

| Sévérité | Définition | Délai de correction |
|----------|------------|---------------------|
| Bloquante | Impossibilité d'utiliser une fonctionnalité critique | 24 heures |
| Majeure | Fonctionnalité dégradée, contournement possible | 5 jours ouvrés |
| Mineure | Dysfonctionnement marginal | 30 jours ouvrés |
| Cosmétique | Problème d'affichage sans impact fonctionnel | Prochaine livraison |

---

## 10. MAINTENANCE ET SUPPORT

### 10.1 Niveaux de support

| Niveau | Description | Intervenant |
|--------|-------------|-------------|
| N1 | Hotline utilisateur, diagnostic initial, FAQ | Prestataire ou MOA |
| N2 | Support technique, analyse approfondie, correction | Prestataire |
| N3 | Expertise technique, correction complexe, évolutions | Prestataire |

### 10.2 Délais d'intervention et de correction (GTR/GTD)

| Criticité | GTR (Guarantee Time to Respond) | GTD (Guarantee Time to Deliver) |
|-----------|--------------------------------|--------------------------------|
| Bloquante (production) | 1 heure (HNO inclus) | 4 heures |
| Majeure | 4 heures (HNO : 8h-20h) | 5 jours ouvrés |
| Mineure | 1 jour ouvré | 30 jours ouvrés |

**HNO :** Heures Non Ouvrées (week-ends, jours fériés, 20h-8h)

### 10.3 Engagements de disponibilité (SLA)

| Indicateur | Seuil | Pénalité si non atteint |
|------------|-------|------------------------|
| Disponibilité mensuelle | 99,5% | 1% du montant mensuel par 0,1% manquant |
| Temps de réponse moyen | < 2 secondes | Analyse corrective obligatoire |
| Taux de résolution au premier contact (N1) | > 60% | Plan d'amélioration |

### 10.4 Conditions de la garantie et maintenance évolutive

| Élément | Durée/Condition |
|---------|---------------|
| Garantie de bon fonctionnement | 3 mois après recette définitive de chaque livraison |
| Maintenance corrective | Incluse dans le forfait annuel |
| Maintenance évolutive | Enveloppe forfaitaire de [X] jours/hommes par an |
| Évolutions hors scope | Chiffrées à l'unité, validées par avenant |

---

## 11. LIVRABLES ET PLANNING

### 11.1 Liste détaillée des livrables attendus

| Livrable | Format | Échéance |
|----------|--------|----------|
| Code source complet | GitLab (dépôt sécurisé) | À chaque livraison |
| Fichier WAR déployable | `sireines-web-[version].war` | À chaque livraison |
| Images Docker | Registry GitLab ou GCP | À chaque livraison |
| Scripts SQL de migration | Fichiers `.sql` versionnés | À chaque évolution BDD |
| Documentation technique | Markdown/PDF | À chaque livraison majeure |
| Rapport de tests | PDF | À chaque livraison |
| Dossier de recette | PDF | À chaque livraison |

### 11.2 Format et modalités de livraison

| Élément | Spécification |
|---------|---------------|
| Gestion de versions | Semantic Versioning (MAJOR.MINOR.PATCH) |
| Branche GitLab | `develop` → `recette` → `preprod` → `main` (production) |
| Livraison recette | Pipeline CI/CD GitLab manuelle |
| Livraison production | Pipeline CI/CD GitLab avec validation manuelle |
| Notification | Email à la MOA avec notes de livraison |

### 11.3 Jalons du projet et échéances

| Jalon | Description | Date indicative |
|-------|-------------|-----------------|
| M1 | Prise de connaissance et audit technique | J+30 |
| M2 | Livraison corrective initiale (bugs hérités) | J+60 |
| M3 | Première évolution fonctionnelle | J+90 |
| M4 | Revue annuelle et plan de modernisation | J+365 |

### 11.4 Pénalités de retard

| Retard | Pénalité |
|--------|----------|
| > 5 jours ouvrés sur un jalon | 0,5% du montant du lot concerné par jour de retard |
| > 15 jours ouvrés | Résiliation possible du marché pour faute |

---

## 12. CONTRAINTES LÉGALES ET RÉGLEMENTAIRES

### 12.1 Propriété intellectuelle et droits d'auteur

| Élément | Disposition |
|---------|-------------|
| Code source développé | Propriété exclusive du pouvoir adjudicateur |
| Code source existant (hérité) | Licences existantes conservées |
| Documentation | Propriété exclusive du pouvoir adjudicateur |
| Cession des droits | Totale et définitive dès paiement |

### 12.2 Licences des composants et logiciels tiers

| Composant | Licence | Contrainte |
|-----------|---------|------------|
| Apache Struts 2 | Apache 2.0 | Mention obligatoire |
| Vertigo | [À vérifier] | Conformité licence |
| PostgreSQL | PostgreSQL Licence | Libre |
| Elasticsearch | SSPL/Elastic License | Vérifier conformité usage |
| BIRT | EPL 1.0 | Mention obligatoire |
| Bootstrap | MIT | Mention obligatoire |
| Cerbère client | Propriétaire État | Usage restreint aux SI de l'État |

**Obligation :** Fourniture du SBOM (Software Bill of Materials) à chaque livraison.

### 12.3 Protection des données personnelles (RGPD)

| Traitement | Finalité | Base légale |
|------------|----------|-------------|
| Gestion des qualifications | Suivi des compétences des agents | Mission de service public |
| Annuaire des rapporteurs | Organisation des comités de domaine | Mission de service public |
| Historique des dossiers | Traçabilité des décisions | Obligation légale (archives) |

**Durée de conservation :** 10 ans après la fin de carrière de l'agent (archives).

### 12.4 Archivage et conservation des données

| Type de données | Durée de conservation | Support |
|-----------------|----------------------|---------|
| Données actives | Durée de vie du contrat | Base de données PostgreSQL |
| Données intermédiaires | 1 an | Export CSV archivé |
| Données définitives | 10 ans après fin de carrière | Archivage électronique (SAE) |

---

## 13. CRITÈRES DE SÉLECTION DES OFFRES

### 13.1 Pondération des critères

| Critère | Pondération | Sous-critères |
|---------|-------------|---------------|
| **Prix** | 40% | Coût total de possession (3 ans) |
| **Valeur technique** | 60% | Voir détail ci-dessous |

### 13.2 Détail de la valeur technique (60 points)

| Sous-critère | Points | Excellent (100%) | Satisfaisant (70%) | Insuffisant (< 50%) |
|--------------|--------|------------------|-------------------|---------------------|
| Méthodologie de maintenance | 10 | Méthode agile éprouvée, outils de suivi intégrés | Méthode structurée, outils basiques | Méthode peu formalisée |
| Expertise technique (Java 1.7/Struts) | 10 | 3+ ans d'expérience sur stack similaire | 1-3 ans d'expérience | Expérience insuffisante |
| Proposition de modernisation | 15 | Roadmap claire, migration Java 17, framework moderne | Proposition partielle, Java 11 | Sans proposition de modernisation |
| Sécurité (RGS, RGPD) | 10 | Certifications, processus sécurité robustes | Connaissance des référentiels | Insuffisance manifeste |
| Performance et optimisation | 5 | Optimisation BDD, cache, requêtes | Optimisation standard | Sans optimisation |
| Tests et qualité | 5 | TDD, couverture > 60%, CI/CD complète | Tests présents, CI/CD basique | Tests insuffisants |
| Documentation et transfert | 5 | Documentation exhaustive, plan de formation | Documentation standard | Documentation insuffisante |

### 13.3 Modalités de notation

| Note | Seuil |
|------|-------|
| Excellent | 100% des points du critère |
| Satisfaisant | 70% des points du critère |
| Passable | 50% des points du critère |
| Insuffisant | 0% des points du critère |

**Seuil d'admissibilité :** Minimum 50% sur la valeur technique pour être retenu.

---

## 14. ANNEXES CONTRACTUELLES

### Annexe A — Glossaire

| Terme | Définition |
|-------|------------|
| **SIREINES** | Système d'Information pour la Recherche et l'Évaluation des compétences INtEgrées Scientifiques |
| **Cerbère** | Solution d'authentification unique (SSO) de l'État |
| **BIRT** | Business Intelligence and Reporting Tools (Eclipse) |
| **Vertigo** | Framework Java de développement (Klee Group) |
| **KSP** | Klee Script Procedure (langage de requêtage Vertigo) |
| **MDA** | Model Driven Architecture (génération de code) |
| **RIE** | Réseau Interministériel de l'État |
| **ECO4** | Cloud souverain de l'État |

### Annexe B — Références normatives

| Référence | Description |
|-----------|-------------|
| Code de la commande publique | Articles R. 2161-1 et suivants (CCTP) |
| RGS v2.0 | Référentiel Général de Sécurité (ANSSI) |
| RGPD | Règlement (UE) 2016/679 |
| RGI 2.0 | Référentiel Général d'Interopérabilité |
| RGAA 4.1 | Référentiel Général d'Amélioration de l'Accessibilité |
| ISO 25010 | Systèmes et logiciels — Modèle de qualité |
| OWASP ASVS 4.0 | Application Security Verification Standard |

### Annexe C — Modèles de documents

#### C.1 Fiche de renseignement technique (à compléter par le candidat)

| Élément | Réponse du candidat |
|---------|---------------------|
| Version Java utilisée | |
| Version Struts utilisée | |
| Version PostgreSQL supportée | |
| Expérience équivalente (nombre de projets) | |
| Références clients (3 minimum) | |
| Équipe projet proposée | |
| Outils de gestion de projet | |
| Outils de qualité (SonarQube, etc.) | |

#### C.2 Grille de conformité technique (à compléter par le candidat)

| Exigence | Conforme | Partiellement | Non conforme | Commentaire |
|----------|----------|---------------|--------------|-------------|
| Java 1.7/Struts 2 | ☐ | ☐ | ☐ | |
| Intégration Cerbère | ☐ | ☐ | ☐ | |
| Dockerisation | ☐ | ☐ | ☐ | |
| Tests automatisés | ☐ | ☐ | ☐ | |
| Migration Java 17 proposée | ☐ | ☐ | ☐ | |

---

**Fait à** [lieu], **le** [date]

**Pour le pouvoir adjudicateur :**

[Nom et qualité du signataire]

**Signature :**

---

*Document contractuel — Toute modification fait l'objet d'un avenant signé par les parties.*