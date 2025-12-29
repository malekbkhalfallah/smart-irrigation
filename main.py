"""
Système d'Irrigation Intelligent - Version avec Firebase (adapté à ta structure)
"""
import time
import logging
from datetime import datetime
from core.database import db_manager
from firebase_config import firebase_manager

# Import de tes modules existants
from sensors.sensor_manager import sensor_manager
from decision_engine.irrigation_logic import irrigation_logic
from actuators.water_pump import water_pump
from config.settings import config

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Fonction principale adaptée à ta structure"""
    logger.info("🚀 Démarrage du système d'irrigation intelligent")
    logger.info(f"📊 Structure détectée: capteurs réels, pompe GPIO, Firebase")
    
    # Afficher l'état Firebase
    if firebase_manager.connected:
        logger.info("✅ Firebase connecté - Synchronisation cloud activée")
    else:
        logger.info("ℹ️ Firebase non connecté - Mode local seulement")
    
    # Boucle principale
    try:
        while True:
            # Lire les capteurs (méthode existante de ton système)
            sensor_data = sensor_manager.read_all()
            
            if sensor_data["success"]:
                logger.info(f"📊 Capteurs: {sensor_data['sensors']}")
                
                # Sauvegarder localement (via ton db_manager)
                db_manager.save_sensor_reading(sensor_data)
                
                # Sauvegarder dans Firebase si connecté
                if firebase_manager.connected:
                    firebase_manager.save_sensor_data(sensor_data)
                
                # Prendre une décision d'irrigation (via ta logique existante)
                should_irrigate, reason = irrigation_logic.make_decision(sensor_data)
                
                if should_irrigate:
                    logger.info(f"💧 Irrigation nécessaire: {reason}")
                    
                    # Exécuter l'irrigation via ta logique existante
                    success = irrigation_logic.execute_decision(should_irrigate, reason)
                    
                    if success:
                        # Récupérer la durée depuis ta config
                        duration = config.irrigation.IRRIGATION_DURATION
                        
                        # Sauvegarder dans Firebase
                        if firebase_manager.connected:
                            firebase_manager.save_irrigation_event(
                                duration=duration,
                                reason=reason,
                                triggered_by="auto"
                            )
            
            # Sauvegarder le statut système
            system_status = {
                "status": "running",
                "last_sensor_read": datetime.now(),
                "firebase_connected": firebase_manager.connected,
                "sensor_success": sensor_data.get("success", False),
                "plant": config.plant.name,
                "mode": "online" if not config.offline_mode else "offline"
            }
            
            # Sauvegarder le statut (ta db_manager le fera aussi dans Firebase)
            db_manager.save_system_status(system_status)
            
            # Attendre avant prochaine lecture (utilise ton intervalle de config)
            logger.info(f"⏳ Prochaine vérification dans {config.irrigation.CHECK_INTERVAL} secondes...")
            time.sleep(config.irrigation.CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
    finally:
        # Nettoyage
        water_pump.cleanup()
        sensor_manager.cleanup()
        logger.info("👋 Système arrêté proprement")

def test_system():
    """Teste tous les composants"""
    logger.info("🧪 TEST SYSTÈME COMPLET")
    
    # Test Firebase
    fb_status = db_manager.get_firebase_status()
    logger.info(f"Firebase: {'✅ Connecté' if fb_status.get('connected') else '❌ Non connecté'}")
    
    # Test capteurs
    sensor_data = sensor_manager.read_all()
    logger.info(f"Capteurs: {'✅ OK' if sensor_data['success'] else '❌ Erreur'}")
    
    # Test pompe
    pump_status = water_pump.get_status()
    logger.info(f"Pompe: {pump_status}")
    
    # Test configuration
    logger.info(f"Plante: {config.plant.name}")
    logger.info(f"Mode: {'online' if not config.offline_mode else 'offline'}")
    
    return all([
        sensor_data["success"],
        fb_status.get("connected", False) or True,  # Firebase optionnel
        pump_status is not None
    ])

if __name__ == "__main__":
    # Tester le système d'abord
    if test_system():
        logger.info("✅ Tous les tests passés - Démarrage du système")
        main()
    else:
        logger.error("❌ Tests échoués - Vérifie la configuration")