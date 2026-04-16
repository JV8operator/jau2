from skill_gap_engine import analyze_student
from recommendation_engine import recommend_skills
from placement_probability import estimate_probability

# Sample Input
branch = "CSE"
year = "Final"
skills = ["Python", "SQL"]
internships = 1
cgpa = 8.2

# Run Skill Gap Analysis
analysis = analyze_student(branch, year, skills, internships, cgpa)

# Run Recommendation Engine
recommendations = recommend_skills(branch, skills)

# Run Placement Probability
probability, salary = estimate_probability(cgpa, internships)

print("=== Skill Gap Analysis ===")
print(analysis)

print("\n=== Recommended Skills ===")
print(recommendations)

print("\n=== Placement Probability ===")
print("Probability:", probability)
print("Expected Salary:", salary)