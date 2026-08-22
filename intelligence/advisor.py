# intelligence/advisor.py
"""
AI Resume & Skills Advisor Engine.

Performs skill-gap analysis for a student's resume against the expected
skill set for their academic stream, and returns a readiness score,
matched/missing skills, recommended projects, and resume bullet suggestions.
"""

from typing import List, Dict, Any


# --- Stream skill maps -------------------------------------------------

STREAM_SKILLS: Dict[str, List[str]] = {
    "Engineering": ["Python", "DSA", "Git", "Docker", "REST APIs", "SQL"],
    "Psychology": ["SPSS", "Statistical Analysis", "Qualtrics", "R", "Behavioral Assessment", "Psychometrics"],
    "BBA": ["Excel Pivot Tables", "Financial Modeling", "Market Research", "Brand Strategy", "Sales Pitching", "CRM"],
    "MBA": ["Corporate Strategy", "Business Analytics", "SQL", "Tableau/PowerBI", "DCF Valuation", "Agile"],
}


# --- Recommended projects per missing-skill area -----------------------
# Keyed by the specific skill so we can recommend a project that fills
# whichever gaps are actually missing for this student.

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


def analyze_resume_skills(resume_skills: List[str], stream: str) -> Dict[str, Any]:
    """
    Compare a student's resume skills against the expected skill set for
    their stream, and return a structured readiness report.

    Args:
        resume_skills: list of skill strings extracted from the resume
                        (e.g. from intel/parse_resume.py's output)
        stream: one of "Engineering", "Psychology", "BBA", "MBA"

    Returns:
        dict with stream, readiness_score, matched_skills,
        missing_critical_skills, recommended_projects, and
        resume_bullet_suggestions.
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

    # Resume bullets for matched skills (things worth highlighting on the resume)
    resume_bullet_suggestions = [
        BULLET_TEMPLATES[skill] for skill in matched_skills if skill in BULLET_TEMPLATES
    ]

    return {
        "stream": stream,
        "readiness_score": readiness_score,
        "matched_skills": matched_skills,
        "missing_critical_skills": missing_critical_skills,
        "recommended_projects": recommended_projects,
        "resume_bullet_suggestions": resume_bullet_suggestions,
    }


if __name__ == "__main__":
    # Quick manual test
    sample_resume_skills = ["Python", "Git", "SQL", "Machine Learning"]
    result = analyze_resume_skills(sample_resume_skills, "Engineering")
    import json
    print(json.dumps(result, indent=2))