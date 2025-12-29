# core/decision_engine/system_state.py

import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SystemState:
    """
    État global du système d'irrigation
    Source de vérité unique
    """

    def __init__(self):
        # =============================
        # Horodatage
        # =============================
        self.last_update: float = time.time()

        # =============================
        # Capteurs
        # =============================
        self.sensors: Dict[str, Optional[float]] = {
            "soil_moisture": None,
            "temperature": None,
            "humidity": None,
            "rain_detected": None,
            "water_level": None,
        }

        # =============================
        # Actionneurs
        # =============================
        self.actuators: Dict[str, bool] = {
            "pump_active": False,
        }

        # =============================
        # États système
        # =============================
        self.system_status: str = "IDLE"
        self.error: Optional[str] = None
        self.warning: Optional[str] = None

        # =============================
        # Historique léger (API / DB)
        # =============================
        self.history: list[dict] = []

    # ==================================================
    # Mise à jour capteurs
    # ==================================================

    def update_sensor(self, name: str, value):
        self.sensors[name] = value
        self.last_update = time.time()

        logger.debug(f"Sensor update: {name} = {value}")

    # ==================================================
    # Mise à jour actionneurs
    # ==================================================

    def update_actuator(self, name: str, state: bool):
        self.actuators[name] = state
        self.last_update = time.time()

        logger.debug(f"Actuator update: {name} = {state}")

    # ==================================================
    # Gestion états système
    # ==================================================

    def set_status(self, status: str):
        self.system_status = status
        logger.info(f"System status: {status}")

    def set_error(self, message: str):
        self.error = message
        self.system_status = "ERROR"
        logger.error(message)

    def clear_error(self):
        self.error = None

    def set_warning(self, message: str):
        self.warning = message
        logger.warning(message)

    def clear_warning(self):
        self.warning = None

    # ==================================================
    # Historique (light)
    # ==================================================

    def snapshot(self):
        """
        Capture un snapshot exploitable par BD / API
        """
        snap = {
            "timestamp": time.time(),
            "sensors": self.sensors.copy(),
            "actuators": self.actuators.copy(),
            "status": self.system_status,
            "error": self.error,
            "warning": self.warning,
        }

        self.history.append(snap)

        # Limite mémoire
        if len(self.history) > 1000:
            self.history.pop(0)

        return snap

    # ==================================================
    # Helpers
    # ==================================================

    def is_raining(self) -> bool:
        return bool(self.sensors.get("rain_detected"))

    def soil_is_dry(self, threshold: float) -> bool:
        moisture = self.sensors.get("soil_moisture")
        return moisture is not None and moisture < threshold

    def water_is_low(self, threshold: float = 30.0) -> bool:
        level = self.sensors.get("water_level")
        return level is not None and level < threshold
