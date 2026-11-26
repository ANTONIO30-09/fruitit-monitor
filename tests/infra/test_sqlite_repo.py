import pytest
from datetime import datetime, timezone
from infra.persistence.database import init_db
from infra.persistence.sqlite_repository import SqliteEventRepository
from domain.models.detection import Detection, DomainType
from domain.models.risk_event import RiskEvent
from domain.value_objects.bounding_box import BoundingBox

@pytest.mark.asyncio
async def test_guardar_y_leer_de_sqlite():
    # 1. Inicializamos la BD (crea el archivo data/app.db)
    await init_db()
    
    repo = SqliteEventRepository()
    
    # 2. Creamos un evento falso
    bird = Detection("parrot", 0.9, BoundingBox(10, 10, 20, 20), DomainType.BIRD)
    fruit = Detection("apple", 0.9, BoundingBox(10, 10, 30, 30), DomainType.FRUIT)
    event = RiskEvent(bird, fruit, datetime.now(timezone.utc), "Test DB")
    
    # 3. Guardamos
    await repo.save_event(event)
    
    # 4. Leemos y verificamos
    eventos_db = await repo.get_recent_events(limit=1)
    assert len(eventos_db) == 1
    assert eventos_db[0].bird.class_name == "parrot"
    assert eventos_db[0].fruit.class_name == "apple"
    assert eventos_db[0].bird.bbox.x1 == 10.0
