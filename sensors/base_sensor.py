"""
Classe de base pour les capteurs
"""
from abc import ABC, abstractmethod
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class BaseSensor(ABC):
    """Interface commune pour tous les capteurs"""
    
    def __init__(self, name: str, pin: Optional[int] = None):
        self.name = name
        self.pin = pin
        self.last_value = None
        self.error_count = 0
        self.max_errors = 3
        
    @abstractmethod
    def read(self) -> Optional[Dict[str, Any]]:
        """Lit la valeur du capteur"""
        pass
    
    def read_safe(self) -> Optional[Dict[str, Any]]:
        """Lecture sécurisée avec gestion d'erreurs"""
        try:
            data = self.read()
            if data is not None:
                self.last_value = data
                self.error_count = 0
            else:
                self.error_count += 1
                logger.warning(f"Capteur {self.name} a retourné None")
                
            return data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Erreur lecture capteur {self.name}: {e}")
            return None
    
    def is_healthy(self) -> bool:
        """Vérifie si le capteur est fonctionnel"""
        return self.error_count < self.max_errors