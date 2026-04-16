import io
import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from .skill_gap_engine import get_skills_df

def extract_text_from_pdf(file_stream):
    if not PyPDF2:
        return ""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + " "
        return text
    except Exception as e:
        print("Error reading PDF:", e)
        return ""

def scan_for_skills(text, branch="CSE", target_role=None):
    """
    Scans freeform text for known skills in the dataset.
    """
    text_lower = text.lower()
    df = get_skills_df()
    
    # Filter dataset simply to get available skills
    known_skills = []
    if branch in df.columns:
        known_skills.extend([str(s).strip().lower() for s in df[branch].dropna().tolist() if str(s).strip()])
    if target_role and target_role in df.columns:
        known_skills.extend([str(s).strip().lower() for s in df[target_role].dropna().tolist() if str(s).strip()])
        
    # If no branch data, fallback to global scan
    if not known_skills:
        for col in df.columns:
            known_skills.extend([str(s).strip().lower() for s in df[col].dropna().tolist() if str(s).strip()])
            
    known_skills = list(set(known_skills))
    
    found_skills = []
    # Very basic substring/regex search
    for skill in known_skills:
        # handle boundary matching for common short words like 'c' to avoid matching 'cat'
        escaped_skill = re.escape(skill)
        if re.search(r'\b' + escaped_skill + r'\b', text_lower):
            found_skills.append(skill.title())
            
    return list(set(found_skills))

def extract_cgpa(text):
    """Attempts to find CGPA via regex. Returns raw value and detected scale."""
    matches = re.findall(r'(?i)(?:cgpa|gpa)[\s:]*([0-9]\.[0-9]+)', text)
    if matches:
        val = round(float(matches[0]), 2)
        # Detect scale: if val is plausibly on a 4.0 scale
        scale = 4 if val <= 4.0 else 10
        return {"cgpa": val, "scale": scale}
    return None


# Known issuers and their canonical pretty names for certificate parsing
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
    """
    Analyses a certificate PDF text and returns:
      title      — best guess at the certificate title/course name
      issuer     — recognised issuer organisation
      raw_excerpt — first 300 chars of the PDF text (for preview)
    """
    text_lower = text.lower()
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # 1. Detect issuer
    issuer = None
    for keyword, pretty in _CERT_ISSUERS:
        if keyword in text_lower:
            issuer = pretty
            break

    # 2. Find title — look for line after a known certificate phrase
    title = None
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Skip very short or boilerplate lines
        if any(kw in line_lower for kw in _CERT_KEYWORDS):
            # The line(s) just before this one often contain the course title
            candidates = [l for l in lines[max(0, i-3):i] if len(l) > 8]
            if candidates:
                title = candidates[-1]
                break

    # 3. Fallback: try regex for common patterns like "Learn <Something>" or "<Something> Specialization"
    if not title:
        m = re.search(
            r'(?i)(?:course|program|specialization|bootcamp|certification)[:\s]+([A-Za-z][A-Za-z0-9 :–\-]{5,80})',
            text
        )
        if m:
            title = m.group(1).strip()

    # 4. Fallback: take the longest line in the first 20 lines that looks like a title
    if not title:
        candidates = sorted(
            [l for l in lines[:20] if 5 < len(l) < 100],
            key=len, reverse=True
        )
        if candidates:
            title = candidates[0]

    # 5. Build a composed title string if we have issuer but a weak title
    composed = title or "Certificate"
    if issuer and issuer.lower() not in composed.lower():
        composed = f"{composed} — {issuer}"

    return {
        "title": composed,
        "raw_title": title,
        "issuer": issuer,
        "raw_excerpt": text[:300]
    }
