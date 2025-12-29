# core/utils/gpio_manager.py

import logging

logger = logging.getLogger(__name__)


class GPIOManager:
    """
    Gestionnaire GPIO robuste
    - gpiozero (sans pigpio)
    - RPi.GPIO
    - simulation
    """

    def __init__(self):
        self.backend = None
        self.OutputDevice = None
        self.InputDevice = None
        self.GPIO = None

        self._init_backend()

    def _init_backend(self):
        # 1️⃣ gpiozero SANS pigpio
        try:
            from gpiozero import OutputDevice, InputDevice

            self.OutputDevice = OutputDevice
            self.InputDevice = InputDevice
            self.backend = "gpiozero"

            logger.info("GPIO backend: gpiozero (sans pigpio)")
            return

        except Exception as e:
            logger.warning(f"gpiozero indisponible → {e}")

        # 2️⃣ RPi.GPIO
        try:
            import RPi.GPIO as GPIO

            GPIO.setmode(GPIO.BCM)
            self.GPIO = GPIO
            self.backend = "RPi.GPIO"

            logger.info("GPIO backend: RPi.GPIO")
            return

        except Exception as e:
            logger.warning(f"RPi.GPIO indisponible → {e}")

        # 3️⃣ Simulation
        self.backend = "SIMULATION"
        logger.warning("GPIO backend: SIMULATION")

    # ==============================
    # GPIO API
    # ==============================

    def setup_output(self, pin: int):
        if self.backend == "gpiozero":
            return self.OutputDevice(pin)
        if self.backend == "RPi.GPIO":
            self.GPIO.setup(pin, self.GPIO.OUT)
        return None

    def setup_input(self, pin: int, pull_up: bool = True):
        if self.backend == "gpiozero":
            return self.InputDevice(pin)
        if self.backend == "RPi.GPIO":
            pud = self.GPIO.PUD_UP if pull_up else self.GPIO.PUD_DOWN
            self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=pud)
        return None

    def write(self, pin: int, value: bool, device=None):
        if self.backend == "gpiozero" and device:
            device.on() if value else device.off()
        elif self.backend == "RPi.GPIO":
            self.GPIO.output(pin, value)

    def read(self, pin: int, device=None) -> bool:
        if self.backend == "gpiozero" and device:
            return bool(device.value)
        elif self.backend == "RPi.GPIO":
            return bool(self.GPIO.input(pin))
        return False

    def cleanup(self):
        if self.backend == "RPi.GPIO":
            self.GPIO.cleanup()
        logger.info("GPIO cleanup done")


# Instance globale
gpio_manager = GPIOManager()
