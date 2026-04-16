import json
import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / "models" / "placement_model.pkl"

# Singleton load
_model = None

def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_placement(cgpa, internships, projects, certificates, aptitude_score):
    """
    Returns the placement probability as a percentage (0.0 to 100.0)
    """
    model = get_model()
    
    # Input must match the exact feature order during training:
    # ["CGPA", "Internships", "Projects", "Certificates", "AptitudeTestScore"]
    input_data = pd.DataFrame([{
        "CGPA": float(cgpa),
        "Internships": int(internships),
        "Projects": int(projects),
        "Certificates": int(certificates),
        "AptitudeTestScore": float(aptitude_score)
    }])
    
    if hasattr(model, "predict_proba"):
        # probability of class 1
        prob = model.predict_proba(input_data)[0][1]
        return round(prob * 100, 2)
    else:
        # fallback if model is somehow strictly returning class
        pred = model.predict(input_data)[0]
        return 95.0 if pred == 1 else 15.0
