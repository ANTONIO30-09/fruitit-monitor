import pytest
from domain.models.detection import Detection, DomainType
from domain.value_objects.bounding_box import BoundingBox
from domain.models.risk_event import RiskEvent
from application.use_cases.analyze_frame_use_case import AnalyzeFrameUseCase
from domain.ports.inference_port import InferencePort
from domain.ports.repository_port import EventRepositoryPort

class FakeInference(InferencePort):
    def __init__(self, detections):
        self.detections = detections
    def detect(self, image_bytes: bytes):
        return self.detections

class FakeRepository(EventRepositoryPort):
    def __init__(self):
        self.events = []
    async def save_event(self, event: RiskEvent) -> None:
        self.events.append(event)
    async def get_recent_events(self, limit: int = 10):
        return self.events[:limit]

@pytest.mark.asyncio
async def test_flujo_completo_detecta_y_guarda():
    # Coordenadas ajustadas al Z-ratio real
    fruta = Detection("apple", 0.9, BoundingBox(10, 10, 60, 60), DomainType.FRUIT)
    loro = Detection("parrot", 0.8, BoundingBox(0, 0, 190, 190), DomainType.BIRD)
    
    fake_ia = FakeInference([fruta, loro])
    fake_db = FakeRepository()
    
    use_case = AnalyzeFrameUseCase(inference_port=fake_ia, repository_port=fake_db)
    alertas = await use_case.execute(b"imagen_falsa.jpg")
    
    assert len(alertas) == 1
    assert len(fake_db.events) == 1
    assert fake_db.events[0].bird.class_name == "parrot"
