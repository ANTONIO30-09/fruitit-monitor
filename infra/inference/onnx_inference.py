from infra.inference.ensemble_detector import EnsembleDetector

class OnnxInference:
    def __init__(self, model_path="models/best.onnx"):
        # Ignoramos el modelo_path por defecto y cargamos la fusión de los dos modelos
        self.detector = EnsembleDetector([
            "models/best.onnx",
            "models/fruit/yolo_fruits_and_vegetables_v1.pt"
        ])

    def detect(self, image, conf_threshold=0.4):
        return self.detector.detect(image, conf_threshold)

    def predict(self, image, conf_threshold=0.4):
        return self.detect(image, conf_threshold)
