# intelligence/advisor.py
"""
AI Resume & Skills Advisor Engine.

Two layers:

1. Deterministic rule-based core (no network, always available):
   skill-gap analysis of a student's resume against their academic stream,
   producing a readiness score, matched/missing skills, and recommended
   projects that fill the actual gaps.

2. Optional Groq-powered LLM layer:
   generates natural, personalized resume bullet suggestions for the
   student's MATCHED skills instead of static templates. Activated only
   when GROQ_API_KEY is present in the environment (.env is loaded via
   python-dotenv). ANY failure - missing key, missing package, network
   error, rate limit, bad response - silently falls back to the static
   BULLET_TEMPLATES so the advisor never breaks a demo.

Security note: the API key lives ONLY in .env (git-ignored). It is never
hardcoded here, never logged, never returned in output dicts.
"""

import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()  # repo-root .env; real values stay out of source control

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TIMEOUT_SECONDS = float(os.getenv("GROQ_TIMEOUT_SECONDS", "20"))
MAX_AI_BULLETS = 6

SYSTEM_PROMPT = (
    "You are a concise career coach for Indian university students. "
    "You write ATS-friendly resume bullet points that start with strong "
    "action verbs. You never invent company names, GPA numbers, or metrics - "
    "where a number would go, use a bracketed placeholder like [X%] or [N]."
)


# --- Stream skill maps -------------------------------------------------

STREAM_SKILLS: Dict[str, List[str]] = {
    "Engineering": ["Python", "DSA", "Git", "Docker", "REST APIs", "SQL"],
    "Psychology": ["SPSS", "Statistical Analysis", "Qualtrics", "R", "Behavioral Assessment", "Psychometrics"],
    "BBA": ["Excel Pivot Tables", "Financial Modeling", "Market Research", "Brand Strategy", "Sales Pitching", "CRM"],
    "MBA": ["Corporate Strategy", "Business Analytics", "SQL", "Tableau/PowerBI", "DCF Valuation", "Agile"],
}


# --- Recommended projects per missing-skill area -----------------------

PROJECT_LIBRARY: Dict[str, Dict[str, Any]] = {
    "DSA": {
        "title": "Competitive Programming Portfolio",
        "description": "Solve and document 50+ algorithmic problems across arrays, trees, and graphs, published on GitHub with complexity analysis.",
        "skills_gained": ["DSA", "Python"],
    },
    "Docker": {
        "title": "Containerized Microservice Deployment",
        "description": "Containerize a small REST API with Docker and deploy it, documenting the build and deployment pipeline.",
        "skills_gained": ["Docker", "REST APIs"],
    },
    "REST APIs": {
        "title": "Personal REST API Project",
        "description": "Design and build a REST API for a small app (e.g. a to-do list or expense tracker) with proper CRUD endpoints.",
        "skills_gained": ["REST APIs", "SQL"],
    },
    "SQL": {
        "title": "Data Analysis with SQL",
        "description": "Query and analyze a public dataset using SQL joins, aggregations, and window functions; present findings in a short report.",
        "skills_gained": ["SQL"],
    },
    "R": {
        "title": "Statistical Report in R",
        "description": "Reproduce a published psychology study's statistical analysis in R, including ANOVA and regression models.",
        "skills_gained": ["R", "Statistical Analysis"],
    },
    "Psychometrics": {
        "title": "Empirical Behavioral Survey & Statistical Report",
        "description": "Design a psychometric survey instrument, collect data from 500+ participants, and analyze results using SPSS ANOVA and regression models.",
        "skills_gained": ["SPSS", "ANOVA", "Psychometrics"],
    },
    "Qualtrics": {
        "title": "Survey Design & Deployment",
        "description": "Build and deploy a structured survey in Qualtrics, covering question design, sampling, and basic response analysis.",
        "skills_gained": ["Qualtrics", "Behavioral Assessment"],
    },
    "Financial Modeling": {
        "title": "Startup Financial Model",
        "description": "Build a 3-statement financial model for a hypothetical startup, including revenue projections and a DCF valuation.",
        "skills_gained": ["Financial Modeling", "Excel Pivot Tables"],
    },
    "Market Research": {
        "title": "Market Entry Research Report",
        "description": "Conduct primary and secondary market research for a product idea, including competitor analysis and a go-to-market recommendation.",
        "skills_gained": ["Market Research", "Brand Strategy"],
    },
    "CRM": {
        "title": "Mock Sales Pipeline in a CRM",
        "description": "Set up a mock sales pipeline in a free CRM tool (HubSpot/Zoho), tracking leads through stages with sample data.",
        "skills_gained": ["CRM", "Sales Pitching"],
    },
    "Business Analytics": {
        "title": "Business Dashboard in Tableau/PowerBI",
        "description": "Build an interactive dashboard analyzing a public business dataset, highlighting key trends and actionable insights.",
        "skills_gained": ["Business Analytics", "Tableau/PowerBI"],
    },
    "DCF Valuation": {
        "title": "Company Valuation Case Study",
        "description": "Perform a full DCF valuation of a publicly listed company using its financial statements, and compare against market cap.",
        "skills_gained": ["DCF Valuation", "Corporate Strategy"],
    },
}


# --- Resume bullet templates per skill ----------------------------------
# Static fallback used whenever the Groq layer is unavailable.

BULLET_TEMPLATES: Dict[str, str] = {
    "SPSS": "Conducted quantitative statistical analysis on sample of 500+ participants using SPSS ANOVA and regression models.",
    "Qualtrics": "Designed and deployed structured surveys in Qualtrics to collect and analyze behavioral response data.",
    "R": "Performed statistical modeling and data visualization in R to analyze experimental results.",
    "Psychometrics": "Applied psychometric principles to design and validate a behavioral assessment instrument.",
    "DSA": "Solved 50+ data structures and algorithms problems, demonstrating strong proficiency in Python-based problem solving.",
    "Docker": "Containerized and deployed a REST API service using Docker, streamlining the development-to-production pipeline.",
    "REST APIs": "Designed and implemented RESTful API endpoints supporting full CRUD functionality for a production-style application.",
    "SQL": "Wrote complex SQL queries involving joins, aggregations, and window functions to extract actionable insights from relational datasets.",
    "Financial Modeling": "Built a 3-statement financial model with DCF valuation to support startup investment decision-making.",
    "Market Research": "Conducted primary and secondary market research to inform go-to-market strategy for a new product line.",
    "CRM": "Managed a mock sales pipeline in a CRM platform, tracking leads through defined conversion stages.",
    "Business Analytics": "Built interactive dashboards in Tableau/PowerBI to surface key business trends from large datasets.",
    "DCF Valuation": "Performed discounted cash flow valuation of a publicly listed company, benchmarking against market capitalization.",
    "Corporate Strategy": "Developed a corporate strategy case study evaluating market entry options for a Fortune 500 company.",
    "Agile": "Applied Agile/Scrum methodology to manage sprint planning and delivery for a cross-functional team project.",
}


def get_groq_client():
    """Build a Groq client from GROQ_API_KEY in the environment.

    Returns None (never raises) when the key is unset, the groq package is
    not installed, or client construction fails - callers treat None as
    'use static templates'.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq
    except ImportError:
        return None
    try:
        return Groq(api_key=api_key, timeout=GROQ_TIMEOUT_SECONDS)
    except Exception:
        return None


def _build_bullet_prompt(
    matched_skills: List[str], missing_skills: List[str], stream: str
) -> str:
    matched_list = ", ".join(matched_skills) or "(none)"
    missing_list = ", ".join(missing_skills[:4]) or "(none)"
    return (
        f"Student stream: {stream}.\n"
        f"Skills this student ALREADY has (evidence on resume): {matched_list}.\n"
        f"Skills they are MISSING (do not write bullets claiming these): {missing_list}.\n\n"
        f"Write one polished resume bullet per matched skill above "
        f"({len(matched_skills)} bullets total). Rules:\n"
        "- One line each, max 22 words, starting with an action verb.\n"
        "- Reflect realistic coursework/personal-project scope, NOT internships at named companies.\n"
        "- Use [N] or [X%] placeholders instead of inventing numbers.\n"
        "- Output ONLY the bullets, one per line, each starting with '- '."
    )


def _extract_bullets(text: str) -> List[str]:
    """Parse LLM output into clean bullet strings."""
    bullets: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*•·]\s*", "", line)
        line = re.sub(r"^\d+[.)]\s*", "", line)
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = line.strip().strip('"')
        if len(line.split()) >= 5:
            bullets.append(line)
        if len(bullets) >= MAX_AI_BULLETS:
            break
    return bullets


def generate_ai_bullets(
    client: Any,
    matched_skills: List[str],
    missing_skills: List[str],
    stream: str,
) -> List[str]:
    """One Groq chat call. Returns [] on ANY failure - caller falls back."""
    if client is None or not matched_skills:
        return []
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _build_bullet_prompt(matched_skills, missing_skills, stream),
                },
            ],
            temperature=0.6,
            max_tokens=400,
        )
        content = completion.choices[0].message.content or ""
        return _extract_bullets(content)
    except Exception:
        # Network down, rate limited, malformed response, quota exhausted...
        # The rule-based advisor must keep working regardless.
        return []


def analyze_resume_skills(
    resume_skills: List[str],
    stream: str,
    use_ai: bool = True,
    client: Any = None,
) -> Dict[str, Any]:
    """
    Compare a student's resume skills against the expected skill set for
    their stream, and return a structured readiness report.

    Args:
        resume_skills: list of skill strings extracted from the resume
                        (e.g. from intel/parse_resume.py's output)
        stream: one of "Engineering", "Psychology", "BBA", "MBA"
        use_ai: when True (default), try Groq for personalized bullets;
                falls back to static templates automatically.
        client: pre-built Groq client (tests inject fakes here). When None
                and use_ai is True, one is built from the environment.

    Returns:
        dict with stream, readiness_score, matched_skills,
        missing_critical_skills, recommended_projects,
        resume_bullet_suggestions, and bullet_source ('groq'|'template').
    """
    if stream not in STREAM_SKILLS:
        raise ValueError(
            f"Unknown stream '{stream}'. Expected one of: {list(STREAM_SKILLS.keys())}"
        )

    expected_skills = STREAM_SKILLS[stream]

    # Case-insensitive matching so "python" in a resume matches "Python" in our map
    resume_skills_lower = {s.strip().lower() for s in resume_skills}

    matched_skills = [
        skill for skill in expected_skills
        if skill.lower() in resume_skills_lower
    ]
    missing_critical_skills = [
        skill for skill in expected_skills
        if skill.lower() not in resume_skills_lower
    ]

    readiness_score = round((len(matched_skills) / len(expected_skills)) * 100) if expected_skills else 0

    # Recommend up to 3 projects targeting the missing skills, avoiding duplicates
    recommended_projects = []
    seen_titles = set()
    for skill in missing_critical_skills:
        project = PROJECT_LIBRARY.get(skill)
        if project and project["title"] not in seen_titles:
            recommended_projects.append(project)
            seen_titles.add(project["title"])
        if len(recommended_projects) >= 3:
            break

    template_bullets = [
        BULLET_TEMPLATES[skill]
        for skill in matched_skills
        if skill in BULLET_TEMPLATES
    ]

    ai_bullets: List[str] = []
    if use_ai:
        if client is None:
            client = get_groq_client()
        ai_bullets = generate_ai_bullets(
            client, matched_skills, missing_critical_skills, stream
        )

    bullet_source = "groq" if ai_bullets else "template"

    return {
        "stream": stream,
        "readiness_score": readiness_score,
        "matched_skills": matched_skills,
        "missing_critical_skills": missing_critical_skills,
        "recommended_projects": recommended_projects,
        "resume_bullet_suggestions": ai_bullets or template_bullets,
        "bullet_source": bullet_source,
    }


if __name__ == "__main__":
    # Quick manual test - fully offline unless GROQ_API_KEY is set in .env
    import json

    sample_resume_skills = ["Python", "Git", "SQL", "Machine Learning"]
    result = analyze_resume_skills(sample_resume_skills, "Engineering")
    print(json.dumps(result, indent=2))
