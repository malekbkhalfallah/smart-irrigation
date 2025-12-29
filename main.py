# main.py

import os
os.environ['GPIO_SIMULATE'] = 'true'
import logging

from core.sensors.soil_moisture import SoilMoistureSensor
from core.sensors.dht22 import DHT22Sensor
from core.sensors.raindrop import RaindropSensor
from core.sensors.water_level import WaterLevelSensor

from core.actuators.water_pump import RelayWaterPump
from core.actuators.status_led import StatusLED

from core.decision_engine.main_controller import MainController
from core.decision_engine.irrigation_logic import IrrigationSettings
from core.config.plant_profile import PlantProfile
from core.config.system_config import SystemConfig


# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ==================================================
# CONFIGURATION
# ==================================================

def create_sensors():
    return {
        "soil_moisture": SoilMoistureSensor(pin=17),
        "air": DHT22Sensor(pin=27),
        "rain": RaindropSensor(pin=22),
        "water_level": WaterLevelSensor(pin=23),
    }


def create_actuators():
    pump = RelayWaterPump(pin=5)
    led = StatusLED(pin=6)
    return pump, led


def create_profiles():
    plant = PlantProfile(
        name="Tomate",
        soil_type="Loam",
        min_moisture=35,
        max_moisture=70,
        optimal_moisture=50,
    )

    settings = IrrigationSettings(
        irrigation_duration_sec=10,
        min_interval_sec=60,
        min_water_level=20,
        max_irrigations_per_day=3,
        enable_rain_skip=True,
    )

    return plant, settings



# ==================================================
# ENTRY POINT
# ==================================================

def main():
    sensors = create_sensors()
    pump, led = create_actuators()
    plant, settings = create_profiles()

    controller = MainController(
        sensors=sensors,
        pump=pump,
        status_led=led,
        plant_profile=plant,
        settings=settings,
        loop_interval=5.0,
    )

    controller.run()


if __name__ == "__main__":
    main()
