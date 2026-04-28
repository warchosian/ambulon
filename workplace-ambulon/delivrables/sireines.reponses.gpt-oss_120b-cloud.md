# SIREINES – Documentation technique

[TOC]

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Présentation du projet
<a id="présentation-du-projet"></a>

SIREINES (Système d’Information des REquetes d’INformation des Experts et Spécialistes) est une application Java/J2EE destinée à recenser, suivre et coordonner les demandes de qualification des agents auprès des comités de domaine.  
Elle assure :

| Élément | Description |
|---|---|
| **Objet** | Constitution d’un répertoire d’experts et spécialistes, suivi de leurs dossiers, génération de courriers et de statistiques BIRT. |
| **Statut** | En production (déploiement national). |
| **Portée géographique** | Nationale. |
| **Environnement d’accès** | Web (HTTPS). |
| **Technologie principale** | Java /J2EE, Struts 2, Spring, BIRT, Talend. |
| **Hébergement** | IaaS (ECO4) – Centre‑serveur ministériel Paris La Défense. |
| **Version en production (12 / 03 / 2024)** | 2.5.20 (date : 12 / 03 / 2026). |
| **Déclaration CNIL** | 29 / 09 / 2014 – n° 1034232. |

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Architecture fonctionnelle
<a id="architecture-fonctionnelle"></a>

| Fonctionnalité | Description |
|---|---|
| **Collecte** | Saisie des dossiers, pièces jointes et métadonnées. |
| **Concentration** | Centralisation des demandes, suivi des avis, génération de courriers. |
| **Statistiques** | Rapports BIRT (ex : pyramide des âges, fréquence des mots‑clés). |
| **Export / Import** | Jobs Talend (rptdesign) pour l’import/export de fichiers. |
| **Gestion des droits** | Autorisations via `authorisation-config.xml` (rôles ADMIN). |
| **Interface** | Struts 2 + FreeMarker (templates `*.ftl`). |

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Architecture technique
<a id="architecture-technique"></a>

```
+-------------------+        +-------------------+        +-------------------+
|  Docker host (WSL) |  -->  |  sireines_app     |  -->   |  Tomcat 7 (war)   |
+-------------------+        +-------------------+        +-------------------+
           |                         |
           v                         v
+-------------------+        +-------------------+
|  sireines_db      |  <--  |  PostgreSQL 14    |
+-------------------+        +-------------------+
           |
           v
+-------------------+
|  pgadmin4         |
+-------------------+
```

- **Conteneurs**  
  - `sireines_app_usine_container` : image `sireines_app_usine_image` (war → `/tmp/ROOT.war`).  
  - `sireines_db_usine_container` : image `postgres:14.1-alpine`.  
  - `sireines_pgadmin_container` : image `dpage/pgadmin4`.  

- **Volumes persistants**  
  - `sireines_db_sireines_vol` : données PostgreSQL.  
  - `sireines_pgadmin_sireines_vol` : configuration pgAdmin.  

- **Frameworks**  
  - **Spring** (`applicationContext.xml`) – gestion des beans, AOP, transactions.  
  - **Struts 2** – actions, interceptors, widgets.  
  - **FreeMarker** – templates `*.ftl` (themes `simple`, `simple_read`, `xhtml`, `xhtml_read`).  
  - **BIRT 4.3** – rapports (`*.rptdesign`).  
  - **Talend** – jobs d’import (`*.jar`).  

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Déploiement applicatif
<a id="déploiement-applicatif"></a>

### Environnements
| Environnement | URL | Alias SSH |
|---|---|---|
| **Production** | https://sireines.e2.rie.gouv.fr/Accueil.do | `sireinesprod` |
| **Pré‑production** | https://sireines.preprod.e2.rie.gouv.fr/Accueil.do | `sireinesppr` |
| **Recette** | http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/Accueil.do | `sireinesrec` |

### Procédure générale (GitLab → Merge Request)

1. Ouvrir le projet **SIREINES** dans GitLab.  
2. Créer une **Merge Request** (source → destination) :  
   - `develop‑cgi → recette` (déploiement Recette)  
   - `recette → preprod` (déploiement Pré‑prod)  
   - `preprod → prod` (déploiement Production).  
3. Décochez **“Delete source branch after merge”** pour conserver la branche.  
4. Valider le pipeline, puis cliquer sur **Merge**.  

> Après le merge, l’application est automatiquement déployée via le pipeline CI/CD.

### Tests post‑déploiement
- Vérifier la version affichée dans le footer (`v${version} du ${appDate}`).  
- Contrôler les fonctionnalités techniques : envoi de courriels, génération de rapports BIRT, accès à la base via pgAdmin.  

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Déploiement Docker (Recette / Poste)
<a id="déploiement-docker"></a>

### 1. Récupération du WAR
- Télécharger `sireines-web-*.war` depuis le **Package Registry** du projet GitLab.  
- Placer le fichier dans le répertoire de travail : `c:/sireines/sireines_pgadmin`.

### 2. Docker‑compose
```bash
cd c:/sireines/sireines_pgadmin
docker-compose up -d          # démarre les 3 services
docker ps                     # vérifie que sireines-app est en cours
```

### 3. Mise à jour d’un WAR
```bash
docker rm -f sireines_app_usine_container
docker rmi -f sireines_app_usine_image
# remplacer le war dans le répertoire, puis relancer
docker-compose up -d
```

### 4. Accès
- Application : `http://localhost:8080/Accueil.do` (ou via le DNS interne).  
- pgAdmin : `http://localhost:8888` (user / password définis dans `.env`).  

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Base de données
<a id="base-de-données"></a>

- **SGBD** : PostgreSQL 14 (image `postgres:14.1-alpine`).  
- **Schéma** : `public` (défini dans `domain.ksp`).  
- **Variables d’environnement** (fichier `.env`) :

```text
POSTGRES_DB=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SCHEMA=postgres
```

### Connexion (Docker)
```bash
docker exec -it sireines-db bash
psql -U postgres
```

### Scripts SQL (répertoire `sireines-database/script`)
| Répertoire | Exemple de script | Objectif |
|---|---|---|
| `alter sireines v1` | `alter_0.7.sql` | Création séquence `SEQ_THESAURUS`, suppression de contraintes obsolètes. |
| `install` | `crebas.sql`, `creuser.sql` | Création du schéma de base. |
| `drop` | `dropuser.sql` | Suppression d’un utilisateur. |
| `update` | `README.md` | Historique des évolutions depuis 16/11/2018. |

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Scripts Maven / Assembly
<a id="scripts-maven-assembly"></a>

- **`settings.xml`** : configuration du serveur Maven du GitLab (`gitlab-maven`).  
- **Assemblies**  
  - `sireines-database/assembly.xml` : empaquette les scripts SQL (`scripts` → ZIP).  
  - `sireines-deployment/assembly-sources.xml` : archive toutes les sources du projet (exclusion des dossiers `target`).  
  - `sireines-doc/assembly.xml` : archive la documentation (`Doc installation`).  
  - `sireines-talend/assembly.xml` : archive les rapports Talend (`reports`).  

```bash
mvn clean install                # compile et installe les artefacts locaux
mvn assembly:single             # crée les archives ZIP définies
```

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Configuration Spring & Struts
<a id="configuration-spring-struts"></a>

- **Spring** (`src/main/resources/META-INF/application-config.xml`) – uniquement les paramètres globaux (`appDate`, `nbRowPage`).  
- **Struts 2** (`src/main/resources/struts.xml`) – définit les actions (ex : `Accueil.do`, `Contact.do`, `ExtractionXX.do`).  
- **Autorisation** (`src/main/resources/META-INF/sireines‑auth‑config.xml`) – rôles `R_ADMIN` avec permissions `PRM_READ_ALL`, `PRM_WRITE_ALL`.  

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Templates FreeMarker
<a id="templates-freemarker"></a>

Thèmes disponibles :

| Thème | Description |
|---|---|
| `simple` / `simple_read` | Formulaires basiques (HTML 5). |
| `xhtml` / `xhtml_read` | Formulaires avec tableau (`layout="table"`), gestion de `controlLayout`. |
| `jquery` | Widgets JavaScript (autocomplete, datepicker). |

Extraits typiques :

```ftl
<#-- template/simple_read/text.ftl -->
<span id="${parameters.id!}" class="${parameters.cssClass!}">
  ${parameters.nameValue?html?replace("\n","<br/>")}
</span>
```

Chaque template se termine par `↩ [Retour au sommaire](#sireines---documentation-technique)` grâce à l’inclusion du fichier `theme.properties` (parent = `simple` ou `xhtml`).

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Versions & livraisons
<a id="versions-et-livraisons"></a>

| Environnement | Version actuelle | Date de mise à jour |
|---|---|---|
| **Production** | 2.5.20 | 12 / 03 / 2026 |
| **Pré‑prod** | – | – |
| **Recette** | – | – |

Les livraisons sont validées via les **Merge Requests** décrites plus haut. Les tests techniques (courriels, BIRT, etc.) sont documentés dans `Recette/LivraisonSurIAAS.md`.

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Contacts & gouvernance
<a id="contacts-gouvernance"></a>

| Rôle | Nom | Fonction | Email |
|---|---|---|---|
| **MOA MTES** | Pascal Zemour | Chef de projet opérationnel | Pascal.Zemour@developpement-durable.gouv.fr |
| **MOA MTES** | Vincent Letrouit | Sponsor projet | Vincent.Letrouit@developpement-durable.gouv.fr |
| **MOE (prestataire)** | Matthieu Georges | Chef de projet | matthieu.georges@kleegroup.com |
| **MOE (prestataire)** | Olivier Venot | Directeur de projet | olivier.venot@kleegroup.com |
| **Support** | – | Portail support DIN | https://portail-support.din.developpement-durable.gouv.fr/projects/sireines |

### Cerbère (gestion des habilitations)
| Environnement | URL d’administration |
|---|---|
| Recette | https://cerbere.recette.e2.rie.gouv.fr/administration/ |
| Pré‑prod & Prod | https://cerbere.e2.rie.gouv.fr/administration/ |
| Ticket | https://portail-support.din.developpement-durable.gouv.fr/projects/assistance-produits-securite/issues |

↩ [Retour au sommaire](#sireines---documentation-technique)

---

## Références & ressources complémentaires
<a id="références-ressources"></a>

- **Code source** : `G:\WarchoLife\WarchoDevplace\Gitlab_Applications\ambulon\workplace-ambulon\gitlab\sireines`  
- **Documentation Wiki** : `sireines.wiki.md` (procédures de déploiement, connexion BDD, livraisons).  
- **Fichiers de configuration** : `.gitignore`, `.gitlab-ci.yml`, `pom.xml`, `settings.xml`.  
- **Rapports BIRT** : nombreux `*.rptdesign` sous `sireines-talend/reports`.  
- **Base de données** : scripts SQL sous `sireines-database/script`.  
- **Docker archives** : `M:\Produits numériques\Ressources humaines\Sireines\Docker\Archives`.  

↩ [Retour au sommaire](#sireines---documentation-technique)