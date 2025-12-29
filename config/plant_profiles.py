"""
Profils de plantes prédéfinis
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class PlantProfile:
    name: str
    soil_type: str
    min_moisture: float
    max_moisture: float
    water_needs: str  # "Low", "Medium", "High"
    description: str

PLANT_PROFILES: Dict[str, PlantProfile] = {
    "tomato": PlantProfile(
        name="Tomate",
        soil_type="Argileux",
        min_moisture=40.0,
        max_moisture=80.0,
        water_needs="Medium",
        description="Nécessite un sol bien drainé et régulièrement humide."
    ),
    "cactus": PlantProfile(
        name="Cactus",
        soil_type="Sableux",
        min_moisture=10.0,
        max_moisture=30.0,
        water_needs="Low",
        description="Arrosage minimal, sol doit sécher complètement entre les arrosages."
    ),
    "lettuce": PlantProfile(
        name="Laitue",
        soil_type="Humifère",
        min_moisture=60.0,
        max_moisture=85.0,
        water_needs="High",
        description="Nécessite un sol constamment humide mais pas détrempé."
    ),
    "rose": PlantProfile(
        name="Rose",
        soil_type="Limonneux",
        min_moisture=50.0,
        max_moisture=75.0,
        water_needs="Medium",
        description="Arrosage profond mais peu fréquent."
    )
}

def get_plant_profile(plant_name: str) -> PlantProfile:
    """Retourne le profil d'une plante"""
    return PLANT_PROFILES.get(plant_name.lower(), PLANT_PROFILES["tomato"])