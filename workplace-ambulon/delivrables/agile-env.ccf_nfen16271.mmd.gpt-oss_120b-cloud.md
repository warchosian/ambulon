# Cahier des Charges Fonctionnel (CCF)  
**Projet :** *agile‑env* – Environnement de développement conteneurisé pour l’application *agile*  

**Norme :** NF EN 16271 :2013 – Management par la valeur – Expression fonctionnelle du besoin et cahier des charges fonctionnel  

**Date :** 28 avril 2026  

---  

## 1. Présentation du projet  

| Élément | Description |
|---------|-------------|
| **Contexte** | Le projet *agile‑env* fournit un environnement de développement reproductible (Docker) pour l’application *agile* (PHP 7.3 + Apache) avec une base de données PostgreSQL 11. L’environnement doit être utilisable par les équipes de développement du service « WarchoDev », en conformité avec les exigences de sécurité et de traçabilité de l’État. |
| **Enjeux stratégiques** | - Accélérer le cycle de développement (CI/CD) grâce à une stack prête‑à‑l’emploi.<br>- Garantir la cohérence entre les environnements de dev, de test et de production.<br>- Respecter les exigences de souveraineté numérique (usage de composants open‑source, traçabilité des versions). |
| **Objectifs du projet** | 1. Fournir un **environnement conteneurisé** complet (application web + base de données).<br>2. Assurer la **portabilité** (exécution sur postes de travail Windows/Linux/macOS via Docker Desktop).<br>3. Permettre la **configuration** (variables d’environnement, paramètres d’application) sans modifier le code source.<br>4. Intégrer les **proxy d’entreprise** (HTTP/HTTPS) de façon paramétrable. |
| **Périmètre fonctionnel** | **Inclus** : <br>• Dockerfile de l’application PHP.<br>• Dockerfile de la base PostgreSQL.<br>• Fichiers de configuration (Apache, PHP, variables d’environnement, paramètres d’application).<br>• Docker‑compose de développement.<br>• Documentation d’utilisation (README).<br><br>**Exclus** : <br>• Gestion du code métier de l’application *agile* (hors du scope de l’environnement).<br>• Déploiement en production (hors du périmètre « développement »). |

---  

## 2. Analyse de la valeur  

### 2.1 Fonctions de service (FS)  

| N° | Fonction de service | Type | Description (QUOI) | Critère(s) de performance |
|---|---------------------|------|--------------------|---------------------------|
| **FS‑01** | **Provisionner l’application web** | FP (Fonction Principale) | Mettre à disposition un conteneur exécutable contenant l’application PHP 7.3 avec Apache. | - Temps de démarrage ≤ 30 s.<br>- Disponibilité du serveur HTTP ≥ 99,5 % (sur période de test). |
| **FS‑02** | **Fournir la base de données** | FP | Mettre à disposition un conteneur PostgreSQL 11 avec les schémas et données d’initialisation. | - Temps d’initiation ≤ 45 s.<br>- Intégrité des données d’initialisation (checksum). |
| **FS‑03** | **Gérer la configuration** | FC (Fonction Contraint) | Permettre la définition des paramètres d’application (variables d’environnement, fichiers `.ini`, etc.) sans recompilation. | - Possibilité de changer une variable d’environnement et de relancer le conteneur sans reconstruction d’image.<br>- Traçabilité des valeurs (log). |
| **FS‑04** | **Assurer la connectivité réseau** | FC | Garantir que les conteneurs peuvent communiquer (app ↔ DB) et que les postes clients peuvent accéder à l’URL HTTP / HTTPS. | - Latence interne ≤ 10 ms.<br>- Pas de perte de paquets (0 %). |
| **FS‑05** | **Intégrer les proxy d’entreprise** | FC | Appliquer automatiquement les paramètres `http_proxy` / `https_proxy` définis par l’infrastructure de l’État. | - Proxy pris en compte dès le démarrage du conteneur.<br>- Aucun dépassement de délai de connexion (> 5 s). |
| **FS‑06** | **Faciliter le déploiement et la réplication** | FC | Permettre le lancement de l’environnement via une seule commande (`docker-compose up`). | - Commande unique, sans paramètres supplémentaires.<br>- Documentation d’utilisation ≤ 2 pages. |
| **FS‑07** | **Assurer la conformité sécurité** | FC | Respecter les exigences RGPD et RGS (journalisation, accès limité aux secrets). | - Aucun secret en clair dans les images.<br>- Logs d’accès auditables. |

> **Note** : La distinction **FP / FC** suit la méthode de l’analyse fonctionnelle de la norme NF EN 16271. Les fonctions de service sont exprimées uniquement en termes de *quoi* (objectif) et non de *comment* (solution technique).  

### 2.2 Critères de performance globaux  

| Critère | Valeur cible | Unité | Méthode de mesure |
|---------|--------------|-------|--------------------|
| Temps de démarrage total (app + DB) | ≤ 90 s | secondes | Chronométrage automatisé sur machine de référence (CPU i7, 16 Go RAM). |
| Portabilité | ≥ 95 % des postes de travail (Windows 10+, macOS 12+, Linux Ubuntu 20.04) | % | Tests d’installation sur un panel de postes. |
| Niveau de documentation | ≤ 2 pages | pages | Relecture par le comité de pilotage. |
| Traçabilité des variables d’environnement | 100 % (toutes les variables déclarées dans `.env` sont journalisées) | % | Analyse des logs de démarrage. |
| Sécurité des secrets | Aucun secret en clair dans les images | - | Scan d’image (Trivy, Anchore). |

---  

## 3. Expression fonctionnelle du besoin  

### 3.1 Niveau système (besoin global)  

| ID | Besoin (QUOI) | Critère d’appréciation | Niveau d’importance | Flexibilité |
|----|----------------|-----------------------|--------------------|------------|
| **B‑01** | Disposer d’un **environnement de développement complet** (application web + base de données) exécutable sur Docker. | - Démarrage complet ≤ 90 s.<br>- Aucun composant manquant. | Obligatoire | Fixe |
| **B‑02** | **Paramétrer** l’environnement via des variables d’environnement et fichiers de configuration. | - Toutes les variables déclarées dans le fichier `.env` sont prises en compte.<br>- Modifications effectives après redémarrage du conteneur. | Obligatoire | Négociable (valeurs par défaut possibles) |
| **B‑03** | **Intégrer les paramètres de proxy** de l’entreprise. | - Les variables `http_proxy` et `https_proxy` sont reconnues par les conteneurs.<br>- Pas de dépassement de délai de connexion > 5 s. | Obligatoire | Fixe |
| **B‑04** | **Assurer la traçabilité** des paramètres sensibles (secrets, mots de passe). | - Aucun secret en clair dans les images.<br>- Logs d’accès auditables. | Obligatoire | Fixe |
| **B‑05** | **Faciliter le lancement** de l’environnement via une commande unique. | - `docker-compose up -d` suffit.<br>- Documentation ≤ 2 pages. | Obligatoire | Négociable (exemple de script fourni). |
| **B‑06** | **Garantir la compatibilité** avec les postes de travail de la collectivité. | - Tests réussis sur Windows 10+, macOS 12+, Ubuntu 20.04. | Souhaitable | Négociable |
| **B‑07** | **Respecter les exigences de sécurité** (RGPD, RGS). | - Scan d’image conforme (aucune vulnérabilité critique).<br>- Gestion des secrets via Docker secrets ou variables d’environnement temporaires. | Obligatoire | Fixe |

### 3.2 Niveau sous‑systèmes (besoins partiels)  

| ID | Sous‑système | Besoin (QUOI) | Critère d’appréciation | Niveau d’importance |
|----|--------------|----------------|-----------------------|----------------------|
| **B‑01‑01** | Conteneur **application** | Fournir un conteneur PHP 7.3 + Apache pré‑configuré. | - Version PHP = 7.3.x.<br>- Apache écoute sur le port 80.<br>- Modules requis (`pdo_pgsql`, `intl`) installés. | Obligatoire |
| **B‑01‑02** | Conteneur **base de données** | Fournir un conteneur PostgreSQL 11 avec scripts d’initialisation. | - Version PostgreSQL = 11.x.<br>- Scripts `initdb/*.sql` exécutés au premier lancement.<br>- Port exposé = 5432. | Obligatoire |
| **B‑02‑01** | **Fichier `.env`** | Centraliser les variables d’environnement (ex : `APP_ENV`, `DB_HOST`, `DB_USER`, `DB_PASSWORD`). | - Toutes les variables listées sont présentes.<br>- Valeurs respectent le format `KEY=VALUE`. | Obligatoire |
| **B‑02‑02** | **Fichier `param.ini`** | Stocker les paramètres d’application spécifiques (ex : sections `[database]`, `[security]`). | - Syntaxe INI valide.<br>- Toutes les sections attendues présentes. | Souhaitable |
| **B‑03‑01** | **Proxy** | Propager les variables `http_proxy` / `https_proxy` dans les conteneurs. | - Variables présentes dans l’image au moment de la construction.<br>- Vérification via `env | grep -i proxy`. | Obligatoire |
| **B‑04‑01** | **Gestion des secrets** | Séparer les secrets (mots de passe) du code source. | - Secrets fournis via Docker secrets ou variables d’environnement au runtime.<br>- Aucun secret dans les layers d’image. | Obligatoire |
| **B‑05‑01** | **Docker‑compose** | Orchestrer les deux conteneurs (app + DB) et les volumes de persistance. | - Fichier `docker‑compose.dev.yml` valide (schema version 3.8).<br>- Volumes montés (`db_data`, `app_code`). | Obligatoire |

### 3.3 Niveau composants (besoins élémentaires)  

| ID | Composant | Besoin (QUOI) | Critère d’appréciation | Niveau d’importance |
|----|-----------|----------------|-----------------------|----------------------|
| **B‑01‑01‑01** | **Dockerfile‑app** | Décrire la construction de l’image PHP 7.3 + Apache. | - Instructions `FROM php:7.3-apache-buster` présentes.<br>- Installation des paquets `git zip unzip vim libpq-dev libicu-dev`.<br>- Extension PHP `pdo_pgsql`, `intl` installées. | Obligatoire |
| **B‑01‑01‑02** | **Fichier de configuration Apache** (`000‑default.conf`) | Exposer le site sur le port 80, configurer le DocumentRoot. | - Port 80 déclaré.<br>- `DocumentRoot` pointant vers `/var/www/html`. | Obligatoire |
| **B‑01‑02‑01** | **Dockerfile‑db** | Décrire la construction de l’image PostgreSQL 11. | - `FROM postgres:11-alpine` présent.<br>- Copie des scripts `initdb/*.sql` et `restore.sh`. | Obligatoire |
| **B‑02‑01‑01** | **`.env`** | Contenir les variables d’environnement. | - Exemples : `APP_ENV=dev`, `DB_HOST=db`, `DB_PORT=5432`, `DB_USER=agile`, `DB_PASSWORD=******`. | Obligatoire |
| **B‑02‑02‑01** | **`param.ini`** | Contenir les paramètres INI de l’application. | - Sections `[database]`, `[security]` présentes.<br>- Valeurs correctement formatées. | Souhaitable |
| **B‑05‑01‑01** | **`docker-compose.dev.yml`** | Orchestrer le lancement de l’environnement. | - Services `app` et `db` déclarés.<br>- Réseaux et volumes correctement configurés.<br>- `environment:` inclut le fichier `.env`. | Obligatoire |

---  

## 4. Caractérisation des besoins  

| Fonction de service | Critère d’appréciation | Niveau d’importance | Flexibilité | Contraintes |
|--------------------|-----------------------|--------------------|-------------|-------------|
| **FS‑01** – Provisionner l’application web | Image Docker contenant PHP 7.3 + Apache, modules requis, configuration Apache. | Obligatoire | Fixe | Aucun composant propriétaire, licence compatible OSS. |
| **FS‑02** – Fournir la base de données | Image Docker PostgreSQL 11 avec scripts d’initialisation exécutés. | Obligatoire | Fixe | Doit pouvoir être initialisée en mode « clean » via `restore.sh`. |
| **FS‑03** – Gérer la configuration | Fichier `.env` + `param.ini` lisibles par l’application au démarrage. | Obligatoire | Négociable (valeurs par défaut possibles) | Les secrets ne doivent pas être versionnés. |
| **FS‑04** – Assurer la connectivité réseau | Conteneurs sur le même réseau Docker, ports exposés (80, 5432). | Obligatoire | Fixe | Pas d’accès extérieur sans VPN. |
| **FS‑05** – Intégrer les proxy d’entreprise | Variables `http_proxy` / `https_proxy` propagées dans les conteneurs. | Obligatoire | Fixe | Doit fonctionner derrière le proxy `pfrie-std.proxy.e2.rie.gouv.fr:8080`. |
| **FS‑06** – Faciliter le déploiement | Commande unique `docker-compose up -d`. | Obligatoire | Négociable (script wrapper autorisé) | Documentation ≤ 2 pages. |
| **FS‑07** – Assurer la conformité sécurité | Aucun secret en clair, logs d’accès, scan d’image conforme. | Obligatoire | Fixe | Conformité RGPD & RGS. |

---  

## 5. Validation de l’expression du besoin  

| Étape | Méthode | Participants | Livrables | Traçabilité |
|-------|---------|--------------|----------|--------------|
| **5.1** | Atelier de cadrage (présentiel) | Chef de projet, Architecte DevOps, Responsable Sécurité, Représentant des développeurs | Tableau des fonctions de service (FS‑01 à FS‑07) | Référence : **V‑01** |
| **5.2** | Revue des exigences fonctionnelles (document partagé) | Tous les acteurs du **Comité de pilotage** | Version signée du CCF (PDF) | Référence : **V‑02** |
| **5.3** | Validation technique (prototype) | Équipe DevOps (Docker) | Environnement fonctionnel déployé sur un poste de test | Référence : **V‑03** |
| **5.4** | Audit de conformité (Sécurité) | RSSI, Auditeur externe | Rapport d’audit (RGPD/RGS) | Référence : **V‑04** |
| **5.5** | Acceptation finale | Direction IT, Direction juridique | Procès‑verbal d’acceptation | Référence : **V‑05** |

---  

## 6. Scénarios d’usage  

| Scénario | Description | Conditions | Résultat attendu |
|----------|-------------|------------|-------------------|
| **S‑NOM‑01** – Lancement standard | L’utilisateur exécute `docker-compose up -d`. | Aucun conteneur en cours d’exécution. | Les services `app` et `db` sont démarrés, accessibles via `http://localhost`. |
| **S‑NOM‑02** – Modification d’une variable d’environnement | L’utilisateur édite `.env` (ex : `APP_ENV=prod`) puis relance `docker-compose up -d`. | Variable modifiée, conteneur arrêté. | Le conteneur redémarre avec la nouvelle valeur, le comportement de l’application change en conséquence. |
| **S‑ERR‑01** – Proxy non disponible | Le proxy d’entreprise est hors service. | Variables `http_proxy`/`https_proxy` définies, mais le serveur proxy ne répond pas. | Le conteneur signale une erreur de connexion (timeout ≤ 5 s) et le lancement s’arrête avec un message explicite. |
| **S‑ERR‑02** – Script d’initialisation DB erroné | Le fichier `initdb/bad.sql` contient une syntaxe invalide. | Conteneur DB démarre la première fois. | Le conteneur échoue, le log indique l’erreur SQL, le processus d’orchestration s’arrête. |
| **S‑LIM‑01** – Ressources machines limitées | Machine de dev avec 2 Go RAM, 1 CPU. | Lancement de l’environnement complet. | Démarrage > 90 s, mais l’application reste fonctionnelle ; le critère de temps de démarrage n’est pas respecté (déviation acceptée à titre de scénario limite). |
| **S‑LIM‑02** – Mise à jour de la version PHP | L’image `php:7.3-apache-buster` devient indisponible. | Dockerfile‑app doit être mis à jour. | Le processus de mise à jour (re‑build) doit être déclenché ; le critère de **portabilité** reste satisfait si la nouvelle version reste compatible. |

---  

## 7. Parties prenantes (Stakeholders)  

| Partie prenante | Rôle | Besoins spécifiques | Impact sur la valeur |
|-----------------|------|----------------------|----------------------|
| **Direction IT** | Décideur stratégique | Garantir cohérence avec la politique d’infrastructure, maîtrise des coûts. | Valeur « efficience » (réduction du temps de mise en place). |
| **Équipe DevOps** | Conception & mise en œuvre de l’environnement | Outils simples, réutilisables, documentation claire. | Valeur « opérabilité ». |
| **Développeurs** | Utilisateurs finaux de l’environnement | Démarrage rapide, configuration flexible, stabilité. | Valeur « productivité ». |
| **RSSI / Sécurité** | Conformité sécurité, protection des données. | Gestion des secrets, conformité RGPD/RGS, traçabilité. | Valeur « sécurité ». |
| **Responsable juridique** | Vérification conformité légale. | Pas de composants sous licence non‑compatible, respect du droit d’auteur. | Valeur « conformité ». |
| **Support technique** | Assistance aux équipes. | Documentation d’installation, procédure de récupération. | Valeur « maintenabilité ». |

---  

## 8. Contraintes et environnement  

| Type | Description |
|------|-------------|
| **Organisationnelles** | - Respect du processus de passation des marchés publics (documentation CCF obligatoire).<br>- Validation par le Comité de pilotage avant le lancement. |
| **Réglementaires** | - RGPD : aucune donnée à caractère personnel dans les images.<br>- RGS : utilisation de certificats d’authentification interne si besoin (hors scope). |
| **Techniques** | - Docker ≥ 20.10, Docker‑Compose ≥ 1.29.<br>- Compatibilité avec Windows 10/11 (Docker Desktop), macOS 12+, Ubuntu 20.04 LTS.<br>- Utilisation de l’image officielle `composer:latest` (licence MIT). |
| **Temporelles** | - Délai de mise en production de l’environnement : 4 semaines après validation du CCF.<br>- Livraison intermédiaire (prototype) : 2 semaines. |
| **Budgétaires** | - Coût d’infrastructure Docker Desktop (licence entreprise) : ≤ 2 000 € / an.<br>- Aucun coût de licence supplémentaire (logiciels OSS uniquement). |

---  

## 9. Critères de sélection et pondération (marché public)  

| Critère | Sous‑critère | Pondération | Modalité de notation |
|---------|--------------|--------------|----------------------|
| **C1 – Conformité fonctionnelle** | Respect de l’ensemble des besoins B‑01 à B‑07. | **40 %** | 0 – 5 points par besoin (max 35 pts) + 5 pts bonus pour dépassement. |
| **C2 – Qualité documentaire** | Clarté du README, procédures d’installation, traçabilité. | **15 %** | 0 – 5 pts (évalué par le Comité de pilotage). |
| **C3 – Sécurité** | Gestion des secrets, résultats du scan d’image, conformité RGPD/RGS. | **20 %** | 0 – 10 pts (scan ≤ 5 vulnérabilités critiques) + 0 – 10 pts (audit). |
| **C4 – Portabilité & Compatibilité** | Fonctionnement sur Windows, macOS, Linux. | **10 %** | 0 – 5 pts (tests réussis sur chaque OS). |
| **C5 – Coût total** | Prix global (licences, support, formation). | **10 %** | 0 – 5 pts (coût le plus bas = 5 pts). |
| **C6 – Délais de mise en œuvre** | Respect du planning (prototype 2 semaines, production 4 semaines). | **5 %** | 0 – 5 pts (délais respectés = 5 pts). |

> **Note** : La somme des pondérations = 100 %. Les offres seront notées sur 100 points, le plus élevé étant retenu.  

---  

## 10. Glossaire et acronymes  

| Acronyme / Terme | Définition |
|------------------|------------|
| **APIs** | Interfaces de programmation applicative. |
| **API** | Application Programming Interface (interface). |
| **Cahier des Charges Fonctionnel (CCF)** | Document décrivant les besoins fonctionnels d’un projet selon la norme NF EN 16271. |
| **Docker** | Plate‑forme de conteneurisation. |
| **Docker‑Compose** | Outil d’orchestration de conteneurs multi‑services. |
| **FP** | Fonction Principale (fonction indispensable à la mission du produit). |
| **FC** | Fonction Contraint (exigence imposée par le contexte ou la réglementation). |
| **RGPD** | Règlement Général sur la Protection des Données. |
| **RGS** | Référentiel Général de Sécurité (France). |
| **SQL** | Structured Query Language (langage de requêtes). |
| **VM** | Machine virtuelle. |
| **VS** | Versioning System (système de gestion de versions). |
| **YAML** | Langage de sérialisation de données (utilisé par Docker‑Compose). |
| **.env** | Fichier contenant les variables d’environnement. |
| **param.ini** | Fichier de configuration au format INI. |
| **.gitkeep** | Fichier vide permettant de conserver un répertoire vide dans Git. |
| **composer** | Gestionnaire de dépendances PHP. |
| **postgres** | Système de gestion de base de données relationnelle (PostgreSQL). |

---  

## Annexes (non obligatoires mais utiles)  

* **Annexe A – Exemple de fichier `.env` (sans secrets)**  
```dotenv
# -----------------------------------------------------------------
# Variables d’environnement – agile‑env
# -----------------------------------------------------------------
APP_ENV=dev
APP_DEBUG=true
APP_URL=http://localhost

# Base de données
DB_HOST=db
DB_PORT=5432
DB_DATABASE=agile
DB_USER=agile_user
# DB_PASSWORD will be supplied via Docker secret at runtime
```

* **Annexe B – Exemple partiel de `docker-compose.dev.yml`**  
```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile-app
    ports:
      - "80:80"
    env_file:
      - docker/extra/app-conf/.env
    depends_on:
      - db
    networks:
      - agile-net

  db:
    build:
      context: docker/db
      dockerfile: Dockerfile
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: agile
      POSTGRES_USER: agile_user
      # POSTGRES_PASSWORD will be injected via secret
    networks:
      - agile-net

networks:
  agile-net:
    driver: bridge

volumes:
  db_data:
```

* **Annexe C – Matrice de traçabilité (ID besoin ↔ ID fonction)**  
| Besoin | Fonction(s) associée(s) |
|--------|------------------------|
| B‑01 | FS‑01, FS‑02 |
| B‑02 | FS‑03 |
| B‑03 | FS‑05 |
| B‑04 | FS‑07 |
| B‑05 | FS‑06 |
| B‑06 | FS‑01, FS‑02 (portabilité) |
| B‑07 | FS‑07 |

---  

**Fin du Cahier des Charges Fonctionnel**  

*Document rédigé conformément à la norme NF EN 16271 :2013, destiné à être utilisé comme référence dans le cadre d’un appel d’offres public pour la réalisation de l’environnement de développement *agile‑env*.*