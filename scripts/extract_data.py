import sys
import os
# Ajouter du chemin du dossier parent au sys.path pour faciliter les importations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
import requests
from pymongo import MongoClient, errors
from configs.db_config import MONGO_URI_LOCAL, DB_NAME, COLLECTION_NAME, COLLECTION_HEADERS
from configs.api_config import base_url, station_ids

# Fonction pour extraire les données depuis l'API
def fetch_data_from_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'extraction des données : {e}")
        return None

# Fonction pour garantir l'existence des collections dans la base de données
def ensure_collections(uri, db_name, collections):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        
        for collection_name in collections:
            if collection_name not in db.list_collection_names():
                print(f"Création de la collection '{collection_name}' dans la base de données '{db_name}'.")
                db.create_collection(collection_name)
            else:
                print(f"La collection '{collection_name}' existe déjà.")
        
        return {name: db[name] for name in collections}
    except errors.ConfigurationError as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        return None

# Fonction pour sauvegarder les données dans MongoDB
def save_to_mongodb(collection, data, metadata, unique_keys):
    if data:
        # Ajout de métadonnées aux documents
        document = {**data, **metadata}
        
        # Vérification de l'existence du document basé sur les clés uniques
        if not collection.find_one(unique_keys):
            try:
                collection.insert_one(document)
            except Exception as e:
                print(f"Erreur lors de l'insertion dans MongoDB : {e}")
        else:
            print(f"Document déjà présent dans {collection.name}, insertion ignorée.")
    else:
        print("Pas de données à insérer.")

# Extraction et sauvegarde des données
if __name__ == "__main__":
    print("Extraction des données depuis l'API...")
    
    # Connexion à MongoDB et garantie de l'existence des collections
    collections = ensure_collections(MONGO_URI_LOCAL, DB_NAME, [COLLECTION_HEADERS, COLLECTION_NAME])
    if collections is None:
        print("Impossible de se connecter à MongoDB. Arrêt du script.")
    else:
        headers_collection = collections[COLLECTION_HEADERS]
        data_collection = collections[COLLECTION_NAME]

        # Parcours des stations et traitement des données
        for station_id in station_ids:
            print(f"Traitement de la station : {station_id}")
            url = base_url + station_id
            response = fetch_data_from_api(url)
            if response:
                # Séparation des parties `header` et `data`
                header = response.get("header", {})
                data = response.get("data", [])
                
                # Ajout des métadonnées
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                metadata = {"station_id": station_id, "date_extraction": timestamp}
                
                # Sauvegarde des headers (vérification de l'existence du station_id)
                if header:
                    save_to_mongodb(headers_collection, header, metadata, {"station_id": station_id})
                
                # Sauvegarde des données
                for record in data:
                    # Renommer le champ "PM2.5" en "PM2_5" si présent
                    if "PM2.5" or "T. int." in record:
                        record["PM2_5"] = record.pop("PM2.5")
                        record["T_int"] = record.pop("T. int.")
                    save_to_mongodb(data_collection, record, metadata, {"station_id": station_id, "timestamp": record.get("timestamp")})
                
                print(f"Fin du traitement pour la station : {station_id}")
                
            else:
                print(f"Échec de la récupération des données pour la station {station_id}.")
