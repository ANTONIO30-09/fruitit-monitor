from pydantic import BaseModel
from typing import List, Dict, Any

class RiskEventResponse(BaseModel):
    id: str
    message: str
    bird_class: str
    fruit_class: str
    
class AnalyzeResponse(BaseModel):
    events_detected: int
    messages: List[str]
