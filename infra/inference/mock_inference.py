import random
from typing import List
from domain.ports.inference_port import InferencePort
from domain.models.detection import Detection, DomainType
from domain.value_objects.bounding_box import BoundingBox

class MockInference(InferencePort):
    """Simula la IA para probar el backend sin necesidad del modelo ONNX real."""
    def detect(self, image_bytes: bytes) -> List[Detection]:
        # Simulamos que el 70% de las veces la IA ve un loro atacando una manzana
        if random.random() > 0.3:
            return [
                Detection("apple", 0.90, BoundingBox(50, 50, 100, 100), DomainType.FRUIT),
                Detection("parrot", 0.85, BoundingBox(60, 60, 90, 90), DomainType.BIRD)
            ]
        return [] # A veces no ve nada
