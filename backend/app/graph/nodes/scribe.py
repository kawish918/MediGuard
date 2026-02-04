# backend/app/graph/nodes/scribe.py

from typing import Dict
from app.graph.state import MediGuardState
from app.models.medgemma import medgemma_generate

def scribe_agent(state: MediGuardState) -> Dict:
    transcript = state["transcript"]
    image_findings = state["image_findings"]

    prompt = f"""
You are an expert medical scribe.

Transcript:
{transcript}

Image Findings:
{image_findings}

Task:
Convert the above information into a structured SOAP note.
Do NOT infer information not explicitly stated.
Be precise and clinical.
"""

    draft_note = medgemma_generate(prompt)

    return {
        "draft_note": draft_note
    }