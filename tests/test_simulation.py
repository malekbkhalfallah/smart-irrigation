import time
import logging

from core.sensors.dht22 import DHT22Sensor
from core.sensors.raindrop import RaindropSensor
from core.sensors.water_level import WaterLevelSensor
from core.actuators.water_pump import RelayWaterPump
from core.actuators.status_led import StatusLED
from core.decision_engine.irrigation_logic import IrrigationLogic
from core.controllers.system_state import SystemState

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# --------------------------------------------------
# INITIALISATION SIMULATION
# --------------------------------------------------
print("\n=== DÉMARRAGE TEST SIMULATION ===\n")

# Capteurs
dht22 = DHT22Sensor(pin=4)
rain = RaindropSensor(digital_pin=17)
water_level = WaterLevelSensor(pin=27)

# Actionneurs
pump = RelayWaterPump(relay_pin=22)
status_led = StatusLED(led_pin=5)

# État système
system_state = SystemState()

# Logique irrigation
logic = IrrigationLogic(
    dht_sensor=dht22,
    rain_sensor=rain,
    water_level_sensor=water_level,
    pump=pump,
    status_led=status_led,
    system_state=system_state
)

# --------------------------------------------------
# BOUCLE DE TEST
# --------------------------------------------------
try:
    for cycle in range(5):
        print(f"\n--- CYCLE {cycle + 1} ---")
        logic.run_cycle()
        time.sleep(3)

except KeyboardInterrupt:
    print("Arrêt manuel")

finally:
    print("\nNettoyage ressources")
    pump.cleanup()
    status_led.cleanup()
