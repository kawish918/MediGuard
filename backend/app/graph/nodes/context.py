from typing import Dict
import json
from pathlib import Path
from app.graph.state import MediGuardState

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "patient_history.json"

def context_agent(state: MediGuardState) -> Dict:
    """
    Context Agent:
    Loads past patient records and extracts relevant historical facts.
    """

    transcript = state["transcript"].lower()

    with open(DATA_PATH, "r") as f:
        patient_data = json.load(f)

    relevant_history = []

    for record in patient_data["history"]:
        note_text = record["note"].lower()

        # Simple relevance heuristic (intentionally transparent)
        if any(keyword in transcript for keyword in ["diabetes", "cough", "x-ray", "chest"]):
            relevant_history.append(
                f"{record['date']}: {record['note']}"
            )

    if not relevant_history:
        relevant_history.append("No relevant prior medical history found.")

    return {
        "past_context": "\n".join(relevant_history)
    }