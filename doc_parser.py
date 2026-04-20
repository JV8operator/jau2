import io
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from .skill_gap_engine import get_skills_df

# ─────────────────────────────────────────────
#  KNOWN TECH SKILLS (comprehensive list)
# ─────────────────────────────────────────────
BROAD_SKILL_KEYWORDS = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "dart", "perl",
    # Web Frontend
    "react", "next.js", "nextjs", "angular", "vue", "html", "css", "tailwind",
    "bootstrap", "jquery", "redux", "sass", "webpack", "vite", "figma",
    # Web Backend
    "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring boot",
    "laravel", "rails", "rest api", "graphql", "websocket",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "firebase",
    "supabase", "cassandra", "elasticsearch", "dynamodb",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "ci/cd", "github actions",
    "terraform", "ansible", "linux", "bash", "nginx", "apache",
    # ML / AI
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch",
    "tensorflow", "scikit-learn", "pandas", "numpy", "keras", "opencv",
    "transformers", "langchain", "llm", "rag", "hugging face",
    # Data
    "data analysis", "data science", "power bi", "tableau", "excel", "spark",
    "hadoop", "airflow", "dbt",
    # Tools & Other
    "git", "github", "postman", "jira", "agile", "scrum", "linux", "oops",
    "object oriented", "data structures", "algorithms", "dsa", "system design",
    "microservices", "kafka", "rabbitmq", "jwt", "oauth",
]

# ─────────────────────────────────────────────
#  SECTION HEADER PATTERNS
# ─────────────────────────────────────────────
_SECTION_PATTERNS = {
    "projects":     re.compile(r'(?i)^\s*(projects?|personal projects?|academic projects?|key projects?|notable projects?)\s*$'),
    "experience":   re.compile(r'(?i)^\s*(experience|work experience|internships?|professional experience|employment)\s*$'),
    "education":    re.compile(r'(?i)^\s*(education|academic|qualifications?)\s*$'),
    "skills":       re.compile(r'(?i)^\s*(skills?|technical skills?|core skills?|key skills?|technologies|tech stack)\s*$'),
    "certificates": re.compile(r'(?i)^\s*(certifications?|certificates?|courses?|achievements?|licenses?)\s*$'),
}

# ─────────────────────────────────────────────
#  COMPANY TIER KEYWORDS (for internship detection)
# ─────────────────────────────────────────────
_KNOWN_COMPANIES = [
    "google", "amazon", "microsoft", "meta", "apple", "netflix", "nvidia",
    "tesla", "openai", "adobe", "oracle", "cisco", "intel", "ibm", "salesforce",
    "uber", "airbnb", "stripe", "isro", "drdo", "tata", "infosys", "wipro",
    "tcs", "hcl", "cognizant", "accenture", "capgemini", "zoho", "freshworks",
    "startup", "pvt ltd", "private limited", "technologies", "solutions", "systems",
    "software", "labs", "research",
]

_DURATION_PATTERN = re.compile(
    r'(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,\-]*(\d{4})'
    r'\s*(?:to|-|–)\s*'
    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|present|current)[a-z]*[\s,\-]*(\d{4})?',
    re.IGNORECASE
)
_DURATION_SIMPLE = re.compile(r'(?i)(\d+)\s*(month|week|year)', re.IGNORECASE)


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


def _split_into_sections(text):
    """
    Split resume text into named sections based on header detection.
    Returns dict: {section_name: [lines]}
    """
    lines = [l.rstrip() for l in text.split('\n')]
    sections = {}
    current_section = "header"
    sections[current_section] = []

    for line in lines:
        matched = False
        for name, pattern in _SECTION_PATTERNS.items():
            if pattern.match(line):
                current_section = name
                sections[current_section] = []
                matched = True
                break
        if not matched:
            sections.setdefault(current_section, []).append(line)

    return sections


def scan_for_skills(text, branch="CSE", target_role=None):
    """Scans freeform text for known skills using broad keyword list + dataset."""
    text_lower = text.lower()
    found = set()

    # 1. Scan broad built-in keyword list
    for skill in BROAD_SKILL_KEYWORDS:
        escaped = re.escape(skill)
        if re.search(r'\b' + escaped + r'\b', text_lower):
            found.add(skill.title())

    # 2. Also scan dataset-based skills as before
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
                found.add(skill.title())

    return sorted(found)


def extract_cgpa(text):
    """Attempts to find CGPA via regex. Returns raw value and detected scale."""
    matches = re.findall(r'(?i)(?:cgpa|gpa|sgpa|cpi)[\s:\/]*([0-9]+\.[0-9]+)', text)
    if matches:
        val = round(float(matches[0]), 2)
        scale = 4 if val <= 4.0 else 10
        return {"cgpa": val, "scale": scale}
    return None


def extract_projects_from_resume(text):
    """
    Extracts project entries from resume text.
    Returns list of {title, description} dicts.
    """
    sections = _split_into_sections(text)
    project_lines = sections.get("projects", [])

    # If no explicit section, try to find project-like blocks anywhere
    if not project_lines:
        # Look for lines near "project" keyword
        all_lines = text.split('\n')
        in_block = False
        for i, line in enumerate(all_lines):
            if re.search(r'(?i)\bprojects?\b', line) and len(line.strip()) < 60:
                in_block = True
                continue
            if in_block:
                project_lines.append(line)
                if len(project_lines) > 30:
                    break

    projects = []
    current_title = None
    current_desc_lines = []

    def flush():
        if current_title:
            desc = " ".join(l.strip() for l in current_desc_lines if l.strip())
            projects.append({
                "title": current_title.strip(),
                "description": desc[:500] if desc else "Built using modern technologies."
            })

    for line in project_lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Heuristic: a project title is a short line (< 80 chars) that is NOT a bullet point
        # and doesn't start with common bullet markers
        is_bullet = stripped.startswith(('-', '*', '•', '>', '–', '→'))
        is_short = len(stripped) < 80
        has_tech = any(kw in stripped.lower() for kw in BROAD_SKILL_KEYWORDS[:30])

        # Detect title: short non-bullet line, possibly with pipe separator
        if is_short and not is_bullet and (
            stripped[0].isupper() or '|' in stripped
        ):
            # Check if it looks like a new project (has tech keywords or title case)
            if current_title and len(current_desc_lines) >= 0:
                flush()
                current_desc_lines = []
            current_title = stripped.split('|')[0].strip()  # Take first part if "Title | Tech Stack"
        else:
            current_desc_lines.append(stripped)

    flush()

    # De-duplicate and cap at 5
    seen = set()
    clean = []
    for p in projects:
        if p['title'] and p['title'] not in seen and len(p['title']) > 3:
            seen.add(p['title'])
            clean.append(p)

    return clean[:5]


def extract_internships_from_resume(text):
    """
    Extracts internship/work experience entries from resume text.
    Returns list of {company, role, duration} dicts.
    """
    sections = _split_into_sections(text)
    exp_lines = sections.get("experience", [])

    internships = []
    current_company = None
    current_role = None
    current_duration = ""

    def flush():
        if current_company or current_role:
            internships.append({
                "company": (current_company or "").strip(),
                "role": (current_role or "").strip(),
                "duration": current_duration.strip()
            })

    for line in exp_lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check for date/duration on this line
        dur_match = _DURATION_PATTERN.search(stripped)
        simple_dur = _DURATION_SIMPLE.search(stripped)

        # Check if line looks like a company name (title case, short, has company keywords)
        is_company_like = (
            len(stripped) < 80 and
            (stripped[0].isupper() if stripped else False) and
            any(kw in stripped.lower() for kw in _KNOWN_COMPANIES)
        )

        # Check if line looks like a job role
        role_keywords = ['intern', 'engineer', 'developer', 'analyst', 'designer',
                         'manager', 'associate', 'consultant', 'researcher', 'scientist',
                         'trainee', 'lead', 'architect']
        is_role_like = (
            any(kw in stripped.lower() for kw in role_keywords) and
            len(stripped) < 80 and
            not dur_match
        )

        if dur_match or simple_dur:
            if dur_match:
                start_mon = dur_match.group(1)
                start_yr = dur_match.group(2)
                end_part = dur_match.group(3)
                end_yr = dur_match.group(4) or ""
                current_duration = f"{start_mon} {start_yr} - {end_part} {end_yr}".strip()
            elif simple_dur:
                num = simple_dur.group(1)
                unit = simple_dur.group(2)
                current_duration = f"{num} {unit}s"
        elif is_company_like and not is_role_like:
            if current_company:
                flush()
            current_company = stripped
            current_role = None
            current_duration = ""
        elif is_role_like:
            if current_role and current_company:
                flush()
                current_role = stripped
                current_duration = ""
            else:
                current_role = stripped

    flush()

    # Clean and cap at 4
    clean = []
    seen = set()
    for item in internships:
        key = item['company'] + item['role']
        if key not in seen and (item['company'] or item['role']):
            seen.add(key)
            # Default duration if none found
            if not item['duration']:
                item['duration'] = "3 months"
            clean.append(item)

    return clean[:4]


def extract_certificates_from_resume(text):
    """
    Extracts certificate entries from resume text.
    Returns list of {title} dicts.
    """
    sections = _split_into_sections(text)
    cert_lines = sections.get("certificates", [])

    # Also scan for certification keywords anywhere if no section found
    if not cert_lines:
        all_lines = text.split('\n')
        for line in all_lines:
            low = line.lower()
            if any(kw in low for kw in ['certified', 'certification', 'certificate', 'coursera', 'udemy', 'nptel']):
                if 10 < len(line.strip()) < 150:
                    cert_lines.append(line)

    certs = []
    seen = set()
    for line in cert_lines:
        stripped = line.strip().lstrip('-*•>–→ ')
        if not stripped or len(stripped) < 8:
            continue
        # Skip lines that look like descriptions, not titles
        if re.match(r'(?i)^(and|the|this|in|for|with|from|to|a |an )', stripped):
            continue
        if stripped not in seen and len(stripped) < 200:
            seen.add(stripped)
            certs.append({"title": stripped})

    return certs[:8]


# ─────────────────────────────────────────────
#  CERTIFICATE PDF PARSING (unchanged)
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
