from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from api.dependencies.dependencies import get_repository_port
from api.dependencies.auth_dep import get_current_user
import pandas as pd
import io
from datetime import datetime

router = APIRouter()

def get_time_block(dt: datetime) -> str:
    hour = dt.hour
    if 6 <= hour < 12: return "Mañana"
    elif 12 <= hour < 19: return "Tarde"
    else: return "Noche"

@router.get("/data")
async def get_report_data(repo=Depends(get_repository_port), current_user: str = Depends(get_current_user)):
    eventos = await repo.get_recent_events(limit=100)
    return [{
        "Hora": e.timestamp.strftime("%H:%M:%S"),
        "Bloque": get_time_block(e.timestamp),
        "Especie": e.bird.class_name.upper(),
        "Cultivo": e.fruit.class_name.upper(),
        "Riesgo": round(e.danger_score, 2),
        "Estado": "ATAQUE 🚨" if e.danger_score >= 0.75 else "MERODEO ⚠️"
    } for e in eventos]

@router.get("/export/excel")
async def export_excel(repo=Depends(get_repository_port), current_user: str = Depends(get_current_user)):
    eventos = await repo.get_recent_events(limit=1000)
    datos = [{
        "Fecha": e.timestamp.strftime("%Y-%m-%d"),
        "Hora": e.timestamp.strftime("%H:%M:%S"),
        "Bloque Horario": get_time_block(e.timestamp),
        "Especie": e.bird.class_name.upper(),
        "Cultivo": e.fruit.class_name.upper(),
        "Score": round(e.danger_score, 2),
        "Estado": "ATAQUE" if e.danger_score >= 0.75 else "MERODEO"
    } for e in eventos]
    
    df = pd.DataFrame(datos)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte_Aves')
    output.seek(0)
    return StreamingResponse(
        output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Reporte_Fruitit.xlsx"}
    )
