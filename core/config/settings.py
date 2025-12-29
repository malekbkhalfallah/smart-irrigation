import json
# Module pour lire/écrire des fichiers JSON
# Permet de sauvegarder/charger la configuration

import os
# Module pour interagir avec le système d'exploitation


from dataclasses import dataclass, field
# dataclass: Crée automatiquement des classes avec méthodes spéciales
# field: Permet de configurer des champs spécifiques dans dataclass

from pathlib import Path
# Module moderne pour manipuler les chemins de fichiers


# =========================
# CONFIGURATION GPIO
# =========================

@dataclass   # Décorateur qui transforme cette classe en "dataclass"
class GPIOConfig:
    """Configuration des broches GPIO"""

    # Capteurs
    SOIL_MOISTURE_PIN: int = 24       # GPIO24
    DHT22_PIN: int = 17               # GPIO17
    RAINDROP_DIGITAL_PIN: int = 27    # GPIO27
    WATER_LEVEL_PIN: int = 23         # GPIO23

    # Actionneurs
    PUMP_RELAY_PIN: int = 26          # GPIO26
    STATUS_LED_PIN: int = 16          # GPIO16


# =========================
# CONFIGURATION IRRIGATION
# =========================

@dataclass
class IrrigationConfig:
    """Configuration des règles d'irrigation"""

    # Intervalles (secondes)
    SENSOR_READ_INTERVAL: int = 30
    DECISION_INTERVAL: int = 120

    # Humidité du sol (%)
    # - Si < DRY → besoin d'irrigation
    # - Si > WET → arrêt irrigation
    SOIL_DRY_THRESHOLD: int = 40
    SOIL_WET_THRESHOLD: int = 80

    # Niveau d'eau du réservoir (%)
    WATER_LEVEL_ALERT: int = 20       # En dessous → alerte + pas d'irrigation

    # Température de l'air (°C)
    MIN_TEMP_FOR_IRRIGATION: int = 5
    MAX_TEMP_FOR_IRRIGATION: int = 35

    # Humidité de l'air (%)
    MAX_AIR_HUMIDITY_FOR_IRRIGATION: int = 85  # Trop humide → pas d'irrigation

    # Prévision météo
    RAIN_FORECAST_WINDOW_DAYS: int = 2  # Jours à regarder pour pluie prévue

    # Durées d'irrigation (secondes)
    MIN_IRRIGATION_TIME: int = 5
    BASE_IRRIGATION_TIME: int = 10
    MAX_IRRIGATION_TIME: int = 60


# =========================
# CONFIGURATION GÉNÉRALE
# =========================

@dataclass
class SystemConfig:
    """Configuration générale du système"""

    gpio: GPIOConfig = field(default_factory=GPIOConfig)
    irrigation: IrrigationConfig = field(default_factory=IrrigationConfig)

    # Chemins
    DATA_DIR: Path = Path("data")
    LOG_DIR: Path = Path("logs")
    DB_PATH: Path = Path("data/irrigation.db")

    # Valeurs par défaut
    DEFAULT_PLANT_TYPE: str = "tomato"
    DEFAULT_SOIL_TYPE: str = "loam"

    def __post_init__(self):
        """Créer les répertoires nécessaires"""
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOG_DIR.mkdir(exist_ok=True)


# =========================
# INSTANCE GLOBALE
# =========================

config = SystemConfig()


# =========================
# SAUVEGARDE / CHARGEMENT
# =========================

def save_config(path: Path = Path("config/system_config.json")):
    """Sauvegarde la configuration dans un fichier JSON"""
    config_dict = {
        "gpio": config.gpio.__dict__,
        "irrigation": config.irrigation.__dict__,
        "DEFAULT_PLANT_TYPE": config.DEFAULT_PLANT_TYPE,
        "DEFAULT_SOIL_TYPE": config.DEFAULT_SOIL_TYPE
    }

    path.parent.mkdir(exist_ok=True)

    with open(path, "w") as f:
        json.dump(config_dict, f, indent=4)

    print(f"[CONFIG] Configuration sauvegardée dans {path}")


def load_config(path: Path = Path("config/system_config.json")):
    """Charge la configuration depuis un fichier JSON"""
    if not path.exists():
        print("[CONFIG] Aucun fichier de configuration trouvé, valeurs par défaut utilisées")
        return

    try:
        with open(path, "r") as f:
            config_dict = json.load(f)

        config.gpio = GPIOConfig(**config_dict.get("gpio", {}))
        config.irrigation = IrrigationConfig(**config_dict.get("irrigation", {}))
        config.DEFAULT_PLANT_TYPE = config_dict.get("DEFAULT_PLANT_TYPE", "tomato")
        config.DEFAULT_SOIL_TYPE = config_dict.get("DEFAULT_SOIL_TYPE", "loam")

        print(f"[CONFIG] Configuration chargée depuis {path}")

    except Exception as e:
        print(f"[CONFIG] Erreur chargement configuration : {e}")
        print("[CONFIG] Utilisation des paramètres par défaut")
