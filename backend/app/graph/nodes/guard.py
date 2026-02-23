from typing import Dict, List
from app.graph.state import MediGuardState

def guard_agent(state: MediGuardState) -> Dict:
    """
    Guard Agent:
    Already computed by Kaggle MedGemma - just pass through.
    Kaggle agent detects hallucinations and assigns confidence using AI.
    """
    # Guard outputs already loaded by scribe from Kaggle JSON
    # This agent just passes them through unchanged
    return {
        "confidence_score": state.get("confidence_score", 0.85),
        "confidence_detail": state.get("confidence_detail", {
            "subjective": 0.85,
            "objective": 0.85,
            "assessment": 0.85,
            "plan": 0.85
        }),
        "hallucination_risk": state.get("hallucination_risk", False),
        "risk_flags": []  # Can be enhanced later if needed
    }