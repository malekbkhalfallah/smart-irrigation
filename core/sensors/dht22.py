# core/sensors/dht22.py
import time
import random
from core.sensors.base_sensor import BaseSensor

try:
    import Adafruit_DHT
except ImportError:
    Adafruit_DHT = None


class DHT22Sensor(BaseSensor):
    """Capteur température / humidité air"""

    def __init__(self, pin: int):
        super().__init__("DHT22", pin)
        self._last_read_time = 0
        self._interval = 2

    def setup(self):
        pass

    def read(self):
        now = time.time()
        if now - self._last_read_time < self._interval:
            return self.last_value

        if Adafruit_DHT:
            h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
        else:
            t = 20 + random.uniform(-2, 2)
            h = 50 + random.uniform(-10, 10)

        if t is not None and h is not None:
            self._last_read_time = now
            return round(t, 1), round(h, 1)

        return self.last_value

    def cleanup(self):
        pass
