# core/decision_engine/main_controller.py

import time
import logging
from typing import Dict

from core.decision_engine.system_state import SystemState
from core.decision_engine.irrigation_logic import (
    IrrigationLogic,
    PlantProfile,
    IrrigationSettings,
)

from core.sensors.base_sensor import BaseSensor
from core.actuators.water_pump import RelayWaterPump
from core.actuators.status_led import StatusLED

logger = logging.getLogger(__name__)


class MainController:
    """
    Orchestrateur principal du système d’irrigation
    """

    def __init__(
        self,
        sensors: Dict[str, BaseSensor],
        pump: RelayWaterPump,
        status_led: StatusLED,
        plant_profile: PlantProfile,
        settings: IrrigationSettings,
        loop_interval: float = 5.0,
    ):
        self.sensors = sensors
        self.pump = pump
        self.status_led = status_led
        self.loop_interval = loop_interval

        self.system_state = SystemState()
        self.logic = IrrigationLogic(
            system_state=self.system_state,
            plant=plant_profile,
            settings=settings,
        )

        self.running = False

    # ==================================================
    # BOUCLE PRINCIPALE
    # ==================================================

    def run(self):
        logger.info("Démarrage du système d’irrigation")
        self.running = True
        self.status_led.set_state("IDLE")

        try:
            while self.running:
                self._update_sensors()
                decision = self.logic.evaluate()
                self._apply_decision(decision)

                time.sleep(self.loop_interval)

        except KeyboardInterrupt:
            logger.info("Arrêt manuel du système")

        except Exception as e:
            logger.critical(f"ERREUR CRITIQUE: {e}", exc_info=True)
            self.status_led.set_state("ERROR")

        finally:
            self.shutdown()

    # ==================================================
    # MISE À JOUR CAPTEURS
    # ==================================================

    def _update_sensors(self):
        for name, sensor in self.sensors.items():
            value = sensor.read_safe()
            self.system_state.update_sensor(name, value)

        logger.debug(f"État système: {self.system_state.sensors}")

    # ==================================================
    # APPLICATION DÉCISION
    # ==================================================

    def _apply_decision(self, decision):
        if decision.should_irrigate:
            self.status_led.set_state("ACTIVE")

            if not self.pump.is_active():
                self.pump.run_for(decision.duration)
                self.logic.notify_irrigation_done(decision.duration)

            self.status_led.set_state("IDLE")

        else:
            self._handle_non_irrigation(decision.reason)

    # ==================================================
    # GESTION DES ÉTATS LED
    # ==================================================

    def _handle_non_irrigation(self, reason: str):
        if reason == "RAIN_DETECTED":
            self.status_led.set_state("RAINING")

        elif reason in ("LOW_WATER_LEVEL", "DAILY_LIMIT_REACHED"):
            self.status_led.set_state("WARNING")

        else:
            self.status_led.set_state("IDLE")

    # ==================================================
    # ARRÊT PROPRE
    # ==================================================

    def shutdown(self):
        logger.info("Extinction du système")

        self.running = False
        self.pump.cleanup()

        for sensor in self.sensors.values():
            try:
                sensor.cleanup()
            except Exception:
                pass

        self.status_led.cleanup()
        logger.info("Système arrêté proprement")
