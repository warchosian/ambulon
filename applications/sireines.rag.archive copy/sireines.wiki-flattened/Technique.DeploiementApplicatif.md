---
css: ./style.css
---

# Procédure de déploiement de l'applicatif {.chapter}


- ## Deploiement applicatif

- ## Activer le VPN

- ## Activer Pageant

   - ### Lancer le bastion sur Pageant
          ssh debian@10.165.134.248

   - ### Connexion sur la bastion PNM3
       pour faire, faire ceci

       et aussi cela 

   - ### Modification du fichier docker compose avec la nouvelle version
   ```bash
     cd /opt/app
 docker ps                                            1 ↵
CONTAINER ID   IMAGE                                        COMMAND                  CREATED        STATUS       PORTS                                NAMES
c5a9345c57ef   eu.gcr.io/dpnm3-lab/sireines:2.5.14-LIVREE   "/scripts/entrypoint…"   2 months ago   Up 8 weeks   0.0.0.0:8080->8080/tcp               sireines-app
a85ba5be0b3d   postgres:15.6-alpine                         "docker-entrypoint.s…"   2 months ago   Up 8 weeks   0.0.0.0:5432->5432/tcp               sireines-db
b63a78dfbf9e   grafana/promtail:latest                      "/usr/bin/promtail -…"   5 months ago   Up 8 weeks   19080/tcp, 0.0.0.0:19080->9080/tcp   metrics-promtail
1c77901f8edf   prom/pushgateway                             "/bin/pushgateway"       5 months ago   Up 8 weeks   19091/tcp, 0.0.0.0:19091->9091/tcp   metrics-push
160ff64fdf50   prom/node-exporter:latest                    "/bin/node_exporter …"   5 months ago   Up 8 weeks   19100/tcp, 0.0.0.0:19100->9100/tcp   metrics-node
36346c5416b9   cmosley/docker_exporter                      "./docker_exporter"      5 months ago   Up 8 weeks   19417/tcp, 0.0.0.0:19417->9417/tcp   metrics-docker

- constater que sireines-app et sireines-db s'executent



     cp docker-compose.yml docker-compose.yml.20241212
     vi docker-compose.yml


```

- ## Arreter le conteneur applicatif
docker stop sireines-app                           
sireines-app

- ## Supprimer le conteneur applicatif
docker rm sireines-app                            
sireines-app


- ## Relancer le docker-compose qui a pour effet de relancer l'application
/opt/app » docker compose up -d                               127 ↵
[+] Running 16/16
 ✔ app Pulled                                                                           32.7s
   ✔ bd8f6a7501cc Already exists                                                         0.0s
   ✔ 44718e6d535d Already exists                                                         0.0s
   ✔ efe9738af0cb Already exists                                                         0.0s
   ✔ f37aabde37b8 Already exists                                                         0.0s
   ✔ b87fc504233c Already exists                                                         0.0s
   ✔ cc62143cb8cc Already exists                                                         0.0s
   ✔ 646a47c88e43 Already exists                                                         0.0s
   ✔ d65bec3def24 Already exists                                                         0.0s
   ✔ 9b7471aadf4c Already exists                                                         0.0s
   ✔ cb4999122126 Already exists                                                         0.0s
   ✔ 537eff314fa1 Pull complete                                                         19.4s
   ✔ 8b1693a28ca0 Pull complete                                                         19.8s
   ✔ c58195575909 Pull complete                                                         21.2s
   ✔ faa83b01ce1b Pull complete                                                         21.3s
   ✔ 4198d8a165e6 Pull complete                                                         21.4s
[+] Running 2/2
 ✔ Container sireines-db   Running                                                       0.0s
 ✔ Container sireines-app  Started   
     
- ## Verifier que les conteneurs sont actifs

 docker ps                                          126 ↵
CONTAINER ID   IMAGE                                        COMMAND                  CREATED          STATUS          PORTS                                NAMES
41e614549398   eu.gcr.io/dpnm3-lab/sireines:2.5.16-LIVREE   "/scripts/entrypoint…"   43 seconds ago   Up 42 seconds   0.0.0.0:8080->8080/tcp               sireines-app
a85ba5be0b3d   postgres:15.6-alpine                         "docker-entrypoint.s…"   2 months ago     Up 8 weeks      0.0.0.0:5432->5432/tcp               sireines-db
b63a78dfbf9e   grafana/promtail:latest                      "/usr/bin/promtail -…"   5 months ago     Up 8 weeks      19080/tcp, 0.0.0.0:19080->9080/tcp   metrics-promtail
1c77901f8edf   prom/pushgateway                             "/bin/pushgateway"       5 months ago     Up 8 weeks      19091/tcp, 0.0.0.0:19091->9091/tcp   metrics-push
160ff64fdf50   prom/node-exporter:latest                    "/bin/node_exporter …"   5 months ago     Up 8 weeks      19100/tcp, 0.0.0.0:19100->9100/tcp   metrics-node
36346c5416b9   cmosley/docker_exporter                      "./docker_exporter"      5 months ago     Up 8 weeks      19417/tcp, 0.0.0.0:19417->9417/tcp   metrics-docker
```

- ## Quitter les connexions bastion

- ## Vérifier que l'application est fonctionnelle sur le réseau du ministère

   - ### Recette :
         http://sireines.recette.pnm3.eco4.cloud.e2.rie.gouv.fr/

   - ### Pré prod :
         https://sireines.preprod.e2.rie.gouv.fr/Accueil.do

   - ### prod :
         https://sireines.e2.rie.gouv.fr/Accueil.do

- ## Effectuer les tests fonctionnels élémentaires

   - ### Courriers

   - ### Statistiques


- ## Avertir la maitrise d'ouvrage
 ```text
     Une fois la recette validée pour :
      - le constat de l'affichage de la nouvelle version
      - les tests fonctionnels propres aux évolutions
      - les tests élémentaires de base, 
     le deploiement de la prod peut intervenir. 
     Une fois la preprod validée par la maitrise d'ouvrage, le deploiement de la prod peut intervenir 
 ```
 