import cv2
import asyncio
import threading
import time
from application.use_cases.analyze_frame_use_case import AnalyzeFrameUseCase
from domain.services.risk_analyzer import RiskAnalyzer
from infra.messaging.ws_manager import manager

latest_frame = None
latest_annotated_frame = None  # <-- Video con cajas dibujadas
camera_active = False
current_url = "http://192.168.1.3:4747/video"
_capture_thread = None

def capture_worker(url: str):
    global latest_frame, camera_active
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        print(f"❌ ERROR: No se pudo abrir la cámara en {url}")
        camera_active = False
        return
        
    print(f"✅ Hilo de captura iniciado para {url}")
    while camera_active:
        ret, frame = cap.read()
        if ret:
            latest_frame = frame
        else:
            time.sleep(0.1)
    cap.release()
    latest_frame = None
    latest_annotated_frame = None
    print("🛑 Cámara desconectada.")

def start_camera(url: str):
    global camera_active, current_url, _capture_thread
    if camera_active: return
    current_url = url
    camera_active = True
    _capture_thread = threading.Thread(target=capture_worker, args=(url,), daemon=True)
    _capture_thread.start()

def stop_camera():
    global camera_active
    camera_active = False

async def start_droidcam_stream(use_case: AnalyzeFrameUseCase):
    global current_url, latest_frame, latest_annotated_frame
    start_camera(current_url)

    while True:
        await asyncio.sleep(1.0) # Analizar 1 vez por segundo
        if camera_active and latest_frame is not None:
            _, buffer = cv2.imencode('.jpg', latest_frame)
            image_bytes = buffer.tobytes()
            
            try:
                # 1. Detectar objetos
                detections = use_case.inference.detect(image_bytes)
                
                # 2. Dibujar cajas (Verde para aves, Rojo para frutas)
                annotated = latest_frame.copy()
                for det in detections:
                    x1, y1, x2, y2 = int(det.bbox.x1), int(det.bbox.y1), int(det.bbox.x2), int(det.bbox.y2)
                    color = (0, 255, 0) if det.domain_type.value == "bird" else (0, 0, 255)
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    label = f"{det.class_name} {det.confidence:.2f}"
                    cv2.putText(annotated, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                latest_annotated_frame = annotated

                # 3. Analizar riesgo y guardar
                events = RiskAnalyzer.analyze_frame(detections)
                if events:
                    print(f"🚨 ¡{len(events)} Alerta(s) guardada(s)!")
                    for event in events:
                        await use_case.repo.save_event(event)
                        payload = {
                            "type": "new_alert",
                            "message": event.message,
                            "bird": event.bird.class_name,
                            "fruit": event.fruit.class_name,
                            "score": round(event.danger_score, 2)
                        }
                        await manager.broadcast(payload)
            except Exception as e:
                print(f"❌ Error procesando frame: {e}")
