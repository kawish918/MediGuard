from typing import Dict, List
import re
from app.graph.state import MediGuardState

def guard_agent(state: MediGuardState) -> Dict:
    """
    Observability / Guard Agent:
    Detects contradictions, assigns per-section confidence score, and flags hallucinations.
    """

    transcript = state["transcript"].lower()
    draft_note = state["draft_note"].lower()
    past_context = state["past_context"].lower()
    image_findings = state["image_findings"].lower()

    risk_flags: List[str] = []
    hallucination_risk = False
    
    # Parse SOAP sections from draft note
    sections = {
        "subjective": "",
        "objective": "",
        "assessment": "",
        "plan": ""
    }
    
    # Extract SOAP sections
    soap_pattern = r"(subjective|objective|assessment|plan):\s*([^\n]+(?:\n(?!(?:subjective|objective|assessment|plan):)[^\n]+)*)"
    matches = re.findall(soap_pattern, draft_note, re.IGNORECASE)
    for section_name, content in matches:
        sections[section_name.lower()] = content.strip()
    
    # Initialize section confidence scores
    confidence_detail = {
        "subjective": 1.0,
        "objective": 1.0,
        "assessment": 1.0,
        "plan": 1.0
    }
    
    # Subjective validation
    if sections["subjective"]:
        # Check if subjective matches transcript
        if "cough" in transcript and "cough" not in sections["subjective"]:
            risk_flags.append("Subjective: Patient symptom 'cough' from transcript missing")
            confidence_detail["subjective"] -= 0.2
        if "pain" in transcript and "pain" not in sections["subjective"]:
            risk_flags.append("Subjective: Patient complaint 'pain' from transcript missing")
            confidence_detail["subjective"] -= 0.2
    
    # Objective validation
    if sections["objective"]:
        # Check consistency with image findings
        if "opacity" in image_findings and "opacity" not in sections["objective"]:
            risk_flags.append("Objective: Imaging finding 'opacity' not documented")
            confidence_detail["objective"] -= 0.25
        if "clear" in sections["objective"] and "opacity" in image_findings:
            risk_flags.append("Objective: Contradicts imaging findings")
            confidence_detail["objective"] -= 0.3
            hallucination_risk = True
    
    # Assessment validation
    if sections["assessment"]:
        # Check against past context
        if "no diabetes" in sections["assessment"] and "diabetes" in past_context:
            risk_flags.append("Assessment: Contradicts past medical history (diabetes)")
            confidence_detail["assessment"] -= 0.3
            hallucination_risk = True
        # Check if assessment is supported by findings
        if len(sections["assessment"]) < 10:
            confidence_detail["assessment"] -= 0.15
    
    # Plan validation
    if sections["plan"]:
        # Check if plan addresses findings
        if "opacity" in image_findings and "follow" not in sections["plan"]:
            risk_flags.append("Plan: Missing follow-up for imaging abnormality")
            confidence_detail["plan"] -= 0.2
    
    # Overall confidence rules
    overall_confidence = 1.0
    
    # Rule 1: Diabetes contradiction
    if "no diabetes" in draft_note and "diabetes" in past_context:
        risk_flags.append(
            "Contradiction: Note states 'no diabetes' but past records indicate Type 2 Diabetes"
        )
        overall_confidence -= 0.3
        hallucination_risk = True

    # Rule 2: Imaging mismatch
    if "lungs clear" in draft_note and "opacity" in past_context:
        risk_flags.append(
            "Imaging mismatch: Draft note states lungs are clear, but prior imaging showed opacity"
        )
        overall_confidence -= 0.3
        hallucination_risk = True

    # Rule 3: Symptom omission
    if "cough" in transcript and "cough" not in draft_note:
        risk_flags.append(
            "Omission: Persistent cough mentioned in transcript but missing from clinical note"
        )
        overall_confidence -= 0.2
    
    # Clamp confidence scores
    for section in confidence_detail:
        confidence_detail[section] = max(0.0, min(1.0, confidence_detail[section]))
    
    overall_confidence = max(overall_confidence, 0.0)

    return {
        "risk_flags": risk_flags,
        "confidence_score": round(overall_confidence, 2),
        "confidence_detail": {k: round(v, 2) for k, v in confidence_detail.items()},
        "hallucination_risk": hallucination_risk
    }