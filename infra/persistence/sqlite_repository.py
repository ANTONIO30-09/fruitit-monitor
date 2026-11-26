
from typing import List
from sqlalchemy import select
from domain.ports.repository_port import EventRepositoryPort
from domain.models.risk_event import RiskEvent
from domain.models.detection import Detection, DomainType
from domain.value_objects.bounding_box import BoundingBox
from infra.persistence.database import async_session
from infra.persistence.models import RiskEventModel

class SqliteEventRepository(EventRepositoryPort):
    async def save_event(self, event: RiskEvent) -> None:
        async with async_session() as session:
            db_event = RiskEventModel(
                timestamp=event.timestamp, message=event.message,
                bird_class=event.bird.class_name, fruit_class=event.fruit.class_name,
                bird_bbox={"x1": float(event.bird.bbox.x1), "y1": float(event.bird.bbox.y1), "x2": float(event.bird.bbox.x2), "y2": float(event.bird.bbox.y2)},
                fruit_bbox={"x1": float(event.fruit.bbox.x1), "y1": float(event.fruit.bbox.y1), "x2": float(event.fruit.bbox.x2), "y2": float(event.fruit.bbox.y2)},
                danger_score=float(event.danger_score)
            )
            session.add(db_event)
            await session.commit()

    async def get_recent_events(self, limit: int = 10) -> List[RiskEvent]:
        async with async_session() as session:
            result = await session.execute(select(RiskEventModel).order_by(RiskEventModel.timestamp.desc()).limit(limit))
            return [RiskEvent(
                Detection(db.bird_class, 1.0, BoundingBox(**db.bird_bbox), DomainType.BIRD),
                Detection(db.fruit_class, 1.0, BoundingBox(**db.fruit_bbox), DomainType.FRUIT),
                db.timestamp, db.message, db.danger_score
            ) for db in result.scalars().all()]
