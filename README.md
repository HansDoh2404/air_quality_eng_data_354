# Air_quality_project_data_354
Projet consistant à mettre en place un ETL pour l'étude de la qualité de l'air

## Prérequis 
Docker : https://docs.docker.com/get-docker <br />
Docker compose : https://docs.docker.com/compose/install <br />
Python : https://www.python.org/downloads <br />
Git : https://git-scm.com/downloads <br />
Une fois installés, lancer docker

## Installation et lancement du projet 
git clone https://github.com/HansDoh2404/air_quality_eng_data_354.git <br />
cd air_quality_eng_data_354 <br />
pip install -r requirements.txt <br />
docker-compose up --build -d<br />
cd scripts <br />
pip install pymongo (si vous rencontrez l'erreur No Module found : pymongo)<br />
python3 extract_data.py <br />
python3 calcul_avg_polluant.py <br />
cd ..<br />
docker cp ./superset.db.backup superset:/app/superset_home/superset.db <br />
sudo chown -R 50000:50000 ./logs <br />
sudo chmod -R 775 ./logs (pour éviter des erreurs de permissions sur les logs)


## Connexions aux différents serveurs
**Allez aux adresses suivantes :**
### localhost:8082 pour avoir accès à Airflow (orchestration) :
username : airflow, login : airflow <br />
Activer les différents jobs si ce n'est pas le cas <br /><br />
Trois jobs sont visibles :<br />
- daily_polluant_averages : pour le calcul des différentes moyennes journalières des polluants <br />
- extraction_by_hour_dag : pour l'extraction des données horaires des différentes stations <br />
- forecasting_by_hour : pour le forecasting sur les deux prochaines heures <br />
### localhost:8047 pour avoir accès à Drill (connecteur à superset) :
- Aller dans Storage :
  Dans la liste des plugin, choisissez mongo en appuyant sur le bouton update <br />
  Modifier le champ "connection" en remplaçant localhost par mymongodb (assurez-vous d'utiliser le port 27017) <br />
  Cliquer sur Enable puis Update (une notification de succès devrait normalement apparaitre à chaque fois) <br /><br />
- Aller dans Query : <br />
  Entrer : SHOW SCHEMAS; (vous devrez voir mongo.air_quality) <br />
  Revenez dans Query puis entrez : USE mongo.air_quality;
### localhost:8091 pour avoir accès à Superset (visualisation) :
username : admin, login : admin <br />
 - Si vous avez la visibilité directement sur les dashboards : visualisez les et appréciez les <br />
 - Sinon : 
    Aller dans Settings > Database Connection > Sélectionnez Apache Drill (parmis la liste des bd qui apparaitront) <br />
    Entrer la chaine de connection suivante : drill+sadrill://drill:8047/mongo.air_quality <br />
    Cliquez sur test connection (pour vous assurer que la connection fonctionne normalement)<br />
    Puis cliquez sur connection<br />
    Après cela vous devrez être en mesure de voir le dashboard AIR_QUALITY_DASHBOARD ainsi que les diagrammes <br />
  - Au cas où une erreur apparait au niveau des diagrammes, raffraichissez la page (plusieurs fois s'il le faut) jusqu'à ce que l'erreur disparaisse <br /> 

**N.B : Le job de forecasting génère un fichier predictions.txt que vous pourrez trouver dans dags/ml**

## Architecture du projet
L'architecture du projet repose sur plusieurs composants demandés et d'autres que nous avons ajoutés pour atteindre les objectifs :

Base de données : MongoDB. <br />
Visualisation : Apache Superset <br />
Driver de connexion entre Superset et MongoDB : Apache Drill <br />
Orchestration des tâches ETL : Apache Airflow <br />
Modèle de Forecasting : Python (basée sur la librairie Prophet) <br /><br />

**Ci-dessous l'image de l'architecture :** <br /><br />
<img src="archi.png" alt="ARCHITECTURE ETL" width="800" height="400"/>


  
  

