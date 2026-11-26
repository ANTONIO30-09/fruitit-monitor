from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import os

from infra.persistence.database import init_db
from api.routes import risk_routes, auth_routes, stream_routes, reports_routes
from infra.capture.droidcam_grabber import start_droidcam_stream
from application.use_cases.analyze_frame_use_case import AnalyzeFrameUseCase
from infra.inference.onnx_inference import OnnxInference
from infra.persistence.sqlite_repository import SqliteEventRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    # --- INICIAR CÁMARA EN SEGUNDO PLANO ---
    # IMPORTANTE: Cambia esta IP por la de tu DroidCam
    droidcam_url = os.getenv("DROIDCAM_URL", "http://192.168.1.3:4747/video")
    
    use_case = AnalyzeFrameUseCase(OnnxInference(), SqliteEventRepository())
    # Lanzamos la cámara como tarea asíncrona
    asyncio.create_task(start_droidcam_stream(use_case))
    
    yield

app = FastAPI(title="Fruit-Bird Detector API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("frontend/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

app.include_router(auth_routes.router, prefix="/api/auth")
app.include_router(risk_routes.router, prefix="/api")
app.include_router(stream_routes.router, prefix="/api")
app.include_router(reports_routes.router, prefix="/api/reports") # <-- NUEVO
