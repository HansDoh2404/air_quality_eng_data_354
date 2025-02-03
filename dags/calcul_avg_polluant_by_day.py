import requests
import pandas as pd
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from pymongo import MongoClient


# URL de l'API
API_URL = "https://airqino-api.magentalab.it/v3/getStationHourlyAvg/"

# Configuration de MongoDB
MONGO_URI = "mongodb://mymongodb:27017/"
DB_NAME = "air_quality"
COLLECTION_NAME = "hourly_data"
DAILY_COLLECTION_NAME = "daily_averages"

# Liste des identifiants des stations
station_ids = ["283164601", "283181971"]  

# Fonction pour extraire les données depuis l'API
def fetch_data_from_api(station_id):
    url = API_URL + station_id
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'extraction des données pour la station {station_id} : {e}")
        return None

# Fonction pour calculer les moyennes des polluants
def calculate_daily_averages():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    daily_collection = db[DAILY_COLLECTION_NAME]
    
    for station_id in station_ids:
        print(f"Traitement des données pour la station {station_id}...")
        
        # Récupération des données de la dernière heure pour chaque station
        data = list(collection.find({"station_id": station_id}).sort("timestamp", -1).limit(1))
        
        if not data:
            print(f"Aucune donnée trouvée pour la station {station_id}.")
            continue
        
        # Calcul des moyennes des polluants
        df = pd.DataFrame(data)
        if 'PM2.5' in df.columns and 'CO' in df.columns:
            avg_pm25 = df['PM2.5'].mean()
            avg_co = df['CO'].mean()
            
            # Préparation des données à insérer dans la collection des moyennes journalières
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            daily_avg_data = {
                "station_id": station_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "Avg_PM2.5": avg_pm25,
                "Avg_CO": avg_co,
                "date_calcul": timestamp
            }
            
            # Vérification de l'existence des données dans la collection daily_averages
            existing_record = daily_collection.find_one({"station_id": station_id, "date": daily_avg_data["date"]})

            if existing_record:
                # Mise à jour du document existant avec les nouvelles moyennes
                daily_collection.update_one(
                    {"station_id": station_id, "date": daily_avg_data["date"]},  # Filtre pour trouver le document existant
                    {"$set": daily_avg_data}  # Mise à jour avec les nouvelles données
                )
                print(f"Les moyennes pour la station {station_id} et la date {daily_avg_data['date']} ont été mises à jour.")
            else:
                # Insertion d'un nouveau document si aucune donnée n'existe
                daily_collection.insert_one(daily_avg_data)
                print(f"Moyennes insérées pour la station {station_id} et la date {daily_avg_data['date']}.")


# Fonction principale pour exécuter le DAG
def run_daily_averages():
    calculate_daily_averages()

# Définition du DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'daily_pollutant_averages_v4',
    default_args=default_args,
    description='DAG pour récupérer les données des polluants et calculer les moyennes de façon journalière',
    schedule_interval='0 23 * * *',  # Exécution tous les jours à 23h00
    start_date=datetime(2025, 1, 27),
    catchup=False,
)

# Définition de la tâche pour calculer les moyennes
task = PythonOperator(
    task_id='calculate_daily_averages',
    python_callable=run_daily_averages,
    dag=dag,
)

task
