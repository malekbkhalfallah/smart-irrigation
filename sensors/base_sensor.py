"""
Classe de base pour tous les capteurs - UTILISE GPIO CENTRAL
"""
from abc import ABC, abstractmethod
import logging
from typing import Optional, Dict, Any
import time
from core.gpio_manager import gpio_central

logger = logging.getLogger(__name__)

class BaseSensor(ABC):
    """Interface commune pour tous les capteurs - UTILISE GPIO CENTRAL"""
    
    def __init__(self, name: str, pin: int):
        self.name = name
        self.pin = pin
        self.last_value = None
        self.error_count = 0
        self.max_errors = 3
        self.last_read_time = 0
        self.read_interval = 2
    
    @abstractmethod
    def read_raw(self) -> Optional[Dict[str, Any]]:
        """
        Méthode abstraite - doit être implémentée par chaque capteur
        Lit la valeur brute du capteur
        Returns: dictionnaire avec les données ou None en cas d'erreur
        """
        pass
    
    def read(self) -> Optional[Dict[str, Any]]:
        """
        Lecture avec gestion de cache et intervalle minimum
        Utilise le GPIO central pour la lecture
        """
        current_time = time.time()
        
        # Si on a déjà lu récemment, retourne la dernière valeur
        if (self.last_value is not None and 
            current_time - self.last_read_time < self.read_interval):
            return self.last_value
            
        try:
            # Lecture de la valeur brute du capteur
            data = self.read_raw()
            
            if data is not None:
                # Ajout du timestamp à la donnée
                data['timestamp'] = current_time
                # Mise en cache
                self.last_value = data
                self.last_read_time = current_time
                # Réinitialisation du compteur d'erreurs
                self.error_count = 0
                logger.debug(f"Capteur {self.name} lu: {data}")
            else:
                # Incrémentation en cas de valeur None
                self.error_count += 1
                logger.warning(f"Capteur {self.name} a retourné None (erreur {self.error_count}/{self.max_errors})")
                
            return data
            
        except Exception as e:
            # Gestion des exceptions
            self.error_count += 1
            logger.error(f"Erreur lecture capteur {self.name}: {str(e)} (erreur {self.error_count}/{self.max_errors})")
            return None
    
    def is_healthy(self) -> bool:
        """
        Vérifie si le capteur est fonctionnel
        Returns: True si moins de max_errors erreurs
        """
        return self.error_count < self.max_errors
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retourne le statut du capteur
        """
        return {
            "name": self.name,
            "pin": self.pin,
            "healthy": self.is_healthy(),
            "error_count": self.error_count,
            "last_value": self.last_value,
            "last_read_time": self.last_read_time
        }
    
    def cleanup(self):
        """
        Nettoyage des ressources
        NOTE: Le GPIO est géré centralement, donc pas de cleanup nécessaire ici
        """
        pass