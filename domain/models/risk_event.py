from dataclasses import dataclass
from datetime import datetime
from domain.models.detection import Detection

@dataclass(frozen=True)
class RiskEvent:
    bird: Detection
    fruit: Detection
    timestamp: datetime
    message: str
    danger_score: float = 0.0
