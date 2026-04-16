"""
Quality Evaluator Engine
========================
Evaluates the *quality* of projects and *legitimacy* of certificates
rather than simply counting them.

Project Quality Score (per project, 0–10):
  - Has a descriptive title                     +1
  - Description is >= 30 words                  +2
  - Uses 2+ tech keywords in description        +3
  - Mentions a problem/outcome/impact           +2
  - Contains keywords like "deployed", "API",
    "machine learning", "backend", "frontend"   +2

Certificate Legitimacy (per certificate):
  - Recognised issuer found in title            → VALID  (weight = 1.0)
  - Title looks academic/course-like            → PARTIAL (weight = 0.5)
  - Unclear / high-school type                  → IGNORED (weight = 0.0)
"""

import re

# ----- TECH KEYWORDS -----
TECH_KEYWORDS = {
    "python", "java", "javascript", "typescript", "react", "next.js", "nextjs",
    "node", "nodejs", "express", "django", "flask", "fastapi", "spring",
    "sql", "mysql", "postgresql", "mongodb", "firebase", "supabase",
    "html", "css", "tailwind", "bootstrap", "figma",
    "machine learning", "deep learning", "nlp", "computer vision", "ai",
    "pandas", "numpy", "sklearn", "scikit", "tensorflow", "pytorch",
    "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git", "github",
    "rest api", "graphql", "microservices", "websocket",
    "c", "c++", "rust", "go", "ruby", "kotlin", "swift", "dart", "flutter",
    "android", "ios", "react native", "expo",
    "linux", "bash", "shell", "devops", "ansible", "terraform",
    "redis", "kafka", "rabbitmq", "celery",
    "data structures", "algorithms", "dsa", "leetcode",
    "blockchain", "web3", "solidity",
}

IMPACT_KEYWORDS = {
    "deployed", "production", "live", "published", "launched",
    "api", "database", "users", "performance", "scalable",
    "automated", "reduced", "improved", "built", "developed", "integrated",
    "client", "company", "startup", "platform", "system", "application",
    "real-time", "realtime", "responsive", "authentication", "secure",
}

# ----- RECOGNISED CERTIFICATE ISSUERS -----
# These are professional / technical certifications that actually carry weight.
RECOGNISED_ISSUERS = [
    # Cloud / Infra
    "aws", "amazon web services", "azure", "microsoft", "google cloud", "gcp",
    "oracle", "ibm", "cisco", "comptia",
    # ML / Data
    "deeplearning.ai", "andrew ng", "tensorflow", "pytorch", "databricks",
    "datacamp", "kaggle",
    # Web Dev / Programming
    "meta", "facebook", "mongodb university", "redis university",
    "freecodecamp", "hackerrank", "codechef",
    # Professional Platforms / Universities
    "coursera", "edx", "udemy", "udacity", "nptel", "linkedin learning",
    "pluralsight", "skillsoft", "great learning", "simplilearn",
    # Tech Certifications
    "java se", "oracle certified", "red hat", "linux foundation",
    "docker certified", "kubernetes", "cka", "cnd",
    "pmp", "scrum", "agile",
    # Testing / Security
    "selenium", "istqb", "ethical hacking", "ceh", "cissp", "oscp",
    # Other common legit ones
    "infosys", "tcs", "wipro", "nasscom", "internshala",
]

# These phrases likely indicate irrelevant certificates
IGNORED_CERT_SIGNALS = [
    "high school", "school", "secondary", "class 10", "class 12", "board",
    "cbse", "icse", "sports", "participation", "debate", "cultural",
    "attendance", "appreciation",
]


def evaluate_project_quality(projects: list) -> dict:
    """
    projects: list of dicts with keys 'title' and 'description'

    Returns:
        {
          "quality_score": float (0–100),   # overall normalised score
          "project_scores": [float],         # per-project score 0–10
          "strong_projects": int,            # count scoring >= 6
          "feedback": [str]                  # qualitative feedback items
        }
    """
    if not projects:
        return {
            "quality_score": 0.0,
            "project_scores": [],
            "strong_projects": 0,
            "feedback": ["No projects added. Add at least 2 substantial projects."]
        }

    project_scores = []
    feedback = []

    for i, proj in enumerate(projects):
        title = str(proj.get("title", "")).strip()
        desc = str(proj.get("description", "")).strip()
        score = 0.0

        # 1. Has meaningful title
        if len(title) >= 5:
            score += 1

        # 2. Description length
        word_count = len(desc.split())
        if word_count >= 50:
            score += 2
        elif word_count >= 20:
            score += 1

        # 3. Tech keywords in description (combined title + desc)
        combined = (title + " " + desc).lower()
        found_tech = [kw for kw in TECH_KEYWORDS if kw in combined]
        if len(found_tech) >= 4:
            score += 3
        elif len(found_tech) >= 2:
            score += 2
        elif len(found_tech) >= 1:
            score += 1

        # 4. Impact / outcome keywords
        found_impact = [kw for kw in IMPACT_KEYWORDS if kw in combined]
        if len(found_impact) >= 3:
            score += 2
        elif len(found_impact) >= 1:
            score += 1

        # 5. Bonus: mentions deployment/production
        deploy_terms = {"deployed", "live", "production", "hosted", "vercel", "heroku", "netlify", "railway"}
        if any(t in combined for t in deploy_terms):
            score += 2

        score = min(score, 10.0)
        project_scores.append(round(score, 1))

        # Feedback
        if score < 4:
            feedback.append(f"Project '{title or f'#{i+1}'}' looks weak — add more technical detail and describe the impact.")
        elif score < 7:
            feedback.append(f"Project '{title or f'#{i+1}'}' is decent. Consider describing deployment or outcomes.")

    strong = sum(1 for s in project_scores if s >= 6)

    # Normalise: average score mapped to 0–100
    avg = sum(project_scores) / len(project_scores)
    quality_score = round(min(avg * 10, 100), 1)

    if not feedback:
        feedback.append("Projects look strong! Keep them updated on your resume.")

    return {
        "quality_score": quality_score,
        "project_scores": project_scores,
        "strong_projects": strong,
        "feedback": feedback
    }


def evaluate_certificates(certificates: list) -> dict:
    """
    certificates: list of dicts with key 'title'

    Returns:
        {
          "valid_count": int,       # fully recognised certs
          "partial_count": int,     # might be valid but unclear
          "ignored_count": int,     # high-school / irrelevant
          "weighted_count": float,  # effective count used for scoring
          "feedback": [str]
        }
    """
    if not certificates:
        return {
            "valid_count": 0,
            "partial_count": 0,
            "ignored_count": 0,
            "weighted_count": 0.0,
            "feedback": ["No certificates added. Add recognized tech certifications (Coursera, AWS, Google, etc.)."]
        }

    valid, partial, ignored = 0, 0, 0
    weighted = 0.0
    feedback = []

    for cert in certificates:
        title_raw = str(cert.get("title", "")).strip()
        title = title_raw.lower()

        # Check ignored signals first
        if any(sig in title for sig in IGNORED_CERT_SIGNALS):
            ignored += 1
            feedback.append(f"'{title_raw}' — skipped (not a professional/technical certificate).")
            continue

        # Check for recognised issuers
        if any(issuer in title for issuer in RECOGNISED_ISSUERS):
            valid += 1
            weighted += 1.0
        else:
            # Heuristic: if it contains words like "course", "certificate", "certification"
            # and a tech-sounding word, treat as partial
            has_cert_word = any(w in title for w in ["course", "certificate", "certification", "bootcamp", "training", "workshop"])
            has_tech_word = any(kw in title for kw in TECH_KEYWORDS)
            if has_cert_word and has_tech_word:
                partial += 1
                weighted += 0.5
                feedback.append(f"'{title_raw}' — counted partially (add issuer name like Coursera/Google/AWS for full credit).")
            else:
                ignored += 1
                feedback.append(f"'{title_raw}' — unclear certificate, not counted. Stick to professional tech certs.")

    if valid > 0 and not any("skipped" in f for f in feedback):
        feedback.append(f"{valid} strong recognised certificate(s) found — great!")

    return {
        "valid_count": valid,
        "partial_count": partial,
        "ignored_count": ignored,
        "weighted_count": round(weighted, 1),
        "feedback": feedback
    }
