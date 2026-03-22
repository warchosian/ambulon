Entretien pro 2026
------
Objectifs
1]
Expoiter les données du WikiSI
via l'IA au travers d'une
interface en langage naturel du
type "chatbot

- Production d'un benchmark
exploratoire des LLMs du marché- Poursuite des travaux de mise en
forme des données du WikiSI pour
exploitation par un LLM,- Réalisation d'un POC de Chatbot
permettant l'exploitation de ces
données avec appui d'un collègue du
GTI et en collaboration avec DPTN,- Appui à l'industrialisation du POC qui
sera à réaliser par DPTN (ressources
matérielles notamment) via
l'exploitation des architectures
éprouvées par des projets similaires,

Notes

Utilisation du PIAG pour la création du chatbot en utilisant Mistral Medium (le PIAG fait continuellement évoluer son offre). 
Tests concluant mais choix du LLM restreint la qualité des réponses. En attentente de l'ouverture de l'API pour les tests à distance.
Offre en continuelle trandformation.

L'API PIAG RAG ne contient pas dans ses services l'envoi d'une question. Pour l'heure, constitution automatisée de collections (RAGS) avec les documents constitutifs.
Elle ne communique pas avec les RAG du chatbot. C'est juste relié à un LLM.
Elle ne permet pas automatiquement d'envoyer une question à un LLM mais il y a l'API PIAG CHAT pour cela.
Test concluant mais impossibilité de faire des bancs de test.
A la place de cela, nous devons faire des tests manuels et cela sur le PIAG avec des questions posées sur des rag alimentés ave des données d'applications. 
Ces données sont extraite et formatés avec des outils de  notre conception (traitement de la wikisi, de la wiki de gitlab et des sources)).  
beta testeur?

Liens : Etudes comparatives.

----

2]

Assurer les déploiements
manuels et la reprise sur
incident des produits
containérisés du département

- Déploiement des nouvelles versions
applicatives sur le IaaS notamment,- Redémarrage sur incident,- Vérifier régulièrement la validité des
accès machines à utiliser en cas de
besoin

Notes

Associé aux demandes et prises de notes.
Mais test d'installation pour Sireine en cours (documentation) et comprendre le nouveau système de déploiement (infratsructure des bastions a évolué).

Réunion socle les les lundi à 14h00 (avec GTI), la personne était malade.
------

3]

Mobiliser l'IA et les techniques
associées pour la génération
automatisée de documentation

- Proposition d'un POC pour la
génération, la complétion ou
l'amélioration de la documentation
d'un projet legacy- Déterminer les limites applicables, le
cas échéant, sur un tel projet (taille de
la codebase, prérequis, coût, etc)- Exemple visé a priori : TTC (calcul des
temps de trajets compensés)

Notes
Etude de divers LLM locaux, des technologies et de rétroanalyse 
a été effectuée (SIREINES, Decommissionement optimatl (DAT), GESAPP, ). 
Générer des pages HTML par IA en utilisant SPHYNX, PYDOC, MKDOXS, D'OXYGEN. Mais ces pages étaient complexes à intégrer à GITLAB. Une autre 
Sphynx Python -> Ambulon
Création des LLM pour chaque application de PNM 3.

Pour le reverse, grosse étude dur le diagramming.

Phase d'installation pour utilisation locale.
Remarque : Le finetuning doit rentrer dans l'offre du PIAG.


Compléments relative sur la qualimétrie de code, Finetuning.
Liens : 


------

4]

Participer à l'amélioration de
l'outil d'urbanisation GUSI et de
son plan des sols

- Participation à l'amélioration des
données liées aux SI du département
dans WikiSI,- Participation aux ateliers et réunions
portant sur l'amélioration des vues
techniques, métiers et fonctionnelles
de GUSI,

- Participation aux études
d'ajustements du système de
confidentialité lié à GUSI,

Notes

Evolution en cours au sujet du WIKI SI, champs "composants" des fiches des applications, des nouveaux cycles et versions disponibles, 
rapport hebdomadaire sur la gestion des composants d'une sélection d'applications généré, 
En cours

Wiki SI MOA : Les application pour lesquelles la DG est identifiée comme MOA dans Wiki SI (quelque soit le type de MOA)

Wiki SI carto : Les applications de Wiki SI ou la DG à un rôle (quel qu’il soit) et qui sont intégrées à la cartographie. Ces applications se retrouvent via l’accès « organigramme »

myGusi MOA : Les applications, par DG, ayant une représentation cartographique. 

EST A CREUSER / DECIDER  :
Faire des cartes fonctionnelles de données comme sont faites les cartes d’applications ?
2 POS distincts pour accéder aux applications d’une part et aux données d’autres part  possible mais pas le découpage fonctionnel doit pouvoir être différent

ORIENTATION PRISE sur le périmètre SI Fédérateurs
Faire des cartes permettant de l’urbanisation des données (vision plus macro notamment tirée par les SI Fédérateurs) ?
S’appuyer sur un regroupement d’application (exemple du cadre légal des SI Fédérateurs injectés dans Wiki SI) et faire de nouvelles cartes de flux inter-SI (en complément des cartes existantes / en cours de mises à jour)


Paramétrage déjà réalisé.
Les acteurs SI Fédérateurs seront « habilités » à renseigner / modifier cette nouvelle information (la traçabilité complète des modifications de fiche restant la règle)

Nexts steps 2025 :
Finalisation des GT « profil » et « données »
Intégration SI Fédérateurs
Intégration DREAL Hauts de France
Lancement des travaux 2026

Travaux 2026 :
Problèmes suites sur SI Fédérateurs et intégration DREAL Hauts de France
Lancement de GT sur de nouveaux thèmes (propositions en cas de besoin)

Pour votre information, la dernière version de myGusi vient d'être mise en ligne. Elle contient la nouvelle vision par flux et objets métiers présentée lors du dernier club des référents.

La création des flux et des objets métiers est à faire par les agents directement dans le WikiSI.

slide 31 à présenter


-----------

Liste des formations effectuées?

Mettre les attestations

 Kubernetes - Orchestration des conteneurs » du 1 décembre 2025 au 2 décembre 2025.
 IA Générative - Les modèles de langages massifs (LLMs) (BI108) planifiée du 08/12/2025 au 09/12/2025.
Big Data - Supervision de solutions avec Grafana, Kibana, Graphite et Prometheus (BD570) qui se déroulera, à distance, du 24/11/2025 au 26/11/2025.
 « Data Science - Les fondamentaux » du 16 octobre 2025 au 17 octobre 2025.
 Docker - Administration avancée (XW334) qui se déroulera, à distance, du 27/10/2025 au 28/10/2025.
 « PostgreSQL - Tuning » du 6 octobre 2025 au 7 octobre 2025.
 Vue.js 3 - Développement d'applications Web (LI270) planifiée du 03/09/2025 au 05/09/2025.


  Analyse de Sécurité
Secret Scanning : Détection de secrets hardcodés (mots de passe, tokens API, clés privées)
Taint Analysis : Analyse de flux de données pour détecter les vulnérabilités d'injection (SQL, XSS, Command Injection)
CodeQL Integration : Analyse sémantique avancée avec les requêtes CodeQL
SonarQube Plugin : Intégration avec SonarQube pour l'analyse continue
📊 Analyse de Qualité
Semantic Analysis : Détection de code complexe, fichiers trop longs, fonctions excessives
Encoding Verification : Vérification de l'encodage UTF-8 des fichiers
SARIF Reports : Génération de rapports au format SARIF pour intégration CI/CD
