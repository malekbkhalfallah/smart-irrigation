"""
Configuration centrale du système - VERSION FINALE
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GPIOConfig:
    """Configuration des broches GPIO - RASPBERRY PI 5"""
    # LEDs d'état
    LED_RED_PIN: int = 18      # GPIO18 - Alerte/Erreur
    LED_GREEN_PIN: int = 19    # GPIO19 - Tout va bien
    LED_YELLOW_PIN: int = 20   # GPIO20 - Irrigation en cours
    LED_WHITE_PIN: int = 21    # GPIO21 - Mode en ligne
    
    # Capteurs
    SOIL_MOISTURE_PIN: int = 24       # GPIO24
    DHT22_PIN: int = 17               # GPIO17
    RAINDROP_PIN: int = 27            # GPIO27
    WATER_LEVEL_PIN: int = 23         # GPIO23
    
    # Actionneurs
    PUMP_RELAY_PIN: int = 26          # GPIO26

@dataclass
class PlantProfile:
    """Profil par défaut"""
    name: str = "Tomate"
    soil_type: str = "Argileux"
    min_moisture: float = 40.0    # % - Seuil minimal
    max_moisture: float = 80.0    # % - Seuil maximal
    optimal_moisture: float = 60.0 # % - Niveau optimal

@dataclass
class IrrigationSettings:
    """Paramètres d'irrigation"""
    CHECK_INTERVAL: int = 300           # 5 minutes entre vérifications
    IRRIGATION_DURATION: int = 30       # 30 secondes d'arrosage
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
    DATABASE_CLEANUP_INTERVAL: int = 3600  # Nettoyage toutes les heures

@dataclass
class APIConfig:
    """Configuration API"""
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_CITY: str = "Paris,FR"
    WEATHER_CACHE_DURATION: int = 3600  # 1 heure
    WEATHER_FORECAST_DAYS: int = 3      # Jours de prévision
    
    # Configuration serveur
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5000
    DEBUG_MODE: bool = False
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

@dataclass
class FirebaseConfig:
    """Configuration Firebase"""
    SERVICE_ACCOUNT_FILE: str = "firebase_service_account.json"
    COLLECTION_SENSORS: str = "sensor_readings"
    COLLECTION_IRRIGATION: str = "irrigation_events"
    COLLECTION_SYSTEM: str = "system_status"
    COLLECTION_USERS: str = "users"

class SystemConfig:
    """Configuration globale"""
    
    def __init__(self):
        self.gpio = GPIOConfig()
        self.plant = PlantProfile()
        self.irrigation = IrrigationSettings()
        self.api = APIConfig()
        self.firebase = FirebaseConfig()
        
        # États système
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
        self.offline_mode: bool = False  # Détecté automatiquement
        self.system_initialized: bool = False
        
        # Chemins
        self.db_path: str = "irrigation.db"
        self.log_path: str = "irrigation_system.log"

# Instance globale
config = SystemConfig()