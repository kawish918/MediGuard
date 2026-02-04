import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.graph.graph import app

initial_state = {
    "transcript": "Patient reports persistent cough for 5 days.",
    "image_findings": "Chest X-ray shows mild opacity in right lower lobe.",
    "past_context": "",
    "draft_note": "",
    "risk_flags": [],
    "confidence_score": 0.0
}

result = app.invoke(initial_state)

print("\n=== FINAL OUTPUT ===")
print(result["draft_note"])
print("\nRisk Flags:", result["risk_flags"])
print("Confidence Score:", result["confidence_score"])