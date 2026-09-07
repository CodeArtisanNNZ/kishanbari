from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "model_artifacts" / "soil_risk.joblib"

def model_status() -> dict:
    if not MODEL_PATH.exists():
        return {"loaded": False, "version": None, "message": "No validated model installed; rules-v1 is active."}
    bundle = joblib.load(MODEL_PATH)
    return {"loaded": True, "version": bundle.get("version", "unknown"), "message": "Validated model artifact found."}
