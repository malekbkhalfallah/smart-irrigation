"""
API météo simplifiée
"""
import time
import logging
from typing import Optional, Dict, Any
from config.settings import config

logger = logging.getLogger(__name__)

class WeatherAPI:
    """Gestion des données météo (simplifiée)"""
    
    def __init__(self):
        self.connected = False
        self.last_update = 0
        self.cache_duration = config.api.WEATHER_CACHE_DURATION
    
    def get_weather_forecast(self) -> Optional[Dict[str, Any]]:
        """Récupère les prévisions météo (simplifié)"""
        # Pour l'instant, retourner None (mode offline par défaut)
        # Vous pourrez ajouter l'API OpenWeatherMap plus tard
        return None
    
    def should_irrigate_based_on_weather(self) -> bool:
        """Décide si on peut irriguer basé sur la météo"""
        # Par défaut, retourner True (pas de restriction météo)
        return True

# Instance globale
weather_api = WeatherAPI()