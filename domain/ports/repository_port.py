from abc import ABC, abstractmethod
from typing import List
from domain.models.risk_event import RiskEvent

class EventRepositoryPort(ABC):
    @abstractmethod
    async def save_event(self, event: RiskEvent) -> None:
        pass

    @abstractmethod
    async def get_recent_events(self, limit: int = 10) -> List[RiskEvent]:
        pass
