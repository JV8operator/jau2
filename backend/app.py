from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Ensure backend modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db
from auth import auth_bp, token_required
from engines.placement_predictor import predict_placement
from engines.skill_gap_engine import analyze_skill_gap
from engines.readiness_scorer import compute_readiness_score
from engines.benchmarking_engine import generate_benchmarks
from engines.roadmap_generator import generate_roadmap
from engines.insight_engine import generate_insights
from engines.doc_parser import extract_text_from_pdf, scan_for_skills, extract_cgpa, extract_certificate_info
from engines.quality_evaluator import evaluate_project_quality, evaluate_certificates
from engines.internship_engine import evaluate_internships

app = Flask(__name__)
# Allow CORS — restrict to frontend URL in production
frontend_url = os.environ.get('FRONTEND_URL', '*')
CORS(app, resources={r"/*": {"origins": frontend_url}})

app.register_blueprint(auth_bp, url_prefix='/auth')

# Initialize SQLite database
with app.app_context():
    init_db()

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/analyze', methods=['POST'])
@token_required
def analyze(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
        
    try:
        # Extract fields
        branch = data.get('branch', 'CSE')
        cgpa = float(data.get('cgpa', 0))
        internships_raw = data.get('internships', [])
        projects_raw = data.get('projects', [])
        certificates_raw = data.get('certificates', [])

        # Normalise to lists (backward compat: int/empty was allowed before)
        if not isinstance(internships_raw, list):
            # Legacy: plain number was sent — wrap into dummy entries
            try:
                n = int(internships_raw)
            except (ValueError, TypeError):
                n = 0
            internships_raw = [{"company": "Unknown", "role": "", "duration": ""} for _ in range(n)]
        if not isinstance(projects_raw, list):
            projects_raw = []
        if not isinstance(certificates_raw, list):
            certificates_raw = []

        internships_count = len(internships_raw)    # raw count for ML model
        projects_count = len(projects_raw)          # raw count still needed for ML model
        certificates_count = len(certificates_raw)

        skills = data.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',') if s.strip()]

        # Scan rich project descriptions for extra skills
        for proj in projects_raw:
            desc = proj.get('description', '')
            if desc:
                extra_skills, _ = scan_for_skills(desc, branch)
                skills.extend(extra_skills)

        # Remove duplicates
        skills = list(set(skills))

        target_role = data.get('target_role')

        # 1. Quality Evaluation (internships + projects + certificates)
        internship_quality = evaluate_internships(internships_raw)
        project_quality = evaluate_project_quality(projects_raw)
        cert_quality = evaluate_certificates(certificates_raw)

        # 2. Prediction — ML model still uses raw counts
        placement_probability = predict_placement(
            cgpa, internship_quality['internship_count'], projects_count,
            int(cert_quality['weighted_count']),   # only pass valid certs to model
            aptitude_score=75
        )

        # 3. Skill Gap (tiered, role-aware)
        skill_analysis = analyze_skill_gap(branch, skills, target_role)

        # 4. Readiness Score (quality-based)
        readiness_data = compute_readiness_score(
            cgpa,
            internship_quality['internship_count'],
            project_quality['quality_score'],        # 0–100 quality
            skill_analysis['skill_match_percentage'],
            placement_probability,
            cert_quality['weighted_count']           # only recognised certs
        )

        # 5. Benchmarking
        benchmarks = generate_benchmarks({
            "cgpa": cgpa,
            "internships": internship_quality['internship_count'],
            "projects": projects_count,
            "certificates": certificates_count
        })

        # 6. Roadmap
        roadmap = generate_roadmap(skill_analysis['missing_skills'], readiness_data['category'])

        # 7. Insights
        insights = generate_insights(
            {"cgpa": cgpa, "internships": internship_quality['internship_count'], "projects": projects_count},
            placement_probability,
            readiness_data['category']
        )

        return jsonify({
            "placement_probability": placement_probability,
            "readiness_score": readiness_data["readiness_score"],
            "category": readiness_data["category"],
            "missing_skills": skill_analysis["missing_skills"],
            "matched_skills": skill_analysis["matched_skills"],
            "skill_match_percentage": skill_analysis["skill_match_percentage"],
            "tier_breakdown": skill_analysis["tier_breakdown"],
            "internship_quality": internship_quality,
            "project_quality": project_quality,
            "cert_quality": cert_quality,
            "roadmap": roadmap,
            "benchmarks": benchmarks,
            "insights": insights
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/upload-document', methods=['POST'])
@token_required
def upload_document(current_user):
    if 'document' not in request.files:
        return jsonify({"error": "No document part"}), 400
        
    file = request.files['document']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400
        
    doc_type = request.form.get('type', 'resume') # 'resume' or 'certificate'
    branch = request.form.get('branch', 'CSE')
    
    try:
        text = extract_text_from_pdf(file)
        result = {"extracted_text_preview": text[:200] + "..."}
        
        if doc_type == 'resume':
            flat_skills, categorized_skills = scan_for_skills(text, branch)
            cgpa_data = extract_cgpa(text)
            result["skills"] = flat_skills
            result["skills_categorized"] = categorized_skills
            result["skills_count"] = len(flat_skills)
            if cgpa_data:
                result["cgpa"] = cgpa_data["cgpa"]
                result["cgpa_scale"] = cgpa_data["scale"]
        elif doc_type == 'certificate':
            cert_info = extract_certificate_info(text)
            result["cert_title"] = cert_info["title"]
            result["cert_issuer"] = cert_info["issuer"]
            result["raw_excerpt"] = cert_info["raw_excerpt"]

        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug)
