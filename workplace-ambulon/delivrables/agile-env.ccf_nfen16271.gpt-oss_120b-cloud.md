# Cahier des Charges Fonctionnel (CCF) – Projet **agile‑env**  
*Conforme à la norme NF EN 16271 :2013 – Management par la valeur*  

> **Version** : 1.0 – 28 avril 2026  
> **Auteur** : Expert Valeur – Service Management par la Valeur  
> **Référence projet** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\agile‑env`  

---  

## 1. Présentation du projet  

| Élément | Description |
|---------|-------------|
| **Contexte** | Le projet *agile‑env* a pour vocation de fournir un **environnement de développement reproductible** pour les équipes de la DSI RIE (gouvernement français). L’environnement doit permettre de développer, tester et valider des applications web PHP / Apache en interaction avec une base de données PostgreSQL, le tout sous forme de conteneurs Docker afin de garantir portabilité, isolation et traçabilité. |
| **Enjeux stratégiques** | • Accélérer le cycle de vie logiciel (CI/CD). <br>• Réduire les coûts d’infrastructure (mutualisation des machines). <br>• Garantir la conformité aux exigences de sécurité (proxy d’entreprise, RGPD, RGS). <br>• Assurer la **valeur** ajoutée en limitant les gaspillages (temps de mise en place, dépendances superflues). |
| **Objectifs du projet** | 1. Déployer un **stack** (Apache + PHP + PostgreSQL) via Docker, sans imposer de technologie précise aux équipes (fonctionnalité « environnement de travail » uniquement). <br>2. Permettre la configuration d’un **proxy HTTP** d’entreprise et la gestion d’environnements (variables d’environnement, fichiers de configuration). <br>3. Garantir la **traçabilité** des versions d’image et des paramètres d’exécution. |
| **Périmètre fonctionnel** | **Inclus** : <br>• Conteneur Apache/PHP (v7.3 ou supérieur). <br>• Conteneur PostgreSQL (v11 ou supérieur). <br>• Gestion des variables d’environnement et des fichiers de configuration (`.env`, `param.ini`, `config_CAS.php`). <br>• Orchestration via `docker‑compose`. <br>• Documentation d’utilisation (README). <br>**Exclus** : <br>• Déploiement en production (hors scope). <br>• Gestion du code applicatif (hors de l’environnement). |

---  

## 2. Analyse de la valeur  

### 2.1 Fonctions de service (FS)  

| Ref. | Fonction de service | Type | Description |
|------|---------------------|------|-------------|
| **FS‑01** | **Fournir un runtime web PHP** | **FP** (Fonction Principale) | Permettre l’exécution d’applications PHP conformes aux standards PSR‑4, avec support des extensions `pdo_pgsql` et `intl`. |
| **FS‑02** | **Fournir un serveur de base de données PostgreSQL** | **FP** | Garantir la persistance des données et la compatibilité avec les requêtes SQL standard. |
| **FS‑03** | **Gérer la configuration applicative** | **FC** (Fonction Contraint) | Centraliser les paramètres (fichiers `.env`, `param.ini`, `config_CAS.php`) afin d’assurer la cohérence entre les services. |
| **FS‑04** | **Assurer la connectivité réseau entre services** | **FC** | Mettre en place un réseau interne Docker isolé, avec résolution DNS de conteneurs. |
| **FS‑05** | **Intégrer le proxy HTTP d’entreprise** | **FC** | Utiliser les variables `http_proxy` / `https_proxy` pour le trafic sortant afin de respecter la politique de sécurité du réseau interne. |
| **FS‑06** | **Faciliter le déploiement et la réinitialisation de l’environnement** | **FC** | Permettre le (re)déploiement complet en < 30 s via une commande unique (`docker‑compose up`). |
| **FS‑07** | **Documenter l’utilisation** | **FC** | Fournir un guide d’utilisation (README) et les références de version des images Docker. |

### 2.2 Critères de performance associés  

| Fonction | Critère de performance (mesurable) | Objectif |
|----------|-----------------------------------|----------|
| FS‑01 | Temps de démarrage du conteneur Apache/PHP | ≤ 20 s |
| FS‑01 | Temps de réponse HTTP (GET `/`) en charge légère | ≤ 200 ms |
| FS‑02 | Temps de démarrage du conteneur PostgreSQL | ≤ 15 s |
| FS‑02 | Disponibilité du service DB après démarrage | 99,9 % (sur période de 24 h) |
| FS‑03 | Capacité à charger les variables d’environnement au démarrage | 100 % des variables déclarées sont disponibles dans le conteneur |
| FS‑04 | Latence réseau intra‑conteneurs | ≤ 1 ms (ping) |
| FS‑05 | Utilisation du proxy pour tout le trafic sortant | 100 % des appels HTTP/HTTPS externes passent par le proxy indiqué |
| FS‑06 | Durée totale du script de (re)déploiement (`docker‑compose up --build`) | ≤ 30 s |
| FS‑07 | Taux de conformité du README aux exigences de documentation | 100 % des sections obligatoires présentes (Objectif, Prérequis, Lancement, Nettoyage) |

---  

## 3. Expression fonctionnelle du besoin  

### 3.1 Hiérarchisation des besoins  

| ID | Niveau | Description (QUOI) | Critère d’appréciation | Importance | Flexibilité |
|----|--------|----------------------|------------------------|------------|--------------|
| **B‑01** | Système | **Environnement de développement web PHP + PostgreSQL** | Le système doit permettre le lancement d’une stack web fonctionnelle (Apache + PHP + PostgreSQL) sans intervention manuelle sur le système hôte. | Obligatoire | Fixe |
| **B‑01‑01** | Sous‑système | Runtime Apache/PHP | Disponibilité du serveur HTTP sur le port 80 avec PHP 7.3+ et extensions `pdo_pgsql`, `intl`. | Obligatoire | Fixe |
| **B‑01‑02** | Sous‑système | Service PostgreSQL | Instance PostgreSQL 11+ accessible sur le port 5432, avec authentification par mot‑de‑passe définie dans `.env`. | Obligatoire | Fixe |
| **B‑01‑03** | Sous‑système | Gestion de la configuration | Les fichiers `.env`, `param.ini` et `config_CAS.php` doivent être injectés au démarrage du conteneur web. | Obligatoire | Négociable (format du fichier) |
| **B‑01‑04** | Sous‑système | Orchestration Docker‑Compose | Un fichier `docker-compose.dev.yml` doit décrire les services, les réseaux et les volumes nécessaires. | Obligatoire | Fixe |
| **B‑01‑05** | Sous‑système | Proxy d’entreprise | Les variables `http_proxy` et `https_proxy` doivent être prises en compte par le conteneur web. | Souhaitable | Négociable (peut être désactivé en dev local) |
| **B‑01‑06** | Sous‑système | Documentation d’utilisation | Un fichier `README.md` doit contenir les instructions d’installation, de lancement et de nettoyage. | Obligatoire | Fixe |
| **B‑02** | Système | **Traçabilité des versions** | Chaque image Docker utilisée doit être identifiée par son tag (ex. `php:7.3-apache-buster`, `postgres:11-alpine`). | Obligatoire | Fixe |
| **B‑03** | Système | **Sécurité du développement** | Aucun conteneur ne doit être exposé directement à l’extérieur du réseau interne (ports publiés uniquement sur `localhost`). | Obligatoire | Fixe |
| **B‑04** | Système | **Portabilité** | L’environnement doit fonctionner sur tout hôte supportant Docker Engine ≥ 20.10, sous Linux ou Windows 10 / 11 (WSL2). | Souhaitable | Négociable (Linux recommandé) |

> **Notation** :  
> • **Obligatoire** = exigence contractuelle (≥ 90 % de conformité exigée).  
> • **Souhaitable** = valeur ajoutée (≥ 70 % de conformité acceptable).  
> • **Optionnel** = bonus non critique.  

---  

## 4. Caractérisation des besoins  

| Fonction | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|----------|------------------------|----------------------|--------------|--------------|
| **FS‑01** (Runtime PHP) | Démarrage < 20 s, réponse HTTP ≤ 200 ms, extensions `pdo_pgsql` & `intl` présentes | Obligatoire | Fixe | Compatible Docker Engine ≥ 20.10 |
| **FS‑02** (DB PostgreSQL) | Démarrage < 15 s, disponibilité 99,9 % sur 24 h | Obligatoire | Fixe | Utiliser image officielle `postgres:11-alpine` ou équivalente |
| **FS‑03** (Configuration) | Injection 100 % des variables `.env` et fichiers `param.ini`, `config_CAS.php` | Obligatoire | Négociable (format .env, .ini) | Doit respecter le standard `dotenv` |
| **FS‑04** (Connectivité) | Latence intra‑réseau ≤ 1 ms, résolutions DNS fonctionnelles | Obligatoire | Fixe | Réseau Docker isolé nommé `agile_env_net` |
| **FS‑05** (Proxy) | Toutes les requêtes HTTP/HTTPS sortantes passent par le proxy indiqué | Souhaitable | Négociable (possibilité de désactiver) | Proxy d’entreprise fourni (`http://pfrie-std.proxy.e2.rie.gouv.fr:8080`) |
| **FS‑06** (Déploiement) | (Re)déploiement complet ≤ 30 s via `docker-compose up` | Obligatoire | Fixe | Aucun volume persistant requis pour le code source |
| **FS‑07** (Documentation) | README contenant sections « Prérequis », « Lancement », « Nettoyage », version des images | Obligatoire | Fixe | Rédaction en français, format Markdown |
| **FS‑08** (Traçabilité) | Tag d’image visible dans `docker images` et consigné dans README | Obligatoire | Fixe | Aucun tag « latest » autorisé en production |
| **FS‑09** (Sécurité) | Ports exposés uniquement sur `127.0.0.1` (localhost) | Obligatoire | Fixe | Conformité RGS – niveau 1 (exposition minimale) |

---  

## 5. Validation de l’expression du besoin  

| Étape | Méthode | Participants | Livrable | Traçabilité |
|-------|----------|--------------|----------|--------------|
| **5.1** | Atelier de cadrage (2 h) | Chef de projet, Architecte SI, Responsable Sécurité, Équipe DevOps | Synthèse des besoins (document B‑xx) | Référence `V‑01` |
| **5.2** | Interviews individuelles (30 min / intervenant) | Responsables de la DSI RIE, équipes dev, équipe QA | Matrice de priorisation | Référence `V‑02` |
| **5.3** | Validation formelle du CCF | Comité de pilotage (PMO, DSI, juridique) | **Cahier des Charges Fonctionnel signé** | Référence `V‑03` |
| **5.4** | Vérification de la traçabilité | Auditeur interne | Rapport de traçabilité (ID → Fonction → Critère) | Référence `V‑04` |

> **Critère d’acceptation** : le CCF est signé par toutes les parties prenantes et chaque besoin possède un identifiant unique (ex. B‑01‑03).  

---  

## 6. Scénarios d’usage  

| Scénario | Description | Conditions | Résultat attendu |
|----------|-------------|------------|------------------|
| **S‑NOM‑01** (Lancement nominal) | Un développeur exécute `docker-compose -f docker-compose.dev.yml up -d`. | Docker Engine installé, variables d’environnement définies. | Tous les services sont opérationnels en ≤ 30 s, le serveur web répond sur `http://localhost`. |
| **S‑NOM‑02** (Arrêt & nettoyage) | Exécution de `docker-compose down -v`. | Aucun conteneur actif. | Tous les conteneurs et volumes sont supprimés, l’état du répertoire de travail revient à zéro. |
| **S‑ERR‑01** (Port déjà utilisé) | Le port 80 est déjà occupé par un autre service. | Conflit de port. | Le lancement échoue avec un message d’erreur clair, le CCF impose la possibilité de re‑mapper le port (ex. `8080:80`). |
| **S‑ERR‑02** (Proxy indisponible) | Le proxy d’entreprise ne répond pas. | Variable `http_proxy` définie, mais le serveur proxy injoignable. | Le conteneur web démarre, mais les appels sortants échouent ; le CCF précise que le proxy est **souhaitable** et que le système doit rester fonctionnel en mode « direct ». |
| **S‑LIM‑01** (Ressources limitées) | L’hôte ne dispose que de 1 Go de RAM. | Contrainte mémoire. | Le démarrage dépasse 30 s ou échoue ; le CCF indique que la configuration minimale recommandée est 2 Go RAM, mais le besoin reste fonctionnel (dégradation acceptable). |
| **S‑LIM‑02** (Version Docker obsolète) | Docker Engine = 19.03. | Version inférieure à la exigée. | Le CCF impose la mise à jour avant validation du besoin (contrainte de compatibilité). |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|-----------------|------|---------------------|----------------------|
| **Direction DSI RIE** | Décideur stratégique | Conformité aux politiques de sécurité, ROI mesurable, réduction des coûts d’infrastructure. | Haute – définit les critères de pondération (sécurité > coût). |
| **Équipe DevOps** | Implémentation & exploitation | Simplicité de (re)déploiement, traçabilité des versions, compatibilité avec CI/CD. | Très haute – moteur principal de la valeur opérationnelle. |
| **Développeurs applicatifs** | Utilisateurs finaux | Environnement de travail stable, temps de mise en route minimal, accès aux variables d’environnement. | Haute – satisfaction utilisateur = productivité accrue. |
| **Responsable Sécurité / RGPD** | Garant de conformité | Isolation réseau, usage du proxy, aucune fuite de données hors du périmètre. | Très haute – non‑conformité → blocage du projet. |
| **Equipe QA / Tests** | Validation fonctionnelle | Possibilité de réinitialiser l’environnement à chaque exécution de tests automatisés. | Moyenne – améliore la fiabilité des livrables. |
| **Auditeur interne** | Contrôle & traçabilité | Documentation complète, versionnage, preuves d’audit. | Haute – assure la pérennité du dispositif. |

---  

## 8. Contraintes et environnement  

| Type | Description |
|------|-------------|
| **Organisationnelles** | Le projet doit être livré **dans le cadre d’un appel d’offres public** (respect des règles de la commande publique). |
| **Réglementaires** | • **RGPD** : aucune donnée personnelle ne doit être stockée dans l’image Docker. <br>• **RGS** : le proxy doit être configuré conformément aux exigences de la Sécurité de l’État. |
| **Techniques** | • Docker Engine ≥ 20.10, compatible Linux (kernel ≥ 4.15) ou Windows 10 / 11 (WSL2). <br>• Utilisation d’images officielles (`php`, `postgres`). <br>• Aucun usage de `latest` – tag explicite requis. |
| **Temporelles** | Délai de mise en œuvre : **4 semaines** à compter de la validation du CCF. |
| **Budgétaires** | Budget maximal : **12 k€** (licences, formation, support). |
| **Environnementales** | L’environnement doit pouvoir s’exécuter sur des postes de travail équipés de **8 Go RAM** et **4 cœurs**. |

---  

## 9. Critères de sélection et pondération  

> **Grille d’évaluation** – adaptée aux **marchés publics** (procédure adaptée, article R.2152‑1 du Code de la commande publique).  

| Critère | Sous‑critère | Pondération (%) | Modalité de notation |
|---------|--------------|----------------|----------------------|
| **C‑01** – Conformité fonctionnelle | Respect des besoins B‑xx (détection automatisée) | 30 | 0 / 10 points (audit des scripts) |
| **C‑02** – Sécurité & conformité | RGPD, RGS, isolation réseau | 25 | 0 / 10 points (rapport d’audit) |
| **C‑03** – Qualité de la documentation | README complet, versionnage, traçabilité | 15 | 0 / 10 points (check‑list) |
| **C‑04** – Coût total de possession (CTP) | Licences, support, formation | 15 | 0 / 10 points (estimation budgétaire) |
| **C‑05** – Performance opérationnelle | Temps de (re)déploiement, latence, disponibilité | 10 | 0 / 10 points (tests de charge) |
| **C‑06** – Portabilité & évolutivité | Compatibilité Docker ≥ 20.10, capacité à ajouter des services | 5 | 0 / 10 points (analyse de conception) |
| **TOTAL** |  | **100** |  |

> **Seuil de qualification** : toute offre obtenant **≥ 6 points** sur chaque critère majeur (C‑01, C‑02, C‑03) sera retenue pour l’étape d’analyse détaillée.  

---  

## 10. Glossaire et acronymes  

| Acronyme | Signification | Définition |
|----------|----------------|------------|
| **CCF** | Cahier des Charges Fonctionnel | Document décrivant les besoins fonctionnels selon NF EN 16271. |
| **FS** | Fonction de Service | Fonction attendue du produit, exprimée sans référence à la solution technique. |
| **FP** | Fonction Principale | Fonction indispensable au cœur du besoin. |
| **FC** | Fonction Contraint | Fonction imposée par le contexte (réglementaire, technique, organisationnel). |
| **RGPD** | Règlement Général sur la Protection des Données | Texte législatif UE sur la protection des données à caractère personnel. |
| **RGS** | Référentiel Général de Sécurité | Ensemble de exigences de sécurité de l’État français. |
| **Docker‑Compose** | Outil d’orchestration de conteneurs Docker | Permet de définir et de lancer plusieurs conteneurs comme une application. |
| **Proxy** | Serveur mandataire HTTP/HTTPS | Intermédiaire qui relaie les requêtes réseau, utilisé ici pour le filtrage d’entreprise. |
| **CI/CD** | Intégration Continue / Déploiement Continu | Pratiques de développement automatisées pour livrer rapidement du code. |
| **CTP** | Coût Total de Possession | Somme des coûts directs et indirects sur la durée de vie du produit. |
| **WSL2** | Windows Subsystem for Linux 2 | Environnement Linux natif sous Windows, compatible Docker. |

---  

### Annexes (non exhaustives)  

* **Annexe A** – Modèle de tableau de traçabilité (ID → FS → Critère).  
* **Annexe B** – Exemple de script de test de performance (temps de démarrage).  
* **Annexe C** – Matrice de risques (sécurité, non‑conformité, dépendance Docker).  

---  

*Fin du Cahier des Charges Fonctionnel – Projet **agile‑env***  