# backend/app/graph/nodes/threat.py

from typing import Dict
from app.graph.state import MediGuardState

def threat_agent(state: MediGuardState) -> Dict:
    """
    Threat Agent:
    Analyzes transcript and image findings for clinical threats.
    """
    threats = []

    transcript_lower = state["transcript"].lower()
    image_findings_lower = state["image_findings"].lower()

    # Check for respiratory risks
    if "shortness of breath" in transcript_lower:
        threats.append("Respiratory risk detected")
    
    if "chest pain" in transcript_lower:
        threats.append("Cardiac evaluation needed")
    
    if "difficulty breathing" in transcript_lower:
        threats.append("Acute respiratory distress")

    # Check imaging findings
    if "opacity" in image_findings_lower:
        threats.append("Possible pneumonia")
    
    if "infiltrate" in image_findings_lower:
        threats.append("Pulmonary infiltrate detected")
    
    if "mass" in image_findings_lower:
        threats.append("Mass lesion requiring immediate follow-up")

    # Check for general urgent terms
    if any(term in transcript_lower for term in ["severe", "acute", "emergency", "urgent"]):
        threats.append("Urgent clinical attention required")

    return {
        "clinical_threats": threats
    }
