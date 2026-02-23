# backend/app/graph/nodes/scribe.py

from typing import Dict
from app.graph.state import MediGuardState
from app.models.kaggle_adapter import load_kaggle_output

def scribe_agent(state: MediGuardState) -> Dict:
    """
    Loads complete agent outputs from Kaggle GPU inference.
    All AI agents (Scribe, Guard, Threat) run on Kaggle with MedGemma.
    Backend just loads and displays results.
    """
    kaggle_data = load_kaggle_output()
    agents = kaggle_data.get("agents", {})
    
    # Extract outputs from each agent
    scribe_output = agents.get("scribe", {})
    guard_output = agents.get("guard", {})
    threat_output = agents.get("threat", {})
    
    return {
        "draft_note": scribe_output.get("draft_note", ""),
        "confidence_score": guard_output.get("confidence_score", 0.85),
        "hallucination_risk": guard_output.get("hallucination_risk", False),
        "clinical_threats": [t.get("condition", "") for t in threat_output.get("clinical_threats", [])],
        "confidence_detail": {
            "subjective": guard_output.get("confidence_score", 0.85),
            "objective": guard_output.get("confidence_score", 0.85),
            "assessment": guard_output.get("confidence_score", 0.85),
            "plan": guard_output.get("confidence_score", 0.85)
        }
    }