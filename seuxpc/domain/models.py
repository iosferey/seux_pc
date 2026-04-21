from dataclasses import dataclass
from typing import Dict

@dataclass
class Site:
    url: str
    cultural_vector: Dict[str, float]

@dataclass
class Result:
    UX_base: float
    UX_cultural: float
    IVS: float
    SEUX_PC: float
    Gap: float