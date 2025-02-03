# Air_quality_project_data_354
Projet consistant à mettre en place un ETL pour l'étude de la qualité de l'air

## Prérequis 
Docker et Docker compose
Une fois installer, lancer docker

## Installation et lancement du projet 
git clone https://github.com/HansDoh2404/air_quality_eng_data_354.git
cd air_quality_eng_data_354
docker-compose up --build
cd scripts
python3 extract_data.py
python3 calcul_avg_polluant.py

## Connexions au différents serveurs
**aller à :**
### localhost:8082 pour avoir accès à Airflow (orchestration) :
username : airflow, login : airflow
### localhost:8047 pour avoir accès à Drill (connecteur à superset) :
- aller dans Storage :
  dans la liste des plugin, choisissez mongo en appuyant sur le bouton update
  modifier le champ connection en remplaçant localhost par mymongodb (assurez-vous que le port est 27017
  cliquer sur update (une notification de succès devrait normalement apparaitre)
- aller dans Query :
  entrer : SHOW SCHEMAS (vous devrez voir mongo.air_quality)
  entrez ensuite : USE mongo.air_quality;
### localhost:8091 pour avoir accès à Superset (visualisation) :
username : admin, login : admin
Aller dans Settings > Database Connection > Sélectionnez Apache Drill
Entrer la chaine de connection suivante : drill+sadrill://drill:8047/mongo.air_quality
  
  

