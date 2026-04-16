from skill_gap_engine import get_top_skills

def recommend_skills(branch, student_skills):

    required_skills = get_top_skills(branch)
    student_skills = [s.strip() for s in student_skills]

    missing = list(set(required_skills) - set(student_skills))

    return missing