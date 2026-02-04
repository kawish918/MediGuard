# backend/app/db/models.py

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional, List, Dict
import uuid

class Session(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    transcript: str
    image_findings: str
    draft_note: str
    past_context: str = ""
    risk_flags: List[str] = Field(default=[], sa_column=Column(JSON))
    confidence_score: float = 0.0
    confidence_detail: Dict[str, float] = Field(default={}, sa_column=Column(JSON))
    clinical_threats: List[str] = Field(default=[], sa_column=Column(JSON))
    hallucination_risk: bool = False
