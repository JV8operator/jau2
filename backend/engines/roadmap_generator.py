import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESOURCES_PATH = BASE_DIR / "resources.json"

_resources = None

def _load_resources():
    global _resources
    if _resources is None:
        if RESOURCES_PATH.exists():
            with open(RESOURCES_PATH, 'r') as f:
                _resources = json.load(f)
        else:
            _resources = {}
    return _resources

def generate_roadmap(missing_skills, readiness_category):
    resources_map = _load_resources()
    
    roadmap = []
    current_week = 1
    
    # Priority based on category
    if readiness_category == "Low" and not missing_skills:
        # Fallback if no specific skills missing but score is low
        missing_skills = ["Data Structures", "Problem Solving"]
        
    for skill in missing_skills:
        skill_info = resources_map.get(skill, {
            "duration_weeks": 2,
            "resources": [f"Search online tutorials for {skill}"]
        })
        
        duration = skill_info["duration_weeks"]
        end_week = current_week + duration - 1
        
        week_str = f"Week {current_week}" if duration == 1 else f"Week {current_week}-{end_week}"
        
        tasks_list = [f"Focus on fundamentals of {skill}"] + [f"Complete: {res}" for res in skill_info["resources"]]
        
        roadmap.append({
            "week": week_str,
            "skill": skill,
            "tasks": tasks_list
        })
        
        current_week = end_week + 1
        
    # Append a final general preparation step
    roadmap.append({
        "week": f"Week {current_week}+",
        "skill": "Placement Readiness",
        "tasks": ["Mock Interviews", "Resume building", "Apply for internships"]
    })
    
    return roadmap
