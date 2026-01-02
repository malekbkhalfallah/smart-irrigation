"""
Gestionnaire d'utilisateurs hors ligne - VERSION COMPLÈTE
"""
import sqlite3
import hashlib
import secrets
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class UserManager:
    """Gestion complète des utilisateurs hors ligne"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = Path(db_path)
        self.initialize_database()
        logger.info(f"✅ UserManager initialisé: {self.db_path}")
    
    def initialize_database(self):
        """Initialise la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    profile_data TEXT DEFAULT '{}',
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Table sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Table plantes utilisateur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_plants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    plant_type TEXT NOT NULL,
                    custom_name TEXT,
                    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Table historique irrigation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS irrigation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration REAL,
                    reason TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation BD: {e}")
            raise
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash sécurisé du mot de passe"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return hashed.hex(), salt
    
    def register_user(self, username: str, password: str, 
                     email: str = None, profile_data: Dict = None) -> Tuple[bool, str, Optional[int]]:
        """Inscription d'un nouvel utilisateur"""
        try:
            # Validation
            username = username.strip()
            if len(username) < 3:
                return False, "Username trop court (min 3 caractères)", None
            if len(password) < 6:
                return False, "Password trop court (min 6 caractères)", None
            
            # Vérifier existence
            if self.user_exists(username):
                return False, "Username déjà pris", None
            
            # Hasher password
            password_hash, salt = self._hash_password(password)
            
            # Profile data
            profile_json = json.dumps(profile_data or {})
            
            # Insérer dans BD
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, profile_data)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, salt, profile_json))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Utilisateur inscrit: {username} (ID: {user_id})")
            return True, "Inscription réussie", user_id
            
        except sqlite3.IntegrityError:
            return False, "Email déjà utilisé", None
        except Exception as e:
            logger.error(f"❌ Erreur inscription: {e}")
            return False, f"Erreur: {str(e)}", None
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """Authentifie un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, profile_data 
                FROM users 
                WHERE username = ? AND is_active = 1
            """, (username.strip(),))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return False, "Utilisateur non trouvé", None
            
            user_id, db_username, email, db_hash, salt, profile_json = row
            
            # Vérifier mot de passe
            test_hash, _ = self._hash_password(password, salt)
            
            if test_hash == db_hash:
                # Mettre à jour dernière connexion
                self._update_last_login(user_id)
                
                # Créer session
                token = self._create_session(user_id)
                
                # Données utilisateur
                user_data = {
                    "id": user_id,
                    "username": db_username,
                    "email": email,
                    "profile": json.loads(profile_json) if profile_json else {},
                    "token": token,
                    "plants": self.get_user_plants(user_id)
                }
                
                logger.info(f"✅ Connexion réussie: {username}")
                return True, "Connexion réussie", user_data
            else:
                return False, "Mot de passe incorrect", None
                
        except Exception as e:
            logger.error(f"❌ Erreur authentification: {e}")
            return False, f"Erreur: {str(e)}", None
    
    def _update_last_login(self, user_id: int):
        """Met à jour la dernière connexion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Erreur update last_login: {e}")
    
    def _create_session(self, user_id: int, duration_hours: int = 24) -> str:
        """Crée une session utilisateur"""
        token = secrets.token_urlsafe(32)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (user_id, token, expires_at)
                VALUES (?, ?, datetime('now', ?))
            """, (user_id, token, f'+{duration_hours} hours'))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Erreur création session: {e}")
        
        return token
    
    def validate_session(self, token: str) -> Optional[Dict]:
        """Valide une session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.id, u.username, u.email
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.token = ? 
                AND s.expires_at > CURRENT_TIMESTAMP
                AND u.is_active = 1
            """, (token,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur validation session: {e}")
            return None
    
    def user_exists(self, username: str) -> bool:
        """Vérifie si un utilisateur existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except Exception as e:
            logger.error(f"❌ Erreur vérification utilisateur: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Récupère un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, profile_data, created_at, last_login
                FROM users WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "profile": json.loads(row[3]) if row[3] else {},
                    "created_at": row[4],
                    "last_login": row[5],
                    "plants": self.get_user_plants(user_id)
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération utilisateur: {e}")
            return None
    
    def get_all_users(self) -> list:
        """Liste tous les utilisateurs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, created_at, last_login
                FROM users 
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "created_at": row[3],
                    "last_login": row[4]
                })
            
            conn.close()
            return users
            
        except Exception as e:
            logger.error(f"❌ Erreur liste utilisateurs: {e}")
            return []
    
    def add_user_plant(self, user_id: int, plant_type: str, custom_name: str = None, notes: str = None) -> bool:
        """Ajoute une plante à un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_plants (user_id, plant_type, custom_name, notes)
                VALUES (?, ?, ?, ?)
            """, (user_id, plant_type, custom_name, notes))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout plante: {e}")
            return False
    
    def get_user_plants(self, user_id: int) -> list:
        """Récupère les plantes d'un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, plant_type, custom_name, added_date, notes
                FROM user_plants 
                WHERE user_id = ?
                ORDER BY added_date DESC
            """, (user_id,))
            
            plants = []
            for row in cursor.fetchall():
                plants.append({
                    "id": row[0],
                    "plant_type": row[1],
                    "custom_name": row[2],
                    "added_date": row[3],
                    "notes": row[4]
                })
            
            conn.close()
            return plants
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération plantes: {e}")
            return []
    
    def log_irrigation(self, user_id: int, duration: float, reason: str = "manual"):
        """Log une irrigation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO irrigation_history (user_id, duration, reason)
                VALUES (?, ?, ?)
            """, (user_id, duration, reason))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Erreur log irrigation: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Statistiques utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total irrigation
            cursor.execute("""
                SELECT COUNT(*), SUM(duration) 
                FROM irrigation_history 
                WHERE user_id = ?
            """, (user_id,))
            
            count, total_duration = cursor.fetchone()
            
            # Dernière irrigation
            cursor.execute("""
                SELECT timestamp, duration, reason
                FROM irrigation_history 
                WHERE user_id = ?
                ORDER BY timestamp DESC 
                LIMIT 1
            """, (user_id,))
            
            last_irrigation = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_irrigations": count or 0,
                "total_water_time": total_duration or 0,
                "last_irrigation": {
                    "timestamp": last_irrigation[0] if last_irrigation else None,
                    "duration": last_irrigation[1] if last_irrigation else 0,
                    "reason": last_irrigation[2] if last_irrigation else None
                },
                "plant_count": len(self.get_user_plants(user_id))
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques: {e}")
            return {}

# Instance globale
user_manager = UserManager()