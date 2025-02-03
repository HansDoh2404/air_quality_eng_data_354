# Air_quality_project_data_354
Projet consistant à mettre en place un ETL pour l'étude de la qualité de l'air

## Prérequis 
Docker : https://docs.docker.com/get-docker <br />
Docker compose : https://docs.docker.com/compose/install <br />
Une fois installer, lancer docker

## Installation et lancement du projet 
git clone https://github.com/HansDoh2404/air_quality_eng_data_354.git <br />
cd air_quality_eng_data_354 <br />
docker-compose up --build -d<br />
cd scripts <br />
python3 extract_data.py <br />
python3 calcul_avg_polluant.py <br />
cd ..<br />
docker cp ./superset.db.backup superset:/app/superset_home/superset.db 


## Connexions aux différents serveurs
**Allez aux adresses suivantes :**
### localhost:8080 pour avoir accès à Airflow (orchestration) :
username : airflow, login : airflow
Activer les différents jobs si ce n'est pas le cas
### localhost:8047 pour avoir accès à Drill (connecteur à superset) :
- Aller dans Storage :
  Dans la liste des plugin, choisissez mongo en appuyant sur le bouton update <br />
  Modifier le champ "connection" en remplaçant localhost par mymongodb (assurez-vous d'utiliser le port 27017) <br />
  Cliquer sur update (une notification de succès devrait normalement apparaitre) <br /><br />
- Aller dans Query : <br />
  Entrer : SHOW SCHEMAS (vous devrez voir mongo.air_quality) <br />
  Revenez dans Query puis entrez : USE mongo.air_quality;
### localhost:8091 pour avoir accès à Superset (visualisation) :
username : admin, login : admin <br />
Aller dans Settings > Database Connection > Sélectionnez Apache Drill (parmi la liste des bd qui apparaitront) <br />
Entrer la chaine de connection suivante : drill+sadrill://drill:8047/mongo.air_quality

**N.B : Le job de forecasting génère un fichier predictions.txt que vous pourrez trouver dans dags/ml**

## Architecture du projet
L'architecture du projet repose sur plusieurs composants demandés et d'autres que nous avons ajoutés pour atteindre les objectifs :

Base de données : MongoDB. <br />
Visualisation : Apache Superset <br />
Driver de connexion entre Superset et MongoDB : Apache Drill <br />
Orchestration des tâches ETL : Apache Airflow <br />
Modèle de Forecasting : Python (basé sur la librairie Prophet) <br /><br />

Ci-dessous l'image de l'architecture : <br />
<img src="archi.png" alt="ARCHITECTURE ETL" width="800" height="600"/>


  
  

