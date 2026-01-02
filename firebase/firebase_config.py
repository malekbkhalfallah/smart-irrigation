"""
Configuration Firebase robuste avec gestion d'erreurs
"""
import os
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Gestionnaire Firebase robuste"""
    
    def __init__(self):
        self.connected = False
        self.db = None
        self.app = None
        self.service_file = "firebase_service_account.json"
        self.project_id = "unknown"
        
        # Statistiques
        self.stats = {
            "sync_count": 0,
            "error_count": 0,
            "last_success": 0,
            "last_error": None,
            "start_time": time.time()
        }
        
        self.setup_firebase()
    
    def setup_firebase(self):
        """Configure Firebase avec gestion d'erreurs robuste"""
        # Vérifier le fichier de service
        if not os.path.exists(self.service_file):
            logger.warning(f"⚠️ Fichier {self.service_file} non trouvé")
            logger.info("💡 Place le fichier firebase_service_account.json à la racine du projet")
            self.connected = False
            return
        
        try:
            # Vérifier le contenu du fichier
            with open(self.service_file, 'r') as f:
                service_data = json.load(f)
                self.project_id = service_data.get("project_id", "unknown")
                
                # Vérifier les champs requis
                required_fields = ["type", "project_id", "private_key_id", 
                                 "private_key", "client_email"]
                missing_fields = [field for field in required_fields 
                                if field not in service_data]
                
                if missing_fields:
                    logger.error(f"❌ Champs manquants dans {self.service_file}: {missing_fields}")
                    self.connected = False
                    return
            
            logger.info(f"📁 Fichier Firebase chargé: {self.service_file}")
            logger.info(f"🏢 Projet: {self.project_id}")
            
            # Importer Firebase
            import firebase_admin
            from firebase_admin import credentials, firestore, exceptions
            
            # Initialiser Firebase
            cred = credentials.Certificate(self.service_file)
            
            # Vérifier si déjà initialisé
            try:
                self.app = firebase_admin.get_app('irrigation_system')
                logger.info("✅ Firebase déjà initialisé")
            except ValueError:
                self.app = firebase_admin.initialize_app(cred, name='irrigation_system')
                logger.info("✅ Firebase initialisé")
            
            # Obtenir Firestore
            self.db = firestore.client(app=self.app)
            self.connected = True
            
            # Tester la connexion
            self.test_connection()
            
        except ImportError:
            logger.error("❌ Module firebase_admin non installé")
            logger.info("   Exécutez: pip install firebase-admin")
            self.connected = False
            
        except exceptions.FirebaseError as e:
            logger.error(f"❌ Erreur Firebase: {e}")
            self.connected = False
            self.stats["error_count"] += 1
            self.stats["last_error"] = str(e)
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration Firebase: {e}")
            self.connected = False
            self.stats["error_count"] += 1
            self.stats["last_error"] = str(e)
    
    def test_connection(self):
        """Teste la connexion à Firebase"""
        if not self.connected or not self.db:
            return False
        
        try:
            # Essayer d'écrire et lire un document de test
            test_ref = self.db.collection("system_tests").document("connection_test")
            
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "message": "Test de connexion",
                "device": "raspberry_pi_irrigation",
                "test_id": int(time.time())
            }
            
            # Écrire
            test_ref.set(test_data)
            
            # Lire
            doc = test_ref.get()
            
            if doc.exists:
                logger.info("✅ Connexion Firebase testée avec succès")
                self.stats["last_success"] = time.time()
                return True
            else:
                logger.warning("⚠️ Test Firebase: document non trouvé après écriture")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test de connexion Firebase échoué: {e}")
            self.stats["error_count"] += 1
            self.stats["last_error"] = str(e)
            return False
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Sauvegarde les données des capteurs dans Firebase"""
        if not self.connected or not self.db:
            return False
        
        try:
            # Préparer les données avec métadonnées
            data_to_save = {
                "timestamp": datetime.now().isoformat(),
                "device_id": "raspberry_pi_irrigation",
                "location": "home_garden",
                "project": self.project_id,
                "data": sensor_data,
                "sync_time": datetime.now().isoformat(),
                "sync_timestamp": time.time()
            }
            
            # Ajouter à Firestore avec ID unique basé sur le timestamp
            doc_id = f"sensor_{int(time.time() * 1000)}"
            doc_ref = self.db.collection("sensor_readings").document(doc_id)
            doc_ref.set(data_to_save)
            
            self.stats["sync_count"] += 1
            self.stats["last_success"] = time.time()
            
            logger.debug(f"📡 Données synchronisées: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation Firebase: {e}")
            self.stats["error_count"] += 1
            self.stats["last_error"] = str(e)
            return False
    
    def save_irrigation_event(self, duration: float, reason: str, 
                            triggered_by: str = "auto") -> bool:
        """Sauvegarde un événement d'irrigation"""
        if not self.connected or not self.db:
            return False
        
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "reason": reason,
                "triggered_by": triggered_by,
                "device_id": "raspberry_pi_irrigation",
                "project": self.project_id,
                "status": "completed",
                "sync_time": datetime.now().isoformat()
            }
            
            doc_id = f"irrigation_{int(time.time() * 1000)}"
            self.db.collection("irrigation_events").document(doc_id).set(event_data)
            
            self.stats["sync_count"] += 1
            logger.info(f"🚰 Événement irrigation synchronisé: {duration}s - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation irrigation: {e}")
            self.stats["error_count"] += 1
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut Firebase"""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "connected": self.connected,
            "project_id": self.project_id,
            "service_file_exists": os.path.exists(self.service_file),
            "stats": {
                "sync_count": self.stats["sync_count"],
                "error_count": self.stats["error_count"],
                "last_success": self.stats["last_success"],
                "uptime_hours": round(uptime / 3600, 2),
                "sync_rate": round(self.stats["sync_count"] / (uptime / 3600), 2) if uptime > 0 else 0
            },
            "last_error": self.stats["last_error"]
        }

# Instance globale
firebase_manager = FirebaseManager()