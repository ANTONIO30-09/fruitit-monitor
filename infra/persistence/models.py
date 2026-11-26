import uuid
from sqlalchemy import Column, String, DateTime, JSON, Float
from infra.persistence.database import Base

class RiskEventModel(Base):
    __tablename__ = "risk_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, nullable=False)
    message = Column(String, nullable=False)
    bird_class = Column(String, nullable=False)
    fruit_class = Column(String, nullable=False)
    bird_bbox = Column(JSON, nullable=False)
    fruit_bbox = Column(JSON, nullable=False)
    danger_score = Column(Float, nullable=False)

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
