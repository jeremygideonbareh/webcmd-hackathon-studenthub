"""
AI Resume & Skills Advisor Engine.

Analyzes a student's profile (skills, projects, education) against target stream expectations:
- Engineering
- Psychology
- BBA
- MBA

Outputs:
1. Stream readiness score (0-100%)
2. Matched & missing critical skills
3. High-impact recommended portfolio projects
4. Tailored resume bullet point suggestions
"""

from __future__ import annotations

from typing import Dict, List, Any

# Stream Skill Benchmarks
STREAM_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "Engineering": {
        "core_skills": ["Python", "Data Structures & Algorithms", "Git", "Docker", "REST APIs", "SQL", "Linux"],
        "recommended_projects": [
            {
                "title": "High-Throughput Microservice Engine",
                "description": "Build a scalable REST API using Python FastAPI, PostgreSQL, and Redis caching for sub-50ms response times.",
                "skills_gained": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
            },
            {
                "title": "Automated Web Scraper & Data Pipeline",
                "description": "Develop a headless browser scraper using Playwright/curl_cffi with automated proxy rotation and pandas ETL transformation.",
                "skills_gained": ["Python", "Web Scraping", "Pandas", "ETL"]
            }
        ],
        "bullet_templates": [
            "Architected distributed backend service processing {X}+ requests/sec with {Y}% uptime.",
            "Optimized SQL query execution plan, reducing database latency by {Y}% across core endpoints.",
            "Integrated CI/CD deployment pipeline with Docker and GitHub Actions, reducing build times by {Y}%."
        ]
    },
    "Psychology": {
        "core_skills": ["SPSS", "Statistical Analysis", "Qualtrics", "R", "Behavioral Assessment", "Psychometrics", "Case Study Analysis"],
        "recommended_projects": [
            {
                "title": "Empirical Behavioral Survey & Statistical Report",
                "description": "Design a multi-variable Qualtrics survey measuring cognitive fatigue, running ANOVA and regression models in SPSS.",
                "skills_gained": ["SPSS", "Qualtrics", "ANOVA", "Regression Analysis"]
            },
            {
                "title": "Mental Health Intervention Meta-Analysis",
                "description": "Conduct a systematic literature review and R meta-analysis evaluating digital mindfulness intervention efficacy.",
                "skills_gained": ["R", "Literature Review", "Psychometrics", "Data Visualization"]
            }
        ],
        "bullet_templates": [
            "Conducted quantitative statistical analysis on sample of {X}+ participants using SPSS ANOVA and regression models.",
            "Authored {X}-page empirical research paper evaluating cognitive behavioral intervention outcomes.",
            "Designed and deployed Qualtrics survey instrument achieving {X}% response rate across {Y}+ respondents."
        ]
    },
    "BBA": {
        "core_skills": ["Excel Pivot Tables", "Financial Modeling", "Market Research", "Brand Strategy", "Sales Pitching", "Google Analytics", "CRM"],
        "recommended_projects": [
            {
                "title": "D2C Brand Go-To-Market Strategy",
                "description": "Formulate a digital marketing acquisition campaign for a D2C startup with CAC/LTV payback financial modeling.",
                "skills_gained": ["Market Research", "Financial Modeling", "Google Analytics", "CAC/LTV Analysis"]
            },
            {
                "title": "B2B Sales Pipeline & CRM Optimization",
                "description": "Build a sales lead scoring matrix and CRM pipeline workflow to optimize conversion funnel metrics.",
                "skills_gained": ["Sales Strategy", "CRM Workflow", "Lead Scoring", "Pitching"]
            }
        ],
        "bullet_templates": [
            "Developed financial valuation model (DCF/LBO) forecasting revenue growth across 5-year period.",
            "Executed digital marketing campaign driving {X}% increase in qualified lead acquisition.",
            "Presented strategic market analysis deck to senior stakeholders, identifying {X}% new market expansion."
        ]
    },
    "MBA": {
        "core_skills": ["Corporate Strategy", "Business Analytics", "SQL", "Tableau / PowerBI", "Financial Valuation (DCF)", "Agile Management", "P&L Analysis"],
        "recommended_projects": [
            {
                "title": "Corporate M&A Synergy & DCF Valuation Model",
                "description": "Build a discounted cash flow (DCF) model analyzing a hypothetical Tech M&A acquisition with sensitivity tables.",
                "skills_gained": ["DCF Valuation", "M&A Analysis", "Financial Modeling", "Corporate Strategy"]
            },
            {
                "title": "Executive Business Intelligence Dashboard",
                "description": "Construct an interactive Tableau/PowerBI dashboard querying SQL data warehouse to track enterprise KPIs.",
                "skills_gained": ["SQL", "Tableau", "PowerBI", "Executive Reporting"]
            }
        ],
        "bullet_templates": [
            "Formulated strategic corporate roadmap for {X} division, resulting in ${Y}M projected operational savings.",
            "Constructed SQL data warehouse queries and Tableau dashboard tracking $5M+ ARR pipeline metrics.",
            "Led cross-functional Agile team of {X} members to deliver strategic product launch 2 weeks ahead of schedule."
        ]
    }
}


def analyze_resume_skills(user_skills: List[str], stream: str = "Engineering") -> Dict[str, Any]:
    """Analyze student skills against target stream benchmarks."""
    benchmark = STREAM_BENCHMARKS.get(stream, STREAM_BENCHMARKS["Engineering"])
    core_skills = benchmark["core_skills"]

    user_skills_lower = {s.lower() for s in user_skills}
    matched = [s for s in core_skills if s.lower() in user_skills_lower or any(u in s.lower() for u in user_skills_lower)]
    missing = [s for s in core_skills if s not in matched]

    match_pct = (len(matched) / len(core_skills)) * 100 if core_skills else 50.0
    readiness_score = min(100, max(20, round(match_pct + (len(user_skills) * 3))))

    bullets = [t.format(X="500", Y="45") for t in benchmark["bullet_templates"]]

    return {
        "stream": stream,
        "readiness_score": readiness_score,
        "matched_skills": matched,
        "missing_critical_skills": missing,
        "recommended_projects": benchmark["recommended_projects"],
        "resume_bullet_suggestions": bullets
    }
