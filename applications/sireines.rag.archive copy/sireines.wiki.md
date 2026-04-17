
<a id="dploiement-dploiement-de-lapplicatif-recette-pr-production-production"></a>

# 📄 Déploiement › Déploiement-de-l'applicatif-(Recette,-pré-production,-production

> **Source :** `Déploiement.Déploiement-de-l'applicatif-(Recette,-pré-production,-production.md`

Déploiement :

Se connecter avec 'Bastion'

puis utiliser un alias de connexion : sireinesrec, sireinesppr ou sireinesprod

cd /opt/app

copie du docker-compose.yml avec la date (ex :  docker-compose.yml.20250523)
ex: 
cp docker-compose.yml docker-compose.yml.20250523

effectuer un docker ps pour identifier le container sireines-app

![Capture](uploads/12738ffe6934641f1c4ed401955817a3/Capture.JPG)

docker rm -f sireines-app 

vi docker-compose.yml (Pour modifier la version à livrer)

docker compose up -d 

Pour le test de la recette aller sur :

http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/Accueil.do

![Capture2](uploads/dba83529ace31f5dc3448548f1e5f1d6/Capture2.JPG)

Effectuer quelques tests fonctionnels simples :

![Capture3](uploads/e282ab2b5a5e58e429f2fcc7f673edcf/Capture3.JPG)

---

<a id="home"></a>

# 📄 Home

> **Source :** `Home.md`

La mission des compétences scientifiques et techniques (DRI/AST4) tient à jour une base de données dénommée SIREINES qui recense toutes les demandes de qualification par les comités de domaine de ses agents. Elle suit l'évolution de ces données, coordonne leur évaluation par les comités de domaine, et tient les agents informés des suites de leurs de leurs demandes.

Sommaire :
* [Qui fait quoi](#quifaitquoi)
* [Historique](#Historique)
* [Accès au site](#Site)
* [Cerbère](#Cerbere)
* [Version](#Version)
* [Documentations](#Doc)


<a name="quifaitquoi"></a>
## Qui fait quoi

| Intervenants | Commentaires |
|--------------|--------------|
| MOA MTES | Zemour Pascal (Chargé de mission) - CGDD/DRI/AST4 Pascal.Zemour@developpement-durable.gouv.fr =\> Chef de projet opérationnel de l'application |
|  | Letrouit Vincent (Chef de bureau) - CGDD/DRI/AST4 Vincent.Letrouit@developpement-durable.gouv.fr =\> Sponsor des projets |
| MOE prestataire | Jusqu'en novembre 2021 : Klee Group |
|  | \- Matthieu Georges (Chef de projet) matthieu.georges@kleegroup.com |
|  | \- Olivier Venot (Directeur de projet) olivier.venot@kleegroup.com |


<a name="Historique"></a>
## Historique

| Date | Références | Type d'évolution | Fichier |
|------|------------|------------------|---------|
| 26/02/2020 | Mantis 0052083 | Évolution mineure des courriers | \[[sireines_mantis_0052083.pdf](uploads/431f99b1ec1a87bc71962a80758af481/sireines_mantis_0052083.pdf)\] |
| 15/09/2020 | Mantis 0056137 | Demande de mise à jour des courriers | \[[sireines_mantis_0056137.pdf](uploads/d67a07eca5a5a248db13b6ebc71e6a0b/sireines_mantis_0056137.pdf)\] |
| 22/10/2020 | Mantis 0056773 | Correction de courriers | \[[sireines_mantis_0056773.pdf](uploads/e855689ab130403e40ada37f2c93848f/sireines_mantis_0056773.pdf)\] |
| 03/05/2021 | Mantis 0059550 | Extractions=erreur eclipse | \[[sireines_mantis_0059550.pdf](uploads/dbf64e820c7296237e5c5eafbe9dca45/sireines_mantis_0059550.pdf)\] |
| 30/09/2021 | Mantis 0061626 | Anomalie dans livraison 2.5.6 | \[[sireines_mantis_0061626.pdf](uploads/ac13ef2303459e85a76ccba84ce9da96/sireines_mantis_0061626.pdf)\] |

<a name="Site"></a>
## Accès au site

[sites](Sireines/sites)

<a name="Cerbere"></a>
## Cerbère

[cerbère](Sireines/Cerbère)

<a name="Version"></a>
## Version

[version](Sireines/Version)

<a name="Doc"></a>
## Documentations

### Guide du chef de produit :
 * [Recette d'une livraison sur poste (Docker)](Recette/LivraisonSurPosteDocker)
 * Recette d'une livraison sur environnement IAAS
 * [Connexion base de données](Recette/ConnexionBDD_Docker)

### Fonctionnel :

### Technique :
  * [Document d'installation et d'exploitation (IAAS)](Technique/DocumentationInstallationEtExploitation)
    
### Reversing
  * [Application](Reversing/App)
  * [Base de données](Reversing/Database)

### Deploiement
  * [Procedure de déploiement applicatif ](Technique/DeploiementApplicatif)

---

<a id="recette-connexionbdd_docker"></a>

# 📄 Recette › ConnexionBDD_Docker

> **Source :** `Recette.ConnexionBDD_Docker.md`

Se mettre sur le serveur de recette (sireinesrec)

Lancer Run pageant 
New Session (Load Bastion)


- /opt/app
- cat .env
- docker exec -it sireines-db bash
- psql -U sireines

---

<a id="recette-livraisonsurpostedocker"></a>

# 📄 Recette › LivraisonSurPosteDocker

> **Source :** `Recette.LivraisonSurPosteDocker.md`

<a name="HautdePage"></a>
# Document d'installation sur Poste de Travail (Docker)


Sommaire :

*[Pré-requis](#prerequis)


<a name="prerequis"></a>
## 0 - Pré-requis

Avoir installé sur son poste : 
* Docker Desktop Installer.exe (application Docker Desktop) (Logo Baleine) avec wsl-updatex64.msi

* L'application Visual code avec les extensions :
    * Dev Containers
    * Docker
    * French Language Pack for Visual Studio Code (*)
    * Markdown Preview Enhanced (*)
    * WSL
* L'application Prince (*) et ajouter dans les variables d'environnement dans le path :
    C:\Program Files (x86)\Prince\engine\bin

* L'interface de base de données Pgadmin 4 v8 (minimal)

(*) Non obligatoire

[Haut de Page](#HautdePage)

## 1 - Les conteneurs et les images

### 1.1 Vocabulaire

**Un conteneur** est une unité logicielle standard qui regroupe le code et toutes ses dépendances afin que l'application s'exécute rapidement et de manière fiable d'un environnement informatique à un autre. Une image de conteneur Docker est un package logiciel léger, autonome et exécutable qui comprend tout ce dont vous avez besoin pour exécuter une application : code, runtime, outils système, bibliothèques système et paramètres.

**Les images de conteneurs**
deviennent des conteneurs au moment de l'exécution et dans le cas des conteneurs Docker, les images deviennent des conteneurs lorsqu'elles s'exécutent sur Docker Engine (logo Baleine). 

### 1.2 Cas particulier  : Application Sireines
L'application Sireines comporte  trois conteneurs, trois images et un volume.

* Le conteneur de l'applicatif s'appelle **sireines_app_usine_container** et l'image associée s'appelle **sireines_app_usine_image**.

* Le conteneur de la base de données s'appelle **sireines_db_usine_container** et l'image associée s'appelle **postgres:14.1-alpine**.

* Un conteneur a été ajouté pour garder en mémoire les connexions à la base de données. Ce conteneur s'appelle **sireines_pgadmin_container** et l'image associée s'appelle **dpage/pgadmin4**.

La base de données est contenu dans un seul volume appelé : **sireines_db_sireines_vol**.
Les connexions sont sauvegardées dans le volume appelé : **sireines_pgadmin_sireines_vol**.

## 2 - Aller chercher le war dans gitlab

### 2.1 Les liens Gitlab

* **Lien Gitlab**

https://gitlab-forge.din.developpement-durable.gouv.fr/

* **Lien Gitlab du projet Sireines**

https://gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/produits/rh/sireines

* **Emplacement du war dans Gitlab**

deploy / package registry 

(https://gitlab-forge.din.developpement-durable.gouv.fr/snum/pnm3/produits/rh/sireines/-/packages) puis cliquer sur le lien pour télécharger le war  (sireines-web-*.war).

### 2.2 Télécharger le fichier *.war et le déposer dans le répertoire de travail de votre poste

c:/sireines/sireines_pgadmin (Répertoire de travail)

### 2.3 Annotation

A noter que dans le fichier Dockerfile, la ligne 
    **COPY --chown=root:root sireines-web-*.war /tmp/ROOT.war**
permet de prendre tous les war commençant par **"sireines-web-"** et se terminant par **".war"**.

Lors d'une nouvelle livraison d'un war, il suffit de substituer l'ancien war par le nouveau war dans le répertoire de travail.

Dans ce cas précis, il n'y aura rien d'autre à changer et le fichier Dockerfile peut rester en l'état.

Toutes les sources se trouvent dans le répertoire partagé du service :

[M:\Produits numériques\Ressources humaines\Sireines\Docker\Archives](M:\Produits numériques\Ressources humaines\Sireines\Docker\Archives)
M: correspond au Dossier partagé [DPNM3]

On y trouvera les war et les dump de l'application.

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

## 3 - Installation de l'applicatif 

### 3.1 Prérequis
* Avoir récupérer le répertoire **[M:\Produits numériques\Ressources humaines\Sireines\Docker\sireines_pgadmin]**(M:\Produits numériques\Ressources humaines\Sireines\Docker\sireines_pgadmin)
M: correspond au Dossier partagé [DPNM3]
et le déposer sur le poste de travail **c:/sireines/sireines_pgadmin**

* Lancer l'application Docker Desktop (Logo Baleine) et s'assurer que les moteurs sont bien en exécution (Running)
![alt text](img/dockerDesktop.png)

### 3.2 Vérification de l'existence des volumes (Visual studio Code)

Se positionner dans le terminal du Visual Code dans le répertoire de travail:
![alt text](img/repertoire.PNG)

* Si le volume sireines_db_sireines_vol n'est pas n'existe pas faire :
    docker volume create sireines_db_sireines_vol
    
    ![alt text](images/creation_volume.png)


    et modifier **si besoin** les lignes 38 et 74 de docker-compose.yml concernant ce volume.
![alt text](<images/Volume Sireines pgadmin lignes 38_74.JPG>)


    Ce volume contiendra les données de la base de données.

* Si le volume sireines_pgadmin_sireines_vol n'existe pas faire :
docker volume create sireines_pgadmin_sireines_vol 

et modifier **si besoin** les lignes 66 et 76 de de docker-compose.yml concernant ce volume.
![alt text](<images/Volume Sreines pgadmin lignes 66-76.JPG>)


Au final, on devrait avoir :

![alt text](images/Volume.PNG)

Ces volumes sont persistants sur le poste de travail.

### 3.3 Si besoin supprimer l'applicatif

Remove sur le conteneur (sireines_app_usine_container) puis l'image(sireines_app_usine_image).

Dans l'application Visual code :
![alt text](images/remove_conteneur.PNG)
![alt text](images/remove_image.PNG)

**Ou** dans Docker Desktop :
![alt text](images/delete_docker.PNG)

**Ou** en ligne de commande Dos (cmd)
```docker rm -f sireines_app_usine_container```
```docker rmi -f sireines_app_usine_image```


### 3.4 Créer et démarrer tous les services 
 
**Lancer sans le VPN :** 
```docker-compose up -d```

  dans le répertoire c:/sireines/sireines_pgadmin

<div style="page-break-after: always; visibility: hidden">\pagebreak</div>

## 4 - Installation de la base de données

### 4.1 Prérequis
Vérifier dans le fichier .env, les arguments de la bdd du Docker
            POSTGRES_DB=postgres
            POSTGRES_HOST=db
            POSTGRES_PORT=5432
            POSTGRES_USER=postgres
            POSTGRES_PASSWORD=postgres
            POSTGRES_SCHEMA=postgres

### 4.2  Installation de la BDD avec pgAdmin et/ou ligne de commande :

1 - Add Server 
Renseigner Onglet General : Name XXXXX ;
Renseigner Onglet Connection :
    Host : localhost
    Port : 8888
    Maintenance Database :
    UserName :
    MotdePasse : 



2- Alimentation de la base via un dump






<div style="page-break-after: always; visibility: hidden">\pagebreak</div>
# Annexe(s) 

## Ouvrir un terminal dans l'application Visual code 

**Choisir "Command prompt" à la place de powershell (par défaut)**


![alt text](images/prompt_cmd.PNG)

Vous pourrez alors utiliser les commandes dos non reconnues par powershell

---

<a id="reversing"></a>

# 📄 Reversing

> **Source :** `Reversing.md`

# Documentation WarchoDevplace

Vous pouvez télécharger le fichier ZIP contenant tous les documents ici :  
[Télécharger documents.zip](https://gitlab.eco4.cloud.e2.rie.gouv.fr/snum/pnm3/produits/rh/ttc/-/raw/documentation/documentation.zip)

Une fois téléchargé, décompressez le fichier pour accéder aux documents.

---

<a id="sireines-cerbre"></a>

# 📄 Sireines › Cerbère

> **Source :** `Sireines.Cerbère.md`

|Cerbère|Pré-production|Production|Recette|
| --- | --- | --- | --- |
|ID|546|546|564|

**Gestion de cerbere recette :**

https://cerbere.recette.e2.rie.gouv.fr/administration/



---

<a id="sireines-sites"></a>

# 📄 Sireines › sites

> **Source :** `Sireines.sites.md`

Recette : http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/

Pré prod : https://sireines.preprod.e2.rie.gouv.fr/Accueil.do

prod : https://sireines.e2.rie.gouv.fr/Accueil.do

---

<a id="sireines-version"></a>

# 📄 Sireines › Version

> **Source :** `Sireines.Version.md`

Version en cours en production (12 mars 2024) : 2.5.11