from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pymongo import MongoClient
from utils.api_client import AirQinoAPIClient

# Configuration MongoDB
MONGO_URI = "mongodb://mymongodb:27017/"
DB_NAME = "air_quality"
COLLECTION_NAME = "hourly_data"

def extract_and_load_to_mongodb(station_id, **kwargs):
    """
    Fonction pour extraire les données depuis l'API AirQino et insérer les derniers enregistrements dans MongoDB.
    """
    # Initialisation du client API
    client = AirQinoAPIClient()
    
    # Extraction des données depuis l'API pour toutes les stations
    data = client.get_hourly_data()
    
    if data and station_id in data and data[station_id]:
        # Récupération des listes de données
        list1 = data[station_id].get("data", [])
        list2 = data[station_id].get("data", [])
        
        # Récupération des derniers éléments de chaque liste
        last_element_list1 = max(list1, key=lambda x: x.get("timestamp", "")) if list1 else None
        last_element_list2 = max(list2, key=lambda x: x.get("timestamp", "")) if list2 else None
        
        # Ajout de station_id et date_extraction aux derniers éléments
        extraction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if last_element_list1:
            last_element_list1["station_id"] = station_id
            last_element_list1["date_extraction"] = extraction_date
        
        if last_element_list2:
            last_element_list2["station_id"] = station_id
            last_element_list2["date_extraction"] = extraction_date
        
        # Connexion à MongoDB
        mongo_client = MongoClient(MONGO_URI, connectTimeoutMS=60000, socketTimeoutMS=60000)
        db = mongo_client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Insertion dans MongoDB
        try:
            if last_element_list1:
                collection.delete_one({"_id": last_element_list1.get("_id")})  
                collection.insert_one(last_element_list1)
                print(f"Dernier enregistrement pour la station {station_id} (list1) inséré avec succès dans MongoDB.")
            
            if last_element_list2:
                collection.delete_one({"_id": last_element_list2.get("_id")}) 
                collection.insert_one(last_element_list2)
                print(f"Dernier enregistrement pour la station {station_id} (list2) inséré avec succès dans MongoDB.")
        except Exception as e:
            print(f"Erreur lors de l'insertion dans MongoDB : {e}")




# Fonction pour récupérer le début de l'heure suivante
def get_next_hour():
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return next_hour

# Récupérer la date et l'heure actuelles pour le `start_date`
start_date = get_next_hour()

# Configuration par défaut
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "extraction_by_hour_dag_v19",
    default_args=default_args,
    description="Extraction horaire des données à partir de l'API de AirQino",
    schedule_interval="0 * * * *",  # Exécution toutes les heures
    start_date=datetime(2025, 1, 27),
    catchup=False,  # Pas d'exécution rétroactive
) as dag:
    # Tâche pour la première station (283164601)
    extract_and_load_task_1 = PythonOperator(
        task_id="extract_and_load_to_mongodb_station_1",
        python_callable=extract_and_load_to_mongodb,
        op_args=["283164601"],  
        provide_context=True,
    )
    
    # Tâche pour la deuxième station (283181971)
    extract_and_load_task_2 = PythonOperator(
        task_id="extract_and_load_to_mongodb_station_2",
        python_callable=extract_and_load_to_mongodb,
        op_args=["283181971"],  
        provide_context=True,
    )

    # Exécution des tâches
    [extract_and_load_task_1, extract_and_load_task_2]

