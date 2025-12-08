"""
Configuration centrale du système d'irrigation
Tous les paramètres ajustables sont ici
date[01/12/2025]
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class GPIOConfig:
    """Configuration des broches GPIO"""
    # Capteurs
    SOIL_MOISTURE_PIN: int = 24         # GPIO24  valide
    DHT22_PIN: int = 17                 # GPIO17  valide
    RAINDROP_DIGITAL_PIN: int = 27      # GPIO27
    WATER_LEVEL_PIN: int = 23           # GPIO23  valide
    
    # Actionneurs
    PUMP_RELAY_PIN: int = 26            # GPIO26  valide
    STATUS_LED_PIN: int = 16            # GPIO16  valide
    
   
@dataclass
class IrrigationSettings:
    """Seuils pour les capteurs"""
    # Humidité du sol (%) - type de sol
    SOIL_MOISTURE_THRESHOLDS: Dict[str, Dict[str, float]] = field(
        default_factory=lambda: {
            'sableux': {'min': 20.0, 'optimal': 35.0, 'max': 50.0},
            'limoneux': {'min': 30.0, 'optimal': 45.0, 'max': 60.0},
            'argileux': {'min': 40.0, 'optimal': 55.0, 'max': 70.0},
        }
    )
    
    # Température air (°C)
    TEMPERATURE_THRESHOLD_MIN: float = 10.0
    TEMPERATURE_THRESHOLD_MAX: float = 35.0
    
    # Humidité air (%)
    AIR_HUMIDITY_THRESHOLD_HIGH: float = 80.0
    
    # Pluie
    RAIN_THRESHOLD: float = 50.0  # Seuil analogique (0-100)
    
    # Niveau d'eau (cm ou %)
    WATER_LEVEL_CRITICAL: float = 10.0  # 10% ou 10cm
    WATER_LEVEL_LOW: float = 25.0
    WATER_LEVEL_HIGH: float = 80.0

@dataclass
class PlantConfig:
    """Configuration par type de plante"""
    WATERING_SETTINGS: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            'tomate': {
                'watering_duration': 30,  # secondes
                'daily_max_water': 2.0,   # litres
                'schedule': ['06:00', '18:00'],
                'soil_type': 'argileux'
            },
            'salade': {
                'watering_duration': 20,
                'daily_max_water': 1.5,
                'schedule': ['07:00', '19:00'],
                'soil_type': 'limoneux'
            },
            'basilic': {
                'watering_duration': 15,
                'daily_max_water': 1.0,
                'schedule': ['08:00', '20:00'],
                'soil_type': 'sableux'
            },
        }
    )

@dataclass
class SystemConfig:
    """Configuration système"""
    # Intervalles
    SENSOR_READ_INTERVAL: int = 60           # secondes
    DECISION_INTERVAL: int = 300             # secondes (5 min)
    DATA_SAVE_INTERVAL: int = 600            # secondes (10 min)
    WATERING_COOLDOWN: int = 1800            # secondes (30 min)
    
    # Base de données
    DB_PATH: str = "/home/pi/irrigation_data.db"
    LOG_PATH: str = "/home/pi/irrigation_logs/"
    MAX_LOG_DAYS: int = 30
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5000
    API_DEBUG: bool = True
    
    # Sécurité
    MAX_WATER_PER_DAY: float = 10.0          # litres maximum par jour
    EMERGENCY_SHUTOFF: bool = True
    MAX_PUMP_RUNTIME: int = 300              # secondes (5 min max continu)

@dataclass
class Config:
    """Configuration complète"""
    gpio: GPIOConfig = GPIOConfig()
    thresholds: SensorThresholds = SensorThresholds()
    plants: PlantConfig = PlantConfig()
    system: SystemConfig = SystemConfig()
    
    @classmethod
    def from_json(cls, filepath: str):
        """Charger la configuration depuis un fichier JSON"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            return cls(**data)
        return cls()

# Instance globale de configuration
config = Config()