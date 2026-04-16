from flask import Flask, request, render_template
from skill_gap_engine import analyze_student
from recommendation_engine import recommend_skills
from placement_probability import estimate_probability

import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

app = Flask(__name__, template_folder=".")

# ---------------------------
# HOME ROUTE
# ---------------------------
@app.route('/')
def home():
    return render_template("index.html")


# ---------------------------
# ANALYZE ROUTE
# ---------------------------
@app.route('/analyze', methods=['POST'])
def analyze():

    branch = request.form['branch']
    year = request.form['year']
    skills = request.form['skills'].split(',')
    internships = int(request.form['internships'])
    cgpa = float(request.form['cgpa'])

    analysis = analyze_student(branch, year, skills, internships, cgpa)
    recommendations = recommend_skills(branch, skills)
    probability, salary = estimate_probability(cgpa, internships)

    return render_template(
        "result.html",
        analysis=analysis,
        recommendations=recommendations,
        probability=probability,
        salary=salary
    )


# ---------------------------
# DASHBOARD ROUTE
# ---------------------------
@app.route('/dashboard')
def dashboard():

    # Load cleaned numeric dataset
    df = pd.read_csv("ML_Feature_Set_Cleaned.csv")

    avg_cgpa = round(df["CGPA"].mean(), 2)
    avg_internships = round(df["Internships"].mean(), 2)

    # Real placement % using aptitude threshold
    placed_students = df[df["AptitudeTestScore"] >= 70]
    placement_percentage = round((len(placed_students) / len(df)) * 100, 2)

    # -----------------------------
    # CGPA Distribution Graph
    # -----------------------------
    plt.figure()
    df["CGPA"].hist()
    plt.title("CGPA Distribution")

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    # -----------------------------
    # Skill Demand Chart
    # -----------------------------
    skills_df = pd.read_csv("skills_dataset.csv")
    placed = skills_df[skills_df["PlacementStatus"] == 1]

    all_skills = []

    for skills in placed["Skills"]:
        skill_list = [s.strip() for s in skills.split(",")]
        all_skills.extend(skill_list)

    skill_series = pd.Series(all_skills)
    top_skills = skill_series.value_counts().head(5)

    plt.figure()
    top_skills.plot(kind='bar')
    plt.title("Top 5 Demanded Skills")

    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    skill_plot_url = base64.b64encode(img2.getvalue()).decode()

    return render_template(
        "dashboard.html",
        avg_cgpa=avg_cgpa,
        avg_internships=avg_internships,
        placement_percentage=placement_percentage,
        plot_url=plot_url,
        skill_plot_url=skill_plot_url
    )


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
