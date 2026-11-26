import cv2
import numpy as np
import onnxruntime as ort
import os
from typing import List
from domain.ports.inference_port import InferencePort
from domain.models.detection import Detection, DomainType
from domain.value_objects.bounding_box import BoundingBox

def calculate_iou(box1, box2):
    x1 = max(box1.x1, box2.x1); y1 = max(box1.y1, box2.y1)
    x2 = min(box1.x2, box2.x2); y2 = min(box1.y2, box2.y2)
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1.x2 - box1.x1) * (box1.y2 - box1.y1)
    area2 = (box2.x2 - box2.x1) * (box2.y2 - box2.y1)
    union = area1 + area2 - intersection
    return intersection / union if union > 0 else 0

def apply_nms(detections: List[Detection], iou_threshold: float = 0.45) -> List[Detection]:
    if not detections: return []
    detections.sort(key=lambda x: x.confidence, reverse=True)
    kept = []
    while detections:
        best = detections.pop(0)
        kept.append(best)
        detections = [d for d in detections if d.class_name != best.class_name or calculate_iou(best.bbox, d.bbox) < iou_threshold]
    return kept

class OnnxInference(InferencePort):
    def __init__(self):
        model_path = "models/best.onnx"
        print(f"🧠 Cargando TU modelo personalizado desde: {model_path}")
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        
        # Las 6 clases exactas de Roboflow
        self.classes = {
            0: "avocado", 1: "grape", 2: "mango", 
            3: "parrot", 4: "thrush", 5: "toucan"
        }
        self.bird_classes = {"parrot", "thrush", "toucan"}

    def _preprocess(self, img, size=(640, 640)):
        img_resized = cv2.resize(img, size)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_batch = np.expand_dims(img_rgb.transpose(2, 0, 1).astype(np.float32) / 255.0, axis=0)
        return img_batch

    def detect(self, image_bytes: bytes) -> List[Detection]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return []

        img_batch = self._preprocess(img)
        outputs = self.session.run(None, {self.input_name: img_batch})[0]
        outputs = np.transpose(np.squeeze(outputs))

        raw_detections = []
        for row in outputs:
            scores = row[4:]
            class_id = int(np.argmax(scores))
            confidence = float(scores[class_id])

            if confidence > 0.45:
                class_name = self.classes.get(class_id, "unknown")
                domain = DomainType.BIRD if class_name in self.bird_classes else DomainType.FRUIT
                
                cx, cy, w, h = row[0], row[1], row[2], row[3]
                bbox = BoundingBox(float(cx-w/2), float(cy-h/2), float(cx+w/2), float(cy+h/2))
                raw_detections.append(Detection(class_name, confidence, bbox, domain))

        return apply_nms(raw_detections, iou_threshold=0.45)
