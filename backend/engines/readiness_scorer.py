def compute_readiness_score(cgpa, internships, project_quality_score,
                            skill_match_percentage, placement_probability,
                            cert_weighted_count=0):
    """
    Computes a normalised 0-100 readiness score using qualitative inputs.

    Weights:
      CGPA                    : 20%  (0–10 scale)
      Internships             : 20%  (quality: 1 = full credit, 0 = none)
      Project Quality Score   : 20%  (0–100, from quality_evaluator)
      Skill Match %           : 25%  (weighted tier match)
      Placement Probability   : 10%  (from ML model)
      Certificate Weight      :  5%  (valid + 0.5 * partial certs, capped at 3)
    """
    score = 0.0

    # 1. CGPA — 20 points max
    # Baseline 5.0 = 0 pts, 10.0 = 20 pts
    cgpa_val = min(max(float(cgpa), 0), 10)
    if cgpa_val > 5:
        score += ((cgpa_val - 5) / 5) * 20

    # 2. Internships — 20 points max
    # 0 = 0 pts, 1 = 13 pts, 2+ = 20 pts
    int_val = int(internships)
    if int_val >= 2:
        score += 20
    elif int_val == 1:
        score += 13

    # 3. Project Quality Score — 20 points max
    # project_quality_score is already 0–100
    pqs = min(max(float(project_quality_score), 0), 100)
    score += pqs * 0.20

    # 4. Skill Match % — 25 points max
    sm_val = min(max(float(skill_match_percentage), 0), 100)
    score += sm_val * 0.25

    # 5. Placement Probability — 10 points max
    pp_val = min(max(float(placement_probability), 0), 100)
    score += pp_val * 0.10

    # 6. Certificate Weight — 5 points max
    # Cap effective certs at 3 (to prevent gaming by listing 20 certs)
    cert_eff = min(float(cert_weighted_count), 3.0)
    score += (cert_eff / 3.0) * 5

    readiness_score = min(round(score, 1), 100)

    if readiness_score >= 75:
        category = "High"
    elif readiness_score >= 50:
        category = "Moderate"
    else:
        category = "Low"

    return {
        "readiness_score": readiness_score,
        "category": category
    }
