import time
import logging
from core.gpio_manager import gpio_manager

logger = logging.getLogger(__name__)


class StatusLED:
    """
    LED d'état du système

    États supportés :
    - IDLE        : LED éteinte
    - IRRIGATING : LED allumée fixe
    - ERROR      : clignotement rapide
    """

    def __init__(self, pin: int):
        self.pin = pin
        gpio_manager.setup_output(self.pin)
        self._state = "IDLE"

    def set_state(self, state: str):
        state = state.upper()

        if state == self._state:
            return

        self._state = state
        logger.info(f"LED 상태 → {state}")

        if state == "IDLE":
            self._off()

        elif state == "IRRIGATING":
            self._on()

        elif state == "ERROR":
            self._blink(times=5, interval=0.2)

        else:
            logger.warning(f"État LED inconnu: {state}")
            self._off()

    def _on(self):
        gpio_manager.write(self.pin, True)

    def _off(self):
        gpio_manager.write(self.pin, False)

    def _blink(self, times: int, interval: float):
        for _ in range(times):
            self._on()
            time.sleep(interval)
            self._off()
            time.sleep(interval)
