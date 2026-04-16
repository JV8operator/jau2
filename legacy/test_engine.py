from skill_gap_engine import analyze_student

result = analyze_student(
    branch="CSE",
    year="Final",
    skills=["Python", "SQL"],
    internships=1,
    cgpa=8.2
)

print(result)