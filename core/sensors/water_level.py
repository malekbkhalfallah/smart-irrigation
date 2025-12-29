# core/sensors/water_level.py
from core.sensors.base_sensor import BaseSensor
from core.utils.gpio_manager import gpio_manager


class WaterLevelSensor(BaseSensor):
    """Capteur de niveau d'eau"""

    def __init__(self, pin: int):
        super().__init__("Water Level", pin)
        self._device = None

    def setup(self):
        self._device = gpio_manager.setup_input(self.pin)

    def read(self) -> float:
        raw = gpio_manager.read(self.pin, self._device)
        return 20.0 if raw else 80.0

    def cleanup(self):
        pass
