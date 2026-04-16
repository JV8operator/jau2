import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ML_DATA_PATH = BASE_DIR / "data" / "ML_Feature_Set_Cleaned.csv"

_averages = None

def _load_averages():
    global _averages
    if _averages is None:
        df = pd.read_csv(ML_DATA_PATH)
        # Filter for placed students proxy (Aptitude >= 70)
        placed_df = df[df["AptitudeTestScore"] >= 70]
        
        _averages = {
            "cgpa": round(placed_df["CGPA"].mean(), 2),
            "internships": round(placed_df["Internships"].mean(), 2),
            "projects": round(placed_df["Projects"].mean(), 2),
            "certificates": round(placed_df["Certificates"].mean(), 2)
        }
    return _averages

def generate_benchmarks(user_data):
    """
    user_data dict with keys: cgpa, internships, projects, certificates
    """
    avg = _load_averages()
    
    cgpa = float(user_data.get('cgpa', 0))
    internships = int(user_data.get('internships', 0))
    projects = int(user_data.get('projects', 0))
    
    return {
        "placed_averages": avg,
        "gaps": {
            "cgpa": round(cgpa - avg["cgpa"], 2),
            "internships": round(internships - avg["internships"], 2),
            "projects": round(projects - avg["projects"], 2)
        },
        "indicators": {
            "cgpa": "ahead" if cgpa >= avg["cgpa"] else "behind",
            "internships": "ahead" if internships >= avg["internships"] else "behind",
            "projects": "ahead" if projects >= avg["projects"] else "behind"
        }
    }
