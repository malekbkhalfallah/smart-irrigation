#!/usr/bin/env python3
"""
SYSTÈME D'IRRIGATION INTELLIGENT - Point d'entrée principal hardware
Version finale avec gestion propre des threads et arrêt
"""
import time
import logging
import sys
import threading
from datetime import datetime

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('irrigation_system.log')
    ]
)

logger = logging.getLogger(__name__)

class IrrigationSystem:
    """Système d'irrigation intelligent principal"""
    
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.cleanup_count = 0
        self.cycle_thread = None
        
        # CORRECTION: S'assurer que GPIO ne se réinitialise pas
        try:
            # Cette importation va réutiliser l'instance GPIO existante
            from core.gpio_manager import gpio_central
            logger.info("✅ Utilisation de l'instance GPIO existante")
        except Exception as e:
            logger.debug(f"Import GPIO: {e}")
        
        # Imports des composants
        from config.settings import config
        from sensors.sensor_manager import sensor_manager
        from actuators.water_pump import water_pump
        from actuators.status_led import status_led
        from decision_engine.irrigation_logic import irrigation_logic
        from core.database_manager import db_manager
        from core.network_manager import network_manager
        
        self.config = config
        self.sensor_manager = sensor_manager
        self.water_pump = water_pump
        self.status_led = status_led
        self.irrigation_logic = irrigation_logic
        self.db_manager = db_manager
        self.network_manager = network_manager
        
        logger.info("✅ Système d'irrigation initialisé")
    
    def stop(self):
        """Arrête le système proprement"""
        logger.info("⏹️ Arrêt du système demandé...")
        self.running = False
        
        if self.cycle_thread and self.cycle_thread.is_alive():
            self.cycle_thread.join(timeout=5)
    
    def initialize(self):
        """Initialisation complète du système"""
        print("\n" + "=" * 50)
        print("🌱 SYSTÈME D'IRRIGATION INTELLIGENT")
        print("=" * 50)
        
        # Test réseau
        is_online = self.network_manager.check_network_status()
        self.config.offline_mode = not is_online
        print(f"🌐 Réseau: {'EN LIGNE' if is_online else 'HORS LIGNE'}")
        
        # Test rapide des capteurs
        print("\n🔍 TEST CAPTEURS:")
        sensor_data = self.sensor_manager.read_all()
        if sensor_data['success']:
            healthy = sensor_data['healthy_sensors']
            total = sensor_data['total_sensors']
            print(f"✅ {healthy}/{total} capteurs OK")
            
            # Afficher les valeurs
            sensors = sensor_data['sensors']
            if sensors.get('soil'):
                print(f"💧 Sol: {sensors['soil'].get('moisture_percent', 'N/A')}%")
            if sensors.get('dht22'):
                print(f"🌡️ Temp: {sensors['dht22'].get('temperature', 'N/A')}°C")
                print(f"💨 Hum: {sensors['dht22'].get('humidity', 'N/A')}%")
            if sensors.get('water'):
                print(f"💦 Eau: {sensors['water'].get('water_percent', 'N/A')}%")
            if sensors.get('rain'):
                print(f"🌧️ Pluie: {'DÉTECTÉE' if sensors['rain'].get('rain_detected') else 'NON'}")
        else:
            print("⚠️ Problème avec les capteurs")
        
        # Configuration
        print(f"\n⚙️ CONFIGURATION:")
        print(f"🌱 Plante: {self.config.plant.name}")
        print(f"💧 Humidité min: {self.config.plant.min_moisture}%")
        print(f"🎯 Humidité optimale: {self.config.plant.optimal_moisture}%")
        print(f"⏱️ Intervalle vérification: {self.config.irrigation.CHECK_INTERVAL}s")
        print(f"🚰 Durée irrigation: {self.config.irrigation.IRRIGATION_DURATION}s")
        print(f"📊 Limite quotidienne: {self.config.irrigation.MAX_IRRIGATION_PER_DAY}s")
        
        print("\n" + "=" * 50)
        print("✅ SYSTÈME PRÊT - DÉMARRAGE AUTOMATIQUE")
        print("=" * 50)
        
        # Mettre à jour les LEDs selon l'état
        try:
            self.status_led.set_system_state("IDLE", 
                soil_ok=False,
                online=not self.config.offline_mode
            )
        except Exception as e:
            logger.error(f"❌ Erreur initialisation LEDs: {e}")
        
        return True
    
    def run_cycle(self):
        """Exécute un cycle complet de surveillance"""
        try:
            self.cycle_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Mettre à jour l'état réseau
            is_online = self.network_manager.check_network_status()
            self.config.offline_mode = not is_online
            
            # Lecture des capteurs
            sensor_data = self.sensor_manager.read_all()
            
            if not sensor_data['success']:
                logger.error("❌ Échec lecture capteurs")
                
                # Enregistrer l'alerte
                self.db_manager.save_alert(
                    "SENSOR_FAILURE", 
                    "Échec lecture capteurs", 
                    "all"
                )
                return
            
            # Sauvegarde des données locales
            self.db_manager.save_sensor_data(sensor_data)
            
            # Synchronisation avec Firebase si en ligne
            if is_online:
                try:
                    from core.sync_manager import sync_manager
                    from firebase.firebase_config import firebase_manager
                    
                    if firebase_manager.connected:
                        if sync_manager.should_sync():
                            # Synchroniser en arrière-plan
                            sync_thread = threading.Thread(
                                target=sync_manager.sync_all_data,
                                daemon=True,
                                name="FirebaseSyncThread"
                            )
                            sync_thread.start()
                            logger.info("🔄 Synchronisation Firebase démarrée en arrière-plan")
                        
                        # Synchroniser la donnée actuelle immédiatement
                        sync_manager.sync_single_sensor_data(sensor_data)
                except ImportError:
                    logger.debug("Modules Firebase non disponibles")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur synchronisation Firebase: {e}")
            
            # Analyse et décision
            should_irrigate, reason, analysis = self.irrigation_logic.make_decision(sensor_data)
            
            # Afficher l'analyse (toutes les 5 cycles pour éviter le spam)
            if self.cycle_count % 5 == 0:
                soil = sensor_data['sensors'].get('soil', {})
                water = sensor_data['sensors'].get('water', {})
                dht22 = sensor_data['sensors'].get('dht22', {})
                
                logger.info(f"📊 CYCLE {self.cycle_count} - {current_time}")
                logger.info(f"💧 Sol: {soil.get('moisture_percent', 'N/A')}% | 💦 Eau: {water.get('water_percent', 'N/A')}%")
                logger.info(f"🌡️ Temp: {dht22.get('temperature', 'N/A')}°C | 💨 Hum: {dht22.get('humidity', 'N/A')}%")
                logger.info(f"🎯 Décision: {'IRRIGUER' if should_irrigate else 'ATTENDRE'}")
                if reason:
                    logger.info(f"📝 Raison: {reason}")
                
                # Afficher statut Firebase
                if is_online:
                    try:
                        from core.sync_manager import sync_manager
                        sync_status = sync_manager.get_sync_status()
                        logger.info(f"📡 Firebase: {'✓' if sync_status['firebase_connected'] else '✗'}")
                    except:
                        pass
            
            # Exécuter la décision
            if should_irrigate:
                success = self.irrigation_logic.execute_decision(should_irrigate, reason, analysis)
                if success:
                    logger.info(f"✅ Irrigation terminée (cycle {self.cycle_count})")
            
            # Nettoyage périodique (toutes les 10 cycles)
            if self.cycle_count % 10 == 0:
                deleted = self.db_manager.cleanup_old_data(3)  # Garder 3 jours seulement
                if deleted > 0:
                    logger.info(f"🧹 Données locales nettoyées: {deleted} lignes supprimées")
                
                self.cleanup_count += 1
                
        except Exception as e:
            logger.error(f"❌ Erreur cycle {self.cycle_count}: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_cycle_loop(self):
        """Boucle principale des cycles"""
        logger.info("\n🚀 DÉMARRAGE SURVEILLANCE AUTOMATIQUE\n")
        
        while self.running:
            # Exécuter un cycle
            self.run_cycle()
            
            # Attendre l'intervalle configuré
            wait_time = self.config.irrigation.CHECK_INTERVAL
            
            # Attente avec vérification d'arrêt toutes les secondes
            for i in range(wait_time):
                if not self.running:
                    break
                time.sleep(1)
    
    def run(self):
        """Démarre le système dans un thread séparé"""
        self.running = True
        
        # Initialisation
        if not self.initialize():
            logger.error("❌ Échec initialisation système")
            return
        
        # Démarrer la boucle des cycles dans un thread
        self.cycle_thread = threading.Thread(
            target=self._run_cycle_loop,
            name="IrrigationCycleThread",
            daemon=True
        )
        self.cycle_thread.start()
        
        logger.info("✅ Système démarré. Appuyez sur Ctrl+C pour arrêter.")
        
        try:
            # Maintenir le thread principal actif
            while self.running and self.cycle_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹️ Arrêt demandé par l'utilisateur (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Erreur système: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Arrêt propre du système"""
        logger.info("\n🧹 Arrêt du système...")
        
        # Arrêter la boucle
        self.stop()
        
        # 1. Arrêter la pompe si en marche
        if self.water_pump.is_running:
            logger.info("🛑 Arrêt de la pompe...")
            self.water_pump.stop()
        
        # 2. Éteindre toutes les LEDs (sans nettoyer GPIO si API tourne)
        logger.info("💡 Éteindre LEDs...")
        try:
            self.status_led.cleanup()
        except:
            pass
        
        # 3. Nettoyer les capteurs
        logger.info("🧹 Nettoyage capteurs...")
        self.sensor_manager.cleanup()
        
        # 4. Ne PAS nettoyer GPIO - laissé à l'API
        logger.info("🔌 GPIO laissé actif pour l'API")
        
        # 5. Statistiques finales
        logger.info(f"\n📊 STATISTIQUES FINALES:")
        logger.info(f"🔁 Cycles exécutés: {self.cycle_count}")
        logger.info(f"🧹 Nettoyages effectués: {self.cleanup_count}")
        logger.info(f"🚰 Irrigation aujourd'hui: {self.db_manager.get_today_irrigation_time():.1f}s")
        
        logger.info("✅ Système d'irrigation arrêté proprement")

def main():
    """Fonction principale pour exécution standalone"""
    print("🚀 LANCEMENT SYSTÈME D'IRRIGATION")
    print("=" * 50)
    
    system = IrrigationSystem()
    
    try:
        system.run()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        system.shutdown()

if __name__ == "__main__":
    main()