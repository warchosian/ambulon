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