"""
Gestion de l'API météo (OpenWeatherMap)
"""
import time
import requests
import logging
from typing import Optional, Dict, Any
from config.settings import config

logger = logging.getLogger(__name__)

class WeatherAPI:
    """Gestion des données météo"""
    
    def __init__(self):
        self.api_key = config.api.OPENWEATHER_API_KEY
        self.city = config.api.OPENWEATHER_CITY
        self.last_update = 0
        self.cached_forecast = None
        self.connected = False
        
    def check_connection(self) -> bool:
        """Vérifie la connexion internet"""
        try:
            # Test simple de connexion
            requests.get("http://www.google.com", timeout=5)
            self.connected = True
            return True
        except:
            self.connected = False
            config.offline_mode = True
            return False
    
    def get_weather_forecast(self) -> Optional[Dict[str, Any]]:
        """Récupère les prévisions météo"""
        # Vérifier si on est hors ligne
        if not self.check_connection():
            logger.info("Mode hors ligne - pas d'accès API météo")
            config.offline_mode = True
            return None
        
        # Vérifier le cache
        current_time = time.time()
        if (self.cached_forecast and 
            current_time - self.last_update < config.api.WEATHER_CACHE_DURATION):
            logger.debug("Utilisation du cache météo")
            return self.cached_forecast
        
        # Vérifier la clé API
        if not self.api_key:
            logger.warning("Clé API OpenWeatherMap non configurée")
            return None
        
        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": self.city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "fr"
            }
            
            logger.info(f"Récupération météo pour {self.city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraire les informations importantes
            forecast = {
                "city": data.get("city", {}).get("name", self.city),
                "current": self._extract_current_weather(data),
                "rain_forecast": self._extract_rain_forecast(data),
                "timestamp": time.time()
            }
            
            self.cached_forecast = forecast
            self.last_update = current_time
            config.offline_mode = False
            
            return forecast
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API météo: {e}")
            config.offline_mode = True
            return None
        except Exception as e:
            logger.error(f"Erreur traitement données météo: {e}")
            return None
    
    def _extract_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les conditions actuelles"""
        if not data.get("list"):
            return {}
        
        current = data["list"][0]
        return {
            "temperature": current["main"]["temp"],
            "humidity": current["main"]["humidity"],
            "description": current["weather"][0]["description"],
            "icon": current["weather"][0]["icon"]
        }
    
    def _extract_rain_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les prévisions de pluie pour les prochaines 24h"""
        rain_forecast = {
            "will_rain": False,
            "next_rain_hours": None,
            "rain_amount": 0
        }
        
        if not data.get("list"):
            return rain_forecast
        
        current_time = time.time()
        
        for forecast in data["list"][:8]:  # Prochaines 24h (3h * 8 = 24h)
            forecast_time = forecast["dt"]
weather_api = WeatherAPI()  
           