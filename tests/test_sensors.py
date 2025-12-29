from core.sensors.soil_moisture import SoilMoistureSensor
from core.sensors.dht22 import DHT22Sensor
from core.sensors.raindrop import RaindropSensor
from core.sensors.water_level import WaterLevelSensor

def test_sensors():
    sensors = [
        SoilMoistureSensor(pin=17),
        DHT22Sensor(pin=27),
        RaindropSensor(digital_pin=22),
        WaterLevelSensor(pin=23),
    ]

    for s in sensors:
        print(f"{s.name}:", s.read_safe())

if __name__ == "__main__":
    test_sensors()
