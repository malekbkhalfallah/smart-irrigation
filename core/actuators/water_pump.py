# core/actuators/water_pump.py
import time
from core.utils.gpio_manager import gpio_manager


class RelayWaterPump:
    """Pompe via relais"""

    def __init__(self, pin: int):
        self.pin = pin
        self._device = gpio_manager.setup_output(pin)
        self._active = False
        self._start_time = None

    def turn_on(self):
        gpio_manager.write(self.pin, False, self._device)
        self._active = True
        self._start_time = time.time()

    def turn_off(self):
        gpio_manager.write(self.pin, True, self._device)
        self._active = False
        self._start_time = None

    def is_active(self) -> bool:
        return self._active
