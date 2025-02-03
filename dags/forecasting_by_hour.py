import os
import pandas as pd
from pymongo import MongoClient
from prophet import Prophet
from datetime import datetime, timedelta

# Importations Airflow
from airflow import DAG
from airflow.operators.python import PythonOperator

# === Partie "Forecasting" (logique métier) ===

# --- Configuration MongoDB ---
MONGO_URI = "mongodb://mymongodb:27017/"
DB_NAME = "air_quality"
COLLECTION_NAME = "hourly_data"

def load_data_from_mongodb():
    """Charge les données depuis MongoDB et retourne un DataFrame."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    docs = list(collection.find())
    records = []
    
    for doc in docs:
        ts = doc.get("timestamp")
        if isinstance(ts, str):
            ts = pd.to_datetime(ts)
        
        station_id = doc.get("station_id")
        # Exclure les champs _id, timestamp et station_id pour récupérer seulement les mesures
        data_dict = {key: value for key, value in doc.items() if key not in ["_id", "timestamp", "station_id"]}
        
        # Ajout des colonnes station_id et timestamp
        data_dict["timestamp"] = ts
        data_dict["station_id"] = station_id
        
        records.append(data_dict)
    
    df = pd.DataFrame(records)
    
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
    
    return df

def forecast_variable(df, variable, periods=2):
    """
    Entraîne un modèle Prophet sur la série temporelle d'une variable et prédit
    les valeurs pour les 'periods' prochaines heures.
    
    :param df: DataFrame contenant les colonnes "timestamp" et la variable d'intérêt.
    :param variable: Nom de la variable à prévoir.
    :param periods: Nombre d'heures à prévoir.
    :return: DataFrame des prévisions (colonnes 'next_hour', 'pred', 'pred_lower', 'pred_upper') ou None si données insuffisantes.
    """
    # Préparer les données pour Prophet : colonnes 'ds' et 'y'
    df_var = df[["timestamp", variable]].dropna().rename(columns={"timestamp": "ds", variable: "y"})
    df_var = df_var.sort_values("ds")
    
    if df_var.empty or len(df_var) < 10:
        print(f"Pas assez de données pour le forecasting de {variable}.")
        return None

    # Entraînement du modèle Prophet
    model = Prophet()
    model.fit(df_var)
    
    # Création du DataFrame pour les prévisions futures (fréquence horaire)
    future = model.make_future_dataframe(periods=periods, freq='h')
    forecast = model.predict(future)
    
    # Récupérer uniquement les prévisions après la dernière date disponible
    last_date = df_var["ds"].max()
    predictions = forecast[forecast["ds"] > last_date]
    
    # Renommer les colonnes comme demandé
    predictions = predictions.rename(columns={
        "ds": "next_hour",
        "yhat": "pred",
        "yhat_lower": "pred_lower",
        "yhat_upper": "pred_upper"
    })
    
    return predictions[["next_hour", "pred", "pred_lower", "pred_upper"]]

def forecasting_main():
    """Exécute la logique de prévision et enregistre les résultats dans un fichier."""
    # Charger les données depuis MongoDB
    df = load_data_from_mongodb()
    
    if df.empty:
        print("Aucune donnée récupérée depuis MongoDB.")
        return
    else:
        print("Données chargées depuis MongoDB :")
        print(df.head())
        print("Colonnes disponibles :", df.columns.tolist())
        
        # Identifier les variables à prévoir (exclure 'timestamp', 'station_id' et 'date_extraction' si présent)
        variables = [col for col in df.columns if col not in ["timestamp", "station_id", "date_extraction"]]
        print(f"Variables à prévoir : {variables}")

        # Itérer sur chaque variable et générer les prévisions pour les 2 prochaines heures
        forecasts = {}
        for var in variables:
            print(f"\nPrévision pour la variable {var}:")
            preds = forecast_variable(df, var, periods=2)
            if preds is not None:
                forecasts[var] = preds
                print(preds)
            else:
                print(f"Forecasting impossible pour {var}.")

        # Sauvegarde des prévisions dans un fichier texte dans le dossier ml
        if forecasts:
            all_forecasts = pd.concat(forecasts.values(), keys=forecasts.keys(), names=["Variable"]).reset_index(level=0)
            ml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml")
            
            os.makedirs(ml_dir, exist_ok=True)
            
            file_path = os.path.join(ml_dir, "predictions.txt")
            absolute_path = os.path.abspath(file_path)
            all_forecasts.to_csv(file_path, sep="\t", index=False, header=True, mode='w')
            print(f"Les prévisions ont été enregistrées dans : {absolute_path}")
        else:
            print("Aucune prévision n'a pu être générée.")

# === Partie "DAG Airflow" ===

def run_forecasting_script():
    """
    Fonction appelée par le DAG Airflow.
    Elle exécute directement la fonction de prévision.
    """
    # On peut directement appeler la fonction principale de prévision
    forecasting_main()

# Paramètres du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'forecasting_by_hour_v8',
    default_args=default_args,
    description='Exécution du script de prévision des polluants chaque heure',
    schedule_interval="0 * * * *",
    catchup=False,
)

forecasting_task = PythonOperator(
    task_id='run_forecasting',
    python_callable=run_forecasting_script,
    dag=dag,
)

# Pour Airflow, il suffit que la variable "forecasting_task" soit définie.
# Si ce script est exécuté directement (en dehors d'Airflow), on lance la fonction de prévision.
if __name__ == "__main__":
    forecasting_main()
