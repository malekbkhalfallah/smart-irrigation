"""
Gestion de la détection réseau (online/offline)
"""
import time
import socket
import requests
import logging
from typing import Dict, Any
from config.settings import config

logger = logging.getLogger(__name__)

class NetworkManager:
    """Gère la détection de l'état réseau"""
    
    def __init__(self):
        self.last_check = 0
        self.check_interval = 60  # Vérifier toutes les minutes
        self.is_online = False
        self.consecutive_failures = 0
        self.max_failures = 3
        
        # Initialiser avec une vérification
        self.check_network_status()
    
    def check_network_status(self, force: bool = False) -> bool:
        """Vérifie si le système est en ligne"""
        current_time = time.time()
        
        # Vérifier le cache
        if not force and current_time - self.last_check < self.check_interval:
            return self.is_online
        
        self.last_check = current_time
        
        # Essayer plusieurs méthodes de vérification
        online = False
        
        # Méthode 1: Ping Google DNS
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            online = True
        except OSError:
            pass
        
        # Méthode 2: Requête HTTP simple
        if not online:
            try:
                response = requests.get("http://www.google.com", timeout=5)
                online = response.status_code < 400
            except:
                pass
        
        # Méthode 3: Vérifier la connexion locale
        if not online:
            try:
                # Vérifier la connexion réseau locale
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.connect(("8.8.8.8", 80))
                online = True
                sock.close()
            except:
                pass
        
        # Mettre à jour l'état
        if online:
            self.consecutive_failures = 0
            if not self.is_online:
                logger.info("🌐 Système maintenant EN LIGNE")
        else:
            self.consecutive_failures += 1
            if self.is_online:
                logger.info("📴 Système maintenant HORS LIGNE")
        
        self.is_online = online
        config.offline_mode = not online
        
        # Mettre à jour la LED blanche
        from core.gpio_manager import gpio_central
        gpio_central.set_led_white(online)
        
        return online
    
    def get_network_info(self) -> Dict[str, Any]:
        """Retourne les informations réseau"""
        info = {
            "is_online": self.is_online,
            "last_check": self.last_check,
            "consecutive_failures": self.consecutive_failures,
            "check_interval": self.check_interval
        }
        
        # Ajouter l'adresse IP si disponible
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info["local_ip"] = s.getsockname()[0]
            s.close()
        except:
            info["local_ip"] = "Inconnue"
        
        return info
    
    def wait_for_connection(self, timeout: int = 30) -> bool:
        """Attend une connexion réseau"""
        logger.info(f"⌛ Attente connexion réseau (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_network_status(force=True):
                logger.info("✅ Connexion réseau établie")
                return True
            time.sleep(2)
        
        logger.warning("❌ Timeout d'attente connexion réseau")
        return False

# Instance globale
network_manager = NetworkManager()