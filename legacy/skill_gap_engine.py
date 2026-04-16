import pandas as pd
import joblib

# Load skills dataset
skills_df = pd.read_csv("skills_dataset.csv")

# Load trained ML model
model = joblib.load("aptitude_model.pkl")

# -------------------------
# Extract Top Skills Per Branch
# -------------------------

def get_top_skills(branch):

    branch_data = skills_df[
        (skills_df["Branch"].str.upper() == branch.upper()) &
        (skills_df["PlacementStatus"] == 1)
    ]

    all_skills = []

    for skills in branch_data["Skills"]:
        skill_list = [s.strip() for s in skills.split(",")]
        all_skills.extend(skill_list)

    skill_series = pd.Series(all_skills)
    top_skills = skill_series.value_counts().head(4).index.tolist()

    return top_skills

# -------------------------
# Main Analyzer
# -------------------------

def analyze_student(branch, year, skills, internships, cgpa):

    score = 0

    # Basic CGPA Logic
    if cgpa >= 8:
        score += 30
    elif cgpa >= 7:
        score += 20

    # Internship Logic
    if internships >= 2:
        score += 30
    elif internships == 1:
        score += 15

    # Skill Matching
    required_skills = get_top_skills(branch)
    student_skills = [s.strip() for s in skills]

    matching = len(set(student_skills) & set(required_skills))

    if len(required_skills) > 0:
        score += (matching / len(required_skills)) * 40
    # Predict aptitude score using ML model
    predicted_aptitude = model.predict([[cgpa, internships, 2, 2]])[0]

    # Add ML weight
    if predicted_aptitude >= 75:
        score += 10
    elif predicted_aptitude >= 60:
        score += 5

    readiness = round(score, 2)

    missing_skills = list(set(required_skills) - set(student_skills))

    if readiness >= 75:
        message = "Highly placement ready."
    elif readiness >= 50:
        message = "Moderately ready."
    else:
        message = "Significant skill gap detected."

    return {
        "readiness": readiness,
        "missing_skills": missing_skills,
        "message": message,
        "top_required_skills": required_skills
    }
    