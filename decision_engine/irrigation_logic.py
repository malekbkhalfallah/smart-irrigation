"""
Logique de décision pour l'irrigation
"""
import time
import logging
from typing import Dict, Any, Optional, Tuple
from config.settings import config
from core.database import database
from core.weather_api import weather_api
from sensors.sensor_manager import sensor_manager
from actuators.water_pump import water_pump

logger = logging.getLogger(__name__)

class IrrigationLogic:
    """Logique intelligente de décision pour l'irrigation"""
    
    def __init__(self):
        self.last_decision_time = 0
        self.last_irrigation_time = 0
        
    def make_decision(self, sensor_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Prend la décision d'irriguer ou non
        Returns: (should_irrigate, reason)
        """
        # Extraire les données des capteurs
        sensors = sensor_data.get("sensors", {})
        
        dht22_data = sensors.get("dht22", {})
        soil_data = sensors.get("soil", {})
        rain_data = sensors.get("rain", {})
        water_data = sensors.get("water_level", {})
        
        # 1. Vérifier les données minimales
        if not all([dht22_data, soil_data, rain_data, water_data]):
            logger.warning("Données capteurs incomplètes")
            return False, "Données capteurs incomplètes"
        
        # 2. Vérifier le niveau d'eau dans le réservoir
        water_percent = water_data.get("water_percent", 0)
        if water_percent < config.irrigation.MIN_WATER_LEVEL:
            logger.warning(f"Niveau d'eau trop bas: {water_percent}%")
            return False, f"Niveau d'eau trop bas ({water_percent}%)"
        
        # 3. Vérifier l'humidité du sol
        soil_moisture = soil_data.get("moisture_percent", 50)
        
        # Si le sol est suffisamment humide, pas besoin d'irriguer
        if soil_moisture >= config.plant.min_moisture:
            logger.info(f"Sol suffisamment humide: {soil_moisture}%")
            return False, f"Sol suffisamment humide ({soil_moisture}%)"
        
        # 4. Vérifier si le sol est trop sec (en dessous du minimum)
        if soil_moisture < config.plant.min_moisture:
            logger.info(f"Sol trop sec: {soil_moisture}% < {config.plant.min_moisture}%")
            
            # 5. Vérifier la pluie actuelle
            if rain_data.get("rain_detected", False):
                logger.info("Pluie détectée - irrigation annulée")
                return False, "Pluie actuellement détectée"
            
            # 6. Vérifier la température de l'air
            temperature = dht22_data.get("temperature", 20)
            if temperature < config.irrigation.MIN_TEMP_FOR_IRRIGATION:
                logger.info(f"Température trop basse: {temperature}°C")
                return False, f"Température trop basse ({temperature}°C)"
            
            if temperature > config.irrigation.MAX_TEMP_FOR_IRRIGATION:
                logger.info(f"Température trop élevée: {temperature}°C")
                return False, f"Température trop élevée ({temperature}°C)"
            
            # 7. Vérifier l'humidité de l'air
            air_humidity = dht22_data.get("humidity", 50)
            if air_humidity > config.irrigation.MAX_AIR_HUMIDITY:
                logger.info(f"Humidité air trop élevée: {air_humidity}%")
                return False, f"Humidité air trop élevée ({air_humidity}%)"
            
            # 8. Vérifier les prévisions météo (si en ligne)
            if not config.offline_mode:
                if not weather_api.should_irrigate_based_on_weather():
                    return False, "Prévisions météo défavorables"
            
            # 9. Vérifier la limite d'irrigation quotidienne
            today_irrigation = database.get_today_irrigation_time()
            if today_irrigation >= config.irrigation.MAX_IRRIGATION_PER_DAY:
                logger.warning(f"Limite quotidienne atteinte: {today_irrigation}s")
                return False, f"Limite quotidienne atteinte ({today_irrigation}s)"
            
            # 10. Vérifier le temps depuis la dernière irrigation
            current_time = time.time()
            if current_time - self.last_irrigation_time < 3600:  # 1 heure
                logger.info("Trop peu de temps depuis la dernière irrigation")
                return False, "Attendre 1 heure entre les irrigations"
            
            # Toutes les conditions sont remplies !
            logger.info(f"✅ Irrigation recommandée - Sol: {soil_moisture}%")
            return True, f"Sol trop sec ({soil_moisture}%)"
        
        return False, "Condition non spécifiée"
    
    def execute_decision(self, should_irrigate: bool, reason: str) -> bool:
        """Exécute la décision prise"""
        if not should_irrigate:
            return False
        
        try:
            logger.info(f"Démarrage irrigation - Raison: {reason}")
            
            # Démarrer la pompe
            success = water_pump.start(config.irrigation.IRRIGATION_DURATION)
            
            if success:
                self.last_irrigation_time = time.time()
                
                # Loguer l'irrigation
                database.log_irrigation(
                    duration=config.irrigation.IRRIGATION_DURATION,
                    reason=reason,
                    triggered_by="auto",
                    success=True
                )
                
                # Loguer l'événement système
                database.log_system_event(
                    event_type="IRRIGATION",
                    message=f"Irrigation auto: {reason}"
                )
                
                logger.info("✅ Irrigation terminée avec succès")
                return True
            else:
                logger.error("Échec du démarrage de la pompe")
                database.log_irrigation(
                    duration=0,
                    reason=reason,
                    triggered_by="auto",
                    success=False
                )
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'irrigation: {e}")
            database.log_system_event(
                event_type="ERROR",
                message=f"Erreur irrigation: {str(e)}"
            )
            return False
    
    def manual_irrigation(self) -> bool:
        """Lance une irrigation manuelle"""
        try:
            logger.info("🚰 Irrigation manuelle demandée")
            
            # Vérifier le niveau d'eau
            water_status = sensor_manager.sensors['water_level'].read_safe()
            if water_status and water_status.get('water_percent', 0) < config.irrigation.MIN_WATER_LEVEL:
                logger.warning("Niveau d'eau insuffisant pour irrigation manuelle")
                return False
            
            # Démarrer l'irrigation
            success = water_pump.start(config.irrigation.IRRIGATION_DURATION)
            
            if success:
                self.last_irrigation_time = time.time()
                
                database.log_irrigation(
                    duration=config.irrigation.IRRIGATION_DURATION,
                    reason="Manuel",
                    triggered_by="manual",
                    success=True
                )
                
                logger.info("✅ Irrigation manuelle terminée")
                return True
            else:
                logger.error("Échec irrigation manuelle")
                return False
                
        except Exception as e:
            logger.error(f"Erreur irrigation manuelle: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du système"""
        sensor_status = sensor_manager.get_sensor_status()
        pump_status = water_pump.get_status()
        
        return {
            "timestamp": time.time(),
            "plant": {
                "name": config.plant.name,
                "min_moisture": config.plant.min_moisture,
                "max_moisture": config.plant.max_moisture
            },
            "system": {
                "offline_mode": config.offline_mode,
                "today_irrigation": database.get_today_irrigation_time(),
                "last_irrigation": self.last_irrigation_time
            },
            "sensors": sensor_status,
            "pump": pump_status
        }

# Instance globale
irrigation_logic = IrrigationLogic()