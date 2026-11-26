from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import numpy as np
import asyncio
from infra.capture import droidcam_grabber
from infra.messaging.ws_manager import manager

router = APIRouter()

_, empty_buffer = cv2.imencode('.jpg', np.zeros((480, 640, 3), dtype=np.uint8))
EMPTY_FRAME = empty_buffer.tobytes()

class CameraConfig(BaseModel):
    ip: str
    port: str
    action: str # "start" o "stop"

async def generate_video():
    while True:
        if droidcam_grabber.camera_active and droidcam_grabber.latest_annotated_frame is not None:
            _, buffer = cv2.imencode('.jpg', droidcam_grabber.latest_annotated_frame)
            frame_bytes = buffer.tobytes()
        else:
            frame_bytes = EMPTY_FRAME
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        await asyncio.sleep(0.1)

@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_video(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/camera/config")
async def config_camera(config: CameraConfig):
    if config.action == "stop":
        droidcam_grabber.stop_camera()
        return {"status": "stopped"}
    else:
        url = f"http://{config.ip}:{config.port}/video"
        droidcam_grabber.start_camera(url)
        return {"status": "started", "url": url}

@router.get("/camera/status")
async def camera_status():
    return {
        "active": droidcam_grabber.camera_active,
        "url": droidcam_grabber.current_url
    }

@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
