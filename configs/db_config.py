# Définition des variables de configuration de la base de données

# configuration du nom de la base de données et des URI
MONGO_URI = "mongodb://mymongodb:27017/" # pour la connexion au conteneur contenant la bd
MONGO_URI_LOCAL = "mongodb://localhost:27018" # pour permettre le lancement des scripts en local
DB_NAME = "air_quality" 

# configuration du nom des différentes collections
COLLECTION_NAME = "hourly_data" # stockage des données extraites par heures
COLLECTION_HEADERS = "headers"  # stockage des données sur les stations
DAILY_COLLECTION_NAME = "daily_averages" # stockage des moyennes journalières des polluants