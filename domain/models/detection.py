from dataclasses import dataclass
from enum import Enum
from domain.value_objects.bounding_box import BoundingBox

class DomainType(str, Enum):
    FRUIT = "fruit"
    BIRD = "bird"

@dataclass(frozen=True)
class Detection:
    """Representa un objeto detectado por la IA (un ave o una fruta)."""
    class_name: str
    confidence: float
    bbox: BoundingBox
    domain_type: DomainType
