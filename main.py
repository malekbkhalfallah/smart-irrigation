#!/usr/bin/env python3
"""
SYSTÈME D'IRRIGATION INTELLIGENT UNIFIÉ - Point d'entrée principal
Inclut : Automatisation + API Flask dans un seul processus
"""
import time
import logging
import sys
import threading
import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

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

class UnifiedIrrigationSystem:
    """Système unifié : automatisation + API dans un seul processus"""
    
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.cleanup_count = 0
        self.cycle_thread = None
        
        # Initialisation du hardware (une seule fois)
        self.initialize_hardware()
        
        # Initialisation de l'API
        self.initialize_api()
        
        logger.info("✅ Système unifié initialisé")
    
    def initialize_hardware(self):
        """Initialise le hardware (GPIO, capteurs, actionneurs)"""
        try:
            # GPIO
            from core.gpio_manager import gpio_central
            self.gpio = gpio_central
            
            # Capteurs
            from sensors.sensor_manager import sensor_manager
            self.sensor_manager = sensor_manager
            
            # Actionneurs
            from actuators.water_pump import water_pump
            from actuators.status_led import status_led
            self.water_pump = water_pump
            self.status_led = status_led
            
            # Logique
            from decision_engine.irrigation_logic import irrigation_logic
            self.irrigation_logic = irrigation_logic
            
            # Base de données
            from core.database_manager import db_manager
            self.db_manager = db_manager
            
            # Réseau
            from core.network_manager import network_manager
            self.network_manager = network_manager
            
            # Configuration
            from config.settings import config
            self.config = config
            
            logger.info("✅ Hardware initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation hardware: {e}")
            raise
    
    def initialize_api(self):
        """Initialise l'API Flask dans le même processus"""
        try:
            self.app = Flask(__name__)
            CORS(self.app)
            
            # Données partagées (thread-safe)
            self.shared_data = {
                'sensor_data': None,
                'last_update': 0,
                'system_status': {}
            }
            self.data_lock = threading.Lock()
            
            # Définir les routes API
            self.setup_api_routes()
            
            logger.info("✅ API Flask initialisée")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation API: {e}")
            raise
    
    def setup_api_routes(self):
        """Configure les routes de l'API"""
        
        @self.app.route('/api/test', methods=['GET'])
        def test_api():
            return jsonify({
                "success": True,
                "message": "Système d'irrigation unifié",
                "timestamp": time.time(),
                "mode": "unified"
            })
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            with self.data_lock:
                return jsonify({
                    "success": True,
                    "data": self.shared_data['system_status'],
                    "timestamp": time.time()
                })
        
        @self.app.route('/api/sensors', methods=['GET'])
        def get_sensors():
            with self.data_lock:
                if self.shared_data['sensor_data']:
                    return jsonify({
                        "success": True,
                        "sensors": self.shared_data['sensor_data'].get("sensors", {}),
                        "timestamp": time.time()
                    })
                else:
                    return jsonify({"success": False, "error": "Données non disponibles"}), 503
        
        @self.app.route('/api/control/pump', methods=['POST'])
        def control_pump():
            try:
                data = request.get_json()
                action = data.get('action', '').lower()
                
                if action == 'start':
                    duration = data.get('duration', 30)
                    success, message = self.irrigation_logic.manual_irrigation()
                    
                    if success:
                        return jsonify({
                            "success": True,
                            "message": f"Pompe démarrée pour {duration}s"
                        })
                    else:
                        return jsonify({"success": False, "error": message}), 400
                        
                elif action == 'stop':
                    self.water_pump.stop()
                    return jsonify({"success": True, "message": "Pompe arrêtée"})
                    
                else:
                    return jsonify({"success": False, "error": "Action invalide"}), 400
                    
            except Exception as e:
                logger.error(f"❌ Erreur contrôle pompe: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # Route pour les plantes
        @self.app.route('/api/plants', methods=['GET'])
        def get_plants():
            try:
                from config.plant_profiles import PLANT_PROFILES
                plants = []
                for key, profile in PLANT_PROFILES.items():
                    plants.append({
                        "id": key,
                        "name": profile.name,
                        "min_moisture": profile.min_moisture,
                        "optimal_moisture": profile.optimal_moisture,
                        "max_moisture": profile.max_moisture,
                        "water_needs": profile.water_needs,
                        "description": profile.description
                    })
                return jsonify({"success": True, "plants": plants})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        # Route pour le diagnostic
        @self.app.route('/api/diagnostic', methods=['GET'])
        def diagnostic():
            diagnostic_data = {
                "timestamp": time.time(),
                "endpoints": [
                    {"path": "/api/test", "method": "GET", "description": "Test API"},
                    {"path": "/api/status", "method": "GET", "description": "Statut système"},
                    {"path": "/api/sensors", "method": "GET", "description": "Données capteurs"},
                    {"path": "/api/control/pump", "method": "POST", "description": "Contrôle pompe"},
                    {"path": "/api/plants", "method": "GET", "description": "Liste plantes"}
                ]
            }
            return jsonify({"success": True, "diagnostic": diagnostic_data})
    
    def run_api(self, host='0.0.0.0', port=5000):
        """Exécute l'API Flask"""
        logger.info(f"🌐 Démarrage API sur {host}:{port}")
        
        # Désactiver le reloader pour éviter les problèmes de threads
        self.app.run(
            host=host, 
            port=port, 
            debug=False, 
            threaded=True, 
            use_reloader=False
        )
    
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
                return
            
            # Sauvegarde des données locales
            self.db_manager.save_sensor_data(sensor_data)
            
            # Mettre à jour les données partagées pour l'API
            with self.data_lock:
                self.shared_data['sensor_data'] = sensor_data
                self.shared_data['last_update'] = time.time()
                
                # Mettre à jour le statut système
                self.shared_data['system_status'] = {
                    "timestamp": time.time(),
                    "online": is_online,
                    "sensors": sensor_data.get("sensors", {}),
                    "system": {
                        "running": True,
                        "today_irrigation": self.db_manager.get_today_irrigation_time(),
                        "plant": {
                            "name": self.config.plant.name,
                            "min_moisture": self.config.plant.min_moisture,
                            "optimal_moisture": self.config.plant.optimal_moisture,
                            "max_moisture": self.config.plant.max_moisture
                        },
                        "offline_mode": self.config.offline_mode
                    }
                }
            
            # Synchronisation avec Firebase si en ligne
            if is_online:
                try:
                    from core.sync_manager import sync_manager
                    from firebase.firebase_config import firebase_manager
                    
                    if firebase_manager.connected:
                        if sync_manager.should_sync():
                            sync_thread = threading.Thread(
                                target=sync_manager.sync_all_data,
                                daemon=True,
                                name="FirebaseSyncThread"
                            )
                            sync_thread.start()
                            logger.info("🔄 Synchronisation Firebase démarrée")
                        
                        sync_manager.sync_single_sensor_data(sensor_data)
                except Exception as e:
                    logger.warning(f"⚠️ Erreur synchronisation Firebase: {e}")
            
            # Analyse et décision
            should_irrigate, reason, analysis = self.irrigation_logic.make_decision(sensor_data)
            
            # Afficher l'analyse (toutes les 5 cycles)
            if self.cycle_count % 5 == 0:
                soil = sensor_data['sensors'].get('soil', {})
                water = sensor_data['sensors'].get('water', {})
                dht22 = sensor_data['sensors'].get('dht22', {})
                
                logger.info(f"📊 CYCLE {self.cycle_count} - {current_time}")
                logger.info(f"💧 Sol: {soil.get('moisture_percent', 'N/A')}% | 💦 Eau: {water.get('water_percent', 'N/A')}%")
                logger.info(f"🌡️ Temp: {dht22.get('temperature', 'N/A')}°C | 💨 Hum: {dht22.get('humidity', 'N/A')}%")
                logger.info(f"🎯 Décision: {'IRRIGUER' if should_irrigate else 'ATTENDRE'}")
            
            # Exécuter la décision
            if should_irrigate:
                success = self.irrigation_logic.execute_decision(should_irrigate, reason, analysis)
                if success:
                    logger.info(f"✅ Irrigation terminée (cycle {self.cycle_count})")
            
            # Nettoyage périodique
            if self.cycle_count % 10 == 0:
                deleted = self.db_manager.cleanup_old_data(3)
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
            self.run_cycle()
            
            # Attendre l'intervalle configuré
            wait_time = self.config.irrigation.CHECK_INTERVAL
            for i in range(wait_time):
                if not self.running:
                    break
                time.sleep(1)
    
    def run(self):
        """Démarre le système unifié"""
        self.running = True
        
        # Initialisation complète
        print("\n" + "=" * 60)
        print("🚀 SYSTÈME D'IRRIGATION INTELLIGENT UNIFIÉ")
        print("=" * 60)
        
        # Test rapide
        is_online = self.network_manager.check_network_status()
        print(f"🌐 Réseau: {'EN LIGNE' if is_online else 'HORS LIGNE'}")
        
        sensor_data = self.sensor_manager.read_all()
        if sensor_data['success']:
            print(f"✅ {sensor_data['healthy_sensors']}/{sensor_data['total_sensors']} capteurs OK")
        
        print(f"🌱 Plante: {self.config.plant.name}")
        print(f"📡 API: http://0.0.0.0:5000")
        
        # IP locale
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            print(f"📍 IP Locale: http://{local_ip}:5000")
        except:
            pass
        
        print("=" * 60)
        
        # Démarrer la surveillance dans un thread
        self.cycle_thread = threading.Thread(
            target=self._run_cycle_loop,
            name="IrrigationCycleThread",
            daemon=True
        )
        self.cycle_thread.start()
        
        logger.info("✅ Système démarré. Appuyez sur Ctrl+C pour arrêter.")
        
        # Démarrer l'API dans le thread principal (bloquant)
        try:
            self.run_api()
        except KeyboardInterrupt:
            logger.info("\n⏹️ Arrêt demandé par l'utilisateur (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Erreur API: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Arrêt propre du système"""
        logger.info("\n🧹 Arrêt du système unifié...")
        
        self.running = False
        
        # Arrêter la pompe si en marche
        if self.water_pump.is_running:
            logger.info("🛑 Arrêt de la pompe...")
            self.water_pump.stop()
        
        # Éteindre les LEDs
        logger.info("💡 Éteindre LEDs...")
        try:
            self.status_led.cleanup()
        except:
            pass
        
        # Nettoyer les capteurs
        logger.info("🧹 Nettoyage capteurs...")
        self.sensor_manager.cleanup()
        
        # Nettoyer GPIO
        logger.info("🔌 Nettoyage GPIO...")
        self.gpio.cleanup()
        
        # Statistiques finales
        logger.info(f"\n📊 STATISTIQUES FINALES:")
        logger.info(f"🔁 Cycles exécutés: {self.cycle_count}")
        logger.info(f"🧹 Nettoyages effectués: {self.cleanup_count}")
        logger.info(f"🚰 Irrigation aujourd'hui: {self.db_manager.get_today_irrigation_time():.1f}s")
        
        logger.info("✅ Système unifié arrêté proprement")

def main():
    """Fonction principale"""
    print("🚀 LANCEMENT SYSTÈME UNIFIÉ (Automatisation + API)")
    print("=" * 60)
    
    system = UnifiedIrrigationSystem()
    
    try:
        system.run()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        system.shutdown()

if __name__ == "__main__":
    main()