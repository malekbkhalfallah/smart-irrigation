# core/decision_engine/irrigation_logic.py

import time
import logging
from dataclasses import dataclass
from typing import Optional

from core.decision_engine.system_state import SystemState
from core.config.plant_profile import PlantProfile


logger = logging.getLogger(__name__)


# ==================================================
# PARAMÈTRES GLOBAUX
# ==================================================

@dataclass
class IrrigationSettings:
    irrigation_duration_sec: float
    min_interval_sec: float
    rain_lock: bool = True
    water_level_min: float = 25.0
    max_daily_irrigation: float = 300.0
    safety_timeout: float = 900.0

# ==================================================
# DÉCISION
# ==================================================

@dataclass
class IrrigationDecision:
    should_irrigate: bool
    duration: float = 0.0
    reason: str = "NONE"


# ==================================================
# LOGIQUE D’IRRIGATION
# ==================================================

class IrrigationLogic:
    """
    Cerveau décisionnel du système
    """

    def __init__(
        self,
        system_state: SystemState,
        plant: PlantProfile,
        settings: IrrigationSettings,
    ):
        self.state = system_state
        self.plant = plant
        self.settings = settings

        self.last_irrigation_time: Optional[float] = None
        self.daily_irrigation_time: float = 0.0
        self._day_start = time.time()

    # ==================================================
    # ÉVALUATION PRINCIPALE
    # ==================================================

    def evaluate(self) -> IrrigationDecision:
        """
        Évalue si l’irrigation doit être lancée
        """

        now = time.time()
        self._reset_daily_counter_if_needed(now)

        # =========================
        # SÉCURITÉS PRIORITAIRES
        # =========================

        if self.settings.rain_lock and self.state.is_raining():
            return self._deny("RAIN_DETECTED")

        if self.state.water_is_low(self.settings.water_level_min):
            return self._deny("LOW_WATER_LEVEL")

        if self.daily_irrigation_time >= self.settings.max_daily_irrigation:
            return self._deny("DAILY_LIMIT_REACHED")

        if self._irrigated_too_recently(now):
            return self._deny("MIN_INTERVAL")

        # =========================
        # LOGIQUE PLANTE
        # =========================

        soil = self.state.sensors.get("soil_moisture")
        if soil is None:
            return self._deny("NO_SOIL_DATA")

        if soil >= self.plant.optimal_moisture:
            return self._deny("SOIL_OK")

        if soil < self.plant.min_moisture:
            return self._allow("SOIL_TOO_DRY")

        return self._deny("WAITING")

    # ==================================================
    # AUTORISATION / REFUS
    # ==================================================

    def _allow(self, reason: str) -> IrrigationDecision:
        logger.info(f"Irrigation autorisée: {reason}")
        return IrrigationDecision(
            should_irrigate=True,
            duration=self.settings.irrigation_duration_sec,
            reason=reason,
        )

    def _deny(self, reason: str) -> IrrigationDecision:
        logger.debug(f"Irrigation refusée: {reason}")
        return IrrigationDecision(
            should_irrigate=False,
            reason=reason,
        )

    # ==================================================
    # UTILITAIRES
    # ==================================================

    def notify_irrigation_done(self, duration: float):
        """
        Appelée par le controller après irrigation
        """
        now = time.time()
        self.last_irrigation_time = now
        self.daily_irrigation_time += duration

        logger.info(
            f"Irrigation terminée ({duration}s, total jour: {self.daily_irrigation_time}s)"
        )

    def _irrigated_too_recently(self, now: float) -> bool:
        if self.last_irrigation_time is None:
            return False
        return (now - self.last_irrigation_time) < self.plant.min_interval_sec

    def _reset_daily_counter_if_needed(self, now: float):
        if now - self._day_start >= 86400:
            self.daily_irrigation_time = 0
            self._day_start = now
            logger.info("Compteur journalier réinitialisé")
