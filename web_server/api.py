"""
API Flask finale pour système d'irrigation - VERSION COMPLÈTE ET STABLE
"""
import time
import json
import logging
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialiser Flask
app = Flask(__name__)
CORS(app)

# Verrou pour éviter les conflits GPIO
gpio_lock = threading.Lock()

# Variables globales
SYSTEM_COMPONENTS = {}
SYSTEM_READY = False
AUTH_READY = False
CHATBOT_READY = False

def safe_initialize():
    """Initialisation sécurisée des composants"""
    global SYSTEM_COMPONENTS, SYSTEM_READY, AUTH_READY, CHATBOT_READY
    
    try:
        logger.info("🔧 Initialisation du système...")
        
        # 1. Configuration de base
        from config.settings import config
        SYSTEM_COMPONENTS['config'] = config
        logger.info("✅ Configuration chargée")
        
        # 2. Composants système
        try:
            from core.gpio_manager import gpio_central
            from sensors.sensor_manager import sensor_manager
            from actuators.water_pump import water_pump
            from actuators.status_led import status_led
            from decision_engine.irrigation_logic import irrigation_logic
            from core.database_manager import db_manager
            from core.network_manager import network_manager
            from core.weather_api import weather_api
            
            SYSTEM_COMPONENTS.update({
                'gpio': gpio_central,
                'sensor_manager': sensor_manager,
                'water_pump': water_pump,
                'status_led': status_led,
                'irrigation_logic': irrigation_logic,
                'db_manager': db_manager,
                'network_manager': network_manager,
                'weather_api': weather_api
            })
            
            SYSTEM_READY = True
            logger.info("✅ Système hardware chargé")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement hardware: {e}")
            SYSTEM_READY = False
        
        # 3. Authentification
        try:
            from mobile_backend.user_manager import user_manager
            SYSTEM_COMPONENTS['user_manager'] = user_manager
            AUTH_READY = True
            logger.info("✅ Authentification chargée")
        except Exception as e:
            logger.warning(f"⚠️ Authentification non disponible: {e}")
            AUTH_READY = False
        
        # 4. Chatbot
        try:
            from web_server.chatbot import EnhancedChatBot
            SYSTEM_COMPONENTS['chatbot'] = EnhancedChatBot()
            CHATBOT_READY = True
            logger.info("✅ Chatbot chargé")
        except Exception as e:
            logger.warning(f"⚠️ Chatbot non disponible: {e}")
            CHATBOT_READY = False
            
        logger.info("✅ Initialisation terminée")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        SYSTEM_READY = False

# Initialiser au démarrage
safe_initialize()

# ==================== ROUTES API ====================

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test simple de l'API"""
    return jsonify({
        "success": True,
        "message": "API Irrigation fonctionnelle",
        "timestamp": time.time(),
        "components": {
            "system": SYSTEM_READY,
            "auth": AUTH_READY,
            "chatbot": CHATBOT_READY
        }
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Statut complet du système"""
    try:
        if not SYSTEM_READY:
            return jsonify({"success": False, "error": "Système non initialisé"}), 503
        
        # Obtenir le statut réseau
        network_info = SYSTEM_COMPONENTS['network_manager'].get_network_info()
        
        # Obtenir les données des capteurs
        sensor_data = SYSTEM_COMPONENTS['sensor_manager'].read_all()
        
        # Obtenir le statut système
        system_status = SYSTEM_COMPONENTS['irrigation_logic'].get_system_status()
        
        data = {
            "timestamp": time.time(),
            "online": network_info.get("is_online", False),
            "local_ip": network_info.get("local_ip", "Unknown"),
            "sensors": sensor_data.get("sensors", {}),
            "system": {
                "running": True,
                "today_irrigation": SYSTEM_COMPONENTS['db_manager'].get_today_irrigation_time(),
                "plant": system_status.get("plant", {}),
                "offline_mode": system_status.get("system", {}).get("offline_mode", True)
            }
        }
        
        return jsonify({"success": True, "data": data})
        
    except Exception as e:
        logger.error(f"❌ Erreur statut: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    """Données des capteurs"""
    try:
        if not SYSTEM_READY:
            return jsonify({"success": False, "error": "Système non initialisé"}), 503
        
        sensor_data = SYSTEM_COMPONENTS['sensor_manager'].read_all()
        
        if sensor_data['success']:
            return jsonify({"success": True, "sensors": sensor_data.get("sensors", {})})
        else:
            return jsonify({"success": False, "error": "Échec lecture capteurs"}), 500
        
    except Exception as e:
        logger.error(f"❌ Erreur capteurs: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/control/pump', methods=['POST'])
def control_pump():
    """Contrôle de la pompe"""
    try:
        data = request.get_json()
        action = data.get('action', '').lower()
        
        if not SYSTEM_READY:
            return jsonify({"success": False, "error": "Système non initialisé"}), 503
        
        with gpio_lock:
            if action == 'start':
                duration = data.get('duration', 30)
                success, message = SYSTEM_COMPONENTS['irrigation_logic'].manual_irrigation()
                
                if success:
                    return jsonify({
                        "success": True,
                        "message": f"Pompe démarrée pour {duration}s",
                        "duration": duration
                    })
                else:
                    return jsonify({"success": False, "error": message}), 400
                    
            elif action == 'stop':
                SYSTEM_COMPONENTS['water_pump'].stop()
                return jsonify({"success": True, "message": "Pompe arrêtée"})
                
            else:
                return jsonify({"success": False, "error": "Action invalide. Utilisez 'start' ou 'stop'"}), 400
                
    except Exception as e:
        logger.error(f"❌ Erreur contrôle pompe: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== AUTHENTIFICATION ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Inscription utilisateur"""
    if not AUTH_READY:
        return jsonify({"error": "Authentification non disponible"}), 503
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username et password requis"}), 400
        
        success, message, user_id = SYSTEM_COMPONENTS['user_manager'].register_user(
            username=username,
            password=password,
            email=email if email else None
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "user_id": user_id
            })
        else:
            return jsonify({"success": False, "error": message}), 400
            
    except Exception as e:
        logger.error(f"❌ Erreur inscription: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Connexion utilisateur"""
    if not AUTH_READY:
        return jsonify({"error": "Authentification non disponible"}), 503
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username et password requis"}), 400
        
        success, message, user_data = SYSTEM_COMPONENTS['user_manager'].authenticate_user(
            username=username,
            password=password
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "user": user_data
            })
        else:
            return jsonify({"success": False, "error": message}), 401
            
    except Exception as e:
        logger.error(f"❌ Erreur connexion: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth/users', methods=['GET'])
def list_users():
    """Liste des utilisateurs (admin)"""
    if not AUTH_READY:
        return jsonify({"error": "Authentification non disponible"}), 503
    
    try:
        users = SYSTEM_COMPONENTS['user_manager'].get_all_users()
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== CHATBOT ====================

@app.route('/api/chatbot/ask', methods=['POST'])
def ask_chatbot():
    """Pose une question au chatbot"""
    if not CHATBOT_READY:
        return jsonify({"error": "Chatbot non disponible"}), 503
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"success": False, "error": "Question requise"}), 400
        
        # Vérifier si en ligne
        is_online = False
        if SYSTEM_READY:
            is_online = SYSTEM_COMPONENTS['network_manager'].is_online
        
        # Obtenir réponse
        if is_online:
            response = SYSTEM_COMPONENTS['chatbot'].ask_online(question)
            mode = "online"
        else:
            response = SYSTEM_COMPONENTS['chatbot'].ask_offline(question)
            mode = "offline"
        
        return jsonify({
            "success": True,
            "question": question,
            "response": response,
            "mode": mode,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur chatbot: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== PLANTES ====================

@app.route('/api/plants', methods=['GET'])
def get_plants():
    """Liste des plantes disponibles"""
    try:
        from config.plant_profiles import PLANT_PROFILES, list_available_plants
        
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

# ==================== DIAGNOSTIC ====================

@app.route('/api/diagnostic', methods=['GET'])
def diagnostic():
    """Diagnostic système"""
    diagnostic_data = {
        "timestamp": time.time(),
        "components": {
            "system": SYSTEM_READY,
            "auth": AUTH_READY,
            "chatbot": CHATBOT_READY
        },
        "endpoints": [
            {"path": "/api/test", "method": "GET", "description": "Test API"},
            {"path": "/api/status", "method": "GET", "description": "Statut système"},
            {"path": "/api/sensors", "method": "GET", "description": "Données capteurs"},
            {"path": "/api/control/pump", "method": "POST", "description": "Contrôle pompe"},
            {"path": "/api/auth/login", "method": "POST", "description": "Connexion"},
            {"path": "/api/auth/register", "method": "POST", "description": "Inscription"},
            {"path": "/api/chatbot/ask", "method": "POST", "description": "Chatbot"},
            {"path": "/api/plants", "method": "GET", "description": "Liste plantes"}
        ]
    }
    
    if SYSTEM_READY:
        diagnostic_data["hardware"] = SYSTEM_COMPONENTS['gpio'].get_gpio_status()
    
    return jsonify({"success": True, "diagnostic": diagnostic_data})

# ==================== GESTION DES ERREURS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erreur interne: {error}")
    return jsonify({"success": False, "error": "Erreur interne du serveur"}), 500
# ==================== FIREBASE ====================

@app.route('/api/firebase/status', methods=['GET'])
def get_firebase_status():
    """Statut Firebase"""
    try:
        from firebase.firebase_config import firebase_manager
        from core.sync_manager import sync_manager
        
        firebase_status = firebase_manager.get_status()
        sync_status = sync_manager.get_sync_status()
        
        return jsonify({
            "success": True,
            "firebase": firebase_status,
            "sync": sync_status
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/firebase/sync', methods=['POST'])
def trigger_sync():
    """Déclenche une synchronisation manuelle"""
    try:
        from core.sync_manager import sync_manager
        
        if not firebase_manager.connected:
            return jsonify({"success": False, "error": "Firebase non connecté"}), 400
        
        # Synchroniser en arrière-plan
        import threading
        thread = threading.Thread(
            target=sync_manager.sync_all_data,
            daemon=True,
            name="ManualSyncThread"
        )
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Synchronisation démarrée en arrière-plan",
            "sync_status": sync_manager.get_sync_status()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/firebase/test', methods=['GET'])
def test_firebase():
    """Test la connexion Firebase"""
    try:
        from firebase.firebase_config import firebase_manager
        
        if firebase_manager.connected:
            # Tester la connexion
            try:
                # Essayer d'écrire un document de test
                import time
                from datetime import datetime
                
                test_data = {
                    "test_timestamp": datetime.now().isoformat(),
                    "message": "Test de connexion depuis API",
                    "device": "raspberry_pi_irrigation",
                    "api_test": True
                }
                
                firebase_manager.db.collection("system_tests").add(test_data)
                
                return jsonify({
                    "success": True,
                    "message": "✅ Firebase connecté et opérationnel",
                    "project_id": "irrigation-raytech",
                    "test_data_sent": test_data
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Erreur écriture Firebase: {str(e)}",
                    "connected": firebase_manager.connected
                }), 500
        else:
            return jsonify({
                "success": False,
                "error": "Firebase non connecté",
                "service_file_exists": os.path.exists("firebase_service_account.json")
            }), 503
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
# ==================== DÉMARRAGE ====================

def run_server(host='0.0.0.0', port=5000, debug=False):
    """Démarre le serveur"""
    print(f"\n{'='*60}")
    print("🌐 SERVEUR IRRIGATION INTELLIGENT")
    print(f"{'='*60}")
    print(f"📡 API: http://{host}:{port}")
    print(f"🔧 Test: http://{host}:{port}/api/test")
    print(f"🔍 Diagnostic: http://{host}:{port}/api/diagnostic")
    print(f"{'='*60}")
    
    # IP locale
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"📍 IP Locale: http://{local_ip}:{port}")
    except:
        pass
    
    print(f"{'='*60}\n")
    
    app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)

if __name__ == '__main__':
    run_server(host='0.0.0.0', port=5000, debug=True)