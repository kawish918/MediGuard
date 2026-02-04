# state.py
from typing import TypedDict, List, Dict

class MediGuardState(TypedDict):
    transcript: str
    image_findings: str
    past_context: str
    draft_note: str
    risk_flags: List[str]
    confidence_score: float
    clinical_threats: List[str]
    confidence_detail: Dict[str, float]
    hallucination_risk: bool