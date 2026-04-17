# 📌 Meta Data
---
Titre: DEX  
projet: $TitreProjet  
- statut:`🟥 À faire` `🟨 En cours` `🟩 Terminé` `obsolete`
- priorité: `🔴 Haute` `🟠 Moyenne` `🟢 Basse` `⚪ Inconnue`
- validation: `✅` `❌`
- tags: #DEX, #TitreProjet, #statut/en-cours, #priorite/haute



# Sommaire

- [📌 Meta Data](#-meta-data)
- [Sommaire](#sommaire)
- [DEX-Template](#dex-template)
  - [**Attention ce document décrit un certain nombre de procédure et fonctionnement de l'application mais il ne doit contenir AUCUN mot de passe ou identifiant.**](#attention-ce-document-décrit-un-certain-nombre-de-procédure-et-fonctionnement-de-lapplication-mais-il-ne-doit-contenir-aucun-mot-de-passe-ou-identifiant)
  - [Historique de version](#historique-de-version)
  - [Généralités](#généralités)
  - [Documents applicables et de référence](#documents-applicables-et-de-référence)
  - [Terminologie](#terminologie)
  - [Spécificités](#spécificités)
  - [Architecture](#architecture)
  - [Serveurs](#serveurs)
  - [Application](#application)
  - [Supervision et Métrologie](#supervision-et-métrologie)
  - [Sauvegardes](#sauvegardes)
  - [Stockage](#stockage)
  - [Inventaires Bases](#inventaires-bases)
  - [Flux inter applicatifs](#flux-inter-applicatifs)
  - [Plan de Production](#plan-de-production)
  - [Sécurisation des images](#sécurisation-des-images)
  - [Opérations courantes](#opérations-courantes)
  - [Opérations récurrentes](#opérations-récurrentes)
  - [Annexes](#annexes)

---

# DEX-Template
**Attention ce document décrit un certain nombre de procédure et fonctionnement de l'application mais il ne doit contenir AUCUN mot de passe ou identifiant.**
---
## Historique de version
|date | version |statut|
| xx-xx-xxxx | 0.1 | initialisation|

---
## Généralités<a name="generalites"></a>

**Objet du document**  
Résumé du contenu de ce document pour le maintien en conditions opérationnelles et de l'exploitation technique de l'application.

**Domaine d'application**  
Périmètre d'application de ce document

**Audience**  
Liste des parties prenantes en destination de ce document

---

## Documents applicables et de référence<a name="documents-applicables-et-de-reference"></a>

**Documents Applicables et de Référence**  
Liste des documents servant de base de travail et complétant ce Dex.

---

## Terminologie<a name="terminologie"></a>

**Définitions**  
Explications des termes techniques.

**Abréviations**  
Liste des abréviations utilisées.

---

## Spécificités<a name="specificites"></a>

**Fonctionnalités**  
Description fonctionnelle du produit.

**SLA et plage de maintenance**  
Définitions des taux de disponibilité et de plages de maintenance.

**Définition des niveaux d'incident (P1/P2/ ...)**  
Définition de la criticité des incidents.

**Communication en cas de P1/P2 sur la PROD**  
Processus de communication lors des incidents critiques.

**Contacts**  
Liste des contacts essentiels (MOA, MOE, infogérance, hébergeur, ...)

**Procédure d’escalade**  
Définitions des niveaux d’escalade et processus d'escalade

---

## Architecture<a name="architecture"></a>

**Environnements**  
Détails des différents environnements de l'application (production, préproduction, recette, école ).

**Schéma de Production Infra**  
Description de l'infra de production.

**Schéma de Production Applicatif**  
Structure applicative de PLAT’AU.

**Flux**  
Modalités des flux au sein de l'application.

**Plan de bascule multisite: PRA, PCA**  
Description du protocole de PRA/PCA pour basculer les opérations en cas de sinistre.

---

## Serveurs<a name="serveurs"></a>

**Connexion à la console d'administration**  
Instructions pour se connecter à l’interface d'administration.

**Connexion aux serveurs**  
Modalités de connexion aux serveurs et outils associés (supervision, file d'attente, ...).

**Caractéristiques des Serveurs**  
Spécifications techniques des serveurs.

---

## Application<a name="application"></a>

**Logiciels des socles techniques mis en œuvre**  
Listes des composants logiciels utilisés.

**Namespace applicatif - Rôles des conteneurs**  
Rôles spécifiques des conteneurs au sein de l'application.

**Description du chemin critique de l’application**  
Ordre de démarrage requis pour l'application.

**Sécurisation de l’application**  
Politiques de sécurité appliquées.

**Procédure d’installation / déploiement**  
Instructions pour le déploiement et intégration continue.

---

## Supervision et Métrologie<a name="supervision-et-metrologie"></a>

**Kibana, suricate, grafana**  
Accès et gestion des outils de supervision pour la métrologie.

**PSIN**  
Page PSIN pour le monitoring et description des scénarii existants. 

---

## Sauvegardes<a name="sauvegardes"></a>

**Procédures de sauvegarde**
Détail des procédures de sauvegarde en place par environnement

**Bases de données**  
Détail des sauvegarde et restauration de base de donnée

**Fichiers binaires**  
Détail des sauvegarde et restauration du système de fichier

**Conteneurs**  
Détail des sauvegarde et restauration des conteneurs

---

## Stockage<a name="stockage"></a>

Présentation des types de stockage utilisés: Block et Objet. Méthode d'accès, serveurs. 

---

## Inventaires Bases<a name="inventaires-bases"></a>

**Bases MongoDB**  
Description des bases de données MongoDB et de leur usage. Méthode d'accès, serveurs. 

---
## Flux inter applicatifs<a name="flux-inter-applicatifs"></a>

Résumé des flux entre les différentes applications et composants (ports ourverts, flux entre les composants, flux ouverts vers l'extérieur).

---

## Plan de Production<a name="plan-de-production"></a>

**Ordonnanceur**  
Instructions pour l'ordonnancement des tâches.

**Tâches planifiées**  
Liste des tâches planifiées, notamment pour les sauvegardes.

---

## Sécurisation des images<a name="securisation-des-images"></a>

**Outil de scan des images**  
Utilisation de Harbor pour la vérification et le scan des images (harbor, trivy, container registry).

---

## Opérations courantes<a name="operations-courantes"></a>

**Vérification d’Aptitude au Bon Fonctionnement – VABF**  
Normes de vérification pour le bon fonctionnement des systèmes.

**Connexion aux composants**  
Guide pour la connexion aux principaux composants comme RabbitMQ.

**Erreurs connues et solution de contournement**  
Explications des erreurs courantes et les solutions appliquées.

---

## Opérations récurrentes<a name="operations-recurrentes"></a>

Instructions pour les tâches récurrentes incluant l'ajout d'utilisateurs, opérations sur la base, DNS update, et plus.

---

## Annexes<a name="annexes"></a>
---
