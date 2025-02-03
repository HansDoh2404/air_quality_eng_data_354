import pandas as pd
import datetime
from pymongo import MongoClient


# Configuration MongoDB
MONGO_URI = "mongodb://localhost:27018"
DB_NAME = "air_quality"
COLLECTION_NAME = "hourly_data"
DAILY_COLLECTION_NAME = "daily_averages"

def calculate_and_store_daily_averages():
    try:
        # Connexion à MongoDB
        mongo_client = MongoClient(MONGO_URI)
        db = mongo_client[DB_NAME]
        input_collection = db[COLLECTION_NAME]
        output_collection = db[DAILY_COLLECTION_NAME]

        # Récupération des données depuis la collection d'entrée
        data = list(input_collection.find())

        if not data:
            print("Aucune donnée trouvée dans la base de données.")
            return

        # Transformation des données en DataFrame
        df = pd.DataFrame(data)

        # Vérification des colonnes nécessaires
        required_columns = {"station_id", "timestamp", "PM2_5", "CO", "NO2", "O3", "PM10", "RH", "T", "T_int"}
        if not required_columns.issubset(df.columns):
            print(f"Les colonnes suivantes sont manquantes : {required_columns - set(df.columns)}")
            return

        # Conversion de timestamp en datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # Suppression des lignes avec des timestamps invalides
        df = df.dropna(subset=["timestamp"])

        # Extraction de la date uniquement
        df["date"] = df["timestamp"].dt.date

        # Calcul des moyennes journalières pour chaque station
        daily_averages = (
            df.groupby(["station_id", "date"])
            .agg({
                "PM2_5": "mean", 
                "CO": "mean", 
                "NO2": "mean",
                "O3": "mean",
                "PM10": "mean",
                "RH": "mean",
                "T": "mean",
                "T_int": "mean"
            })
            .reset_index()
        )

        # Conversion de date en timestamp
        daily_averages["date"] = daily_averages["date"].apply(lambda x: x.strftime("%Y-%m-%d"))

        # Ajout d'un champ date_calcul pour suivre la date de calcul des polluants et d'insertion dans la BD
        daily_averages["date_calcul"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Conversion en dictionnaires pour l'insertion dans MongoDB
        records_to_insert = daily_averages.to_dict("records")

        cpt_record_inserted = 0
        # Vérification des doublons avant insertion
        for record in records_to_insert:
            # Vérifier si une entrée avec le même station_id et date existe déjà
            existing_record = output_collection.find_one({
                "station_id": record["station_id"],
                "date": record["date"]
            })

            if existing_record:
                print(f"Doublon trouvé pour station_id {record['station_id']} et date {record['date']}, saut de l'insertion.")
            else:
                output_collection.insert_one(record)
                cpt_record_inserted += 1
                
        print(f"{cpt_record_inserted} enregistrements insérés dans la collection '{DAILY_COLLECTION_NAME}'.")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    calculate_and_store_daily_averages()
