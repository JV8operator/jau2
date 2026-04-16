import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
IMPORTANCE_PATH = BASE_DIR / "models" / "feature_importance.json"

_importance = None

def _load_importance():
    global _importance
    if _importance is None:
        if IMPORTANCE_PATH.exists():
            with open(IMPORTANCE_PATH, "r") as f:
                _importance = json.load(f)
        else:
            _importance = {"CGPA": 0.35, "Internships": 0.25, "Projects": 0.15, "Certificates": 0.05}
    return _importance

def generate_insights(user_data, current_probability, current_category):
    """
    user_data dict with cgpa, internships, projects
    """
    importance = _load_importance()
    insights = []
    
    # Very crude "what-if" based on simple logic
    
    cgpa = float(user_data.get('cgpa', 0))
    internships = int(user_data.get('internships', 0))
    projects = int(user_data.get('projects', 0))
    
    # Identify top most important feature the user is lacking in
    
    if cgpa < 7.5:
        insights.append("Improving your CGPA to 7.5+ is one of the highest impact actions for placement.")
        
    if internships == 0:
        val = importance.get("Internships", 0) * 100
        insights.append(f"Securing at least 1 internship strongly correlates with a higher aptitude pass rate.")
        
    if projects < 2:
        insights.append(f"Adding 1 more solid project to your resume covers basic technical requirements.")
        
    if current_category == "Low":
        insights.append("Your current focus should be exclusively on building the fundamental skills in your roadmap.")
    elif current_category == "High":
        insights.append("You are in a great spot! Focus on mock interviews and applying to top tier roles.")
        
    if not insights:
        insights.append("Keep maintaining your current profile trajectory.")
        
    return insights
