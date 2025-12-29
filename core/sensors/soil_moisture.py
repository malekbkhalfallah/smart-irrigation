# core/sensors/soil_moisture.py
import time
from core.sensors.base_sensor import BaseSensor
from core.utils.gpio_manager import gpio_manager


class SoilMoistureSensor(BaseSensor):
    """Capteur d'humidité du sol (capacitif ou digital)"""

    def __init__(self, pin: int):
        super().__init__("Soil Moisture", pin)
        self._device = None
        self._last_read_time = 0
        self._interval = 2

    def setup(self):
        self._device = gpio_manager.setup_input(self.pin, pull_up=False)

    def read(self) -> float:
        now = time.time()
        if now - self._last_read_time < self._interval:
            return self.last_value

        raw = gpio_manager.read(self.pin, self._device)

        # Mapping simple (à adapter si ADC)
        moisture = 30.0 if raw else 70.0
        moisture = max(0.0, min(100.0, moisture))

        self._last_read_time = now
        return moisture

    def cleanup(self):
        pass
