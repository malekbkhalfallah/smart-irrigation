# Configuration des broches GPIO
class GPIOPins:
    # Capteurs
    DHT22_PIN = 4
    SOIL_MOISTURE_PIN = 17
    RAIN_SENSOR_PIN = 27
    WATER_LEVEL_PIN = 22
    
    # Actionneurs
    WATER_PUMP_RELAY_PIN = 18

# Paramètres d'irrigation
class IrrigationSettings:
    SOIL_MOISTURE_THRESHOLD = 30
    CHECK_INTERVAL = 300
    WATERING_DURATION = 10