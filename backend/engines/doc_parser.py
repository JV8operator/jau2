import io
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from .skill_gap_engine import get_skills_df

# ─────────────────────────────────────────────
#  SKILL CATEGORY DICTIONARY
#  Used to auto-sort extracted skills into 3 UI buckets
# ─────────────────────────────────────────────
SKILL_CATEGORIES = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "rust",
        "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "dart", "perl",
        "sql", "bash", "shell",
    ],
    "frameworks": [
        "react", "next.js", "nextjs", "angular", "vue", "redux", "jquery", "tailwind",
        "bootstrap", "sass", "webpack", "vite",
        "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring boot",
        "laravel", "rails", "rest api", "graphql", "websocket",
        "pytorch", "tensorflow", "scikit-learn", "keras", "opencv", "langchain",
        "pandas", "numpy", "transformers", "hugging face",
        "spark", "hadoop", "airflow", "dbt",
    ],
    "tools": [
        "git", "github", "docker", "kubernetes", "aws", "gcp", "azure",
        "mysql", "postgresql", "mongodb", "redis", "sqlite", "firebase",
        "supabase", "cassandra", "elasticsearch", "dynamodb",
        "linux", "nginx", "apache", "terraform", "ansible", "ci/cd", "github actions",
        "postman", "jira", "figma", "power bi", "tableau", "excel",
        "kafka", "rabbitmq", "jwt", "oauth",
    ],
}

# Flat list of all known skills for scanning
BROAD_SKILL_KEYWORDS = list(set(
    SKILL_CATEGORIES["languages"] +
    SKILL_CATEGORIES["frameworks"] +
    SKILL_CATEGORIES["tools"] + [
        "machine learning", "deep learning", "nlp", "computer vision",
        "data analysis", "data science", "llm", "rag",
        "html", "css", "oops", "object oriented", "data structures",
        "algorithms", "dsa", "system design", "microservices",
    ]
))


def extract_text_from_pdf(file_stream):
    if not PyPDF2:
        return ""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text
    except Exception as e:
        print("Error reading PDF:", e)
        return ""


def scan_for_skills(text, branch="CSE", target_role=None):
    """
    Scans freeform text for known skills.
    Returns a flat list AND a categorized dict.
    """
    text_lower = text.lower()
    found = set()

    for skill in BROAD_SKILL_KEYWORDS:
        escaped = re.escape(skill)
        if re.search(r'\b' + escaped + r'\b', text_lower):
            found.add(skill)

    # Also scan dataset-based skills
    try:
        df = get_skills_df()
        if df is not None:
            known_skills = []
            if branch in df.columns:
                known_skills.extend([str(s).strip().lower() for s in df[branch].dropna().tolist() if str(s).strip()])
            if not known_skills:
                for col in df.columns:
                    known_skills.extend([str(s).strip().lower() for s in df[col].dropna().tolist() if str(s).strip()])
            for skill in set(known_skills):
                escaped = re.escape(skill)
                if re.search(r'\b' + escaped + r'\b', text_lower):
                    found.add(skill)
    except Exception:
        pass

    # Sort into categories
    categorized = {"languages": [], "frameworks": [], "tools": [], "other": []}
    for skill in found:
        placed = False
        for cat, cat_skills in SKILL_CATEGORIES.items():
            if skill in cat_skills:
                categorized[cat].append(skill.title())
                placed = True
                break
        if not placed:
            categorized["other"].append(skill.title())

    # Sort each category alphabetically
    for cat in categorized:
        categorized[cat] = sorted(categorized[cat])

    flat_list = sorted([s.title() for s in found])
    return flat_list, categorized


def extract_cgpa(text):
    """Attempts to find CGPA via regex. Returns raw value and detected scale."""
    matches = re.findall(r'(?i)(?:cgpa|gpa|sgpa|cpi)[\s:\/]*([0-9]+\.[0-9]+)', text)
    if matches:
        val = round(float(matches[0]), 2)
        scale = 4 if val <= 4.0 else 10
        return {"cgpa": val, "scale": scale}
    return None


# ─────────────────────────────────────────────
#  CERTIFICATE PDF PARSING
# ─────────────────────────────────────────────
_CERT_ISSUERS = [
    ("amazon web services", "Amazon Web Services (AWS)"),
    ("aws", "Amazon Web Services (AWS)"),
    ("google cloud", "Google Cloud"),
    ("google", "Google"),
    ("microsoft", "Microsoft"),
    ("microsoft azure", "Microsoft Azure"),
    ("coursera", "Coursera"),
    ("deeplearning.ai", "DeepLearning.AI"),
    ("andrew ng", "DeepLearning.AI / Andrew Ng"),
    ("edx", "edX"),
    ("udemy", "Udemy"),
    ("udacity", "Udacity"),
    ("nptel", "NPTEL"),
    ("linkedin learning", "LinkedIn Learning"),
    ("meta", "Meta"),
    ("ibm", "IBM"),
    ("oracle", "Oracle"),
    ("cisco", "Cisco"),
    ("comptia", "CompTIA"),
    ("red hat", "Red Hat"),
    ("linux foundation", "Linux Foundation"),
    ("kaggle", "Kaggle"),
    ("datacamp", "DataCamp"),
    ("hackerrank", "HackerRank"),
    ("infosys", "Infosys"),
    ("tcs", "TCS"),
    ("nasscom", "NASSCOM"),
    ("internshala", "Internshala"),
    ("great learning", "Great Learning"),
    ("simplilearn", "Simplilearn"),
    ("databricks", "Databricks"),
    ("mongodb university", "MongoDB University"),
]

_CERT_KEYWORDS = [
    "certificate of completion", "certificate of achievement", "this certifies that",
    "has successfully completed", "has completed", "is awarded", "has been awarded",
    "certification", "professional certificate", "specialization",
]


def extract_certificate_info(text):
    text_lower = text.lower()
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    issuer = None
    for keyword, pretty in _CERT_ISSUERS:
        if keyword in text_lower:
            issuer = pretty
            break

    title = None
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in _CERT_KEYWORDS):
            candidates = [l for l in lines[max(0, i-3):i] if len(l) > 8]
            if candidates:
                title = candidates[-1]
                break

    if not title:
        m = re.search(
            r'(?i)(?:course|program|specialization|bootcamp|certification)[:\s]+([A-Za-z][A-Za-z0-9 :\-]{5,80})',
            text
        )
        if m:
            title = m.group(1).strip()

    if not title:
        candidates = sorted([l for l in lines[:20] if 5 < len(l) < 100], key=len, reverse=True)
        if candidates:
            title = candidates[0]

    composed = title or "Certificate"
    if issuer and issuer.lower() not in composed.lower():
        composed = f"{composed} - {issuer}"

    return {
        "title": composed,
        "raw_title": title,
        "issuer": issuer,
        "raw_excerpt": text[:300]
    }

