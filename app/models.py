from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .database import Base

class Matter(Base):
    __tablename__ = "matters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    client_name = Column(String(150), nullable=True)
    practice_area = Column(String(100), nullable=True)
    priority = Column(String(50), nullable=True)
    ai_summary = Column(Text, nullable=True)
    suggested_next_step = Column(Text, nullable=True)
    knowledge_source = Column(String(255), nullable=True)
    status = Column(String(50), default="New")
    created_at = Column(DateTime, default=datetime.utcnow)
