# Dossier d'architecture technique

**Document en chantier**

[TOC]

## Introduction et objectifs

### Vue d'ensemble

**Brève** description fonctionnelle du système créé.

Un résumé du système accompagné d'un schéma de blocs fonctionnels ou des principaux cas d'usage est adapté.

### Objectifs principaux de qualité

Indiquez ici les trois (maximum cinq) principaux objectifs de qualité auxquels devra répondre l'architecture retenue. Expliquez en quoi ces objectifs sont importants.<br>
La suite du document doit montrer comment l'architecture retenue répond à ces objectifs.

Il s'agit ici d'objectifs de qualité **orientés utilisateurs du système** (au sens large : bénéficiaires directes, exploitants, etc.). Ne les confondez pas avec les objectifs du projet. Ils ne sont pas nécessairement identiques. 

[Quelques **exemples** non exhaustifs](https://quality.arc42.org/  ) issus de Arc42. Cele reste des exemples, ils sont déclinables et doivent être **contextualisé au système** : 

- Fiable le système doit fonctionner sans panne ni défaut en mode nominal
- Flexible : le système est à même de s'adapter simplement à des exigences évolutives.
  - Ex. "*Les evolutions de la réglementation doivent être intégrables simplement et à coûts réduits.*"
- Efficient : le système peut fonctionner de bonne manière avec des ressources raisonnables, réduites. Un objectif de responsablité numérique. Le système peut évoluer à coût et délai maitrisé.
- Utilisable : le système est compréhensible de ses utilisateurs, non complexe à l'usage. Cela comprends tous les utilisateurs, donc les aspects d'accessiblité.
  - Ex : "*Le système doit être utilisable sur la tablette de l'inspecteur en visite terrain*"
  - Ex : "*Les graphiques et autres visualisations doivent tenir des comptes des difficultés visuelles (ex. daltonismes) et intégrer systématiquement un résumé textuel*"
- sûr : le système ne met pas en danger des vies humaines et plus globalement son environnement.  
- Sécurisé : le système protège ses données et son intégrité. Les données ne sont accssibles et modifiables que par leurs ayants-droits. Le sytème fait l'objet d'une maintenance régulière.
  - Ex. "*Tout modification des données est conditionné à une authentification sur un fournisseur d'idenitité reconnu (Cebere, AgentConnect, FranceConnect).*"
  - Ex. "*Toute modification des données doit être consignée dans un journal d'audit.*"
  - Ex. "*Toute modification de dossier doit être notifiée par mail à son bénéficaire.*"
- opérable : le système est déployable, exploitable, réparable sans complexité, à coûts convenus. Il est interopérable avec son environnement.
  - Ex. "*Le système doit pouvoir s'interfacer avec tout nouvel équipement de collecte transmettant ses données au format xxx.*"
  - Ex. "*Le déploiement d'une nouvelle version ne doit pas excéder 15'.*"
  - Ex. "*Le système doit exposer des métriques permettant sa surveillance en temps réel.*"

Exemples pratiques

### Parties prenantes

Vue d'ensemble explicite des parties prenantes du système, c'est-à-dire toutes les personnes, rôles ou organisations qui

- doivent connaître l'architecture ou
- doivent être convaincu de l'architecture ou
- doivent travailler avec l'architecture ou avec le code ou
- ont besoin de la documentation d'architecture pour leur travail ou
- doivent prendre des décisions concernant le système ou son développement ou

Ceci pour avoir une bonne vision des personnes ou organisations concernées par les choix architecturaux

Un tableau est la façon la plus efficace pour lister ces personnes ou organisations.

| Rôle/Nom    | Contact                   | Attentes       |
| ----------  | ------------------------- | -------------- |
| Role-1      | Contact-1 (@ typiquement) | Attente rôle 1 |
| Role-2      | Contact-2 (@ typiquement) | Attente rôle 2 |

## Constraintes 

### Contraintes d'architecture

Indiquez ici youte exigence qui limite la liberté des architectes dans leurs décisions de conception et de mise en œuvre ou dans leurs décisions concernant le processus de développement.

Les architectes doivent savoir exactement où ils sont libres dans leurs décisions de conception et où ils doivent respecter des contraintes. Les contraintes doivent toujours être prises en compte ; elles peuvent toutefois être négociables.

Les contraintes peuvent être de natures diverses : techniques, organisationnelles, politiques et convention, etc.

Exemples : 

- *Les developpement doivent se faire dans le langage xxx pour harmonisation avec les autres applications du SI (ou parceque compétences acquises de l'équipe).*
- *Le système doit être consultable sur un terminal mobile (smartphone)et bureau (desktop) avec la même application. Le budget et les ressouces ne permettent de développer une application native mobile.*
- *Le système sera publié en licence libre, il ne doit pas intégrer de composants sous licences.*
- *Une première version doit être ouverte à la date XXX pour raison réglementaire.*
- *Le système sera déployé sur le cloud xxx sur l'offre yyy*"

### Contraintes de sécurité

Indiquer ici les exigences de sécurité du système en terme de D(isponibilité), I(ntégrité), C(onfidentialité) et T(raçabilité).

## Contexte et périmètre

Le contexte et le périmètre délimitent votre système (c'est-à-dire votre périmètre) de tous ses partenaires de communication (systèmes voisins et utilisateurs, c'est-à-dire le contexte de votre système). Il spécifie ainsi les interfaces externes.

Le système est ici vue comme une **boite noire**

Les interfaces de domaine et les interfaces techniques avec les partenaires de communication font partie des aspects les plus critiques
de votre système.

Privilégiez une représentation simple et directe, schémas et tableaux, à un descriptif verbeux.

Les contextes métiers er techniques peuvent être fusionnés ou conservés distincts selon la complexité du système.

### Contexte métier

Spécification de **tous** les partenaires de communication (utilisateurs, systèmes informatiques, ...) avec des explications la nature fonctionnelle de l'interface (référentiel, service de validation, authentification, etc.)

### Contexte Technique

Descriptif succinct des interfaces techniques, des protocoles utilisés pour interconnecter les systèmes tiers.

N'entrez pas à ici dans le détail du protocole : https/443 OK, détails xml/json/etc. non. Si vous estimez nécessaire de détailler le format, faite le dans un document annexe et référencez le ici. 

## Stratégie de solution

Un résumé et une explication des décisions fondamentales et des stratégies de solution qui façonnent l'architecture du système. Il
comprend.\
Les explications relatives à ces décisions clés doivent être brèves et motivées si non évidentes. La motivation repose sur les objectifs de qualités et les contraintes.

- les décisions technologiques
- les décisions relatives à la décomposition du système au niveau le plus élevé, par exemple l'utilisation d'un modèle architectural ou d'un modèle de conception
- les décisions sur la manière d'atteindre les principaux objectifs de qualité
- les décisions organisationnelles pertinentes, par exemple la sélection d'un processus de développement ou la délégation de certaines tâches à des tiers.

Les sous-chapitres suivants peuvent être complétes selon les besoins et la complexité du système.

### Modèles de conception - Décisions d'architecture

Indiquez les principaux modèles de conception retenus accompagnés d'une brève motivation. Ce chapitre doit rester synthétique, si un choix justifie d'une explication détaillée faite le en annexe dans une [décision d'architecture -ADR](https://adr.github.io/  ) et réféfencez là ici.

Exemples :

- *Conception monolithe au vu de la simplicité du système et du couplage fort de tous ses services.*
- *Conception micro-services pour découpage des responsabilités et déploiements différenciés*
- *Exposition par API pour ouverture de la données (opendata)*
- *Bus de message, asynchronisme pour gestion des fortes charges ou des tâches différées*
- *etc.*

### Environnement technologique

Listez les solutions logicielles retenues: langage, produits logiciels, frameworks, etc.  

### Forge logicielle - CI/CD

Indiquez les solutions retenues pour gérer les sources applicatifs et les processus de construction (*build*) et déploiement (*run*).

## Vue en Briques

La vue en briques montre la décomposition statique du système en briques ainsi que leurs dépendances
(relations, associations, ...).

Cette vue est obligatoire pour toute documentation sur l'architecture. Par analogie avec une maison, il s'agit du *plan de masse*.

Plusieurs niveaux de vue sont possibles. Le [formalisme C4](https://c4model.com/  ) par exemple propose 4 niveaux

- Vue contextuelle, le système en tant que boite noire dans son ensemble. Si cette vue n'a pas été réalisée dans le chapitre "Contexte" vous pouvez la fournir ici.
- Vue conteneur (un conteneur est un élément déployable, exécutable, par forcément un conteneur OCI/Docker). Cette vue est obligatoire ici, c'estla vue en **boîte blancheù* de plus haut niveau. Fournissez un schéma décrivant l'ensemble des éléments déployés et leurs interactions.
- Vue en composants : un zoom sur chaque conteneur (au sens déploiment). Schématisez et décrivez **brièvement** les principaux conposants de chaque conteneur.
- Vue code: l'implémentation sous forme de code de chaque composant, sous forme par exemple de diagramme de classe. **Cette vue n'est pas souhiatée ici car trop fine**. Dans li'idéal le code doit être suffisament clair, structuré et documenté pour qu'un développeur n'ai pas besoin de ces vues pour comprendre le système. Si vous estimez préférable d'en disposez parcque votre organisation s'y prête ou par forte complexité du code, alors annexez le ou faire en un document distinct (conception logicielle).


## Vue Exécution

La vue d'exécution décrit le comportement concret et les interactions des briques du système sous la forme de scénarios.

Il n'est pas question de décrire ici tous les scénarios d'usages possibles du système. Retenez ceux qui se détachent par leur complexité, leur criticité ou leur particularité architecturale (ceux dont la compréhension n'est pas "évidente, immédiate").

Ces scénarios peuvent être décrits par exemple sous la forme de diagrammes de séquence, d'autres formalismes sont possibles.

### Scénario 1

Description scénario 1

### Scénario 2

Description scénario 2

[ ... Autres scénarios ... ]

## Vue Déploiement

La vue déploiement décrit l'infrastructure technique utilisée pour exécuter votre système avec des éléments d'infrastructure tels que les emplacements géographiques, les environnements, les serveurs, les processeurs, les canaux et les topologies de réseau, ainsi que d'autres éléments d'infrastructure, et la correspondance entre les briques (logicielles) et les éléments d'infrastructure.

Une représentation par schéma et/ou tableaux est appropriée. Plusieurs niveaux de vue sont possibles selont la complexité du système


Les systèmes sont souvent exécutés dans différents environnements, par exemple l'environnement de développement, l'environnement d'intégration, l'environnement de production, etc.

- Listez ces environnement
- Il est fortement recommandé que tous ces environnements soient similaires. Si tel n'est pas le cas décrivez les particularités de chacun d'entre eux.

## Sujets transverses

Ce chapitre concerne les sujets communs aux différentes briques du système, souvent non rattachables à un domaine métier. Ce sont souvent ds sujets génériques, quelques exemples ni exhaustifs ni systématiques :

- Mécanismes d'authentification (utilisateur, système)
- Gestion des API
- Mécanismes de journalisation, de traçabilité
- Règles ORM
- etc.

## Exigences de qualité

Lstez ici les exigences de qualités de façon plus complète que les principales déja citées en introduction. Les exigences de qualités sont un entrant essentiel des les choix d'architecture, elles sont pilotées par les besoins métiers, par l'expérience utilisateur.\

Pour chaque exigence retenue rédiger un scénario permettant de vérifier qu'elle est satisfaite.

Arc42 propose [un ensemble de critères de qualités](https://quality.arc42.org/  ) sur lesquels vous pouvez vous appuyer, ou en retenir d'autres. Il est important que chaque exigence fasse l'objet d'un ou plusieurs scénario(s) permettant de valider sa réalisation.

## Risques et Dettes techniques

Listez les risques ou dettes techniques identifiés, classés par ordre de priorité.\
Suggerez les mesures à prendre pour y remédier.

Exemples de risques

* *L'interface avec le système XXX impose un format défini par la norme ISO XXXX dont l'accès n'est pas aisé et gratuit pour les nouvaux venus*.
  - *=> Acquérir une exemple de cette norme pour le projet et rédiger une prise en main pour les nouveaux venus.*
- *Le système repose sur le framework XXX dont le support d'une version est limité à un an*
  - *=> Assurer une mise à jour régulière de ce framework, annuelle au plus*


## Crédits

Ce modèle est une adaptation des modèles de [Arc42](https://arc42.org  ) ( [License](https://arc42.org/license  ) ).

Principaux changements apportés :

- 
- Regroupement des chapitres "Stratégie de solution"  et "Décisions d'architectures" pour simplifier la rédaction du document et réduire les risques de redondances.

## Annexes

### Glossaire

Listez les termes et acronymes dont le compréhension de tous n'est pas acquise.

### Décisions d'architectures - ADR

Insérez les décisions d'architecture prise sous forme d'ADR, tel que mentionné dans le chapitre "Stratégie de solution"