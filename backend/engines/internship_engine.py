"""
Internship Engine
=================
Evaluates the *quality* and *legitimacy* of internships rather than
simply counting them.

Internship companies are grouped into three tiers:
  Tier 1 (Elite)     — FAANG, top product companies, government research labs
  Tier 2 (Strong)    — MNCs, well-known service/product companies
  Tier 3 (Standard)  — Startups, small firms, unrecognised names

Scoring per internship (0–10):
  - Recognised Tier 1 company                   +4
  - Recognised Tier 2 company                   +3
  - Recognised Tier 3 / unknown                 +1
  - Has a proper role title                     +2
  - Duration >= 3 months                        +2
  - Duration >= 1 month                         +1
  - Description mentions tech keywords          +2
"""

import re

# ──────────────────────────────────────────────
#  Curated Company / Institution Taxonomy
# ──────────────────────────────────────────────

# Tier 1 — Elite: FAANG, top product cos, gov research
TIER1_COMPANIES = [
    # Big Tech / FAANG
    "google", "alphabet", "meta", "facebook", "amazon", "apple", "microsoft",
    "netflix", "nvidia", "tesla", "openai", "deepmind",
    # Top Product Companies
    "adobe", "salesforce", "oracle", "vmware", "cisco", "intel", "amd",
    "qualcomm", "samsung", "uber", "airbnb", "spotify", "stripe", "palantir",
    "snowflake", "databricks", "atlassian", "shopify", "twitter", "x corp",
    "linkedin", "paypal", "square", "block",
    # Government / Research
    "isro", "drdo", "barc", "nasa", "cern", "iit", "iisc", "nit",
    "csir", "iiit", "bits", "mit", "stanford", "harvard", "oxford",
    "cambridge", "eth zurich",
    # Top Startups (well-funded)
    "razorpay", "cred", "zerodha", "phonepe", "byjus", "swiggy", "zomato",
    "flipkart", "meesho", "groww", "dream11", "unacademy",
]

# Tier 2 — Strong: Well-known MNCs and service companies
TIER2_COMPANIES = [
    # IT Service Giants
    "tcs", "tata consultancy", "infosys", "wipro", "hcl", "hcl technologies",
    "tech mahindra", "mindtree", "mphasis", "ltimindtree", "l&t infotech",
    "cognizant", "capgemini", "accenture", "deloitte", "kpmg", "ey",
    "ernst & young", "pwc", "pricewaterhousecoopers", "mckinsey", "bcg",
    # Product / SaaS (mid-tier)
    "zoho", "freshworks", "druva", "icertis", "postman", "browserstack",
    "hasura", "chargebee", "clevertap", "moengage",
    # Banks & Finance
    "jpmorgan", "jp morgan", "goldman sachs", "morgan stanley", "deutsche bank",
    "barclays", "hsbc", "citibank", "icici", "hdfc", "axis bank",
    "kotak", "sbi", "rbi",
    # Telecom / Manufacturing
    "reliance", "jio", "airtel", "bharti", "tata", "mahindra",
    "larsen & toubro", "l&t", "siemens", "bosch", "continental",
    # Ed-tech / Others
    "great learning", "simplilearn", "upgrad", "internshala", "naukri",
    "linkedin", "indeed",
]

# Ignored / Suspicious patterns (not counted as real internships)
IGNORED_INTERNSHIP_SIGNALS = [
    "self", "freelance", "personal project", "college project",
    "virtual internship", "simulation", "forage",
    "high school", "school",
]


def _match_tier(company_lower: str) -> int:
    """Returns 1, 2, or 3 based on which tier the company belongs to."""
    for t1 in TIER1_COMPANIES:
        if t1 in company_lower or company_lower in t1:
            return 1
    for t2 in TIER2_COMPANIES:
        if t2 in company_lower or company_lower in t2:
            return 2
    return 3


def evaluate_internships(internships: list) -> dict:
    """
    internships: list of dicts with keys:
        'company'     — company / institution name
        'role'        — job title / role
        'duration'    — duration string (e.g. "3 months", "6 weeks")

    Returns:
        {
          "internship_count": int,       # total accepted internships
          "quality_score": float,        # 0–100 normalised
          "tier_breakdown": {
              "tier1": int,
              "tier2": int,
              "tier3": int,
              "ignored": int
          },
          "internship_details": [
              {"company": str, "tier": int, "tier_label": str, "score": float}
          ],
          "feedback": [str]
        }
    """
    if not internships:
        return {
            "internship_count": 0,
            "quality_score": 0.0,
            "tier_breakdown": {"tier1": 0, "tier2": 0, "tier3": 0, "ignored": 0},
            "internship_details": [],
            "feedback": ["No internships added. Even 1 quality internship significantly boosts placement chances."]
        }

    tier_counts = {"tier1": 0, "tier2": 0, "tier3": 0, "ignored": 0}
    scored_internships = []
    feedback = []

    for i, intern in enumerate(internships):
        company = str(intern.get("company", "")).strip()
        role = str(intern.get("role", "")).strip()
        duration = str(intern.get("duration", "")).strip()
        company_lower = company.lower()

        # Check for ignored / suspicious entries
        if any(sig in company_lower for sig in IGNORED_INTERNSHIP_SIGNALS):
            tier_counts["ignored"] += 1
            feedback.append(f"'{company}' — skipped (doesn't appear to be a formal internship).")
            continue

        score = 0.0

        # 1. Company Tier (0–4 pts)
        tier = _match_tier(company_lower)
        tier_label = {1: "Elite (Tier 1)", 2: "Strong (Tier 2)", 3: "Standard (Tier 3)"}[tier]

        if tier == 1:
            score += 4
            tier_counts["tier1"] += 1
        elif tier == 2:
            score += 3
            tier_counts["tier2"] += 1
        else:
            score += 1
            tier_counts["tier3"] += 1

        # 2. Has role title (+2 pts)
        if len(role) >= 3:
            score += 2

        # 3. Duration (+1 or +2 pts)
        dur_months = _parse_duration_months(duration)
        if dur_months >= 3:
            score += 2
        elif dur_months >= 1:
            score += 1

        score = min(score, 10.0)

        scored_internships.append({
            "company": company,
            "role": role,
            "tier": tier,
            "tier_label": tier_label,
            "score": round(score, 1)
        })

        # Feedback
        if tier == 1:
            feedback.append(f"'{company}' — Excellent! Recognised as a top-tier institution/company.")
        elif tier == 2:
            feedback.append(f"'{company}' — Great! Recognised as a reputed organisation.")

    accepted_count = len(scored_internships)

    # Normalise: average score mapped to 0–100
    if accepted_count > 0:
        avg = sum(s["score"] for s in scored_internships) / accepted_count
        quality_score = round(min(avg * 10, 100), 1)
    else:
        quality_score = 0.0

    if not feedback:
        feedback.append("Consider applying to well-known companies/labs for stronger placement impact.")

    return {
        "internship_count": accepted_count,
        "quality_score": quality_score,
        "tier_breakdown": tier_counts,
        "internship_details": scored_internships,
        "feedback": feedback
    }


def _parse_duration_months(duration_str: str) -> float:
    """
    Best-effort extraction of duration in months from strings like:
      "3 months", "6 weeks", "2 mo", "1 year", "45 days"
    """
    if not duration_str:
        return 0

    duration_str = duration_str.lower().strip()

    # Direct month match: "3 months", "2 mo"
    m = re.search(r'(\d+\.?\d*)\s*(?:months?|mo\b)', duration_str)
    if m:
        return float(m.group(1))

    # Week match: "6 weeks"
    m = re.search(r'(\d+\.?\d*)\s*(?:weeks?|wk)', duration_str)
    if m:
        return float(m.group(1)) / 4.0

    # Year match: "1 year"
    m = re.search(r'(\d+\.?\d*)\s*(?:years?|yr)', duration_str)
    if m:
        return float(m.group(1)) * 12.0

    # Day match: "45 days"
    m = re.search(r'(\d+\.?\d*)\s*(?:days?)', duration_str)
    if m:
        return float(m.group(1)) / 30.0

    # Fallback: just a number, assume months
    m = re.search(r'(\d+)', duration_str)
    if m:
        return float(m.group(1))

    return 0
