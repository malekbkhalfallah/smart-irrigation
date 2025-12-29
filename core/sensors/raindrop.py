# core/sensors/raindrop.py
from core.sensors.base_sensor import BaseSensor
from core.utils.gpio_manager import gpio_manager


class RaindropSensor(BaseSensor):
    """Détection de pluie"""

    def __init__(self, pin: int):
        super().__init__("Rain Sensor", pin)
        self._device = None

    def setup(self):
        self._device = gpio_manager.setup_input(self.pin)

    def read(self) -> bool:
        # LOW = pluie pour la majorité des modules
        return not gpio_manager.read(self.pin, self._device)

    def cleanup(self):
        pass
