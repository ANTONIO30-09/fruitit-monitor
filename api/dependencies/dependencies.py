from infra.inference.onnx_inference import OnnxInference
from infra.persistence.sqlite_repository import SqliteEventRepository
from application.use_cases.analyze_frame_use_case import AnalyzeFrameUseCase

# Instancia global del modelo ONNX (se carga una sola vez al arrancar el servidor)
_model_instance = None

def get_inference_port() -> OnnxInference:
    global _model_instance
    if _model_instance is None:
        _model_instance = OnnxInference()
    return _model_instance

def get_repository_port() -> SqliteEventRepository:
    return SqliteEventRepository()

def get_analyze_use_case() -> AnalyzeFrameUseCase:
    return AnalyzeFrameUseCase(
        inference_port=get_inference_port(),
        repository_port=get_repository_port()
    )
