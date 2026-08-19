from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class MatterCreate(BaseModel):
    title: str
    description: str
    client_name: Optional[str] = None

class MatterStatusUpdate(BaseModel):
    status: str

class MatterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    client_name: Optional[str] = None
    practice_area: Optional[str] = None
    priority: Optional[str] = None
    ai_summary: Optional[str] = None
    suggested_next_step: Optional[str] = None
    knowledge_source: Optional[str] = None
    status: str
    created_at: datetime
