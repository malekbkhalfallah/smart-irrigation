"""
Configuration Firebase pour synchronisation des données
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Gestionnaire Firebase pour synchronisation cloud"""
    
    def __init__(self):
        self.connected = False
        self.db = None
        self._app = None
        self.setup_firebase()
    
    def setup_firebase(self):
        """Configure la connexion Firebase"""
        service_file = "firebase_service_account.json"
        
        if not os.path.exists(service_file):
            logger.warning(f"⚠️ Fichier {service_file} non trouvé - Firebase désactivé")
            return
        
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Vérifier si Firebase est déjà initialisé
            try:
                # Essayer de récupérer une app existante
                self._app = firebase_admin.get_app('irrigation_system')
                logger.info("✅ Utilisation de l'app Firebase existante")
            except ValueError:
                # Initialiser une nouvelle app avec nom unique
                cred = credentials.Certificate(service_file)
                self._app = firebase_admin.initialize_app(cred, name='irrigation_system')
                logger.info("✅ Firebase initialisé avec succès")
                logger.info(f"📡 Projet: {cred.project_id}")
            
            # Obtenir la référence à la base de données
            self.db = firestore.client(app=self._app)
            self.connected = True
            
            logger.info("✅ Firebase connecté avec succès")
            
            # Test de connexion (seulement si pas encore fait)
            try:
                test_ref = self.db.collection("system_status").document("connection_test")
                test_doc = test_ref.get()
                if not test_doc.exists:
                    test_ref.set({
                        "timestamp": datetime.now(),
                        "status": "connected",
                        "device": "raspberry_pi_irrigation",
                        "first_connection": True
                    })
                    logger.info("✅ Test de connexion Firebase réussi")
            except Exception as test_error:
                logger.debug(f"Test de connexion déjà fait: {test_error}")
            
        except Exception as e:
            logger.error(f"❌ Erreur configuration Firebase: {e}")
            self.connected = False
    
    def save_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Sauvegarde les données des capteurs dans Firebase"""
        if not self.connected or not self.db:
            logger.warning("Firebase non connecté - données sauvegardées localement seulement")
            return False
        
        try:
            # Préparer les données
            data_to_save = {
                "timestamp": datetime.now(),
                "device": "raspberry_pi_irrigation",
                "location": "home",
                "sensors": sensor_data.get("sensors", {}),
                "success": sensor_data.get("success", False),
                "local_timestamp": sensor_data.get("timestamp"),
                "sync_source": "raspberry_pi"
            }
            
            # Ajouter à la collection
            doc_ref = self.db.collection("sensor_readings").add(data_to_save)
            
            logger.debug(f"📡 Données capteurs envoyées à Firebase: {doc_ref[1].id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde Firebase capteurs: {e}")
            return False
    
    def save_irrigation_event(self, duration: float, reason: str, 
                            triggered_by: str = "auto") -> bool:
        """Sauvegarde un événement d'irrigation dans Firebase"""
        if not self.connected or not self.db:
            logger.warning("Firebase non connecté - événement sauvegardé localement seulement")
            return False
        
        try:
            event_data = {
                "timestamp": datetime.now(),
                "duration": duration,
                "reason": reason,
                "triggered_by": triggered_by,
                "device": "raspberry_pi_irrigation",
                "status": "completed",
                "sync_source": "raspberry_pi"
            }
            
            self.db.collection("irrigation_events").add(event_data)
            logger.info(f"🚰 Événement irrigation envoyé à Firebase: {duration}s - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde Firebase irrigation: {e}")
            return False
    
    def save_system_status(self, status_data: Dict[str, Any]) -> bool:
        """Sauvegarde le statut système dans Firebase"""
        if not self.connected or not self.db:
            logger.warning("Firebase non connecté - statut sauvegardé localement seulement")
            return False
        
        try:
            # Ajouter des métadonnées
            status_data["timestamp"] = datetime.now()
            status_data["device"] = "raspberry_pi_irrigation"
            status_data["last_update"] = datetime.now()
            status_data["sync_source"] = "raspberry_pi"
            
            # Mettre à jour le document système
            doc_ref = self.db.collection("system_status").document("current")
            doc_ref.set(status_data, merge=True)  # merge=True pour ne pas écraser d'autres champs
            
            logger.debug("📡 Statut système envoyé à Firebase")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde statut système: {e}")
            return False
    
    def get_last_sync(self) -> Optional[datetime]:
        """Récupère la date de la dernière synchronisation"""
        if not self.connected or not self.db:
            return None
        
        try:
            from firebase_admin import firestore
            docs = self.db.collection("sensor_readings")\
                          .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                          .limit(1)\
                          .stream()
            
            for doc in docs:
                data = doc.to_dict()
                timestamp = data.get("timestamp")
                if isinstance(timestamp, datetime):
                    return timestamp
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération dernière synchro: {e}")
        
        return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retourne les informations de connexion Firebase"""
        return {
            "connected": self.connected,
            "project_id": self._get_project_id() if self.connected else None,
            "last_sync": self.get_last_sync(),
            "service_file_exists": os.path.exists("firebase_service_account.json")
        }
    
    def _get_project_id(self) -> Optional[str]:
        """Récupère l'ID du projet depuis le fichier de service"""
        try:
            with open("firebase_service_account.json", "r") as f:
                data = json.load(f)
                return data.get("project_id")
        except:
            return None

# Instance globale unique
firebase_manager = FirebaseManager()

# Test de la connexion uniquement si exécuté directement
if __name__ == "__main__":
    import time
    import sys
    
    # Configurer le logging pour la sortie console
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    print("🧪 TEST FIREBASE CONFIGURATION")
    print("=" * 50)
    
    # Afficher les infos de connexion
    info = firebase_manager.get_system_info()
    
    print(f"📁 Fichier service: {'✅ Trouvé' if info['service_file_exists'] else '❌ Non trouvé'}")
    print(f"🔗 Connecté à Firebase: {'✅ OUI' if info['connected'] else '❌ NON'}")
    
    if info['connected']:
        print(f"📡 Projet: {info['project_id']}")
        print(f"🕒 Dernière synchro: {info['last_sync'] or 'Aucune donnée encore'}")
        
        # Test d'écriture simple
        print("\n📝 Test d'écriture...")
        test_data = {
            "sensors": {
                "dht22": {"temperature": 22.5, "humidity": 65.0},
                "soil": {"moisture_percent": 35.0, "state": "DRY"}
            },
            "success": True,
            "timestamp": time.time()
        }
        
        if firebase_manager.save_sensor_data(test_data):
            print("✅ Test d'écriture réussi!")
            print("✅ Configuration Firebase VALIDÉE!")
        else:
            print("❌ Échec du test d'écriture")
    else:
        print("\n🔧 Actions nécessaires:")
        print("1. Vérifiez que firebase_service_account.json est dans le dossier")
        print("2. Vérifiez que Firestore est activé dans Firebase Console")
        print("3. Exécutez: python3 -c \"import firebase_admin; print('✅ firebase-admin installé')\"")
        
    print("\n" + "=" * 50)
    print("Pour intégrer dans votre système:")
    print("from firebase_config import firebase_manager")
    print("if firebase_manager.connected:")
    print("    firebase_manager.save_sensor_data(vos_donnees)")