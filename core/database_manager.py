"""
Base de données SQLite locale - VERSION CORRIGÉE
"""
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestion de la base de données SQLite locale - VERSION CORRIGÉE"""
    
    def __init__(self, db_path: str = "irrigation.db"):
        self.db_path = Path(db_path)
        self.initialize_database()
    
    def initialize_database(self):
        """Initialise la base de données avec les bonnes colonnes - CORRIGÉ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table des lectures de capteurs - COLONNES CORRIGÉES
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    soil_moisture REAL,
                    soil_is_dry BOOLEAN,
                    water_level REAL,
                    water_detected BOOLEAN,
                    rain_detected BOOLEAN,
                    temperature REAL,
                    air_humidity REAL,  -- NOM CORRIGÉ (était 'humidity')
                    device_id TEXT DEFAULT 'raspberry_pi'
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
            
            # Table des alertes système
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    message TEXT,
                    sensor_name TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
            """)
            
            conn.commit()
            logger.info(f"✅ Base de données initialisée: {self.db_path}")
            
            # Vérifier les colonnes
            cursor.execute("PRAGMA table_info(sensor_readings)")
            columns = [col[1] for col in cursor.fetchall()]
            logger.info(f"📋 Colonnes table sensor_readings: {columns}")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation BD: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Sauvegarde les données des capteurs - VERSION CORRIGÉE"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sensors = sensor_data.get("sensors", {})
            soil = sensors.get("soil", {})
            water = sensors.get("water", {})
            rain = sensors.get("rain", {})
            dht22 = sensors.get("dht22", {})
            
            # Vérifier que toutes les valeurs sont présentes
            temperature = dht22.get('temperature')
            air_humidity = dht22.get('humidity')  # Note: c'est 'humidity' dans le dict, 'air_humidity' dans la table
            
            cursor.execute("""
                INSERT INTO sensor_readings 
                (soil_moisture, soil_is_dry, water_level, water_detected, 
                 rain_detected, temperature, air_humidity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                soil.get('moisture_percent', 0.0),
                soil.get('is_dry', True),
                water.get('water_percent', 0.0),
                water.get('water_detected', False),
                rain.get('rain_detected', False),
                temperature if temperature is not None else 0.0,
                air_humidity if air_humidity is not None else 0.0
            ))
            
            conn.commit()
            logger.debug("✅ Données capteurs sauvegardées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde données: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    # ... (le reste du code reste identique)
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Sauvegarde les données des capteurs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sensors = sensor_data.get("sensors", {})
            soil = sensors.get("soil", {})
            water = sensors.get("water", {})
            rain = sensors.get("rain", {})
            dht22 = sensors.get("dht22", {})
            
            cursor.execute("""
                INSERT INTO sensor_readings 
                (soil_moisture, soil_is_dry, water_level, water_detected, 
                 rain_detected, temperature, air_humidity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                soil.get('moisture_percent', 0.0),
                soil.get('is_dry', True),
                water.get('water_percent', 0.0),
                water.get('water_detected', False),
                rain.get('rain_detected', False),
                dht22.get('temperature', 0.0),
                dht22.get('humidity', 0.0)
            ))
            
            conn.commit()
            logger.debug("✅ Données capteurs sauvegardées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde données: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def save_irrigation_event(self, duration: float, reason: str, 
                            triggered_by: str = "auto", success: bool = True) -> bool:
        """Sauvegarde un événement d'irrigation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO irrigation_events (duration, reason, triggered_by, success)
                VALUES (?, ?, ?, ?)
            """, (duration, reason, triggered_by, success))
            
            conn.commit()
            logger.info(f"✅ Irrigation sauvegardée: {duration}s - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde irrigation: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def save_alert(self, alert_type: str, message: str, sensor_name: str = None) -> bool:
        """Sauvegarde une alerte système"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_alerts (alert_type, message, sensor_name)
                VALUES (?, ?, ?)
            """, (alert_type, message, sensor_name))
            
            conn.commit()
            logger.warning(f"⚠️ Alerte enregistrée: {alert_type} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde alerte: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_today_irrigation_time(self) -> float:
        """Retourne le temps total d'irrigation aujourd'hui"""
        try:
            conn = sqlite3.connect(self.db_path)
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
        finally:
            if conn:
                conn.close()
    
    def get_recent_sensor_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les dernières lectures de capteurs"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT * FROM sensor_readings 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def cleanup_old_data(self, days_to_keep: int = 7) -> int:
        """Nettoie les vieilles données pour gagner de l'espace"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Supprimer les données de capteurs vieilles de plus de X jours
            cursor.execute("""
                DELETE FROM sensor_readings 
                WHERE timestamp < datetime('now', ?)
            """, (f'-{days_to_keep} days',))
            
            deleted_rows = cursor.rowcount
            
            # Supprimer les événements d'irrigation vieux
            cursor.execute("""
                DELETE FROM irrigation_events 
                WHERE timestamp < datetime('now', ?)
            """, (f'-{days_to_keep} days',))
            
            deleted_rows += cursor.rowcount
            
            # Marquer les anciennes alertes comme résolues
            cursor.execute("""
                UPDATE system_alerts 
                SET resolved = 1 
                WHERE timestamp < datetime('now', ?)
            """, (f'-{days_to_keep} days',))
            
            conn.commit()
            logger.info(f"🧹 Données nettoyées: {deleted_rows} lignes supprimées")
            return deleted_rows
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage données: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    def close(self):
        """Ferme proprement la connexion"""
        logger.info("🔒 Base de données fermée")

# Instance globale
db_manager = DatabaseManager()