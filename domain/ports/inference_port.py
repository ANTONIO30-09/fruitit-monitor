from abc import ABC, abstractmethod
from typing import List
from domain.models.detection import Detection

class InferencePort(ABC):
    """
    Puerto (Interfaz) para los modelos de IA.
    El Dominio no sabe si es YOLO, ONNX o PyTorch. Solo pide detecciones.
    """
    @abstractmethod
    def detect(self, image_bytes: bytes) -> List[Detection]:
        """Recibe una imagen y devuelve una lista de objetos detectados."""
        pass
