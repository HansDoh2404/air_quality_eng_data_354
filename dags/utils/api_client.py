import requests
from config.api_config import base_url, station_ids

class AirQinoAPIClient:
    
    def __init__(self):
        """
        Initialisation du client API AirQino avec la configuration directement incluse.
        """
        self.base_url = base_url
        self.station_ids = station_ids

    def get_hourly_data(self):
        """
        Récupération des données horaires pour toutes les stations spécifiées.
        """
        results = {}
        
        for station_id in self.station_ids:
            # Construction de l'URL pour chaque station
            url = f"{self.base_url}{station_id}"
            
            try:
                # Requête à l'API
                response = requests.get(url)
                response.raise_for_status()  
                results[station_id] = response.json()
            except requests.exceptions.RequestException as e:
                
                print(f"Erreur pour la station {station_id} : {e}")
                results[station_id] = None
        
        return results

if __name__ == "__main__":
    client = AirQinoAPIClient()
    data = client.get_hourly_data()
    print(data)
