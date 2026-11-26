from domain.ports.inference_port import InferencePort
from domain.ports.repository_port import EventRepositoryPort
from domain.models.risk_event import RiskEvent
from domain.services.risk_analyzer import RiskAnalyzer
from typing import List

class AnalyzeFrameUseCase:
    def __init__(self, inference_port: InferencePort, repository_port: EventRepositoryPort):
        self.inference = inference_port
        self.repo = repository_port

    async def execute(self, image_bytes: bytes) -> List[RiskEvent]:
        detections = self.inference.detect(image_bytes)
        risk_events = RiskAnalyzer.analyze_frame(detections)
        for event in risk_events:
            await self.repo.save_event(event)
        return risk_events
