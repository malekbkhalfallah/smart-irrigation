"""
Logique de décision pour l'irrigation - VERSION FINALE
"""
import time
import logging
from typing import Dict, Any, Optional, Tuple
from config.settings import config
from core.database_manager import db_manager
from core.weather_api import weather_api
from sensors.sensor_manager import sensor_manager
from actuators.water_pump import water_pump
from actuators.status_led import status_led

logger = logging.getLogger(__name__)

class IrrigationLogic:
    """Logique intelligente de décision pour l'irrigation"""
    
    def __init__(self):
        self.last_decision_time = 0
        self.last_irrigation_time = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        logger.info("✅ Logique d'irrigation initialisée")
    
    def check_system_health(self) -> Tuple[bool, str]:
        """
        Vérifie la santé globale du système
        Returns: (système_sain, raison)
        """
        try:
            # Vérifier les capteurs
            health_report = sensor_manager.get_system_health_report()
            
            if not health_report['all_healthy']:
                failed_sensors = [name for name, status in health_report['sensors'].items() 
                                if not status['healthy']]
                error_msg = f"Capteurs défaillants: {', '.join(failed_sensors)}"
                
                # Enregistrer l'alerte
                db_manager.save_alert("SENSOR_ERROR", error_msg)
                
                return False, error_msg
            
            # Vérifier la pompe
            pump_status = water_pump.get_status()
            if pump_status.get('is_running', False):
                return False, "Pompe déjà en fonctionnement"
            
            return True, "Système sain"
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification santé: {e}")
            return False, f"Erreur système: {str(e)}"
    
    def analyze_sensor_data(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse les données des capteurs pour prise de décision
        """
        analysis = {
            "timestamp": time.time(),
            "can_irrigate": False,
            "reasons": [],
            "warnings": [],
            "errors": [],
            "sensor_values": {}
        }
        
        try:
            sensors = sensor_data.get("sensors", {})
            
            # 1. Humidité du sol
            soil_data = sensors.get("soil", {})
            if soil_data:
                moisture = soil_data.get("moisture_percent", 0)
                is_dry = soil_data.get("is_dry", True)
                
                analysis["sensor_values"]["soil_moisture"] = moisture
                analysis["sensor_values"]["soil_is_dry"] = is_dry
                
                # Mettre à jour la LED verte
                status_led.update_soil_status(moisture)
                
                if moisture < config.plant.min_moisture:
                    analysis["reasons"].append(f"Sol trop sec ({moisture}% < {config.plant.min_moisture}%)")
                    analysis["can_irrigate"] = True
                else:
                    analysis["reasons"].append(f"Humidité sol OK ({moisture}%)")
            
            # 2. Niveau d'eau
            water_data = sensors.get("water", {})
            if water_data:
                water_detected = water_data.get("water_detected", False)
                water_percent = water_data.get("water_percent", 0)
                
                analysis["sensor_values"]["water_level"] = water_percent
                analysis["sensor_values"]["water_detected"] = water_detected
                
                if not water_detected or water_percent < config.irrigation.MIN_WATER_LEVEL:
                    error_msg = f"Niveau d'eau insuffisant ({water_percent}%)"
                    analysis["errors"].append(error_msg)
                    analysis["can_irrigate"] = False
                    status_led.set_system_state("NO_WATER")
                    
                    # Enregistrer l'alerte
                    db_manager.save_alert("WATER_LOW", error_msg, "water")
                else:
                    analysis["reasons"].append(f"Niveau d'eau OK ({water_percent}%)")
            
            # 3. Pluie
            rain_data = sensors.get("rain", {})
            if rain_data:
                rain_detected = rain_data.get("rain_detected", False)
                
                analysis["sensor_values"]["rain_detected"] = rain_detected
                
                if rain_detected:
                    analysis["reasons"].append("Pluie détectée")
                    analysis["can_irrigate"] = False
            
            # 4. Température/humidité air
            dht22_data = sensors.get("dht22", {})
            if dht22_data:
                temperature = dht22_data.get("temperature")
                humidity = dht22_data.get("humidity")
                
                if temperature is not None:
                    analysis["sensor_values"]["temperature"] = temperature
                    if temperature < config.irrigation.MIN_TEMP_FOR_IRRIGATION:
                        analysis["reasons"].append(f"Température trop basse ({temperature}°C)")
                        analysis["can_irrigate"] = False
                    elif temperature > config.irrigation.MAX_TEMP_FOR_IRRIGATION:
                        analysis["reasons"].append(f"Température trop élevée ({temperature}°C)")
                        analysis["can_irrigate"] = False
                
                if humidity is not None:
                    analysis["sensor_values"]["humidity"] = humidity
                    if humidity > config.irrigation.MAX_AIR_HUMIDITY:
                        analysis["reasons"].append(f"Humidité air trop élevée ({humidity}%)")
                        analysis["can_irrigate"] = False
            
            # 5. Vérifier les limites quotidiennes
            today_irrigation = db_manager.get_today_irrigation_time()
            if today_irrigation >= config.irrigation.MAX_IRRIGATION_PER_DAY:
                analysis["reasons"].append(f"Limite quotidienne atteinte ({today_irrigation:.1f}s)")
                analysis["can_irrigate"] = False
            
            # 6. Vérifier l'intervalle depuis la dernière irrigation
            current_time = time.time()
            if current_time - self.last_irrigation_time < 3600:  # 1 heure
                analysis["reasons"].append("Attendre 1 heure entre les irrigations")
                analysis["can_irrigate"] = False
            
            # 7. Vérifier les prévisions météo si en ligne
            if not config.offline_mode and weather_api:
                should_irrigate = weather_api.should_irrigate_based_on_weather()
                if not should_irrigate:
                    analysis["reasons"].append("Prévisions météo défavorables")
                    analysis["can_irrigate"] = False
            
            # Décision finale
            if (analysis["can_irrigate"] and 
                not analysis["errors"] and
                analysis.get("sensor_values", {}).get("soil_moisture", 100) < config.plant.min_moisture):
                analysis["final_decision"] = "IRRIGATE"
            else:
                analysis["final_decision"] = "WAIT"
                
        except Exception as e:
            analysis["errors"].append(f"Erreur analyse: {str(e)}")
            analysis["can_irrigate"] = False
            analysis["final_decision"] = "ERROR"
            logger.error(f"❌ Erreur analyse données: {e}")
        
        return analysis
    
    def make_decision(self, sensor_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Prend la décision d'irriguer ou non
        Returns: (should_irrigate, reason, analysis)
        """
        try:
            # Vérifier la santé du système
            system_healthy, health_reason = self.check_system_health()
            if not system_healthy:
                status_led.set_system_state("ERROR")
                return False, f"Système défaillant: {health_reason}", {}
            
            # Analyser les données
            analysis = self.analyze_sensor_data(sensor_data)
            
            # Prendre la décision finale
            if analysis["final_decision"] == "IRRIGATE":
                if not analysis["errors"]:
                    reason = " + ".join(analysis["reasons"])
                    return True, reason, analysis
                else:
                    status_led.set_system_state("ERROR")
                    return False, f"Erreurs: {'; '.join(analysis['errors'])}", analysis
            else:
                if analysis["errors"]:
                    status_led.set_system_state("ERROR")
                    reason = f"Erreurs: {'; '.join(analysis['errors'])}"
                else:
                    reason = " | ".join(analysis["reasons"])
                return False, reason, analysis
                
        except Exception as e:
            logger.error(f"❌ Erreur prise de décision: {e}")
            status_led.set_system_state("ERROR")
            return False, f"Erreur système: {str(e)}", {}
    
    def execute_decision(self, should_irrigate: bool, reason: str, analysis: Dict[str, Any]) -> bool:
        """Exécute la décision prise"""
        if not should_irrigate:
            logger.info(f"⏸️ Pas d'irrigation: {reason}")
            return False
        
        try:
            logger.info(f"🚰 Démarrage irrigation - Raison: {reason}")
            
            # Mettre à jour les LEDs
            status_led.set_system_state("IRRIGATING")
            
            # Démarrer la pompe
            success = water_pump.start(config.irrigation.IRRIGATION_DURATION)
            
            if success:
                self.last_irrigation_time = time.time()
                self.consecutive_errors = 0
                
                # Sauvegarder l'événement
                db_manager.save_irrigation_event(
                    duration=config.irrigation.IRRIGATION_DURATION,
                    reason=reason,
                    triggered_by="auto",
                    success=True
                )
                
                # Revenir à l'état normal après irrigation
                soil_moisture = analysis.get("sensor_values", {}).get("soil_moisture", 0)
                status_led.set_system_state("IDLE", 
                    soil_ok=(soil_moisture >= config.plant.optimal_moisture),
                    online=not config.offline_mode
                )
                
                logger.info(f"✅ Irrigation terminée avec succès: {config.irrigation.IRRIGATION_DURATION}s")
                return True
            else:
                self.consecutive_errors += 1
                status_led.set_system_state("ERROR")
                
                db_manager.save_irrigation_event(
                    duration=0,
                    reason=reason,
                    triggered_by="auto",
                    success=False
                )
                
                logger.error("❌ Échec du démarrage de la pompe")
                return False
                
        except Exception as e:
            self.consecutive_errors += 1
            logger.error(f"❌ Erreur lors de l'irrigation: {e}")
            status_led.set_system_state("ERROR")
            return False
    
    def manual_irrigation(self) -> Tuple[bool, str]:
        """Lance une irrigation manuelle"""
        try:
            logger.info("🚰 Irrigation manuelle demandée")
            
            # Vérifier la santé du système
            system_healthy, health_reason = self.check_system_health()
            if not system_healthy:
                status_led.set_system_state("ERROR")
                return False, f"Système défaillant: {health_reason}"
            
            # Vérifier le niveau d'eau
            water_data = sensor_manager.read_sensor("water")
            if water_data and not water_data.get("water_detected", False):
                status_led.set_system_state("NO_WATER")
                return False, "Niveau d'eau insuffisant"
            
            # Mettre à jour les LEDs
            status_led.set_system_state("IRRIGATING")
            
            # Démarrer l'irrigation
            success = water_pump.start(config.irrigation.IRRIGATION_DURATION)
            
            if success:
                self.last_irrigation_time = time.time()
                
                db_manager.save_irrigation_event(
                    duration=config.irrigation.IRRIGATION_DURATION,
                    reason="Manuel",
                    triggered_by="manual",
                    success=True
                )
                
                # Revenir à l'état normal
                status_led.set_system_state("IDLE", online=not config.offline_mode)
                
                logger.info("✅ Irrigation manuelle terminée")
                return True, "Irrigation manuelle réussie"
            else:
                status_led.set_system_state("ERROR")
                return False, "Échec irrigation manuelle"
                
        except Exception as e:
            logger.error(f"❌ Erreur irrigation manuelle: {e}")
            status_led.set_system_state("ERROR")
            return False, f"Erreur: {str(e)}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du système"""
        sensor_status = sensor_manager.get_sensor_status()
        pump_status = water_pump.get_status()
        led_status = status_led.get_status()
        
        return {
            "timestamp": time.time(),
            "plant": {
                "name": config.plant.name,
                "min_moisture": config.plant.min_moisture,
                "optimal_moisture": config.plant.optimal_moisture,
                "max_moisture": config.plant.max_moisture
            },
            "system": {
                "offline_mode": config.offline_mode,
                "today_irrigation": db_manager.get_today_irrigation_time(),
                "last_irrigation": self.last_irrigation_time,
                "last_decision": self.last_decision_time,
                "consecutive_errors": self.consecutive_errors
            },
            "sensors": sensor_status,
            "pump": pump_status,
            "leds": led_status
        }

# Instance globale
irrigation_logic = IrrigationLogic()