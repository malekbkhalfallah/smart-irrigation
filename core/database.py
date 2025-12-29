"""
Base de données SQLite thread-safe avec Firebase optionnel
"""
import sqlite3
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import Firebase
try:
    from firebase_config import firebase_manager
    FIREBASE_AVAILABLE = True
    logger.info("✅ Firebase disponible pour synchronisation")
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.info("ℹ️ Firebase non configuré - Synchronisation locale seulement")

# Thread-local storage pour SQLite
thread_local = threading.local()

class DatabaseManager:
    """Gestionnaire de base de données avec synchronisation Firebase"""
    
    def __init__(self, db_path: str = "irrigation.db"):
        self.db_path = Path(db_path)
        self.local_db = LocalDatabase(db_path)
        self.firebase_available = FIREBASE_AVAILABLE
        
        logger.info(f"📊 DatabaseManager initialisé - Firebase: {'✅ Activé' if self.firebase_available else '❌ Désactivé'}")
    
    def save_sensor_reading(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde une lecture de capteur dans SQLite et Firebase
        """
        # Sauvegarde locale
        local_success = self.local_db.save_sensor_data(sensor_data)
        
        # Sauvegarde Firebase si disponible et connecté
        firebase_success = False
        if self.firebase_available and firebase_manager.connected:
            try:
                firebase_success = firebase_manager.save_sensor_data(sensor_data)
                if firebase_success:
                    logger.debug("📡 Données synchronisées avec Firebase")
            except Exception as e:
                logger.error(f"❌ Erreur synchronisation Firebase: {e}")
        
        return local_success or firebase_success
    
    def save_irrigation_event(self, duration: float, reason: str, 
                            triggered_by: str = "auto", success: bool = True) -> bool:
        """
        Sauvegarde un événement d'irrigation dans SQLite et Firebase
        """
        # Sauvegarde locale
        local_success = self.local_db.log_irrigation(duration, reason, triggered_by, success)
        
        # Sauvegarde Firebase
        firebase_success = False
        if self.firebase_available and firebase_manager.connected:
            try:
                firebase_success = firebase_manager.save_irrigation_event(
                    duration, reason, triggered_by
                )
                if firebase_success:
                    logger.info(f"🚰 Irrigation synchronisée avec Firebase: {duration}s")
            except Exception as e:
                logger.error(f"❌ Erreur synchronisation irrigation Firebase: {e}")
        
        return local_success or firebase_success
    
    def save_system_status(self, status_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde le statut système dans SQLite et Firebase
        """
        # Ajouter timestamp si pas présent
        if "timestamp" not in status_data:
            status_data["timestamp"] = datetime.now()
        
        # Sauvegarde locale (dans system_events)
        local_success = self.local_db.log_system_event(
            "system_status", 
            f"Status: {status_data.get('status', 'unknown')}"
        )
        
        # Sauvegarde Firebase
        firebase_success = False
        if self.firebase_available and firebase_manager.connected:
            try:
                firebase_success = firebase_manager.save_system_status(status_data)
                if firebase_success:
                    logger.debug("📡 Statut système synchronisé avec Firebase")
            except Exception as e:
                logger.error(f"❌ Erreur synchronisation statut Firebase: {e}")
        
        return local_success or firebase_success
    
    # Méthodes de lecture (seulement depuis SQLite)
    
    def get_today_irrigation_time(self) -> float:
        """Retourne le temps total d'irrigation aujourd'hui"""
        return self.local_db.get_today_irrigation_time()
    
    def get_last_irrigation(self) -> Optional[Dict[str, Any]]:
        """Récupère la dernière irrigation"""
        return self.local_db.get_last_irrigation()
    
    def get_recent_sensor_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les dernières lectures de capteurs"""
        return self.local_db.get_recent_sensor_data(limit)
    
    def get_firebase_status(self) -> Dict[str, Any]:
        """Retourne le statut de la synchronisation Firebase"""
        if self.firebase_available and firebase_manager.connected:
            return {
                "connected": True,
                "last_sync": firebase_manager.get_last_sync(),
                "project_id": firebase_manager._get_project_id()
            }
        return {
            "connected": False,
            "message": "Firebase non disponible",
            "setup_required": True
        }
    
    def close(self):
        """Ferme proprement les connexions"""
        self.local_db.close_all_connections()
        logger.info("🔒 DatabaseManager fermé")

# ============================================================================
# Classe LocalDatabase (inchangée)
# ============================================================================

class LocalDatabase:
    """Gestion de la base de données SQLite locale - Thread-safe"""
    
    def __init__(self, db_path: str = "irrigation.db"):
        self.db_path = Path(db_path)
        self.initialize_database()
    
    def get_connection(self):
        """Obtient une connexion SQLite pour le thread courant (thread-safe)"""
        if not hasattr(thread_local, "connection"):
            thread_local.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            thread_local.connection.row_factory = sqlite3.Row
            
            # Créer les tables si elles n'existent pas
            self.create_tables(thread_local.connection)
        
        return thread_local.connection
    
    def create_tables(self, conn):
        """Crée les tables nécessaires"""
        try:
            cursor = conn.cursor()
            
            # Table des lectures de capteurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    temperature REAL,
                    air_humidity REAL,
                    soil_moisture REAL,
                    soil_is_dry BOOLEAN,
                    rain_detected BOOLEAN,
                    water_level REAL,
                    water_detected BOOLEAN
                )
            """)
            
            # Table des événements d'irrigation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS irrigation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration REAL,
                    reason TEXT,
                    triggered_by TEXT,
                    success BOOLEAN
                )
            """)
            
            # Table des événements système
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    message TEXT
                )
            """)
            
            conn.commit()
            logger.info("✅ Tables de base de données créées/vérifiées")
            
        except Exception as e:
            logger.error(f"❌ Erreur création tables: {e}")
    
    def initialize_database(self):
        """Initialise la base de données"""
        try:
            # Test de connexion
            conn = self.get_connection()
            logger.info(f"✅ Base de données initialisée: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation BD: {e}")
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Sauvegarde les données des capteurs - Thread-safe"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Extraire les données des capteurs
            sensors = sensor_data.get("sensors", {})
            dht22 = sensors.get("dht22", {})
            soil = sensors.get("soil", {})
            rain = sensors.get("rain", {})
            water = sensors.get("water_level", {})
            
            cursor.execute("""
                INSERT INTO sensor_readings 
                (temperature, air_humidity, soil_moisture, soil_is_dry, 
                 rain_detected, water_level, water_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dht22.get('temperature'),
                dht22.get('humidity'),
                soil.get('moisture_percent'),
                soil.get('is_dry'),
                rain.get('rain_detected'),
                water.get('water_percent'),
                water.get('water_detected')
            ))
            
            conn.commit()
            logger.debug(f"✅ Données capteurs sauvegardées localement (Thread: {threading.get_ident()})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde données capteurs: {e}")
            return False
    
    def log_irrigation(self, duration: float, reason: str, 
                      triggered_by: str = "auto", success: bool = True) -> bool:
        """Log un événement d'irrigation - Thread-safe"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO irrigation_events 
                (duration, reason, triggered_by, success)
                VALUES (?, ?, ?, ?)
            """, (duration, reason, triggered_by, success))
            
            conn.commit()
            logger.info(f"✅ Irrigation loguée localement: {duration}s - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur log irrigation: {e}")
            return False
    
    def log_system_event(self, event_type: str, message: str) -> bool:
        """Log un événement système - Thread-safe"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_events (event_type, message)
                VALUES (?, ?)
            """, (event_type, message))
            
            conn.commit()
            logger.debug(f"✅ Événement système logué: {event_type} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur log événement système: {e}")
            return False
    
    def get_today_irrigation_time(self) -> float:
        """Retourne le temps total d'irrigation aujourd'hui"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(duration) as total 
                FROM irrigation_events 
                WHERE DATE(timestamp) = DATE('now') 
                AND success = 1
            """)
            
            result = cursor.fetchone()
            return result[0] or 0.0
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul temps irrigation: {e}")
            return 0.0
    
    def get_last_irrigation(self) -> Optional[Dict[str, Any]]:
        """Récupère la dernière irrigation"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM irrigation_events 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération dernière irrigation: {e}")
            return None
    
    def get_recent_sensor_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les dernières lectures de capteurs"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT * FROM sensor_readings 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données capteurs: {e}")
            return []
    
    def close_all_connections(self):
        """Ferme toutes les connexions (pour arrêt propre)"""
        if hasattr(thread_local, "connection"):
            try:
                thread_local.connection.close()
                del thread_local.connection
            except:
                pass
        logger.info("🔒 Connexions BD locales fermées")

# ============================================================================
# Instance globale
# ============================================================================

# Instance globale de DatabaseManager
db_manager = DatabaseManager()

# Alias pour compatibilité (si d'autres fichiers utilisent "database")
database = db_manager.local_db

# Test rapide
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 TEST DATABASE MANAGER")
    print("=" * 50)
    
    # Test Firebase
    fb_status = db_manager.get_firebase_status()
    print(f"Firebase: {'✅ Connecté' if fb_status.get('connected') else '❌ Non connecté'}")
    if fb_status.get('connected'):
        print(f"Projet: {fb_status.get('project_id')}")
        print(f"Dernière synchro: {fb_status.get('last_sync')}")
    
    # Test données simulées
    test_data = {
        "sensors": {
            "dht22": {"temperature": 23.5, "humidity": 64.0},
            "soil": {"moisture_percent": 40.0, "is_dry": False},
            "rain": {"rain_detected": False},
            "water_level": {"water_percent": 80.0, "water_detected": True}
        },
        "success": True,
        "timestamp": time.time()
    }
    
    # Test sauvegarde
    result = db_manager.save_sensor_reading(test_data)
    print(f"\nSauvegarde capteurs: {'✅ Réussie' if result else '❌ Échouée'}")
    
    result = db_manager.save_irrigation_event(5.0, "test")
    print(f"Sauvegarde irrigation: {'✅ Réussie' if result else '❌ Échouée'}")
    
    result = db_manager.save_system_status({"status": "testing"})
    print(f"Sauvegarde statut: {'✅ Réussie' if result else '❌ Échouée'}")
    
    print(f"\nTemps irrigation aujourd'hui: {db_manager.get_today_irrigation_time():.1f}s")
    print(f"Dernière irrigation: {db_manager.get_last_irrigation()}")
    
    db_manager.close()
    print("\n✅ DatabaseManager testé avec succès!")