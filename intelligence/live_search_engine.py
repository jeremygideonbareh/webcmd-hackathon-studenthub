"""
Live Search Engine — executes real-time WebCMD scraping based on student input:
- Housing / PGs / Hostels (NoBroker & Stanza Living near student locality)
- Internships (Internshala & Indeed TF-IDF matched to student skills)
- Scholarships (NSP & Buddy4Study matched to student GPA & stream)
- Discounts (SheerID & Student Beans matched to student stream)
"""

from __future__ import annotations

from typing import Any, Dict, List

import intelligence


def execute_live_student_search(
    stream: str = "Engineering",
    gpa: float = 8.0,
    locality: str = "Koramangala",
    city: str = "Bangalore",
    skills: List[str] | None = None,
    budget_max: int = 25000,
) -> Dict[str, Any]:
    """
    Execute real-time scraping & matching based strictly on student input details.
    No buffer data — all results are dynamically filtered & scraped for the user.
    """
    user_skills = skills or ["Python", "Git", "SQL"]

    # 1. Scrape live internships & match with TF-IDF against exact user skills
    resume_profile = {
        "skills": user_skills,
        "projects": [f"{stream} Academic Projects"],
    }
    category = "python-internship"
    if "psychology" in stream.lower():
        category = "psychology-research"
    elif "bba" in stream.lower() or "mba" in stream.lower():
        category = "business-development"

    jobs_data = intelligence.get_matched_jobs(resume_data=resume_profile, category=category, top_n=6)

    # 2. Scrape live housing / PGs / hostels near campus locality
    housing_data = intelligence.get_housing(locality=locality, city=city, budget_max=budget_max)

    # 3. Match active scholarships for student GPA & stream
    scholarships_data = intelligence.get_scholarships(gpa=gpa, stream=stream)

    # 4. Filter student discounts for student stream
    discounts_data = intelligence.get_discounts(stream=stream)

    # 5. Run AI Resume Skill Gap Analysis
    advisor_data = intelligence.analyze_resume_skills(user_skills=user_skills, stream=stream)

    return {
        "user_profile": {
            "stream": stream,
            "gpa": gpa,
            "locality": locality,
            "city": city,
            "skills": user_skills,
        },
        "jobs": jobs_data.get("jobs", []),
        "housing": housing_data.get("listings", []),
        "scholarships": scholarships_data,
        "discounts": discounts_data,
        "advisor": advisor_data,
    }
