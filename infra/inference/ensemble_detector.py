from ultralytics import YOLO

class EnsembleDetector:
    def __init__(self, model_paths):
        print(f"Cargando {len(model_paths)} modelos en el ensemble...")
        # Cargamos best.onnx y el modelo de frutas .pt
        self.models = [YOLO(path, task='detect') for path in model_paths]
        
        # Mapeo exacto de todas las clases al sistema de tu app
        self.class_mapping = {
            # Aves (del modelo original best.onnx)
            'thrush': 'thrush_blackbird', 'blackbird': 'thrush_blackbird',
            'sparrow': 'sparrow_finch', 'finch': 'sparrow_finch',
            'woodpecker': 'woodpecker', 'parrot': 'parrot', 'toucan': 'toucan',
            'tanager': 'tanager_frutero', 'frutero': 'tanager_frutero',
            'starling': 'starling_tordo', 'tordo': 'starling_tordo',
            
            # Frutas (del modelo original y del modelo de 63 clases)
            'mango': 'mango', 'avocado': 'avocado', 'grape': 'grape', 
            'cherry': 'cherry', 'apple': 'apple', 'peach': 'peach', 'pear': 'pear',
            'fig': 'fig', 'fig/fig fruit': 'fig',
            'mandarin orange': 'citrus', 'orange/orange fruit': 'citrus',
            'lemon': 'citrus', 'lime': 'citrus', 'clementine': 'citrus',
            'strawberry': 'berry', 'blackberry': 'berry', 'blueberry': 'berry', 'raspberry': 'berry'
        }

    def detect(self, image, conf_threshold=0.4):
        all_detections = []
        for model in self.models:
            results = model(image, conf=conf_threshold, verbose=False)
            for r in results:
                for box in r.boxes:
                    xyxy = box.xyxy[0].cpu().numpy().tolist()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    original_name = model.names[cls_id].lower().strip()
                    
                    mapped_name = self.class_mapping.get(original_name)
                    if mapped_name:
                        all_detections.append({
                            'class_name': mapped_name,
                            'confidence': conf,
                            'bbox': xyxy
                        })
        return all_detections
