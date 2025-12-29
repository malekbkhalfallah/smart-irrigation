# core/sensors/base_sensor.py
"""
Classe de base pour tous les capteurs
Gère la configuration, la lecture sécurisée et les erreurs
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseSensor(ABC):
    """Classe abstraite pour tous les capteurs"""

    def __init__(self, name: str, pin: int):
        self.name = name
        self.pin = pin

        self._is_setup = False
        self.enabled = True

        # Diagnostic
        self.last_value: Optional[Any] = None
        self.last_error_time: Optional[float] = None

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def read(self) -> Any:
        pass

    @abstractmethod
    def cleanup(self):
        pass

    def read_safe(self) -> Optional[Any]:
        if not self.enabled:
            logger.warning(f"Capteur désactivé : {self.name}")
            return None

        try:
            if not self._is_setup:
                self.setup()
                self._is_setup = True

            value = self.read()
            self.last_value = value
            return value

        except Exception as e:
            self.last_error_time = time.time()
            logger.error(f"Erreur capteur {self.name} (GPIO {self.pin}) : {e}")
            return None

    def reset(self):
        self._is_setup = False
        self.last_value = None
        self.last_error_time = None
