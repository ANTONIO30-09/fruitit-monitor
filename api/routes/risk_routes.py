from fastapi import APIRouter, UploadFile, File, Depends
from api.dependencies.dependencies import get_analyze_use_case, get_repository_port
from api.dependencies.auth_dep import get_current_user
from application.use_cases.analyze_frame_use_case import AnalyzeFrameUseCase
from api.schemas.risk_schema import AnalyzeResponse

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...), 
    use_case: AnalyzeFrameUseCase = Depends(get_analyze_use_case),
    current_user: str = Depends(get_current_user) # <-- PROTEGIDO
):
    image_bytes = await file.read()
    eventos = await use_case.execute(image_bytes)
    return AnalyzeResponse(events_detected=len(eventos), messages=[e.message for e in eventos])

@router.get("/events")
async def get_recent_events(
    limit: int = 10, 
    repo=Depends(get_repository_port),
    current_user: str = Depends(get_current_user) # <-- PROTEGIDO
):
    eventos = await repo.get_recent_events(limit)
    return [
        {"message": e.message, "time": e.timestamp, "bird": e.bird.class_name, 
         "fruit": e.fruit.class_name, "score": e.danger_score} for e in eventos
    ]
