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