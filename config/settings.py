"""
Configuration centrale du système
"""
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GPIOConfig:
    """Configuration des broches GPIO"""
    # Capteurs
    SOIL_MOISTURE_PIN: int = 24       # GPIO24
    DHT22_PIN: int = 17               # GPIO17
    RAINDROP_DIGITAL_PIN: int = 27    # GPIO27
    WATER_LEVEL_PIN: int = 23         # GPIO23
    
    # Actionneurs
    PUMP_RELAY_PIN: int = 26          # GPIO26

@dataclass
class PlantProfile:
    """Profil de la plante"""
    name: str = "Tomate"
    soil_type: str = "Argileux"
    min_moisture: float = 40.0    # % - Seuil minimal
    max_moisture: float = 80.0    # % - Seuil maximal
    
@dataclass
class IrrigationSettings:
    """Paramètres d'irrigation"""
    CHECK_INTERVAL: int = 300           # 5 minutes entre vérifications
    IRRIGATION_DURATION: int = 30       # 30 secondes d'arrosage par défaut
    MAX_IRRIGATION_PER_DAY: int = 300   # 5 minutes max par jour
    
    # Conditions météo
    MIN_TEMP_FOR_IRRIGATION: float = 10.0
    MAX_TEMP_FOR_IRRIGATION: float = 32.0
    MAX_AIR_HUMIDITY: float = 85.0
    
    # Gestion eau
    MIN_WATER_LEVEL: float = 20.0       # % minimal dans réservoir
    
    # Mode hors ligne
    OFFLINE_MODE_ENABLED: bool = True
    HISTORY_DAYS: int = 7               # Jours d'historique à conserver

@dataclass
class APIConfig:
    """Configuration API"""
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_CITY: str = "Paris,FR"
    WEATHER_CACHE_DURATION: int = 3600  # 1 heure

class SystemConfig:
    """Configuration globale"""
    
    def __init__(self):
        self.gpio = GPIOConfig()
        self.plant = PlantProfile()
        self.irrigation = IrrigationSettings()
        self.api = APIConfig()
        
        # Mode système
        self.debug_mode: bool = True
        self.offline_mode: bool = False
        self.manual_override: bool = False

# Instance globale
config = SystemConfig()