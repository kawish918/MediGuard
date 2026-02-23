import json
from pathlib import Path

# Use absolute path relative to this module file
KAGGLE_OUTPUT_PATH = Path(__file__).parent.parent / "data" / "mediguard_output.json"

def load_kaggle_output():
    if not KAGGLE_OUTPUT_PATH.exists():
        raise FileNotFoundError(f"Kaggle output file not found at: {KAGGLE_OUTPUT_PATH}")

    with open(KAGGLE_OUTPUT_PATH, "r") as f:
        return json.load(f)
