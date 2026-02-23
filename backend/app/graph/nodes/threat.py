# backend/app/graph/nodes/threat.py

from typing import Dict
from app.graph.state import MediGuardState

def threat_agent(state: MediGuardState) -> Dict:
    """
    Threat Agent:
    Already computed by Kaggle MedGemma - just pass through.
    Kaggle agent detects clinical risks using AI.
    """
    # Threats already loaded by scribe from Kaggle JSON
    # This agent just passes them through unchanged
    return {
        "clinical_threats": state.get("clinical_threats", [])
    }
