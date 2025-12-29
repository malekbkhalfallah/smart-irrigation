# core/actuators/status_led.py
import threading
import time
from core.utils.gpio_manager import gpio_manager


class StatusLED:
    def __init__(self, pin: int):
        self.pin = pin
        self._device = gpio_manager.setup_output(pin)
        self._stop_event = threading.Event()

    def on(self):
        gpio_manager.write(self.pin, True, self._device)

    def off(self):
        gpio_manager.write(self.pin, False, self._device)

    def blink(self, interval: float):
        def loop():
            while not self._stop_event.is_set():
                self.on()
                time.sleep(interval)
                self.off()
                time.sleep(interval)

        self._stop_event.clear()
        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self._stop_event.set()
        self.off()
