"""
Skill Gap Engine
================
Compares a student's skills against a curated, role-aware taxonomy
of skills expected by top hiring companies — not just the top-5 from
the raw dataset.

Skills are grouped into tiers:
  Tier 1 (Core)    — Must-have for entry-level roles
  Tier 2 (Strong)  — Differentiators that boost offer chances
  Tier 3 (Bonus)   — Nice-to-have, show maturity
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
SKILLS_DATA_PATH = BASE_DIR / "data" / "skills_dataset.csv"

# ──────────────────────────────────────────────
#  Curated Skill Taxonomy (branch → role → tiers)
# ──────────────────────────────────────────────
SKILL_TAXONOMY = {
    "CSE": {
        "default": {
            "tier1": ["Python", "Data Structures", "Algorithms", "SQL", "Git"],
            "tier2": ["System Design", "REST APIs", "Linux", "Problem Solving", "OOP"],
            "tier3": ["Docker", "Cloud (AWS/GCP/Azure)", "CI/CD", "Testing"],
        },
        "Software Engineer": {
            "tier1": ["Python", "Data Structures", "Algorithms", "SQL", "Git"],
            "tier2": ["System Design", "REST APIs", "Linux", "OOP", "Java or C++"],
            "tier3": ["Docker", "Kubernetes", "Cloud", "Microservices"],
        },
        "Frontend Developer": {
            "tier1": ["HTML", "CSS", "JavaScript", "React", "Git"],
            "tier2": ["TypeScript", "REST APIs", "Responsive Design", "State Management"],
            "tier3": ["Next.js", "Testing (Jest)", "CI/CD", "Figma"],
        },
        "Backend Developer": {
            "tier1": ["Python or Node.js or Java", "SQL", "REST APIs", "Git", "Data Structures"],
            "tier2": ["System Design", "PostgreSQL or MongoDB", "Authentication (JWT)", "Linux"],
            "tier3": ["Docker", "Redis", "Message Queues", "Cloud Deployment"],
        },
        "Data Scientist": {
            "tier1": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy"],
            "tier2": ["Statistics", "Data Visualization", "Scikit-learn", "Jupyter"],
            "tier3": ["Deep Learning", "TensorFlow or PyTorch", "Cloud ML", "Big Data"],
        },
        "ML Engineer": {
            "tier1": ["Python", "Machine Learning", "Deep Learning", "pandas", "NumPy"],
            "tier2": ["TensorFlow or PyTorch", "SQL", "Model Deployment", "Scikit-learn"],
            "tier3": ["MLOps", "Docker", "Cloud AI", "Data Pipelines"],
        },
    },
    "IT": {
        "default": {
            "tier1": ["Networking Fundamentals", "SQL", "Python or Java", "Linux", "Git"],
            "tier2": ["Cybersecurity Basics", "REST APIs", "Cloud Concepts", "Problem Solving"],
            "tier3": ["Docker", "System Administration", "ITIL", "Scripting (Bash)"],
        },
        "Cybersecurity Analyst": {
            "tier1": ["Networking", "Linux", "Python", "Ethical Hacking Basics", "SQL"],
            "tier2": ["Firewalls", "SIEM Tools", "Vulnerability Assessment", "OWASP"],
            "tier3": ["Cloud Security", "CEH/CompTIA", "OSCP", "Penetration Testing"],
        },
    },
    "ECE": {
        "default": {
            "tier1": ["C", "C++", "Embedded Systems", "Digital Electronics", "Microcontrollers"],
            "tier2": ["Python", "PCB Design", "Signal Processing", "MATLAB"],
            "tier3": ["FPGA", "VLSI", "IoT", "Communication Protocols (I2C/SPI/UART)"],
        },
        "Embedded Systems Engineer": {
            "tier1": ["C", "C++", "Microcontrollers (Arduino/STM32)", "RTOS", "Digital Electronics"],
            "tier2": ["PCB Design", "Communication Protocols", "Debugging Tools", "Python"],
            "tier3": ["FPGA", "Linux Kernel", "IoT Platforms", "Power Electronics"],
        },
    },
}

# Add case-insensitive aliases for common skill name variations
SKILL_ALIASES = {
    "ml": "Machine Learning",
    "dl": "Deep Learning",
    "js": "JavaScript",
    "ts": "TypeScript",
    "dsa": "Data Structures",
    "data structure": "Data Structures",
    "algorithm": "Algorithms",
    "react.js": "React",
    "reactjs": "React",
    "next.js": "Next.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongo": "MongoDB",
    "aws": "Cloud (AWS/GCP/Azure)",
    "gcp": "Cloud (AWS/GCP/Azure)",
    "azure": "Cloud (AWS/GCP/Azure)",
    "cloud": "Cloud (AWS/GCP/Azure)",
    "oop": "OOP",
    "object oriented": "OOP",
    "git/github": "Git",
    "github": "Git",
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "scikit-learn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "c programming": "C",
    "c language": "C",
}

# Singleton load for legacy dataset (still used as supplementary signal)
_skills_df = None

def get_skills_df():
    global _skills_df
    if _skills_df is None and SKILLS_DATA_PATH.exists():
        _skills_df = pd.read_csv(SKILLS_DATA_PATH)
    return _skills_df


def normalise_skill(skill: str) -> str:
    """Normalise a skill string using aliases and title-case."""
    s = skill.strip().lower()
    if s in SKILL_ALIASES:
        return SKILL_ALIASES[s]
    return skill.strip().title()


def get_required_skills(branch: str, target_role: str = None):
    """
    Returns a dict with tier1, tier2, tier3 required skills
    based on branch and target role.
    """
    branch_upper = branch.upper()
    branch_taxonomy = SKILL_TAXONOMY.get(branch_upper, SKILL_TAXONOMY["CSE"])

    if target_role and target_role in branch_taxonomy:
        skill_set = branch_taxonomy[target_role]
    else:
        skill_set = branch_taxonomy["default"]

    return skill_set  # {"tier1": [...], "tier2": [...], "tier3": [...]}


def analyze_skill_gap(branch: str, student_skills: list, target_role: str = None):
    """
    Analyses skill gap with tiered matching.

    Returns:
        required_skills      — flat list (tier1 + tier2)
        matched_skills       — skills the student has from required
        missing_skills       — skills the student is missing (tier1 first)
        skill_match_percentage — weighted % (tier1 worth more)
        tier_breakdown       — {tier1_matched, tier2_matched, tier3_matched}
    """
    tiers = get_required_skills(branch, target_role)
    tier1 = tiers["tier1"]
    tier2 = tiers["tier2"]
    tier3 = tiers["tier3"]

    # Normalise student skills
    student_normalised = set(normalise_skill(s).lower() for s in student_skills)

    def is_matched(required_skill: str) -> bool:
        req_lower = required_skill.lower()
        # Exact match
        if req_lower in student_normalised:
            return True
        # Partial match — e.g., student says "AWS" and required says "Cloud (AWS/GCP/Azure)"
        for s in student_normalised:
            if s in req_lower or req_lower in s:
                return True
        return False

    t1_matched = [s for s in tier1 if is_matched(s)]
    t1_missing = [s for s in tier1 if not is_matched(s)]

    t2_matched = [s for s in tier2 if is_matched(s)]
    t2_missing = [s for s in tier2 if not is_matched(s)]

    t3_matched = [s for s in tier3 if is_matched(s)]

    # Weighted scoring: tier1 = 60%, tier2 = 30%, tier3 = 10%
    t1_score = (len(t1_matched) / len(tier1) * 100) if tier1 else 100
    t2_score = (len(t2_matched) / len(tier2) * 100) if tier2 else 100
    t3_score = (len(t3_matched) / len(tier3) * 100) if tier3 else 100

    weighted_pct = round(t1_score * 0.60 + t2_score * 0.30 + t3_score * 0.10, 2)

    # Required = tier1 + tier2 for display
    required_all = tier1 + tier2
    matched_all = t1_matched + t2_matched
    # Missing: tier1 gaps first (higher priority)
    missing_all = t1_missing + t2_missing

    return {
        "required_skills": required_all,
        "matched_skills": matched_all,
        "missing_skills": missing_all,
        "skill_match_percentage": weighted_pct,
        "tier_breakdown": {
            "tier1_matched": len(t1_matched),
            "tier1_total": len(tier1),
            "tier2_matched": len(t2_matched),
            "tier2_total": len(tier2),
            "tier3_matched": len(t3_matched),
            "tier3_total": len(tier3),
        }
    }
