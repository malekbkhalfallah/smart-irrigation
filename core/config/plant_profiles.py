# core/config/plant_profile.py
from dataclasses import dataclass


@dataclass
class PlantProfile:
    name: str
    soil_type: str
    min_moisture: float
    max_moisture: float
    optimal_moisture: float


TOMATO = PlantProfile(
    name="Tomato",
    soil_type="Loam",
    min_moisture=40.0,
    max_moisture=80.0,
    optimal_moisture=50,
)
