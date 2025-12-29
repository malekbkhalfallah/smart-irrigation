"""
Serveur web Flask pour l'API REST
"""
from flask import Flask, jsonify, request
import threading
import time
import logging
from typing import Dict, Any

from config.settings import config
from sensors.sensor_manager import sensor_manager
from decision_engine.irrigation_logic import irrigation_logic
from core.database import database
from core.weather_api import weather_api
from actuators.water_pump import water_pump

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables globales pour le thread de surveillance
monitoring_thread = None
stop_monitoring = False

@app.route('/')
def index():
    """Page d'accueil"""
    return jsonify({
        "message": "Smart Irrigation System API",
        "version": "1.0",
        "endpoints": {
            "/status": "Statut du système",
            "/sensors": "Données des capteurs",
            "/irrigate": "Lancer irrigation manuelle",
            "/history": "Historique",
            "/config": "Configuration"
        }
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retourne le statut complet du système"""
    try:
        # Lire les capteurs
        sensor_data = sensor_manager.read_all()
        
        # Obtenir le statut système
        system_status = irrigation_logic.get_system_status()
        
        # Obtenir les prévisions météo si disponibles
        weather_forecast = weather_api.get_weather_forecast() if not config.offline_mode else None
        
        # Dernière irrigation
        last_irrigation = database.get_last_irrigation()
        
        response = {
            "success": True,
            "timestamp": time.time(),
            "system": {
                "plant": system_status["plant"],
                "offline_mode": config.offline_mode,
                "today_irrigation": system_status["system"]["today_irrigation"]
            },
            "sensors": sensor_data["sensors"],
            "weather": weather_forecast,
            "last_irrigation": last_irrigation,
            "pump": water_pump.get_status()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erreur /status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """Retourne uniquement les données des capteurs"""
    try:
        sensor_data = sensor_manager.read_all()
        return jsonify({
            "success": sensor_data["success"],
            "timestamp": sensor_data["timestamp"],
            "sensors": sensor_data["sensors"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/irrigate', methods=['POST'])
def irrigate():
    """Lance une irrigation manuelle"""
    try:
        success = irrigation_logic.manual_irrigation()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Irrigation manuelle démarrée"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Échec de l'irrigation manuelle"
            }), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/irrigate/stop', methods=['POST'])
def stop_irrigation():
    """Arrête l'irrigation en cours"""
    try:
        success = water_pump.stop()
        
        return jsonify({
            "success": success,
            "message": "Irrigation arrêtée" if success else "Aucune irrigation en cours"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Retourne l'historique des données"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        
        sensor_history = database.get_recent_sensor_data(limit)
        
        return jsonify({
            "success": True,
            "sensor_data": sensor_history,
            "today_irrigation": database.get_today_irrigation_time()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Retourne la configuration actuelle"""
    try:
        return jsonify({
            "success": True,
            "config": config.to_dict() if hasattr(config, 'to_dict') else {
                "plant": {
                    "name": config.plant.name,
                    "min_moisture": config.plant.min_moisture,
                    "max_moisture": config.plant.max_moisture
                },
                "irrigation": {
                    "check_interval": config.irrigation.CHECK_INTERVAL,
                    "duration": config.irrigation.IRRIGATION_DURATION
                }
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/config/plant', methods=['PUT'])
def update_plant():
    """Met à jour le profil de la plante"""
    try:
        data = request.json
        
        if 'name' in data:
            config.plant.name = data['name']
        if 'min_moisture' in data:
            config.plant.min_moisture = float(data['min_moisture'])
        if 'max_moisture' in data:
            config.plant.max_moisture = float(data['max_moisture'])
        
        database.log_system_event(
            event_type="CONFIG_UPDATE",
            message=f"Plante mise à jour: {config.plant.name}"
        )
        
        return jsonify({
            "success": True,
            "message": "Configuration mise à jour",
            "plant": {
                "name": config.plant.name,
                "min_moisture": config.plant.min_moisture,
                "max_moisture": config.plant.max_moisture
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def monitoring_loop():
    """Boucle de surveillance automatique"""
    logger.info("Démarrage boucle de surveillance")
    
    while not stop_monitoring:
        try:
            # Lire les capteurs
            sensor_data = sensor_manager.read_all()
            
            if sensor_data["success"]:
                # Sauvegarder les données
                database.save_sensor_data(sensor_data)
                
                # Prendre une décision
                should_irrigate, reason = irrigation_logic.make_decision(sensor_data)
                
                # Exécuter la décision
                if should_irrigate:
                    irrigation_logic.execute_decision(should_irrigate, reason)
            
            # Attendre avant la prochaine vérification
            time.sleep(config.irrigation.CHECK_INTERVAL)
            
            # Nettoyage périodique de la base de données
            if time.time() % 3600 < config.irrigation.CHECK_INTERVAL:  # Toutes les heures
                database.cleanup_old_data(config.irrigation.HISTORY_DAYS)
                
        except Exception as e:
            logger.error(f"Erreur boucle surveillance: {e}")
            time.sleep(60)  # Attendre 1 minute en cas d'erreur

def start_monitoring():
    """Démarre la surveillance en arrière-plan"""
    global monitoring_thread, stop_monitoring
    
    stop_monitoring = False
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    logger.info("Surveillance démarrée")

def stop_monitoring_thread():
    """Arrête la surveillance"""
    global stop_monitoring
    stop_monitoring = True
    if monitoring_thread:
        monitoring_thread.join(timeout=5)

# Démarrer la surveillance IMMÉDIATEMENT au chargement
start_monitoring()

@app.teardown_appcontext
def cleanup(exception=None):
    stop_monitoring_thread()

# Démarrer la surveillance SI le fichier est exécuté directement
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger.info("🚀 Démarrage système hardware réel...")
    start_monitoring()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)