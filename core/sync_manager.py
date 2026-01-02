"""
Gestionnaire de synchronisation Firebase - Version complète
"""
import time
import logging
import threading
import sqlite3  # AJOUT IMPORT
from typing import List, Dict, Any
from core.database_manager import db_manager
from firebase.firebase_config import firebase_manager

logger = logging.getLogger(__name__)

class SyncManager:
    """Gère la synchronisation entre base locale et Firebase"""
    
    def __init__(self):
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = 0
        self.sync_in_progress = False
        self.sync_lock = threading.Lock()
        
        logger.info("✅ SyncManager initialisé")
    
    def should_sync(self) -> bool:
        """Détermine si une synchronisation est nécessaire"""
        current_time = time.time()
        
        # Vérifier l'intervalle
        if current_time - self.last_sync_time < self.sync_interval:
            return False
        
        # Vérifier si Firebase est connecté
        if not firebase_manager.connected:
            logger.debug("Firebase non connecté, pas de synchronisation")
            return False
        
        return True
    
    def sync_all_data(self) -> Dict[str, Any]:
        """Synchronise toutes les données avec Firebase"""
        with self.sync_lock:
            if self.sync_in_progress:
                logger.debug("Synchronisation déjà en cours")
                return {"success": False, "message": "Sync déjà en cours"}
            
            self.sync_in_progress = True
            
            try:
                logger.info("🔄 Démarrage synchronisation Firebase...")
                
                stats = {
                    "sensor_data_synced": 0,
                    "irrigation_events_synced": 0,
                    "alerts_synced": 0,
                    "errors": 0
                }
                
                # 1. Synchroniser les données des capteurs
                logger.info("📊 Synchronisation des données capteurs...")
                sensor_data = db_manager.get_recent_sensor_data(limit=50)
                
                for data in sensor_data:
                    try:
                        # Convertir le format SQLite vers format Firebase
                        firebase_data = {
                            "timestamp": data.get("timestamp"),
                            "soil_moisture": data.get("soil_moisture"),
                            "soil_is_dry": data.get("soil_is_dry"),
                            "water_level": data.get("water_level"),
                            "water_detected": data.get("water_detected"),
                            "rain_detected": data.get("rain_detected"),
                            "temperature": data.get("temperature"),
                            "air_humidity": data.get("air_humidity"),
                            "device_id": "raspberry_pi_irrigation",
                            "sync_time": time.time()
                        }
                        
                        if firebase_manager.save_sensor_data(firebase_data):
                            stats["sensor_data_synced"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"❌ Erreur sync données capteur: {e}")
                
                # 2. Synchroniser les événements d'irrigation
                logger.info("🚰 Synchronisation des événements d'irrigation...")
                # Récupérer les événements non synchronisés
                try:
                    # CORRECTION: Accès direct à la base SQLite
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT * FROM irrigation_events 
                        WHERE timestamp > datetime('now', '-1 day')
                        ORDER BY timestamp DESC
                    """)
                    
                    irrigation_events = cursor.fetchall()
                    conn.close()
                    
                    for event in irrigation_events:
                        try:
                            if firebase_manager.save_irrigation_event(
                                duration=event[2],  # duration
                                reason=event[3],    # reason
                                triggered_by=event[4]  # triggered_by
                            ):
                                stats["irrigation_events_synced"] += 1
                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"❌ Erreur sync irrigation: {e}")
                            
                except Exception as e:
                    logger.error(f"❌ Erreur récupération événements: {e}")
                
                # Mettre à jour le temps de dernière synchronisation
                self.last_sync_time = time.time()
                
                # Nettoyer les anciennes données locales
                if stats["sensor_data_synced"] > 0:
                    deleted = db_manager.cleanup_old_data(3)  # Garder 3 jours seulement
                    logger.info(f"🧹 Données locales nettoyées: {deleted} lignes supprimées")
                
                logger.info(f"✅ Synchronisation terminée: {stats}")
                return {"success": True, "stats": stats}
                
            except Exception as e:
                logger.error(f"❌ Erreur synchronisation: {e}")
                return {"success": False, "error": str(e)}
            finally:
                self.sync_in_progress = False
    
    def sync_single_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Synchronise une seule lecture de capteur"""
        if not firebase_manager.connected:
            return False
        
        try:
            firebase_data = {
                "timestamp": time.time(),
                "sensor_data": sensor_data,
                "device_id": "raspberry_pi_irrigation",
                "sync_time": time.time()
            }
            
            return firebase_manager.save_sensor_data(firebase_data)
            
        except Exception as e:
            logger.error(f"❌ Erreur sync donnée unique: {e}")
            return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Retourne le statut de synchronisation"""
        firebase_status = firebase_manager.get_status()
        
        return {
            "last_sync_time": self.last_sync_time,
            "sync_in_progress": self.sync_in_progress,
            "sync_interval": self.sync_interval,
            "firebase_connected": firebase_status["connected"],
            "firebase_sync_count": firebase_status["sync_count"],
            "firebase_error_count": firebase_status["error_count"]
        }

# Instance globale
sync_manager = SyncManager()