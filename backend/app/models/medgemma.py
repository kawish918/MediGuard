# backend/app/models/medgemma.py

def medgemma_generate(prompt: str) -> str:
    """
    Temporary stub for MedGemma.
    This will be replaced with the real MedGemma inference call.
    """

    # VERY SIMPLE MOCK OUTPUT
    return f"""
SOAP NOTE (Mocked Output)

Subjective:
Patient reports symptoms as described in the transcript.

Objective:
Findings based on provided imaging and observations.

Assessment:
Clinical assessment pending further verification.

Plan:
Recommend follow-up and additional tests if required.

---
MODEL PROMPT USED:
{prompt[:300]}...
"""